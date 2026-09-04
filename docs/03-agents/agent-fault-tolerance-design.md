# Agent 容错设计:不止于重试的完整思路

> **一句话摘要**:工具调用失败时,优秀的 Agent 容错远不止"重试"——核心是建立系统性工程思维:**先把错误按发生阶段分类定界(调用前/调用中/调用后),再对每类故障采取精准策略**,最后把预防、执行控制、降级、观测串成完整架构,实现"**失败得体面,恢复得优雅**"。本文是这套方法的完整拆解,并给出错误分类路由、韧性三件套、降级链的可运行演示。
>
> **来源**:用户提供(方法论文案);原始资料存档于 `docs/inbox/agent-fault-tolerance-source.md`

## 概念:容错不是"重试"

!!! tip "一句话判断**
    好的容错设计,是在写重试代码**之前**先回答三个问题:错在哪一层?该不该重试?重试之外还有什么选择?——把错误分类,再谈策略。

## 原理:错误三分类 + 分层应对

### 第一步:错误分类定界(设计基础)

| 错误层级 | 发生阶段 | 典型表现 |
| --- | --- | --- |
| **调用前(歧义层)** | LLM 生成参数后、执行前 | 参数名错误、类型错误、必填字段缺失(**参数幻觉**) |
| **调用中(执行层)** | 工具执行过程中 | HTTP 超时、服务挂了、被限流(429)、服务器错误(5xx) |
| **调用后(语义层)** | 工具返回结果后 | 结果为空、格式无法解析、数据内容错误 |

!!! note "为什么先分类**
    三层的失败语义完全不同:歧义层是"Agent 说错了话"(可修正)、执行层是"服务暂时不行"(可重试/熔断)、语义层是"拿到了但没用"(需判断与降级)——**用同一套重试逻辑处理三层,必然要么过度重试(浪费)要么漏重试(崩溃)**。

### 第二步:分层应对策略

**调用前——预防参数幻觉(在 LLM 与工具之间加确定性校验):**

1. **Schema 校验**:用 Pydantic / Zod 为每个工具定义清晰输入 Schema——LLM 生成的参数先过 Schema 再执行;
2. **错误反馈与修正**:校验失败不直接崩溃,把失败信息**反馈给 LLM 自我修正参数**(再试一轮);
3. **防函数签名漂移**:定期对比期望 Schema 与 API 实际返回结构,提前发现外部 API 升级导致的不兼容。

**调用中——韧性三件套(应对执行故障,注意细节):**

| 机制 | 要点 |
| --- | --- |
| **指数退避重试** | 等待时间指数增长(1s→2s→4s…)+ **随机抖动**防"惊群效应";**只对暂时性错误重试**(超时/限流),永久性错误直接走降级 |
| **超时控制** | 每次调用设**硬超时**,超时信号交给 Agent 决策后续(不无限等待) |
| **断路器模式** | 连续失败达阈值 → 暂时**熔断**该工具(不再调用,省资源);冷却后进入**半开状态**试探性恢复 |

**调用后——语义错误处理(成功≠可用):**

- **明确区分"成功但无结果"与"执行失败"**:把准确的信号(空结果/解析失败/内容错误)传给 Agent 判断——不要把它吞成"成功";
- **优雅降级**:提前配置工具优先级列表,高级工具不可用时自动降级到备选(如语义搜索 → 关键词搜索);
- **人类兜底**:所有降级方案都失败后,Agent **携带完整错误上下文 + 已尝试的恢复步骤,暂停请求人工介入**——绝不静默失败(呼应 [企业工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md) 的人工接管与 [Agentic Abstention](agentic-abstention.md) 的"该停就停")。

## 代码 / 实现:错误分类路由 + 韧性三件套(纯 Python)

```python
import random, time

# —— 1) 错误分类路由:按阶段判定策略 ——
def classify_strategy(stage: str, retryable: bool = True) -> str:
    if stage == "pre":      # 调用前:参数幻觉 → Schema 校验 + 反馈修正,不重试
        return "参数幻觉:Schema 校验 → 失败信息反馈 LLM 自我修正(不重试)"
    if stage == "during":
        return ("执行故障:" + ("指数退避+抖动重试(只重暂时性错误)" if retryable
                                else "永久错误不重试,直接走降级/兜底"))
    return "语义错误:区分空结果与失败 → 优雅降级 → 人类兜底(不静默)"

for s, r in [("pre", True), ("during", True), ("during", False), ("post", True)]:
    print(f"  [{s:6} retryable={r}] → {classify_strategy(s, r)}")
assert "Schema" in classify_strategy("pre")
assert "退避" in classify_strategy("during", True)
assert "降级" in classify_strategy("during", False)
assert "人类兜底" in classify_strategy("post")

# —— 2) 指数退避 + 抖动(防止惊群)——
def backoff(attempt: int, base=1.0, cap=8.0, jitter=0.3) -> float:
    exp = min(base * (2 ** attempt), cap)
    return exp + random.uniform(-jitter, jitter)   # 随机抖动

random.seed(1)
for a in range(3):
    print(f"  退避第 {a+1} 次: {backoff(a):.2f}s")

# —— 3) 断路器:连续失败熔断,冷却后半开试探 ——
class CircuitBreaker:
    def __init__(self, threshold=3, cooldown=5):
        self.fails, self.threshold, self.cooldown, self.open_until = 0, threshold, cooldown, 0
    def allow(self):
        if time.time() < self.open_until:
            return "熔断中:直接短路,不调用工具"
        return "放行"
    def record(self, ok):
        if ok:
            self.fails = 0
        else:
            self.fails += 1
            if self.fails >= self.threshold:
                self.open_until = time.time() + self.cooldown
                self.fails = 0
                return "触发熔断:冷却后进入半开状态试探"
        return ""

cb = CircuitBreaker(threshold=3, cooldown=2)
for i in range(4):
    msg = cb.record(False) or (cb.allow() if i < 3 else "")
    print(f"  第 {i+1} 次失败 → {msg or cb.allow()}")
print("代码验证通过 ✔")
```

## 实践 / 应用:完整架构与核心难点

### 完整容错架构(四层串起来)

```
① 可观测性层(基石):分布式追踪、错误分类、熔断指标、告警——没有它生产就是"盲飞"
② 预防(调用前):Schema 校验 + 错误反馈修正 + 签名漂移检测
③ 执行控制(调用中):指数退避+抖动 / 硬超时 / 断路器
④ 降级与兜底(调用后):工具优先级降级 → 人类兜底(带完整上下文暂停请求)
```

!!! warning "可观测性不是可选项**
    错误分类、熔断指标、追踪缺失时,容错策略对不对都无从验证——**先接观测,再谈容错**(呼应 [性能剖析](agent-performance-analysis.md) 的"没有归因就优化是盲人摸象"与 [9 层架构](ai-infra-layering.md) 的 L8)。

### 核心难点:LLM 的非确定性

传统机制是确定性的(重试/熔断/超时),而 LLM 行为是概率性的。三个解法:

1. **结构化错误处理**:在 Prompt 中明确告知 LLM 遇到特定错误(如 429)时的具体操作流程——把"该做什么"写死,不让模型自由发挥;
2. **状态机约束**:关键路径用状态机限定 Agent 行为(哪些状态可重试/可降级/必须暂停)——避免模型在错误路径上自由探索(呼应 [云端软件工厂](../08-harness/cloud-software-factory.md) 的 Graph 状态机控制面);
3. **幂等性**:发邮件、下单等**非幂等操作**重试可能导致重复执行——重试前必须保证操作幂等或先查重(呼应 [企业工程化(三)](../06-enterprise/ontology-agent-adoption/enterprise-agent-permission-integration-observability.md) 的 tool_id 对账)。

### 与站内其他文章的呼应

- [企业 Agent 工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md):那篇讲"重试/回滚/接管"的**决策**,本文讲错误**分类与完整架构**——互补;
- [Agent 系统设计的 5 个决策](agent-system-5-decisions.md):"三类失败三种策略"是本文调用中层的雏形;
- [Agentic Abstention](agentic-abstention.md):"该停就停"与人类兜底同源;
- [Graph Engineering 14 步](../07-agent-coding/experience/graph-engineering-14-steps.md):断路器=验证器的"containment"思想;
- [企业四道防线](../06-enterprise/ontology-agent-adoption/enterprise-agent-production-deployment.md):容错与 SLO 的关系。

## 总结

- **先分类后策略**:调用前(参数幻觉→Schema+反馈修正)/ 调用中(执行故障→韧性三件套)/ 调用后(语义错误→降级+人类兜底);
- **韧性三件套细节**:只重暂时性错误、退避加抖动、断路器冷却后半开;
- **完整架构**:观测(基石)→ 预防 → 执行控制 → 降级兜底;
- **核心难点**:LLM 非确定性 → 结构化错误处理 + 状态机约束 + 幂等性;
- **一句话**:容错系统不保证永不失败,但确保**失败得体面,恢复得优雅**——把错误分类清楚,比把重试写漂亮更重要。

## 延伸阅读

- 原始素材:用户提供的方法论文案,存档于 `docs/inbox/agent-fault-tolerance-source.md`
- 站内:[企业 Agent 工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md)、[Agent 系统设计的 5 个决策](agent-system-5-decisions.md)、[Agentic Abstention](agentic-abstention.md)、[生产级 Agent 9 层架构](ai-infra-layering.md)、[Agent 性能剖析](agent-performance-analysis.md)、[云端软件工厂](../08-harness/cloud-software-factory.md)
