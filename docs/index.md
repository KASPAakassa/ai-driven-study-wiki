# AI 驱动的学习 Wiki

欢迎来到我的 AI 学习知识库。这里按照 **概念 → 原理 → 代码 → 实践** 的方式组织内容,把零散的资料沉淀成可以随时查阅的知识。

> 🗺 **新来的?先看 [知识库索引(渐进式加载入口)](knowledge-index.md)** —— 带章节地图、主题交叉索引与加载协议,快速定位任意主题;或直接看下方学习地图。

## 学习地图

| 章节 | 内容 | 适合谁 |
| --- | --- | --- |
| [🤖 AI · ML · DL 基础](01-ai-basics/index.md) | AI/ML/DL 概念、经典 ML 算法、神经网络与深度学习 | 入门到进阶的地基 |
| [💬 大语言模型](02-llm/index.md) | Transformer、预训练、微调、RLHF、RAG、推理 | 理解 LLM 全链路 |
| [🛠 Agent](03-agents/index.md) | Agent 概念、框架、工具调用、多 Agent、开发实践 | Agent 使用与开发 |
| [🚀 实战](04-practice/index.md) | 从理论到落地:项目、复现、踩坑记录 | 动手实践 |
| [📚 参考](05-reference/index.md) | 论文、书、课程、博客、工具清单 | 随时查阅 |
| [🏢 企业落地与 FDE](06-enterprise/index.md) | Ontology 与 Agent 企业落地、FDE 理论与方法论 | 落地视角 |
| [🛠️ Agent Coding 经验](07-agent-coding/index.md) | 个人使用经验、技巧、现成 Skill 收藏 | 个人实践 |
| [🧰 Harness 框架与开源方案](08-harness/index.md) | 编码 Agent 工具、编排框架、配套方案(协议/沙箱/评测) | 开源索引 |
| [🏫 Agent 前沿学术](09-agent-research/index.md) | 论文解析、研究方法论、开源数据集与基准 | 学术前沿 |
| [📱 鸿蒙开发](10-harmonyos/index.md) | 鸿蒙平台全景、ArkTS/ArkUI、质量发布、AI 辅助开发 | 平台专题 |

## 快速开始

- 想**学东西**:从 [AI 基础](01-ai-basics/index.md) 开始,沿着学习地图往下走。
- 想**丢资料**:扔进 [📥 收件箱](inbox/README.md),告诉 AI 助手整理。
- 想**本地浏览**:`python3 -m venv .venv && .venv/bin/pip install mkdocs-material`,然后 `.venv/bin/mkdocs serve` 打开 http://127.0.0.1:8000(详见仓库根 `README.md`)。

!!! tip "关于收件箱"
    任何找到的文章、课程、代码、笔记,先丢进 `docs/inbox/`,由 AI 助手梳理成标准格式后再归位到对应章节。
