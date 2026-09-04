# Agent Hook 使用指南:切面机制、挂载点与框架对比

> **一句话摘要**:Agent 框架普遍提供 Hook(又称 Callback)机制——围绕"模型调用"和"工具调用",各有执行前/后暴露切面。框架到点自动回调,同一切面可挂多个、按序执行。本文从**使用角度**讲清:五个核心切面各挂什么逻辑、ADK 总结的 8 种 Hook 设计模式、DECO 十余个 Hook 的实际分类,以及"原生够用 vs 必须自研"的判断。
>
> **来源**:微信公众号「腾讯程序员」《Agent 治理:用 Hook 堵住 LLM 的偷懒、越权与失忆》(作者:xiangnzhang,DECO 实践系列·护栏层),https://mp.weixin.qq.com/s/ISwjIw5lj7JlcQJV7BOx5g;设计角度见站内 [Agent 治理设计](../../03-agents/agent-governance-hooks.md);原始资料存档于 `docs/inbox/deco-hooks-source.md`

## 概念:Hook 是什么

Hook 是 Agent 框架在运行关键节点暴露的**切面**(Aspect):框架在"模型调用"和"工具调用"的执行前/后各有一个回调点,开发者把拦截/增强逻辑挂载到这些切面上——到点框架自动回调,**同一切面可挂多个、按序执行**。

!!! tip "设计原则"
    基础设施和推理逻辑解耦——Hook 切面上的逻辑独立运作,模型的 ReAct 循环不用感知;**新增/删除一个 Hook,主流程一行代码都不用改**。这就是"横切关注点"在 Agent 框架里的落地。

## 原理:五个核心切面与 ADK 8 种模式

### 核心切面(挂什么、什么时候触发)

| 切面 | 触发时机 | 典型用途 |
| --- | --- | --- |
| **beforeTool** | 工具真正执行前(可改入参、可直接拦截) | 长脚本写回前加载全文、危险操作确认(HITL 门禁)、SQL 执行前存盘 |
| **afterTool** | 工具执行后、结果回给 LLM 前(可改返回值) | 长脚本拉取后替换成引用句柄、血缘响应落盘、工具返回格式化 |
| **beforeModel / afterModel** | 每次请求 LLM 前/后 | 响应用户取消、请求/响应修改 |
| **beforeAgent / afterAgent** | 单个 Agent 运行前/后 | 对话持久化 |

### ADK 总结的 8 种 Hook 设计模式(行业通用分类)

| 模式 | 说明 | DECO 对应示例 |
| --- | --- | --- |
| **防护栏与策略执行** | before_xxx 拦截,违规直接返回预设响应 | HITL 门禁(DangerousToolGuard) |
| **动态状态管理** | 回调中读写 state 做跨步骤传递 | offload 元数据写 state |
| **日志与监控** | 关键点埋结构化日志 | ToolCallLogHook(toolName@threadId 配对) |
| **缓存** | before_xxx 查缓存命中直返 | 反向模式:查文件缓存回填 |
| **请求/响应修改** | 修改 LlmRequest 或工具入参/出参 | offload/onload 核心机制 |
| **条件跳过步骤** | 返非空结果阻止后续执行 | Guard 返短路值 |
| **认证与摘要控制** | 工具级 auth、跳过 LLM 摘要 | — |
| **工件处理** | save/load artifact | COS 落盘 read-only snapshot |

## 代码 / 实现:Hook 链编排的最小演示(纯 Python)

把"多个 Hook 挂同一切面、按序执行"与"一次会话沿流水线跑"落成可运行实现:

```python
# —— Hook 链:挂载点 → 多个 Hook 按序执行 ——
class HookChain:
    EVENTS = ("beforeModel", "afterModel", "beforeTool", "afterTool",
              "beforeAgent", "afterAgent")

    def __init__(self):
        self.hooks = {e: [] for e in self.EVENTS}

    def on(self, event, fn):
        self.hooks[event].append(fn)

    def fire(self, event, ctx):
        """到点自动回调:同一切面多个 Hook 按挂载顺序执行,可改写 ctx"""
        for fn in self.hooks[event]:
            ctx = fn(ctx) or ctx
        return ctx

# —— 挂载:一个"危险工具守卫" + 一个"调用日志"挂在 beforeTool ——
chain = HookChain()

def guard(ctx):                                   # 按序第 1 个:拦截危险工具
    if ctx["tool"] in {"packCommit", "deployCommit"} and not ctx.get("authorized"):
        ctx["blocked"] = "危险操作:需用户确认(HITL)"
    return ctx

def log_call(ctx):                                # 按序第 2 个:记录调用
    ctx["log"] = f"{ctx['tool']} @ {ctx['step']}"
    return ctx

chain.on("beforeTool", guard)
chain.on("beforeTool", log_call)

# —— 模拟一次会话:每一步工具调用都经过 Hook 链 ——
session = [{"tool": "read_file",   "step": 1},
           {"tool": "str_replace", "step": 2},
           {"tool": "packCommit",  "step": 3, "authorized": False}]
for step in session:
    ctx = chain.fire("beforeTool", step)
    status = "BLOCKED" if ctx.get("blocked") else "ALLOWED"
    print(f"  [{status}] {ctx['log']}" + (f" ← {ctx['blocked']}" if ctx.get("blocked") else ""))
```

## 实践 / 应用:DECO 实际挂载的 Hook 全景与框架对比

### DECO 十余个 Hook 的分类(直接可借鉴的清单)

| 分类 | Hook 示例 | 挂载点 |
| --- | --- | --- |
| 长文本护栏 | TaskScriptOffload/Onload、TableColumnsOffload、DdlBodyOffload | afterTool / beforeTool |
| 危险操作护栏 | DangerousToolGuard(配置驱动,requiredState + 确认框) | beforeTool |
| 工具返回处理 | LineageResponseOffload、ToolResponseTruncator、ToolResponseFormatter | afterTool |
| 可观测与持久化 | ToolCallLogHook、LoggingHook、ConversationPersistenceHook | 多点 |
| 前端刷新与业务事件 | SqlExecuteHook、CopyFileHook、ReleaseItemCollectorHook、DocumentSaveHook | before/afterTool |
| Hook→Attachment 联动 | RiskAnalysisHook、PythonImageHook | before/afterTool |
| 沙箱环境 | EnvVarCaptureHook | afterTool |

### 行业框架对比(HITL 与 offload 两个维度)

**HITL 开箱程度对比**:

| 框架 | 开箱程度 | 交互模式 |
| --- | --- | --- |
| ADK ToolConfirmation | ✅ 一行配置(yes/no + payload) | 布尔确认,无原生多选 UI |
| LangGraph HITL Middleware | ✅ 声明式 interruptOn | approve / edit / reject / respond |
| Claude Code PreToolUse | ✅ shell 脚本 + permissionDecision | deny / allow / ask |
| DECO DangerousToolGuard | ❌ 需自研 | 多选项 + 带输入控件 + 变更预览 |

**长文本 offload 对比**(读侧 vs 写侧):

| 工程 | 读侧 | 写侧 | 自动化程度 |
| --- | --- | --- | --- |
| ADK Artifacts | ✅ save/load_artifact + 示例 | ❌ 需工具内手动调 | ⚠️ 每个工具手动调用 |
| LangGraph DeepAgents | ✅ >20k token 自动落盘 | ❌ 只做读侧 | ✅ 中间件全自动 |
| Claude Code | ❌ 无 offload(Read 分页) | ❌ | — |
| DECO(自研) | ✅ 读侧 offload | ✅ **写侧 onload**(框架协议) | ✅ 全自动 + 参数交换契约 |

### 何时用原生、何时自研(两条判断)

1. **只需要"调危险工具前问一声 yes/no"** → 直接用 ADK 原生 ToolConfirmation / LangGraph interruptOn,一行配置,框架处理暂停/恢复/防循环——**恰是自研最易出 bug 处**;
2. **需要"业务级集成确认"**(发布前展示变更清单 COMMIT_PREVIEW / 确认框带参数 / 危险清单配置驱动 / 与 SSE 流式一体)→ 才值得自研——**框架的 HITL 是"工具级通用拦截",你要的是"业务级集成确认"**;
3. **长文本 offload**:读侧用框架原生机制即可;有"把长产物原样发回外部 API"的场景(如数仓保存工具)才需要写侧 onload 自研。

## 总结

- **Hook 机制**:围绕模型/工具调用各前/后暴露切面,同一切面多 Hook 按序执行;基础设施与推理逻辑解耦;
- **五个核心切面**:beforeTool(拦截/改入参)、afterTool(改返回值)、before/afterModel、before/afterAgent;
- **8 种模式**:防护栏/动态状态/日志监控/缓存/请求响应修改/条件跳过/认证摘要/工件处理;
- **两条判断**:通用 HITL 用框架原生;业务级集成确认与写侧 offload 才自研;
- **一句话**:prompt 定意图,Skill 定规矩,**框架 Hook 定边界**——能用确定性兜底的,别交给模型。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/ISwjIw5lj7JlcQJV7BOx5g;设计角度:[Agent 治理设计](../../03-agents/agent-governance-hooks.md)(三类问题三道护栏)
- 站内:[生产级 Agent 架构](../../03-agents/agent-production-architecture.md)(权限/容错)、[企业 Agent 上生产的四道防线](../../06-enterprise/ontology-agent-adoption/enterprise-agent-production-deployment.md)、[AI Coding Harness 设计经验](ai-coding-harness-design.md)(护栏生长)、[给 Coding Agent 立规矩](agent-rules-agents-md.md)(硬约束兜底)、[Agent 架构反熵增](../../03-agents/agent-architecture-antientropy.md)
