# AI Native 工作方式:像管理团队一样用 AI 的五件事

> **一句话摘要**:面对标准明确、能快速验证的任务,AI 执行往往比人更快、更稳。但 AI Native 不是"更频繁地使用 AI",而是一次**角色切换**——像管理团队一样做好五件事:定目标(允许不完善)、定原则(纠偏沉淀成机制)、配资源(承认 AI 在具体任务上更强)、看结果(忍住不盯每一步)、做决策(只在关键时刻介入)。AI 负责计划、执行、检查、迭代;人负责目标、原则、边界和关键判断。
>
> **来源**:微信公众号《AI Native,和管理一样反人性》,https://mp.weixin.qq.com/s/dr3G1zIn0gusnGd3KCLgBw;原始资料存档于 `docs/inbox/ai-native-manage-source.md`

## 概念:为什么 AI Native 和管理一样"反人性"

一个 Codex 自主设计的 App icon 效果远超预期——朋友问出灵魂问题:"真能智能到这个程度?足够自动化?"答案不仅是肯定的,而且指向一个更深的判断:

!!! tip "角色切换,不是工具升级"
    **AI Native 不是更频繁地使用 AI,而是一次角色切换:**
    - AI 负责:**计划、执行、检查、迭代**;
    - 人负责:**目标、原则、边界和关键判断**。
    过去,"能力强"是亲自把事情做好;以后,"能力强"是**让一套系统持续把事情做好**。

"反人性"在于:管理者和 AI 使用者都面临同一种诱惑——**回到亲手执行**。微操、盯过程、接过鼠标,这些都是即时掌控感,却是对"AI Native"的背叛。能做到"忍住",就是这份工作方式最难也最值钱的地方。

## 原理:五件事的完整框架

### 1. 定目标:允许一开始并不完善

复杂目标很难一次说清。正确做法:**先给出当前目标,让 AI 完整执行,再根据结果纠偏**。

!!! warning "反人性点"
    人总想直接告诉 AI 每一步怎么做——这样更有掌控感,却又回到了微操。目标要"先跑起来再校准",而不是"一次说全"。

### 2. 定原则:把纠偏沉淀成机制

原则也不是提前想全的——**很多边界,只有真正执行后才会暴露**。关键是发现问题后的处理方式:

!!! tip "纠偏的三种层次"
    1. **最低效**:只在对话里提醒("这次注意点")——下一轮大概率重犯;
    2. **有效**:沉淀成文档/脚本,作为 AI **验证输入的起点**——可继承、可执行、可验证;
    3. **闭环**:下一轮必须遵守,且检查点能验证是否遵守。

这正呼应站内 [Spec-First](spec-first-decision-stack.md) 的"证据等级"与 [AI 协作规则设计](../../03-agents/agent-collaboration-rules.md) 的"规则沉淀"——原则的价值在机制化,不在提醒。

### 3. 配资源:承认 AI 在具体任务上更强

为不同任务选择合适的模型、工具和上下文;**人只控制预算、权限和风险**。

!!! warning "最反人性的地方"
    承认自己做了很多年的事,AI 现在可能做得更好。管理者同样需要招聘某个方向上比自己更优秀的人——认可并尊重。这是"能力观"的根本转变:你的价值不在"我会做",而在"我知道该让谁做、怎么设边界"。

### 4. 看结果:忍住不盯每一步

自己做,过程完全可见;交给 AI,过程会暂时失控,人很容易不断追问和干预。但管理不是盯过程,而是:

- **设检查点**,用测试、截图和数据验收结果;
- **发现偏差也不接过鼠标**,而是修正目标或机制,再让 AI 重新执行。

!!! tip "验收结果 vs 盯过程"
    这呼应 [生产级 Agent 9 层架构](../../03-agents/agent-production-architecture.md) 的"验证才算完成"与 [OpenAI 官方 Prompt 指南](openai-prompt-guide.md) 的"生成后必须验证"——检查点是机器的,人是设定检查点的人。

### 5. 做决策:只在关键时刻介入

普通问题让 AI 处理;方向选择、风险取舍和高权限操作,再由人介入。

!!! note "亲自动手与判断方向"
    亲自改一个按钮很轻松,判断方向该往哪里走却很难——**后者才是人的核心价值**。把"做事"的成就感让给 AI,把"做判断"的稀缺性留给自己。

## 代码 / 实现:管理式任务循环(纯 Python)

把"定目标 → AI 执行 → 检查点验收 → 偏差则修正目标/机制而非接管 → 再执行"落成可运行演示:

```python
# —— 管理式任务循环:人定目标与检查点,AI 负责执行与迭代 ——
def manager_loop(goal, execute, checkpoint, refine, max_rounds=5):
    """人:定目标(goal)+ 设检查点(checkpoint)+ 修正机制(refine);AI:执行(execute)"""
    result = execute(goal)
    for round_no in range(1, max_rounds + 1):
        verdict, evidence = checkpoint(result)
        if verdict == "pass":
            return {"status": "done", "rounds": round_no, "result": result, "evidence": evidence}
        # 偏差:不接管执行,修正目标/机制后让 AI 重跑
        goal = refine(goal, evidence)
        print(f"  第 {round_no} 轮验收未过({evidence}) → 修正目标,重新执行")
        result = execute(goal)
    return {"status": "max_rounds", "result": result}

# —— 场景:让 AI 生成"登录按钮样式",检查点是 CSS 规范 ——
def execute(goal):                       # AI 执行:按当前目标生成
    if "1890ff" in goal:                 # 目标里已写入品牌规范 → 遵守
        return "button { color: #1890ff; }"
    return "button { color: red; }"      # 早期版本:AI 自主发挥,用了未授权红色

def checkpoint(result):                  # 人设的检查点:样式必须符合品牌规范
    return ("pass", "符合品牌色规范") if "red" not in result else ("fail", "使用未授权红色")

def refine(goal, evidence):              # 人修正机制:把规范写进目标(沉淀成可验证输入)
    return goal + "| 品牌规范:按钮主色必须为 #1890ff,禁止 red"

outcome = manager_loop("做一个登录按钮", execute, checkpoint, refine)
print("最终结果:", outcome)
```

## 实践 / 应用:五件事对照表与每日自查

### AI 协作 vs 传统执行的对照

| 维度 | 传统执行(微操) | AI Native(管理式) |
| --- | --- | --- |
| 目标 | 一次说全,说不出就卡住 | 先给当前目标,执行后纠偏 |
| 原则 | 对话里提醒 | 沉淀成文档/脚本,下一轮必须遵守 |
| 资源 | 自己什么都做 | 选对模型/工具/上下文,人控预算权限风险 |
| 过程 | 全程盯着每一步 | 设检查点,用测试/截图/数据验收 |
| 介入 | 随时抢过鼠标 | 只在方向/风险/高权限时介入 |

### 每日自查(五问)

1. 我今天是不是又在"微操"(告诉 AI 每一步怎么做)?
2. 今天发现的纠偏,沉淀成文档/脚本了吗,还是只留在对话里?
3. 我为这个任务配对了模型/工具,还是什么都用默认?
4. 我在盯过程还是设检查点验收结果?
5. 最后那一下"亲自改",是不是本来该让 AI 做?

!!! note "与站内其他文章的呼应"
    - [个人 AI 思维:从"写代码的人"到"AI 协作者"](../../06-enterprise/ai-org-transformation/ai-native-mindset-individual.md):那篇讲认知与数据(经济指数/技能树重写),本文是**操作框架**(五件事管理法);
    - [Spec-First 决策栈](spec-first-decision-stack.md):定原则=证据分级与规则沉淀;
    - [Agent 交接方法论](handoff-handover-methodology.md):看结果=检查点验收,纠偏=修正机制;
    - [AI Coding Harness 设计经验](ai-coding-harness-design.md):定原则=护栏生长,看结果=让 AI 看见问题。

## 总结

- **角色切换**:AI 负责计划/执行/检查/迭代,人负责目标/原则/边界/关键判断——不是更频繁地用 AI,而是换一种工作方式;
- **五件事**:定目标(允许不完善)、定原则(纠偏成机制)、配资源(承认 AI 更强)、看结果(验收不盯过程)、做决策(只在关键时刻介入);
- **反人性三关**:克制微操的掌控感、忍住盯过程的冲动、承认"自己做了很多年的事 AI 做得更好";
- **一句话**:过去能力强是亲自把事情做好,以后能力强是**让一套系统持续把事情做好**。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/dr3G1zIn0gusnGd3KCLgBw;原始资料存档于 `docs/inbox/ai-native-manage-source.md`
- 站内:[个人 AI 思维](../../06-enterprise/ai-org-transformation/ai-native-mindset-individual.md)(认知篇)、[Spec-First 决策栈](spec-first-decision-stack.md)(原则机制化)、[Agent 交接方法论](handoff-handover-methodology.md)(检查点验收)、[AI Coding Harness 设计经验](ai-coding-harness-design.md)(护栏生长)、[OpenAI 官方 Prompt 指南](openai-prompt-guide.md)(验证才算完成)、[给 Coding Agent 立规矩](agent-rules-agents-md.md)(规则沉淀载体)
