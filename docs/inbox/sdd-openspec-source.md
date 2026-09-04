# 原始资料:AI coding 从个人提效到赋能团队(一)走向可控--Spec-Driven Development

> 来源:微信公众号「一个技术豆」;原文链接:https://mp.weixin.qq.com/s/USigX8-a5fHOWV_WVod5pg
> 抓取日期:2026-08-09;状态:已整理为 docs/07-agent-coding/skills/sdd-openspec-superpowers.md
> 性质:SDD(Spec-Driven Development)方法论 + OpenSpec(需求层工具)+ Superpowers(执行层 15 skill)+ 组合方案与落地思考

---

目前AI编程越来越成熟，今年土豆在对团队进行AI编程转型时，也没遇到过25年时质疑的声音，大家都在主动拥抱AI，相对兴趣创意者，职业程序员第一课就是如何使AI可控。今天我们一起聊下SDD(Spec-Driven Development)。

一、先分清：Vibe Coding 与 SDD 规范编码，天差地别
传统 Vibe Coding（凭感觉编码）
这是绝大多数人使用 AI 写代码的现状：只抛出模糊需求，AI 自由发挥生成代码，全程边写边改。
痛点：需求无书面共识、即兴开发；代码零散，后期维护成本极高；新增功能扩展困难；大量无效 Token 浪费算力与时间。
SDD（Spec-Driven Development 规范驱动开发）
核心逻辑：先定规范，再写代码。开工前和 AI 协同产出结构化需求文档，把 “要做什么、为什么做、怎么做” 全部白纸黑字敲定，再让 AI 严格按照规范落地代码。核心优势：规范驱动、先设计后编码、代码实现精度高、项目结构清晰，天然支持长期迭代、可维护可扩展。

二、OpenSpec：轻量化 SDD 落地工具，打通需求到代码全流程
OpenSpec 是面向 AI 编程助手的开源规范驱动开发工具，适配 Cursor、Claude Code、Gemini 等主流 AI 开发工具，核心作用是让人和 AI 在编码前对齐全部需求，标准化变更流程。
开源地址：https://github.com/Fission-AI/OpenSpec
快速安装初始化

# 全局安装工具npm install -g @fission-ai/openspec@latestnpm install -g @openspeccn/openspec# 查看版本校验安装openspec --version# 项目根目录初始化配置openspec --init
初始化后可选择日常使用的 AI 编程工具，自动生成命令、配置文件，重启 IDE 即可启用全套斜杠命令快捷操作。内置核心快捷指令：
/opsx:new：创建新需求变更
/opsx:continue：迭代完善规范 / 设计
/opsx:apply：依据规范自动生成代码
/opsx:archive：归档规范至项目全局库
标准 6 阶段开发流水线
1.提案 PROPOSAL
执行/opsx-propose创建需求，AI 自动在.openspec/changes/生成 3 份核心 Markdown 文档，统一人机认知：
proposal.md：业务需求文档，明确需求背景、目标、业务边界（Why & What）

design.md：技术方案文档，敲定技术选型、数据结构、API、架构（How）

tasks.md：可执行任务清单，拆分最小开发步骤，AI 编码唯一执行依据

2.规范 SPECS：细化接口、数据、业务逻辑，形成项目可复用标准
3.设计 DESIGN：落地技术架构、模型调整、分层实现方案
4.任务 TASKS：把设计拆解为逐条可落地编码任务
5.应用 APPLY：执行/opsx-apply [变更ID]，AI 严格遵循设计与任务清单生成代码，减少反复修改
6.归档 ARCHIVE：将本次迭代规范合并至项目全局openspec/specs/库，解决 “代码更新、文档滞后” 行业痛点，所有需求纳入 Git 版本管理，可追溯、可评审、可回滚。
OpenSpec 核心亮点
灵活流动流程：无强制瀑布阶段锁死，任意环节可回溯修改规范，适配敏捷迭代；

兼容存量项目：增量式记录变更，无需重构全量文档，老系统改造友好；

轻量化增量迭代：单次只处理单一功能 / 缺陷，拒绝一次性超大设计；

规范即源码：把spec(需求、设计文档)和业务代码同仓库管理，成为可校验的开发契约。
三、Superpowers：给 AI 立开发规矩，强约束保障代码质量

如果说 OpenSpec 负责定义 “写什么”，Superpowers 就负责管控“怎么做”。它不靠提升 AI 智商，而是通过一套标准化技能体系，强制 AI 遵循资深工程师最佳实践：TDD 测试驱动、分层代码审查、多代理隔离开发。
开源地址：https://github.com/obra/superpowers
适配平台：Claude Code、Cursor、Copilot、Gemini CLI 等主流 AI 编程工具

完整 7 步开发流程
头脑风暴 Brainstorming：梳理业务意图，划定需求边界，输出顶层业务大纲

Git 隔离工作区：创建独立 git worktree，变更隔离，不污染主分支代码

编写设计方案：拆解 5 分钟内可完成的最小任务，标注文件路径、代码、验收步骤

子代理协同开发：拆分编码、校验多类独立 AI 子代理，两阶段审核规范与代码质量，支持并行执行

TDD 测试驱动开发：强制 “先写失败用例→实现最小代码→测试通过→重构”，杜绝无测试代码

代码审查：自动比对代码与原始规范偏差，人工 + 机器双重评审，拦截缺陷收尾开发分支：全量校验测试用例，提供合并 / 保留 / 丢弃分支选项，清理工作区

SKills目录清单

Skill
用途
头脑风暴 (brainstorming)
需求分析 → 设计规格，不写代码先想清楚
编写计划 (writing-plans)
把规格拆成可执行的实施步骤
执行计划 (executing-plans)
按计划逐步实施，每步验证
测试驱动开发 (test-driven-development)
严格 TDD：先写测试，再写代码
系统化调试 (systematic-debugging)
四阶段调试法：定位→分析→假设→修复
请求代码审查 (requesting-code-review)
派遣审查 agent 检查代码质量
接收代码审查 (receiving-code-review)
技术严谨地处理审查反馈，拒绝敷衍
完成前验证 (verification-before-completion)
证据先行——声称完成前必须跑验证
派遣并行 Agent (dispatching-parallel-agents)
多任务并发执行
子 Agent 驱动开发 (subagent-driven-development)
每个任务一个 agent，两轮审查
Git Worktree 使用 (using-git-worktrees)
隔离式特性开发
完成开发分支 (finishing-a-development-branch)
合并/PR/保留/丢弃四选一
编写 Skills (writing-skills)
创建新 skill 的方法论
使用 Superpowers (using-superpowers)
元技能：如何调用和优先使用 skills

核心优势
多代理隔离调度：方案、编码、测试、校验代理分工独立，上下文互不干扰；

质量原生内置：规划阶段同步定义验收用例，开发强制单元 / 边界测试，全流程校验；

开发全链路可控可追溯，AI 输出代码标准化、低缺陷。

四、强强联合：OpenSpec + Superpowers 最优组合方案
两套工具互补短板，形成完整 AI 开发闭环：
OpenSpec 负责需求层：产出结构化、可归档、纳入版本管理的 Proposal/Design/Tasks，解决需求易丢失、无统一文档载体的问题；短板是代码落地阶段质量约束较弱。
Superpowers 负责执行层：用 TDD、多级审查、子代理机制严控编码质量，规范 AI 开发行为；短板是前期需求设计无标准化持久化文档，需求容易遗失在聊天记录。
搭配使用后，既能在开发前完整沉淀业务与技术规范，又能在编码阶段强约束 AI 行为，兼顾需求可追溯与代码高质量。
五、落地思考：企业不要盲目跟风工具流
作为研发负责人，土豆最大的收获，是找到了企业级 AI 编程的落地流程。此前他一直在思考如何把研发流程在 AI 开发场景下实现闭环，也沉淀过不少思路，但对方案本身心存顾虑。在研究 SDD 各类工作流之后，过往的猜想得到了充分印证。
除 OpenSpec、Superpowers 外，行业还有gtasck、RalphLoop，以及新一代当红炸子鸡 grill-me 等同类 AI 开发工作流，各大厂商也在自研内部 SDD 流程。建议各位不必直接照搬开源工具：
吸收其规范前置、文档即代码、TDD 质量内建、任务拆解核心思路；
结合公司现有研发流程、代码资产、技术栈定制适配方案；