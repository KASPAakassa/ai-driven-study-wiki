# Claude Code 隐藏技巧:创始人与社区的实用手册

> **一句话摘要**:从创始人 Boris Cherny 推特、社区和 changelog 中整理的 Claude Code 实用技巧,按八个主题聚合:**快捷键、实用命令与自动化、配置与诊断、上下文管理、输入与交互、会话管理、思考与模型控制**。每条技巧解决一个具体痛点,可直接用于日常开发。
>
> **来源**:Yu 的赛博工位笔记《Claude Code 隐藏技巧》系列 8 篇,https://yudesk.dev/docs/notes/claude-code-tips(及 /advanced、/commands-automation、/config-diagnostics、/context-management、/input-interaction、/session-management、/shortcuts、/thinking-model);原始内容存档于 `docs/inbox/yudesk-claude-code/`

## 一、快捷键(编辑器集成)

- **VS Code / Zed / Vim** 三种编辑器各有快捷键体系(切换对话、接受/拒绝 diff、打开侧栏等)——建议在对应编辑器扩展文档中查看完整列表,常用的记住几个:切换最近会话、快速接受建议、打开 agent 视图。

## 二、实用命令与自动化

| 技巧 | 用途 |
| --- | --- |
| 让 Claude 分析错误日志 | 贴日志 → 让 Claude 定位根因 |
| 让 Claude 总结最近的改动 | `git diff` 结果 → 生成变更摘要/commit message |
| 让 Claude 解读命令输出 | 跑命令 → 让 Claude 解释结果含义 |
| **设置花费上限**(超过就停) | 防止 token 失控 |
| **限制对话轮数** | 防止无限循环 |
| **输出 JSON 格式**(方便程序解析) | `--output-format json` 类参数 |
| **要求输出符合特定 JSON Schema** | 结构化输出保证 |
| **多轮 headless 对话**(用 session-id 保持上下文) | 脚本化调用 Claude |
| **指定备用模型**(主模型过载自动切换) | 高可用 |
| **限制可用工具** | 减少工具噪音 |
| **完全替换系统提示词** | 高级定制 |

!!! note "自动化三个常见需求"
    ①分析错误日志(定位根因);②总结最近改动(变更摘要);③解读命令输出(结果解释)——都是"让 Claude 处理命令产物"的高频用法,可封装为 Commands 或 Skill 复用。

## 三、配置与诊断

- 查看当前配置与权限模式(permission mode);
- 诊断 Hook/Skill/MCP 加载问题(检查路径、配置项);
- 排查"工具不生效"类问题(配置路径错误、版本不匹配);
- 用 `/doctor` 或类似命令检查环境健康度。

## 四、上下文管理

!!! tip "Compact Instructions(压缩指令)**
    上下文接近窗口上限时,Claude Code 会自动压缩历史对话。技巧:**自定义 compact instructions**——告诉 Claude 压缩时保留哪些关键信息(当前任务、关键决策、未完成事项),避免压缩后丢失重要上下文。

其他技巧:定期 `/compact` 主动压缩、把长文件用 Read 分页而非全量、工具结果过大时主动截断。

## 五、输入与交互

- 多行输入的处理技巧;
- 中断/恢复当前回复(ESC);
- 对话中切换主题的上下文管理;
- 粘贴长文本/代码块的格式注意(避免触发误操作)。

## 六、会话管理

| 命令/技巧 | 用途 |
| --- | --- |
| 恢复当前目录最近的会话 | 断线续聊 |
| 打开会话选择器 / 按名称恢复 | 多会话切换 |
| 启动时直接命名会话 | 便于后续查找 |
| **Fork 上一次会话**(保留上下文,创建新分支) | 尝试新方向不丢原上下文 |
| 恢复与特定 PR 关联的会话 | 按 PR 找上下文 |
| **在隔离的 git worktree 中启动** | 并行任务隔离(呼应 [Worktree](claude-worktree-teams.md)) |

## 七、思考与模型控制

- 控制 reasoning effort / thinking budget(思考强度);
- 指定模型与备用模型;
- 限制思考 token 预算(成本控制);
- 完全替换系统提示词的高级用法。

## 代码 / 实现:命令自动化小工具(纯 Python)

把"分析错误日志 / 总结改动 / 解读输出"三个高频需求落成 CLI 骨架:

```python
# —— Claude Code 自动化的三个高频姿势 ——
def analyze_log(log_text: str) -> str:
    """姿势 1:分析错误日志——定位根因"""
    return f"分析日志({len(log_text)} 字符):定位异常模式与根因建议"

def summarize_changes(diff_text: str) -> str:
    """姿势 2:总结最近改动——生成变更摘要"""
    return f"变更摘要({len(diff_text)} 字符 diff):提取改动要点与影响"

def interpret_output(cmd_output: str) -> str:
    """姿势 3:解读命令输出——解释结果含义"""
    return f"解读输出({len(cmd_output)} 字符):解释结果与下一步建议"

for fn, arg in [(analyze_log, "ERROR: timeout in db-conn"),
                (summarize_changes, "+login -logout"),
                (interpret_output, "3 passed, 1 failed")]:
    print(f"  {fn.__name__} → {fn(arg)}")
```

## 实践 / 应用:技巧使用建议

1. **先配成本护栏**:花费上限 + 对话轮数限制 + token 预算——防止失控(呼应 [5 个决策](../../03-agents/agent-system-5-decisions.md) 的成本熔断);
2. **自动化三件套**(分析日志/总结改动/解读输出)封装为 Commands 或 Skill,高频复用;
3. **会话管理靠习惯**:命名会话 + Fork + 按 PR 恢复——长任务不断线;
4. **上下文纪律**:主动 compact + 自定义压缩指令 + 工具结果截断——呼应 [Context Engineering](../../03-agents/context-engineering.md);
5. **worktree 启动并行任务**——多任务隔离(呼应 [Worktree 篇](claude-worktree-teams.md))。

## 总结

- **八个主题**:快捷键 / 命令与自动化 / 配置诊断 / 上下文 / 输入交互 / 会话 / 思考模型;
- **三条高频姿势**:分析错误日志、总结最近改动、解读命令输出——可 Skill 化;
- **三个成本护栏**:花费上限、对话轮数、思考 token 预算;
- **一句话**:隐藏技巧的价值不在单个命令,而在**把高频操作固化成习惯与自动化**(Commands/Skill),让 Claude Code 越用越顺。

## 延伸阅读

- 原页面:https://yudesk.dev/docs/notes/claude-code-tips(及 7 个子页面)
- 站内:[Claude Code 架构与工具系统](claude-architecture-tools.md)、[Worktree 与 Agent Teams](claude-worktree-teams.md)、[Skills/Plugin/Subagent](claude-skills-plugin-subagent.md)(本子主题其他篇);[Context Engineering](../../03-agents/context-engineering.md)、[Agent 系统设计的 5 个决策](../../03-agents/agent-system-5-decisions.md)
