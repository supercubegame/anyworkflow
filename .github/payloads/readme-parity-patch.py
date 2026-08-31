import hashlib, json, os, sys

def blob(raw):
    return hashlib.sha1(b'blob %d\x00' % len(raw) + raw).hexdigest()

# Single-escaped file: json.load returns the real strings. No second decode -- that was run #3's
# failure, and its cause was a twin fed a double-escaped lookalike. The generator for this file
# puts RAW strings in and lets json.dumps(ensure_ascii=True) escape them exactly once, and the
# local twin reads these very bytes (blob 8a20e68c), not a re-serialised copy of them.
P = json.load(open('.github/payloads/readme-parity-payloads.json', encoding='ascii'))

TARGET = os.environ.get('TARGET', 'verify.py')
GATE_DOC = 'docs/MINIMAL-GATE.md'
MANIFEST = 'manifest.json'
NEW_ID = 'readme_pair_parity'

CHECK_ANCHOR = "declared_checks = ((manifest.get('checks') or {}).get('verify'))\n"

src = open(TARGET, encoding='utf-8').read()
before = src.encode()
print('target', TARGET, len(before), 'bytes  blob', blob(before))
assert NEW_ID not in src, 'already patched'
assert src.count(CHECK_ANCHOR) == 1, 'check anchor not unique'

out = src.replace(CHECK_ANCHOR, P['NEWCHECK'] + '\n' + CHECK_ANCHOR, 1)
after = out.encode()
assert len(after) > len(before), 'file must grow'

# Pure insertion: nothing may vanish, every original line reappears in order.
a, b = src.split('\n'), out.split('\n')
gone = [l for l in a if l not in b]
assert not gone, 'inserts only; nothing may vanish, but lost: %r' % gone[:4]
i = 0
for line in a:
    while i < len(b) and b[i] != line:
        i += 1
    assert i < len(b), 'original line did not survive in order: %r' % line[:80]
    i += 1
print('lines %d -> %d, pure insertion, all %d survived in order' % (len(a), len(b), len(a)))

# The count check uses len(checks) + 1 and assumes it runs last, so assert the order rather than
# trusting where the anchor happens to sit.
assert out.index("check('" + NEW_ID + "'") < out.index(CHECK_ANCHOR), 'new check must precede the count check'
assert out.count("check('" + NEW_ID + "'") == 1, 'new check id must appear exactly once'
print('CHECK ORDER OK')

# Run the new check on this repo's real READMEs, here, before anything is written. An assertion
# that is red on arrival must never land: it would make the next person's first experience of it
# a failure they did not cause.
ns = {'ROOT': __import__('pathlib').Path('.'), 'check': lambda c, t, o, d: ns.setdefault('_v', (o, d))}
lo = out.index('README_PAIR =')
hi = out.index(CHECK_ANCHOR)
exec('import re\nfrom pathlib import Path\n' + out[lo:hi], ns)
ok, detail = ns['_v']
print('new check on the real READMEs:', 'PASS' if ok else 'FAIL', '|', detail)
assert ok, 'the new check fails on this repo -- refusing to land an assertion that is red on arrival'

# ---- MINIMAL-GATE: three counts plus one new section. Targeted replaces, never a blanket
# 21 -> 22: a global replace would corrupt the historical quote about the old count, and any date.
gsrc = open(GATE_DOC, encoding='utf-8').read()
print('gate doc', len(gsrc.encode()), 'bytes  blob', blob(gsrc.encode()))
pairs = [('heading', P['H_OLD'], P['H_NEW']),
         ('section-note', P['N_OLD'], P['N_NEW']),
         ('closing', P['T_OLD'], P['T_NEW'])]
for nm, o, n in pairs:
    c = gsrc.count(o)
    assert c == 1, 'gate %s anchor appears %d times, expected 1' % (nm, c)
gout = gsrc
for nm, o, n in pairs:
    gout = gout.replace(o, n, 1)
ANCH = P['ANCHOR']
assert gout.count(ANCH) == 1, 'gate section anchor not unique'
gout = gout.replace(ANCH, ANCH + '\n\n' + P['SECT'].rstrip('\n'), 1)
assert '### 19.' in gout, 'new section heading missing'
assert P['H_OLD'] not in gout and P['T_OLD'] not in gout
ga, gbl = gsrc.split('\n'), gout.split('\n')
lost = [l for l in ga if l not in gbl]
olds = [o for _n, o, _x in pairs]
assert len(lost) == 3, 'expected exactly 3 rewritten gate-doc lines, got %d: %r' % (len(lost), lost[:4])
for l in lost:
    assert any(o in l for o in olds), 'a gate doc line vanished that was not one of the three: %r' % l[:90]
kept = [l for l in ga if l in gbl]
j = 0
for line in kept:
    while j < len(gbl) and gbl[j] != line:
        j += 1
    assert j < len(gbl), 'gate doc line did not survive in order: %r' % line[:80]
    j += 1
print('gate doc lines %d -> %d, exactly 3 rewritten, %d kept in order' % (len(ga), len(gbl), len(kept)))
assert '20 \u4ef6\u4e8b' in gout, 'the historical quote about the old count was destroyed'
print('historical quote intact')

if '--check' in sys.argv:
    print('check only, not writing'); sys.exit(0)

open(TARGET, 'w', encoding='utf-8').write(out)
open(GATE_DOC, 'w', encoding='utf-8').write(gout)
print('verify.py ->', len(after), 'bytes blob', blob(after))
print('gate doc  ->', len(gout.encode()), 'bytes blob', blob(gout.encode()))

# Full readback -> targeted mutation -> whole-file reserialize. A 40-hex digit is never typed.
raw = open(MANIFEST, encoding='utf-8').read()
obj = json.loads(raw)
inv = obj['invariants']
assert NEW_ID not in inv
items = list(inv.items())
at = [k for k, _v in items].index('consumer_set_self_derived')
obj['invariants'] = dict(items[:at + 1] + [(NEW_ID, True)] + items[at + 1:])
old_n = obj['checks']['verify']
assert old_n == 21, 'expected checks.verify 21, found %r' % old_n
obj['checks']['verify'] = old_n + 1
reg = obj['docs_integrity']
touched = {}
for rel in (TARGET, GATE_DOC):
    assert rel in reg, '%s is not registered' % rel
    o, n = reg[rel], blob(open(rel, 'rb').read())
    assert o != n
    reg[rel] = n
    touched[rel] = (o, n)
outm = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
a2, b2 = json.loads(raw), json.loads(outm)
assert a2.keys() == b2.keys()
for k in a2:
    if k not in ('invariants', 'checks', 'docs_integrity'):
        assert a2[k] == b2[k], 'unrelated key changed: %s' % k
assert set(b2['invariants']) - set(a2['invariants']) == {NEW_ID}
assert set(a2['docs_integrity']) == set(b2['docs_integrity'])
diff = [k for k in a2['docs_integrity'] if a2['docs_integrity'][k] != b2['docs_integrity'][k]]
assert sorted(diff) == sorted(touched), 'unexpected hash changes: %r' % diff
open(MANIFEST, 'w', encoding='utf-8').write(outm)
for rel, (o, n) in sorted(touched.items()):
    print('refreshed %-24s %s -> %s' % (rel, o[:12], n[:12]))
print('checks.verify %d -> %d, invariants +%s, HASHES REFRESHED, EXACTLY 2' % (old_n, old_n + 1, NEW_ID))
