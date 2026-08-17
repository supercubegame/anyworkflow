# Recovery Checklist

这不是原理说明，也不是演练记录。
这是一张**恢复时可以逐项打勾**的清单。

如果恢复过程里你需要一条能顺着走、不用临场回忆的东西，就看这份。

---

## A. 仓库壳子
- [ ] 目标仓库已创建
- [ ] 默认分支存在
- [ ] `README.md` 在
- [ ] `AGENTS.md` 在
- [ ] `CLAUDE.md` 在
- [ ] `AGENTS.md` 与 `CLAUDE.md` 逐字节相同

---

## B. 最小诚实闸门
- [ ] `manifest.json` 在
- [ ] `verify.py` 在
- [ ] `.github/workflows/verify.yml` 在
- [ ] 最小闸门会在 push / workflow_dispatch 上触发
- [ ] `not_backed_up` 不是空数组
- [ ] 至少跑过一次 live green（见 `VERIFY-EVIDENCE-0001.md`）
- [ ] 至少跑过一次 deliberate red -> green（见 `VERIFY-EVIDENCE-0002.md`）

---

## C. 文档骨架
- [ ] `docs/FULL-WORKFLOW.md`
- [ ] `docs/OFFLINE-BACKUP-SCHEME.md`
- [ ] `docs/FULL-WORKFLOW-FIGURE.md`
- [ ] `docs/OFFLINE-BACKUP-FIGURE.md`
- [ ] `docs/INDEX.md`

---

## D. 恢复与演练
- [ ] `docs/RECOVERY.md`
- [ ] `docs/RESTORE-DRILL-TEMPLATE.md`
- [ ] 至少一条真实演练记录（当前是 `RESTORE-DRILL-0001.md`）

---

## E. 事故、盲区、依赖
- [ ] `docs/BLIND-SPOTS.md`
- [ ] `docs/INCIDENT-LEDGER.md`
- [ ] `docs/OBSERVERS.md`
- [ ] `docs/DEPENDENCIES.md`
- [ ] `docs/LIVE-READBACK-LEDGER.md`
- [ ] `docs/CHANGELOG-BOOTSTRAP.md`

---

## F. 真抄本
- [ ] `agents/gate-audit-quinn.md`
- [ ] `agents/drift-devon.md`
- [ ] `vendor/ci-workflows/report.yml`
- [ ] 每一份真抄本都在 `LIVE-READBACK-LEDGER.md` 里有最后读回时间

---

## G. 仍然需要仓外或人工补证的项
- [ ] skill summary 自动触发归因
- [ ] ClickUp UI-only 字段
- [ ] agent 工具显示名 / UI 标签
- [ ] prompt 里的散文在仓外改动后仍然为真
- [ ] 解释性注释没有在重写中消失

> 这些不是“忘了做”，而是**当前仍然不能只靠仓内文件证明**。恢复时要明确承认，不许装成已覆盖。

---

## H. 恢复完成前最后问自己三句
- [ ] 我恢复的是文件，还是恢复了“这份文件最后一次和真身对上是在什么时候”？
- [ ] 我现在手里的绿灯，证明的是“真输入会绿”，还是也证明了“坏输入会红”？
- [ ] 哪些东西我只是抄回来了，哪些东西我真的读回真身核过了？

---

## 一句话标准

> 只有当 A 到 F 都能打勾，且 G 被诚实写明，这次恢复才算“像样”，不只是“文件回来了”。
