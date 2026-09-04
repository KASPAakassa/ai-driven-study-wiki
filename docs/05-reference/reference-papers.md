# 必读论文清单:从感知机到 AI Agent 的经典路线

> **一句话摘要**:按「机器学习基础 → 深度学习 → Transformer 与 LLM → RLHF 与对齐 → Agent」五主题整理核心论文,每条附原文链接与一句价值。
>
> **来源**:各论文官方页面(arXiv / Nature / NeurIPS),链接均为原文出处。

## 概念

### 为什么直接读论文?

- **一手资料**:教科书是二手转述,论文是知识原始出处,能看清作者的动机与局限。
- **理解演进逻辑**:LLM、Agent 能力是一篇篇论文累积的,按时间线读能建立因果链。
- **找到真问题**:Related Work 与 Limitations 是找研究空白的最佳入口。

### 收录原则

- 只收录**里程碑级**、可公开获取(arXiv / 官网 PDF)的经典。
- 每个主题 3-6 篇,够建立主线即可。
- 论文要**配合实现读**:边读边跑官方代码(见 [参考工具清单](reference-tools.md))。

## 清单主体

### 机器学习基础

| 论文 | 作者 / 年份 | 链接 | 一句话价值 |
| --- | --- | --- | --- |
| The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain | Rosenblatt / 1958 | [psycnet](https://psycnet.apa.org/doi/10.1037/h0042519) | 神经网络开山之作:第一个能学习的"机器神经元"。 |
| Support-Vector Networks | Cortes & Vapnik / 1995 | [Springer](https://link.springer.com/article/10.1007/BF00994018) | SVM 奠基论文,理解"间隔最大化 + 核方法"范式。 |
| Random Forests | Breiman / 2001 | [Springer](https://link.springer.com/article/10.1023/A:1010933404324) | 集成学习代表:"多个弱模型投票"为何强于单个强模型。 |
| Greedy Function Approximation: A Gradient Boosting Machine | Friedman / 2001 | [Project Euclid](https://projecteuclid.org/journals/annals-of-statistics/volume-29/issue-5/Greedy-function-approximation-A-gradient-boosting-machine/10.1214/aos/1013203451.full) | Gradient Boosting 原论文,XGBoost / LightGBM 的理论源头。 |

### 深度学习

| 论文 | 作者 / 年份 | 链接 | 一句话价值 |
| --- | --- | --- | --- |
| Learning representations by back-propagating errors | Rumelhart, Hinton & Williams / 1986 | [Nature](https://www.nature.com/articles/323533a0) | 反向传播的奠基论文,今天所有神经网络的训练基石。 |
| Long Short-Term Memory | Hochreiter & Schmidhuber / 1997 | [JKU PDF](https://www.bioinf.jku.at/publications/older/2604.pdf) | LSTM 原文,RNN 时代的代表作,理解"门控记忆"思想。 |
| Gradient-Based Learning Applied to Document Recognition | LeCun et al. / 1998 | [Stanford PDF](http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf) | LeNet / 卷积网络经典,CNN 的教科书级论文。 |
| ImageNet Classification with Deep Convolutional Neural Networks | Krizhevsky, Sutskever & Hinton / 2012 | [NeurIPS](https://papers.nips.cc/paper_files/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html) | AlexNet:深度学习引爆点,GPU + ReLU + Dropout 组合拳。 |
| Adam: A Method for Stochastic Optimization | Kingma & Ba / 2015 | [arXiv](https://arxiv.org/abs/1412.6980) | 自适应学习率的代表,今天用得最多的优化器。 |
| Deep Residual Learning for Image Recognition | He et al. / 2016 | [arXiv](https://arxiv.org/abs/1512.03385) | ResNet:残差连接让"越深越好"成为可能,Transformer 也靠它。 |

### Transformer 与 LLM

| 论文 | 作者 / 年份 | 链接 | 一句话价值 |
| --- | --- | --- | --- |
| Attention Is All You Need | Vaswani et al. / 2017 | [arXiv](https://arxiv.org/abs/1706.03762) | Transformer 原文,现代 LLM 的根基,Self-Attention 必须亲手推导。 |
| Improving Language Understanding by Generative Pre-Training | Radford et al. / 2018 | [OpenAI PDF](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) | GPT-1:"预训练 + 微调"范式的开端。 |
| BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding | Devlin et al. / 2019 | [arXiv](https://arxiv.org/abs/1810.04805) | BERT:双向编码器代表作,与 GPT 对比理解收获最大。 |
| Language Models are Unsupervised Multitask Learners | Radford et al. / 2019 | [OpenAI PDF](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) | GPT-2:规模化与零样本泛化的实证。 |
| Language Models are Few-Shot Learners | Brown et al. / 2020 | [arXiv](https://arxiv.org/abs/2005.14165) | GPT-3:1750 亿参数 + In-Context Learning,LLM 时代开幕。 |
| LoRA: Low-Rank Adaptation of Large Language Models | Hu et al. / 2021 | [arXiv](https://arxiv.org/abs/2106.09685) | 微调成本解药:低秩近似,一切高效微调 (PEFT) 的基石。 |

### RLHF 与对齐

| 论文 | 作者 / 年份 | 链接 | 一句话价值 |
| --- | --- | --- | --- |
| Deep Reinforcement Learning from Human Preferences | Christiano et al. / 2017 | [arXiv](https://arxiv.org/abs/1706.03741) | RLHF 思想源头:用人类偏好信号训练奖励模型,再强化学习优化。 |
| Training language models to follow instructions with human feedback | Ouyang et al. / 2022 | [arXiv](https://arxiv.org/abs/2203.02155) | InstructGPT 技术报告:RLHF 落地的完整配方。 |
| Emergent Abilities of Large Language Models | Wei et al. / 2022 | [arXiv](https://arxiv.org/abs/2206.07682) | 解释"模型大了突然变聪明"的涌现现象,理解规模的意义。 |
| Constitutional AI: Harmlessness from AI Feedback | Bai et al. / 2022 | [arXiv](https://arxiv.org/abs/2212.08073) | 用 AI 代替人工标注的对齐方案,Claude 系列的技术前身。 |
| Direct Preference Optimization: Your Language Model is Secretly a Reward Model | Rafailov et al. / 2023 | [arXiv](https://arxiv.org/abs/2305.18290) | DPO:绕开 RL 直接优化偏好,对齐从"重工程"变成"轻训练"。 |

### Agent

| 论文 | 作者 / 年份 | 链接 | 一句话价值 |
| --- | --- | --- | --- |
| Chain-of-Thought Prompting Elicits Reasoning in Large Language Models | Wei et al. / 2022 | [arXiv](https://arxiv.org/abs/2201.11903) | CoT:让模型"先想再说",推理能力大幅提升的起点。 |
| Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Lewis et al. / 2020 | [arXiv](https://arxiv.org/abs/2005.11401) | RAG 原文:检索 + 生成,LLM 外挂知识的标配架构。 |
| ReAct: Synergizing Reasoning and Acting in Language Models | Yao et al. / 2022 | [arXiv](https://arxiv.org/abs/2210.03629) | ReAct 循环:思考 → 行动 → 观察,Agent 思考-行动范式鼻祖。 |
| Toolformer: Language Models Can Teach Themselves to Use Tools | Schick et al. / 2023 | [arXiv](https://arxiv.org/abs/2302.04761) | 让模型自己决定何时调用工具,工具自动化的早期探索。 |
| Reflexion: Language Agents with Verbal Reinforcement Learning | Shinn et al. / 2023 | [arXiv](https://arxiv.org/abs/2303.11366) | 把失败反馈写成文字再改进,Agent 自我反思代表作。 |
| Generative Agents: Interactive Simulacra of Human Behavior | Park et al. / 2023 | [arXiv](https://arxiv.org/abs/2304.03442) | "斯坦福小镇":带记忆、计划、社交的拟人 Agent,想象力的天花板。 |

## 实践:如何用这些论文制定学习计划

- **第一阶段(打地基,2-3 周)**:只读「机器学习基础 + 深度学习」两组,重点是**复现而非通读**。每篇挑一个核心实验,用 [PyTorch](https://pytorch.org/) 或 [scikit-learn](https://scikit-learn.org/) 跑通,对照 [Papers with Code](https://paperswithcode.com/) 的官方实现。
- **第二阶段(理解 LLM,3-4 周)**:按时间线读「Transformer 与 LLM」:Attention → GPT-1 → BERT → GPT-2 → GPT-3 → LoRA,搭配 Karpathy 的 "Let's build GPT" 系列(见 [博客清单](reference-blogs.md))边读边写。
- **第三阶段(对齐与应用,2-3 周)**:先读 CoT,再读 InstructGPT → DPO → Constitutional AI,理解"为什么需要对齐"与"DPO 为何更简单"。
- **第四阶段(做项目,持续)**:做 Agent 时按需精读 RAG / ReAct / Toolformer,用 [LangGraph](https://www.langchain.com/langgraph) 或 [AutoGen](https://github.com/microsoft/autogen) 复现论文场景。

**读论文方法论**:

- 三遍法:第一遍只看标题、摘要、图表;第二遍读正文勾出推导;第三遍带着"我要复现什么"精读细节。
- 只读一手:**综述和博客用来选论文,但最终必须回到原文**。
- 每读完一篇用三句话写笔记:"解决什么问题 / 怎么解决 / 留下什么"。沉淀到 [📥 收件箱](../inbox/README.md) 或本站章节。

## 延伸阅读

- 站内:[机器学习基础](../01-ai-basics/index.md)、[大语言模型](../02-llm/index.md)、[Agent](../03-agents/index.md)、[书籍与课程](reference-books-courses.md)、[博客与社区](reference-blogs.md)
- 外部:arXiv 机器学习分类页 <https://arxiv.org/list/cs.LG/recent>;Semantic Scholar <https://www.semanticscholar.org/>;Papers with Code <https://paperswithcode.com/>
