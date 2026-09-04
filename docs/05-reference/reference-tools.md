# 工具与库清单:从训练到部署的一站式索引

> **一句话摘要**:按「ML/DL 框架、LLM 推理与部署、向量数据库、Agent 框架、数据处理、可视化」六组收录常用工具,每项附一句话简介与官网链接。
>
> **来源**:各工具官网 / GitHub 官方仓库。

## 概念

### 为什么单独列一份工具清单?

- **工具是学习的"脚手架"**:论文和书籍给原理,工具给实现。读 [必读论文清单](reference-papers.md) 时,每个概念都能在这份清单里找到对应的库。
- **避免"重复造轮子"**:除 Karpathy 式的"亲手实现"练习外,真实项目应该直接站在成熟工具上。
- **版本与生态会变**:这里只收**稳定、主流、有官方维护**的工具,并给出官网入口,方便你随时查最新文档。

### 选择工具的四个原则

1. **看维护活跃度与社区规模**(GitHub Stars、Issue 响应)。
2. **优先官方文档齐全、有示例的库**——工具是拿来用的,文档即教程。
3. **匹配硬件与场景**:本地机器跑不动大模型,就用 llama.cpp / Ollama 这类轻量方案。
4. **能用命令行/API 就别上重型平台**,保持可复现、可迁移。

## 清单主体

### ML / DL 框架

- **PyTorch** — 动态计算图,研究界事实标准,所有现代 LLM 库的底座;官网 <https://pytorch.org/>
- **Hugging Face Transformers** — 数千个预训练模型的统一 API,模型、Tokenizer、训练微调一站搞定;<https://huggingface.co/docs/transformers>
- **scikit-learn** — 经典机器学习算法全家桶,数据预处理、模型评估、管道一体化;<https://scikit-learn.org/>
- **XGBoost / LightGBM** — 梯度提升树双雄,表格数据竞赛的首选;<https://xgboost.readthedocs.io/>、<https://lightgbm.readthedocs.io/>
- **JAX** — 函数式自动微分 + XLA 编译,加速研究实验与大规模训练;<https://jax.readthedocs.io/>
- **TensorFlow / Keras** — 生产部署生态成熟,适合 TF 存量项目;<https://www.tensorflow.org/>

### LLM 推理与部署

- **vLLM** — 高吞吐 LLM 推理引擎,PagedAttention 与连续批处理,服务化部署标配;<https://github.com/vllm-project/vllm>
- **llama.cpp** — 纯 C/C++ 推理,GGAUF 格式与量化,笔记本 CPU 也能跑 LLM;<https://github.com/ggml-org/llama.cpp>
- **Ollama** — 一行命令下载并运行本地模型,自带 API,个人实验最友好;<https://ollama.com/>
- **Text Generation Inference (TGI)** — Hugging Face 官方推理服务,支持量化与多 GPU 张量并行;<https://github.com/huggingface/text-generation-inference>
- **SGLang** — 新一代推理框架,RadixAttention 做前缀复用,吞吐优势明显;<https://github.com/sgl-project/sglang>
- **LM Studio** — 桌面 GUI 工具,本地加载 GGUF 模型、聊天与 OpenAI 兼容 API;<https://lmstudio.ai/>
- **LLaMA-Factory** — 微调神器:LoRA/QLoRA 等 PEFT 方法图形化训练开源模型;<https://github.com/hiyouga/LLaMA-Factory>

### 向量数据库

- **FAISS** — Meta 开源,最广泛使用的向量检索库,轻量嵌入,和 RAG 无缝配合;<https://github.com/facebookresearch/faiss>
- **Chroma** — 嵌入式向量库,几行代码跑通"文档 → 向量 → 检索",学习曲线最平;<https://www.trychroma.com/>
- **Milvus** — 分布式向量数据库,支持十亿级向量与混合检索,生产场景;<https://milvus.io/>
- **Qdrant** — Rust 实现的高性能向量库,自带过滤与语义缓存,API 简洁;<https://qdrant.tech/>
- **pgvector** — PostgreSQL 官方扩展,给现有关系库直接加向量检索,免新组件;<https://github.com/pgvector/pgvector>
- **LanceDB** — 嵌入式 Serverless 向量库,轻量、零运维;<https://lancedb.com/>

### Agent 框架

- **LangChain** — 生态最大的 LLM 应用框架:工具调用、记忆、Agent、RAG 全都有;<https://www.langchain.com/langchain>
- **LangGraph** — 基于图的状态机式 Agent 编排,可控、可调试,当前生产首选;<https://www.langchain.com/langgraph>
- **LlamaIndex** — 数据侧专家:文档解析、索引、检索,配合任何 Agent 做 RAG;<https://www.llamaindex.ai/>
- **AutoGen** — 微软开源多 Agent 对话框架,擅长"多个 Agent 互相协作解决任务";<https://microsoft.github.io/autogen/>
- **CrewAI** — 角色扮演式多 Agent 协作,像管理团队一样定义"角色-任务-流程";<https://github.com/crewAIInc/crewAI>
- **OpenAI Agents SDK** — OpenAI 官方 Agent 工具包,轻量、生产级,基于"指令 + 工具 + 交接";<https://github.com/openai/openai-agents-python>
- **Dify** — 低代码 LLM 应用平台,拖拽搭建工作流、RAG 与 Agent 应用;<https://dify.ai/>

### 数据处理

- **NumPy** — 数值计算基石,张量、广播、线性代数,所有框架的共同底座;<https://numpy.org/>
- **Pandas** — 表格数据处理的标准工具,清洗、合并、聚合一把梭;<https://pandas.pydata.org/>
- **Polars** — 更快的内存 DataFrame,多线程 + 惰性求值,大数据量替代 Pandas;<https://pola.rs/>
- **Hugging Face Datasets** — 海量开源数据集的统一加载与处理接口,和训练无缝衔接;<https://huggingface.co/docs/datasets>
- **Dask** — 把 Pandas/NumPy 扩展到分布式与超内存数据集;<https://www.dask.org/>

### 可视化

- **Matplotlib** — 最经典的绘图库,论文配图与训练曲线首选;<https://matplotlib.org/>
- **Plotly** — 交互式图表,浏览器里缩放、悬停,适合做分析演示;<https://plotly.com/>
- **TensorBoard** — 训练指标与计算图可视化,`writer.add_scalar` 一行接一行;<https://www.tensorflow.org/tensorboard>
- **Weights & Biases (W&B)** — 实验追踪、超参数扫描、模型对比,团队协作标配;<https://wandb.ai/>
- **Streamlit** — 纯 Python 把模型包成 Web 应用,几十行代码出一个 Demo;<https://streamlit.io/>
- **Gradio** — 给模型一键生成交互界面,分享链接即可演示,ML 社区最爱;<https://www.gradio.app/>

## 实践:如何用这套工具制定学习计划

- **第 1-2 周(环境)**:装好 Python + PyTorch + scikit-learn,用 NumPy/Pandas 完成数据处理基础。参考站内 [AI 入门](../01-ai-basics/index.md) 中的环境搭建建议。
- **第 2-4 周(复现)**:读 [必读论文清单](reference-papers.md) 时,用 PyTorch 复现每篇的核心实验;跑 Kaggle 小竞赛练 XGBoost/LightGBM。
- **第 5-8 周(LLM)**:用 Ollama 或 llama.cpp 本地跑通一个小模型 → 用 Transformers + LLaMA-Factory 做一次微调 → 用 vLLM 部署一个服务,走完"训练-微调-部署"链路。
- **第 9 周起(RAG + Agent)**:Chroma/FAISS 做检索 → LlamaIndex 整理数据 → LangGraph 或 AutoGen 搭 Agent。做项目时按需选型,不贪多。
- **贯穿始终**:用 W&B 或 TensorBoard 记录每一次实验,用 Streamlit/Gradio 把结果变成可展示的 Demo——**工具只有用起来才是自己的**。

**避坑提示**:

- 版本冲突是常态:LLM 生态迭代极快,**先读官方文档的安装说明**,固定 Python 版本与 CUDA 版本。
- 不要盲目追新:生产环境选"稳定 + 文档全"的库,新框架先在 Demo 里试。
- 每个工具学"够用即可":能跑通一个官方示例 + 一个自己的小项目,就算入门,不必通读全部文档。

## 延伸阅读

- 站内:[必读论文清单](reference-papers.md)、[书籍与课程](reference-books-courses.md)、[博客与社区](reference-blogs.md)、[大语言模型](../02-llm/index.md)、[Agent](../03-agents/index.md)
- 外部:Papers with Code <https://paperswithcode.com/>;GitHub Trending <https://github.com/trending/python>
