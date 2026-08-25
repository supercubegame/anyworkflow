# anyworkflow 文档索引

这份仓库现在已经不是“几个散落的备份文件”，而是一份开始成形的离线档案。

如果不做索引，下一步最容易发生的不是“文件丢了”，而是：

> 文件都在，但没有人知道该先看哪一份。

所以这里按用途分，不按文件名分。

---

## 1. 原理说明

### `FULL-WORKFLOW.md`
整套工作流从需求到闸门、回写、观察者的闭环说明。

### `OFFLINE-BACKUP-SCHEME.md`
离线备份方案四层结构：真身、拄本、台账、外部观察者。

### `FULL-WORKFLOW-FIGURE.md`
“完整工作流程示意图”的文字版图说。

### `OFFLINE-BACKUP-FIGURE.md`
“离线备份方案示意图”的文字版图说。

---

## 2. 真拄本

### `../agents/gate-audit-quinn.md`
Quinn 当前 prompt、schedule、trigger 与角色说明的离线副本。

### `../agents/drift-devon.md`
Devon 当前 prompt、schedule、trigger 与角色说明的离线副本。

### `../vendor/ci-workflows/report.yml`
共享回写 workflow 的当前归档拷贝。

### `LIVE-READBACK-LEDGER.md`
这些真拄本最后一次和真身对上的时间账本。

> 注意：这些都是**拄本**。它们能证明“上次有人这样导出过”，不能证明真身此刻还是这样。
>
> 而且它们目前**在最小闸门的视野之外**（见 `MINIMAL-GATE.md` 的“不守 6”）：可以被清成空壳而闸门全绿。那是一笔明写的欠账。

---

## 3. 恢复与演练

### `RECOVERY.md`
恢复顺序：从 repo、workflow、prompt、shared writeback 到 live readback。

### `RECOVERY-CHECKLIST.md`
恢复时可以逐项打钩的清单，不用临场回忆。

### `RESTORE-DRILL-TEMPLATE.md`
以后真的做过一次恢复演练时，应该怎么记账。

### `RESTORE-DRILL-0001.md`
第一条真实恢复演练记录：这份备份仓自身结构可以重建什么，哪些仍然是 blind spot。

---

## 4. 盲区、事故与边界

### `BLIND-SPOTS.md`
当前仍然不能自动证明的东西清单。

### `INCIDENT-LEDGER.md`
这套东西曾经怎么坏过，以及后来怎么把那种坏法钉成断言。

### `OBSERVERS.md`
Quinn / Devon 的职责分工与为什么不能互相复读。

### `DEPENDENCIES.md`
这份备份真正依赖哪些仓外真身、权限、时序和手动动作。

### `CHANGELOG-BOOTSTRAP.md`
这份离线备份仓是怎么一层层长起来的，不让“这些文件好像一直都在”变成错觉。

---

## 5. 仓库自校验

### `../manifest.json`
这份备份仓自己已经备了什么、没备什么、哪些字段必须非空,以及 `writeback` 一节：回写 marker 的真源。

### `../verify.py`
最小闸门：守最基本的诚实，不让这份备份仓自己安静地说谁。

### `MINIMAL-GATE.md`
解释这条最小闸门**守什么、不守什么、为什么故意只守这么少**，以及它上面那两层（回写、送达核对）各自负责什么。这页是理解 `verify.py` 的入口，不是附属品。

### `../.github/workflows/verify.yml`
把三层接进 CI：闸门 → 回写 → 送达核对。

### `../scripts/compose-report.mjs`
把闸门的逐项结果合成一条评论。共享回写 workflow 以 `node <entry> reports` 调它,这仓唯一的 JavaScript，那是跨仓契约不是选择。

### `../scripts/attest_delivery.py`
回头去 API 上确认**这一次**那条评论真的存在。它带九个合成样本的离线自证，尺子坏了会 `exit 2`,而那不是绿。

---

## 6. 证据链

### `VERIFY-EVIDENCE-0001.md`
第一条 live CI 绿灯证据：最小闸门真的跑过一次，而且是绿的。

### `VERIFY-EVIDENCE-0002.md`
第一条负向证明：故意把 `not_backed_up` 清空，闸门按预期变红，再修回去后恢复成绿。

> 这两页合在一起，才第一次证明最小闸门不只会亮绿灯，也会在最值钱的地方真的喊。

### 还欠一条：送达证据
回写与 attest 是刚接上的。**在真的观察过一次运行之前，这里不该有页。** 观察到之后补 `VERIFY-EVIDENCE-0003`，写实测值，不写“预期”。

---

## 7. 先看哪一份

### 如果你第一次进这个仓库
先看：
1. `FULL-WORKFLOW.md`
2. `OFFLINE-BACKUP-SCHEME.md`
3. `DEPENDENCIES.md`

### 如果你要恢复这套东西
先看：
1. `RECOVERY.md`
2. `RECOVERY-CHECKLIST.md`
3. `RESTORE-DRILL-TEMPLATE.md`
4. `RESTORE-DRILL-0001.md`
5. 真拄本（agents / vendor）

### 如果你想知道这套东西以前怎么坏过
先看：
1. `INCIDENT-LEDGER.md`
2. `BLIND-SPOTS.md`
3. `OBSERVERS.md`
4. `CHANGELOG-BOOTSTRAP.md`

### 如果你只想确认这份仓库自己是不是还诚实
先看：
1. `manifest.json`
2. `MINIMAL-GATE.md`
3. `verify.py`
4. `.github/workflows/verify.yml`
5. `VERIFY-EVIDENCE-0001.md`
6. `VERIFY-EVIDENCE-0002.md`

### 如果你想确认这份仓库不是摆设
先看：
1. `MINIMAL-GATE.md`
2. `verify.py`
3. `VERIFY-EVIDENCE-0001.md`
4. `VERIFY-EVIDENCE-0002.md`

---

## 一句话总结

这份索引存在的原因不是好看，而是防止另一种安静坏法：

> 备份已经越来越完整了，但人开始找不到该先读哪一份。
