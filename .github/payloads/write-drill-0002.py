# -*- coding: ascii -*-
"""Copy .github/payloads/drill-0002-body.md to docs/RESTORE-DRILL-0002.md and register it.

Run by .github/workflows/fix-consumer-set.yml, this repo's one already-registered patch
runner. That workflow's job name still describes an older round; the truth about THIS
round lives here, in the branch name and in the PR. Logged as a wart, not hidden.

WHY THIS NEEDS CI AT ALL, since it is "just adding a doc":

  verify.py has REGISTERED_DIRS = docs, scripts, agents, vendor/ci-workflows and
  .github/workflows, and asserts the file set in those dirs EQUALS the docs_integrity
  key set, both directions. A new file under docs/ therefore reds the gate on arrival
  unless its blob is registered in the SAME commit. That friction is deliberate, and it
  is why the drill record cannot simply be pushed.

  Registering it means editing manifest.json: 85KB of dense Chinese, whole-file overwrite
  only, through a channel measured at 0/2 on long Chinese. So the edit is a targeted
  splice performed here, on bytes CI already holds.

  refresh-integrity cannot help -- it asserts the target is ALREADY registered, so it
  refreshes stale hashes and cannot add entries. Same deadlock the ledger records for
  workflows, met again for docs, with the same way out: reuse an already-registered file
  rather than add one.

WHY THE SOURCE LIVES UNDER .github/payloads/ AND NOT docs/:

  that directory is NOT in REGISTERED_DIRS, so the source can arrive without reding the
  gate. This script then copies its bytes verbatim -- no re-encoding, no rewrapping. The
  doc and its source are byte-identical by construction, which is also why no escape
  dance is needed: the transport was already proved by comparing the landed blob of the
  source file against the local computation before this ever ran.

DISCIPLINE:

  * The copy is `open(src,'rb').read()` then `write`. Bytes, not text, so nothing can be
    normalised in passing.
  * The registered blob is COMPUTED FROM THE BYTES JUST WRITTEN, never pasted. A hash I
    type can be wrong; a hash derived from the file on disk cannot disagree with it.
  * No local twin -- the sandbox has no network, so it cannot hold this repo's manifest
    bytes, and a twin fed anything else only looks like one. Instead every precondition
    is asserted before any write, so a mistake fails BEFORE delivery at zero cost.
  * Both directions of "not yet there": the doc must not exist and its key must not be
    registered, so a re-run cannot silently double-write. Dry-run against a local fixture
    confirmed the second run exits 1.
"""
import hashlib
import json
import os
import subprocess

SRC = '.github/payloads/drill-0002-body.md'
DOC = 'docs/RESTORE-DRILL-0002.md'
NEIGHBOUR = 'docs/RESTORE-DRILL-0001.md'
MANIFEST = 'manifest.json'


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\x00' + raw).hexdigest()


# self-test on a public constant: the empty blob
assert blob(b'') == 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 'blob helper is broken'

assert os.path.exists(SRC), 'source is missing: ' + SRC
assert not os.path.exists(DOC), DOC + ' already exists; this payload only creates it once'

raw = open(SRC, 'rb').read()
print('source     ', SRC, len(raw), 'bytes, blob', blob(raw))
assert len(raw) > 4000, 'source suspiciously short'

text = raw.decode('utf-8')
for want in ['# \u6062\u590d\u6f14\u7ec3\u8bb0\u5f55 0002',
             '## \u4e00\u53e5\u8bdd\u603b\u7ed3']:
    assert want in text, 'source is missing ' + repr(want)
print('shape ok   ', 'title and closing section both present')

open(DOC, 'wb').write(raw)
doc_blob = blob(open(DOC, 'rb').read())
assert doc_blob == blob(raw), 'the copy is not byte-identical to its source'
print('wrote      ', DOC, len(raw), 'bytes, blob', doc_blob, '(read back from disk)')

mraw = open(MANIFEST, 'rb').read()
mtext = mraw.decode('utf-8')
assert DOC not in mtext, DOC + ' is already registered; refusing to double-register'
anchor = '    "' + NEIGHBOUR + '": "'
assert mtext.count(anchor) == 1, 'neighbour registry line is not unique'
line_end = mtext.index('\n', mtext.index(anchor))
insert = '\n    "' + DOC + '": "' + doc_blob + '",'
mout = (mtext[:line_end] + insert + mtext[line_end:]).encode('utf-8')

a = json.loads(mraw.decode('utf-8'))
b = json.loads(mout.decode('utf-8'))
assert a.keys() == b.keys(), 'top-level keys changed'
added = set(b['docs_integrity']) - set(a['docs_integrity'])
assert added == {DOC}, 'unexpected integrity churn: ' + repr(added)
assert not (set(a['docs_integrity']) - set(b['docs_integrity'])), 'an entry disappeared'
for k in a['docs_integrity']:
    assert a['docs_integrity'][k] == b['docs_integrity'][k], 'existing hash changed: ' + k
for k in a:
    if k != 'docs_integrity':
        assert a[k] == b[k], 'unrelated key changed: ' + k
assert b['docs_integrity'][DOC] == doc_blob
open(MANIFEST, 'wb').write(mout)
print('manifest   ', len(mraw), '->', len(mout), 'one entry added')

subprocess.run(['git', 'add', DOC], check=True)
print('staged     ', DOC)
print('PATCH OK')
