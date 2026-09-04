# AutoGen:多智能体协作框架——GroupChat 与发言者策略

> **一句话摘要**:AutoGen 是微软开源的多智能体对话框架——核心理念是让 Agent 之间通过**自然语言对话**协作(而非硬编码函数调用),用 `GroupChat` 容器把多个角色 Agent 放进同一对话,配合 `round_robin/random/auto/自定义` 四种发言者选择策略完成分工。⚠️ 微软已将其置为维护模式,新项目推荐迁移到 Agent Framework。
>
> **来源**:微信公众号《2026年AI Agent构建指南:框架选型与工程实践》(刘律辰),https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg;官方文档 https://microsoft.github.io/autogen

## 概念

**定位**:多 Agent 协作框架——用于构建多个 AI Agent 协作完成复杂任务,让 Agent 之间通过自然语言对话协作,而非硬编码函数调用。

**选 AutoGen 的场景**:任务太复杂,一个人(Agent)干不完,需要团队(多角色)吵架/协作才能出结果。

!!! warning "AutoGen 已进入维护模式"
    2025 年 10 月起,微软将 AutoGen 置为**维护模式**——仅修漏洞,不再新增功能;所有新特性都做到 Agent Framework 上。官方文档明确把 [Agent Framework](microsoft-agent-framework.md) 称为下一代 Semantic Kernel 与 AutoGen,鼓励新项目直接迁移。

## 原理:Agent 与 GroupChat

### Agent 基本单元

每个 Agent 具备四个属性:

| 属性 | 说明 |
| --- | --- |
| `name` | Agent 名称标识,对话中用于区分发言者 |
| `system_message` | 角色设定/提示词,定义 Agent 职责和行为方式 |
| `llm_config` | LLM 配置(模型、API Key、温度等) |
| `tools` | 可调用的外部工具函数,扩展 Agent 能力 |

**常用 Agent 类型**:

| 类型 | 用途 | 特点 |
| --- | --- | --- |
| `ConversableAgent` | 基础对话 Agent | 最灵活,可完全自定义 |
| `AssistantAgent` | 助手 Agent | 默认由 LLM 驱动,适合生成内容 |
| `UserProxyAgent` | 用户代理 | 可执行代码、调用工具、请求人工输入 |

### GroupChat 群聊

将多个 Agent 放在同一对话中协作的容器:

```python
from autogen import GroupChat, GroupChatManager

group_chat = GroupChat(
    agents=[
        self.data_agent,    # 1. 数据员先获取数据
        self.analyst_agent, # 2. 分析师进行分析
        self.risk_agent,    # 3. 风控官评估风险
        self.trader_agent   # 4. 交易员给出建议
    ],
    messages=[],
    max_round=8,                     # 4个Agent各发言1-2次
    speaker_selection_method="round_robin",
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=self.data_agent.llm_config,
)

result = self.data_agent.initiate_chat(
    manager,
    message="用户查询: 分析一下宁德时代能不能买",
)
```

**对话流程**:用户发起查询 → GroupChatManager 根据策略选择第一个发言 Agent → 被选中 Agent 生成回复(可能调用工具)→ 回复加入对话历史(所有 Agent 可见)→ Manager 选择下一个发言者 → 重复直到 max_round 或满足终止条件。

### 发言者选择策略

| 策略 | 说明 | 适用场景 |
| --- | --- | --- |
| `round_robin` | 按 agents 列表顺序轮流发言 | 流程明确的任务(数据→分析→风控→决策) |
| `random` | 随机选择下一个发言者 | 头脑风暴、创意讨论 |
| `auto` | 由 LLM 判断谁最适合回答 | 开放式讨论、问答场景 |
| 自定义函数 | 完全控制选择逻辑 | 复杂业务流程、条件分支 |

> **经验**:任务有明确执行顺序用 round_robin(投资委员会决策就是固定流程:先获取数据→分析→风控→决策);需要灵活讨论用 auto。

## 实践 / 应用:投资委员会案例

项目中使用 `ConversableAgent` 创建 4 个角色,区别在于是否注册工具函数:

- **data_agent(数据员)**:注册数据获取工具;
- **analyst_agent(分析师)**:分析数据;
- **risk_agent(风控官)**:评估风险;
- **trader_agent(交易员)**:给出建议。

用户问"宁德时代能不能买" → 数据员先拿数据 → 分析师分析 → 风控官评估 → 交易员建议,`round_robin` 保证固定流程顺序。

**记忆管理**:GroupChat 自动维护对话历史(messages 列表),所有 Agent 可见——多 Agent 场景的记忆由群聊容器统一管理,无需手动传入。

## 总结

- **定位**:多智能体对话协作框架——Agent 之间用自然语言对话而非硬编码调用;
- **Agent 四属性**:name / system_message / llm_config / tools;三种常用类型(ConversableAgent/AssistantAgent/UserProxyAgent);
- **GroupChat**:多 Agent 协作容器 + 四种发言者选择策略(round_robin/random/auto/自定义);
- **⚠️ 维护模式**:微软已停止新增功能,新项目迁移到 [Agent Framework](microsoft-agent-framework.md);
- **下一步**:对比 [AgentScope](agentscope-framework.md)(事件总线多智能体)与 [MAF](microsoft-agent-framework.md)(AutoGen 官方继任者)。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/NTvoC1GE3zuw6Dlo72FTOg;官方文档 https://microsoft.github.io/autogen
- 站内:[Agent 框架](agent-frameworks.md)(AutoGen 收录)、[Microsoft Agent Framework](microsoft-agent-framework.md)(AutoGen 继任者,双语言+企业级)、[AgentScope](agentscope-framework.md)(另一多智能体方案)、[Agent 框架七方对比](agent-frameworks-seven-comparison.md)
