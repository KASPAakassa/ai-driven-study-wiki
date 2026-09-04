# 🏫 Agent 前沿学术

> 收录 Agent 领域的**前沿学术内容**:论文解析与解读、研究方法论、开源数据集与评测基准、领域进展综述。偏"学术/研究"视角,与 03-agents(工程/开发)互补。

## 本章节文章

- [推理时验证(DeepVerifier):Agent"自我进化"的新范式](inference-time-verification.md) — 腾讯AI Lab+港中文:验证不对称性、DRA 失败分类学、三模块框架、4K 反思数据集(论文解析)
- [Critique of Agent Model 论文解析](agent-model-critique-paper.md) — 邢波等(arXiv:2606.23991):五维度批判、agentic vs agentive 区分、GIC 架构(六组件+四定理)、分层透明安全论证(基础概念版见 03-agents)
- [现代智能体自我改进综述:从模型更新到脚手架演化](self-improving-agents-survey.md) — 吉林大学+KAUST+Schmidhuber(arXiv:2607.13104,97 页):统一形式化(Agent=基础模型+脚手架)、FM 改进 vs Scaffolding 改进两路径、六类应用、评测范式与开放问题
- [Self-Harness:让 Agent 学会改造自己的"操作系统"](self-harness-paper.md) — arXiv:2606.09498:不改权重,让固定模型按失败轨迹提议小步 harness 修改,回归门(held-in+held-out)决定升级;Terminal-Bench-2.0 三模型全涨(最大 +138%)
- [自进化 Agent 综述:三大技术路线与 14 篇论文全景](self-evolving-agents-survey.md) — 腾讯PCG:经验存储型/RL训练型/0数据自学型,论文全提炼+概念扩展(GRPO/课程学习/信用分配)+研究空白与工程启示
- [Harness Handbook:行为定位与可演化 Agent 系统](harness-handbook.md) — 腾讯+高校(arXiv:2607.13285):三层文档树+状态寄存器+BGPD,改代码前先找到完整行为(论文解析+知识库汇总)
- [LLM 记忆综述:三轴分类法](llm-memory-survey.md) — 清华+NUS+Bosch(arXiv:2607.25380):表示×更新×持久三轴统一隐式/显式记忆、混合架构、效率与多维度评测(模型级记忆,与工程视角互补)
- [Cordis《Spatiotemporal Composability》论文深度综述](spatiotemporal-composability-paper-survey.md) — 插件化范式形式化地基:可逆 effect(时间可组合性)+ 反应式 coeffect(空间可组合性)+ 动态组合演算元理论;DeepSeek 为什么这样做(选 Cordis/预览开源/可观测性)、设计好处、插件化是否 AGI 最终路径、对字节自研 AGI 框架 8 条启发(综合知乎/V2EX/linux.do 社区评论)
- [LongHorizon-Harness:长程 Agent 任务状态管理新思路](longhorizon-harness-paper.md) — AMAP-ML(arXiv:2608.01964):MEA(Manage-Execute-Audit)状态机让任务状态脱离上下文,执行轨迹/任务状态/完成证据三分离,独立审计 + AgentAdapter 接 Claude Code/Codex;WeaveBench 51.8%→80.7%(开源 `lh-harness`)

## 待整理 / 规划

<!-- 从 inbox 收件箱转入本主题的素材,梳理前先登记在这里 -->

## 收录原则

- 优先收录**有论文出处、有开源代码/数据**的前沿工作;
- 每篇注明:论文标题、作者、arXiv/会议、开源资源;
- 与 03-agents(设计/工程视角)文章互相链接,同一工作从"学术方法"与"工程落地"两个角度沉淀。

## 学习指引

- 适合:想跟进 Agent 研究前沿、复现论文、做 Agent 学术工作的读者;
- 论文方法 → 看本文档;工程落地/设计启示 → 看 [03-agents](../03-agents/index.md) 对应文章。
