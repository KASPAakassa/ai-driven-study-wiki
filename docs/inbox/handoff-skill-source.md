# 原始资料:handoff:把上下文压成接力文档

> 来源:微信公众号「AI普惠」日更 Research Note;Skill 来源:Matt Pocock skills 仓库 skills/productivity/handoff/SKILL.md
> 原文链接:https://mp.weixin.qq.com/s/2GmN8lCjbTJLf_bQyd29yw;Skill:https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff;Raw:https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/handoff/SKILL.md
> 抓取日期:2026-08-09;状态:双章节沉淀——Skill 收藏进 docs/07-agent-coding/skills/handoff-skill.md,使用经验进 docs/07-agent-coding/experience/handoff-handover-methodology.md

---

AI 普惠日更 / Research Note
handoff：把上下文压成接力文档
`handoff` 值得进前十，因为它解决的是 AI 工作流里一个非常实际的问题：任务没做完，但上下文快散了。它要求把当前状态压缩成下一位 agent 能接住的交接件，而不是留一串又长又难读的聊天记录。

很多人开始把 AI 当成“能持续推进任务的同事”，但一到真正长任务，问题很快就出来了：
任务没做完，聊天已经很长。
下一轮还要继续，但上下文已经散了。
你不想重新解释一遍，也不想让下一位 agent 从头爬聊天记录。
`handoff` 这个 skill，解决的就是这个现实问题。
它的思路很简单：不要把交接理解成“把聊天记录全留着”，而要理解成“把下一轮必须知道的内容压出来”。
公开 `SKILL.md` 里有几个要求非常实用。
第一，交接文档要单独写出来，而不是继续埋在线程里。
第二，要有 suggested skills，也就是明确告诉下一位 agent：这件事接下来更适合用哪些 skill。
第三，不要重复已有需求文档、计划、架构决策记录、issue、commit 或 diff 的内容，而是直接引用路径或链接。
这三条放在一起，其实是在做同一件事：降低下一轮接手成本。
为什么我觉得这类 skill 很重要？
因为 AI 协作一旦变成长链路，真正稀缺的不是“再生成一点内容”，而是“让接力不中断”。
你可以把它想成异步工程协作里的交班单。
一个好的 handoff，不应该只是“我做到这里了”，而应该至少回答六个问题：
1目标是什么。
2已经确认了哪些事实。
3已经做了哪些改动或验证。
4还有哪些问题没解。
5哪些风险值得优先注意。
6下一步最适合调用什么 skill。
这特别适合多 agent 或跨天工作。
比如你今天让 agent 排查 bug，已经建立了复现脚本、排除了两个假设、找到一个可疑模块，但还没修。这个时候最怕的不是停下来，而是明天重新花 20 分钟回忆“昨天到底做到哪了”。
如果有 `handoff`，你就能把这 20 分钟压缩成 2 分钟。
今天如果你要试，可以在每次阶段性完成后触发一次：
“把当前任务整理成 handoff。面向下一位 agent。列目标、现状、已完成、未完成、风险、建议 skill。不要复制已有计划和 diff，只引用路径。注意脱敏。”
这个用法的价值，不是文书漂亮，而是形成工作记忆。
很多团队已经开始接受 AI 参与执行，但还没真正为“AI 如何交接”建立习惯。
`handoff` 这个 skill 恰好补了这块。
任务能不能持续推进，往往不取决于单轮表现有多亮眼，而取决于上下文能不能被稳稳接住。
主图：把任务说明、工具执行、来源检查和人工确认串成一条可控工作流。

一条可直接复制的提示词
章节图：这一节用一张图帮助读者快速抓住结构。

你可以直接这样要求 agent：
“把当前线程整理成 handoff。目标是让下一位 agent 10 分钟内接手。请写清目标、输入、输出、边界、确认点、权限和来源。引用现有 issue、PR、diff、review、测试结果和代码路径，不要重复抄写。最后附一份下一步清单和建议 skill。”
这条提示词的重点，不是摘要，而是交接格式。
最适合放在哪些环节
章节图：这一节用一张图帮助读者快速抓住结构。

我会建议把 `handoff` 放在这几种场景：
第一，GitHub 上一个 PR 还没 ready，但已经有 issue、diff、测试和 review 线索。
第二，一段代码排查做了一半，已经形成来源和证据，但你准备明天再接。
第三，任务准备从一个 agent 交给另一个 agent，或者交回给人。
这时候 handoff 不是“顺手总结”，而是正式交班。
一份够用的交接清单
章节图：这一节用一张图帮助读者快速抓住结构。

一个能用的 handoff，至少要让接手方立刻看到：
1目标是什么
2输入有哪些
3输出到哪里
4边界是什么
5确认点有哪些
6涉及什么权限
7依据哪些来源
8下一步清单是什么
如果一份 handoff 连这几项都没有，那它更像聊天摘录，不像接力文档。
放到整个 AI 工作流里看，handoff 的意义就是：每次行动都留下边界、来源和下一步入口，而不是把上下文重新打散。
一个好的 handoff 还应该告诉接手方：下一步先读哪个 issue，先看哪个 PR，先对哪段代码和测试做 review，哪些 diff 可以忽略，哪些权限不能越界。这样它才不只是总结，而是真正的接力工具。
来源
GitHub：mattpocock/skills `skills/productivity/handoff/SKILL.md`
https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff
GitHub Raw：`handoff` skill 原文
https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/handoff/SKILL.md