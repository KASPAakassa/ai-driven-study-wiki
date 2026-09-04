# SDD(Spec-Driven Development):从个人提效到团队可控的 Agent Coding 思路

> **一句话摘要**:职业程序员的第一课是"如何使 AI 可控"。SDD(Spec-Driven Development,规范驱动开发)的核心逻辑:**先定规范,再写代码**——开工前和 AI 协同产出结构化需求文档(要做什么/为什么做/怎么做),再让 AI 严格按规范落地。本文提炼 SDD 的 agent coding 思路,并收录两个落地工具:**OpenSpec(需求层,轻量 SDD 工具)+ Superpowers(执行层,15 个 skill 强约束编码质量)**,最后给出组合方案与企业落地思考。
>
> **来源**:微信公众号「一个技术豆」《AI coding 从个人提效到赋能团队(一)走向可控--Spec-Driven Development》,https://mp.weixin.qq.com/s/USigX8-a5fHOWV_WVod5pg;OpenSpec https://github.com/Fission-AI/OpenSpec;Superpowers https://github.com/obra/superpowers;原始资料存档于 `docs/inbox/sdd-openspec-source.md`

## 概念:Vibe Coding vs SDD

| | Vibe Coding(凭感觉编码) | SDD(规范驱动开发) |
| --- | --- | --- |
| 需求 | 模糊需求抛出,AI 自由发挥 | 开工前与 AI 协同产出结构化需求文档 |
| 方式 | 即兴开发,边写边改 | 先设计后编码,规范驱动 |
| 代码 | 零散,后期维护成本极高 | 实现精度高、结构清晰 |
| 扩展 | 新增功能困难 | 天然支持长期迭代、可维护可扩展 |
| 成本 | 大量无效 Token 浪费 | 减少反复修改 |

**Vibe Coding 的痛点**:需求无书面共识、即兴开发、代码零散、无效 token 浪费。

**SDD 的核心逻辑**:"要做什么(Why)、为什么做(What)、怎么做(How)"全部白纸黑字敲定,再让 AI 严格按规范落地代码。**对职业程序员来说,SDD 是把 AI 从"提效玩具"变成"可控生产力"的关键一步。**

## 原理:OpenSpec——轻量 SDD 落地工具(需求层)

**OpenSpec** 是面向 AI 编程助手的开源规范驱动开发工具,适配 Cursor、Claude Code、Gemini 等主流工具。核心作用:**让人和 AI 在编码前对齐全部需求,标准化变更流程**。

### 安装初始化

```bash
npm install -g @fission-ai/openspec@latest   # 或 @openspeccn/openspec
openspec --version                            # 校验安装
openspec --init                               # 项目根目录初始化
```

初始化后可选择日常 AI 编程工具,自动生成命令/配置文件,重启 IDE 启用全套斜杠命令。内置核心快捷指令:`/opsx:new`(创建新需求变更)、`/opsx:continue`(迭代完善规范/设计)、`/opsx:apply`(按规范自动生成代码)、`/opsx:archive`(归档规范至项目全局库)。

### 标准 6 阶段开发流水线

1. **提案 PROPOSAL**:`/opsx-propose` 创建需求,AI 自动在 `.openspec/changes/` 生成 3 份核心 Markdown(统一人机认知):
   - `proposal.md`:业务需求文档(背景、目标、业务边界,Why & What);
   - `design.md`:技术方案文档(技术选型、数据结构、API、架构,How);
   - `tasks.md`:可执行任务清单(拆分最小开发步骤,AI 编码唯一执行依据);
2. **规范 SPECS**:细化接口、数据、业务逻辑,形成项目可复用标准;
3. **设计 DESIGN**:落地技术架构、模型调整、分层实现方案;
4. **任务 TASKS**:把设计拆解为逐条可落地编码任务;
5. **应用 APPLY**:`/opsx-apply [变更ID]`,AI 严格遵循设计与任务清单生成代码;
6. **归档 ARCHIVE**:本次迭代规范合并至项目全局 `openspec/specs/` 库,解决"代码更新、文档滞后"痛点;所有需求纳入 Git 版本管理,可追溯、可评审、可回滚。

### 核心亮点

- **灵活流动流程**:无强制瀑布阶段锁死,任意环节可回溯修改规范,适配敏捷迭代;
- **兼容存量项目**:增量式记录变更,无需重构全量文档,老系统改造友好;
- **轻量化增量迭代**:单次只处理单一功能/缺陷,拒绝一次性超大设计;
- **规范即源码**:spec(需求/设计文档)与业务代码同仓库管理,成为可校验的开发契约。

## 原理:Superpowers——给 AI 立开发规矩(执行层)

如果说 OpenSpec 负责定义"写什么",**Superpowers** 就负责管控"怎么做"——不靠提升 AI 智商,而是通过一套标准化技能体系强制 AI 遵循资深工程师最佳实践:**TDD 测试驱动、分层代码审查、多代理隔离开发**。适配 Claude Code、Cursor、Copilot、Gemini CLI 等。

### 完整 7 步开发流程

1. **头脑风暴 Brainstorming**:梳理业务意图,划定需求边界,输出顶层业务大纲;
2. **Git 隔离工作区**:创建独立 git worktree,变更隔离,不污染主分支;
3. **编写设计方案**:拆解 5 分钟内可完成的最小任务,标注文件路径、代码、验收步骤;
4. **子代理协同开发**:拆分编码、校验多类独立 AI 子代理,两阶段审核规范与代码质量,支持并行;
5. **TDD 测试驱动开发**:强制"先写失败用例→实现最小代码→测试通过→重构",杜绝无测试代码;
6. **代码审查**:自动比对代码与原始规范偏差,人工 + 机器双重评审;
7. **收尾开发分支**:全量校验测试用例,提供合并/保留/丢弃分支选项,清理工作区。

### Skills 目录清单(15 个)

| Skill | 用途 |
| --- | --- |
| 头脑风暴 (brainstorming) | 需求分析 → 设计规格,不写代码先想清楚 |
| 编写计划 (writing-plans) | 把规格拆成可执行的实施步骤 |
| 执行计划 (executing-plans) | 按计划逐步实施,每步验证 |
| 测试驱动开发 (test-driven-development) | 严格 TDD:先写测试,再写代码 |
| 系统化调试 (systematic-debugging) | 四阶段调试法:定位→分析→假设→修复 |
| 请求代码审查 (requesting-code-review) | 派遣审查 agent 检查代码质量 |
| 接收代码审查 (receiving-code-review) | 技术严谨地处理审查反馈,拒绝敷衍 |
| 完成前验证 (verification-before-completion) | 证据先行——声称完成前必须跑验证 |
| 派遣并行 Agent (dispatching-parallel-agents) | 多任务并发执行 |
| 子 Agent 驱动开发 (subagent-driven-development) | 每个任务一个 agent,两轮审查 |
| Git Worktree 使用 (using-git-worktrees) | 隔离式特性开发 |
| 完成开发分支 (finishing-a-development-branch) | 合并/PR/保留/丢弃四选一 |
| 编写 Skills (writing-skills) | 创建新 skill 的方法论 |
| 使用 Superpowers (using-superpowers) | 元技能:如何调用和优先使用 skills |

### 核心优势

- **多代理隔离调度**:方案、编码、测试、校验代理分工独立,上下文互不干扰;
- **质量原生内置**:规划阶段同步定义验收用例,开发强制单元/边界测试,全流程校验;
- **全链路可控可追溯**:AI 输出代码标准化、低缺陷。

## 实践 / 应用:OpenSpec + Superpowers 组合与落地思考

### 强强联合:完整 AI 开发闭环

| | OpenSpec(需求层) | Superpowers(执行层) |
| --- | --- | --- |
| 职责 | 产出结构化、可归档、纳入版本管理的 Proposal/Design/Tasks | 用 TDD、多级审查、子代理机制严控编码质量 |
| 短板 | 代码落地阶段质量约束较弱 | 前期需求设计无标准化持久化文档,需求易遗失在聊天记录 |

**搭配效果**:开发前完整沉淀业务与技术规范 + 编码阶段强约束 AI 行为 = **需求可追溯 + 代码高质量**。

### 企业落地思考(研发负责人视角)

行业同类工作流还有 **gstack、Ralph Loop、grill-me** 等,各大厂商也在自研内部 SDD 流程。**建议不要直接照搬开源工具**,而是:

1. 吸收核心思路:**规范前置、文档即代码、TDD 质量内建、任务拆解**;
2. 结合公司现有研发流程、代码资产、技术栈定制适配方案。

### 与站内 Spec 驱动生态的关系

站内已有多个规格驱动方案,本篇是"方法论 + 需求层工具(OpenSpec)+ 执行层 skill(Superpowers)"的完整视角:

| 站内文章 | 定位 |
| --- | --- |
| [Spec-First Skill](spec-first-skill.md) | 理念与机制(spec-prd/plan/review 系列 skill) |
| [Spec Kit](spec-kit-github.md) | GitHub 官方工具(specify-cli + /speckit.*) |
| [GSD](gsd-workflow-skill.md) | 上下文工程 + 规格驱动系统 |
| [Matt Pocock Skills](mattpocock-skills.md) | 纪律型 skill 集合(含 Superpowers 姊妹章节) |
| **本篇(SDD+OpenSpec+Superpowers)** | **方法论对比 + OpenSpec 工具 + Superpowers 15 skill 全清单** |

## 总结

- **SDD 核心**:先定规范再写代码——把"要做什么/为什么做/怎么做"白纸黑字敲定,是职业程序员让 AI 可控的第一课;
- **OpenSpec(需求层)**:6 阶段流水线(提案→规范→设计→任务→应用→归档),`/opsx:*` 斜杠命令,规范即源码、增量式迭代、兼容存量;
- **Superpowers(执行层)**:7 步流程(TDD/子代理/双重审查)+ 15 个 skill 清单,质量原生内置;
- **组合方案**:OpenSpec 管需求可追溯 + Superpowers 管代码高质量 = 完整闭环;
- **落地建议**:吸收"规范前置、文档即代码、TDD 质量内建、任务拆解"四思路,按团队定制而非照搬;
- **下一步**:对比 [Spec-First](spec-first-skill.md)(理念)与 [Spec Kit](spec-kit-github.md)(GitHub 工具),选择适合自己的规格驱动方案。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/USigX8-a5fHOWV_WVod5pg
- OpenSpec:https://github.com/Fission-AI/OpenSpec;Superpowers:https://github.com/obra/superpowers
- 站内:[Spec-First Skill](spec-first-skill.md)、[Spec Kit:GitHub 官方规格驱动工具](spec-kit-github.md)、[GSD 工作流系统](gsd-workflow-skill.md)、[Matt Pocock 的 Skills(含 Superpowers 姊妹章节)](mattpocock-skills.md)、[gstack 角色化技能集](gstack-skills.md)
