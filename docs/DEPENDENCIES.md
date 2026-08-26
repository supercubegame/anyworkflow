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
- 其余七个仓库里，**至少各有一份 workflow 的 `uses:` 真行在调用共享回写**。它们不是按名字猜的，是逐个读 `.github/workflows/*.yml` 里的真文件读回来的。

### 这一节为什么重写
原来这张表漏了 `crossyroad`。那不是小疏忽，是同一个形状的第二次：**手写清单永远追不上目录。**

第一次是 `flappycat`：有人拿一条只扫本仓 workflow 的断言，去论证「多消费者分叉不会发生」，而恰好漏掉了一个已经在用 `@main` 的消费者。第二次就是这里：一张写着「哪些是承重仓库」的表，把一个真实消费者漏在外面，而整份备份仓没有任何东西会红。

**正确修法不是“记得以后别漏”。** 这页现在直接把当次读回到的真值写出来：

- `clickup-brain-backup`: `split-apply.yml`、`split-dry-run.yml`、`verify.yml`
- `TodoX`: `verify.yml`、`release.yml`、`screenshots.yml`、`mirror.yml`
- `flappycat`: `verify.yml`
- `meetnote`: `verify.yml`
- `jumpwow`: `verify.yml`
- `image-grabber`: `verify.yml`
- `crossyroad`: `verify.yml`

一共 **15** 份 workflow 文件，分布在 **7** 个消费者仓库里。这个数字是这次读回来数的，不是拍脑袋写的。

**但这页仍然不是机器派生的。** 它现在只是从“手写记忆”提升到了“带一次真读回的手写台账”。下次如果这些仓里又长出新的 workflow，这页**仍然会过期而全绿**。所以这张表最好的下一步不是继续补字，是把「消费者集合」本身变成一条断言或一份生成物。

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

### 当下读回到的真实消费者分布
按这次逐仓读回 `.github/workflows/*.yml` 的真实 `uses:` 行：

- **跟随 `@main`**：`clickup-brain-backup`（3 份）、`flappycat`（1 份）、`jumpwow`（1 份）、`image-grabber`（1 份）、`crossyroad`（1 份）
- **仍然钉在 `f0fccd3f`**：`TodoX` 的 `verify.yml`、`release.yml`、`screenshots.yml`、`mirror.yml`
- **不走共享 reusable workflow，而是自己写回**：`meetnote` 的 `verify.yml`

也就是说，这页现在能诚实地说：**版本策略真的还在分叉，而分叉目前集中在 TodoX。** 这不是从别的台账抄来的，是从那些仓自己的 workflow 真文件读回来的。

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
