# Agent 框架选型地图:2026 年五框架对比与三层控制权模型

> **一句话摘要**:主流 Agent 框架"该有的能力大多都有",真正的区别不是能不能做,而是**你准备把哪一层控制权交给框架**——循环层(模型调用/工具执行/停止)、运行时层(状态/持久化/中断恢复/人工审批)、协作层(多 Agent 角色/委派/交接)。本文给出 2026 年五框架的选型地图(OpenAI Agents SDK / LangGraph / CrewAI / Eino / Google ADK,附 LangChainGo),配官方仓库数据,并提炼四条"防迁移成本"的工程边界。
>
> **来源**:微信公众号「后端搞AI」《2026 Agent 框架地图》(技术资料核验于 2026-08-09),https://mp.weixin.qq.com/s/3ZGCIEvdgFn_h5XaDl7a7Q;官方数据(2026-08-09 核验):GitHub Star 与定位;原始资料存档于 `docs/inbox/agent-framework-selection-source.md`

## 概念:选型不是比功能,是选"把哪层控制权交出去"

!!! tip "核心判断"
    一开始想找"功能对比表"(看谁支持工具/记忆/多 Agent/MCP,打勾最多就选谁)——**这条路基本没用**。真正区别:**抽象越高,上手越快,但出问题时要穿透的层也越多**。框架的价值 = 从你手里接走一部分层的控制权。

**三层模型**(一个 Agent 系统从下往上):

| 层 | 内容 | 谁替你管 |
| --- | --- | --- |
| **循环层** | 模型调用、工具执行、结果回填、停止条件 | OpenAI Agents SDK(最顺手) |
| **运行时层** | 状态、分支、持久化、中断恢复、人工审批 | LangGraph |
| **协作层** | 多 Agent 的角色、委派、交接、团队流程 | CrewAI |

!!! note "版本号不能直接判断能否上生产"
    0.x / 1.x 不代表成熟度;更值得看 **API 变动、发布节奏、可观测性、状态兼容、团队能否兜底**。

## 原理:五个框架详解(含官方数据)

### 1. OpenAI Agents SDK(Python 0.19.4,★28.5k)——循环层

- **定位**:给手写 Agent 装上工程配件——Agent(指令+工具)/ Runner(循环)/ Handoff(会话控制权移交)/ Guardrail / Session / Tracing / 可暂停恢复的人工审批;
- **后端类比**:不是工作流平台,更像**带中间件和链路追踪的 Agent Runtime SDK**;
- **适合**:单 Agent + 一组工具为主;想少写循环/重试/会话/trace,但保留普通代码可读性;Python/TS 快速接入;多 Agent 只是局部委派;
- **注意**:模型与 Provider 有扩展入口,但接口演进/托管工具/观测天然围绕 OpenAI 生态——**要求彻底厂商中立需单独评估迁移成本**。

### 2. LangGraph(Python 1.2.10,★39.2k)——运行时层

- **定位**(官方自述克制):面向**长时间运行、有状态 Agent 的低层编排框架和运行时**;官方明确"新手快速做 Agent 可先用更高层的 LangChain Agents";
- **核心卖点不是少写工具调用,而是工程问题**:任务跑到第 8 步服务重启能否断点续跑?人工审批能否暂停几小时恢复?哪些节点固定逻辑、哪些允许模型自主?状态如何持久化、分支怎么回放、失败路径怎么定位?
- **核心抽象**:State / Node / Edge / Checkpoint——状态机 + 工作流引擎 + checkpoint,节点里可以放 LLM;
- **适合**:长任务、强状态、中断恢复;固定流程与 Agent 决策混合;审批/重跑/审计明确;愿意为可控性接受图结构;
- **代价**:简单问题显重(40 行循环要加 State/Node/Edge/Checkpoint)——**不是默认起点,是复杂度长出来之后的升级路线**。

### 3. CrewAI(1.15.13,★56.8k)——协作层

- **最有辨识度的抽象**:Crew(给 Agent 分角色/目标/工具,把任务交给团队);
- **当前官方架构两部分**:Flow(管状态、事件和确定性整体流程)+ Crew(某步骤里组织多 Agent 自主协作);**官方建议生产从 Flow 开始,再在需要创造性协作的节点调用 Crew**——多 Agent 最后还是需要一个可控的外壳;
- **适合**:研究/内容生产/方案评审等天然可描述成多个专业角色;业务方能直接理解"研究员 → 撰稿人 → 审核员";快速验证多 Agent 分工假设;
- **风险**:角色越多不代表越好——每加一个 Agent 就加一组 Prompt/上下文/模型调用/故障点;一个普通函数能完成的校验,不必请"质量审核 Agent"再思考一遍。**只有当"谁和谁协作"是需求本身时才选 CrewAI**。

### 4. Eino(Go 0.9.13,★12.6k)——循环+运行时+协作(Go 原生)

- **定位**:Go 团队不必为"AI 生态都在 Python"默认引入新运行时;按 Go 习惯分层:
  - **Components**:ChatModel / Tool / Retriever / ChatTemplate 组件接口;
  - **Compose**:Chain / Graph 组合确定性流程,统一处理流式数据;
  - **ADK**:工具调用、上下文管理、多 Agent、Interrupt/Resume 等 Agent 能力;
  - **Callback**:组件/图/Agent 固定切面接日志、Tracing、指标;
- **关键设计**:普通业务流程继续写确定性 Graph,需要自主决策时把 Graph 暴露成 Tool 交给 Agent——**不是所有东西都塞进一个大 Agent**;
- **适合**:主力 Go;在意类型约束/并发/流式/服务内集成;愿意跟进未到 1.0 的快速演进生态;
- **对照 LangChainGo**(★9.6k,最新 v0.1.14 发布于 2025-10):更像 LangChain 的 Go 实现,组件覆盖不少;**新 Agent 编排项目优先评估发布更活跃、同时具备 Compose 和 ADK 的 Eino**;仅需特定组件集成再比 LangChainGo。

### 5. Google ADK(Python 2.6.3,★21k)——Agent/Workflow/评估/部署

- 2026 已进入 2.x;提供 Agent、图式 Workflow、Task 委派、评估、部署工具;
- **适合**:模型与基础设施明显偏 Gemini / Google Cloud;
- **提醒**:未绑定云平台的后端初学者,不必同时铺开 LangGraph/OpenAI SDK/CrewAI/ADK——概念大量重叠,**先吃透一条路线,迁移时对照会快得多**。

## 代码 / 实现:框架推荐器(纯 Python,对应"选择五问")

```python
# —— 按需求五问推荐框架(对应文章"选择路径")——
def recommend(flow_writable=False, is_go=False, just_loop=True,
              needs_persistence=False, role_collab_core=False,
              google_stack=False) -> str:
    if flow_writable:
        return "普通 Workflow 即可,别上 Agent 框架(确定性流程用代码/图)"  # 问题 1
    if is_go:
        return "Eino(Go 原生;仅组件集成再看 LangChainGo)"                 # 问题 2
    if just_loop:
        return "OpenAI Agents SDK(Python/TS 轻量起步)"                     # 问题 3
    if needs_persistence:
        return "LangGraph(状态持久化/暂停恢复/审批)"                        # 问题 4
    if role_collab_core:
        return "CrewAI" + (" + Google ADK" if google_stack else "")         # 问题 5
    return "从抽象最低、能解决当前问题的方案开始(轻量 SDK 升级比深度绑定迁移成本低)"

cases = [
    (True,  False, True,  False, False, False),   # 流程可写死
    (False, True,  False, False, False, False),   # Go 项目
    (False, False, True,  False, False, False),   # 只要循环
    (False, False, False, True,  False, False),   # 要持久化/审批
    (False, False, False, False, True,  True),    # 角色协作 + Google
]
for c in cases:
    print(f"  {c} → {recommend(*c)}")
assert recommend(True, False, True, False, False, False).startswith("普通 Workflow")
assert recommend(False, True, False, False, False, False).startswith("Eino")
assert recommend(False, False, True, False, False, False).startswith("OpenAI")
print("代码验证通过 ✔")
```

## 实践 / 应用:四条边界 + 我的选择

!!! warning "真正该提前防的,是迁移成本"
    框架以后大概率会换,业务工具和状态数据最好别跟着陪葬。写第一版就守住四条边界:

1. **工具保持普通函数**:参数和返回值用清晰 schema,别让业务逻辑只能在某个框架的装饰器里运行;
2. **状态结构自己定义**:会话/任务状态/审批记录放在你能控制的存储里;框架 checkpoint 是运行机制,不该成为唯一数据源;
3. **模型调用留适配层**:"兼容 OpenAI 接口"不等于行为完全一致——工具调用、流式事件、错误结构都可能不同;
4. **Tracing 从第一天就接**:框架帮你隐藏了循环,也会顺手隐藏故障现场——至少能看到每次模型调用/工具参数/状态变化/耗时/token。

**作者当前选择**(仅供参考):Python/TS 简单 Agent 用 OpenAI Agents SDK 起步;复杂/长时间/有审批恢复用 LangGraph;角色协作是业务本体用 CrewAI;Go 项目优先评估 Eino。

!!! note "与站内其他文章的呼应"
    - [Agent 框架](agent-frameworks.md):那篇是框架**基础**(核心抽象/执行循环/手写对比);本文是**选型决策**(三层控制权/五框架 2026 对比/四条边界);
    - [Agent 系统设计的 5 个决策](agent-system-5-decisions.md):"四条边界"是其中"循环/工具/状态"决策的框架视角;
    - [生产级 Agent 9 层架构](ai-infra-layering.md):运行时层(LangGraph)= L4 编排;循环层(OpenAI SDK)= L1-L2;
    - [Harness 收录清单](../08-harness/index.md):08 章节有框架索引(通用编排框架),本文补充选型视角。

## 总结

- **选型本质**:用控制权换开发速度,用抽象换工程能力——先看清三层(循环/运行时/协作)你要把哪层交出去;
- **五框架定位**:OpenAI SDK(循环层,轻量)/ LangGraph(运行时层,可恢复状态机)/ CrewAI(协作层,角色团队)/ Eino(Go 原生三层)/ Google ADK(Gemini/云技术栈);
- **四条边界**:工具普通函数、状态自己定义、模型留适配层、Tracing 第一天接——比争论功能更值钱;
- **五问路径**:流程可写死→Workflow;Go→Eino;只要循环→OpenAI SDK;要持久化审批→LangGraph;角色协作核心→CrewAI(+ADK);
- **一句话**:真正要学的不是某个 API,而是循环、状态、工具、恢复和可观测性这些**不会过时的工程问题**。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/3ZGCIEvdgFn_h5XaDl7a7Q;原始资料存档于 `docs/inbox/agent-framework-selection-source.md`
- 官方资料:LangGraph https://docs.langchain.com/oss/python/langgraph/overview · OpenAI Agents SDK https://developers.openai.com/api/docs/guides/agents · CrewAI https://docs.crewai.com/en/introduction · Eino https://www.cloudwego.io/docs/eino/overview/ + https://github.com/cloudwego/eino · Google ADK https://github.com/google/adk-python · LangChainGo https://github.com/tmc/langchaingo
- 站内:[Agent 框架](agent-frameworks.md)(基础篇)、[Agent 系统设计的 5 个决策](agent-system-5-decisions.md)、[生产级 Agent 9 层架构](ai-infra-layering.md)、[Harness 收录清单](../08-harness/index.md)
