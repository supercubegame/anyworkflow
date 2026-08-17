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
- `supercubegame/ci-workflows`

### 为什么这些是承重依赖
- `clickup-brain-backup` 是台账与抄本中枢
- `ci-workflows` 是共享回写的单点
- 其余几个仓库是 Quinn 每天读回的真实消费者，证明 shared workflow 和观察链条没有只在一个仓库里成立

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
