# AGENTS.md — AI 驱动的学习 Wiki

个人 AI 知识库:把零散的学习资料整理成结构化 Wiki。收录 AI 基础、机器学习、深度学习、LLM、Agent 使用与开发相关的知识。组织方式参考 Karpathy 教学风格(概念 → 原理 → 代码 → 实践)。

## 核心工作流

**用户的期望:往 `docs/inbox/` 丢任何可学可做的资料(文章、链接、代码、课程、甚至一句学习要求),由 AI 助手系统梳理、整理、落成 Wiki 文章。**

处理一条素材的标准流程(每次"整理收件箱"任务都要走完):

1. **收件**:确认素材在 `docs/inbox/`,在 `docs/inbox/tasks.md` 登记一行(#、来源、主题、用户要求、状态)。
2. **阅读与提炼**:读懂素材 → 提取核心知识 → 去重(查站内是否已有同类文章,有则合并/补充而非新建)。
3. **成文**:按 `docs/_template.md` 结构写文章(概念 / 原理 / 代码 / 实践 / 总结 / 延伸阅读)。
4. **归位**:文章放到对应分类目录,原始素材保留在 `docs/inbox/` 根目录作为存档(不删除原文、不新建 archive 目录,文件名以 `-source.md` 后缀标记)。
5. **联动更新**(漏掉任何一项都算没完成):
   - 所属分类的 `index.md` 的"本章节文章"列表
   - `mkdocs.yml` 的 `nav`(新文章加入对应章节)
   - `docs/inbox/README.md` 与 `docs/inbox/tasks.md`(勾选状态、归档位置)
   - `docs/index.md` 学习地图(如影响章节结构)
6. **提交与同步**:跑通 `.venv/bin/mkdocs build` 验证后,必须 `git add -A && git commit`,并 `git push origin main` 同步到 GitHub——**每次新增/修改知识后都触发一次提交与推送,不攒批**。

## 命令

```bash
.venv/bin/mkdocs build     # 构建静态站点到 site/(构建通过 = 基本校验通过)
.venv/bin/mkdocs serve     # 本地预览 http://127.0.0.1:8000
.venv/bin/pip install mkdocs-material   # 首次或补依赖(在 .venv 里)
```

环境:python3 + venv(`.venv/`),无 node/docker。改动 Markdown 后必须跑 `mkdocs build` 验证没有链接/语法错误。

## 目录结构

```
docs/
├── 01-ai-basics/          # AI 基础 + 机器学习 + 深度学习(概念/算法/神经网络/训练)
├── 02-llm/                # 大语言模型(Transformer、预训练、微调、RLHF、RAG)
├── 03-agents/             # Agent 使用与开发
├── 04-practice/           # 实战项目
├── 05-reference/          # 参考资料(论文/书/课程/工具)
├── 06-enterprise/         # 企业落地与 FDE:ontology-agent-adoption/、ai-friendly-architecture/、ai-org-transformation/ 与 fde-methodology/ 四个子主题
├── 07-agent-coding/       # 个人 Agent Coding 经验:experience/(经验分享)、skills/(Skill 收藏)、agent-config/(项目配置)、claude-code-deep-dive/(Claude Code 深度解析)
├── 08-harness/            # Harness 框架与开源方案:编码 Agent、编排框架、开源方案索引 + 各框架专题收录
├── 09-agent-research/     # Agent 前沿学术:论文解析/研究方法论/开源数据集
├── 10-harmonyos/          # 鸿蒙开发专题:平台全景/ArkUI/质量发布/AI 辅助开发
├── inbox/                 # 📥 收件箱:用户丢资料的暂存区,配套 tasks.md 登记表
└── _template.md           # 文章结构模板
```

分类映射(归档时按此判断放哪):
- AI/ML/DL 概念与术语、经典 ML 算法、神经网络/CNN/RNN、训练技术 → `01-ai-basics`
- Transformer/Tokenizer/预训练/微调/RLHF/量化/RAG → `02-llm`
- Agent 概念/框架/工具调用/多 Agent/开发 → `03-agents`
- 完整项目/复现/踩坑 → `04-practice`
- 资源清单/论文/书/课程/工具 → `05-reference`
- Ontology/企业语义层/Agent 落地 → `06-enterprise/ontology-agent-adoption`
- AI Friendly 架构/系统知识显式化/SKILL/Harness → `06-enterprise/ai-friendly-architecture`
- AI 组织转型/超级个体/组织变革/管理者认知 → `06-enterprise/ai-org-transformation`
- FDE 角色/方法论/案例 → `06-enterprise/fde-methodology`
- 个人 Agent Coding 经验/技巧/踩坑 → `07-agent-coding/experience`
- 现成 Skill 收藏与索引 → `07-agent-coding/skills`
- 项目 Agent 配置(CLAUDE.md/AGENTS.md 搭建) → `07-agent-coding/agent-config`
- Claude Code 架构/机制/技巧深度解析 → `07-agent-coding/claude-code-deep-dive`
- 开源 Harness 框架/工具索引 → `08-harness`(编码 Agent/编排框架/开源方案索引 + 各框架专题收录)
- Agent 前沿学术/论文解析/数据集 → `09-agent-research`
- 鸿蒙开发/ArkTS/ArkUI/鸿蒙 AI 开发 → `10-harmonyos`

## 约定

- **文章结构**:严格遵循 `_template.md`(概念 → 原理 → 代码 → 实践 → 总结 → 延伸阅读);用不上的小节留 `<!-- 待补充 -->`,不要删结构。
- **语言**:正文用简体中文;代码、术语、变量名、文件名保留英文原文,不翻译。
- **来源**:每篇文章必须带来源链接/出处,便于追溯;整理是"提炼+引用",不是抄袭。
- **文件名**:英文 kebab-case(如 `transformer-architecture.md`),目录 index 固定为 `index.md`。
- **链接**:站内链接用相对路径(如 `../02-llm/xxx.md`);在 MkDocs 里链接到其他页用 `.md` 相对路径。
- **不删除原始资料**:素材归档后保留在 `inbox/` 根目录(文件名 `-source.md` 标记),只移动不删除、不新建 archive 目录。
- **收件箱规则**:所有新素材先落 `inbox`,整理完成才算正式内容;未整理完的不要直接写进正式分类。
- **验证**:改动后跑 `.venv/bin/mkdocs build`;报错必须修复后再交付。
- **提交与同步**:每次新增/修改知识后,在 `mkdocs build` 通过后执行一次 `git add -A && git commit -m "..." && git push origin main`(remote: `git@github.com:zhaoqilong/ai-driven-study-wiki.git`,分支 `main`);提交信息按 `docs(分类): 简述` 的约定写;不得把多次独立改动攒成一个提交。

## Notes

<!-- 快速记录区:临时发现、用户偏好、待办。 -->
