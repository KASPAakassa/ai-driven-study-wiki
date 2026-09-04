# Context Engineering:比 Prompt Engineering 更重要的 Agent 上下文管理

> **一句话摘要**:随着 Agent 从单轮走向多轮、从一次性任务走向长时间运行,管理进入 LLM 上下文窗口的 token 集合比怎么写 prompt 重要得多。本文拆解 Context Engineering 与 Prompt Engineering 的关系、四个核心杠杆(Write/Select/Compress/Isolate),以及不重视它的真实代价。
>
> **来源**:微信公众号「昕悦技术栈」《Context Engineering——比 Prompt Engineering 更重要的 Agent 省钱术》(昕悦成福),https://mp.weixin.qq.com/s/4zDq6EmX3YzvwC8SHHXNUg;基础参考 Anthropic 工程博客《Effective context engineering for AI agents》

## 概念:Context Engineering vs Prompt Engineering

- **Prompt Engineering** 管的是**怎么写指令**:系统提示词怎么组织、few-shot 例子怎么放、输出格式怎么要求。主战场是**单轮推理**:写好 prompt → 模型给回答 → 完事。
- **Context Engineering** 管得更宽:agent 多轮推理的全过程里,**进入 LLM 上下文窗口的所有 token**:

| 上下文组成 | 说明 |
| --- | --- |
| 系统指令 | system prompt |
| 工具定义 | tool definitions |
| MCP server 返回的工具列表 | 动态注入 |
| 检索来的文档 | RAG 结果 |
| 对话历史 | 之前所有轮次的 message |
| 工具调用输出 | 之前几轮工具返回的结果 |
| 用户当前这轮的输入 | — |

!!! note "核心关系"
    **Prompt Engineering 是 Context Engineering 的子集**——系统提示词只是上下文的一部分。单轮任务时 prompt 是大头,两者差别不大;做 agent(几十轮对话、每轮调多个工具、上下文不断累积)时,管理整个上下文才是决定成败与成本的关键。Anthropic 的说法:Context Engineering 是 Prompt Engineering 的**自然演进**。

## 原理:为什么上下文是 agent 的命脉

1. **上下文是 agent 的短期记忆**:模型每轮推理"看到"的东西就是上下文里的 token。跨轮次记忆不靠模型权重(训练时固化),靠的就是上下文里的对话历史和工具输出;
2. **上下文是有限的**:标称 128K/200K/1M ≠ 实际有效上下文。Chroma Research 的 "**context rot**"(上下文腐烂)研究:所有前沿模型在上下文超过约 **50K token** 后性能显著下降——不是窗口没填满,而是填得越多模型越容易"走神"、忽略关键信息;
3. **上下文是要花钱的**:每轮推理整个上下文都会被重新处理。Claude Opus 4.8 输入 $5/M token,一个 150K 上下文的会话,光重读已有上下文每轮 $0.75,跑 20 轮就是 $15(还没算工具调用产生的新 token)。

!!! warning "核心矛盾"
    上下文既是 agent 的**命脉**,又是**成本黑洞**,还有**性能衰减的隐形天花板**。管得好,agent 又准又省钱;管不好,又蠢又烧钱。

## 原理进阶:四个核心杠杆

一套从轻到重的上下文管理策略(Anthropic 与多个工程团队的实践总结):

### 杠杆一:Write——把信息写到外部,别堆在上下文里

长任务产生大量中间结果(计划、分析、代码片段、测试输出),留在对话历史里会让上下文迅速膨胀。正确做法:**中间结果写外部存储**(文件、数据库、scratchpad),上下文只保留必要引用或摘要。

> 例:agent 分析 10 个文件的依赖关系。错误做法:10 个文件全读进上下文分析。正确做法:读一个文件 → 分析结果写 `notes.md` → 清掉该文件上下文 → 再读下一个。最后上下文只有 notes.md 的摘要,不是 10 个文件的完整内容。

!!! tip "本质"
    把上下文当 **CPU 寄存器**用,不当硬盘用。寄存器贵且小,只放当前要用的;其他的放"内存"(外部存储),需要时再加载。

### 杠杆二:Select——按需选取,别全量加载

主要针对 RAG 与工具列表管理。常见坑:agent 有 20 个工具,每次推理都把 20 个工具的完整定义塞进上下文——但一轮通常只用 1-2 个,其余 18 个白占 token。

- **工具懒加载**:MCP 协议支持延迟加载——先只加载工具名 + 一句话描述(每个几十 token),模型决定用哪个时再加载完整 schema;
- **RAG 按需**:检索回 10 篇文档,先看标题摘要,相关的才加载正文;或用 **rerank** 把最相关的 3 篇放前面,其余丢掉/只留摘要。

核心:**每个 token 都要挣到自己的位置**——进上下文之前问一句"这轮推理真的需要吗",不需要就不放。

### 杠杆三:Compress——压缩旧轮次,扔掉已完成工具的输出

上下文不是只增不减。agent 跑 20 轮后,前 5 轮的历史基本没用(计划已执行、中间分析已被覆盖),但仍占 token。定期压缩:

| 粒度 | 做法 |
| --- | --- |
| 最轻·删除 | 已完成工具的输出不再需要就直接移除,只留"调用了工具 X,成功" |
| 中等·摘要 | 前 5 轮压成"已完成 A、B、C,发现 D 问题"一段摘要 |
| 最重·重构 | 整个历史重组为结构化任务状态 |

Claude Code 的 agent loop 里有工业级实现——**4 阶段压缩链**:Snip(轻量删除)→ Micro Compact(局部摘要)→ Context Collapse(大段折叠)→ Auto-Compact(全量重构),从轻到重逐级尝试,避免过度压缩丢失关键信息。

### 杠杆四:Isolate——子 agent 隔离,每个子 agent 返回摘要

最重的杀手锏。任务天生需要大量上下文(分析 50K token 的代码库、复杂多步搜索)时,让主 agent 直接干,这 50K 就永远占在主上下文里,后续每轮买单。

正确做法:**派子 agent 去干**——子 agent 有自己的上下文窗口,在那 50K token 里随便折腾(读代码、跑搜索、做分析),干完只把 **1-2K token 的结论摘要**返回给主 agent。主 agent 的上下文里只有这 1-2K 摘要。

!!! tip "威力所在"
    不管子 agent 内部用了多少 token,主 agent 的上下文成本**固定**。子 agent 跑 100 轮、读 1M token,主 agent 只多 1-2K——这是处理大规模上下文任务的**标配模式**(Anthropic 多 agent 研究系统即如此:主 agent 编排,子 agent 隔离深度工作,只返回结论)。

## 代码 / 实现:一个 token 账本

原文为方法论文章,无代码。下面用纯 Python 演示"不重视 Context Engineering 的代价"——同一份文件,留在上下文 vs 外化后重读,25 轮会话的成本对比:

```python
def session_cost(read_tokens: int, keep_in_context: bool, rounds: int = 25,
                 price_per_m: float = 5.0) -> float:
    """模拟一个 25 轮会话中,某个 6000 token 文件的成本($)
    keep_in_context=True  : 第 2 轮读入后一直留在上下文,第 3~25 轮每轮重读
    keep_in_context=False : 第 2 轮读完后摘成摘要,只占少量 token
    """
    if keep_in_context:
        total_reads = read_tokens * (rounds - 2)      # 第 3~25 轮共 23 次重读
    else:
        total_reads = read_tokens + 200 * (rounds - 2)  # 读 1 次 + 23 轮携带摘要
    return total_reads / 1_000_000 * price_per_m

file_tokens = 6_000
cost_keep = session_cost(file_tokens, keep_in_context=True)
cost_out  = session_cost(file_tokens, keep_in_context=False)

print(f"25 轮会话,6000 token 的配置文件:")
print(f"  留在上下文(重读 23 次): ${cost_keep:.3f}")
print(f"  读一次 + 携带摘要(200 token): ${cost_out:.3f}")
print(f"  节省: ${cost_keep - cost_out:.3f} / 会话")
# 每 10 个 agent 会话/天,一个月(30 天)能省多少?
print(f"  10 个会话/天 × 30 天 共节省: ${(cost_keep - cost_out) * 10 * 30:.1f}")
```

**运行结果**:留在上下文约 $0.72,外化后约 $0.03,单会话省 ~$0.69;10 会话/天 × 30 天可省约 $207/月——**"大部分钱花在反复重读已有上下文上,而不是新产生的推理上"**。

## 实践 / 应用:对工程师意味着什么

1. **不再只盯着 prompt**:设计整个**上下文的生命周期**——什么信息什么时候进、什么时候出、什么时候压缩、什么时候隔离(架构层设计,不是 prompt 层技巧);
2. **监控上下文规模**:每轮推理的上下文 token 数是核心监控指标;上下文单调递增或某轮暴涨 = Context Engineering 没做好;设阈值(如超 80K 触发压缩);
3. **工具列表懒加载**:MCP 延迟加载或自建工具路由——先看列表选工具,再加载选中工具的完整定义;
4. **给 agent 配 scratchpad**:让 agent 有地方写中间结果、读回需要的信息(外部记忆,减轻上下文压力);
5. **子 agent 是标配不是优化**:任何需要大量上下文输入的子任务,都应考虑子 agent 隔离——主 agent 编排决策,子 agent 深度工作,是长跑 agent 的标准架构。

### 与 Prompt Caching 的关系

两者**互补,不是替代**:

- **Prompt Caching** 解决"同样的前缀不用重新计费"(命中缓存按折扣价),但有限制:缓存有 **TTL**(OpenAI 30 分钟 / Anthropic 5 分钟,超时失效)、有**大小要求**(通常 ≥1024 token)、**上下文变化会打断缓存**(前缀中间插一句话,后面全 miss);
- **Context Engineering 更根本**:先把上下文规模压下来,再配合 caching——**上下文越精简,缓存命中比例越高、失效概率越低**。缓存讲"怎么存",Context Engineering 讲"怎么不瞎存"。

## 总结

- Context Engineering = 管理 agent 多轮推理时进入上下文窗口的**所有 token**,是 Prompt Engineering 的自然演进;
- 上下文是 agent 的短期记忆、有效长度有限(>50K token 出现 context rot)、每轮重读都要花钱;
- **四个杠杆**:Write(外化)、Select(选取)、Compress(压缩)、Isolate(子 agent 隔离);
- 对工程师:设计上下文生命周期、监控上下文规模、工具懒加载、scratchpad、子 agent 标配;与 Prompt Caching 配合使用。

## 延伸阅读

- 站内:[AI Agent 入门](agent-intro.md)、[核心组件](agent-core-components.md)、[TencentDB Agent Memory](../08-harness/agent-memory-plugin.md)(外部记忆落地)、[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(Harness 上下文装载层)
- 外部:原文(昕悦技术栈);Anthropic 工程博客《Effective context engineering for AI agents》;Chroma Research 的 "context rot" 研究;原始资料存档于 `docs/inbox/context-engineering-source.md`
