#!/usr/bin/env python3
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / 'artifacts'
manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))

checks = []

# --------------------------------------------------------------------------
# 每条检查带一个稳定 id。**id 才是承重的，标题可以随便改** ——
# 拿可读名字当键会让「改个名」变成承重操作，而重命名应该是响亮的、
# 不是静默的。id 与 manifest.invariants 的键集合必须相等（见文件末尾那条）。
#
# id 重复也要红：两条检查共用一个 id 的话，集合相等依然成立，
# 而其中一条就无人登记了 —— 那是用集合当期望的经典漏网口。
# --------------------------------------------------------------------------
def check(cid, title, ok, detail):
    checks.append((cid, title, ok, detail))
    print(("PASS" if ok else "FAIL") + f"  {title} | {detail}")

agents = (ROOT / 'AGENTS.md').read_bytes()
claude = (ROOT / 'CLAUDE.md').read_bytes()
check('rules_files_identical', 'AGENTS.md 与 CLAUDE.md 逐字节相同', agents == claude, f'{len(agents)} bytes')

recovery_exists = (ROOT / 'docs' / 'RECOVERY.md').exists()
check('recovery_doc_exists', '恢复说明存在', recovery_exists, 'docs/RECOVERY.md')

blind_exists = (ROOT / 'docs' / 'BLIND-SPOTS.md').exists()
check('blind_spots_doc_exists', '盲区清单存在', blind_exists, 'docs/BLIND-SPOTS.md')

nonempty = isinstance(manifest.get('not_backed_up'), list) and len(manifest['not_backed_up']) > 0
check('not_backed_up_nonempty', 'not_backed_up 不是空数组', nonempty, f"count={len(manifest.get('not_backed_up', [])) if isinstance(manifest.get('not_backed_up'), list) else 'bad-type'}")

missing = [k for k in ['purpose','backed_up','not_backed_up','invariants','writeback','docs_integrity'] if k not in manifest]
check('manifest_top_keys', 'manifest 顶层键齐全', len(missing) == 0, 'missing=' + (','.join(missing) if missing else 'none'))

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
check('writeback_marker_pinned', '回写 marker：workflow 与 manifest 逐字相同', ok, detail)

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
check('composer_sentinel_pinned', 'composer 哨兵：写入方与核对方逐字相同', ok, detail)

EMPTY_BLOB = 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
REGISTERED_DIRS = ('docs', 'scripts', 'agents', 'vendor/ci-workflows')

def git_blob(raw):
    return hashlib.sha1(b'blob %d\x00' % len(raw) + raw).hexdigest()

integrity = manifest.get('docs_integrity') or {}
check('blob_hash_selftest', 'blob 哈希函数自证（git 空 blob 常量）',
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
check('registered_files_byte_identical', '承重文件逐字节身份（blob 哈希）', ok, detail)

on_disk = set()
for d in REGISTERED_DIRS:
    for f in sorted((ROOT / d).glob('*')):
        if f.is_file():
            on_disk.add(f'{d}/{f.name}')
declared_reg = {k for k in integrity if any(k.startswith(d + '/') for d in REGISTERED_DIRS)}
missing_reg = sorted(on_disk - declared_reg)
ghost_reg = sorted(declared_reg - on_disk)
ok = not missing_reg and not ghost_reg
dirs_label = ' · '.join(d + '/' for d in REGISTERED_DIRS)
detail = (f'{dirs_label} 共 {len(on_disk)} 份，登记集合完全重合' if ok else f'未登记：{missing_reg or "无"} · 登记了但不存在：{ghost_reg or "无"}')
check('registry_equals_directory', f'登记表与目录集合相等（{dirs_label}）', ok, detail)

true_copies = manifest.get('true_copies') or {}
copies = (true_copies.get('copies') or {})

bad = []
anchor_total = 0
for rel in sorted(copies):
    spec = copies[rel]
    target = ROOT / rel
    anchors = spec.get('anchors') or []
    anchor_total += len(anchors)
    if not anchors:
        bad.append(f'{rel}：一条锚点都没登记 —— 那这份抄本就回到了只靠哈希守')
        continue
    if not target.exists():
        bad.append(f'{rel}：登记了但文件不在')
        continue
    text = target.read_text(encoding='utf-8', errors='replace')
    miss = [a for a in anchors if a not in text]
    if miss:
        bad.append(f'{rel}：{len(miss)}/{len(anchors)} 条锚点失配 -> {miss}')
if not copies:
    ok, detail = False, 'manifest.true_copies.copies 是空的 —— 空登记表让这条断言当场变空'
else:
    ok = not bad
    detail = (f'{len(copies)} 份抄本共 {anchor_total} 条锚点全部命中' if ok else '; '.join(bad))
check('true_copy_anchors', '真抄本正文锚点（逐条命中）', ok, detail)

bad = []
section_total = 0
for rel in sorted(copies):
    spec = copies[rel]
    target = ROOT / rel
    want = spec.get('required_sections') or []
    section_total += len(want)
    if not want:
        bad.append(f'{rel}：没登记任何必需小节')
        continue
    if not target.exists():
        bad.append(f'{rel}：文件不在')
        continue
    lines = target.read_text(encoding='utf-8', errors='replace').splitlines()
    for head in want:
        idx = next((i for i, l in enumerate(lines) if l.strip() == head.strip()), None)
        if idx is None:
            bad.append(f'{rel}：缺小节 {head!r}')
            continue
        body = []
        for l in lines[idx + 1:]:
            if l.strip().startswith('### ') or (head.endswith(':') and l and not l[0].isspace()):
                break
            body.append(l)
        if not ''.join(body).strip():
            bad.append(f'{rel}：小节 {head!r} 在，但内容是空的')
ok = bool(copies) and not bad
detail = (f'{len(copies)} 份抄本共 {section_total} 个必需小节全部非空' if ok else ('; '.join(bad) if bad else 'copies 为空'))
check('true_copy_restore_sufficiency', '真抄本恢复充分性（必需小节非空）', ok, detail)

max_age = true_copies.get('max_readback_age_days')
valid_max_age = isinstance(max_age, int) and not isinstance(max_age, bool) and max_age > 0
now = datetime.now(timezone.utc)
bad = []
ages = []
limits = {}
for rel in sorted(copies):
    spec = copies[rel] or {}
    limit = max_age
    override = spec.get('max_readback_age_days')
    if override is not None:
        if not (isinstance(override, int) and not isinstance(override, bool) and override > 0):
            bad.append(f'{rel}：读回期限覆盖值不是正整数：{override!r}')
            continue
        if valid_max_age and override > max_age:
            bad.append(f'{rel}：覆盖值 {override} 天比全局上限 {max_age} 天更松 —— **覆盖只许更严**，放宽一条上限等于亲手把断言改成装饰')
            continue
        limit = override
    limits[rel] = limit
    raw = spec.get('readback_at')
    if not raw:
        bad.append(f'{rel}：没有 readback_at —— 一份没有读回时间的抄本等于一张旧纸')
        continue
    try:
        when = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError:
        bad.append(f'{rel}：readback_at 解析不了：{raw!r}')
        continue
    age = (now - when).total_seconds() / 86400.0
    ages.append((rel, age, limit))
    if age < -(10 / 1440.0):
        bad.append(f'{rel}：readback_at 落在未来（{-age:.2f} 天后）：{raw}')
    elif isinstance(limit, int) and age > limit:
        bad.append(f'{rel}：读回已 {age:.1f} 天，超过上限 {limit} 天：{raw}')
if not valid_max_age:
    ok, detail = False, f'max_readback_age_days 不是正整数：{max_age!r} —— 没有期限的新鲜度断言是空的'
elif not copies:
    ok, detail = False, 'copies 为空'
else:
    ok = not bad
    tightest = min((a for a in ages), key=lambda x: x[2] - x[1]) if ages else None
    detail = ((f'最吃紧那份 {tightest[0]} 已 {tightest[1]:.1f} 天，还剩 {tightest[2] - tightest[1]:.1f} 天（它的上限 {tightest[2]}，全局 {max_age}）') if ok else '; '.join(bad))
check('true_copy_readback_freshness', '真抄本读回新鲜度（按抄本可收紧的期限）', ok, detail)

shrink_ratio = true_copies.get('max_shrink_ratio')
bad = []
notes_sz = []
if not isinstance(shrink_ratio, float) or not (0.0 < shrink_ratio <= 0.5):
    ok, detail = False, (f'max_shrink_ratio 必须是 (0, 0.5] 区间的浮点数：{shrink_ratio!r} —— 太大会放走被抽空的抄本，太小则是一台假红工厂')
elif not copies:
    ok, detail = False, 'copies 为空 —— 空登记表让这条断言当场变空'
else:
    for rel in sorted(copies):
        spec = copies[rel] or {}
        base = spec.get('size_baseline_bytes')
        target = ROOT / rel
        if not (isinstance(base, int) and not isinstance(base, bool) and base > 0):
            bad.append(f'{rel}：没登记 size_baseline_bytes 或不是正整数：{base!r} —— 缺了它这条断言对这一份就是空的')
            continue
        if not target.exists():
            bad.append(f'{rel}：登记了但文件不在')
            continue
        cur = len(target.read_bytes())
        floor = int(base * (1.0 - shrink_ratio))
        if cur < floor:
            bad.append(f'{rel}：现在 {cur} 字节，低于下限 {floor}（高水位 {base}，容差 {int(shrink_ratio * 100)}%），缩水 {100 - cur * 100 // base}%。**一份被抽空的抄本和一次正当精简长得一样**，所以改 baseline 必须是显式动作')
        elif cur > base:
            bad.append(f'{rel}：现在 {cur} 字节，高于高水位 {base} —— 把 baseline 抬到 {cur}，否则这个水位会慢慢变得抓不住任何东西')
        else:
            notes_sz.append(f'{rel}：{cur}/{base}（下限 {floor}）')
    ok = not bad
    detail = (f'{len(copies)} 份抄本体积都在高水位与下限之间（容差 {int(shrink_ratio * 100)}%）：' + ' · '.join(notes_sz)) if ok else '; '.join(bad)
check('true_copy_size_floor', '真抄本体积下限（高水位 + 缩水容差，两侧都红）', ok, detail)

CONFUSABLES = {
    '\u62c4\u672c': '\u6284\u672c',
    '\u8bf4\u8c01': '\u8bf4\u8c0e',
    '\u6492\u8c01': '\u6492\u8c0e',
    '\u5206\u5c98': '\u5206\u5c94',
    '\u9ab6\u67b6': '\u9aa8\u67b6',
    '\u9806': '\u987a',
}
degenerate = [b for b, g in CONFUSABLES.items() if b == g]
scanned = []
found = []
STRIP_BY_SUFFIX = {'.py': ('#',), '.mjs': ('//',), '.yml': ('#',)}
for rel in sorted(integrity):
    target = ROOT / rel
    if not target.exists() or target.suffix not in ('.md', '.json', '.py', '.mjs', '.yml'):
        continue
    raw = target.read_text(encoding='utf-8', errors='replace')
    tokens = STRIP_BY_SUFFIX.get(target.suffix)
    if tokens:
        text = strip_comments(raw, tokens)
        if len(text.strip()) < len(raw.strip()) * 0.3:
            found.append(f'{rel}：剥掉注释后只剩不到三成，剥过头了，这一份的扫描不可信')
            continue
    else:
        text = raw
    scanned.append(rel)
    for b, g in CONFUSABLES.items():
        n = text.count(b)
        if n:
            found.append(f'{rel}：{b} ×{n}（应为 {g}）')
if degenerate:
    ok, detail = False, f'黑名单里有 {len(degenerate)} 项错字等于正字 —— 那几项永远不会命中'
elif not scanned:
    ok, detail = False, '一份文件都没扫到 —— 这条断言当场变空'
else:
    ok = not found
    detail = (f'扫了 {len(scanned)} 份，{len(CONFUSABLES)} 项黑名单 0 命中' if ok else '; '.join(found))
check('confusables_blacklist', '形近错字黑名单（负向扫描）', ok, detail)

def section_value(path, head):
    if not path.exists():
        return None
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    idx = next((i for i, l in enumerate(lines) if l.strip() == head.strip()), None)
    if idx is None:
        return None
    for l in lines[idx + 1:]:
        if l.strip().startswith('### '):
            break
        t = l.strip()
        if t.startswith('- '):
            return t[2:].strip()
    return None

obligations = {o.get('id'): o for o in (manifest.get('obligations') or [])}
pairs = true_copies.get('cross_copy') or []
bad = []
notes_cc = []
for spec in pairs:
    pid = spec.get('id')
    src, tgt = ROOT / spec['source'], ROOT / spec['target']
    want = section_value(tgt, spec['target_section'])
    if want is None:
        bad.append(f"{spec['target']}：读不到 {spec['target_section']} 下的值—— 这条跨抄本断言什么都证明不了")
        continue
    src_text = src.read_text(encoding='utf-8', errors='replace') if src.exists() else ''
    if not src_text:
        bad.append(f"{spec['source']}：读不到正文")
        continue
    consistent = want in src_text
    ob = obligations.get(pid)
    if consistent and ob:
        bad.append(f'{pid}：两份抄本已经一致了，而义务还挂着 —— 做完了请删掉它，一份挂着已完成事项的清单没人会再读')
    elif consistent:
        notes_cc.append(f'{pid}：一致（{want!r} 出现在 {spec["source"]} 里）')
    elif not ob:
        bad.append(f'{pid}：不一致且**没有登记义务** —— {spec["target"]} 的 {spec["target_section"]} 是 {want!r}，而它没出现在 {spec["source"]} 里')
    else:
        due_raw = ob.get('due')
        try:
            due = datetime.fromisoformat(str(due_raw) + 'T00:00:00+00:00')
        except ValueError:
            bad.append(f'{pid}：义务的 due 解析不了：{due_raw!r}')
            continue
        left = (due - now).total_seconds() / 86400.0
        if left < 0:
            bad.append(f'{pid}：义务已过期 {-left:.1f} 天（due {due_raw}）。到期只有两个正确反应：真的修完，或确认做不到并挑进 _tested_limits。把日期往后挑不在选项里')
        else:
            notes_cc.append(f'{pid}：不一致，已登记为带期限的义务，还剩 {left:.1f} 天（{spec["target"]} 是 {want!r}）')
if not pairs:
    ok, detail = False, 'true_copies.cross_copy 是空的 —— 空清单让这条断言当场变空'
else:
    ok = not bad
    detail = ('; '.join(notes_cc) if ok else '; '.join(bad))
check('cross_copy_consistency', '跨抄本一致性（不一致必须有带期限的义务）', ok, detail)

CONSUMER_FILES = {
    'clickup-brain-backup': ['split-apply.yml', 'split-dry-run.yml', 'verify.yml'],
    'TodoX': ['verify.yml', 'release.yml', 'screenshots.yml', 'mirror.yml'],
    'flappycat': ['verify.yml'],
    'meetnote': ['verify.yml'],
    'jumpwow': ['verify.yml'],
    'image-grabber': ['verify.yml'],
    'crossyroad': ['verify.yml'],
}
consumer_path = ROOT / 'docs' / 'SHARED-WRITEBACK-CONSUMERS.md'
expected_repo_count = len(CONSUMER_FILES)
expected_workflow_count = sum(len(v) for v in CONSUMER_FILES.values())

def render_consumers():
    lines = [
        '# Shared Writeback Consumers',
        '',
        "This file is generated from the backup repo's current workspace knowledge of repos that call `supercubegame/ci-workflows/.github/workflows/report.yml`.",
        'It exists because a hand-maintained prose list already missed real consumers twice, and the first version of this generated list missed one again.',
        '',
        f'- Repositories: **{expected_repo_count}**',
        f'- Workflow files: **{expected_workflow_count}**',
        '',
    ]
    for repo in sorted(CONSUMER_FILES):
        lines.append(f'## {repo}')
        for wf in CONSUMER_FILES[repo]:
            lines.append(f'- `.github/workflows/{wf}`')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'

generated = render_consumers()
actual = consumer_path.read_text(encoding='utf-8') if consumer_path.exists() else None
if actual is None:
    ok, detail = False, 'docs/SHARED-WRITEBACK-CONSUMERS.md 不存在 —— 散文又会退回成手写记忆'
else:
    ok = actual == generated
    detail = (f'{expected_repo_count} 个仓库 / {expected_workflow_count} 份 workflow，生成物与登记完全一致' if ok else '生成物与当前登记不一致 —— 新增/删改了消费者但没同步这份文件')
check('shared_writeback_consumers_generated', '共享回写消费者生成物与登记相等', ok, detail)

split = manifest.get('prompt_split') or {}
notes_rel = split.get('archive')
prompt_rel = split.get('prompt_copy')
moved = split.get('moved_sections') or []
notes_path = ROOT / notes_rel if notes_rel else None
prompt_path = ROOT / prompt_rel if prompt_rel else None
bad = []
if not notes_rel or not prompt_rel:
    ok, detail = False, 'manifest.prompt_split 缺 archive 或 prompt_copy —— 这条断言对着一份空声明会免费通过'
elif len(moved) < 3:
    ok, detail = False, (f'moved_sections 只登记了 {len(moved)} 条 —— 少于 3 条时这条断言基本是装饰，而拆分最容易的失败方式就是「各留一份」')
elif not notes_path.exists() or not prompt_path.exists():
    ok, detail = False, f'{notes_rel} 或 {prompt_rel} 不在'
else:
    notes_text = notes_path.read_text(encoding='utf-8', errors='replace')
    prompt_text = prompt_path.read_text(encoding='utf-8', errors='replace')
    if len(notes_text.strip()) < 2000:
        bad.append(f'{notes_rel} 只有 {len(notes_text.strip())} 字 —— 一份被抽空的档案和一份真档案在文件树上一样')
    if notes_rel not in prompt_text:
        bad.append(f'{prompt_rel} 正文里找不到 {notes_rel} —— **指路牌没了，档案就等于不存在**。重导出 prompt 抄本时忘了同步也会红在这里，那是有意的')
    missing_moved = [s for s in moved if s not in notes_text]
    if missing_moved:
        bad.append(f'档案里缺 {len(missing_moved)}/{len(moved)} 节：{missing_moved}')
    leaked = [s for s in moved if s in prompt_text]
    if leaked:
        bad.append(f'**搬走的小节还留在 prompt 抄本里**（{len(leaked)}/{len(moved)}）：{leaked}。各留一份是这类拆分最容易的失败方式，而它本来全绿')
    archive_anchors = split.get('archive_anchors') or []
    if len(archive_anchors) < len(moved):
        bad.append(f'archive_anchors 只登记了 {len(archive_anchors)} 条，而搬走了 {len(moved)} 节 —— **锚点要跟着那一节走**，拆分不是删锚点的理由')
    else:
        miss_a = [a for a in archive_anchors if a not in notes_text]
        if miss_a:
            bad.append(f'档案锚点失配 {len(miss_a)}/{len(archive_anchors)} 条：{miss_a}')
    ok = not bad
    detail = (f'{len(moved)} 节全在 {notes_rel}（{len(notes_text.encode())} bytes）、一条都不在 {prompt_rel} 里，指路牌在，档案 {len(archive_anchors)} 条锚点全部命中' if ok else '; '.join(bad))
check('prompt_archive_split', '指令与档案拆分（负向那侧承重）', ok, detail)

declared_inv = set((manifest.get('invariants') or {}).keys())
SELF = ROOT / 'verify.py'
self_code = strip_comments(SELF.read_text(encoding='utf-8'), ('#',))
scanned_ids = re.findall(r"^[ \t]*check\(\s*'([a-z0-9_]+)'", self_code, re.M)
dup_ids = sorted({i for i in scanned_ids if scanned_ids.count(i) > 1})
actual_inv = set(scanned_ids)
unregistered = sorted(actual_inv - declared_inv)
orphaned = sorted(declared_inv - actual_inv)

if not scanned_ids:
    ok, detail = False, ('从源码里一个 check id 都没扫到 —— 正则写歪了，而空集合会让这条断言对着一份空声明免费通过')
elif 'invariants_match_checks' not in actual_inv:
    ok, detail = False, ('扫到的 id 里没有本条自己 —— 正向对照失败，扫描结果不可信')
elif dup_ids:
    ok, detail = False, (f'有 {len(dup_ids)} 个 id 重复：{dup_ids} —— 集合相等依然成立，而其中一条就无人登记了')
elif not declared_inv:
    ok, detail = False, 'manifest.invariants 是空的 —— 空声明让这条断言当场变空'
elif unregistered or orphaned:
    ok, detail = False, (f'未登记的检查：{unregistered or "无"} · 登记了但没有对应检查：{orphaned or "无"}。**修法是两边对齐，不是把声明删成空的**')
else:
    ok, detail = True, f'{len(actual_inv)} 条检查与声明集合完全重合（按 id 从源码扫，不按标题、不按顺序）'
check('invariants_match_checks', 'manifest.invariants 与实际检查集合相等', ok, detail)

declared_checks = ((manifest.get('checks') or {}).get('verify'))
actual_checks = len(checks) + 1
gate_doc = ROOT / 'docs' / 'MINIMAL-GATE.md'
gate_text = gate_doc.read_text(encoding='utf-8', errors='replace') if gate_doc.exists() else ''
if not isinstance(declared_checks, int) or declared_checks <= 0:
    ok, detail = False, f'manifest.checks.verify 不是正整数：{declared_checks!r}'
elif declared_checks != actual_checks:
    ok, detail = False, (f'登记 {declared_checks} 条，实际跑了 {actual_checks} 条。**修法是把断言补回来，不是把期望数改小**')
elif not gate_text:
    ok, detail = False, 'docs/MINIMAL-GATE.md 读不到 —— 那句话的交叉核对无法进行'
elif str(actual_checks) not in gate_text:
    ok, detail = False, (f'docs/MINIMAL-GATE.md 里找不到 {actual_checks} 这个数 —— 那句「守哪几件事」已经不成立了')
else:
    ok, detail = True, f'{actual_checks} 条，登记值与 MINIMAL-GATE 里那个数都对上了'
check('checks_count_equals', '检查总数（等号）与 MINIMAL-GATE 里那个数', ok, detail)

if scanned_ids and scanned_ids[-1] != 'checks_count_equals':
    checks.append(('checks_count_last', '计数那一条必须排在最后', False, f'源码里最后一个 check 是 {scanned_ids[-1]!r} —— len(checks)+1 那个偏移量已经不成立。**把新检查移到计数那一条之前，不要改偏移量**'))
    print('FAIL  计数那一条必须排在最后 | ' + checks[-1][3])

failures = [f'{t} | {d}' for _, t, ok_, d in checks if not ok_]
report = {
    'gate': 'backup',
    'passed': len(checks) - len(failures),
    'total': len(checks),
    'failures': failures,
    'checks': [{'id': i, 'title': t, 'ok': ok_, 'detail': d} for i, t, ok_, d in checks],
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
        'trueCopies': len(copies),
        'anchorTotal': anchor_total,
        'requiredSectionTotal': section_total,
        'maxReadbackAgeDays': max_age,
        'perCopyReadbackLimits': {k: limits[k] for k in sorted(limits)},
        'oldestReadbackAgeDays': (round(max(a for _, a, _l in ages), 2) if ages else None),
        'maxShrinkRatio': shrink_ratio,
        'copySizeBaselines': {k: (copies[k] or {}).get('size_baseline_bytes') for k in sorted(copies)},
        'confusablesScanned': len(scanned),
        'confusablesBlacklist': len(CONFUSABLES),
        'crossCopyPairs': len(pairs),
        'sharedWritebackRepos': expected_repo_count,
        'sharedWritebackWorkflows': expected_workflow_count,
        'promptSplitMovedSections': len(moved),
        'promptSplitArchiveAnchors': len(split.get('archive_anchors') or []),
        'promptArchiveBytes': (len(notes_path.read_bytes()) if notes_path and notes_path.exists() else None),
        'openObligations': len(obligations),
        'checksVerify': actual_checks,
        'invariantsDeclared': len(declared_inv),
        'invariantIds': sorted(actual_inv),
    },
}
ARTIFACTS.mkdir(exist_ok=True)
(ARTIFACTS / 'verify-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(f"\n共执行 {len(checks)} 条检查，通过 {len(checks)-len(failures)}，失败 {len(failures)}")
print('报告已写入 artifacts/verify-report.json')
raise SystemExit(1 if failures else 0)
