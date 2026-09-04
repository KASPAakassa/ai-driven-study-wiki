# Reasonix 使用教程:小白从零到跑通编码 Agent

> **一句话摘要**:Reasonix(DeepSeek-Reasonix,开源 · MIT · 单个 Go 二进制)是一个**可以一直开着跑的编码 Agent 引擎**——给它一个任务,它自己读代码、改文件、跑命令、验证结果,把活干完。一套本地引擎,四个入口:终端、桌面端、浏览器、编辑器(ACP)。本教程面向**完全没接触过编码 Agent 的小白**,从"它是什么"讲到"第一次跑通""日常怎么用""安全与权限",最后给常见问题——跟着做,30 分钟内跑起来。
>
> **来源**:Reasonix 官方仓库(https://github.com/esengine/deepseek-reasonix)与中文文档(README.zh-CN / GUIDE.zh-CN / CLI.zh-CN / CHECKPOINTS.zh-CN / TOOL_APPROVAL_MODES.zh-CN 等);原始文件存档于 `references/reasonix/`

## 第一步:Reasonix 是什么(大白话版)

想象你请了一个**实习生**,他会:
- 听懂你的需求("帮我修一下登录 bug");
- 自己看代码、找问题、改文件、跑测试验证;
- 干完活向你汇报,中间每一步**都记了账(日志),做错了还能撤销(checkpoint)**;
- 你不在的时候,他也能**自己一直干**(长时间自治运行),你回来检查结果。

Reasonix 就是这样一个"AI 实习生",区别是它跑在你自己的电脑上(本地引擎),**只有一个小程序文件,不用装一堆依赖**。

!!! tip "四个入口,同一个引擎"
    | 入口 | 适合谁 | 怎么进 |
    | --- | --- | --- |
    | **终端(CLI/TUI)** | 程序员、喜欢命令行 | `reasonix` 直接启动 |
    | **桌面端** | 不想碰命令行的小白 | 官网下载安装包,点开就用 |
    | **浏览器(Serve)** | 远程访问 | `reasonix serve` → 浏览器打开 |
    | **编辑器(VS Code 扩展)** | 写代码时顺手用 | 装扩展,走 ACP 接入 |

## 第二步:安装(三条路,选一条)

!!! warning "先搞定一件事:API Key"
    Reasonix 需要调用大模型(默认 DeepSeek)。先去 DeepSeek 开放平台注册拿一个 `API Key`(形如 `sk-xxxxxxxx`),后面要用。

### 路线 A:终端安装(最常用,推荐)

```sh
# 任选其一:
npm i -g reasonix          # 任意系统,自动下载对应平台程序(需要已装 Node.js)
brew install esengine/reasonix/reasonix   # macOS 用户(需要 Homebrew)

# 验证安装成功:
reasonix --version
# 应该打印出版本号,例如 v1.x.x
```

### 路线 B:桌面端(不想碰命令行)

打开官方下载页 https://reasonix.io/?download=desktop#start,下载对应系统的安装包(macOS 的 `.dmg` / Windows 的 `.exe` / Linux 的 `.deb`),双击安装即可。**界面是图形化的,设置模型、审批工具都在菜单里点。**

### 路线 C:VS Code 扩展(写代码时用)

1. 先按路线 A 装好 CLI(扩展不内置引擎,它调用本机的 `reasonix acp`);
2. VS Code 扩展市场搜索 `SivanLiu.reasonix-agent` 安装;
3. 打开命令面板(Cmd/Ctrl+Shift+P)→ 输入 "Reasonix" → 选 "Start Session"。

## 第三步:第一次运行(3 分钟跑通)

### 1. 告诉 Reasonix 用哪个模型(配置 API Key)

最简单的方式,在终端设置环境变量:

```sh
export DEEPSEEK_API_KEY="sk-你的密钥"
# macOS/Linux 想永久生效,把它写进 ~/.zshrc 或 ~/.bashrc
```

!!! note "密钥安全"
    **不要把 API Key 写进 `reasonix.toml` 配置文件**——配置文件里只写环境变量名(`api_key_env = "DEEPSEEK_API_KEY"`),密钥值存在 Reasonix 的全局 `.env` 里。

### 2. 启动并下达第一个任务

```sh
# 进入你的项目目录(比如 ~/my-project)
cd ~/my-project
reasonix
```

出现交互界面后,输入:

```
帮我写一个 Python 函数:输入一个数字 n,返回斐波那契数列的前 n 项
```

看它干活:Reasonix 会**思考 → 写文件 → 跑测试验证 → 汇报结果**。完成后,输入 `/exit` 退出。

!!! success "恭喜,你已经跑通了 Reasonix!"

## 第四步:配置文件 reasonix.toml(小白版讲解)

Reasonix 是"配置驱动"的——**模型、工具、权限都写在配置文件里,代码里没有写死的模型**。首次运行时它会在项目目录生成 `reasonix.toml` 模板。下面用大白话解释每个部分是干嘛的:

```toml
default_model = "deepseek"          # 默认用哪个模型(写 provider 的名字)

[agent]
temperature = 0.0                   # 0 = 最严谨(推荐);数字越大越"有创意"越不稳定
soft_compact_ratio = 0.5            # 上下文到 50% 时提醒;到 80%/90% 自动压缩历史
# planner_model = "deepseek-pro"    # 打开后:一个模型当"规划器",一个当"执行器"(双模型)

[[providers]]                       # 模型供应商(可以有多个)
name = "deepseek"                   # 名字,default_model 引用它
kind = "openai"                     # 类型:openai 兼容 / anthropic
base_url = "https://api.deepseek.com"  # API 地址
models = ["deepseek-v4-flash", "deepseek-v4-pro"]  # 可用的模型列表
api_key_env = "DEEPSEEK_API_KEY"    # 密钥从哪个环境变量读(不要直接写密钥!)

[environment]
enabled = true                      # 启动时给模型注入系统环境摘要(OS/工具),回答更准

[tools]
enabled = []                        # 空 = 启用全部内置工具;可以只留白名单

[sandbox]                           # 沙箱:限制 Agent 能碰什么(安全关键!)
# workspace_root = ""               # 文件写工具只允许改这个目录;空 = 当前目录
# allow_write = ["/tmp"]            # 额外允许写的目录
# forbid_read = ["${HOME}/.ssh"]    # 禁止读的敏感目录
```

!!! tip "想换模型?改一行"
    想用 Claude?在 `[[providers]]` 加一个 `claude` 条目(参照模板里的 Anthropic 示例),然后 `default_model = "claude"`。想用自己的 OpenAI 兼容服务?照抄 `openai-compatible-custom` 示例改地址即可。

## 第五步:日常怎么用(三个核心场景)

### 场景 1:写代码(最简单)

直接对话就行——"写一个二分查找函数,带单元测试"。Reasonix 会写文件、跑测试、确认通过。

### 场景 2:改 bug

```
修复登录页的报错。复现步骤:输入错误密码会崩溃,而不是提示错误。
```

它会自己:看报错 → 定位代码 → 修复 → 跑测试验证 → 汇报。

### 场景 3:长时间自主任务(重点功能)

Reasonix 的核心卖点是"**可以留它一直跑**"。跑长任务前,建议:

1. **开计划模式**(按 `Shift+Tab`):它先给方案,你确认后它才动手;
2. **看权限审批**:高危操作(删文件、改生产配置)会弹确认,你同意才执行;
3. **依赖 checkpoint**:每一步都有检查点,跑坏了随时 `/checkpoint` 回退到之前的干净状态;
4. **放心离开**:后台任务、长链路它会自己推进,你回来检查结果即可。

### 常用命令速查表

| 命令 | 作用 |
| --- | --- |
| `/plan` | 切换计划模式(先方案后动手) |
| `/yolo` | 切换"全自动模式"(不逐个确认,高危操作除外,谨慎用) |
| `/permissions` | 查看/修改工具权限 |
| `/checkpoint` | 查看/回退到历史检查点 |
| `/compact` | 手动压缩上下文(长对话后) |
| `/skill` | 管理技能(list/show/new) |
| `/mcp` | 管理 MCP 服务器连接 |
| `/usage` | 查看 token 消耗与费用 |
| `/exit` | 退出 |

## 第六步:安全与权限(小白必读)

!!! warning "三条安全习惯"
    1. **日常用 Plan 模式**:先看方案再让它动手,避免它自作主张;
    2. **高危操作一定人工确认**:删除、外部写、大额操作会触发审批——不要无脑放行;
    3. **敏感目录藏起来**:在 `[sandbox]` 里 `forbid_read = ["${HOME}/.ssh", "${HOME}/.aws"]`,让 Agent 碰不到密钥。

- **工具审批模式**:`default`(未匹配的工具询问)/ `dontAsk`(不预批准的拒绝)/ `acceptEdits`(自动批准文件编辑)/ `bypassPermissions`(全部放行,慎用);
- **Checkpoint**:每次工具调用前自动快照文件状态,`/checkpoint` 可回退——**这就是"跑错了能撤销"的保障**;
- **沙箱**:`workspace_root` 限制写文件范围、`forbid_read` 隐藏敏感目录、bash 可强制沙箱(macOS/Linux 默认开)。

## 第七步:进阶(了解即可,不用现在学)

- **接入编辑器**:VS Code / VSCodium 装扩展走 ACP 协议,编辑器里直接聊天、审批工具调用;
- **接入 IM 机器人**:QQ/飞书/微信机器人(`reasonix bot start --channels qq,feishu,weixin`),在群里给 Agent 派活(注意配置 allowlist 白名单);
- **远程使用**:`reasonix serve` 启动 Web 前端,浏览器远程访问(可配 token/密码认证);
- **自定义技能(Skills)**:把常用工作流写成 SKILL.md 放进 `.reasonix/skills/`,`/<名字>` 调用;
- **插件与 MCP**:MCP server 提供工具/提示/资源,插件可拦截运行时事件(扩展协议 v1)。

## 代码 / 实现:启动前检查器(纯 Python 演示)

把"配置 + API Key + 沙箱"的检查逻辑落成可运行演示,理解 Reasonix 启动前会确认什么:

```python
# —— Reasonix 启动前检查:配置完整性 ——
def preflight(config: dict, env: dict) -> list:
    issues = []
    if not config.get("default_model"):
        issues.append("缺少 default_model(默认模型)")
    provider = next((p for p in config.get("providers", [])
                     if p["name"] == config.get("default_model")), None)
    if not provider:
        issues.append(f"default_model 指定的 provider 未定义")
    else:
        key_env = provider.get("api_key_env", "")
        if key_env and not env.get(key_env):
            issues.append(f"环境变量 {key_env} 未设置(去模型平台申请 API Key)")
        if key_env and "sk-" not in env.get(key_env, ""):
            issues.append(f"{key_env} 看起来不像有效密钥(应以 sk- 开头)")
    return issues or ["检查通过:可以启动"]

config = {"default_model": "deepseek",
          "providers": [{"name": "deepseek", "api_key_env": "DEEPSEEK_API_KEY"}]}
print("有密钥:", preflight(config, {"DEEPSEEK_API_KEY": "sk-123"}))
print("无密钥:", preflight(config, {}))
assert preflight(config, {"DEEPSEEK_API_KEY": "sk-123"}) == ["检查通过:可以启动"]
assert any("未设置" in i for i in preflight(config, {}))
print("代码验证通过 ✔")
```

## 常见问题 FAQ

| 问题 | 解答 |
| --- | --- |
| 启动报"找不到模型/认证失败" | 检查 `DEEPSEEK_API_KEY` 是否设置且有效;`echo $DEEPSEEK_API_KEY` 看是否为空 |
| 界面全是英文 | 配置 `language = "zh"`(或 `REASONIX_LANG=zh`) |
| 它一直干不完/烧钱 | 按 `Esc` 中断;看 `/usage`;日常用 Plan 模式 + 权限审批 |
| 它改了我的文件我不满意 | `/checkpoint` 回退到之前的检查点 |
| 想让它别碰某些目录 | `[sandbox]` 里配置 `forbid_read` / `workspace_root` |
| 装完 `reasonix` 命令找不到 | 重开终端;或确认 npm 全局 bin 在 PATH 里 |
| 更多问题 | 官方双语 Discord:`#help` / `#求助`(https://discord.gg/XF78rEME2D) |

## 总结

- **它是什么**:一个能自己一直干活的编码 Agent 引擎(本地、单文件、配置驱动);
- **怎么开始**:装(三条路)→ 设 API Key → `reasonix` 跑通第一个任务;
- **日常三场景**:写代码 / 改 bug / 长任务(Plan + 审批 + checkpoint);
- **安全三习惯**:Plan 模式、高危确认、藏敏感目录;
- **一句话**:Reasonix 让"把活交给 AI 实习生"变得可读、可控、可撤销——**先跑通,再按需加深**。

## 延伸阅读

- 仓库:https://github.com/esengine/deepseek-reasonix;中文 README/GUIDE 存档于 `references/reasonix/`;官方文档:https://esengine.github.io/DeepSeek-Reasonix/
- 站内:[Harness 收录清单](index.md)(Reasonix 定位:可留它一直跑的编码 Agent Harness)、[给 Coding Agent 立规矩](../07-agent-coding/experience/agent-rules-agents-md.md)(CLAUDE.md/AGENTS.md 配合)、[AI 协作规则设计](../03-agents/agent-collaboration-rules.md)(先跑起来再长护栏)
