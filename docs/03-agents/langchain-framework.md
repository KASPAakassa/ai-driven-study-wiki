# LangChain 1.x:全能型 Agent 框架——LCEL 管道、@tool 与记忆管理

> **一句话摘要**:LangChain 是生态最丰富的"全能型"Agent 框架——用组件化(Runnable)的方式把 Prompt、Model、Memory、Retriever 做成标准积木,核心创新 **LCEL 管道语法**(`|` 连接组件);工具注册用最简洁的 `@tool` 装饰器(自动从 docstring 解析描述与类型);记忆用 `RunnableWithMessageHistory` 管理多用户会话。配套 LangGraph 提供流程编排。
>
> **来源**:微信公众号《2026年AI Agent构建指南:框架选型与工程实践》(刘律辰),https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg;官方文档 https://docs.langchain.com

## 概念

**定位**:全能型框架——管道式编排与丰富生态。LangChain 用组件化方式把 Prompt、Model、Memory、Retriever 都做成标准积木(Runnable),可自由组合;生态最丰富,社区工具/集成最多。

**与站内其他文章的关系**:本文聚焦 LangChain **1.x 的具体用法**(LCEL / @tool / 记忆),站内 [Agent 框架](agent-frameworks.md) 是框架总览对比;[Agent 框架七方对比](agent-frameworks-seven-comparison.md) 覆盖了更新一代的七个框架。选 LangChain 的场景:**开发通用 AI 应用、需要灵活控制流程、需要切换多种模型**。

## 原理:LCEL 管道语法与组件化

LangChain 1.x 的核心创新是 **LangChain Expression Language (LCEL)**——用 `|` 管道符连接组件:

```python
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Tongyi

llm = Tongyi(model_name="qwen-turbo", dashscope_api_key=api_key)

prompt = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?",
)

# 管道语法组合
chain = prompt | llm

# invoke 调用
result = chain.invoke({"product": "colorful socks"})
print(result)
```

**LLM 适配层(大脑)**:框架层做中间层,把统一指令(如 `invoke("你好")`)翻译成特定模型 API 调用——统一调用方式、统一参数配置(temperature)、统一输出格式(Message 对象)。LangChain 用 `ChatTongyi` / `ChatOpenAI` 等适配器类。

**Prompt 工程化**:System Message 动态注入,将人设与上下文解耦:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
```

## 代码 / 实现:工具注册与记忆

### @tool 装饰器(最简洁的工具注册)

自动从 docstring 解析工具描述和参数说明,支持类型注解,一行装饰器零配置:

```python
from langchain_core.tools import tool

@tool
def ping_tool(target: str) -> str:
    """检查本机到指定主机名或IP地址的网络连通性。
    参数: target: 目标主机名或IP地址
    返回: 模拟的ping结果
    """
    if "unreachable" in target:
        return f"Ping {target} 失败"
    return f"Ping {target} 成功"
```

**LLM 如何"看见"工具**:框架把 Python 函数的 name、docstring(功能描述)、type hints(参数类型)转换成 **JSON Schema** 喂给 LLM,LLM 返回 `{"tool_name": "get_weather", "tool_params": {...}}`,框架识别拦截后在 SDK 中找到并调用对应方法。

### 创建 Agent(LangChain 1.x 新写法)

```python
from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi

llm = ChatTongyi(model_name="deepseek-v3", dashscope_api_key=api_key)
tools = [ping_tool, dns_tool, calculator]

agent = create_agent(llm, tools)

result = agent.invoke({"messages": [("user", "我无法访问 w帮我诊断一下")]})
print(result["messages"][-1].content)
```

### 记忆管理(短期记忆)

`RunnableWithMessageHistory` + `InMemoryChatMessageHistory`,`session_id` 机制支持多用户并发会话,MessagesPlaceholder 自动注入历史到 Prompt:

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

config = {"configurable": {"session_id": "user_123"}}
output = conversation.invoke({"input": "Hi!"}, config=config)
print(output.content)
```

## 实践 / 应用:场景与选型

| 场景 | 推荐 |
| --- | --- |
| 通用 AI 应用、灵活流程控制、多模型切换 | **LangChain** |
| 企业知识库 RAG | LlamaIndex |
| 快速 Demo / POC | Qwen-Agent / nanobot |
| 复杂业务流程 | **LangChain/LangGraph**(LCEL 流程编排 + 丰富组件生态,可与其他框架组合) |
| 多人协作 | AutoGen |

**LangChain 优势**:组件最丰富、LCEL 管道编排灵活、可组合其他框架。**注意**:记忆需要自行集成(RunnableWithMessageHistory 是短期,长期记忆靠 RAG/VectorStore);多 Agent 需配 LangGraph。

## 总结

- **定位**:全能型框架,组件化(Runnable)+ LCEL 管道编排,生态最丰富;
- **LLM 适配**:ChatTongyi/ChatOpenAI 等适配器统一调用方式/参数/输出格式;
- **工具注册**:`@tool` 装饰器最简洁——docstring + 类型注解自动转 JSON Schema;
- **记忆**:`RunnableWithMessageHistory` + session_id 管理多用户短期会话;
- **下一步**:复杂流程编排用 [LangGraph](agent-framework-selection.md)(站内已收录,运行时层定位),或对比新一代框架见 [Agent 框架七方对比](agent-frameworks-seven-comparison.md)。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg;官方文档 https://docs.langchain.com
- 站内:[Agent 框架](agent-frameworks.md)(总览对比)、[Agent 框架选型地图](agent-framework-selection.md)(LangGraph 运行时层定位)、[Agent 框架七方对比](agent-frameworks-seven-comparison.md)(新一代框架)、[LlamaIndex](llamaindex-framework.md)(RAG 专家)
