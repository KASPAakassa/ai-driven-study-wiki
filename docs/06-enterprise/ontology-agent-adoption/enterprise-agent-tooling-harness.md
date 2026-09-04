# 企业 Agent 工程化(四):Tool、MCP、Skills、Harness 四件套

> **一句话摘要**:Tool、MCP、Skills、Harness 常被说成一回事,本文顺着一条真实生产任务执行链拆清四件套职责——Tool 定义动作、MCP 解决接入、Skills 规定方法、Harness 管住执行轨道,并给出搭配 checklist 与最小 harness 循环代码。
>
> **来源**:微信公众号《企业 Agent 工程化手记》第 9 篇《企业 Agent 如何搭配 Tool、MCP、Skills、Harness》(企业系统开发负责人一线实践,原文链接见收件箱登记);原始资料存档于 `docs/inbox/enterprise-agent-engineering-src-b2.md`

## 概念

真正该问的不是"这四个词有什么区别",而是:**一次企业任务里,每件事到底该由谁负责?**

| 组件 | 一句话职责 | 回答的问题 | 常见误区 |
| --- | --- | --- | --- |
| **Tool** | 定义一个可执行动作 | 做什么动作? | 当成"一个能调的函数",忽略 Schema、风险、副作用 |
| **MCP** | 以统一方式接入外部能力 | 能力怎么接入? | 以为替代了 Tool;连上就算完事,不管连接是否可控 |
| **Skills** | 规定一类任务该怎么做 | 按什么方法完成任务? | 当成安全机制;写隐藏状态而非方法 |
| **Harness** | 让执行链可控、可停、可恢复、可追踪 | 谁来保证跑得住? | 没有对应模块;只剩让模型不断调工具的循环 |

四者互补,**不是在四者里选一个,而是让它们各守责任**。

!!! note "为什么必须搭配"
    越靠近生产,越不能让一层替另一层兜底。动作定义不清 → 权限/重试/审计无落点;接入混乱 → 凭据失控;方法缺失 → 没人定义"怎样才算做完整";轨道缺失 → 中断后不知从哪继续。分层的价值不是让架构图更漂亮,而是**出问题时知道该改哪里**。

## 原理

### 协作层次:四层各守责任

四者不是"Harness 调 Skill、Skill 调 MCP、MCP 调 Tool"的线性调用链,而是四个正交关注面叠在同一条执行链上:

```
用户消息
   ▼
Harness  ─ 管整个回合:消息落盘、会话恢复、权限模式、工具事件、恢复与资源释放
   │
   ├── Skills ─ 管任务方法:步骤、证据、完整性约束(N 项)、交付格式
   ├── MCP    ─ 管能力接入:连接池、工具发现、namespace、凭据生命周期
   └── Tools  ─ 管具体动作:参数 Schema、风险等级、副作用、确认边界
```

| 层次 | 负责 | 不负责 |
| --- | --- | --- |
| Harness | 状态、生命周期、权限前置检查、恢复路径、事件留痕 | 决定能力该怎么用 |
| Skills | 完成任务的方法、步骤顺序、交付完整性 | 运行状态、写入结果、恢复点 |
| MCP | 连接、工具发现、参数传递、结果返回 | 业务治理 |
| Tool | 一个可独立描述/授权/审计的动作 | 编排、恢复 |

### Tool:一份完整的动作契约

Demo 里的 Tool 是一个函数;生产级注册表里还有参数 Schema、执行方式、安全模式下是否可用、**风险等级和风险类别**:

```yaml
query_quality:
  description: 查询目标批次质量指标(只读,无副作用)
  params_schema: {batch_id: string, window: enum[1,3,7]}
  execution: read-only
  risk: low
  require_confirm: false
```

**权限不能靠名字猜,风险也不能等动作发生后再判断。** 一个"查询客户"工具若顺手更新访问时间,它就不是纯查询。

!!! warning "最小 Tool 原则"
    一个 Tool 只承担一个可独立描述、授权、审计的动作。查询/判断/写入/通知要拆开——把四种风险塞进一个巨型 Tool,不是能力强,而是把四种风险藏进了同一个黑盒。

### MCP:解决接入,不代替治理

MCP 把连接、工具发现、参数传递、结果返回收进一套协议。它与 Tool 不是替代关系:**MCP Server 最终仍向 Agent 暴露 Tool**——Tool 是 Agent 看到的动作,MCP 是这些动作进入运行环境的一种连接方式。平台用 **MCP 连接池**统一管理连接,外部 Runtime 通过受治理的 HTTP MCP 代理暴露工具,所有外部能力从**同一个受控入口**进入。

进入生产后,重点从"能不能连上"变成"连接是否可控":过滤敏感环境变量、工具列表健康检查、限制调用时间、Session 结束关闭连接并释放凭据。

### Skills:把工作方法交给 Agent

Skill 是带元数据的 **SKILL.md 指令包**:声明名称、描述、触发线索、允许的工具、所需 Source。

- **分层装载**:系统 → 配置 → 插件 → 工作区 → 项目级,越接近项目越优先——既是灵活性也是隐患(见下方案例);
- **执行强制**:匹配后先要求模型读 SKILL.md,跳过规则直接调其它工具会被前置检查拦住;
- **边界**:前置读取不是安全隔离。**Skill 管方法,不管运行状态**,可收窄选择,不能代替权限判断。

### Harness:让一次执行真正跑得住

Harness 由会话管理器、统一 Agent Backend、权限与前置检查、会话存储、MCP 连接池、事件处理**共同组成**。不同模型/SDK 底层差异很大,但统一 Backend 对上层提供同一套契约:开始对话、流式返回事件、调用工具、请求权限、处理中断、切换 Source、恢复 Session、释放资源。工具执行前统一前置检查(权限、Source 启用、读过说明、Skill 已读、Ask 确认),执行中 Tool 的开始/结果/错误/完成事件统一写入会话。

!!! tip "Harness 与 Agent Loop 的分水岭"
    只有让模型不断调工具的循环,最多算 Agent Loop。真正的 Harness 还得回答:谁拥有会话,谁做权限判断,工具失败怎么收场,事件写到哪里,中断后从哪继续——**让一次执行有生命周期、有边界、有状态、有恢复路径**。

### 案例复盘:一次批次异常分析暴露的三个坑

任务"判断生产批次是否异常并输出报告":查目标批次及可比批次 → 补充质量规则 → 找异常检查项 → 逐项查分布与统计量 → 确定性规则判断 → 编译趋势图与分布图 → 组装可验证 HTML 报告。

- **坑 1:Skill 把 7 个检查项缩成 1 个。** 候选返回 7 个唯一检查项,实际只保留第一个——Tool 没坏、MCP 没断,错的是任务方法:高优先级旧配置级 Skill 覆盖了已更新的基础版本。修复:候选 N 项,则分布查询/图表/报告区块必须都是 N 项,**少一个就补齐或失败关闭,不静默选"代表项"**。
- **坑 2:图都生成了,报告工具却调用错了。** Agent 调用 `mcp__runtime__report.generate`、`mcp__runtime__report_generate`,实际注册的是 `mcp__analysis__report.generate`——只差一个 namespace。**Tool 名表达动作,MCP namespace 说明能力来自哪条连接、哪组凭据。** 7 项证据超 16 万行被塞进报告参数,JSON 20KB+ 被截断;修复是**缩短模型边界**:模型只传结论、范围和可信引用,接入服务在同一 Session 内补齐数据再交报告生成器验证。
- **坑 3:长任务身份和状态漂移。** 报告阶段刷新凭据后读不到旧凭据创建的资源。修复:每个 Session 首次取得凭据后固定使用,建独立引用索引,关闭时一并释放。**这属于 Harness,不能塞进 Skill,也不能让 Tool 自己维护。**

**失败边界**:Agent 把有数据质量问题的结论写成 `normal`,渲染器按证据算出 `incomplete` 拒绝生成——**模型可提出结论,最终工件必须服从确定性证据**。修复是返回明确期望结论状态、允许基于原证据纠正一次;其它错误立即失败,不靠反复重试撞结果。

### 工具说明 = 接口契约,不是产品介绍

| 要素 | 要求 |
| --- | --- |
| 解决什么问题 | 明确能力边界与典型用法 |
| 什么时候不该用 | 与其它工具的重叠区、边界条件 |
| 参数结构 | 结构化参数、枚举值、必填字段、取值范围 |
| 成功和失败返回什么 | 返回格式可校验,失败有明确反馈 |

只靠自然语言描述参数,模型常生成"看起来合理但无法执行"的输入;schema 校验能显著降低失败率。

### 记忆三分与污染问题

- **工作记忆**:当前上下文窗口,最直接也最贵;放目标、状态、约束、最近观察,不放完整流水账;
- **会话记忆**:跨轮问题,存结构化摘要,不塞对话原文;
- **长期记忆**:可复用经验(偏好、领域知识、常见修复),常配向量检索;难点在**什么值得存、何时取、取回是否可信**。

最易出问题的是**旧信息污染新判断**:上次任务的临时路径、过期结论、失败假设被检索回来混进上下文。工程上要给记忆加**来源、时间、置信度和适用范围**。

### 反思落到外部验证

没有外部验证的反思是模型自我安慰。有效反思绑定**观察结果、验收标准、下一步动作**,拆成三类检查:目标是否仍清楚、证据是否支持继续、失败是否需要换路径。落到代码就是下节的 `verify(result, acceptance)`——最好是测试、schema 校验、文件检查、接口返回检查,而不是模型自述"看起来没问题"。

## 代码 / 实现

原文为工程复盘,无代码。下面用纯 Python 演示**最小 harness 循环**:候选筛选 → 模型选择 → schema 校验 → 执行 → 验证驱动反思。真实"模型"由 LLM 承担,此处用规则模拟展示 harness 骨架:

```python
# -*- coding: utf-8 -*-
"""最小 harness 循环:候选筛选->模型选择->schema校验->执行->验证反思(纯 Python)"""
TOOLBOX = {
    "query_quality": {"category": "read", "risk": "low",
        "schema": {"params": ["batch_id", "window"],
                   "types": {"batch_id": str, "window": int},
                   "required": ["batch_id"], "enum": {"window": [1, 3, 7]}}},
    "render_chart": {"category": "artifact", "risk": "medium",
        "schema": {"params": ["check_name", "data"],
                   "types": {"check_name": str, "data": list},
                   "required": ["check_name", "data"]}},
    "send_report": {"category": "notify", "risk": "high",
        "schema": {"params": ["report_id"],
                   "types": {"report_id": str}, "required": ["report_id"]}},
}
# 验收标准:外部检查,而非模型自述
ACCEPTANCE = {
    "query_quality": {"has_checks": lambda r: r.get("checks", 0) > 0},
    "render_chart": {"artifact": lambda r: "artifact" in r},
    "send_report": {"sent": lambda r: r.get("sent") is True},
}

def validate(tool_name, args):
    """纯 Python schema 校验:必填/类型/枚举/未知参数"""
    schema = TOOLBOX[tool_name]["schema"]
    errors = []
    for p in schema["required"]:
        if p not in args:
            errors.append("缺少必填参数 " + p)
    for p, v in args.items():
        if p not in schema["params"]:
            errors.append("未知参数 " + p)
        elif p in schema["types"] and not isinstance(v, schema["types"][p]):
            errors.append("参数 %s 类型错误:期望 %s,实际 %s" % (
                p, schema["types"][p].__name__, type(v).__name__))
        elif p in schema.get("enum", {}) and v not in schema["enum"][p]:
            errors.append("参数 %s 取值 %r 不在枚举 %s" % (p, v, schema["enum"][p]))
    return errors

class FakeModel:
    """极简模型:在候选内选择工具并填参;真实场景换成 LLM"""
    def choose(self, candidates, task):
        if "报告" in task:
            return "send_report"
        if "图" in task:
            return "render_chart"
        return candidates[0]
    def fill(self, tool_name, fail_once=False):
        if tool_name == "query_quality":
            return {"batch_id": "B-2026-08", "window": 3}
        if tool_name == "render_chart":
            return ({"check_name": "cpk"} if fail_once
                    else {"check_name": "cpk", "data": [1.0, 1.1, 0.9, 1.2]})
        return {} if fail_once else {"report_id": "R-1001"}

_chart_n = {"n": 0}
def run_tool(tool_name, args):
    """工具执行(打桩);高风险动作前置人工确认"""
    if tool_name == "send_report":
        print("   [harness] Ask 模式:人工确认已通过")
        return {"sent": True, "report_id": args["report_id"]}
    if tool_name == "query_quality":
        return {"batch_id": args["batch_id"], "checks": 7, "rows": 160000}
    if tool_name == "render_chart":
        _chart_n["n"] += 1
        if _chart_n["n"] == 1:
            return {"error": "timeout"}                  # 首次执行超时
        return {"artifact": args["check_name"] + ".png", "size": 2048}
    return {}

def verify(result, acceptance):
    """验证驱动反思:逐条检查验收标准,返回 (verdict, missing)"""
    missing = [k for k, c in acceptance.items() if not c(result)]
    return ("passed", []) if not missing else ("failed", missing)

def harness(task, fail_once=False, max_retry=2):
    """执行轨道:候选筛选->选择->填参->schema校验->执行->验证"""
    model = FakeModel()
    events = []
    category = "read" if "查询" in task else ("artifact" if "图" in task else "notify")
    candidates = [n for n, t in TOOLBOX.items() if t["category"] == category]
    events.append("候选工具(动作面=%s): %s" % (category, candidates))
    tool = model.choose(candidates, task)
    args = model.fill(tool, fail_once=fail_once)
    events.append("模型选择: %s, 参数: %s" % (tool, args))
    errors = validate(tool, args)
    if errors:                                          # 参数无法落地 -> 直接 help
        events.append("schema 校验拒绝: %s" % errors)
        events.append("判定: help(参数级失败,不重试,重试只是烧钱)")
        return events
    for attempt in range(1, max_retry + 1):             # 执行 + 验证驱动反思(带上限)
        result = run_tool(tool, args)
        verdict, missing = verify(result, ACCEPTANCE[tool])
        events.append("attempt %d: %s -> verify=%s %s" % (attempt, result, verdict, missing))
        if verdict == "passed":
            events.append("判定: passed,标记该步完成")
            return events
        events.append("判定: retryable,修正动作后重试" if attempt < max_retry
                      else "判定: help(超过重试上限,失败关闭或转人工)")
    return events

if __name__ == "__main__":
    print("=== 场景 A:生成分布图,首次超时 -> 重试成功 ===")
    for e in harness("生成分布图"):
        print(" ", e)
    print("\n=== 场景 B:模型漏填参数,schema 拦截 -> help ===")
    for e in harness("生成分布图", fail_once=True):
        print(" ", e)
    print("\n=== 场景 C:高风险动作进入人工确认边界 ===")
    for e in harness("发送报告"):
        print(" ", e)
```

**运行方式**:`python3 文件名.py`(纯标准库)。关键点:① **候选筛选**(`category`)——工具越多越不能把整个工具箱倒进上下文,先按动作面收窄候选再让模型选;② **schema 校验**(`validate`)——必填/类型/枚举/未知参数,参数无法落地直接 `help` 不重试;③ **验证驱动反思**(`verify`)——验收标准是外部检查(文件/接口/测试),`passed` 完成、可重试则修正后重试(有上限)、超限转 `help`;④ **高风险动作**(`send_report`)——Ask 模式人工确认后才执行,权限由前置检查保障,不依赖模型自觉。

**运行结果**:三分支全走通——场景 A `timeout → retryable → 成功 → passed`;场景 B 参数级失败直接 `help`;场景 C 人工确认边界。

## 实践 / 应用

### 四件套搭配 checklist

| 层次 | 检查项 |
| --- | --- |
| **Tool** | 一个 Tool 一个可审计动作;按动作面分级(只读/写草稿/发外部消息/改生产数据/执行 shell);参数 schema 完整(必填/枚举/类型/范围);标注风险等级与副作用;影响外部的工具带最小权限、审计日志、人工确认边界 |
| **MCP** | 只解决接入,不代替业务治理;先选 Source 再收窄 Tool,最后才谈模型怎么调用;连接池统一管理;过滤敏感环境变量;健康检查;限制调用时间;Session 结束关闭连接并释放凭据 |
| **Skills** | 写方法不写隐藏状态;模板化验证步骤(证据 → 校验 → 完整性约束 → 交付格式);候选 N 项则后续工件必须 N 项;执行位置、写入结果、恢复点放进 Harness 状态,不进 SKILL.md |
| **Harness** | 统一管权限、状态、恢复、观测;记录 run/task/step/tool call 四层事件;工具开始/结果/错误/完成事件写入会话;提供检查点与恢复路径;所有模型、Source、Tool 都绕不开的前置检查 |

### 一次任务的六步执行链(生产复盘版)

1. Harness 保存用户消息,恢复 Session,匹配"批次异常分析 Skill";
2. Skill 声明业务分析 Source、证据步骤、N 项完整性约束和交付格式;
3. MCP 连接池建立连接,把查询/图表编译/报告生成暴露为带 namespace 的 Tool;
4. Agent 按依赖层批量执行注册查询,再为每个检查项编译分布图;
5. 报告 Tool 只收结论、范围和可信引用,接入服务在同一 Session 内补齐证据并确定性校验;
6. Harness 记录工具事件、维持会话身份,处理超时、中断与资源释放。

最终验证:7 项全部独立查询、7 张分布图有效、完整 HTML 交付、Skill 契约测试通过——**"发现了 7 项,执行了 7 项,也交付了 7 项"**,而不是"看起来完成、实际缺证据"。

### 多 Agent 协调成本与三种模式

要不要上多 Agent,先回答:**任务能否清楚拆分?结果能否被独立验证?末端有无可靠合并机制?** 回答不清,多 Agent 只会放大混乱。

| 模式 | 适用 | 风险 |
| --- | --- | --- |
| 层级模式 | 边界清楚、可拆分的任务(调研、批量分析) | Manager 单点瓶颈;拆错后执行越快偏差越大 |
| 并行模式 | 互相独立的任务(同时分析几个竞品) | 必须有汇总与冲突处理,否则输出是一堆并列材料 |
| 评审模式 | 生产系统(一个生成、一个检查、必要时规则验证) | 生成与审查必须分离,降低一路错到底的概率 |

自由对话式协作最不稳定,除非有清楚的轮次限制、终止条件和评估标准。

### 框架选型三个问题

| 问题 | 含义 |
| --- | --- |
| 状态能清楚表达吗? | 能否持久化、快照、恢复 |
| 工具调用能受控吗? | 候选筛选、参数校验、权限前置检查是否有落点 |
| 失败恢复和人工介入好做吗? | 有没有明确的 help 分支与恢复路径 |

MVP 先选轻量方案验证任务是否适合 Agent;复杂生产流程优先状态表达强、可观测性好的框架;关键业务系统**不要把安全、评估和恢复能力完全交给框架默认值**。

## 总结

- **四件套回答四个问题**:做什么动作(Tool)、怎么接入能力(MCP)、按什么方法完成任务(Skills)、谁来保证跑得住(Harness)。
- **四条搭配原则**:一个 Tool 一个可审计动作;MCP 只解决接入;Skill 写方法不写隐藏状态;Harness 统一管权限、状态、恢复、观测。
- **失败边界**:模型可提出结论,最终工件服从确定性证据;允许纠正一次,其它错误立即失败。
- **反思落到外部验证**:`verify(result, acceptance)` 是测试/schema/文件/接口检查,不是模型自述。
- **排查指南**:参数错改 Tool;接入难查 MCP;步骤跑偏改 Skill;权限/恢复/留痕不可靠补 Harness。

## 延伸阅读

- 站内:[Ontology 与 Agent 企业落地](index.md)、[Agent 是什么:从聊天到任务执行](../../03-agents/agent-intro.md)、[工具调用(Tool Calling)](../../03-agents/tool-calling.md)、[多 Agent 协作的真相](../../03-agents/multi-agent.md)、[Agent 框架选型](../../03-agents/agent-frameworks.md)、[Harness 与工具边界](../../08-harness/harness-tools.md)
- 外部:微信公众号《企业 Agent 工程化手记》第 9 篇《企业 Agent 如何搭配 Tool、MCP、Skills、Harness》;原始资料存档于 `docs/inbox/enterprise-agent-engineering-src-b2.md`
