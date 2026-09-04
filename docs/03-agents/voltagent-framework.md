# VoltAgent:框架 + VoltOps 平台双形态的 TypeScript Agent 工程平台

> **一句话摘要**:VoltAgent 是端到端 AI Agent 工程平台,由"开源 TypeScript Agent 框架 + VoltOps 云端/自托管控制台"双形态构成——框架内建 Memory、RAG、Guardrails、Tools、MCP、Voice、Workflow,平台端提供可观测性、部署、Evals、Prompt 管理。全 provider 内建开箱即用、Guardrails/evals/scorers 一体、resumable-streams 可恢复流都是特色。
>
> **来源**:GitHub https://github.com/voltagent/voltagent;官方文档 https://voltagent.dev/docs;对比数据见 [Agent 框架七方对比](agent-frameworks-seven-comparison.md)

## 概念

**定位**:端到端 AI Agent 工程平台(10.3k stars,MIT,npm 包 `@voltagent/core`,v2.0.x)。设计理念:**"以完整代码控制构建 Agent,再以生产级可视性与运维能力交付"**——开源框架保代码可控,VoltOps 补足 observability、deployment、triggers/actions、prompt 管理,形成"开发→测试→部署→监控"闭环。

**在七方对比中的位置**:框架+平台双形态、全 provider 内建开箱即用、Guardrails/evals/scorers 一体、文档/示例生态强(342 md+87 示例+多语言 README)、工程基础扎实(Biome/commitlint/syncpack/publint/husky);短板:测试治理最薄弱(测试/源码比 0.19×)、核心包依赖最重(44 prod deps)、12/33 包无 README、起步晚但迭代快(2025-04 起,14 个月 1.7k 提交)。

## 原理:核心概念

- **Agent**:包装语言模型的对象,聚合 `name`/`instructions`/`model`/`tools`/`memory`/`guardrails`/`subAgents` 等。核心方法 `generateText`/`streamText`(支持 `fullStream` 细粒度事件);可通过 Hono HTTP server(默认端口 3141)暴露 REST/SSE 端点(`/agents/:id/text|stream|chat|object`);
- **Guardrails**:运行时拦截并校验 Agent 输入/输出。`createInputGuardrail()` 在输入到达模型前执行;`createOutputGuardrail()` 在模型生成后执行,支持 `allow`/`modify`/`block` 三种动作,`streamHandler` 可实时改写/丢弃流式 chunk 甚至 `abort` 终止流;
- **Evals**:离线+在线评估——离线跑固定数据集做回归/CI 门禁,在线采样生产流量做监控与内容审核;构建块为 `createExperiment`(数据集+runner+scorers+通过标准)、CLI(`npm run volt eval run`)或 Node API,结果回流 VoltOps;
- **Scorers**(`@voltagent/scorers`):评分函数——启发式无 LLM 版(exactMatch、levenshtein、jsonDiff、listContains、numericDiff)、LLM-judge 版(answerCorrectness、factuality、moderation、summary、translation、humor、RAG 评分:contextPrecision/Recall/Relevancy 等)、工具调用准确性(toolCallAccuracy)与自定义 `buildScorer`;
- **Resumable-streams**(`@voltagent/resumable-streams`):让客户端刷新后重连进行中的流并继续接收同一响应。双存储设计(stream store 存 chunk+pub/sub、active stream store 映射 `userId+conversationId→streamId`);Hono 暴露恢复端点;存储可选 VoltOps 托管/Redis(生产推荐)/Memory(开发);启用需 `resumableStream:true`+`conversationId`+`userId`,启用后不可用 abort;
- **VoltOps Console**(console.voltagent.dev,云或自托管 Docker/K8s):基于 OpenTelemetry 的 traces/dashboard/logs/memory 管理/成本监控、Prompt Builder、Evals 运行、Triggers & Actions 自动化、一键 GitHub 部署、RAG 知识库;
- **全 Provider 内建**:框架构建在 Vercel AI SDK 之上;模型字符串(如 `openai/gpt-4o-mini`)由内置 Model Router 解析(registry 快照源自 models.dev),**无需导入 provider 包**,只设 API key 环境变量,覆盖 30+ provider。

## 代码 / 实现:最小示例

```ts
// 最小 Agent + HTTP 服务
import { VoltAgent, Agent } from "@voltagent/core";
import { honoServer } from "@voltagent/server-hono";

const agent = new Agent({
  name: "my-voltagent-app",
  instructions: "A helpful assistant that answers questions",
  model: "openai/gpt-4o-mini", // "provider/model" 字符串,无需导入 provider 包
});

new VoltAgent({ agents: { agent }, server: honoServer() }); // 默认 3141 端口
```

带 Zod 类型化工具与 Guardrails 的 Agent:

```ts
import { Agent, createTool, createOutputGuardrail } from "@voltagent/core";
import { z } from "zod";

const weatherTool = createTool({
  name: "get_weather",
  description: "Get current weather for a location",
  parameters: z.object({ location: z.string() }),
  execute: async ({ location }) => ({ temperature: 72, conditions: "sunny" }),
});

const trimGuardrail = createOutputGuardrail({
  id: "trim-output",
  name: "Trim Whitespace",
  handler: async ({ output }) => ({
    pass: true, action: "modify",
    modifiedOutput: typeof output === "string" ? output.trim() : output,
  }),
});

const agent = new Agent({
  name: "Weather Assistant",
  instructions: "Answer weather questions using get_weather.",
  model: "openai/gpt-4o-mini",
  tools: [weatherTool],
  outputGuardrails: [trimGuardrail],
});
const result = await agent.generateText("What's the weather in SF?");
console.log(result.text);
```

## 实践 / 应用:适合场景与局限

### 适合场景

需要"从原型到生产一条龙"的 TypeScript Agent 应用;多 Agent 编排与带人工审批的长流程;对可观测性/traces、guardrails、evals 有强需求;移动端刷新/弱网需要可重连流式响应的场景;愿意绑定 VoltOps 平台(云或自托管)的团队。

### 局限

- **测试治理仍较薄弱**:Evals 文档多处标注"(upcoming)",eval/CI 治理成熟度与 LangSmith 等相比处于早期;
- **核心依赖偏重**:强耦合 Vercel AI SDK(`ai` 包必装)与 models.dev 快照;要求 Node.js 20.19+;生产环境 resumable-streams 需 Redis;
- 原生 provider 包(`@voltagent/anthropic-ai` 等)已弃用需迁移;
- 部分能力(VoltOps managed store 并发流)受商业套餐额度限制(Free 仅 1 并发流),深度使用会绑定付费平台。

## 总结

- **定位**:端到端 TS Agent 工程平台——开源框架 + VoltOps 控制台双形态,"开发→测试→部署→监控"闭环;
- **独家能力**:全 provider 内建开箱即用、Guardrails/evals/scorers 一体(框架与平台共享同一套 registry)、resumable-streams 可恢复流;
- **工程特点**:Biome/commitlint/syncpack 现代工具链,但测试治理最薄弱、核心依赖最重;
- **适合**:TS 全栈 + 对可观测性/guardrails/evals 有强需求的团队、弱网可重连流式场景;
- **注意**:Evals 文档部分未落地、深度使用绑定 VoltOps 平台;
- **下一步**:对比 [Mastra](mastra-framework.md)(同为 TS 但更重全栈生态)与 [OpenAI Agents SDK](openai-agents-sdk.md)(Python 侧 Guardrails 对照)。

## 延伸阅读

- 官方:https://github.com/voltagent/voltagent · https://voltagent.dev/docs(agents/guardrails/evaluation-docs/resumable-streaming/observability-docs/providers-models)
- 站内:[Agent 框架七方对比](agent-frameworks-seven-comparison.md)、[Agent 框架选型地图](agent-framework-selection.md)、[Agent 框架基础](agent-frameworks.md)
