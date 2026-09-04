# AgentScope:阿里通义的开箱即用平台级 Agent 框架

> **一句话摘要**:AgentScope 是阿里通义开源的"生产级、开箱即用"Python Agent 框架——从 Agent SDK 到多租户后端再到前端 Web UI 全栈覆盖,沙箱 + 权限 + 长期记忆 + 多租户一体化在七方对比中最完整,docstring 覆盖率 95%+(七方最高),支持中英双语社区。2.0 是相对 1.0 的 breaking change 重写。
>
> **来源**:GitHub https://github.com/agentscope-ai/agentscope;官方文档 https://docs.agentscope.io;对比数据见 [Agent 框架七方对比](agent-frameworks-seven-comparison.md);站内另有 08-harness 视角的 [AgentScope 2.0 专文](../08-harness/agentscope-managed-agents.md)

## 概念

**定位**:阿里通义团队开源的"生产级、开箱即用"Python(3.11+)Agent 框架,强调**随 LLM 能力提升而演进**——不靠严苛提示词和固定编排约束模型,而是"发挥模型的推理与工具调用能力"。官方定调"安全、高效、灵活、完备"(Secure/Efficient/Flexible/Complete)。

**在七方对比中的位置**:平台一体化设计最优秀(多租户/沙箱/权限/长期记忆一站式)、docstring 最全(95%+)、双语社区;短板:Beta + v2.0 刚起步(2.0.0 于 2026-05 发布)、仓库内文档薄、Lint 工具链旧(无 ruff)、测试无门控。

## 原理:核心概念

- **Agent**:框架核心抽象——一个**无状态的"推理-行动"循环引擎**,把模型、工具、权限系统、HITL、上下文管理、中间件、状态管理与事件系统统一为一个接口。主方法:`reply()`(返回最终 Msg)、`reply_stream()`(流式产出事件)、`observe()`(注入消息不触发推理)、`compress_context()`(超限压缩);
- **Msg 消息**:智能体间通信与持久化的基本单元,`UserMsg/AssistantMsg/SystemMsg` 三个工厂构造;content 由**内容块(ContentBlock)**组成:TextBlock、DataBlock(图片/音频/视频)、ThinkingBlock(思维链)、ToolCallBlock/ToolResultBlock(带状态机)、HintBlock(定时触发/团队消息/后台工具结果注入);
- **事件系统**:事件是消息的"流式视图",遵循 `start→delta→end` 模式;**一次 reply 产出的事件流可精确重建一条完整 Msg**(`append_event()`),后端经 SSE 推流、前端可断点重放;官方提供 TypeScript 版 `@agentscope-ai/agentscope` 让前后端用同一 API 重建消息;
- **Redis 消息总线**:服务层用 inbox 队列 + wakeup 信号唤醒会话——定时任务、团队消息、后台工具结果都经它投递,是分布式/多进程部署的基石;
- **多智能体协作**:SDK 层是"每个 agent 一个独立 ReAct 循环 + 独立事件流";服务层提供 **Agent Team**——leader agent 通过内置工具(TeamCreate/AgentCreate/TeamSay/TeamDelete/AgentInvite)按需孵化 worker 并协调,worker 是并行运行、各有状态/工作区/事件流的独立会话;
- **Sandbox/Workspace**:agent 的执行环境,提供工具(Bash/Read/Write/Edit…)、技能、MCP 服务器、上下文 offload 持久化。**7 种实现共用同一接口**:Local、Bubblewrap、Docker、E2B、Daytona、K8s、OpenSandbox;
- **长期记忆**:全部实现为**非侵入式 middleware**,三种后端可切换——Agentic Memory(原生 Markdown,agent 自主建/查 `Memory/` 目录)、ReMe(进程内文件式,自动抽取回写,可开向量检索)、Mem0(可复用 AgentScope 模型免额外 key);均支持 `static_control`(自动注入)/`agent_control`(提供 `memory_search` 等工具)/`both` 三种模式。

## 代码 / 实现:最小示例

```python
import asyncio, os
from agentscope.agent import Agent
from agentscope.model import DashScopeChatModel
from agentscope.credential import DashScopeCredential
from agentscope.message import UserMsg
from agentscope.tool import Toolkit, Bash, Read, Write, Edit

async def main():
    agent = Agent(
        name="Friday",
        system_prompt="You are a helpful assistant named Friday.",
        model=DashScopeChatModel(
            credential=DashScopeCredential(api_key=os.getenv("DASHSCOPE_API_KEY")),
            model="qwen-plus"),
        toolkit=Toolkit(tools=[Bash(), Read(), Write(), Edit()]),
    )
    # 方式1:await 最终消息;方式2:流式事件
    async for evt in agent.reply_stream(UserMsg("user", "Hello, who are you?")):
        print(evt.type)  # 处理 TEXT_BLOCK_DELTA / TOOL_CALL_START 等
asyncio.run(main())
```

长期记忆:给 Agent 挂上 `AgenticMemoryMiddleware(workdir=...)`,同一 workdir 重建 agent 即可跨会话回忆起"住在杭州、偏好简洁中文回答"。

## 实践 / 应用:关键特性与局限

### 一体化能力

**Agent Service(FastAPI)一屏托管**:多租户多会话、SQL/Redis 持久化、SSE 会话流 + 迟到重放、Cron 调度、后台任务 offload、RAG 服务、workspace 按 `per_agent/per_session/per_user` 粒度隔离。官方"三层安全防护":**工具级审查 + HITL 权限(require confirm/allow/deny/ask)+ 沙箱**。

**文档/docstring 极详尽**:每页含完整字段表和可下载示例代码;README 自带 DeepWiki 入口。**双语社区**:中文主页、Docs 支持 English|中文,Discord + 钉钉群,通义 DashScope/qwen 模型开箱即用(Apache-2.0)。

### 局限(2.0 Beta 态)

- 2.0.0 于 2026-05 发布,2.0.5(2026-07-23)为 stable;**realtime/tts/rag/evaluate 模块在 2.0 曾被临时移除待重构**(实时语音 agent 仍只见于 v1.0 文档,明确标注"实验性、开发中",仅支持少数 qwen 实时模型且工具支持不全);
- Agent Service **分布式部署标记 WIP**;
- **无内置用户认证**(默认 `X-User-ID` 占位,生产须自接 JWT/OAuth);
- 1.x 迁移需重构。

## 总结

- **定位**:阿里通义开源的平台级 Agent 框架——SDK + 多租户后端 + Web UI 全栈覆盖,开箱即用;
- **独家优势**:沙箱(7 种实现共用接口)+ 权限 + 长期记忆(3 种 middleware 后端)+ 多租户一体化最完整;docstring 95%+ 最全;双语社区;
- **事件系统**:start→delta→end 流式事件可精确重建完整消息,前端可断点重放;
- **适合**:要"研究原型直接进生产"的团队、安全敏感的工具型 agent、阿里生态、跨会话记忆/leader-worker 多智能体;
- **注意**:2.0 尚在 Beta,realtime/rag 等模块待重构,生产需自接认证;
- **下一步**:对比 [Agno](agno-framework.md)(同为平台级但生态更广)与 [MAF](microsoft-agent-framework.md)(企业级治理),或看站内 [AgentScope 2.0 专文](../08-harness/agentscope-managed-agents.md)(Managed Agents/Harness 视角)。

## 延伸阅读

- 官方:https://github.com/agentscope-ai/agentscope · https://docs.agentscope.io(v1.0 文档 https://doc.agentscope.io)
- 站内:[Agent 框架七方对比](agent-frameworks-seven-comparison.md)、[AgentScope 2.0 专文](../08-harness/agentscope-managed-agents.md)(08-harness:Managed Agents 底座视角)、[Agent 框架选型地图](agent-framework-selection.md)
