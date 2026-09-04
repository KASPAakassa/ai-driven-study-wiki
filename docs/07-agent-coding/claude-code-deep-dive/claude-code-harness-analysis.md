# Claude Code 源码解析:从 Agent Loop 到完整 Harness(20 章全整合)

> **一句话摘要**:shareAI 的 learn-claude-code 系列用"教学版 + 源码路径"逐层拆解 Claude Code:从 30 行的最小 Agent Loop 开始,每章只加一个机制——工具分发、权限、hooks、todo、子 Agent、技能加载、上下文压缩、记忆、system prompt 组装、错误恢复、任务系统、后台任务、cron、Agent Teams、团队协议、自治 Agent、Worktree 隔离、MCP 插件,最后合成完整 harness。核心哲学:**Agency 来自模型训练,Agent 产品 = 模型 + Harness——本系列教你造车(vehicle),模型是司机。**
>
> **来源**:shareAI-lab/learn-claude-code(https://github.com/shareAI-lab/learn-claude-code,20 节中文教学 + 源码路径);原始文件存档于 `references/learn-claude-code/`(20 节 README 全量)

## 概念:一条主线,二十个机制

!!! tip "核心哲学(顶层 README)**
    **Agency——感知、推理、行动的能力——来自模型训练,不是外部代码编排。** 但可用的 Agent 产品需要模型 + harness 两者:模型是司机,harness 是车。这个仓库教你如何造车。循环本身始终不变(一个 while True + 工具执行),后面 19 章都在这个循环上叠加机制。

**二十章地图**:

| 章 | 机制 | Harness 层 |
| --- | --- | --- |
| s01 | Agent Loop(30 行内核) | 循环——模型与真实世界的第一道连接 |
| s02 | 工具分发(dispatch map) | 扩展模型能触达的边界 |
| s03 | 权限(4 种结果/8 来源拒绝列表) | 边界控制 |
| s04 | Hooks(27 个事件/注册表) | 扩展点 |
| s05 | TodoWrite(+ nag reminder) | 目标保持 |
| s06 | Subagent(3 种模式) | 上下文隔离 |
| s07 | Skill 加载(两级) | 按需知识 |
| s08 | 上下文压缩(4 级管线) | 上下文管理 |
| s09 | Memory(文件+索引+LLM 选) | 跨会话记忆 |
| s10 | System Prompt 组装(section 缓存) | 提示组装 |
| s11 | 错误恢复(3 路径/退避) | 可靠性 |
| s12 | 任务系统(DAG/blockedBy) | 目标持久化 |
| s13 | 后台任务(启发式+通知) | 异步执行 |
| s14 | Cron 调度(4 层模型) | 定时触发 |
| s15 | Agent Teams(文件收件箱) | 多 Agent 通信 |
| s16 | 团队协议(请求-响应状态机) | 结构化协作 |
| s17 | 自治 Agent(空闲轮询+认领) | 自主性 |
| s18 | Worktree 隔离(任务绑定) | 并行隔离 |
| s19 | MCP 插件(工具池组装) | 外部接入 |
| s20 | 综合(全部组件归位) | 完整 harness |

## 第一部分:核心循环(s01-s05)

### s01 Agent Loop:一个循环就够了

**问题**:模型能输出 bash 命令,但不会自己跑、不会看结果继续推理——手动贴回是"人在做中间层"。

**方案**:一个 `while True` 循环,两个信号:

| 信号 | 含义 | 动作 |
| --- | --- | --- |
| `stop_reason == "tool_use"` | 模型举手要工具 | 执行 → 结果喂回 → 继续 |
| 其他 | 模型说"做完了" | 退出 |

**内核(不到 30 行)**:发消息+工具定义 → 追加模型回答 → 判断 stop_reason → 执行工具收集结果 → 结果作新消息追加回循环。**它不是智能本身,而是让模型能持续行动的最小运行框架**——模型负责决策,harness 负责执行。

### s02 Tool Use:多加一个工具,只加一行

**问题**:只有 bash,读文件要 `cat`、写文件要 `echo`——多一层翻译浪费 token 还容易拼错。

**方案**:循环完全保留,工具执行那 1 行从 `run_bash()` 变成查表分发 `TOOL_HANDLERS[block.name]()`。加工具 = ①在 `TOOLS` 加描述 ②在 `TOOL_HANDLERS` 注册 handler。从 1 个(bash)到 5 个(bash/read_file/write_file/edit_file/glob),每个工具独立定义 + 独立实现。**扩展点原则:循环不动,新工具注册进 dispatch map。**

### s03 Permission:不是 3 种结果,是 4 种

**问题**:所有工具裸奔,模型可以 `rm -rf`。

**方案**:工具执行前过权限检查。教学版关键设计(教学版简化是刻意的,真实 CC 更细):

1. **PermissionResult 是 4 种**(不是 allow/deny/ask 3 种):allow / deny / ask / **rewrite(改参数放行)**——rewrite 是"这命令本身危险,但换个写法可以";
2. **拒绝列表来自 8 个来源**(不是一个文件):内置默认、配置文件、CLI 参数、hooks 等合并;
3. **`isDestructive()`**:判定命令是否破坏性(rm/覆盖/外部写);
4. **YoloClassifier(自动审批)**:简单命令自动放行,复杂命令交人工;
5. **权限冒泡(permission bubbling)**:子 Agent 不能比父 Agent 有更多权限——子请求升级为父确认。

!!! note "教学版刻意简化"
    教学版是"能跑的最小系统",真实 CC 在权限上有更多来源与分类;简化的目的是让机制清晰,而不是实现全部细节——每个 Deep Dive 段落标注了"教学版 vs 真实 CC"。

### s04 Hooks:扩展挂外面,循环保持稳定

**问题**:每加一个检查(日志/权限/通知/自动 git add)都改 `agent_loop` 循环——循环很快认不出来。

**方案**:循环只调用 `trigger_hooks(event, ...)`,扩展通过 `register_hook()` 添加。教学版 4 个事件(真实 CC **27 个**):UserPromptSubmit(输入提交后、进 LLM 前)/ PreToolUse(工具执行前)/ PostToolUse(工具执行后)/ Stop(循环退出时,可强制续跑)。

**关键不变式**:**Hook 的 `allow` 不能绕过 deny/ask 规则**——hook 只是"我这层没意见",最终权限由权限系统裁决(与站内 [Hook 治理](../../03-agents/agent-governance-hooks.md) 的"每层职责"一致)。另有 `stopHookActive` 机制:一个 hook 触发 stop 后,后续 hook 不再执行;`hook_stopped_continuation` 处理被 hook 中断的对话续跑。

### s05 TodoWrite:让 Agent 不忘目标

**问题**:复杂任务(改 10 个文件)做完 1-3 步就开始即兴发挥——4-10 步被测试失败吸走了注意力。

**方案**:`todo_write` 工具(不做实际工作,只理清思路)+ **nag reminder**(教学版:连续 3 轮没调 todo_write 就注入提醒;真实 CC 没有固定轮数)。工具输入是带状态列表(pending/in_progress/completed),存进程内存 + 终端显示进度。**让 Agent 在动手之前先把计划"写出来"、过程中"看得见"。**

## 第二部分:上下文与知识(s06-s10)

### s06 Subagent:不是一种模式,是三种

**问题**:读了 30 个文件、聊了 60 轮——中间过程占满上下文,Agent 忘了最初目标。就像人"开新终端"追调用链,追完关掉、结果写笔记、回原终端继续。

**方案**:`task` 工具 spawn 子 Agent——全新 `messages[]`、跑自己的循环、结束后只回传摘要;文件系统副作用保留在工作目录;子 Agent 工具受限(无 task,不能递归);工具调用仍过权限 hook。

**三种模式**(真实 CC,教学版讲透):①**Fork 模式**(为了共享 Prompt Cache,上下文结构复制);②**Context Isolation 的精确粒度**(哪些隔离哪些共享);③**递归 Fork 防护**(防止无限嵌套)+ Permission Bubbling(子权限不超父)+ Async vs Sync(异步子任务)。

### s07 Skill 加载:两层设计,用到才花 token

**问题**:6500 行规范全塞 system prompt——99% 内容与当前任务无关,白烧 token。

**方案**:两级加载——**目录层**(启动时注入 SYSTEM,~100 tokens/skill,每轮都带)/ **内容层**(Agent 调 `load_skill` 时 tool_result 加载,~2000 tokens,按需)。SKILL.md frontmatter 常见字段(name/description 等);**技能来源不止一个 skills/ 目录**(真实 CC 有多个来源)。目录告诉 Agent"我有哪些技能",内容按需展开——正是 [Skills 渐进式披露](claude-skills-plugin-subagent.md) 的源码实现。

### s08 上下文压缩:四层管线,便宜的先跑

**问题**:上下文窗口满了,API 直接拒绝 `prompt_too_long`——不压缩没法在大项目干活。

**方案:四层压缩管线(核心设计:便宜的先跑,贵的后跑)**:

| 层 | 机制 | 0 API |
| --- | --- | --- |
| **L1 snip_compact** | 消息 >50 条 → 保留头部 3 条 + 尾部 47 条,中间裁掉;保护边界(不拆开 tool_use 与 tool_result) | ✅ |
| **L2 micro_compact** | 旧工具结果占位:只保留最近 3 条 tool_result 全文,更早的压缩 | ✅ |
| **L3 tool_result_budget** | 大结果落盘:超预算的工具输出写临时文件,上下文只留引用 | ✅ |
| **L4 compact_history** | LLM 全量摘要:前三层仍超阈值 → 用 LLM 总结(1 API) | ❌ |
| **应急 reactive_compact** | API 报 prompt_too_long 时紧急裁剪重试 | ✅/❌ |

执行顺序:snip → micro → budget → history,逐层升级;**compaction 执行在每轮 LLM 调用前,摘要保留当前目标/剩余工作/用户约束**。

### s09 Memory:不参与压缩、跨会话保留

**问题**:压缩有损("用 tab 不用空格"被简化成"有风格偏好"),新会话连摘要也没了——LLM 没有持久状态。

**方案**:文件系统存储——`.memory/` 下每个记忆一个 `.md`(YAML frontmatter:name/description/type)+ `MEMORY.md` 索引(一行一链接,注入 SYSTEM,可被 prompt cache 缓存)。

- **四类记忆**:user(你是谁)/ feedback(怎么做事)/ project(正在发生什么)/ reference(东西在哪找);
- **加载两条路径**:索引常驻 SYSTEM(不破坏 cache)+ 文件内容按需注入当前 user turn;
- **写入**:每轮结束后提取器(用户显式说"记住"或稳定偏好);
- **整理**:低频合并去重;
- **记忆选择:LLM 选,不是 embedding**(按 filename/description 匹配当前对话);
- **提取时机:stop hook,不是 autoCompact 后**。

### s10 System Prompt:按需拼接 + 缓存

**问题**:硬编码 SYSTEM 三个问题——换项目重写全量 / 改一处影响全局 / 每次全带浪费 token。

**方案**:拆成 section,运行时按真实状态拼接,缓存结果:

| Section | 策略 | 判断依据 |
| --- | --- | --- |
| identity | 始终 | 你是谁、怎么做事 |
| tools | 始终 | enabled_tools |
| context | 按需 | 真实状态(工作目录/当前任务),**不是关键词猜测** |

**实现**:`PROMPT_SECTIONS`(分段定义)→ `assemble_system_prompt`(按需拼接)→ `get_system_prompt`(缓存避免重复拼接);**cache scope** 控制哪些内容稳定以命中 prompt cache。CC 真实 system prompt 有 15+ 个 section。

## 第三部分:可靠性与自动化(s11-s14)

### s11 错误恢复:一碰就熄火的车不是好车

**问题**:`529 overloaded` 直接崩溃——生产环境 API 错误是常态。

**方案**:LLM 调用包 try/except,按错误类型走恢复路径,恢复后 continue 回循环。三种恢复模式:

| 模式 | 触发 | 恢复动作 |
| --- | --- | --- |
| 输出截断 | max_tokens | **升级 8K→64K 重试同一请求**(不追加截断输出)→ 仍不够才注入续写提示,最多 3 次 |
| 上下文超限 | prompt_too_long | reactive compact → 重试 |
| 临时故障 | 429/529 | **指数退避 + 抖动**,连续 529 可切换备用模型 |

真实 CC 有 **13+ reason code**(教学版只处理 429/529);指数退避有精确公式;CONTINUATION 提示有原文;流式错误另有处理。

### s12 任务系统:DAG 依赖 + 跨会话持久化

**问题**:TodoWrite 是会话内执行清单,任务间没依赖——写 API 时发现没数据库表。

**方案**:任务系统——每个任务一个 JSON 文件(`.tasks/{id}.json`),`blockedBy` 依赖,跨会话持久化。5 个任务工具 + 状态机:

- **Task 数据结构**:id/content/status(pending/in_progress/completed)/owner/blockedBy;
- **create_task**(创建)/ **can_start**(依赖检查)/ **claim_task**(认领,owner 检查)/ **complete_task**(完成与解锁依赖)/ **get_task**(查看);
- **状态机:两个动作,三个状态**;DAG 依赖,教学版演示 blockedBy 无环检测;
- **与 TodoWrite 分工表**:TodoWrite=当前任务执行清单(会话内、无依赖);Task System=可恢复任务系统(磁盘、blockedBy、可认领追踪)。

### s13 后台任务:别站在洗衣机前干等

**问题**:`npm install` 10 分钟,Agent 干等——空转按 token 计费就是浪费。

**方案**:慢操作扔后台线程,Agent 继续循环,后台完成把通知注入对话。

- **should_run_background**:模型显式请求 `run_in_background` 参数优先;教学版关键词启发式兜底(install/build/test/deploy/compile 等慢命令);
- **start_background_task**:后台执行 + 生命周期;**collect_background_results**:通知收集;
- **pendingToolUseSummary**:后台进行时给 LLM 的摘要(真实 CC 用 Haiku 生成);
- **线程模型:没有真正的线程**(真实 CC 是异步协作);**七种后台任务类型**(真实 CC)。

### s14 Cron 调度:闹钟不需要你盯着

**问题**:后台任务仍手动触发——"每天早上 9 点跑测试"不该每次人推。

**方案:四层模型**——Scheduler(daemon 线程每秒轮询)→ Queue(cron_queue)→ Queue Processor(队列非空且 Agent 空闲时启动 agent_loop)→ Consumer(从队列消费注入 messages)。

- **CronJob**:id/cron(五段式表达式)/prompt/recurring;
- **cron_matches 五段式匹配**;独立调度线程每秒轮询;**校验:防止坏 cron 杀掉调度器**;
- **Durable vs Session-only**:持久任务跨重启,会话任务随会话。

## 第四部分:团队与隔离(s15-s18)

### s15 Agent Teams:能通信、能协作的队友

**问题**:s06 子 Agent 是"临时工",叫来干一件事就走了;大项目需要能持续通信协作的队友。

**方案**:MessageBus(文件收件箱)+ spawn_teammate_thread(启动队友线程)+ inbox 注入(Lead 接收队友消息注入 history)。

- **MessageBus:没有中央消息总线,是文件系统**——每个 Agent 一个 `.jsonl` 邮箱,发消息 = append 一行 JSON,读消息 = 读文件 + 删除(消费式);**15 种消息类型**(真实 CC);
- **子 Agent vs 队友**:一次性 vs 多轮、只回结论 vs 异步收件箱随时通信、完全隔离 vs 消息共享;
- **权限冒泡:双向轮询**(队友向 Lead 申请,Lead 确认)。

### s16 团队协议:请求-响应状态机

**问题**:协调松散——关机直接杀线程,Alice 写一半的文件留在磁盘;计划审批没有门控。

**方案**:ProtocolState(请求状态追踪)+ dispatch_message(按类型路由)+ match_response(request_id 关联回复,含类型校验)。两种协议一套机制:

| 协议 | 方向 | 用途 |
| --- | --- | --- |
| shutdown_request/response | Lead → 队友 | 体面关机握手 |
| plan_approval_request/response | 队友 → Lead | 计划审批 |

**ProtocolState**:request_id/type/sender/target/status(pending/approved/rejected)/payload。四步协议流程 + 统一 inbox 消费(consume_lead_inbox)+ 队友 idle loop(等待而不是退出)。教学版演示消息流程,未实现执行门控(真实 CC 队友有 permission gating)。

### s17 自治 Agent:自己看板、自己认领

**问题**:10 个未认领任务要 Lead 手动 assign 10 次——不能扩展。队友应该自己看任务板。

**方案**:idle_poll(空闲每 5 秒轮询)+ scan_unclaimed_tasks(扫描可认领任务)+ 自动认领。生命周期从两阶段变三阶段:

| 阶段 | 行为 | 退出条件 |
| --- | --- | --- |
| WORK | inbox → LLM → 工具循环 | stop_reason != tool_use |
| IDLE | 每 5s 轮询 inbox + 任务板 | 60s 超时 |
| SHUTDOWN | 发 summary,退出 | — |

真实 CC 的空闲机制是**组合路径,不是单一轮询**(多种来源检查);身份重注入(队友每次轮询后确认自己是谁);consume_lead_inbox 统一消费。

### s18 Worktree 隔离:解决"在哪干"

**问题**:Alice 和 Bob 都 `write_file("config.py")` 互相覆盖,无法干净回滚——任务系统解决"谁干什么"、消息总线解决"怎么通信",但没解决"在哪干"。

**方案**:Git worktree——同仓库多个独立工作目录 + 独立分支。

- **create_worktree**:为任务创建独立目录 + 分支(`git worktree add -b wt/{name} HEAD`);
- **bind_task_to_worktree**:任务绑定 worktree(不改状态,任务仍 pending,队友认领才推进);
- **remove/keep_worktree**:完成后清理或保留;**validate_worktree_name**:拒绝路径穿越(只允许 `[A-Za-z0-9._-]{1,64}`);
- **事件流可审计**(log_event);run_git 返回成功/失败;**EnterWorktree**:当前会话切换;**AgentTool isolation**:子 agent 隔离。

## 第五部分:外部接入与整合(s19-s20)

### s19 MCP 插件:标准协议接入外部服务

**问题**:3 个外部服务(Jira/部署系统/Notion)不想为每个重写工具代码——需要标准协议。

**方案**:MCP(Model Context Protocol)——外部服务实现 `tools/list` + `tools/call`,Agent 直接调用。

- **MCPClient**:发现 + 调用(register 模拟 tools/list,call_tool 模拟 tools/call);教学版用 mock handler,真实版 stdio JSON-RPC 子进程;
- **connect_mcp**:连接 + 发现;normalize_mcp_name(名称规范化);
- **assemble_tool_pool**:内置工具 + MCP 工具组装成工具池;**mcp__server__tool 命名避免冲突**;
- **无缓存:工具池变了,prompt 也变**(不能缓存过时工具列表);**6 种 Transport 类型**;MCP 工具只有 Lead 可用。

### s20 综合:所有组件归位

**问题**:前 19 章每章一个机制;真实 Agent 需要同时拥有全部——难点不是堆功能,是看清都挂在循环哪个位置。

**完整 harness 数据流**:

```
用户输入 → UserPromptSubmit hooks → cron/background 通知注入 → context compact
  → memory + skills + MCP 状态组装 system prompt → LLM
  → 有 tool_use block?
      否 → Stop hooks → 返回
      是 → PreToolUse hooks + permission → TOOL_HANDLERS/MCP/background
          → PostToolUse hooks → tool_result/task_notification 回 messages → 下一轮
```

!!! tip "关键洞察(s20)**
    循环本身仍是同一个结构:调用模型 → **检查响应里是否实际出现 tool_use block**(CC 源码不直接信任 `stop_reason == "tool_use"`,而是以实际出现的 block 为准)→ 执行工具 → 结果追加回 messages。**变化的是循环周围的 harness 变完整了。**

**组件在循环中的位置**(全表):用户输入前后(UserPromptSubmit)/ LLM 前(cron queue、background notifications、compaction pipeline、memory/skills/MCP 状态)/ LLM 调用(error recovery)/ 工具执行前(PreToolUse + permission)/ 工具分发(assemble_tool_pool)/ 工具执行后(PostToolUse)。

## 代码 / 实现:最小 Agent Loop(30 行内核,来自 s01)

```python
def agent_loop(messages):
    while True:
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messages,
            tools=TOOLS, max_tokens=8000,
        )
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = run_bash(block.input["command"])
                results.append({"type": "tool_result",
                                "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": results})
```

!!! note "与站内其他解析篇的分工"
    本文件是 **learn-claude-code 20 章的教学版源码解析**(从零叠加机制);站内 [Claude Code 架构与工具系统](claude-architecture-tools.md) 是**产品功能全景**、[Worktree 与 Agent Teams](claude-worktree-teams.md) 是**功能使用指南**——三者互补:功能怎么用 / 产品怎么组成 / 机制怎么实现。

## 实践 / 应用:从解析中学到什么

1. **循环是稳定的核心,机制挂外面**:所有扩展(权限/hooks/工具/记忆/压缩)都不改循环本身——这是 harness 架构的第一原则;
2. **便宜的先跑,贵的后跑**:压缩四层(0 API 先行,LLM 摘要兜底)、技能两级(目录常驻,内容按需)——token 效率的通用模式;
3. **确定性兜底,概率性增强**:权限/hooks/压缩用确定性代码,模型只负责决策与摘要;
4. **隔离是协作的前提**:子 Agent 上下文隔离、Worktree 文件隔离、任务/队友收件箱隔离——先隔离再协作;
5. **教学版 vs 真实 CC**:每章 Deep Dive 标注差异(27 个 hook、13+ reason code、15 种消息类型、7 种后台任务)——学习看机制,生产看细节。

## 总结

- **一条主线**:Agency 来自模型,Agent 产品 = 模型 + Harness;从 30 行 Loop 到完整 harness,20 章每章一个机制;
- **四个阶段**:核心循环(s01-s05)→ 上下文与知识(s06-s10)→ 可靠性与自动化(s11-s14)→ 团队与隔离(s15-s18)→ 外部接入与整合(s19-s20);
- **五大原则**:循环稳定扩展挂外、便宜先跑贵后跑、确定性兜底、先隔离再协作、教学看清机制生产看细节;
- **一句话**:Claude Code 的强大不是某个单点机制,而是**几十个机制正确挂在同一条循环上的工程结果**——这就是 Harness Engineering。

## 延伸阅读

- 仓库:https://github.com/shareAI-lab/learn-claude-code(20 节中文 README 全量存档于 `references/learn-claude-code/`)
- 站内:[Claude Code 架构与工具系统](claude-architecture-tools.md)、[Worktree 与 Agent Teams](claude-worktree-teams.md)、[Skills/Plugin/Subagent](claude-skills-plugin-subagent.md)、[Claude Code 隐藏技巧](claude-code-tips.md)(本子主题其他篇);[Hook 治理](../../03-agents/agent-governance-hooks.md)、[多智能体协作设计](../../03-agents/agent-team-room-collaboration.md)、[Git Worktree 并行开发](../experience/git-worktree-parallel-agents.md)
