# 离线备份方案

## 四层

### 1. 真身
GitHub 仓库、ClickUp Skills、Super Agents、PR/commit 评论、Pages、heartbeat 文件。
这些东西会变，而且很多变化不会主动喊。

### 2. 抄本
skills markdown、agent JSON、workflow 文件、导出的 prompt、文档。
这些是闸门能真正读到的东西，但**抄本不是真身**。

### 3. 台账与运行时真表
manifest 分片、合表脚本、非空守卫、cross_repo、writeback ledger、verified_against_live。
这层守的是“别让备份安静地说谎”。

### 4. 外部观察者
Quinn、Devon、人工截图、外部时间戳、真仓库读回。
有些真值只能在这层拿到。

## 这套备份真正防的是什么
不是“文件在不在”，而是：
- 键还在，数组被清空
- 抄本和登记表彼此自洽，但和真身一起过时
- 记录值没人重读，期限被顺手往后挪
- 做完了还挂着，清单没人再读

## 还不能自动证明的东西
- skill summary 自动触发
- ClickUp UI-only 配置
- agent 界面里每个工具显示什么名字
- prompt 里的散文在别的仓库改动后是否仍然为真
- 解释性注释是否在重写里消失
