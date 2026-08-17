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

## What this repo should contain
- Human-readable backup docs for the workflow and its principles
- Ledgers of live dependencies and external observers
- Recovery instructions for recreating the workflow elsewhere
- Explicit lists of what is still not backed up or not machine-verifiable

## What this repo should not pretend to do
- It does not prove summary auto-triggering unless that was explicitly tested
- It does not prove live ClickUp UI state from static exports
- It does not prove external repos are still true unless they were read back

## Editing discipline
- One change shape per PR
- If a statement depends on "what time it is now", use an external timestamp, not the local conversation clock
- If a record is fulfilled, either delete it or convert its completion rule into a standing check
