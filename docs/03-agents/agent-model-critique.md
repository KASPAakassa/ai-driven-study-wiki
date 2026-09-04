# 什么是真正的 Agent?——Agentic 与 Agentive 的分界(邢波《Critique of Agent Model》)

> **一句话摘要**:市场上到处是"coding agent""AI co-scientist",但邢波(Eric Xing)等人在《Critique of Agent Model》中提出一个尖锐问题:**自动化在哪里结束,agency(机构性/自主性)在哪里开始?** 核心论断:当前 AI 系统"largely agentic but not yet agentive"——能力驻留在外部工程脚手架里,而非系统内部。真正的 agency 需要 goal/identity/decision-making/self-regulation/learning 五维结构**内化于系统本身**。本文提炼这一基础概念框架,作为理解 Agent 本质的起点。
>
> **来源**:论文《Critique of Agent Model》(arXiv:2606.23991,2026-06-22,邢波/Mingkai Deng/Jinyu Hou,MBZUAI+CMU);原始资料存档于 `docs/inbox/agent-model-critique-source.md`;学术深度解析见 [09-agent-research 专文](../09-agent-research/agent-model-critique-paper.md)

## 概念:为什么要问"什么是 Agent"

**两个矛盾现象**驱动这个问题:

- 一方面,LLM 系统被市场化为 "coding agents""AI co-scientists" 等"agentic"工具,承诺提升生产力;
- 另一方面,存在"AI 逃离人类控制、具备破坏性机器 agency"的臆想式担忧。

因此必须澄清:**自动化在哪里结束、agency 在哪里开始**——既为构建有能力系统,也为理解该怕什么、不该怕什么。

**哲学与科幻的双重坐标**:

- **Descartes"我思故我在"**:把 agency 锚定于**独立思想**;
- **Blade Runner 的 replicants**:会困惑、犯错、受苦,质疑自我,走出被指派角色迈向不确定与自由。

作者由此论断:**agency ≠ operational excellence(操作卓越)**——而是目标导向行动、自我发展、自我反思、参与复杂社会环境,乃至自由意志、道德与自我实现驱动的能力。这构成了衡量当代系统的标尺。

## 原理:Agentic vs Agentive——最核心的区分

!!! tip "一句话区分"
    - **Agentic systems(能动系统)**:通过外部编排的工具、工作流、程序化控制环完成任务,**能力主要驻留在围绕推理模型的工程中**;
    - **Agentive systems(自主系统)**:能力**内生(endogenously)**——维持长期目标、演化自我身份、内部模拟未来、自我调节推理、自主学习,以及社会互动能力(如生物 agent)。

**判据不是结构是否存在,而是这些结构如何起源**:由外部工程流水线规定,还是由内部 configurator 自主调整、修订与组织。

> **真正的 agency 要求这些结构内化于系统本身,而非通过外部脚手架拼装。**

**为什么重要**:

1. 划出了"被限制在预设生产流水线中的系统"与"能在开放世界以真正自主性运作的系统"之间的边界;
2. 反驳了"枚举一切行为(工具/提示/技能)即可扩展到生物级多样性与适应性"的想象——当前 AI 系统更适合被理解为**复杂软件流水线而非真正自主 agent**。

## 原理:五维度分析——结构如何被"外化"与应如何"内化"

作者沿五个维度分析当前 agent 架构,每维都是"外部规定 → 内部维护"的谱系:

| 维度 | 当前系统的做法(外化) | 真正 agent 应该做的(内化) |
| --- | --- | --- |
| **Goal 目标** | 每步由用户供给短期目标,交互结束即消失("拾起瓶子"可行,"一年酿酒"不可行) | 一次性接受长期目标,用学习的**层次化分解模块 δ** 分解为可修订的子目标序列 |
| **Identity 身份** | 用 system prompt、配置文件、MCP/Skills 外部固定身份,环境变化时无法适应 | 身份内生演化,采用**快慢双时间尺度更新**(慢:改参数;快:修订紧凑自模型,免重训) |
| **Decision-Making 决策** | 端到端黑盒策略,寄望 CoT "涌现"规划 | **模拟推理(System II)**:用独立训练的世界模型预测动作后果、critic 评估选优(CoT 是叙述合理性,不是对真实动力学的接地预测) |
| **Self-Regulation 自我调节** | 要么期待无约束 RL 涌现推理模式(不可控),要么固定规划-执行流水线/始终在线 MPC(过度/不足规划) | 学习的 **configurator κ(System III)** 输出调节变量(直接行动/延续计划/新建计划/修订目标/进入学习),像"人类情绪"一样按情境配置行为模式 |
| **Learning 学习** | 训练是"部署前终止的有限阶段、由人类工程师调度" | **模拟优先、现实作验证**;学习预测(WM)与学习行动(AM)分离;何时学、用什么数据、何时停由 configurator 治理 |

**总括(关键主线)**:所有批判的共同主线是——当前系统把五维结构**外化成人类工程脚手架**;而每一个建设性替代都依赖**内部模拟现实的能力**。

> **世界模型不是众多组件之一,而是让其它维度成为可能的"连接基板"**——agent 与 WM 的关系类比飞行员与飞行模拟器。

## 实践 / 应用:这套框架对 Agent 开发者的意义

**判断一个"Agent"是 agentic 还是 agentive**:

- 它的目标是一次性短期还是可演化的长期?
- 它的身份是外部 prompt 固定,还是能随交互内生演化?
- 它的"规划"是真模拟后果,还是 CoT 叙述?
- 它的自我调节是固定流水线,还是学习到的 configurator?
- 它的学习止于部署,还是持续?

**对当前工程实践的启示**:

1. 今天的主流 Agent(Claude Code、各类 SDK)大多是 **agentic**——能力在脚手架(工具/提示/工作流)里,这没有错,它们是"复杂软件流水线";
2. 向 **agentive** 演进的关键投资:内部世界模型(模拟未来)、层次化目标分解、内生身份、学习的自我调节;
3. 理解这个区分,能避免两个误区:①把"工具多、提示好"等同于"真自主";②对当前系统过度恐惧(它们远未具备 agentive 自主性)。

**与站内文章的衔接**:这个"agentic/agentive"框架可作为 [Agent 入门](agent-intro.md) 的概念深化,与 [Agent 架构全景](agent-architecture-panorama.md)(七种架构档位)互补——那篇讲工程档位,这篇讲本质分界。

## 总结

- **核心问题**:自动化在哪里结束、agency 在哪里开始?既为构建系统,也为理解该怕什么;
- **最核心区分**:agentic(能力在外部脚手架)vs agentive(能力内生,包括社会互动);真正的 agency 要求五维结构内化;
- **五维度**:goal(长期目标+层次分解)、identity(内生演化+快慢双尺度)、decision-making(模拟推理而非 CoT 叙述)、self-regulation(学习到的 configurator)、learning(模拟优先+持续);
- **关键论断**:当前 AI 系统"largely agentic but not yet agentive",是复杂软件流水线而非真正自主 agent;
- **世界模型是连接基板**:内部模拟现实的能力让其它维度成为可能;
- **下一步**:深入论文的 GIC 架构与安全论证见 [09 学术专文](../09-agent-research/agent-model-critique-paper.md)。

## 延伸阅读

- 论文:https://arxiv.org/abs/2606.23991
- 站内:[Agent 入门](agent-intro.md)(基础)、[Agent 架构全景](agent-architecture-panorama.md)(工程档位)、[Agent 系统设计的 5 个决策](agent-system-5-decisions.md)(工程决策)、[09 学术专文](../09-agent-research/agent-model-critique-paper.md)(GIC 架构+定理+安全)
