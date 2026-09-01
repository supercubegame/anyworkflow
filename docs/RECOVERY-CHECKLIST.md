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

<p><br/></p>

**技能正文，六份，住在备份仓 `clickup-brain-backup` 的 `skills/` 下。** 2026-09-01 补进这张清单：在那之前这一节只列了两个 agent 与共享 workflow，**于是整张清单可以全部打勾而一份技能都没恢复**。每条断言都承重，而技能这个属性压根没有断言在看,那是覆盖缺口，不是空断言，两者在报告上长得一模一样。

- [ ] `agent-self-verification-pipeline`（父技能，正文是 `skills/agent-self-verification-pipeline/` 下的**五个分片**，合起来 61181 字节；仓根那份同名 `.md` 是构建产物，2026-09-01 已从 git 摘掉）
- [ ] `gate-pitfalls-archive`（23565）
- [ ] `mutation-check-assertions`（22797）
- [ ] `cross-account-migration`（5469）
- [ ] `wechat-miniprogram-gate`（3981）
- [ ] `html-single-file-iteration`（3080）
- [ ] 父子关系人工重建：父技能有四个子技能，接口不会告诉你谁是谁的
- [ ] 每一份都在 `manifest/30-skills.json` 里有锚点，且锚点逐条命中

<p><br/></p>

**恢复顺序与判据，四条，缺一条这一节就只是「文件回来了」：**

1. **先子技能，后父技能。** 父技能正文里按名字引用子技能，反过来建会指向一个还不存在的东西。
2. **正文逐字粘贴，包括 `<p><br/></p>` 和 HTML 表格痕迹。** 「顺手清理格式」会让恢复变成重写，而且会让登记的锚点跟着失配。
3. **建完立刻读回来做 diff,而且要归一化之后再比。** 2026-09-01 实测：读回通道是**内容级真抄本，不是字节级**。同一份技能仓里 3080 字节、读回来 3070，差在项目符号、空段落标记、连续空行三处；归一化后两侧完全相同，各 3056 个字符。**所以别拿 blob 哈希去比技能正文** —— 它永远不等，而那不是漂移。
4. **先拿最小那份走通整条链路，再搬大的。** 从 `html-single-file-iteration`（3080）开始验粘贴 -> 读回 -> 归一化 diff -> 锚点核对；父技能 61181 字节而天花板 65536，余量只剩 4355，而粘贴长中文是登记在案的高危动作。

<p><br/></p>

**这一节做不到的事，写清楚而不是留白：** ClickUp 没有技能的导出或导入功能（截至 2026-09-01 在官方文档里没找到），所以这六项只能靠重建打勾,而「分享链接能不能跨账号直接安装」**没有试过**，别当成可行路径写进计划。

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
