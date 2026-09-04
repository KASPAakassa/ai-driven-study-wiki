# OpenAI Agents SDK:官方轻量多智能体框架——Realtime/Voice 独家

> **一句话摘要**:OpenAI Agents SDK 是实验项目 Swarm 的"生产级升级版"——用极少量抽象原语(Agent / Handoff / Guardrail / Session)表达复杂智能体关系,内置 tracing 与评估支持;Realtime/Voice 实时语音能力在七方对比中独家。核心原则:"足够好用但足够少学"、"开箱即用但可精确定制"。
>
> **来源**:GitHub https://github.com/openai/openai-agents-python;官方文档 https://openai.github.io/openai-agents-python/;对比数据见 [Agent 框架七方对比](agent-frameworks-seven-comparison.md)

## 概念

**定位**:OpenAI 官方轻量级 Python 多智能体框架,底层默认走 **Responses API**,由 SDK 管理 turns、工具执行、guardrails、handoffs 与 sessions。两个驱动设计原则:

1. **"足够好用但足够少学"**:原语少(Agents、Agents-as-tools/Handoffs、Guardrails),学习曲线平缓;
2. **"开箱即用但可精确定制"**:默认行为合理,复杂场景可逐层定制。

**在七方对比中的位置**:轻量核心(7 依赖)、类型注解近 100%、四语文档 + 214 示例、沙箱生态广、Realtime/Voice 独家;短板:0.x API 不稳定、docstring 32% 薄、coverage 85% 有水分。

## 原理:核心概念

- **Agent**:被 instructions、tools、可选 runtime 行为(handoffs、guardrails、结构化输出 output_type)配置的 LLM;可配置 model、prompt 模板、hooks(生命周期回调)、tool_choice;
- **Runner**:执行器,`Runner.run()/run_sync()/run_streamed()` 驱动单次或多轮运行,自动处理工具调用、handoffs、guardrails、sessions,返回 RunResult(final_output、last_agent、to_input_list() 等);
- **Handoff**:agent 把对话控制权转交给专业 agent——对 LLM 呈现为 tool(如 `transfer_to_refund_agent`),可定制工具名、on_handoff 回调、input_type 结构化参数、input_filter(过滤传给下一 agent 的历史)、动态启用开关;
- **Guardrail**:输入/输出校验。**输入 guardrail 只作用于链条首个 agent,输出 guardrail 只作用于产出最终输出的 agent**;还支持 tool guardrail(每次函数工具调用前后)。校验失败触发 tripwire 异常立即中断;输入 guardrail 支持并行(默认)与阻塞两种模式;
- **Session**:内置会话记忆层,自动在多次 run 间维护对话历史;内置 SQLite/AsyncSQLite/Redis/SQLAlchemy/MongoDB/Dapr/加密等实现,支持自定义 Session 协议;
- **Tracing**:内置且默认开启,记录 LLM 生成、工具调用、handoff、guardrail 等事件,导出到 OpenAI Traces 仪表盘;traces 由 spans 组成,可自定义 processors 转发到第三方后端(20+ 集成);
- **Tool**:任意 Python 函数经 `@tool` 变为工具(自动生成 schema + Pydantic 校验),另有 MCP server 工具、hosted 工具(WebSearch/FileSearch 等)、`Agent.as_tool()` 将子 agent 包装为工具(manager 模式)。

## 代码 / 实现:最小示例

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")
result = Runner.run_sync(agent, "Write a haiku about recursion.")
print(result.final_output)
```

带 handoff 的多 agent:

```python
from agents import Agent, Runner

triage = Agent(name="Triage", instructions="Route to the right specialist.",
               handoffs=[Agent(name="History", handoff_description="历史问题专家",
                               instructions="回答历史问题")])
result = Runner.run_sync(triage, "罗马帝国何时灭亡?")
print(result.final_output, result.last_agent.name)
```

## 实践 / 应用:关键特性与局限

### 独家能力

1. **Realtime/Voice**:`RealtimeAgent`/`RealtimeRunner` 基于 WebSocket 的服务端低延迟语音智能体(gpt-realtime-2.1),支持自动打断检测(semantic_vad + interrupt_response)、上下文管理、guardrails、SIP/telephony 接入;`VoicePipeline` 提供 STT→agent→TTS 三段式语音管线(注意 Python SDK 不提供浏览器 WebRTC transport);
2. **沙箱生态**:`SandboxAgent` 让智能体在真实隔离工作区运行(manifest 定义文件、UnixLocal/Docker/托管沙箱客户端、可恢复会话),适合编码/文档类长任务;
3. **扩展生态**:LiteLLM/AnyLLM 第三方模型适配、MCP 原生集成、多后端 session、20+ 第三方 tracing 集成(LangSmith、Langfuse、W&B、Datadog、MLflow)。

### 局限

- API 尚在 **0.x 阶段**(当前 PyPI 0.19.4,2026-08-05),破坏性变更风险高;
- 部分功能标为 opt-in beta(如 nest_handoff_history);
- guardrail 有边界限制(输入 guardrail 只跑首个 agent);
- 要求 Python ≥3.10;ZDR(零数据留存)组织不可用 tracing。

**选型提示**:若只想"调用一次返回结果"或想自行掌控循环,直接用 Responses API 更合适——SDK 与 API 可混用。站内 [Agent 框架选型地图](agent-framework-selection.md) 将其定位为"循环层最顺手"的框架。

## 总结

- **定位**:OpenAI 官方 Swarm 的生产级升级版,原语极少(Agent/Handoff/Guardrail/Session),内置 tracing;
- **独家能力**:Realtime/Voice 实时语音、SandboxAgent 沙箱、20+ tracing 集成;
- **工程特点**:类型注解近 100%、四语文档、轻量核心;但 0.x 不稳定、docstring 薄;
- **适合**:需要 runtime 托管工具循环、多步协调、guardrails/handoffs/sessions 的生产应用;多智能体分工;低延迟语音助手;
- **下一步**:对比 [Pydantic AI](pydantic-ai-framework.md)(工程严谨度)与 [MAF](microsoft-agent-framework.md)(企业级双语言)。

## 延伸阅读

- 官方:https://github.com/openai/openai-agents-python · https://openai.github.io/openai-agents-python/(quickstart/handoffs/guardrails/sessions/realtime/voice/sandbox_agents/tracing)
- 站内:[Agent 框架七方对比](agent-frameworks-seven-comparison.md)、[Agent 框架选型地图](agent-framework-selection.md)(循环层定位)、[Agent 框架基础](agent-frameworks.md)
