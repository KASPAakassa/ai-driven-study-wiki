# 企业 Agent 体系设计:四要素、三层体系与关键决策

> **一句话摘要**:个人用 Agent,装个工具、写几个 prompt 就能跑起来;企业场景完全不一样——多用户、多 agent、多入口、不同权限,问题复杂度是指数级的。本文把核心设计讲透:**Agent = LLM + 上下文 + 工具 + Harness 四要素**;企业场景再加**三层体系**(生产层知识资产与工具底座 / 服务层配置驱动 Agent 运行时 / 消费层多入口路由)与横跨的运维层。企业 Agent 体系本质上是**基础设施设计问题**——框架会演进,模型会迭代,但"多用户、多 agent、多入口"的架构约束不会变。
>
> **来源**:微信公众号「风筝」《企业Agent体系设计》(2026-07-15 技术实践),https://mp.weixin.qq.com/s/28MGVdk46OEDZSB2elTqBw;原始资料存档于 `docs/inbox/enterprise-agent-system-design-source.md`

## 概念:用户级 Agent 和企业级 Agent 是两件事

!!! tip "真实场景的四连问"
    你写了一个查数据的 agent:**张三能不能用?李四用的时候查的是他自己的数据还是你的?王五在群里 @ 机器人问了一句,消息怎么路由到正确的 agent?回复之后上下文要不要保留、保留多久?跨 agent 协作谁来调度?** 这些不是"装什么工具"的问题,是**架构问题**。

## 原理:Agent 四要素与三层体系

### 一、Agent 四要素

!!! tip "公式**
    **Agent = LLM(推理引擎)+ 上下文(知)+ 工具(行)+ Harness(工程保障)**
    LLM 是引擎,上下文是燃料,工具是手脚,**Harness 是神经系统**——控制怎么思考、怎么执行、怎么不出错。

**① LLM:推理引擎**——选什么模型/参数决定能力天花板,但 **LLM 本身不携带任何企业知识**:裸模型面对"查一下昨天的消耗",不知道"消耗"在哪个表、"昨天"对应哪个分区字段、当前用户有没有权限。**模型选择固然重要,更关键的是喂了什么上下文、给了什么工具。**

**② 上下文:企业上下文 vs LLM 有效上下文**(最容易忽略的关键区分):

| | 企业上下文 | LLM 有效上下文 |
| --- | --- | --- |
| 内容 | 全量知识资产:元信息/规范文档/血缘图谱/术语词典/PRD | context window 里实际存在的内容 |
| 形态 | 静态、持续积累、体量巨大 | 动态、有长度限制、随会话变化 |
| 位置 | 知识库/Git/图数据库 | system prompt/对话历史/检索片段/工具结果 |

!!! warning "企业上下文不能直接塞给 Agent——context window 瞬间就爆了"
    真正的工作流:**工具检索从企业上下文捞出相关子集 → Skill 引导如何组合 → Harness 负责注入时机和格式 → 形成 LLM 有效上下文**。企业上下文是原材料,工具和 Skill 是加工过程,Agent 看到的是成品。**你不能靠"写更长的 prompt"解决问题,得有一套能把知识按需装进 context window 的机制——这就是为什么 RAG 在企业 Agent 里不是可选项、而是必选项**(呼应 [高德知识库](ai-native-knowledge-base-gaode.md) 的"最小有用片段"检索)。

**③ 工具:用户级 vs 服务级**(最容易踩坑的分类标准):

!!! tip "直觉上按技术形态分(CLI vs MCP),但真正的维度是:工具能不能区分用户身份**
    - **CLI 落在用户级**:per-user cookie 透传,张三和李四查同一张表看到各自有权限看的数据,**权限隔离天然成立**;
    - **MCP 落在服务级**:不传用户身份、只看到调用方,多用户场景**权限模型直接失效**;
    - **这不是协议决定的,是工程选择**——CLI 也可以不绑 cookie,MCP 也能透传用户身份。但分类一旦搞错,多用户权限模型就从根上做不对。

    工具标准化的正确做法:**先在 API 层做统一鉴权、格式标准化、凭证注入,CLI 和 MCP 都变成这层 API 的薄壳**——标准化逻辑只写一次,能力集天然对齐。

**④ Harness:工程保障(Agent 的"运行时操作系统")**——不决定 Agent 能做什么,但决定怎么做。四个核心机制:

| 机制 | 内容 |
| --- | --- |
| **思考模式** | ReAct(数据分析)/ Plan-then-Execute(代码生成)/ Loop(持续迭代)——不同场景选不同模式 |
| **Hooks** | 关键节点埋点:工具调用前权限校验、执行后结果校验,出错拦截而非盲目继续(呼应 [Hook 治理](../../03-agents/agent-governance-hooks.md)) |
| **记忆管理** | 自动压缩长对话,保留关键丢弃冗余——否则多轮后 context window 被历史占满 |
| **权限控制** | Harness 层决定 Agent 能调哪些工具、以什么身份调用、频率上限 |

!!! warning "很多 Agent '跑着跑着就停'或'无限循环调用工具',根因都在 Harness 层没有做好边界控制**

**⑤ Skill:四要素的打包复用**——按领域打包(引用领域上下文/搭载专属工具/指定 Harness 模式),可插拔能力单元。**工具是"怎么做"(检索知识、执行操作),Skill 是"什么时候做什么"(策略和节奏)**——比如"做数据分析时先探查元数据、再写 SQL、最后验数"是策略,做成**文档格式、人机共读**,维护成本低;Skill 本质是知识的一种封装形式,不是代码(呼应站内 [四件套](../../07-agent-coding/experience/ai-coding-harness-design.md) 与 [AI 原生组织](ai-native-organization-methodology.md) 的 Skill 资产化)。

### 二、三层体系:生产、服务、消费

```
消费层 — 多入口接入与路由(Web UI / 企微机器人 / API;命令路由 / 意图路由)
服务层 — Agent 运行时(本地模式 / 服务化模式;Agent 工厂配置驱动组装)
生产层 — 知识资产(元信息/规范/血缘/术语/PRD)+ 工具底座(标准化 API 层 → CLI/MCP 薄壳)
运维层 — 注册中心 / 配置中心 / 监控告警 / 评估反馈(横跨三层)
```

- **生产层**:两类原材料——知识资产(持续积累、版本化管理,资产越完整 Agent 能回答的边界越宽)+ 工具底座(标准化在 API 层做一次:统一鉴权/统一格式/注入 per-user 凭证,CLI 和 MCP 基于同一套 API 暴露);
- **服务层**:两种部署形态——本地模式(单用户,启动时确定身份权限,适合调试)+ 服务化模式(多用户,配置驱动组装,消费层注入用户身份,配置中心提供版本/灰度/回滚);**关键设计:同一套 Agent 和 Skill 不感知部署形态**;Agent 工厂运行时读配置、拉组件、注入 system prompt、产出实例——**新增一个 agent = 提交一份配置声明**,不需要新建项目/复制代码/重新配环境;工具和 Skill 在注册中心独立管理版本,修改一处全局生效;
- **消费层**:三种接入模式——独立入口(多 Tab 显式选 agent,专业工具型)/ 共享上下文·命令路由(/ 前缀路由,企微群聊场景)/ 共享上下文·意图路由(意图识别自动路由,长期演进方向);公共能力层做协议适配/身份注入(per-user cookie/OAuth 透传到工具层)/会话管理/意图路由(跨 agent 传上下文);
- **运维层**:注册中心(工具+Skill 版本)、配置中心(Agent+消费配置灰度回滚)、监控告警(完成率/工具准确率/延迟)、评估反馈(端到端完成率回流驱动配置迭代)。

## 代码 / 实现:用户级 vs 服务级权限隔离(纯 Python)

把"工具能不能区分用户身份"这一核心决策落成可运行演示:

```python
# —— 用户级 vs 服务级工具:多用户权限隔离 ——
ROWS = [  # (数据行, 可见角色)
    ("客户A-销售额", "sales_team"),
    ("客户B-销售额", "sales_team"),
    ("HR-薪资表", "hr_team"),
]
ROLES = {"zhangsan": "sales_team", "lisi_hr": "hr_team", "admin": "admin"}

def query_user_level(user, table):
    """用户级(CLI 式):per-user cookie 透传,后端原生权限过滤——张三看不到 HR 数据"""
    role = ROLES.get(user, "")
    return [r[0] for r in ROWS if r[1] == role or role == "admin"]

def query_service_level(table):
    """服务级(MCP 式):不传用户身份,只看到调用方——权限模型直接失效"""
    return [r[0] for r in ROWS]   # 所有用户都看到全部数据(越权)

print("用户级工具:张三查询 →", query_user_level("zhangsan", "表"))
print("用户级工具:HR 查询  →", query_user_level("lisi_hr", "表"))
print("服务级工具:任何用户 →", query_service_level("表"), "← 权限失效,多用户场景必须避免")

assert query_user_level("zhangsan", "表") == ["客户A-销售额", "客户B-销售额"]
assert "HR-薪资表" not in query_user_level("zhangsan", "表")   # 隔离成立
assert "HR-薪资表" in query_service_level("表")                 # 越权
print("\n结论:工具层透传用户身份 → 权限隔离天然成立;不透传 → 多用户场景权限失效")
```

## 实践 / 应用:关键设计决策与演进路径

### 四个关键决策

1. **为什么选 CLI 做工具标准化入口**:CLI 能同时覆盖人(终端直接敲)和 agent(bash tool);per-user cookie 天然支持多用户权限隔离;单一 Go 二进制分发简单;**更关键:CLI 天然落在"用户级工具"一侧,权限隔离在工具层就解决,消费层不需要再做一层权限映射**;
2. **为什么权限做在工具层而不是消费层**:多后端 API 各有独立鉴权体系,消费层统一接管成本太高;工具层 per-user cookie 透传利用各后端原生权限机制,简单有效;消费层只做粗粒度能力路由补充;
3. **多 agent 边界怎么划分**:同一领域质量审查 → sub-agent 协作(reviewer/checker);不同业务域 → 独立 agent;不同消费端 → 消费适配器共用同一套 agent;
4. **顺序不能反**:先在工具层做用户身份透传 → 再用配置驱动降低 agent 组装成本 → 最后在消费层做统一路由——**没有用户级工具就没有真正的多用户隔离,没有配置驱动就谈不上规模化**。

### 演进路径(四阶段,每层独立推进不互相阻塞)

| 阶段 | 内容 |
| --- | --- |
| **Phase 1 Skill 层收敛** | 各项目分散的 Skill 统一治理,版本化分发,跨 AI 工具使用 |
| **Phase 2 Agent 层规范化** | 提取独立业务 agent;Agent 后端拆为纯运行时 + 平台基础设施(认证/WebSocket/DB 独立) |
| **Phase 3 工具底座标准化** | 建立标准化 API 层,CLI 和 MCP 重构为薄壳,能力集完全对齐 |
| **Phase 4 消费层统一** | 多入口路由/会话管理统一为消费层网关,各入口只做 UI 适配 |

### 与站内其他文章的呼应

- [Agent 落地方法论](agent-landing-micro-agents.md):本文是"落地方法论"的**体系设计版**(四要素/三层是微智能体的规模化形态);
- [企业业务 Agent 落地(四步路径)](enterprise-agent-business-rollout.md):四步上线是单 agent 的节奏,本文是**多 agent 体系的架构**;
- [高德知识库](ai-native-knowledge-base-gaode.md):生产层的知识资产 = 高德的六域知识底座;
- [Agent 系统设计的 5 个决策](../../03-agents/agent-system-5-decisions.md):四要素 = 5 决策的概括形态(LLM 路由/循环/工具/安全);
- [Palantir 操作型本体论](palantir-operational-ontology.md):工具底座与 Action 受控写回、配置驱动与 Ontology 的治理同构。

## 总结

- **四要素**:LLM(引擎)+ 上下文(知,企业上下文 vs 有效上下文,RAG 必选)+ 工具(行,**用户级 vs 服务级是真正分类**)+ Harness(工程保障,思考模式/Hooks/记忆/权限);
- **三层体系**:生产层(知识资产 + 标准化工具底座)、服务层(配置驱动 Agent 工厂,同一套 Agent 不感知部署形态)、消费层(多入口路由,命令/意图两种共享上下文模式)+ 横跨运维层;
- **两条铁律**:权限隔离靠工具层 per-user 透传(不是消费层映射);顺序不能反(用户级工具 → 配置驱动 → 消费路由);
- **一句话**:企业 Agent 体系本质是**基础设施设计问题**——框架会演进,模型会迭代,但"多用户、多 agent、多入口"的架构约束不会变;把三层想清楚,剩下的只是工程节奏。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/28MGVdk46OEDZSB2elTqBw;原始资料存档于 `docs/inbox/enterprise-agent-system-design-source.md`
- 站内:[Agent 落地方法论](agent-landing-micro-agents.md)、[企业业务 Agent 落地(四步路径)](enterprise-agent-business-rollout.md)、[企业 Agent 工程化系列](index.md)、[高德知识库](ai-native-knowledge-base-gaode.md)、[Agent 系统设计的 5 个决策](../../03-agents/agent-system-5-decisions.md)、[AI 原生组织方法论](ai-native-organization-methodology.md)、[Hook 治理](../../03-agents/agent-governance-hooks.md)
