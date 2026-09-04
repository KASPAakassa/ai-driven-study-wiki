# Agentic Abstention:Agent 该学会"停下来"——停止判断力的设计与实证

> **一句话摘要**:LLM Agent 最缺的不是完成能力,而是"**判断何时继续行动只会浪费算力和用户耐心**"的止损判断力。一篇用 28,000 个任务实证的论文(arXiv:2606.28733)发现:最强基线在网购场景的**及时止损率只有 26.7%**——超过 70% 的情况下,Agent 要么放弃得太晚,要么干脆不放弃。论文提出的 CONVOLVE(上下文工程)不动模型参数,把失败轨迹蒸馏成"停止规则"注入上下文,能把及时止损率翻倍。
>
> **来源**:微信公众号「超能力」《Agentic Abstention:当 AI Agent 该学会"停下来"》(论文独立解读);论文:Luo, Wen & Wang (2026), arXiv:2606.28733;项目:https://lhannnn.github.io/agentic-abstention;代码:https://github.com/lhannnn/agentic-abstention;原始资料存档于 `docs/inbox/agentic-abstention-source.md`

## 概念:粉色枕头困境与"什么时候该弃权"

!!! tip "场景:用户说'帮我买一个粉色客厅枕头,价格在 30 美元以内'"
    Agent 开始搜索:第 1 轮 "pink living room pillow under $30" → 第 2 轮发现没有粉色 → 第 3 轮 "light pink pillow" → 第 4 轮 "pink cushion" → 第 5 轮点进详情发现是桃色 → **第 10 轮**才停下来告诉用户"找不到"。

同一个不可行任务,不同 Agent 的轨迹天差地别:有人第 2 轮就停下解释,有人搜满 10 轮也没停。**问题不在于 Agent 能不能完成任务,而在于 Agent 不知道什么时候该停止。**

| 概念 | 单轮 vs 多轮 |
| --- | --- |
| **传统 LLM Abstention** | 单轮决策:用户问一句,模型答或不答("我不知道") |
| **Agentic Abstention** | 多轮决策:每轮之后判断——继续、回答、还是放弃 |

!!! note "Agentic Abstention 的三问(每轮)**
    ①我已经有足够信息回答吗?②我再搜一轮会不会更接近答案?③环境是不是已经给出足够的否定证据?(继续行动的收益,还值不回用户等待的时间 + 消耗的 token 吗?)

这就像经验丰富的顾问:不会在客户说完需求后立刻说"办不到",也不会在证据已经足够时继续浪费客户的钱——**在恰当的时机给出判断**。

## 原理:三类弃权场景、实证数据与 CONVOLVE 方法

### 三类应该停下来的任务

| 类型 | 含义 | 典型例子 |
| --- | --- | --- |
| **Request-based** | 请求本身有问题 | "推荐一款最贵但性价比最高的手机"(主观偏好矛盾);"拍照好、续航长、又便宜的游戏手机" |
| **Environment-based** | 环境缺少目标或依赖 | "买粉色枕头"但店里没有粉色 |
| **QA Abstention** | 检索后仍无法回答,或问题带假前提 | "请用 Google Scholar 证明 AI 会毁灭人类" |

!!! tip "从单轮判断到多轮决策:问题的本质变了"
    传统弃权只问"我现在知不知道?";Agent 弃权问三句话:现在知道吗?**再行动一次会知道吗?环境已经告诉我"不可能"了吗?** 论文用 POMDP 形式化——Agent 的"信息状态"不断变化,每一次搜索/点击/工具调用都带来新观察,Agent 根据累积信息状态决定继续/回答/放弃。**弃权本身也是一种行动**:继续可能浪费资源,停止可能错过本可解的任务。

### 28,000 个任务的实证(13 个 LLM-as-Agent 系统)

| 场景 | 规模 | 最强基线及时止损率(AbsRec@1) |
| --- | --- | --- |
| WebShop(网购) | 20,000+ 任务 | **26.7%**(70%+ 放弃太晚或不放弃) |
| 终端(代码任务) | 数千 | 21.6%(某些设置) |
| QA(HotpotQA 等) | 数千 | 某些类别 <50% |

这不是某个模型的 bug,而是**整个行业的问题:我们训练 Agent 去完成,却很少训练它们去停止**。

### CONVOLVE:不改模型参数,只改上下文(Agentic Context Engineering)

核心思路:给 Agent 附加一本不断学习的**经验手册(playbook)**——记录"什么信号出现时,Agent 应该停止"。两个阶段:

1. **Reflection(反思)**:让 Agent 跑大量任务收集完整轨迹,反思模型回顾找出——哪一轮环境已告诉"任务不可行"?哪些后续动作是多余的重复?如果更早停止,该用什么理由向用户解释?
2. **Curation(整理)**:把反思提炼成**结构化、可执行**的规则写入 playbook:

> 如果连续两次搜索返回"无结果",且第三次搜索只换了同义词,则停止并解释"环境中找不到匹配商品"。
> 如果终端命令连续返回 "command not found",且用户要求的是特定工具,则停止并解释"环境缺少必要依赖"。

**小模型也能教大模型(规则可迁移)**:用 Llama-3.3-8B 生成停止规则,放进 70B 的上下文——及时止损率从 26.7% 提升到 55.3%,接近 70B 自己学自己的 57.4%。**停止规则本身比模型规模更重要**——不是教学生更多知识,而是给有经验的专家一本操作手册。

## 代码 / 实现:停止判断器与及时止损率(纯 Python)

把"多轮停止判断"与论文的 AbsRec 指标落成可运行演示:

```python
# —— 停止判断器:基于环境证据决定继续/停止 ——
def should_stop(search_history: list) -> tuple:
    """连续 2 轮无结果 + 只换同义词 → 停止并解释;否则继续"""
    last_two = search_history[-2:]
    if len(last_two) == 2:
        no_result = all(h["found"] is False for h in last_two)
        samey = last_two[0]["query"] != last_two[1]["query"]  # 换了词(简化)
        if no_result and samey:
            return True, "环境中找不到匹配商品,停止搜索并解释"
    return False, "继续搜索"

# —— 模拟:粉色枕头(有/无停止规则)——
def run_agent(stop_rule: bool, max_rounds=10):
    queries = ["pink living room pillow under $30", "light pink pillow",
               "pink cushion", "pink throw pillow", "blush pillow"]
    history = []
    for i in range(max_rounds):
        q = queries[i % len(queries)]
        history.append({"query": q, "found": False})
        if stop_rule and should_stop(history)[0]:
            return i + 1, should_stop(history)[1]
    return max_rounds, "搜满上限仍未停止"

# —— AbsRec@1:第一次有机会停止时就正确停止的比例 ——
def abs_rec_at_1(episodes: list) -> float:
    """episodes: (理想停止轮次, 实际停止轮次);实际==理想计为及时止损"""
    timely = sum(1 for ideal, actual in episodes if actual == ideal)
    return timely / len(episodes)

print("无停止规则:", run_agent(stop_rule=False))
print("有停止规则:", run_agent(stop_rule=True))
episodes = [(2, 2), (2, 10), (3, 3), (3, 7)]
print(f"AbsRec@1 = {abs_rec_at_1(episodes):.0%}  (2/4,一半的任务在第一次机会时正确停止)")
```

## 实践 / 应用:反直觉结论与三点行业启示

### 数据里的反直觉结论

1. **Agent 不是不会弃权,而是弃权太晚**:AbsRec@1 普遍低、AbsRec@10 明显高——通常要多浪费好几轮工具调用才意识到任务不可行(真实产品里 = 用户等更久、token 更多、体验更差);
2. **模型越大,不一定越会停**(Scaling Law 在 Agentic Abstention 上失效):Qwen3 8B→235B,整体弃权率(AbsRec@10)提升,但**及时止损率几乎没有变化**——更大的模型更"执着",更相信"我再搜一次就能找到",过度自信让它更难及时止损;
3. **推理与 scaffold 是双刃剑**:更多推理在 Web 任务提升及时止损,但整体弃权率下降(更谨慎但该停时不停);过度推理带来过度弃权(Qwen3-235B 在 Web 可解任务上错误弃权率 34%);**Codex CLI 作为 scaffold 比 Terminus 2 强一倍**——同样的模型放在不同工具环境里,判断力完全不同。

!!! warning "行业提醒"
    **模型能力的提升,不等于判断力的提升。** "模型越大越可靠"在"什么时候停"这个问题上可能适得其反——Agentic Abstention 不是单纯靠换大模型或加推理就能解决,需要系统性的方法设计。

### 对行业的三点直接启示

1. **客服和导购 Agent 不能只教"推荐",也要教"拒绝"**:只会推荐的 Agent,遇到无法满足的需求要么给错误推荐、要么无限循环;真正有用的 Agent 应能识别"需求无法被满足",及时给出解释和替代方案(呼应站内 [Agent 如何理解业务](agent-business-understanding.md) 的"四类出口:执行/追问/拒识/确认");
2. **搜索和研究 Agent 需要"搜索边际收益递减"的停止机制**:多搜几轮作为卖点,但不知道何时停止只是增加等待与 token;应判断"当前检索结果是否足够?继续检索还有新信息吗?";
3. **RPA 和代码 Agent 的 scaffold 设计要和模型能力匹配**:scaffold 让模型容易陷入无意义循环时,再大的模型也救不回来——**把"停止"作为工具设计的一等公民**(呼应 [生产级 Agent 架构](agent-production-architecture.md) 的 maxTurns/熔断与 [企业工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md) 的停止条件)。

### CONVOLVE 为什么有效:补"经验"而非"参数"

停止规则是**隐性经验**(资深的客服知道什么时候说"抱歉没有",资深工程师知道什么时候说"这个环境跑不了")——很难通过预训练获得,因为它高度依赖具体环境和任务类型。CONVOLVE 把这些经验显式写成规则注入上下文,对企业意味着:**不需要大规模标注、不需要昂贵微调、规则可解释可审计可更新、小模型总结规则大模型执行规则**(合规性/成本/可控性三重优势)。

## 总结

- **核心概念**:Agentic Abstention = 多轮决策的止损判断力("知道何时继续只是浪费")——从"答或不答"升级为"继续/回答/放弃"的三选;
- **三类弃权**:Request-based(请求矛盾)/ Environment-based(环境缺资源)/ QA(检索后仍无法回答);
- **实证**:13 个系统 28,000 任务,及时止损率全行业偏低(WebShop 26.7%,终端 21.6%);
- **CONVOLVE**:Reflection + Curation 两阶段,失败轨迹蒸馏成停止规则注入上下文;8B 提炼规则给 70B 用,26.7%→55.3%(接近 57.4% 上限)——**停止规则比模型规模更重要**;
- **一句话**:Agent 的下一个竞争点不是"多能做",而是"**多懂停**";及时止损率目前仍是全行业的短板,用失败轨迹蒸馏规则注入上下文,是一条低成本、可迁移的改进路径。

## 延伸阅读

- 论文:arXiv:2606.28733(Luo, Wen & Wang, 2026);项目:https://lhannnn.github.io/agentic-abstention;代码:https://github.com/lhannnn/agentic-abstention;原文:https://mp.weixin.qq.com/s/OGe4us1YKh8XeikZ2g6RJw
- 站内:[Agent 如何理解业务](agent-business-understanding.md)(拒识/追问出口)、[Agent 规划与工作流模式](agent-planning-patterns.md)(停止条件与收敛)、[生产级 Agent 架构](agent-production-architecture.md)(maxTurns/熔断)、[企业 Agent 工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md)(停止条件/人工接管)、[Graph Engineering 14 步](../07-agent-coding/experience/graph-engineering-14-steps.md)(loop-until-dry 收敛)、[Agent 性能剖析](agent-performance-analysis.md)(失败重试的统计口径)
