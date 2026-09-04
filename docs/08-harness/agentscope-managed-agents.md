# AgentScope 2.0:专为 Managed Agents 而生的 Harness 底座

> **一句话摘要**:Managed Agents(托管 Agent)让推理、编排、Harness 管理由云端统一承担——长任务不依赖本地在线,业务开发者不再拼装 Harness。AgentScope 2.0 的 `HarnessAgent` + 文件系统/沙箱抽象,正是数据面与 Hands(工具执行)的内核:同一套 Harness,既能做分布式 Agent Framework,又能撑起企业级 Managed Agents 底层 Runtime。
>
> **来源**:微信公众号《专为 Managed Agents 而生的 Harness 底座:AgentScope 2.0》(作者:刘军),https://mp.weixin.qq.com/s/rAla7_6DXhMuBM8YQn_I9Q;项目:https://github.com/agentscope-ai/agentscope-java;文档:https://java.agentscope.io;原始资料存档于 `docs/inbox/agentscope-source.md`

## 概念:Managed Agents 是什么

Managed Agents 让 Agent 运行在云端:推理、编排、Harness 管理等核心环节**云端统一托管**;长周期任务不再依赖本地设备持续在线——电脑关机,任务依然在云端继续跑。

与传统低代码 Agent 平台相比,Managed Agents 在 Harness 时代突出两点:

1. **不再让业务开发者拼装 Harness**:记忆维护、上下文压缩、状态恢复、工具权限、子任务回收这些通用工程能力收进统一 Harness;开发者只定义业务相关的 **Skills、Tools、Subagents 和权限策略**。平台升级 Harness,所有 Agent 共享同一套工程改进;
2. **让客户掌握工具执行和数据回传边界**:刻意拆分 **Brain(推理编排)与 Hands(工具执行)**——Brain 负责下一轮推理、状态恢复、上下文管理;Hands 负责真正接触文件、网络与业务系统,可运行在平台托管的 Cloud Sandbox,也可运行在客户 VPC 内的 Self-hosted Worker。

!!! tip "Anthropic 的三层递进(状态归属逐步上移)"
    ```
    Claude Code CLI      → Agent 与本地工作区/终端/会话直接结合
    Claude Agent SDK     → Session/事件流/工具交互 API 化,身份租户由接入方负责
    Managed Agents       → Agent/Environment/Session/执行面变托管资源,平台管版本/权限/运行时治理
    ```

## 原理:AgentScope 2.0 为什么适合做底座

### HarnessAgent:ReActAgent 之上装配工程默认项

`HarnessAgent` 在 `ReActAgent` 之上通过 **Hook 机制**装配长期运行所需的能力:

- **工作区驱动的人格与知识**:`AGENTS.md` / `MEMORY.md` / `KNOWLEDGE.md` 注入系统提示;
- **会话持久化**:按 sessionId 恢复 Agent 状态,进程重启后仍能续聊;
- **压缩与溢出处理**:默认启用 compaction 与 tool-result eviction(大结果淘汰到文件系统,上下文只留可检索引用),阈值可覆盖;
- **Skills / Subagents**:工作区 skills、任务委派(`task` 等)开箱可用;
- **统一文件系统抽象**:本地、远程 KV、云沙箱(E2B)走同一套工具语义——用 Environment 类型切换执行面,不改 Agent 业务定义。

!!! note "HarnessAgent 与 Session 不是同一生命周期"
    HarnessAgent 是在共享 `AgentStateStore` 与可恢复 Workspace 后端上**可重建的运行对象**;Session 是**有稳定 ID、事件序列和持久状态的产品资源**。分清两者才能做水平扩展:节点挂掉可以丢弃 Java 对象,但对话与长期记忆必须从共享状态恢复。

### 平台三层:控制面 / 数据面 / Worker

!!! tip "一句话分层"
    **控制面管"定义与权限",数据面管"跑起来并记下来",Worker 管"在谁的机器上动手"**;AgentScope 2.0 是数据面与 Hands 的内核,不重新实现推理循环。

| 层 | 职责 | 关键状态/资源 |
| --- | --- | --- |
| **控制面** | 定义什么可以运行、谁可以使用:Agent 静态定义与版本、Model/Skills/MCP/Tools/Environment/Memory/Vault/Resources;变更治理(版本快照、key rotate、archive 而非物理删除) | 资源按"定义/引用/挂载"三种关系组织;Environment 是执行面模板(`local/sandbox/remote/self_hosted`) |
| **数据面** | 让 Session 真正运行并完整记录:模型调用、ReAct loop、Harness hooks、turn 租约、Session 状态机、事件持久化、SSE 推送、interrupt/HITL/外化工具结果续跑 | 四类生命周期状态:Session 事件、AgentStateStore、Workspace 文件、外部副作用——**必须分别恢复再用事件 ID/tool call ID 重新关联** |
| **Worker** | 工具从 Brain 到达真正的执行环境:全托管(Brain 主动调 E2B/FC Sandbox)vs Self-hosted(客户 Worker 出站 poll) | Work 状态机:`queued → starting → active → stopping → stopped` |

### 工具执行的两条路径

| 维度 | 全托管(Cloud Sandbox) | Self-hosted |
| --- | --- | --- |
| 谁发起执行 | Brain 主动调用 E2B 兼容沙箱 API | 客户侧 Worker 主动出站 poll 队列 |
| 沙箱生命周期 | 平台掌握句柄,统一设置超时/快照/回收 | 客户 Worker 负责本地沙箱存活、重复任务安全、结果脱敏 |
| 故障责任 | Brain 知道沙箱句柄 | Brain 只知道 work 状态与工具结果,客户定义业务工具幂等语义 |
| 信任边界 | 平台托管 | 数据库/代码库/发布系统留在客户边界内 |

!!! warning "恢复一致性"
    Cloud Sandbox 采用快照/TAR 持久化时,**恢复策略必须与 AgentStateStore 一起设计**——"恢复了模型上下文却没恢复文件"(或反之),会造成"Agent 记得做过、工作区却不存在"的不一致。生产系统必须把两者当作**一个恢复单元**。

## 代码 / 实现:Work 状态机与执行路径分发(纯 Python 演示)

```python
# —— Work 状态机(工具任务的生命周期)——
WORK_FLOW = {"queued": "starting", "starting": "active", "active": "stopping", "stopping": "stopped"}

def advance(state: str) -> str:
    return WORK_FLOW.get(state, "terminal")

def simulate_work():
    s = "queued"
    log = [s]
    while s != "stopped":
        s = advance(s)
        log.append(s)
    return log

# —— 工具执行路径分发(同一工具调用,三种 Hands 位置)——
def execute_tool(tool_call: str, mode: str) -> str:
    if mode == "local":
        return f"[Local] Brain 进程内直接执行 {tool_call} —— 开发联调用"
    if mode == "cloud_sandbox":
        return f"[Cloud Sandbox] Brain 主动调 E2B/FC 沙箱执行 {tool_call} —— 平台管句柄"
    if mode == "self_hosted":
        return (f"[Self-hosted] {tool_call} 入队(queued→active) → "
                f"客户 Worker 出站 poll → 本地执行 → user.tool_result 回传续跑")
    return "unknown"

print("Work 生命周期:", " → ".join(simulate_work()))
for mode in ["local", "cloud_sandbox", "self_hosted"]:
    print(execute_tool("write_file(draft.md)", mode))
```

**Agent 定义(API 示例,`Agent 定义不变,Hands 位置改变`)**:给 Agent 配 `agent_toolset`(read_file/list_files/write_file,`permissionPolicy: always_allow`),然后只改 **Environment type**(`local` / `sandbox` / `self_hosted`)即可切换执行面——同一份系统提示词与工具配置,三条 Hands 路径。

```json
{
  "name": "Workspace Copilot",
  "system": "You are a workspace copilot. Prefer tools when listing or reading files.",
  "tools": [{
    "type": "agent_toolset",
    "defaultConfig": {"enabled": true, "permissionPolicy": {"type": "always_allow"}},
    "configs": [
      {"name": "read_file", "enabled": true},
      {"name": "list_files", "enabled": true},
      {"name": "write_file", "enabled": true}
    ]
  }]
}
```

!!! warning "MCP 权限的边界"
    `mcp_toolset` 的 `permissionPolicy` **不会进入 ToolConfirmationMiddleware**——高风险 MCP 写操作需要在 MCP 网关侧做身份、审批与幂等控制,不能只依赖 Agent body 里的 `always_ask`。

## 实践 / 应用:企业级 Managed Agents 平台

### 多 Agent 编排的两种方式

| 方式 | 机制 | 适用 |
| --- | --- | --- |
| **Harness 原生委派** | Team Lead 在推理中用 `sessions_spawn` / Subagent 工具动态拆解任务,父子任务有明确委派与结果回收关系 | 有依赖、需动态拆解的任务 |
| **平台 fan-out** | `/api/multiagent/run` 为多个 Agent 分别创建 Managed Session,同一消息顺序/并行发送 | 独立分析、批处理、投票 |

!!! tip "Agent Team 三角色示例(最小权限 + 独立审计)"
    - **Repo Surgeon**:只拥有工作区读取与检索工具(只读);
    - **Ops Publisher**:只生成发布草案,不调外部系统(`permissionPolicy: deny` + 仅开 read_file);
    - **Team Lead**:只保留委派与结果收集工具(`sessions_spawn` / `sessions_pending_completions` / `wait_async_results`),不直接接触业务数据;
    - 拆三个 Agent 不是为了堆角色,而是**分别约束工作区权限、外部系统接入和汇总职责**——收益是最小权限与独立审计,而不是把所有工具塞进一个超级 Agent 只靠提示词约束。

### 从单 Agent 走向 Managed Agents 的平台化清单

真正产品化需要补齐(不是加几个 Controller 就行):**租户 ACL、Agent 版本快照、Session 状态机、append-only 事件、turn 租约、HITL ticket、Environment key、Worker 队列、共享协调存储、归档审计**。Harness 让平台不必重写 AgentLoop,但这些分布式职责仍是独立的工程系统。

### 完整形态

> **SaaS 控制面负责资源治理 + AgentScope 2.0 提供运行内核 + FC Sandbox / E2B 或客户 Worker 承接不同信任边界下的 Hands。**

## 总结

- **Managed Agents 的两点本质**:通用工程能力收进统一 Harness(开发者只管业务差异);Brain/Hands 拆分(模型决定调什么 ≠ 模型进程必须亲自执行什么);
- **AgentScope 2.0 的角色**:HarnessAgent(工程默认项)+ 文件系统/沙箱抽象(执行面可替换)= 数据面与 Hands 内核;平台负责租约、事件契约、多租与 ACL;
- **三层分工**:控制面管定义与权限、数据面管运行与记录、Worker 管执行位置;四种状态分层恢复;
- **两条执行路径**:全托管(Brain 主动调沙箱)vs Self-hosted(客户 Worker 出站执行,结果脱敏回传);
- **定位**:同一套 Harness 内核两种模式——企业不必在"自己拼积木"和"完全黑盒托管"之间二选一。

## 延伸阅读

- 项目:https://github.com/agentscope-ai/agentscope-java;文档:https://java.agentscope.io;AgentScope Builder:https://github.com/agentscope-ai/agentscope-java/tree/main/agentscope-examples/agents/agentscope-builder;原文:https://mp.weixin.qq.com/s/rAla7_6DXhMuBM8YQn_I9Q
- 站内:[Harness 收录清单](index.md)、[PenguinHarness](penguin-harness.md)(自进化平台)、[OpenWorker 架构](openworker-architecture.md)(桌面 Agent Harness)、[Multica](multica.md)(编码 Agent 调度中台)、[TencentDB Agent Memory](agent-memory-plugin.md)(外部记忆)、[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(Harness 七层方法论)、[生产级 Agent 9 层架构](../03-agents/ai-infra-layering.md)(L4/L5/L6 编排、沙箱、记忆)
