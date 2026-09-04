# 代码注释纪律:WHY 而非 WHAT——三个社区 Skill 的共识

> **一句话摘要**:AI 写代码的过度注释倾向(每行加注释、docstring 重复签名、复述显而易见)让注释从资产变成噪音。三个社区 Skill(code-comments / comment-guidelines / code-commenting)给出高度一致的纪律:**注释解释 WHY 而非复述 WHAT、自我文档化优先、注释过期即更新、删掉被注释的死代码、TODO/FIXME 带 owner 或 issue 链接**。本文整合三者的规则表、标记约定与反模式清单,可作为 [上下文工程](context-engineering-playbook.md) 中"代码内上下文"的配套纪律。
>
> **来源**:三个社区 Skill(jylhis/code-comments、ahonn/comment-guidelines、monkilabs/opencastle code-commenting),文献清单见 `docs/inbox/context-engineering-references-source.md`

## 概念:注释不是写得越多越好

**AI 过度注释倾向**是模型通病:每行加注释、docstring 重复签名、叙述显而易见的事。正确做法:**仅在注释能传达代码无法表达的信息时才添加**——"最好的注释往往是更好的名字"。

**核心原则**(三 Skill 高度一致):

1. **代码自我文档化优先**——精确命名、拆小函数、命名常量、提前返回;注释是最后手段;
2. **WHY 优先于 WHAT**——代码已说明"做什么",注释应说代码无法表达的"为什么";
3. **降低认知负荷**——把非显而易见的隐性知识显式化;
4. **零冗余**——绝不重复代码本身已表达的内容。

## 原理:何时值得写注释

**值得写注释的场景**:

- **WHY 不明显**:非显然理由、权衡、上游 bug 的 workaround、性能/安全原因;
- **行为令人意外**:顺序约束、副作用、故意偏离常规做法;
- **公共 API 契约**:调用者需不读函数体就得知参数、返回值、错误与不变量;
- **项目要求的法律/许可样板**。

**不该写注释的场景**:

- 代码字面上在做什么(显而易见的 `i += 1` 不注释);
- 命名良好的变量/函数;
- 标准模式与惯用法;
- 代码中可见的实现细节。

**BAD vs GOOD 对照**(comment-guidelines):

```typescript
// BAD:复述显而易见
// 将用户名设为输入值
user.name = input.value;

// GOOD:解释非显而易见行为
// 归一化为小写,实现搜索中的大小写不敏感匹配
user.searchKey = user.name.toLowerCase();

// BAD:复述显而易见
// 遍历所有条目
for (const item of items) { ... }

// GOOD:解释决策原因
// 逆序遍历,便于迭代中安全删除
for (let i = items.length - 1; i >= 0; i--) { ... }
```

对照要点:BAD 例只是把代码翻译成文字;GOOD 例揭示代码背后的决策原因(大小写归一化用于匹配、逆序是为了安全删除)——这些信息无法从代码本身读出。

## 代码 / 实现:标记约定与反模式清单

### 注释标记约定(code-commenting 完整表)

| 标记 | 语义 | 必须附加 |
| --- | --- | --- |
| `TODO` | 计划中的工作 | owner 或 issue 链接 |
| `FIXME` | 已知 bug | owner 或 issue 链接 |
| `HACK` | 变通方案 | **原因 + 何时可以移除** |
| `NOTE` | 非显而易见的约束 | — |
| `WARNING` | 副作用 / 变更风险 | — |
| `PERF` | 热路径性能点 | — |
| `SECURITY` | 安全敏感点 | — |
| `DEPRECATED` | 已弃用 | **替代方案 + 移除版本** |

```typescript
// TODO(JYL-512): replace with the streaming parser once it ships
// FIXME(auth-341): 令牌刷新竞态,单测间歇失败
// HACK: 上游 SDK v2 有 bug,临时绕行;SDK v3 发布后移除
```

!!! warning "没有链接、没有 owner 的 TODO 是永远不会被删除的注释。"

### 反模式清单(Never)

1. **注释掉的代码**——直接删除,历史交给 git(版本控制已保留历史,注释里的死代码只会默默腐烂);
2. **在注释里维护 changelog**——那是 `git log` 的职责;
3. **装饰性分隔线注释**(整行 `#`/`*`/`=` 横幅)——无信息量,改用空行或短标题;
4. **为烂名字道歉的注释**——应直接改名而非解释;
5. **过期注释**——错误的注释比没有注释更糟(读者会信任它)。

### 修改代码时的五条自动应用规则(comment-guidelines)

1. 删除任何复述代码行为的注释;
2. 保留解释 WHY 的注释;
3. 只为非显而易见的行为或设计决策新增注释;
4. 代码变更使旧注释过期时,同步更新(同一编辑内);
5. **绝不为凑篇幅或显得详尽而添加注释**。

### 注释质量检查清单

- 这条注释是 WHY 还是复述 WHAT?复述型应删除或改为改进命名;
- 能被命名解决的就重命名;
- 标记用词是否符合语义表(已知 bug 用 FIXME 而非 TODO)?
- `HACK` 是否写了原因与移除时机?`DEPRECATED` 是否写了替代与版本?
- 是否有被注释掉的代码、注释内 changelog、装饰性分隔线残留?
- 注释密度与风格是否匹配文件现状(稀疏文件保持稀疏)?

## 实践 / 应用:docstring 与行内注释的区分

**公共 API 用语言官方文档格式**(docstring、JSDoc/TSDoc、godoc、rustdoc、Javadoc)——支撑生成文档与编辑器悬浮提示;doc 注释描述契约(参数/返回/错误/不变量)而非复述函数体。**实现细节用简短行内注释**,紧贴棘手代码行,而不是放在远离代码的头部注释块。

**作为 Skill 落地**:comment-guidelines 设计为 `user-invocable: false`(无需显式调用)——Claude 在编辑任何代码时始终遵循上述原则:主动清理遇到的冗余注释(遇则删),仅当能切实降低认知负荷时才添加策略性注释。支持 Claude Code、OpenAI Codex、Cursor AI、Manus AI。

**对 AI 时代的意义**:AI 生成代码天然倾向过度注释,把这些纪律做成 Skill/规则注入上下文,是 [上下文工程](context-engineering-playbook.md) 中"静态上下文层"的一部分——让 AI 写的注释成为资产而非噪音。

## 总结

- **核心纪律**:注释解释 WHY 不复述 WHAT;自我文档化优先;零冗余;注释过期即更新;
- **值得写**:非显然 WHY、意外行为、公共 API 契约、法律样板;
- **标记约定**:TODO/FIXME 带 owner 或 issue;HACK 写原因与移除时机;DEPRECATED 写替代与版本;
- **反模式**:被注释的死代码、注释内 changelog、装饰性分隔线、为烂名字道歉;
- **AI 落地**:做成 user-invocable 的 Skill,编辑代码时自动清理冗余注释;
- **下一步**:把这些纪律写进 AGENTS.md/CLAUDE.md(见 [官方一手资料](context-engineering-official-sources.md)),或作为 [上下文工程管理方案](context-engineering-playbook.md) 的注释纪律章节。

## 延伸阅读

- code-comments(jylhis/skillsmp):https://skillsmp.com/zh/creators/jylhis/skills/skills-engineering-code-comments
- comment-guidelines(skillmd.ai):https://skillmd.ai/skills/comment-guidelines(源码 github.com/ahonn/dotfiles/.claude/skills/comment-guidelines)
- code-commenting(monkilabs/opencastle):https://github.com/monkilabs/opencastle/blob/main/src/orchestrator/skills/code-commenting/SKILL.md(原 claudewave 页面已 404)
- 站内:[上下文工程管理方案](context-engineering-playbook.md)(代码内上下文)、[官方一手资料](context-engineering-official-sources.md)(CLAUDE.md 编写规范)、[给 Coding Agent 立规矩](../07-agent-coding/experience/agent-rules-agents-md.md)
