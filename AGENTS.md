# anyworkflow

## Purpose
- This repo is an offline backup of the Agent self-verification workflow itself: skills, prompts, workflow ledgers, recovery notes, and known blind spots.
- It is not the source of truth for live ClickUp assets or live GitHub repos. It is the auditable copy.

## Core Rules
- Gate first, content second.
- Every backup claim needs either a check, a timestamped human readback, or an explicit blind-spot note.
- Never write a clean status for something that was not actually verified.
- Cross-repo truth is never inferred from one repo alone.
- If a file grows large enough that one-shot rewrite becomes unreliable, split it before changing behavior.

## Gate, writeback, attest
- The gate is `python3 verify.py`. CI runs it, the shared `ci-workflows/report.yml@main` turns the per-check result into one comment, and `scripts/attest_delivery.py` goes back to the API to confirm the comment for **this run** really exists.
- A green gate whose conclusion was never delivered counts as not run. That is why attest is a separate job with `always()`: the red runs have to prove delivery too.
- `scripts/attest_delivery.py` exits `2` when its own offline self-test fails or a prerequisite is missing. Exit 2 means "this run verified nothing", which is not green and not the same as exit 1 ("delivery is broken").
- `scripts/compose-report.mjs` is the only JavaScript here. That is the shared workflow's calling convention (`node <entry> reports`), not a choice about this repo.

## Coupled parameters (change one, recompute the other)
- `manifest.json` → `writeback.marker` is the source of truth for the writeback marker. The `marker:` input in `.github/workflows/verify.yml` must equal it byte for byte; attest reads it from the manifest. The gate asserts both directions.
- `COMPOSER_SENTINEL` in `scripts/compose-report.mjs` and in `scripts/attest_delivery.py` must stay byte-identical. The shared workflow's degraded fallback comment carries the **same marker**, so this sentinel is the only thing separating "full report" from "fallback". The gate asserts it by reading both call sites, holding no copy of the literal itself.
- The gate job name `备份仓闸门` is load-bearing: `docs/VERIFY-EVIDENCE-0001` and `0002` both identify it by that name.

## What this repo should contain
- Human-readable backup docs for the workflow and its principles
- Ledgers of live dependencies and external observers
- Recovery instructions for recreating the workflow elsewhere
- Explicit lists of what is still not backed up or not machine-verifiable

## What this repo should not pretend to do
- It does not prove summary auto-triggering unless that was explicitly tested
- It does not prove live ClickUp UI state from static exports
- It does not prove external repos are still true unless they were read back
- Attest does not prove the shared writeback workflow upstream is unchanged; it only proves this run's comment arrived

## Editing discipline
- One change shape per PR
- If a statement depends on "what time it is now", use an external timestamp, not the local conversation clock
- If a record is fulfilled, either delete it or convert its completion rule into a standing check
- Any scanner that asks "does this file contain X" must strip comment lines first, then prove the stripping left real code behind
