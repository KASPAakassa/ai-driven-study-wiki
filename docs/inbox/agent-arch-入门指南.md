# 原始资料:从零开始理解 Agent 开发:LangChain/LangGraph/DeerFlow 小白入门指南

> 来源:微信公众号(Agent 架构设计系列),原文链接:https://mp.weixin.qq.com/s/cR0kF-AsxwtACPJ_1WGWJw
> 抓取日期:2026-08-09;状态:已拆解入库(见归档记录)

---

这篇文章帮你搞懂三件事：Agent 到底是什么？三个热门框架是什么关系？怎么从零开始搭建一个 Agent 运行时？

一、先搞懂一个概念：Agent 不是 ChatBot
很多人把 Agent 和 ChatBot 搞混。区别其实很简单：ChatBot 只会对话聊天，而Agent 会做事。
Agent 的核心能力是调用工具。它不是一个只会聊天的模型，而是一个能理解需求、选择工具、执行操作、观察结果、循环推理的系统。
这个"理解→决策→执行→观察→循环"的过程，有一个学术名称：ReAct（Reasoning + Acting）。

Agent 的四个核心组件
组件
作用
类比
LLM（大脑）
理解语言、推理决策
人的大脑
Tool（工具）
执行具体操作（搜索、计算、读写文件等）
手和脚
Memory（记忆）
记住对话历史和跨会话信息
人的记忆
Harness（身体）
运行 Agent 的环境，管理状态、调度工具
人的身体
Harness 就是这篇文章的重点——它是让 Agent 真正跑起来的"运行时"。

二、LangChain / LangGraph / DeerFlow：什么关系？
这三个技术是一个自底向上的三层栈：

LangChain 是基础——它定义了"什么是工具""怎么和 LLM 对话"这些底层能力。所有 LLM 应用几乎都绕不开它。
LangGraph 建立在 LangChain 之上——LangChain 早期的 Agent 实现比较简陋（一个简单的 while 循环），LangGraph 用"图"的方式重新定义了 Agent 的工作流：节点是处理步骤，边是流转方向，支持条件分支和循环。LangGraph 是 LangChain 团队自己出的，是 Agent 编排的官方推荐方案。

DeerFlow 建立在 LangGraph 之上——LangGraph 给了你造车的零件，DeerFlow 直接给你一辆能开的车。它把 LangGraph 的 Agent 包装成完整的运行时，加了前端界面、API 网关、沙箱执行、技能系统、记忆系统等工程化能力。字节跳动开源，已经在生产环境中验证过。

三、第一阶段：用 LangChain 跑通第一个 Agent（2-3 天）
3.1 第一个 Agent：10 行代码

from langchain_openai import ChatOpenAIfrom langchain_core.tools import toolfrom langchain.agents import create_react_agent# 1. 定义一个工具@tooldef calculate(expression: str) -> str:    """计算数学表达式，例如 '2 + 3' 或 '100 * 0.85'"""    try:        result = eval(expression)        return f"计算结果: {result}"    except Exception as e:        return f"计算错误: {e}"# 2. 创建 Agentllm = ChatOpenAI(model="gpt-4o-mini", temperature=0)agent = create_react_agent(llm, tools=[calculate])# 3. 运行response = agent.invoke({    "messages": [{"role": "user", "content": "帮我算一下 15% 的税后 8500 是多少"}]})print(response["messages"][-1].content)# 输出: 8500 × 0.85 = 7225，税后是 7225 元
3.2 create_react_agent 发生了什么？

当你运行这段代码时，Agent 内部经历了一个循环：
理解：LLM 分析用户意图 → "用户要算税后金额"

决策：LLM 选择工具 → 调用 calculate("8500 * 0.85")

执行：工具执行 → 返回 7225

观察：LLM 检查结果 → 信息足够，生成最终回答

这就是 ReAct 循环——所有 Agent 框架的核心逻辑都是这个。
3.3 Agent多工具调用

@tooldef search_web(query: str) -> str:    """搜索网页信息"""    # 这里用真实的搜索 API    from langchain_community.tools import DuckDuckGoSearchRun    return DuckDuckGoSearchRun().run(query)@tooldef read_file(file_path: str) -> str:    """读取文件内容"""    with open(file_path, "r") as f:        return f.read()@tooldef write_file(file_path: str, content: str) -> str:    """写入文件"""    with open(file_path, "w") as f:        f.write(content)    return f"文件已保存: {file_path}"# 给 Agent 多个工具agent = create_react_agent(llm, tools=[calculate, search_web, read_file, write_file])response = agent.invoke({    "messages": [{"role": "user", "content": "搜索一下 Python 3.13 的新特性，然后保存到文件里"}]}

至此你已经掌握了 Agent 的基本写法。但 create_react_agent 是一个黑盒——你无法控制循环逻辑、无法加条件分支、无法管理复杂状态。这就是 LangGraph 要解决的问题。

四、第二阶段：用 LangGraph 构建有状态的 Agent（1-2 周）
4.1 为什么需要 LangGraph？
LangChain 的 create_react_agent 是一个简单循环：LLM → 工具 → LLM → ... → 结束。
但真实的 Agent 场景远比这复杂：
需要条件分支：根据不同结果走不同路径

需要并行执行：同时调用多个工具

需要状态管理：记住之前做了什么

需要人机交互：中间暂停，等人确认后继续

需要检查点：出错后能恢复到之前的某个状态

LangGraph 用图（Graph）来描述这些复杂的工作流。

4.2 核心概念
概念
说明
类比
State（状态）
在整个图中流转的数据
流水线上的产品
Node（节点）
处理状态数据的函数
流水线上的工位
Edge（边）
节点之间的连接，可以带条件
传送带的分叉口
Checkpoint（检查点）
保存中间状态，支持回滚
存档点
4.3 代码示例：一个有状态的研究 Agent

from typing import TypedDict, Annotatedfrom langchain_openai import ChatOpenAIfrom langchain_core.messages import HumanMessage, AIMessagefrom langgraph.graph import StateGraph, START, ENDfrom langgraph.graph.message import add_messages# 1. 定义状态class ResearchState(TypedDict):    messages: Annotated[list, add_messages]  # 消息历史    research_results: str                    # 研究结果    report_ready: bool                        # 报告是否就绪# 2. 定义节点llm = ChatOpenAI(model="gpt-4o-mini")def research_node(state: ResearchState):    """研究节点：分析问题"""    messages = state["messages"]    response = llm.invoke(messages)    return {        "messages": [response],        "research_results": response.content    }def write_report_node(state: ResearchState):    """写报告节点：基于研究结果写报告"""    prompt = f"基于以下研究结果，写一份报告:\n\n{state['research_results']}"    response = llm.invoke([HumanMessage(content=prompt)])    return {        "messages": [response],        "report_ready": True    }# 3. 定义条件路由def should_continue(state: ResearchState):    """判断是否需要写报告"""    if "写报告" in state["messages"][-1].content if state["messages"] else "":        return "write_report"    return "research"# 4. 构建图graph = StateGraph(ResearchState)graph.add_node("research", research_node)graph.add_node("write_report", write_report_node)graph.add_edge(START, "research")graph.add_conditional_edges("research", should_continue)graph.add_edge("write_report", END)# 5. 编译并运行app = graph.compile()result = app.invoke({    "messages": [HumanMessage(content="帮我研究一下 2026 年 AI Agent 的发展趋势，然后写一份报告")],    "research_results": "",    "report_ready": False})print(result["messages"][-1].content
4.4 LangGraph 的威力
上面的代码做了什么？
定义了一个有状态的工作流（不只是简单循环）

用条件边控制流向：研究结果够好才写报告

每个节点只关心自己的输入输出，互不耦合

LangGraph 自动管理检查点——出错了可以回滚

当你理解了这段代码，你就理解了 DeerFlow 的核心——因为 DeerFlow 的 Lead Agent 就是一个用 LangGraph 构建的复杂图。

4.5 带工具的 LangGraph Agent

from langgraph.prebuilt import create_react_agent# LangGraph 提供了开箱即用的 ReAct Agent# 这比 LangChain 的 create_react_agent 更强大：# - 支持检查点（可回滚）# - 支持流式输出# - 支持中断和恢复# - 支持人机交互（Human-in-the-loop）agent = create_react_agent(    model=ChatOpenAI(model="gpt-4o-mini"),    tools=[calculate, search_web, read_file, write_file],    # 可以加中间件    state_modifier="你是一个助手，请简洁回答。")# 带检查点的版本（可恢复）from langgraph.checkpoint.memory import MemorySaveragent_with_memory = create_react_agent(    model=ChatOpenAI(model="gpt-4o-mini"),    tools=[calculate, search_web],    checkpointer=MemorySaver())# 流式输出for chunk in agent.stream(    {"messages": [HumanMessage(content="搜索 LangChain 的最新版本号")]},    stream_mode="values"):    if chunk["messages"]:        chunk["messages"][-1].pretty_print()
五、第三阶段：用 DeerFlow 搭建 Harness（2-3 周）
5.1 什么是 Harness？
一个完整的 Agent Harness 需要解决这些问题：
问题
LangChain/LangGraph
DeerFlow
Agent 怎么运行？
你自己写 while 循环
内置运行时引擎
怎么和用户交互？
自己写 CLI 或 API
自带 Next.js 前端 + FastAPI
怎么安全执行代码？
自己想办法
内置 Docker 沙箱
怎么管理长上下文？
手动截断
自动摘要压缩中间件
怎么记住跨会话信息？
自己实现
内置记忆系统
怎么复用业务能力？
手写工具
技能系统（Skill）
怎么委派子任务？
自己编排
子 Agent 自动协调
怎么部署上线？
自己搞 Docker
Docker Compose 一键部署
5.2 中间件（Middleware）
中间件是包裹每次 LLM 调用的插件，在调用前和调用后执行自定义逻辑：用户消息 → [摘要压缩] → [记忆注入] → [计划更新] → LLM → [标题生成] → [记忆排队] → 响应

内置中间件：
- SummarizationMiddleware：自动压缩旧消息，防止上下文溢出
- MemoryMiddleware：跨会话记忆注入
- TodoMiddleware：计划模式，跟踪任务进度
- TokenUsageMiddleware：追踪 Token 用量和成本
- LoopDetectionMiddleware：检测死循环
5.3 技能（Skill）
技能是面向任务的能力包，按需加载——不污染基础 Agent 的上下文。

# skills/custom/weekly-report/SKILL.md---name: weekly-reportdescription: 生成工作周报category: productivity---# 工作周报生成技能## 指令当用户请求生成周报时，按以下步骤：1. 询问本周完成的主要工作2. 询问下周计划3. 生成结构化周报4. 保存为 Markdown 文件
5.4 沙箱（Sandbox）
Agent 执行代码和文件操作的隔离环境：
- 本地沙箱：开发用，直接在本地文件系统操作
- Docker 沙箱：生产用，完全隔离的容器环境
5.5 子 Agent（SubAgent）
处理委派子任务的专注执行者：
Lead Agent（主控）
  ├─ 子 Agent 1：并行搜索资料
  ├─ 子 Agent 2：并行分析数据
  └─ 子 Agent 3：并行生成报告
六、常见问题
Q1：我需要先学完 LangChain 再学 LangGraph 吗？
不需要。 LangChain 的概念很杂（Chain、Agent、Memory、Retriever...），建议只学最基础的（LLM 调用 + Tool 定义），然后直接上 LangGraph。LangGraph 的 API 更清晰、更现代，是官方推荐的方向。
Q2：DeerFlow 和 Dify / Coze 有什么区别？
对比
DeerFlow
Dify / Coze
定位
Agent 运行时（开发者向）
Agent 搭建平台（产品向）
目标用户
工程师
产品经理 / 运营
定制深度
源码级定制
配置级定制
代码控制力
完全可控
有限
适合场景
需要深度定制的 Agent 平台
快速搭建不需要写代码的 Agent
简单说：想拖拽就搭的用 Dify/Coze，想写代码深度定制的用 DeerFlow。

Q3：DeerFlow 和 LangChain 的 Open Agent 有什么区别？
LangChain 的 Open Agent 是 LangChain 团队自己的 Agent 运行时项目，定位和 DeerFlow 类似。区别：
Open Agent：LangChain 官方出品，和 LangChain 生态深度绑定

DeerFlow：字节跳动出品，在 LangGraph 之上构建，有生产验证

两者技术上很相似（都基于 LangGraph），选哪个更多是看社区活跃度和团队偏好。
Agent 开发不像你想的那么神秘。本质上就是三件事：
让 LLM 能调用工具（LangChain）

用图编排复杂工作流（LangGraph）

把工作流包装成可运行的服务（DeerFlow）

从第一个 10 行代码的 Agent 开始，到搭建一个企业级 Agent 运行时，路径是清晰的。关键是动手写代码——看再多文章不如自己跑一遍。