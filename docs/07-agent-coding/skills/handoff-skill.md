# handoff Skill:把上下文压成接力文档

> **一句话摘要**:任务没做完,但上下文快散了——这是长链路 AI 协作最实际的痛点。`handoff` skill(Matt Pocock skills 仓库 `skills/productivity/handoff`)把交接理解为"把下一轮必须知道的内容压出来",生成下一位 agent 能直接接住的接力文档,而不是留一串又长又难读的聊天记录。
>
> **来源**:微信公众号「AI普惠」《handoff:把上下文压成接力文档》,https://mp.weixin.qq.com/s/2GmN8lCjbTJLf_bQyd29yw;Skill 源码:https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff;原始资料存档于 `docs/inbox/handoff-skill-source.md`

## 概念:为什么要一个"交接"专用 Skill

很多人开始把 AI 当成"能持续推进任务的同事",但一到真正长任务,问题立刻出现:任务没做完、聊天已经很长;下一轮还要继续、上下文已经散了;不想重新解释一遍,也不想让下一位 agent 从头爬聊天记录。

!!! tip "核心思路"
    不要把交接理解成"把聊天记录全留着",而要理解成"**把下一轮必须知道的内容压出来**"。AI 协作一旦变成长链路,真正稀缺的不是"再生成一点内容",而是"**让接力不中断**"。

## 原理:SKILL.md 的三个硬要求

公开的 SKILL.md 里有三个非常实用的要求,合起来是在做同一件事:**降低下一轮接手成本**。

1. **交接文档要单独写出来**,而不是继续埋在线程里;
2. **要有 suggested skills**——明确告诉下一位 agent:这件事接下来更适合用哪些 skill;
3. **不要重复已有需求文档、计划、架构决策记录(ADR)、issue、commit 或 diff 的内容**,而是直接**引用路径或链接**。

!!! note "为什么引用路径而不是复制内容"
    复制会把上下文越堆越长,而且复制的内容会过时(源文件更新后,复制件变成误导)。引用路径让下一位 agent 按需读取,交接文档保持精简、可信、可追踪——这也是 [OpenAI 官方 Prompt 指南](../experience/openai-prompt-guide.md)"Prompt 做减法"的同一原理在交接文档上的体现。

## 代码 / 实现:一份够用的交接清单(八项)

一个能用的 handoff,至少要让接手方立刻看到这八项。**如果连这几项都没有,它更像聊天摘录,不像接力文档。**

| # | 项 | 说明 |
| --- | --- | --- |
| 1 | **目标** | 任务要达成的最终结果是什么 |
| 2 | **输入** | 有哪些输入(数据、文件、线索) |
| 3 | **输出** | 输出到哪里(文件/PR/分支) |
| 4 | **边界** | 做什么、明确不做什么 |
| 5 | **确认点** | 哪些步骤需要人工确认 |
| 6 | **权限** | 涉及什么权限、哪些不能越界 |
| 7 | **来源** | 依据哪些 issue/PR/diff/测试/代码路径 |
| 8 | **下一步清单** | 先读哪个 issue、先看哪个 PR、先 review 哪段代码 |

## 实践 / 应用:怎么用

### 三句话的触发方式(阶段性完成后)

> "把当前任务整理成 handoff。面向下一位 agent。列目标、现状、已完成、未完成、风险、建议 skill。不要复制已有计划和 diff,只引用路径。注意脱敏。"

### 详细版提示词(可直接复制)

> "把当前线程整理成 handoff。目标是让下一位 agent 10 分钟内接手。请写清目标、输入、输出、边界、确认点、权限和来源。引用现有 issue、PR、diff、review、测试结果和代码路径,不要重复抄写。最后附一份下一步清单和建议 skill。"

!!! tip "重点是交接格式,不是摘要"
    这条提示词的价值不是"总结得好",而是把对话历史压缩成**有边界的接力文档**——每次行动都留下边界、来源和下一步入口,而不是把上下文重新打散。

### 最适合放 handoff 的场景

1. GitHub 上一个 PR 还没 ready,但已经有 issue、diff、测试和 review 线索;
2. 一段代码排查做了一半,已经形成来源和证据,但准备明天再接;
3. 任务准备从一个 agent 交给另一个 agent,或者交回给人。

!!! warning "什么时候不要用"
    handoff 是**正式交班**,不是"顺手总结"。短任务、一次性能完成的任务不需要交班文档;只有"上下文将被丢弃、任务尚未完成"时才值得生成——它压缩的是"下次接手要花的 20 分钟回忆",而不是文书工作。

## 总结

- **一句话定位**:handoff 把"下一轮必须知道的内容"压成接力文档,让任务跨 session、跨 agent、跨天持续推进;
- **三个要求**:单独成文、suggested skills、引用路径不复制内容;
- **八项清单**:目标/输入/输出/边界/确认点/权限/来源/下一步清单;
- **价值**:形成工作记忆——任务能不能持续推进,不取决于单轮表现有多亮眼,而取决于**上下文能不能被稳稳接住**。

## 延伸阅读

- Skill 源码:https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff;所属仓库:https://github.com/mattpocock/skills(参见站内 [Matt Pocock 的 Skills 集合](mattpocock-skills.md))
- 站内:[Agent 交接方法论](../experience/handoff-handover-methodology.md)(使用经验角度)、[Skill 收藏](index.md)、[Git Worktree 并行开发](../experience/git-worktree-parallel-agents.md)(任务契约的交接视角)、[OpenAI 官方 Prompt 指南](../experience/openai-prompt-guide.md)(做减法原则)
