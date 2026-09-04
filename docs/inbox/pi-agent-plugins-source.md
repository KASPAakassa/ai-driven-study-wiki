# 原始资料:我的 Pi Agent 插件清单

> 来源:微信公众号(作者:糖醋鱼哈),《我的 Pi Agent 插件清单》
> 原文链接:https://mp.weixin.qq.com/s/6E_cAjfnLFGlveCOdBHvXw
> 抓取日期:2026-08-09;状态:已整理为正式文章 docs/08-harness/pi-agent-plugins.md

---

我的 Pi Agent 插件清单
#Pi 是什么？
从官网 pi.dev 的介绍来看：Pi 是一个极简的 Agent 框架（minimal agent harness）。
它的核心理念是：你去适配 Pi，还是 Pi 适配你？ Pi 选择了后者。它不内置子智能体、不搞计划模式、没有权限弹窗、也没有内置的待办事项——这些统统留给用户自己组装。如果你需要某个功能，要么让 Pi 自己写一个，要么装个现成的包。
Pi 提供四种运行模式：交互式 TUI、打印/JSON 模式、RPC 进程集成、以及 SDK 嵌入。支持 15+ 模型供应商、数百个模型，会话以树结构存储，可以在任意节点回溯分支。
插件（Extensions）是 TypeScript 模块，可以访问 Pi 的全部工具、命令、快捷键、事件和 TUI 组件。插件可以打包成 Pi Package，通过 npm 或 git 分发：
pi install npm:@xxx/pi-xxx
pi install git:github.com/user/repo
#已安装插件
1. pi-cache-optimizer — 缓存优化
作用：稳定 Prompt 结构，提升 KV 缓存命中率。跨模型切换时自动适配不同供应商的缓存策略，对话末尾展示缓存统计。
使用场景：日常编码对话动辄几十轮，开启后第二次打开相同项目时响应明显变快，每月能省一笔 API 费用。
pi install npm:pi-cache-optimizer
2. pi-slopchop — 终端代码审查
作用：不用打开浏览器，在终端里就能审查代码 diff、加注释、生成修改建议，审查结果直接喂给 Pi 改代码。
使用场景：提 PR 之前先过一遍自己的改动，让 Pi 从 reviewer 视角找问题。配合 subagents 一起用，可以让子智能体自动审查。
pi install npm:pi-slopchop
3. pi-rtk-optimizer — 命令重写
作用：Pi 调用 bash 时自动拦截，把低效的 shell 命令重写成更优的等价命令。同时压缩工具输出（去 ANSI、截断、聚合测试输出、过滤构建日志），减少 Token 消耗。
使用场景：调试时同样的对话，以前 5-6 轮才能定位问题，现在 3-4 轮就够了，因为每次看到的是精简后的有效信息。
pi install npm:pi-rtk-optimizer
# 需要额外安装 rtk 二进制（>= 0.23.0）
cargo install rtk
# 或 brew install rtk
4. pi-subagents — 子智能体编排
作用：让 Pi 动态创建子智能体，支持链式执行（前一步输出自动成为下一步输入）和并行执行（多个子智能体同时干活）。
使用场景：大重构之前让两个子智能体并行跑——一个做代码质量审查，一个做安全审计。开发新功能时按链式执行：先分析需求、再输出设计、最后写代码，像流水线一样。
pi install npm:pi-subagents
5. pi-agent-browser-native — 浏览器自动化
作用：Pi 可以直接打开网页、截图、点击、填表单、运行 QA 检查。把浏览器控制能力注入到对话中。
使用场景：查最新 API 文档不用自己搜；部署完了让 Pi 自动打开线上页面检查控制台有没有报错。
pi install npm:pi-agent-browser-native
6. pi-mcp-adapter — MCP 协议适配器
作用：按照 MCP 标准协议连接任意 MCP 服务器，自动发现和注册其提供的工具，支持 OAuth 授权。
使用场景：搭一个 MCP 服务器连本地 MySQL，对话里直接让 Pi 查数据库，不用开数据库客户端。
pi install npm:pi-mcp-adapter
7. dcg-guard — 命令安全防护
作用：每次执行 bash 前先经过 dcg 评估，拦截有破坏性的命令（如 rm -rf）。采取 Fail-Open 策略，dcg 挂了不影响命令执行。
使用场景：让 Pi 批量重构时不怕误操作。有过一次 Pi 生成了 rm -rf，dcg 直接拦截并提示原因，避免了误删。
# dcg-guard 是本地扩展，需手动创建文件
# 将 dcg-guard.ts 放置到 ~/.pi/agent/extensions/ 目录下
pi reload
# 需要额外安装 dcg 二进制：brew install dcg
8. pi-hashline-edit-pro — 哈希锚点编辑
作用：为每一行代码生成唯一的 3 字符哈希锚点，所有编辑操作基于哈希而不是行号，消除行号偏移导致的误改。
使用场景：修改上千行的 K8s YAML 或 Terraform 模板时，行号会随文件变化偏移，哈希锚点不受影响，每次都能命中目标行。
pi install npm:pi-hashline-edit-pro
9. pi-add-dir — 外部目录接入
作用：加载外部目录的 AGENTS.md、CLAUDE.md 和技能文件，让 Pi 理解多个项目的上下文。
使用场景：微服务架构中前端、后端、基础设施分别在三个仓库，加载后 Pi 能在一次对话里理解完整的调用链，不再跨仓库时"断片"。
pi install npm:pi-add-dir
10. pi-workspace-history — 工作区撤销/重做
作用：在 Pi 当前会话中跟踪文件修改，支持一键撤销，类似 Claude Code 的 /rewind。
使用场景：TypeScript 重构时 Pi 批量改了 30+ 文件，类型定义冲突无法编译，一句"撤销刚才的修改"所有文件瞬间恢复。
pi install npm:pi-workspace-history
11. pi-autoresearch — 自主实验循环
作用：受 Karpathy 的 autoresearch 启发，让 Pi 自主提出假设、运行实验、测量结果，决定保留还是丢弃，循环迭代直到找到最优解。
使用场景：优化数据处理管道时，Pi 自动跑了 20 多轮实验，最终找到一个比原始方案快 3 倍的参数组合。中间只需要偶尔看看进度。
pi install npm:pi-autoresearch
#主题
@victor-software-house/pi-curated-themes
从 iTerm2-Color-Schemes 精选的暗色终端主题。夜间编程时切换到暗色主题，长时间编码舒适度提升不少。
pi install npm:@victor-software-house/pi-curated-themes
#管理命令
# 查看已安装的 npm 包
ls ~/.pi/agent/npm/node_modules/ | grep ^pi-

# 查看启用的扩展
ls ~/.pi/agent/extensions/

# 安装新插件
pi install npm:<package-name>

# 更新所有插件
pi update --extensions