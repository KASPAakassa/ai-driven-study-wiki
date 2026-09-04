# 得物:AI Native 交易核心系统的研发范式——Spec-Driven 五道关口

> **一句话摘要**:订单系统是交易核心,引入 AI Coding 后"代码产出又快又多"但质量不会自动跟上。得物把旧研发流水线重构成适配 AI 编码的五道标准化关口——需求澄清、技术方案、TDD 实施、门禁卡控、全流程埋点,让 AI 的产出变成**可验证、可度量、可负责**的研发生产方式。
>
> **来源**:微信公众号「得物技术」《AI Native 交易核心系统的研发范式》(作者:行亦),https://mp.weixin.qq.com/s/B29yrjptZiV4d_6cSskjmg;原始资料存档于 `docs/inbox/dewu-ai-native-source.md`

## 概念:核心系统为什么怕 AI Coding

得物订单系统此前已完成三阶段改造:①**筑牢稳定底线**(SLA 99.99%、杜绝跌单、三级保障规范);②**剥离核心链路**(以支付节点为分界,独立拆分订单创建/支付回调并专属保障);③**模块化重构链路**(按业务语义重构执行序列、配齐全链路埋点)。

这三阶段解决了稳定性、扩展性、可观测性,但 AI Coding 普及带来**全新的五类挑战**:

| 挑战 | 表现 |
| --- | --- |
| **错误模式迁移** | 从"个人手误"转向"系统性偏差"——AI 倾向复用历史模式,错误被批量复制 |
| **知识结构化压力** | 约束规约散落各处时,AI 等于"看不见"团队积累的知识 |
| **代码量与审查力失衡** | 变更量是之前数倍,CR 资源不同步增加,缺陷逃逸风险放大 |
| **故障回溯难** | 人 + AI 协同完成的代码,事后难定位根因(知识库/skill/规约/prompt 哪一步出错) |
| **单点提效,链路熵增** | 编码变快但前后步骤没变快,阶段间信息折损变大,整条链路熵在增加 |

!!! tip "核心洞察"
    问题不在 AI 不会写代码,而在**旧流程没有给 AI 准备"可执行的输入和可验证的出口"**——旧流程是为人理解人设计的。**要重新设计的不是 AI,而是它工作的流水线。**

## 原理:五道标准化关口

得物用 Claude Code 的 **Spec-Driven 开发插件**把研发流水线串成五道关口,整体采用五层自底向上架构:

```
治理层   : 核心治理能力内嵌(spec/code/arch/BDD 四维并行审查)
度量层   : 全链路可观测,量化采集/分析/报告/可视化
开发流程层: 五阶段核心研发流程
Agent 系统层: 设计 Agent、意图工程、上下文工程(链式调用→并行协作→反馈修正→结果汇总)
基础设施层: 统一埋点定义 + 阶段性产出规范(双层采集:Hook 自动层 + SKILL 显式层)
```

### 关口 1:需求澄清——保证方向不错

这一阶段**不产出代码,甚至不讨论代码**,只做一件事:让业务意图被精确地、结构化地记录。四个关键机制:

- **BDD 场景驱动验收**:用 Gherkin 场景(Given-When-Then)钉死"算什么、什么情况算错了要阻断"。例如出海礼品卡:"Given 出海下单选礼品卡支付,面值 100 元 + 出海服务费 10 元,When 用户确认订单,Then 礼品卡金额 = 110 元";异常边界:"金额异常时阻断并提示,不创建异常金额订单";优先级标定 P0 必须通过才能发布。后续 `bdd-acceptance` agent 把每条 Gherkin 场景**一对一映射**到 TDD 用例——需求、测试、实现三者一一对齐,验收标准从起点就是机器可读、可执行的;
- **统一模板,禁止技术语言**:Spec 固定六节(文档基本信息 / 业务目标与用户价值 / 核心业务流程 / 边界条件与异常场景 / 业务规则与协作边界 / 优先级与验收方法),每节强制业务语言,字段类型、表结构、接口签名一律不写(那是 tech-design 的事)。模板由独立子 Agent 渲染、不注入主会话上下文;
- **知识库现状对齐**:开始前自动拉取"现状分析报告"(知识库 + 代码现状),避免 AI"凭印象描述现状"、避免新能力与已有逻辑撞车、让每个判断可溯源;
- **提问管理**:按"该问 / 不该问 / 可跳过"三类管理提问,把"该问的问清楚"。

### 关口 2:技术方案设计——编码前锁定所有设计决策

核心思想:**不让 AI 在编码时临场发挥**。两个动作:

- **自上而下的模块拆解**:解析服务清单 → 逐服务拆到模块粒度,每个场景固定五段式(目标 / 变更位置 / 字段配置变更 / 构建处理逻辑 / 阻断兜底行为)+ 异常与边界 + 新增清单 + 上下游协作表;
- **知识库模块规约拉取**:命中的约束逐条让用户选"纳入"或"明确排除"(排除必须填理由,门禁阶段强制复查)。纳入的约束像影子跟到编码与门禁阶段——**"入口拉了哪些规约,出口就查哪些规约"**,形成完整证据链。CLI 不可用时降级跳过并在产物中明确标注,不静默漏过。

统一技术方案模板五大章节固定顺序(业务用例分析 → 整体架构 → 场景详细设计 → 数据结构设计 → 稳定性设计),稳定性设计按**可灰度 / 可监控 / 可回滚**三维度展开,弱依赖模块补全熔断、降级链路。

### 关口 3:编码执行 TDD——AI 的"完成"必须是测试通过

- **任务拆分(write-plan)**:技术方案拆成可独立验证的任务列表,三个硬约束——足够小可独立完成、有明确 RED/GREEN 验证点、可独立回退。把"写一段大代码"变成"完成 N 个小任务";
- **架构预检(入口)**:编码前先卡分层越界、依赖方向反转、模块边界穿透——**"事前防"比"事后查"成本低得多**;
- **RED-GREEN 循环**:先写失败的测试(RED)→ 实现让测试通过(GREEN)→ 重构(REFACTOR)。出海礼品卡案例:先写"100 + 10 = 110"的测试,再实现 `GiftCardCalculator.calcAmount`,最后把算法抽成公共方法让确认订单和创建订单复用同一份。

!!! warning "为什么 AI 时代 TDD 格外重要"
    AI 写代码最大的问题不是写不出来,而是**太自信**——会在没有测试的情况下写一段看起来合理的实现,然后自信地说"完成了"。TDD 的价值在于:先有一个失败的测试摆在那里,AI 必须让测试通过——**没有 TDD,AI 的"完成"是主观判断;有了 TDD,AI 的"完成"是测试通过——客观、可验证、不可糊弄。**

### 关口 4:门禁卡控——机器判定为主,人工决策为辅

门禁不是只在最后,而是**每个阶段产物落地时都有对应审核 Agent**,gate-check 是最终汇总。四个核心原则:

1. **机器判定为主**:每个审核 Agent 输出结构化 JSON,门禁读 JSON 判 PASS/FAIL,**不靠 LLM 主观总结**;
2. **人工决策为辅**:只有关键决策点(回退方向、排除规约的理由)才需要人确认;
3. **结论落本地磁盘,数据可回溯**:每一步都有结构化证据;
4. **失败回退到具体阶段**:门禁 FAIL 不是简单打回重来,而是定位到具体阶段、具体问题。

典型审核 Agent(出海礼品卡案例):

| 审核 Agent | 检查什么 | FAIL 条件示例 |
| --- | --- | --- |
| `invariant-reviewer` | 技术方案"纳入"的跨环节约束是否同步落实 | "确认订单和创建订单都要算礼品卡金额"两处调用点只改一处 |
| `delta-guard` | 增量代码的登记与降级 | 新增的外部调用(出海服务费查询)未登记、无降级 |
| `bdd-acceptance` | Gherkin 场景 ↔ 测试一一对应 | "礼品卡 = 110 元""金额 ≤ 0 阻断"两条场景没有对应测试或未通过 |

门禁检查采用**三层 DAG 结构:层内并行、层间串行**;另有增量代码体检工具(9 维度扫描:新增外部调用、新线程池、错误码重复、关键调用链节点变动等),纯文本扫描 60 秒超时、秒级返回、三级兜底,结果整理成飞书报告发到项目知识库。

### 关口 5:全流程埋点监控——把研发过程变成数据

前四道关口是"闸门",这一道是"仪表盘":这次需求花了多少人力、哪个阶段最耗时、知识库调用成功率、门禁通过率、回退两次根因是需求没写清还是方案漏了。看板分三层从需求到代码逐层下钻,按五个维度观察,三个典型改进场景:

- **知识库补充**:知识库调用成功率低 + 引用条目少 + 用户问答多 → 高频问题清单就是知识库该补充的内容清单;
- **流程优化**:耗时高 + 对话轮数异常高 → 是流程设计问题,不是模型慢;
- **子代理与工具调用收敛**:从"谁在白干"里找哪里该收敛。

## 代码 / 实现:门禁判定器(机器判定 PASS/FAIL)

门禁核心是"审核 Agent 输出结构化 JSON,门禁读 JSON 判 PASS/FAIL,失败定位到具体阶段"。纯 Python 演示:

```python
# 门禁判定器:读取各阶段产物 JSON,机器判定 + 失败定位到具体阶段
def gate_check(artifacts: dict) -> dict:
    """artifacts: {阶段名: {检查项: {"status": "pass"|"fail", "detail": str}}}"""
    results = {}
    for stage, checks in artifacts.items():
        failed = [name for name, c in checks.items() if c["status"] != "pass"]
        results[stage] = {
            "verdict": "FAIL" if failed else "PASS",
            "failed_items": failed,
        }
    # 汇总判定:任一阶段 FAIL 则整体 FAIL,并给出回退目标
    overall = all(r["verdict"] == "PASS" for r in results.values())
    if not overall:
        first_fail = next(s for s, r in results.items() if r["verdict"] == "FAIL")
        return {"overall": "FAIL", "rollback_to": first_fail, "details": results}
    return {"overall": "PASS", "rollback_to": None, "details": results}

def invariant_reviewer(call_sites_updated: dict, required_invariants: list) -> dict:
    """invariant-reviewer:跨环节约束检查(如'两处调用点算法必须一致')"""
    return {inv: {"status": "pass" if call_sites_updated.get(inv) else "fail",
                  "detail": f"约束「{inv}」调用点是否全部同步更新"} for inv in required_invariants}

# —— 演练:出海礼品卡 ——
artifacts = {
    "requirement":  {"spec_complete": {"status": "pass", "detail": "Gherkin 场景 P0 已标定"},
                     "p0_scenarios": {"status": "pass", "detail": "2 条 P0 场景齐备"}},
    "tech_design":  {"five_sections": {"status": "pass", "detail": "五段式+稳定性三维度齐备"},
                     **invariant_reviewer(
                         {"确认订单算礼品卡金额": True, "创建订单算礼品卡金额": True},
                         ["确认订单算礼品卡金额", "创建订单算礼品卡金额"])},
    "coding":       {"red_green": {"status": "pass", "detail": "GiftCardCalculator 测试通过"},
                     "architecture_precheck": {"status": "pass", "detail": "无分层越界/依赖反转"}},
    "gate":         {"delta_guard": {"status": "fail", "detail": "新增出海服务费外部调用未登记降级"}},
}
print(gate_check(artifacts))
```

运行结果:

```text
{'overall': 'FAIL', 'rollback_to': 'gate', 'details': {...'gate': {'verdict': 'FAIL', 'failed_items': ['delta_guard']}...}}
```

失败精确回退到 `gate` 阶段的 `delta_guard` 检查项——不是笼统的"打回重来",而是"这一条没降级,补上再进"。

## 实践 / 应用:落地要点与可迁移经验

**对任何想在企业核心系统引入 AI Coding 的团队**:

1. **先给 AI 准备"可执行的输入"**:需求必须结构化到机器可读(BDD/Gherkin + 六节模板),否则 AI 只能"猜";
2. **知识库是事实底座**:把分散的规约、约束收进知识库,需求/方案阶段主动拉取"现状分析报告",让 AI 基于事实而非印象;
3. **设计决策在编码前锁死**:五段式 + 统一模板 + 约束纳入/排除机制(排除必填理由),堵住"临场发挥";
4. **TDD 是唯一的客观验收**:RED→GREEN→REFACTOR,每个任务可独立验证、可独立回退;
5. **门禁机器判定**:审核 Agent 输出 JSON、门禁读 JSON 判 PASS/FAIL,失败定位到具体阶段;人工只在关键决策点介入;
6. **埋点驱动改进**:知识库补充、流程优化、子代理收敛三个场景都要有指标支撑,否则优化靠感觉。

!!! tip "与站内其他文章的呼应"
    五道关口的"可执行输入 + 可验证出口"正是 [AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 强调的系统显式化;[企业 Agent 工程化(二)](../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md) 的"失败处理写在出错之前"在本案例落地为门禁 FAIL 回退到具体阶段;Superpowers 的"双审查合并/计划预检"([Skill 收藏](../07-agent-coding/skills/mattpocock-skills.md))与这里的预检、审核 JSON 化异曲同工。

## 总结

- **五道关口**:需求澄清(BDD 钉验收)→ 技术方案(五段式锁设计)→ TDD 实施(RED-GREEN 客观完成)→ 门禁卡控(JSON 机器判定)→ 埋点监控(数据驱动改进);
- **核心原则**:AI 的"完成"必须是测试通过;审核以机器判定为主、人工决策为辅;失败精确回退到具体阶段;每步留结构化证据;
- **范式提炼**:AI Native 研发 = **可验证、可度量、可负责**——模型能力是变量,流程设计是常数;变量决定上限,常数决定底线。交易核心系统的底线,不能交给变量。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/B29yrjptZiV4d_6cSskjmg(得物技术,作者:行亦);原始资料存档于 `docs/inbox/dewu-ai-native-source.md`
- 站内:[企业 Agent 工程化系列](../06-enterprise/ontology-agent-adoption/index.md)(异常恢复/门禁/可观测)、[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)、[Agent 是任务执行系统](../06-enterprise/ontology-agent-adoption/agent-as-task-execution-system.md)、[Agent 安全审计实战](agent-security-audit-practice.md)
- 概念延伸:TDD(Beck)、BDD(Gherkin Given-When-Then)、Spec-Driven Development(得物 Claude Code 插件实践)
