# Recovery Guide

## What this backup is for
This repository is the offline copy of the Agent self-verification workflow itself: the method, the ledgers, the known blind spots, and the recovery steps.

## To restore this workflow elsewhere
1. Recreate the target GitHub repos or identify the existing ones.
2. Recreate the core workflow files and CI jobs.
3. Recreate the ClickUp agent prompts and schedules.
4. Reconnect the shared writeback workflow dependency.
5. Re-test the delivery path: PR comment, commit comment, and attest.
6. Re-test any heartbeat or scheduled jobs with a manual write that does not pollute the real freshness field.
7. Rebuild the ledgers so the backup stops pretending old state is current state.

## What must be verified live after restore
- Shared report workflow still writes somewhere readable
- Schedules actually fire
- Heartbeat files update on schedule
- PR and commit comment paths both work
- Any cross-repo ledger matches real files
- Agent prompts in ClickUp match the exported copies

## What this backup still cannot restore by itself
- Whether a skill is auto-triggered by summary
- UI-only agent fields not exposed through readable config
- Human judgments such as whether a watcher message is too noisy
