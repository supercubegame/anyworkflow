import hashlib, json, os, sys

def blob(raw):
    return hashlib.sha1(b'blob %d\x00' % len(raw) + raw).hexdigest()

def dec(s):
    return json.loads('"' + s + '"')

TARGET = os.environ.get('TARGET', 'verify.py')
DOC = 'docs/SHARED-WRITEBACK-CONSUMERS.md'
GATE_DOC = 'docs/MINIMAL-GATE.md'
MANIFEST = 'manifest.json'
NEW_ID = 'consumer_set_self_derived'

P = json.load(open('.github/payloads/self-derive-payloads.json', encoding='ascii'))
NEWCHECK = dec(P['NEWCHECK'])
SECT = dec(P['SECT'])

# ---- verify.py: three pure insertions, each anchored on a line that is unique in the file
DICT_ANCHOR = "    'crossyroad': ['verify.yml'],\n"
DICT_ADD = "    'anyworkflow': ['verify.yml'],\n"
PROSE_ANCHOR = ("        ' home repo, which is the third time this list was wrong in the same direction.',\n")
PROSE_ADD = ("        'Read 2026-08-31 again, hours later: anyworkflow itself calls the shared writeback from its'\n"
             "        ' own verify.yml, and this dict had never listed it -- the fourth error, and the one where'\n"
             "        ' the list omitted the repo it lives in. That entry is now derived from the real files on'\n"
             "        ' disk, so it is the only truly derived line here; the other six repos are still hand-written'\n"
             "        ' because deriving them needs a cross-repo token.',\n")
CHECK_ANCHOR = "declared_checks = ((manifest.get('checks') or {}).get('verify'))\n"

src = open(TARGET, encoding='utf-8').read()
before = src.encode()
print('target', TARGET, len(before), 'bytes  blob', blob(before))

assert NEW_ID not in src, 'already patched: %s present' % NEW_ID
assert "'anyworkflow'" not in src, "already lists anyworkflow"
for nm, a in (('dict', DICT_ANCHOR), ('prose', PROSE_ANCHOR), ('check', CHECK_ANCHOR)):
    n = src.count(a)
    assert n == 1, '%s anchor appears %d times, expected 1' % (nm, n)

out = src.replace(DICT_ANCHOR, DICT_ANCHOR + DICT_ADD, 1)
out = out.replace(PROSE_ANCHOR, PROSE_ANCHOR + PROSE_ADD, 1)
out = out.replace(CHECK_ANCHOR, NEWCHECK + '\n' + CHECK_ANCHOR, 1)
after = out.encode()
assert len(after) > len(before), 'file must grow'

# This patch inserts only. Nothing may vanish, and every original line must reappear in order.
# "Most lines survived" is how a guard quietly stops guarding.
a, b = src.split('\n'), out.split('\n')
gone = [l for l in a if l not in b]
assert not gone, 'this patch inserts only; nothing may vanish, but lost: %r' % gone[:4]
i = 0
for line in a:
    while i < len(b) and b[i] != line:
        i += 1
    assert i < len(b), 'original line did not survive in order: %r' % line[:80]
    i += 1
print('lines %d -> %d, pure insertion, all %d original lines survived in order' % (len(a), len(b), len(a)))

# The count check uses len(checks) + 1, which assumes it runs last. A new check landing after it
# would silently break that offset, so assert the order rather than trusting where the anchor is.
assert out.index("check('" + NEW_ID + "'") < out.index(CHECK_ANCHOR), 'new check must precede the count check'
assert out.count("check('" + NEW_ID + "'") == 1, 'new check id must appear exactly once'
print('CHECK ORDER OK: new check precedes checks_count_equals')

# ---- render the doc with the PATCHED file's own renderer, never a second copy of it
lo = out.index('CONSUMER_FILES = {')
hi = out.index("    return '\\n'.join(lines).rstrip() + '\\n'\n", lo)
hi += len("    return '\\n'.join(lines).rstrip() + '\\n'\n")
sl = '\n'.join(l for l in out[lo:hi].split('\n') if 'consumer_path' not in l)
ns = {}
exec(sl, ns)
doc = ns['render_consumers']()
repos, wfs = ns['expected_repo_count'], ns['expected_workflow_count']
print('rendered doc: %d repos / %d workflows' % (repos, wfs))
assert (repos, wfs) == (7, 15), 'expected 7 repos / 15 workflows, got %d / %d' % (repos, wfs)
assert ns['CONSUMER_FILES']['anyworkflow'] == ['verify.yml']
assert '## anyworkflow' in doc, 'anyworkflow section missing from the rendered doc'
# Predicted before this ran, by a local twin of this renderer that first reproduced the CURRENT
# doc byte for byte (blob 19b180f3). Ruler proven, then used. Two witnesses, not one.
EXPECT_DOC_BLOB = '0582e38dcfd7f1198c7bfcb2e576dd34feae1bda'
EXPECT_DOC_BYTES = 2159
gb2, bz2 = blob(doc.encode()), len(doc.encode())
print('doc bytes %d (expected %d) blob %s (expected %s)' % (bz2, EXPECT_DOC_BYTES, gb2, EXPECT_DOC_BLOB))
assert (gb2, bz2) == (EXPECT_DOC_BLOB, EXPECT_DOC_BYTES), 'the rendered doc is not the one that was predicted'

# ---- MINIMAL-GATE: three counts, plus one new section. Targeted replaces, because a blanket
# 20 -> 21 would corrupt every date containing 20 (2026-08-26 and friends).
gsrc = open(GATE_DOC, encoding='utf-8').read()
gb = gsrc.encode()
print('gate doc', len(gb), 'bytes  blob', blob(gb))
pairs = [('heading', dec(P['H_OLD']), dec(P['H_NEW'])),
         ('section-note', dec(P['N_OLD']), dec(P['N_NEW'])),
         ('closing', dec(P['T_OLD']), dec(P['T_NEW']))]
for nm, o, n in pairs:
    c = gsrc.count(o)
    assert c == 1, 'gate %s anchor appears %d times, expected 1' % (nm, c)
gout = gsrc
for nm, o, n in pairs:
    gout = gout.replace(o, n, 1)
ANCH = dec(P['ANCHOR'])
assert gout.count(ANCH) == 1, 'gate section anchor not unique'
gout = gout.replace(ANCH, ANCH + '\n\n' + SECT.rstrip('\n'), 1)
assert gout.count(dec(P['H_NEW'])) == 1 and gout.count(dec(P['T_NEW'])) == 1
assert dec(P['H_OLD']) not in gout and dec(P['T_OLD']) not in gout
assert '### 18.' in gout, 'new section heading missing'
ga, gbl = gsrc.split('\n'), gout.split('\n')
lost = [l for l in ga if l not in gbl]
olds = [o for _nm, o, _n in pairs]
assert len(lost) == 3, 'expected exactly 3 rewritten lines in the gate doc, got %d: %r' % (len(lost), lost[:4])
for l in lost:
    assert any(o in l for o in olds), 'a gate doc line vanished that was not one of the three rewrites: %r' % l[:90]
kept = [l for l in ga if l in gbl]
j = 0
for line in kept:
    while j < len(gbl) and gbl[j] != line:
        j += 1
    assert j < len(gbl), 'gate doc line did not survive in order: %r' % line[:80]
    j += 1
print('gate doc lines %d -> %d, exactly 3 rewritten, %d kept in order' % (len(ga), len(gbl), len(kept)))

if '--check' in sys.argv:
    print('check only, not writing'); sys.exit(0)

open(TARGET, 'w', encoding='utf-8').write(out)
open(DOC, 'w', encoding='utf-8').write(doc)
open(GATE_DOC, 'w', encoding='utf-8').write(gout)
print('verify.py  ->', len(after), 'bytes blob', blob(after))
print('doc        ->', len(doc.encode()), 'bytes blob', blob(doc.encode()))
print('gate doc   ->', len(gout.encode()), 'bytes blob', blob(gout.encode()))

# ---- manifest: register the new invariant, bump the count, refresh exactly three hashes.
# Full readback -> targeted mutation -> whole-file reserialize. A 40-hex digit is never typed.
raw = open(MANIFEST, encoding='utf-8').read()
obj = json.loads(raw)
inv = obj['invariants']
assert NEW_ID not in inv, 'invariant already registered'
items = list(inv.items())
at = [k for k, _v in items].index('shared_writeback_consumers_generated')
obj['invariants'] = dict(items[:at + 1] + [(NEW_ID, True)] + items[at + 1:])
old_n = obj['checks']['verify']
assert old_n == 20, 'expected checks.verify 20, found %r' % old_n
obj['checks']['verify'] = old_n + 1
reg = obj['docs_integrity']
touched = {}
for rel in (TARGET, DOC, GATE_DOC):
    assert rel in reg, '%s is not registered, refusing to invent an entry' % rel
    o, n = reg[rel], blob(open(rel, 'rb').read())
    assert o != n, '%s hash did not change' % rel
    reg[rel] = n
    touched[rel] = (o, n)
outm = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'
a2, b2 = json.loads(raw), json.loads(outm)
assert a2.keys() == b2.keys(), 'top-level keys changed'
for k in a2:
    if k not in ('invariants', 'checks', 'docs_integrity'):
        assert a2[k] == b2[k], 'unrelated key changed: %s' % k
assert set(b2['invariants']) - set(a2['invariants']) == {NEW_ID}
assert set(a2['invariants']) - set(b2['invariants']) == set()
assert set(a2['docs_integrity']) == set(b2['docs_integrity']), 'registry key set changed'
diff = [k for k in a2['docs_integrity'] if a2['docs_integrity'][k] != b2['docs_integrity'][k]]
assert sorted(diff) == sorted(touched), 'unexpected hash changes: %r' % diff
open(MANIFEST, 'w', encoding='utf-8').write(outm)
for rel, (o, n) in sorted(touched.items()):
    print('refreshed %-42s %s -> %s' % (rel, o[:12], n[:12]))
print('checks.verify %d -> %d, invariants +%s, HASHES REFRESHED, EXACTLY 3' % (old_n, old_n + 1, NEW_ID))
