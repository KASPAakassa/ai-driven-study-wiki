# OpenAI 长时 agent 三件套:Skills + hosted Shell + Compaction

> **一句话摘要**:OpenAI 官方给"真正干活的长时 agent"的三件套:**Skills**(SKILL.md 可复用程序)、**hosted shell**(托管容器环境)、**server-side compaction**(服务端自动上下文压缩)。核心技巧:skill description 写成路由逻辑而非营销文案(缺负例时 Glean 触发率掉 ~20%)、模板示例放 skill 内而非 system prompt、确定性优先(显式 "Use the `<skill>` skill")、安全上双层 allowlist + domain_secrets、`/mnt/data` 作为产物交接边界。
>
> **来源**:OpenAI《Shell + Skills + Compaction: Tips for long-running agents that do real work》(https://developers.openai.com/blog/skills-shell-tips)

## 概念

### 三件套

| 组件 | 作用 |
| --- | --- |
| **Skills** | SKILL.md + frontmatter 的可复用程序(agent 的"能力包") |
| **Hosted shell** | OpenAI 托管容器:隔离、可执行、产物持久 |
| **Server-side compaction** | 上下文自动压缩(服务端);`/responses/compact` 亦可手动 |

三者解决长时 agent 的三个问题:能力复用、执行环境、上下文无限膨胀。

## 原理(可执行技巧)

### 1. Skill description 是路由逻辑,不是营销文案

- 写 **"Use when vs. don't use when"**(何时用/何时不用),而非夸夸其谈;
- **负例 + 边界案例防止误触发**:Glean 实测缺负例时**触发率掉 ~20%**。

### 2. 模板/示例放 skill 内,不放 system prompt

- 命中 skill 才加载模板/示例,**不膨胀无关 token**;
- Glean 因此获得**最大质量/延迟收益**(对比放 system prompt)。

### 3. 确定性优先

- 直接说 **"Use the `<skill>` skill"**,把模糊路由变成显式契约——不让模型自由发挥"选哪个能力"。

### 4. 安全(open skills + 网络 = 高风险)

- **org 级 + request 级双层 allowlist**(组织白名单 + 单次请求白名单);
- **domain_secrets**:防凭据泄漏(禁止 skill 输出/访问密钥);
- 假设**工具输出不可信**(agent 看到的网络内容可能被注入)。

### 5. /mnt/data:产物交接边界

- **"工具写盘、模型读盘、开发者取盘"**:产物落在 `/mnt/data`,作为 agent 与开发者的交接面;会话结束产物不丢。

### 6. 三个组合模式

1. `install → fetch → 写产物`:固定流程的完整闭环;
2. **skill + shell 固化流程**:把反复操作沉淀成可复用程序;
3. **skill 作企业 SOP 载体**:Glean 的 Salesforce skill 用 eval 迭代——**准确率 73%→85%、TTFT -18.1%**。

## 代码 / 实现

```markdown
---
name: process-salesforce-record
description: |
  处理 Salesforce 记录。Use when:用户要更新/查询 Salesforce 记录;
  Don't use when:与 Salesforce 无关的数据操作。
  (负例 + 边界:避免误触发)
---
# 使用步骤
1. 读 /mnt/data/input.csv
2. 调用 <salesforce skill 内脚本> 处理
3. 结果写 /mnt/data/output.csv
```

```bash
# hosted shell 内执行,产物持久在 /mnt/data
curl .../responses -d '{"model":"gpt-5.6","tools":[{"type":"function",...}],"input":"..."}'
# server-side compaction 自动触发;手动: POST /responses/compact
```

## 实践 / 应用

- **设计 skill**:description 用路由逻辑(Use when/Don't use when + 负例);模板示例放 skill 内;
- **显式路由**:prompt 里直接说 "Use the `<skill>` skill";
- **安全底线**:双层 allowlist、domain_secrets 防泄漏、不信任工具输出;
- **交接**:产物统一落 `/mnt/data`;长会话靠 server-side compaction 防膨胀;
- **固化**:用 eval 迭代 skill(见 [skill-evaluation.md](../07-agent-coding/skills/skill-evaluation.md) 的 OpenAI evals 方法),像 Glean 一样量化提升;
- 与 Anthropic 的长时方案对比:

| 维度 | OpenAI(本文) | Anthropic([长时 harness](agent-harness-long-running.md)) |
| --- | --- | --- |
| 跨窗口记忆 | server-side compaction(服务端压缩) | 文件系统三件套(init.sh/progress/feature_list) |
| 环境 | hosted shell 托管容器 | 本地 + init.sh 冒烟 |
| 能力复用 | Skills + 双层 allowlist | SKILL.md + 测试保护 |

## 总结

1. **三件套**:Skills(能力复用)+ hosted shell(执行环境)+ server-side compaction(上下文治理)。
2. **Skill description 是路由逻辑**:Use when/Don't use when + 负例——缺负例 Glean 触发率掉 ~20%。
3. **模板放 skill 内而非 system prompt**:命中才加载,不膨胀 token;确定性优先显式路由。
4. **安全**:org+request 双层 allowlist、domain_secrets 防泄漏、不信任工具输出。
5. **/mnt/data 交接**:工具写盘、模型读盘、开发者取盘;skill 作 SOP 载体(eval 迭代 73%→85%)。

**下一步学什么**:对比 [Anthropic 长时 harness](agent-harness-long-running.md)(两种跨窗口方案);Skill 设计细节见 [Agent Skills 设计理念](../07-agent-coding/skills/agent-skills-design.md);评测见 [Skill 测评(OpenAI evals 方法)](../07-agent-coding/skills/skill-evaluation.md)。

## 延伸阅读

- 站内:[Anthropic 长时 harness](agent-harness-long-running.md)、[Agent Skills 设计理念](../07-agent-coding/skills/agent-skills-design.md)、[Skill 测评](../07-agent-coding/skills/skill-evaluation.md)、[OpenAI Harness Engineering](../07-agent-coding/experience/openai-harness-engineering.md)、[Vibe Coding 最佳实践](../07-agent-coding/experience/vibe-coding-engineering-practice.md)
- 外部:原文(https://developers.openai.com/blog/skills-shell-tips)
