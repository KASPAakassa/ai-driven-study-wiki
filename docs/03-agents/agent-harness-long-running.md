# Effective harnesses for long-running agents:跨上下文窗口的多窗口工作流

> **一句话摘要**:长时 agent 的真正问题是**跨 context window 无记忆**(类比工程师换班)。Anthropic 给出可照抄的双 agent 方案:initializer agent(首窗口写 `init.sh` + `claude-progress.txt` + `feature_list.json` + 初始 commit)+ coding agent(每个窗口只做增量,结束时 git commit + 更新进度)——用文件系统当跨窗口记忆,每会话从"读进度→挑一个 feature→冒烟测试"开始。配 Puppeteer MCP 端到端自测。
>
> **来源**:Anthropic Engineering《Effective harnesses for long-running agents》(https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents,2025-11-26)

## 概念

### 问题:跨 context window 无记忆

长时 agent(几小时到几天的任务)的核心障碍:**context window 有上限,一次窗口装不下整个任务**。窗口耗尽后,agent 对之前的上下文"失忆"——就像工程师换班,新班次的人不知道上一班做到哪、做过什么、还差什么。

两个典型失败模式:

1. **一次性硬撸整个应用**:在单个 context window 里从头到尾,中途耗尽上下文,任务烂尾;
2. **过早宣布完成**:agent 在一个窗口里"感觉做完了"就声称完成,实际没验证完整功能。

### 类比:工程师换班制

解决方式借鉴真实工程交接:**文件系统成为跨窗口记忆**。每个窗口结束时把状态落盘(git commit + 进度文件),下个窗口从文件恢复——不依赖模型"记得",而是**每次都能从磁盘读到事实**。

## 原理(双 agent 方案)

### 角色一:Initializer agent(初始化器,首窗口)

在第一个 context window 里完成"开工准备":

- 写 **`init.sh`**:环境搭建 + 冒烟测试脚本,后续每个会话都先跑它验证环境可用;
- 写 **`claude-progress.txt`**:人类可读的进度日志(做了什么、下一步是什么);
- 写 **`feature_list.json`**:结构化功能清单(机器可读,模型不易误改);
- 做初始 **git commit**:建立基线。

### 角色二:Coding agent(编码 agent,每窗口只做增量)

每个 context window 结束时:

- **git commit**(把增量固化成文件系统状态);
- 更新 `claude-progress.txt` 和 `feature_list.json`(记录进度)。

**每个会话开始时的固定流程**:

```
1. pwd(确认位置)
2. 读 git log / claude-progress.txt(上次做到哪)
3. 读 feature_list.json,挑一个 feature(任务范围)
4. 跑 init.sh 做冒烟测试(环境是否可用)
```

### 关键设计:feature_list.json 的"只许改 passes"约束

- feature list 用 **JSON** 而非自然语言 markdown——**模型不易误改结构**;
- 初始所有 feature 标记为 `"failing"`(未完成);
- **只允许修改 `passes` 字段**(从不允许改成真);
- 强指令:**禁止删改测试**——防止 agent 为了"通过"而删测试/改测试作弊。

### 验证:端到端自测

用 **Puppeteer MCP** 做浏览器端到端自测(真实用户路径),而非只信模型自述。已知局限:Puppeteer MCP 看不到浏览器原生 `alert` 弹窗——这类场景需额外处理。

## 代码 / 实现

三件套脚手架(可直接照抄,配套 quickstart:`github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding`):

```bash
# init.sh —— 环境搭建 + 冒烟测试(每个会话先跑)
#!/bin/bash
set -e
npm install                 # 或 pip install 等
npm run build
npm test -- --smoke          # 冒烟测试:环境可用才算数
```

```json
// feature_list.json —— 结构化功能清单
{
  "features": [
    { "id": "auth", "name": "用户登录", "passes": false },
    { "id": "billing", "name": "账单支付", "passes": false }
  ]
}
// 初始全部 "failing";每窗口只允许把验收过的 feature 的 passes 改为 true
```

```text
# claude-progress.txt —— 人类可读进度日志
2026-08-13:完成 auth 登录流程,测试通过;下一步:实现 billing 支付。
```

每窗口结束的收尾指令模板:

```text
1. git add -A && git commit -m "<本轮增量描述>"
2. 更新 claude-progress.txt(做了什么/下一步)
3. 更新 feature_list.json(通过验收的 feature 置 passes=true;不得删除或修改测试)
```

## 实践 / 应用

- **适用**:需要跨多个 context window 的自动化长任务(构建完整应用、大型重构、多日代理工作);
- **铁律**:feature list 用 JSON 且只改 passes;禁止删改测试;每窗口收尾必 commit + 更新进度;每会话开头先冒烟测试;
- **验证**:Puppeteer MCP 端到端自测,注意原生 alert 弹窗盲区;
- **教训**:从高层面提示 Opus 4.5 在 Claude Agent SDK 上"构建生产级应用"会失败——**必须给 harness(脚手架),不能只给提示词**;
- 与 [Agent 持久化运行范式](agent-persistence-patterns.md)(7 小时问题)互补:那篇讲"崩溃恢复/会话持久化",这篇讲"**跨窗口记忆**的落地三件套"。

## 总结

1. **长时 agent 的核心问题是跨 context window 无记忆**,像工程师换班——解决靠文件系统当记忆,不靠模型记得。
2. **双 agent 分工**:initializer(首窗口备好 init.sh/progress/feature list/commit)+ coding agent(每窗口增量 + 收尾固化)。
3. **每会话固定开场**:pwd → 读 git log/progress → 挑 feature → 跑 init.sh 冒烟测试。
4. **防作弊设计**:JSON 只改 passes 字段、禁止删改测试——完成判定由可验证状态驱动,不由模型自述。
5. **验证靠端到端自测**(Puppeteer MCP),并承认工具盲区(原生 alert)。

**下一步学什么**:对比 [Agent 持久化运行范式](agent-persistence-patterns.md)、[Anthropic 多智能体研究系统](agent-multi-agent-research-system.md)(跨窗口 + 多 agent 组合);想动手用 quickstart 三件套跑一个多窗口任务。

## 延伸阅读

- 站内:[Agent 持久化运行范式](agent-persistence-patterns.md)、[Anthropic 多智能体研究系统](agent-multi-agent-research-system.md)、[Building effective agents(五种模式)](agent-building-effective-agents.md)、[LongHorizon-Harness 长程任务状态管理](../09-agent-research/longhorizon-harness-paper.md)、[Harness 框架与开源方案](../08-harness/index.md)
- 外部:原文(https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents);quickstart(https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
