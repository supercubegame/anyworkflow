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
# 一模一样**。于是一份讲「别安静地说谎」的文档变成了「别安静地说谎」，
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
# agents / vendor 这两个目录 2026-08-26 才加进来。在那之前三份真抄本
# 完全在闸门视野之外 —— 整个删掉都不会红。
REGISTERED_DIRS = ('docs', 'scripts', 'agents', 'vendor/ci-workflows')

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
declared_reg = {k for k in integrity
                if any(k.startswith(d + '/') for d in REGISTERED_DIRS)}
missing_reg = sorted(on_disk - declared_reg)
ghost_reg = sorted(declared_reg - on_disk)
ok = not missing_reg and not ghost_reg
# 目录名不手写：上一版这里写死了「docs/ · scripts/」，而加进 agents / vendor
# 之后那句话当场就不成立了 —— 散文腐化在我自己的 detail 里发生了一次。
dirs_label = ' · '.join(d + '/' for d in REGISTERED_DIRS)
detail = (f'{dirs_label} 共 {len(on_disk)} 份，登记集合完全重合' if ok else
          f'未登记：{missing_reg or "无"} · 登记了但不存在：{ghost_reg or "无"}')
check(f'登记表与目录集合相等（{dirs_label}）', ok, detail)

# --------------------------------------------------------------------------
# 真抄本的四条断言。这一组补的是 MINIMAL-GATE 里明写的「不守 6」：
# agents/*.md 与 vendor/ci-workflows/report.yml 之前**在闸门视野之外**，可以被清成
# 空壳而全绿。而这三份正是这仓的立仓之本。
#
# **不断言「文件存在」** —— git 已经证明了，那是空断言。四条分工：
#   清单双向 -> 上面那条集合相等（REGISTERED_DIRS 已含 agents / vendor）
#   逐字节身份 -> 上面那条 blob 哈希
#   正文锚点  -> 下面第一条（防空壳：哈希换了但内容被整段抽空）
#   恢复充分性 -> 下面第二条（恢复这个 agent 需要哪几节，逐个非空）
#   新鲜度    -> 下面第三条（读回时间戒30 天期限）
#
# **为什么还需要锚点，哈希不够吗？** 哈希只能说「文件变了」。一次正当的重导出
# 会让哈希变，而那时候重算登记值是对的 —— 但如果那次「重导出」其实是一份
# 被抽空的壳子，重算登记值后门门照样全绿。锚点守的是那一刻。
# --------------------------------------------------------------------------
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
check('真抄本正文锚点（逐条命中）', ok, detail)

# --------------------------------------------------------------------------
# 恢复充分性。「恢复这个 agent 需要哪几个字段」列出来，逐个断言非空。
# **「本来就空」和「导出丢了」要分得清** —— 所以它报的是哪一节空了，
# 不是笼统地说「不完整」。
# --------------------------------------------------------------------------
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
detail = (f'{len(copies)} 份抄本共 {section_total} 个必需小节全部非空' if ok
          else ('; '.join(bad) if bad else 'copies 为空'))
check('真抄本恢复充分性（必需小节非空）', ok, detail)

# --------------------------------------------------------------------------
# 新鲜度。备份最常见的死法是悄悄过期。
#
# **这里用的是 runner 的时钟，而那是真时钟。** _tested_limits 里那条说的是我
# 上下文里那行「现在几点」（实测差过一个多小时），两回事，别搞混。
# 而登记的读回时间本身来自归档提交的外部时间戳，不是我拍的。
#
# 两侧都要能红：过期红（抄本旧了），**落在未来也红**（有人拿一个未来时间戳
# 把期限涂绿了，那比过期更阴）。未来容差 10 分钟。
# --------------------------------------------------------------------------
max_age = true_copies.get('max_readback_age_days')
# **先验上限，再进循环。** 变异体实测：把这个键删掉，age > None 直接抛
# TypeError —— 而**崩溃不是红**：报告压根不落盘，composer 只能送一条降级评论，
# 于是「新鲜度过期」和「有人删了这个键」在评论上长得不一样，但都读不到逐项证据。
valid_max_age = isinstance(max_age, int) and not isinstance(max_age, bool) and max_age > 0
now = datetime.now(timezone.utc)
bad = []
ages = []
for rel in sorted(copies):
    raw = (copies[rel] or {}).get('readback_at')
    if not raw:
        bad.append(f'{rel}：没有 readback_at —— 一份没有读回时间的抄本等于一张旧纸')
        continue
    try:
        when = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError:
        bad.append(f'{rel}：readback_at 解析不了：{raw!r}')
        continue
    age = (now - when).total_seconds() / 86400.0
    ages.append((rel, age))
    if age < -(10 / 1440.0):
        bad.append(f'{rel}：readback_at 落在未来（{-age:.2f} 天后）：{raw}')
    elif valid_max_age and age > max_age:
        bad.append(f'{rel}：读回已 {age:.1f} 天，超过上限 {max_age} 天：{raw}')
if not valid_max_age:
    ok, detail = False, f'max_readback_age_days 不是正整数：{max_age!r} —— 没有期限的新鲜度断言是空的'
elif not copies:
    ok, detail = False, 'copies 为空'
else:
    ok = not bad
    oldest = max(ages, key=lambda x: x[1]) if ages else None
    detail = ((f'最旧那份 {oldest[0]} 已 {oldest[1]:.1f} 天，还剩 {max_age - oldest[1]:.1f} 天'
               f'（上限 {max_age}）') if ok else '; '.join(bad))
check('真抄本读回新鲜度（带期限）', ok, detail)

# --------------------------------------------------------------------------
# 形近错字黑名单。**这一条守的是我自己反复踩的坑（次数记在 _tested_limits）。**
#
# 根因定位了，而且不在任何存储通道上：我往文件里写中文时会敲成形近字，
# 而且**字节长度不变**，于是体积与关键字类检查全部看不见。
# 最贵的一处：一份讲「别安静地说谎」的文档，那两个字被换成了形近字，
# 于是一句话当场失去意义，而没有任何东西会喊。具体现场与次数记在
# manifest._tested_limits 里（那里可以安全地引用错字，JSON 不被本扫描剥注释
# —— 所以那里也只写描述，不写错字本体）。
#
# 一条规矩被违反两次就该变成断言，而这条远过两次。
#
# **黑名单本身用码位构造，绝不在这里手写那几个字** —— 手写正是病因，
# 而一个拼错的黑名单项永远不会命中，那就是一条空断言。
# **方向是黑名单，而黑名单对新错字默认泄漏** —— 这一条写在这里，
# 不假装它守住了所有形近字。
# --------------------------------------------------------------------------
CONFUSABLES = {
    '\u62c4\u672c': '\u6284\u672c',
    '\u8bf4\u8c01': '\u8bf4\u8c0e',
    '\u6492\u8c01': '\u6492\u8c0e',
    '\u5206\u5c98': '\u5206\u5c94',
    '\u9ab6\u67b6': '\u9aa8\u67b6',
    '\u9806': '\u987a',
}
# 自证：黑名单里的错字与正字必须真的不同。拼成一样的话这条当场变空。
degenerate = [b for b, g in CONFUSABLES.items() if b == g]
scanned = []
found = []
# **先剥注释，再找。** 这是同一个回环的第三次：一份**记录**了错字的文件
# 会被自己判红。前两次是 marker 印进报告、attest 日志印进评论。
# 代码文件里提到错字只会出现在注释里（黑名单本身用码位写），
# 所以剥掉注释就够。**Markdown 不剥** —— 那里的字就是真内容。
STRIP_BY_SUFFIX = {'.py': ('#',), '.mjs': ('//',), '.yml': ('#',)}
for rel in sorted(integrity):
    target = ROOT / rel
    if not target.exists() or target.suffix not in ('.md', '.json', '.py', '.mjs', '.yml'):
        continue
    raw = target.read_text(encoding='utf-8', errors='replace')
    tokens = STRIP_BY_SUFFIX.get(target.suffix)
    if tokens:
        text = strip_comments(raw, tokens)
        # 剥完先自证还剩真东西：剥成空字符串的话这一份会免费通过。
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
    detail = (f'扫了 {len(scanned)} 份，{len(CONFUSABLES)} 项黑名单 0 命中' if ok
              else '; '.join(found))
check('形近错字黑名单（负向扫描）', ok, detail)

# --------------------------------------------------------------------------
# 跨抄本一致性。**两份抄本各自都是忠实的读回，而它们互相矛盾** ——
# 这种形状没有任何单份断言看得见，因为每一份自己都是对的。
#
# 实例：Quinn 的活里有一项是每天读回 Devon 的定时，而它 prompt 里那个期望值
# 已经不是 Devon 真实的 cron 了。于是那条巡检每天都会拿错的期望值去比。
#
# 这条修不在本仓（要改 ClickUp 里的 live prompt），所以它走**带期限的义务**：
# 宽限期内只报剩多少天，过期判红。两侧都要能红：
#   不一致 + 没义务  -> 红（悄悄抹掉了一条真问题）
#   不一致 + 义务过期 -> 红
#   已一致 + 义务还挂  -> 红（做完了还挂着，那份清单就没人读了）
# --------------------------------------------------------------------------
def section_value(path, head):
    """读一个小节下的第一条列表项值（形如 `- 20 10 * * *`）。"""
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
        bad.append(f"{spec['target']}：读不到 {spec['target_section']} 下的值"
                   f"—— 这条跨抄本断言什么都证明不了")
        continue
    src_text = src.read_text(encoding='utf-8', errors='replace') if src.exists() else ''
    if not src_text:
        bad.append(f"{spec['source']}：读不到正文")
        continue
    consistent = want in src_text
    ob = obligations.get(pid)
    if consistent and ob:
        bad.append(f'{pid}：两份抄本已经一致了，而义务还挂着 '
                   f'—— 做完了请删掉它，一份挂着已完成事项的清单没人会再读')
    elif consistent:
        notes_cc.append(f'{pid}：一致（{want!r} 出现在 {spec["source"]} 里）')
    elif not ob:
        bad.append(f'{pid}：不一致且**没有登记义务** —— {spec["target"]} 的 '
                   f'{spec["target_section"]} 是 {want!r}，而它没出现在 {spec["source"]} 里')
    else:
        due_raw = ob.get('due')
        try:
            due = datetime.fromisoformat(str(due_raw) + 'T00:00:00+00:00')
        except ValueError:
            bad.append(f'{pid}：义务的 due 解析不了：{due_raw!r}')
            continue
        left = (due - now).total_seconds() / 86400.0
        if left < 0:
            bad.append(f'{pid}：义务已过期 {-left:.1f} 天（due {due_raw}）。'
                       f'到期只有两个正确反应：真的修完，或确认做不到并挑进 '
                       f'_tested_limits。把日期往后挑不在选项里')
        else:
            notes_cc.append(f'{pid}：不一致，已登记为带期限的义务，还剩 {left:.1f} 天'
                            f'（{spec["target"]} 是 {want!r}）')
if not pairs:
    ok, detail = False, 'true_copies.cross_copy 是空的 —— 空清单让这条断言当场变空'
else:
    ok = not bad
    detail = ('; '.join(notes_cc) if ok else '; '.join(bad))
check('跨抄本一致性（不一致必须有带期限的义务）', ok, detail)

# --------------------------------------------------------------------------
# 检查总数的等号断言，以及 MINIMAL-GATE 里那个数字。
#
# 下限型的计数会自己漂（「最少 N 条」是个地板，多一条少一条都不红），
# 所以这里是等号。删掉三条检查而忘了改登记值 —— 红。
#
# **而 MINIMAL-GATE.md 里那句「守哪几件事」是手写散文，它上一版就已经漂了**：
# 写着七件事，而闸门早就不是七条了。散文里的数字注定漂，而漂了不会有任何动静，
# 所以给它配一条交叉核对：真值就在同一个仓里（登记值），所以这条做得成。
#
# 这一条自己也计入总数，所以期望值是 len(checks) + 1。
# --------------------------------------------------------------------------
declared_checks = ((manifest.get('checks') or {}).get('verify'))
actual_checks = len(checks) + 1
gate_doc = ROOT / 'docs' / 'MINIMAL-GATE.md'
gate_text = gate_doc.read_text(encoding='utf-8', errors='replace') if gate_doc.exists() else ''
if not isinstance(declared_checks, int) or declared_checks <= 0:
    ok, detail = False, f'manifest.checks.verify 不是正整数：{declared_checks!r}'
elif declared_checks != actual_checks:
    ok, detail = False, (f'登记 {declared_checks} 条，实际跑了 {actual_checks} 条。'
                         f'**修法是把断言补回来，不是把期望数改小**')
elif not gate_text:
    ok, detail = False, 'docs/MINIMAL-GATE.md 读不到 —— 那句话的交叉核对无法进行'
elif str(actual_checks) not in gate_text:
    ok, detail = False, (f'docs/MINIMAL-GATE.md 里找不到 {actual_checks} 这个数 —— '
                         f'那句「守哪几件事」已经不成立了')
else:
    ok, detail = True, f'{actual_checks} 条，登记值与 MINIMAL-GATE 里那个数都对上了'
check('检查总数（等号）与 MINIMAL-GATE 里那个数', ok, detail)

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
        'trueCopies': len(copies),
        'anchorTotal': anchor_total,
        'requiredSectionTotal': section_total,
        'maxReadbackAgeDays': max_age,
        'oldestReadbackAgeDays': (round(max(a for _, a in ages), 2) if ages else None),
        'confusablesScanned': len(scanned),
        'confusablesBlacklist': len(CONFUSABLES),
        'crossCopyPairs': len(pairs),
        'openObligations': len(obligations),
        'checksVerify': actual_checks,
    },
}
ARTIFACTS.mkdir(exist_ok=True)
(ARTIFACTS / 'verify-report.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(f"\n共执行 {len(checks)} 条检查，通过 {len(checks)-len(failures)}，失败 {len(failures)}")
print('报告已写入 artifacts/verify-report.json')
raise SystemExit(1 if failures else 0)
