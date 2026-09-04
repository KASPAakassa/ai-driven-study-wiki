# Crush:Charm 出品的终端编程搭档(编码 Agent)

> **一句话摘要**:Crush(Charmbracelet 出品,Go 编写)是"终端里的编程新搭档"——把你的工具、代码、工作流接入任意 LLM。特色:**多模型**(Anthropic/OpenAI/Gemini/Bedrock/Copilot/MiniMax 等或自加 OpenAI/Anthropic 兼容 API)、**会话中切换模型且保留上下文**、**每项目多会话**(SQLite 持久化)、**LSP 增强**(像人一样用 LSP 补全/诊断)、**MCP 扩展**(http/stdio/sse)、**hooks 引擎**(Claude Code 兼容事件),以及 **bash 风格配置 `crushrc`**(`model`/`option`/`mcp add` 内置命令)。跨平台:macOS/Linux/Windows(PowerShell/WSL)/Android/FreeBSD/OpenBSD/NetBSD。
>
> **来源**:Crush 官方仓库(https://github.com/charmbracelet/crush)与 AGENTS.md;原始文件存档于 `references/crush/`

## 概念:终端编码 Agent 的又一位成员

| 工具 | 出品 | 特色 |
| --- | --- | --- |
| Claude Code | Anthropic | 官方、闭源为主、生态全 |
| OpenCode | Anthropic 团队 | 开源、双 Agent(build/plan) |
| Reasonix | esengine | 开源、可长跑自治、配置驱动 |
| **Crush** | **Charmbracelet** | **开源、多模型会话中切换、LSP 增强、Charm 生态(25k+ 应用)** |

!!! tip "一句话定位**
    Your tools, your code, and your workflows, wired into your LLM of choice——把工具/代码/工作流接进你选的模型;Charm 出品意味着**工业级质量**与跨平台(不止桌面,还有 Android/BSD)。

## 原理:核心能力与架构

### 1. 七项核心能力

| 能力 | 说明 |
| --- | --- |
| **Multi-Model** | 多种 LLM 或自加(OpenAI-/Anthropic-兼容 API);provider:Anthropic/OpenAI/Gemini/Bedrock/Copilot/Hyper/MiniMax/Vercel 等 |
| **Flexible** | **会话中切换 LLM 且保留上下文**(不用重开会话) |
| **Session-Based** | 每项目多会话、多上下文(SQLite 持久化) |
| **LSP-Enhanced** | 用 LSP 补全/诊断作为额外上下文(像人读代码一样) |
| **Extensible** | MCP 扩展(`http`/`stdio`/`sse`) |
| **Works Everywhere** | macOS/Linux/Windows(PowerShell/WSL)/Android/FreeBSD/OpenBSD/NetBSD |
| **Industrial Grade** | 构建于 Charm 生态(支撑 25k+ 应用) |

### 2. 架构(来自 AGENTS.md)

```
internal/
  app/       顶层装配:DB、config、agents、LSP、MCP、events
  cmd/       CLI(root/run/login/models/stats/sessions)
  config/    crushrc(bash 风格)+ crush.json 加载与校验、provider 配置
  shellconfig/  Bash 风格配置内置命令(model/option/mcp add)
  agent/     SessionAgent(每会话 LLM 对话)+ Coordinator(命名 agents:"coder"/"task")
             + hooked_tool(PreToolUse hooks)+ prompts(Go 模板系统提示词)
             + tools/(bash/edit/view/grep/glob + mcp 客户端)
  hooks/     Hook 引擎:用户 shell 命令响应事件(Claude Code 兼容输入)
  session/   Session CRUD(SQLite)
```

!!! note "关键设计**
    - **命名 agents**:Coordinator 管理 `coder` / `task` 等角色(每个有自己的系统提示词模板),`runAs=agent` 可切换;
    - **hooks 引擎**:PreToolUse 等在工具执行前运行用户 shell 命令,支持决策类型/聚合/超时/去重——与站内 [Hook 治理](../03-agents/agent-governance-hooks.md) 同构;
    - **crushrc 实时配置(规划中)**:未来 agent 的 bash 工具可运行配置命令(`model large …`)**实时切换当前会话模型**,持久化仍需编辑 crushrc。

### 3. 安装(多平台)

```bash
brew install charmbracelet/tap/crush    # macOS/Linux
npm install -g @charmland/crush          # 任意系统
yay -S crush-bin / nix run github:numtide/nix-ai-tools#crush   # Arch/Nix
winget install charmbracelet.crush / scoop install crush        # Windows
```

## 代码 / 实现:命名 Agent 协调 + 模型切换模拟(纯 Python)

把"Coordinator 管理命名 agents + 会话中切换模型保留上下文"落成可运行演示:

```python
# —— Crush 的命名 agents 协调(coder / task)——
AGENTS = {
    "coder": {"prompt": "你是编码代理:写代码、改文件、跑测试", "tools": ["bash", "edit", "view", "grep"]},
    "task":  {"prompt": "你是任务代理:长链路多步任务、协调子代理", "tools": ["bash", "grep", "mcp"]},
}

def dispatch(agent_name: str, task: str) -> str:
    agent = AGENTS.get(agent_name)
    if not agent:
        return f"未知 agent:{agent_name}(可选 coder/task)"
    return f"[{agent_name}] {agent['prompt'][:12]}… 处理: {task} (工具: {', '.join(agent['tools'])})"

# —— 会话中切换模型,上下文保留(模型变量换,会话不变)——
class Session:
    def __init__(self, model): self.model = model; self.history = []
    def switch_model(self, m): self.model = m
    def say(self, msg):
        self.history.append(msg)
        return f"{self.model}: 已处理「{msg}」(历史 {len(self.history)} 条)"

s = Session("anthropic")
print(dispatch("coder", "修登录 bug"))
print(s.say("第一轮"))
s.switch_model("gemini")              # 会话中切换,上下文保留
print(s.say("第二轮(换了模型)"))
assert dispatch("coder", "x").startswith("[coder]")
assert s.history == ["第一轮", "第二轮(换了模型)"]
print("代码验证通过 ✔")
```

## 实践 / 应用:使用要点与知识库整合

!!! tip "三个使用要点**
    1. **会话管理**:每项目开多个会话(不同任务不同上下文),`sessions` 命令查看切换;
    2. **模型自由**:随时 `model` 换模型(贵模型做难任务、便宜模型做重复活)——会话中切换不丢上下文;
    3. **能力扩展**:缺工具用 MCP 接(http/stdio/sse),缺约束用 hooks(PreToolUse 拦截)。

### 与站内其他文章的呼应

- [Harness 收录清单](index.md):Crush 加入"编码 Agent 工具"家族(与 Claude Code/OpenCode/Reasonix 并列,见 [编码 Agent 工具索引](coding-agents.md));
- [Hook 治理](../03-agents/agent-governance-hooks.md):Crush 的 hooks 引擎(Claude Code 兼容事件)是 [DECO Hook 链](../03-agents/agent-governance-hooks.md) 的又一个实现;
- [Context Engineering](../03-agents/context-engineering.md):LSP 增强 = 用代码智能做上下文(高德"最小有用片段"的 LSP 版);
- [Agent 系统设计的 5 个决策](../03-agents/agent-system-5-decisions.md):会话中切换模型 = "模型路由"的交互式形态。

## 总结

- **定位**:Charm 出品的终端编码 Agent——工具/代码/工作流接入任意 LLM,工业级跨平台;
- **七能力**:多模型、会话中切换、多会话、LSP 增强、MCP 扩展、全平台、Charm 生态;
- **架构要点**:命名 agents(coder/task)+ hooks 引擎 + crushrc bash 风格配置 + SQLite 会话;
- **一句话**:想要"终端里能随时换模型、像人一样用 LSP、还能挂 hooks 和 MCP"的编码 Agent,Crush 是值得试的开源选择。

## 延伸阅读

- 仓库:https://github.com/charmbracelet/crush;Charm 生态:https://charm.sh;文档:https://github.com/charmbracelet/crush/tree/main/docs
- 站内:[编码 Agent 工具索引](coding-agents.md)、[OpenCode 使用教程](opencode-tutorial.md)、[Reasonix 使用教程](reasonix-tutorial.md)、[Hook 治理](../03-agents/agent-governance-hooks.md)、[Context Engineering](../03-agents/context-engineering.md)
