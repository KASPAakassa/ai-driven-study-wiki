# 生产级 AI Agent 系统:9 层架构 + 4 横切能力全景

> **一句话摘要**:绝大多数 Agent 项目停在 Demo 阶段,不是模型不行,是 **Infra 不行**。本文从 L0 到 L8 逐层拆解生产级 Agent 的 9 层架构(算力/模型/数据/Prompt/编排/工具/记忆/评测/可观测)与 4 个横切能力(安全/CI-CD/FinOps/DevEx),并给出技术选型路线图。
>
> **来源**:微信公众号《AI Infra 全景图:Agent Framework、调度、编排、沙箱、记忆管理、Tracing 分层拆解》(Knock),https://mp.weixin.qq.com/s/dmlwqGylzG0eQVUlcZocUQ

## 概念:Demo 与生产的分水岭

2026 年几乎每家公司都在做 AI Agent,但绝大多数项目**停留在 Demo 阶段、无法融入生产**。关键洞察:

!!! tip "不是模型不行,是 Infra 不行"
    生产级 Agent 需要的不只是大模型 + 向量库,而是算力调度、模型网关、数据管道、Prompt 管理、Agent 编排、工具沙箱、记忆系统、评测体系、可观测平台——还要让安全、CI/CD、成本与开发者体验贯穿每一层。**大多数团队只关注 L4(Agent Framework)+ L2(向量库),忽略了其他 7 层与 4 个横切能力;而生产级稳定性恰恰取决于那些"不起眼"的基础设施。**

## 原理:纵向 9 层架构

| 层 | 名称 | 核心问题 | 关键组件/工具 |
| --- | --- | --- | --- |
| **L0** | 基础资源层 | 模型和应用运行在哪里? | GPU(K8s/Ray/Slurm)、对象存储(S3/MinIO)、镜像(Harbor/HF Hub)、密钥(KMS) |
| **L1** | 模型与推理层 | 用哪个模型?怎么调用?怎么降本? | Model Gateway(LiteLLM/Portkey)、Router、vLLM/TGI、Fallback/限流、量化/KV Cache |
| **L2** | 数据与知识层 | 模型如何安全、准确用企业私有知识? | RAG 管道:解析→Chunking→Embedding→索引→检索→Rerank→权限继承 |
| **L3** | Prompt 与上下文层 | 如何组织模型能可靠执行的输入? | PromptOps(版本管理/Registry/实验/审批)、上下文压缩、Token Budget |
| **L4** | 编排与 Agent 层 | 复杂任务如何拆解、调度、执行? | LangGraph/CrewAI/AutoGen/OpenAI Agents SDK + Workflow Engine(Temporal/Airflow) |
| **L5** | 工具执行层 | Agent 能做什么?执行边界? | 函数调用、MCP、代码解释器、浏览器自动化、RPA、沙箱(E2B/Modal)、权限校验 |
| **L6** | 状态与记忆层 | 系统如何记住一切而不越权? | 记忆分层(工作/短期/长期/情景/语义)、Mem0/Zep/LangGraph Memory、TTL 与隐私 |
| **L7** | 评测与质量层 | 改动后质量变好还是变坏? | 离线(Golden Set/回归)/在线(指标/A-B)/人审抽检;RAGAS/DeepEval/LangSmith |
| **L8** | 可观测与运营层 | 出问题能否定位?成本能否归因? | Tracing/Metrics/Logs;LangSmith/LangFuse/OpenTelemetry/Arize Phoenix |

### 逐层要点(生产级最佳实践)

- **L0**:推理 GPU 按需弹性伸缩(Modal/RunPod),避免空跑;训练用 Ray Cluster + Kueue 公平调度;模型权重统一进 Artifact Registry,禁止散落本地磁盘;
- **L1**:智能路由(简单任务用小模型降本、复杂任务用大模型保质量)、自动 Fallback(主模型超时切备用)、按用户/应用设 Token 预算、KV Cache 复用;
- **L2**:从朴素 RAG(Query→Top-K→拼接)到 Advanced RAG(Query Rewrite→混合检索→Rerank→Citation)再到 **Agentic RAG**(Agent 主动决定何时检索、检索什么、是否二次检索);
- **L3**:上下文由 System/Developer Prompt、RAG 结果、Few-shot、用户画像、会话记忆、当前输入拼装;**Prompt 即代码**——版本控制、Code Review、灰度发布;
- **L4 四大框架选型**:

| 框架 | 架构模式 | 多 Agent | 学习曲线 | 适合 |
| --- | --- | --- | --- | --- |
| LangGraph | 有向图状态机 | 原生 | 陡峭 | 复杂工作流、精细控制 |
| CrewAI | 角色扮演+任务分工 | 内置协作 | 平缓 | 多角色团队分工 |
| AutoGen 0.4+ | 异步事件驱动 | 对话式 | 中等 | 实时对话、事件驱动 |
| OpenAI Agents SDK | 简单链式+Handoff | Handoff | 最平缓 | 快速原型、OpenAI 生态 |

- **L5 沙箱对比**:E2B(<150ms,VM 级,代码执行首选)、Modal(<500ms,容器级,GPU 任务)、Fly.io Machines(<300ms,全球分布式)、Docker(1-3s,弱隔离,仅开发);安全三原则:**最小权限、网络隔离(默认禁外网)、资源限制**;
- **L6 记忆分层**:工作记忆(Context Window)、短期(Redis)、长期(向量库)、情景(结构化)、语义(知识图谱);必须管理 TTL、PII 脱敏、写入/召回策略;
- **L7**:没有评测就是"盲飞";**发布门禁**——每次 Prompt/模型/RAG/工具改动必须通过评测才能上线;指标:Faithfulness、Answer Relevance、Context Precision、Tool Success Rate、Completion Rate、幻觉检测;
- **L8**:完整 Trace 应包含用户问题、实际 Prompt、Tool Calls 与参数、Tool Results、LLM 输出、最终回复、Token/延迟/成本;**OpenTelemetry 是厂商中立底座**(LangFuse/Arize 均支持 OTel)。

## 横向 4 个能力(贯穿所有层)

| 横切能力 | 关键内容 |
| --- | --- |
| **安全治理** | 身份认证与权限、租户隔离、PII/DLP、Prompt Injection 防护、工具调用审批、审计日志、模型供应链合规 |
| **CI/CD 与发布治理** | 代码/Prompt/模型/RAG 索引/工具 Schema/Workflow 全部版本化、灰度与回滚 |
| **FinOps 成本治理** | Token(按模型/应用/用户)、GPU、向量库、Embedding/Rerank、日志留存、带宽——**每笔成本可归因** |
| **开发者体验 DevEx** | Playground、Trace 回放、Prompt/RAG 调试、Eval 看板、SDK/CLI、模板工程 |

## 代码 / 实现:L1 智能路由 + Fallback

原文为方法论文章,无代码。下面用纯 Python 演示 L1 层最核心的两个机制——**智能路由**(简单任务用小模型降本)+ **自动 Fallback**(主模型失败切备用):

```python
import random

# 模型池:任务复杂度 -> 模型,含成本(每千 token 美元)
MODELS = {
    "simple":  {"name": "deepseek-flash", "cost_per_1k": 0.0002},   # 小模型,便宜
    "complex": {"name": "claude-opus",    "cost_per_1k": 0.015},    # 大模型,贵但强
}

def classify_task(prompt: str) -> str:
    """简易任务分类:关键词命中判为复杂任务,否则简单任务"""
    complex_kw = ["分析", "重构", "架构", "设计", "总结", "调试"]
    return "complex" if any(k in prompt for k in complex_kw) else "simple"

def call_model(model: str) -> str:
    """模拟模型调用:8% 概率失败(超时/报错)"""
    if random.random() < 0.08:
        raise TimeoutError(f"{model} 调用超时")
    return f"[{model} 的回复]"

def gateway(prompt: str) -> tuple[str, float]:
    """智能路由 + Fallback:简单任务小模型,失败自动切大模型"""
    tier = classify_task(prompt)
    primary = MODELS[tier]["name"]
    try:
        reply = call_model(primary)
    except TimeoutError:
        reply = call_model(MODELS["complex"]["name"])          # Fallback 到备用
        return reply, MODELS["complex"]["cost_per_1k"]
    return reply, MODELS[tier]["cost_per_1k"]

random.seed(1)
for prompt in ["把这句话翻译成英文", "帮我分析这份 CSV 的销售趋势"]:
    reply, cost = gateway(prompt)
    print(f"{prompt!r:32} -> 路由: {reply:24} 成本: ${cost:.4f}/1k token")
```

**运行结果**:简单任务(翻译)路由到小模型、复杂任务(分析)路由到大模型;小模型偶发超时时自动 Fallback 到大模型保证可用——这就是 L1 层"降本 + 保稳"的机制原型。

## 实践 / 应用:一次调用如何穿越 9 层

以"帮我分析这份 CSV 文件里的销售趋势"为例:

```
L0: 请求到达 K8s,调度到 GPU 节点
L1: 网关路由到复杂模型,启用 KV Cache
L2: 从向量库检索「CSV 分析最佳实践」
L3: System Prompt + RAG 结果 + 用户偏好拼装上下文
L4: LangGraph 启动工作流,Agent 决定读文件 + 执行代码
L5: E2B 沙箱启动 Python,执行 pandas 分析
L6: 读取用户偏好(中文报告),结果写入长期记忆
L7: 离线评测质量达标,在线监控幻觉率
L8: LangFuse 记录完整 Trace(Prompt/Tool Calls/Token/延迟)
```

每一步都有日志、都可追溯、都有 Fallback——**这就是生产级 Agent 与 Demo 级 Agent 的区别**。

### 技术选型路线图

| 阶段 | 每层怎么选(精简) |
| --- | --- |
| **验证期(1-2 周)** | 直接 OpenAI API + ChromaDB + Prompt 硬编码 + LangChain Chain + 本地 Docker + 变量存储 + 人工检查 + print 日志 |
| **原型期(1-2 月)** | LiteLLM + Pinecone/Qdrant + LangFuse + LangGraph/CrewAI + E2B + LangGraph Memory + RAGAS/Golden Set + LangFuse |
| **生产期(持续)** | 自建网关 + vLLM + 智能路由 + Milvus/Qdrant 集群 + Prompt Registry + LangGraph + Temporal + E2B/Modal/MCP + Mem0 + 在线评测门禁 + OTel/Grafana/告警,横切四能力全面落地 |

### Loop Engineering:循环的设计纪律

!!! tip "给生产环境设计循环"
    Loop 输出的质量,取决于它周围的 system。设计这个 system 的四件事:①保持 codebase 整洁(Claude 会遵循已有模式);②让 Agent 能验证自己(skills 编码团队对"高质量"的定义);③让 docs 容易获取(framework/library 文档含最新 best practices);④**用第二个 agent 做 code review——拥有全新 context 的 reviewer 偏见更少**。

- **失败要沉淀进 system**:某次结果没达标时,不要只修这一个问题——把经验编码进 system(新 skill / 新验证步骤 / 新规则),改善**未来所有 iteration**;
- **token 边界管理**(loop 必须拥有清晰边界):
  1. 选对 primitive 和 model——小任务不需要多个 agents 或复杂 loop,model/effort 选择是影响成本最大的杠杆之一;
  2. 定义成功标准和停止条件,明确"完成"长什么样;
  3. 大规模运行前先**试点**:在较小的工作切片上评估 usage;
  4. deterministic work 用 **script**(运行 script 比每次重新推理便宜得多);
  5. 不要超频运行 routine:让运行间隔匹配被监控对象的实际变化频率;
  6. 检查 usage(`/usage`、`/goal`、`/workflows` 查看消耗)。
- 与 9 层架构的关系:loop 设计落在 **L4(工作流编排)** 与 **L8(可观测)**——停止条件与 turn 上限就是 L4 的边界控制,每一步的 token/结果记录就是 L8 的 trace 来源。

## 总结

- 完整 AI Infra = **算力底座 + 模型网关 + 数据/RAG 管道 + Prompt/Context 管理 + Agent/Workflow 编排 + 工具执行沙箱 + 状态记忆 + 评测体系 + 可观测/SRE + 安全合规 + 成本与开发者平台**;
- **9 层纵向架构 + 4 横切能力缺一不可**;Demo 只需要 L1+L4,生产需要全部;
- 核心心法:每一层都要有日志、可追溯、有 Fallback;评测门禁与可观测是"能不能上生产"的裁判。

## 延伸阅读

- 站内:[Context Engineering](context-engineering.md)(L3 深入)、[Agent 评测](agent-evaluation.md)(L7 深入)、[Harness 章节](../08-harness/index.md)(L4/L5 开源索引)、[TencentDB Agent Memory](../08-harness/agent-memory-plugin.md)(L6 落地)、[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(权限/可观测工程化)、[中金:基于 Loop Engineering 的自动化因子发现引擎](../07-agent-coding/experience/loop-engineering.md)(loop 落地案例)
- 外部:原文(约 7500 字);LangGraph/CrewAI/AutoGen/OpenAI Agents SDK、E2B、Mem0、LangFuse、OpenTelemetry GenAI 语义约定、RAGAS、vLLM、LiteLLM、Pinecone/Qdrant 官方文档;原始资料存档于 `docs/inbox/ai-infra-source.md`
