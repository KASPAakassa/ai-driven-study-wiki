# OpenAI Harness Engineering:0 行手写代码的全 agent 团队战报

> **一句话摘要**:OpenAI 内部一个 5 个月、约 100 万行代码、~1500 个 PR 的产品,由 3 人→7 人团队用 Codex 完成,**0 行手写代码**(人均 3.5 PR/天,约 1/10 手写时间)。核心不是"模型多强",而是 **harness 工程**:AGENTS.md 当目录而非百科全书、固定分层 + 自定义 linter 机械强制架构、仓库内版本化制品才算"存在"(agent legibility)、agent 对 agent 评审、"熵"管理像垃圾回收。
>
> **来源**:OpenAI《Harness engineering: leveraging Codex in an agent-first world》(Ryan Lopopolo 团队,https://openai.com/index/harness-engineering/,约 2026-02,5 个月内部 beta)

## 概念

### 0 行手写代码的实证

OpenAI 团队用 Codex 从零构建了一个生产级产品(首个 commit 2025 年 8 月底,约 5 个月):

| 指标 | 数值 |
| --- | --- |
| 手写代码 | **0 行**(agent 生成全部代码) |
| 代码量 | ~100 万行 |
| PR 数 | ~1500 个 |
| 团队规模 | 3 人 → 7 人 |
| 产出效率 | 人均 3.5 PR/天,约 1/10 手写时间 |

### 工程师角色的转变

- 工程师不再写代码,而是:**设计环境、表达意图、建立反馈回路**;
- 失败时的提问方式变了:不问"能不能再试一次",而问"**缺什么能力**"(agent 卡住 = harness 缺能力,不是模型不行)。

## 原理(harness 工程四支柱)

### 1. AGENTS.md 是目录,不是百科全书

- 仓库 `docs/` 是 **system of record**(文档在目录深处,按需读);
- 根目录 `AGENTS.md` 约 **100 行**,只做导航(progressive disclosure);
- **巨型说明文件会"腐烂"且不可验证**——指令一旦无法验证,agent 就会忽略或冲突。

### 2. 严格边界 + 可预测结构:固定分层 + 机械强制

- 架构用固定分层:`Types → Config → Repo → Service → Runtime → UI`;
- 用**自定义 linter** 机械强制依赖方向(不许跨层引用)——agent 环境需要"严格边界 + 可预测结构",比人类团队更依赖纪律;
- 环境要"agent legible":让 agent 一眼看懂该往哪改、不该碰哪。

### 3. Agent legibility:仓库内版本化制品才算"存在"

- **可见性**:每工作树可启动应用,接 Chrome DevTools Protocol,DOM 快照/截图技能;用 LogQL/PromQL 查询运行时状态——agent 能"看到"自己的产物;
- **持久性**:单次 run 最长 **6+ 小时**,跨窗口靠制品落盘;
- 目标:agent 的判断基于**可验证的仓库状态**,而非记忆或自述。

### 4. 吞吐改变工程哲学

- **最小化阻塞 gate**:合并哲学改变(短命 PR、flake 后补跑);
- **agent 对 agent 评审**:用 Ralph Wiggum Loop(无限循环 + 全新上下文)做独立审查;
- **熵管理**:早期每周五手工清 "AI slop" → 改为"golden principles"+ **后台 cleanup agents 定期重构**,像垃圾回收一样持续处理熵。

## 代码 / 实现

```text
# 仓库结构(固定分层 + 自定义 linter 强制依赖方向)
Types/           # 类型定义
Config/          # 配置
Repo/            # 仓库层
Service/         # 服务层
Runtime/         # 运行时
UI/              # 前端

# 根 AGENTS.md(~100 行,目录式)
- 本仓库是 <product>,架构分层见上,依赖方向由 linter 强制
- docs/ 是 system of record,详细说明按需阅读 docs/xxx
- 改动必须跑 <linter + tests>,禁止跨层引用
```

可复用的工程动作:

1. **根目录只放导航 AGENTS.md(~100 行)**,细节进 docs/;
2. **用 linter 机械强制架构约束**(依赖方向/禁止模式);
3. **让 agent 可"看到"运行时**(CDP 截图、LogQL/PromQL 查询);
4. **评审交给独立 agent**(Ralph Wiggum Loop 式全新上下文审查);
5. **熵管理自动化**(cleanup agents 定期重构,不攒周五)。

## 实践 / 应用

- **适用**:全 agent 团队/agent-first 组织;想让 agent 独立产出大规模代码的团队;
- **关键前提**:AGENTS.md + docs/ 分层(目录非百科全书)、严格架构边界(linter 强制)、可观测(agent legibility)、独立评审、熵治理;
- **教训**:失败时补"能力"而非重试;巨型说明文件会腐烂(不可验证的指令 = 无效指令);
- 与 [AI Coding Harness 设计经验](ai-coding-harness-design.md)(个人/团队护栏)互补:那篇是方法论框架,这篇是**大规模实证**。

## 总结

1. **实证**:0 行手写代码、~100 万行、~1500 PR、人均 3.5 PR/天——agent-first 可行。
2. **AGENTS.md 是目录不是百科全书**:docs/ 为 system of record,根文件 ~100 行导航;巨型说明文件会腐烂。
3. **严格边界 + 可预测结构**:固定分层 + 自定义 linter 机械强制依赖方向。
4. **Agent legibility**:仓库内版本化制品才算"存在";CDP 截图/LogQL 让 agent 看到运行时;单 run 6+ 小时。
5. **吞吐改变哲学 + 熵管理**:短命 PR/agent 互审;cleanup agents 像垃圾回收治理 "AI slop"。

**下一步学什么**:对比 [AI Coding Harness 设计经验](ai-coding-harness-design.md) 与 [Vibe Coding 最佳实践](vibe-coding-engineering-practice.md)(工程栈总纲);想看另一家的长时实践见 [OpenAI 长时 agent 三件套](../../03-agents/agent-long-running-openai.md)。

## 延伸阅读

- 站内:[AI Coding Harness 设计经验](ai-coding-harness-design.md)、[Vibe Coding 最佳实践](vibe-coding-engineering-practice.md)、[给 Coding Agent 立规矩](agent-rules-agents-md.md)、[Ralph Wiggum 循环](ralph-wiggum-loop.md)、[OpenAI 长时 agent 三件套](../../03-agents/agent-long-running-openai.md)
- 外部:原文(https://openai.com/index/harness-engineering/)
