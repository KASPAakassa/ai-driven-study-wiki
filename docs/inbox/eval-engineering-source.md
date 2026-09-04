# 原始资料:LangChain 刚开源了个 Eval Engineering Skill

> 来源:微信公众号(作者:seebin),《LangChain 刚开源了个 Eval Engineering Skill,专门用来评估你开发的 Agent 质量》
> 原文链接:https://mp.weixin.qq.com/s/HpejKK3-rbYbqPmG3RuB-Q
> 抓取日期:2026-08-09;状态:已拆解为两篇文章:07-agent-coding/skills/eval-engineering-skill.md(Skill 收藏)+ 03-agents/agent-eval-driven-dev.md(评估驱动开发基础)
> 相关:https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/eval-engineering

---

做 Agent 开发最痛苦的事是什么？

不是调 prompt，不是选模型，是评估。

你的 Agent 改了提示词，到底变好了还是没变好？换了模型，新版本真的更强？加了个工具，是进步了还是退步了？你心里没底。

不是不想评估，是手写评估太累了。而且写出来的东西经常和真实场景对不上。你精心设计的测试用例，生产环境里根本不会出现。真正出问题的场景，你的测试又没覆盖到。这中间的鸿沟一直在那里。

今天 LangChain 开源了一个新东西，叫 Eval Engineering Skill。装进 Claude Code 或 Codex 之后，它能自己读懂你的代码仓库，分析真实运行轨迹，然后帮你设计出一套可执行的评估测试。

不是一键生成，是跟你一起迭代。

它到底在解决什么问题

做 Agent 的人都有三个痛点。

第一个，评估和真实使用脱节。你手写的测试用例是凭经验猜的，但生产环境里用户怎么用、Agent 在哪里翻车，你其实不知道。

第二个，生产 traces 里藏着金矿。Agent 每次运行都会留下轨迹，工具调用了什么、返回了什么、哪里出错了，全在里面。但这些信息很难转化成系统性的测试。

第三个，改了东西没法快速验证。你换了模型、调了 prompt、加了工具，怎么知道是真的变好了还是引入了新问题？靠感觉不行，靠手动测试又太慢。

它的工作方式

这个 Skill 的工作流程分四步。

先读代码仓库。它自动扫描你的 Agent 仓库，识别出 prompt、模型、工具、API 调用这些组件，搞清楚整个 Agent 的结构。

再分析 traces。如果你提供了生产环境的运行轨迹，它会从里面提取真实的工具调用参数、返回结果、错误信息，还原 Agent 在生产环境里的真实行为。

然后是它最聪明的设计，"面试"。它不是一次性生成一堆测试，而是先提出几个值得测试的能力方向，然后通过对话跟你确认。哪些工具要真实调用？哪些需要模拟？哪些能力最值得测？你来拍板。

最后输出标准的 Harbor 格式评估。每个评估包含三个部分。Instruction，给 Agent 的任务指令。Environment，用 Dockerfile 定义的可复现环境。Verifier，验证器，判断任务是否真正完成。

为什么不能一键生成

团队发现一个反直觉的事实。最好的评估，几乎都是经过多轮反馈才出来的。

尤其是验证器，第一版特别容易被 Agent 钻空子。他们会观察到几种典型作弊方式。过度引用无关文档来刷分。假装完成了某个动作其实没做。利用暴露的答案信息走捷径。

怎么修？同时看 Agent 的运行轨迹和验证器的运行轨迹，快速定位问题，然后修正。

这背后有个更大的想法

LangChain 团队提了一个持续学习的闭环。

从生产 traces 里挖出真实问题，转化成评估测试，用测试驱动 Agent 改进，改进完再跑评估验证。评估变成了 Agent 的训练目标和回归测试集。

环境是容器化的，模型、提示词、工具版本可以随意替换对比，信号更干净，迭代更快。

他们在自己的文档问答 Agent chat-langchain 上跑过这套流程。在 Terminal-Bench 2.0 上，光靠调整 harness（提示词、工具、编排策略），在评估指标上 hill-climbing，就拿到了 13.7% 的提升。没换模型，没做微调，就是更好的 harness engineering 加上评估驱动。

怎么用

代码开源在 langchain-ai/langchain-skills。

装进 Claude Code 或 Codex，打开你要评估的 Agent 仓库，可选提供 traces，然后用一句话启动。

启动之后它会先读你的代码仓库，提出几个评估方向让你选，你选完它帮你建好完整的评估任务，跑一遍，看结果，再迭代。

所以呢

如果你在认真做 Agent 工程，不是只调几句 prompt，这个工具值得试试。

评估不该是上线前的临时检查，而应该是开发流程的一部分。每次迭代都从真实数据里挖出问题，用标准化评估锚定改进方向，这才是持续进步的方式。
GitHub 仓库地址： https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/eval-engineering

—精选文章—
Karpathy谈AI未来：大模型会越来越小，教育会越来越重要

AI 自纠错循环：一个三角色架构，让模型自己发现错误

吴恩达做了一个桌面应用 OpenWorker，要把 AI 从「聊天工具」变成「真正的同事」

Replit 的自驱动公司：像自动驾驶汽车一样自己运营