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

## 当前仍然欠的证据
1. **第一条完整的 green PR 证据链**
   到目前为止，大部分内容是直接写在 `main` 上长出来的。结构是真的、文档是真的，但交付链证据弱。
2. **最小闸门的可读运行证据**
   需要一条能回头指给别人看的“它真跑过，而且是绿的”。
3. **summary 自动触发归因**
   这条仍然不在本仓能证明的范围里。

---

## 为什么这份文件存在
因为以后回头看，最容易发生的错觉是：

> 仓库里这些文件一直都在。

不对。它们是分阶段长出来的，而且每一层解决的是不同的坏法。

这份 changelog 守的是“来路”，不是“现状”。