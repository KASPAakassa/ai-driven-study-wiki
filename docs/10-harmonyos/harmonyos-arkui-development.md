# ArkUI 开发:组件、状态管理与导航

> **一句话摘要**:ArkUI 是鸿蒙的声明式、状态驱动 UI 框架(不是 React/Compose 那套)。本文给出三张实战表:①**组件选型表**(Column/Row/Stack/Flex/List/Grid/Tabs/Swiper/Navigation——按布局需求选);②**状态装饰器决策表**(State/Prop/Link/ObjectLink/Provide-Consume/StorageLink——按数据流向选);③**导航原则**(Navigation/NavPathStack,单一事实源)。加上 ArkTS 严格语法规则与审查清单,构成"用鸿蒙原生方式写 UI"的完整知识。
>
> **来源**:HarmonyOS AI Skill 知识包(https://github.com/DengShiyingA/harmonyos-ai-skill)的 `references/arkui-components.md`、`references/state-management.md`、`references/navigation.md`、`references/arkts-rules.md`;原始文件存档于 `references/harmonyos-ai-skill/`

## 概念:声明式 ArkUI 的正确姿势

!!! tip "铁律"
    用 **HarmonyOS 原生组件与 API**,不要用 React、DOM、Android View 或 Jetpack Compose 的模式——把 `@State` 写成 `useState`、把 `module.json5` 当 `package.json` 改,是通用模型最常见的鸿蒙错误。目标 SDK 影响行为时,明确声明 SDK 版本假设。

## 原理:三张实战表 + ArkTS 规则

### 1. 组件选型表(按布局需求)

| 需求 | 用 |
| --- | --- |
| 垂直布局 | `Column` |
| 水平布局 | `Row` |
| 覆盖/分层布局 | `Stack` |
| 弹性换行布局 | `Flex` |
| 大列表 | `List` + `LazyForEach` |
| 网格内容 | `Grid` / `GridItem` |
| 随容器响应 | **`ContainerReader`**(容器断点,比窗口断点更精确) |
| 分页标签 | `Tabs` / `TabContent` |
| 轮播 | `Swiper` |
| 导航外壳 | `Navigation` / `NavDestination` |

!!! note "ContainerReader 容器响应式(重要)**
    可复用组件要**根据自身容器**改变布局(侧边栏/分屏/嵌套面板/可复用卡片)时,用 `ContainerReader`——比一次性窗口宽度查询更精确;**断点决策要附着在容器上**,父布局变化时能更新,不要用一次性 window-width 查询替代。

**审查清单**:布局嵌套合理、`build()` 内不做重计算、动态列表用稳定 key、组件状态所有权清晰、依赖权限/路由/配置时补全 module 配置。

### 2. 状态装饰器决策表(按数据流向)

| 需求 | 装饰器 |
| --- | --- |
| 本地原始状态 | `@State` |
| 父→子单向值 | `@Prop` |
| 父子双向绑定 | `@Link` |
| 对象条目传入子行组件 | `@ObjectLink` + `@Observed` 类 |
| 跨层级依赖注入 | `@Provide` / `@Consume` |
| 应用级/存储支撑状态 | `@StorageLink` / `@StorageProp` |
| 页面级本地存储 | `@LocalStorageLink` / `@LocalStorageProp` |

!!! warning "三条规则"
    ①**不要在没有 `@Observed` 类的情况下用 `@ObjectLink`**;②列表行优先稳定对象模型与稳定 key;③解释"改变数组元素属性是否触发刷新"在所选模式下的行为——**不要用 React hook 类比**(除非用户明确要求对比)。

### 3. 导航原则(Navigation/NavPathStack)

- 新应用**优先 `Navigation` + `NavPathStack`**(替代 legacy router);
- **单一事实源**:路由名、参数、页面注册显式声明;路由栈由正确的组件/页面外壳拥有;
- 页面参数**类型化、可序列化**、校验;嵌套导航时讲清栈所有权与返回行为;
- 涉及新 Navigation 行为时注明 SDK 版本假设。

### 4. ArkTS 规则(严格语法)

- 优先 `.ets` 示例;优先显式类型(避免动态对象形状);
- 避免通用 TypeScript / DOM / React / Android / Web 专属建议(除非用户明确要求对比);
- 导入尽量用 `@kit.*`;
- **常见输出模式**:文件路径建议 → ArkTS 代码 → 需要的配置变更 → 集成说明 → API 基线说明。

## 代码 / 实现:组件 + 状态的最小示例(ArkTS 与纯 Python 演示)

### ArkTS 最小示例(参考 Skill 的 examples 风格)

```typescript
// 建议路径: entry/src/main/ets/pages/UserList.ets
@Observed
class User { name: string; active: boolean }
@Component
struct UserRow {
  @ObjectLink user: User           // 对象条目 → ObjectLink(类必须 @Observed)
  build() {
    Row() {
      Text(this.user.name)
      if (this.user.active) { Text('在线') }
    }
  }
}
@Entry
@Component
struct UserListPage {
  @State users: User[] = []        // 本地状态 → @State
  build() {
    List() {                        // 大列表 → List + LazyForEach
      ForEach(this.users, (u: User) => { UserRow({ user: u }) }, (u: User) => u.name)
    }
  }
}
```

### 状态装饰器选型演示(纯 Python,可运行)

```python
# —— 状态装饰器决策表:按数据流向选 ——
def choose_decorator(data_flow: str) -> str:
    table = {
        "local":           "@State",
        "parent_to_child": "@Prop",
        "two_way":         "@Link",
        "object_in_child": "@ObjectLink + @Observed",
        "cross_level":     "@Provide/@Consume",
        "app_level":       "@StorageLink/@StorageProp",
        "page_local":      "@LocalStorageLink/@LocalStorageProp",
    }
    return table.get(data_flow, "按数据流向选择(不要用 React hook 类比)")

for flow in ["local", "object_in_child", "cross_level", "unknown"]:
    print(f"  {flow:16} → {choose_decorator(flow)}")
assert choose_decorator("object_in_child") == "@ObjectLink + @Observed"
assert choose_decorator("local") == "@State"
print("代码验证通过 ✔")
```

## 实践 / 应用:代码审查与常见错误

### 审查顺序(参考 Skill 的 review-arkts-code 配方)

1. **目标 SDK 与生产/预览边界**(API 24 vs 26);
2. ArkTS 严格类型与空安全;
3. ArkUI 状态装饰器正确性(`@ObjectLink` 必须有 `@Observed`);
4. 生命周期副作用与异步工作位置;
5. 权限与 module 配置要求;
6. UI 渲染与列表性能(`LazyForEach`/稳定 key)。

### 常见错误速查

| 错误 | 正确 |
| --- | --- |
| `useState` / React Hook 类比 | `@State` 等装饰器,不用 React 类比 |
| 大列表用 `ForEach` 全量渲染 | `List` + `LazyForEach` + 稳定 key |
| 组件布局依赖窗口断点 | `ContainerReader` 容器断点 |
| `@ObjectLink` 类未加 `@Observed` | 类必须 `@Observed` |
| 用 Android Activity 术语解释生命周期 | 用 Stage 模型术语(UIAbility 等) |
| 改 module.json5 当 package.json | module.json5 声明 abilities/权限/模块元数据 |

## 总结

- **组件选型**:按布局需求选(Column/Row/Stack/Flex/List/Grid/Tabs/Swiper/Navigation),`ContainerReader` 做容器响应式;
- **状态管理**:按数据流向选装饰器(State/Prop/Link/ObjectLink+Observed/Provide-Consume/Storage),不用 React 类比;
- **导航**:Navigation + NavPathStack,单一事实源、参数类型化;
- **ArkTS 纪律**:严格类型、`@kit.*` 导入、输出含文件路径/代码/配置/集成/基线五件套;
- **一句话**:写鸿蒙 UI = 用鸿蒙原生组件 + 正确装饰器 + 明确 SDK 基线——不是 React 换皮。

## 延伸阅读

- 站内:[鸿蒙平台全景与开发基线](harmonyos-platform-overview.md)、[鸿蒙质量与发布](harmonyos-quality-release.md)、[AI 辅助鸿蒙开发](harmonyos-ai-development.md)(本章节其他篇)
- 华为官方:ArkUI 指南、State Management(状态管理)、Navigation 文档;HarmonyOS AI Skill 的 examples(`lazyforeach-list.ets`、`permission-request.ets`)与 `recipes/review-arkts-code.md`
