# Agent 性能剖析:找到系统的真正瓶颈

> **一句话摘要**:架构师的日常不是在学新名词,而是在几个看似独立的概念之间建立连接——性能剖析、延迟归因、trace 实际上指向同一个核心问题:**怎样让 Agent 在复杂环境中持续做出正确的决策**。本文从端到端 trace 出发,讲清剖析的统计口径、归因的工程方法、trace 的规范设计,并附一个可运行的剖析/归因演示与设计练习。
>
> **来源**:微信公众号「岚岚」《Agent性能剖析:找到系统的真正瓶颈》,https://mp.weixin.qq.com/s/JbqRS58j-d_usyVDkmSLnQ;原始资料存档于 `docs/inbox/agent-performance-analysis-source.md`

## 概念:Agent 的性能问题为什么不一样

传统系统的性能剖析是"定位慢函数";Agent 的性能问题发生在**一条决策链路上**:一次请求可能包含路由、检索、rerank、LLM 推理、工具调用、格式校验、通知投递……任何一环都可能慢或出错,而"慢"的根因往往藏在调用次数与失败重试里,不在单次耗时里。

!!! tip "核心判断"
    **Agent 性能剖析要从端到端 trace 开始,而不是先怀疑模型慢。** 模型通常不是瓶颈;路由策略、检索候选量、工具超时、队列堆积才是。

## 原理:三件事,同一个目标

### 1. 性能剖析:先拿到正确的统计数据

| 统计口径 | 正确做法 | 常见误区 |
| --- | --- | --- |
| **分位数** | 看 **P95 / P99**,抓"偶尔慢一下" | 被平均值骗了——平均值掩盖长尾 |
| **调用次数** | 看调用次数,发现"调用次数最多的组件" | 只看单次耗时,忽略频率杠杆 |
| **失败与重试** | 看失败重试路径,而非只盯成功路径 | 只看成功路径,重试风暴被隐藏 |

!!! warning "蟑螂效应"
    性能问题最喜欢躲在"偶尔慢一下"里,**像蟑螂,开灯才跑出来**——常态监控看不见,只有 P95/P99、失败重试这类口径才能暴露它。慢请求的标准"三问":慢在哪一段?为什么慢?下次怎么避免?

### 2. 延迟归因:把"系统慢"拆成可行动的原因

**归因目标**:让每次慢请求都能回答"慢在哪一段、为什么慢、下次怎么避免"。

| 慢的现象 | 常见根因 | 对应解法 |
| --- | --- | --- |
| 模型首包慢 | 模型路由到重模型 / 预热不足 | 路由策略、小模型兜底 |
| 检索慢 | 候选过多 / 索引缺失 | 候选裁剪、向量索引、rerank 前置 |
| 工具 API 超时 | 外部依赖慢 / 无超时 | 超时 + 重试策略、缓存 |
| 队列堆积 | 并发过高 / 消费慢 | 限流、水平扩展、批处理 |
| 日志同步写入 | I/O 阻塞主链路 | 异步日志、采样上报 |

!!! warning "没有归因就优化,通常会把最便宜的地方优化十遍,真正的瓶颈纹丝不动"
    归因的前提:统一 trace ID 贯穿所有组件 + 每段记录开始/结束时间。没有这些,一切"优化"都是猜。

### 3. Trace:质量的最后一道防线

三者关系**不是线性**的:

```
性能剖析(基础)→ 延迟归因(工程化保障)→ trace(质量最后防线)
没有剖析,归因是空中楼阁;没有归因,优化是盲人摸象;没有 trace,整条链路可能在最后一步翻车。
```

**分布式追踪规范**(一次 Agent 请求的典型链路:前端 → API 网关 → Agent 引擎 → LLM 推理 → 工具调用 A → 数据库查询 → 工具调用 B → 外部 API → 结果聚合 → 返回用户):

1. **入口生成 trace ID**,贯穿所有下游调用;
2. 每个 **span** 记录:父 span ID、操作名称、开始/结束时间、状态码、关键参数 hash;
3. 所有 span 发送到统一后端(Jaeger / Tempo)。

有了完整 trace,你可以回答任何问题:这个请求为什么慢了?它在等什么?哪一步超时了?

!!! note "与站内 [生产级 Agent 9 层架构](ai-infra-layering.md) 的对应"
    Trace 正是 9 层架构的 **L8(可观测性)** 落地:统一 span 定义、trace ID 贯穿、集中后端——没有 L8,生产级 Agent 无从谈起(呼应 [企业 Agent 上生产的四道防线](../06-enterprise/ontology-agent-adoption/enterprise-agent-production-deployment.md) 的"可观测"防线)。

## 代码 / 实现:剖析 + 归因演示(纯 Python)

生成一批端到端 span 数据,计算 P95/P99、按调用次数找热点、对"偶尔慢"做归因:

```python
import statistics

# —— 模拟一次 Agent 请求的 span 数据(多段,部分有重试)——
SPANS = [
    # (segment, duration_ms, success)
    ("router",       12,  True),
    ("retrieval",    88,  True),
    ("rerank",       15,  True),
    ("llm_inference", 220, True),   # 均值上像主瓶颈
    ("tool_api_a",   9,  True),
    ("tool_api_b",   320, True),    # P99 视角的真正瓶颈
    ("validate",     8,  True),
    ("notify",       11,  True),
    ("tool_api_b",   310, True),    # 同一工具的第二次调用
    ("tool_api_b",   300, False),   # 失败重试
    ("tool_api_b",   340, True),
    ("retrieval",    92,  True),
]

def p95_p99(values):
    vs = sorted(values)
    def pct(p):
        idx = min(len(vs) - 1, int(len(vs) * p))
        return vs[idx]
    return pct(0.95), pct(0.99)

def analyze(spans):
    seg_times = {}
    seg_calls = {}
    seg_fail = {}
    for seg, dur, ok in spans:
        seg_times.setdefault(seg, []).append(dur)
        seg_calls[seg] = seg_calls.get(seg, 0) + 1
        seg_fail[seg] = seg_fail.get(seg, 0) + (0 if ok else 1)
    print(f"{'segment':<14}{'calls':>6}{'avg(ms)':>9}{'P95(ms)':>9}{'P99(ms)':>9}{'fails':>6}")
    for seg, times in seg_times.items():
        p95, p99 = p95_p99(times)
        print(f"{seg:<14}{seg_calls[seg]:>6}{statistics.mean(times):>9.0f}{p95:>9}{p99:>9}{seg_fail[seg]:>6}")
    # 归因:按"调用次数 × 单次耗时"识别热点(频率杠杆)
    hot = max(seg_times, key=lambda s: len(seg_times[s]) * statistics.mean(seg_times[s]))
    print(f"\n归因结论:热点 = {hot}(调用次数 × 平均耗时最大),不是均值最大的 llm_inference")

analyze(SPANS)
```

运行结果会显示:`tool_api_b` 调用 4 次(含失败重试)、P99 达 340ms,总耗时权重远超单次均值最高的 `llm_inference`——**这就是"看调用次数 + 失败重试"抓出真正瓶颈的过程**。

## 实践 / 应用:设计练习——生产级代码审查 Agent

假设要为"检查 PR 安全漏洞的代码审查 Agent"做生产设计,四份文档(原文练习的深化版):

### 1) 系统边界定义

| 做(Do) | 明确不做(Don't) |
| --- | --- |
| 读取 PR diff 与相关上下文,扫描注入/密钥/提权风险 | 不修改代码(只读审查,产出报告) |
| 调用 SAST 扫描 + LLM 语义审查 + 规则匹配 | 不自动合并/关闭 PR |
| 按风险等级输出发现与修复建议 | 不访问生产环境凭证 |
| 在超时/不确定时降级为"待人工确认" | 不做架构级重构建议 |

!!! tip "不要写'需要时再扩展'这种暧昧表述"
    边界必须显式:不做就是不做,含糊的边界是上线后事故的温床。

### 2) 异常场景矩阵(≥3 个)

| 失败场景 | 恢复策略 | 用户感知(恢复期间用户看到什么) |
| --- | --- | --- |
| LLM 调用超时 | 重试一次 → 降级为纯 SAST + 规则结果 | 报告标注"语义审查未完成",仍可看静态扫描结果 |
| 外部 SAST 服务不可用 | 切换到内置规则引擎;记录降级事件 | 延迟增加但审查不中断;报告注明降级 |
| 大 PR 超出上下文预算 | 按文件分片审查 + 汇总 | 进度条 + "正在审查第 3/8 个文件";不假死 |
| 权限不足(无 repo 读权限) | 拒绝并说明所需权限 | 明确错误信息 + 联系管理员指引 |

### 3) 成本预算(单次任务各环节预估)

| 环节 | 延迟预估 | 成本预估(每千 token 计) |
| --- | --- | --- |
| diff 拉取与分片 | 200-500ms | — |
| SAST 扫描 | 1-3s | — |
| LLM 语义审查 | 5-15s(取决于 diff 大小) | $0.02-0.20 |
| 汇总与报告 | 1-2s | $0.005-0.02 |
| **单任务合计** | **~10-20s** | **~$0.03-0.25** |

### 4) 上线监控方案(3 个 P0 指标 + 告警阈值)

| 指标 | 为什么 P0 | 告警阈值 |
| --- | --- | --- |
| **P95 端到端延迟** | 用户等待的核心体验 | > 30s 持续 5 分钟告警 |
| **失败重试率** | 蟑螂效应:掩盖真实瓶颈 | 重试占比 > 10% 告警 |
| **高误报率(人工标记"误报"比例)** | 信任流失是最难修复的指标 | > 20% 触发人工复盘 |

## 总结

- **三个概念是一个问题的三面**:性能剖析(拿到正确的统计口径)、延迟归因(拆成可行动原因)、trace(让链路可回答"为什么慢");
- **统计纪律**:看 P95/P99 不看平均、看调用次数不看单次耗时、看失败重试不看成功路径;
- **工程纪律**:统一 trace ID 贯穿 + 每段记录时间,是归因的前提;没有归因就优化,等于反复优化最便宜的地方;
- **设计纪律**:上线前写清系统边界(含明确不做)、异常矩阵(含用户感知)、成本预算、P0 监控指标——这就是"让 Agent 在复杂环境中持续做出正确决策"的落地形态。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/JbqRS58j-d_usyVDkmSLnQ;原始资料存档于 `docs/inbox/agent-performance-analysis-source.md`
- 站内:[生产级 Agent 9 层架构](ai-infra-layering.md)(L8 可观测)、[大规模 Agent 系统设计](agent-system-scaling.md)(成本与监控)、[企业 Agent 上生产的四道防线](../06-enterprise/ontology-agent-adoption/enterprise-agent-production-deployment.md)(成本/可观测防线)、[Agent 评测](agent-evaluation.md)(质量与评测)、[Graph Engineering 14 步](../07-agent-coding/experience/graph-engineering-14-steps.md)(节点/边与 trace 的 span 对应)
- 概念延伸:OpenTelemetry、Jaeger、Tempo、Distributed Tracing
