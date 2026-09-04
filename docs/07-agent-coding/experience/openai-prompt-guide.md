# OpenAI 官方 Prompt 指南(GPT-5.6):给 Coding Agent 的 System Prompt 做减法

> **一句话摘要**:模型越来越强,Prompt 却越写越长——旧模型留下的补丁、重复规则、层层叠叠的工具说明,不仅烧 Token 还可能互相冲突。OpenAI 官方指南(面向 GPT-5.6,作者 Eric Provencher,Codex DX)给出五个核心判断:先做减法、结果优先、明确权限边界、控制推理成本、生成后必须验证。内部 Coding Agent 实验中,精简 System Prompt 让评分提高约 10%~15%,Token 减少 41%~66%,成本降低 33%~67%。
>
> **来源**:Datawhale 翻译整理(作者 Eric Provencher,OpenAI),https://mp.weixin.qq.com/s/lSvGH3nCK9oWf8wOyeCTGA;官方指南全文:https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6;原始资料存档于 `docs/inbox/openai-prompt-guide-source.md`

## 概念:为什么长 Prompt 是负债

很多 System Prompt 都是在长期迭代中**逐渐变长**的:模型漏过一个步骤,就加一条 `MUST`;工具调用出过一次问题,就补一条 `NEVER`;模型更新后,为旧版本写的规则往往还继续保留。时间一长,重复、过时甚至互相矛盾的指令越来越多——**每一条都持续消耗 Token,还可能让新模型发挥不出来**。

!!! tip "核心判断"
    **Prompt 做减法,删的是无效信息,不是必要要求。**
    需要删除:已经不再影响模型行为、却仍在消耗上下文的内容;需要保留:任务目标、成功标准、权限边界、证据要求、交付前的验证方式。

## 原理:五个核心原则

### 原则 1:先做减法(Simplify prompts first)

- 不要急着加新规则,先重新检查现有 Prompt;
- 从**一套已经能正常工作的 Prompt 和工具集**开始,每次只删除一组重复指令、无效示例或无关工具;
- 用**同一批评测**检查结果——既能控制改动范围,也能判断具体是哪项修改影响了模型表现。

### 原则 2:结果优先 + 提前写清停止条件(Outcome-first)

- **别规定模型的每一步**:过去常写"先搜索→再读文件→接着调工具→按固定顺序输出";现在应写清**最终目标、可用证据、行动边界、验收标准**,让模型根据任务情况自选执行路径;
- **ALWAYS / NEVER / MUST 仍然有用**:安全限制、必填字段、禁止执行的操作必须明确;但"是否继续搜索、何时调用工具、信息不足是否追问"更适合给**判断标准**,而不是固定成一套流程;
- **停止条件提前写清**:证据已足够 → 进入交付;仍缺关键事实 → 说明缺什么,并选择成本较低的方式补充。这能减少重复搜索和无效 Token 消耗。

### 原则 3:做事之前先明确授权范围(权限边界)

!!! warning "能判断下一步该做什么,不代表已经获得执行这一步的权限"

| 用户请求类型 | 模型可以做什么 |
| --- | --- |
| 分析 / 审查 / 制定计划 | 检查材料并报告结论(只读) |
| 修改 / 构建 / 修复 | 执行范围内的本地变更 + 非破坏性验证 |
| 外部写入 / 删除 / 购买 / 明显扩大范围 | **再次确认** |

- **工具按任务需要提供**:工具描述说明用途、适用时机、关键返回字段、失败后的处理方式;工具过多或说明不清都会增加选择负担;
- **检索设范围与停止条件**:普通问答先一次宽搜,拿到核心证据直接回答;只有缺关键事实/日期/来源/引用时才做针对性补充检索;**没搜到某项信息,不应直接推断它不存在**;来源冲突要如实说明。

### 原则 4:长任务状态更新与推理成本控制

- 只在**重要阶段发生变化**时更新进度,不必逐次说明常规工具调用;
- **上下文压缩放在关键里程碑之后**;之前保存的推理,只在目标、假设和优先级**仍然有效**时才继续使用;
- **Reasoning Effort 不是越高越好**:保留当前设置作基线,测试同档与低档,只有评测证明 `high`/`xhigh` 带来收益才承担更高成本;`max` 只给难度最高、质量优先的任务;
- **提高推理强度前先检查 Prompt**:成功标准、依赖关系、工具使用条件、验证要求是否写清——信息不明确时,单纯提高 Reasoning Effort 未必解决问题。

### 原则 5:生成结果之后必须验证

!!! warning "模型生成了结果,不代表任务已经完成"

- 代码修改完成后:跑测试、类型检查、Lint、构建检查或最小冒烟测试;
- 前端/视觉任务:查看实际渲染结果,检查布局、裁切、间距、内容完整性;
- 环境无法完成验证时:说明原因,并给出下一步检查方法——**不能直接把结果表述为"已完成"**。

## 代码 / 实现:授权决策 + 验证驱动的完成判断

把"权限边界"和"验证才算完成"两条原则落成可运行的决策逻辑(纯 Python):

```python
# —— 原则 3:授权级别判定 ——
READ_ONLY_VERBS = {"analyze", "review", "plan", "check", "summarize"}
LOCAL_CHANGE_VERBS = {"modify", "build", "fix", "refactor", "implement"}
EXTERNAL_VERBS = {"delete", "purchase", "send", "publish", "write_to_prod"}

def authorization_level(user_request: str) -> str:
    verb = user_request.split()[0].lower().rstrip("s,.!")
    if verb in READ_ONLY_VERBS:
        return "read_only"        # 只读:检查材料并报告结论
    if verb in LOCAL_CHANGE_VERBS:
        return "local_change"     # 本地变更 + 非破坏性验证
    if verb in EXTERNAL_VERBS:
        return "needs_confirmation"  # 外部写入/删除/购买:必须再次确认
    return "unknown"              # 拿不准 → 按最保守处理,先确认

for req in ["analyze the sales report", "modify the order service",
            "delete the staging data", "fix the login bug"]:
    print(f"  {req!r:38} → {authorization_level(req)}")

# —— 原则 5:验证才算完成 ——
def report_done(task: str, verify: callable, environment_ready: bool) -> str:
    if not environment_ready:
        return f"未完成:{task} 无法在当前环境验证,需人工在本地跑验证"
    ok = verify()
    return f"完成:{task}(验证通过)" if ok else f"未完成:{task}(验证失败,已修复后重试)"

# 演练:代码修改任务,验证 = 冒烟测试
def smoke_test() -> bool:
    return True  # 演示:测试通过

print(report_done("修改订单状态流转", smoke_test, environment_ready=True))
```

## 扩展:2026 版官方指南的新变化(与旧版相比)

> 官方指南已更新(面向 Responses API 与 gpt-5.6 系列,developers.openai.com/api/docs/guides/prompt-engineering)。与本文整理的 Datawhale 旧版相比,以下新变化值得注意:

1. **Responses API 的响应结构**:`output` 数组可能包含 **tool calls / reasoning tokens**,不要假设 `output[0]` 就是最终文本——解析时按类型过滤;
2. **角色优先级**:`developer / user / assistant` 按 model spec 的 chain of command 分级(developer 消息优先级最高);developer 消息推荐结构:`Identity → Instructions → Examples → Context`;
3. **Prompt 版本化进代码**:可复用 **prompt objects** 将于 2026-06-03 起降级、`v1/prompts` 2026-11-30 关停——Prompt 不再只存在于聊天框/文件里,而要用 **typed args、fixtures、tests、feature flags** 像代码一样管理发布;
4. **GPT-5 系列 vs reasoning 模型的 prompting 差异**:类比"senior coworker vs junior coworker"——更强模型给目标与边界,较弱模型给详细步骤;
5. **agentic 任务三实践**:①计划到完全解决(plan 明确终点)②工具调用前给 preamble(说明意图/上下文)③用 TODO 工具 + rubric 追踪进度;
6. **前端工程推荐栈**:Tailwind / shadcn / Radix + Lucide + Motion;**提示词缓存优化**:稳定内容放开头(前缀),易变内容放尾部。

## 实践 / 应用:Prompt 结构模板与迁移工作流

### 官方推荐的 8 段式 Prompt 结构

`Role` → `Personality` → `Goal` → `Success criteria` → `Constraints` → `Tools` → `Output` → `Stop rules`

!!! note "模板不是越长越好"
    这套结构不是要求每项都写很长,而是帮你**确认 Prompt 中的每条信息是否真的会影响模型行为**——只有确实影响行为的信息,才有必要写进 Prompt。

### Prompt 迁移工作流(时间有限就看这三步)

1. **Simplify prompts first**:从正常工作的 Prompt+工具集出发,每次删一组重复指令/无效示例/无关工具,同一批评测验证;
2. **Outcome-first prompts and stopping conditions**:把过程指令改成"目标+证据+边界+验收标准",提前写清停止条件;
3. **迁移后再过一遍验证原则**:生成结果 ≠ 完成,代码要跑测试,环境受限要说明。

### 与站内文章的呼应

- [给 Coding Agent 立规矩的正确姿势](agent-rules-agents-md.md):规则文件(AGENTS.md/CLAUDE.md)的"规则不是越多越好"与本指南的"Prompt 做减法"是同一原理在文件与提示词两个层面的体现;
- [Loop Engineering](loop-engineering.md):停止条件/验证步骤编码进 SKILL 与原则 2、5 一致;
- [Prompt 工程](../../03-agents/prompt-engineering.md):基础技巧(指令清晰、few-shot、CoT);本篇是面向 Coding Agent 的**系统提示词治理**进阶;
- [企业 Agent 工程化(四):四件套](../../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md):"工具说明像接口契约"与原则 3 的工具描述要求一致。

## 总结

- **五条核心判断**:①先做减法(删无效信息,不删必要要求);②结果优先 + 停止条件写清;③授权边界(能判断下一步 ≠ 有权限执行);④控制推理成本(Reasoning Effort 按评测定档);⑤生成后必须验证;
- **量化收益**:精简 System Prompt 后评分 +10%~15%、Token -41%~66%、成本 -33%~67%(OpenAI 内部 Coding Agent 实验);
- **模板**:Role / Personality / Goal / Success criteria / Constraints / Tools / Output / Stop rules——只保留真正影响行为的信息。

## 延伸阅读

- 官方指南全文:https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6;Datawhale 翻译:https://mp.weixin.qq.com/s/lSvGH3nCK9oWf8wOyeCTGA
- 作者 Eric Provencher 过往项目:RepoPrompt(代码库上下文与 Prompt 设计)
- 站内:[给 Coding Agent 立规矩](agent-rules-agents-md.md)、[Prompt 工程](../../03-agents/prompt-engineering.md)、[Loop Engineering](loop-engineering.md)、[企业 Agent 工程化(四)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md)
