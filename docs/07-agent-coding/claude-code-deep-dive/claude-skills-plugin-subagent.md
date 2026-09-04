# Claude Code Skills / Plugin / Subagent:扩展体系三件套

> **一句话摘要**:Claude 系统的扩展能力由三个互补模块构成:**Skills**(程序性知识,教 Claude 怎么做,渐进式披露、token 极省)、**Plugin**(打包分发,把 Skills+Commands+Subagents+Hooks+MCP 装进可安装单元)、**Subagents**(独立上下文的专职员工,任务委派与并行)。Simon Willison 评价 Skills"可能比 MCP 更重要"——本文拆解三者定位、用法与最佳实践。
>
> **来源**:Yu 的赛博工位笔记《Claude Skills 概念介绍/实践指南/Skill-Creator 解析》《Claude Code Plugin 概念介绍/实践指南》《Claude Code Subagent 概念介绍/实践指南》,https://yudesk.dev/docs/notes/claude-skills/concept、https://yudesk.dev/docs/notes/claude-plugin/concept、https://yudesk.dev/docs/notes/claude-subagent/concept;原始内容存档于 `docs/inbox/yudesk-claude-code/`

## 一、Skills:给 AI 助手的可重用工作手册

!!! tip "为什么被评价'可能比 MCP 更重要'"
    Simon Willison:"Claude Skills are awesome, maybe a bigger deal than MCP... I expect we'll see a Cambrian explosion in Skills which will make this year's MCP rush look pedestrian by comparison."——解决的核心痛点:**每次新对话都要重复输入相同的工作流程说明**。

### 定义与组成

Skills 是包含**指令、脚本和资源的文件夹**,Claude 按需动态加载,跨对话持久保存——"培训一次,之后无论何时都记得"。

| 组件 | 作用 | 是否必需 |
| --- | --- | --- |
| **SKILL.md** | 核心指令文档(YAML frontmatter + 正文) | 必需 |
| 参考资料 | 品牌指南、模板、政策文件 | 可选 |
| 脚本 | Python/JS 代码,处理复杂计算或文件操作 | 可选 |

SKILL.md 的 frontmatter 两个关键字段:`name`(≤64 字符)+ `description`(≤200 字符,**Claude 根据描述判断何时调用,写得越清晰准确,触发概率越高**)。

### 渐进式披露(核心架构)

```
📋 目录(元数据层)   启动时预加载,仅 30-50 tokens,所有 Skill 目录同时可见
📖 正文(核心文档层)  Claude 判断需要时才展开,数百-数千 tokens
📎 附录(引用资源层)  需要时加载
```

**传统 MCP 工具描述可能消耗数千甚至数万 token;Skills 元数据仅数十 token——可以同时启用大量 Skills 而不担心上下文被占满。**

### 与其他功能对比

| 维度 | Skills | MCP | Subagents | 斜杠命令 |
| --- | --- | --- | --- | --- |
| 核心 | 教 Claude 如何执行任务 | 连接外部系统 | 独立执行的子代理 | 手动触发的工作流 |
| Token | 极低(数十) | 较高(数千-数万) | — | — |
| 激活 | **自动匹配**(description) | 配置后可用 | 手动/自动委托 | 手动输入 |
| 形象 | 培训材料 | USB 接口 | 专职员工 | 快捷键 |

!!! tip "三者组合的经典用法"
    MCP 连接 CRM 获取客户数据 + Skills 定义如何分析生成报告 + Subagents 委托独立子任务——**互补而非替代**;代码审查 Subagent 可加载语言特定最佳实践 Skill("专家 + 专业知识")。

## 二、Plugin:打包分发的可安装单元

### 解决的问题

团队配置分散、难以共享标准化——每个人都有自己的一套 Skills/Commands/Hooks。**Plugin 将 Skills + Commands + Subagents + Hooks + MCP 打包为可安装单元,一键分发、团队标准化**。

### 目录结构与安装

```
my-plugin/
├── .claude-plugin/plugin.json   # 插件清单(必需)
├── commands/  agents/  skills/  hooks/  .mcp.json  README.md
# 安装
claude plugin install github:your-org/your-plugin   # 从 GitHub
claude plugin install /path/to/plugin               # 从本地
```

资源:claude-plugins-official(官方仓库)、wshobson/agents(⭐24.3k 高质量 Agent 模板)、Claude Plugin Hub(社区市场)、awesome-claude-code(⭐19.3k 精选资源)。

## 三、Subagents:独立上下文的专职员工

### 设计理念

单一 Agent 的挑战:上下文窗口有限、无法并行、职责不清。**Subagents 采用 Orchestrator-Worker 架构**:

```
Main Agent(Orchestrator)分析/计划/分解/生成专门化子代理
  → Sub 1(代码)/ Sub 2(测试)/ Sub 3(文档)并行执行(Workers)
  → 汇总结果 → 主代理综合输出
```

### 核心特性与数据

- 上下文隔离(避免污染)/ 任务专门化(自定义系统提示)/ 工具权限控制 / 并行执行;
- **性能数据:多代理系统比单代理高 90.2%,并行化削减研究时间 90%(token 约 15×,复杂任务值得)**;
- 配置:`~/.claude/agents/<name>.md`(frontmatter 定义 name/description/tools + 正文角色指令)。

## 代码 / 实现:三者的选型判断(纯 Python)

```python
# —— 扩展体系选型:什么时候用 Skills / MCP / Subagent ——
def choose_extension(task: dict) -> str:
    """按任务特征选择扩展:数据连接 → MCP;标准化流程 → Skills;独立子任务 → Subagent"""
    if task.get("needs_external"):
        return "MCP(连接外部数据/API)"
    if task.get("standardized") or task.get("repeatable"):
        return "Skills(教 Claude 怎么做,自动匹配)"
    if task.get("independent") and task.get("complex"):
        return "Subagent(委托独立执行,结果返回)"
    return "直接对话(不需要扩展)"

cases = [
    {"needs_external": True},                       # 查数据库
    {"repeatable": True, "standardized": True},     # 生成周报
    {"independent": True, "complex": True},         # 审查整个模块
    {},                                             # 简单问答
]
for c in cases:
    print(f"  {c} → {choose_extension(c)}")
```

## 实践 / 应用:最佳实践与知识库整合

### 三个最佳实践

1. **Skills**:description 写"做什么 + 什么时候用",保持简洁准确;复杂流程放 Instructions,示例放 Examples;把品牌规范/标准流程做成 Skill 跨对话复用;
2. **Plugin**:团队标准化用 Plugin 分发(版本化、一键安装);个人零散配置先用 Skills/Commands 收敛;
3. **Subagents**:每个子代理职责单一 + 工具权限最小化;并行任务(测试/文档/审查)拆给不同子代理;组合 Skills 提升子代理专业度。

### 与站内其他文章的呼应

- [Skill 收藏](../../07-agent-coding/skills/index.md):本站 Skills 收藏的官方概念篇;
- [四件套](../../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md):Skills 与 MCP 的分工(怎么做 vs 连什么)同源;
- [Superpowers v6](../../07-agent-coding/skills/mattpocock-skills.md):渐进式披露与"审查优化"的实践;
- [多智能体协作设计](../../03-agents/agent-team-room-collaboration.md):Subagents = Orchestrator-Worker 的官方形态;
- [Eval Engineering Skill](../../07-agent-coding/skills/eval-engineering-skill.md):Skill 化评估流程的实例。

## 总结

- **Skills**:程序性知识,渐进式披露(元数据 30-50 tokens),自动匹配激活——"教 Claude 怎么做";
- **Plugin**:打包分发单元(Skills+Commands+Subagents+Hooks+MCP),团队标准化;
- **Subagents**:独立上下文专职员工,Orchestrator-Worker 并行,性能 +90.2%;
- **一句话**:MCP 连数据(WHAT)、Skills 教方法(HOW)、Subagents 干独立活(WHO)、Plugin 打包分发(ALL)——四者互补,按需组合。

## 延伸阅读

- 原页面:https://yudesk.dev/docs/notes/claude-skills/concept、https://yudesk.dev/docs/notes/claude-plugin/concept、https://yudesk.dev/docs/notes/claude-subagent/concept
- 站内:[Claude Code 架构与工具系统](claude-architecture-tools.md)、[Worktree 与 Agent Teams](claude-worktree-teams.md)、[Claude Code 隐藏技巧](claude-code-tips.md)(本子主题其他篇);[四件套](../../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md)、[多智能体协作设计](../../03-agents/agent-team-room-collaboration.md)
