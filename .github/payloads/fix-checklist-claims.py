# -*- coding: ascii -*-
"""Point-fix six stale claims in docs/RECOVERY-CHECKLIST.md, then refresh its registered hash.

Run by .github/workflows/fix-consumer-set.yml, this repo's one already-registered patch runner.
That workflow's job name and commit message still describe an older round (tested limit 32); the
truth about THIS round lives in this file, in the branch name and in the PR. Logged as a wart
rather than pretended away: editing the workflow would make its own registered hash stale, and
there is no way to land that without a red main first.

Every Chinese byte below is an ascii escape sequence, decoded here in CI. The escapes were
generated from text that was read back and eyeballed once: a lone-Han scan over the 206 new Han
characters, which caught exactly one confusable and fixed it (0x6491 -> 0x649E).

What is wrong today, and why each fix is safe:

  1. "the parent has four subskills" -- today's live load unlocks five.
  2. "skill bodies, six" -- the backup repo's skills/ now holds the parent plus seven files.
  3. gate-pitfalls-archive was 23565 -- it is 23679 since the archive sync (backup PR #94), and
     the two skills born from the reshard were never listed at all.
  4. the parent body was 61181 -- after the reshard its five shards total 26121.
  5. "ceiling 65536, only 4355 left" -- the real wall is skill check's 12000-character body
     limit, which the 25065-character pre-split parent hit. 65536 never bound anything.
  6. "never compare skill bodies by blob hash" -- true of the task read-back channel, false of
     the sandbox skill clone channel, which is byte-exact. The claim was wider than the
     measurement, and a claim wider than the fact retires a road that actually works.

Discipline notes:

  * There is no local twin. The sandbox has no network, so it cannot hold the production bytes,
    and a twin fed anything else is not a twin, it only looks like one. Instead this script
    asserts the input blob up front and requires every old string to occur exactly once. A typo
    on my side therefore fails BEFORE delivery, which costs nothing.
  * Each hit prints its line number and how many other copies of that string live elsewhere in
    the file, so a surprise third occurrence names itself instead of being guessed at.
  * The doc is staged from here (git add). The workflow's commit step commits the index, so the
    patched doc rides along without editing the workflow.
"""
import hashlib
import json
import subprocess

DOC = 'docs/RECOVERY-CHECKLIST.md'
MANIFEST = 'manifest.json'
DOC_BLOB_BEFORE = 'af72ebc2f9d22f151260a66b023c9142840ffea6'


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\x00' + raw).hexdigest()


# self-test on a public constant: the empty blob
assert blob(b'') == 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 'blob helper is broken'

PAIRS = [
 # 1. subskill count: today's live load unlocked exactly five children
 ("\u7236\u6280\u80fd\u6709\u56db\u4e2a\u5b50\u6280\u80fd",
  "\u7236\u6280\u80fd\u6709\u4e94\u4e2a\u5b50\u6280\u80fd"),
 # 2. body count: parent + seven files under skills/
 ("\u6280\u80fd\u6b63\u6587\uff0c\u516d\u4efd",
  "\u6280\u80fd\u6b63\u6587\uff0c\u516b\u4efd"),
    ("- [ ] `gate-pitfalls-archive`\uff0823565\uff09",
     "- [ ] `gate-pitfalls-archive`\uff0823679\uff09\n"
        "- [ ] `assertion-craft`\uff0822292\uff09\n"
        "- [ ] `gate-shapes`\uff0813357\uff09"),
    ("\u5408\u8d77\u6765 61181 \u5b57\u8282",
     "\u5408\u8d77\u6765 26121 \u5b57\u8282"),
    ("\u7236\u6280\u80fd 61181 \u5b57\u8282\u800c\u5929\u82b1\u677f 65536\uff0c"
        "\u4f59\u91cf\u53ea\u5269 4355\uff0c\u800c\u7c98\u8d34\u957f\u4e2d\u6587\u662f"
        "\u767b\u8bb0\u5728\u6848\u7684\u9ad8\u5371\u52a8\u4f5c\u3002",
     "\u800c\u771f\u6b63\u7684\u5899\u4e0d\u662f 65536\uff0c\u662f `skill check` "
        "\u7684\u6b63\u6587 12000 \u5b57\u7b26\uff1a\u62c6\u5206\u524d\u7684\u7236\u6280\u80fd "
        "25065 \u5b57\u7b26\u649e\u7684\u5c31\u662f\u5b83\uff0c\u6240\u4ee5\u5f53\u65f6"
        "\u8fde\u8865\u4e00\u53e5\u8bdd\u90fd\u6539\u4e0d\u52a8\u3002\u62c6\u5206\u540e"
        "\u7236\u6280\u80fd\u4e0e\u4e94\u4efd\u5b50\u6280\u80fd\u5404\u81ea\u90fd\u5728"
        "\u7ebf\u4e0b\uff0c\u800c\u7c98\u8d34\u957f\u4e2d\u6587\u4ecd\u7136\u662f"
        "\u767b\u8bb0\u5728\u6848\u7684\u9ad8\u5371\u52a8\u4f5c\u3002"),
    ("**\u6240\u4ee5\u522b\u62ff blob \u54c8\u5e0c\u53bb\u6bd4\u6280\u80fd\u6b63\u6587**"
        " \u2014\u2014 \u5b83\u6c38\u8fdc\u4e0d\u7b49\uff0c\u800c\u90a3\u4e0d\u662f\u6f02\u79fb\u3002",
     "**\u6240\u4ee5\u5728\u4efb\u52a1\u8bfb\u56de\u8fd9\u6761\u8def\u4e0a\u522b\u62ff blob "
        "\u54c8\u5e0c\u53bb\u6bd4** \u2014\u2014 \u5b83\u6c38\u8fdc\u4e0d\u7b49\uff0c\u800c"
        "\u90a3\u4e0d\u662f\u6f02\u79fb\u3002**\u800c 2026-09-02 \u6d4b\u51fa\u53e6\u4e00"
        "\u6761\u8def\uff1a\u6c99\u7bb1\u91cc\u7684 `skill clone` \u62c9\u4e0b\u6765\u7684"
        "\u6b63\u6587\u662f\u9010\u5b57\u8282\u7cbe\u786e\u7684** \u2014\u2014 \u5254\u6389 "
        "frontmatter \u4e4b\u540e\uff0c\u4e24\u4e2a\u5b50\u6280\u80fd\u7684 body blob \u4e0e"
        "\u5907\u4efd\u4ed3\u5b58\u7740\u7684\u5b8c\u5168\u76f8\u540c\u3002\u6240\u4ee5"
        "\u5224\u636e\u6309\u901a\u9053\u5206\uff1a\u4efb\u52a1\u8bfb\u56de\u53ea\u80fd"
        "\u5f52\u4e00\u5316\u540e\u6bd4\uff0cCLI clone \u5fc5\u987b\u7528 blob \u6bd4\u3002"
        "\u800c\u8bfb\u5f97\u8fdb\u4e0d\u7b49\u4e8e\u5199\u5f97\u51fa\uff0c\u89c1\u4e0b"
        "\u4e00\u6761\u3002"),
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

out = text.encode('utf-8')
open(DOC, 'wb').write(out)
new_blob = blob(out)
print('new bytes  ', len(out), 'delta', len(out) - len(raw))
print('new blob   ', new_blob)
assert new_blob != DOC_BLOB_BEFORE, 'bytes changed but blob did not'

# refresh the one registered hash by targeted replacement, not by reserialising 80KB of manifest
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
