# OpenCode 使用教程:小白从零到跑通开源 AI 编码 Agent

> **一句话摘要**:OpenCode(Anthropic 团队开源,"The open source AI coding agent")是一个终端里的开源 AI 编码 Agent——你描述需求,它自己读代码、改文件、跑命令、验证。特色是**双 Agent 模式**:`build`(默认,全权限,干活)+ `plan`(只读,先分析规划),Tab 一键切换;还内置 `general` 子 Agent 做复杂搜索。桌面版(BETA)让不碰命令行的人也能用。本教程面向小白,从安装到跑通第一个任务,30 分钟内上手。
>
> **来源**:OpenCode 官方仓库(https://github.com/anomalyco/opencode)与中文 README;官方文档:https://opencode.ai/docs;原始文件存档于 `references/opencode/`

## 第一步:OpenCode 是什么(大白话版)

想象一个**坐在你终端里的 AI 程序员**:
- 你对它说需求("修一下登录 bug"、"写个排序函数");
- 它自己**读项目代码 → 改文件 → 跑测试验证 → 汇报结果**;
- 你随时可以用 **Tab 键切换它的"工作模式"**:`build`(认真干活,能改文件)或 `plan`(只分析,不乱动代码);
- 它是**开源的**(代码全公开,可自己改),本地运行,数据不出你的电脑。

!!! tip "与其他编码 Agent 的区别"
    | 工具 | 特点 |
    | --- | --- |
    | Claude Code | Anthropic 官方,闭源为主 |
    | Cursor | 编辑器内 AI,商业产品 |
    | **OpenCode** | **开源**、终端 TUI、双 Agent(build/plan)模式 |
    | Reasonix(站内另一篇教程) | 开源、可长跑自治、配置驱动 |

## 第二步:安装(三种方式,选一个)

### 方式 1:一键安装(最简单)

```bash
curl -fsSL https://opencode.ai/install | bash
# 装好后重开终端,运行 opencode --version 验证
```

### 方式 2:包管理器(推荐)

```bash
npm i -g opencode-ai@latest      # Node.js 用户(也支持 bun/pnpm/yarn)
brew install anomalyco/tap/opencode   # macOS/Linux(推荐,始终最新)
scoop install opencode           # Windows
```

### 方式 3:桌面版(不碰命令行的选择,BETA)

从 https://opencode.ai/download 或 GitHub releases 下载安装包:
- macOS:`opencode-desktop-mac-arm64.dmg`(Apple 芯片)/ `-mac-x64.dmg`(Intel)
- Windows:`opencode-desktop-windows-x64.exe`
- Linux:`.deb` / `.rpm` / `.AppImage`

!!! warning "安装前注意"
    先移除 0.1.x 之前的旧版本;macOS 用 Homebrew 装桌面版:`brew install --cask opencode-desktop`。

## 第三步:第一次跑通(3 分钟)

### 1. 准备模型(OpenCode 支持各家模型)

```bash
# 登录模型提供商(任选其一):
opencode auth login          # 交互式选择并登录(Anthropic/OpenAI/Gemini/DeepSeek/本地模型等)
# 或设置环境变量:
export ANTHROPIC_API_KEY="sk-ant-xxx"   # 用 Claude 时
export OPENAI_API_KEY="sk-xxx"          # 用 OpenAI 时
export DEEPSEEK_API_KEY="sk-xxx"        # 用 DeepSeek 时
```

### 2. 启动并下达第一个任务

```bash
cd ~/my-project        # 进入你的项目目录
opencode               # 启动 TUI
```

出现终端界面后,直接输入:

```
帮我写一个 Python 函数:输入数字 n,返回斐波那契数列前 n 项,并配上单元测试
```

OpenCode 会**思考 → 写文件 → 跑测试 → 汇报**。完成后按 `Ctrl+C` 或输入 `/exit` 退出。

!!! success "跑通了吗?这就是 OpenCode 的基本用法!"

## 第四步:双 Agent 模式(OpenCode 的特色)

按 **Tab 键** 在两种 Agent 间切换:

| Agent | 模式 | 权限 | 适合 |
| --- | --- | --- | --- |
| **build** | 默认,干活 | **完整权限**(可改文件、跑命令) | 写代码、修 bug、重构 |
| **plan** | 只读,分析 | **默认拒绝改文件**;跑 bash 前会询问 | 探索陌生代码库、规划改动方案 |

!!! tip "推荐工作流:先 plan 后 build**
    拿到不熟悉的项目,先用 `plan` 模式问"这个项目怎么组织的?我要加个功能该改哪里?"——它只读不乱动;方案清晰后切 `build` 让它动手。

**general 子 Agent**:内置用于复杂搜索和多步任务,在消息里输入 `@general 你的问题` 调用。

## 第五步:日常怎么用(场景 + 常用命令)

### 三个场景

1. **写新功能**:直接对话,它写代码 + 测试;
2. **修 bug**:描述复现步骤,它定位 → 修复 → 验证;
3. **改造项目**:先 `plan` 摸清结构 → 切 `build` 动手。

### 常用命令速查表

| 命令 | 作用 |
| --- | --- |
| `Tab` | 切换 build / plan 模式 |
| `@general 问题` | 调用 general 子 Agent 做复杂搜索 |
| `/init` | 初始化/读取项目上下文(AGENTS.md 等) |
| `/status` | 查看会话/文件状态 |
| `/compact` | 压缩长对话上下文(省钱提速) |
| `/undo` | 撤销上一步操作(改错了回退) |
| `/tokens` | 查看 token 消耗 |
| `/share` | 分享会话(导出链接) |
| `/exit` | 退出 |

## 第六步:安全与权限(小白必读)

!!! warning "三条安全习惯"
    1. **不熟悉的项目先 plan**:让它在只读模式下分析,别一上来就 full 权限;
    2. **看它要跑什么命令**:bash 执行前留意内容,高危命令(删除、外部写)多确认;
    3. **敏感信息藏好**:不要把 API Key 明文写进项目文件;密钥用环境变量。

- OpenCode 的 build 模式权限完整——**就像给了实习生写权限,活干得快,但要看住**;
- plan 模式默认拒绝改文件、跑命令前询问——适合当"安全模式";
- 会话历史持久化(`~/.local/share/opencode/`),随时可查它做过什么。

## 第七步:进阶(了解即可)

- **模型配置**:`opencode models` 查看/切换;支持 Anthropic/OpenAI/Gemini/DeepSeek/本地模型(Ollama 等);
- **Skills / LSP**:支持自定义技能与语言服务器(LSP 补全/诊断);
- **API 模式**:OpenCode 提供 HTTP API(specs 见 `references/opencode/specs/`),可被其他程序调用;
- **桌面版同步**:桌面与 CLI 共享同一本地引擎与会话;
- **官方文档**:https://opencode.ai/docs(模型、工具、权限、自托管完整说明)。

## 代码 / 实现:双 Agent 模式模拟(纯 Python 演示)

把"plan 只读 + build 全权限"的权限差异落成可运行演示:

```python
# —— OpenCode 双 Agent 模式:build vs plan 的权限差异 ——
def agent_mode(mode: str, action: str) -> str:
    if mode == "plan" and action in ("write_file", "run_mutating_cmd"):
        return "拒绝:plan 模式只读,不能改文件/跑破坏性命令(可先切 build)"
    if mode == "plan":
        return "允许:plan 模式可以读文件、跑只读命令(git status/搜索)"
    return "允许:build 模式完整权限(写文件/跑命令)"

for mode, action in [("plan", "read_file"), ("plan", "write_file"), ("build", "write_file")]:
    print(f"  {mode:5} {action:14} → {agent_mode(mode, action)}")

assert agent_mode("plan", "write_file").startswith("拒绝")
assert agent_mode("plan", "read_file").startswith("允许")
assert agent_mode("build", "write_file").startswith("允许")
print("代码验证通过 ✔")
```

## 常见问题 FAQ

| 问题 | 解答 |
| --- | --- |
| 装完 `opencode` 找不到命令 | 重开终端;或检查安装路径(`$HOME/bin` / `$HOME/.opencode/bin` 是否在 PATH) |
| 提示模型未配置/认证失败 | `opencode auth login` 重新登录;检查 API Key 环境变量 |
| 界面是英文 | OpenCode TUI 当前以英文为主,官方文档有中文 README(https://github.com/anomalyco/opencode/blob/main/README.zh.md) |
| 它把代码改坏了 | `/undo` 撤销;有 git 的话 `git diff` 看改动后回滚 |
| 怎么让它别乱改文件 | 用 `plan` 模式(只读) |
| 烧 token 快 | `/tokens` 查看;长对话后 `/compact` 压缩 |
| 更多问题 | 官方 Discord:https://opencode.ai/discord;文档:https://opencode.ai/docs |

## 总结

- **它是什么**:开源 AI 编码 Agent(终端 TUI + 桌面版),本地运行,数据不出电脑;
- **怎么开始**:一键安装 → `opencode auth login` → 项目目录 `opencode` → 第一个任务;
- **核心特色**:**双 Agent**(Tab 切换 build/plan)+ general 子 Agent——先 plan 规划、再 build 动手;
- **安全习惯**:陌生项目先 plan、留意 bash 命令、密钥用环境变量;
- **一句话**:OpenCode 把"开源、本地、可控"三个词同时给到 AI 编码 Agent——**先跑通,再按需加深**。

## 延伸阅读

- 仓库:https://github.com/anomalyco/opencode;中文 README:https://github.com/anomalyco/opencode/blob/main/README.zh.md;文档:https://opencode.ai/docs;下载:https://opencode.ai/download
- 站内:[Harness 收录清单](index.md)(编码 Agent 工具索引)、[Reasonix 使用教程](reasonix-tutorial.md)(另一款开源编码 Agent,对照学习)、[给 Coding Agent 立规矩](../07-agent-coding/experience/agent-rules-agents-md.md)(AGENTS.md 与 build/plan 配合)
