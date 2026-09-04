# Skill 测评:五大维度与测试闭环

> **一句话摘要**:Skill 的核心事故不是"不会执行",而是"**乱触发或抢任务**"——所以测评必须从多维度进行。本文给出 Skill 有效性测评的完整框架:两大核心(测触发 / 测执行)、**五大维度**(触发准确性、独立执行、共存冲突、指令遵循、输出质量)各自的测试方法与成功标准,以及"基线 → 线上监控 → 回流优化"的测试闭环——形成大模型工程化的完整测试闭环。
>
> **来源**:用户提供(视频《如何证明 Skill 的有效性》);原始资料存档于 `docs/inbox/skill-evaluation-source.md`

## 概念:Skill 测评的两个核心

!!! tip "核心判断"
    **Skill 最容易出的事故不是执行不了,而是乱触发或抢任务。** 所以测评先分两路:测触发(会不会被正确触发)+ 测执行(触发了能不能按正确流程做完)。两者都通过,Skill 才真正"有效"。

## 原理:五大维度详解

| 维度 | 测什么 | 测试方法 | 成功标准 |
| --- | --- | --- | --- |
| **① 触发准确性** | 触发行为是否符合预期 | 提供**至少三类输入**(正常/边界/错误),观察触发 | 无漏触发或误触发 |
| **② 独立执行** | 无干扰下能否独立完成任务 | 单独运行该 Skill,给完整任务 | 流程正确,能独立产出结果 |
| **③ 共存冲突** | 多 Skill 共存是否抢任务/冲突 | **模拟多个 Skill 同时存在**的场景 | 各 Skill 协同工作,无任务冲突 |
| **④ 指令遵循** | 是否严格遵循用户指令 | 验证参数传递、执行顺序 | 完全遵循,无自主行为 |
| **⑤ 输出质量** | 最终结果是否正确完整 | 检查输出内容 | 正确、无信息缺失 |

!!! warning "维度 ③ 最容易被忽略,也最致命**
    单个 Skill 测得好,不代表多个 Skill 放一起没问题——**触发条件重叠的 Skill 会抢任务**(呼应 [Agent 规划模式](../../03-agents/agent-planning-patterns.md) 的"工具三失控"与 [企业工程化(一)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-boundaries-tools.md) 的工具治理)。共存测试必须在"多个 Skill 同时可用"的环境下做。

## 代码 / 实现:触发测试 + 共存冲突检测(纯 Python)

```python
# —— 1) 触发测试:正常/边界/错误三类输入,判定触发是否符合预期 ——
# cases: {case名: (输入文本, 期望是否触发)}
def trigger_test(skill: callable, cases: dict) -> dict:
    result = {}
    for case, (text, expected) in cases.items():
        actual = bool(skill(text))
        result[case] = "通过" if actual == expected else "失败(误触发或漏触发)"
    return result

# 模拟一个触发条件过宽的 Skill:含"写"就触发 → 会把无关任务抢走
skill_a = lambda t: ("总结" in t) or ("分析" in t) or ("写" in t)
CASES = {
    "正常输入": ("帮我总结这份文档", True),
    "边界输入": ("只需要做个简要分析", True),
    "错误输入": ("帮我写个周报模板", False),   # 无关任务,不应触发
}
print("Skill A 触发测试:")
for case, verdict in trigger_test(skill_a, CASES).items():
    print(f"  [{case}] → {verdict}")
assert trigger_test(skill_a, CASES)["错误输入"] == "失败(误触发或漏触发)"

# —— 2) 共存冲突检测:多个 Skill 对同一输入是否都触发(抢任务)——
def co_existence_conflict(skills: dict, input_text: str) -> list:
    fired = [name for name, trig in skills.items() if trig(input_text)]
    return fired if len(fired) > 1 else []

skill_b = lambda t: "报告" in t or "周报" in t
print("\n共存冲突检测('帮我写一份周报总结'):")
conflict = co_existence_conflict({"SkillA": skill_a, "SkillB": skill_b}, "帮我写一份周报总结")
print(f"  同时触发的 Skill: {conflict or '无'}")
assert len(conflict) == 2, "两个 Skill 抢任务,应被检测到"

# —— 3) 测试闭环:基线 → 监控 → 回流 ——
def close_loop(baseline_trigger, live_trigger, conflict_rate):
    issues = []
    if live_trigger < baseline_trigger - 0.05:
        issues.append("触发准确率下降 → 迭代触发条件,重新测试")
    if conflict_rate > 0.05:
        issues.append("冲突率升高 → 收窄触发边界/拆分 Skill")
    return issues or ["监控正常:继续运行"]
print("\n闭环检查:", close_loop(0.95, 0.88, 0.08))
print("代码验证通过 ✔")
```

## 实践 / 应用:测试闭环与知识库整合

### 测试闭环三阶段(不是一次性测试)

```
① 建立基线:上线前跑五维度测试,记录触发准确率/执行成功率/冲突发生率的初始基线
② 线上监控:持续采集触发准确率、执行成功率、冲突发生率等关键指标
③ 回流优化:触发准确率下降/冲突增多 → 迭代 Skill(收窄触发、拆分、改流程)→ 重新测试 → 更新基线
```

!!! note "与站内其他文章的呼应**
    - [Eval Engineering Skill](eval-engineering-skill.md):"读仓库+分析 traces+设计评估测试" = 本框架的**工具与方法**(怎么设计评估),本文是**维度与标准**(测什么、算通过);
    - [评估驱动开发](../../03-agents/agent-eval-driven-dev.md):"生产 traces → 评估测试 → 改进"闭环与本文"监控 → 回流 → 重测"同一思想;
    - [Agent Skill 版本管理](skill-version-management.md):五维度测试结果就是 Skill 版本上线的"评测关卡"数据(语义化版本发布依据);
    - [自进化 Agent 综述](../../09-agent-research/self-evolving-agents-survey.md):"Skill 质量评估缺位是第一类工作最大痛点"——本文给出可落地的五维评估标准。

### 落地建议

1. **每个 Skill 上线前**跑五维测试并记录基线(触发三类输入 / 独立执行 / 与相邻 Skill 共存 / 指令遵循 / 输出);
2. **触发条件写窄**:触发测试失败(误触发)最常见原因是 description/trigger 写太宽——参照 [Skill 版本管理](skill-version-management.md) 的"修改触发边界=不兼容改动,升主版本";
3. **共存测试常态化**:每新增一个 Skill,与存量 Skill 做一次触发重叠检查(抢任务是最隐蔽的线上事故);
4. **线上监控回流**:触发准确率/冲突率进入监控,异常即回流迭代——形成闭环。

## 扩展:OpenAI 官方 Skill 评测方法(Testing Agent Skills with Evals)

> OpenAI 开发者博客给出了可复刻的 Skill 评测流程(https://developers.openai.com/blog/eval-skills),与上文"五维框架"互补:上文是**维度与标准**(测什么、算通过),这里是**工具与方法**(用 evals + codex 怎么测)。

**核心公式**:`eval = prompt → 捕获 run(trace + artifacts)→ 少量检查 → 可比分数`——用"证明"而非"感觉"。

1. **先定义成功**:四类检查——**outcome**(结果对不对)、**process**(过程是否合规,如是否跑过测试)、**style**(风格约定)、**efficiency**(token/工具调用预算);keep small,每类几条即可;
2. **10–20 个 prompt 就够起步**(与多智能体研究的"20 条开测"一致);CSV 含 **should_trigger 正反例**:显式/隐式/上下文触发 + **负控制**(不该触发时绝不触发,防误触发);
3. **codex exec --json** 输出 JSONL 事件流,对 `command_execution` 事件写**确定性检查**(如"是否跑过 npm install""是否生成 package.json");
4. 规则覆盖不了的风格/约定,用 **--output-schema + rubric 二次评分**(结构化 JSON,可进 CI);
5. **扩展方向**:token 预算、build check、runtime smoke、git status 清洁度、最小权限回归。

```bash
# 确定性检查:验证 run 里确实执行过关键命令
codex exec --json --prompt "..." | jq 'select(.type=="command_execution") | .command'
# 输出 schema + rubric:风格类检查进 CI
codex exec --json --output-schema '{"type":"object","properties":{"score":{"type":"number"}}}' ...
```

**落地**:skill 上线前先用 10-20 个含正反例的 prompt 跑一轮(触发 + 执行),再用 rubric 评风格;与 [Skill 版本管理](skill-version-management.md) 结合——评测结果作为版本发布关卡。

## 总结

- **两大核心**:测触发(不误触发不漏触发)+ 测执行(流程正确);
- **五大维度**:触发准确性 / 独立执行 / 共存冲突 / 指令遵循 / 输出质量——各自有测试方法与成功标准;
- **三类触发输入**:正常 / 边界 / 错误(必测);
- **测试闭环**:基线 → 线上监控(触发准确率/执行成功率/冲突发生率)→ 回流优化 → 重测;
- **一句话**:Skill 有效的证明 = 触发准、执行对、共存不冲突、指令不走样、输出不缺失,并且**上线后持续被监控回流**——而不是"跑通一次就完事"。

## 延伸阅读

- 原始素材:用户提供(视频《如何证明 Skill 的有效性》),存档于 `docs/inbox/skill-evaluation-source.md`
- 站内:[Eval Engineering Skill](eval-engineering-skill.md)、[Agent Skill 版本管理](skill-version-management.md)、[评估驱动开发](../../03-agents/agent-eval-driven-dev.md)、[Agent 评测](../../03-agents/agent-evaluation.md)、[自进化 Agent 综述](../../09-agent-research/self-evolving-agents-survey.md)
