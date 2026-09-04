# 搭建个人项目的 Agent 配置:EltexSoft 的 Claude Code 设置拆解

> **一句话摘要**:大多数人的"配置"就是丢一个 CLAUDE.md。真正让 Coding Agent 可靠的是**结构**:一个永不更改的全局骨架 + 按文件路径自动加载的规则包 + 每个代理只负责一件事 + 在糟糕提交发生之前拦住它的钩子。本文拆解 EltexSoft 团队的真实 Claude Code 配置,并提炼出一套**可迁移到任何个人项目的 Agent 配置搭建思路**。
>
> **来源**:微信公众号「拾一」翻译《"我"的 Claude Code 设置》(EltexSoft 团队),https://mp.weixin.qq.com/s/XWi4FGZF_Re2bxNnajMI4w;项目:https://github.com/roadhero/claude-code-setup;原始资料存档于 `docs/inbox/claude-code-setup-source.md`

## 概念:配置不是 CLAUDE.md,是结构

配置一个 Coding Agent,最常见的做法是"发布一个 CLAUDE.md 就完事"。但真正让 Claude Code 变得可靠的是**五层结构**:

| 层 | 位置 | 作用 |
| --- | --- | --- |
| **全局骨架** | `~/.claude/CLAUDE.md` | 精简(约 215 行)、技术栈无关的核心文件:工作流程、Git 规则、编码规范、密钥管理、反模式;**永不更改,被提示缓存** |
| **平台规则包** | `~/.claude/rules/{web,android,ios,compute}.md` | 带 `paths:` 元数据通配符,**按文件路径触发加载**,不碰的文件类型规则不进上下文 |
| **子代理阵容** | `~/.claude/agents/` + 各技术栈包 | 42 个专职子代理:四帽链 + 专家 + 按栈覆盖 |
| **钩子** | `~/.claude/hooks/{guard-commit,format}.sh` | 在糟糕提交发生之前拦住它、自动格式化 |
| **脚手架** | `~/.claude/skills/new-repo` + `templates/` | 用正确配置创建新仓库,复制模板即用 |

!!! tip "核心理念(一段话)"
    **两层架构**:全局层(`~/.claude/`)包含所有项目都成立的内容;项目层是仓库根目录下一个**简短的 CLAUDE.md**,只含该项目特定内容。规则**按路径触发**专门化,代理**按名称覆盖**专门化——两者都不会预先扫描仓库。**配置一次,基本不用管。**

## 原理:五层结构的设计逻辑

### 1. 两层架构:全局不变,项目只改一处

- 全局层保存"无论构建什么都成立"的内容;项目层只写该项目特有的东西(§19:技术栈、质量门禁、发布指引、合规范围);
- **骨架文件被提示缓存且永不更改**;项目文件是每个仓库唯一需要编辑的东西——改动面最小,心智负担最低。

### 2. 按路径触发的规则包(而不是全量加载)

```
rules/web.md        paths:  *.ts / *.py / ...
rules/android.md    paths:  *.kt
rules/ios.md        paths:  *.swift
rules/compute.md    paths:  *.cpp / *.cu
```

Claude Code 读取匹配通配符的文件(如 `*.kt` → Android)时才加载对应规则包。好处:**你从不触碰的文件类型对应的规则,永远不会进入上下文**——省 Token,也避免无关规则干扰。

### 3. 专职子代理阵容:每个代理只负责一件事

- **通用阵容(15 个)**:"四帽链"——架构师 → 高级工程师 → 代码审查 → QA,加上各类专家(安全、性能、数据库迁移、调试器、DevOps、文档、设计)、发布工程师 + 技术写作、交付层(技术项目经理、Scrum Master);
- **按技术栈覆盖(27 个)**:`agents-android/`(7)、`agents-ios/`(7)、`agents-compute/`(13);放入仓库的 `.claude/agents/` 目录即可用平台定制版本**覆盖同名通用代理**;
- 设计逻辑:**职责单一**——每个代理只负责一件事,比一个"万能代理"更可控、更易审查。

### 4. 钩子:把防线放在工具层

- `guard-commit.sh`(PreToolUse 钩子):阻止 Agent **强制推送、以非人类身份提交、在提交信息中写入 AI 归属、暂存明显的密钥**;
- `format.sh`:按扩展名自动格式化已编辑的文件,覆盖所有技术栈,**缺少格式化工具时静默跳过,绝不报错**;
- 注意:钩子守护的是 **Claude 的 Git 命令**,不是人类在终端里直接敲的 `git`——分工明确。

!!! warning "为什么要拦住'AI 归属'提交"
    在提交信息中写 `Generated with Claude` 这类归属声明,会污染提交历史且无信息量。配置里显式禁止,让提交信息回归"描述变更"本身——这也是 [给 Coding Agent 立规矩](../experience/agent-rules-agents-md.md) 里"硬约束兜底"的实例。

### 5. 脚手架与模板:让新项目开箱即用

- `skills/new-repo`:一个脚手架技能,用正确的 CLAUDE.md、.gitignore、质量门禁和发布工作流创建新仓库;
- `templates/`:空白项目 CLAUDE.md 模板(通用版 + 计算版),复制到新仓库填写 §19 即可;
- `examples/CLAUDE.example-web.md`:填好的示例,让你"动手之前先看到完成的样子";
- `docs/`:骨架文件按需指向的参考文档(完整代理阵容表、Phase-3 审查清单、错误恢复表、PR 模板),**仅在桩文件引用时才加载**。

## 代码 / 实现:规则包按路径触发的机制演示

核心机制是"路径通配符 → 命中才加载"。纯 Python 演示(与 Claude Code 的 `paths:` 行为一致):

```python
import fnmatch

RULES = {
    "web":      ["*.ts", "*.tsx", "*.py", "*.js"],
    "android":  ["*.kt", "*.kts"],
    "ios":      ["*.swift"],
    "compute":  ["*.cpp", "*.cc", "*.cu"],
}

def load_rules_for_file(filepath: str) -> list[str]:
    """按文件路径触发:命中哪个规则包才加载哪个,未命中的不进上下文。"""
    loaded = []
    for pkg, patterns in RULES.items():
        if any(fnmatch.fnmatch(filepath, p) for p in patterns):
            loaded.append(pkg)
    return loaded

# 演练:在一个 Web + 计算混编的仓库里编辑不同文件
for f in ["src/components/Login.tsx", "core/solver.cu", "MainActivity.kt", "README.md"]:
    pkgs = load_rules_for_file(f)
    print(f"  编辑 {f:30} → 加载规则包: {pkgs if pkgs else '(无,保持最小上下文)'}")

# 关键:即使仓库里有 .kt 文件,只要你不编辑它,Android 规则就不会加载
print("\n  只编辑 .tsx → Android/Compute 规则始终不进入上下文 ✓")
```

## 实践 / 应用:提炼一套"搭建个人项目 Agent 配置"的思路

!!! tip "从这套配置提炼的通用搭建思路(与工具无关)"
    1. **先定两层**:把"所有项目通用"的内容(工作流、Git 纪律、密钥管理、反模式)放全局;项目层只留技术栈、质量门禁、发布指引——改动面最小;
    2. **按路径加载规则**:不同语言/技术栈的规则分开存放,用路径通配符触发,而不是把所有规则塞进一个文件全量加载;
    3. **子代理职责单一**:通用阵容(架构→实现→审查→QA 四帽链 + 专家)+ 按栈覆盖——每个代理只负责一件事;
    4. **钩子守底线**:把"不能做"的事(强制推送、AI 归属提交、提交密钥)做成工具层钩子,而不是提示词里的口头要求——硬约束比软约束可靠;
    5. **脚手架 + 模板**:把"正确配置"固化成 new-repo 技能与空白模板,新项目复制即用、开箱即用;
    6. **文档按需加载**:长参考材料放 docs/,只在被引用时加载,不常驻上下文。

**安装这套配置(参考)**:

```bash
git clone https://github.com/roadhero/claude-code-setup.git && cd claude-code-setup
mkdir -p ~/.claude/{rules,agents,hooks,skills,docs}
cp CLAUDE.md ~/.claude/CLAUDE.md
cp rules/*.md ~/.claude/rules/
cp agents/*.md ~/.claude/agents/ && cp -R agents-android agents-ios agents-compute ~/.claude/
cp hooks/*.sh ~/.claude/hooks/ && chmod +x ~/.claude/hooks/*.sh
cp -R skills/new-repo ~/.claude/skills/
# 依赖:guard-commit.sh 需要 jq(缺失时安全失败拒绝运行)
# 然后为每个仓库复制 templates/ 模板作为项目 CLAUDE.md,填写 §19 部分
```

!!! warning "诚实说明(原文作者)与适配建议"
    这套配置是**个人化的**,为基于 PR 工作流和受保护分支的团队构建;钩子假设格式化工具已装(没装会干净跳过);计算栈(C++/CUDA/Python 系统级)对纯 Web 项目大材小用。**重点不是照搬,而是看到真实可用的配置后,构建你自己的。**

## 总结

- **五层结构**:全局骨架(永不更改)+ 按路径规则包(按需加载)+ 专职子代理(职责单一 + 按栈覆盖)+ 钩子(工具层守底线)+ 脚手架/模板(开箱即用);
- **两层架构原则**:全局管通用、项目只管差异,骨架文件被缓存、项目文件是唯一需要编辑的东西;
- **可迁移思路**:两层划分 → 按路径加载 → 代理单一职责 → 钩子守底线 → 脚手架固化 → 文档按需加载——这套思路与具体工具解耦,Claude Code/Cursor/Reasonix 都适用;
- **一句话**:配置 Agent 的核心不是写更多规则,而是**设计好结构,让规则只在需要时出现**。

## 延伸阅读

- 项目:https://github.com/roadhero/claude-code-setup(STRUCTURE.md 建议先读);翻译原文:https://mp.weixin.qq.com/s/XWi4FGZF_Re2bxNnajMI4w;作者著作《42:AI 构建者技术栈》(2026-08-15 Amazon 上线)
- 站内:[给 Coding Agent 立规矩](../experience/agent-rules-agents-md.md)(AGENTS.md/CLAUDE.md 正交关系)、[OpenAI 官方 Prompt 指南](../experience/openai-prompt-guide.md)(System Prompt 做减法)、[Loop Engineering](../experience/loop-engineering.md)、[Skill 收藏](../skills/index.md)
- 概念延伸:Claude Code hooks(PreToolUse)、agents 目录覆盖机制、fnmatch 路径通配符
