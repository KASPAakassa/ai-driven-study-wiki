# 原始资料:Agent架构全解析:从入门到企业级(七种主流架构)

> 来源:用户提供(视频讲解);抓取日期:2026-08-09
> 状态:已整理为正式文章 docs/03-agents/agent-architecture-panorama.md(全景地图+选择档位,与站内各架构深入文章交叉链接)

## 核心内容(原文)
核心结论:架构选择取决于场景复杂度和控制力需求;演进路径:单Agent → 多Agent协作 → 基于图的工作流;AI Coding 场景 Router + Skill 是当前相对最优解。

七种架构对比:
- 单Agent:一个LLM包揽一切;简单成本低;复杂时上下文污染严重易"晕掉"
- ReAct:推理+行动循环(思考→行动→观察);可解释好多步骤;Token消耗大不稳定易跑偏,不适合大规模工程化
- Plan & Execute:先规划后执行;稳定性高适合代码生成长流程;计划出错全盘崩溃灵活性不足
- 多Agent:多个Agent分工协作;拆解清晰上下文污染低可扩展;成本高,适合流程一致性要求高的复杂场景
- Router + Skill:先识别意图再路由到对应技能模块;稳定性极强企业级可控性能高;Skill设计成本高可能出现路由冲突
- Blackboard:多个Agent共享"黑板"读写状态驱动;适合复杂协作;状态管理重出问题难追踪
- Graph/Workflow:基于DAG编排工作流支持分支并行;企业级稳定可Debug长流程;最重,适合生产流程自动化

选择档位:简单验证=单Agent / 多步探索=ReAct / 工程化=Plan&Execute / 复杂协作=多Agent / 精准技能=Router+Skill / 共享状态=Blackboard / 企业生产=Graph/Workflow
