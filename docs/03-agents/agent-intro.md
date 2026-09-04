# AI Agent 入门:从"会对话"到"能办事"

> **一句话摘要**:AI Agent 是以大模型为大脑,能自主决策、调用工具、多步执行并达成目标的系统;本文讲清定义、与 LLM 应用的差异、四大能力与提示工程边界。
>
> **来源**:综合公开资料,参考 ReAct(Yao et al., 2022)与 OpenAI Function Calling 文档。

## 概念

**AI Agent(AI 智能体)** 是**能感知环境、自主决策、采取行动达成目标**的软件系统:接收输入与反馈 → 由大模型判断下一步 → 调用工具改变世界 → 分解并逐步完成目标。公式表达:

$$\text{Agent} = \underbrace{\text{LLM}}_{\text{大脑/推理}} + \underbrace{\text{工具}}_{\text{行动}} + \underbrace{\text{记忆}}_{\text{上下文/经验}} + \underbrace{\text{规划}}_{\text{任务分解}}$$

!!! note "关键认知"
    普通 LLM 应用是"**一次性生成**":提问 → 回答 → 结束;Agent 是"**循环执行**":生成动作、观察结果、再生成动作,直到任务完成。差异不在模型,而在外层**编排循环(agent loop)**。

### 与普通 LLM 对话应用的区别

| 维度 | 普通 LLM 应用 | AI Agent |
| --- | --- | --- |
| 交互模式 | 单轮问答 / 纯文本 | 多轮 think-act-observe 循环 |
| 决策主体 | 用户拆任务 | Agent 自主拆解下一步 |
| 外部世界 | 只输出文本 | 调工具:读数据、写文件、发请求 |
| 失败处理 | 重新提问 | 观察反馈、纠正路线、重试 |

### 四大能力

1. **规划(Planning)**:把目标拆成子任务并排序;典型模式:ReAct、Plan-and-Execute。
2. **工具使用(Tool Use)**:通过 function calling 调用搜索、数据库、计算器等,突破"只会生成文本"。
3. **记忆(Memory)**:短期(上下文、任务栈)+ 长期(向量库、知识库)。
4. **行动(Action)**:执行代码、调 API、回复用户。

### 与提示工程的边界

- **提示工程**优化**单次生成**(prompt、few-shot、格式约束);
- **Agent** 优化**多次思考 + 行动闭环**(何时思考、行动后干什么、结果如何回填);
- 边界连续:写 ReAct 模板是提示工程;循环调模型、执行工具、维护状态才是 Agent。

### Agent 的产品本质:认知和行动产品

!!! tip "Agent 不是 SaaS 的替代品"
    传统 SaaS 解决的是**记录问题**(填表单、存数据);Agent 解决的是**执行问题**(你说一句话,它把整个任务做完)——它是一种新的产品类型:**认知(决策)和行动产品**。

- **产品结构演变**:原来的 SaaS 会**下沉一层**,变成承载事实的内容;Agent 成为用户**新任务的入口**,甚至替代人成为"循环的数字劳动力";
- **核心价值**:**缩短用户"起心动念到心想事成"的距离**——端到端完成用户的高价值任务(AI Coding 工具不是新 Office,而是新一代工作台的雏形:用户从直接操作对象,变成委托 Agent 管理任务过程);
- **通用 vs 垂直,两种产品逻辑**:
  - **通用 Agent**(CC/Codex 类):追求大而全,吃白领生产任务;形态以 **Chat 为主**(灵活性最强,能覆盖更多过程);
  - **垂直 Agent**(销售/客服/供应链/运营):必须有一层**业务语义层**(业务策略与知识)——垂直业务里约 20% 的"黄金流程"占 80% 工作量,要用 Workflow 固化、用业务策略层规范 Agent 行为方向;
- **B 端 Agent 的"三面设计"**:Chat 是**探索面**(如 SaaS 的新建表单),但企业级产品还需要 **运营面**(Dashboard/列表/运营监控——真正的工作场景)和 **管理面**(Agent 运行监控、每个任务的状态、出问题如何人工介入)。**只有 Chat 的 B 端 Agent,还不是合格的企业级产品。**

## 原理

### 核心循环:think-act-observe

几乎所有 Agent 都围绕同一循环工作:

```
while 任务未完成 and 步数未超限:
    thought = LLM(当前状态)    # 思考
    action  = 解析出动作        # 决策
    result  = execute(action)  # 行动
    state  += result           # 观察:回填状态
```

- **think**:把新观察与记忆交给 LLM 重新推理;
- **act**:把动作翻译成真实调用(函数 / HTTP / 命令);
- **observe**:把执行结果(成功、失败、报错)写回上下文。

每一步的状态都是下一步的输入——这正是 Agent **自我纠错**的来源:失败信息带回上下文,LLM 换一条路再试。

### ReAct 模式

**ReAct(Reasoning + Acting)** 是主流 Agent 范式(Yao et al., 2022),让模型输出"推理 + 动作",再拼接观察结果:

```
Thought 1: 用户要查北京天气,需要天气工具。
Action 1:  search_weather("北京")
Observation 1: 北京 晴转多云,23°C
Thought 2: 还需要计算 7×8。
Action 2:  calc("7 * 8")
Observation 2: 56
Thought 3: 信息齐全,给出最终答复。
Final: 北京 23°C,7×8=56。
```

推理与行动**相互增强**:推理决定下一步,观察修正后续推理,缓解纯 CoT"想得对、做不出"的问题。

### Agentic Loop:循环的四种类型

!!! tip "Loop Engineering"
    Claude Code 团队对 **agentic loop** 的定义:Agent **重复执行工作 cycle,直到满足 stop condition**。四类 loop 由四件事区分:**如何触发、如何停止、使用哪一种 primitive、最适合哪一类任务**。并不是所有任务都需要复杂 loop——**应当从最简单的方案开始**。

| Loop 类型 | 触发方式 | 停止条件 | 典型 primitive | 最适合 | Usage 控制 |
| --- | --- | --- | --- | --- | --- |
| **Turn-based**(手动) | 用户输入一条 prompt | Claude 判断任务完成 / 需补充 context | 普通 prompt + SKILL | 非固定流程的短任务(探索、决策) | 更具体的 prompt;把"人工验证步骤"编码进 SKILL.md 改进 verification,减少 turn 数 |
| **Goal-based**(目标) | 实时输入一条 manual prompt | goal 达成,或达到最大 turn 数 | `/goal` | 有**可验证 exit criteria** 的任务(如"首页 Lighthouse 分数 ≥ 90,最多尝试 5 次") | 明确完成标准 + 显式 turn 上限;deterministic criteria(测试通过数/分数阈值)最有效 |
| **Time-based**(定时) | 指定的时间间隔 | 你取消它,或工作完成 | `/loop`(本机)、`/schedule`(云端) | 重复性工作、与外部 system 交互(每天早晨汇总 Slack、检查 PR) | 拉长间隔;按 event 而非时间响应 |
| **Proactive**(主动) | event / schedule 触发,无需人实时参与 | 每个 task 达成自身 goal 即退出;routine 持续运行 | `/schedule` + `/goal` + dynamic workflows + auto mode | 持续流入且定义清晰的工作 | 把 routine 路由给更小、更快的 model |

!!! note "验证步骤可以编码成 Skill"
    手动验证步骤可以写进 SKILL.md,让 Agent 端到端检查自己的工作(如"启动 dev server → 交互确认 state change → 截前后截图 → 检查 console 无 error → 跑 performance trace")。**检查越量化,Agent 越容易完成 self-verification。**

!!! warning "常见误解"
    - Agent 不一定比 LLM 更聪明:推理上限由底层模型决定。
    - Agent ≠ 多轮对话:无工具、无目标、无循环只是聊天。
    - 复杂任务需多步迭代,受上下文与成本限制。

## 代码 / 实现

纯 Python 实现最简 think-act-observe 循环。用"模拟 LLM"(`llm_think`,规则决策)代替真实大模型,重点演示**循环骨架**:

```python
"""
极简 Agent:think-act-observe(思考-行动-观察)循环。
用一个"模拟 LLM"根据当前状态决定下一步动作。
"""

# 模拟工具集:Agent 可以调用的能力
TOOLS = {
    "search_weather": lambda city: f"{city} 今天晴转多云,23°C",
    "calc": lambda expr: eval(expr),  # 仅为演示,真实代码不要用 eval
}

def llm_think(state):
    """模拟 LLM 的思考:根据状态返回动作(action)和思考(text)。"""
    request = state["request"].lower()
    if "天气" in request and "search_weather" not in state.get("done", []):
        return {"thought": "用户想查天气,我需要调用天气工具。",
                "action": "search_weather", "action_input": "北京"}
    if "计算" in request and "calc" not in state.get("done", []):
        return {"thought": "用户想计算,我需要调用计算工具。",
                "action": "calc", "action_input": "7 * 8"}
    return {"thought": "所有请求都处理完了,给用户最终答复。",
            "action": "FINISH", "action_input": ""}

def run_tool(action, action_input):
    """执行工具(act 环节)。"""
    if action not in TOOLS:
        return f"未知工具:{action}"
    return TOOLS[action](action_input)

def agent(request):
    """Agent 主循环:think -> act -> observe,直到 FINISH。"""
    state = {"request": request, "step": 0, "done": [], "observations": []}
    max_steps = 5
    while state["step"] < max_steps:
        state["step"] += 1
        decision = llm_think(state)                # think:LLM 决策
        print(f"[第{state['step']}步] 思考:{decision['thought']}")
        if decision["action"] == "FINISH":         # 任务完成
            return f"最终答复:已根据 {len(state['done'])} 次工具调用为你整理好结果。"
        observation = run_tool(decision["action"], decision["action_input"])  # act
        state["done"].append(decision["action"])   # observe:记录观察结果
        state["observations"].append(observation)
        print(f"  -> 行动:{decision['action']}({decision['action_input']!r})")
        print(f"  -> 观察:{observation}")
    return "达到最大步数,停止。"

if __name__ == "__main__":
    print(agent("我想查北京天气,顺便计算 7 乘 8"))
```

**运行**:`python3 agent-intro-demo.py`,纯标准库。要点:

- `llm_think` 扮演大脑,输出 `thought` + `action`——真实 LLM 通过 tool calling 返回同构结构(见《工具调用》);
- `state["done"]` 是**一格最简记忆**,防止重复调用同一工具;
- `FINISH` 是终止信号;实际框架设 `max_steps` 上限防死循环。

### 运行模式与使用要领(Craft / Plan / Ask)

!!! note "教学版四步循环命名"
    上文 think-act-observe 是工程视角;教学/产品视角常用 **Observe(观察)→ Think(思考)→ Act(执行)→ Reflect(反思)** 四步命名(同源于 ReAct,2022)。差别只在拆法:Reflect 把"判断任务是否完成"显式独立成一步——不满足完成标准就回到 Observe 重新看信息。**普通 AI 一次性输出;Agent 跑循环,直到事情真做完。**

**三种运行模式**(决定 Agent 跑到哪一步停,与权限边界——见 [OpenAI Prompt 指南原则 3](../07-agent-coding/experience/openai-prompt-guide.md) 与 [Agent 生产架构](agent-production-architecture.md)——呼应):

| 模式 | 行为 | 适合场景 |
| --- | --- | --- |
| **Craft(执行)** | 直接干,干完汇报 | 写周报、整理文件等低风险任务 |
| **Plan(计划)** | 先出方案让人审,再干 | 高风险 / 复杂决策 |
| **Ask(询问)** | 只读不写,纯讨论 | 技术调研、代码审查 |

**别打断 Agent 的循环**——"AI Agent 不好用"的常见真实原因:

| 打断方式 | 后果 |
| --- | --- |
| 每隔 30 秒问"快好了吗?" | Agent 反复回到"观察"步,循环重跑 |
| 中途换需求("再加个 PPT") | Agent 推倒重来 |
| 关窗口 / 杀进程 | 循环中断,下次从头跑 |

> 启示:把 Agent 当"委派任务的员工"而非"即时应答工具"——给足上下文、别频繁插话、中途改需求 = 让它白跑。(实例:WorkBuddy 用"写周报"逐步拆解四步循环,详见素材 `docs/inbox/agent-loop-breakdown-source.md`。)

## 实践 / 应用

| 场景 | Agent 做什么 | 关键工具 |
| --- | --- | --- |
| 个人助理 | 查日历、订会议、回邮件 | 日历 / 邮件 API |
| 代码助手 | 读仓库 → 写补丁 → 跑测试 | 代码执行、git |
| 数据分析 | 查库 → 清洗 → 出报告 | SQL、pandas |
| 运维 | 看监控 → 定位 → 恢复 | 监控 API、命令执行 |

工程硬约束:① **幻觉沿多步累积**——观察结构化回填;② **成本与延迟**——每步都是 LLM 调用;③ **护栏**——最大步数、超时、工具白名单、敏感操作确认;④ **可观测性**——记录每步 trace。

## 总结

- Agent = LLM + 工具 + 记忆 + 规划,靠 **think-act-observe 循环**把"生成文本"升级为"完成任务"。
- 与 LLM 应用的本质区别:**自主决策、多步执行、工具使用**。
- 四大能力:规划、工具使用、记忆、行动;ReAct 是主流范式。
- 警惕:幻觉累积、成本/延迟、缺护栏的安全风险。

**下一步**:读《[Agent 核心组件](agent-core-components.md)》看四大件如何协作,再学《[工具调用](tool-calling.md)》与《[Agent 框架](agent-frameworks.md)》工程化。

## 延伸阅读

- 站内:[Agent 规划与工作流模式](agent-planning-patterns.md)、[工具调用](tool-calling.md)、[生产级 Agent 9 层架构](ai-infra-layering.md)(loop 设计纪律)、[中金:基于 Loop Engineering 的自动化因子发现引擎](../07-agent-coding/experience/loop-engineering.md)(Loop Engineering 落地案例)
- 外部:Anthropic《Getting started with loops》(https://claude.com/blog/getting-started-with-loops);ReAct(Yao et al. 2022)论文;《拆 Agent:AI 的"自己拿主意"是怎么发生的》(https://mp.weixin.qq.com/s/_QGjNvwnKiFkteC7alEmbA)

- 站内:[Agent 核心组件](agent-core-components.md)、[工具调用](tool-calling.md)、[Agent 框架](agent-frameworks.md)、[LLM 基础](../02-llm/index.md)
- 外部:Yao et al., *ReAct* (2022);Lilian Weng, *LLM Powered Autonomous Agents* (2023);OpenAI *Function calling* 文档
