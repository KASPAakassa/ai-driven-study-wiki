# AI 驱动的学习 Wiki

> 一个持续生长的个人知识库:收录 AI 基础知识、机器学习/深度学习、大语言模型(LLM)、Agent 使用与开发相关的文章与资料,经系统梳理后落成结构化 Wiki。

## 这是什么

把零散的学习资料整理成可检索、可追溯、可复用的知识体系。你可以随时往 [`docs/inbox/`](docs/inbox/README.md) 丢任何文章、笔记、链接或学习要求,由 AI 助手(本项目的 agent)负责:

1. **收件**:资料先进 `docs/inbox/`,不丢失、不混入正式内容。
2. **梳理**:按主题归类,提炼成统一格式的 Wiki 文章(概念 → 原理 → 代码 → 实践)。
3. **落库**:文章归位到对应分类目录,同步更新索引、`mkdocs.yml` 导航。

组织方式参考 Karpathy 的教学风格:先讲清概念,再讲透原理,然后落到代码实现,最后给实践要点。

## 目录结构

```
docs/
├── 01-ai-basics/          # AI 基础 + 机器学习 + 深度学习
├── 02-llm/                # 大语言模型
├── 03-agents/             # Agent 使用与开发
├── 04-practice/           # 实战项目
├── 05-reference/          # 参考资料
├── 06-enterprise/         # 企业落地与 FDE(Ontology、前向部署工程师)
├── 07-agent-coding/       # 个人 Agent Coding 经验(使用经验、Skill 收藏)
├── 08-harness/            # Harness 框架与开源方案(编码 Agent、编排框架、配套工具)
├── 09-agent-research/     # Agent 前沿学术(论文解析、数据集、研究前沿)
├── inbox/                 # 📥 收件箱:未整理的原始资料
└── _template.md           # 文章结构模板
```

## 使用方式

### 丢资料

把任何想学习的资料(文章、PDF 链接、课程、代码、甚至一句"我想学 XXX")放进 `docs/inbox/`,然后告诉 agent 去整理即可。

### 本地浏览(Wiki 站点)

```bash
# 第一次需要准备环境
python3 -m venv .venv
.venv/bin/pip install mkdocs-material

# 构建并本地预览
.venv/bin/mkdocs serve      # http://127.0.0.1:8000

# 构建静态站点到 site/
.venv/bin/mkdocs build
```

纯 Markdown 方式:直接用任意 Markdown 阅读器打开 `docs/` 下的文件即可。

## 约定(给未来 agent 的摘要)

完整约定见 [`AGENTS.md`](AGENTS.md),核心几条:

- 新资料一律先进 `docs/inbox/`,整理完再归位,不删除原始资料。
- 每篇文章遵循 `_template.md` 结构:概念 / 原理 / 代码 / 实践 / 总结 / 延伸阅读。
- 文章中文书写,代码、术语、文件名保留英文原文;引用必须带来源链接。
- 整理后更新:`docs/inbox/README.md`、所属分类的 `index.md`、`mkdocs.yml` 的 `nav`。
