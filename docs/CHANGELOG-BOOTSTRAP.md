# Bootstrap Changelog

这不是项目更新日志。它只记录 `anyworkflow` 这份离线备份仓**是怎么长起来的**，以及哪些里程碑已经具备了可读证据，哪些还没有。

---

## Phase 0: 空仓初始化
- 手动新建仓库 `supercubegame/anyworkflow`
- 第一个提交只种下 `README.md`，把空仓变成有默认分支的仓库

**当前证据强度**：弱。只有 commit，没有 PR 交付链。

---

## Phase 1: 最小诚实闸门
落下这些最小结构：
- `AGENTS.md`
- `CLAUDE.md`
- `manifest.json`
- `verify.py`
- `.github/workflows/verify.yml`

这一步的目标不是“备份完整”，是先保证**这份备份仓自己不会安静地说谎**：
- 规则文件必须同步
- 恢复文档必须存在
- 盲区清单必须存在
- `not_backed_up` 不许是空数组
- `manifest` 顶层键不能缺

**当前证据强度**：中。结构齐了，但最开始那几步是直写 `main`，没有一条可读的 green PR 证据链。

---

## Phase 2: 文字骨架
补入基础说明：
- `docs/RECOVERY.md`
- `docs/BLIND-SPOTS.md`
- `docs/FULL-WORKFLOW.md`
- `docs/OFFLINE-BACKUP-SCHEME.md`
- `docs/FULL-WORKFLOW-FIGURE.md`
- `docs/OFFLINE-BACKUP-FIGURE.md`

这一步解决的是另一种坏法：

> 文件在，但没人知道它们为什么存在、该先看哪一份。

---

## Phase 3: 方法论记忆
补入：
- `docs/INCIDENT-LEDGER.md`
- `docs/OBSERVERS.md`
- `docs/DEPENDENCIES.md`
- `docs/INDEX.md`

这一步把“为什么这些规矩存在”以及“这套东西真正依赖什么”钉了下来。

如果没有这一层，备份仓很快会退化成一个只有结论、没有上下文的文件夹。

---

## Phase 4: 真抄本
补入当前真抄本：
- `vendor/ci-workflows/report.yml`
- `agents/gate-audit-quinn.md`
- `agents/drift-devon.md`

这一步的意义是把“现在这套系统真的怎么说话、怎么回写”落进仓库，而不只留在 live 系统里。

但它仍然只是抄本，不是真身。

---

## Phase 5: 恢复演练开始有记录
- `docs/RESTORE-DRILL-TEMPLATE.md`
- `docs/RESTORE-DRILL-0001.md`

到这一步，这份仓库才第一次不只是“知道以后该怎么演练”，而是真的留下了一条演练记录。

---

## Phase 6: 这仓自己终于有了回写与送达核对

在这一步之前，**这份仓库示范的是一套三层方法，而它自己只有第一层。**

`.github/workflows/verify.yml` 一共 313 字节：checkout + 跑闸门。没有回写、没有 artifact、没有送达核对。而这不是“还没做”，是一件已经被实测确认的事：**PR #10 的闸门是 success，那条 PR 上评论 0 条。**

同期对照更难看,同一个 owner 下的 `crossyroad`（一个网页版过马路小游戏）的 verify.yml 是 7.2KB，双闸门 + pipefail + artifact + 心跳 + 走共享 workflow 回写。**一个小游戏的闭环比方法本仓完整。**

这一步补的：
- `scripts/compose-report.mjs`,把逐项结果合成评论（共享 workflow 的调用方约定要求 Node 入口）
- `scripts/attest_delivery.py`,回头去 API 上确认**这一次**那条评论真的存在，带九个合成样本的离线自证
- `verify.py`,逐项结果落成 `artifacts/verify-report.json`；新增两条断言守这次接线自己造出来的两组耦合参数
- `.github/workflows/verify.yml`,闸门（pipefail + artifact）→ 回写（`ci-workflows/report.yml@main`）→ attest（`always()`，红的那次也要证明送达）

**这一步没有做的一半，明写在这里：**
1. 真抄本（`agents/*.md`、`vendor/ci-workflows/report.yml`）仍然在闸门视野之外,可以被清成空壳而全绿。修法是“备份类需求”那四条：清单双向、正文锚点、恢复充分性、新鲜度。
2. `manifest.invariants` 仍然是声明，没有任何东西核对它和实际检查集合相等。
3. 没有定时、没有心跳,“cron 静默停用”那一类在这仓还不适用（目前没有 cron），但一旦加了定时就必须同时加心跳。
4. `LIVE-READBACK-LEDGER.md` 的读回时间仍然是散文，没有期限断言。
5. `docs/INDEX.md` 自称 full index，实际还漏着几份文档。

**第一轮实测（PR #14，run 32905110223）**：三个 job 全绿，attest 也绿 —— 评论真的送出去了，带 composer 哨兵、本次短 SHA、本次 run id。两条边界要写清楚：

- **只走了 commit 评论那条通道**（回写跑的时候 PR 还没开）。PR 那条还没验过。
- **attest 至今没在 live CI 里红过一次。** 离线自证九个样本都过了，但从没红过的断言和空断言在报告上长得一样。

**顺带抓到一件不在计划里的事：写入通道会悄悄改写字。** 逐个文件读回核对 blob 哈希时发现 `说谎`→`说谁`、`抄本`→`拄本`、`骨架`→`骶架`、`分岔`→`分岘`,全是形近字，**每一处字节长度都没变**，于是两份文档读回来体积和本地完全一致，只有哈希不同。这条已经写进 `MINIMAL-GATE.md` 的“不守 6”，并且把真抄本那四条断言里的 blob 哈希提成了最高优先级。

**当前证据强度**：一半。“评论送得出去”有实测了；“送不出去的时候会喊”还没有,那条记录留给 `VERIFY-EVIDENCE-0003`，等 PR 通道与一次真红都拿到再写，写实测值，不写预期。

---

## 当前仍然欠的证据
1. **第一条完整的 green PR 证据链**
   到目前为止，大部分内容是直接写在 `main` 上长出来的。结构是真的、文档是真的，但交付链证据弱。
2. **回写与送达真的成立的可读证据**
   Phase 6 把链接上了，但需要一条能回头指给别人看的“评论真的贴出来了，而且红的那次也贴了”。
3. **summary 自动触发归因**
   行为证据已经有了（`SUMMARY-TRIGGER-EVIDENCE-0001`，正负样本各一个），内部归因仍然不在本仓能证明的范围里。

---

## 为什么这份文件存在
因为以后回头看，最容易发生的错觉是：

> 仓库里这些文件一直都在。

不对。它们是分阶段长出来的，而且每一层解决的是不同的坏法。

这份 changelog 守的是“来路”，不是“现状”。
