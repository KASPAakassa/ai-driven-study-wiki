# Ralph Wiggum 循环:无限循环 + 全新上下文的"天真坚持"方法论

> **一句话摘要**:`while :; do cat PROMPT.md | claude ; done`——一个无限循环反复把任务喂给 Claude,每次迭代从干净状态开始、通过文件系统继承状态。它是**方法论而非工具**,靠"新鲜上下文 + 文件真相源 + 反馈循环"三个支柱解决 Context Rot;有人用它花 $297 完成了报价 $50,000 的项目。
>
> **来源**:Geoffrey Huntley 提出,https://github.com/geoffrey-huntley/ralph;中文解读整理自 Yu 的赛博工位(https://yudesk.dev/docs/notes)

## 概念

**Ralph Wiggum** 名字来自《辛普森一家》里警察局长的儿子——全剧最"单纯"的人,不太清楚自己在做什么但永远不会停下来。标志性台词 **"I'm helping!"** 意外揭示了这项技术的精髓:**天真且不懈的坚持(Naive and relentless persistence)**。

```bash
while :; do cat PROMPT.md | claude ; done
```

**重要区分:Ralph 是方法论,不是工具。** 就像"敏捷开发"是方法论而不是某个软件,Ralph 描述的是一种工作方式——"无限循环 + 每次全新上下文,让 AI 反复尝试同一个任务,每次迭代都从干净状态开始,通过文件系统看到之前的工作成果"。不同实现效果可能差异巨大。

Anthropic 后来发布了官方插件,发明者 Geoffrey Huntley 却说 **"This isn't it"**——因为他认为官方实现偏离了"每次全新上下文"的核心原则。

## 原理:Context Rot 与三个支柱

### 为什么要 Ralph:Context Rot(上下文腐烂)

用 Claude 处理复杂任务时,对话越长它越"迟钝"——忘记重要信息、重复犯同样的错误、代码质量下降、开始幻觉。**问题不在 AI 不够聪明,而是上下文窗口被污染了**:九次失败的代码、九组错误信息、大量不再相关的讨论塞满上下文。

Geoffrey Huntley 和社区发现的现象 **"Dumb Zone"**:

| 上下文大小 | 表现 |
| --- | --- |
| 0 - 50k tokens | 最佳性能 |
| 50k - 100k tokens | 良好,轻微下降 |
| 100k+ tokens | 明显退化,开始忽略指令 |
| 150k+ tokens | 严重退化 |

经验法则:**上下文用到一半左右就该警惕**。对于 200k tokens 的 Claude,超过 100k 时你可能在和一个"变笨"的 AI 交流。

> **反直觉洞察:累积的上下文不是资产,而是负债。** 对话越长,上下文里充斥的"负面信息"越多(失败代码、过时讨论、被纠正的错误理解),不仅占用空间还分散 AI 的"注意力"。

### 三个支柱

**支柱 1:新 Session** —— 每次循环迭代启动一个**全新的 Claude 实例**,获得完全干净的上下文窗口。不是"清空对话历史",而是彻底关闭当前进程、启动新进程。这就是为什么循环必须在 Claude Code 外部运行——bash 循环需要控制 Claude 进程的生命周期。

**支柱 2:文件作为真相来源** —— 每次都是新上下文,AI 靠文件系统而非对话历史知道之前做了什么:

- **PRD/spec 文件** — 定义目标、功能列表、成功标准;
- **IMPLEMENTATION_PLAN.md** — 任务分解和进度;
- **progress.txt** — 自由格式日志,每次迭代结束追加学到的内容;
- **Git 历史** — 代码修改的证明。

> "规格文档和实施计划才是真相来源,而不是之前的对话。" —— Roman (Mentat)

**支柱 3:反馈循环** —— 仅有干净上下文和持久化状态不够,如果 AI 写了有问题的代码并提交,错误会累积。反馈循环是自动化质量门槛:**TypeScript 类型检查、单元测试、CI/CD**。测试失败 → 代码不提交 → Claude 看到失败信息 → 下一次迭代的新实例尝试修复。

### Human on the Loop(监督式管理)

Geoffrey Huntley 反复强调的概念区别:

| Human in the Loop | Human on the Loop |
| --- | --- |
| 保姆式陪伴 | 监督式管理 |
| AI 每一步都等你确认 | 你设定目标和边界,AI 自主运行 |
| 你是工作流程的瓶颈 | 你偶尔检查进度 |

就像监督一个实习生——你给他任务、边界、检验标准,然后让他去做。实际使用两种模式:**AFK 模式**(下班前启动,回家睡觉,早上检查结果)和 **human-in-the-loop 模式**(每次迭代后暂停检查,适合复杂或不确定任务)。

### 什么任务适合 Ralph

**适合**:有明确成功标准的任务(可自动验证)、需要迭代改进的任务、绿地项目(无需担心破坏现有代码)、有自动测试的项目(测试作为反压机制)。

**不适合**:需要人工判断的设计决策(无法自动验证"好不好看")、一次性操作、生产环境调试(风险太高不适合无人值守)、成功标准不清晰的任务(无法判断何时停止)。

### 三种使用模式

1. **完整实现模式**:从头构建完整功能/项目——准备 spec 和实施计划,让 Ralph 自动执行所有任务。真实案例:价值 $50,000 的外包项目(MVP + 测试 + 代码审查全程自动化)仅 $297 API 成本;React v16 升 v19 跑了 14 小时完全无人干预;
2. **探索模式**:不是产出代码而是理解——prompt 是"阅读代码库生成架构文档"或"找出所有 API 端点",每次迭代深入探索逐步建立完整理解;
3. **暴力测试模式**:知道症状和期望行为但找不到根因——"修复这个 bug,让这个测试稳定通过",Ralph 不断尝试不同修复方案,直到找到有效的。特别适合"我不知道怎么修,但我知道什么时候算修好了"的问题。

## 代码 / 实现:两种实现路线

社区发展出两种工程化程度不同的实现:

| 维度 | 极简(snarktank/ralph,10k+ stars) | 工程化(frankbria/ralph-claude-code) |
| --- | --- | --- |
| 会话模式 | 每次全新 | 默认复用(`--continue`),可切换全新 |
| 监控 | 手动查看 | 内置 tmux 仪表盘 |
| 安全机制 | max_iterations | 断路器 + 速率限制 + 超时 |
| 安装复杂度 | Skill 复制 | install.sh + 向导 |
| 哲学 | 用最少的代码做最多的事 | 工程化一切(可控性优先) |

### 极简路线:snarktank/ralph

**安装**(四选一):

```bash
# 方式一(推荐):在 Claude Code 中粘贴链接,让它自动装
# Install this skill for me: https://github.com/snarktank/ralph

# 方式二:市场安装
/plugin marketplace add snarktank/ralph
/plugin install ralph-skills@ralph-marketplace

# 方式三:手动复制
git clone https://github.com/snarktank/ralph.git /tmp/ralph
cp -r /tmp/ralph/skills/prd ~/.claude/skills/
cp -r /tmp/ralph/skills/ralph ~/.claude/skills/

# 方式四:项目级安装(团队共享/自定义脚本)
mkdir -p scripts/ralph
cp /tmp/ralph/ralph.sh scripts/ralph/
cp /tmp/ralph/CLAUDE.md scripts/ralph/
chmod +x scripts/ralph/ralph.sh
```

**核心文件结构**(记忆完全依赖文件系统):

- `ralph.sh` — **循环引擎**:bash 脚本不断生成新的 AI 实例。每次迭代:创建功能分支(来自 prd.json 的 branchName)→ 选最高优先级未完成 story(`passes: false`)→ 生成全新 AI 实例实现 → 跑质量检查(类型检查、测试)→ 通过则 git commit,失败留给下次 → 更新 prd.json 标记 `passes: true` → 经验追加到 progress.txt → 重复直到全部完成或达上限(默认 10 次);

```bash
./scripts/ralph/ralph.sh [max_iterations]          # 默认 Amp
./scripts/ralph/ralph.sh --tool claude [iterations]  # Claude Code
```

- `prd.json` — **任务定义**(Ralph 的"大脑"):扁平 JSON,含 projectName、branchName、userStories(id/title/description/acceptanceCriteria/priority/passes/dependsOn/notes);
- `progress.txt` — **经验日志**(Ralph 的"长期记忆"):每次迭代追加学到的经验(发现的命令、模式、坑),下一次全新实例读取后立即获得之前所有经验——**这就是 Ralph 越跑越顺的原因:知识在迭代间积累,而上下文保持干净**;
- `AGENTS.md` — **持久知识库**:记录稳定的、跨项目的知识(代码约定、Gotchas),Claude Code 和 Amp 启动时自动读取。

**PRD 编写原则**(PRD 质量直接决定执行效果):

1. **Story 粒度适中**:一次迭代能完成、有独立价值——经验法则:涉及 1-3 个文件修改、3-5 条验收标准;
2. **验收标准必须可自动验证**:❌ "Code quality is good" → ✅ "pnpm types:check passes"、"File src/auth/login.ts exists and exports loginHandler function";
3. **用 dependsOn 控制执行顺序**:US-002 dependsOn ["US-001"];
4. **在 notes 中提供上下文**:把你知道但 AI 不一定知道的信息写进去。

执行:`/prd I want to add i18n support...` 生成 PRD → `/ralph` 转换 prd.json → `./scripts/ralph/ralph.sh --tool claude 30`。完成信号:所有 story 标记 `passes: true` 后输出 `<promise>COMPLETE</promise>`。监控:`cat tasks/prd.json | jq '.userStories[] | {id, title, passes}'`。

### 工程化路线:frankbria/ralph-claude-code

**安装与命令**:

```bash
git clone https://github.com/frankbria/ralph-claude-code.git
cd ralph-claude-code && ./install.sh
# 获得:ralph / ralph-enable / ralph-setup / ralph-import / ralph-monitor

cd your-project && ralph-enable    # 已有项目(自动检测 Node/Python/Go 与框架)
ralph-setup my-new-project         # 全新项目
ralph-import path/to/your-prd.md   # 导入现有 PRD
```

**`.ralph/` 目录结构**(对照 snarktank):

| frankbria | snarktank | 作用 |
| --- | --- | --- |
| PROMPT.md | prd.json 的 projectName + description | 定义项目目标 |
| fix_plan.md | prd.json 的 userStories | 任务列表和进度 |
| AGENT.md | CLAUDE.md / AGENTS.md | 构建命令和项目约定(**自动维护**) |
| specs/ | prd.json 的 notes 字段 | 详细需求 |
| sessions/ | 无(每次新进程) | 会话状态追踪 |

**差异化特性:多层安全机制**:

- **断路器**:连续 N 次迭代无新任务完成、或连续出现相同错误信息(AI 陷入死循环)→ 自动停止循环,防止无意义 API 消耗;
- **速率限制**:默认 100 calls/hour;
- **5 小时 API 限额三层检测**:预检测(调用前估算剩余额度)+ 响应检测(解析 rate limit headers)+ 回退策略(接近限额自动降频);
- **会话过期管理**:默认 24 小时,超时自动清理会话数据;
- **智能退出检测**:`退出条件 = completion_indicators >= 2 AND EXIT_SIGNAL: true`——双条件防止过早退出(单一信号可能是误判,比如 AI 说"任务完成"但实际只完成了当前 story)。

**常用参数**:`ralph --resume`(从上次中断继续)、`ralph --calls 50 --timeout 120`(限制 API 调用与超时)、`ralph --monitor`(实时监控)、`ralph --live`(tmux 中运行,推荐长时间运行)。

## 实践 / 应用:怎么用好 Ralph

1. **好的 prompt 是前提**:Ralph 循环完全依赖前置准备——PRD 够不够好?功能定义够不够紧凑?你知道"完成"长什么样吗?答案不精确,循环跑多少次都是 garbage in, garbage out;
2. **配合反馈机制**:没有自动验证的 Ralph 只是"盲跑",类型检查/测试/CI 是让它"知道什么时候算好了"的关键;
3. **选实现**:快速开始用 snarktank(轻量),需要可控性和安全机制用 frankbria(断路器/仪表盘/限额);
4. **与 GSD 的关系**:Ralph 是"给 AI 一个任务让它反复尝试"(自主执行但需自带蓝图);[GSD](../skills/gsd-workflow-skill.md) 是"理解你要什么,研究怎么做,规划怎么分步,执行并验证"(每阶段人类校验)。Ralph 循环假设你带着完整蓝图来——GSD 帮你构建这个蓝图。两者不矛盾,GSD 继承 Ralph 的核心原则(新鲜上下文、文件真相源)并补上项目理解和质量验证;
5. **边界**:Ralph 是执行技术而非完整方案——没有项目理解、没有阶段规划、没有质量验证。它最擅长的是"迭代直到成功"类任务。

## 总结

- **本质**:方法论而非工具——`while :; do cat PROMPT.md | claude ; done` 无限循环 + 每次全新上下文;
- **解决问题**:Context Rot(Dumb Zone:上下文过半 AI 明显退化);累积上下文是负债而非资产;
- **三个支柱**:新 Session(干净上下文)+ 文件作为真相来源(PRD/计划/progress.txt/Git)+ 反馈循环(类型检查/测试/CI);
- **Human on the Loop**:设定目标与边界,AI 自主运行,人偶尔检查进度——监督式管理而非保姆式陪伴;
- **两种实现**:snarktank(极简,10k+ stars)/ frankbria(工程化,断路器+仪表盘+速率限制);三种模式:完整实现/探索/暴力测试;
- **下一步**:对照 [GSD 工作流系统](../skills/gsd-workflow-skill.md)(GSD 是"整个军火库"而 Ralph 是"一件武器")与 [Loop Engineering](loop-engineering.md),理解"自主型 vs 规划型"Agent 工作流的取舍。

## 延伸阅读

- 原始概念:https://github.com/geoffrey-huntley/ralph;snarktank/ralph:https://github.com/snarktank/ralph;frankbria/ralph-claude-code:https://github.com/frankbria/ralph-claude-code
- 视频:Roman (Mentat)《You're Using Ralph Wiggum Loops WRONG》
- 站内:[GSD 工作流系统](../skills/gsd-workflow-skill.md)(规划型对照)、[gstack 角色化技能集](../skills/gstack-skills.md)、[Loop Engineering](loop-engineering.md)、[用 Agent 持续交付](agent-cognitive-complexity-gates.md)、[AI Coding Harness 设计经验](ai-coding-harness-design.md)
