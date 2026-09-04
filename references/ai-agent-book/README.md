# 引用资料存档:《深入理解 AI Agent:设计原理与工程实践》

> 本目录是**外部书籍源码的本地引用存档**,不进入 MkDocs 站点,仅供知识库拆解与核对使用。

## 来源

- **书名**:《深入理解 AI Agent:设计原理与工程实践》(李博杰 著)
- **仓库**:https://github.com/bojieli/ai-agent-book(Apache-2.0,34.7K+ stars,13 种语言)
- **在线阅读**:https://bojieli.github.io/ai-agent-book/
- **存档日期**:2026-08-09(抓取 main 分支快照)

## 全书核心

> **Agent = LLM(大脑)+ 上下文(眼睛)+ 工具(手脚)**

10 章正文 + 95 个配套实验,从原理讲到工程实战。

## 目录(book/ 目录下为全书中文正文)

| 文件 | 章 | 主题 | 一句话核心 |
| --- | --- | --- | --- |
| `book/introduction.md` | 引言 | 为什么 Agent 是 AI 的未来 | 从 ChatBot 到 Agent 的范式转变 |
| `book/chapter1.md` | 1 | Agent 基础知识 | Agent = LLM + 上下文 + 工具;Harness 工程才是竞争力 |
| `book/chapter2.md` | 2 | 上下文工程 | KV Cache、提示工程、Agent Skills、上下文压缩 |
| `book/chapter3.md` | 3 | 用户记忆和知识库 | 用户记忆、RAG、结构化索引、知识图谱 |
| `book/chapter4.md` | 4 | 工具 | MCP 协议、感知/执行/协作工具、事件驱动异步 Agent |
| `book/chapter5.md` | 5 | Coding Agent 与代码生成 | 代码是"能创造新工具的工具" |
| `book/chapter6.md` | 6 | Agent 的评估 | 评估环境、指标、统计显著性、评估驱动选型 |
| `book/chapter7.md` | 7 | 模型后训练 | 预训练/SFT/RL、工具调用内化、样本效率 |
| `book/chapter8.md` | 8 | Agent 的持续进化 | 从运行轨迹获得学习信号,更新知识/指令/程序/参数 |
| `book/chapter9.md` | 9 | 多模态与实时交互 | 语音三范式、Computer Use、机器人 |
| `book/chapter10.md` | 10 | 多 Agent 协作 | 群体智能、上下文共享/隔离、Agent 社会 |
| `book/afterword.md` | 后记 | 全书总结与展望 | — |
| `book/reference-answers.md` | 附录 | 思考题参考答案 | — |

## 知识库拆解进度

- [x] 全书导读与知识索引 → docs/03-agents/ai-agent-book-guide.md
- [x] 第 7 章 模型后训练 → docs/02-llm/agent-post-training.md
- [x] 第 8 章 持续进化 → docs/03-agents/agent-continuous-evolution.md
- [x] 第 9 章 多模态与实时交互 → docs/03-agents/agent-multimodal-realtime.md
- [ ] 第 1-6、10 章:已有对应文章覆盖,需时按章补充细化(见导读文章知识索引)

## 说明

- 存档仅含正文 markdown(约 1.1MB);代码实验在仓库 `chapter1/`~`chapter10/` 目录,未随存档(需要时按需拉取)。
- 版权归作者所有,存档仅供个人学习研究。
