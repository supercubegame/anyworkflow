#!/usr/bin/env python3
"""Fix one wrong number inside one _tested_limits entry, and refresh the hash of the
workflow that runs this script.

Why a patcher and not a hand edit: manifest.json is 76KB, and this repo has already
proved that rewriting a file that size by hand silently drops things -- four collections
were once emptied by a rewrite that meant to add a bracket. So the rule is: read the full
file, mutate one field programmatically, reserialize, then blob-prove the landed bytes.

Why a patcher and not an append: the wrong number is *inside* an entry whose whole subject
is not trusting unmeasured numbers. Appending a correction would leave the false sentence
in place, and a reader who stops at the first mention gets the wrong fact.

What was wrong: the entry said the live pipeline skill body in the backup repo is 59677
bytes. That was read off skills/agent-self-verification-pipeline.md, which is a *build
artifact* -- the merger overwrites it from five shards before the gate audits it, so no
assertion has ever read those bytes in either direction. The shards total 61181. The stale
file has since been untracked (backup repo PR #93).
"""
import hashlib
import json
import os
import sys

MANIFEST = 'manifest.json'
WORKFLOW = '.github/workflows/fix-consumer-set.yml'

OLD = '\u771f\u8eab\u90a3\u4e00\u4efd\u5728\u5907\u4efd\u4ed3\u91cc\u662f 59677 \u5b57\u8282\u3002'
NEW = ('\u771f\u8eab\u90a3\u4e00\u4efd\u5728\u5907\u4efd\u4ed3\u91cc\u662f\u4e94\u4e2a\u5206\u7247\uff0c'
       '\u5408\u8d77\u6765 61181 \u5b57\u8282,\u800c\u6211\u5f53\u65f6\u5199\u7684 59677 '
       '\u53d6\u81ea\u4e00\u4efd\u62c6\u5206\u524d\u7684\u6784\u5efa\u4ea7\u7269\uff1a'
       '\u5b83\u88ab git \u8ffd\u8e2a\u7740\uff0c\u5374\u4ece\u6765\u6ca1\u6709\u4efb\u4f55'
       '\u95f8\u95e8\u8bfb\u8fc7\u5b83\uff08\u5408\u5e76\u5668\u6392\u5728 verify '
       '\u4e4b\u524d\uff0c\u65e0\u6761\u4ef6\u8986\u5199\u90a3\u4e2a\u8def\u5f84\uff09\u3002'
       '\u90a3\u4efd\u6b8b\u7559\u5df2\u7ecf\u6458\u6389\uff0c\u89c1\u5907\u4efd\u4ed3 PR #93\u3002'
       '**\u4e00\u4e2a\u6ca1\u6709\u4efb\u4f55\u65ad\u8a00\u8bfb\u8fc7\u7684\u6587\u4ef6\uff0c'
       '\u9a97\u7684\u53ea\u6709\u4eba\u3002**')


def blob(raw):
    return hashlib.sha1(b'blob %d\x00' % len(raw) + raw).hexdigest()


def patch_entries(entries, old, new):
    """Return (new_entries, index). Refuses anything but exactly one hit, in exactly one
    entry. Cut the section first, then look inside it -- the same rule this repo has now
    broken seven times by scanning a whole file for a substring that lives elsewhere.
    """
    hits = [i for i, e in enumerate(entries) if old in e]
    if len(hits) != 1:
        raise AssertionError('the old sentence sits in %d entries, expected exactly 1' % len(hits))
    i = hits[0]
    n = entries[i].count(old)
    if n != 1:
        raise AssertionError('entry %d holds the old sentence %d times, expected 1' % (i, n))
    if new in entries[i]:
        raise AssertionError('entry %d already carries the new sentence -- already patched')
    out = list(entries)
    out[i] = entries[i].replace(old, new, 1)
    return out, i


def selfproof():
    """Prove the replacer refuses the two ways it could quietly do the wrong thing.
    A replacer that cannot be shown to refuse is indistinguishable from one that patches
    whatever it happens to find.
    """
    results = []
    cases = [
        ('absent', ['nothing here', 'nor here']),
        ('twice in one entry', ['x %s y %s z' % (OLD, OLD)]),
        ('in two entries', ['a %s' % OLD, 'b %s' % OLD]),
    ]
    for name, fixture in cases:
        try:
            patch_entries(fixture, OLD, NEW)
            results.append((name, False, 'it accepted a fixture it must refuse'))
        except AssertionError as e:
            results.append((name, True, str(e)))
    good = ['untouched', 'lead %s tail' % OLD, 'also untouched']
    try:
        out, idx = patch_entries(good, OLD, NEW)
        ok = (idx == 1 and out[0] == good[0] and out[2] == good[2]
              and out[1] == 'lead %s tail' % NEW)
        results.append(('positive control', ok, 'index=%d' % idx))
    except AssertionError as e:
        results.append(('positive control', False, str(e)))
    return results


def main():
    bad = 0
    for name, ok, detail in selfproof():
        print('%s selfproof: %-20s | %s' % ('PASS' if ok else 'FAIL', name, detail))
        if not ok:
            bad += 1
    if bad:
        print('the replacer failed its own self-proof -- it judges nothing until this is green')
        return 1

    raw = open(MANIFEST, encoding='utf-8').read()
    before = raw.encode()
    print('manifest bytes', len(before))
    print('manifest blob ', blob(before))

    obj = json.loads(raw)
    entries = obj['_tested_limits']
    n_before = len(entries)
    patched, idx = patch_entries(entries, OLD, NEW)
    obj['_tested_limits'] = patched

    wf_bytes = open(WORKFLOW, 'rb').read()
    wf_blob = blob(wf_bytes)
    integrity = obj['docs_integrity']
    if WORKFLOW not in integrity:
        print('FAIL %s is not in docs_integrity -- refusing to invent a registry line' % WORKFLOW)
        return 1
    was = integrity[WORKFLOW]
    integrity[WORKFLOW] = wf_blob
    print('workflow bytes', len(wf_bytes))
    print('workflow blob ', was[:12], '->', wf_blob[:12], '(unchanged)' if was == wf_blob else '')

    out = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
    after = out.encode()

    a, b = json.loads(raw), json.loads(out)
    assert a.keys() == b.keys(), 'top-level keys changed'
    assert len(b['_tested_limits']) == n_before, 'entry count changed'
    for i, (x, y) in enumerate(zip(a['_tested_limits'], b['_tested_limits'])):
        if i == idx:
            assert y == x.replace(OLD, NEW, 1), 'target entry changed beyond the one sentence'
        else:
            assert x == y, 'entry %d was altered and must not have been' % i
    for k in a:
        if k not in ('_tested_limits', 'docs_integrity'):
            assert a[k] == b[k], 'unrelated key changed: %s' % k
    ai, bi = a['docs_integrity'], b['docs_integrity']
    assert ai.keys() == bi.keys(), 'docs_integrity key set changed'
    drifted = sorted(k for k in ai if ai[k] != bi[k])
    assert drifted in ([], [WORKFLOW]), 'unexpected hash refreshes: %r' % drifted
    assert OLD not in b['_tested_limits'][idx], 'the old sentence survived'
    assert NEW in b['_tested_limits'][idx], 'the new sentence is not there'

    predicted = len(before) + (len(NEW.encode()) - len(OLD.encode()))
    print('entry %d: %d -> %d bytes' % (idx, len(entries[idx].encode()), len(patched[idx].encode())))
    print('sentence delta +%d' % (len(NEW.encode()) - len(OLD.encode())))
    print('predicted total', predicted)
    print('actual total   ', len(after))
    if predicted != len(after):
        print('PREDICTION MISSED by %d -- read that gap, do not explain it away'
              % (len(after) - predicted))
        return 1
    print('new blob ', blob(after))
    print('hashes refreshed:', drifted or 'none needed')

    if '--check' in sys.argv:
        print('check only, not writing')
        return 0
    open(MANIFEST, 'w', encoding='utf-8').write(out)
    print('written')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
