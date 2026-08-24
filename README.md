<p align="center">
  <img src="./assets/logo-1080.png" alt="anyworkflow logo" width="120" />
</p>

<h1 align="center">anyworkflow</h1>

<p align="center"><strong>Agent workflow for building, verifying, and shipping software with evidence.</strong></p>

<p align="center">English | <a href="./README_CN.md">简体中文</a></p>

---

## Quick Install

Start here if you want the fastest path from zero to a first working version:

1. Create three repos: a shared writeback repo, a project repo, and an offline backup repo. Build them in that order.
2. Make the shared writeback repo **public** unless you have a reason not to. A private reusable workflow needs extra access setup before other repos can call it.
3. In the shared repo: Settings -> Actions -> General -> set **Workflow permissions** to **Read and write permissions**, and check **"Allow GitHub Actions to create and approve pull requests"**.
4. Add the required secrets and tokens. A cross-repo token is only needed if the repos are private.
5. Set up the shared report workflow, and give it its own gate. A shared workflow with no gate of its own is a single point of silent failure.
6. Start a fresh project conversation with an agent-friendly prompt.
7. Get one green PR.
8. Get one deliberate red -> green proof, and confirm the report was delivered on the **red** run too.
9. Capture live readback timestamps for the true copies.
10. Back the whole thing up into a repo like this one.

Need the full path? Go to:
- [`docs/BOOTSTRAP-FROM-ZERO.md`](./docs/BOOTSTRAP-FROM-ZERO.md)
- [`docs/SETUP-CHECKLIST.md`](./docs/SETUP-CHECKLIST.md)
- [`docs/PROMPT-EXAMPLES.md`](./docs/PROMPT-EXAMPLES.md)

Want to see it actually done by someone starting cold? [`docs/STRANGER-WALKTHROUGH-0001.md`](./docs/STRANGER-WALKTHROUGH-0001.md)

---

## What You Get

This repo gives you:
- an offline, auditable copy of the workflow
- setup and recovery docs
- true-copy archives for key prompts and shared workflow logic
- green and red -> green proof records
- a clear list of what still needs human or external proof

It does **not** pretend to be the live system.

---

## Example Prompts

Use these to test whether a fresh conversation naturally enters the workflow:

- “Build a 2D game and keep the quality bar yourself. I don’t want to hand-test it.”
- “Build a simple web tool. Keep the feature small, but keep the delivery quality high.”
- “Build a Chrome extension prototype. Set up the quality and verification chain first, then add features.”

More: [`docs/PROMPT-EXAMPLES.md`](./docs/PROMPT-EXAMPLES.md)

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

### Structure proof
The files, ledgers, and rules exist.

### Green proof
[`docs/VERIFY-EVIDENCE-0001.md`](./docs/VERIFY-EVIDENCE-0001.md) proves the minimal gate really ran green in live CI.

### Red -> green proof
[`docs/VERIFY-EVIDENCE-0002.md`](./docs/VERIFY-EVIDENCE-0002.md) proves the minimal gate really goes red on a meaningful bad input, then returns green when fixed.

The minimal gate itself is `python3 verify.py`.

What it guards, and what it deliberately does **not** guard, is documented in:
[`docs/MINIMAL-GATE.md`](./docs/MINIMAL-GATE.md)

---

## Known Limits

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
- Stranger walkthrough: [`docs/STRANGER-WALKTHROUGH-0001.md`](./docs/STRANGER-WALKTHROUGH-0001.md)
- Summary trigger evidence: [`docs/SUMMARY-TRIGGER-EVIDENCE-0001.md`](./docs/SUMMARY-TRIGGER-EVIDENCE-0001.md)
- Bootstrap history: [`docs/CHANGELOG-BOOTSTRAP.md`](./docs/CHANGELOG-BOOTSTRAP.md)
- Full index: [`docs/INDEX.md`](./docs/INDEX.md)

---

## Summary

A readable, auditable backup of an agent-first verification workflow.
