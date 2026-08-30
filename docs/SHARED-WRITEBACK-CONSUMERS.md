# Shared Writeback Consumers

This file is rendered from the CONSUMER_FILES dict in verify.py -- repos that call `supercubegame/ci-workflows/.github/workflows/report.yml`.
**It is not derived from those repos.** The gate compares this file against that dict, so both sides are one witness counted twice: a wrong dict renders a matching wrong file and the check stays green. That happened -- meetnote sat in the dict for weeks while its verify.yml wrote back on its own. A real derivation needs a cross-repo token, which this offline gate does not have.
It exists because a hand-maintained prose list already missed real consumers twice, and the first version of this generated list missed one again.

- Repositories: **6**
- Workflow files: **11**

## TodoX
- `.github/workflows/verify.yml`
- `.github/workflows/release.yml`
- `.github/workflows/screenshots.yml`
- `.github/workflows/mirror.yml`

## clickup-brain-backup
- `.github/workflows/split-apply.yml`
- `.github/workflows/split-dry-run.yml`
- `.github/workflows/verify.yml`

## crossyroad
- `.github/workflows/verify.yml`

## flappycat
- `.github/workflows/verify.yml`

## image-grabber
- `.github/workflows/verify.yml`

## jumpwow
- `.github/workflows/verify.yml`
