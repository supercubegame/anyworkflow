<p align="center">
  <img src="./assets/logo-1080.png" alt="anyworkflow logo" width="120" />
</p>

<h1 align="center">anyworkflow</h1>

<p align="center"><strong>Agent workflow for building, verifying, and shipping software with evidence.</strong></p>

<p align="center">English | <a href="./README_CN.md">简体中文</a></p>

<p align="center">
  <a href="./docs/BOOTSTRAP-FROM-ZERO.md">Tutorial</a>
  ·
  <a href="./docs/PROMPT-EXAMPLES.md">Examples</a>
  ·
  <a href="./docs/RECOVERY.md">Recovery</a>
  ·
  <a href="./docs/MINIMAL-GATE.md">Verification</a>
</p>

---

## Quick Install

If you want the shortest path from zero to a first working version, do this:

1. Create three repos:
   - a shared writeback repo
   - a project repo
   - an offline backup repo
2. Enable GitHub Actions with write permissions for PR and commit comments.
3. Add the required secrets and tokens.
4. Set up the shared report workflow.
5. Start a fresh project conversation with an agent-friendly prompt.
6. Get one green PR.
7. Get one deliberate red -> green proof.
8. Capture live readback timestamps for the true copies.
9. Back the whole thing up into a repo like this one.

Full path: [`docs/BOOTSTRAP-FROM-ZERO.md`](./docs/BOOTSTRAP-FROM-ZERO.md)

---

## What You Get

This repo is the offline, auditable copy of an agent-first delivery workflow.

It preserves:
- how the workflow runs
- what it depends on
- which parts are backed by evidence
- which parts still need human or external proof

It does **not** pretend to be the live system.

---

## Example Prompts

Use these to test whether a fresh conversation naturally enters the workflow:

- “Build a 2D game and keep the quality bar yourself. I don’t want to hand-test it.”
- “Build a simple web tool. Keep the feature small, but keep the delivery quality high.”
- “Build a Chrome extension prototype. Set up the quality and verification chain first, then add features.”

Full set: [`docs/PROMPT-EXAMPLES.md`](./docs/PROMPT-EXAMPLES.md)

---

## Tutorial

If you are starting from zero, read these in order:

1. [`docs/BOOTSTRAP-FROM-ZERO.md`](./docs/BOOTSTRAP-FROM-ZERO.md)
2. [`docs/SETUP-CHECKLIST.md`](./docs/SETUP-CHECKLIST.md)
3. [`docs/FULL-WORKFLOW.md`](./docs/FULL-WORKFLOW.md)
4. [`docs/DEPENDENCIES.md`](./docs/DEPENDENCIES.md)

---

## Verification

This repo already contains three proof layers:

### 1. Structure proof
The files, ledgers, and rules exist.

### 2. Green proof
[`docs/VERIFY-EVIDENCE-0001.md`](./docs/VERIFY-EVIDENCE-0001.md) proves the minimal gate really ran green in live CI.

### 3. Red -> green proof
[`docs/VERIFY-EVIDENCE-0002.md`](./docs/VERIFY-EVIDENCE-0002.md) proves the minimal gate really goes red on a meaningful bad input, then returns green when fixed.

The minimal gate itself is `python3 verify.py`.

What it guards, and what it deliberately does **not** guard, is documented in:
[`docs/MINIMAL-GATE.md`](./docs/MINIMAL-GATE.md)

---

## Known Limits

This repo does **not** pretend to prove everything.

Still outside direct repo proof:
- whether a skill auto-triggered by summary
- ClickUp UI-only fields
- exact tool labels in the agent UI
- whether prompt prose is still true after another repo changed
- whether explanatory comments silently disappeared during repeated rewrites

See: [`docs/BLIND-SPOTS.md`](./docs/BLIND-SPOTS.md)

---

## Recovery

If you are using this repo to rebuild the workflow, start here:

1. [`docs/RECOVERY.md`](./docs/RECOVERY.md)
2. [`docs/RECOVERY-CHECKLIST.md`](./docs/RECOVERY-CHECKLIST.md)
3. [`docs/RESTORE-DRILL-TEMPLATE.md`](./docs/RESTORE-DRILL-TEMPLATE.md)
4. [`docs/RESTORE-DRILL-0001.md`](./docs/RESTORE-DRILL-0001.md)

---

## Deeper Docs

- Workflow overview: [`docs/FULL-WORKFLOW.md`](./docs/FULL-WORKFLOW.md)
- Offline backup scheme: [`docs/OFFLINE-BACKUP-SCHEME.md`](./docs/OFFLINE-BACKUP-SCHEME.md)
- Observer split: [`docs/OBSERVERS.md`](./docs/OBSERVERS.md)
- Dependency ledger: [`docs/DEPENDENCIES.md`](./docs/DEPENDENCIES.md)
- Incident ledger: [`docs/INCIDENT-LEDGER.md`](./docs/INCIDENT-LEDGER.md)
- Live readback ledger: [`docs/LIVE-READBACK-LEDGER.md`](./docs/LIVE-READBACK-LEDGER.md)
- Bootstrap history: [`docs/CHANGELOG-BOOTSTRAP.md`](./docs/CHANGELOG-BOOTSTRAP.md)
- Full index: [`docs/INDEX.md`](./docs/INDEX.md)

---

## One-line Summary

This repo is here to stop one specific failure mode:

> **The files still exist, but the system has already started lying quietly.**
