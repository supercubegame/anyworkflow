# anyworkflow

离线备份仓：不是备份某一个项目，而是备份**这套工作流本身**。

## 这里备份的是什么
- Agent 自验证流水线的方法论
- GitHub MCP + ClickUp Skills 的闭环结构
- 观察者分工（Quinn / Devon）
- 回写、心跳、台账、恢复步骤、已知盲区
- 这套东西曾经怎么坏过，以及后来怎么把那种坏法钉成断言

## 这里不假装备份了什么
- live ClickUp 真身
- live Super Agent 当前 UI 配置
- 技能会不会靠 summary 自动触发
- 其它仓库此刻的真实状态（除非另有读回证据）

## 最小闸门
这份仓库现在有一条最小闸门：`python3 verify.py`

它只守最基本的诚实：
- `AGENTS.md` 与 `CLAUDE.md` 必须逐字相同
- `docs/RECOVERY.md` 必须存在
- `docs/BLIND-SPOTS.md` 必须存在
- `manifest.json` 顶层键必须齐全
- `not_backed_up` 不许是空数组

这条闸门还不够硬，但它至少能防一种最蠢的坏：**把盲区清单清空了，备份看起来更完整，而仓库一句话都不说。**

## 下一步该往里放什么
1. 完整工作流程说明
2. 离线备份方案说明
3. 观察者分工与节奏
4. 共享 workflow / 心跳 / cross-repo / 恢复演练台账
5. 已知限制与真空白清单
