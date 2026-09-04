# Agno(原 Phidata):Agent 平台 SDK——最广集成矩阵 + AgentOS 生产运行时

> **一句话摘要**:Agno 是"**构建 → 运行 → 管理**"的 Agent 平台框架——用 Python SDK 构建 Agent,用 **AgentOS** 运行时把它跑成生产服务(REST/MCP/多聊天接口 + 持久化 + RBAC + 调度),用 Control Plane Web UI 监控。生态覆盖面七方对比中最广:30+ 模型、100+ 工具、19 向量库、多数据库。
>
> **来源**:GitHub https://github.com/agno-agi/agno;官方文档 https://docs.agno.com;对比数据见 [Agent 框架七方对比](agent-frameworks-seven-comparison.md)

## 概念

**定位**:"Build, run, and manage agent platforms"——Agno(2025 年初由 Phidata 更名)不是单个 Agent 库,而是一套完整平台:用 Python SDK 构建 Agent,用 **AgentOS** 运行时跑成生产服务,用 **Control Plane(Web UI)** 监控管理。核心理念是**"拥有你自己的 agent 栈"**:数据、记忆、安全(JWT-based RBAC)都由你掌控,可部署到任意云。

**在七方对比中的位置**:生态覆盖面最广(46 模型 / 100+ 工具 / 18 向量库 / 16 存储),自带 AgentOS 生产运行时,cookbook 海量(2,101 个示例),发版最频繁(1–3 天/版),核心依赖最轻(13)。短板:docs 私有不透明、超大文件(workflow.py 10,794 行)、无 coverage 门控。

## 原理:核心概念

- **Agent**:构建模型上下文、执行工具、返回响应的程序——最小编排单元,可挂 memory/knowledge/storage/guardrails/human-in-the-loop;
- **Model**:连接 Agent/Team 与模型提供商的抽象,支持字符串(`"openai:gpt-5.5"`)或类形式,内置重试/回退模型;
- **Tool**:可被调用的函数,来源包括 Python 函数、预建 Toolkit、MCPTools、Context Provider;支持 `requires_confirmation`(人工审批);
- **Memory**:跨会话记住用户偏好/事实,按 `user_id` 存库,分 automatic(`update_memory_on_run`)与 agentic(`enable_agentic_memory`)两种模式;
- **Storage(Database)**:`db` 参数持久化 session/run/state/memory/traces,支持 SQLite/Postgres/MySQL/MongoDB/Redis/DynamoDB 等;
- **Knowledge**:文档/URL/数据库的 RAG 知识库,ingestion→chunking/embedding→检索,默认 **Agentic RAG**,支持 19 种向量库;
- **Workflow**:用定义好的 steps 编排 Agent/Team/函数/嵌套 Workflow,支持顺序、并行、循环、条件分支;
- **Team**:leader 协调多 agent(可嵌套),有 coordinate/route/broadcast/tasks 等委派模式;
- **AgentOS**:"The FastAPI for agents"——把同一批 Agent 变成 REST API + MCP server + 多聊天接口,提供持久化、JWT RBAC、后台执行、tracing、调度等生产能力。

## 代码 / 实现:最小示例

```python
from agno.agent import Agent
from agno.tools.workspace import Workspace

agent = Agent(
    name="Sorting Hat",
    model="openai:gpt-5.5",
    tools=[Workspace(".")],
    instructions="Inventory the folder and propose a structure.",
    markdown=True,
)
agent.print_response("Inventory ./my_folder", stream=True)
```

带上存储与运行时的服务版(`pip install 'agno[os]'`):

```python
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS

agent = Agent(model="openai:gpt-5.5",
              db=SqliteDb(db_file="workbench.db"),
              enable_agentic_memory=True, add_history_to_context=True)
agent_os = AgentOS(agents=[agent], tracing=True)
app = agent_os.get_app()
if __name__ == "__main__":
    agent_os.serve(app="workbench:app", reload=True)   # localhost:7777
```

## 实践 / 应用:适合场景与局限

**适合**:产品 Copilot/客服 agent、知识型 Agent(RAG)、工作流自动化、多租户 SaaS Agent 平台、Slack/TG/WA 办公 bot;官方起点模板覆盖 Railway/AWS/GCP/Azure/K8s。

**局限**:

1. 官方 SDK 为 **Python 专用**;
2. **Team 会带来延迟与 token 成本**(leader+成员多次模型调用),单任务优先用单个 Agent;
3. 功能面大、演进快(v2.x 迭代频繁,部分 API 有弃用),需跟紧文档;
4. 默认开启遥测(仅统计运行次数,可设 `AGNO_TELEMETRY=false`);
5. License 为 Apache-2.0,但部分企业特性偏向 AgentOS 生态。

## 总结

- **定位**:Agent 平台 SDK——构建(SDK)→ 运行(AgentOS)→ 管理(Control Plane),"拥有你自己的 agent 栈";
- **集成广度七方第一**:30+ 模型、100+ 工具、19 向量库、多数据库、Slack/TG/WA 多聊天接口;
- **AgentOS 生产运行时**:50+ REST 端点、JWT RBAC、后台执行、checkpoint、cron 调度、OpenTelemetry tracing;
- **关键权衡**:生态最广 + 核心最轻,但 docs 私有、超大文件、无 coverage 门控;
- **下一步**:对比 [Pydantic AI](pydantic-ai-framework.md)(工程严谨度)与 [Mastra](mastra-framework.md)(JS 全栈),或看 [Agent 框架选型地图](agent-framework-selection.md)。

## 延伸阅读

- 官方:https://github.com/agno-agi/agno · https://docs.agno.com(AgentOS: https://docs.agno.com/agent-os/introduction)
- 站内:[Agent 框架七方对比](agent-frameworks-seven-comparison.md)、[Agent 框架选型地图](agent-framework-selection.md)、[Agent 框架基础](agent-frameworks.md)
