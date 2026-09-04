# 原始资料:写个 Markdown 就叫开发 Agent?三种 Agent 开发方式,你在哪一层?

> 来源:微信公众号(Agent 架构设计系列),原文链接:https://mp.weixin.qq.com/s/JYSHpmIBhTbOwrFuJZkoig
> 抓取日期:2026-08-09;状态:已拆解入库(见归档记录)

---

同样是"开发 Agent"，有人写 3 行配置，有人写 300 行 Python，有人写了 3000 行状态机。 他们做的事情天差地别，却都被装进了同一个词里。 这篇文章帮你分清：你到底在哪一层，以及该不该往上走。

一、为什么是三层？
先讲个真实场景。
某天技术群里，三个人同时说"我用 AI 搭了个 Agent"：
A 说：我在项目根目录写了个 CLAUDE.md，告诉 Claude Code "提交前跑测试"，搞定。

B 说：我给 Claude Code 接了个 MCP Server，让 AI 能查我们内部的 Jira 和钉钉，搞定。

C 说：我用 LangGraph 写了 500 行状态机，搭了一套多 Agent 协调系统，支持检查点和 human-in-the-loop，搞定。

LangChain 官方博客 Agent Frameworks, Runtimes, and Harnesses—oh my! 给出了一个清晰的分层：
https://www.langchain.com/blog/agent-frameworks-runtimes-and-harnesses-oh-my#agent-frameworks-langchain
层级
术语
你写多少代码
核心价值
Harness
开箱即用的 Agent 运行环境
零或极少
默认行为已经足够好
Runtime
Agent 执行的基础设施
中等
持久化、检查点、状态管理
Framework
构建 Agent 的抽象组件
多
LLM 封装、工具、提示词模板
但这个分法是纵向的（抽象层级），实际开发中团队更关心的是横向的：我投入多少研发，能拿到什么结果？

二、Tier 1：配置即用——写 Markdown 就能跑
这是什么？
拿一个别人造好的 Harness（比如 Claude Code），不写任何代码，只通过配置文件来定义 Agent 的行为。
怎么做？
以 Claude Code 为例：
项目根目录/
├── CLAUDE.md          # 项目指令：告诉 Agent 你的项目规则
├── .claude/
│   ├── commands/       # 自定义斜杠命令
│   │   ├── review.md   # /review 代码审查
│   │   └── deploy.md   # /deploy 部署检查
│   ├── skills/         # 技能：按需加载的能力包
│   │   └── test-gen/   # 自动生成测试
│   ├── subagents/      # 子 Agent 定义
│   │   └── db-agent.md # 专门处理数据库的子 Agent
│   ├── hooks/          # 生命周期钩子
│   │   └── pre-commit.sh
│   └── tools/          # 自定义工具声明CLAUDE.md 长这样：
# Project Instructions

- 使用 TypeScript 严格模式
- 提交前必须运行 `npm run check`
- 不要直接修改 production 分支
- 测试覆盖率不低于 80%一个自定义命令 review.md：
审查当前 git diff 中的代码变更，关注：
1. 类型安全问题
2. 潜在的空指针异常
3. 是否有未处理的边界情况
输出格式：按严重程度排序的问题列表适合谁？
个人开发者，想让 AI 更懂自己的项目

小团队，快速建立 AI 编码规范

不想写代码，只想"配置一下就能用"

代表工具
工具
定位
配置方式
Claude Code
AI 编码助手
CLAUDE.md + .claude/ 目录
Codex (OpenAI)
AI 编码助手
AGENTS.md + 配置文件
OpenClaw
个人 AI 助手
AGENTS.md / SOUL.md / MEMORY.md
三、Tier 2：扩展定制——在别人地基上盖楼
这是什么？
Harness 已经够用了，但你想加一些它没有的能力——比如接一个内部系统、加一个自定义工具、或者搭一个简单的 Web 界面。你不需要从零造，只需要在现有 Harness 上写扩展。
怎么做？
场景 A：Agent CLI + Web 轻定制
以 pi-agent 为例——它本身是个终端工具，但你可以在上面加：
# 安装 pi
npm install -g --ignore-scripts @earendil-works/pi-coding-agent

# 写一个 TypeScript 扩展，给 pi 加新工具// extensions/my-tool/index.ts
exportdefaultfunction (pi) {
  pi.tool("query-internal-db", async (params) => {
// 调用公司内部数据库
const result = await internalDB.query(params.sql);
returnJSON.stringify(result);
  });

  pi.command("/deploy-check", async (ctx) => {
// 自定义部署检查流程
const checks = awaitrunDeployChecks();
return checks.report;
  });
}场景 B：通过 MCP Server 扩展能力
MCP（Model Context Protocol）是连接外部能力的标准协议。你可以：
# 写一个 MCP Server，把内部系统暴露给任何 Agent
from mcp.server import Server

server = Server("internal-tools")

@server.tool("query-jira")
asyncdefquery_jira(ticket: str):
"""查询 Jira 工单状态"""
returnawait jira_api.get(ticket)

@server.tool("send-dingtalk")
asyncdefsend_dingtalk(message: str, chat_id: str):
"""发送钉钉消息"""
returnawait dingtalk_api.send(message, chat_id)然后在任何支持 MCP 的 Harness 里接入：
// .claude/mcp.json
{
"servers":{
"internal-tools":{
"command":"python",
"args":["mcp_server.py"]
}
}
}场景 C：DeerFlow 配置级定制
DeerFlow 2.0 也支持 Tier 2 用法——不改源码，只改配置：
# config.yaml
model:
provider:deepseek
name:deepseek-chat

tools:
-group:built-in# 内置工具
-group:community# 社区工具
-mcp:
server:internal-db# MCP 工具
command:python
args: ["db_mcp.py"]

skills:
-name:code-review# 加载代码审查技能
-name:test-gen# 加载测试生成技能适合谁？
中小团队，需要接内部系统但不想造轮子

有一些开发能力，但不想维护整套框架

想保留 Harness 升级路径的团队

代表工具/方式
方式
代码量
典型场景
pi-cli + extensions
少量 TS
个人/小团队编码增强
Claude Code + MCP Servers
少量 Python/TS
接入内部系统
DeerFlow 配置定制
零代码改配置
换模型、加工具、加技能
四、Tier 3：深度构建——从零件造整车
这是什么？
你需要的不是一个"配置好的助手"，而是一个Agent 平台——多 Agent 编排、状态管理、任务调度、生产部署。这时候配置和扩展都不够了，你需要基于 Framework/Runtime 从头搭建。
怎么做？
第一层：用 LangChain 造零件
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 造一个 LLM 封装
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 造一个工具
@tool
defsearch_database(query: str) -> str:
"""搜索内部数据库"""
return db.search(query)

# 造一个提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个数据分析助手"),
    ("human", "{input}"),
])第二层：用 LangGraph 画流程并执行
from langgraph.graph import StateGraph, END
from typing import TypedDict

classAgentState(TypedDict):
    messages: list
    next_action: str
    results: list

defplan_node(state: AgentState) -> AgentState:
"""规划：决定下一步做什么"""
    response = llm.invoke("分析任务，制定计划")
    state["next_action"] = response.content
return state

defexecute_node(state: AgentState) -> AgentState:
"""执行：调用工具完成任务"""
    result = search_database.invoke(state["next_action"])
    state["results"].append(result)
return state

defshould_continue(state: AgentState) -> str:
"""条件路由：继续还是结束"""
iflen(state["results"]) < 3:
return"plan"
return END

# 构建工作流
workflow = StateGraph(AgentState)
workflow.add_node("plan", plan_node)
workflow.add_node("execute", execute_node)
workflow.set_entry_point("plan")
workflow.add_edge("plan", "execute")
workflow.add_conditional_edges("execute", should_continue)

# 编译并运行
app = workflow.compile()
result = app.invoke({"messages": [], "results": []})第三层：用 DeerFlow 搭 Harness
# DeerFlow 的 Lead Agent 就是基于 LangGraph 构建的
# 你可以自定义中间件、技能、子 Agent

# 自定义中间件：在每次 LLM 调用前注入记忆
classMemoryInjectionMiddleware:
asyncdefbefore_llm_call(self, state):
        memories = await memory_store.search(state["messages"][-1])
        state["messages"].insert(0, {
"role": "system",
"content": f"相关记忆: {memories}"
        })
return state

# 自定义技能：按需加载的领域能力
classCodeReviewSkill:
    name = "code-review"
    instructions = "你是一个资深代码审查专家..."
    tools = [read_file, run_tests, check_coverage]

# 自定义子 Agent：并行处理子任务
classResearchSubAgent:
    name = "researcher"
    system_prompt = "你负责信息检索和整理"
    tools = [web_search, read_url]适合谁？
需要搭建企业级 Agent 平台的团队

需要多 Agent 编排、状态管理、生产部署

有充足研发投入（至少几个人月）

代表工具
工具
层级
语言
典型用途
LangChain
Framework
Python/JS
组件库
LangGraph
Runtime
Python/JS
状态机 + 执行引擎
DeerFlow 2.0
Harness
Python
完整 Agent 运行时
CrewAI
Framework
Python
多 Agent 协作
AutoGen
Framework
Python
多 Agent 对话
三种 Agent 开发方式，决定你处于哪个 Tier 的，不是你选了什么工具，而是你投入了多少研发。