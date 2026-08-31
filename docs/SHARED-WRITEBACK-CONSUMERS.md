# Shared Writeback Consumers

This file is rendered from the CONSUMER_FILES dict in verify.py -- repos that call `supercubegame/ci-workflows/.github/workflows/report.yml`.
**It is not derived from those repos.** The gate compares this file against that dict, so both sides are one witness counted twice: a wrong dict renders a matching wrong file and the check stays green. That happened -- meetnote sat in the dict for weeks while its verify.yml wrote back on its own. A real derivation needs a cross-repo token, which this offline gate does not have.
It exists because a hand-maintained prose list already missed real consumers twice, and the first version of this generated list missed one again.
Read 2026-08-31 from the real files: clickup-brain-backup calls it from six workflows, not three. The three CI patchers were added after this dict was written, and an offline gate cannot see a repo grow a new caller -- so the generated file has now under-counted its own home repo, which is the third time this list was wrong in the same direction.
Read 2026-08-31 again, hours later: anyworkflow itself calls the shared writeback from its own verify.yml, and this dict had never listed it -- the fourth error, and the one where the list omitted the repo it lives in. That entry is now derived from the real files on disk, so it is the only truly derived line here; the other six repos are still hand-written because deriving them needs a cross-repo token.

- Repositories: **7**
- Workflow files: **15**

## TodoX
- `.github/workflows/verify.yml`
- `.github/workflows/release.yml`
- `.github/workflows/screenshots.yml`
- `.github/workflows/mirror.yml`

## anyworkflow
- `.github/workflows/verify.yml`

## clickup-brain-backup
- `.github/workflows/split-apply.yml`
- `.github/workflows/split-dry-run.yml`
- `.github/workflows/verify.yml`
- `.github/workflows/fix-confusable.yml`
- `.github/workflows/patch-heartbeat-gap.yml`
- `.github/workflows/patch-yaml-shape.yml`

## crossyroad
- `.github/workflows/verify.yml`

## flappycat
- `.github/workflows/verify.yml`

## image-grabber
- `.github/workflows/verify.yml`

## jumpwow
- `.github/workflows/verify.yml`
