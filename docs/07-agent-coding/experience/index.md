# 💡 使用经验

> 个人 Agent Coding 的使用经验库:工具选型与对比、高效工作流、提示词技巧、配置调优、踩坑记录。

## 本章节文章

- [Ralph Wiggum 循环:无限循环 + 全新上下文的"天真坚持"方法论](ralph-wiggum-loop.md) — `while :; do cat PROMPT.md | claude ; done` 解决 Context Rot:三个支柱 + Human on the Loop + 两种实现(snarktank 极简 / frankbria 工程化)
- [AI 时代的 TDD:把"相信模型"换成"相信反馈"](ai-tdd-practice.md) — RED(证明缺口)/GREEN(最小实现)/REFACTOR(只改结构)三道门 + 四层落地 Codex(AGENTS.md 纪律 + Skill + Subagents 隔离 + Hooks 盯防)
- [Loop Engineering:让 Agent 无人值守地持续迭代](loop-engineering.md) — Anthropic 提出的 Loop 范式 + 中金自动化因子引擎实战复盘(检查点/质量闸门/失败学习)
- [Vibe Coding 最佳实践:从"让 AI 写代码"到可验证的软件工程闭环](vibe-coding-engineering-practice.md) — 工程方法论总纲:Specification→Prompt→Context→Harness→Loop→Verifiable 六层栈 + 12 条最佳实践(完成条件/设计前置/仓库即上下文/信息选择/Subagent 隔离/Skill 沉淀/可靠性环境/Loop 收敛/TDD/Review 变化/复杂性/失败模式反推);每条映射站内深度文章(汇总枢纽,不合并)
- [OpenAI Harness Engineering:0 行手写代码的全 agent 团队战报](openai-harness-engineering.md) — 5 个月 ~100 万行/~1500 PR 由 Codex 生成(0 行手写,人均 3.5 PR/天);AGENTS.md 是目录非百科全书、固定分层+linter 机械强制、agent legibility(制品才算存在)、agent 互审、熵管理像垃圾回收
- [给 Coding Agent 立规矩的正确姿势](agent-rules-agents-md.md) — AGENTS.md / CLAUDE.md / .cursorrules 的正交关系与"一份源文件三消费"解法
- [OpenAI 官方 Prompt 指南:给 System Prompt 做减法](openai-prompt-guide.md) — 面向 GPT-5.6:五原则(减法/结果优先/权限边界/推理成本/验证)+ 8 段式模板,Token -41%~66%
- [Git Worktree:多 Agent 并行开发的隔离底座](git-worktree-parallel-agents.md) — 共享对象库隔离工作现场、多 Agent 任务契约六要素、集成链路与常见坑
- [Graph Engineering:多 Agent 工作流的 14 步路线图](graph-engineering-14-steps.md) — Node/Edge 思维、contract、fan-out/fan-in、菱形拓扑、验证器、收敛循环、模型分层、self-routing
- [Agent 交接方法论:让长任务接力不中断](handoff-handover-methodology.md) — 六问压缩状态、八项交接清单、引用路径不复制内容、三类场景与两版提示词
- [Spec-First 决策栈:16 个思维模型校准 AI Coding 判断](spec-first-decision-stack.md) — 四层决策栈(系统/本质/边界/长期)、证据四等级、8 检查点清单
- [AI Coding Harness 设计经验:护栏怎么长出来](ai-coding-harness-design.md) — 先跑起来再长护栏、Rules 三层/Skills 双角色/CLI 安全工具/看见问题四层/Everything as Code,省 Token 七条
- [Agent Hook 使用指南:切面机制与框架对比](agent-hooks-usage.md) — 五个核心切面、ADK 8 种 Hook 模式、DECO 十余个 Hook 分类、原生 vs 自研判断
- [Agent Hook 实战:Codex 与 Claude Code 双框架配置](agent-hooks-codex-claude-practice.md) — Codex 三层结构 + Claude Code 事件/作用域实战配置、hook 安全编写 15 条、落地分级清单与最小三 hook
- [AI Native 工作方式:像管理团队一样用 AI 的五件事](ai-native-manage-5-things.md) — 定目标/定原则/配资源/看结果/做决策,角色切换:AI 执行迭代,人管目标边界关键判断
- [和 AI 写代码半年:7 条救命操作规范](ai-coding-7-safety-rules.md) — 需求边界/架构把关/配置单一源/前端必重建/启动即报错/安全校验/测试冒烟,附 Skill 模板
- [用 Agent 持续交付:控制认知复杂度](agent-cognitive-complexity-gates.md) — 撒手→Spec 优先→Gate 控制三模式、AGENTS.md 八步流程、对抗性推演清单、hermes autoresearch
- [Gate 模式详解](gate-pattern.md) — 人工确认点的通用化:三要素/语义性判定/放哪/粒度治理,与权限/Hooks/Checkpoint/Abstention 区别
- [AI 时代的代码审查:Agentic Code Review](agentic-code-review.md) — 分层审查(三变量定档)+ 异质 AI 传感器阵列交叉验证 + Agent 提交契约(决策日志/小 PR/证据)+ 人类四大任务
- [📡 数据抓取/分析经验笔记](data-scraping-notes.md) — 滚动记录抓取/解析/分析实战经验(场景/方法/坑/解法/可复用),由 `data-scraping-experience` skill 维护

## 待整理 / 规划

<!-- 从 inbox 收件箱转入本主题的素材,梳理前先登记在这里 -->

## 预计覆盖方向

- **工具对比**:Cursor / Claude Code / Reasonix / Copilot 等工具的能力边界与适用场景
- **工作流**:从需求到交付的 Agent Coding 流程、规则文件(AGENTS.md/CLAUDE.md)设计
- **技巧**:上下文管理、分步任务拆解、review 与验证习惯、成本控制
- **踩坑**:常见失败模式与规避方法

## 学习指引

- 每条经验建议包含:场景 → 做法 → 效果 → 适用边界,方便日后复用。
