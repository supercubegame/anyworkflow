<p align="center">
  <img src="./assets/logo-1080.png" alt="anyworkflow logo" width="120" />
</p>

<h1 align="center">anyworkflow</h1>

<p align="center"><strong>用证据驱动构建、验证与交付的 Agent 工作流。</strong></p>

<p align="center"><a href="./README.md">English</a> | 简体中文</p>

---

## 快速开始

如果你想用最短路径，从零搭出第一版可运行闭环，按这个顺序做：

1. 建三个仓库：一个共享回写仓、一个项目仓、一个离线备份仓。**按这个顺序建。**
2. 共享回写仓**设为 public**，除非你有别的理由。私有的 reusable workflow 要额外配访问权限，别的仓才调得动。
3. 在共享回写仓：Settings -> Actions -> General，把 **Workflow permissions** 设成 **Read and write permissions**，并勾上 **“Allow GitHub Actions to create and approve pull requests”**。
4. 配好需要的 secrets 和 tokens。**跨仓令牌只有在仓库是私有时才需要。**
5. 把共享 report workflow 搭好，**并给它自己配一条闸门**。一份没有闸门的共享 workflow，是一个会安静失效的单点。
6. 在 ClickUp 里**安装**那个已有技能，不要重新创建一个。打开 Skills Hub（Home 侧栏 -> Skills，或 AI Hub -> Skills），点开技能，用右侧栏的 **+ Install**，或者列表里的 **Installed for** 那一栏。在对话里跟 Brain 说「create a skill」会新建一个空技能，那是另一件事，**也是新工作区里最常走错的一步**。
7. 用一条适合 Agent 的新对话提示词启动项目。
8. 拿到第一条 green PR。
9. 再拿到一次 deliberate red -> green 负向证明，**并确认那次 red 的报告也真的送达了**。
10. 给真抄本记下 live readback 时间。
11. 最后把整套东西回写进像本仓这样的离线备份仓。

如果你要走完整路径，直接看：
- [`docs/BOOTSTRAP-FROM-ZERO.md`](./docs/BOOTSTRAP-FROM-ZERO.md)
- [`docs/SETUP-CHECKLIST.md`](./docs/SETUP-CHECKLIST.md)
- [`docs/PROMPT-EXAMPLES.md`](./docs/PROMPT-EXAMPLES.md)

想看一个真的从零开始的人怎么走完这一遍？[`docs/STRANGER-WALKTHROUGH-0001.md`](./docs/STRANGER-WALKTHROUGH-0001.md)

---

## 技能：安装、备份、恢复

把这套方法带进对话里的东西就是技能，所以新工作区必须先装上它，下面那些示例提示词才会按本仓描述的样子工作。

- Skills Hub 需要管理员先启用 **AI** 与 **Custom Skills** 两个 ClickApp。
- **分享不等于安装。** 分享只是让别人能打开、能读；安装才会让 Brain 自动加载它。通常两件都要做。
- **截至 2026-09-01，在 ClickUp 官方文档里没有找到技能的导出或导入功能。** 找到的内置项只有 Copy link、Copy ID、Duplicate、Description history 和 Sharing，没有任何一项能给你一个可以搬进另一个工作区的文件。
- **但正文是读得回来的。** 每个技能都是自动生成的 Skills Space 里的一个任务，所以指令正文可以读回来存成文件。备份仓 `skills/` 目录就是这么填的。
- **这条读回通道是内容级真抄本，不是字节级真抄本。** 2026-09-01 在一个技能上实测：仓里那份 3080 字节，读回来 3070 字节；把项目符号和空行归一化之后，两侧完全相同，各 3056 个字符。所以散文可信、原始字节不可信,这也是技能正文没法像仓库文件那样用 blob 自证的原因。
- **恢复顺序：先子技能，后父技能。** 父技能正文里按名字引用子技能，而父子关系是人工重建的。正文要逐字粘贴，包括富文本残留，否则备份仓里登记的锚点会失配。

---

## 你会得到什么

这份仓库给你的不是 live 系统本身，而是：
- 一份离线、可审计的 workflow 抄本
- 完整的 setup / recovery 文档
- 关键 prompt 与 shared workflow 的真抄本归档
- green 与 red -> green 两层证据
- 一张明确写清“哪些还不能只靠仓内证明”的边界清单

它**不假装**自己就是 live 系统。

---

## 示例提示词

你可以用这些提示词测试一个新对话会不会自然走进这套工作流：

- “做个 2D 小游戏，自己把质量关好，我不想手动帮你验。”
- “做个简单网页工具，功能别花哨，但要自己把交付质量关好。”
- “做个 Chrome 扩展原型，先把质量和验证链条搭好，再做功能。”

更多见：[`docs/PROMPT-EXAMPLES.md`](./docs/PROMPT-EXAMPLES.md)

---

## 教程

如果你今天要从零开始，按这个顺序读：

1. [`docs/BOOTSTRAP-FROM-ZERO.md`](./docs/BOOTSTRAP-FROM-ZERO.md)
2. [`docs/SETUP-CHECKLIST.md`](./docs/SETUP-CHECKLIST.md)
3. [`docs/FULL-WORKFLOW.md`](./docs/FULL-WORKFLOW.md)
4. [`docs/DEPENDENCIES.md`](./docs/DEPENDENCIES.md)

---

## 如何验证它不是摆设

这份仓库现在已经有三层不同强度的证据：

### 结构证据
文件、台账、规则都在。

### 正向证据
[`docs/VERIFY-EVIDENCE-0001.md`](./docs/VERIFY-EVIDENCE-0001.md) 证明最小闸门真的在 live CI 里跑绿过一次。

### 负向证据
[`docs/VERIFY-EVIDENCE-0002.md`](./docs/VERIFY-EVIDENCE-0002.md) 证明最小闸门真的会对有意义的坏输入亮红灯，修回去后再恢复绿。

最小闸门本体是 `python3 verify.py`。

它守什么、故意不守什么，看：
[`docs/MINIMAL-GATE.md`](./docs/MINIMAL-GATE.md)

---

## 当前边界

这份仓库**没有装作**自己能证明一切。

当前仍然不在仓内直接证明范围里的有：
- 技能是不是靠 summary 自动触发
- ClickUp 的 UI-only 字段
- agent 界面里工具的显示名
- prompt 里的散文在别的仓库改动后是否仍然为真
- 解释性注释是否在多轮重写里静悄悄消失

见：[`docs/BLIND-SPOTS.md`](./docs/BLIND-SPOTS.md)

---

## 恢复

如果你是拿这份仓库来恢复整套系统，从这里开始：

1. [`docs/RECOVERY.md`](./docs/RECOVERY.md)
2. [`docs/RECOVERY-CHECKLIST.md`](./docs/RECOVERY-CHECKLIST.md)
3. [`docs/RESTORE-DRILL-TEMPLATE.md`](./docs/RESTORE-DRILL-TEMPLATE.md)
4. [`docs/RESTORE-DRILL-0001.md`](./docs/RESTORE-DRILL-0001.md)

---

## 深入文档

- 工作流总览：[`docs/FULL-WORKFLOW.md`](./docs/FULL-WORKFLOW.md)
- 离线备份方案：[`docs/OFFLINE-BACKUP-SCHEME.md`](./docs/OFFLINE-BACKUP-SCHEME.md)
- 观察者分工：[`docs/OBSERVERS.md`](./docs/OBSERVERS.md)
- 依赖台账：[`docs/DEPENDENCIES.md`](./docs/DEPENDENCIES.md)
- 事故台账：[`docs/INCIDENT-LEDGER.md`](./docs/INCIDENT-LEDGER.md)
- 真抄本读回时间账本：[`docs/LIVE-READBACK-LEDGER.md`](./docs/LIVE-READBACK-LEDGER.md)
- 建仓过程记录：[`docs/CHANGELOG-BOOTSTRAP.md`](./docs/CHANGELOG-BOOTSTRAP.md)
- 完整索引：[`docs/INDEX.md`](./docs/INDEX.md)

---

## 一句话说明

一份可读、可审计的 Agent 验证工作流离线备份。
