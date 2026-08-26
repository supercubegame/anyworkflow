# Live Readback Ledger

这份台账不是在说“这些文件现在在仓库里”。
它在说：**这些抄本最后一次从真身读回是什么时候。**

如果没有这张表，离线备份最容易发生的坏法就是：

> 抄本还在，看起来很完整，但已经和真身一起过时了。

---

## 为什么这张表单独存在

`agents/*.md`、`vendor/ci-workflows/report.yml`、以及以后会放进来的其它真抄本，
都不是“存在就够了”的文件。它们的价值来自两件事：

1. 你知道它们是从哪一个真身读回来的
2. 你知道那次读回发生在什么时候

没有第 2 条，它们会安静地变成旧纸。

**而这里现在只负责“给人读”，不再自己承诺新鲜度规则。**
新鲜度的真源已经搬到 `manifest.true_copies` 里：
- 每份抄本的 `readback_at`
- `max_readback_age_days`
- 那条会红的新鲜度断言

这页以后如果再自己写一遍“上限是多少天、还剩多少天”，就是第二份台账，迟早再长歪。

---

## 当前已归档的真抄本

### 1. Quinn prompt
- 文件：`agents/gate-audit-quinn.md`
- 真身：ClickUp Super Agent `闸门审计 Quinn`
- 读回方式：live agent 配置读回后导出
- 最后读回时间（外部时间）：2026-08-17T08:26:47Z
- 证据来源：归档提交 `74517f9`
- 当前内容类型：**全文 prompt**
- 说明：这是当前真 prompt 的离线副本，不是摘要

### 2. Devon prompt
- 文件：`agents/drift-devon.md`
- 真身：ClickUp Super Agent `Drift Devon`
- 读回方式：live agent 配置读回后导出
- 最后读回时间（外部时间）：2026-08-17T08:27:05Z
- 证据来源：归档提交 `76ad05c`
- 当前内容类型：**全文 prompt**
- 说明：这份副本已经包含“第二只眼，不是第二个喇叭”的收紧版

### 3. Shared writeback workflow
- 文件：`vendor/ci-workflows/report.yml`
- 真身：`supercubegame/ci-workflows/.github/workflows/report.yml@main`
- 读回方式：GitHub 真文件读回后归档
- 最后读回时间（外部时间）：2026-08-17T08:23:58Z
- 证据来源：归档提交 `696b1bb`
- 当前内容类型：**全文 workflow 文件**
- 说明：它只证明“那次读回时主干长这样”，证明不了远端主干现在还是这样

---

## 机器真正会看的地方

这页现在**不再自带期限**。机器看的真源是 `manifest.true_copies`：

- `copies.<path>.readback_at`
- `max_readback_age_days`
- `copies.<path>.required_sections`
- `copies.<path>.anchors`

也就是说：

- 这页给人快速读
- `manifest.json` 给闸门下判词

**别反过来。** 让散文去宣布“现在还剩几天”，迟早会变成假话，而闸门不会知道它假了。

---

## 目前只有摘要、不算全文抄本的东西

### 1. 观察者分工模型
- 文件：`docs/OBSERVER-PROMPTS.md`
- 性质：摘要
- 为什么不是全文：它守的是分工结构，不是逐字级 prompt 恢复
- 风险：摘要可以防“角色漂了”，防不了“措辞漂了”

---

## 还没有真抄本、以后可能要补的东西

- 其它承重 Skills 的当前正文全文
- 其它承重 agent 的当前 prompt 全文（如果以后新增）
- 任何 shared workflow 的上游自测说明与 selftest 定义

---

## 这张表不证明什么

- 不证明 skill summary 自动触发
- 不证明 ClickUp UI-only 字段
- 不证明 prompt 里的散文在别的仓库改动后仍然为真
- 不证明仓外真身现在还没变
- 不证明这些抄本**此刻**还没过期：那条判词已经交给 `manifest.true_copies` 的新鲜度断言

这些都需要仓外读回、人工截图、或新的 live 验证证据。

---

## 更新规则

1. **改真身和同步抄本，是一件事的两半。**
2. 只有真的读回过真身，才能刷新这张表的时间。
3. “顺手改了几句说明文字”**不许**刷新这张表的时间，那会把一条活的时间戳变成涂绿工具。
4. 如果某个文件其实只是摘要，必须在这张表里明说它不是全文抄本。
5. **别在这页再写一份期限规则。** 期限、剩余天数、过不过期，统一看 `manifest.true_copies`。

---

## 一句话总结

> 这张台账守的不是“文件在不在”，而是“这份抄本最后一次和真身对上，是哪一天”；而“这一天现在算不算过期”，已经交给 `manifest.true_copies` 那条会红的断言。
