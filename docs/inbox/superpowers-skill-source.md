# 原始资料:247k Star 的编程 Skills 被 Fable 5 重构了!Token 消耗降 60%、提速 50%

> 来源:微信公众号「关注AI开源项目」(智猩猩AI整理),介绍 Superpowers v6
> 原文链接:https://mp.weixin.qq.com/s/o4pgoT43L-zi3CDwi9sUng;项目:https://github.com/obra/superpowers;v6 公告:https://primeradiant.com/blog/2026/superpowers-6.html
> 抓取日期:2026-08-09;状态:已整合进 docs/07-agent-coding/skills/mattpocock-skills.md(编程 Skills 集合主题新增 Superpowers 姊妹章节),不单独成章

---

智猩猩AI整理
编辑：没方

这个收获 247k Star 的 Superpowers 不是突然冒出来的新项目。

项目链接：
https://github.com/obra/superpowers

上半年，它已经在 AI 编程圈火了一轮《34k Star！Claude skills项目superpowers开源，让智能体写出工程规范级代码》，很多 Claude Code、Codex、Cursor 用户把它当成“AI 编程外挂”来用，因为它能给 Coding Agent 装上一整套工程化开发流程——先澄清需求，再写计划，再用 TDD 实现，最后做代码审查和质量验证。

但项目作者 Jesse Vincent 在介绍 Superpowers 6 时提到，他们最常听到的用户抱怨，就是 Token 太贵，而 Superpowers 又会消耗大量 Token。同时，用它构建软件速度也会变得更慢。

来源：
https://primeradiant.com/blog/2026/superpowers-6.html

慢和贵虽然换来了更高质量，但它们依然会影响用户体验。对于重度使用 AI 编程工具的开发者来说，Token 成本不是抽象数字，而是真金白银。构建耗时也不是小问题，而是会直接影响开发节奏。

Superpowers 6 正是直面这些反馈的重大升级版本。

项目团队借助 Claude Fable 5，对 Subagent Driven Development 中最耗时、最耗 Token 的审查链路进行了重构与优化。在官方 Anthropic eval benchmarks 中，Superpowers 6 在保持代码质量的前提下，构建速度提升50%、token消耗降低60%。

此外，Superpowers 6 还扩展了新的harness支持，包括 Kimi Code、Pi 和 Antigravity，并改进了 Codex、OpenCode、Cursor 等已有工具的适配。

01

Superpowers 6重构子智能体
开发链路：质量、成本与
可控性的再平衡

Superpowers 6 的关键变化，发生在 Subagent Driven Development，也就是“子智能体驱动开发”这条链路上。

此前，Superpowers 为了保证质量，会在每个任务完成后让不同 reviewer 分别检查两件事：第一，代码是否严格实现了需求；第二，代码质量、测试覆盖、可维护性是否达标。

这个双审查流程很严谨，但也非常耗 Token。因为两个 reviewer 都需要读取上下文、理解任务、分析 diff，很多信息会被重复消费。

在 Superpowers 6 中，项目团队把这个流程改成了“一名 reviewer，一次读取，两类判断”。

也就是说，原来分开的 spec compliance review 和 code quality review 被合并成一个 task-reviewer-prompt。

新的 reviewer 在读取一次任务 diff 后，同时给出需求符合性和代码质量两个维度的判断。这样一来，一个修复轮次就可以同时处理两类问题，不再需要两个 reviewer 各跑一遍。

另一个很关键的优化，是把任务说明和 review diff 从“粘贴进上下文”改成“写入文件”。

过去，Agent 会把大段 diff 直接塞进上下文里，reviewer 也可能为了确认变化反复运行 git 命令。这会带来两个问题：一是 diff 会长期占据昂贵上下文，二是 reviewer 为了重建审查材料浪费大量工具调用和 Token。

Superpowers 6 新增了 task-brief 和 review-package 两个脚本，把任务文本、审查 diff 和相关元数据提前整理成文件，交给 subagent 读取。这也是它能够显著降本提速的重要原因之一。

Superpowers 6 还在计划阶段提前做了一次“预检”（pre-flight read）。在第一个任务真正开始前，controller 会先检查计划里是否存在内部冲突，或者是否包含后续 reviewer 会判定为缺陷的要求。这个设计很像真实工程团队里的方案评审，与其等代码写到一半才发现需求互相打架，不如在执行前一次性暴露问题。对长任务来说，这一步尤其重要，因为 Agent 一旦沿着错误计划跑下去，后续返工成本会非常高。

此外，过去很多 Skills 的描述方式带着明显的 Claude Code 口吻，比如“使用 Task tool”“写进 CLAUDE.md”。

在 v6 中，项目把这些表述改成更通用的动作，比如“派发一个 subagent”“写入你的 instructions file”，再通过不同 harness 的映射文件适配 Claude Code、Codex、Copilot、Pi、Antigravity 等环境。

来源：

https://github.com/obra/superpowers/blob/main/RELEASE-NOTES.md

02

安装教程 

安装教程非常简单，根据使用的AI编程环境选择对应方式：

Claude Code，可以直接通过 Anthropic 官方插件市场安装：

/plugin install superpowers@claude-plugins-official

Kimi Code，打开插件管理器：

/plugins
前往 Marketplace > Superpowers 并安装。
或者直接执行：

/plugins install https://github.com/obra/superpowers

其他编程智能体安装教程可参考：
https://github.com/obra/superpowers#installation

03

从模型能力到流程能力，
AI Coding进入工程化竞争阶段

Superpowers 6 没有牺牲质量去追求速度，而是通过 Fable 5辅助分析、审查流程合并、review package 文件化、计划预检、模型选择约束和跨 harness 适配，让原本沉重的子智能体开发链路变得更轻。

这其实代表了 AI Coding 工具发展的一个重要方向。早期大家关注的是“模型能不能写代码”，后来关注的是“Agent 能不能自主完成任务”，而现在真正进入日常开发后，问题变成了“Agent 能不能低成本、稳定、可审计地完成任务”。

Superpowers 6 给出的答案是，不能只靠更强的模型，还要靠更好的流程设计。

未来，编程工具的竞争可能不会只停留在补全速度、模型能力和上下文长度上，而会越来越关注 Agent 的工程组织能力。谁能把需求澄清、计划拆解、测试验证、代码审查、成本控制和多工具适配做成稳定基础设施，谁就更有机会成为开发者日常工作流的一部分。

END

关注+星标，获取AI前沿进展与优质开源项目