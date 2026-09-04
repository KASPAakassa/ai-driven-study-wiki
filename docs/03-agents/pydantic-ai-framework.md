# Pydantic AI:工程严谨度天花板的 Python Agent 框架

> **一句话摘要**:Pydantic AI 以"工程严谨、类型安全、可直接上生产"为目标——把 FastAPI 的开发体验搬到 Agent 开发上:类型标注错误在写代码时(而非运行时)就被拦截,追求"Rust 式 if it compiles, it works"。自带 agent loop、依赖注入、Graph/Evals/Durable Execution 闭环,仓库强制 pyright strict + 100% coverage。
>
> **来源**:GitHub https://github.com/pydantic/pydantic-ai;官方文档 https://ai.pydantic.dev;对比数据见 [Agent 框架七方对比](agent-frameworks-seven-comparison.md)

## 概念

**定位**:Python GenAI Agent 框架,官方自称 "GenAI Agent Framework, the Pydantic way"。核心设计理念:以 **Pydantic Validation + Python 类型标注**为地基,让 IDE/静态检查器在写代码时就拦截整类错误——"如果编译通过,它就能工作"。自带 agent loop(内置重试/自我纠错)、可组合的 capabilities 系统(thinking、web search、web fetch、MCP 即插即用),以及 Graph 与 Evals 子框架,深度集成自家 OpenTelemetry 可观测平台 **Pydantic Logfire**。

**在七方对比中的位置**:工程严谨度天花板——pyright strict + 100% coverage 硬门控、测试/源码比 2.2×(七方最高)、社区最大(516 贡献者)、供应链安全最严(Dependabot+zizmor+SHA);短板:代码库庞大复杂、v1→v2 breaking 多、无内置服务运行时。

## 原理:核心概念

- **Agent**:对 LLM 交互的主接口,是"指令 + 工具 + 输出校验 + 依赖注入"的容器。泛型类型 `Agent[Deps, Output]`,一次 `run` 会进行多轮工具调用循环直至产出最终结果;
- **Dependencies(依赖注入)**:通过 `deps_type` 声明依赖类型(通常是 dataclass),`run(deps=...)` 时注入。system prompt/tool/output validator 通过 `RunContext[Deps]` 访问 `ctx.deps`,类型写错会被静态检查器立即捕获;单测时用 `agent.override(deps=...)` 替换;
- **Tools**:`@agent.tool` / `@agent.tool_plain` 注册函数工具;函数签名自动生成 JSON Schema,docstring 解析为工具/参数描述,参数由 Pydantic 校验,失败时把错误回传 LLM 重试;支持 `ModelRetry` 主动要求重试、deferred tools 人工审批、toolsets 批量管理;
- **Result**:`agent.run()` 返回 `AgentRunResult`,`.output` 被 Pydantic 校验并保证为 `output_type`(校验失败自动反射重试);`.all_messages()` 暴露完整消息历史;
- **Evals(pydantic-evals)**:独立包,code-first 评测框架——`Dataset → Case → Experiment(Task + Evaluator)` 数据模型,类比"单测套件 + pytest 报告";支持内置 evaluator、LLM Judge、span-based 评估(基于 OTel trace 评估内部工具调用过程)、在线评测,结果写入 Logfire;
- **Graphs(pydantic-graph)**:独立包,纯类型标注驱动的异步图/状态机库。节点 `BaseNode.run(ctx)` 的**返回类型即出边**(union 表示分支,`End` 表示终止),支持 state、依赖注入、自动生成 mermaid 图。官方提醒:**Agent 是锤子、Graphs 是钉枪**,复杂工作流才需要;
- **Durable Execution**:让 agent 在 API 瞬时故障、应用重启后保留进度,支撑长时/异步/human-in-the-loop 工作流。官方集成 Temporal、DBOS、Prefect,Restate 通过公共接口对接。

## 代码 / 实现:最小示例

```python
from pydantic_ai import Agent

agent = Agent(
    'anthropic:claude-sonnet-4-6',
    instructions='Be concise, reply with one sentence.',
)
result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
```

依赖注入 + 结构化输出 + 工具的最小完整形态:

```python
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

@dataclass
class SupportDependencies:
    customer_id: int
    db: object  # 如 DatabaseConn

class SupportOutput(BaseModel):
    support_advice: str
    block_card: bool
    risk: int  # 0-10

agent = Agent('openai:gpt-5.2', deps_type=SupportDependencies,
              output_type=SupportOutput)

@agent.tool
async def customer_balance(ctx: RunContext[SupportDependencies]) -> float:
    """Returns the customer's current account balance."""
    return 123.45  # ctx.deps.db.customer_balance(id=ctx.deps.customer_id)

result = agent.run_sync('What is my balance?',
                        deps=SupportDependencies(customer_id=123, db=...))
print(result.output)  # 保证是 SupportOutput
```

## 实践 / 应用:工程严谨度与适合场景

### 工程严谨度(源码实测)

- `pyproject.toml`:`[tool.pyright] typeCheckingMode = "strict"`、`[tool.coverage.report] fail_under = 100`(强制 100% 覆盖率,配 strict-no-cover 工具)、ruff 严格规则集;
- `make` 默认执行 format+lint+typecheck+coverage;README 常驻 CI 与 coverage badge;
- **slim 核心**:`pydantic-ai-slim` 为最小核心,全部模型/功能(openai、google、mcp、temporal、evals 等)都是 optional extras 按需装配;完整版 `pydantic-ai` 只是预装常用 extras 的元包;Evals 与 Graph 均不依赖 pydantic-ai,可独立使用。

### 适合场景

需要强类型、高可测、可观测的生产级 Agent/RAG/SQL 生成/多 agent 编排;追求 evals 与日志链路闭环的团队;依赖注入模式便于单测替换的代码库。

### 局限

- 上手门槛高于 LangChain 等框架(官方自嘲"不喜类型标注的人可能已被劝退");
- Graph 面向高级用户,泛型重、对初学者不友好;
- 文档体量大,部分集成(durable 各家、Agent Specs YAML 配置)复杂度高;
- 生态广度与社区规模不及 LangChain;快速演进的 capabilities API 可能有迁移成本。

## 总结

- **定位**:Pydantic 官方,"the Pydantic way"——类型安全 + 强校验 + 工程严谨度天花板;
- **独有闭环**:evals + graph + durable-exec + Logfire 观测,同一数据模型贯穿;
- **工程纪律**:pyright strict + 100% coverage 硬门控、slim 核心按需装配、供应链安全最严;
- **适合**:追求"能编译就能跑"的生产级团队,依赖注入便于单测;
- **下一步**:对比 [MAF](microsoft-agent-framework.md)(同为工程严谨但双语言+企业治理)与 [OpenAI Agents SDK](openai-agents-sdk.md)(轻量快上手)。

## 延伸阅读

- 官方:https://github.com/pydantic/pydantic-ai · https://ai.pydantic.dev(agents/tools/dependencies/evals/graph/capabilities/durable_execution)
- 站内:[Agent 框架七方对比](agent-frameworks-seven-comparison.md)、[Agent 框架选型地图](agent-framework-selection.md)、[Skill 测评](../07-agent-coding/skills/skill-evaluation.md)(evals 思路呼应)
