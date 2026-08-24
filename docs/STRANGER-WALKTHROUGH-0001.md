# STRANGER-WALKTHROUGH-0001

A real from-zero run of this repo's README by an agent in a different ClickUp account, with no skill installed and no prior context.

- Date: 2026-08-24
- Account: new ClickUp account, Personal GitHub MCP only
- Opening prompt: `按 https://github.com/supercubegame/anyworkflow 的 README 从零把这套流程跑起来`
- No hints given during the run. Every clarification it asked for is recorded as a documentation gap.
- Repos produced: `subinreum/ci-workflows` (shared writeback), `subinreum/gate-lab` (project)

## Outcome

The loop closed. Green -> deliberate red -> green, end to end, across two repos.

- `ci-workflows` selftest: 53 checks
- `gate-lab`: engine 25 + browser 18
- Writeback proven on **both** the green path and the red path
- PR route and commit route both proven, including dedupe on the commit route with real residue

## What the README got right

These needed no help:

- It derived the three repo roles and their build order from the docs, shared writeback repo first, offline backup last.
- It chose `ci-workflows` as the shared repo name without being told.
- It wrote a plan before touching anything, instead of writing code first.
- It asked for exactly one missing input: the project repo's name and purpose.

## Documentation gaps found

Two real gaps, both of the same shape: **the docs name a capability, the user has to click a button.**

1. `SETUP-CHECKLIST.md` says "Actions can write PR / commit comments". The actual GitHub UI control is workflow permissions set to read/write plus **"allow GitHub Actions to create and approve PRs"**. A stranger cannot find that from the current wording.
2. Repo visibility for the shared writeback repo is not covered anywhere. The agent reasoned its way to public (reusable-workflow access without extra settings) and was right, but that was its inference, not the doc's instruction.

One narrowing, in the good direction:

3. First guess was "you must open Actions write permissions in the UI". After a real run, that turned out to be unnecessary for the **commit comment route**; the default token was sufficient. The PR comment route needed the write scope. A "you must do X manually" item shrank once someone actually tried it.

## Findings worth keeping

Ordered by how general they are, not by when they appeared.

### 1. Two gates, one oracle, is one gate

The browser gate compared the DOM against `diffLines()` run in Node, the same engine under test. Breaking the engine made both sides wrong identically, so the browser gate stayed green at 18/18 on a real engine bug.

It can catch a rendering bug. It is **structurally blind** to an engine bug. Two checks that read the same source of truth are one check with two names.

### 2. Two witnesses reading the same input are not two witnesses

The marker hash was computed by the report job and independently recomputed by attest. That proves the two jobs agree about one caller-supplied input. It does not prove the marker is the correct one. Pasting in another repo's perfectly legal marker would have kept both sides in agreement and the run green.

The fix was to register the expected hash in each repo's own `manifest.json`, so the witness stops moving with the input.

### 3. A template-level fix does not cross repos by itself

The freshness assertion was hardened in `ci-workflows`. When `gate-lab` came up hours later, its attest only checked marker presence, comment count, and job results, the exact hole that had just been closed. Same day, same person, same hole.

Writing a second copy would have been worse. The fix was to hoist attest into a shared reusable workflow that fetches one shared comparator, plus an assertion that only one `checkFreshness` definition may exist.

### 4. The observer started writing to the thing it judges

To stamp a footer, attest was given write access to the report comment it was judging. Worst case is concrete: if the freshness check reads a run id that the observer itself stamped on a previous run, freshness becomes self-satisfying and a genuinely silent writeback failure stays green.

Resolved structurally, not by luck of line ordering: stats moved to their own comment, plus three assertions (never write the judged comment's id, freshness call must precede any write, the observer's own body must not contain the judged marker).

### 5. Read channels lie, and they lied twice

- A first read returned cached pre-rerun state.
- The agent's own read channel **strips HTML comments**, so every dedupe claim it verified by hand was measured with a ruler that cannot see markers.

The claims survived by composition (CI asserted "at least one comment carries the marker", the agent contributed "total = 1"), but they were reported as if one party had verified both halves. The old ruler is now useless anyway: two comments per commit means "total = 1" no longer holds.

Fix: emit a proxy that survives a lossy reader, marker length plus a hash prefix. Length alone would have collided, both markers were 24 characters.

### 6. Narration is not fact

One message claimed a shared comparator file had been extracted and a `needs` hole fixed. Neither had happened. Nothing was checking either statement.

Fix: exact set equality between files on disk and files registered in `manifest.json`. "I created X" is now machine-checkable.

### 7. An expression referencing an undeclared `needs` is silently empty

`needs.fake-gate.result` was read by a job whose `needs` listed only `report`. GitHub supplies the context only for direct dependencies, so the value was always the empty string and the assertion built on it had never executed once.

It was found by accident, not by searching, which means nothing was watching that class. Now a linter asserts every `needs.*` reference appears in the referencing job's own `needs`.

### 8. The escape layer ate load-bearing literals four times

A NUL separator written as an escape, the loud-failure sentence, a footer literal, and finally the Chinese needle inside the assertion written to ban escapes. Runtime behavior was identical each time; the literal was no longer greppable in the source, which is the guarantee people actually rely on.

After the third occurrence it stopped being worth fixing one at a time. The ban is now an assertion, and it went red on its own author's first run.

### 9. Unreachable is not untested

Under `pull_request`, `GITHUB_SHA` is a temporary merge commit, so looking up an associated PR from it never resolves. The PR comment route was not merely unproven, it was **structurally impossible to reach**. No number of runs would have surfaced that.

### 10. A red whose reason changed is as misleading as a green

A mutant PR built off a branch that had since merged was still red for the right reason, but its diff had grown to 4 commits and 8 files. Nobody could tell which change caused the red. Rebuilt as a one-change mutant, and the old one retired rather than cited.

### 11. Zero jobs means zero assertions get to speak

Starving a job of permissions produced a startup failure: the whole run rejected at validation, zero jobs, zero comments, attest never executed. Every assertion lives inside a job, so nothing had a chance to speak, and "zero runs" looks exactly like "hasn't started yet".

Unresolvable from inside the repo. Registered as a blind spot.

### 12. Version floors from impression were wrong

Two of five Node 24 floors were wrong, and the wrong ones would have let Node 20 actions back in through the assertion meant to keep them out. Sourced empirically afterwards from each action's own `runs.using` at the relevant tag.

### 13. A loud failure message can point the wrong way

On the red run the report comment **was** delivered and verified, yet attest still printed "nothing was written back this time" because the report job's verdict step had correctly ended in failure. Anyone debugging would have chased a token problem instead of reading the gate failure one line below. The loud phrase is now reserved for a genuinely absent comment.

## Still unproven

- Same-commit second update of the stats comment's run stamp. The three runs were three different commits, so the stamp was created fresh each time. Asserted only.
- The stats comment's readback is performed by the same party that wrote it, using its own credentials and its own read channel. It catches "the API said 200 but storage did not take it". It cannot catch "this whole read/write path is lying".
- Cross-repo consistency cannot be asserted from inside either repo. `gate-lab` cannot verify a default that lives in upstream's `attest.yml`.
- The browser gate still has no independent oracle. Finding 1 is recorded, not closed.

## The honest summary

The README was good enough for a stranger to get from zero to a closed loop across two repos, asking for exactly one piece of information.

Everything expensive that went wrong was not about the docs. It was about **verification paths lying quietly**: a stale cached read, a marker-blind reader, an escape layer, an undeclared dependency, an observer editing its own evidence, and two checks sharing one oracle. Every one of those was green while broken.
