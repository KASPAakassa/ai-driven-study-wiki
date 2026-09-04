# Microsoft Agent Framework (MAF):双语言企业级 Agent SDK

> **一句话摘要**:MAF 是微软官方的生产级 Agent SDK,**Semantic Kernel 与 AutoGen 的直接继任者**——融合 AutoGen 的简单 agent 抽象与 Semantic Kernel 的企业级能力,新增基于图的 workflow;Python + .NET 双语言 API 对称,核心极轻量(4 依赖),Durable Task 持久化/time-travel、声明式 YAML Agent、Azure Purview 治理都是独家能力。
>
> **来源**:GitHub https://github.com/microsoft/agent-framework;官方文档 https://learn.microsoft.com/en-us/agent-framework/;对比数据见 [Agent 框架七方对比](agent-frameworks-seven-comparison.md)

## 概念

**定位**:微软开源的生产级 Agent SDK,官方明确称其为 **Semantic Kernel 与 AutoGen 的直接继任者**(同一团队打造)。设计理念:融合 **AutoGen 简单直接的 agent 抽象**与 **Semantic Kernel 的企业级能力**(session 状态管理、类型安全、middleware/filters、遥测),并**新增基于图的 workflow** 获得对多 agent 编排路径的显式控制。Python + .NET 同步支持、API 一致,Go 已加入(public preview)。

**在七方对比中的位置**:双语言独一档、核心最轻(4 依赖)、类型检查最严(pyright strict + mypy strict + bandit 双栈全覆盖)、Durable Task 持久化/time-travel 强;短板:扩展包大量 preview(35 包仅 5 个 released)、历史短(2025 起)、深度绑定 Azure。

## 原理:核心概念

- **Agent**:由 LLM 驱动的独立个体,支持调用工具、MCP server 与生成响应;全部派生自统一基类 `AIAgent`,可跨 agent 编排。提供方覆盖 Microsoft Foundry、Azure OpenAI、OpenAI、Anthropic、Ollama、Gemini、Bedrock 等。另有 **Harness**(内置能力"全家桶"agent:规划与 todo 跟踪、上下文压缩、文件访问、内存、工具审批、可观测性);
- **Workflow**:基于有向图的编排,用 **executor**(处理单元)+ **edge**(带条件的连接)表达 sequential/concurrent/handoff/group 等模式;支持类型安全路由、superstep 并行、HITL、checkpoint。另有 **Functional Workflow API**(Python experimental,`@workflow`/`@step` 装饰器,原生 Python 控制流);
- **Durable Task(持久化执行)**:通过 Durable Extension 接入——自动持久化会话、checkpoint 编排/workflow、故障后恢复不重跑已完成步骤、跨分布式无状态 worker 扩容、等待人工输入不耗 token;托管方式:Azure Functions(serverless)或 bring-your-own-compute(自托管 worker/容器/K8s),后端为 Azure Durable Task Scheduler(BaaS,gRPC 接入、内置 dashboard);
- **time-travel**:workflow 基于 checkpoint 实现"时间旅行"——每个 superstep 结束保存完整状态(executor 状态、待处理消息、共享状态),可从任意 checkpoint 就地恢复或将状态 rehydrate 到新 run 重新执行(调试/回放);Python 端提供 InMemory/File/Cosmos 三种存储;
- **YAML 声明式 Agent**:用 YAML/JSON 定义 agent(`kind: Prompt`、instructions、model options、outputSchema 等),无需代码即可创建/版本化/分享;
- **多语言运行时**:Python 与 .NET 完整支持且 API 对称;Go 处于 public preview(declarative/RAG/CodeAct/functional workflows 尚缺);另有 Agent Skills(遵循 agentskills.io 开放规范、四阶段渐进披露)与 DevUI。

## 代码 / 实现:最小示例

Python(`pip install agent-framework`):

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

agent = Agent(
    client=FoundryChatClient(credential=AzureCliCredential()),
    name="HelloAgent",
    instructions="You are a friendly assistant. Keep your answers brief.",
)
print(await agent.run("What is the largest city in France?"))
```

.NET:

```csharp
AIAgent agent = new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
    .AsAIAgent(model: deploymentName,
               instructions: "You are a friendly assistant. Keep your answers brief.");
Console.WriteLine(await agent.RunAsync("What is the largest city in France?"));
```

## 实践 / 应用:关键特性与局限

### 企业级能力

- **Python + .NET 双栈**:统一核心 API、齐全 provider/样本,Go 跟进中;
- **依赖构成**:`pip install agent-framework`(1.13.0)只需 `agent-framework-core[all]` 单一核心依赖——早期拆分的 4 个基础子包已收敛为 core + 大量可选扩展包(a2a、foundry、declarative、purview、azure-cosmos 等);
- **Durable Task 持久化**:会话/编排状态落盘于 Durable Task Scheduler,跨实例恢复、TTL 清理、dashboard 监控;
- **Azure 生态**:深度集成 Foundry、Azure OpenAI、Cosmos(checkpoint/记忆)、Redis(可靠流)、OpenTelemetry 可观测性;**Purview 治理**(preview)以 middleware 在 prompt/response 两阶段做 DLP 策略拦截,输出可进入 Purview 审计/eDiscovery/Insider Risk。

### 局限

- 大量扩展包为 preview(declarative、durable、purview、functional workflows 等),需 `--pre` 安装、API 迭代快;
- **强绑定 Azure**(quickstart 默认 Azure 凭据与 Foundry endpoint,非 Azure/第三方使用被官方声明"自担风险");
- Go 支持不完整;Python 功能式 workflow 标注 experimental;框架不自动加载 .env。

## 总结

- **定位**:Semantic Kernel 与 AutoGen 的直接继任者——AutoGen 的简单抽象 + Semantic Kernel 的企业能力 + 图 workflow;
- **独家能力**:Python+.NET 双语言、声明式 YAML Agent、Durable Task 持久化/time-travel、Purview 治理;
- **工程纪律**:核心 4 依赖最轻、pyright strict + mypy strict + bandit 双栈最严;
- **适合**:生产级 agent、需长期运行/重启恢复/多 agent 编排/人工介入/治理审计的企业场景,尤其 Azure 技术栈团队;
- **注意**:扩展包大量 preview、强绑定 Azure;
- **下一步**:对比 [Pydantic AI](pydantic-ai-framework.md)(同为工程严谨标杆但无服务运行时)与 [AgentScope](agentscope-framework.md)(平台一体化)。

## 延伸阅读

- 官方:https://github.com/microsoft/agent-framework · https://learn.microsoft.com/en-us/agent-framework/(overview/agents/workflows/checkpoints/declarative/durable-extension)
- 站内:[Agent 框架七方对比](agent-frameworks-seven-comparison.md)、[Agent 框架选型地图](agent-framework-selection.md)、[通用编排框架](../08-harness/orchestration-frameworks.md)(MAF 收录条目)
