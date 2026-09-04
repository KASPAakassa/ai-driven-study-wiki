# 📱 鸿蒙开发(HarmonyOS)

> 鸿蒙(HarmonyOS)原生应用开发知识体系:平台全景与版本基线、ArkTS 严格语法、ArkUI 声明式 UI、状态管理、导航、性能、权限、构建发布,以及用 AI 工具高效开发鸿蒙(DevEco Code/CLI、Agent Framework Kit、鸿蒙 AI Skill)。**本章节只收录鸿蒙相关知识**,与 [01-ai-basics](../01-ai-basics/index.md)(AI 基础)等章节完全独立。

## 为什么需要独立章节

鸿蒙从 HarmonyOS NEXT 起**完全脱离 Android(AOSP-free)**:语言是 **ArkTS**(TypeScript 的严格静态检查超集,不是 React/Android 那套)、UI 框架是 **ArkUI**(声明式、状态驱动,不是 Jetpack Compose/React Native)、应用模型是 **Stage model**(不是 Android Activity)。通用大模型没系统学过鸿蒙——训练数据里几乎没有 ArkTS、Stage 模型、HarmonyOS Kit,常把 `@State` 写成 `useState`、把 `module.json5` 当 `package.json` 改。本章节把华为官方文档、最佳实践、API 参考浓缩成可直接使用与喂给 AI 的知识体系。

## 本章节文章

- [鸿蒙平台全景与开发基线](harmonyos-platform-overview.md) — 版本时间线、Stage 模型、ArkTS/ArkCompiler、打包体系、DevEco 工具链、API 24 生产基线策略
- [ArkUI 开发:组件、状态管理与导航](harmonyos-arkui-development.md) — 声明式组件选型表、状态装饰器决策表、Navigation/NavPathStack、ContainerReader 容器响应式
- [鸿蒙质量与发布:性能、权限、构建签名](harmonyos-quality-release.md) — 性能清单与内存泄漏诊断、权限授权流程、构建签名发布、原生 API 兼容(APIAVAILABLE)、API 26 预览边界
- [AI 辅助鸿蒙开发](harmonyos-ai-development.md) — HarmonyOS AI Skill(11+ 工具分发)、DevEco Code/CLI、Agent Framework Kit/Intents/Skill/A2A、构建错误调试与代码审查配方、评估用例
- [鸿蒙离线知识库:HarmonyOS NEXT 开发者专家技能包](harmonyos-offline-reference.md) — 3708 个离线文档(API 12-23):SKILL→KITS/TASK_MAP→INDEX 检索范式、API 参考地图、自动化脚本、多端跨端、Hypium 测试

## 学习指引

按"平台基线 → 语言与 UI → 质量与发布 → AI 提效"四步:先搞清 API 24 生产基线(避免混入 API 26 预览特性),再学 ArkTS 严格语法与 ArkUI 状态管理,然后掌握性能/权限/发布的检查清单,最后用 AI 工具与 Skill 提效。

## 主要参考

- HarmonyOS AI Skill 仓库:https://github.com/DengShiyingA/harmonyos-ai-skill(4461 行实战知识/243 章节/105+ 代码示例,原始文件存档于 `references/harmonyos-ai-skill/`)
- 华为官方:https://developer.huawei.com/consumer/cn/(DevEco Studio、HarmonyOS 指南、API 参考、示例代码)
