> 来源:微信公众号「昕科技团队」《用 Hermes Agent 搭建 OKF 知识库》
> 链接:https://mp.weixin.qq.com/s/FDR4NollfbGP8u3fhShCzA
> 抓取日期:2026-08-10

用 Hermes Agent 搭建 OKF 知识库
让 AI 代理在纯 Markdown 中管理结构化知识——无向量数据库，无特殊工具链。

概览
项目
说明
okf-kb-skill
OKF 知识库管理 Skill。纯 Markdown + YAML frontmatter，Git 友好
Hermes Agent
开源 AI 代理框架，Skill 即插即用
核心操作
Init / Ingest / Query / Lint / Update / Create Entity
安装 & 更新
前提： 已安装 Hermes Agent。
告诉 Hermes：
安装或更新 kb skill：从 https://github.com/ouranoshong/okf-kb-skill.git 安装

验证：hermes skills list | grep kb
更新：再次执行同一句话即可。
使用（零配置）
你说
代理执行
使用 kb skill 初始化知识库创建 knowledge-base/ → SCHEMA.md + CONVENTIONS.md + index.md + log.md + 子目录索引
将 raw/articles/ 下的所有文档编译为 Concept扫描 raw/ → 提取关键信息 → 生成 OKF Concept → 写入 concepts// → 更新索引和日志
基于知识库回答：什么是 Actor Model？从 concepts/ 检索 → 按 cross-reference 链加载 → 合成回答
对知识库做一次健康检查遍历所有 Concept，检查 7 项规则（孤立、矛盾、过期、断裂链接等）
目录结构

ounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineknowledge-base/├── SCHEMA.md              # 类型系统 + frontmatter 规范├── CONVENTIONS.md         # 命名 + 质量规则├── index.md               # 根索引├── log.md                 # 变更历史├── raw/                   # 原始资料（只读）├── concepts/              # OKF Concept 文档（按类型分目录）├── entities/              # 可复用实体页面└── assets/                # 图表、图片
Concept 类型
类型
必需章节
Technology# Overview, # Key Concepts, # Trade-offs
Architecture# Problem, # Decision, # Consequences
Protocol# Overview, # Message Format, # Examples
Research# Summary, # Key Findings, # Limitations
Playbook# Trigger, # Steps, # Verification
Entity# Overview, # Key Facts
Reference# Schema, # Examples
Metric# Definition, # Formula, # Thresholds
Decision# Context, # Decision, # Consequences
Frontmatter 示例

ounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(lineounter(line---type: Technologytitle: Actor Modeldescription: 基于消息传递的并发计算模型source: /raw/papers/actor-model.pdftags: [concurrency, distributed]confidence: highrelated:  - /concepts/technology/csp.mdcontradicts:  - /concepts/technology/shared-memory.mdtimestamp: 2026-06-17T00:00:00Z---
实战场景
初始化：使用 kb skill 初始化知识库，放入 raw/ 后执行 Ingest。
导入资料： 把 Markdown 放入 raw/articles/，然后说 将 raw/articles/ 下的所有文档编译为 Concept。
查询：基于知识库回答：<你的问题>。
更新： 告诉代理 更新 concepts/technology/xxx.md，添加新内容。
冲突： 在 contradicts 字段中显式声明，两侧都标注。
常见问题
问题
解决
hermes skills list 看不到 kb
/reload-skills 或重启 Hermes 会话
代理找不到知识
检查 index.md 链接是否正确；raw/ 非空
如何更新已有 Concept
直接告诉代理更新目标文件
能否删除 Concept
不删除——标记废弃，通过 git 保留历史
设计原则
纯文本：Markdown + YAML，cat 可读，git 可 diff

无向量库依赖：< 50k 全量加载，50k-200k 按导航加载，> 200k 才需要索引

显式矛盾 > 沉默不一致

永不删除：git 保留完整历史

公众号内添加AI客服智能体，已将公众号内文章作为知识库，公众号内提问即可体验，快来关注吧！

如果您觉得文章内容对您有所帮助，请点赞，关注，收藏，如有问题欢迎留言，创作不易，感谢有您！