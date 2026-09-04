# LLM 记忆综述:三轴分类法与模型级记忆架构(论文解析)

> **一句话摘要**:记忆已演化为 LLM 的基础架构维度——从计算的隐式副产物转向一系列显式、可控的机制。清华/新加坡国立/Bosch 的综述(arXiv:2607.25380)提出**架构中心的三正交轴分类法**:表示(隐式 vs 显式)、更新动力学(离线 vs 在线)、持久性(短期 vs 长期),并统一了分散的机制——瞬态注意力、循环状态动力学、测试时参数更新、可扩展查找存储、MoE 条件参数、多时间尺度更新。注意:本文聚焦**模型级记忆**(架构内/推理期),排除 agent 级/prompt 级记忆(如 MemGPT/RAG)——与站内 [Agent 记忆系统](../03-agents/agent-memory-systems.md) 互补。
>
> **来源**:Sining Zhoubian(清华)、Dan Zhang(NUS)、Evgeny Kharlamov(Bosch AI)、Jie Tang(清华)《Memory for Large Language Models》,arXiv:2607.25380v1 [cs.CL],2026-07-28,CC BY 4.0;https://arxiv.org/abs/2607.25380;原始资料存档于 `docs/inbox/llm-memory-survey-source.md`

## 概念:记忆从副产物到架构维度

!!! tip "核心转变"
    传统 Transformer 中记忆主要是**隐式**的:注意力提供受上下文窗口约束的内容寻址工作记忆,但计算/存储开销随序列长度**二次方增长**,且记忆短暂、耦合在前向计算图中。近年一个明显的架构转向:**显式、持久的记忆机制**在推理之外自适应演化——Titans、端到端测试时训练(TTT)支持部署期动态参数更新;Engram 等查找架构把记忆存储与密集计算解耦;嵌套/多时间尺度更新策略模糊了训练与推理的边界;MoE 按输入上下文选择性激活参数子集,构成结构化条件记忆。**记忆正在成为主要、显式的架构设计维度,而非规模化的副产物。**

本综述的动机:**文献缺乏统一视角**——注意力缓存、循环状态、测试时适应、检索模块、条件参数路由被孤立研究,尽管它们回答同构问题:存什么、何时怎么更新、如何与前向计算交互、保留多久、存储粒度是什么。

## 原理:三轴分类法与两大记忆体系

### 1. 三正交轴分类法(统一框架)

| 轴 | 极 | 含义 | 例子 |
| --- | --- | --- | --- |
| **表示 Representation** | **Implicit(隐式)** | 计算耦合,无独立读写接口 | KV Cache、Hidden States |
| | **Explicit(显式)** | 独立可寻址接口 | Datastore、Parameter modules |
| **更新 Update** | **Offline(离线)** | 仅训练期更新 | 预训练、MoE |
| | **Online(在线)** | 推理期更新 | TTT、Recurrent States |
| **持久 Persistence** | **Short-Term(短期)** | 瞬态,受上下文窗口约束 | Attention Cache |
| | **Long-Term(长期)** | 跨上下文/会话持久 | Titans、Engram |

!!! note "定位声明(与相关综述的区别)"
    本文聚焦**模型级记忆**(架构内实例化或推理期动力学);**排除 agent 级/prompt 级记忆系统**(依赖外部存储、prompt 注入,如 MemGPT/RAG 类)。论文指出这与其他"LLM agent 记忆综述"(站内 [Agent 记忆系统](../03-agents/agent-memory-systems.md) 即此类)正交互补。

### 2. 隐式记忆(§III):计算耦合的三种形态

| 形态 | 机制 | 代表 |
| --- | --- | --- |
| **Attention 作为隐式记忆** | 内容寻址瞬态记忆;容量受上下文长度约束;流式/窗口化扩展 | Transformer(KV Cache)、StreamingLLM、Sliding-Window、HyperMLP |
| **稀疏/选择性/结构化** | 稀疏作为记忆访问控制;内容路由稀疏注意;选择性注意与记忆准入;局部-全局结构 | MoBA、NSA、Selective Attention、BigBird |
| **循环序列记忆** | 线性注意与结构化状态模型;状态编辑/投影/过滤;表达性 Delta 与双线性更新;层次状态容量;训练诱导信念状态 | Mamba-3、RWKV-7、Gated DeltaNet-2、Log-Linear Attention、Kalman Linear Attention |

**隐式记忆的局限(§III-D)**:①容量有界且难以控制;②缺乏可适应的读写语义(不能显式"写入/删除");③跨上下文持久有限——这些局限直接推动显式记忆的兴起。

### 3. 显式记忆(§IV):可寻址、可适应的存储

| 类别 | 机制 | 代表 |
| --- | --- | --- |
| **参数化外部记忆** | 快速权重/元学习记忆;测试时参数更新;快速权重复用与选择性写入;专用可写模块 | Titans、TTT-E2E、MEMORYLLM、LM2、In-Place TTT |
| **查找/检索记忆** | 最近邻与数据存储增强;可编辑记忆库;FF 层作为查找记忆;**与 RAG 的区别:模型级检索 vs 外部检索** | kNN-LM、PlugLM、Engram、ExplicitLM |
| **MoE 条件参数记忆** | 按输入激活参数子集 = 结构化条件记忆 | Switch Transformer、Mixtral、DeepSeek-MoE |
| **多时间尺度更新** | 测试时适应=短时间尺度记忆;嵌套/层次更新调度;慢-快参数分解 | Nested Learning(Hope)、Slow-Fast Modules、Continual Memory |

!!! tip "显式记忆的更新规则视角"
    论文形式化了细粒度机制:记忆**写入(writing)、路由(routing)、状态转换(state transitions)、巩固(consolidation)**——把"测试时适应"统一看作**短时间尺度的在线记忆更新**,把"层次更新调度"看作多尺度巩固。

**显式记忆的风险(§IV-E)**:容量增长与记忆扩展、干扰与记忆漂移、优化与收敛挑战、跨情节一致性、架构复杂性与可解释性、参数稳定性的几何约束。

## 代码 / 实现:三轴分类器(纯 Python)

把"按三轴给记忆机制打标签"落成可运行演示(判断一个机制属于哪个象限):

```python
# —— 三轴分类器:给定机制特征,输出三轴标签 ——
def classify_memory(is_compute_coupled: bool, updates_at_inference: bool,
                    persists_across_sessions: bool) -> dict:
    return {
        "representation": "Implicit(计算耦合)" if is_compute_coupled else "Explicit(独立可寻址)",
        "update":         "Online(推理期更新)" if updates_at_inference else "Offline(训练期更新)",
        "persistence":    "Long-Term(跨会话)" if persists_across_sessions else "Short-Term(窗口内)",
    }

cases = [
    ("KV Cache(Transformer 注意力)",   True,  False, False),
    ("Titans(测试时参数更新)",          False, True,  True),
    ("Mamba-3(循环状态)",               True,  True,  False),
    ("kNN-LM(查找存储)",                False, False, True),
]
for name, coupled, online, persist in cases:
    c = classify_memory(coupled, online, persist)
    print(f"  {name:26} → {c['representation']} | {c['update']} | {c['persistence']}")

assert classify_memory(True, False, False)["representation"].startswith("Implicit")
assert classify_memory(False, True, True)["update"].startswith("Online")
assert classify_memory(False, False, True)["persistence"].startswith("Long")
print("代码验证通过 ✔")
```

## 实践 / 应用:模型级架构、效率、评测与开放挑战

### 1. 混合记忆架构(§V-A):现实模型的选择

- **交错的注意力与结构化状态层**:Jamba、Kimi Linear、OLMo Hybrid——局部用注意力、全局用状态;
- **自适应混合记忆路由**:AMOR(自适应熵门)、HAM(混合联想记忆)、固定与自适应路由互补记忆;
- **隐式记忆 + 显式存储**:Titans(神经网络记忆模块 + 注意力)。

### 2. 记忆管理与效率(§V-B)

KV Cache 压缩与量化、**PagedAttention(内存虚拟化)**、工作记忆巩固、滑窗 vs 稀疏全局注意的架构权衡——这些是长上下文模型落地的系统级关键。

### 3. 评测(§V-C):不能只看 Recall

- **长上下文检索与回忆**:RULER、LongBench、∞Bench、L-Eval、SCROLLS;
- **结构化依赖与推理测试**:超越简单检索;
- **遗忘/干扰/稳定性**:记忆系统特有的评测维度;
- **效率-性能权衡** + **隐式 vs 显式对比** + **统一记忆指标**(开放问题)。

### 4. 开放挑战(§VI):六大方向

①统一记忆理论;②终身/持续参数记忆;③鲁棒且可解释的更新规则;④自适应记忆分配与控制;⑤硬件-算法协同设计(可扩展记忆);⑥多维度评测框架。

### 与站内其他文章的呼应

- [Agent 记忆系统](../03-agents/agent-memory-systems.md):那篇是 **agent 级/prompt 级记忆**(工程视角),本文是 **模型级记忆**(架构视角)——互补关系(综述 §II-D 明确区分);
- [TencentDB Agent Memory](../08-harness/agent-memory-plugin.md):外部记忆存储 = 本文"显式查找记忆"在 Harness 层的实现;
- [自进化 Agent 综述](self-evolving-agents-survey.md):"存技能/训技能/内化参数"与本文的隐式/显式/多时间尺度记忆直接呼应(如 SKILL0 把 Skill 内化进参数 = 在线参数记忆);
- [Context Engineering](../03-agents/context-engineering.md):上下文压缩(L1-L4)对应本文"注意力记忆容量受限"的工程化缓解。

## 总结

- **三轴分类法**:表示(隐式 vs 显式)× 更新(离线 vs 在线)× 持久(短期 vs 长期)——统一了注意力缓存/循环状态/TTT/检索/MoE/多时间尺度等分散机制;
- **两大体系**:隐式记忆(注意力/稀疏/循环,计算耦合、读写不可控)+ 显式记忆(参数化/查找/MoE/多时间尺度,可寻址可适应);
- **模型级定位**:聚焦架构内记忆,与 agent 级/prompt 级记忆(站内工程文章)互补;
- **落地要点**:混合架构是现实选择;效率看 KV 缓存/PagedAttention;评测要多维度(Recall 只是其一);
- **一句话**:LLM 记忆正在从"计算的副产物"走向"显式的架构维度"——三轴分类法是理解这场转变的统一地图。

## 延伸阅读

- 论文:https://arxiv.org/abs/2607.25380;HTML:https://arxiv.org/html/2607.25380v1;原始资料存档于 `docs/inbox/llm-memory-survey-source.md`
- 站内学术章节:[推理时验证(DeepVerifier)](inference-time-verification.md)、[自进化 Agent 综述](self-evolving-agents-survey.md)、[Harness Handbook](harness-handbook.md)(09 四篇并列);[Agent 记忆系统](../03-agents/agent-memory-systems.md)、[TencentDB Agent Memory](../08-harness/agent-memory-plugin.md)、[Context Engineering](../03-agents/context-engineering.md)
