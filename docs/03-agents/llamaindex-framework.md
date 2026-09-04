# LlamaIndex:为 LLM 装上私有数据的 RAG 专家

> **一句话摘要**:LlamaIndex 是"数据驱动的 RAG 专家"——**Index-First 哲学**:不同于 LangChain 关注流程,LlamaIndex 关注数据结构,认为 LLM 应用的核心瓶颈是"如何让 LLM 索引私有数据"。一站式文档处理(加载/分块/向量化/索引/检索)、索引持久化、多种检索策略,并用 `FunctionTool` 封装查询引擎无缝集成 Agent。
>
> **来源**:微信公众号《2026年AI Agent构建指南:框架选型与工程实践》(刘律辰),https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg;官方文档 https://docs.llamaindex.ai

## 概念

**定位**:数据驱动的 RAG 专家——为 LLM 装上私有数据的最强接口。如果不涉及复杂多人协作、只是想基于文档问答,它是首选。

**核心优势**:

- **一站式文档处理**:加载、分块、向量化、索引、检索;
- **索引持久化**:避免重复创建,快速启动;
- **多种检索策略**:向量检索、关键词检索、混合检索;
- **与 Agent 无缝集成**:`FunctionTool` 封装查询引擎。

**适合场景**:企业知识库(内部文档/FAQ/操作手册智能问答)、合同审查助手、学术论文分析、客服机器人(产品手册/服务政策实时检索)。

## 原理:Index-First 哲学

LlamaIndex 的核心是 **Index 优先**:LLM 应用的核心瓶颈在于如何让 LLM 索引私有数据,因此它围绕数据结构(而非流程)设计。

**记忆/上下文管理**:长期记忆用 `VectorStoreIndex` 向量索引——文档分块 + Embedding + 相似度检索,回答可追溯到具体文档来源,避免模型幻觉。

## 代码 / 实现:加载、索引、检索与 Agent 集成

### 加载文档并创建索引

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 读取文档目录
reader = SimpleDirectoryReader('./docs')
documents = reader.load_data()
print(f"加载了 {len(documents)} 个文档")

# 创建向量索引
index = VectorStoreIndex.from_documents(documents)

# 持久化索引 (避免重复创建)
index.storage_context.persist(persist_dir="./storage")
```

### 从存储加载索引(快速启动)

```python
from llama_index.core import StorageContext, load_index_from_storage

persist_dir = "./storage"

if os.path.exists(persist_dir):
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)
    print("从存储加载索引成功")
else:
    index = VectorStoreIndex.from_documents(documents)
```

### ReAct Agent 与工具集成

将 retrieve_tool 作为一个函数插拔到 Agent 上:

```python
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool

# 创建查询引擎
query_engine = index.as_query_engine(similarity_top_k=5)

# 定义检索工具
def retrieve_documents(query: str) -> str:
    """从文档中检索相关信息"""
    response = query_engine.query(query)
    return str(response)

# 封装为 FunctionTool
retrieve_tool = FunctionTool.from_defaults(fn=retrieve_documents)

# 创建 ReAct Agent
agent = ReActAgent.from_tools(
    tools=[retrieve_tool],
    llm=llm,
    verbose=True,  # 显示思考过程
    system_prompt="你是一个乐于助人的AI助手，可以从文档中检索信息",
)
```

## 实践 / 应用:完整案例(多文件智能问答 Agent)

**案例**:保险产品智能问答 Agent——加载多个保险产品文档(雇主责任险、平安商业综合责任保险、财产一切险、施工保等),用户通过自然语言提问,系统从文档检索并回答。

**技术方案**:RAG(检索增强生成)——用户问题 → 向量检索 → 召回相关文档 → LLM 生成回答。用 RAG 的原因:LLM 没有私有数据知识、避免幻觉(编造信息)、回答可追溯到具体文档来源。

**工程要点**(数据清洗 + Agent 方案设计):

- PDF 提取:文字 PDF 用 PyPDF2 生成 Markdown;扫描版 PDF 需独立 OCR 方案(PaddleOCR);
- 技术栈:Agent 框架(deepagents)+ RAG(llama_index)+ 向量检索(faiss-cpu)+ 向量库(ChromaDB)+ embedding(text-embedding-v4)+ LLM 语义切片;
- 本地持久化:Faiss 索引文件(.faiss)+ 元数据(.pkl)+ 页码映射(page_info.pkl);
- Query 改写:利用上下文把用户 query 分类改写(上下文依赖型/对比型/模糊指代型/多意图型/反问型/条件型)。

**LlamaIndex 实现要点**:Index 优先、一站式 RAG、ReAct Agent 内置思考-行动循环。对比 DeepAgents 实现:配置极简、内置沙箱、多模文件直接解析。

## 总结

- **定位**:数据驱动的 RAG 专家——Index-First,关注数据结构而非流程;
- **一站式**:文档加载/分块/向量化/索引/检索一体化,索引持久化避免重复创建;
- **多种检索**:向量、关键词、混合检索;回答可溯源防幻觉;
- **Agent 集成**:FunctionTool 封装查询引擎 + ReActAgent;
- **下一步**:对比 [LangChain](langchain-framework.md)(流程编排)与 [DeepAgents](deepagents-framework.md)(Agent harness),或看站内 RAG 基础。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg;官方文档 https://docs.llamaindex.ai;案例源码 liulvuchen/Llamaindex-agent-RAG
- 站内:[RAG 检索增强生成](../02-llm/rag.md)(原理基础)、[LangChain 1.x](langchain-framework.md)、[DeepAgents](deepagents-framework.md)、[Agent 框架](agent-frameworks.md)
