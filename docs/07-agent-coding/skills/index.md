# 📦 Skill 收藏

> 现成 Skill 的收藏与索引:可直接复用/改写的 Agent Skill 文件、配置、提示词模板。

## 本章节文章

- [GSD (Get Shit Done):上下文工程 + 规格驱动开发系统](gsd-workflow-skill.md) — TÂCHES 开源:讨论→计划→执行→验证循环、子代理编排、XML 任务格式、原子提交,主上下文保持 30-40%
- [gstack:YC CEO 的角色化虚拟工程团队](gstack-skills.md) — Garry Tan 开源 23+ 角色化 Skill:Sprint 七步、Browse Daemon 浏览器自动化、角色分解设计模式、工程体系拆解
- [Spec Kit:GitHub 官方的规格驱动开发工具包](spec-kit-github.md) — specify-cli 初始化 + /speckit.specify→clarify→plan→tasks→implement 命令链,规格落盘可追溯
- [SDD(Spec-Driven Development):从个人提效到团队可控](sdd-openspec-superpowers.md) — SDD 方法论(Vibe vs SDD)+ OpenSpec(需求层 6 阶段流水线)+ Superpowers(执行层 15 skill)+ 组合方案与落地思考
- [prd-writer:用 AI 写 PRD 需求文档](prd-writer-skill.md) — 三视角诊断、概念版/落地版两版交付、MVP 闸门、补全盲区、先读再写;全栈工作者自己写需求的抓手(MIT 开源)
- [Matt Pocock 的 "Skills For Real Engineers"](mattpocock-skills.md) — GitHub 仓库总结:设计哲学、四个失败模式解法、36 个 skill 清单;含核心 Skill 深度拆解与姊妹项目 Superpowers(247k Star)
- [科研领域现成 Skill 收藏](research-skills-collection.md) — 2026 最值得装的 8 个科研 Skill 仓库(读论文/跑实验/写论文/做图)
- [Eval Engineering Skill](eval-engineering-skill.md) — LangChain 开源:读仓库+分析 traces+"面试"式设计评估测试
- [handoff Skill:把上下文压成接力文档](handoff-skill.md) — Matt Pocock skills:交接文档单独成文、suggested skills、引用路径不复制内容,八项交接清单
- [Spec-First Skill:把 AI Coding 装进工程闭环](spec-first-skill.md) — spec-prd/plan/review 系列 skill:需求澄清、scope 锁定、证据四等级+非法组合拦截、经验沉淀
- [patent-disclosure-skill(专利交底书)](patent-disclosure-skill.md) — 国产开源 4000+ Star:扫描挖掘/查新检索(摘要+LLM 判断 60%→95%)/Mermaid 图表/自检迭代,防幻觉工作流
- [Obsidian AI Skill 收藏](obsidian-ai-skills.md) — 9 个必装仓库(Anthropic 官方主仓/Obsidian 基座/第二大脑/索引/替代品)+ 4 个插件 + 安装与安全
- [Agent Skill 版本管理](skill-version-management.md) — 源码层(Git 整目录+SemVer)+ 运行时层(生产锁定+评测/兼容/灰度/回滚):面试题拆解
- [Skill 治理:用 Nacos AI Registry 给团队 Skill 一份可信来源](skill-governance-registry.md) — 六步治理链路(本机统一→元数据→准入→权限→版本/标签→同步进 Agent)+ 两种部署形态 + doc-format 落地案例
- [Skill 测评:五大维度与测试闭环](skill-evaluation.md) — 触发/独立执行/共存冲突/指令遵循/输出质量五维,基线→监控→回流闭环
- [腾讯 SkillHub:10 万+ Skill 的质量评测与分发](skillhub-trace-evaluation.md) — 平台级 TRACE 五维评测(Trust/Reliability/Adaptability/Convention/Effectiveness)+ 云端隔离试运行 + 榜单标签 + find skill(面向 Agent 的发现)
- [Agent Plugins 1.0:Skill 的"统一插头"规范](agent-plugins-spec.md) — 2026-08-06 谷歌/微软/亚马逊/OpenAI/Cursor/Vercel 联合发布:一个插件一个目录(plugin.json+skills/+mcp.json+客户端扩展);闭合 manifest、MCP 显式传输、组件独立失败、PLUGIN_ROOT/DATA;单 Skill 不用打包、多组件一起走才需要(规范原文已核验)
- [Equipping agents with Agent Skills:官方 Skill 设计理念与 progressive disclosure](agent-skills-design.md) — Anthropic 官方:skill=目录+SKILL.md、三级渐进式披露(元数据→SKILL.md→捆绑文件,上下文 unbounded)、捆绑确定性 Python 脚本、先 eval 后沉淀、安全审计(与 Plugin 规范/治理/版本/评测分工)

## 待整理 / 规划

<!-- 从 inbox 收件箱转入本主题的素材,梳理前先登记在这里 -->

## 收录原则

- 每个 Skill 注明:**用途、适用工具、来源、依赖、使用方式**(如何安装/调用)。
- 原始 Skill 文件尽量原样存档,整理文章负责说明"怎么用、什么时候用"。
- 只收录你授权收录的 Skill,不擅自对外传播。
