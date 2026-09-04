# Claude Code 官方最佳实践:验证闭环、四阶段工作流与规模化

> **一句话摘要**:Anthropic 官方《Best practices for Claude Code》全貌——一切受"上下文窗口是最重要资源"约束;给 Claude 可运行的验证检查(四档门控)、Explore→Plan→Implement→Commit 四阶段工作流、提供具体上下文四策略、自动化与规模化(claude -p / Writer-Reviewer / fan-out / auto mode / 对抗性审查)、五大失败模式。上下文与验证的详细展开见 [上下文工程官方一手资料](../../03-agents/context-engineering-official-sources.md),本文聚焦其余增量并保留全貌索引。
>
> **来源**:Anthropic《Best practices for Claude Code》(https://anthropic.com/engineering/claude-code-best-practices;官方文档,持续更新)

## 概念

### 一切最佳实践源于一个约束:上下文窗口

Claude Code 是 agentic 编码环境——读文件、跑命令、改代码、自主解决问题。与聊天机器人不同,它工作的约束是:**上下文窗口很快被填满,模型性能随填充退化**(窗口快满时"忘记"早期指令、犯更多错)。**上下文窗口是最重要的资源**。这也是 [上下文工程官方一手资料](../../03-agents/context-engineering-official-sources.md) 里"注意力预算/context rot"的实操版。

### 使用方式的变化

不是"人写代码、Claude 审查",而是"人描述想要什么、Claude 探索-计划-实现"。自治有学习曲线,本指南是 Anthropic 内部团队与各代码库工程师验证过的模式。

## 原理(核心模式)

### 1. 给 Claude 可验证的检查(验证闭环)

Claude 会在"看起来完成"时停止;没有可运行的检查,"看起来完成"是唯一信号,你就成了验证循环。**给 Claude 一个能跑出 pass/fail 的检查**:测试套件、构建退出码、linter、diff 脚本、浏览器截图对比。

| 策略 | 之前(模糊) | 之后(可验证) |
| --- | --- | --- |
| 提供验证标准 | "实现一个校验邮箱的函数" | "写 validateEmail 函数;示例用例 user@example.com 为 true、invalid 为 false、user@.com 为 false;实现后跑测试" |
| 视觉验证 | "让仪表盘更好看" | "[贴截图] 实现这个设计;截图对比原图;列出差异并修复" |
| 治本非治标 | "构建失败了" | "构建报这个错:[贴错误];修复并验证构建通过;治根因,不要压制错误" |

**门控强度四档**(逐级投入换取无人值守):

1. **单条 prompt 内**:让 Claude 跑检查并在同一条消息里迭代;
2. **跨会话**:把检查设为 `/goal` 条件,独立评估器每轮重查,直到满足;
3. **确定性门控**:Stop hook 把检查写成脚本,阻止回合结束直到通过(Claude Code 连续 8 次 block 后覆盖 hook 结束回合);
4. **第二意见**:verification subagent / dynamic workflow 用全新模型尝试证伪结果——**干活的人不给自己打分**。

(详细展开与上下文管理实践见 [上下文工程官方一手资料](../../03-agents/context-engineering-official-sources.md)。)

### 2. 四阶段工作流:Explore → Plan → Implement → Commit

先研究规划、再实施,避免解决错误问题:

1. **Explore**:进入 plan mode(`Shift+Tab` 或 `claude --permission-mode plan`),Claude 只读文件、回答问题、不改动;
2. **Plan**:让 Claude 产出详细实施计划(改哪些文件、会话流如何);`Ctrl+G` 在编辑器直接改计划;
3. **Implement**:批准计划或 `Shift+Tab` 退出 plan mode,让 Claude 按计划编码并验证;
4. **Commit**:让 Claude 用描述性信息提交并开 PR。

**什么时候跳过计划**:范围清晰的小改动(改 typo、加日志行、重命名变量)直接做;**能用一句话描述 diff 就跳过 plan**。计划在有不确定性、跨多文件、不熟悉代码时最有用。

### 3. 提供具体上下文(四策略)

| 策略 | 之前 | 之后 |
| --- | --- | --- |
| **范围任务** | "给 foo.py 加测试" | "写 foo.py 的测试,覆盖用户登出边缘情况,避免 mock" |
| **指向来源** | "为什么 ExecutionFactory API 这么怪?" | "翻 ExecutionFactory 的 git history,总结它的 API 怎么来的" |
| **引用现有模式** | "加个日历组件" | "看首页现有组件怎么实现的,HotDogWidget.php 是好例子,遵循其模式;除代码库已有库外不引新库" |
| **描述症状** | "修登录 bug" | "用户反馈会话超时后登录失败;查 src/auth/ 的 auth 流;修复后登录应能恢复" |

附:**提供丰富内容**(粘贴设计稿、真实报错、数据样本)+ **配置环境**(CLAUDE.md / 权限 / CLI 工具 / MCP / hooks / skills / subagents / plugins)。

### 4. 有效沟通与会话管理

- **Ask codebase questions**:先问代码库问题再动手;
- **Let Claude interview you**:让 Claude 访谈你(需求澄清);
- **Course-correct early and often**:尽早频繁纠偏;
- **Manage context aggressively**:主动管理上下文;
- **Use subagents for investigation**:调查性任务用 subagent,别烧主上下文;
- **Rewind with checkpoints**:用 checkpoint 回退;**Resume conversations**:恢复会话。

## 代码 / 实现(自动化与规模化)

### 非交互模式 claude -p(进 CI/脚本)

```bash
claude -p "Explain what this project does"                    # 纯文本
claude -p "List all API endpoints" --output-format json       # 脚本可解析
claude -p "Analyze this log file" --output-format stream-json --verbose  # 流式 JSON
```

`claude -p` 可进 CI 流水线、pre-commit hooks、自动化工作流;`--no-session-persistence` 不建可恢复会话。

### 多 session 并行 + Writer/Reviewer 模式

并行方式按协调量自选:Worktrees(隔离 git checkout 防编辑冲突)、桌面应用多会话、Claude Code on the web、Agent teams(自动协调+共享任务+消息+team lead)。

**质量向**:全新上下文避免"自评偏置"——Writer/Reviewer 双 session:

| Session A(Writer) | Session B(Reviewer) |
| --- | --- |
| 为 API 端点实现限流器 | 审查 @src/middleware/rateLimiter.ts 的限流实现,找边缘情况/竞态/与现有中间件模式一致性 |
| ← 处理 B 的反馈 | 输出审查反馈 |

同理可让一个 Claude 写测试、另一个写代码去通过它。

### Fan-out 跨文件批量

```bash
# 1. 让 Claude 生成任务清单
claude -p "列出所有需要迁移的 2000 个 Python 文件,保存到 files.txt"
# 2. 循环调用
for file in $(cat files.txt); do
  claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
# 3. 先测 2-3 个文件,再全量跑;--allowedTools 限制无人值守时能做什么
```

也可接进现有管道:`claude -p "<prompt>" --output-format json | your_command`。

### auto mode 自主运行

`claude --permission-mode auto -p "fix all lint errors"`——**分类器模型**在命令执行前审查:阻止 scope 升级、未知基础设施、敌意内容驱动的动作,常规工作免提示。非交互 `-p` 下分类器反复 block 会中止(没有用户可回退)。

### 对抗性审查步骤

长时间无人值守后,独立检查更关键:**reviewer 在全新 subagent 上下文里只看 diff 和给定标准,不看产生变更的推理**,独立评估结果:

```
Use a subagent to review the rate limiter diff against PLAN.md. Check that every
requirement is implemented, the listed edge cases have tests, and nothing outside
the task's scope changed. Report gaps, not style preferences.
```

正确性检查可直接用内置 `/code-review` skill(全新 subagent 审当前 diff 的 bug)。⚠️ **别追每个 finding**:reviewer 被要求找缺口就会报缺口,可能导致过度工程(多余抽象层、防御代码、不可能发生的测试用例)——**只 flag 影响正确性或明确需求的问题,其余视为可选**。长时自主运行可用 agent team 保持循环,人抽查记录。

## 实践 / 应用

### 五大失败模式(尽早识别)

| 失败模式 | 表现 | 修复 |
| --- | --- | --- |
| **Kitchen sink session** | 一个任务中途插入无关请求,上下文充满无关信息 | 无关任务之间 `/clear` |
| **反复纠正** | 纠正两次还错,上下文被失败尝试污染 | 两次失败后 `/clear` 并重写更好的初始 prompt |
| **过度膨胀的 CLAUDE.md** | 太长,重要规则淹没在噪音里被忽略一半 | 无情精简;Claude 已能正确做就删掉或转成 hook |
| **trust-then-verify gap** | 产出看着合理但不处理边缘情况 | 总是提供验证(测试/脚本/截图);不能验证就别交付 |
| **无限探索** | 让 Claude"调查"却不限范围,读几百个文件撑爆上下文 | 窄化调查范围或用 subagent,别让探索消耗主上下文 |

### Develop your intuition(反教条)

模式是起点不是铁律:深钻一个复杂问题时让上下文积累;探索性任务跳过计划;故意模糊的 prompt 可以看 Claude 如何解读。注意什么有效(结构/上下文/模式)、什么挣扎(噪音?prompt 太模糊?任务太大?),形成指南无法捕获的直觉。

## 总结

1. **一切源于上下文约束**:窗口是最重要资源;给 Claude 可运行验证(pass/fail),否则你就是验证循环;门控四档逐级换取无人值守。
2. **四阶段工作流**:Explore(plan mode)→ Plan(Ctrl+G 编辑)→ Implement → Commit;一句话能描述 diff 就跳过计划。
3. **具体上下文四策略**:范围任务、指向来源、引用现有模式、描述症状+修复后长什么样。
4. **规模化**:claude -p 进 CI、Writer/Reviewer 双 session 破自评偏置、fan-out + --allowedTools、auto mode 分类器把关、对抗性审查(只 flag 影响正确性的缺口)。
5. **五失败模式可当 checklist**:kitchen sink/反复纠正/CLAUDE.md 过载/trust-then-verify/infinite exploration,每条都有明确修复动作。

**下一步学什么**:上下文与验证细节见 [上下文工程官方一手资料](../../03-agents/context-engineering-official-sources.md);Claude Code 机制见本子主题其余文章(架构/工具系统/Workflows/Skills/源码);规模化方法论对比 [Vibe Coding 最佳实践](../experience/vibe-coding-engineering-practice.md)。

## 延伸阅读

- 站内:[上下文工程官方一手资料](../../03-agents/context-engineering-official-sources.md)、[Claude Code 架构与工具系统](claude-architecture-tools.md)、[Claude Code Dynamic Workflows](claude-workflows.md)、[Claude Code 隐藏技巧](claude-code-tips.md)、[Vibe Coding 最佳实践](../experience/vibe-coding-engineering-practice.md)、[Agentic Code Review](../experience/agentic-code-review.md)
- 外部:Best practices for Claude Code(https://anthropic.com/engineering/claude-code-best-practices);Claude Code Docs(https://platform.claude.com/docs/en/claude-code/)
