# 给 Coding Agent 立规矩的正确姿势:AGENTS.md / CLAUDE.md / .cursorrules 的正交关系

> **一句话摘要**:团队里有人用 Cursor、有人用 Claude Code、有人用 Codex CLI,同一 repo 的规则文件(AGENTS.md / CLAUDE.md / .cursorrules)到底谁管谁?答案是三者不是三选一,而是**三种正交能力**——用"一份源文件 + 两种消费方式"统一落地,并认清"规则不是越多越好、软约束需要硬拦截兜底"。
>
> **来源**:微信公众号《给 Coding Agent 立规矩的正确姿势》(图片版文章,基于官方摘要整理),https://mp.weixin.qq.com/s/YkgkhSBCZw5tz7TpF7U8Rw

## 概念:问题从哪来

**场景**:team 里三个人分别用 **Cursor、Claude Code、Codex CLI**,同一个 repo 跑出来的 PR 风格越来越乱——命名不一致、测试写不写全看心情。想统一规则,翻一圈却发现 **AGENTS.md / CLAUDE.md / .cursorrules** 到底谁管谁、优先级是什么,根本没人说得清。

**核心洞察**:把三份官方文档和几十个开源项目过一遍之后,结论是——**它们不是三选一,而是三种正交能力**,各自解决不同的问题。

## 原理:三种规则文件的正交定位

| 文件 | 定位 | 关键能力 |
| --- | --- | --- |
| **AGENTS.md** | 最大公约数(标准) | OpenAI 主导、**Linux Foundation 维护**;20+ 工具原生支持、60000+ 项目采用;跨工具统一的入口 |
| **CLAUDE.md** | 作用域分层 + 引入语法 | 多了一层 **Managed → User → Project → Local** 作用域分层;支持 **`@import`** 语法引用其他文件 |
| **.cursor/rules/\*.mdc** | 精细激活 | 支持 **glob 模式**按文件路径/类型精确激活规则 |

三者是**正交**的:AGENTS.md 解决"标准统一",CLAUDE.md 解决"分层与引入",`.cursor/rules` 解决"按场景精确激活"——它们不冲突,只是能力维度不同。

## 工程解法:一份源文件,三种消费

正确的落地方式不是维护三份文件,而是:

```
repo/
├── AGENTS.md          ← 唯一源文件(全量规则,团队 review 只盯这一份)
├── CLAUDE.md          ← 只写一行:@AGENTS.md(引入源文件,不复制内容)
└── .cursor/
    └── rules/         ← 只有需要 glob 精细激活的规则才拆到这里
```

```markdown
<!-- CLAUDE.md 全部内容(演示) -->
@AGENTS.md
```

**要点**:

1. 根目录写一份 **AGENTS.md 作为源文件**,承载团队统一规则;
2. **CLAUDE.md 只用一行 `@AGENTS.md` 引入**——借助 `@import` 语法消费同一份内容;
3. 只有需要 **glob 精细激活**的规则(如"仅对 `tests/**` 生效的测试规范")才拆到 `.cursor/rules/`;
4. 结果:**一份内容三消费**——不用维护三份、更不用担心不同步,团队 code review 只需盯一个文件。

!!! tip "为什么这样设计"
    维护多份拷贝必然漂移;用"源文件 + 引入/激活"把三份工具各自的特性用起来,既统一又保留各工具的独特能力。

## 反直觉的洞察:规则不是越多越好

越短的规则越有效:

- **Claude 官方文档明写**:CLAUDE.md 越简短越有效,**超过 200 行就掉遵循度**;
- **Cursor 的 `alwaysApply` 超过 2 条就会显著吃 context**,模型开始输出"同时满足所有规则的平均态"——**什么都对、什么都没做**。

!!! warning "长规则的反效果"
    规则文件越长,模型越容易"每条都沾一点"而不是"严格照做"。立规矩的目标是让 agent 有清晰优先级,而不是淹没在条款里。

## 硬约束兜底:软约束与工程约束

最后一层认知:**CLAUDE.md 只是软约束,模型仍可能违反**。规则文件是"让 Agent 知道",真正要让违规**做不到**,需要工程手段:

- **PreToolUse hook**(如 Claude Code 的 hooks):在执行危险操作前硬拦截;
- **CI 检查**:提交前验证命名、测试覆盖等规则是否被满足;
- 其他强制手段:lint、schema 校验、沙箱权限。

> 规则文件是让 Agent **知道**,工程约束才是让它**做不到**。

## 实践 / 应用:落地 checklist

1. **先收敛到一份 AGENTS.md**:把散在群聊/个人偏好里的规则集中,控制篇幅(200 行内);
2. **给各工具接入口**:CLAUDE.md 一行 `@AGENTS.md`;Cursor 用 `.cursor/rules` 只放 glob 规则;
3. **review 只盯一个文件**:新增/修改规则都改 AGENTS.md,PR 里可见;
4. **补硬约束**:对"必须"级规则加 PreToolUse hook / CI 检查,别指望模型自觉;
5. **定期修剪**:规则是有维护成本的,删掉已经内化成习惯的旧条款。

## 实战模板:Blinkoo 六维度 AGENTS.md(内容模板)

前面讲的是规则文件的**载体工程**(正交关系/一份源三消费/软硬约束);内容往哪写?Blinkoo(https://github.com/Nicotine00/Blinkoo-Vibe-Daily)从半年项目对话记录里提炼的**六维度模板**是一份可复制的起点,与本篇方法论互补:

| 维度 | 覆盖内容 | 防的坑 |
| --- | --- | --- |
| **开发基础** | 技术栈声明、项目结构约定、依赖管理规则 | AI 自作主张引入你没用过的框架 |
| **工作方式** | 先 plan 后动手、增量修改、最小输出、多文件改动先列计划 | "不确认直接大改项目" |
| **开发边界** | 该做/不该做;超出能力、用户做法低效、高复杂度需求怎么办 | 需求澄清前的擅自实现 |
| **代码规范** | 不硬编码、留扩展口、函数粒度控制、不搞过度设计 | 所有功能堆一个文件直逼千行 |
| **自检验证** | 写完先自测、核心逻辑必须有测试、改完做对比、外部依赖连通测试 | 改崩了不自知 |
| **安全检查** | Git 基线、对话长度控制、敏感信息保护 | 没有 Git 就让 AI 大规模改项目 |

!!! tip "使用流程与裁剪"
    复制到项目根目录 → 改开头项目目标和技术栈 → 告诉 AI"先读它再干活"。**小项目只要前几条就够;项目越大,规则越全的优势越明显**;改规则前先备份(尤其有进度的项目)。规则内容设计方法(怎么挖对话、怎么写"怎么办"、怎么裁剪)详见站内 [AI 协作规则设计](../../03-agents/agent-collaboration-rules.md)。

## 总结

- AGENTS.md(标准)/ CLAUDE.md(分层+引入)/ `.cursor/rules`(glob 激活)是**三种正交能力**,不是互斥选项;
- 工程解法:**一份 AGENTS.md 源文件 + CLAUDE.md 用 `@AGENTS.md` 引入 + glob 规则才拆 `.cursor/rules`**——一份内容三消费;
- 规则不是越多越好:**200 行掉遵循度、alwaysApply 超 2 条吃 context**;
- 软约束靠规则文件,硬约束靠 **PreToolUse hook / CI**——"规则让它知道,工程让它做不到"。

## 延伸阅读

- 站内:[个人 Agent Coding 经验](../index.md)、[mattpocock/skills 的 writing-for-agents](../skills/mattpocock-skills.md)、[AI Friendly 后端架构](../../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(架构规则策略/Harness 执行器)
- 外部:原文《给 Coding Agent 立规矩的正确姿势》;OpenAI Agents(AGENTS.md)与 Anthropic Claude Code(CLAUDE.md)官方文档;原始资料存档于 `docs/inbox/agent-rules-source.md`
