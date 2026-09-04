# 鸿蒙平台全景与开发基线

> **一句话摘要**:从 HarmonyOS NEXT 起鸿蒙完全独立于 Android(AOSP-free)。要正确回答鸿蒙开发问题,先建立平台快照:版本时间线(API 23/24/26)、主语言 ArkTS(TS 严格超集)、UI 框架 ArkUI(声明式)、应用模型 Stage(FA 已废弃)、打包体系(HAP/HSP/HAR)、编译器 ArkCompiler。**基线策略:生产默认 API 24 Release,API 26 Beta1 仅用于预览适配**——这是整个鸿蒙知识体系的第一原则。
>
> **来源**:HarmonyOS AI Skill 知识包(https://github.com/DengShiyingA/harmonyos-ai-skill)的 SKILL.md 与 `references/platform-baseline.md`、`references/stage-model.md`;原始文件存档于 `references/harmonyos-ai-skill/`

## 概念:鸿蒙不是"又一个 Android"

通用模型常把鸿蒙当 Android 系(Activity/`package.json`/React 组件),因为训练数据里几乎没有鸿蒙内容。核心事实:

| 维度 | 鸿蒙(HarmonyOS NEXT) | 常见误解 |
| --- | --- | --- |
| 底层 | **AOSP-free**(2024 起完全独立) | "安卓套壳" |
| 语言 | **ArkTS**(TS 严格静态检查超集)+ Cangjie(beta)+ C/C++ via NAPI | "JavaScript/React" |
| UI 框架 | **ArkUI**(声明式、状态驱动;ArkUI-X 跨平台) | "React Native/Jetpack Compose" |
| 应用模型 | **Stage model**(FA 已废弃) | "Android Activity" |
| 编译器 | **ArkCompiler**(AOT 编译为原生机器码;LiteActor 并发) | — |
| 包管理器 | **ohpm**(`oh-package.json5`,DevEco Service/OHPM Central) | "npm" |
| IDE | **DevEco Studio**(含 DevEco Code 编码 Agent、DevEco CLI) | — |
| 打包 | HAP(entry/feature)、HSP(共享包)、HAR(静态库)、原子化 .app | "APK" |

## 原理:平台快照与版本基线

### 版本时间线(近期)

| 版本 | API | 时间 | 状态 |
| --- | --- | --- | --- |
| HarmonyOS 6.0.1 | 21 | 2025/11/25 | 稳定(Mate 80 系列首发) |
| HarmonyOS 6.0.2 | 22 | 2026/01/23 | 增量更新 |
| HarmonyOS 6.1 | 23 | 2026/04/20 | **稳定正式版** |
| HarmonyOS 6.1.1 | 24 | 2026/05/26 | **Release 生产基线** |
| HarmonyOS 7 / 26.0.0 | 26 | 2026/06/12 | 开发者预览 Beta1 |

!!! tip "基线策略(平台基线的四条回答规则)"
    1. 用户未指定目标 SDK → **默认 API 24 Release** 生产代码;
    2. **不要把 API 26 专属 API 混进 API 24 生产示例**;
    3. 讨论 API 26 时明确标注"预览/适配专用";
    4. 调试时先要:DevEco Studio 版本、compileSdkVersion、compatibleSdkVersion/targetSdkVersion、module.json5、oh-package.json5、完整构建错误日志。

### API 23(6.1)重点新增

- **ArkUI**:`Navigation` 支持把路由栈绑定到组件自身、`NavDestination` 作为导航栏(无需独立根容器);`Menu` 新增 `anchorPosition`;`Image` 改进 SVG 解析;
- **Native/NAPI**:UDMF(统一数据管理框架)C API、组件拖放 C API、加密算法 C API;
- **数据**:`relationalStore` 增强 `sendable`(跨线程数据传递)。

### Stage 模型(应用模型核心)

- **AbilityStage**:应用进程级初始化与回调;
- **UIAbility**:页面窗口入口与前台 UI 生命周期;
- **WindowStage**:窗口创建与页面加载;
- **ExtensionAbility**:后台或系统集成能力(按扩展类型);
- **module.json5**:声明 abilities、权限与模块元数据;
- **规则**:新应用必须用 Stage 模型;FA 模型仅用于迁移/遗留维护语境;用鸿蒙术语解释生命周期(不用 Android Activity 类比)。

## 代码 / 实现:基线选择的最小演示(纯 Python)

把"API 24 生产基线 vs API 26 预览"的边界落成可运行演示:

```python
# —— 鸿蒙 API 基线策略:生产默认 API 24,API 26 仅预览 ——
PRODUCTION_API = 24
PREVIEW_API = 26

def baseline_for(target_sdk=None, purpose="production"):
    """回答鸿蒙开发问题时的基线选择"""
    if target_sdk == PREVIEW_API or purpose == "preview_adaptation":
        return ("API 26 Beta1", "仅预览/适配;标记为 Beta;分离迁移风险与实现步骤;签名不确定时标注概念性代码")
    return ("API 24 Release", "生产默认;不混入 API 26 专属 API;Debug 时检查 DevEco Studio/SDK 版本与构建日志")

for q in [(None, "production"), (26, "production"), (26, "preview_adaptation")]:
    sdk, policy = baseline_for(*q)
    print(f"  target={q[0]}, purpose={q[1]:18} → {sdk} | {policy[:26]}...")

assert baseline_for(None)[0] == "API 24 Release"
assert baseline_for(26)[0] == "API 26 Beta1"
assert baseline_for(26, "preview_adaptation")[1].startswith("仅预览")
print("\n代码验证通过 ✔")
```

## 实践 / 应用:工具链与排障基线

- **IDE**:DevEco Studio 6.1.1 Release(API 24 生产)/ 26.0.0 Beta1(API 26 预览);
- **排障四件套**:DevEco Studio 版本 + compileSdk + module.json5 + 完整构建错误日志——缺一不可(否则 AI 只能猜);
- **新项目默认**:Stage 模型 + API 24 + ArkUI 声明式 + `@kit.*` 导入;
- **与站内其他章节的关系**:本章节是**鸿蒙专属**,与其他章节(Agent 设计、Harness 等)相互独立;鸿蒙中的 AI Agent 能力(Agent Framework Kit 等)见 [AI 辅助鸿蒙开发](harmonyos-ai-development.md)。

## 总结

- **平台快照**:AOSP-free / ArkTS / ArkUI / Stage 模型 / ArkCompiler / ohpm / DevEco Studio / HAP-HSP-HAR;
- **版本基线**:生产 = API 24 Release;API 26 Beta1 仅预览——**不混用、要标注**;
- **Stage 模型**:AbilityStage / UIAbility / WindowStage / ExtensionAbility / module.json5;
- **一句话**:回答鸿蒙问题前先确定基线(API 24 生产),再用鸿蒙原生术语(不是 Android 类比),这是整个鸿蒙知识体系的起点。

## 延伸阅读

- 站内:[ArkUI 开发:组件、状态管理与导航](harmonyos-arkui-development.md)、[鸿蒙质量与发布](harmonyos-quality-release.md)、[AI 辅助鸿蒙开发](harmonyos-ai-development.md)(本章节后续篇)
- 华为官方:https://developer.huawei.com/consumer/cn/(HarmonyOS 指南、API 参考、示例目录);HarmonyOS AI Skill:https://github.com/DengShiyingA/harmonyos-ai-skill
