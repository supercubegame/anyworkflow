#!/usr/bin/env python3
# ===========================================================================
# 送达核对（attest）
# ===========================================================================
#
# 闸门绿了不等于结论送出去了。这两件事在面板上长得一模一样，而后者坏掉的时候
# 从外面看仓库依然是「跑过了」。这个脚本回头去 API 上确认：**这一次运行**贴出来
# 的那条评论真的存在。
#
# 共享回写 workflow 内部已经有「发完读回来」，但那是监控自证清白。这里是从外面
# 看，看的和读评论的人拿到的是同一份东西。
#
# 五个设计点，每一个都是为了不让它变成空断言：
#
# 1. **两条通道都查。** 只查一条的话，另一条坏掉时它会安静通过。
# 2. **钉在本次运行上。** 「存在一条带 marker 的评论」是幂等写入的经典假绿 ——
#    上一次运行留下的那条会让它在回写完全坏掉的情况下照样通过。所以正文里必须
#    同时含本次短 SHA 和本次 run id。
# 3. **区分完整报告与兜底报告。** 降级那条评论**同样带着 marker**，所以必须靠
#    composer 哨兵区分，否则「送达了」会把「送出去的是一份没有逐项证据的兜底」
#    读成成功。
# 4. **轮询，不睡一觉。** 判据是布尔，不是计数。
# 5. **自证。** 下面那套离线用例每次都先跑：同一个检查器在合成的好样本上必须
#    0 问题，在八个坏样本上必须各自判红。尺子坏了就 exit 2，而那和「送达失败」
#    是两件不同的事。
#
# marker 从 manifest.json 读（那是真源，也是这里成为「真取用点」的原因）。
# 闸门有一条断言把 workflow 里传出去的那个值钉在同一处。
#
# 退出码：0 送达且是完整报告 · 1 送达链有问题 · 2 尺子或前置条件坏了
# ===========================================================================
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPOSER_SENTINEL = '<!-- anyworkflow-composer-ran -->'
DEGRADED_PHRASE = '报告降级'
POLL_ATTEMPTS = 8
POLL_SLEEP_SECONDS = 5
# 数字不手写：由 selftest() 里那张表算出来。散文里手写的条数注定漂，而漂了不会有任何动静。
SELFTEST_CASE_COUNT = 0


def hits(comments, marker):
    """同一个查找器，真货和自证样本都走它。"""
    return [c for c in comments if marker in (c.get('body') or '')]


def evaluate(marker, sha, run_id, pr_number, pr_comments, commit_comments):
    """纯函数：给定两条通道的评论，判这次送达成不成立。"""
    problems = []
    notes = []
    channel = 'pr' if pr_number else 'commit'
    notes.append('这次走的是 ' + (f'PR #{pr_number}' if pr_number else f'commit {sha[:7]}') + ' 这条路')
    notes.append(f'两条通道读到的评论总数：PR {len(pr_comments)} 条 · commit {len(commit_comments)} 条')

    hit = hits(pr_comments if channel == 'pr' else commit_comments, marker)
    other = hits(commit_comments if channel == 'pr' else pr_comments, marker)

    # 自证：一个必然不存在的 marker 必须 0 命中。对照也是 0 的话，那 0 说的是
    # 通道，不是世界。
    impossible = marker + f':attest-selftest-nonexistent:{run_id}'
    ghosts = hits(pr_comments, impossible) + hits(commit_comments, impossible)
    if ghosts:
        problems.append(f'自证失败：一个必然不存在的标记命中了 {len(ghosts)} 条 —— 查找器在乱匹配，'
                        '下面每一条结论都不可信')

    if not hit:
        total = len(pr_comments) if channel == 'pr' else len(commit_comments)
        problems.append(
            f'该出现评论的地方（{channel}）没有找到带这个标记的评论 —— 报告没送达。'
            + (f'那条通道上一共读到 {total} 条评论，所以通道是读得到的，缺的是我们这条。'
               if total else '那条通道上一条评论都没读到 —— 可能是权限，也可能是回写整段没跑。')
            + ' 这正是「闸门全绿却一条评论都没有」的那种失败。')
    if other:
        problems.append(f'评论同时出现在了另一条路上（{"commit" if channel == "pr" else "PR"} 有 '
                        f'{len(other)} 条）—— 分岘逻辑选错了地方，读 {channel} 的人看不到它')
    if len(hit) > 1:
        problems.append(f'带这个标记的评论有 {len(hit)} 条，应该只有 1 条 —— 回写没有更新已有那条，'
                        '而是又贴了一条。刷屏也是一种坏掉，而且是看起来还在工作的那种')

    if hit:
        body = hit[0].get('body') or ''
        # 钉在本次运行上。这两条才是把「幂等写入的陈旧评论」和「这次真的送达了」
        # 分开的东西。
        if sha[:7] not in body:
            problems.append(f'评论正文里没有本次短 SHA `{sha[:7]}` —— 找到的可能是上一次运行留下的陈旧评论')
        if f'/actions/runs/{run_id}' not in body:
            problems.append(f'评论正文里没有本次 run id `{run_id}` —— 同上，这条命中证明不了本次送达')
        if DEGRADED_PHRASE in body:
            problems.append('评论自称是降级报告 —— 送达了，但送出去的是没有逐项证据的兜底那份')
        elif COMPOSER_SENTINEL not in body:
            problems.append('评论里没有 composer 哨兵，而它也没自称降级 —— 说不清送出去的是哪一份，'
                            '这种说不清本身就该红')
        else:
            notes.append('正文带 composer 哨兵、本次短 SHA、本次 run id —— 是这一次的完整报告')
    return problems, notes


# --------------------------------------------------------------------------
# 离线自证。每次都先跑，跑在任何网络调用之前。
# --------------------------------------------------------------------------
def selftest():
    marker = '<!-- m -->'
    sha, run_id = 'deadbeefcafe', '4242'
    good_body = f'{marker}\n{COMPOSER_SENTINEL}\n6/6 · 提交 `{sha[:7]}` · [日志](https://x/actions/runs/{run_id})'
    good = [{'body': good_body}]
    cases = [
        ('好样本必须 0 问题', ([], good, None), 0),
        ('评论不存在必须红', ([], [], None), 1),
        ('贴错通道必须红', (good, [], None), 1),
        ('同一标记两条必须红', ([], good + [{'body': good_body}], None), 1),
        ('陈旧评论（没有本次 SHA）必须红', ([], [{'body': good_body.replace(sha[:7], '0000000')}], None), 1),
        ('陈旧评论（没有本次 run id）必须红', ([], [{'body': good_body.replace(run_id, '1')}], None), 1),
        ('降级报告必须红', ([], [{'body': good_body + f'\n{DEGRADED_PHRASE}'}], None), 1),
        ('没有哨兵必须红', ([], [{'body': good_body.replace(COMPOSER_SENTINEL, '')}], None), 1),
        ('查找器乱匹配必须红', ([], [{'body': good_body + marker + f':attest-selftest-nonexistent:{run_id}'}], None), 1),
    ]
    global SELFTEST_CASE_COUNT
    SELFTEST_CASE_COUNT = len(cases)
    broken = []
    for title, (prc, cc, _), want_min in cases:
        problems, _ = evaluate(marker, sha, run_id, None, prc, cc)
        if want_min == 0 and problems:
            broken.append(f'{title} —— 却报了 {len(problems)} 条：{problems}')
        if want_min == 1 and not problems:
            broken.append(f'{title} —— 却一条都没报，这个检查器是装饰')
    return broken


def api(pathname, token):
    base = os.environ.get('GITHUB_API_URL') or 'https://api.github.com'
    req = urllib.request.Request(base + pathname, headers={
        'authorization': 'Bearer ' + token,
        'accept': 'application/vnd.github+json',
        'x-github-api-version': '2022-11-28',
        'user-agent': 'anyworkflow-attest',
    })
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode('utf-8'))


def main():
    broken = selftest()
    for b in broken:
        print('  x 自证 ' + b)
    if broken:
        print('\n检查器自己的离线用例没过 —— 尺子坏了，这次什么都没验到（不是绿）。')
        return 2
    print(f'  · 检查器离线自证通过（{SELFTEST_CASE_COUNT} 个合成样本，好的绿、坏的各自红）')

    marker = ((json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8')).get('writeback')) or {}).get('marker')
    token = os.environ.get('GH_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    sha = os.environ.get('GITHUB_SHA')
    run_id = os.environ.get('GITHUB_RUN_ID')
    for name, val in [('manifest.writeback.marker', marker), ('GH_TOKEN', token),
                      ('GITHUB_REPOSITORY', repo), ('GITHUB_SHA', sha), ('GITHUB_RUN_ID', run_id)]:
        if not val:
            print(f'缺 {name} —— 前置条件不全，本次没有核对任何东西（不是绿）。')
            return 2

    attempts = 0
    problems, notes = ['还没查过'], []
    try:
        for attempt in range(1, POLL_ATTEMPTS + 1):
            attempts = attempt
            pulls = api(f'/repos/{repo}/commits/{sha}/pulls', token)
            open_pr = next((p for p in pulls if p.get('state') == 'open'), None)
            pr_number = open_pr.get('number') if open_pr else None
            pr_comments = api(f'/repos/{repo}/issues/{pr_number}/comments?per_page=100', token) if pr_number else []
            commit_comments = api(f'/repos/{repo}/commits/{sha}/comments?per_page=100', token)
            problems, notes = evaluate(marker, sha, run_id, pr_number, pr_comments, commit_comments)
            if not problems:
                break
            if attempt < POLL_ATTEMPTS:
                time.sleep(POLL_SLEEP_SECONDS)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as err:
        problems = [f'核对过程本身出错：{err} —— 这次没有验证到送达（不是「没送达」）']

    # 尝试次数要写进报告：「一次就过」和「第八次才过」长得一样，
    # 而上游在慢慢变差的话，只有这个数看得见。
    notes.append(f'标记 {marker}')
    notes.append(f'轮询 {attempts}/{POLL_ATTEMPTS} 次（每次间隔 {POLL_SLEEP_SECONDS}s）')
    for n in notes:
        print('  · ' + n)
    if problems:
        print('\n失败项：')
        for p in problems:
            print('  x ' + p)
        return 1
    print('\n送达核对通过：这一次的完整报告真的贴出来了，而且读得到。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
