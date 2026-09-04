# Agent 架构全景:七种架构对比与选择档位

> **一句话摘要**:从个人项目到企业级,Agent 架构按场景复杂度与控制力需求分七个"档位":单 Agent → ReAct → Plan & Execute → 多 Agent → Router + Skill → Blackboard → Graph/Workflow。**没有最好的架构,只有最合适的架构**——演进路径通常是"单 Agent → 多 Agent 协作 → 基于图的工作流";对 AI Coding 场景,**Router + Skill 是当前相对最优解**。本文是全景地图:每档给对比与选型,并指向站内对应的深入文章。
>
> **来源**:用户提供(视频讲解《Agent架构全解析:从入门到企业级》);原始资料存档于 `docs/inbox/agent-architecture-panorama-source.md`

## 概念:架构选择 = 场景复杂度 × 控制力

!!! tip "两个核心结论**
    1. **选择取决于场景复杂度和所需控制力**——没有最好的架构,只有最合适的档位;
    2. **演进路径**:单 Agent → 多 Agent 协作 → 基于图的工作流(复杂度长出来再升级,别一开始就上最重的)。

## 原理:七种架构对比表

| 架构 | 核心特点 | 优点 | 缺点 | 站内深入文章 |
| --- | --- | --- | --- | --- |
| **单 Agent** | 一个 LLM 包揽一切(输入→思考→工具→输出) | 简单、成本低 | 任务复杂时上下文污染严重、易"晕掉" | [AI Agent 入门](agent-intro.md) |
| **ReAct** | 推理+行动循环(思考→行动→观察) | 可解释性好、能处理多步骤 | Token 消耗大、不稳定易跑偏,不适合大规模工程化 | [规划与工作流模式](agent-planning-patterns.md) |
| **Plan & Execute** | 先规划后执行(先生成完整计划再逐步落地) | 稳定性高,适合代码生成和长流程 | 计划一旦出错全盘崩溃、灵活性不足 | [规划与工作流模式](agent-planning-patterns.md) |
| **多 Agent** | 多个 Agent 分工协作、各司其职 | 任务拆解清晰、上下文污染低、可扩展 | 成本高,适合流程一致性要求高的复杂场景 | [多 Agent 协作](multi-agent.md)、[多智能体协作设计](agent-team-room-collaboration.md) |
| **Router + Skill** | 先识别意图,再路由到对应技能模块 | **稳定性极强、企业级可控、性能高** | Skill 设计成本高,可能出现路由冲突 | [Agent 如何理解业务](agent-business-understanding.md)(意图路由)、[企业工程化(四)](../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md)(四件套) |
| **Blackboard** | 多个 Agent 共享"黑板",通过读写状态驱动执行 | 适合复杂协作场景 | 状态管理重,出问题后难以追踪 | [多智能体协作设计](agent-team-room-collaboration.md)(共享状态) |
| **Graph/Workflow** | 基于 DAG 编排工作流,支持分支、并行 | **企业级稳定、可 Debug、支持长流程** | 最重的架构,适合生产环境流程自动化 | [Agent 图工作流设计](agent-graph-design.md)、[云端软件工厂](../08-harness/cloud-software-factory.md) |

!!! note "与站内内容的关系**
    本表是**全景地图**:站内每档都有深入文章(ReAct/Plan&Execute 的机制、多 Agent 的设计、图工作流的拓扑、Router+Skill 的业务理解)——本文负责"选哪档",站内文章负责"怎么搭"。

## 代码 / 实现:架构推荐器(纯 Python,按档位选择)

```python
# —— 按场景特征推荐架构档位 ——
def recommend_architecture(complexity: str, need_control: str,
                           needs_shared_state=False, is_production=False) -> str:
    if is_production:
        return "Graph/Workflow(DAG 编排:分支/并行,企业级稳定可 Debug)"
    if needs_shared_state:
        return "Blackboard(共享黑板:复杂协作,注意状态追踪成本)"
    if complexity == "高":
        return "多 Agent(分工协作)或 Router+Skill(意图路由,企业级可控)"
    if complexity == "中":
        return "Plan & Execute(先规划后执行,工程化)"
    if complexity == "低":
        return "单 Agent(简单验证)或 ReAct(多步探索)"

for c, ctrl, share, prod in [
    ("低", "低", False, False),
    ("中", "中", False, False),
    ("高", "高", False, False),
    ("高", "高", True, False),
    ("高", "高", False, True),
]:
    print(f"  {c}复杂度/控制{ctrl}/共享{share}/生产{prod} → {recommend_architecture(c, ctrl, share, prod)}")
assert recommend_architecture("低", "低").startswith("单 Agent")
assert "Plan" in recommend_architecture("中", "中")
assert recommend_architecture("高", "高", True).startswith("Blackboard")
assert recommend_architecture("高", "高", is_production=True).startswith("Graph")
print("代码验证通过 ✔")
```

## 实践 / 应用:七个选择档位

!!! tip "按档位选择(视频结论)**
    | 项目阶段/需求 | 选 |
    | --- | --- |
    | 简单验证 | **单 Agent** |
    | 多步探索 | **ReAct** |
    | 工程化 | **Plan & Execute** |
    | 复杂协作 | **多 Agent** |
    | 精准技能 | **Router + Skill** |
    | 共享状态 | **Blackboard** |
    | 企业生产 | **Graph/Workflow** |

**AI Coding 场景的最优解**:视频指出 **Router + Skill** 是当前相对最优解——意图识别路由到对应技能模块,稳定性强、企业级可控、性能高。这与站内 [Agent 如何理解业务](agent-business-understanding.md) 的"意图识别 → 路由 → 直达"和 [企业工程化(四)](../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md) 的"四件套(Tool/MCP/Skills/Harness)"互相印证。

!!! note "与站内其他文章的呼应**
    - [规划与工作流模式](agent-planning-patterns.md):ReAct/Plan&Execute/Reflexion/ToT 推理四模式 + 工作流四模式——本文的 ReAct 与 P&E 档位的机制细节;
    - [Agent 图工作流设计](agent-graph-design.md):Graph/Workflow 档位的拓扑与验证设计;
    - [多智能体协作设计](agent-team-room-collaboration.md):多 Agent 与 Blackboard 档位的实现(收件箱/共享状态);
    - [Agent 框架选型地图](agent-framework-selection.md):架构档位 → 具体框架(OpenAI SDK/LangGraph/CrewAI)的映射。

## 总结

- **七档架构**:单 Agent / ReAct / Plan & Execute / 多 Agent / Router + Skill / Blackboard / Graph;
- **选择逻辑**:复杂度 + 控制力需求 → 档位;演进路径 = 单 Agent → 多 Agent → 图工作流;
- **AI Coding 结论**:Router + Skill 当前相对最优(意图路由 + 技能模块,企业级可控);
- **一句话**:没有最好的架构,只有最合适的档位——**先用最轻的跑通,复杂度长出来再升级**。

## 延伸阅读

- 原始素材:用户提供(视频《Agent架构全解析》),存档于 `docs/inbox/agent-architecture-panorama-source.md`
- 站内:[AI Agent 入门](agent-intro.md)、[规划与工作流模式](agent-planning-patterns.md)、[多 Agent 协作](multi-agent.md)、[多智能体协作设计](agent-team-room-collaboration.md)、[Agent 图工作流设计](agent-graph-design.md)、[Agent 如何理解业务](agent-business-understanding.md)、[Agent 框架选型地图](agent-framework-selection.md)、[企业工程化(四)](../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md)
