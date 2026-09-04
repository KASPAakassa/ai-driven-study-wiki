# 🚀 实战

> 从理论到落地:项目复现、环境搭建、踩坑记录、完整案例(训练、微调、部署、Agent 应用)。

## 本章节文章

- [端到端机器学习项目](practice-end-to-end-ml.md) — 房价预测全流程(纯 numpy 可运行)
- [numpy 从零实现神经网络](practice-numpy-nn.md) — MLP 三分类手写实现
- [调用 LLM API 构建应用](practice-llm-api.md) — chat/func calling/流式输出
- [训练与开发排查清单](practice-debug-checklist.md) — 症状-原因-排查顺序速查
- [Agent 安全审计实战](agent-security-audit-practice.md) — 阿里云 AgentLoop 审计链路:事实底座、低保真→高保真、证据定位
- [Agent 效果优化实战:3 天 7 步建立观测→评估→优化闭环](agent-effect-optimization-practice.md) — 阿里云 AgentLoop(游戏 Agent):观测取证→分层评估(通用/事实/玩法)→三级取证→Skill 护栏回写→BadCase 回归→常态化监控;评估器六段式 Prompt + 避坑 9 条
- [SKILL.md 结果驱动自进化:用评测和轨迹把 Agent 拉回正轨](skill-evolution-results-driven.md) — 阿里技术(代码安全):改 skill 打地鼠→五步闭环(评测→规则诊断→LLM 生成候选 diff→四层 gate→接受/黑名单);诊断不用 LLM、GT 审计怀疑数据、taboo 黑名单、文件系统版本管理、语义陷阱(换词 -27pp);真实数据 77.8%→88.9%
- [得物:AI Native 交易核心系统的研发范式](ai-native-order-system-spec-driven.md) — Spec-Driven 五道关口,让 AI 产出可验证、可度量、可负责
- [腾讯 Vibe Flowing:AI 原生研发团队落地](ai-native-dev-team-vibeflowing.md) — 企业级底座+Rules 三层护栏+Skills+CLI+DB 管控+Everything as Code,运营同事不写代码也能参与建设
- [DeepTutor:港大开源的 AI 个性化辅导工作空间](deeptutor-agent-workspace.md) — 六种学习模式共享一个 Agent 引擎,数据跨工作流流动;Partners 接本地 Claude Code/Codex、三层记忆、多引擎 RAG(25k Star agent 应用案例)
- [阿里云 AgentTeams:企业级多 Agent 协作平台](aliyun-agentteams-enterprise.md) — 四层架构+安全四道防线(零信任)+Manager/TL/Worker 三层协作+弹性沙箱运行时+双飞轮进化,把"Agent 组织"当企业工作负载治理
- [用 Hermes Agent 搭建 OKF 知识库](hermes-okf-knowledge-base.md) — 纯 Markdown + YAML frontmatter 的 Agent 知识库管理:9 种 Concept 类型、Init/Ingest/Query/Lint、无向量库分级策略("先文件系统、后向量库")

## 待整理 / 规划

<!-- 从 inbox 收件箱转入本主题的素材,梳理前先登记在这里 -->

## 学习指引

- 每个实战篇建议包含:目标 → 环境与依赖 → 步骤 → 结果 → 踩坑与心得。
