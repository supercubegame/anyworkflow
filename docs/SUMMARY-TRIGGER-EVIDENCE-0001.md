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
