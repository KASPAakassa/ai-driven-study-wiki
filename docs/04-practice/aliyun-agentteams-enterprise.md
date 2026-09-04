# 阿里云 AgentTeams:当 Agent 开始真正在企业里干活——企业级多 Agent 协作平台拆解

> **一句话摘要**:阿里云 AgentTeams 把多 Agent 协作从"一次任务怎么并行跑快"升级到"一个 Agent 组织怎么长期运转"——就像临时组局打羽毛球 vs 运营一个几百人的俱乐部。四层架构(入口/Agent Identity/Agent Team 组织/统一 AI 资产管理)+ 安全四道防线(零信任网关/Sandbox/通信加密/Skill 市场)+ 三层协作(Manager/TL/Worker)+ 弹性沙箱运行时 + AgentLoop 双飞轮进化,把企业 IT 为人类员工做过一遍的事,为 Agent 再做一遍。
>
> **来源**:微信公众号「阿里云云原生」《阿里云 AgentTeams 解读:当 Agent 开始真正在企业里干活》(付宇轩/邵丹),https://mp.weixin.qq.com/s/oM3V-URazBmlLBeJQR3O_A;原始资料存档于 `docs/inbox/aliyun-agentteams-source.md`

## 概念:从"并行快跑"到"组织长期运转"

**命题差异**:大多数多 Agent 方案解决的是"一次任务怎么并行跑快";AgentTeams 想解决的是"一个 Agent 组织怎么长期运转"——差距就像**临时组个局打羽毛球 vs 运营一个几百号人的羽毛球俱乐部**。

**四层落地架构**(从上到下):

| 层 | 内容 |
| --- | --- |
| ① 入口层 | 原生 AgentTeams 客户端、钉钉/飞书/企业微信等 IM 集成、自研 Web 端 HTTP 服务化接入——**不逼员工换工具,让 Agent 出现在他们本来就在用的地方** |
| ② Agent Identity | 接入企业 IdP/SSO 用户体系,为 Agent 工作负载签发身份,把用户身份透传到 Agent,**每一步操作都可归属到人** |
| ③ Agent Team 组织 | 按职能编成研发/客服/数据分析/运营团队,每团队由 TL Agent 调度,底层引擎热插拔可替换 |
| ④ 统一 AI 资产管理 | 模型、Skill、MCP Server、Worker Agent 模板集中管理,BYOC(Bring Your Own Cloud)保证 AI 资产自主可控 |

**右侧贯穿四层**:一套观测、度量、治理中台——从 Token 消耗到 Prompt 分析到效果审计,全程可观测。

> **核心判断:Agent 不是散装的脚本,而是一种需要被管理、被治理、被观测的企业级工作负载。**

## 原理:安全四道防线(零信任 Agent 管理底座)

!!! danger "安全是目前整个多 Agent 领域最被低估的风险"
    大家都在卷能力、卷效果、卷 benchmark,很少有人认真讨论:当 Agent 开始真正在企业里干活,它手里攥着一堆 API Key 和数据库凭证,这些事情有多危险。一个被注入攻击的 Agent 如果有数据库写权限和 API Key,它能干的事情跟一个被攻陷的管理员账号没有区别——区别只是管理员是人,你知道该找谁问责;Agent 被攻陷了,你连爆炸半径有多大都不知道。

| 防线 | 机制 | 解决的问题 |
| --- | --- | --- |
| ① **AI 网关(零凭证持有)** | 所有 LLM 调用和外部密钥统一收进网关加密托管,**Agent 本身不持有任何凭证**;叠加细粒度风控(Agent 身份认证 + Skill/MCP 指令级拦截) | 身份可信:Agent 零明文持有出站凭证(STS/OAuth/API Key 全托管) |
| ② **Sandbox 沙箱(运行时隔离)** | 每个 Agent 跑在独立沙箱,实例/网络/存储三维物理隔离 | 运行可控:越权/注入攻击被锁死在单个沙箱内 |
| ③ **通信安全** | Agent 间基于端到端加密协议传输,任务派发/上下文/数据流转全程加密;Room 机制保证信息透明、审计可溯源 | 通信可靠:协同过程既保密又可追查 |
| ④ **Skill 市场(供应链安全)** | 所有 Skill 和 MCP 能力须通过安全扫描审核才能注册上架;调用经网关 per-consumer ACL 按需授权,最小权限原则;Skill 分组管理实现分组间隔离和统一分发 | 资产可查:从源头杜绝恶意能力混入 |

**四道防线层层递进:身份可信、运行可控、通信可靠、资产可查。** 设计时的强烈感受:**太多人把 Agent 当成"更聪明的脚本",但生产环境里安全是生死线,不是锦上添花。**

## 原理:三层协作架构(Manager / TL / Worker)

**比 Claude Managed Agents(CMA)多一层 TL**——CMA 是两层(Lead + Teammates),AgentTeams 是三层:

| 层 | 角色 | 类比 |
| --- | --- | --- |
| **Manager Agent** | 全局监管 + 任务拆解 | CEO |
| **Team Leader Agent** | 具体团队调度和分配 | VP → Team Lead |
| **Worker Agent** | 最底层执行任务 | 一线员工 |

**TL 这层不是白加的**——解决的是**管理幅度(span of control)**问题:一个人(或 Agent)能有效管理的直接下属有限,超过阈值需要分层。人类组织几千年实践沉淀的最优解,搬进 Agent 系统。

**与 CMA 的差异**:

- CMA 的 Lead 是固定主会话,不可转移、不可把 Teammate 提升为 Lead;AgentTeams 的 Manager 和 TL 都是**独立 Agent 实例,可灵活调整**——企业场景不可能每次都从头搭团队结构;
- **真人成员 + Agent 成员混合组织模型**:团队群里 Admin 管团队、TL 编排任务、Worker 执行,真人可随时介入打断、实时纠偏;交互模式有团队群聊协作编排 + 一对一私聊专项沟通,权限严格隔离在团队范围内;
- **与 Subagent 的关系**:类 CMA 模式的主 Agent + Subagent 对应 AgentTeams 里 Worker Agent 进程内的 Subagent 链——定义为"**延迟敏感的连贯流程收进单 Worker 内的 Subagent 链**"。

## 原理:弹性沙箱运行时(隔离、弹性、成本)

基于 ACS Sandbox 把"安全的 Agent 运行环境"与"经济的资源模型"合二为一:

- **安全隔离**:每个 Agent 在资源、网络、存储三维物理隔离——企业级硬门槛;
- **Session 亲和路由**:"单 Session 单 Sandbox"原则,每会话稳定路由到独立沙箱,彼此互不串扰;
- **弹性伸缩三种方式**:
  1. **Session 级扩并发**:五个人同时跟同一 Worker 交互 → 拉起五个独立 Sandbox 并行接请求,并发随 Session 数线性扩展;
  2. **Team 级多副本分流**:创建多个相同 Team 副本,以副本为单位分流请求,像多实例负载均衡横向扩并发;
  3. **Subagent 同进程编排压时延**:Worker 内建多个 Subagent(独立 SOUL.md 和 Skill 配置)跑在同一进程,零网络跳数——**按业务时延敏感度选择编排粒度**;
- **成本:深休眠机制**——无请求时 Sandbox 进入深休眠,只以快照保留现场不产生费用;有请求秒级从快照拉起恢复现场。"用多少、付多少";
- **存储灵活**:Worker Sandbox 可用独享存储,也可按需挂载 OSS/NAS 跨 Sandbox 共享存储,兼顾隔离与共享。

**实际例子(售后退款)**:对应一个 Worker Agent,内部退款受理/订单核验/责任判定/规则计算/风控校验/退款执行/通知归档七个步骤由七个 Subagent 同一进程内串行完成,端到端零网络跳数;只有跨功能协作(如退款后通知财务结算 Worker)才走跨进程调用。

## 实践 / 应用:Agent 持续进化——双飞轮结构

Agent 系统不应该是一个静态的工具,而应该是一个**能够从使用中学习、持续进化的系统**:

- **左飞轮(AgentTeams)**:多 Agent 协作底座,在真实业务运转中自然沉淀执行轨迹、工具调用日志、数字员工协作记录、成功和失败案例;
- **右飞轮(AgentLoop)**:接过数据做清洗、自动评估、SFT 和 RLHF 训练,再反哺为 Prompt 优化、模型更新、技能库优化和组织结构优化;
- **核心链路三动作**:**发现**(监控高频失败 Task,沉淀 Bad Case)→ **对齐**(结合人类偏好数据,构建企业专属 DPO/RLHF 训练集)→ **进化**(自动重构 Prompt,持续提升效果);
- **现实壁垒**:飞轮转动后 Agent Team 越来越懂企业自己的 SOP 和业务流程——**这种积累是别家搬不走的**。

!!! note "作者坦承"
    这个飞轮现阶段还比较偏理想化——要真正转起来,需要足够多的真实业务数据、成熟的评估体系和持续的工程投入。但方向是对的。

## 总结

- **定位**:企业级多 Agent 协作平台——从"一次任务并行快跑"到"Agent 组织长期运转";四层架构(入口/Agent Identity/Agent Team 组织/统一 AI 资产管理)+ 贯穿式观测治理中台;
- **安全四道防线**:零信任 AI 网关(零凭证持有)、Sandbox 三维隔离、端到端加密通信、Skill 市场供应链安全——身份可信/运行可控/通信可靠/资产可查;
- **三层协作**:Manager(全局监管拆解)/ TL(团队调度,按需动态)/ Worker(执行);比 CMA 多一层 TL 解决管理幅度问题,支持真人+Agent 混合组织;
- **弹性沙箱运行时**:单 Session 单 Sandbox、三种伸缩方式(Session 级/Team 副本/Subagent 同进程)、深休眠省成本;
- **持续进化**:AgentTeams + AgentLoop 双飞轮(发现→对齐→进化),沉淀企业专属 SOP 形成壁垒;
- **核心判断**:Agent 是需要被管理、被治理、被观测的企业级工作负载——企业 IT 为人类员工做过的事,为 Agent 再做一遍;
- **下一步**:对照站内 [Agent 生产架构](../03-agents/agent-production-architecture.md)(权限洋葱/分层容错)、[Agent 治理 Hook](../03-agents/agent-governance-hooks.md)(护栏)、[多智能体协作设计](../03-agents/agent-team-room-collaboration.md)(Team/Room 建模),理解企业级多 Agent 平台的完整设计。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/oM3V-URazBmlLBeJQR3O_A
- 站内:[Agent 生产架构](../03-agents/agent-production-architecture.md)(权限/协作/容错/部署)、[Agent 治理:用 Hook 堵住偷懒越权失忆](../03-agents/agent-governance-hooks.md)、[多智能体协作设计](../03-agents/agent-team-room-collaboration.md)、[Agent 安全审计实战](agent-security-audit-practice.md)、[DeepTutor 港大 AI 工作空间](deeptutor-agent-workspace.md)(同为 agent 应用案例)
