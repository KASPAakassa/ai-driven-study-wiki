# Mastra:JS 生态最完整的全栈 Agent 平台

> **一句话摘要**:Mastra 是"现代 TypeScript 栈"的全栈开源 Agent 框架——把从原型到生产的一切(Agent、工作流、记忆、存储、可观测性、评估、部署)装进一套 JS 生态,可嵌入 React/Next.js/Node,也可作为独立 Node 服务器部署。140+ 包/27 store/17 voice/12 auth、Playground 可视化、模板脚手架,是七方对比中 JS 生态最完整的平台。
>
> **来源**:GitHub https://github.com/mastra-ai/mastra;官方文档 https://mastra.ai/docs;对比数据见 [Agent 框架七方对比](agent-frameworks-seven-comparison.md)

## 概念

**定位**:"TypeScript 专属 + 围绕成熟 AI 模式设计"——一条命令建项目、一个 `Mastra` 实例注册全部资产(agents/workflows/storage/server)。把从早期原型到生产部署所需的一切装进一套 JS 生态。

**在七方对比中的位置**:JS 生态最完整全栈(140+ 包/27 store/17 voice/12 auth/8 server-adapter/4 deployer)、文档最多(905 md)、发版最频繁(16k 提交)、发布流水线最先进(changesets+OIDC+Renovate)、Playground 可视化;短板:体量巨大(118 万行源码)、"上帝包"(packages/core 23.4 万行)、无 coverage 门控、依赖网络复杂、AI bot 提交占比高。

## 原理:核心概念

- **Agent**(`@mastra/core/agent`):用 LLM+工具解决开放式任务的自主智能体,`.generate()`(完整响应)与 `.stream()`(流式);多个子 agent 可组成 supervisor 多智能体系统;
- **Workflow**(`createStep()`/`createWorkflow()`):图式编排引擎,`.then()/.branch()/.parallel()/.foreach()/.map()/.sleep()` 显式控制流;支持 state 共享、suspend/resume(人类介入)、time travel(重放单步)、嵌套工作流、调度;
- **Tool**(`createTool()`):结构化可调用能力,必须含 `id/description/inputSchema/execute()`(zod/valibot/arktype 均可);支持 MCP 服务器、subagent/工作流转 tool、hooks、流式生命周期;
- **Memory**(`@mastra/memory`):**四层记忆**——消息历史、Observational Memory(后台 agent 把旧消息压缩成 observation 保持上下文精简)、Working Memory(持久化用户结构化数据)、Semantic Recall(语义检索),支持多用户线程;
- **Store/Storage**(`@mastra/libsql` 等):运行时持久化层,按 9 个 domain(memory/workflows/observability/scores/datasets/experiments/backgroundTasks/schedules/threadState)组织;`MastraCompositeStore` 可按域路由到不同数据库;默认内存库,本地 libSQL 文件库,生产推荐 Postgres;
- **Voice**:统一语音接口(TTS/STT/实时语音),`OpenAIVoice`/`ElevenLabsVoice`/`AzureVoice`/`DeepgramVoice`/`GeminiLiveVoice` 等;`CompositeVoice` 可混用不同 provider;实时通话交给 LiveKit;
- **Studio(Playground)**:`mastra dev` 后打开 `localhost:4111`——对话测试 agent(切换模型/temperature)、以图形式可视化运行 workflow、单跑 tool、查看 traces/logs,内置 Scorers/Datasets/Experiments 评估能力;
- **Deployer/部署**:三条路径——`mastra build`(独立 Hono 服务器)/ `mastra deploy`(Mastra 云平台,含托管数据库、多环境、GitHub push-to-deploy)/ 内置 deployers(Vercel/Netlify/Cloudflare)。

## 代码 / 实现:最小示例

```ts
// ① 工具 + ② Agent(注册于 Mastra 实例)
import { createTool } from '@mastra/core/tools'
import { Agent } from '@mastra/core/agent'
import { z } from 'zod'

const weatherTool = createTool({
  id: 'get-weather',
  description: 'Get current weather for a location',
  inputSchema: z.object({ location: z.string() }),
  execute: async ({ location }) => ({ location, temp: 21, conditions: 'sunny' }),
})

export const weatherAgent = new Agent({
  id: 'weather-agent', name: 'Weather Agent',
  instructions: 'You are a helpful weather assistant. Use the weatherTool.',
  model: 'openai/gpt-5.6-sol', // "provider/model" 字符串,自动读 OPENAI_API_KEY
  tools: { weatherTool },
})
```

```ts
// ③ Workflow:确定性多步流程
import { createWorkflow, createStep } from '@mastra/core/workflows'
const step1 = createStep({
  id: 'step-1',
  inputSchema: z.object({ message: z.string() }),
  outputSchema: z.object({ formatted: z.string() }),
  execute: async ({ inputData }) => ({ formatted: inputData.message.toUpperCase() }),
})
export const testWorkflow = createWorkflow({ id: 'test-workflow',
  inputSchema: z.object({ message: z.string() }) }).then(step1).commit()

// 注册与调用:
// new Mastra({ agents: { weatherAgent }, workflows: { testWorkflow } })
// mastra.getAgentById('weather-agent').generate('Weather in SF')
```

## 实践 / 应用:适合场景与局限

### 适合场景

TypeScript/JS 全栈团队在 Node/React/Next.js 生态内构建生产级 AI 应用,需要 agent+工作流编排+记忆+观测+评估一体化;要接 MCP、RAG、多通道(Slack/Discord/Telegram/WhatsApp)或实时语音;想从"玩具 demo"平滑走到"可部署服务器"。客户案例:Replit、Sanity、SoftBank、WorkOS、Factorial、Fireworks。

### 局限

1. **体量大/上帝包**:百级 npm 包、数百文档页,概念面(Agent/Workflow/Harness/Memory/Processors/Signals/Workspaces…)学习曲线陡;
2. **快速演进 API 波动**:v1 大量迁移指南(AI SDK v4→v5、network→supervisor 等)印证破坏性变更频繁;
3. 面向 JS 生态,不服务 Python 团队;
4. 完整体验(托管 Observability/Studio/Server、EE 功能)依赖付费云平台与商业授权。

## 总结

- **定位**:TypeScript 专属全栈 Agent 平台——"一条命令建项目、一个实例注册全部资产";
- **独家能力**:JS 生态最完整全栈(store/voice/auth/deployer/playground 全覆盖)、四层记忆、Studio 可视化、模板脚手架(20+ 官方模板);
- **工程特点**:发布流水线最先进(changesets+OIDC+Renovate),但体量巨大、上帝包、无 coverage 门控;
- **适合**:Node/React/Next.js 生态的生产级 AI 应用,一体化需求强;
- **下一步**:对比 [VoltAgent](voltagent-framework.md)(同为 TS 但框架+平台双形态、Guardrails/evals 一体)与 [Agno](agno-framework.md)(Python 侧生态最广)。

## 延伸阅读

- 官方:https://github.com/mastra-ai/mastra · https://mastra.ai/docs(agents/workflows/memory/storage/studio/deployment/mastra-platform)
- 站内:[Agent 框架七方对比](agent-frameworks-seven-comparison.md)、[Agent 框架选型地图](agent-framework-selection.md)、[Agent 框架基础](agent-frameworks.md)
