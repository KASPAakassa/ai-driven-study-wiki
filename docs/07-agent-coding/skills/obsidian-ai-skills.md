# Obsidian AI Skill 收藏:9 个必装仓库 + 4 个插件

> **一句话摘要**:当公司文档"不太适合上云",本地知识库 Obsidian 就成了 AI Agent 的第二大脑。本文整理当前最值得装的 **9 个 Obsidian AI Skill**(按 GitHub Star 排序,从 Anthropic 官方 15.9 万星主仓到硬核替代品),加上 Obsidian 本身的 4 个插件与安装/安全要点——装完后 AI 能直接操作 vault,**读、改、剪藏、建图、写日报整条链跑通**。
>
> **来源**:微信公众号《Agent联动Obsidian 9大AI Skill 实测》;原始资料存档于 `docs/inbox/obsidian-ai-skills-source.md`

## 一、9 个必装 Skill(按 GitHub Star 排序)

| # | 仓库 | Star | 定位 | 适合 |
| --- | --- | --- | --- | --- |
| 1 | **anthropics/skills** | 15.9 万 | **Anthropic 官方 Agent Skills 主仓**,17 个 skill 覆盖算法画板/品牌规范/PPT/PDF/Word/Excel,**安全分满分** | 办公全场景通吃(通用基座) |
| 2 | **kepano/obsidian-skills** | 4 万 | **Obsidian 官方 5 件套**:markdown / bases / json-canvas / obsidian-cli / defuddle;wikilink、frontmatter、Bases 视图全规范 | 必装基座(让 AI 真正懂 Obsidian 语法) |
| 3 | **obsidian-second-brain** | 3K | 44 个命令跨 6 个 CLI(Claude Code/Codex/Gemini/OpenCode/Hermes/Pi);vault 自己重写自己,**自演化第二大脑** | 想让 AI 持续维护 vault |
| 4 | **stevesolun/ctx** | 545 | **68K skills / 467 agents / 10K MCPs 全索引**,按需加载省 token | 想找 skill 时先搜这个索引 |
| 5 | **lingxling/awesome-skills-cn** | 172 | **中文圈最大 Skills 教程合集**,7000+ Skills、claude-skills、openclaw-skills 一次配齐 | 新手友好(中文教程) |
| 6 | **chacosoldier/compabob** | 26 | 知识工人定制版:agents + **安全 hooks** + Obsidian 知识库 | 进阶定制 |
| 7 | **anliberant/obsidian-ai-setup** | — | 个性化 AI vault **一键 bootstrap,3 条命令** | 新人最快上手 |
| 8 | **ibrahimkobeissy/ai-second-brain-template** | — | **自组织 vault + AI agent 协作**模板 | 深度定制党 |
| 9 | **inkeep/open-knowledge** | — | **Obsidian 和 Notion 的开源 AI-first 替代**(381 HN 点赞硬核项目) | 想换更 AI-first 的工具 |

!!! tip "按场景选择**
    - **通用办公**:装 #1 anthropics/skills(官方,安全满分);
    - **让 AI 操作 Obsidian 本体**:装 #2 obsidian-skills(必装基座,否则 AI 不懂 wikilink/frontmatter/Bases);
    - **长期维护第二大脑**:加 #3 obsidian-second-brain(vault 自演化);
    - **想找更多 skill / 中文教程**:用 #4 ctx 索引 / #5 awesome-skills-cn;
    - **换更 AI-first 的方案**:看 #9 open-knowledge。

## 二、安装一行命令(以基座为例)

```bash
npx skills add https://github.com/kepano/obsidian-skills
```

!!! warning "安全提示(原文)**
    首次让 AI 操作 vault 前,**先用 Git 提交一次**——可回滚才敢放权。装完后 AI 能直接操作 vault:读、改、剪藏、建图、写日报整条链跑通,但**授权前先留好回滚点**。

## 三、Obsidian 本身的 4 个插件

| 插件 | 用途 |
| --- | --- |
| **Templater** | 模板引擎(动态生成笔记) |
| **Calendar** | 日历视图(日记/计划) |
| **Text Generator** | 文本生成(AI 辅助写作) |
| **Excalidraw** | 画布/图示(建图) |

!!! note "与站内其他 Skill 收藏的呼应**
    - [科研领域现成 Skill 收藏](research-skills-collection.md):同为"按场景收藏 Skill 仓库"的风格;
    - [Matt Pocock 的 Skills 集合](mattpocock-skills.md):#1 anthropics/skills 是**官方主仓**(比社区集合更权威);
    - [handoff Skill](handoff-skill.md):#2 obsidian-skills 与 handoff 同属"让 Agent 操作真实文件系统"的 Skill 族;
    - [Spec-First Skill](spec-first-skill.md):知识库(如 Obsidian vault)是 Agent 上下文的重要来源,与本站 [高德知识库](../../06-enterprise/ontology-agent-adoption/ai-native-knowledge-base-gaode.md) 的思路同源。

## 总结

- **9 个 Skill**:官方主仓(anthropics/skills)+ Obsidian 官方基座(obsidian-skills)+ 第二大脑(second-brain)+ 索引(ctx/awesome-skills-cn)+ 定制(compabob/setup/template)+ 替代(open-knowledge);
- **一条安装命令**:`npx skills add`;**4 个插件**:Templater/Calendar/Text Generator/Excalidraw;
- **一条安全纪律**:首次授权 AI 操作 vault 前先 Git 提交(可回滚才敢放权);
- **一句话**:Obsidian + AI Skill = 让 Agent 真正"住进"你的第二大脑——装好基座,配好插件,留好回滚,整条知识工作链跑通。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/SMLmwZ8jUUoqdL-LHnx4QQ;原始资料存档于 `docs/inbox/obsidian-ai-skills-source.md`
- 站内:[Skill 收藏](index.md)、[科研领域现成 Skill 收藏](research-skills-collection.md)、[Matt Pocock 的 Skills 集合](mattpocock-skills.md)、[handoff Skill](handoff-skill.md)
