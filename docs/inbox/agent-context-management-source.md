> 原文存档:微信文章《大厂面试题 Agent多轮对话上下文管理:原理与源码拆解》(公众号:阿杰Agent开发日志)
> 原始链接:https://mp.weixin.qq.com/s/HLN2U6gXfJB0HRkZ3-fDyg
> 抓取日期:2026-08-11(手机 UA curl,避开微信环境验证)
> 用途:整理收件箱素材,正文原样保留供追溯。

---



 

>

**导读：** 上周有粉丝留言说，面试官问"Agent 多轮对话上下文是怎么管理的"，回答"把历史消息传给模型"，然后被追问五个问题，全没答上来。这道题看起来简单，藏的坑却很深。本文从根本原理出发，结合真实框架源码，把每一层细节讲清楚——Session 隔离、消息结构、上下文拼装、压缩策略、崩溃恢复，最后附面试答题框架。小白友好，建议收藏。

## 一、这道题，70% 的人只答了表面

上周收到一条粉丝留言：

>

"面试官问 Agent 多轮对话上下文怎么管理，我说'把历史消息一起传给模型，模型就能记住了'。

面试官微微一笑，问：'那如果对话很长，超过 Token 上限了呢？'

我说：'压缩一下？'

他继续问：'怎么压缩？压缩时工具调用的消息链如何保证合法？并发场景下多个请求同时修改 Session 会冲突吗？Agent 崩溃了恢复时怎么处理？'

然后我就……"

诶，这个场景小编太熟悉了。

"把历史传给模型"这个答案没有错，但它就像有人问"飞机为什么能飞"，你回答"因为有翅膀"——没错，但只说了表面。

今天这篇文章，小编带你把这道题背后的工程细节一层层挖出来：

-

• LLM 为什么"记不住"，根本原因是什么
-

• 两种"多轮"怎么区分，面试最容易混
-

• Session 是什么，怎么隔离，为什么要加锁
-

• 消息链里的 tool_call_id 是干什么的，断链会发生什么
-

• 上下文拼装时，模型看到的远不止聊天记录
-

• 对话太长了，五层压缩防线如何兜底
-

• 崩溃恢复、原子写入，工程上怎么保证不丢数据
-

• 记忆为什么要分层，各层有什么区别

最后附一份面试答题框架，拿走直接用。

---

## 二、从根上理解：LLM 为什么"记不住你"

讲上下文管理之前，必须先搞清楚一件事：**大模型 API 本身是无状态的。**

"无状态"是什么意思？小编举个例子。

你在代码里调用 LLM API，第一次发了这条消息：

```
# 第一次 API 调用
response = llm.call(messages=[
    {"role": "user", "content": "我叫小张，我在做 RAG 项目"}
])
# AI 回复："好的，小张！……"
```

紧接着第二次调用，你只发了新问题：

```
# 第二次 API 调用（只传了新问题）
response = llm.call(messages=[
    {"role": "user", "content": "我叫什么名字？"}
])
# AI 回复："我不知道你叫什么名字……"
```

它真的不知道。不是在装傻。

因为第二次调用，你只发了一条新消息，完全没有把第一次的对话传过去。**每次 API 调用，模型只能看到你这次传来的 messages，上一次调用的内容对它来说根本不存在。**

每次调用 LLM API，就像给一个**完全失忆的人**打电话。你得把所有背景从头告诉他，他才知道你在说什么。

>

💡 **一句话定义**：Agent 的多轮对话上下文管理，不是"模型自己记住了"，而是**我们写的代码，在每次调用模型前，把需要的历史拼进 messages 重新发过去**。

"记忆"是代码维护的，不是模型自带的。

这就是上下文管理存在的根本原因。

---

## 三、先分清两种"多轮"——面试必考，容易混

很多人把两种"多轮"混在一起说，面试官一追问就露馅了。分清楚这两种，后面每个章节才能对号入座。

### 3.1 跨回合多轮：用户和 AI 的来回对话

这是大家最熟悉的多轮：

```
第 1 轮
用户：我叫小张，我在做 RAG 项目
AI：你好，小张！RAG 是个好方向……

第 2 轮（隔了 10 分钟）
用户：我的项目用什么语言？
AI：你之前提到是 Python      ← 它怎么知道的？
```

第二轮能回答"Python"，是因为代码在发第二轮请求时，把第一轮的对话历史一起塞进了 messages：

```
系统提示：你是一个 AI 助手……
[第一轮] 用户：我叫小张，我在做 RAG 项目
[第一轮] AI：你好，小张！……
[当前]   用户：我的项目用什么语言？
```

**模型没有记忆，代码帮它记的。**

### 3.2 单回合内部多轮：Agent 自己在循环

这种不太直观，但做 Agent 开发必须理解。

用户只发了一句话：`帮我查 pyproject.toml，告诉我最低 Python 版本`

这句话背后，Agent 内部发生的事是：

```
第 1 次调 LLM
↓ 模型决定：先用 read_file 工具读取文件

执行 read_file
↓ 返回文件内容（可能有几十行配置）

第 2 次调 LLM（把文件内容也塞进 messages）
↓ 模型根据内容生成最终答案："最低版本是 Python 3.10"
```

用户只看到了一次对话，内部经历了多次 LLM 调用——每次调用都要维护一份完整的上下文。

**为什么要分清这两种？**

因为它们涉及的上下文管理机制不同：跨回合多轮靠 Session 持久化来恢复历史；单回合内部多轮靠 AgentRunner 在内存里维护当前循环的 messages。面试回答时分开说，才能体现你真的理解了这两个层次。

![](https://mmbiz.qpic.cn/mmbiz_gif/Xsy64ZIAuLqoAHq0ZhRZRWiap9GCT5z3jU8icMYxMayB41hic5h7cjick6x53DQX152tQ49S2l5icibo4C8UtAgK0juATqictlcNic3IK0QHQAEpKtQ/640?wx_fmt=gif&from=appmsg)

>

---

## 四、一条消息进来，系统到底做了什么？

好，现在小编带你看一个真实的 Agent 框架（nanobot）是怎么处理一条消息的。

### 4.1 七步状态机

消息进来之后，系统走七个阶段，每个阶段职责清晰：

![](https://mmbiz.qpic.cn/mmbiz_png/Xsy64ZIAuLr8w1Xy9icC3yj1eThuoefIaVll3zEy5gBKUa7ZFRxia6e1br9YPpfGhNnhYyN8T3xWnibOibxsp8vPeE3kMdloeVemia9tI8Eru9qI/640?wx_fmt=png&from=appmsg)

**因为状态机可以恢复。** 如果系统在 RUN 阶段崩溃，下次重启时 RESTORE 阶段能识别出"上次没做完"，从断点继续，而不是从头重来。这是后面"崩溃恢复"章节的关键设计。

下面我们逐步拆解 BUILD → RUN → SAVE 这三个核心状态。

---

## 五、SESSION：每段对话都有一张"身份证"

### 5.1 session_key 是什么

从第四章的状态机可以看到，消息进来之后，第一步就是"识别 session_key"——在 RESTORE、BUILD 等阶段开始之前，系统先要搞清楚这条消息属于谁的对话。

系统用 `session_key` 区分不同对话窗口：

```
# 默认格式：频道:聊天ID
session_key = f"{channel}:{chat_id}"

# 实际例子
"telegram:12345"   # Telegram 某个用户的私聊
"cli:direct"       # 在命令行直接运行
"slack:C001"       # Slack 某个频道
```

**为什么要隔离？**

小张在 Telegram 跟 Agent 聊了他的 RAG 项目，小李在 Slack 问了一个完全不同的问题。如果没有 `session_key` 隔离，两人的对话历史会混在一起——AI 可能拿着小张的背景去回答小李的问题。

`session_key` 就是每段对话的"门牌号"，不同门牌，对话不混。

### 5.2 同一个 Session，为什么必须加锁？

这是面试追问里很经典的一个点。

想象一个场景：同一个聊天窗口，用户快速连发了两条消息：

```
消息 A：帮我查一下明天天气
消息 B：顺便看看适不适合骑车
```

两条消息几乎同时到达，系统如果并发处理同一个 Session 会怎样？

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Xsy64ZIAuLpuvJEqs1PFHJ9J9F8YBkTRmKjiaaSRfLrAIvt9j8eSMBKCbSIgYcsfrVWQ5NGu2REfqEtZWbI7iaaiakxmyHAXiaCF4wkJmAVlS0c/640?wx_fmt=png&from=appmsg)

`session_key` 准备一把 `asyncio.Lock`：

-

• **同一个 Session**：串行，一个处理完才轮到下一个
-

• **不同 Session**：可以并发，互不影响

![](https://mmbiz.qpic.cn/mmbiz_png/Xsy64ZIAuLo30UbvsLN7icicD8STN2KDI2pK51yQzST03ZdibO2x6YWicZOiaJRvVUOcrqHDvKqDmfj8Psp6lNLqQCm52YRvL81hyfeXPxPxp2uI/640?wx_fmt=png&from=appmsg)

###

nanobot 把每段对话保存成 JSONL 文件：

```
workspace/sessions/
├── telegram:12345.jsonl    ← 小张的对话记录
├── cli:direct.jsonl
└── slack:C001.jsonl
```

JSONL 格式每行一个 JSON 对象。好处是：哪怕写到一半进程崩溃，已经写完的行不会损坏，未完成的行顶多就是残缺的那一行。

读取时的优先级：

```
先查内存缓存（热数据，最快）
        ↓ 没有命中
再读 JSONL 文件（从磁盘加载）
        ↓ 文件不存在
创建新的 Session（第一次对话）
```

---

## 六、消息结构：工具调用那条链，不能断

### 6.1 四种角色的消息

Session 里存的消息不只是"用户说了什么、AI 说了什么"。一段包含工具调用的完整对话，在 Session 里长这样：

```
# ① 用户发来的问题
{"role": "user", "content": "帮我查北京今天的天气"}

# ② 模型决定调用工具（只声明，还没执行）
{
    "role": "assistant",
    "content": "",              # 没有文字，只是在声明要调工具
    "tool_calls": [{
        "id": "call_abc123",    # ← 给这次工具调用分配了一个 ID
        "function": {
            "name": "search_weather",
            "arguments": '{"city": "北京"}'
        }
    }]
}

# ③ 工具执行完毕，返回结果
{
    "role": "tool",
    "tool_call_id": "call_abc123",   # ← 必须和 ② 里的 id 完全一致
    "name": "search_weather",
    "content": "北京今天晴，25度，东南风3级"
}

# ④ 模型读取工具结果，生成最终回答
{"role": "assistant", "content": "北京今天晴，25度，非常适合出门！"}
```

### 6.2 tool_call_id：这条链断了，API 会报错

注意消息 ② 和 ③ 之间那对 ID：`call_abc123`。

小编把它理解成**快递单号**：

-

• 消息 ②：模型填了一张发货单，单号是 `call_abc123`，注明要取 search_weather 这个工具的结果
-

• 消息 ③：工具执行完，带着同一个单号 `call_abc123` 把结果送回来
-

• 单号对不上，或者有单号但找不到对应的货（或有货但找不到单号），整个流程就断了

![](https://mmbiz.qpic.cn/mmbiz_png/Xsy64ZIAuLrqJ3mnO74URGluducd02W8lgShJPlTxg8XNZ6TKohWDNSoibxyetcFBspvB3ViboiaGnEVEMZDAYM9z7BfnyK8Fu17DS9iawFXDDA/640?wx_fmt=png&from=appmsg)

###

既然 tool_call_id 必须配对，那切断历史就很有讲究了。

假设 Session 里已经有 50 条消息，现在因为 Token 预算，只能取最近 20 条。

很可能出现这种情况：

```
第 30 条：assistant 声明调用工具（call_id = call_xyz）← 被切掉了！
第 31 条：tool 返回结果（tool_call_id = call_xyz）  ← 保留了
...
第 50 条：当前消息
```

发给模型的消息链里，第 31 条"工具结果"找不到对应的"工具声明"。

这就叫**孤儿工具结果**。主流模型 API 遇到这种不合法的消息链，会直接报错拒绝请求。

所以 `get_history()` 必须做额外检查：从合法的用户回合边界开始切，保证每一个 tool_call_id 都有对应的声明。

>

💡 "上下文管理不只是'选多少条'，更重要的是：**选出来的消息链结构必须是合法的**。"

---

## 七、上下文拼装：模型看到的，远不止聊天记录

历史读取好了，还要经过 `ContextBuilder` 把所有素材拼在一起，才能变成发给模型的最终 messages。

发给 LLM 的完整结构是：

```
  messages = [                                            
      {"role": "system", "content": system_prompt},      
      ...history...   ← 筛选过的历史消息                  
      {"role": "user", "content": 当前消息 + 运行时信息}  
  ]                                                       

```

三段拼在一起。重点说说每段里装了什么。

### 7.1 System Prompt 里装了九样东西

很多人以为 system prompt 就是"你是一个智能助手"这几个字。nanobot 的 system prompt 拼装了以下内容：

身份说明、行为规范、人格设定、用户偏好、工具使用规则、长期记忆、skills说明、近期归档摘要，session压缩摘要

这就解释了两个常见问题：

**"为什么 Agent 能记住我的偏好？"**

用户说"我习惯看简洁回答"，系统把这条信息写进 `USER.md`。下次对话时，`USER.md` 的内容拼进 system prompt，发给模型。模型每次都是刚醒的，但有人帮它备好了用户档案。

**"隔了几天回来，Agent 还知道上次聊了什么？"**

旧对话生成的摘要保存在 Session metadata 里，下次对话时作为第 ⑨ 条塞进 system prompt。不是模型自己记的，是摘要帮它"记"的。

### 7.2 当前消息后面还附了什么

用户发来的消息，末尾会自动附上一段运行时信息：

```
用户原始消息内容

<system_metadata>
Current Time: 2026-08-07 10:30:00
Channel: telegram
Chat ID: 12345
MCP 连接状态: 3 个工具可用
</system_metadata>
```

这段信息为什么不放进 system prompt？

因为时间、连接状态**每次都变化**。放进 system prompt，system prompt 每次都不同，**Prompt Cache**（按前缀缓存）就无法命中。把稳定内容放 system prompt，把易变信息放用户消息末尾，缓存命中率更高——实际上能省下不少 token 费用。

---

## 八、Runner 内部：LLM-工具循环是怎么工作的

BUILD 阶段拼装好 messages 之后，RUN 阶段的 `AgentRunner` 接手，开始单回合内部的 LLM-工具循环（就是第三章说的"单回合内部多轮"）。

核心逻辑用伪代码来看：

```
# -----------------------------------------------
# 🔧 AgentRunner 核心循环（简化版）
# -----------------------------------------------

# initial_messages 来自 BUILD 阶段 ContextBuilder 的输出：
# [system_prompt, ...history..., 当前用户消息]
messages = list(initial_messages)

for iteration in range(max_iterations):   # 设上限，防止工具死循环

    # ① 每次发给模型前，先"治理"一遍上下文（后面细讲）
    messages_for_model = treat_context(messages)

    # ② 调用 LLM
    response = await llm.call(messages_for_model)

    if response.has_tool_calls:         # 模型要调工具
        # ③ 把"我要调工具"这个声明追加到 messages
        messages.append({
            "role": "assistant",
            "tool_calls": [{"id": "call_abc123", "function": {...}}]
        })

        # ④ 真正去执行工具
        results = await execute_tools(response.tool_calls)

        # ⑤ 把工具结果也追加进去（call_id 必须和 ③ 一致！）
        messages.extend([{
            "role": "tool",
            "tool_call_id": "call_abc123",   # ← 和 ③ 里的 id 相同
            "content": "工具返回的内容"
        }])

        continue    # 让模型继续看工具结果，决定下一步

    # 模型给出了最终文字答案，结束循环
    messages.append(response.final_message)
    break
```

### 8.1 每轮发送前的"上下文治理"

注意步骤 ① 里的 `treat_context()`——每次调用 LLM 之前，都要先对 messages 做一遍治理。

这一步很多人不知道，但它是保证上下文合法和不超 Token 的关键：

治理操作

干了什么

为什么要做

删孤儿工具结果

删除找不到对应声明的tool 消息

防止API 报错 （参考第六章）

补缺失工具结果

工具执行中断时， 补一条合成错误信息

保持call_id配对完整

压缩旧工具输出

把几轮前的大工具结果压缩变小

防止单个工具结果撑爆上下文

限制工具结果总量

工具结果不能占超过预算的token

给历史和用户信息留空间

裁剪旧历史

整体还超出预算时，删最旧的消息

控制整体token数

**重要区别**：治理只改变"本次发给模型的副本"（`messages_for_model`），Session 文件里的完整记录不动。这两个不是同一份数据，不要混淆。

---

## 九、对话太长了？五层压缩防线来救场

这是整个上下文管理里最复杂，也是生产环境最重要的部分。

小编先给你看整体结构：

```
对话越来越长，Token 越占越多
         ↓ 超出回放窗口
第一层：Session 回放窗口限制
         ↓ 发给模型前还是太长
第二层：Runner 实时治理（压缩工具结果、裁旧历史）
         ↓ 估算整体 prompt 超预算
第三层：Consolidator——让 LLM 把旧消息写成摘要
         ↓ 会话空闲超过 TTL
第四层：AutoCompact——后台自动压缩整个会话
         ↓ Session 文件本身太大
第五层：文件硬上限，强制保留最近合法后缀
```

```

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/Xsy64ZIAuLprDE5NwDJzcnOia3grHeGNGPeSOunJFXTvCgxDDdTPGg5iaLib05mdG4icBv6UC0SUP3GwjSicVhGXY1yU8UicITLrCoE7XH4euP3GE/640?wx_fmt=gif&from=appmsg)

```

>

### 第一层：Session 回放窗口

BUILD 阶段 `get_history()` 读取历史时，用两个条件决定选哪些：

-

1. **消息条数上限**：比如只取最近 50 条
-

2. **Token 预算上限**：从最新消息往前倒推，超预算就截止

同时必须从合法的用户回合边界开始，不留孤儿消息（第六章讲过的）。

这一层是最轻量的过滤，没有任何额外开销。

### 第二层：Runner 实时治理

第八章里讲的 `treat_context()`，在每次调用 LLM 之前自动执行：

-

• 把几轮之前的大工具结果压缩（比如读了个大文件，后续几轮不需要全文）
-

• 整体还超预算就裁剪最旧的一段历史

这层只改发给模型的副本，Session 原始记录不动。

### 第三层：Consolidator——让 AI 给自己写摘要

当估算整体 prompt 超过 Token 预算时，`Consolidator` 触发：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Xsy64ZIAuLqj7OB2QIwiaEGLtwfKldytYPSvTzmTePMY7llPahdmQ9hApJ38OaFtv8iafdWfkfvJ80W0jrW9hzibHjtVNJJILLicibQEYsJhKuYE/640?wx_fmt=png&from=appmsg)

### 第四层：AutoCompact——空闲时的后台整理

会话超过一定时间没有活动（超过 TTL），后台自动触发：

![](https://mmbiz.qpic.cn/mmbiz_png/Xsy64ZIAuLojicG8s6JKqhXiaTp7xtJF7JcxO7huTKfMU10n6w0gl0unnumaTfPiacTK3aIl1VWz2sibEkw5MTYxfAPDQjnU2PiczFCjtzORN8uk/640?wx_fmt=png&from=appmsg)

### 第五层：Session 文件硬上限

JSONL 文件达到磁盘硬上限（比如文件大小超过某个阈值），强制处理：

```
保留最近合法的消息后缀（有头有尾，结构完整）
            ↓
被移除的更旧部分做原始归档（防止彻底丢失）
```

这是最后一道防线，防止 Session 文件永久无限增长撑爆磁盘。

---

## 十、崩溃了怎么办：故障恢复机制

这是面试追问里比较冷门、但很能体现工程功底的点。

### 10.1 不处理崩溃会怎样

假设 Agent 正在执行一个工具链，突然进程崩溃：

```
assistant：我要调用 3 个工具完成任务
tool_1 结果：已完成 ✅  已写入 Session
tool_2：正在执行 ← 这时崩溃了 💥
tool_3：还没开始
```

如果什么都不处理，下次启动时 Session 文件里是：

```
assistant 消息：声明要调用 tool_1、tool_2、tool_3（三个 call_id）
tool_1 结果：有 ✅
tool_2 结果：无 ← 孤儿 call_id，声明有结果却没有
tool_3 结果：无 ← 同上
```

发给模型，API 报错。用户发来的消息永远得不到回复，体验直接崩掉。

### 10.2 四步恢复机制

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Xsy64ZIAuLpz3obpbNF6U8f1RVgEzCNy88qtIy7VpUl7ucmMiaTDmdS3hlB1P0oKRFibJ6NHtt8ibJDnw2PlY9Ss6QFic2uyL3K9RYTYqndlWkc/640?wx_fmt=png&from=appmsg)

****

用户消息在真正调 LLM 之前就已经持久化。崩溃后，用户的输入不会丢失，下次启动时系统知道用户问了什么。

**② 工具执行边界保存 Checkpoint**

每执行完一个工具，都把当前进度保存进 Session metadata：

```
# Session metadata 里的 runtime_checkpoint
runtime_checkpoint = {
    "assistant_message": ...,          # 模型的工具声明（含所有 call_id）
    "completed_tool_results": [...],   # 已完成的工具结果
    "pending_tool_calls": [...],       # 还没执行的工具
    "iteration": 2,                    # 当前是第几次迭代
}
```

就像打游戏每关结束自动存档——崩了可以从上次存档继续，不用从头来。

**③ RESTORE 阶段重建消息链**

第四章状态机里的 RESTORE 阶段就是干这个的。下次处理同一个 Session 时：

-

1. 检测到 Session metadata 里有 `runtime_checkpoint`
-

2. 恢复已完成的工具结果
-

3. 对没完成的工具调用，补一条合成错误："任务在完成前被中断"
-

4. 检查与 Session 尾部有没有重复，避免重复追加
-

5. 清除 checkpoint，消息链重新合法，可以继续新的请求

**④ 原子写入防止文件半损坏**

JSONL 文件的写入不是直接覆盖，而是：

```
# ① 先写到临时文件（写到一半崩溃，正式文件还是旧的完整版）
with open("session.jsonl.tmp", "w") as f:
    f.write(content)

# ② 写完确认无误，原子替换正式文件
os.replace("session.jsonl.tmp", "session.jsonl")
```

`os.replace()` 在操作系统层面是原子操作——要么完全替换成功，要么保持旧文件，不会留下"写到一半"的损坏文件。

---

## 十一、记忆的四个层次：不要搞混了

面试常被问到"长期记忆和历史有什么区别"，很多人说不清楚。

小编用一个"员工的工作记录"来类比这四层：

![](https://mmbiz.qpic.cn/mmbiz_png/Xsy64ZIAuLoibicX2DOLfCucYDsEldv2zJfKcUompA2DkNibl4oMLiazaZlD2KiassfzEscMxbGBTNibrWTf1c5WNGia4gl163hyDGrnBOoCUvgI5I/640?wx_fmt=png&from=appmsg)

对应存储

触发写入的时机

主要用途

原始消息

sessions/

每轮对话结束后save

精确回放最近上下文

session摘要

session.metadata

AutoCompact 或会话压缩

注入System Prompt,帮模型“想起”就内容

history.json

memory/history.json

Consolidator 归档时

可别Dream 进一步加工

Memory.md

memory/memory.md

Dream模块提炼时

跨会话的长期知识库

**最本质的区别**：

-

• **历史**：记录"发生了什么"（每一句，包括废话，全都存）
-

• **长期记忆**：保存"以后还有用的稳定事实"（只存精华）

不要把每条聊天记录都当长期记忆——那叫流水账，不叫记忆。

---

## 十二、用一个完整例子串起来

光讲概念容易绕，小编带你把小张和 Agent 的对话完整过一遍，把前面十一章的概念都对号入座。

### 第一轮：第一次对话

```
小张：我叫小张，正在用 Python 开发一个 RAG 项目。
```

系统做了什么：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Xsy64ZIAuLqeFkK8YAo2viaZXIncYf9KG3gxwd7u8o9uf1ItfXtHgyfNQKGVia3Oia9rg6YDr5a7eEwicalP1vZyLHkvTyfTckDhXOnoagJkaqA/640?wx_fmt=png&from=appmsg)

###

```
小张：帮我读取 pyproject.toml，告诉我最低 Python 版本。
```

系统做了什么：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Xsy64ZIAuLoTk2QEDz3ISvTEgRMDBaerGTJp5QEVINTMelzZ68Vn8datJ5KaOEAUpKOUt3az23I0J5YMhTF7pUhIxg1dS6sKXrTicqWMibzPc/640?wx_fmt=png&from=appmsg)

###

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Xsy64ZIAuLp3gRJ7b2qkghYibibtC1ibCYcbicQvuKGl5hWRXYNWawlB4ticdJVl2tbuXaD42TkRfhAfZkeABlO5sUpADRkS4srkYLwVbQ4MzdSU/640?wx_fmt=png&from=appmsg)

---

## 最后：这道面试题，你该怎么答

原理全讲完了，最后帮你整理答题框架。

**这不是让你背的——理解了上面十二章，这些话你自己也能说出来。**

### 一分钟版本

     大模型 API 是无状态的，多轮对话能力由应用层实现。系统用 session key 隔离不同会话，把 user、assistant、tool call、tool result 四类消息持久化。每次新请求，从 Session 里按消息条数和 Token 预算选最近一段合法历史（不能随意切，切断了 tool_call_id 配对就报错），再拼接 system prompt（含长期记忆、历史摘要）和当前消息发给模型。

     Agent 单回合内，工具调用和结果继续追加到 messages，循环调用模型直到得出最终答案。上下文过长有五层兜底：Session 回放窗口 → Runner 实时治理 → Consolidator LLM 摘要 → AutoCompact 空闲压缩 → 文件硬上限。同时要保证 tool call 与 result 的 call_id 配对、同 Session 串行加锁、崩溃后 checkpoint 恢复消息链、JSONL 文件原子写入。

### 五个高频追问

面试官问

核心回答 

Token 上限怎么处理？

五层：回放窗口 → 实时治理 → LLM 摘要 → 空闲压缩 → 文件硬上限，层层兜底

为什么不能随意切历史？

随意切会产生孤儿 tool 消息（声明和结果 call_id 不配对），主流 API 直接报错

并发请求怎么处理？

每个 session_key 一把 asyncio.Lock，同 Session 串行，不同 Session 并发

Agent 崩溃了怎么恢复？

提前保存用户消息 + 工具边界存 checkpoint + RESTORE 阶段补齐配对 + 原子写入 

长期记忆和历史有什么区别？

历史是完整流水账；长期记忆是提炼后跨会话有价值的稳定事实

### 记住这个口诀

**分、存、取、拼、跑、配、裁、压、记、复**

```
分 → session_key 隔离每段对话
存 → 持久化 user/assistant/tool 消息到 JSONL
取 → 按条数+Token预算+合法边界选历史
拼 → 拼 system_prompt + 历史 + 当前消息
跑 → Runner 循环调 LLM 和工具
配 → tool_call_id 必须配对，否则断链
裁 → 超预算时裁旧历史和旧工具结果
压 → Consolidator 让 LLM 把旧消息压成摘要
记 → 稳定事实提炼到 MEMORY.md 长期保存
复 → checkpoint + 原子写入支持故障恢复
```

面试时能围绕这十个字展开，再举出 1-2 个具体机制（比如孤儿消息为什么会报错、asyncio.Lock 怎么解决并发问题），就已经比大多数人答得完整了。

---

觉得这篇讲透了的话，**点个关注在看**吧——帮更多在准备 AI 岗面试的朋友看到这篇。
下期见 👋
