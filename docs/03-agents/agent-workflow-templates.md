# 10 个 AI Agent 工作流模板:把重复工作重新设计成可复用系统

> **一句话摘要**:AI agent 比聊天机器人强在"完成一整条工作流"而非只回答。本文给出 10 个可直接套用的业务 Agent 工作流模板(收件箱/研究简报/表单填写/会议行动项/客服分类/内容再利用/竞品监控/发票核对/CRM 补全/QA 审查),每个模板带触发条件、步骤、决策规则与人工检查点的 JSON 骨架,以及通用设计原则——**Prompt 是临时的,工作流模板是持久的**。
>
> **来源**:数据派THU《10个AI Agent工作流,帮团队省出大量重复工作时间》(原 by EasyClaw,https://mp.weixin.qq.com/s/oRKEWMLxRf1gKvbxdLbFrw)

## 概念

### Agent 工作流 vs 聊天机器人

聊天机器人只负责回答;agent 会完成**一整条工作流**:读取信息、核对、比较、决策、起草、更新,**风险太高时才停下来请人拍板**。常见错误是把 AI agent 当成更聪明的 Prompt 输入框——让它"处理客户支持"或"做研究",结果自然不可靠,然后失望。**工具选型应该排在工作流设计之后。**

### 通用五部分框架

一个可用的 agent 工作流通常包含五个部分(Anthropic 观点:最好的实现是简单、可组合的模式,而非过度设计的框架):

| 部分 | 作用 |
| --- | --- |
| **Trigger(触发条件)** | 什么事件启动(新邮件/新发票/定时/页面变化) |
| **Context(上下文)** | agent 需要的输入与背景(源数据/历史记录) |
| **Tools(工具)** | 读取、执行、浏览器等能力 |
| **Decision rule(决策规则)** | 什么情况执行、什么情况升级 |
| **Human checkpoint(人工检查点)** | 高风险动作前停下来等人批准 |

**基本结构**:

```
Trigger → Collect context → Use tools/browser → Apply decision rules
  → {Risk level?} Low → Execute or draft / High → Ask human for approval
  → Log result(审计轨迹)
```

**最后一步是审计轨迹(audit trail)**——留不下这个记录,agent 就还称不上能承担正式工作。

## 原理(10 个模板)

### 1. 收件箱分类与回复

扫描新邮件 → 按意图分类 → 判断是否需要回复 → 用你的语气草拟回复;**不自动发送**,只准备好放在那儿。价值不在于回复写得完美,而在于**不用从一片空白打开每一封邮件**。

```json
{
  "trigger": "new_email",
  "steps": ["classify intent", "detect urgency", "search previous related emails",
            "draft reply", "mark as needs_review or no_action"],
  "human_review_required": true
}
```

### 2. 研究简报生成器

研究是一条链:搜索、筛选、比较、总结、提取来源、整理成可看的东西。**来源规范性是关键**——cite every factual claim、分离确认事实与推断、标记过期来源。市场调研/合规检查/供应商比较/技术尽调/政策跟踪通用;还省掉隐蔽成本:上周研究没留结构,这周同主题又搜一遍。

```json
{
  "sections": ["short answer", "source-backed findings", "what changed recently",
               "risks or uncertainties", "recommended next actions"],
  "rules": ["cite every factual claim", "separate confirmed facts from inference",
            "flag outdated sources"]
}
```

### 3. 浏览器表单填写

很多重复工作流发生在**没有干净 API 的网站**(供应商门户、商品列表、招聘网站、合规表单、物流仪表盘、内部后台)。步骤:从表格/CRM 加载源数据 → 打开目标网站 → 字段与源数据匹配 → 填写 → 截图或摘要 → **最终提交前等批准**。上传商品列表场景:只填标题/描述/图片/尺寸/SKU/分类,在最终审核页停住,不让 agent 自动发布一切。

### 4. 会议记录转行动清单

有用的会议记录是把讨论直接转成**责任归属**:读取转录 → 提取决策 → 识别行动项 → 有提到负责人就分配、没提到就标记(不猜)。输出格式:

```
## Decisions
- Decision: - Context: - Owner: - Deadline:
## Action Items
- Task: - Owner: - Due date: - Dependency: - Confidence:
## Open Questions
- Question: - Who needs to answer:
```

重点不是记录写得好,是**承诺少被落下几个**。

### 5. 客户支持分类

AI agent 不该扮演资深支持经理,它最擅长**第一层工作**:分类、检索上下文、起草、路由、升级。四件事:识别问题类型、查客户历史、给解决方案建议、判断是否需人工介入。优先级规则示例:

```json
{
  "priority_rules": {
    "refund_request": "human_review",
    "technical_bug": "route_to_support_engineer",
    "shipping_status": "draft_response",
    "angry_customer": "human_review"
  }
}
```

助手与 agent 的差别:助手只能回答一个问题;agent 能查订单系统、翻对话记录、起草回复、打标签、准备下一步。

### 6. 内容再利用

把一篇长文章拆成 LinkedIn 帖子、X 线程、通讯简报导语、短视频脚本、图片 Prompt、SEO 摘要。**没有质量把关产出会很平庸**——preserve original thesis、remove generic AI phrases、keep examples concrete、avoid unsupported claims。关键:**适配渠道特性**(LinkedIn 浏览式阅读、简报要上下文、短视频要更犀利的钩子),不是单纯"总结"。

### 7. 竞品与定价监控

按计划检查竞品页面/商品列表/更新日志/公开定价页,**记录变化并总结重要性**——抓取所有内容不是重点,检测出有意义的变化才是。报告格式:Change detected / Old value / New value / Possible impact / Recommended action / Evidence(screenshot+URL)。被动监控变成运营节奏。

### 8. 发票与费用核对

财务工作流重复、规则化、例外多——**适合协助,不适合完全交给它做主**。读发票与 PO 比对、核对供应商名、比较金额、检测重复项、标出不匹配;付款依然人来批。决策规则是核心:

```json
{
  "auto_clear_if": ["vendor matches approved list", "amount matches PO within tolerance",
                    "no duplicate invoice number", "payment terms are standard"],
  "escalate_if": ["new vendor", "bank details changed", "amount mismatch", "missing tax information"]
}
```

减少审核工作量,但**不能让它悄悄批掉有风险的付款**——这是负责任的 agent 设计该有的样子。

### 9. CRM 信息补全与跟进

通话/邮件/演示/LinkedIn 互动后更新 CRM 是销售团队的时间黑洞。agent 收集公司信息、总结近期对话、给交易阶段建议、起草跟进邮件、创建提醒。**关键:别把每个信号当板上钉钉的事实**——输出带 Confidence + Evidence:

```
Suggested deal stage: Evaluation   Confidence: Medium
Evidence: - Prospect requested pricing - Demo completed - No procurement timeline confirmed
Recommended next step: - Send pricing summary and ask about decision process
```

CRM 更有用又不至于凭空捏造:**agent 负责提议,销售负责拍板**。

### 10. 重复性数字工作的 QA 审查

业务问题常是小地方漏了:失效链接、名字打错、价格不一致、alt 缺失、日期错误、文件版本对不上、格式跑偏。QA agent 发布前检查页面/文档/表格/商品列表,对照清单**只挑需要处理的**:

```json
{
  "checks": ["all buttons have valid links", "no placeholder text remains",
             "images include alt text", "pricing is consistent",
             "mobile layout is readable", "schema fields are present"]
}
```

不光是这活儿不鲜,而是**重复性 QA 恰好是 agent 能省注意力、又不夺走人主导权的地方**。

## 代码 / 实现

以上每个模板都是三层结构,可直接落地:

- **触发器**:事件驱动(新邮件/发票/定时任务/页面变更检测);
- **执行链**:步骤列表(分类→检索→草拟→标记)或工具链(浏览器表单/API/CRM);
- **决策与人工闸门**:`auto_clear_if` / `escalate_if` / `human_review_required` / `priority_rules` 四类规则,加上**风险分级**(Low 执行或草拟 / High 请人批准)与**审计轨迹**。

**落地建议**:从第 1 条(收件箱)或第 10 条(QA)这类低风险、边界清晰的工作流起步;把 trigger、tools、decision rules、review points、output format 定义清楚后,同一个 agent 能一遍遍跑下去,越改越顺手、越来越好审计。

## 实践 / 应用

### 十个模板速查

| # | 工作流 | 适用团队 | 人工检查点位置 |
| --- | --- | --- | --- |
| 1 | 收件箱分类与回复 | 通用 | 回复不自动发送 |
| 2 | 研究简报生成器 | 市场/合规/尽调 | 来源规范性规则 |
| 3 | 浏览器表单填写 | 电商/供应商/招聘 | 最终提交前等批准 |
| 4 | 会议记录转行动清单 | 产品/运营/管理 | 未提到负责人就标记 |
| 5 | 客户支持分类 | 客服 | refund/angry → human |
| 6 | 内容再利用 | 市场/内容 | 质量检查清单 |
| 7 | 竞品与定价监控 | SaaS/电商/代理 | 变化摘要给人看 |
| 8 | 发票与费用核对 | 财务 | 付款人来批 |
| 9 | CRM 补全与跟进 | 销售 | 交易阶段由人拍板 |
| 10 | 数字工作 QA 审查 | 通用/发布 | 只挑问题不自动修 |

### 与站内理论的对应

- **五部分框架**(trigger/context/tools/decision rule/human checkpoint)→ 对应 [Agent 规划与工作流模式](agent-planning-patterns.md) 的"工作流四模式"理论层:本文是**具体模板实例**,那篇是**抽象模式**;
- **风险分级 + 人工检查点** → 呼应 [Agentic Abstention](agentic-abstention.md)(何时该停)与 [Gate 模式](../07-agent-coding/experience/gate-pattern.md)(人工确认点);
- **审计轨迹** → 呼应 [WorkBuddy Bench](workbuddy-bench.md)(完成由什么证明)与 [Agent 效果优化实战](../04-practice/agent-effect-optimization-practice.md)(证据可回查);
- **决策规则显式化**(auto_clear/escalate 四类)→ 呼应 [Agent 业务理解](agent-business-understanding.md) 的"决策记录"与 [Agent 系统设计的 5 个决策](agent-system-5-decisions.md)。

### 设计要点

1. 工作流设计先于工具选型;2. 触发条件、工具、规则、审核点、输出格式一次定义清楚;3. 高风险动作必有**人工检查点**,低风险自动执行;4. **留审计轨迹**才配承担正式工作;5. 从低风险、边界清晰的工作流起步(Prompt 是临时的,工作流模板是持久的)。

## 总结

1. **Agent 的定位是"完成工作流"而非"回答问题"**:读取→核对→比较→决策→起草→更新,风险高才请人拍板。
2. **五部分框架是通用骨架**:trigger / context / tools / decision rule / human checkpoint + 审计轨迹。
3. **10 个模板覆盖高频重复工作**:收件箱/研究/表单/会议/客服/内容/竞品/发票/CRM/QA,每个都是"触发器+执行链+决策闸门"三层结构。
4. **负责任的设计**:付款、发布、退款等高风险动作留人工闸门;提议与拍板分离(agent 提议、人拍板);决策规则显式化而非临场发挥。
5. **可复用是核心价值**:定义好五要素后同一工作流可反复跑、可审计、可解释——效率来自把重复工作重新设计成系统。

**下一步学什么**:读 [Agent 规划与工作流模式](agent-planning-patterns.md)(理论模式)与 [Agent 意图识别](agent-intent-recognition.md)(分类路由);想动手就选第 1 或第 10 条落地,再看 [Agent 评测](agent-evaluation.md) 建立验证。

## 延伸阅读

- 站内:[Agent 规划与工作流模式](agent-planning-patterns.md)、[Agent 意图识别](agent-intent-recognition.md)、[Agentic Abstention](agentic-abstention.md)、[WorkBuddy Bench](workbuddy-bench.md)、[Gate 模式](../07-agent-coding/experience/gate-pattern.md)、[Agent 业务理解](agent-business-understanding.md)、[Agent 系统设计的 5 个决策](agent-system-5-decisions.md)、[Agent 效果优化实战](../04-practice/agent-effect-optimization-practice.md)
- 外部:原文(https://mp.weixin.qq.com/s/oRKEWMLxRf1gKvbxdLbFrw);观点出处原文见站内 [Building effective agents:workflow 与 agent 的五种模式](agent-building-effective-agents.md)
