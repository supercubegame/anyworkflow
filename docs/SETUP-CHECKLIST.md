# Setup Checklist

这份清单只列**必须手动确认 / 手动配置**的东西。

---

## A. GitHub 仓库与 Actions
- [ ] 已创建共享回写仓
- [ ] 已创建目标项目仓
- [ ] 已创建离线备份仓
- [ ] 仓库默认分支存在
- [ ] Actions 已启用
- [ ] Actions 对 PR / commit 评论有写权限
- [ ] 必要的 Pages / deploy 功能已启用（如果项目需要在线试玩）

---

## B. Secrets / Tokens
- [ ] 跨仓 token 已创建
- [ ] token 的授权范围覆盖目标仓
- [ ] token 不是在目标仓创建前就冻结了旧授权列表
- [ ] mirror / deploy / external API secrets 已填入正确仓库

---

## C. ClickUp 侧
- [ ] 技能已安装 / 可加载
- [ ] 承重 Super Agent 已存在
- [ ] schedule 已配置
- [ ] triggers 已配置
- [ ] 需要的 private knowledge 范围已给到

---

## D. 需要截图定案的项
这些不是每次都要，但一旦卡住，优先让人截图：
- [ ] agent 工具悬浮清单
- [ ] Actions 用量页
- [ ] agent 的 workspace knowledge 面板
- [ ] UI-only trigger 配置
- [ ] 任何“两个读取通道打架”的界面证据

---

## E. 首次跑通的最低证据
- [ ] 至少一条 green PR
- [ ] 至少一次 deliberate red -> green
- [ ] PR 评论路径通
- [ ] commit 评论路径通
- [ ] attest 真的确认过评论存在
- [ ] 如果有 schedule，手动写入链路验证过一次
- [ ] 如果有 heartbeat，真正的 scheduled 字段至少从 null 变成过一次时间戳

---

## F. 仍然不该装作已证明的东西
- [ ] skill summary 自动触发归因
- [ ] ClickUp UI-only 字段
- [ ] 仓外 prompt 散文在别的 repo 改动后是否仍为真
- [ ] 解释性注释有没有在多轮重写里消失

---

## 一句话标准

> 只要还有一项你必须靠猜、靠印象、或靠“它看起来没问题”来打勾，这次 setup 就还没真的完成。
