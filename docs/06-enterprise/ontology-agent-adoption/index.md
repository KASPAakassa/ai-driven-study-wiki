# 🧬 Ontology 与 Agent 企业落地

> 记录本体论(Ontology)如何与 Agent 结合,支撑企业级落地:统一术语与语义、知识图谱、语义层/元数据层、Agent 的规划与推理约束、治理与合规。

## 本章节文章

- [Ontology as Code:像代码一样管理本体](ontology-as-code.md) — 继承/引用/版本/行为四能力、对账管线、agent 时代的治理落点(整理自 OntoEffect 系列)
- [Ontology 的四大技术:RDF、OWL、SPARQL、SHACL](ontology-four-technologies.md) — 图数据/语义/查询/校验四技术分工与协同工作流(整理自 AI神经)
- [Palantir 操作型本体论:从范式跃迁到工程实现](palantir-operational-ontology.md) — 三重困境与四十年演化、四维集成(Data/Logic/Action/Security)、五大构建块与五微服务(深度总结《Palantir 本体论》①-③)
- [OAG 与 Ontology 驱动的企业 Agent](palantir-oag-agent.md) — RAG 之后的下一个范式:五层 Agent 架构、动词一等公民、与主流框架四差距、五类业务结构
- [Palantir Ontology 的构建、案例与边界](palantir-cases-and-reflection.md) — 构建三段式、实体解析、bp/通用磨坊/温蒂/空客/坦帕五案例、四大局限与工业物理本体批判
- [Palantir Foundry:5 步把数据变对象](palantir-foundry-5-steps.md) — 安全接入→管线转换→质量血缘→Ontology 建模→应用行动,供应链走查(对象→Function→Scenario→Action→Decision Lineage)
- [Palantir 公司全景:企业级操作系统与 Ontology 内核](palantir-company-overview.md) — 公司定位、决策四组件(Data/Logic/Action/Security)、四产品关系、官方文档深度解读(英文已翻译)、对国内企业启示
- [企业业务 Agent 落地:从听懂到做对的四步路径](enterprise-agent-business-rollout.md) — 意图级联与四类出口、RAG 边界与五类真相源、四步渐进上线(回放/影子/低风险/扩权)、分层指标
- [Agent 落地方法论:微智能体与 SOP Agent](agent-landing-micro-agents.md) — 80% 陷阱、微智能体嵌入确定性工作流、成功率数学(0.95^10≈0.6)、四条实践经验(70% 代码包围 30% LLM)
- [企业 Agent 体系设计:四要素与三层体系](enterprise-agent-system-design.md) — Agent=LLM+上下文+工具+Harness;用户级 vs 服务级工具;生产/服务/消费三层+配置驱动 Agent 工厂;演进四阶段
- [企业 Agent 上生产的四道防线](enterprise-agent-production-deployment.md) — 纵深安全(容器隔离/代理模式/最小权限)、成本四道防线、可观测指标、容错与 SLO
- [高德 AI Native 知识库体系(案例)](ai-native-knowledge-base-gaode.md) — 六域知识底座、意图识别三件套、直达短路检索、多 Agent 批量抽取、闭环保鲜(企业 Agent 落地案例)
- [AI 原生组织方法论:Anthropic 的 65% PR](ai-native-organization-methodology.md) — AI 直接开 PR 人来审、4 要素协作模型、Skills 最小单元、产品矩阵、Mythos 可观测性兜底、五步转型路径
- [企业 Agent 工程化(一):任务边界与工具治理](enterprise-agent-boundaries-tools.md) — 为什么慢不是犯错而是停不下来;工具是负债,三类失控与治理 checklist
- [企业 Agent 工程化(二):异常恢复与人工接管](enterprise-agent-recovery-handoff.md) — 重试/回滚/接管三选一,后果半径四档,接管请求六块信息
- [企业 Agent 工程化(三):权限、集成与可观测性](enterprise-agent-permission-integration-observability.md) — 替谁做事、接口通了≠接稳、四类记录与最小记录契约
- [企业 Agent 工程化(四):Tool、MCP、Skills、Harness 四件套](enterprise-agent-tooling-harness.md) — 四件套职责边界、工具接口契约、记忆三分、反思落到验证
- [Agent 是任务执行系统:十个工程要点](agent-as-task-execution-system.md) — 控制循环、工具边界、记忆取舍、验证机制、多 Agent 成本与框架选型
- [Agent 落地失败的根因在筛选:三个筛子选对活儿](enterprise-agent-selection-screening.md) — 频次/明确性/容错性三筛;法务 AI 起草合同反例;选岗位优于选任务、首单避开高风险(知乎回答,原文截断待补)

## 待整理 / 规划

<!-- 从 inbox 收件箱转入本主题的素材,梳理前先登记在这里 -->

## 预计覆盖方向

- **Ontology 基础**:本体定义(概念、属性、关系、公理)、与知识图谱/数据模型的关系
- **企业语义层**:统一术语表、业务对象模型,让 Agent 与业务系统说"同一种语言"
- **Ontology + RAG/Agent**:本体驱动的检索、规划约束、工具与数据源编排
- **治理与合规**:权限、审计、幻觉防控的企业级要求
- **案例**:某行业/场景的本体驱动 Agent 落地实践

## 学习指引

- 入门顺序:本体基础概念 → 企业语义层 → 与 RAG 结合 → 治理 → 案例复盘。
