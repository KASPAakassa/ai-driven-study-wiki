# Deep Agents:LangChain 官方的"开箱即用型"Agent Harness

> **一句话摘要**:Deep Agents 是 LangChain 官方推出的**强预设(opinionated)Agent harness**——不写图、不拼 middleware,几十行代码就能跑起一个能规划、读写文件、调子代理、管理上下文的生产级 Agent。内置可插拔沙箱(LangSmith/E2B/Modal/Daytona 等后端)、多模文件解析(PDF/PPT/图片/音视频直接送视觉模型)、MCP 一等公民。
>
> **来源**:GitHub https://github.com/langchain-ai/deepagents;官方文档 https://docs.langchain.com/oss/python/deepagents/overview;微信公众号《2026年AI Agent构建指南:框架选型与工程实践》(刘律辰),https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg

## 概念

**定位**:LangChain 官方的"开箱即用型 Agent 框架"(batteries-included agent harness)——强预设:不写图、不拼 middleware,几十行代码跑起能规划、读写文件、调子代理、管理上下文的生产级 Agent(27.6k stars / 3.8k forks,2025-07 创建,迭代极快;另有 TS 版 deepagentsjs、终端 CLI「Deep Agents Code」及 LangSmith 托管版「Managed Deep Agents」)。

**与 LangChain/LangGraph 的关系**(三层同栈):

- **LangChain**:提供模型/工具等积木;
- **LangGraph**:运行时(流式、持久化 checkpointing、human-in-the-loop);
- **Deep Agents**:构建在 `langchain.agents.create_agent` 之上的更完整 harness——自带文件系统、子代理、上下文管理、skills。任何 LangGraph `CompiledStateGraph` 可作为子代理嵌入;需要自定义 agent 循环时可下沉到 LangGraph。

## 原理:核心特性

- **配置极简**:`uv add deepagents` 后一个 `create_deep_agent(model=..., tools=[...], system_prompt=...)` 即得可用 agent;模型经 LangChain chat model 字符串指定,兼容 OpenAI/Anthropic/Google/OpenRouter/Ollama 及任意支持 tool calling 的开源/本地模型;
- **内置沙箱(可插拔后端)**:核心安全机制。配 `backend=` 把文件系统与命令执行隔离到沙箱,获得 `ls/read_file/write_file/edit_file/delete/glob/grep/execute` 全套工具。官方提供 LangSmith、E2B、Modal、Daytona、Runloop、Vercel、NVIDIA OpenShell、AWS AgentCore 等内置 backend;文件经 `upload_files/download_files` 跨宿主-沙箱传输;超大命令输出自动落盘供 `read_file` 分页读;
- **多模文件解析**:`read_file` 对非文本文件(png/jpg/gif/heic、mp4/mov、wav/mp3、**pdf/ppt/pptx** 等)返回多模态内容块,直接送视觉模型——不是普通文本提取;
- **工具调用与生态**:自带函数、LangChain tools 或任意 MCP server 均可作为工具,**MCP 一等公民**;
- **其他**:子代理(隔离上下文、单次回传报告)、上下文压缩/offload、持久记忆(AGENTS.md)、`skills`(按需渐进加载)、human-in-the-loop 审批(`interrupt_on`)、prompt caching、LangSmith 可观测/评估。

## 代码 / 实现:最小示例

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[my_custom_tool],
    system_prompt="You are a research assistant.",
)
result = agent.invoke({"messages": "Research LangGraph and write a summary"})
```

## 实践 / 应用:适合场景与局限

### 适合场景

长周期多步任务(研究、编码、数据分析)、需要文件操作 + 代码执行 + 上下文自动管理的生产部署;默认能力即可满足大部分场景,且可逐件覆盖/替换。

### 局限

1. 定位是"预设好"的 harness,**深度自定义编排不如直接用 LangGraph 灵活**;
2. 安全模型为"信任 LLM",边界靠工具/沙箱强制执行;
3. **沙箱不防上下文注入,密钥绝不能放进沙箱**;
4. 大版本行为变化快(v0.7 起任务规划改为 opt-in,delete 工具需 0.7+),文档与代码可能不同步。

### 案例(保险产品智能问答 Agent 中的角色)

在《2026 指南》的多文件智能问答案例中,Deep Agents 作为 Agent 框架层(AGICTO 平台 qwen3.7-plus 模型),与 llama_index(RAG)+ faiss-cpu(向量检索)+ ChromaDB(向量库)组合——Deep Agents 负责 agent 业务、query 改写(qwen3.5-35b-a3b)与方案设计,体现其"配置极简、内置沙箱、多模文件解析"的定位。

## 总结

- **定位**:LangChain 官方强预设 Agent harness——开箱即用,几十行代码出生产级 Agent;
- **三层同栈**:LangChain(积木)+ LangGraph(运行时)+ Deep Agents(完整 harness),可下沉 LangGraph 自定义;
- **核心能力**:可插拔沙箱(LangSmith/E2B/Modal/Daytona…)、多模文件解析(PDF/PPT/图片/音视频)、MCP 一等公民、子代理/上下文管理/skills;
- **注意**:深度自定义不如 LangGraph 灵活、沙箱不防上下文注入(密钥勿入沙箱)、版本变化快;
- **下一步**:对比 [LangChain 1.x](langchain-framework.md)(底层积木)与 [nanobot](nanobot-framework.md)(轻量自托管),或看 [Agent 框架七方对比](agent-frameworks-seven-comparison.md) 中同类 harness。

## 延伸阅读

- 官方:https://github.com/langchain-ai/deepagents · https://docs.langchain.com/oss/python/deepagents/overview
- 站内:[LangChain 1.x](langchain-framework.md)、[LlamaIndex](llamaindex-framework.md)(案例组合)、[nanobot](nanobot-framework.md)、[Agent 框架](agent-frameworks.md)
