# 生产级 Agent 架构:权限洋葱、多 Agent 协作与容错恢复

> **一句话摘要**:把"能跑的 Agent"变成"能上线的 Agent",缺的不是更强的模型,而是**权限、协作、容错、部署**四件事。本文拆解 Claude Agent SDK 的六层权限洋葱、子 Agent 协作与分层容错机制,给出可落地的生产设计清单。
>
> **来源**:微信公众号「数字拾荒」《生产级 Agent 应用架构》(Claude Agent SDK 系列第六篇·终篇),https://mp.weixin.qq.com/s/Iq5qXb0NZhZLbCThIvhIlQ;参考 Claude Agent SDK 官方文档(Permissions / Multi-Agent / Hosting / Secure Deployment / Cost Tracking);原始资料 `docs/inbox/agent-production-architecture-source.md`

## 概念:从原型到生产差什么

Agent 功能"齐活"很容易:一个循环 + 几个工具 + 一点记忆,就能跑出 Demo 效果。但要上生产,还差**最关键的一环——安全、权限和容错**。

!!! note "系列定位"
    Claude Agent SDK 系列前五篇:Agent Loop、自定义工具、Hooks、Session(记忆与回滚)、流式输出——功能层面就此齐活,本文补上**生产架构**最后一环。生产与原型差什么?原型关心"能不能把任务做完",生产关心"能不能**安全、可控、可恢复**地做完"——即**权限**(六层洋葱)、**协作**(子 Agent)、**容错**(分层 + 检查点 + Session)、**部署**(三模式 + 成本/观测)。

!!! tip "与站内文章的定位分工"
    [9 层架构](ai-infra-layering.md) 是**概念全景**、[大规模 Agent 系统设计](agent-system-scaling.md) 是**演进路径**;本文是 **Claude Agent SDK 的具体实现方案**。[企业落地(四道防线/运维治理)](../06-enterprise/ontology-agent-adoption/enterprise-agent-production-deployment.md) 由另一篇负责,本文只讲机制。

## 原理

### ① 权限六层洋葱:一次工具调用的完整旅程

Claude 请求使用工具时,SDK 按**严格顺序**评估:`Hooks → Deny → Ask → Permission Mode → Allow → canUseTool`,**任何一层都可终止评估链**。

| 顺序 | 层 | 核心行为 |
| --- | --- | --- |
| 1 | **Hooks** | 最先执行;**deny 终止,allow 不跳过后续** |
| 2 | **Deny** | 黑名单,**全模式生效**(含 bypass) |
| 3 | **Ask** | 命中则路由 canUseTool;dontAsk 下**直接拒绝** |
| 4 | **Permission Mode** | 全局开关;bypass 放行,dontAsk 拒白名单外 |
| 5 | **Allow** | 白名单命中**即放行** |
| 6 | **canUseTool** | 兜底:allow / deny / `updatedInput` 改写 |

!!! warning "三个最容易被误解的点"
    1. **Hook 的 allow 不跳过后续 deny/ask 规则**,只代表"这一层没意见";
    2. **Deny 规则在 bypassPermissions 下依然生效**;裸名(如 `Bash`)移除工具,作用域(如 `Bash(rm *)`)拦截调用;
    3. **dontAsk 模式下 canUseTool 永不触发**,未预批准一律拒绝。

### ② 六种 Permission Mode

| 模式 | 行为 | 适用场景 |
| --- | --- | --- |
| `default` | 未匹配规则的工具触发 canUseTool | 默认 |
| `dontAsk` | **未预批准一律拒绝,永不弹确认** | 生产锁定、无人值守 |
| `acceptEdits` | 自动批准文件编辑和文件系统操作 | 编码 Agent |
| `bypassPermissions` | 全部放行(除非显式 ask 规则) | 受信环境、沙箱内 |
| `plan` | 只读模式,编辑工具强制确认 | 规划/方案阶段 |
| `auto` | 分类器自动判断(仅 TS) | 权衡安全与效率 |

### ③ 锁定模式:最小权限白名单

生产环境最推荐 **`allowedTools` + `dontAsk`**——白名单外的一切都被拒绝,无需人工介入:

```typescript
for await (const m of query({
  prompt: "分析项目代码质量",
  options: {
    allowedTools: ["Read", "Glob", "Grep"],  // 只读
    permissionMode: "dontAsk",               // 白名单外拒绝
    maxTurns: 15,
  },
})) { /* Agent 只能读取文件 */ }
```

!!! note "白名单兜底"
    Deny 是"已知的坏",追不上未知威胁;`allowedTools + dontAsk` 是"未知即拒绝"。

### ④ canUseTool:运行时动态审批

需要人工审批时(如执行危险命令),`canUseTool` 提供运行时拦截:返回 `allow` 批准(可带 `updatedInput` 改写参数),或 `deny` + `message` 拒绝(Claude 看到原因后调整策略)。典型策略:读类自动放行;Bash 弹窗审批;文件编辑展示 diff 后放行。

### ⑤ 子 Agent 权限继承:只能收紧,不能放松

**当父 Agent 使用 `bypassPermissions`、`acceptEdits` 或 `auto` 模式时,所有子 Agent 自动继承且不可覆盖**——**权限只能收紧,不能放松**,宽严搭配应在父层完成。

### ⑥ 多 Agent 协作:三种创建方式与四个核心优势

单个 Agent 处理所有任务会导致**上下文膨胀、工具集过大、指令冲突**。子 Agent 机制把复杂任务分解给专门的 Agent,各自拥有独立上下文、工具集与系统提示。

| 创建方式 | 定义位置 | 特点 | 适用场景 |
| --- | --- | --- | --- |
| **编程式定义**(推荐) | `query()` 的 `agents` 参数 | 随任务动态配置 | 应用内定制 |
| **文件系统定义** | `.claude/agents/*.md` | 团队共享的固定配置 | 团队协作、复用 |
| **内置通用 Agent** | 无需定义 | 随时通过 `Agent` 工具调用 | 临时子任务 |

| 核心优势 | 机制 | 价值 |
| --- | --- | --- |
| **上下文隔离** | 独立对话,只回传最终结论 | 主上下文精简,免中间污染 |
| **并行执行** | 多个子 Agent 可并发运行 | 总耗时 = 最慢的那个,而非三者之和 |
| **专业化指令** | 独立系统提示 | 针对特定任务深度优化,无指令冲突 |
| **工具限制** | 只能使用显式授予的工具 | 审查 Agent 不需要编辑权限 |

!!! tip "混合模型策略"
    按复杂度分配:主 Agent 用 Opus 决策,子 Agent 用 Sonnet 分析、Haiku 跑模板化工作;`modelUsage` 按模型统计成本。

**AgentDefinition 配置字段:**

```typescript
interface AgentDefinition {
  description: string;          // 何时使用(驱动自动委派)
  prompt: string;               // 系统提示
  tools?: string[];             // 允许的工具(省略则继承)
  disallowedTools?: string[];   // 禁止的工具
  model?: string;               // haiku|sonnet|opus|inherit|模型 ID
  maxTurns?: number;            // 最大轮次
  mcpServers?: (string|object)[]; // MCP 服务器
}
```

### ⑦ 错误处理与恢复:四层容错

**1) 进程级:SDK 异常层级** —— `ClaudeSDKError` 为基类:`CLINotFoundError`(找不到 CLI)、`CLIConnectionError`(连不上 CLI 进程)、`ProcessError`(进程异常退出,含 `exit_code`/`stderr`)、`CLIJSONDecodeError`(JSON 解析失败)、`MessageParseError`(消息 schema 不符)。

**2) 任务级:分层 try-catch + result subtype**

- **超时**:`AbortController` 到点 abort,捕获后重试;
- **进程错误**:`ProcessError` 按**指数退避**(`1000 * attempt` ms)重试到上限;
- **不可恢复错误**(如 `CLINotFoundError`):直接上抛;

| subtype | 含义 | 处理策略 |
| --- | --- | --- |
| `success` | 正常完成 | 返回结果与成本 |
| `error_max_turns` | 陷入循环耗尽轮次 | **缩小任务范围**重试 |
| `error_during_execution` | 执行中出错 | 记录日志后重试 |

**3) 文件级** `rewindFiles` 检查点:任务失败自动恢复到开始前状态,可结合 subtype 回滚。

**4) 会话级** `resume`:恢复之前的会话 ID,成功则清掉、失败则自动保存续跑;跨容器恢复依赖共享 SessionStore(如 Redis)。

!!! note "恢复策略要分层"
    超时重试、轮次耗尽缩小范围、退避、回滚、续跑——每层解决一种失败;混在一起会过度重试烧钱,或漏掉可恢复场景。

## 代码 / 实现

原文为 TypeScript SDK 代码。下面用**纯 Python** 实现权限六层洋葱的评估链,输出每一层的判断与最终裁决,直接演示 deny 拦截 / ask 审批 / dontAsk 拒绝 / allow 放行:

```python
# 权限六层洋葱评估链:纯 Python 实现,评估顺序见 _check

class ToolCall:
    def __init__(self, name, **kw):
        self.name, self.input = name, kw

    def __repr__(self):
        return f"ToolCall({self.name}, {self.input})"


class PermissionChain:
    """按严格顺序评估一次工具调用,记录每一层的结果与最终裁决。"""

    def __init__(self, hooks=None, disallowed=(), ask_rules=(),
                 allowed=(), mode="default", can_use_tool=None):
        self.hooks = hooks or {}           # {tool_name: (call)->"allow"|"deny"}
        self.disallowed = set(disallowed)  # 裸名 Deny:直接移除工具
        self.ask_rules = set(ask_rules)    # ask 规则:匹配则走 canUseTool
        self.allowed = set(allowed)        # allow 规则:自动批准
        self.mode = mode                   # 六种 PermissionMode 之一
        self.can_use_tool = can_use_tool   # (name, input)->{"behavior": ...}

    def evaluate(self, call):
        trace = []
        ok, reason = self._check(call, trace)
        return ok, reason, trace

    def _check(self, call, trace):
        name = call.name
        # 1) Hooks 最先执行;deny 终止,allow 不跳过后续
        if name in self.hooks:
            r = self.hooks[name](call)
            trace.append(("1.Hooks", r))
            if r == "deny":
                return False, "Hook 直接拒绝"
        else:
            trace.append(("1.Hooks", "no-hook"))
        # 2) Deny 全模式生效(含 bypassPermissions)
        if name in self.disallowed:
            trace.append(("2.Deny", "deny"))
            return False, "Deny 规则拦截(工具已移除)"
        # 3) Ask 规则
        if name in self.ask_rules:
            if self.mode == "dontAsk":
                trace.append(("3.Ask", "deny(dontAsk)"))
                return False, "dontAsk 模式:ask 规则调用被直接拒绝,永不弹确认"
            trace.append(("3.Ask", "route-to-canUseTool"))
        # 4) Permission Mode
        if self.mode == "bypassPermissions":
            trace.append(("4.Mode", "bypass"))
            return True, "bypassPermissions 全部放行"
        if self.mode == "dontAsk" and name not in self.allowed:
            trace.append(("4.Mode", "deny(dontAsk)"))
            return False, "dontAsk 模式:白名单外一律拒绝"
        # 5) Allow 规则
        if name in self.allowed:
            trace.append(("5.Allow", "allow"))
            return True, "Allow 白名单放行"
        # 6) canUseTool 兜底(dontAsk 下永不触发)
        if self.can_use_tool:
            r = self.can_use_tool(name, call.input)
            trace.append(("6.canUseTool", r["behavior"]))
            if r["behavior"] == "allow":
                return True, f"canUseTool 审批通过, updatedInput={r.get('updatedInput')}"
            return False, f"canUseTool 拒绝: {r.get('message', '')}"
        return False, "未匹配任何权限,默认拒绝"


def print_verdict(call, chain):
    ok, reason, trace = chain.evaluate(call)
    print(f"\n工具调用: {call}")
    for layer, r in trace:
        print(f"   {layer:<20} -> {r}")
    print(f"   最终裁决 -> {'PASS' if ok else 'DENY'} | {reason}")


def human_approval(name, inp):
    print(f"      [人工审批] Agent 想执行: {inp.get('command')}")
    return {"behavior": "allow", "updatedInput": {**inp, "approved": True}}


chain = PermissionChain(
    hooks={"Bash": lambda c: "allow"},  # PreToolUse 钩子:我这一层没意见
    disallowed=["WebFetch"],            # 裸名 Deny:Claude 看不到这个工具
    ask_rules={"Bash"},
    allowed=["Read", "Glob", "Grep"],
    mode="default",
    can_use_tool=human_approval,
)

print("=" * 62)
print("场景 A:default 模式(只读 + Bash 人工审批)")
print_verdict(ToolCall("Read", file_path="main.py"), chain)
print_verdict(ToolCall("WebFetch", url="https://evil.example"), chain)
print_verdict(ToolCall("Bash", command="rm -rf /tmp/agent_ws"), chain)

locked = PermissionChain(allowed=["Read", "Glob", "Grep"], mode="dontAsk")
print("=" * 62)
print("场景 B:锁定模式(dontAsk + 只读白名单)")
print_verdict(ToolCall("Read", file_path="a.py"), locked)
print_verdict(ToolCall("Bash", command="curl http://evil.example"), locked)
```

- **场景 A**:Read 第 5 层 Allow 放行;`WebFetch` 第 2 层 Deny 拦截;`Bash` 命中 ask 规则,由 canUseTool 审批放行并改写参数;
- **场景 B**:白名单内 Read 放行,白名单外 Bash 第 4 层直接拒绝,**canUseTool 永不触发**;
- 关键设计:**Hook allow 不跳过后续层**、**dontAsk 下 ask 规则直接拒绝**、**未匹配任何规则默认拒绝**。

再演示**分层容错恢复循环**(超时 → 指数退避重试 → 上限返回失败):

```python
import time


def run_agent_task(attempt):
    """模拟 Agent 任务:前 2 次超时,第 3 次成功"""
    if attempt < 3:
        raise TimeoutError(f"CLI 进程无响应(尝试 {attempt})")
    return {"subtype": "success", "num_turns": 12, "total_cost_usd": 0.31}


def run_with_recovery(max_retries=3, base_delay=0.1):
    """超时 -> 指数退避重试 -> 上限返回失败(模拟 AbortController 超时)"""
    for attempt in range(1, max_retries + 1):
        try:
            result = run_agent_task(attempt)
            print(f"  尝试 {attempt}: 成功,{result['num_turns']} 轮,${result['total_cost_usd']}")
            return {"success": True, **result}
        except TimeoutError:
            delay = base_delay * 2 ** (attempt - 1)   # 指数退避:0.1s -> 0.2s -> 0.4s
            print(f"  尝试 {attempt}: 超时;{delay:.1f}s 后重试")
            time.sleep(delay)
    return {"success": False, "reason": "达到最大重试次数"}


print("\n恢复循环运行结果:")
print(run_with_recovery())
```

- 运行方式:`python3` 直接运行,无第三方依赖,均已实测通过;
- 与真实 SDK 的对应:超时→`AbortController`;进程错误→`ProcessError`;轮次耗尽→`error_max_turns` 缩小范围;未知错误→上抛而非无限重试。

## 实践 / 应用

### 部署三模式:子进程模型决定部署形态

SDK 的 `query()` 每次调用都会启动一个 `claude` CLI 子进程、通过 stdio 通信——**部署架构由会话生命周期决定**:

| 模式 | 生命周期 | 适用场景 | 工程要点 |
| --- | --- | --- | --- |
| Ephemeral 短任务 | 一容器一任务 | 一次性任务 | 冷启动要快 |
| Long-running 长驻 | 持久容器多进程 | 持续服务 | `startup()` 预热;按最大并发数规划内存 |
| Hybrid 混合 | 按需启动 + SessionStore | 交互间隔长 | **SessionStore 必需**,否则销毁即丢 |

### 完整生产示例:代码审查 Agent(检查表)

原文把全部机制组合成一个可部署的代码审查 Agent,提炼为检查表:

| 维度 | 配置 | 目的 |
| --- | --- | --- |
| 权限锁定 | `allowedTools=["Read","Grep","Glob","Agent"]` + `dontAsk` | 只读 + 不弹确认 |
| 多 Agent 并行 | 质量 + 安全两个子 Agent(`sonnet`) | 并行审查,耗时 = 最慢者 |
| 超时控制 | `AbortController` 120s | 防止无限挂起 |
| 流式输出 | `includePartialMessages: true` | 实时展示进度 |
| Session 持久化 | `sessionStore` + `resume` | 崩溃后续跑 |
| 成本追踪 | `total_cost_usd` + `modelUsage` | 单任务/按模型记账 |

### 与站内文章的分工与交叉引用

- [生产级 Agent 9 层架构](ai-infra-layering.md):权限洋葱对应 **L5 工具执行层**与横切"安全治理";
- [大规模 Agent 系统设计](agent-system-scaling.md):子 Agent 并行与混合模型 = "分级路由降本"的单任务内实现;
- [Subagent:复杂任务的上下文隔离与职责分工](subagent-isolation.md):从任务契约讲子 Agent,本文从 SDK 配置讲;
- [Agent 架构设计体系(系列导读)](agent-architecture-series.md):"权限内聚/子 Agent 工具子集"等源码设计与六层洋葱相互印证;

## 总结

- **权限**:六层洋葱严格求值,任何一层可终止;生产首选 `allowedTools + dontAsk`;
- **协作**:子 Agent 四大优势(隔离/并行/专业化/工具限制);**权限继承只收不松**,宽严在父层;
- **容错**:进程级(SDK 异常分层 + 指数退避)、任务级(subtype 分流)、文件级(rewindFiles)、会话级(resume)四层配合;
- **部署**:按会话生命周期选 Ephemeral / Long-running / Hybrid,Hybrid 必须配 SessionStore;
- 核心洞察:**能跑的 Agent → 能上线的 Agent,靠权限、协作、容错、部署**——能力是模型给的,可靠性是架构给的。

## 延伸阅读

- 站内:[9 层架构](ai-infra-layering.md)、[大规模 Agent 系统设计](agent-system-scaling.md)、[Subagent](subagent-isolation.md)、[Agent 架构系列导读](agent-architecture-series.md)、[多 Agent 协作](multi-agent.md)
- 外部:原文 https://mp.weixin.qq.com/s/Iq5qXb0NZhZLbCThIvhIlQ;Claude Agent SDK 官方文档(Permissions / Multi-Agent / Hosting / Secure Deployment / Cost Tracking,https://platform.claude.com/docs/en/agent-sdk/overview);资料存档 `docs/inbox/agent-production-architecture-source.md`
