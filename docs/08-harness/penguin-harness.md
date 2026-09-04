# PenguinHarness:让 Agent 自主构建 Agent 的开源平台

> **一句话摘要**:LlamaFactory 作者(hiyouga)推出的开源"自进化 Agent 构建平台":输入一句话自动生成 Agent 应用,Agent 还能自己跑评测、找失分点、迭代发布 N+1 版本。本文收录其定位、核心能力与生态。
>
> **来源**:微信公众号《PenguinHarness:自进化 Agent 的时代来了》,https://mp.weixin.qq.com/s/lWlMRXeUDFYCBvAByjF4Cg;项目官方仓库 https://github.com/Prism-Shadow/penguin-harness(2026-07 开源)

## 概念

**PenguinHarness** 是 2026 年 7 月上线的开源 Agent 构建平台,作者 **Yaowei Zheng(hiyouga)**——此前以 **LlamaFactory**(GitHub 47k+ stars,大模型微调框架)闻名。它的定位一句话:**让 Agent 自主构建 Agent**。

| 项目信息 | 内容 |
| --- | --- |
| 仓库 | [github.com/Prism-Shadow/penguin-harness](https://github.com/Prism-Shadow/penguin-harness) |
| 协议 | Apache-2.0 |
| 技术栈 | Node.js / TypeScript |
| 平台 | macOS / Windows / Linux(桌面端 App / CLI / SDK / 无界面服务) |
| 支持模型 | DeepSeek V4 / Kimi / GLM / Qwen / GPT / Claude |
| 官网 / 文档 | https://penguin.ooo/ · https://penguin.ooo/docs/ |

!!! note "可信度提示"
    本文性能数据(96% 数据分析准确率、成本约为 Claude Code 的 1/70、构建 RAG 应用 $0.02、100× 提速)来自**官方基准与产品宣传口径**,尚未独立复现,收录仅供参考。

## 原理:三个核心能力

### 1. "小而精"的工具集 + 开源模型深度适配

PenguinHarness 刻意精简工具集——更少的工具调用、更少的 Token 消耗,并对 DeepSeek 等开源模型做了深度适配。官方基准宣称:数据分析任务准确率 96%、成本仅为 Claude Code 的 1/70,编程能力与 OpenAI Codex 持平。

### 2. 一句话构建 Agent 应用

输入一句话,Agent 自动完成:搭建脚手架 → 编写代码 → 生成运行说明。官方案例:用 DeepSeek V4 Pro 构建一个完整 RAG 文档问答应用,仅消耗约 **$0.02**(0.2 元)的 Token。

### 3. 自进化循环(核心卖点)

Agent 可以**自己跑 Benchmark → 自己找失分点 → 自己发布 N+1 版本**:

- 每轮迭代前自动**快照**,随时可回滚;
- 每个请求都能在 **Trace(轨迹观测)中回放**;
- 整个过程透明、可追溯——"你的 Agent 会越用越强"。

!!! tip "与本站知识的呼应"
    自进化机制正是 [Agent 评测](../03-agents/agent-evaluation.md) 中"观测 + 评测 = 持续迭代"数据飞轮的自动化版:评测结果直接驱动版本迭代,而 Trace 回放对应评测基建的"全链路回放"能力。

## 架构与生态:内置 Skill 库,Agent 也能写 Skill

内置 Skill 库分四类,且 **Agent 可以编写并优化自己的 Skill——Skill 库本身也在进化**:

| 分类 | Skill |
| --- | --- |
| 📊 办公效率 | `data-analysis`、`firecrawl` |
| 💻 软件开发 | `web-design`、`software-engineering` |
| 🤖 AI 应用开发 | `penguin-sdk`、`vllm`、`ollama`、`llamafactory` |
| 🔄 Agent 调优 | `agent-creation`、`benchmark-design`、`agent-evaluation` |

官方与 LangChain 的范式对比(宣传口径):

| 维度 | LangChain | PenguinHarness |
| --- | --- | --- |
| 构建方式 | 人工编写代码 | 一句话让 Agent 构建 |
| 开发速度 | 1× | 100× |
| Token 消耗 | 高(大量工具调用) | 极低(精简工具集) |
| 模型适配 | 通用 | 对 DeepSeek 深度优化 |
| 进化能力 | 人工迭代 | 自动自进化 |
| 学习曲线 | 陡峭 | 平缓 |

## 代码 / 实现:安装与上手

```bash
# Linux / macOS 在线安装
curl -fsSL https://penguin.ooo/install.sh | sh && penguin web

# Windows PowerShell
irm https://penguin.ooo/install.ps1 | iex && penguin web

# npm 安装(任意平台)
npm install -g @prismshadow/penguin-cli && penguin web
```

系统要求:Linux / macOS / Windows 10+,x64 与 arm64 均支持。

## 实践 / 应用:怎么看待这类"Agent 构建 Agent"工具

- **适用场景**:快速原型与内部工具(文档问答、数据分析、简单应用);对"效率优先、成本敏感"的团队有吸引力。
- **注意点**:
  - 官方数据是宣传口径,**先跑自己的基准再信**;
  - 深度绑定 DeepSeek 等开源模型的优化,换模型可能打折扣;
  - "自进化"依赖其评测机制的质量——评测跑偏,进化就会朝错误方向迭代(见 [Agent 评测方法论](../03-agents/agent-evaluation.md));
  - 新项目(2026-07 上线),关注社区成熟度与维护节奏。
- **与生态的关系**:它同时是 [编排框架](orchestration-frameworks.md) 与 [Skill 生态](../07-agent-coding/skills/index.md) 的实践者——"Agent 编写并优化自己的 Skill"正是 [mattpocock/skills](../07-agent-coding/skills/mattpocock-skills.md) 思路的自动化延伸。

## 总结

- PenguinHarness = **Agent 自主构建 Agent 的开源平台**:一句话生成应用 + 自进化迭代 + 精简工具集 + 开源模型深度适配。
- 作者即 LlamaFactory 作者,延续"把专业能力交到普通开发者手里"的工具化路线。
- 官方宣称成本/速度优势显著,但数据需自行验证;自进化机制与评测方法论强相关。

## 延伸阅读

- 站内:[Harness 章节首页](index.md)、[通用编排框架](orchestration-frameworks.md)、[Agent 评测](../03-agents/agent-evaluation.md)、[Skill 收藏](../07-agent-coding/skills/index.md)
- 外部:GitHub 仓库 https://github.com/Prism-Shadow/penguin-harness;官网 https://penguin.ooo/;原始资料存档于 `docs/inbox/penguin-harness-source.md`
