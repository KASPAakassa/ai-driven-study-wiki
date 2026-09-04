# 原始资料:论文 Memory for Large Language Models(核心存档)

> 论文:《Memory for Large Language Models》;作者:Sining Zhoubian(清华)、Dan Zhang(NUS)、Evgeny Kharlamov(Bosch AI)、Jie Tang(清华)
> arXiv:2607.25380v1 [cs.CL],2026-07-28,License: CC BY 4.0
> 链接:https://arxiv.org/abs/2607.25380;HTML:https://arxiv.org/html/2607.25380v1

## Abstract(原文摘要)
Memory has evolved into a foundational architectural dimension in LLMs, shifting from an implicit byproduct of computation to a spectrum of explicit, controllable mechanisms... In this survey, we present a systematic, architecture-centric taxonomy of memory in LLMs. Our framework characterizes memory along three orthogonal axes: representation (implicit versus explicit), update dynamics (offline versus online), and persistence (short-term versus long-term). We further formalize the granular mechanisms dictating memory writing, routing, state transitions, and consolidation. This unified perspective elucidates the conceptual boundaries between computation-coupled and independently addressable memory...

## 三正交轴分类法
- Representation:Implicit(计算耦合:KV Cache/Hidden States)vs Explicit(独立接口:D Data store/Parameter modules)
- Update Dynamics:Offline(训练期:Pre-training/MoE)vs Online(推理期:TTT/Recurrent States)
- Persistence:Short-Term(临时:Attention Cache)vs Long-Term(跨上下文/会话:Titans/Engram)

## 隐式记忆(§III)
- III-A Attention as Implicit Memory:内容寻址瞬态记忆、记忆容量与上下文长度、流式/窗口化注意(StreamingLLM)、注意力作为记忆计算的替代视角
- III-B Sparse/Selective/Structured:稀疏作为记忆访问控制、内容路由稀疏注意(MoBA/NSA)、选择性注意与记忆准入、局部-全局结构与记忆保留(BigBird)
- III-C Recurrent Sequence Memory:RNN、线性注意与结构化状态模型(Mamba-3/RWKV-7/Gated DeltaNet-2)、状态编辑投影过滤、表达性 Delta 与双线性更新、层次状态容量、混合循环-注意变体、训练诱导信念状态
- III-D Limitations:容量有界难控、缺乏可适应读写语义、跨上下文持久有限

## 显式记忆(§IV)
- IV-A Parameterized External Memory:快速权重与元学习记忆、测试时参数更新(Titans/TTT-E2E/MEMORYLLM/LM2/In-Place TTT)、快速权重复用与选择性写入、专用可写模块
- IV-B Lookup-based/Retrieval:kNN-LM/PlugLM/Engram/ExplicitLM/可编辑数据存储/哈希查找槽;FF 层作为查找记忆;与 RAG 的区别(模型级检索 vs RAG)
- IV-C MoE 作为条件参数记忆:Switch Transformer/Mixtral/DeepSeek-MoE
- IV-D Multi-Timescale 更新:测试时适应=短时间尺度记忆、嵌套/层次更新调度(Nested Learning Hope)、慢-快参数分解、稳定性-可塑性权衡
- IV-E 风险:容量增长、干扰与记忆漂移、优化收敛、跨情节一致性、架构复杂度、参数稳定性几何约束

## 模型级架构(§V)
- V-A 混合架构:Jamba/Kimi Linear/OLMo Hybrid/AMOR/HAM/固定与自适应路由互补记忆
- V-B 效率管理:KV 缓存压缩量化、PagedAttention、工作记忆巩固、滑窗 vs 稀疏全局
- V-C 评测:RULER/LongBench/∞Bench/L-Eval/SCROLLS、结构化依赖推理、遗忘/干扰/稳定性、效率-性能权衡、隐式 vs 显式、统一记忆指标

## 开放挑战(§VI)
统一记忆理论、终身参数记忆、鲁棒可解释更新规则、自适应记忆分配控制、硬件-算法协同、多维度评测框架

## 与相关综述的区别(§II-D)
定位:模型级记忆(架构内或推理期动力学),排除 agent 级/prompt 级记忆(如 MemGPT/RAG 等外部系统)——与站内 agent-memory-systems(工程/agent 级)互补
