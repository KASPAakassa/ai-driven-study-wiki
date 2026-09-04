# 书籍与课程清单:按主题选书,按阶段进阶

> **一句话摘要**:按「机器学习、深度学习、LLM、Agent、数学基础」五组整理经得起检验的书与课程,每项注明作者、类型、适合水平与链接。
>
> **来源**:各出版社 / 课程官方页面;免费资源优先收录一手来源。

## 概念

### 为什么需要一个书单?

- 资料太多反而学不下去。**书单帮你锁定少数几本主线**,围绕主线建立知识,而不是刷收藏夹。
- 书籍和课程互补:**课程给节奏与反馈**(视频、作业、社区),**书籍给深度与体系**(推导、参考)。两者搭配,效果远好于单刷其中一种。
- 数学基础是隐性地基:读论文卡壳,十有八九是线性代数、概率、微积分没跟上。见 [必读论文清单](reference-papers.md) 的对应方法论。

### 选书原则

- 优先**一手/官方来源**:作者本人写的书、官方出的免费课程,胜过二手解读。
- 优先**能免费获取**:标注"免费"的资源可直接上手,零成本试错。
- 标注**适合水平**,避免"上来就读花书"式的劝退。
- 配套代码优先:能边读边跑,学习效率翻倍(见 [参考工具清单](reference-tools.md))。

## 清单主体

### 机器学习

- **《统计学习方法》**(李航,第 1 版 2012 / 第 2 版 2019)—— 书 · 入门至进阶
  - 中文经典:十种统计学习方法,公式推导严谨、篇幅精炼,适合"学完课程后当手册"或做面试复习。
  - <https://book.douban.com/subject/10590856/>
- **《机器学习(西瓜书)》**(周志华,2016)—— 书 · 入门至进阶
  - 中文覆盖面最广的教科书,西瓜数据集贯穿全书,讲原理、不教调包;适合配合课程使用。
  - <https://book.douban.com/subject/26708119/>
- **Machine Learning Specialization**(Andrew Ng / DeepLearning.AI)—— 课程 · 零基础入门
  - 最经典入门课:线性回归、逻辑回归、神经网络、推荐系统,作业简单、直觉极强。
  - <https://www.coursera.org/specializations/machine-learning-introduction>
- **The Elements of Statistical Learning (ESL)**(Hastie, Tibshirani & Friedman, 2009)—— 书 · 进阶
  - 统计学习圣经,免费 PDF;机器学习理论(回归、树、SVM、集成)的权威参考。
  - <https://hastie.su.domains/ElementsOfStatLearning/>
- **Pattern Recognition and Machine Learning (PRML)**(Bishop, 2006)—— 书 · 进阶至高级
  - 概率视角的机器学习经典,贝叶斯方法讲得尤其透彻,适合研究生水平。
  - <https://www.microsoft.com/en-us/research/publication/pattern-recognition-machine-learning/>

### 深度学习

- **《动手学深度学习 (Dive into Deep Learning)》**(李沐等,2020)—— 书+课程 · 入门至进阶
  - 代码驱动的开源教材,从线性回归写到 Transformer,中文版免费,配合视频课食用。
  - <https://zh.d2l.ai/>(英文: <https://d2l.ai/>)
- **《深度学习(花书)》**(Goodfellow, Bengio & Courville, 2016)—— 书 · 进阶
  - 深度学习的"圣经",网络结构、优化、正则化的理论源头,在线版免费。
  - <https://www.deeplearningbook.org/>
- **CS231n: Deep Learning for Computer Vision**(Stanford, Li Fei-Fei 团队)—— 课程 · 入门至进阶
  - 计算机视觉+卷积网络经典课,笔记(CS231n Notes)是全网最好的 DL 入门读物之一。
  - <http://cs231n.stanford.edu/>
- **CS224n: Natural Language Processing with Deep Learning**(Stanford)—— 课程 · 入门至进阶
  - NLP 与 Transformer 的经典课程,作业从 word2vec 一路做到机器翻译。
  - <https://web.stanford.edu/class/cs224n/>
- **Practical Deep Learning for Coders**(fast.ai)—— 课程 · 零基础入门
  - "先跑通、再理解"的教学法,8 节课做出可用模型,特别适合非科班。
  - <https://course.fast.ai/>
- **Neural Networks 系列视频**(3Blue1Brown)—— 视频 · 零基础入门
  - 深度学习直觉之王:反向传播、梯度下降的动画化解释,看一遍胜过读十页推导。
  - <https://www.3blue1brown.com/topics/neural-networks>

### 大语言模型 (LLM)

- **Neural Networks: Zero to Hero**(Andrej Karpathy, 2022-2023)—— 视频课程 · 入门至进阶
  - 从零手写 micrograd → makemore → GPT,一集集把 LLM 底层"点亮",最适合"必须亲手实现"的学习者。
  - <https://karpathy.ai/zero-to-hero.html>
- **Hugging Face NLP Course**—— 课程 · 入门
  - 官方免费课程:用 Transformers 做分类、翻译、微调、部署,一站式了解生态。
  - <https://huggingface.co/learn/nlp-course>
- **《Build a Large Language Model (From Scratch)》**(Sebastian Raschka, 2024)—— 书 · 进阶
  - 不依赖任何 LLM 库,从数据准备到预训练到微调,完整实现一个 GPT-2 级模型,普通笔记本可跑。
  - <https://www.manning.com/books/build-a-large-language-model-from-scratch>
- **The Full Stack LLM Bootcamp**(The Full Stack / Chip Huyen 等)—— 课程 · 进阶
  - 覆盖 LLM 应用全链路:Prompt 工程、RAG、LLMOps、Agent,含 2023 春季全套视频。
  - <https://fullstackdeeplearning.com/llm-bootcamp/>

### Agent

- **Hugging Face Agents Course**—— 课程 · 入门至进阶
  - 免费开源课程:Agent 是什么、工具调用、RAG Agent、多 Agent 协作,配 Code 实现。
  - <https://huggingface.co/learn/agents-course>
- **LangChain / LangGraph Academy**—— 课程 · 入门
  - 官方入门课,从"用 LangGraph 写第一个 Agent"到状态机、记忆、多 Agent 编排。
  - <https://academy.langchain.com/>
- **Building Effective Agents**(Anthropic, 2024-12)—— 文章 · 入门
  - 一线实战总结:workflow 与 agent 的区别、五种常见模式、"能简单就不要复杂"。
  - <https://www.anthropic.com/research/building-effective-agents>
- **LLM Powered Autonomous Agents**(Lilian Weng, 2023)—— 文章 · 进阶
  - Agent 领域被引用最多的综述长文:规划、记忆、工具使用三件套,配海量参考文献。
  - <https://lilianweng.github.io/posts/2023-06-23-agent/>

### 数学基础

- **3Blue1Brown《线性代数的本质》**—— 视频 · 零基础入门
  - 用几何直觉讲透矩阵、线性变换、特征值,DL 里的一切"张量操作"都有了画面。
  - <https://www.3blue1brown.com/topics/linear-algebra>
- **3Blue1Brown《微积分的本质》**—— 视频 · 零基础入门
  - 导数、链式法则的直观理解,学反向传播前的必修课。
  - <https://www.3blue1brown.com/topics/calculus>
- **《Mathematics for Machine Learning》**(Deisenroth, Faisal & Ong, 2020)—— 书 · 入门至进阶
  - 专为 ML 写的数学书:线性代数、向量微积分、概率、优化,PDF 免费。
  - <https://mml-book.github.io/>
- **The Matrix Calculus You Need for Deep Learning**(Parr & Howard, 2018)—— 文章 · 入门至进阶
  - 用"分子布局"把深度学习的矩阵求导讲得明明白白,适合补梯度推导。
  - <https://explained.ai/matrix-calculus/>

## 实践:如何组合这些资源制定学习计划

- **第 1 个月(零基础打底)**:3Blue1Brown 线代/微积分 + Andrew Ng 机器学习专项 + fast.ai。目标:建立直觉,跑通第一个模型。站内可配合 [AI 入门](../01-ai-basics/ai-intro.md) 系列文章。
- **第 2-3 个月(深度学习)**:《动手学深度学习》为主线,CS231n/CS224n 按兴趣二选一。每个章节结束,回到 [论文清单](reference-papers.md) 读对应论文原文。
- **第 4-5 个月(LLM)**:Karpathy Zero to Hero 全程 + Raschka《从零构建 LLM》二选一(建议都做),再刷 Hugging Face NLP Course 熟悉生态,进入 [LLM 章节](../02-llm/index.md) 学习。
- **第 6 个月起(Agent + 项目)**:Hugging Face Agents Course → LangGraph Academy,同时读 Anthropic《Building Effective Agents》与 Lilian Weng 综述;之后带着问题做项目,进入 [Agent 章节](../03-agents/index.md)。
- **贯穿始终**:**书 + 课程 + 论文 + 代码**四件套缺一不可。课程给节奏,书补深度,论文给源头,代码给手感。

**经验之谈**:

- 不要同时开太多课。**一次一门主线 + 一本参考书**是极限。
- 免费的优先:本清单里 ESL、花书、D2L、MML 全部免费,入门阶段零成本。
- 遇到公式卡壳,先回数学基础组补课,再回来读,而不是硬啃。

## 延伸阅读

- 站内:[必读论文清单](reference-papers.md)、[工具与库](reference-tools.md)、[博客与社区](reference-blogs.md)、[机器学习基础](../01-ai-basics/index.md)
- 外部:arXiv <https://arxiv.org/>;Papers with Code <https://paperswithcode.com/>
