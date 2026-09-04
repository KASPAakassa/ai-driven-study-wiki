# AI 辅助鸿蒙开发:HarmonyOS AI Skill 与鸿蒙 AI 能力

> **一句话摘要**:鸿蒙最大的 AI 编程知识库 HarmonyOS AI Skill(4461 行/243 章节/105+ 代码示例,一份 Markdown 源自动产出 11+ AI 工具配置)让 Claude Code/Cursor/Copilot 等真正会写 ArkTS——装前把 `@State` 写成 `useState`,装后像读过华为文档的工程师。同时鸿蒙 7 自带 AI 开发工具链(DevEco Code 编码 Agent、DevEco CLI 执行层)与 Agent Framework Kit/Intents/Skill/A2A 等应用内 Agent 能力。本文讲清三件事:Skill 怎么装、DevEco AI 工具怎么分工、鸿蒙应用内 Agent 能力有哪些。
>
> **来源**:HarmonyOS AI Skill 仓库 README 与 `references/ai-development-tools.md`(https://github.com/DengShiyingA/harmonyos-ai-skill);原始文件存档于 `references/harmonyos-ai-skill/`

## 一、HarmonyOS AI Skill:让 AI 真正会写 ArkTS

!!! tip "为什么需要它"
    通用大模型从来没系统学过鸿蒙——训练数据里几乎没有 ArkTS、Stage 模型、HarmonyOS Kit。问 Cursor 写 ArkUI 它给 React 组件;让 Claude 改 `module.json5` 它当 `package.json` 改;问 Copilot `@ObjectLink` 它说"这 API 不存在"。**这份知识包把华为官方文档、最佳实践、API 参考浓缩成可直接喂进 LLM 上下文的知识**(API 24 生产覆盖,跟踪 HarmonyOS 7/API 26 Beta1)。

### 安装(Claude Code,macOS/Linux 30 秒)

```bash
git clone https://github.com/DengShiyingA/harmonyos-ai-skill.git ~/src/harmonyos-ai-skill
mkdir -p ~/.claude/skills
ln -s ~/src/harmonyos-ai-skill/harmonyos-development ~/.claude/skills/harmonyos-development
# 重启 Claude Code,然后问:"What skills are available?"
# Windows(PowerShell 7+,需开发者模式)用 New-Item -ItemType SymbolicLink
```

### 支持 11+ AI 工具(一份源自动产出配置)

`dist/` 目录为各工具产出对应配置:Claude Code(SKILL.md)、Cursor(.mdc/.cursorrules)、Copilot、Cline、Gemini CLI、Windsurf、Continue、AGENTS.md、system-prompt、plain(单文件知识全量)。**工具对应关系**:Cursor 用 `dist/cursor/harmonyos.mdc`,Copilot 用 `dist/copilot/copilot-instructions.md`,通用 Agent 用 `dist/agents-md/AGENTS.md` 或 `dist/plain/harmonyos-knowledge.md`。

### 知识包结构(库内)

```
harmonyos-development/
├── SKILL.md            技能入口:平台快照/版本时间线/API 新特性/Kit 索引
├── references/         13 个参考:stage-model / arkts-rules / arkui-components /
│                        state-management / navigation / performance / permissions /
│                        platform-baseline / build-sign-release / native-api-compatibility /
│                        api26-preview / ai-development-tools ...
├── recipes/            实战配方:debug-build-error(构建错误调试)、review-arkts-code(代码审查)
├── examples/           .ets 示例:lazyforeach-list、permission-request
└── evals/              评估用例(cases.yaml:ObjectLink、API 基线、预览边界等 must_include/must_not_include)
```

!!! note "评估用例的价值(must_not_include)"
    例如 `objectlink-vs-state` 用例要求回答**必须包含** Observed/ObjectLink/父子组件,**不得包含** useState/React Hook——这直接可复用于验证任何 AI 是否真懂鸿蒙(站内 [评估驱动开发](../03-agents/agent-eval-driven-dev.md) 的鸿蒙实例)。

## 二、DevEco AI 工具链:Code 与 CLI 的分工

| 工具 | 定位 |
| --- | --- |
| **DevEco Studio** | 全功能 IDE:编辑、预览、性能剖析、签名、模拟器、图形化调试 |
| **DevEco Code** | 鸿蒙专属编码 Agent:Agent 主导的实现 + 迭代 build/run/verify/fix 工作流 |
| **DevEco CLI** | 执行层:脚本化 project/build/check/device/debug,面向 Agent 与 CI/CD |
| 第三方编码 Agent | 原生工作流 + DevEco CLI/Hvigor/HDC + 本 Skill |

!!! tip "基线不变"
    DevEco Code/CLI 不改变生产 SDK 基线:默认 API 24 Release,API 26 Beta1 仅预览/适配。

## 三、鸿蒙应用内 Agent 能力(Agent Framework Kit 等)

| 能力 | 用途 |
| --- | --- |
| **Agent Framework Kit** | 应用通过 UI 控件主动启动系统 Agent 组合 |
| **Intents Kit** | 把应用或原子化服务功能声明为系统可识别的 intents |
| **ArkTS 脚本应用 Skill** | 通过声明契约,把应用业务能力暴露给系统智能入口 |
| **设备端 A2A** | 应用侧 Agent 与系统 Agent 连接:注册组件、认证双向通信、交互 UI |
| **AgentCard** | 通过支持的卡片能力呈现 Agent 相关内容/交互 |

## 代码 / 实现:两个配方 + 评估用例演示(纯 Python)

### 配方 1:构建错误调试(debug-build-error)

```
① 识别错误类型:ArkTS 编译错误 / Hvigor 构建错误 / ohpm 依赖错误 /
   SDK 版本不匹配 / module 或 app 配置错误
② 按类型收集:DevEco Studio 版本、compileSdk、target/compatible SDK、
   module.json5、oh-package.json5、完整错误日志
③ 修复后验证:重新构建 + 设备/模拟器运行
```

### 配方 2:代码审查(review-arkts-code)

```
① 目标 SDK 与生产/预览边界 → ② ArkTS 严格类型与空安全 →
③ 状态装饰器正确性 → ④ 生命周期副作用与异步位置 →
⑤ 权限与 module 配置 → ⑥ UI 渲染与列表性能
```

### 评估用例语义演示(纯 Python)

```python
# —— Skill 的 evals 用例语义:must_include / must_not_include ——
def check_answer(answer: str, must_include: list, must_not_include: list) -> bool:
    ok = all(k in answer for k in must_include)
    bad = any(k in answer for k in must_not_include)
    return ok and not bad

answer1 = "ObjectLink 用于父子组件传对象属性,类需 @Observed"
answer2 = "ObjectLink 类似 React 的 useState,用于组件本地状态"
case = {"must_include": ["ObjectLink", "Observed"], "must_not_include": ["useState", "React Hook"]}
print("正确答案:", check_answer(answer1, case["must_include"], case["must_not_include"]))
print("React 类比答案:", check_answer(answer2, case["must_include"], case["must_not_include"]))
assert check_answer(answer1, case["must_include"], case["must_not_include"]) is True
assert check_answer(answer2, case["must_include"], case["must_not_include"]) is False
print("代码验证通过 ✔(可复用于验证任意 AI 是否真懂鸿蒙)")
```

## 实践 / 应用:落地建议

1. **个人用**:按 [安装](#一harmonyos-ai-skill让-ai-真正会写-arkts) 30 秒装进 Claude Code,问 "What skills are available?" 验证;
2. **团队用**:用 `dist/agents-md/AGENTS.md` 或 `dist/plain/harmonyos-knowledge.md` 作为团队统一规则;用 evals 用例做 AI 鸿蒙能力验收;
3. **CI/CD**:DevEco CLI + Hvigor + HDC 脚本化构建/检查/设备操作(Linux CI 基线);
4. **应用内 Agent**:结合 Agent Framework Kit / Intents / 应用 Skill / A2A 构建鸿蒙原生 AI 功能(与站内 [03-agents](../03-agents/index.md) 的 Agent 设计知识互补——本章节聚焦鸿蒙平台实现)。

## 总结

- **Skill**:一份源产出 11+ 工具配置,让 AI 会写 ArkTS(安装 30 秒,知识含 references/recipes/examples/evals);
- **DevEco 工具链**:Studio(IDE)/ Code(编码 Agent)/ CLI(执行层)三层分工,基线不变;
- **应用内 Agent**:Agent Framework Kit / Intents / 应用 Skill / A2A / AgentCard——鸿蒙原生的 Agent 能力面;
- **一句话**:让 AI 高效开发鸿蒙 = 装对 Skill(会写 ArkTS)+ 用对工具链(DevEco Code/CLI)+ 守对基线(API 24 生产)。

## 延伸阅读

- 站内:[鸿蒙平台全景与开发基线](harmonyos-platform-overview.md)、[ArkUI 开发](harmonyos-arkui-development.md)、[鸿蒙质量与发布](harmonyos-quality-release.md)(本章节其他篇)
- 仓库:https://github.com/DengShiyingA/harmonyos-ai-skill(README 含各工具安装命令、验证效果、知识包内容、Kit 索引)
