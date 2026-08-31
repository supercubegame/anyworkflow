# 依赖台账

## 这份备份真正依赖哪些外部真身

这份仓库是离线抄本，不是活的系统。它要想恢复成真正会工作的那套链条，依赖的不只是文件，还依赖**仓外的真身、权限、时序和人手动作**。

## 一、GitHub 仓库依赖

### 承重仓库
- `supercubegame/clickup-brain-backup`
- `supercubegame/TodoX`
- `supercubegame/flappycat`
- `supercubegame/meetnote`
- `supercubegame/jumpwow`
- `supercubegame/image-grabber`
- `supercubegame/crossyroad`
- `supercubegame/ci-workflows`

### 为什么这些是承重依赖
- `clickup-brain-backup` 是台账与抄本中枢
- `ci-workflows` 是共享回写的单点
- 其余仓库**多数**各有至少一份 workflow 的 `uses:` 真行在调用共享回写，**而 `meetnote` 是例外**：它的 `verify.yml` 用 `actions/github-script` 自己写回，一行调用共享回写的 `uses:` 都没有。它仍然是承重依赖（Quinn 每天点名看它），但**不是共享回写的消费者**。
- 谁是消费者、各有几份，**只看 `docs/SHARED-WRITEBACK-CONSUMERS.md`**。这页不再复述那份清单。

### 这一节为什么重写
原来这张表漏了 `crossyroad`。那不是小疏忽，是同一个形状的第二次：**手写清单永远追不上目录。**

第一次是 `flappycat`：有人拿一条只扫本仓 workflow 的断言，去论证「多消费者分叉不会发生」，而恰好漏掉了一个已经在用 `@main` 的消费者。第二次就是这里：一张写着「哪些是承重仓库」的表，把一个真实消费者漏在外面，而整份备份仓没有任何东西会红。

**而“记得以后别漏”这条修法，2026-08-31 被第三次否证了。** 原来这一节有一张手写表，写着「一共 15 份、分布在 7 个仓」，**而它自己列出来的只加得出 12 份**；`meetnote` 被算成了消费者，而它的 `verify.yml` 自己写回、没有一行调用共享回写；`TodoX` 那四份被写成「仍然钉在 f0fccd3f」，而它们早就跟着 `@main`。**三处假话住在同一节里，而整份备份仓没有任何东西会红。**

**所以那张表整段删掉了，不是把数字重打一遍。** 两份表就是这个病本身：补字只能把下一次漂移往后推。消费者集合的真值只有一处 —— `docs/SHARED-WRITEBACK-CONSUMERS.md`，它由 `verify.py` 里的 `CONSUMER_FILES` 渲染，**而两侧是否相等有一条断言在守**。

**那份生成物也不是真派生的，这一点必须写清，别拿它当闭合。** 它渲染自一份手写字典，所以「字典错了就渲染出一份配套错的文件而检查照绿」这条路仍然开着 —— 而它真的走过两次：先是 `meetnote` 在字典里挂了几周，后来是三个 CI 补丁器一份都没被数进去。真正的派生需要跨仓令牌，而这道离线闸门没有。**它唯一强过这页的地方是：相等这件事有断言，而这页从来没有。**

## 二、共享 workflow 依赖

### 单点
- `supercubegame/ci-workflows/.github/workflows/report.yml`

### 依赖性质
- 这是所有回写逻辑的共享单点
- 它决定 PR 评论 / commit 评论 / 降级报告 / attest 回头核对 是否成立
- 它自己必须有 selftest；否则“守别人送达”的那一层会安静失效

### 当前备份策略
- 这份 repo 里已归档一份当前抄本：`vendor/ci-workflows/report.yml`
- 但归档拷贝只证明“上次读回时它长这样”，证明不了远端主干此刻还是这样
- 所以需要外部观察者和带期限的读回时间戳

### 版本策略：分叉已经没有了
2026-08-31 逐仓读回真文件：**六个消费者仓的 14 份 workflow 全部跟随 `@main`，一处 pin SHA 都不剩。**

`TodoX` 那四份是 2026-08-16 从钉 SHA 改过来的，而 TodoX 自己的快闸门现在有一条断言要求那几行**恰好是 `@main`、且不许是 40 位 SHA** —— 防的正是有人偷偷钉回去。

**所以上面原来那句「分叉集中在 TodoX」是反的，而它在这页上活了两周。** 换个方向记：这页不再登记「谁跟哪个引用」，那件事归 TodoX 自己的断言和那份生成物。这页只登记**跟随 `@main` 的代价**，因为那条风险本仓断言覆盖不了 —— 上游改一行这边行为就跟着变，而闸门不会红。它的落点在仓外：备份仓 `manifest.writeback.upstream_read_at` 那道 30 天期限，以及 Quinn 每天读回上游主干。

## 三、ClickUp 真身依赖

### 承重观察者
- `闸门审计 Quinn`
- `Drift Devon`

### 承重技能
- `AGENT 自验证流水线`
- `Gate Pitfalls Archive`
- `Mutation Check Assertions`

### 为什么它们不能只靠抄本
- skill summary 是否真的触发，只能在 live 对话里证明
- agent 的 schedule、工具、UI-only 字段，抄本只能证明“上次有人这样导出过”
- prompt 是否仍然为真，可能会被别的仓库改动推翻

## 四、权限与手动动作依赖

### 必须手动给的权限
- GitHub Actions 写权限（否则回写评论根本送不出去）
- 跨仓访问令牌 / mirror token / 相关 secrets
- Pages / deploy / environment 类配置

### 为什么这些不能省
- 这类依赖坏掉时，最危险的形状是“闸门本体绿了，但结论没人读得到”
- 所以恢复时必须把“权限已给到”视为和“文件已恢复”同等重要的一半

## 五、外部证据依赖

### 需要仓外或系统外证明的东西
- Actions 运行记录是否真的存在
- 定时任务是否真的触发
- 某次运行的外部时间戳
- 别的仓库当前文件内容
- 人工截图（UI-only 字段、未知工具、用量页）

### 为什么这些值钱
因为它们能把：
- “我以为现在几点”
- “抄本写着是这样”
- “代码里还留着 cron 那行”

变成外部证据，而不是自言自语。

## 六、恢复时的最短顺序
1. 确认 GitHub 仓库在
2. 确认 shared workflow 仓在
3. 恢复 workflow 文件与规则文件
4. 给回写权限和 secrets
5. 恢复承重 agent prompt 与 schedules
6. 手动验一次写入链路
7. 再等一次真实 schedule
8. 最后回写台账，承认哪些仍然是 blind spots

## 七、这份依赖台账在防什么
它防的是一种很常见的错觉：

> 文件都在，所以系统就在。

不对。文件只是壳。真正让它活着的，是：
- 共享 workflow 还在
- 权限还在
- 定时真的会跑
- 评论真的送达
- 观察者还在说真话
- 真值不在本仓库里的那几处，还有人去外面读
