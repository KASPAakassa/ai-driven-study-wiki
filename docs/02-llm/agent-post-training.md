# 模型后训练:预训练、SFT、RL 三阶段与"为 Agent 而训练"

> **一句话摘要**:优化 Agent 的"大脑"(LLM)靠后训练——预训练打地基、SFT 教格式与协议、RL 提升泛化。本文基于《深入理解 AI Agent》第 7 章,讲清三阶段分工、"SFT 记忆 vs RL 泛化"的真相、以及"数据和环境比算法更重要"这条工业界最值钱的经验。
>
> **来源**:《深入理解 AI Agent:设计原理与工程实践》第 7 章(李博杰,https://github.com/bojieli/ai-agent-book),全文存档于 `references/ai-agent-book/book/chapter7.md`

## 概念:能力开发的三个阶段

现代模型的能力开发分三阶段,本质都是"调整输出的概率分布",区别只在"想要什么"和"用什么信号定义想要":

| 阶段 | 用什么数据 | 优化目标 | 学到什么 | 典型代价 |
| --- | --- | --- | --- | --- |
| **预训练** | 海量原始互联网文本 | 预测下一个词(NTP) | 语言规律、世界知识、基本推理 | 极高(数千万美元) |
| **SFT** | 几千~几万条"输入-输出"示范对 | 预测下一个词(只在回答上算损失) | 指令遵循、输出格式、风格、流程协议 | 低(几小时~几天) |
| **RL** | 任务、环境 + 奖励信号 | 最大化期望奖励 | 可迁移的决策策略、探索出的新解法 | 高(常是 SFT 的几十~上百倍) |

!!! note "直觉类比"
    预训练是"读万卷书"(积累知识),SFT 是"老师手把手教标准解法"(模仿示范),RL 是"自己下场做题、根据对错反复打磨"(试错提升)。

## 原理 1:SFT 的本质——换了数据的"预测下一个词"

**SFT 在数学上和预训练是同一个任务**,差别只有两点:

1. **数据不同**:预训练用原始互联网文本,SFT 用人工准备的"提问→理想回答"示范对;
2. **损失屏蔽(loss masking)**:只对"回答"部分回传梯度,不学"提问"。

因此 SFT 用**极高的样本效率**把一套稳定的"输入→输出"映射与协议固化进参数——它固化的是**协议性知识**(该怎么说、怎么做),而非**事实性知识**(知道什么,后者靠预训练或 RAG)。

!!! tip "工程默认项:LoRA"
    全参微调显存要求高,**LoRA**(低秩适配)只挂一个小"补丁"(参数量仅 1%-5%)却能接近全参效果,且对基座扰动小。实践要点:必须应用到所有主要权重矩阵(尤其 MLP 层);最优学习率约是全参微调的 **10 倍**;SFT 用中高 rank(64-256),RL 用小 rank(8-32);一台推理服务器可同时加载多个 adapter 做多租户。

## 原理 2:SFT vs RL——"SFT 记忆,RL 泛化"

| 维度 | SFT | RL |
| --- | --- | --- |
| 优化目标 | 最大化标注答案概率(极大似然) | 最大化期望奖励 |
| 训练信号 | 标注回答的逐 token 监督 | 策略生成的轨迹 + 标量奖励 |
| 样本效率 | 高(几千条见效) | 低(几十~上百倍) |
| 稳定性 | 高、收敛快 | 低、易震荡 |
| 分布漂移下 | 有限示范下易过拟合(记忆) | 本章实验中迁移更好(泛化) |
| 最适合 | 固化格式/风格/流程,环境稳定 | 需泛化到新场景、探索最优策略 |

概率分布视角还有一组重要差别:**SFT 是 mass-covering(覆盖式)**——尽量覆盖训练数据中的多个合理回答模式;**RL 是 mode-seeking(寻峰)**——把概率集中到少数高奖励峰上。

!!! warning "重要边界"
    "SFT 记忆、RL 泛化"是**受控实验倾向,不是普遍规律**:数据足够多样、正则化得当时 SFT 也能泛化;奖励或环境有偏时 RL 也会过拟合。

## 原理 3:何时先 SFT 后 RL(先形后神)

RL 要能算奖励,首先得能**解析模型的输出**——如果模型吐出一团格式混乱的文本,连"成功失败"都判断不了。所以在**较小基础模型 + 严格结构化输出**的设定下:

- **SFT 先立"形"**(格式、结构稳定、可解析),**RL 再求"神"**(策略、泛化)——这是业界稳健的"先 SFT 后 RL"两阶段范式;
- 但基础模型足够强时可跳过 SFT 直接 RL(DeepSeek-R1-Zero 证明了强基模能自行涌现反思与长链思考),代价是输出可读性差,所以 R1 最终仍加回"冷启动 SFT"把"形"立稳。

## 原理 4:数据和环境比算法更重要(工业界最反直觉的经验)

- 现成的 RL 算法(PPO、GRPO 等)会用就行,**真正拉开差距的是仿真环境的保真度和训练数据的质量**;
- 造不出真实环境时,用模型模拟环境(合成工具返回值、仿真环境动态)可行,但**模拟器的偏差就是训练的天花板**;
- 很多场景下只要 SFT 数据质量到位,甚至不需要做 RL;
- 训练数据的**任务分布本身**也可以成为优化对象(筛选答案之外,还能优化任务构成)。

## 原理 5:当前 RL 的主要瓶颈——样本效率

两条最有希望的方向(共同点:把环境和数据里"被纯结果奖励浪费掉的信息"重新变成可学习信号):

- **On-Policy Distillation**:把一条 rollout 的终点标量扩展为逐 token 监督;
- **RLVP(Penalize the Path, Reward the Outcome)**:把被浪费的环境反馈变成可学习信号(李博杰 & Noah Shi,2026)。

## 代码 / 实现:如何把这些用到自己的项目

后训练不是每人都要做的(大多数应用开发者用现成模型),但决策框架值得掌握:

```python
def choose_post_training(path, task_requirements):
    """根据任务特征决定后训练路径(概念性决策框架)"""
    decisions = []
    structured = task_requirements.get("structured_output", False)   # 严格 JSON/工具调用?
    model_size = task_requirements.get("model_size", "small")        # 基模强不强?
    new_scenario = task_requirements.get("generalize", False)        # 需要分布外泛化?

    if structured and model_size == "small":
        decisions.append("先 SFT:稳定输出格式(立'形'),使奖励可解析")
        if new_scenario:
            decisions.append("再 RL:在 SFT 基础上探索策略、改善泛化(求'神')")
    elif new_scenario:
        decisions.append("强基模可直接 RL(如 R1-Zero 路线),必要时补冷启动 SFT")
    else:
        decisions.append("SFT 数据质量到位时,可能根本不需要 RL")

    # 无论哪条路:数据和环境质量 > 算法选择
    decisions.append("核心:仿真环境保真度 + 训练数据质量决定上限;LoRA 是工程默认项")
    return decisions

print(choose_post_training("tool-calling-agent", {
    "structured_output": True, "model_size": "small", "generalize": True}))
```

**运行结果**:输出典型决策路径——"先 SFT 稳定格式 → 再 RL 探索泛化 → 同时保证数据/环境质量"。真实项目里,何时靠 prompt/Skill 解决(便宜)、何时值得微调,是 [Harness 工程](../03-agents/ai-infra-layering.md) 的关键取舍。

## 实践 / 应用:Agent 应用开发者的行动指南

1. **先问要不要后训练**:能靠 prompt/RAG/Harness 解决的,别微调(成本与维护代价完全不同);
2. **SFT 是默认第一步**:几乎所有部署模型都会经过;数据质量到位可能不需要 RL;
3. **做 RL 前先确认输出可解析**:格式不稳定时奖励是噪声,训练必败;
4. **用评估环境和仿真喂后训练**:第六章的评估体系是第七章的练习场与目标函数(见 [Agent 评估](../03-agents/agent-evaluation.md));
5. **从 bad case 到后训练**:线上 bad case 是训练数据的富矿(见 [持续进化](../03-agents/agent-continuous-evolution.md))。

## 总结

- 三阶段分工:**预训练**打知识地基、**SFT** 固化格式与协议、**RL** 提升策略与泛化;"先形后神"是稳健范式;
- "SFT 记忆、RL 泛化"是实验倾向而非规律;**数据与环境比算法更重要**是工业界最值钱的经验;
- RL 当前瓶颈是**样本效率**(On-Policy Distillation、RLVP 是有希望的方向);
- LoRA 是所有后训练的工程默认项(必须覆盖 MLP 层、学习率约为全参的 10 倍)。

## 延伸阅读

- 站内:[预训练与规模定律](../02-llm/pretraining.md)、[微调](../02-llm/fine-tuning.md)、[对齐:RLHF 与 DPO](../02-llm/rlhf-alignment.md)、[Agent 评估](../03-agents/agent-evaluation.md)
- 书内:第 7 章全文 `references/ai-agent-book/book/chapter7.md`;引用论文:SFT Memorizes, RL Generalizes(arXiv:2501.17161)、On-Policy Distillation(Thinking Machines,2025)、RLVP(arXiv:2607.07435)
- 外部:仓库 https://github.com/bojieli/ai-agent-book
