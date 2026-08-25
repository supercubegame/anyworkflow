#!/usr/bin/env python3
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

missing = [k for k in ['purpose','backed_up','not_backed_up','invariants','writeback'] if k not in manifest]
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
    },
}
ARTIFACTS.mkdir(exist_ok=True)
(ARTIFACTS / 'verify-report.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(f"\n共执行 {len(checks)} 条检查，通过 {len(checks)-len(failures)}，失败 {len(failures)}")
print('报告已写入 artifacts/verify-report.json')
raise SystemExit(1 if failures else 0)
