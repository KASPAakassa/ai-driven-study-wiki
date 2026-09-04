# 原始资料:用 Agent 持续交付:控制认知复杂度

> 来源:微信公众号「flyer」
> 原文链接:https://mp.weixin.qq.com/s/Il5Cr_O5EiG1hLptnAqh8A
> 抓取日期:2026-08-09;状态:整理为 docs/07-agent-coding/experience/agent-cognitive-complexity-gates.md(实践经验)+ docs/07-agent-coding/experience/gate-pattern.md(Gate 模式独立详解)

---

在 Agent 全流程参与的开发时代，coding agent 和 general agent 已经成为日常工具。但工具越强大，一个老问题反而越突出：人该在哪些环节停下来认真理解，而不是把认知负担全部交给 agent？ 
本文记录了我从”让 agent 全权负责”到”在关键 gate 人工介入”的实践演变。核心观点是：核心决策和设计必须由人理解清楚再落地，认知债务不能往后放。
一、演进过程
从今年年初开始，我进行调研、编程、写文档等，几乎全部借助 AI 进行。使用过程中经历了两条演进线。
1.1 Coding Agent：三种使用方式
撒手模式一句话描述大功能，不读 agent 生成的代码，遇到问题就让 agent 解决。最终精力耗尽，需求仍无法满足。

Spec 优先模式我或 agent 来写 spec，然后让 agent 实现。比模式 1 好，但随着项目复杂度增加，人对项目的认知复杂度失控。

Gate 控制模式spec 优先，但严格控制几个 gate，在这几个 gate 处花时间认真理解，理解通过后再让 agent 继续。目前在 提升 agent 交付质量 和 降低人的认知负担 两方面，都有较好效果。

1.2 General Agent (Hermes)：四个阶段
Discord 通道模式通过 Discord channel 按 topic 分类交互，希望历史使用产生复利，把点连成面。

多 Profiles + Kanban 编排专用 profile 处理聚焦任务，default profile 仅做 orchestrator。编排完任务后即可编排下个任务，提升并发度；同时聚焦的 context 也带来更好的输出质量。

全流程 AI 化 + 等待焦虑所有交互都通过 hermes 进行。但即使 kanban 任务状态显示运行中，仍不放心进展。这种不放心，根源是对当前任务的 认知负担 没有把握好。

结合 Gate 模式将 coding agent 的 gate 控制经验迁移到 hermes，达到初步满意效果。

核心洞察：无论是 coding agent 还是 general agent，问题的本质都一样——如果人不对核心决策保持理解，认知债务会随迭代积累，最终失控。

二、Coding Agent 实践
在写一个新项目时（问题域之前没有遇到过），我用了约 3 天时间，按如下方式进行：
通过社区类似项目、自己的理解与 hermes 交互，持续产出调研类文档

基于自己的理解从调研类文档中抽出设计文档

不断对设计文档每句话进行人为推敲，对于没有理解清楚或觉得描述不对的内容，通过 agent 或 AI search 进一步验证，直到对设计文档没有疑问，自己理解清楚

然后在 AGENTS.md 中，做如下约束：
## 核心理念

软件变更的错误成本随阶段指数上升：**设计/规范 分钟级 → 编码 小时级 → 上线 不可逆**。
因此把校验尽量前移到成本最低的阶段，并在关键节点暂停做对抗性 review。

## 变更流程（严格按顺序，不得跳步）

1. **更新设计/需求** — 先更新产品/功能文档（功能定义、验收标准、指标），确保与目标对齐。有疑问先与 human 确认，再把决策固化到文档，不留口头默契。2. **更新技术方案** — 更新 spec / 技术文档（接口契约、状态机、数据流）。**落笔前必须做对抗性推演**：假设系统在最坏时点失败/被中断，逐条回答"恢复后语义是否连续"——
   - 不变量会不会被破坏？
   - 计数 / 状态 / 引用会不会漂移或重复？
   - 中断的未完成动作如何续跑 / 回滚？
   - 推演出自相矛盾的点，必须在 spec 阶段修正，不要留到 coding 返工

3. **方案确认 gate（暂停，等 human 确认）** — spec 完成后、进入测试/编码前暂停。**仅当本次为语义性变更时触发**：新增/修改接口契约、状态机、持久化语义、权限/安全边界、对外行为变更。
   纯文档 / 注释 / 为既有行为补测试 / 不改语义的重构 / 构建脚本 / 依赖升级 —— **无需 gate，直接进入 step 4**。
   - human 聚焦 review 两点：① step 2 的对抗性推演是否自洽；② 本次接口/行为的 delta
   - gate 保持轻量：不是全 spec 审批，human 确认"通过"即继续；不通过则回到 step 1/2 修正

4. **更新测试用例** — 测试用例应文档化：自然语言描述 → Given/When/Then → 代码。**断言"某事再次发生/已发生"类语义时，等待条件必须是触发该状态的真实证据（事件、副作用产物），不得依赖中间状态投影的即时值**——即时值可能是上一轮遗留的旧值，产生竞态。

5. **编码** — 实现代码，直到全部测试（含 lint、类型检查、race、防 flake 重跑）通过。

6. **更新用户文档** — 同步 README / 使用文档（特性、快速开始、结构、路线图）。

7. **整体 review** — 回顾本次变更的全部产出，判断是否有需要改善的内容（文档一致性、设计偏差、遗漏用例），有问题则回到对应步骤修复。

8. **过程复盘** — 回顾整个处理过程中做得好与不好的内容，与 human 对齐：好的保持，不好的改善；可复用的好实践沉淀回本文件或项目级 `AGENTS.md`。

## 对抗性推演的通用清单

写 spec 时主动问自己：
- **崩溃恢复**：进程在任意点被杀，重启后状态能否正确恢复？未完成动作会不会重复执行或丢失？
- **并发**：多个执行单元同时操作，会不会破坏不变量？
- **边界**：空输入、超大输入、重复输入、恶意输入，行为是否符合预期？
- **幂等**：同一操作重放 N 次，结果是否与执行 1 次一致？
- **回滚**：失败时已发生的副作用如何撤销或补偿？

## Gate 判定速查

| 变更类型 | 需要 gate？ |
|---|---|
| 新增/修改接口契约、状态机、持久化、权限、对外行为 | ✅ 需要 |
| 纯文档 / 注释 | ❌ 不需要 |
| 为既有行为补测试 | ❌ 不需要 |
| 不改语义的重构 | ❌ 不需要 |
| 构建脚本 / 依赖升级 | ❌ 不需要 |
| 拿不准 | 默认走 gate，向 human 确认 |
在这种约束下，人是要严格在 human gate 环节落实自己的责任，这也是为长期迭代降低认知负担的关键。
不能偷懒！
接下来就是与 coding agent 按照上述约束进行迭代。
三、Hermes Agent 实践
hermes 几乎成了我的个人助理。除了需要显式和 coding agent 交互的场景，我用 hermes 做几乎全部的事情，尤其是有研究性质的项目。
之前写过一篇 autoresearch 的文章，目前我强依赖 autoresearch 这种模式来做项目：
按照上述 coding agent 的方式，实现一版工程代码

增加一个 research 目录，其中重点维护 AGENTS.md 和 README.md 两个文件：

AGENTS.md：定义 research 的迭代步骤

README.md：帮助我理解 research 采用的方法，如 Bradley-Terry / Matrix Factorization 算法、评估的 metrics 等

抽取出了 AGENTS.md 部分内容：
**Process (strictly in this order):**

1. **Review** — read `research/PROGRESS.md` (Pipeline Overview + Current State + Round Log index) and the `design/` docs (DESIGN.md, review.md, decisions/) to assess XXX current state, progress, and gaps. Load individual round files from `research/progress/` only as needed.

2. **Direction** — analyze and propose the next round's improvement direction.

3. **Align** — get the human's sign-off on the direction BEFORE any implementation. No alignment, no execution.

4. **Execute** — orchestrate local profiles (subagents) via kanban to land the direction; ONE change scope per round, `eval_judge.py` against a XXX is the gate.

5. **Record** — after the round: write one self-contained round file `research/progress/YYYY-MM-DD_HH-MM-SS_<round-id>.md` (hypothesis, setup, results, gate verdict, decision, next-round suggestions), then update `research/PROGRESS.md` (Current State + one new line in the Round Log index), and judge whether the `design/` docs need updating (e.g. new ADR for an architecture decision, review.md gap list refresh).

6. **Retrospect** — review what went well and what didn't: reinforce what worked; for what didn't, analyze root cause and how to prevent recurrence (e.g. write lessons learned into AGENTS.md Gotchas or hard constraints, the dead-ends list in PROGRESS.md, or the design/ docs).
与 coding agent 的实践一样，这里同样遵循 gate 约束原则：人的责任是在 human gate 环节严格把关，不能把理解的责任留给 agent。
关键区别：coding agent 的 gate 在具体变更的 spec 确认环节；hermes 的 gate 在每轮 research 的方向确认（Align）环节。位置不同，但原则一致——在不可逆动作之前，人必须确认方向正确。

然后由 hermes 通过多 profiles 和 kanban 编排任务持续进行 autoresearch。
四、小结
上述过程，最核心的命题是如何把握认知复杂度。coding 阶段可以交给 agent 去做，但对核心决策、核心设计必须由人理解清楚，然后再落地，不能把认知债务往后放。
落地到具体操作，有三条可执行的建议：
在 AGENTS.md 中明确 gate 的触发条件和判定标准不要笼统地说”重要决策需要确认”，而是像 Gate 判定速查表那样，把每种变更类型是否走 gate 写清楚。Agent 自己能判断是否需要暂停，人不需要全程盯着。

gate 只聚焦语义性决策，不要变成审批瓶颈纯文档、补测试、不改语义的重构，都不需要 gate。保持 gate 足够轻量，人才有意愿认真对待每一次 gate 确认。

定期复盘 gate 的粒度如果发现某个 gate 频繁触发但每次都没有实质变化，说明这个 gate 的门槛太低，需要合并或删除。反之，如果上线后频繁暴露设计问题，说明 gate 覆盖不足，需要补充。

认知复杂度不会消失，只会转移——要么由人在前期主动消化，要么由系统在后期被动暴露。选择前者，是维持长期交付能力的基础。