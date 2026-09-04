# 科研领域现成 Skill 收藏:2026 最值得装的 8 个仓库

> **一句话摘要**:读论文、跑实验、改稿、做组会 PPT 的科研场景,有 8 个开源的 Agent Skill 仓库可以大幅减少重复劳动。本文收录并核验这 8 个仓库(来源作者已逐仓核验,本站再次核验链接),给出选装建议。
>
> **来源**:微信公众号《2026科研必备,最值得装的8个skills》(栗润腾,信息核验 2026-08-02),https://mp.weixin.qq.com/s/OUd9uMGogAsCflSfG2CFYA

## 概念:科研 Skill 是什么

科研 Skill = 把"读论文、写论文、做图、跑实验"的完整流程沉淀成 Agent 可调用的任务包(安装到 Codex / Claude Code 等 Coding Agent 中使用)。它们的共同价值:**把资深科研者的操作流程变成可复用资产**(呼应本站 [mattpocock/skills](mattpocock-skills.md) 的 SKILL 化思想)。

!!! note "归类说明"
    本页收录的 8 个仓库属于**科研垂直领域的现成 Skill 收藏**,与 [mattpocock/skills](mattpocock-skills.md)(通用工程)互补,同属 `07-agent-coding/skills/` 子主题的"可复用 Skill 索引"。

## 收录清单(8 个仓库)

| # | 名称 | 定位 | 仓库(本站核验) | Stars |
| --- | --- | --- | --- | --- |
| 1 | **Scientific Agent Skills** | 把任意 Agent 变成 AI 科学家;"#1 Agent Skills 库" | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 33.0k |
| 2 | **ARIS**(Auto-Research-In-Sleep) | 找缺口、生成想法、跑实验、审结果、下一轮迭代组成闭环 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 14.4k |
| 3 | **AI Research SKILLs** | 23 类 98 个 Skill,覆盖训练/微调/评测/推理/部署的 AI/ML 工程研究 | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 11.5k |
| 4 | **Research Paper Writing** | 轻量写作助手,检查章节结构、段落衔接、观点-证据对应 | [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills) | 5.9k |
| 5 | **PaperSpine** | 先确认贡献,再组织结果与全文,最后做审稿人视角审计 | [WUBING2023/PaperSpine](https://github.com/WUBING2023/PaperSpine) | 4.7k |
| 6 | **Paper Craft Skills** | 把论文继续做成方法图、深度文章和汇报 PPT | [zsyggg/paper-craft-skills](https://github.com/zsyggg/paper-craft-skills) | 995 |
| 7 | **ARS-Codex** | 研究、写作、审稿和实验规划的一体化入口 | 地址见原文图片(本站搜索未定位,待核验) | — |
| 8 | **Nature Skills** | 18 个 Skill,中文精读、润色、科研绘图和返修全覆盖 | 地址见原文图片(本站搜索未定位,待核验) | — |

!!! note "核验说明"
    #1-#6 仓库地址经 GitHub API 核验有效(2026-08-09);#7-#8 两个仓库在 GitHub 搜索中未定位到确切地址,以原文图片中的仓库地址为准,安装时以各自 README 为准(原作者也提醒:"仓库更新很快,安装时仍以各自 README 为准")。

## 原理:这些 Skill 解决什么

按科研流程拆解这 8 个仓库的分工:

| 科研环节 | 对应 Skill | 典型能力 |
| --- | --- | --- |
| 读论文 / 学方法 | Scientific Agent Skills、ARS-Codex | 精读、方法拆解、文献检索(100+ 数据库、70+ Python 包工作流) |
| 想 idea / 规划实验 | ARIS、ARS-Codex | 找研究缺口、生成想法、实验规划闭环 |
| 跑实验 / 训练调优 | AI Research SKILLs、Scientific Agent Skills | 训练/微调/评测/推理/部署的工程化流程 |
| 写论文 / 改稿 | Nature Skills、Research Paper Writing | 中文精读润色、章节结构、段落衔接、观点-证据对应 |
| 投稿返修 / 审计 | PaperSpine、Nature Skills | 审稿人视角审计、返修处理 |
| 做图 / 汇报 | Paper Craft Skills | 方法图、深度文章、组会 PPT |

## 实践 / 应用:怎么选、怎么装

**选装建议(原作者原话)**:

1. **先按"当前最痛的一个任务"选一个**,不要一次性全装——Skill 仓库动辄上百个文件,全装只会让上下文变脏、成本变高;
2. **安装时把仓库地址发给 Codex,并补一句**:

!!! tip "安装安全提示"
    安装时对 Agent 说:"**先检查依赖、权限和风险,只安装与我当前任务相关的 Skill。**"——呼应本站 [AI Friendly 后端架构](../../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 的"最小权限 + 风险检查"原则,第三方 Skill 仓库是新的信任边界。

3. 大仓库(如 Scientific Agent Skills 158 个 Skill、AI Research SKILLs 98 个)建议**只装子集**,按任务挑;
4. 安装后以各自 README 为准(仓库更新快)。

**本站使用建议**:把选中的 Skill 仓库 clone 到本地后,参照 [Skill 收藏收录原则](index.md) 建档——记录用途、适用工具、来源、依赖、使用方式,便于日后复用。

## 总结

- 8 个科研 Skill 仓库覆盖读论文/想 idea/跑实验/写论文/返修/做图全流程;
- 已核验 #1-#6 链接有效;#7-#8 待核验(以原文图片地址与 README 为准);
- **先选最痛的一个任务,不要全装**;安装时要求 Agent"先检查依赖、权限和风险";
- 与 [mattpocock/skills](mattpocock-skills.md) 互补,构成科研 + 工程的 Skill 收藏体系。

## 延伸阅读

- 站内:[Skill 收藏](index.md)、[mattpocock/skills](mattpocock-skills.md)、[Harness 章节](../../08-harness/index.md)
- 外部:原文(栗腾润,微信);各仓库 README;原始资料存档于 `docs/inbox/research-skills-source.md`
