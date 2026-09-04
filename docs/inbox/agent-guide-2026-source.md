# 原始资料:2026年AI Agent构建指南:框架选型与工程实践

> 来源:微信公众号(作者:刘律辰);原文链接:https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg
> 抓取日期:2026-08-09;状态:已整理为六个框架独立文章(LangChain/LlamaIndex/AutoGen/nanobot/Qwen-Agent/DeepAgents)
> 性质:框架选型 + 工程实践(大脑/双手/记忆/中枢四件套抽象 + 完整代码示例 + 场景选型 + 保险 RAG 案例)

---

主流的AI Agent框架：
LangChain： 全能型框架，管道式编排与丰富生态；

nanobot： 轻量级全能选手，工具调用与代码解释器；

LlamaIndex： 数据驱动的 RAG 专家；

AutoGen： 多智能体协作的；

Agent框架对比
维度
LangChain
LlamaIndex
AutoGen
核心定位
全能型框架
RAG 数据接口
多Agent协作
工具注册
@tool 装饰器
FunctionTool 类
@register 装饰器
RAG 支持
需集成 VectorStore
专业级向量索引
需自行集成
多Agent
LangGraph 支持
需自行编排
原生GroupChat
代码执行
需集成
需集成
UserProxyAgent
记忆管理
RunnableWithMessageHistory
Agent chat()
GroupChat 自动
学习曲线
中等
中等
中等
生态完整度
最丰富
RAG 社区
微软生态
根据业务场景，选择Agent框架：
选 LangChain： 如果你要开发通用的 AI 应用，需要灵活控制流程，或者需要切换多种模型。

选 LlamaIndex： 如果你主要做 RAG（企业知识库），手里有一堆 PDF/Word/Excel 要处理。

选 AutoGen： 如果任务太复杂，一个人（Agent）干不完，需要团队（多角色）吵架/协作才能出结果。

场景 1：企业知识库问答推荐：LlamaIndex
专业的文档处理能力；

多种检索策略（向量、关键词、混合）；

索引持久化，支持增量更新；

场景 2：快速 Demo / POC
推荐：Qwen-Agent/Nanobot
配置最简单；

内置 WebUI，无需前端开发；

开箱即用的工具（code_interpreter）；

场景 3：复杂业务流程推荐：LangChain/LangGraph
LCEL 支持灵活的流程编排；

丰富的组件生态；

可与其他框架组合使用；

场景 4：多人协作推荐：AutoGen
多智能体协同对话；

支持角色自定义与任务分工；

内置群聊管理与执行控制；

AI Agent框架解决的问题
AI Agent框架，解决的核心问题：
LLM适配层，可以进行统一调度（头脑）；

工具注册与调度（双手）；

Context管理（记忆、上下文、RAG）；

控制流编排（中枢）；

LLM主动解决各自问题，就需要设计一个机制，抽象出来共性的东西。
大脑的适配层：LLM 统一接口与 Prompt 管理
大脑的适配层： LLM 统一接口与 Prompt 管理。
Model Adapter (适配器模式)： 抹平不同模型 (OpenAI, DeepSeek, Qwen) 的 API 差异，各框架的实现方式：
from langchain_community.chat_models
import ChatTongyi

llm = ChatTongyi(
	model_name="deepseek-v3",
	dashscope_api_key=api_key
)
from llama_index.llms.dashscope import DashScope

llm = DashScope(
	model="deepseek-v3",
	api_key=api_key,
	temperature=0.7
)
框架层做了一个中间层，把统一的指令（如 invoke(“你好”)）翻译成特定模型的 API 调用。LLM 统一接口的作用：
统一调用方式;

统一了参数配置（如 temperature）;

输出格式（统一转为 Message 对象）;

框架
LLM 封装方式
特点
LangChain
ChatTongyi / ChatOpenAI 类
丰富的模型适配器，统一接口
LlamaIndex
DashScope / OpenAI 类
与 Settings 全局配置结合
Prompt Engineering 工程化System Message 的动态注入，将人设与上下文解耦：
# LangChain 的 PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
("system","You are a helpful assistant."),
	MessagesPlaceholder(variable_name="history"),
("human","{input}")
])
# Qwen-Agent 的 system_message
system_instruction ='''你是一个乐于助人的AI助手。在收到用户的请求后，你应该：
- 首先绘制一幅图像，得到图像的url，
- 然后运行代码下载该图像。
你总是用中文回复用户。'''
人设 (角色定义) 与任务流程 (上下文指令) 分离，便于复用和维护。
双手的标准化：工具注册与调度 (Tool Registry)
各框架提供了不同的工具注册方式：
模式
框架
特点
@tool 装饰器
LangChain
最简洁，docstring 自动解析
@register_tool + 类
Qwen-Agent
显式参数定义，结构清晰
FunctionTool 封装
LlamaIndex
强类型约束，适合复杂工具
LLM的调度也叫做LLM自我问答：System Prompt + Tool Prompt（工具自我问答的模板）工具通过@tool、@register_tool 或FunctionTool把工具的相关信息（name、param、description）给到Tool Prompt。
比如：以下是我可以使用的工具，包括1）tool_name = 天气预告，描述：tool_description，参数tool_params；2）tool_name = 地图导航，描述：tool_description，参数tool_params；…
如果我想要调用工具，我将返回以下格式：{“tool_name”：“”，“tool_params”：{}}
====LLM response ={“tool_name”：“get_weather”，“tool_params”：{“city”:“beijing”}}
下一步，在agent框架中，进行识别拦截tool_name == get_weather的方法名，tool_params方法的参数{“city”:“beijing”}在SDK内找到后，调用脚本get_weather方法的代码。
三大框架工具注册对比
LangChain @tool 的优势： 自动从 docstring 解析工具描述和参数说明,支持类型注解，LLM 自动理解参数类型,一行装饰器，零配置即可使用。
# ========== LangChain @tool 装饰器 ==========
from langchain_core.tools import tool

@tool
defping_tool(target:str)->str:
"""检查本机到指定主机名或IP地址的网络连通性。
参数:target: 目标主机名或IP地址
返回:模拟的ping结果
"""

if"unreachable"in target:
returnf"Ping {target} 失败"
returnf"Ping {target} 成功"
# ========== Qwen-Agent @register_tool ==========
@register_tool('my_image_gen')
classMyImageGen(BaseTool):
	description ='AI 绘画服务，输入文本描述，返回图像 URL'
	parameters =[{
'name':'prompt',
'type':'string',
'description':'期望的图像内容的详细描述',
'required':True
}]

defcall(self, params:str, kwargs)->str:
	prompt = json5.loads(params)['prompt']
return json5.dumps({'image_url':f'https://...'})
# ========== LlamaIndex FunctionTool ==========
defretrieve_documents(query:str)->str:
"""从文档中检索相关信息"""
	response = query_engine.query(query)
returnstr(response)

retrieve_tool = FunctionTool.from_defaults(fn=retrieve_documents)
LLM 是如何看见工具的？框架会将 Python 函数的 name、docstring (功能描述) 和 type hints (参数类型) 转换成 JSON Schema 喂给 LLM 。
LangChain: 也就是 @tool，主要是在使用 Python 原生特性，最符合直觉 。Qwen-Agent: @register_tool，使用显式定义，强约束，适合复杂参数 。
记忆的存储：Context 管理机制
记忆系统的架构：1）短期记忆 (Window)
对话历史截断；

滑动窗口策略；

避免 Token 爆炸；

2）长期记忆 (RAG)
VectorStoreIndex 向量索引；

文档分块与 Embedding；

相似度检索；

三大框架记忆管理对比
# LangChain 短期记忆 (RunnableWithMessageHistory)
from langchain_core.chat_history import InMemoryChatMessageHistory

from langchain_core.runnables.history import RunnableWithMessageHistory

# 会话存储
store ={}

defget_session_history(session_id:str):
if session_id notin store:
		store[session_id]= InMemoryChatMessageHistory()
return store[session_id]

# 创建带记忆的对话链
conversation = RunnableWithMessageHistory(
	chain,
	get_session_history,
	input_messages_key="input",
	history_messages_key="history"
)

# 使用时指定 session_id
config ={"configurable":{"session_id":"user_123"}}
output = conversation.invoke({"input":"Hi!"}, config=config)
session_id 机制支持多用户并发会话；MessagesPlaceholder 自动注入历史到 Prompt。
# === Qwen-Agent 短期记忆 (messages 列表) ===
messages =[]# 对话历史
messages.append({'role':'user','content': query})

for response in bot.run(messages=messages):
pass
messages.extend(response)# 追加响应
# ==== LlamaIndex 长期记忆 (VectorStoreIndex) ====
index = VectorStoreIndex.from_documents(documents)
# 持久化
index.storage_context.persist(persist_dir="./storage")
框架
短期记忆
长期记忆
LangChain
RunnableWithMessageHistory + session_id
需集成 VectorStore
Qwen-Agent
messages 列表手动管理
files 参数加载文档
LlamaIndex
Agent chat() 内置
专业级 VectorStoreIndex
为什么需要进行Context管理？LLM 是无状态的，它记不住你说过什么，且 Context Window（上下文窗口）是昂贵的资源。 => 有限注意力的管理。
短期记忆：
Session ID 很重要，它是多用户并发的基础 。

滑动窗口策略——只保留最近 N 轮，防止 Token 爆炸。

长期记忆：
这是 RAG 的范畴，利用向量数据库进行相关性检索，而非时间顺序回忆 。

中枢的编排：控制流设计 (Orchestration)
复杂的任务不能靠 LLM 一口气说完，需要拆解步骤。
模式
说明
适用场景
管道模式 (Pipeline)
LangChain 的 prompt | llm | parser 链式调用
线性处理流程
单人模式 (Loop)
经典 ReAct 循环：思考 -> 行动 -> 观察
单 Agent 完成任务
多人模式 (DAG)
接力赛：明确的执行顺序
流程化任务 (如投资决策)
多人模式 (Chat)
圆桌会议：自由讨论
开放式协作
LangChain LCEL (LangChain Expression Language) 特点：
| 管道符：直观的链式调用，类似 Unix 管道；

invoke()：统一的调用接口；

支持流式输出、批处理、异步调用；

LangChain 管道模式：Prompt => LLM => Parser
# ========== LangChain 管道式编排 (LCEL)，管道语法: prompt | llm ==========
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate(
	input_variables=["product"],
	template="What is a good name for a company that
	makes {product}?",
)

# 使用管道符组合
chain = prompt | llm
# invoke 调用
result = chain.invoke({"product":"colorful socks"})
ReAct 循环 (Agent模式)：Thought思考=> Action行动=> Observation 观察=> Thought思考…
# ========== Agent 模式: create_agent ==========
from langchain.agents import create_agent

# 定义工具
tools =[ping_tool, dns_tool, calculator]

# 创建 Agent (LangChain 1.x 新写法)
agent = create_agent(llm, tools)

# 使用 messages 格式调用
result = agent.invoke({"messages":[("user","检查www.example.com 的连通性")]})
print(result["messages"][-1].content)
控制流的编排：
Chain (链式)：由于输入确定，输出确定，像工厂流水线（Pipeline）。

Loop (循环)：即 ReAct 模式（思考-行动-观察-思考），像一个不断试错的实验员，直到任务完成 。

DAG (有向无环图)：像多人接力赛，有明确的前后依赖关系。

LangChain 全能型LLM应用框架
大家对Langchain感兴趣，可以去看下我之前写的文章 LangChain=AI瑞士军刀？零基础小白秒变多任务高手！。
LangChain 全能型LLM应用框架，丰富的生态和组件，适合各种复杂场景。
LangChain 的核心优势：
生态丰富：支持 100+ 模型、50+ 向量数据库、大量预置工具；

LCEL 管道语法：直观的链式调用，支持流式/批处理/异步；

@tool 装饰器：最简洁的工具注册方式；

完善的记忆管理：session_id 机制支持多用户并发；

场景
说明
工具调用型 Agent
网络诊断、数据查询、API 调用等需要多工具协作的场景
多轮对话系统
客服机器人、智能助手等需要记忆上下文的场景
复杂流程编排
使用 LCEL 构建多步骤处理流程
快速原型开发
丰富的组件库，快速搭建 POC
核心特性：LCEL 管道语法
LangChain Expression Language (LCEL) 是 LangChain 1.x 的核心创新，使用 | 管道符连接组件。

LangChain 采用组件化的方式，核心优势是把 Prompt、Model、Memory、Retriever 都做成了标准积木（Runnable）。
基础管道示例
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Tongyi

# 加载模型
llm = Tongyi(model_name="qwen-turbo", dashscope_api_key=api_key)

# 创建 Prompt Template
prompt = PromptTemplate(
	input_variables=["product"],
	template="What is a good name for a company that makes {product}?",
)

# 管道语法组合
chain = prompt | llm

# invoke 调用
result = chain.invoke({"product":"colorful socks"})
print(result)
工具注册：@tool 装饰器
LangChain 的 @tool 装饰器是最简洁的工具注册方式，自动从 docstring 解析工具描述：
from langchain_core.tools import tool

@tool
defping_tool(target:str)->str:

"""检查本机到指定主机名或IP地址的网络连通性。
	参数: target: 目标主机名或IP地址
	返回: 模拟的ping结果
	"""

if"unreachable"in target:
returnf"Ping {target} 失败：请求超时。"
returnf"Ping {target} 成功：延迟 20ms。"

@tool
defdns_tool(hostname:str)->str:
"""解析给定的主机名，获取其对应的IP地址。
	参数: hostname: 要解析的主机名
	返回: 模拟的DNS解析结果
	"""

if hostname =="www.example.com":
returnf"DNS 解析 {hostname} 成功：IP 地址是 93.184.216.34"
returnf"DNS 解析 {hostname} 失败：找不到主机。"
创建 Agent
# LangChain 1.x Agent 创建方式
from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi

# 加载模型 (使用 ChatModel 以支持 tool calling)
llm = ChatTongyi(model_name="deepseek-v3", dashscope_api_key=api_key)

# 定义工具列表
tools =[ping_tool, dns_tool, calculator]

# 创建 Agent (LangChain 1.x 新写法)
agent = create_agent(llm, tools)

# 使用 messages 格式调用
result = agent.invoke({"messages":[("user","我无法访问 w帮我诊断一下")]})

# 获取最终回复
print(result["messages"][-1].content)
带记忆的对话链
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.chat_history import InMemoryChatMessageHistory

from langchain_core.runnables.history import RunnableWithMessageHistory

# 创建带历史记录的 prompt
prompt = ChatPromptTemplate.from_messages([
("system","You are a helpful assistant."),
	MessagesPlaceholder(variable_name="history"),
("human","{input}")
])

# 创建 chain
chain = prompt | llm
store ={}# 会话存储

defget_session_history(session_id:str):
if session_id notin store:
		store[session_id]= InMemoryChatMessageHistory()
return store[session_id]

# 创建带记忆的对话链
conversation = RunnableWithMessageHistory(
	chain,
	get_session_history,
	input_messages_key="input",
	history_messages_key="history"
)

# 使用时指定 session_id
config ={"configurable":{"session_id":"user_123"}}
output = conversation.invoke({"input":"Hi there!"}, config=config)
print(output.content)
LlamaIndex - 数据驱动的RAG 专家
LlamaIndex：为 LLM 装上私有数据的最强接口，如果不涉及复杂的多人协作，只是想基于文档问答，它是首选。
LlamaIndex 的核心优势：
一站式文档处理：加载、分块、向量化、索引、检索；

索引持久化：避免重复创建，快速启动；

多种检索策略：向量检索、关键词检索、混合检索；

与 Agent 无缝集成：FunctionTool 封装查询引擎；

场景
说明
企业知识库
内部文档、FAQ、操作手册的智能问答
合同审查助手
基于合同文档的条款检索与解读
学术论文分析
论文摘要、引用关系、知识图谱构建
客服机器人
产品手册、服务政策的实时检索回答
核心概念：Index优先
Index-First 哲学：不同于 LangChain 关注流程，LlamaIndex 关注数据结构。它认为 LLM 应用的核心瓶颈在于如何让 LLM 索引私有数据。

加载文档并创建索引
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 读取文档目录
reader = SimpleDirectoryReader('./docs')
documents = reader.load_data()
print(f"加载了 {len(documents)} 个文档")

# 创建向量索引
index = VectorStoreIndex.from_documents(documents)

# 持久化索引 (避免重复创建)
index.storage_context.persist(persist_dir="./storage")
从存储加载索引
from llama_index.core import StorageContext, load_index_from_storage

# 检查索引是否已存在
persist_dir ="./storage"

if os.path.exists(persist_dir):
# 从存储中加载索引 (快速启动)
	storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
	index = load_index_from_storage(storage_context)
print("从存储加载索引成功")
else:
# 创建新索引
	index = VectorStoreIndex.from_documents(documents)
ReAct Agent 与工具集成
将 retrieve_tool 作为一个函数插拔到 Agent 上：
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool

# 创建查询引擎
query_engine = index.as_query_engine(similarity_top_k=5)

# 定义检索工具
defretrieve_documents(query:str)->str:
"""从文档中检索相关信息"""
	response = query_engine.query(query)

returnstr(response)

# 封装为 FunctionTool
retrieve_tool = FunctionTool.from_defaults(fn=retrieve_documents)

# 创建 ReAct Agent
agent = ReActAgent.from_tools(
	tools=[retrieve_tool],
	llm=llm,
	verbose=True,# 显示思考过程
	system_prompt="你是一个乐于助人的AI助手，可以从文档中检索信息",
)
AutoGen 多智能体框架
AutoGen 是微软开源的多智能体对话框架，用于构建多个 AI Agent 协作完成复杂任务。它的核心理念是让 Agent 之间通过自然语言对话来协作，而非硬编码的函数调用。
你也可以使用 Agent Framework 2025 年 10 月起，微软将 AutoGen 置为维护模式——仅修漏洞，不再新增功能；所有新特性都做到 Agent Framework 上。官方文档明确把 Agent Framework 称为下一代 Semantic Kernel 与 AutoGen，鼓励新项目直接迁移。
Agent 是 AutoGen 的基本单元，每个 Agent 具备以下属性：
属性
说明
name
Agent 的名称标识，在对话中用于区分发言者
system_message
角色设定/提示词，定义 Agent 的职责和行为方式
llm_config
LLM 配置，包括模型、API Key、温度等参数
tools
可调用的外部工具函数，扩展 Agent 能力
常用 Agent 类型
类型
用途
特点
ConversableAgent
基础对话 Agent
最灵活，可完全自定义
AssistantAgent
助手 Agent
默认由 LLM 驱动，适合生成内容
UserProxyAgent
用户代理
可执行代码、调用工具、请求人工输入
项目中使用 ConversableAgent 创建了 4 个角色，区别在于是否注册工具函数。
GroupChat (群聊)： 将多个 Agent 放在同一个对话中协作的容器。

from autogen import GroupChat, GroupChatManager

# 创建群聊，设定发言顺序
group_chat = GroupChat(
	agents=[
# 1. 数据员先获取数据
		self.data_agent,
# 2. 分析师进行分析
		self.analyst_agent,
# 3. 风控官评估风险
		self.risk_agent,
# 4. 交易员给出建议
		self.trader_agent
],

messages=[],
# 4个Agent各发言1-2次
max_round=8,
# 按顺序轮流发言
speaker_selection_method="round_robin",
)

# 创建群聊管理器
manager = GroupChatManager(
	groupchat=group_chat,
	llm_config=self.data_agent.llm_config,
)

# 发起对话
result = self.data_agent.initiate_chat(
	manager,
	message="用户查询: 分析一下宁德时代能不能买",
)
对话流程：1）用户发起查询；2）GroupChatManager 根据策略选择第一个发言的 Agent；3）被选中的 Agent 生成回复（可能调用工具）；4）回复加入对话历史，所有 Agent 可见；5）GroupChatManager 选择下一个发言者；6）重复 3-5，直到达到 max_round 或满足终止条件；

发言者选择策略
策略
说明
适用场景
round_robin
按 agents 列表顺序轮流发言
流程明确的任务（如：数据→分析→风控→决策）
random
随机选择下一个发言者
头脑风暴、创意讨论
auto
由 LLM 判断谁最适合回答当前问题
开放式讨论、问答场景
自定义函数
完全控制选择逻辑
复杂业务流程、条件分支
如果你的任务有明确的执行顺序，用 round_robin；如果需要灵活讨论，用 auto。

投资委员会使用 round_robin 是因为投资决策有固定流程：先获取数据 → 再分析 → 再风控 → 最后决策。

案例：多文件智能问答Agent
搭建一个 保险产品智能问答Agent，用于帮助用户快速了解各类保险产品的详细信息。加载了多个保险产品文档，包括：
雇主责任险；

平安商业综合责任保险；

企业团体综合意外险；

财产一切险；

施工保、装修保等；

用户可以通过自然语言提问，系统会从文档中检索相关信息并给出回答。
源码仓库：liulvuchen/Llamaindex-agent-RAG。
技术方案：RAG (检索增强生成)RAG 的核心流程：用户问题 → 向量检索 → 召回相关文档 → LLM 生成回答
使用RAG的原因：
LLM 没有私有数据的知识；

避免模型幻觉（编造信息）；

回答可追溯到具体文档来源；

DeepAgents 实现
配置极简，上手迅速；

专属界面，便捷交互；

内置沙箱，支撑编码；

多模文件，直接解析；

LlamaIndex 实现
Index 优先：专注于数据索引和检索；

一站式 RAG：文档加载、分块、索引、检索一体化；

ReAct Agent：内置思考-行动循环；

数据清洗
prompt：
你先扫码下 @docs 内的.pdf文件，我建议使用PyPDF2库提取@docs 内.pdf文件，生成对应的markdown文件，给我3个方案，并且给出置信度；

补充，平安商业综合责任保险（亚马逊）.pdf没办法通过PyPDF2提取文本，需要使用ocr，单独为这个文件给个方案，能进行文本提取；

文字 PDF：我选方案三；亚马逊 PDF：固定本独立 OCR 方案（PaddleOCR）；输出统一建议：docs/ * .md；requirements.txt 增加：PyPDF2、paddleocr（及所需 paddle 依赖）。按照我给的方案更新todos；

Agent方案设计
prompt：
我要搭建一个 保险产品智能问答Agent，用于帮助用户快速了解各类保险产品的详细信息。加载了@docs/md 文件夹内所有的.md文件(保险产品文档)，包括：

雇主责任险；

平安商业综合责任保险；

企业团体综合意外险；

财产一切险；

施工保、装修保等；用户可以通过自然语言提问，系统会从文档中检索相关信息并给出回答。

技术方案：agent框架使用deepagents，RAG使用llama_index，向量检索使用faiss-cpu，向量库使用ChromaDB,embedding嵌入模型使用AGICTO平台的text-embedding-v4模型，可以直接参考@at/DEV_AGI进行LLM请求.py,切片策略使用LLM语义切片，本地进行数据持久化：保存Faiss索引文件（.faiss）、元数据信息（.pkl）、页码映射关系（page_info.pkl）,向量相关文件都放到@rag_data 文件夹内。其他的向量逻辑，你可以参考@cankao/langchain-agent-multi-files.py，进行优化，参考文件内涉及用户query改写（利用上下文信息，把用户query不同query类型进行改写：上下文依赖性型、对比型、模糊指代型、多意图型、反问型、条件型），query改写的LLM模型可以使用qwen3.5-35b-a3b模型，LLM调用你可以参考@at/DEV_AGI进行LLM请求.py。Llamindex相关的，你可以参考@cankao/llamaindex-agent-multi-files.py 进行优化。agent使用deepagents框架AGICTO平台的qwen3.7-plus模型，LLM调用你可以参考@at/DEV_AGI进行LLM请求.py，剩下的你可以参考@cankao/qwen-agent-multi-files.py 进行优化agent业务。

你帮我设计3套方案，并且给出置信度。

页面展示：