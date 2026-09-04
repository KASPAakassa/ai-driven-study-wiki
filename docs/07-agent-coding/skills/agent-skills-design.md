# Equipping agents with Agent Skills:官方 Skill 设计理念与 progressive disclosure

> **一句话摘要**:Anthropic 官方 Agent Skills 设计理念(2025-10-16,2025-12-18 开源标准 agentskills.io)——**skill = 目录 + SKILL.md**,核心是三级 progressive disclosure:元数据进系统提示 → 按需读 SKILL.md → 按需读捆绑文件,让可打包上下文从"窗口内有限"变成"窗口外 unbounded";可捆绑 Python 脚本做确定性工具;开发流程先跑 eval 找能力缺口再沉淀;安全上只装可信来源、审计捆绑代码。
>
> **来源**:Anthropic Engineering《Equipping agents for the real world with Agent Skills》(https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills,2025-10-16)

## 概念

### 为什么需要 Skill

Agent 在真实世界要接的东西太多:PDF 表单、专有 API、内部知识库……把指令和代码塞进 context window 不现实。Skill 是给 agent 的**可重用能力包**:一个目录,含 `SKILL.md`(指令 + 元数据)+ 捆绑的参考文件/脚本。

> 相关规范背景:Skill 标准已由 Linux Foundation 的 AGENTS.md 生态与 [Agent Plugins 1.0](agent-plugins-spec.md) 标准化打包;本文是 Anthropic 官方**设计理念**源头。

### 核心:Progressive disclosure(渐进式披露)

不是把所有内容一次性塞进上下文,而是**按需加载,层层披露**:

```
第 1 级:元数据(skill 名 + 一句话描述)→ 进系统提示
第 2 级:SKILL.md(完整指令)→ agent 决定需要时读取
第 3 级:捆绑文件(references/、forms.md 等)→ 具体用到时再读
```

效果:**可打包的上下文是 unbounded 的**——上下文窗口只放"地图",细节留在窗口外按需取,与 Claude Code 的 CLAUDE.md 混合策略(前置注入 + glob/grep 即时检索)一脉相承。

## 原理

### SKILL.md 结构

```markdown
---
name: fill-pdf-forms
description: 填写 PDF 表单;当用户需要填写/提取 PDF 表单时使用
---
# 使用说明
1. ...(步骤)
2. ...(按需读取 references/ 或 forms.md)
```

- **YAML frontmatter**:`name` + `description`(description 决定 agent 何时调用——要写得像搜索词);
- **正文**:指令 + 指向捆绑文件的引用。

### 捆绑确定性工具

Skill 不只是提示词:可捆绑 **Python 脚本**作为确定性工具(如 PDF 表单提取)。脚本处理规则化部分(可靠、可审计),LLM 处理开放式判断(理解意图)——**脚本 + LLM 分工**。

### 开发流程:先 eval,再沉淀

1. **跑 eval 找能力缺口**:用真实任务评估,发现 agent 缺什么;
2. **为规模拆分文件**:文件过大时拆成 references/ 多文件,按需读取;
3. **从 Claude 视角监控使用轨迹**:看它实际怎么用 skill,哪里卡住;
4. **让 Claude 迭代沉淀**:把成功的做法沉淀成 skill,再跑 eval 验证。

### 安全

- 只安装**可信来源**的 skill;
- 审计捆绑的**代码与网络请求**(脚本可能执行任意操作);
- 与 Agent Plugins 规范的边界一致:标准管"放哪",安全责任在使用者。

## 代码 / 实现

PDF 表单技能示例(官方 github.com/anthropics/skills):

```
fill-pdf-forms/
├── SKILL.md          # name/description + 使用说明
├── fill_pdf.py       # 确定性脚本:解析/填写 PDF(如 PyMuPDF)
└── references/       # 按需加载的参考文件
```

```python
# fill_pdf.py —— 确定性部分:提取/填写表单字段
import fitz  # PyMuPDF
def extract_fields(pdf_path):
    doc = fitz.open(pdf_path)
    # 返回字段名/类型/坐标,供 LLM 决定填什么
```

**与站内 Skill 系列的分工**:

| 主题 | 站内文章 |
| --- | --- |
| 官方设计理念(本文:progressive disclosure/SKILL.md) | 本文 |
| 打包分发标准 | [Agent Plugins 1.0](agent-plugins-spec.md) |
| 团队级治理/可信来源 | [Skill 治理(Nacos AI Registry)](skill-governance-registry.md) |
| 版本/灰度/回滚 | [Agent Skill 版本管理](skill-version-management.md) |
| 五维测评 | [Skill 测评](skill-evaluation.md) |
| 平台级评测分发 | [腾讯 SkillHub(TRACE)](skillhub-trace-evaluation.md) |

## 实践 / 应用

- **什么时候沉淀 Skill**:任务规则化部分多(可拆确定性脚本)、需要专有知识(API/内部规范)、跨会话反复出现;
- **怎么设计**:description 写得像搜索词;文件按规模拆分;先跑 eval 再沉淀,别凭感觉写;
- **怎么验证**:监控使用轨迹 + eval 回归;
- **安全底线**:只装可信来源、审计捆绑代码/网络请求;
- 本仓库的 `.reasonix/skills/` 就是这套理念的落地实例(如 `data-scraping-experience` playbook)。

## 总结

1. **skill = 目录 + SKILL.md**:指令(含元数据)+ 捆绑参考/脚本,是可重用能力包。
2. **Progressive disclosure 是灵魂**:元数据进提示、SKILL.md 按需读、捆绑文件用时读——上下文窗口外 unbounded。
3. **脚本 + LLM 分工**:规则化部分用确定性脚本(可审计),判断部分用 LLM。
4. **先 eval 后沉淀**:找能力缺口 → 拆分文件 → 监控轨迹 → 迭代验证。
5. **安全责任在使用者**:可信来源 + 审计捆绑代码/网络请求。

**下一步学什么**:读 [Agent Plugins 1.0](agent-plugins-spec.md)(打包标准)与 [Skill 治理](skill-governance-registry.md)(团队落地);想动手按本文流程为你的高频任务沉淀一个 skill 并跑 eval。

## 延伸阅读

- 站内:[Agent Plugins 1.0](agent-plugins-spec.md)、[Skill 治理](skill-governance-registry.md)、[Agent Skill 版本管理](skill-version-management.md)、[Skill 测评](skill-evaluation.md)、[SkillHub TRACE](skillhub-trace-evaluation.md)、[Skill 收藏首页](index.md)
- 外部:原文(https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills);开源标准 agentskills.io;示例 skills(https://github.com/anthropics/skills)
