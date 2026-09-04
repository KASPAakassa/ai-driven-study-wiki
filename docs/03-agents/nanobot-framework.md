# nanobot:超轻量自托管个人 AI Agent(HKUDS/nanobot)

> **一句话摘要**:nanobot(HKUDS,46.8k stars)是 Python 写的**超轻量、开源、自托管个人 AI Agent 框架**——把工具调用、长期记忆、MCP、模型路由、多智能体、定时自动化、OpenAI 兼容 API 装进一个"小而可读"的核心,可跑在浏览器 WebUI、终端或聊天 App 里,是名副其实的"轻量级全能选手"。
>
> **来源**:GitHub https://github.com/HKUDS/nanobot;官网 https://nanobot.wiki;微信公众号《2026年AI Agent构建指南:框架选型与工程实践》(刘律辰)将其列为"轻量级全能选手,工具调用与代码解释器"

## 概念

**定位**:超轻量、开源、自托管的个人 AI Agent 框架。设计目标是"小而可读"——核心保持简洁,能力通过模块组合。

!!! note "注意同名项目"
    GitHub 上 star 数最高的 nanobot 即 HKUDS/nanobot(官网 nanobot.wiki)。另有 obot-platform/nanobot(Go,MCP host,`brew install obot-platform/tap/nanobot`,用 nanobot.yaml 定义 agent + MCP server)与已重定向到 obot.ai 的 nanobot.ai 域名——同名易混,按需取用。

**选 nanobot 的场景**:快速 Demo / POC——配置最简单、内置 WebUI 无需前端开发、开箱即用的工具。

## 原理:核心特性

- **工具调用**:内置 files(文件)、shell(命令执行)、web search、web fetch、MCP 外部工具、cron(定时任务)、image generation、subagents(子代理委托);
- **代码执行**:通过 `exec`(shell)工具实现本地代码执行,默认 60s 超时;Linux 上可启用 `tools.exec.sandbox: "bwrap"`(bubblewrap)沙箱限制进程只能看到工作区;另有 `tools.restrictToWorkspace` 工作区隔离和 SSRF 防护。⚠️ **没有 ChatGPT 式云端代码解释器**——是"本机 shell 执行 + 可选沙箱";
- **模型支持**:OpenAI 兼容 API(OpenAI、OpenRouter、Groq 等)、Anthropic、Azure OpenAI、AWS Bedrock、OpenAI Codex、GitHub Copilot、本地 Ollama/vLLM,以及 MiniMax、Kimi、VolcEngine/BytePlus、Grok 等;支持模型路由、fallback 链、per-session 模型切换;
- **记忆**:会话历史 + "Dream"长期记忆;
- **多智能体**:spawn 子代理、跨会话委托;
- **自动化**:cron、HEARTBEAT.md 心跳任务;
- **多聊天平台**:Telegram/Discord/Slack/微信/飞书/邮件/Mattermost。

## 代码 / 实现:安装与最小示例

```bash
pip install nanobot-ai
nanobot webui      # 打开 http://127.0.0.1:8765,Settings→Models 配置模型后即可对话

# 或纯 CLI 一次请求:
nanobot agent -m "Hello!"
```

依赖:Python ≥3.11。一键脚本(`curl ...install.sh | sh`)、`uv tool install nanobot-ai`、`pip install nanobot-ai` 或源码安装;MIT 协议;支持 Docker/Render 一键部署。

## 实践 / 应用:适合场景与局限

**适合**:个人/小团队自托管——跨聊天平台的常驻 AI 助手、本地模型接入、定时自动化、多模型 fallback、快速 Demo/POC(内置 WebUI + code_interpreter)。

**局限**:

1. 定位是**个人助手而非企业级编排平台**;
2. shell 工具默认本机可执行,放开访问有安全隐患(沙箱仅 Linux);
3. 处于快速迭代期(open issues 约 800 个);
4. 代码执行是"本机 shell + 可选沙箱",不是云端隔离解释器。

## 总结

- **定位**:超轻量自托管个人 Agent,46.8k stars,"小而可读"核心;
- **能力**:工具调用(含 shell 代码执行)、MCP、模型路由/fallback、长期记忆、子代理、cron 自动化、多聊天平台;
- **上手最快**:`pip install nanobot-ai && nanobot webui` 即得 WebUI;
- **注意**:shell 安全边界(沙箱仅 Linux)、非企业级、同名项目易混;
- **下一步**:对比 [Qwen-Agent](qwen-agent-framework.md)(内置 WebUI + 通义生态)与 [DeepAgents](deepagents-framework.md)(内置沙箱的生产级 harness)。

## 延伸阅读

- 官方:https://github.com/HKUDS/nanobot · https://nanobot.wiki
- 站内:[Qwen-Agent](qwen-agent-framework.md)、[DeepAgents](deepagents-framework.md)、[LangChain 1.x](langchain-framework.md)、[Agent 框架](agent-frameworks.md)
