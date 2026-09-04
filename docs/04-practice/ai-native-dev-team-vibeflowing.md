# 腾讯 Vibe Flowing:从 Vibe Coding 到 AI 原生研发团队的完整落地

> **一句话摘要**:AI 写个人玩具项目很顺手,落到真实业务里就是另一回事。腾讯网络运营团队用 Vibe Flowing 项目给出了一套完整答案:先搭好企业级底座(日志/鉴权/权限/API/定时任务/MCP/工作流),再让 AI 在上面持续开发——运营同事不写代码,也能完成"提需求 → AI 全栈开发 → 自己验收 → 合并上线"的完整流程。团队 3 分钟全自动完成环境配置,人人可参与开发。
>
> **来源**:微信公众号「腾讯程序员」《从 Vibe Coding 到 AI 原生研发团队:一套能落地的工程实践》(作者:masoncai),https://mp.weixin.qq.com/s/DrIpzHm777Zd8klcyAICBA;原始资料存档于 `docs/inbox/vibeflowing-source.md`

## 概念:Vibe Coding 的边界与 AI 原生研发的定义

!!! tip "Vibe Coding 适合写'一次性'的东西,做不了'能持续迭代的系统'"
    **缺的不是 AI 的能力,而是一个专业开发先搭好的架子**:日志、鉴权、权限控制、外部接口封装、数据库变更流程、定时任务——这些都得先打通。有了底座,AI 在上面开发就不必每次从零开始,也不在基础设施问题上浪费时间和 token。

**Vibe Coding 的三大问题**(团队实践总结):
1. **重复造轮子、数据不互通、只有自己说得清**:每个人各写各的页面调用后端接口,鉴权方式、数据口径还不一样;数据散落在孤岛里没法关联分析;
2. **想正经做点事,拦路虎太多**:系统接口权限申请流程漫长,接口文档不全、字段含义不清、鉴权方式各异,AI 想对接也经常踩坑;
3. 超链接聚合入口是"草台班子":页面风格五花八门,哪个能用、出问题找谁说不清,时间一长成"历史遗产"。

**AI 原生研发的定义**(本文):项目的**所有组件和能力**(页面功能、定时任务、Agent 智能体、开放 API、外部接口对接)都由 AI 统一维护;使用者只需要描述需求——简单需求直接对话,复杂需求写成文档经过流程对齐后开发。在这套机制下,**不管会不会写代码,每个人都能参与进来**。

## 原理:三层架构的落地

### 第一层:通用底层能力(企业级底座)

把每个项目都要从头搭的能力沉淀成标准设施,新项目直接继承:

| 能力 | 实现 | 对 AI 的意义 |
| --- | --- | --- |
| **日志** | 复用 SDK 统一日志方法,全项目统一调用签名 | Rules 里写一行说明,AI 每次写代码都用对 |
| **页面权限控制** | RBAC 模型;身份由太湖网关注入 → 人事系统查部门组 → 权限规则存库(页面/操作两粒度),管理员走七彩石远程配置 | 对 AI 透明:写新页面只声明是否受限资源,权限自动生效 |
| **页面访问审计** | 所有请求过鉴权中间件,身份/路径/API Token 记录落库 | 可审计追踪 |
| **开放 API** | API Token 机制(Bearer/自定义 Header),路径白名单、过期时间、明文仅管理员可见 | AI 也能自助创建和管理 Token |
| **MCP 工具** | FastMCP 搭建,把专线分析/拓扑分析封装成 MCP 工具 | 供其他 AI 客户端调用 |
| **定时任务** | APScheduler 装饰器注册(`@cron_job` 声明 ID/间隔/描述),独立进程、页面管控、数据库抢占 | AI 新增任务只写业务函数,调度脚手架自动就位 |
| **工作流** | DBOS 实现 Durable Function:人工待办/异步回调/长时间任务,中断可从历史恢复 | 复杂流程能跑一个月不断 |

### 第二层:工程护栏(Harness 工程实践)

**大仓组织**:后端 `flo/` + 前端 `web/` 同一 Git 仓库(AI 一次会话看全栈,上下文完整);后端严格分层 `controllers → services → models → source` 调用只向下(写进 AGENTS.md);**每个职能目录下 `_framework/` 放框架脚手架**——业务代码只管业务函数,框架管调度与生命周期;前端 components 按业务域分,配套 Storybook story。

**Rules 三层护栏**(规则集中、分场景加载、不重复):

| 层 | 载体 | 内容 |
| --- | --- | --- |
| 第一层 | 根目录 `AGENTS.md` | 工程护栏与偏好:文件红线、后端分层规范、前端约定、DB 变更流程、图表配色、拓扑可视化偏好——AI 每次会话读,等于随身带"项目规范手册" |
| 第二层 | `.vscode/anydev_rule.md` | 研发流程约束与用户保护:三阶段流程不可绕过(需求讨论→开发实现→确认提交,每阶段需用户确认)、用户非专业开发(白话解释/先讲再动手/不做选择题)、分支管理对用户透明、Git 操作护栏、产品误区主动提醒(如"清掉数据"→提醒无 DELETE 权限建议软删除) |
| 第三层 | 插件 Memory 系统 | 项目记忆自动触发("时间字段统一 DATETIME""前端改完必须 type-check""入流量绿出流量蓝") |

**Skills 预装技能包**(Rules 保底线,Skills 提效率):Agent 创建、工作流创建、Changelog 发布、前端设计、Vue 开发、工蜂(代码平台)、**代码去腐化(两个职责分离的技能:扫描创建 issue vs 认领修复——避免既当裁判又当运动员,高频小批量定期跑)**、iWiki、技能创建。AI 遇到对应场景自动触发。

**TDD 实践与取舍**:AI 写测试很快但容易"自欺欺人"(只覆盖 happy path/断言太弱),用规则约束兜底而非追求严格"先写测试"——后端 pytest + ruff + ty check,前端 vitest + oxlint + vue-tsc,提交前必须通过;核心业务必须有后端单测(快速定位),前端 E2E 覆盖关键流程(验证整条链路),**两者互补而非替代**;覆盖率 70% 作参考不阻断,更看重"改动的文件有测试覆盖";最终更看重**验收**(页面表现符合预期,Playwright headless 截图 + 提需求人确认)。

**轻量 SDD(文档命名约定就是工作流)**:`features/` 存需求文档,按 `draft_ → ready_ → done/` 三阶段流转;方案讨论在 `ai_docs/running/` 同样遵循命名约定。AI 读完一个 `ready_` 文档就有完整需求上下文,不用人反复解释;文档本身也是 AI 协助写的(运营口述 → AI 整理结构化文档 → 开发 review → 改前缀 ready_ 开始开发)。**不用额外的项目管理工具,文件名本身就在表达状态**。

**CLI 工具**(把高频运营操作封装成"安全、留痕、可重复"的命令):

| 工具 | 职责 | 设计要点 |
| --- | --- | --- |
| `flow-db-exec` | DB 变更唯一入口 | 高危关键字(DROP/DELETE/TRUNCATE)硬拦截+账号权限双保险;强制先写 changelog.sql 再执行;结果可读 |
| `flow-config` | 业务配置管理 | 配置存数据库表 + CLI + 管理页面,与代码同仓库,AI 直接读写改完即生效;Key 按模块分层命名 |
| `run-cron` | 定时任务独立进程 | 只启动调度器不启动 API,避免重任务阻塞线上接口 |

**前端组件化**(让审查可行):Vue SFC 500 行内超即拆;子组件 100~200 行、composable 30~70 行;工具函数移 `utils/`;**所有组件配套 Storybook story(143 个,作为"组件说明书"——AI 开发新功能先看 story 了解已有能力避免重复造轮子,写完补 story 相当于自测)**;页面视图层走"智能组件 + 展示组件"模式。

**让 AI 看见问题(四层)**:①静态检查即反馈(ruff/ty/oxlint/vue-tsc 输出 AI 直接读到并自修);②AGENTS.md 汇总规则;③开发服务 AI 自主管理(`dev.sh` 统一启动,AI 自己看日志查进程);④Playwright 验证(headless 截图/检查 API/验证交互——AI 自己做 QA)。四层叠加,大部分问题 AI 会话内就能发现修复。

**DB 变更管控(极简、透明、可验证)**:所有 DDL/DML 走 `flow-db-exec` 一个入口;任何变更先落 changelog.sql(注明日期与目的)+ 同步主结构定义文件,按行号执行片段;风险分级——加字段/加索引/主键单行 UPDATE 直接执行后告知,ALTER 改字段先讲方案确认,不带主键批量 UPDATE 先 SELECT COUNT(*) 评估,DROP/DELETE/TRUNCATE 硬拦截改软删除或人工;时间字段统一 DATETIME 禁 BIGINT 时间戳(方便运营理解)。

**Agent 工作流(Everything as Code)**:不搞"平台 + 后台配置"——**提示词是文件、工具是函数、注册是装饰器**,所有产物都在代码仓库里,可追踪、可 review、可回滚。ReactAgent 基类统一模型配置/上下文注入/SSE 流式/会话持久化,新增 Agent 只关注:名字、系统提示词、工具。AI 给业务目标 → 自己探索代码库(数据模型/service/工具函数)→ 写提示词 → 封装工具 → 注册 → 端到端验证 → 交付可用 Agent。细节:SSE 流式支持断连重连(刷新不丢);**工具返回值尽量 markdown 字符串而非原始 JSON**(Agent 更好理解、token 大幅减少、人看着也方便)。

**Anydev 统一研发环境**:`scripts/system/setup.sh` 7 步全自动(上报环境/装系统依赖/装工具链/注入开发规范/渲染 private.env/装项目依赖/启动开发服务),3 分钟内从模板容器到完整可用环境,全程零人工。设计要点:每步独立可单独执行、失败即停原因清晰(`set -e` + 报具体缺项)、幂等可重跑。`private.env` 用模板 + envsubst 渲染,渲染前校验所有必填变量,缺一个直接报错,不生成"半残"配置。

### 第三层:协作机制(开发与产品协同)

- **页面级评论系统**:运营同事在页面上任意位置圈点评论(记录路径、xpath、html 片段、坐标、截图)——"所见即所得"的需求提交工具;评论状态 open/resolved/closed 全流程页面可见;复杂需求由开发同事整理成 `features/draft_` 文档走 SDD;
- **开发容器自助注册**:容器启动自动上报前后端地址/分支到 devops 管理页面,运营同事可提前验收,确认再合并;
- **能力地图**:把功能模块/Agent/定时任务/开放 API 按业务域分类罗列的结构化文档——运营同事读一遍就知道"系统能做什么",提需求有的放矢(重复提和不敢提都大幅减少)。

## 代码 / 实现:两个可运行的机制演示(纯 Python)

### 演示 1:文档命名约定 = 工作流(SDD 流转)

```python
# features/ 目录: draft_ → ready_ → done/ 三阶段流转
def advance_doc(filename: str) -> str:
    """按前缀推进文档状态;命名约定即工作流,不需要项目管理工具"""
    if filename.startswith("draft_"):
        return filename.replace("draft_", "ready_", 1)   # 方案对齐确认 → 可以开发
    if filename.startswith("ready_"):
        return f"done/{filename}"                          # 开发完成 → 归档
    return filename

for f in ["draft_出口桑基图.md", "ready_专线质量分析.md", "随便.md"]:
    print(f"  {f:24} → {advance_doc(f)}")
```

### 演示 2:DB 变更风险分级管控(flow-db-exec 的决策逻辑)

```python
HIGH_RISK = ("DROP", "DELETE", "TRUNCATE")

def decide_db_operation(sql: str, is_alter=False, has_primary_key=True, count=None):
    """DB 变更风险分级:高危硬拦截 / ALTER 先讲方案 / 批量先评估 / 其余直接执行"""
    if any(kw in sql.upper() for kw in HIGH_RISK):
        return "BLOCK", "高危操作硬拦截,改用软删除或人工执行"
    if is_alter:
        return "CONFIRM", "先讲方案,用户确认后再执行"
    if not has_primary_key and count and count > 1000:
        return "EVALUATE", "无主键批量 UPDATE,先 SELECT COUNT(*) 评估再确认"
    return "EXECUTE", "直接执行后告知"

for sql in ["DELETE FROM t WHERE id=1", "ALTER TABLE t DROP COLUMN x",
            "UPDATE t SET v=1", "INSERT INTO t VALUES (1)"]:
    verdict, reason = decide_db_operation(sql, is_alter="ALTER" in sql.upper(),
                                          has_primary_key="WHERE id" in sql)
    print(f"  [{verdict:8}] {sql:28} → {reason}")
```

## 实践 / 应用:两条场景主线与 Lessons

### 场景一:AI 原生的研发整体流程(运营同事全流程)

运营同事想加"出口流量按 AS 聚合的桑基图":从模板创建 anydev 容器(零配置)→ CodeBuddy 里白话告诉 AI 需求 → AI 对齐需求(维度/数据源/页面位置)→ AI 全栈开发(后端接口/前端组件/DB 查询,自己启动服务、跑测试、查日志)→ AI 给访问地址 → 运营同事浏览器验证 → 回"OK" → AI 自动跑静态检查 + 兜底测试 → 推送分支创建 MR → 管理员审批合并。**全程没写一行代码、没碰过 git、不知道"分支"概念**。

### 场景二:AI 原生的 Agent 开发流程

运营同事想要"专线质量分析 Agent"(输入专线 ID → 查流量趋势/丢包率/时延 → 输出质量评估+异常原因,验收标准:30 秒内输出结构化报告):AI 自己探索代码库 → 写系统提示词 → 封装工具函数 → 注册到 Agent 框架 → 自己跑端到端验证迭代(调提示词/换模型/改工具返回格式)→ 交给运营同事一个能用的 Agent。

### Lessons from AI Coding

1. **避免廉价习得感**:AI 写代码久了容易产生"我也会编程"的错觉——人看不懂就没法审查,质量无法保障。要求团队学基本概念(分层/ORM/中间件/SSE),"这个函数职责太重拆一下""这逻辑该放 service 层"比"感觉不对你再看看"有用得多——**AI 输出质量取决于人的反馈质量**;
2. **给非开发者一张"能力地图"**:运营同事不需要懂代码,但需要懂"产品语言"(导航栏/面包屑/抽屉)和系统整体能力——能力地图让提需求有的放矢;
3. **省 token**:AGENTS.md 集中规则(AI 读一次就够)、工具返回 markdown 而非原始数据(200 token vs 10 倍 JSON)、CLI 工具替代临时脚本、大仓 + 语义搜索、SDD 文档驱动、组件化 + Storybook;RTK 等 Token 压缩工具验证后效果一般(偶尔压缩出 bug/语义混淆)就放弃了——"省不了几块钱,还让 AI 依赖一个不稳定的命令行代理,得不偿失"。

## 总结

- **一句话**:搭好底座,让 AI 在上面高效干活,让团队里每个人(不管会不会写代码)都能参与建设;
- **三层架构**:基础设施(通用能力标准设施)/ 工程护栏(大仓+Rules 三层+Skills+CLI+DB 管控+TDD+SDD+组件化)/ 协作机制(页面评论+Anydev 环境+能力地图);
- **核心设计**:Everything as Code(Agent 提示词是文件、工具是函数、注册是装饰器);文档命名约定就是工作流;CLI 把高频操作封装成"安全、留痕、可重复";
- **正向循环**:基础设施越好 → AI 产出质量越高 → 人的审查负担越轻 → 人有更多精力优化基础设施;
- **设计经验提炼**:详见站内 [AI Coding Harness 设计经验](../07-agent-coding/experience/ai-coding-harness-design.md)。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/DrIpzHm777Zd8klcyAICBA;原始资料存档于 `docs/inbox/vibeflowing-source.md`
- 站内:[AI Coding Harness 设计经验](../07-agent-coding/experience/ai-coding-harness-design.md)(设计经验角度)、[得物 AI Native 研发范式](ai-native-order-system-spec-driven.md)(同为 AI 原生研发案例)、[AI 原生组织方法论](../06-enterprise/ontology-agent-adoption/ai-native-organization-methodology.md)(65% PR)、[给 Coding Agent 立规矩](../07-agent-coding/experience/agent-rules-agents-md.md)(Rules 载体)、[AI 协作规则设计](../03-agents/agent-collaboration-rules.md)(六维度规则模板)
