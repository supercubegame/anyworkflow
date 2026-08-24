# Setup Checklist

This checklist only covers the things that must be confirmed or configured manually.

Every UI item below names the **actual control you click**, not the capability it grants. Naming only the capability was the first real gap found in `STRANGER-WALKTHROUGH-0001.md`.

---

## A. GitHub repos and Actions
- [ ] Shared writeback repo exists
- [ ] Project repo exists
- [ ] Offline backup repo exists
- [ ] Default branch exists
- [ ] Shared writeback repo visibility decided: **public** is the low-friction choice, because a private reusable workflow needs extra access configuration before other repos may call it. Decide this before wiring callers, not after.
- [ ] Backup repo visibility decided **on contents, not on billing**: if it holds prompts, configs, or internal method notes, going public to save Actions minutes publishes exactly what it exists to protect.
- [ ] GitHub Actions is enabled
- [ ] Settings -> Actions -> General -> **Workflow permissions** set to **Read and write permissions**
- [ ] Same page: **"Allow GitHub Actions to create and approve pull requests"** is checked
- [ ] Pages / deploy features are enabled if the project needs a live preview

### What each permission actually buys
Measured, not assumed:
- The **commit comment** route works on the default token. Read-only was enough.
- The **PR comment** route needs the write scope above.
- If the attest step writes anything of its own (a stats comment, a footer), that call site needs write too. Read-only there fails in a way that reads like "nothing was written back".

---

## B. Secrets and tokens
- [ ] Cross-repo token exists
- [ ] Token scope actually covers the target repo
- [ ] Token was not created before the target repo existed with a frozen allowlist
- [ ] Mirror / deploy / external API secrets are present in the correct repo

---

## C. ClickUp side
- [ ] Skills are installed and loadable
- [ ] Load-bearing Super Agents exist
- [ ] Schedules are configured
- [ ] Triggers are configured
- [ ] Required private knowledge scope is granted

---

## D. Screenshot-only proof points
These are not needed every time, but when two reading paths disagree, ask for one of these before guessing:
- [ ] Agent tool hover list
- [ ] Actions usage page
- [ ] Agent workspace knowledge panel
- [ ] UI-only trigger configuration
- [ ] Any interface evidence where two channels disagree on the same state

---

## E. Buttons only a human can press
These cannot be done by an agent, and each one proves something no amount of pushing will prove:
- [ ] **Actions -> the workflow -> Run workflow** on the same commit, twice. A second run on a **new** commit does not test dedupe; only a repeat on one commit forces update-instead-of-create against real residue.
- [ ] Note both run ids and hand them back. The agent cannot see which run you triggered, so without the ids it cannot tell a fresh write from stale residue.
- [ ] Prefer **Run workflow** over **Re-run all jobs**: a re-run reuses the same run id, so a freshness check reading stale content would still pass.

---

## F. Minimum proof that the system really works
- [ ] At least one green PR
- [ ] At least one deliberate red -> green proof
- [ ] PR comment path works
- [ ] Commit comment path works
- [ ] Attest really confirmed the comment exists
- [ ] The report was also delivered on a **red** run, not only on green ones
- [ ] If schedules exist, the manual write path has been tested once
- [ ] If heartbeat exists, the scheduled field has changed from null to a timestamp at least once

---

## G. Things you still must not pretend are proven
- [ ] Skill summary auto-trigger attribution
- [ ] ClickUp UI-only fields
- [ ] Prompt prose staying true after another repo changes
- [ ] Explanatory comments surviving repeated rewrites
- [ ] Anything a startup failure would have swallowed: zero jobs means zero assertions got to speak, and that looks identical to "has not started yet"

---

## One-line standard

> If even one checkbox still depends on guessing, memory, or “it looks fine”, setup is not actually complete.
