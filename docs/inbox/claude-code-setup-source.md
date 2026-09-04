# 原始资料:"我"的 Claude Code 设置(EltexSoft 团队)

> 来源:微信公众号「拾一」翻译,原文 EltexSoft 团队(roadhero/claude-code-setup,https://github.com/roadhero/claude-code-setup)
> 原文链接:https://mp.weixin.qq.com/s/XWi4FGZF_Re2bxNnajMI4w
> 抓取日期:2026-08-09;状态:已整理为正式文章 docs/07-agent-coding/agent-config/claude-code-setup.md(新子主题:项目 Agent 配置)

---

这是我在 EltexSoft[1] 日常使用的真实 Claude Code 配置：一套技术栈无关的工程化「骨架」、按文件路径自动加载的平台规则包、横跨四大技术栈的 42 个子代理、提交守卫钩子加自动格式化工具，以及一个仓库脚手架。这也是我在 《42：AI 构建者技术栈》 一书中描述的那套配置。各取所需。
大多数人的做法是发布一个 CLAUDE.md 就称之为「配置」了。但真正让 Claude Code 变得可靠的，是结构：一个永不更改的全局文件、按路径通配符按需加载的规则、每个代理只负责一件事，以及在糟糕提交发生之前就拦住它的钩子。这就是这个项目所提供的。
项目内容

          路径说明CLAUDE.md通用骨架——精简的（约 215 行）始终加载的核心文件：工作流程、Git 规则、编码规范、密钥管理、反模式。与技术栈无关。更长的参考材料放在 docs/ 中按需加载。rules/{web,android,ios,compute}.md平台规则包。每个包都带有 paths: 前置元数据通配符；当 Claude Code 读取匹配该通配符的文件时（如 *.kt → Android，*.swift → iOS，*.ts/*.py → Web，*.cpp/*.cu → 计算）就会加载对应的规则包。按路径触发，所以你从不触碰的文件类型对应的规则包不会进入上下文。agents/（15 个）默认子代理阵容：四帽链（架构师 → 高级工程师 → 代码审查 → QA），加上各类专家（安全、性能、数据库迁移、调试器、DevOps、文档、设计），发布工程师 + 技术写作，以及交付层（技术项目经理、Scrum Master）。agents-android/（7 个）、agents-ios/（7 个）、agents-compute/（13 个）按技术栈的覆盖代理。将它们放入仓库的 .claude/agents/ 目录，它们就会用平台定制版本覆盖同名的通用代理。hooks/guard-commit.sh一个 Claude Code Bash 钩子（PreToolUse），阻止代理强制推送、以非人类身份提交、在提交信息中写入 AI 归属、或暂存明显的密钥。它守护的是 Claude 的 Git 命令——而不是人类在自己的终端中直接输入 git。hooks/format.sh按扩展名自动格式化已编辑的文件，覆盖所有技术栈。缺少格式化工具时静默跳过，绝不报错。skills/new-repo/一个脚手架技能：用正确的 CLAUDE.md、.gitignore、质量门禁和发布工作流创建新仓库。目前支持 Web + Android 脚手架；iOS 和计算栈以规则包 + 代理包形式提供（尚无脚手架）。docs/骨架文件按需指向的参考文档（完整代理阵容表、Phase-3 审查清单、错误恢复表、PR 模板、扩展性说明）。安装到 ~/.claude/docs/；仅在桩文件引用时才加载。templates/空白项目 CLAUDE.md 模板（通用版 + 计算版），可复制到新仓库中填写。examples/CLAUDE.example-web.md一个填好的示例，让你在动手之前看到「完成」是什么样子。STRUCTURE.md完整的目录结构、安装步骤以及双设置文件切换的工作原理。建议先读这个。

      核心理念：一段话概括
两层架构。全局层（~/.claude/CLAUDE.md + rules/ + agents/ + hooks/）包含所有无论你在构建什么项目都成立的内容。项目层是仓库根目录下的一个简短的 CLAUDE.md，只包含该项目的特定内容（§19：技术栈、质量门禁、发布指引、合规范围）。骨架文件会被提示缓存且永不更改；项目文件是每个仓库唯一需要编辑的东西。规则按路径触发专门化（当 Claude 读取匹配某个规则包 paths: 通配符的文件时，该包被加载）；代理按名称覆盖专门化（仓库的 .claude/agents/<name>.md 会覆盖同名的全局代理）。两者都不会预先扫描仓库。你只需配置一次，然后基本就不用管了。
安装
适用于 Mac/Linux，需要已安装 Claude Code。完整步骤和每个仓库的安装在 STRUCTURE.md[2] 中。首先安装钩子依赖 jq（没有它，guard-commit.sh 会安全失败拒绝运行）：brew install jq（macOS）/ sudo apt-get install jq（Debian/Ubuntu）。然后执行：

  git clone https://github.com/roadhero/claude-code-setup.git && cd claude-code-setup
mkdir -p ~/.claude/rules ~/.claude/agents ~/.claude/hooks ~/.claude/skills
cp CLAUDE.md      ~/.claude/CLAUDE.md
cp settings.json  ~/.claude/settings.json      # 自行合并你的模型/插件配置
cp rules/*.md     ~/.claude/rules/
cp agents/*.md    ~/.claude/agents/
cp -R agents-android agents-ios agents-compute ~/.claude/   # 各技术栈的代理包
cp hooks/*.sh     ~/.claude/hooks/ && chmod +x ~/.claude/hooks/*.sh
cp -R skills/new-repo ~/.claude/skills/
mkdir -p ~/.claude/docs && cp -R docs/* ~/.claude/docs/然后为每个仓库复制一个模板作为项目的 CLAUDE.md 并填写 §19 部分。查看 examples/ 目录获取完整示例。
一些诚实的说明
这套配置是个人化的，是为我的团队的工作方式构建的。Git 规则假设你使用基于 PR 的工作流和受保护分支。钩子假设格式化工具已安装（如果没装，它们会干净地跳过）。计算栈是 C++/CUDA/Python 的系统级工作，如果你只做 Web 应用就会显得大材小用。去掉你不需要的部分。重点不在于照搬我的配置，而在于看到一个真实可用的配置，然后构建你自己的。
更多
• 关于 Claude Code 的章节深入讲解了这一切背后的「为什么」——完整版见 Sub-Etha Press[3]
• 图书：《42：AI 构建者技术栈》，2026 年 8 月 15 日在 Amazon[4] 上线
• 其他样章见 eltexsoft.com[1]
MIT 许可证。随意使用、Fork、修改。无需署名。
引用链接
[1] EltexSoft: https://eltexsoft.com

[2] `STRUCTURE.md`: ./STRUCTURE.md

[3] Sub-Etha Press: https://subethapress.com

[4] Amazon: https://www.amazon.com/dp/B0H8WQZ7B8