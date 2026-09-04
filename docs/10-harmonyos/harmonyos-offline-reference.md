# 鸿蒙离线知识库:HarmonyOS NEXT 开发者专家技能包

> **一句话摘要**:第二个鸿蒙 AI 知识源(harmony-next.skills,3708 个 Markdown / 33MB,面向 API 12-23)解决的核心问题:**AI 编程助手在鸿蒙开发中"找不到 `@ohos.*` 模块真实文档"**。它的特色不是"写知识",而是**离线检索范式**:按 `SKILL.md → KITS.md/TASK_MAP.md → INDEX.md` 命中文档路径 → 打开目标文件 → 给出代码与验证命令(`hdc`/`uitest`/wrapper 脚本)。另有**私有能力隔离**(DevEco 模拟器/IDE 未公开接口)、**自动化脚本**(命令行工具管理/证据采集/UI 体检/trace 审计)与**可运行最小工程**(empty-ability-app smoke fixture)。
>
> **来源**:linhay/harmony-next.skills(https://github.com/linhay/harmony-next.skills);原始文件存档于 `references/harmony-next-skills/`;与站内 [鸿蒙平台全景](harmonyos-platform-overview.md) 等篇(基于第一个 Skill)互补。

## 概念:与第一个鸿蒙 Skill 的定位差异

| 维度 | harmonyos-ai-skill(前文) | harmony-next.skills(本篇) |
| --- | --- | --- |
| 侧重 | 4461 行**知识包**(ArkTS/ArkUI/状态/权限/性能) | **3708 个离线文档**(API 12-23 全量参考 + 实战指引) |
| 使用方式 | 直接喂进上下文的提炼知识 | **按需检索**:先命中文档路径,再打开读取 |
| 覆盖 | 生产 API 24 / 跟踪 API 26 | API 12-23 本地知识源 |
| 独有 | recipes/examples/evals 评估用例 | **JsEtsAPIReference 3678 个 API 文档**、自动化脚本、多端跨端 |

!!! tip "一句话"
    第一个 Skill 让 AI"知道鸿蒙怎么写";第二个 Skill 让 AI"**知道去哪里查鸿蒙的真实文档**"——两者叠加,AI 既有规则又有权威来源。

## 原理:三层检索范式与 API 参考地图

### 1. 离线检索范式(不依赖模型记忆)

```
SKILL.md(技能规则:如何检索、哪些优先信文档)
  → KITS.md(按 Kit 导航:AbilityKit/ArkUI/ArkData…)或 TASK_MAP.md(按任务反查:UI/网络/媒体/NDK…)
  → INDEX.md(全库 3708 个路径)用 rg 命中目标
  → 只打开那 1-3 个 .md 文件阅读
```

!!! tip "KITS.md 与 TASK_MAP.md 的用法"
    先看"常用 Kit 快速入口"拿关键词或模块前缀(如 AbilityKit → `@ohos.app.ability.`),再用 `rg -n "(关键词)" INDEX.md | rg "JsEtsAPIReference/" | head` 命中精确路径——**不要在本文件里找"准确文件路径",它是识别入口,不是内容仓库**。

### 2. API 参考地图(JsEtsAPIReference 3678 个文件)

按桶组织:`modules`(@ohos.* 模块)、`topics`、`errors`(API 错误码,如 ArkTS/HTTP/Media/HUKS 错误码)、`classes`(RectUtils/WebCookieManager 等)。另有 **C API 错误码**目录——NDK 场景同样可检索。

### 3. 覆盖模块(实战指引类)

| 模块 | 内容 |
| --- | --- |
| **quickStart/ets** | 快速上手 8 篇:创建工程、第一个/第二个页面、页面跳转、真机运行、最小工程脚手架 |
| **appBasics** | 应用基础与包结构、应用模型与并发 |
| **testing** | 应用测试与 Hypium 测试框架 |
| **ndkGuides** | NDK 开发与 Node-API 指南 |
| **continuation / multiDevice** | 自由流转与跨端协同、一次开发多端部署 |
| **ideGuides** | 运行与环境配置、应用签名、命令行工具、**DevEco Studio IDE 私有接口与 AI 自动化**、DevEco 模拟器私有接口、调试与日志分析、ArkWeb CDP 调试 |
| **performanceAndStandards** | 应用体验与性能规范、性能调优与 Profiler |
| **publishing** | 应用上架与发布指南 |
| **templates/empty-ability-app** | 可复制的最小工程(smoke fixture) |

## 代码 / 实现:检索范式的最小演示(纯 Python)

把"KITS 识别 → rg 命中 → 打开文档"落成可运行演示:

```python
import re

# —— 模拟 KITS.md 的 Kit 快速入口与 INDEX.md 检索 ——
KIT_ENTRIES = {
    "AbilityKit":  {"keywords": ["UIAbility", "AbilityStage", "Context", "Want"],
                    "prefix": "@ohos.app.ability."},
    "ArkUI":       {"keywords": ["List", "Grid", "Tabs", "Navigation", "LazyForEach"],
                    "prefix": "@ohos.arkui."},
    "NetworkKit":  {"keywords": ["http", "socket", "Web", "rcp"],
                    "prefix": "@ohos.net."},
}
INDEX_PATHS = [
    "JsEtsAPIReference/modules/@ohos.app.ability.UIAbility.md",
    "JsEtsAPIReference/modules/@ohos.arkui.Navigation.md",
    "JsEtsAPIReference/modules/@ohos.net.http.md",
    "JsEtsAPIReference/modules/@ohos.hiviewdfx.hilog.md",
]

def offline_search(question: str) -> list:
    """按 TASK_MAP 思路:关键词 → 命中 Kit → rg 过滤 INDEX → 返回待打开文档"""
    hits = []
    for kit, meta in KIT_ENTRIES.items():
        if any(k in question for k in meta["keywords"]):
            for path in INDEX_PATHS:
                if meta["prefix"] in path:
                    hits.append(f"{kit} → {path}")
    return hits or ["未命中:换关键词或查 errors/classes 分桶"]

for q in ["用 UIAbility 实现页面生命周期", "Navigation 页面跳转怎么写", "http 请求怎么做"]:
    print(f"  {q!r:24} → {offline_search(q)}")
assert offline_search("UIAbility 生命周期")[0].startswith("AbilityKit")
assert "http" in offline_search("http 请求")[0]
print("代码验证通过 ✔")
```

## 实践 / 应用:安装、自动化与私有能力

### 安装(三种 Agent 路径,详见 docs/agent-portability.md)

- **Gemini CLI / Claude Code / Codex**:按 `SKILL.md` 规则加载 references 目录;
- **可移植性**:`docs/agent-portability.md` 说明各 Agent 的安装与适配路径;
- **无网络场景**:完全离线检索(不依赖模型记忆与在线文档)。

### 自动化与诊断脚本(非交互式)

| 脚本 | 功能 |
| --- | --- |
| `commandline_tools_manager.py` | Command Line Tools 下载与安装 |
| 证据采集 / UI/UX 离线体检 / trace 审计 | 本地自动化验证策略 |
| `hdc` / `uitest` / wrapper 脚本 | 验证命令(先给代码,再给可执行验证) |

!!! warning "私有能力隔离"
    **DevEco 模拟器、IDE 未公开接口单独成章,默认先验证版本和风险**——未公开接口可用但脆弱,使用时必须标注风险(呼应站内 [Agent 工程化](../06-enterprise/ontology-agent-adoption/enterprise-agent-tooling-harness.md) 的"工具权限边界")。

### 与站内其他鸿蒙文章的整合

- [鸿蒙平台全景与开发基线](harmonyos-platform-overview.md):本篇的 API 12-23 与第一篇的 API 24/26 基线互补——查 API 用本篇,定基线用第一篇;
- [ArkUI 开发](harmonyos-arkui-development.md):本篇的 JsEtsAPIReference 提供 ArkUI 组件的权威文档路径;
- [鸿蒙质量与发布](harmonyos-quality-release.md):本篇的 testing(Hypium)/publishing/performanceAndStandards 是其发布清单的官方文档来源;
- [AI 辅助鸿蒙开发](harmonyos-ai-development.md):本篇的"私有能力 + 自动化脚本"是 DevEco AI 自动化的落地补充。

## 总结

- **定位**:3708 个离线文档的鸿蒙知识库(API 12-23),解决"找不到 `@ohos.*` 真实文档";
- **检索范式**:SKILL.md → KITS/TASK_MAP → INDEX(rg 命中)→ 打开 1-3 个文件——**不依赖模型记忆**;
- **API 参考地图**:modules/topics/errors/classes 分桶 + C API 错误码;
- **独有模块**:测试(Hypium)、NDK/Node-API、多端跨端、IDE/模拟器私有接口、自动化脚本、empty-ability-app 模板;
- **一句话**:第一个 Skill 给 AI"规则",本篇给 AI"权威来源"——鸿蒙开发的正确姿势是**先命中文档路径,再给代码,最后给验证命令**。

## 延伸阅读

- 仓库:https://github.com/linhay/harmony-next.skills;安装适配:https://github.com/linhay/harmony-next.skills/blob/main/docs/agent-portability.md
- 站内:[鸿蒙平台全景与开发基线](harmonyos-platform-overview.md)、[ArkUI 开发](harmonyos-arkui-development.md)、[鸿蒙质量与发布](harmonyos-quality-release.md)、[AI 辅助鸿蒙开发](harmonyos-ai-development.md)(本章节其他篇)
