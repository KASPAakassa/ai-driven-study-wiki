# 微软 AI for Beginners 课程导读:AI 基础的系统学习地图

> **一句话摘要**:《AI for Beginners》(微软开源课程,github.com/microsoft/AI-For-Beginners,13400+ 文件/20+ 章/多语言)是一套从零到一的 AI 基础课程:符号 AI(知识表示与专家系统)→ 神经网络(感知机到框架)→ 计算机视觉(CNN/GAN/目标检测)→ NLP(文本分类到 Transformer)→ 其他(遗传算法/强化学习/多智能体系统)→ 伦理。**注意:本课程是 AI 基础而非 Agent 专题**——Agent 相关内容集中在符号 AI 的知识表示/推理与"多智能体系统"一章。本导读给出课程地图,并与站内 [01-ai-basics](../01-ai-basics/index.md) 逐章映射,作为基础知识的配套学习路径。
>
> **来源**:微软开源课程《AI for Beginners - A Curriculum》,https://github.com/microsoft/AI-For-Beginners;作者 Dmitry Soshnikov 等;原始资料存档于 `references/ai-for-beginners/`

## 概念:这是一套什么样的课程

微软 AI for Beginners 是面向初学者的 AI 基础课程,强调**概念 + 动手(Jupyter Notebooks)**。它不是 Agent 专题库,而是一张完整的 AI 知识地图——理解 Agent 所需的神经网络、NLP、推理基础都在其中。

!!! tip "与站内知识库的关系"
    站内 [01-ai-basics](../01-ai-basics/index.md) 已覆盖 AI 基础/ML/DL 概念文章;本课程是**系统化的配套课程**——适合按章系统学习,站内文章做要点速查,课程做动手实践。

## 原理:课程地图(13 章 + 扩展)

| 章节 | 主题 | 站内对应文章 |
| --- | --- | --- |
| **1-Intro** | AI 入门:弱 AI vs 强 AI(AGI)、AI 能做什么 | [AI/ML/DL 概念](../01-ai-basics/ai-ml-dl.md) |
| **2-Symbolic** | 知识表示与专家系统:知识/信息/数据(DIKW 金字塔)、知识表示、推理、Ontology | [Ontology 四大技术](../06-enterprise/ontology-agent-adoption/ontology-four-technologies.md)、[操作型本体论](../06-enterprise/ontology-agent-adoption/palantir-operational-ontology.md) |
| **3-NeuralNetworks** | 神经网络入门:感知机、自建框架、PyTorch/TensorFlow 框架 | [神经网络基础](../01-ai-basics/dl-backpropagation.md)、[numpy 从零实现 NN](../04-practice/practice-numpy-nn.md) |
| **4-ComputerVision** | 计算机视觉:OpenCV、CNN、迁移学习、自编码器、GAN、目标检测、语义分割 | [卷积神经网络 CNN](../01-ai-basics/dl-cnn.md)(基础章节);GAN/目标检测/语义分割等 CV 专题待补充 |
| **5-NLP** | 自然语言处理:文本分类、情感分析、命名实体、QA、文本生成、摘要、翻译 | [Transformer/LLM 章节](../02-llm/index.md)基础 |
| **6-Other** | 遗传算法、深度强化学习、**多智能体系统** | [多 Agent 协作](../03-agents/multi-agent.md)、[多智能体协作设计](../03-agents/agent-team-room-collaboration.md) |
| **7-Ethics** | 伦理与负责任 AI:公平/可靠/隐私/包容/透明/问责 + Responsible AI Toolbox | 待补充 |
| **X-Extras** | 多模态网络 | [多模态与实时交互 Agent](../03-agents/agent-multimodal-realtime.md)(Agent 侧);多模态模型专题待补充 |

!!! note "Agent 相关内容的真实分布"
    用户可能期望"Agent 内容很多",实际本课程是 AI 基础:①**2-Symbolic** 的知识表示/推理是经典 Agent(符号智能体)的理论基础;②**6-Other/23-MultiagentSystems** 是经典多智能体系统(详见站内 [经典多智能体系统](../03-agents/multi-agent-systems-classical.md))。现代 LLM Agent 内容请见站内 [03-agents 章节](../03-agents/index.md)。

## 代码 / 实现:课程动手环境

课程以 Jupyter Notebook 为主,可用 Binder 在线运行(仓库含 `binder/` 与 `environment.yml`):

```bash
# 本地运行环境(基于 requirements.txt)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

课程每章含:**Pre-lecture quiz**(测验)、**README 概念讲解**、**Notebook 动手实验**、**assignment**(作业)。

## 实践 / 应用:学习路径建议

!!! tip "按目标选择路径**
    1. **补 AI 基础**(想系统入门):按 1→2→3→5 顺序学(Intro → Symbolic → NN → NLP),配合站内 01-ai-basics 文章;
    2. **想理解 Agent 底层**:重点学 2-Symbolic(知识表示/推理——经典 Agent 基础)+ 6-Other/23 多智能体 + 5-NLP(Transformer);
    3. **做视觉应用**:4-ComputerVision 全章(CNN/迁移学习/目标检测/分割);
    4. **关注负责任 AI**:7-Ethics(公平/透明/问责——与站内 [企业 AI 战略](../06-enterprise/ai-org-transformation/ai-value-models-openai.md) 的治理呼应)。

## 总结

- **课程定位**:微软开源 AI 基础课程(20+ 章),概念 + Notebook 动手,多语言;
- **章节地图**:Intro → Symbolic(知识表示/推理)→ NN → CV → NLP → 其他(遗传/RL/多智能体)→ 伦理 → 多模态扩展;
- **与站内关系**:01-ai-basics 是站内速查,本课程是系统学习路径;Agent 相关内容在 Symbolic 与多智能体系统章(已另文整理);
- **一句话**:如果你想补 AI 基础或理解经典 Agent(知识表示/推理/多智能体)的理论源头,这套课程是最好的系统教材之一。

## 延伸阅读

- 仓库:https://github.com/microsoft/AI-For-Beginners;配套:Machine Learning for Beginners(https://github.com/microsoft/ml-for-beginners);多智能体章全文存档于 `references/ai-for-beginners/lessons/6-Other/23-MultiagentSystems/README.md`
- 站内:[01-ai-basics](../01-ai-basics/index.md)(基础速查)、[经典多智能体系统](../03-agents/multi-agent-systems-classical.md)(23 章整理)、[多 Agent 协作](../03-agents/multi-agent.md)
