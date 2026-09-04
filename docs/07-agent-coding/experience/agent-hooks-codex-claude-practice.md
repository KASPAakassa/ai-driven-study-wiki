# Agent Hook 实战:Codex 与 Claude Code 双框架配置、安全编写与落地清单

> **一句话摘要**:Hook 是 AI Agent 的"自动执行工程规则"机制——在 Agent 工作流关键节点(用户提交 prompt 前 / 调用 shell 前 / 修改文件后 / 请求权限时 / 准备结束前 / 上下文压缩前后 / 子 Agent 启停时)自动触发预先配置的脚本、HTTP 请求、规则检查或提示逻辑。本文是**实战篇**:Codex 与 Claude Code 两套主流 hook 体系的具体配置、hook 安全编写 15 条、落地分级清单(最小三 hook),并与站内设计/原理两篇互补。
>
> **来源**:微信公众号「良辰AI私房菜」《AI Agent Hook 深度解析:概念、用法、优缺点与 AI Coding 实践》,https://mp.weixin.qq.com/s/gUkGHRLsIXzfok7gSL0AdQ;原始资料存档于 `docs/inbox/agent-hooks-practice-source.md`;官方文档:Codex Hooks https://github.com/openai/codex/blob/main/docs/hooks.md、Claude Code Hooks https://code.claude.com/docs/en/hooks

## 概念:Hook 是什么、为什么重要

**Hook** 可理解为:在 Agent 工作流程的关键节点,自动触发你预先配置的脚本、HTTP 请求、规则检查或提示逻辑。类似后端开发里的 Spring Interceptor / Servlet Filter / AOP Before-After Advice / Git pre-commit / CI pipeline stage / 数据库 trigger——区别是**拦截的是 Agent 的工作生命周期**,而非普通 HTTP 请求。

**AI Coding 场景里 Hook 的核心价值**:把团队工程规范、安全策略、自动校验、上下文注入、日志审计,从"靠人提醒"变成"自动执行"。

**为什么只靠 prompt 不够**:现代 AI Coding Agent 会读文件、改文件、运行命令、安装依赖、启动服务、调 MCP 工具、创建子任务、总结上下文、请求权限、甚至自动提交 PR——模型可能忘记团队规范、没跑必要测试、误读项目上下文、执行高风险命令。**只靠 prompt 约束是不够的**。

**Hook vs AGENTS.md / CI-CD 的关系**:

| 层 | 作用 | 执行时机 |
| --- | --- | --- |
| AGENTS.md / CLAUDE.md | **说明书**:告诉模型"应该怎么做"(软约束,靠模型自觉) | 启动时加载 |
| Hook | **执行器**:强制规则"必须怎么做"(确定性,自动触发) | 工作流关键节点 |
| CI/CD | **兜底**:合并前校验(最外层保障) | PR / 合并时 |

> **本质分层**:AGENTS.md 是"意图",Hook 是"强制执行",CI/CD 是"最后防线"。Hook 把团队工程规范从"prompt 里的一句提醒"变成"无法绕过的自动检查"。

## 代码 / 实现:Codex Hooks 实战

### 配置位置与结构

```bash
~/.codex/config.toml    # 全局配置
~/.codex/hooks.json     # 全局 hooks
$PROJECT/.codex/hooks.json   # 项目级 hooks(优先推荐,随仓库走)
```

hook 分三层:**matched hooks**(按 matcher 匹配的钩子)、**stopped hooks**(Agent 停止时)、**subagent hooks**(子 Agent 专属),可在 `[features] codex_hooks = true` 下启用。

### 三层结构

1. **matched hooks**:按 `matcher`(事件 + 可选工具名)匹配,是最常用的一层。事件包括 `PromptCreated`、`PromptTranscribed`、`PreToolUse`、`PostToolUse`、`SessionStart`、`ChatCompletionRequested` 等;每个 hook 有三个执行阶段——`pre`(解析输入/决定是否执行)、`exec`(执行脚本/HTTP 请求)、`post`(解析输出/生成阻断或提示消息);

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|apply_patch",
        "hooks": [
          { "type": "command", "command": "bash \"$(git rev-parse --show-toplevel)/.codex/hooks/check-lint.sh\"" }
        ]
      }
    ]
  }
}
```

2. **stopped hooks**:任务结束(Success/Failure/Interrupted/ExceededBudget)时触发,适合做收尾审计、生成任务摘要、通知;
3. **subagent hooks**:子 Agent 专用,控制子 Agent 的启停与行为。

### 能力边界(重要)

- **修改 Agent 行为**:`permissionDecision`(allow / deny / ask)、`stopReason`(阻断/继续);
- **注入系统提示**:`systemMessage`(追加到模型上下文,如"你已越界,请回到主题");
- **读取会话信息**:`sessionID`、`conversationID`、`transcriptPath`(会话记录);
- **注意**:hook 不能直接修改 Agent 历史消息,但可通过注入 systemMessage 和 permissionDecision 间接控制。

## 代码 / 实现:Claude Code Hooks 实战

### 配置位置与作用域

```json
// ~/.claude/settings.json      全局(所有项目)
// .claude/settings.json       项目级(推荐,团队共享,进 Git)
// .claude/settings.local.json 本地个人(个人偏好,gitignore)
```

### 核心事件

| 事件 | 触发时机 | 常用用途 |
| --- | --- | --- |
| `PreToolUse` | 调用工具前 | **危险命令拦截**(rm -rf/DROP TABLE/force-push)、权限决策 |
| `PostToolUse` | 工具执行后 | 自动 lint/typecheck、校验产物 |
| `UserPromptSubmit` | 用户提交 prompt 后 | 密钥扫描、敏感信息检查 |
| `Stop` | Agent 准备结束 | 结束前质量检查(是否跑过测试) |
| `PreCompact` | 上下文压缩前 | 保存关键状态防丢失 |
| `SubagentStart` / `SubagentStop` | 子 Agent 启停 | 子 Agent 角色约束、任务摘要 |
| `SessionStart` | 会话开始 | 注入项目上下文 |
| `Notification` | 通知事件 | 异步通知 |

### 示例脚本(命令型 hook)

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/check-dangerous.sh",
            "timeout": 5
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/verify-tests.sh" }
        ]
      }
    ]
  }
}
```

**脚本输出控制**(通过 stdout JSON 决定行为):

```bash
# PreToolUse:拦截危险命令
echo '{"permissionDecision": "deny", "reason": "禁止删除 .env 文件"}'
# 或放行但提示
echo '{"permissionDecision": "allow", "systemMessage": "注意:此命令会修改生产配置"}'
# PostToolUse 校验失败
echo '{"hookSpecificOutput": {"hookEventName": "PostToolUse", "decision": "block", "reason": "lint 未通过"}}'
```

**async hooks**:`"type": "async"` 的命令不阻塞 Agent(如记日志、后台通知),但注意 stdout 不会被解析为控制指令。

!!! warning "Claude Code hook 安全提醒"
    hook 输入来自不可信工具输出,输出会注入模型上下文——**不要信任 hook 输入**;`permissionDecision: deny` 阻止工具调用但不取消 LLM 已生成的其余输出;`.claude/settings.json` 改动需重启会话生效,避免 hook 中途被篡改。

## 原理:Hook 安全编写 15 条

hook 自己就是可执行代码,必须按生产脚本标准写:

1. **始终使用非交互 shell**:`#!/usr/bin/env bash` + `set -euo pipefail`;
2. **给 hook 合理超时**:`"timeout": 10`,避免卡死 Agent;
3. **输出不能太吵**:hook stdout 会进入 Agent 上下文,只输出结论/关键错误/下一步建议,日志全文写文件;
4. **JSON 输出必须格式正确**:一行有效 JSON,非法输出被忽略或触发降级;
5. **收到 JSON 参数必须校验**:hook 收到的是 Agent 的输入,可能存在意外字段;
6. **变量必须加引号**:`rm -rf "$TARGET"`(错误: `rm -rf $TARGET`);
7. **路径必须校验**:检查是否为空、是否包含 `..`、是否指向 repo 外、是否命中敏感路径;
8. **小心 git 命令**:`git reset --hard` / `git clean -fd` 是高危操作,默认拒绝;
9. **不要在 hook 里存密钥**:日志和上下文都可能泄露;
10. **明确 fail 策略**——安全 hook 解析失败应 **fail closed**(拒绝高风险操作),辅助 hook 可 **fail open**(只记录 systemMessage,不阻断);
11. **Hook 只能访问需要的文件**:不要给 hook 全盘读取权限;
12. **避免递归调用**:hook 里调用 Agent 命令可能再次触发 hook;
13. **隔离环境**:hook 在 Agent 进程外运行,但注意环境变量继承;
14. **记录审计日志**:输入摘要、匹配规则、输出决策、耗时;
15. **hook 变更走版本管理**:配置和脚本都进 Git。

## 实践 / 应用:哪些场景适合、落地分级

### 适合用 Hook

安全拦截、敏感信息扫描、测试门禁、lint/typecheck 自动反馈、项目上下文自动加载、命令审计、Agent 结束前质量检查、子 Agent 角色约束、自动生成任务摘要。

### 不适合用 Hook

复杂业务决策(需要 LLM 判断的)、需要大量上下文的逻辑(hook 环境信息有限)、需要人类情感判断的场景。

### 落地分级清单

**初级**(单人或小团队):
- PreToolUse 拦截危险命令和敏感路径;
- UserPromptSubmit 扫描密钥和敏感信息;
- Stop 前检查是否跑过必要检查。

**中级**:
- 改 API 类型后跑前后端契约检查;
- 记录 Agent 命令失败原因;
- PostToolUse 自动跑 lint/typecheck。

**高级**(企业 managed hooks):
- 统一 hook 脚本包或插件;
- hook 事件日志入审计系统;
- 结合 MCP 做代码所有权、工单、PR 检查;
- 根据失败数据自动改进 Agent 指令;
- Stop hook 接入轻量 eval。

### 推荐的最小三 hook(覆盖最核心问题)

1. **PreToolUse:危险命令和敏感路径拦截**(别乱执行);
2. **UserPromptSubmit:密钥和敏感信息扫描**(别泄密);
3. **Stop:任务结束前验证是否跑过必要检查**(别半成品结束)。

## 总结

- **本质**:Hook = 在 Agent 工作流关键节点自动触发预配置逻辑——把工程规范、安全策略、自动校验从"靠人提醒"变"自动执行";
- **分层**:AGENTS.md 是说明书(软约束)/ Hook 是执行器(强制)/ CI/CD 是兜底;
- **Codex**:`~/.codex/hooks.json` + 项目 `.codex/hooks.json`,三层结构(matched/stopped/subagent),permissionDecision + systemMessage 控制;
- **Claude Code**:`.claude/settings.json` 三作用域,核心事件 PreToolUse/PostToolUse/UserPromptSubmit/Stop/PreCompact,stdout JSON 控制;
- **安全 15 条**:非交互 shell、超时、输出短、JSON 正确、变量引号、路径校验、fail closed/open 明确;
- **落地**:最小三 hook(PreToolUse 拦截 + UserPromptSubmit 扫密 + Stop 验证);hook 不是银弹——不能替代人类 review、CI 和权限隔离;
- **与站内关系**:本文是**实战配置篇**,与 [Agent 治理 Hook](../../03-agents/agent-governance-hooks.md)(设计角度:offload/HITL/state-Attachment 三道护栏)和 [Agent Hook 使用指南](agent-hooks-usage.md)(原理角度:五切面/8 模式/框架对比)互补;
- **下一步**:对照 [Agent Hook 使用指南](agent-hooks-usage.md) 的五切面原理,或看 [给 Coding Agent 立规矩](agent-rules-agents-md.md)(AGENTS.md 层)理解三层治理的完整链条。

## 延伸阅读

- 官方文档:Codex Hooks https://github.com/openai/codex/blob/main/docs/hooks.md;Claude Code Hooks https://code.claude.com/docs/en/hooks
- 原文:https://mp.weixin.qq.com/s/gUkGHRLsIXzfok7gSL0AdQ
- 站内:[Agent 治理:用 Hook 堵住偷懒、越权与失忆](../../03-agents/agent-governance-hooks.md)(设计角度)、[Agent Hook 使用指南(切面机制)](agent-hooks-usage.md)(原理角度)、[给 Coding Agent 立规矩](agent-rules-agents-md.md)(AGENTS.md 层)、[Context Engineering 官方资料](../../03-agents/context-engineering-official-sources.md)(Claude Code hooks 在上下文管理中的角色)
