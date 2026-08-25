#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / 'artifacts'
manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))

checks = []

def check(title, ok, detail):
    checks.append((title, ok, detail))
    print(("PASS" if ok else "FAIL") + f"  {title} | {detail}")

agents = (ROOT / 'AGENTS.md').read_bytes()
claude = (ROOT / 'CLAUDE.md').read_bytes()
check('AGENTS.md 与 CLAUDE.md 逐字节相同', agents == claude, f'{len(agents)} bytes')

recovery_exists = (ROOT / 'docs' / 'RECOVERY.md').exists()
check('恢复说明存在', recovery_exists, 'docs/RECOVERY.md')

blind_exists = (ROOT / 'docs' / 'BLIND-SPOTS.md').exists()
check('盲区清单存在', blind_exists, 'docs/BLIND-SPOTS.md')

nonempty = isinstance(manifest.get('not_backed_up'), list) and len(manifest['not_backed_up']) > 0
check('not_backed_up 不是空数组', nonempty, f"count={len(manifest.get('not_backed_up', [])) if isinstance(manifest.get('not_backed_up'), list) else 'bad-type'}")

missing = [k for k in ['purpose','backed_up','not_backed_up','invariants','writeback','docs_integrity'] if k not in manifest]
check('manifest 顶层键齐全', len(missing) == 0, 'missing=' + (','.join(missing) if missing else 'none'))

# --------------------------------------------------------------------------
# 回写 marker 是一组耦合参数：workflow 传出去的那个，和 attest 回头去找的那个，
# 必须逐字相同。真源在 manifest.writeback.marker —— attest 从那里读（真取用点），
# 这条断言把 workflow 里那一行钉在同一个值上。改一处忘了另一处，两个方向都红。
#
# 扫描前先剥掉注释行：下面这段解释文字里就出现过 marker 这个词，而
# 「某段里有没有 X」不先切段就找，会同时制造漏报和误报。剥完先自证还剩真东西，
# 剥成空字符串的话后面这条会免费通过。
# --------------------------------------------------------------------------
WF_PATH = ROOT / '.github' / 'workflows' / 'verify.yml'
wf_raw = WF_PATH.read_text(encoding='utf-8')
wf_code = '\n'.join(l for l in wf_raw.splitlines() if not l.lstrip().startswith('#'))
declared = (manifest.get('writeback') or {}).get('marker')
found = re.findall(r"^[ \t]*marker:[ \t]*'([^']+)'[ \t]*$", wf_code, re.M)

if 'jobs:' not in wf_code or 'uses:' not in wf_code:
    ok, detail = False, '剥掉注释之后 workflow 里连 jobs:/uses: 都不见了 —— 剥过头了，这条断言本身不可信'
elif len(found) != 1:
    ok, detail = False, f'workflow 里的 marker: 行有 {len(found)} 条，应该恰好 1 条（找到：{found}）'
elif not declared:
    ok, detail = False, 'manifest.writeback.marker 缺失或为空 —— attest 会拿空值去找评论，那条断言当场变空'
else:
    ok = found[0] == declared
    detail = f'workflow={found[0]!r} manifest={declared!r}'
check('回写 marker：workflow 与 manifest 逐字相同', ok, detail)

# --------------------------------------------------------------------------
# composer 哨兵是第二组耦合参数：compose-report.mjs 往评论里写的那串，和
# attest_delivery.py 回头找的那串，必须逐字相同。它承重的原因是共享回写
# workflow 的**兜底评论也带着同一个 marker** —— 分开「完整报告」与「没有逐项
# 证据的兜底」，全靠这个哨兵。两边漂开的话 attest 会把每一次完整报告都判成
# 说不清，或者更糟：把兜底读成完整。
#
# 这条断言自己不持有那个字面量，它从两个真取用点各抄一次再比 —— 整段重写
# 弄丢一处，另一处还在用它，当场红。
# --------------------------------------------------------------------------
SENTINEL_RE = re.compile(r"^[ \t]*(?:const[ \t]+)?COMPOSER_SENTINEL[ \t]*=[ \t]*'([^']+)'", re.M)

def strip_comments(text, tokens):
    kept = [l for l in text.splitlines()
            if not any(l.lstrip().startswith(t) for t in tokens)]
    return '\n'.join(kept)

composer_src = strip_comments((ROOT / 'scripts' / 'compose-report.mjs').read_text(encoding='utf-8'), ('//',))
attest_src = strip_comments((ROOT / 'scripts' / 'attest_delivery.py').read_text(encoding='utf-8'), ('#',))
composer_hits = SENTINEL_RE.findall(composer_src)
attest_hits = SENTINEL_RE.findall(attest_src)

if 'writeFileSync' not in composer_src or 'def evaluate' not in attest_src:
    ok, detail = False, '剥掉注释之后两个脚本里连主体代码都不见了 —— 剥过头了，这条断言本身不可信'
elif len(composer_hits) != 1 or len(attest_hits) != 1:
    ok, detail = False, (f'哨兵定义应该各恰好 1 处，实际 composer={len(composer_hits)} attest={len(attest_hits)}')
else:
    ok = composer_hits[0] == attest_hits[0]
    detail = f'composer={composer_hits[0]!r} attest={attest_hits[0]!r}'
check('composer 哨兵：写入方与核对方逐字相同', ok, detail)

# --------------------------------------------------------------------------
# 承重文件的逐字节身份。
#
# 这条是一次真事故换来的，而不是为了「看起来更完整」：把文档推上去之后逐个
# 读回核对，发现存储里的字和发出去的不一样 —— 全是形近字，而且**字节长度
# 一模一样**。于是一份讲「别安静地说谎」的文档变成了「别安静地说谁」，
# 而体积、关键字、“文件存在”这三类检查全部毫无意见。
#
# 真源是本地导出的那份，登记在 manifest.docs_integrity 里。登记值是 40 位十六进制，
# 纯 ASCII —— 它本身不会被这类改写碰到，而 CI 读的是**存储字节**重算。
# 两边不等就红。
#
# 两件要记住：
# 1. **这是一组有意的摩擦。** 改这些文件里的任何一个字，都必须同时重算登记值。
#    报告会直接告诉你是哪一份、期望多少、实际多少。
# 2. **它只守登记了的那几份。** 没登记的文件仍然可以被改字而闸门全绿，
#    所以下面还有一条双向的清单断言盯着“该登记的都登记了”。
#
# 哈希函数自证：git 对空 blob 的公认常量。算错了的话下面每一条比较都不可信。
# --------------------------------------------------------------------------
EMPTY_BLOB = 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
REGISTERED_DIRS = ('docs', 'scripts')

def git_blob(raw):
    return hashlib.sha1(b'blob %d\x00' % len(raw) + raw).hexdigest()

integrity = manifest.get('docs_integrity') or {}
check('blob 哈希函数自证（git 空 blob 常量）',
      git_blob(b'') == EMPTY_BLOB, f'空 blob = {git_blob(b"")}')

bad = []
for rel in sorted(integrity):
    want = integrity[rel]
    target = ROOT / rel
    if not target.exists():
        bad.append(f'{rel}：登记了但文件不在')
        continue
    got = git_blob(target.read_bytes())
    if got != want:
        bad.append(f'{rel}：期望 {want[:12]} 实际 {got[:12]}'
                   f'（{len(target.read_bytes())} bytes）')
if not integrity:
    ok, detail = False, 'manifest.docs_integrity 是空的 —— 一个空登记表让这条断言当场变空'
else:
    ok = not bad
    detail = (f'{len(integrity)} 份全部逐字节相同' if ok
              else '; '.join(bad))
check('承重文件逐字节身份（blob 哈希）', ok, detail)

# --------------------------------------------------------------------------
# 清单即期望，双向。手写清单永远追不上目录：新加一份文档而忘了登记，
# 它不会喊，它只是不被检查。所以这里把**目录下实际存在的集合**当期望，
# 多一个少一个都红。新增默认不通过，方向才是对的。
# --------------------------------------------------------------------------
on_disk = set()
for d in REGISTERED_DIRS:
    for f in sorted((ROOT / d).glob('*')):
        if f.is_file():
            on_disk.add(f'{d}/{f.name}')
declared_reg = {k for k in integrity if k.split('/')[0] in REGISTERED_DIRS}
missing_reg = sorted(on_disk - declared_reg)
ghost_reg = sorted(declared_reg - on_disk)
ok = not missing_reg and not ghost_reg
detail = (f'docs/ 与 scripts/ 共 {len(on_disk)} 份，登记集合完全重合' if ok else
          f'未登记：{missing_reg or "无"} · 登记了但不存在：{ghost_reg or "无"}')
check('登记表与目录集合相等（docs/ · scripts/）', ok, detail)

# --------------------------------------------------------------------------
# 报告落盘。它不是断言，是让这条闸门的结论走得出这个 job —— Actions 的运行
# 日志读不到，所以逐项结果要变成 artifact，再由共享回写 workflow 合成评论。
# --------------------------------------------------------------------------
failures = [f'{t} | {d}' for t, ok_, d in checks if not ok_]
report = {
    'gate': 'backup',
    'passed': len(checks) - len(failures),
    'total': len(checks),
    'failures': failures,
    'checks': [{'title': t, 'ok': ok_, 'detail': d} for t, ok_, d in checks],
    'metrics': {
        'rulesBytes': len(agents),
        'notBackedUpCount': len(manifest.get('not_backed_up', []) or []),
        'manifestTopKeys': sorted(manifest.keys()),
        'writebackMarker': declared,
        'upstreamRef': (manifest.get('writeback') or {}).get('upstream_ref'),
        'composerSentinel': composer_hits[0] if len(composer_hits) == 1 else None,
        'registeredFiles': len(integrity),
        'registeredDirsFileCount': len(on_disk),
        'unregistered': sorted(missing_reg),
        'registryLocalExport': len((manifest.get('docs_integrity_provenance') or {}).get('local_export') or []),
        'registryStoredOnly': len((manifest.get('docs_integrity_provenance') or {}).get('stored_bytes_only') or []),
    },
}
ARTIFACTS.mkdir(exist_ok=True)
(ARTIFACTS / 'verify-report.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(f"\n共执行 {len(checks)} 条检查，通过 {len(checks)-len(failures)}，失败 {len(failures)}")
print('报告已写入 artifacts/verify-report.json')
raise SystemExit(1 if failures else 0)
