# -*- coding: ascii -*-
"""Narrow the last two over-broad sentences in docs/RECOVERY-CHECKLIST.md, then refresh its hash.

Second round of the same shape as fix-checklist-claims.py, and deliberately a separate round: the
previous PR found these two while reading its own result, and folding them in would have blurred
which half of that diff landed. Debt written into the PR body then, paid here.

  1. "so these six items can only be ticked by rebuilding" -- the list above it is eight items
     since the reshard. The number was corrected in one place and not in the other, which is the
     exact failure the file itself keeps logging: prose drifts and nothing goes red.
  2. "ClickUp has no skill export or import" -- too broad in the same way the blob-hash sentence
     was. There is no export entry point in the UI, which is true and stays. But the sandbox pair
     skill clone / skill save IS a read-write channel: clone is byte-exact, save is bounded by the
     12000-character body limit. Calling the whole thing nonexistent is what retires a road that
     works, and this ledger has now recorded that shape five times. What is genuinely untested is
     the cross-account hop, so the sentence now says that instead.

Same discipline as round one, for the same reasons:

  * Chinese arrives as ascii escapes and is decoded here, so no Han character crosses the channel
    that drifts. The escapes were read back and eyeballed once via a lone-Han scan over the 101
    new Han characters; nothing was flagged this time.
  * No local twin: the sandbox has no network, so it cannot hold the production bytes, and a twin
    fed anything else only looks like one. The input blob is asserted first and every old string
    must occur exactly once, so a typo fails BEFORE delivery at zero cost.
  * Old strings were chosen to avoid the comma-shaped characters elsewhere in this file, because
    the read channel normalises some of them and an old_string that went through it can silently
    stop matching. Refusing to match is the correct failure here, but it is cheaper to dodge.
"""
import hashlib
import json
import subprocess

DOC = 'docs/RECOVERY-CHECKLIST.md'
MANIFEST = 'manifest.json'
DOC_BLOB_BEFORE = '91f84d4270bbba08c48230e8be33c651bd6ff4e5'


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\x00' + raw).hexdigest()


# self-test on a public constant: the empty blob
assert blob(b'') == 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 'blob helper is broken'

PAIRS = [
    ("\u8fd9\u516d\u9879\u53ea\u80fd\u9760\u91cd\u5efa\u6253\u52fe",
     "\u8fd9\u516b\u9879\u53ea\u80fd\u9760\u91cd\u5efa\u6253\u52fe"),
    ("ClickUp \u6ca1\u6709\u6280\u80fd\u7684\u5bfc\u51fa\u6216\u5bfc\u5165\u529f\u80fd"
        "\uff08\u622a\u81f3 2026-09-01 \u5728\u5b98\u65b9\u6587\u6863\u91cc\u6ca1\u627e\u5230\uff09",
     "ClickUp \u7684\u754c\u9762\u91cc\u6ca1\u6709\u6280\u80fd\u7684\u5bfc\u51fa\u6216"
        "\u5bfc\u5165\u5165\u53e3\uff08\u622a\u81f3 2026-09-01 \u5728\u5b98\u65b9\u6587\u6863"
        "\u91cc\u6ca1\u627e\u5230\uff09\uff0c**\u800c\u300c\u754c\u9762\u6ca1\u6709\u5165\u53e3"
        "\u300d\u4e0d\u7b49\u4e8e\u300c\u6ca1\u6709\u901a\u9053\u300d**\uff1a2026-09-02 "
        "\u5b9e\u6d4b\u6c99\u7bb1\u91cc\u7684 `skill clone` \u80fd\u628a\u7ebf\u4e0a\u6280\u80fd"
        "\u62c9\u6210\u672c\u5730\u6587\u4ef6\u3001`skill save` \u80fd\u955c\u50cf\u5199\u56de"
        "\uff0cclone \u4fa7\u9010\u5b57\u8282\u7cbe\u786e\uff0csave \u4fa7\u53d7 12000 "
        "\u5b57\u7b26\u4e0a\u9650\u7ea6\u675f\u3002\u771f\u6b63\u6ca1\u9a8c\u8fc7\u7684\u662f"
        "**\u8de8\u8d26\u53f7**\u90a3\u4e00\u6b65"),
]

raw = open(DOC, 'rb').read()
print('doc bytes  ', len(raw))
print('doc blob   ', blob(raw))
assert blob(raw) == DOC_BLOB_BEFORE, 'input is not the registered baseline; refusing to edit'

text = raw.decode('utf-8')
before = text

for old, new in PAIRS:
    n = text.count(old)
    assert n == 1, 'expected exactly 1 hit, found ' + str(n) + ' for: ' + repr(old[:40])
    line = text[:text.index(old)].count('\n') + 1
    print('hit line', line, 'elsewhere', n - 1, '  ', old[:36])
    text = text.replace(old, new, 1)
    assert new in text, 'replacement did not land'
    assert text.count(old) == 0, 'old text survived'

assert text != before, 'nothing changed'

# the point of round two: the stale six must be gone from this file, and the eight-item list
# above it must still say eight. Both sides, so a fix in one place cannot look complete alone.
assert '\u516b\u9879\u53ea\u80fd\u9760\u91cd\u5efa' in text, 'the corrected count is missing'
assert '\u6280\u80fd\u6b63\u6587\uff0c\u516b\u4efd' in text, 'the list header no longer says eight'

out = text.encode('utf-8')
open(DOC, 'wb').write(out)
new_blob = blob(out)
print('new bytes  ', len(out), 'delta', len(out) - len(raw))
print('new blob   ', new_blob)
assert new_blob != DOC_BLOB_BEFORE, 'bytes changed but blob did not'

# refresh the one registered hash by targeted replacement, not by reserialising the manifest
mraw = open(MANIFEST, 'rb').read()
mtext = mraw.decode('utf-8')
key = '"' + DOC + '": "' + DOC_BLOB_BEFORE + '"'
assert mtext.count(DOC_BLOB_BEFORE) == 1, 'old hash is not unique in the manifest'
assert mtext.count(key) == 1, 'registry line is not in its expected shape'
mtext = mtext.replace(key, '"' + DOC + '": "' + new_blob + '"', 1)
mout = mtext.encode('utf-8')

a = json.loads(mraw.decode('utf-8'))
b = json.loads(mtext)
assert a.keys() == b.keys(), 'top-level keys changed'
churn = [k for k in a['docs_integrity'] if a['docs_integrity'][k] != b['docs_integrity'][k]]
assert churn == [DOC], 'unexpected integrity churn: ' + repr(churn)
for k in a:
    if k != 'docs_integrity':
        assert a[k] == b[k], 'unrelated key changed: ' + k
assert len(mout) == len(mraw), 'a hash swap must not change the manifest length'
open(MANIFEST, 'wb').write(mout)
print('manifest   ', len(mraw), '->', len(mout), 'blob', blob(mout))

subprocess.run(['git', 'add', DOC], check=True)
print('staged     ', DOC)
print('PATCH OK')
