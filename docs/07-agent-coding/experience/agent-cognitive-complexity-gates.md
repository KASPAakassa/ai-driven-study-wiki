# 用 Agent 持续交付:控制认知复杂度

> **一句话摘要**:工具越强大,一个老问题越突出——**人该在哪些环节停下来认真理解,而不是把认知负担全部交给 agent**?作者记录了从"让 agent 全权负责"到"在关键 gate 人工介入"的实践演变:撒手模式 → Spec 优先模式 → **Gate 控制模式**(spec 优先 + 严格控制几个 gate,在 gate 处花时间认真理解)。核心:核心决策和设计必须由人理解清楚再落地,**认知债务不能往后放**。
>
> **来源**:微信公众号「flyer」《用 Agent 持续交付:控制认知复杂度》,https://mp.weixin.qq.com/s/Il5Cr_O5EiG1hLptnAqh8A;原始资料存档于 `docs/inbox/agent-gate-pattern-source.md`;Gate 模式本身见站内 [Gate 模式详解](gate-pattern.md)

## 概念:三种使用方式的演进

| 模式 | 做法 | 结果 |
| --- | --- | --- |
| **撒手模式** | 一句话描述大功能,不读 agent 代码,问题让 agent 解决 | 精力耗尽,需求仍无法满足 |
| **Spec 优先模式** | 写 spec 让 agent 实现 | 项目复杂度上升后,人对项目认知复杂度失控 |
| **Gate 控制模式** | spec 优先 + 严格控制几个 gate,在 gate 处认真理解后放行 | **提升交付质量 + 降低认知负担**,两方面都较好 |

!!! tip "核心洞察"
    **无论是 coding agent 还是 general agent,问题的本质都一样:如果人不对核心决策保持理解,认知债务会随迭代积累,最终失控。** 认知复杂度不会消失,只会转移——要么由人在前期主动消化,要么由系统在后期被动暴露。

## 原理:AGENTS.md 的八步变更流程(核心约束)

**核心理念**:软件变更的错误成本随阶段指数上升——**设计/规范 分钟级 → 编码 小时级 → 上线 不可逆**。因此把校验尽量前移到成本最低的阶段,并在关键节点暂停做对抗性 review。

```
1. 更新设计/需求    功能定义、验收标准、指标;有疑问先与 human 确认,决策固化到文档,不留口头默契
2. 更新技术方案    spec/技术文档(接口契约、状态机、数据流);落笔前必须做对抗性推演
3. 方案确认 gate   spec 完成后暂停,等 human 确认(仅语义性变更触发)
4. 更新测试用例    自然语言 → Given/When/Then → 代码;等待条件用真实证据,不依赖中间状态投影
5. 编码            实现直到全部测试(含 lint/类型检查/race/防 flake 重跑)通过
6. 更新用户文档    同步 README/使用文档
7. 整体 review     回顾全部产出,有问题回到对应步骤
8. 过程复盘        对齐好坏,可复用实践沉淀回 AGENTS.md
```

### 对抗性推演的通用清单(step 2)

- **崩溃恢复**:进程任意点被杀,重启后状态能否正确恢复?未完成动作会不会重复执行或丢失?
- **并发**:多个执行单元同时操作,会不会破坏不变量?
- **边界**:空输入、超大输入、重复输入、恶意输入?
- **幂等**:同一操作重放 N 次,结果是否与执行 1 次一致?
- **回滚**:失败时已发生的副作用如何撤销或补偿?

### Gate 判定速查表(step 3 的触发标准)

| 变更类型 | 需要 gate? |
| --- | --- |
| 新增/修改接口契约、状态机、持久化、权限、对外行为 | ✅ 需要 |
| 纯文档 / 注释 | ❌ 不需要 |
| 为既有行为补测试 | ❌ 不需要 |
| 不改语义的重构 | ❌ 不需要 |
| 构建脚本 / 依赖升级 | ❌ 不需要 |
| 拿不准 | 默认走 gate,向 human 确认 |

!!! warning "不能偷懒"
    在这种约束下,人是要严格在 human gate 环节落实自己的责任——这也是为长期迭代降低认知负担的关键。

## 实践:General Agent(Hermes)的 gate 迁移

hermes 从 Discord 通道 → 多 Profiles + Kanban → 全流程 AI + 等待焦虑,最终把 coding agent 的 gate 经验迁移过来,形成 **autoresearch 模式**:

```
Review → Direction(提出下轮改进方向)→ Align(gate:human 确认方向,不确认不执行)
  → Execute(kanban 编排子代理落地,一轮一个变更范围,eval 门禁)
  → Record(写 self-contained round 文件 + 更新 PROGRESS.md)
  → Retrospect(复盘沉淀回 AGENTS.md)
```

!!! note "关键区别**
    Coding agent 的 gate 在**具体变更的 spec 确认**环节;hermes 的 gate 在**每轮 research 的方向确认(Align)**环节。位置不同,但原则一致:**在不可逆动作之前,人必须确认方向正确**。

## 总结:三条可执行的建议

1. **在 AGENTS.md 明确 gate 的触发条件和判定标准**:不要笼统说"重要决策需要确认",而是像判定速查表那样把每种变更类型是否走 gate 写清楚——**Agent 自己能判断是否需要暂停,人不需要全程盯着**;
2. **gate 只聚焦语义性决策,不要变成审批瓶颈**:纯文档/补测试/不改语义的重构都不需要 gate;保持 gate 轻量,人才有意愿认真对待每一次确认;
3. **定期复盘 gate 粒度**:gate 频繁触发但每次无实质变化 → 门槛太低,合并或删除;上线后频繁暴露设计问题 → 覆盖不足,需要补充。

!!! note "与站内其他文章的呼应**
    - [Gate 模式详解](gate-pattern.md):本实践的通用化方法论(三要素/判定/粒度治理);
    - [企业 Agent 工程化(二)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md):gate 是"后果半径"的人工确认点实现;
    - [Agentic Abstention](../../03-agents/agentic-abstention.md):gate 与"停止判断"互补(agent 判断该不该停,gate 规定人在哪里必须介入);
    - [AI 协作规则设计](../../03-agents/agent-collaboration-rules.md):把判定表写进 AGENTS.md = "规则沉淀成机制"。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/Il5Cr_O5EiG1hLptnAqh8A;原始资料存档于 `docs/inbox/agent-gate-pattern-source.md`
- 站内:[Gate 模式详解](gate-pattern.md)、[给 Coding Agent 立规矩](agent-rules-agents-md.md)、[AI 协作规则设计](../../03-agents/agent-collaboration-rules.md)、[企业 Agent 工程化(二)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md)
