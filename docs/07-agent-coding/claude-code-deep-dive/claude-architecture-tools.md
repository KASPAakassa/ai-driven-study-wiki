# Claude Code 架构与工具系统:从组件全景到可验证的 agent loop

> **一句话摘要**:Anthropic CEO 透露 **90% 的 Claude Code 代码由它自己编写**——凭什么?Claude Code 不是"模型加一堆工具",而是一套模块化架构(MCP 提供工具、Skills 教用法、Subagents 并行、Hooks 确保可控)与一条**可验证的 agent loop**(工具发现 → 权限约束 → hooks 埋点 → sandbox 限制 → checkpoint 回退 → 结果回流)。真正值得学的不是"会调用工具",而是把工具调用变成**可以持续行动、可以被约束、可以被验证的工作流**。
>
> **来源**:Yu 的赛博工位(https://yudesk.dev/docs/notes)笔记《Claude 系统架构全解析》与《Claude Code 真正厉害的,不是会调用工具》,原页面:https://yudesk.dev/docs/notes/claude-architecture、https://yudesk.dev/docs/notes/claude-code-tool-calling-system;原始内容存档于 `docs/inbox/yudesk-claude-code/`

## 概念:为什么 Claude Code 能"自己写自己"

2025 年 9 月,Anthropic 以 $183B 估值完成 $13B 融资;Claude Code 已吸引 11.5 万活跃开发者,每周处理 1.95 亿行代码,用户增长 300%。**90% 的 Claude Code 代码由它自己编写**。

!!! tip "核心设计原则(官方)**
    Claude needs the same tools that programmers use every day. By giving Claude access to the user's computer (via the terminal), it had what it needed to write code like programmers do.
    答案藏在模块化架构中:**MCP 提供工具、Skills 教会用法、Subagents 并行执行、Hooks 确保可控**——这些组件协同工作,让 Claude 具备"像程序员一样工作"的能力。

## 原理:模块化架构与工具调用系统

### 1. 组件全景(同级互补,非层级依赖)

| 你想要... | 使用... | 一句话定位 |
| --- | --- | --- |
| 连接外部数据源和服务 | **MCP** | 给 Claude 装上"手脚",访问数据库/API/文件系统(WHAT) |
| 教 Claude 特定工作流 | **Skills** | 让 Claude"知道"某个领域怎么做事(HOW) |
| 并行处理复杂任务 | **Subagents** | 大任务拆小任务,多个 Agent 同时干活 |
| 快速触发重复操作 | **Commands** | 一键启动常用工作流 |
| 确保某些操作必须执行 | **Hooks** | 无论 Claude 怎么决策,这步必须跑(确定性) |
| 打包分发整套配置 | **Plugins** | Skills+Commands+Subagents+Hooks+MCP 打包为可安装单元 |

### 2. 核心运行时:Agent SDK

- **主循环**:收集上下文 → 执行操作 → 验证工作 → 重复(agent harness 的基本循环);
- **上下文管理**:Token 预算、自动压缩(**92% 使用率时触发**);
- **工具调度**:决定使用哪个工具、如何执行;
- **权限系统**:控制工具访问权限;
- **Built-in Tools 20+**:读取(Read/Glob/Grep)、操作(Write/Edit/Bash)、网络(WebSearch/WebFetch)——默认可用,无需配置。

### 3. 配置与上下文:CLAUDE.md(持久化上下文)

每次新对话都要重复说明项目背景?CLAUDE.md 一次配置、自动加载——它是 **README for AI**。层级覆盖(越具体优先级越高):Enterprise → User(`~/.claude/CLAUDE.md`)→ Project(`./CLAUDE.md`)→ Module(`./src/module/CLAUDE.md`)。内容建议:技术栈/构建命令/代码规范/项目结构;**关键原则:保持简洁——每次对话都加载,过长浪费 token**。

### 4. 扩展能力详解

**MCP(外部连接)**:设计为 AI 应用的 **USB-C 接口**——一次接入、处处可用,解决 N×M 集成地狱;开放标准(2024.11 发布,2025.12 捐赠 Linux 基金会),OpenAI/Microsoft/Google/AWS 已采用,97M+ 月 SDK 下载;架构模式 MCP Host → 1:N Clients → Servers。配置:项目根 `.mcp.json`。

**Hooks(确定性控制)**:某些操作必须执行,不能依赖 LLM 判断。事件表:PreToolUse/PostToolUse/PostToolUseFailure/PermissionRequest/SessionStart/SessionEnd/Stop/SubagentStart/SubagentStop/UserPromptSubmit/Notification/PreCompact。

**Subagents(任务委派与并行)**:Orchestrator-Worker 模式(Main Agent 分析/计划/分解/生成专门化子代理 → Workers 并行 → 汇总);核心特性:上下文隔离/任务专门化/工具权限控制/并行执行;**性能数据:多代理比单代理高 90.2%,并行化可削减研究时间 90%(token 约 15×,复杂任务值得)**;配置:`~/.claude/agents/*.md`。

**Skills(程序性知识)**:可重用工作手册,按需动态加载;**渐进式披露三层**——目录(元数据层,30-50 tokens 启动预加载)/ 正文章节(核心文档层,相关时加载)/ 附录(引用资源层,需要时加载)。Token 高效(数十个 Skills 同时启用)/ 自动激活/ 可组合/ 可移植。配置:`~/.claude/skills/<name>/SKILL.md`。

### 5. 工具调用系统:不是 tool calling,是 agent runtime

!!! warning "工具调用的误解"
    模型判断意图 → 选函数 → 填参数 → 返回结果 → 继续回答——这套模型适合天气查询,但**不足以解释 Claude Code**。开发任务不是一次函数调用能完成的,而是一条循环:**观察当前状态 → 选择下一步行动 → 执行工具 → 接收结果 → 更新判断 → 再选择**。普通聊天模型生成文本,Claude Code 会在这个循环里**持续改变工作环境**。

**一次失败测试背后的真实链路**(登录测试失败):

```
Bash 跑测试 → 得到失败现场 → Read 读测试和实现 → Grep 找调用点
  → Read 读相关代码 → Edit 修改 → Bash 再跑测试 → 根据结果继续调整或收束
```

Bash 返回的不是"答案",而是**下一轮推理的依据**;Read 在补齐当前任务的事实;Grep 在缩小问题空间;Edit 后面必须有验证。

**工具不是越多越好**(尤其接入 MCP 后):①工具定义吃大量上下文(token 被工具清单塞满);②工具太多降低选择质量(名字相近易选错)——这就是 **ToolSearch** 出现的位置:**Grep 搜代码,WebSearch 搜网页,ToolSearch 搜能力**。MCP 解决工具从哪里来,ToolSearch 解决工具太多后怎么找到——按需发现工具,再把少量相关定义带进上下文。

!!! note "对自研 agent 的启发"
    工具设计不是后端 API 封装,而是**给模型设计行动空间**。一个叫 `query` 的万能工具很难被稳定使用;一个叫 `search_sentry_events` 的工具在"查一下最近登录失败的线上报错"时清楚得多。

**能执行之前,先要被约束(四层边界)**:

| 层 | 回答的问题 | 例子 |
| --- | --- | --- |
| **权限** | 能不能执行 | Read 自动放行、rm -rf/生产库写/外部发送需确认或拒绝 |
| **hooks** | 执行前后必须发生什么 | 读 .env 前拦截、改文件后自动格式化、任务结束前跑测试 |
| **sandbox** | 命令能访问哪些文件/网络/系统资源 | 限制执行范围 |
| **checkpoint** | 文件改坏了能不能回退 | **能回滚本地文件,但不能回滚外部副作用**(写了生产库/调了远程 API 无法复原) |

**工具结果不是日志垃圾桶**:Agent 的上下文不是垃圾桶,工具结果应服务下一步决策。好的 agent 工具特征:名字明确/参数少而清楚/返回有摘要+证据+下一步提示/大结果过滤分页聚合/说明副作用和权限边界。人类 API 给工程师调用,agent 工具帮模型判断下一步——**两者不是一回事**。

**真正值得学的是收束能力**:一个会收束的 agent 会不断问——当前最缺的事实是什么?哪个工具能以最低成本拿到?这一步有没有副作用?结果是否足够支持下一步?什么时候停止、停止前验证什么?

## 代码 / 实现:按需工具发现(ToolSearch 式,纯 Python)

把"工具不是越多越好 + 按需发现"落成可运行演示:

```python
# —— ToolSearch:按需求发现工具,而不是全量加载 ——
TOOL_REGISTRY = [
    {"name": "search_sentry_events", "keywords": ["报错", "错误", "事件", "sentry"]},
    {"name": "read_file",            "keywords": ["读", "文件", "源码"]},
    {"name": "run_test",             "keywords": ["测试", "跑", "test"]},
    {"name": "query_database",       "keywords": ["数据", "表", "sql", "查询"]},
    {"name": "send_message",         "keywords": ["发消息", "通知", "slack"]},
]

def discover_tools(requirement: str, top_k=2) -> list:
    """按需发现:只把少量相关工具定义带进上下文,避免全量塞满"""
    scored = []
    for tool in TOOL_REGISTRY:
        hit = sum(1 for k in tool["keywords"] if k in requirement)
        if hit:
            scored.append((tool["name"], hit))
    scored.sort(key=lambda x: -x[1])
    return [name for name, _ in scored[:top_k]]

for req in ["查一下最近登录失败的线上报错", "跑一下登录测试", "读一下 auth.py"]:
    print(f"  {req!r:22} → 发现工具: {discover_tools(req)}")
```

## 实践 / 应用:组件协同与知识库整合

### 快速上手的配置清单

1. **CLAUDE.md**(项目根):技术栈 + 构建命令 + 代码规范——一次配置自动加载;
2. **MCP**(`.mcp.json`):接 GitHub/数据库/内部 API;
3. **Skills**(`.claude/skills/`):把领域工作流做成 SKILL.md(渐进式披露);
4. **Subagents**(`.claude/agents/`):拆并行任务;
5. **Hooks**(`settings.json`):确定性控制(格式化/权限拦截/测试门禁);
6. **Plugins**:把上面整套打包分发(团队标准化)。

### 与站内其他文章的呼应

- [Tool/MCP/Skills/Harness 四件套](../../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md):本笔记的组件全景是四件套的官方实现版本;
- [工具治理(工程化一)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-boundaries-tools.md):ToolSearch 是"候选工具筛选"的官方机制;
- [Hook 治理](../../03-agents/agent-governance-hooks.md):Hooks 事件表与 DECO 的 Hook 链同构;
- [Graph Engineering 14 步](../../07-agent-coding/experience/graph-engineering-14-steps.md):agent loop 的"观察→行动→验证"与节点循环一致;
- [落地方法论](../../06-enterprise/ontology-agent-adoption/agent-landing-micro-agents.md):"工具结果高信号"与"收束能力"是落地成败的关键。

## 总结

- **模块化架构**:MCP(手脚)/ Skills(HOW)/ Subagents(并行)/ Commands(快捷)/ Hooks(确定性)/ Plugins(打包)——同级互补,按需组合;
- **agent runtime 思维**:Claude Code 不是"会调用工具",而是把工具调用组织成**可验证的 agent loop**(发现→约束→执行→验证→收束);
- **四层边界**:权限(能不能)/ hooks(前后必须发生什么)/ sandbox(能碰什么)/ checkpoint(能不能回退)——工具越多越需要边界;
- **两条设计原则**:工具要为推理链路设计(高信号返回,不是 API 封装);真正值得学的是**收束能力**(每个 agent 都该问"当前最缺什么事实、最低成本怎么拿到、该停了吗")。

## 延伸阅读

- 原页面:https://yudesk.dev/docs/notes/claude-architecture、https://yudesk.dev/docs/notes/claude-code-tool-calling-system;站内子主题:[Claude Code 深度解析](index.md)
- 站内:[Claude Code Worktree 与 Agent Teams](claude-worktree-teams.md)、[Skills/Plugin/Subagent](claude-skills-plugin-subagent.md)、[Claude Code 隐藏技巧](claude-code-tips.md)(本子主题后续篇);[四件套](../../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md)、[工具治理](../../06-enterprise/ontology-agent-adoption/enterprise-agent-boundaries-tools.md)、[Hook 治理](../../03-agents/agent-governance-hooks.md)、[Graph Engineering 14 步](../../07-agent-coding/experience/graph-engineering-14-steps.md)
