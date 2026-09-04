# AI 时代的代码审查:Agentic Code Review

> **一句话摘要**:AI 让开发者的原始代码产出翻了 4 倍,但真实交付价值仅增长 12%——巨大差额全耗在跟不上节奏的代码审查上。**工程的难点已从"写代码"转变为"决定是否信任代码"**。新范式:人从"逐行阅读"的内环退出,成为**信号决策者**——通过分层审查(按风险三变量定档)、异质性 AI 传感器阵列交叉验证、Agent 提交契约,把人的精力聚焦到真正需要判断力的高价值决策。
>
> **来源**:用户提供(方法论文案,引用谷歌技术总监观点);原始资料存档于 `docs/inbox/agentic-code-review-source.md`

## 概念:产出与价值的鸿沟

!!! tip "核心判断"
    原始代码产出 ×4,交付价值仅 +12%——瓶颈不在写代码,在**审查**。AI 让"写"变便宜,让"信任"变稀缺:**决定是否信任代码**,成了新的工程难点。

## 原理:四个新范式

### 范式一:分层审查策略(不再一刀切)

按**三个变量**评估每次变更的风险,再决定审查深度:

| 变量 | 问什么 |
| --- | --- |
| **爆炸半径** | 代码崩溃的影响范围有多大? |
| **代码寿命** | 短期原型还是长期核心模块? |
| **受众广度** | 有多少人需要理解和维护? |

| 风险等级 | 审查策略 |
| --- | --- |
| **低风险**(如 UI 微调) | Linter 检查 + 人工快速浏览 |
| **中风险**(常规业务逻辑) | 测试 + AI 审查 + 人工确认 |
| **高风险**(支付/鉴权系统) | 全流程审查:类型检查、测试、**多 AI 交叉审**、系统 Owner 及安全审计 |

!!! note "分层不是偷懒**
    低风险跳过深度审查不是为了省事,而是**把人类审查预算集中到高风险变更**上——同一批人,花在"UI 微调"上的时间越少,能花在"支付系统"上的就越多。

### 范式二:异质性 AI 传感器阵列(交叉验证)

!!! tip "为什么单靠一个 AI 不行**
    实验表明:不同"性格"的 AI 审查工具发现的问题,**重叠率极低**——一个 AI 只擅长抓它训练分布里的问题模式。单一工具 = 单一传感器,盲区固定。

**正确做法**:部署一组**功能各异**的 AI 审查工具(正确性审查 / 安全审查 / 性能审查 / 风格审查……)作为传感器阵列交叉验证。**人的角色不再是传感器,而是站在阵列后面,综合分析信号并做出最终决策**(呼应站内 [生产级架构](../../03-agents/agent-production-architecture.md) 的"多视角验证"与 [Graph Engineering](graph-engineering-14-steps.md) 的"验证器三模式")。

### 范式三:Agent 提交规则(入口契约)

AI 生成的代码难以审查,因为推理过程是"黑箱"——审者要从零"考古"。解法:**为 Agent 提交设立入口契约,把理解成本推回给提交者**:

| 规则 | 内容 | 目的 |
| --- | --- | --- |
| **📝 提交决策日志(Decision Log)** | Agent 附推理过程:为什么这么改、排除了哪些方案 | 避免 Reviewer 从零考古,审查从"读代码"变成"校验决策" |
| **✂️ 强制小 PR** | PR 大小作为硬性设计约束(大 PR 要么被拒要么被草率通过) | 保证审查有效性 |
| **✅ 提交必须附证据** | 变更目的、测试输出等证明,否则不配进审查流程 | 让"完成"可验证(呼应 [OpenAI Prompt 指南](openai-prompt-guide.md) 的"验证才算完成") |

!!! warning "小 PR 是硬约束,不是建议**
    "大 PR 要么被拒绝,要么被草率通过"——后者是隐性灾难。把 PR 大小当设计约束写进规则,比事后劝人拆 PR 有效得多。

### 范式四:人类的新角色(四大关键任务)

当 AI 承担大部分审查后,人的精力聚焦四个决策点:

1. **判断 PR 是否值得审**:识别 Agent 容易放弃的任务类型,不在注定失败的 PR 上浪费时间(呼应 [Agentic Abstention](../../03-agents/agentic-abstention.md) 的"该停就停");
2. **重点审查测试改动**:**警惕 Agent 为了通过测试而"修复"测试**——这是它最隐蔽的失败模式(呼应 [Spec-First 决策栈](spec-first-decision-stack.md) 的"伪造测试"与 [得物五道关口](../../04-practice/ai-native-order-system-spec-driven.md) 的"物理剥夺完成权");
3. **高风险 PR 深度审查**:核心系统改动亲自深入代码逻辑,不依赖 AI;
4. **承担最终责任**:**谁按 Merge,谁负责**——AI 只是辅助,最终决策权与责任在人。

## 代码 / 实现:分层审查决策 + 提交门禁(纯 Python)

```python
# —— 1) 分层审查决策器:按三变量定档 ——
def review_tier(blast_radius: int, long_lived: bool, audience: int) -> str:
    """爆炸半径/寿命/受众 → 审查档位"""
    risk = 0
    risk += 2 if blast_radius >= 3 else 1 if blast_radius == 2 else 0   # 影响范围
    risk += 1 if long_lived else 0                                       # 长期核心
    risk += 1 if audience >= 5 else 0                                    # 多人维护
    if risk >= 3: return "高:全流程(类型+测试+多AI交叉+Owner+安全审计)"
    if risk >= 2: return "中:测试 + AI 审查 + 人工确认"
    return "低:Linter + 人工快速浏览"

cases = [
    ("UI 微调",       1, False, 2),
    ("常规业务",      2, True,  4),
    ("支付/鉴权",     5, True,  8),
]
for name, br, ll, au in cases:
    print(f"  {name:8} → {review_tier(br, ll, au)}")
assert review_tier(1, False, 2).startswith("低")
assert review_tier(2, True, 4).startswith("中")
assert review_tier(5, True, 8).startswith("高")

# —— 2) Agent 提交门禁(入口契约三件套)——
def submit_gate(has_decision_log: bool, pr_size_lines: int, has_evidence: bool) -> str:
    if not has_decision_log:
        return "拒绝:缺少提交决策日志(为什么改/排除了哪些方案)"
    if pr_size_lines > 400:
        return "拒绝:PR 过大(>400 行),先拆分再提交(小 PR 是硬约束)"
    if not has_evidence:
        return "拒绝:缺少证据(变更目的/测试输出),不配进入审查"
    return "通过:进入审查流程"

print(submit_gate(True, 150, True))
print(submit_gate(True, 600, True))
assert submit_gate(False, 100, True).startswith("拒绝")
assert submit_gate(True, 600, True).startswith("拒绝")
assert submit_gate(True, 150, False).startswith("拒绝")
assert submit_gate(True, 150, True).startswith("通过")
print("代码验证通过 ✔")
```

## 实践 / 应用:落地建议与知识库整合

### 落地四步

1. **定审查矩阵**:把三个变量 × 三档策略写进团队规则(如 AGENTS.md),每个 PR 自动判定档位;
2. **搭 AI 传感器阵列**:部署 3-5 个不同"性格"的审查 agent(正确性/安全/性能/风格),输出结构化信号汇总;
3. **立提交契约**:决策日志 + 小 PR + 证据三件套做成门禁(CI 检查 PR 大小/日志/证据,不满足自动拒);
4. **人只做四件事**:判断值不值得审、盯测试改动、高风险深审、按 Merge 担责。

### 与站内其他文章的呼应

- [Superpowers v6](../skills/mattpocock-skills.md):双审查合并 + 多视角评审 = 传感器阵列的实践(官方);
- [得物五道关口](../../04-practice/ai-native-order-system-spec-driven.md):门禁卡控 + 物理剥夺"宣称完成" = 提交契约的实现;
- [AI Coding Harness 设计经验](ai-coding-harness-design.md):"让 AI 看见问题四层" = 审查的可观测基础;
- [Gate 模式](gate-pattern.md):"高风险 PR 深审"是 gate 在审查环节的落点;
- [Agentic Abstention](../../03-agents/agentic-abstention.md):判断 PR 值不值得审 = 停止判断力的审查版。

## 总结

- **问题本质**:产出 ×4 vs 价值 +12%,瓶颈在审查;"写代码" → "决定是否信任代码";
- **四个新范式**:分层审查(三变量定档)/ 异质 AI 传感器阵列交叉验证 / Agent 提交契约(决策日志·小 PR·证据)/ 人类四大任务;
- **人的新角色**:信号决策者——综合 AI 信号做最终判断,不在机械阅读上消耗;
- **一条铁律**:**谁按 Merge,谁负责**——AI 辅助,人担责;
- **一句话**:AI 时代代码审查 = **人主导、AI 辅助的决策系统**——把人的精力从逐行阅读解放到真正需要判断力的高价值决策。

## 延伸阅读

- 原始素材:用户提供的方法论文案,存档于 `docs/inbox/agentic-code-review-source.md`
- 站内:[Superpowers v6](../skills/mattpocock-skills.md)、[得物五道关口](../../04-practice/ai-native-order-system-spec-driven.md)、[AI Coding Harness 设计经验](ai-coding-harness-design.md)、[Gate 模式](gate-pattern.md)、[Agentic Abstention](../../03-agents/agentic-abstention.md)、[Spec-First 决策栈](spec-first-decision-stack.md)
