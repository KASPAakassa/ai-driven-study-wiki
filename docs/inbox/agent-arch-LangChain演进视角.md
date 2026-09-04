# 原始资料:一文搞懂 Agent 开发(从 LangChain 版本演进视角)

> 来源:微信公众号(Agent 架构设计系列),原文链接:https://mp.weixin.qq.com/s/CRccAYUeeAelf6dK7OzO7A
> 抓取日期:2026-08-09;状态:已拆解入库(见归档记录)

---

2022 年 10 月，LangChain 以一个 800 行的 Python 侧项目诞生。那时 ChatGPT 尚未发布，"Agent"这个词在 LLM 领域几乎无人提起。三年后，LangChain v1.0 发布，整个框架只剩一个核心 API——create_agent。
这三年间发生了什么？为什么一个框架最终把自己收敛成了一个"Agent 驾驶舱"？答案藏在 LangChain 的四次版本迭代里。每一次迭代，都折射出业界对"Agent 到底是什么"的理解变化。

Agent = Model + Harness
这是 LangChain v1.0 对 Agent 的最终定义。但要真正理解这句话，我们需要回到起点。
1什么是 Agent？先抛一个最朴素的定义
在 LLM 语境下，Agent 是一个让模型在循环中调用工具、直到完成给定任务的系统。
关键词有三个：
循环——不是单次调用，而是反复"思考→行动→观察"直到任务完成

工具——模型本身只能生成文本，需要工具才能与外部世界交互（搜索、计算、读写文件）

任务驱动——Agent 自主决定调用什么工具、什么时候停止，而非人工编排每一步

这个定义看起来简单，但它的实现方式在过去三年经历了三次根本性变化。LangChain 的版本号，恰好标记了这三个阶段。
2阶段一：Chain 时代（v0.0.x，2022.10 - 2024.01）
——Agent 还不是主角，"链"才是
v0.0.1 — v0.0.3xx
核心抽象：Chain
LangChain 的名字来自 Language + Chains。最初的设计哲学是：把 LLM 应用拆解为预定义的计算步骤序列。比如 RAG = 检索步骤 + 生成步骤。每一步是一个"链"，多条链可以串联成更复杂的流程。
Chain 长什么样
# v0.0.x 时代的典型写法
from langchain.chains import LLMChain, RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

llm = OpenAI(model_name="text-davinci-003")

# 定义一条"链"
chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["question"],
        template="回答以下问题: {question}"
    )
)

result = chain.run("什么是快速排序？")这个阶段的 Agent 是怎么做的？2022 年 12 月，LangChain 加入了首批通用 Agent，基于 ReAct 论文（Reasoning + Acting）。核心思路是让 LLM 生成一段 JSON 来表示工具调用，然后框架解析这段 JSON 去执行工具：
# v0.0.x 时代的 Agent — 基于 JSON 解析
from langchain.agents import initialize_agent, Tool

tools = [
    Tool(name="Search", func=search_func, description="搜索信息"),
]

agent = initialize_agent(
    tools, llm,
    agent="zero-shot-react-description",
    verbose=True
)

# LLM 实际生成的是这样的文本：
# Thought: I need to search for this.
# Action: Search
# Action Input: "快速排序算法"
# Observation: 快速排序是一种...
# Thought: I now know the answer.
# Final Answer: 快速排序是...

agent.run("什么是快速排序？")这个阶段的致命问题：工具调用依赖解析 LLM 生成的自由文本/JSON。模型稍微"发挥一下"，格式就错了，整个循环就崩了。Agent 在原型阶段很惊艳，但完全无法用于生产。
转折点：2023 年 3 月 — function calling
OpenAI 发布了 function calling API，让模型可以直接生成结构化的工具调用载荷，而不是自由文本。其他模型提供商跟进。LangChain 更新为使用 function calling 作为工具调用的首选方式。
这是一个分水岭：工具调用从"解析 JSON 赌运气"变成了"API 原生支持"。Agent 的可靠性提升了数量级。
3阶段二：稳定化与 LangGraph 接管（v0.1 - v0.3，2024.01 - 2024.10）
——Agent 被交给 LangGraph，LangChain 开始"让位"
v0.1.0   v0.2   v0.3
核心矛盾：高级抽象太黑盒，开发者要控制权
v0.1 是 LangChain 的第一个稳定版，标志着行业从"原型"走向"生产"。但生产环境暴露了一个根本问题：AgentExecutor 是一个黑盒——你能传工具和模型，但无法控制循环的每一步。你想加一个"工具调用前的人类审批"节点？想在特定条件下跳过某个工具？想分支执行？都做不到。
v0.1：稳定但不灵活
# v0.1 时代 — AgentExecutor 仍是黑盒
from langchain.agents import AgentExecutor, create_openai_tools_agent

agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
executor.invoke({"input": "天气如何？"})

# 问题：你无法控制循环内部的流程
# 想加 human-in-the-loop？想加条件分支？想加重试逻辑？
# —— 都需要绕过 AgentExecutor 自己重写v0.2：LangGraph 登场（2024 年 2 月）
LangChain 团队的解决方案是：不修补黑盒，而是建一个新的底层。LangGraph 发布了。
LangGraph 的核心是基于图的执行模型——你定义节点（函数）和边（流转条件），框架按图执行。这给了开发者对 Agent 流程的完全控制权：
# v0.2 时代 — 用 LangGraph 构建可控的 Agent
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

# 方式一：用预构建的 create_react_agent（简单场景）
agent = create_react_agent(model, tools)
agent.invoke({"messages": ["天气如何？"]})

# 方式二：用 StateGraph 自定义流程（复杂场景）
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)
workflow.add_node("human_review", human_review)  # 人类审批！
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "human_review")  # 工具后审批
workflow.add_edge("human_review", END)关键转变：从 v0.2 开始，LangChain 官方推荐用 LangGraph 构建 Agent，而非 LangChain 自己的 AgentExecutor。LangChain 自身的高级抽象开始"让位"。
v0.3：大扫除（2024 年 9 月）
v0.3 做了两件事：
技术升级：全面迁移到 Pydantic 2，放弃 Python 3.8

标记弃用：大量旧 Chain（LLMChain、ConversationChain 等）被标记弃用，并附迁移指南指向 LangGraph 或 LCEL（LangChain Expression Language）

到 2024 年 10 月，LangGraph 正式成为构建 AI 应用的首选。LangChain 中多数 Chain 和 Agent 被标记弃用。这个信号非常明确：LangChain 在自我瘦身，准备把"Agent 构建"这件事彻底交给 LangGraph。
4阶段三：纯 Harness（v1.0，2025.10）
——所有抽象收敛为唯一的 create_agent
v1.0.0
核心抽象：create_agent（唯一的 Agent 入口）
v1.0 做了三年来最激进的重构。所有 Chain 和 Agent 被砍掉，只留下 langchain.agents.create_agent 一个入口。遗留功能移至 langchain-classic 包。框架从一个"什么都包"的工具箱，收敛成了一个纯粹的"Agent 驾驶舱"。
Harness 到底是什么
Harness 的字面意思是"驾驭装置"——就像马的缰绳和马鞍。你不需要重新造一匹马（模型），你只需要一套驾驭它的装置。
Harness = Prompt + Tools + Middleware + State
Harness 的职责用一句话概括：在正确的时间，为给定任务，把正确的上下文交给模型。 它是模型循环周围的一切——提示词、工具、中间件、状态管理——但唯独不包含模型本身。

v1.0 的 Agent 长什么样
# v1.0 — 唯一的 Agent 入口
from langchain.agents import create_agent

def get_weather(city: str) -> str:
"""Get weather for a given city."""
returnf"It's always sunny in {city}!"

agent = create_agent(
    model="openai:gpt-5.5",         # 模型：统一 "provider:model" 格式
    tools=[get_weather],              # 工具：任何 Python callable
    system_prompt="You are a helpful assistant",  # 提示词
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "SF天气如何？"}]
})5中间件：Harness 的灵魂
v1.0 最核心的设计决策不是"砍掉旧 API"，而是用中间件系统取代了之前所有的扩展机制。
在 v0.x 中，如果你想：
在模型调用前注入动态提示词 → 用 pre_model_hook

在模型调用后拦截输出 → 用 post_model_hook

处理工具调用错误 → 自己写 try/except 包裹

压缩溢出的上下文 → 自己写逻辑

加人类审批 → 用 LangGraph 的 interrupt

这些机制散落在不同地方，无法组合复用。v1.0 把它们统一成了中间件——每个中间件处理一个关注点，在正确时机钩入 Agent 循环，自由组合：

一个生产级 Agent 的配置，可能长这样：
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRetryMiddleware, ToolRetryMiddleware,
    SummarizationMiddleware, HumanInTheLoopMiddleware,
)
from deepagents.middleware import (
    FilesystemMiddleware, SubAgentMiddleware,
)
from deepagents.backends import StateBackend

backend = StateBackend()

agent = create_agent(
    model="openai:gpt-5.5",
    tools=[search, write_file, run_code],
    system_prompt="你是一个研究助手",
    middleware=[
FilesystemMiddleware(backend=backend),           # 文件系统
SummarizationMiddleware(model="openai:gpt-5.5",  # 上下文压缩
                              trigger={"tokens": 10000}),
SubAgentMiddleware(backend=backend,              # 子 Agent 委派
            subagents=[{"name": "researcher", "tools": [search]}]),
ModelRetryMiddleware(max_retries=3),             # 模型容错
ToolRetryMiddleware(max_retries=2),              # 工具容错
HumanInTheLoopMiddleware(                         # 人类审批
            interrupt_on={"write_file": True}),
    ],
)中间件的设计哲学：取所需，弃其余。每个中间件处理一个关注点，在正确时机钩入循环。你可以只用一个，也可以全用，还可以自己写。这正是 Harness 的精髓——它不替你做决定，只提供挂钩。
6Agent 的核心循环：一张图看懂
无论是 v0.0 的 ReAct Agent 还是 v1.0 的 create_agent，Agent 的核心机制始终是同一个循环：

这个循环在 v0.0 时代就已经存在（Thought → Action → Observation → Thought → ...），只是 v1.0 把每个环节都变成了可插拔的中间件挂钩点。
总结：Agent 的三年进化史

回头看，LangChain 的三年做了一件事：不断做减法，直到剩下不可再减的核心。
减掉了 Chain（被  LangGraph 取代）、减掉了 AgentExecutor（被 create_agent 取代）、减掉了 Memory 模块（被 checkpointer + 中间件取代）。最终剩下的，就是一个模型循环 + 工具 + 提示词 + 中间件挂钩的 Harness。
这不是退化，而是进化。因为 Agent 的核心从来不是"框架替你做了多少事"，而是"框架给你多少控制权"。v1.0 的 Harness 给了你最小但完整的控制面：模型你选、工具你定、提示词你写、中间件你组合。框架只负责把循环跑起来，把挂钩留给你。