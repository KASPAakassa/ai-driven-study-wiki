# 原始资料:Context Engineering——比 Prompt Engineering 更重要的 Agent 省钱术

> 来源:微信公众号「昕悦技术栈」(作者:昕悦成福),《Context Engineering——比 Prompt Engineering 更重要的 Agent 省钱术》
> 原文链接:https://mp.weixin.qq.com/s/4zDq6EmX3YzvwC8SHHXNUg
> 抓取日期:2026-08-09;状态:已整理为正式文章 docs/03-agents/context-engineering.md

---

Context Engineering——比 Prompt Engineering 更重要的 Agent 省钱术
全文速览
Context Engineering 是 Prompt Engineering 的自然演进，管的是 agent 多轮推理时的整个上下文状态。四个杠杆：Write（外化）、Select（选取）、Compress（压缩）、Isolate（隔离）。不重视的代价是真金白银——一个 6000 token 的文件在 25 轮会话里被重读 24 次。管好上下文，agent 又准又省钱。

如果你这两年一直在跟 AI Agent 开发，应该有个感受：光会写 prompt 不够了。
2025 年下半年开始，工程圈越来越频繁地提一个词——Context Engineering（上下文工程）。Anthropic 的工程博客专门发了篇文章讲这个，标题叫 "Effective context engineering for AI agents"。核心论断一句话：随着 agent 从单轮走向多轮、从一次性任务走向长时间运行，怎么管理进入 LLM 上下文窗口的 token 集合，比怎么写 prompt 重要得多。
这篇就把 Context Engineering 拆开看：它和 Prompt Engineering 到底什么关系、为什么是 agent 省钱的关键、四个核心杠杆怎么用、以及不重视它的代价是什么。
01   Context Engineering vs Prompt Engineering 
先把这两个概念分清楚。
Prompt Engineering 管的是怎么写指令——系统提示词怎么组织、few-shot 例子怎么放、输出格式怎么要求。它的主战场是单轮推理：你写好一个 prompt，模型给一个回答，完事。
Context Engineering 管的更宽：在 agent 多轮推理的全过程里，进入 LLM 上下文窗口的所有 token 都归它管。这包括：
系统指令（system prompt）

工具定义（tool definitions）

MCP server 返回的工具列表

检索来的文档（RAG 结果）

对话历史（之前所有轮次的 message）

工具调用输出（之前几轮工具返回的结果）

用户当前这轮的输入

Prompt Engineering 是 Context Engineering 的子集——系统提示词只是上下文的一部分。当你做的是单轮任务，prompt 是大头，两者差别不大。但当你做的是 agent——几十轮对话、每轮调好几个工具、上下文不断累积——prompt 就只是冰山一角了，怎么管理整个上下文才是决定成败和成本的关键。
Anthropic 的说法很准确：Context Engineering 是 Prompt Engineering 的自然演进。早期 LLM 应用主要是单轮的，所以 prompt 写法是核心；现在 agent 跑多轮长时间任务，上下文管理就成了新的核心问题。
02   为什么上下文是 agent 的命脉 
要理解 Context Engineering 为什么重要，得先理解上下文对 agent 意味着什么。
上下文是 agent 的短期记忆。 模型每轮推理能"看到"的东西，就是上下文里的 token。上下文里有什么，模型就知道什么；上下文里没有的，模型就不知道。agent 跨轮次的记忆不靠模型内部的权重（那是训练时固化的），靠的就是上下文里的对话历史和工具输出。
上下文是有限的。 不管模型标称上下文窗口多大（128K、200K、1M），实际有效上下文远小于标称值。Chroma Research 做过一项研究叫 "context rot"（上下文腐烂），发现所有前沿模型在上下文超过大约 50K token 后，性能都显著下降——不是窗口没填满，而是填得越多模型越容易"走神"，忽略关键信息。
上下文是要花钱的。 每轮推理，整个上下文都会被重新处理一遍。这意味着上下文里每个 token 都在持续产生费用。Claude Opus 4.8 输入 $5/M token，一个 150K 上下文的 agent 会话，光重读已有上下文每轮就要 $0.75。跑 20 轮，光上下文重读就 $15。这还不算工具调用产生的新 token。
✗ 核心矛盾
上下文既是 agent 的命脉，又是 agent 的成本黑洞，还有个性能衰减的隐形天花板。管得好，agent 又准又省钱；管不好，agent 又蠢又烧钱。

03   四个核心杠杆 
Anthropic 和多个工程团队的实践总结出 Context Engineering 的四个核心杠杆。这四个不是孤立技巧，是一套从轻到重的上下文管理策略。
Context Engineering 四个核心杠杆杠杆一：Write——把信息写到外部，别堆在上下文里
最基础的一招：别把所有东西都塞在上下文窗口里，该外化的外化。
agent 在长任务中会产生大量中间结果——计划、分析、代码片段、测试输出。如果你让这些都留在对话历史里，上下文会迅速膨胀。正确做法是让 agent 把中间结果写到外部存储（文件、数据库、scratchpad），上下文里只保留必要的引用或摘要。
举个具体场景：agent 做代码重构，需要分析 10 个文件的依赖关系。错误做法是让 agent 把 10 个文件全读进上下文，在上下文里做分析。正确做法是让 agent 读一个文件、把分析结果写到一个 notes.md 文件、清掉这个文件的上下文、再读下一个。最后上下文里只有 notes.md 的摘要，不是 10 个文件的完整内容。
TIP · 本质
把上下文当 CPU 寄存器用，不当硬盘用。寄存器贵且小，只放当前要用的；其他的放内存（外部存储），需要时再加载。

杠杆二：Select——按需选取，别全量加载
第二招：需要什么拿什么，别一股脑全塞进来。
这主要针对 RAG（检索增强生成）和工具列表管理。常见的坑：agent 有 20 个工具可用，每次推理都把 20 个工具的完整定义塞进上下文。但一轮对话里通常只用 1-2 个工具，剩下 18 个的工具定义白占 token。
正确做法是按需选取。MCP 协议支持延迟加载工具定义——先只加载工具名和一句话描述（每个几十 token），模型决定要用哪个工具时再加载那个工具的完整 schema。这样上下文里平时只有 20 个工具的简短列表，不是 20 个工具的完整定义。
RAG 同理。检索回来 10 篇文档，别全塞进上下文。先看标题和摘要，相关的才加载正文。或者更精细：用 rerank 把最相关的 3 篇放前面，其他的丢掉或只保留摘要。
Select 杠杆的核心：每个 token 都要挣到自己的位置。进上下文之前问一句"这轮推理真的需要这个信息吗"，不需要就不放。
杠杆三：Compress——压缩旧轮次，扔掉已完成工具的输出
第三招：上下文不是只增不减的，旧的东西要压缩。
agent 跑 20 轮后，前 5 轮的对话历史基本没用了——计划已经执行完、中间分析已经被后续行动覆盖。但这些旧轮次还占着上下文 token。正确做法是定期压缩旧历史。
压缩有几种粒度。最轻的是直接删——已完成工具的输出如果不再需要，直接从历史里移除，只保留"调用了工具 X，成功"这条记录。中等的是摘要——把前 5 轮对话压成一段 "已完成 A、B、C，发现 D 问题" 的摘要。最重的是全量重构——把整个历史重新组织成结构化的任务状态。
Claude Code 的 agent loop 里有个 4 阶段压缩链，就是这个思路的工业级实现：Snip（轻量删除）→ Micro Compact（局部摘要）→ Context Collapse（大段折叠）→ Auto-Compact（全量重构）。从轻到重逐级尝试，尽量用最小的压缩力度解决问题，避免过度压缩丢失关键信息。
杠杆四：Isolate——子 agent 隔离，每个子 agent 返回摘要
第四招是最重的杀手锏：用子 agent 做隔离。
有些任务天生需要大量上下文——比如分析一个 50K token 的代码库、或者跑一个复杂的多步搜索。如果让主 agent 直接干，这 50K token 就永远占在主 agent 的上下文里，后续每轮都要为它买单。
正确做法是派一个子 agent 去干。子 agent 有自己的上下文窗口，它在那 50K token 里随便折腾——读代码、跑搜索、做分析。干完后，只把 1-2K token 的结论摘要返回给主 agent。主 agent 的上下文里只有这 1-2K 的摘要，不是 50K 的原始数据。
这招的威力在于：不管子 agent 内部用了多少 token，主 agent 的上下文成本是固定的。你可以让子 agent 跑 100 轮、读 1M token，主 agent 只多 1-2K。这是处理大规模上下文任务的标配模式。
Anthropic 的多 agent 研究系统就是这么设计的——主 agent 做编排，每个子 agent 在隔离上下文里做深度工作，只返回结论。子 agent 的 token 消耗大但孤立，主 agent 的上下文保持精简高效。
04   一个 token 账本：不重视的代价 
说个具体的账，感受下不重视 Context Engineering 的代价。
假设你的 agent 会话跑 25 轮。第 2 轮时 agent 读了一个 6000 token 的配置文件。之后这个文件内容就一直待在上下文里（因为对话历史会累积）。
到第 25 轮时，这个 6000 token 的文件被重新处理了 24 次（第 3 到 25 轮每轮都要重读它）。按 Claude Opus 4.8 输入 $5/M token 算，光这一个文件就花了 24 × 6000 / 1M × 5 = $0.72。如果有 prompt caching，能省一部分，但不是全省。
如果你在第 2 轮读完这个文件后，把关键信息摘到 scratchpad，然后从上下文里移除完整文件——后续 23 轮就不用为这 6000 token 买单。省下的钱乘以你每天的 agent 会话数，就是 Context Engineering 的直接收益。
⚠ 真实场景
这不是理论推演，是真实生产场景。很多团队第一次认真算 agent 的 token 账单时都会发现：大部分钱花在反复重读已经存在的上下文上，而不是新产生的推理上。Context Engineering 就是要堵这个漏。

05   和 Prompt Caching 的关系 
可能有人会问：Prompt Caching 不就是解决这个问题的吗？
不完全是。Prompt Caching 和 Context Engineering 是互补的，不是替代的。
Prompt Caching 解决的是"同样的前缀不用重新计费"——上下文前缀如果和上一轮一样，命中缓存按折扣价计费。它确实能省上下文重读的钱。但缓存有三个局限：
一是缓存有 TTL（OpenAI 30 分钟，Anthropic 5 分钟），超时失效。二是缓存有大小要求（通常要 1024 token 以上才缓存），小段不缓存。三是上下文变化会打断缓存——你在前缀中间插一句话，后面全 miss。
Context Engineering 是更根本的解法：先把上下文规模压下来，再配合 prompt caching 省钱。上下文越精简，缓存命中的比例越高、失效的概率越低。两个一起用才对。
06   对工程师意味着什么 
落到咱们写代码的，Context Engineering 改变的是 agent 架构设计的思路。
不再只盯着 prompt。 写好系统提示词只是起点，得设计整个上下文的生命周期：什么信息什么时候进上下文、什么时候出上下文、什么时候压缩、什么时候隔离。这是架构层面的设计，不是 prompt 层面的技巧。
监控上下文规模。 生产环境里，agent 每轮推理的上下文 token 数应该是个核心监控指标。如果发现上下文单调递增、或者某轮突然暴涨，大概率是 Context Engineering 没做好。设个阈值，上下文超过比如 80K 就触发压缩。
工具列表要懒加载。 别把所有工具定义一股脑塞进上下文。用 MCP 的延迟加载，或者自己实现工具路由——先看工具列表选工具，再加载选中工具的完整定义。
给 agent 配 scratchpad。 让 agent 有地方写中间结果、读回需要的信息。这相当于给 agent 一个外部记忆，减轻上下文窗口的压力。
子 agent 是标配不是优化。 任何需要大量上下文输入的子任务，都应该考虑用子 agent 隔离。主 agent 做编排和决策，子 agent 做深度工作，这是长跑 agent 的标准架构。
07   和历史文章的关系 
咱们之前写过的 Prompt Caching 对比、KV-Cache 原理、Prefix-Caching 原理，讲的都是"缓存怎么工作"——底层机制。Context Engineering 是上一层的策略：在知道缓存怎么工作的基础上，怎么设计上下文让缓存更有效、让总 token 更少。
缓存讲怎么存，Context Engineering 讲怎么不瞎存。两个配合起来才是完整的上下文成本优化。
一 句 话 总 结
Context Engineering 是 Prompt Engineering 的自然演进，管 agent 多轮推理的整个上下文。四个杠杆：Write（外化）、Select（选取）、Compress（压缩）、Isolate（隔离）。管好上下文，agent 又准又省钱；管不好，又蠢又烧钱。

#ContextEngineering #上下文工程 #AIAgent #PromptEngineering #Token优化 #LLM #ClaudeCode #Agent架构 #省钱 #AI工程 
     觉得有用？扫码关注「昕悦技术栈」
持续输出实战干货
长按识别二维码，关注我！