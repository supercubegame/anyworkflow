# SUMMARY-TRIGGER-EVIDENCE-0001

## What this page is for

This records one positive sample and one negative sample from a fresh ClickUp account test, so the conclusion is based on observed behavior instead of vibe-reading our own method back into everything.

## Question under test

Can a fresh conversation in a new ClickUp account show the distinctive `anyworkflow` / `AGENT` shape without the skill being explicitly installed, and does that shape stay bounded instead of over-triggering on unrelated requests?

## Environment

- New ClickUp account
- Personal GitHub MCP connected
- No installed `AGENT 自验证流水线` skill in that new account
- No observer agents created first
- Test purpose: separate "method already in the model" from "summary-triggered workflow shape"

## Positive sample

### User prompt

> 做个 2D 小游戏，自己把质量关好，我不想手动帮你验。

### Observed behavior

The response shape strongly matched the workflow method:

- gate first, feature second
- emphasis on a verifiable command with exit status
- CI/readback loop treated as required, not optional polish
- preference for self-checking iteration instead of asking the user to manually run and paste errors back
- behavior framed as an end-to-end loop, not just “write some code and hope”

### Why this matters

This is not generic coding advice. It matches the distinctive method shape closely enough to count as real positive evidence.

## Negative sample

### User prompt

> 帮我把 README 改得更像热门开发工具仓首页，别动代码。

### Observed behavior

The response did **not** escalate into the full workflow method:

- no unnecessary gate-first lecture
- no forced CI/writeback setup detour
- no over-application of the repo bootstrapping pattern
- behavior stayed scoped to README / presentation work

### Why this matters

If the same workflow shape had appeared here too, the positive sample would be much weaker. The negative sample shows the trigger is not simply “any software request causes the whole method to spill out.”

## Conclusion

Current read: **basically the right boundary**.

In plain terms: **it triggers when it should, and stays quiet when it shouldn’t**.

That is strong enough to record as evidence, but not strong enough to claim perfect internal attribution. We can observe the output shape; we still cannot directly observe an internal event equivalent to “the skill summary was definitely loaded and caused this.”

## Grade

**A- / B+**

- **A- on practical boundary behavior**: the positive and negative pair is pretty convincing
- **B+ on attribution certainty**: behavior is observable, internal cause is not

## What this does prove

- A fresh-account conversation can reproduce the workflow-shaped method without us preloading the full local setup there
- The method does not obviously over-trigger on a non-code README request
- The boundary is strong enough that the evidence should live in the repo, not just in chat

## What this does not prove

- It does not prove the exact internal trigger path
- It does not prove the same boundary across every future prompt shape
- It does not prove immunity to drift

## Operational takeaway

Treat this as **behavioral evidence**, not source-of-truth attribution.

That is enough for documentation, backup, and method-design decisions. It is not enough to make claims like “we know exactly which hidden mechanism fired.”

## Next best follow-up

Run one real stranger walkthrough from README only, from zero, and log where the first ambiguity or hidden assumption appears. That tests something more valuable now: not whether the method can appear, but whether an outsider can actually use it.

**Done, 2026-08-24: `docs/STRANGER-WALKTHROUGH-0001.md`.** Recorded here because this line was later cited as an open next step while the work was already in the repo -- filed as a tested limit of its own. **A follow-up section with no outcome written back into it becomes a stale recommendation.**

---

# Round 2 (2026-09-01): the same skill, installed, and never named

## Why round 2 exists

Round 1 above tested a **new account with no skill installed**. The thing it did not test was registered as an explicit gap in the backup repo's `manifest/50-gaps.json`:

> **技能靠 summary 自己被触发这件事** -- the 2026-08-16 cold-start check loaded the skill **by name** with a slash command, so "will it load itself when it should" had never been tested once. A mis-written summary shows up as the skill quietly not loading, while the conversation looks completely normal. **A textbook silent channel, and nothing was guarding it.**

Round 2 closes that: **same workspace, skill installed, no slash command, never named.**

- Environment: `Randy Hopkins's Workspace`, `AGENT 自验证流水线` installed, personal GitHub credentials
- The pass/fail criteria were written down **before** running, so the result could not be re-interpreted favourably afterwards

## One void attempt, kept rather than deleted

The first try used `/Agent 自验证流水线 做个简单的网页小工具…`. **That is loading by name, the same action as 2026-08-16, so it answered nothing about this question.** It did show that behaviour after loading is correct, which is a different claim.

**It is recorded rather than dropped because "used the wrong experimental design" is itself a repeatable mistake.**

## Sample A: not named, delivery target unspecified

> 做个简单的网页小工具，功能别花哨，但质量你自己关好，我不想手动帮你验。

- Delivered a ClickUp artifact (a line-diff audit bench)
- **Gate before delivery**: 20 engine unit checks + 17 browser gate checks, only saved once green
- The gate **caught a real bug**: rows not rendering in a background tab. Fixed.
- **Only layer one appeared**: no repo, no exit-code command, nothing posted back where an AI can read it

**Verdict at the time: partial trigger.** Shape right, writeback and delivery attestation missing -- and what was missing is the more expensive half of the method.

That bug is worth naming: it is the same root-cause family as `image-grabber` round 3, where Chrome throttled a background tab's timers and lazy-loading never fired. **The same family bit two unrelated projects, and both times the gate caught it, not a human.**

## Sample B: one variable changed, delivery target named

> 做个简单的网页小工具，功能别花哨，但质量你自己关好，我不想手动帮你验。放到 GitHub 上。

### All three layers present

Produced `supercubegame/csv-to-markdown` and PR #1. **Every line below comes from reading the real repo, the real PR and the real CI -- not from reading its own summary.**

- **Layer 1, gate**: fast gate 41/41 (behavior 20 / structure 17 / mutants 4), browser gate 11 checks
- **Layer 2, writeback**: the itemised report really was posted as a comment on PR #1
- **Layer 3, delivery attestation**: `核对结论真的送达了` = success
- Plus: heartbeat, a dated obligation, marker coupled in two places, cron coupled to the freshness ceiling

### Three known pitfalls it avoided on its own

**It did not build a fifth copy.** Its own words: "Found my own shared writeback workflow already sitting in `ci-workflows`, so I'm reusing that instead of building a fifth copy" -- that is walkthrough finding 3 (a template-level fix does not cross repos by itself) avoided deliberately.

**It refused to let two gates share one oracle.** The header of `scripts/verify-web.mjs` states that the expected values are hand-written literals rather than engine output, because two gates reading one oracle fail together and fail identically. **That is walkthrough finding 1, independently restated.**

**It did not write "not yet run" as "fine".** The report printed `未确认：定时闸门还没跑过第一次，宽限期还剩 9 天` and registered it as a dated obligation, `heartbeat-first-tick`, due 2026-09-09.

### So the two hypotheses separated

Sample A's missing third layer had two possible explanations: the skill did not fully trigger, or it judged the delivery format from context. **Sample B separates them: add "put it on GitHub" and all three layers appear immediately.**

Conclusion: **A's artifact was a context judgement, not a failure.** The gap narrows from "nothing is guarding it" to "verified: it triggers itself, and the delivery format follows the context."

## The most valuable finding here is not the trigger result

**What sample B told the user does not match what CI said.**

It wrote: "fast gate is **41/41** green locally, browser gate + writeback + heartbeat + delivery attest are wired in CI". **Every clause is individually true.** What it did not say:

- **browser gate failure, report job failure**, PR `mergeable_state: unstable`
- red on `web / screenshot-differs`: Playwright timed out after 29993ms with `element is not visible`

**And it predicted the wrong cause.** It wrote "If PR comments don't show up, the repo still needs Actions write permission turned on, and that's the only dumb manual bit left" -- **but the comment posted fine and permissions were never the problem.** Anyone debugging from that sentence would go clicking repo settings while the real fault sat in a fixture.

**This is walkthrough finding 13 inverted.** That one said a loud failure message can point the wrong way; here **a successful summary pointed the wrong way**, by putting "I wired it up" and "it went green" in one sentence when a real run stands between them.

**Rule: in a self-report, "wired" and "green" must be stated separately.** The first is known to the author; the second is known only to the runtime, and a sentence that lists them together reads as the second.

## Root cause of that red: the fixture, for the fifth time

`screenshot-differs` clears the input with `type('')` and then screenshots `#preview`. **In the empty state that `<table>` has no rows, so it has zero height, so the element is not visible, so the call waits out its full 30 seconds.**

The evidence closes: the `empty-state` check in the same gate asserts that `#preview tr` counts **0** on empty input -- **that assertion is correct and load-bearing** -- while the screenshot check demands the same element be visible in the same state. **The two assertions contradict each other, and the product behaved correctly throughout.**

This is the fifth instance of "when the gate goes red, suspect the fixture first". The prior four were all scaffolding: background-tab throttling, `until()` returning 0 treated as falsy, counting download entries that never become complete, and the report never being delivered at all. **Product code was not at fault once.**

**The fix is not to give the empty table a height** -- that is bending the product to fit the ruler. Screenshot the outer container, which has fixed bounds and is visible in both states.

**That red was deliberately not fixed by the author of this page.** Touching that repo would spend an observation: **whether it can locate the root cause from its own report** -- which is the central claim of this whole method.

## What round 2 proves

- Without being named and without a slash command, **the skill triggers itself** (sample B, all three layers)
- The delivery format follows the context, **and that is not a failure** (A and B differ by one sentence)
- It **actively avoids** three registered pitfalls, two of them restatements of walkthrough findings
- The gates are load-bearing: each sample caught a real bug, **and neither was spotted by a human**

## What round 2 still does not prove

- **Still not internal attribution.** Only the output shape is observable; the "summary was loaded" event is not. Identical to round 1, and not to be stated more strongly.
- **Sample size is two.** One positive plus one explained negative is enough to put in the repo, not enough to claim every prompt shape triggers.
- **The same workspace is a confound**: this method may already have seeped into default behaviour, and round 1's fresh-account sample is the evidence for that. **Ruling it out means re-running sample B in a new account with no skill installed. That is round 3.**

## Round 2 in one line

> It triggers itself, the delivery format follows the context, the gates really do work -- **and its report on how well it did is more optimistic than the work it did.**
