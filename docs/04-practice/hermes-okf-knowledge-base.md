# 用 Hermes Agent 搭建 OKF 知识库:纯 Markdown 的结构化知识管理

> **一句话摘要**:让 AI 代理在纯 Markdown 中管理结构化知识——无向量数据库、无特殊工具链。本文拆解 OKF(Obsidian-Knowledge-Framework 风格)知识库管理 Skill 的完整用法:**目录结构、9 种 Concept 类型、YAML frontmatter 规范、Init/Ingest/Query/Lint 四大核心操作、以及"纯文本 + 显式矛盾 + 永不删除"的设计原则**,并对比 RAG 与文件系统两种知识组织路径的取舍。
>
> **来源**:微信公众号「昕科技团队」《用 Hermes Agent 搭建 OKF 知识库》(https://mp.weixin.qq.com/s/FDR4NollfbGP8u3fhShCzA),素材存档 `docs/inbox/hermes-okf-source.md`

## 概念

- **OKF 知识库是什么**:一种**纯文本优先的结构化知识库**——知识全部以 Markdown 文件 + YAML frontmatter 存储,配合一个 Agent Skill(`okf-kb-skill`)让 AI 代理完成初始化、收录、查询、体检等管理动作。核心口号:**无向量数据库,无特殊工具链**,Git 天然友好(cat 可读、diff 可追踪)。
- **为什么重要**:传统 RAG 知识库(向量库 + embedding + 检索管道)对个人/小团队是重武器——要维护索引、要选 embedding、要担心召回质量。OKF 的思路是:**知识量没到阈值前,文件系统本身就是最好的"数据库"**,目录即索引、链接即关系、Git 即版本管理,而 AI 代理负责把"人写笔记"升级为"结构化 Concept 文档"。
- **与 RAG 的关系**:不是替代,而是**分级策略**——`< 50k` 全量加载、`50k-200k` 按导航加载、`> 200k` 才引入索引。OKF 先把前两档做到零依赖,把向量库推迟到真正需要的规模。可对比站内 [Agent 记忆体系](../03-agents/agent-memory-systems.md) 中"知识层 vs 记忆层"的划分。

## 原理

### 1. 目录即结构

```text
knowledge-base/
├── SCHEMA.md          # 类型系统 + frontmatter 规范(知识库的"Schema")
├── CONVENTIONS.md     # 命名 + 质量规则(知识库的"Style Guide")
├── index.md           # 根索引(代理检索的入口)
├── log.md             # 变更历史
├── raw/               # 原始资料(只读,知识原料)
├── concepts/          # OKF Concept 文档(按类型分目录)
├── entities/          # 可复用实体页面
└── assets/            # 图表、图片
```

- `SCHEMA.md` + `CONVENTIONS.md` 是知识库的**元规则**,代理依据它们判断"一条知识该用什么类型、怎么写才合格"——这本质是给 Agent 的显式 Schema 约束(呼应站内 [AI Friendly 架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md) 中"让系统对 Agent 可读"的思想)。
- `index.md` 是检索锚点:代理找不到知识时,先查 index 链接再沿 `cross-reference` 链加载。

### 2. 9 种 Concept 类型(结构化约束)

| 类型 | 必需章节 |
|---|---|
| Technology | `# Overview`, `# Key Concepts`, `# Trade-offs` |
| Architecture | `# Problem`, `# Decision`, `# Consequences` |
| Protocol | `# Overview`, `# Message Format`, `# Examples` |
| Research | `# Summary`, `# Key Findings`, `# Limitations` |
| Playbook | `# Trigger`, `# Steps`, `# Verification` |
| Entity | `# Overview`, `# Key Facts` |
| Reference | `# Schema`, `# Examples` |
| Metric | `# Definition`, `# Formula`, `# Thresholds` |
| Decision | `# Context`, `# Decision`, `# Consequences` |

- 每种类型强制"必需章节",是**把模板内建到知识库**的做法——代理生成时按模板填空,保证所有 Concept 结构一致、可比较、可批量处理。这与本站 `_template.md` 的思路同源。

### 3. Frontmatter:显式表达关系与冲突

```yaml
---
type: Technology
title: Actor Model
description: 基于消息传递的并发计算模型
source: /raw/papers/actor-model.pdf
tags: [concurrency, distributed]
confidence: high
related:
  - /concepts/technology/csp.md
contradicts:
  - /concepts/technology/shared-memory.md
timestamp: 2026-06-17T00:00:00Z
---
```

- `related` / `contradicts` 把知识之间的**关系显式化**:`contradicts` 声明矛盾并双侧标注,对应设计原则"**显式矛盾 > 沉默不一致**"——宁可让冲突可见、可讨论,也不让知识库假装一致。
- `source` 追溯原料,`confidence` 标记可信度,`timestamp` 支持过期判断(呼应 Lint 的"过期"检查)。

## 代码 / 实现

### 安装 Skill(Hermes Agent 即插即用)

```text
# 前提:已安装 Hermes Agent(开源 AI 代理框架)
# 告诉 Hermes:
安装或更新 kb skill:从 https://github.com/ouranoshong/okf-kb-skill.git 安装

# 验证:
hermes skills list | grep kb
```

- 更新 = 再次执行同一句话即可(Skill 即插即用,无需手工拷贝文件)。
- 若 `hermes skills list` 看不到 kb,执行 `/reload-skills` 或重启 Hermes 会话。

### 零配置使用(自然语言驱动)

| 你说 | 代理执行 |
|---|---|
| 使用 kb skill 初始化知识库 | 创建 `knowledge-base/` → 生成 SCHEMA.md + CONVENTIONS.md + index.md + log.md + 子目录索引 |
| 将 raw/articles/ 下的所有文档编译为 Concept | 扫描 raw/ → 提取关键信息 → 生成 OKF Concept → 写入 concepts// → 更新索引和日志 |
| 基于知识库回答:什么是 Actor Model? | 从 concepts/ 检索 → 按 cross-reference 链加载 → 合成回答 |
| 对知识库做一次健康检查 | 遍历所有 Concept,检查 7 项规则(孤立、矛盾、过期、断裂链接等) |

- 检索是**导航式而非语义式**:先查 `index.md`,沿链接链加载相关 Concept——知识量没超过阈值时,这比向量检索更快、更可控、零成本。
- `Lint`(健康检查)是知识库的 CI:孤立节点、互相矛盾、过期内容、断裂链接一次性暴露。

## 实践 / 应用

### 实战场景

1. **初始化**:用 kb skill 初始化知识库,把 Markdown 资料放入 `raw/articles/` 后执行 Ingest;
2. **导入资料**:说"将 raw/articles/ 下的所有文档编译为 Concept";
3. **查询**:说"基于知识库回答:xxx"——代理检索 + 沿链接加载 + 合成;
4. **更新**:说"更新 concepts/technology/xxx.md,添加新内容";
5. **处理冲突**:在 `contradicts` 字段显式声明,两侧都标注,保留矛盾供后续裁决。

### 常见问题速查

| 问题 | 解决 |
|---|---|
| `hermes skills list` 看不到 kb | `/reload-skills` 或重启 Hermes 会话 |
| 代理找不到知识 | 检查 index.md 链接是否正确;raw/ 是否非空 |
| 如何更新已有 Concept | 直接告诉代理更新目标文件 |
| 能否删除 Concept | 不删除——标记废弃,通过 git 保留历史 |

### 设计原则与注意点

- **纯文本**:Markdown + YAML,cat 可读、git 可 diff——知识资产不被专有格式绑架;
- **无向量库依赖**:按规模分级(`<50k` 全量 / `50k-200k` 按导航 / `>200k` 才索引),避免过早引入重基础设施;
- **显式矛盾 > 沉默不一致**:冲突要写出来,不掩盖;
- **永不删除**:知识库是积累不是消耗,废弃用标记 + git 历史保留。

## 总结

1. **OKF 把知识库做成"AI 可维护的 Markdown 工程"**:目录 = Schema,frontmatter = 关系,Agent Skill = 管理员,Git = 版本与审计。
2. **先文件系统、后向量库**的分级思路,让个人/小团队在知识量达标前保持零依赖。
3. **显式结构约束**(9 种类型 + 必需章节)是 Agent 产出质量的关键——模板内建到知识库。
4. **"显式矛盾"与"永不删除"** 两条原则,让知识库在冲突与迭代中保持诚实与完整。
5. **下一步**:把 OKF 与站内 [Agent 记忆体系](../03-agents/agent-memory-systems.md) 对比,理解"知识层(结构化文件) vs 记忆层(上下文注入) vs 状态层(RAG 索引)"的分工;或参考 [Obsidian 与 AI Skills](../07-agent-coding/skills/obsidian-ai-skills.md) 看另一条纯本地知识管理路径。

## 延伸阅读

- 站内:[Agent 记忆体系](../03-agents/agent-memory-systems.md)(RAG/Memory/State 分离)、[Obsidian 与 AI Skills](../07-agent-coding/skills/obsidian-ai-skills.md)(另一条纯本地知识路径)、[AI Friendly 后端架构](../06-enterprise/ai-friendly-architecture/ai-friendly-backend.md)(系统对 Agent 可读)、[DeepTutor 知识中心](deeptutor-agent-workspace.md)(多引擎 RAG 的知识中心实现)
- 外部:okf-kb-skill 仓库 https://github.com/ouranoshong/okf-kb-skill.git;Hermes Agent(开源 AI 代理框架,Skill 即插即用)
