# Agent 多轮对话上下文管理:Session、消息链与五层压缩(nanobot 源码拆解)

> **一句话摘要**:大模型 API 无状态,"多轮记忆"全靠应用层代码维护。本文以 nanobot 源码为线索拆解 Agent 多轮对话上下文管理的完整工程链路:session_key 隔离与加锁、四类消息与 tool_call_id 配对、ContextBuilder 拼装、五层压缩防线、崩溃恢复与原子写入、记忆四层次——并附面试答题框架。
>
> **来源**:阿杰Agent开发日志《大厂面试题 Agent多轮对话上下文管理:原理与源码拆解》(https://mp.weixin.qq.com/s/HLN2U6gXfJB0HRkZ3-fDyg);源码框架 [nanobot(HKUDS)](https://github.com/HKUDS/nanobot)

## 概念

### LLM 为什么"记不住":API 本身是无状态的

每次调用 LLM API,模型只能看到本次传来的 `messages`,上一次调用对它来说不存在。第二次调用若只传新问题,模型就像**完全失忆的人**——你得把所有背景从头讲一遍。

> 💡 **一句话定义**:Agent 的多轮对话上下文管理,不是"模型自己记住了",而是**代码在每次调用模型前,把需要的历史拼进 `messages` 重新发过去**。"记忆"是代码维护的,不是模型自带的。

### 两种"多轮",机制完全不同

| 类型 | 定义 | 上下文管理机制 |
| --- | --- | --- |
| **跨回合多轮** | 用户和 AI 的来回对话(隔几分钟/几天) | 靠 **Session 持久化**恢复历史 |
| **单回合内部多轮** | 用户发一句话,Agent 内部多次调 LLM(工具循环) | 靠 **Runner 在内存**维护当前循环的 `messages` |

用户只看到一次对话,内部可能经历了"调 LLM → 执行工具 → 再调 LLM"多次;每次调用都要维护一份完整上下文。面试回答时分开说,才能体现真理解两个层次。

### 消息的四种角色:工具调用是一条不能断的链

一段含工具调用的对话,Session 里存的是四种角色消息:

```
# ① 用户问题
{"role": "user", "content": "帮我查北京今天的天气"}

# ② 模型决定调用工具(只声明,未执行)
{"role": "assistant", "content": "",
 "tool_calls": [{"id": "call_abc123", "function": {"name": "search_weather", "arguments": '{"city": "北京"}'}}]}

# ③ 工具执行结果
{"role": "tool", "tool_call_id": "call_abc123", "name": "search_weather",
 "content": "北京今天晴,25度,东南风3级"}

# ④ 模型读取结果,生成最终回答
{"role": "assistant", "content": "北京今天晴,25度,非常适合出门！"}
```

`tool_call_id` 就像**快递单号**:② 填发货单、③ 带同一单号送回。单号对不上、或有单号找不到货、或有货找不到单号,整个流程就断——主流模型 API 会**直接报错拒绝请求**。

## 原理

### 七步状态机:一条消息进来,系统做了什么

消息进来后走七个阶段,核心是 **RESTORE → BUILD → RUN → SAVE**。状态机可恢复:若在 RUN 阶段崩溃,重启时 RESTORE 能识别"上次没做完",从断点继续而非从头重来。

1. **识别 session_key**:这条消息属于谁的对话
2. **RESTORE**:恢复上次可能未完成的工作(checkpoint)
3. **BUILD**:拼装发给模型的完整 `messages`(ContextBuilder)
4. **RUN**:AgentRunner 执行 LLM-工具循环
5. **SAVE**:把新消息写回 Session 持久化
6. 其余阶段处理收尾/归档

### Session 隔离:每段对话一张"身份证"+ 一把锁

**session_key** 区分不同对话窗口:

```
session_key = f"{channel}:{chat_id}"
"telegram:12345"   # Telegram 某用户私聊
"cli:direct"       # 命令行直接运行
"slack:C001"       # Slack 某频道
```

没有隔离,多用户的对话历史会混在一起——AI 可能拿小张的背景回答小李的问题。

**同一个 Session 必须加锁**:用户快速连发两条消息,若并发处理同一 Session,两个请求都会基于旧历史拼装、互相覆盖写入。解法:每个 `session_key` 一把 `asyncio.Lock`——**同 Session 串行,不同 Session 并发**,互不影响。

**持久化**:每段对话一个 JSONL 文件(`workspace/sessions/telegram:12345.jsonl`),每行一个 JSON 对象。JSONL 的好处:写到一半崩溃,已写完的行不损坏,顶多残缺最后一行。读取优先级:内存缓存(热数据)→ JSONL 文件 → 新建 Session。

### 消息链合法性:切历史不能切出"孤儿工具结果"

假设 Session 有 50 条消息,Token 预算只能取最近 20 条。若从中间硬切,可能第 30 条"assistant 声明调工具(call_id=call_xyz)"被切掉、第 31 条"tool 结果(tool_call_id=call_xyz)"保留——这就是**孤儿工具结果**,API 报错。

所以 `get_history()` 必须做额外检查:**从合法的用户回合边界开始切**,保证每个 `tool_call_id` 都有对应声明。

> 💡 上下文管理不只是"选多少条",更重要的是:**选出来的消息链结构必须是合法的**。

### 上下文拼装:模型看到的远不止聊天记录

发给 LLM 的完整结构是三段:

```
messages = [
    {"role": "system", "content": system_prompt},   # 稳定内容
    ...history...,                                   # 筛选过的历史
    {"role": "user", "content": 当前消息 + 运行时信息}  # 易变内容
]
```

**System Prompt 装了九样东西**:身份说明、行为规范、人格设定、用户偏好、工具使用规则、长期记忆、skills 说明、近期归档摘要、session 压缩摘要。这解释了"Agent 为什么记得我的偏好"(用户偏好写进 `USER.md` 拼进 system prompt)和"隔几天回来还记得上次聊了什么"(旧对话摘要存 metadata,作为第 ⑨ 条注入)。

**当前消息末尾附运行时信息**(当前时间、频道、Chat ID、MCP 连接状态)。为什么不放 system prompt?因为这些**每次都变化**,放 system prompt 会让前缀缓存失效;**稳定内容进 system prompt、易变信息放用户消息末尾**,Prompt Cache(按前缀缓存)才能命中,省 token 费用。

### AgentRunner:LLM-工具循环 + 每轮"上下文治理"

```python
# initial_messages 来自 BUILD 阶段: [system_prompt, ...history..., 当前用户消息]
messages = list(initial_messages)

for iteration in range(max_iterations):      # 设上限,防止工具死循环
    messages_for_model = treat_context(messages)   # ① 每次发送前治理上下文
    response = await llm.call(messages_for_model)  # ② 调 LLM

    if response.has_tool_calls:                    # 模型要调工具
        messages.append({"role": "assistant",
                         "tool_calls": [{"id": "call_abc123", "function": {...}}]})
        results = await execute_tools(response.tool_calls)   # ④ 真正执行
        messages.extend([{"role": "tool", "tool_call_id": "call_abc123",
                          "content": "工具返回的内容"}])      # ⑤ call_id 必须一致
        continue                                # 让模型继续看工具结果
    messages.append(response.final_message)     # 最终答案,结束循环
    break
```

**`treat_context()` 治理操作**——每次调 LLM 前对副本做一遍,保证合法 + 不超 Token:

| 治理操作 | 干什么 | 为什么 |
| --- | --- | --- |
| 删孤儿工具结果 | 删除找不到对应声明的 tool 消息 | 防 API 报错 |
| 补缺失工具结果 | 工具执行中断时补一条合成错误信息 | 保持 call_id 配对完整 |
| 压缩旧工具输出 | 把几轮前的大工具结果压缩变小 | 防单个结果撑爆上下文 |
| 限制工具结果总量 | 工具结果不能超预算 token | 给历史和用户信息留空间 |
| 裁剪旧历史 | 整体超预算时删最旧消息 | 控制整体 token 数 |

⚠️ **重要区别**:治理只改变"本次发给模型的副本"(`messages_for_model`),**Session 文件里的完整记录不动**——这是两份数据,不要混淆。

### 五层压缩防线:对话太长的兜底体系

```
对话越来越长,Token 越占越多
    ↓ 超出回放窗口
第一层:Session 回放窗口限制(条数上限 + Token 预算,从合法边界切)
    ↓ 发给模型前还是太长
第二层:Runner 实时治理(压缩工具结果、裁旧历史)
    ↓ 估算整体 prompt 超预算
第三层:Consolidator——让 LLM 把旧消息写成摘要
    ↓ 会话空闲超过 TTL
第四层:AutoCompact——后台自动压缩整个会话
    ↓ Session 文件本身太大
第五层:文件硬上限,强制保留最近合法后缀(旧部分原始归档)
```

各层触发时机不同:第一层最轻量零开销;第二层每次调用前自动;第三层按 Token 预算触发;第四层按空闲 TTL 触发;第五层是防磁盘撑爆的最后防线(被移除的更旧部分**做原始归档**,防止彻底丢失)。

### 崩溃恢复:四步机制 + 原子写入

不处理崩溃的后果:工具执行到一半进程崩溃,Session 里"assistant 声明 3 个 call_id"但只有 tool_1 有结果——下次请求 API 直接报错,用户永远得不到回复。

四步恢复:

1. **用户消息先持久化**:真正调 LLM 之前已落盘,崩溃后用户输入不丢;
2. **工具边界存 Checkpoint**:每执行完一个工具,把进度写进 Session metadata(`runtime_checkpoint` = 模型的工具声明 + 已完成结果 + 待执行调用 + 当前迭代数),像游戏自动存档;
3. **RESTORE 重建消息链**:检测到 checkpoint → 恢复已完成结果 → 对未完成调用补合成错误"任务在完成前被中断" → 检查与 Session 尾部重复 → 清除 checkpoint,消息链重新合法;
4. **原子写入防半损坏**:

```python
# ① 先写临时文件(写到一半崩溃,正式文件还是旧的完整版)
with open("session.jsonl.tmp", "w") as f:
    f.write(content)
# ② 确认无误后原子替换
os.replace("session.jsonl.tmp", "session.jsonl")
```

`os.replace()` 在 OS 层面是原子操作——要么完全替换,要么保持旧文件,不会留下"写到一半"的损坏文件。

### 记忆的四个层次:历史 ≠ 长期记忆

| 层次 | 存储位置 | 触发写入时机 | 主要用途 |
| --- | --- | --- | --- |
| 原始消息 | `sessions/*.jsonl` | 每轮对话结束 SAVE | 精确回放最近上下文 |
| session 摘要 | `session.metadata` | AutoCompact / 会话压缩 | 注入 System Prompt,帮模型"想起"旧内容 |
| history | `memory/history.json` | Consolidator 归档时 | 可被 Dream 模块进一步加工 |
| 长期记忆 | `memory/memory.md` | Dream 模块提炼时 | 跨会话的长期知识库 |

**最本质的区别**:历史记录"发生了什么"(每一句、包括废话全存);长期记忆保存"以后还有用的稳定事实"(只存精华)。不要把每条聊天记录都当长期记忆——那叫流水账,不叫记忆。

## 代码 / 实现

以上核心机制在 nanobot 中的落地要点:

- **session_key 生成**:`f"{channel}:{chat_id}"`,消息进入第一步就识别;
- **并发控制**:`session_key` 字典维护 `asyncio.Lock`,同 Session 串行、异 Session 并发;
- **持久化**:`workspace/sessions/<session_key>.jsonl`,JSONL 追加写 + 原子替换;
- **历史读取**:`get_history()` 按"条数上限 + Token 预算"从最新往前倒推,并从**合法用户回合边界**开始切;
- **拼装**:`ContextBuilder` 产出 `[system_prompt, ...history, 当前消息+运行时信息]`;
- **循环**:`AgentRunner` 内 `for iteration in range(max_iterations)`,每轮 `treat_context()` 治理副本;
- **压缩**:`Consolidator`(LLM 摘要)、`AutoCompact`(空闲 TTL 触发)、文件硬上限;
- **恢复**:`runtime_checkpoint` 存 metadata,RESTORE 阶段重建合法消息链。

这些模式不依赖 nanobot,是 Agent 框架通用工程范式——任何多轮对话 Agent(含 Claude Code 这类 harness)的上下文管理都围绕同样的"分、存、取、拼、跑、配、裁、压、记、复"展开。

## 实践 / 应用

### 面试答题框架(一分钟版本)

> 大模型 API 是无状态的,多轮对话能力由应用层实现。系统用 session key 隔离不同会话,把 user、assistant、tool call、tool result 四类消息持久化。每次新请求,从 Session 里按消息条数和 Token 预算选最近一段**合法**历史(不能随意切,切断了 tool_call_id 配对就报错),再拼接 system prompt(含长期记忆、历史摘要)和当前消息发给模型。
>
> Agent 单回合内,工具调用和结果继续追加到 messages,循环调用模型直到得出最终答案。上下文过长有五层兜底:Session 回放窗口 → Runner 实时治理 → Consolidator LLM 摘要 → AutoCompact 空闲压缩 → 文件硬上限。同时要保证 tool call 与 result 的 call_id 配对、同 Session 串行加锁、崩溃后 checkpoint 恢复消息链、JSONL 文件原子写入。

**五个高频追问与核心回答**:

| 面试官问 | 核心回答 |
| --- | --- |
| Token 上限怎么处理? | 五层:回放窗口 → 实时治理 → LLM 摘要 → 空闲压缩 → 文件硬上限,层层兜底 |
| 为什么不能随意切历史? | 随意切会产生孤儿 tool 消息(声明和结果 call_id 不配对),主流 API 直接报错 |
| 并发请求怎么处理? | 每个 session_key 一把 asyncio.Lock,同 Session 串行,不同 Session 并发 |
| Agent 崩溃了怎么恢复? | 提前保存用户消息 + 工具边界存 checkpoint + RESTORE 阶段补齐配对 + 原子写入 |
| 长期记忆和历史有什么区别? | 历史是完整流水账;长期记忆是提炼后跨会话有价值的稳定事实 |

**十字口诀**:分(session_key 隔离)→ 存(JSONL 持久化四类消息)→ 取(条数+Token+合法边界)→ 拼(system prompt+历史+当前消息)→ 跑(Runner 循环)→ 配(tool_call_id 配对)→ 裁(超预算裁旧历史/旧工具结果)→ 压(LLM 摘要)→ 记(稳定事实提炼到 memory.md)→ 复(checkpoint+原子写入)。

### 工程要点与坑

- **孤儿消息是高频事故**:裁剪历史必须从用户回合边界切;工具执行中断必须补合成错误消息,否则用户消息永远得不到回复;
- **治理只动副本,不动 Session**:Session 是完整流水账,发给模型的副本才做压缩/裁剪——两份数据混淆会导致"记不住"或"报错";
- **缓存友好拼装**:稳定内容(身份/规范/长期记忆)进 system prompt,易变内容(时间/连接状态)放用户消息末尾,保证 Prompt Cache 命中;
- **加锁粒度**:锁挂在 session_key 上(对话级串行),不是全局串行——既防写冲突又保住并发吞吐;
- **崩溃恢复是状态机能力**:七步状态机 + checkpoint + 原子写,缺一不可;只做原子写不存 checkpoint,会丢执行进度。

## 总结

1. **记忆是代码维护的**:LLM API 无状态,多轮能力 = 每次调用前把历史拼进 messages;跨回合靠 Session 持久化,单回合内部靠 Runner 内存循环。
2. **消息链合法性优先于数量**:四类角色消息靠 tool_call_id 配对,裁剪历史必须从用户回合边界切,孤儿工具结果会让 API 直接报错。
3. **拼装有讲究**:system prompt 装稳定内容(含长期记忆/摘要),运行时信息放用户消息末尾保缓存命中;每轮发送前 `treat_context()` 治理副本。
4. **五层压缩防线 + 崩溃恢复**:回放窗口→实时治理→LLM 摘要→空闲压缩→文件硬上限;checkpoint + RESTORE + 原子写入保证"崩了不丢、断了能续"。
5. **历史 ≠ 长期记忆**:历史是完整流水账,长期记忆是提炼后的稳定事实,分层存储各有触发时机。

**下一步学什么**:对比站内 [工具调用](../03-agents/tool-calling.md)(消息结构与 function calling 协议)、[上下文压缩与提示缓存](../03-agents/context-engineering-compression-caching.md)(缓存纪律与 token 预算)、[Agent 记忆体系](../03-agents/agent-memory-systems.md) 与 [Hermes 记忆工程设计](../03-agents/agent-memory-harness-design.md);想动手可直接读 [nanobot 源码](https://github.com/HKUDS/nanobot) 的 `get_history()` / `ContextBuilder` / `AgentRunner` 三个文件。

## 延伸阅读

- 站内:[工具调用](tool-calling.md)、[上下文压缩与提示缓存](context-engineering-compression-caching.md)、[Context Engineering](context-engineering.md)、[Agent 记忆体系](agent-memory-systems.md)、[Agent 记忆模块工程设计(Hermes)](agent-memory-harness-design.md)、[Agent 持久化运行范式](agent-persistence-patterns.md)、[Agent 面试题知识提炼](agent-interview-knowledge.md)、[nanobot 框架](nanobot-framework.md)
- 外部:原文《大厂面试题 Agent多轮对话上下文管理》(https://mp.weixin.qq.com/s/HLN2U6gXfJB0HRkZ3-fDyg);[nanobot(HKUDS)](https://github.com/HKUDS/nanobot) 源码
