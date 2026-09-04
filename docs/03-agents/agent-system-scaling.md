# 大规模 Agent 系统设计:从个人助手到十亿用户服务

> **一句话摘要**:能正确调用工具的 Agent 和能稳定服务百万用户的 Agent 系统,中间隔着"写 Hello World 到构建一个淘宝"的距离。本文按规模拆解四个阶段的架构演进——单用户跑通脑回路、多用户上 LLM Gateway 与异步化、规模化拼成本与质量、十亿级拼合规与治理——并给出量化测算与关键数字。
>
> **来源**:微信公众号「迈索斯」《大规模Agent系统设计:从个人助手到十亿用户服务》,https://mp.weixin.qq.com/s/Fyk9O0nlBV1HIoPzV_tvJg;参考:Anthropic《Building Effective Agents》、AgentBench(arXiv:2308.03688)、LangGraph;原始资料存档于 `docs/inbox/agent-scaling-source.md`

## 概念:规模即架构

很多人第一次搭 Agent,觉得就是"套个 LLM API + 加几个工具调用"。跑通 Demo——问天气能正确调天气 API——就以为复杂度仅此而已。

!!! warning "现实是:1 个用户、10 个用户、10 万个用户,架构完全不同"
    一个能正确调用工具的 Agent,和一个能稳定服务百万用户的 Agent 系统,中间隔着的复杂度,与你从 Hello World 到构建一个淘宝的距离相当。

!!! tip "与站内 9 层架构的关系"
    [生产级 Agent 9 层架构](ai-infra-layering.md) 回答"生产系统需要哪些层"(Demo vs 生产);本文回答"**按用户规模分阶段演进**"——每个阶段该补上哪些层、哪些可以后置。两者互补:9 层是目标全景,本文是演进路径。

## 原理:四个阶段的架构演进

### 第一阶段:能跑就行(1 个用户)

最简单的 Agent:一个 while 循环,根据 LLM 输出决定调工具还是返回结果。Session 存内存、工具同步调用、无容错。

**核心任务**:把 Agent 的"脑回路"跑通——Prompt 怎么写、工具怎么描述、Plan 和 Execute 怎么串联。不需要考虑并发、容错、成本。

**离开信号**:能力基本稳定,开始有真实用户想用的时候。

### 第二阶段:多用户服务(10-1000 用户)

两个关键问题:**Session 隔离**和 **LLM 调用并发管理**。

- **Session 隔离**:Agent 是有状态的,用户 A 的对话历史/工具进度/中间结果不能让用户 B 看到。直觉做法是每个用户一个 Session 对象存内存 Map(能扛几十个用户);
- **LLM Gateway**(真正的挑战):假设每次任务平均调 30 次 LLM(Plan 一次、Execute 每步一次、ReAct 兜底几次),100 个并发用户 = 数百个 LLM 请求排队;而大多数 API 有速率限制(如 Claude Tier 1 只有 50 RPM)。Gateway 四件事:

| 能力 | 说明 |
| --- | --- |
| **模型路由** | 简单任务用小模型(Haiku 类),复杂任务用大模型(Sonnet 类) |
| **限流排队** | 超过 RPM 限制的请求排队等待 |
| **Fallback** | 主模型挂了切备用模型 |
| **成本追踪** | 每个 Session 消耗了多少 Token |

- **异步执行**:复杂任务要跑几分钟,用户不能干等。①发任务 → 立即返回"已接收";②Agent 后台执行,通过 **SSE** 推送进度;③用户可随时断开,回来还能看结果。Session 从"同步阻塞"变"异步持久化",状态存数据库。

!!! note "1000 用户规模的典型压力"
    | 指标 | 估算值 |
    | --- | --- |
    | 并发 Agent 执行 | ~50(不是所有用户同时在用) |
    | LLM 总调用量峰值 | ~1500/任务周期(50 并发 × 30 调用) |
    | LLM QPS | ~5-50(取决于单次任务 30s-5min) |
    | 单次任务耗时 | 30s-5min |
    | 月 LLM 成本 | ~$5K-20K(取决于模型选择) |

### 第三阶段:规模化(万级-百万级用户)

问题从"怎么扛住并发"变成"**怎么控制成本和质量**"。

**资源调度**(Agent 执行代码/操作文件/访问网络,每个 Session 需要隔离环境):
- **预热池**:提前启动一批空闲容器,任务来了直接分配(容器冷启动 2-5 秒,不能等);
- **分级调度**:简单任务用小容器,复杂任务用大容器;
- **超时回收**:任务完成后 10 分钟回收容器。

**成本优化**——先算一笔账(100 万日活 × 2 任务/天 × 30 次 LLM × 2000 token ≈ $0.01/次):

```
日成本 = 1,000,000 × 2 × 30 × $0.01 = $600,000/天
月成本 = $600,000 × 30 = $18,000,000/月
```

1800 万美元/月——这是真实规模下的成本问题。四个降本方向:

1. **小模型做简单事**:意图分类、格式化输出用 4B 小模型(千问 3-4B、Llama 3.2-3B),成本是大模型的 1/100;
2. **Plan 缓存**:相似请求的 Plan 可复用,不必每次重新规划;
3. **执行结果缓存**:同样的工具调用 + 同样参数,直接返回上次结果;
4. **分级模型路由**:80% 请求用小模型,只有 20% 真正复杂的上大模型。

**质量保障**:大规模系统最难的不是架构,是质量——Agent 行为非确定性,改个 Prompt 明天就可能失败。必须建**评测体系 + 数据飞轮**(线上问题持续补充测试集 → 驱动模型改进 → 再评估)。飞轮转起来质量持续提升,转不起来优化就是盲人摸象。

### 第四阶段:十亿级(核心不是技术)

技术挑战反而"常规"了——分布式 Session、多区域部署、异地多活都是经典分布式问题,有成熟方案。真正的挑战:

1. **合规**:不同国家的数据不能跨境存储(GDPR、中国数据安全法)。Session 数据、执行日志、长期记忆按区域隔离;
2. **成本**:十亿用户的 LLM 调用成本是天文数字,必须**自研小模型 + 端侧推理**;
3. **治理**:Agent 能做什么、不能做什么,从技术层面提升到**组织层面**定义。

## 代码 / 实现:规模化成本与分级路由测算(纯 Python)

把第三阶段的成本逻辑落成可运行的测算器——对比"全大模型"与"分级路由"的成本,并给出关键数字:

```python
# —— 规模化 LLM 成本测算器 ——
def cost_simulation(dau, tasks_per_user, calls_per_task, tokens_per_call,
                    price_per_million_tokens):
    """全大模型成本:日活 × 任务/人 × 调用/任务 × token × 单价"""
    calls_per_day = dau * tasks_per_user * calls_per_task
    tokens_per_day = calls_per_day * tokens_per_call
    cost_per_day = tokens_per_day / 1_000_000 * price_per_million_tokens
    return {"calls_per_day": calls_per_day, "cost_per_day": cost_per_day,
            "cost_per_month": cost_per_day * 30}

def tiered_routing(dau, tasks_per_user, calls_per_task, tokens_per_call,
                   small_price, large_price, small_ratio=0.8):
    """分级路由:80% 请求走小模型,20% 走大模型"""
    total_calls = dau * tasks_per_user * calls_per_task
    small_calls = total_calls * small_ratio
    large_calls = total_calls * (1 - small_ratio)
    cost = (small_calls * tokens_per_call / 1_000_000 * small_price
            + large_calls * tokens_per_call / 1_000_000 * large_price)
    return {"total_calls": total_calls, "cost_per_day": cost,
            "cost_per_month": cost * 30}

# 场景:100 万日活,每用户每天 2 次任务,每次 30 次调用,每次 2000 token
# 单价(每百万 token):大模型 $5(约 Sonnet 档),小模型 $0.05(约 4B 档)
all_large = cost_simulation(1_000_000, 2, 30, 2000, 5.0)
tiered = tiered_routing(1_000_000, 2, 30, 2000, small_price=0.05, large_price=5.0)

print(f"全大模型: 日成本 ${all_large['cost_per_day']:,.0f} | 月成本 ${all_large['cost_per_month']:,.0f}")
print(f"分级路由: 日成本 ${tiered['cost_per_day']:,.0f} | 月成本 ${tiered['cost_per_month']:,.0f}")
print(f"节省比例: {(1 - tiered['cost_per_month'] / all_large['cost_per_month']) * 100:.1f}%")
```

## 实践 / 应用:基础设施四件套

很多人把精力放在 Agent 的"脑力"上——Prompt 工程、工具设计、Plan 算法。但**大规模 Agent 系统真正的差异化是基础设施**:

| 基础设施 | 决定的问题 | 缺失的后果 |
| --- | --- | --- |
| **评测体系** | 你能多快发现退化? | 质量回归无感知,线上事故累积 |
| **成本控制** | 你的利润率能不能撑住? | 1800 万美元/月的账单无人买单 |
| **可观测性** | 出问题能否 5 分钟定位根因? | 故障定位靠猜(呼应 [9 层架构](ai-infra-layering.md) 的 L8) |
| **容错能力** | LLM 挂了/工具超时/用户断连,如何优雅降级? | 单点故障拖垮全系统 |

!!! warning "这些设施决定系统生命周期"
    评测、成本、可观测、容错缺乏技术亮点,但**决定了系统的生命周期是三个月还是三年**。Demo 阶段可以没有;从第二阶段开始,每一样都要逐步补齐。

**演进路线图**(结合本文化与站内文章):

```
阶段 1(单用户)  → 跑通 think-act-observe 循环([AI Agent 入门](agent-intro.md))
阶段 2(多用户)  → 加 LLM Gateway、异步 SSE、Session 持久化、开始埋 trace
阶段 3(规模化)  → 容器预热池、分级路由、Plan/结果缓存、评测飞轮([评估驱动开发](agent-eval-driven-dev.md))
阶段 4(十亿级)  → 数据分区合规、自研小模型 + 端侧推理、组织级治理
```

## 总结

- **规模即架构**:1 个用户和 10 万个用户的 Agent 系统,架构完全不同——按阶段演进,不提前过度设计;
- **阶段 2 的关键**:LLM Gateway(路由/限流/Fallback/成本追踪)+ 异步持久化 Session;
- **阶段 3 的关键**:资源调度(预热/分级/回收)+ 成本优化(小模型/缓存/分级路由)+ 评测数据飞轮;
- **阶段 4 的关键**:合规(数据跨境)、成本(自研小模型+端侧)、治理(组织层面);
- **核心洞察**:大规模 Agent 的差异化是**基础设施**(评测/成本/可观测/容错),不是脑力。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/Fyk9O0nlBV1HIoPzV_tvJg;Anthropic《Building Effective Agents》(https://www.anthropic.com/engineering/building-effective-agents);AgentBench(arXiv:2308.03688);LangGraph(https://langchain-ai.github.io/langgraph/)
- 站内:[生产级 Agent 9 层架构](ai-infra-layering.md)(分层全景)、[Agent 评测](agent-evaluation.md) 与 [评估驱动开发](agent-eval-driven-dev.md)(评测飞轮)、[Context Engineering](context-engineering.md)(上下文与成本)、[企业 Agent 工程化(四):四件套](../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md)(工具治理与成本)、[Git Worktree 并行开发](../07-agent-coding/experience/git-worktree-parallel-agents.md)(并发隔离)
