# Setup Checklist

This checklist only covers the things that must be confirmed or configured manually.

---

## A. GitHub repos and Actions
- [ ] Shared writeback repo exists
- [ ] Project repo exists
- [ ] Offline backup repo exists
- [ ] Default branch exists
- [ ] GitHub Actions is enabled
- [ ] Actions can write PR / commit comments
- [ ] Pages / deploy features are enabled if the project needs a live preview

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

## E. Minimum proof that the system really works
- [ ] At least one green PR
- [ ] At least one deliberate red -> green proof
- [ ] PR comment path works
- [ ] Commit comment path works
- [ ] Attest really confirmed the comment exists
- [ ] If schedules exist, the manual write path has been tested once
- [ ] If heartbeat exists, the scheduled field has changed from null to a timestamp at least once

---

## F. Things you still must not pretend are proven
- [ ] Skill summary auto-trigger attribution
- [ ] ClickUp UI-only fields
- [ ] Prompt prose staying true after another repo changes
- [ ] Explanatory comments surviving repeated rewrites

---

## One-line standard

> If even one checkbox still depends on guessing, memory, or “it looks fine”, setup is not actually complete.
