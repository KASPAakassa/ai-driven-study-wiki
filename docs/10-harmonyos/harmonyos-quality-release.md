# 鸿蒙质量与发布:性能、权限、构建签名与原生兼容

> **一句话摘要**:鸿蒙应用从开发到上线要过四道质量关:**性能**(LazyForEach 大列表、构建函数轻量化、内存泄漏用 jsLeakWatcher 定位)、**权限**(静态声明 + 运行时请求 + 拒绝兜底)、**构建签名发布**(DevEco Studio/Hvigor/ohpm、HAP/HSP/HAR、签名 profile)、**原生 API 兼容**(C API 弱引用 + APIAVAILABLE,API 22 起跨版本兼容)。每条都有可执行的检查清单。
>
> **来源**:HarmonyOS AI Skill 知识包(https://github.com/DengShiyingA/harmonyos-ai-skill)的 `references/performance.md`、`references/permissions.md`、`references/build-sign-release.md`、`references/native-api-compatibility.md`、`references/api26-preview.md`;原始文件存档于 `references/harmonyos-ai-skill/`

## 一、性能:清单 + 内存泄漏诊断

### 性能检查清单

- 大列表/动态列表优先 `LazyForEach` + 稳定 key;
- 避免过度嵌套布局容器;
- **渲染/build 函数内不做重活**(IO、解析、昂贵计算移出 UI 渲染);
- 组件复用只在匹配目标 SDK 与页面模式时用;
- 检查图片:尺寸、解码成本、缓存策略、懒加载;
- 检查 Ability 生命周期副作用与资源清理。

### 内存泄漏诊断(用最小的工具定位)

| 疑似区域 | 首选工具 |
| --- | --- |
| ArkTS 组件/生命周期对象 | `@ohos.hiviewdfx.jsLeakWatcher`(开发期) |
| ArkTS 堆保留路径 | DevEco Studio JS Heap / 堆快照 |
| Native 分配或释放错误 | HWASan / AddrSanitizer(开发/测试) |
| 运行时卡顿/资源压力 | AppFreeze、HiAppEvent、HiLog、DevEco Testing |

!!! warning "泄漏修复的纪律"
    **不要从一次堆快照就声称泄漏已修复**——复现生命周期、按需强制/等待回收、对比保留对象、修复所有权路径、重复同一场景验证。`jsLeakWatcher` 主要面向开发期;生产诊断不可避免时用**小规模灰度**,不要对全部用户永久开启。

### 调试必问信息

target SDK、设备型号或模拟器、页面路由、复现步骤、HiLog / AppFreeze / 性能报告、UI 卡顿时附截图或录屏。

## 二、权限:声明、请求与拒绝兜底

**回答模式(五步)**:①识别所需权限(用鸿蒙权限名,如 Ability Kit 的相机权限常量);②在 module 配置中声明;③需要用户授权时**运行时请求**(用正确的 ability context);④**优雅处理拒绝**;⑤涉及 SDK 版本差异时说明。

!!! note "API 26 权限行为变化不要套用到 API 24 生产答案"
    生产默认按 API 24 回答;API 26 的权限行为变化仅在用户明确目标 API 26 预览时提及。

**审查清单**:权限名是鸿蒙权限;运行时请求用正确 context;拒绝路径已处理。

## 三、构建、签名与发布

### 构建排障清单(先要什么)

DevEco Studio 版本、compile SDK、target SDK、compatible SDK、module 配置、app 配置、package 配置、**Hvigor 错误日志**、签名 profile 或证书错误信息。

### 关键约定

- 确认生产基线后再建议 SDK/工具链变更(**API 24 Release 默认**);
- 生成的 `dist/` 输出与源 Skill 文件分开;
- Linux CI 基线:用 DevEco CLI + Hvigor + HDC 做脚本化构建/检查/设备操作(见 [AI 辅助鸿蒙开发](harmonyos-ai-development.md));
- 打包:HAP(entry/feature)、HSP(共享包)、HAR(静态库)、原子化 .app。

## 四、原生 API 兼容(NAPI/C++)

!!! tip "核心规则(API 22 起)**
    HarmonyOS 可以用 **C API 弱引用 + `APIAVAILABLE`** 让一套原生代码跨系统版本兼容——这是高级机制:**缺失的链接依赖仍可能编译成功,然后运行时崩溃**。

**不要只依赖其中任何一个**:
- compileSdkVersion
- SystemCapability 检查
- 预处理版本检查
- 异常处理
- `APIAVAILABLE` 而无正确链接配置

**Hvigor 项目正确姿势(六步)**:①用匹配的 DevEco Studio 与 SDK 版本;②把 `compatibleSdkVersion` 传给编译器启用可用性检查;③链接每个提供被引用 API 的库;④若提供动态库在旧设备上不存在,配置为弱库 + 链接依赖;⑤每个新 API 调用包 `APIAVAILABLE` 并提供 fallback;⑥在**最旧兼容设备**与**支持新 API 的设备**上都测试。

## 代码 / 实现:权限流程与兼容性检查演示(纯 Python)

```python
# —— 权限授权流程:声明 → 运行时请求 → 拒绝兜底 ——
def permission_flow(permission: str, module_declared: bool, user_grants: bool) -> str:
    if not module_declared:
        return f"① 先在 module.json5 声明 {permission}(鸿蒙权限名)"
    if not user_grants:
        return "③ 运行时请求被拒 → 优雅处理(降级/说明/引导设置)"
    return "通过:声明 + 运行时授权 → 使用能力(注意 ability context)"

# —— 原生兼容:APIAVAILABLE + 弱库 + fallback 才是完整方案 ——
def native_compat(has_apiavailable, has_weak_link, has_fallback):
    if not (has_apiavailable and has_weak_link and has_fallback):
        return "不完整:三者缺一不可(缺失链接仍可编译,但运行时会崩)"
    return "完整:旧设备走 fallback,新设备用新 API"

print(permission_flow("ohos.permission.CAMERA", module_declared=False, user_grants=True))
print(permission_flow("ohos.permission.CAMERA", module_declared=True, user_grants=False))
print(native_compat(True, False, True))
assert permission_flow("P", False, True).startswith("①")
assert "降级" in permission_flow("P", True, False)
assert "不完整" in native_compat(True, False, True)
print("代码验证通过 ✔")
```

## 实践 / 应用:发布前检查清单

1. **性能**:大列表 LazyForEach + 稳定 key;build() 无重活;图片三查(尺寸/解码/缓存);
2. **内存**:jsLeakWatcher 定位(开发期)、复现对比验证修复;
3. **权限**:module.json5 声明 + 运行时请求 + 拒绝兜底;
4. **构建**:API 24 基线确认;DevEco Studio/SDK 版本匹配;Hvigor 日志检查;
5. **原生兼容**:APIAVAILABLE + 弱库 + fallback 三件套,新旧设备双测;
6. **API 26 边界**:预览能力明确标注 Beta,不混入生产示例。

!!! tip "与 AI 辅助开发的关系"
    调试构建错误(DevEco Studio/Hvigor/ohpm/ArkTS/签名/打包错误)与审查 ArkTS/ArkUI 代码,有现成的 recipe 配方——详见 [AI 辅助鸿蒙开发](harmonyos-ai-development.md) 的"两个配方"。

## 总结

- **性能**:LazyForEach、build() 轻量化、内存泄漏用最小工具定位(jsLeakWatcher→JS Heap→HWASan→AppFreeze 分级);
- **权限**:五步模式(识别→声明→运行时请求→拒绝兜底→SDK 差异说明);
- **发布**:API 24 基线 + 版本匹配 + Hvigor 日志 + 签名 profile;
- **原生兼容**:APIAVAILABLE + 弱库 + fallback 三件套(缺一不可);
- **一句话**:上线前把性能、权限、构建、兼容四条检查清单走一遍,再用小规模灰度验证。

## 延伸阅读

- 站内:[鸿蒙平台全景与开发基线](harmonyos-platform-overview.md)、[ArkUI 开发](harmonyos-arkui-development.md)、[AI 辅助鸿蒙开发](harmonyos-ai-development.md)(本章节其他篇)
- 华为官方:性能优化指南、权限文档、签名与发布、Native API 兼容性;HarmonyOS AI Skill 的 `recipes/debug-build-error.md`
