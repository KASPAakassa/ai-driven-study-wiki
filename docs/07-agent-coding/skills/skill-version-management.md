# Agent Skill 版本管理:源代码层与运行时层

> **一句话摘要**:Skill 不是普通文档,而是**会改变 Agent 行为的可执行资产**——改一个触发词或删一个步骤,Agent 的行为就可能变。因此它的版本管理必须分两层:**源代码层**(Git,版本控制的最小单位是**整个 Skill 目录**而非单个文件)+ **运行时层**(生产环境锁定版本,配合评测、兼容性检查、灰度验证与快速回滚)。开发环境可以跟随最新版,生产环境必须钉死版本。
>
> **来源**:大模型工程化面试题拆解(视频内容,用户提供);原始资料存档于 `docs/inbox/skill-versioning-source.md`

## 概念:为什么 Skill 需要版本管理

!!! tip "一句话判断"
    **Skill 是会改变 Agent 行为的可执行资产**——它不是知识卡片,而是"给 Agent 装上的一段行为"。这个定位决定了:它的变更必须像代码一样可追踪、可评审、可回滚。

Skill 的"行为"由四部分共同决定:**说明(SKILL.md)、脚本、模板、参考资料**。改任何一部分都可能改变 Agent 在触发时的表现——这正是版本管理的最小单位必须是**整个目录**而非单个文件的原因。

## 原理:两层版本管理

### 第一层:源代码层(用 Git 管)

| 管理维度 | 做法 | 为什么 |
| --- | --- | --- |
| **版本控制最小单位** | **整个 Skill 目录**,不是单个文件 | 行为由说明/脚本/模板/参考共同决定,单文件版本会丢失"整体行为"语义 |
| **变更流程** | 每次修改有提交记录 + 评审人 + 变更说明 | 可审计:谁改的、为什么改、影响什么 |
| **依赖管理** | 脚本依赖版本也锁定(requirements/packages 锁版本) | 依赖升级可能悄悄改变 Skill 行为 |
| **版本标记** | 语义化版本标记业务发布 | 见下表 |

**语义化版本(SemVer)对 Skill 的映射**:

| 版本位 | Skill 场景 | 例子 |
| --- | --- | --- |
| **修订号 patch**(x.y.`z`) | 不影响兼容性的改动 | 修复错别字、调整提示词措辞、补充示例 |
| **次版本 minor**(x.`y`.z) | 新增兼容能力 | 新增可选步骤、扩展脚本功能(行为兼容) |
| **主版本 major**(`x`.y.z) | **不兼容改动** | 修改触发边界、删除步骤、改变输出格式 |

!!! warning "两个高频错误**
    ①把 Skill 当文档管理:只改文件不提交、不评审、不标记版本——行为漂移无据可查;
    ②单文件版本化:只给 SKILL.md 加版本号,脚本/模板改了却没反映——目录内各文件版本不一致,整体行为不可复现。

### 第二层:运行时层(生产环境的重点)

!!! tip "开发 vs 生产分离**
    **开发环境跟随最新版**(快速迭代);**生产环境必须锁定明确版本**(行为可预期)——这是 Skill 版本管理区别于普通代码管理的核心:代码发布是"打包上线",Skill 发布是"行为变更上线",影响的是 Agent 的决策与行动。

**生产上线四道关卡**(对应视频概述):

1. **评测(Eval)**:新版本在评估集上跑分/对比——Skill 版本与 Agent 效果挂钩,必须先证明"新版不劣于旧版"(呼应站内 [Eval Engineering Skill](eval-engineering-skill.md) 与 [评估驱动开发](../../03-agents/agent-eval-driven-dev.md));
2. **兼容性检查**:触发边界、输出格式、依赖版本是否破坏既有调用方;
3. **灰度验证**:先让部分流量/任务使用新版,观察行为与指标,再逐步放量;
4. **快速回滚**:一旦异常,立即切回上一个锁定版本——回滚能力是"敢上线"的前提(呼应 [企业工程化(二)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md) 的"回滚后路"与 [Gate 模式](../experience/gate-pattern.md) 的上线门禁)。

## 代码 / 实现:语义化版本判定 + 目录版本标记(纯 Python)

```python
import hashlib, re

# —— 1) 语义化版本判定:按变更类型决定升哪一位 ——
def bump_version(current: str, breaking: bool, feature: bool = False) -> str:
    """breaking→主版本;feature→次版本;否则→修订号"""
    major, minor, patch = (int(x) for x in current.split("."))
    if breaking:
        return f"{major + 1}.0.0"
    if feature:
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"

for change, breaking, feature in [
    ("修复触发词错别字", False, False),   # → patch
    ("新增可选输出格式", False, True),    # → minor
    ("删除一个执行步骤", True, False),    # → major(不兼容)
]:
    print(f"  {change:14} → {bump_version('1.2.3', breaking, feature)}")
assert bump_version("1.2.3", False, False) == "1.2.4"
assert bump_version("1.2.3", False, True) == "1.3.0"
assert bump_version("1.2.3", True) == "2.0.0"

# —— 2) 目录级版本指纹:整个 Skill 目录决定行为版本 ——
def skill_fingerprint(skill_dir_files: dict) -> str:
    """对目录内全部文件(SKILL.md/脚本/模板/参考)做合并 hash——
    任一文件变化,指纹即变(行为可能变),而不是只看 SKILL.md"""
    h = hashlib.sha256()
    for name in sorted(skill_dir_files):
        h.update(name.encode())
        h.update(skill_dir_files[name].encode())
    return h.hexdigest()[:12]

v1 = {"SKILL.md": "trigger: 总结\nsteps: [a, b]", "script.py": "print('a,b')", "tpl.md": "tpl"}
v2 = {"SKILL.md": "trigger: 总结\nsteps: [a, b, c]", "script.py": "print('a,b')", "tpl.md": "tpl"}  # 步骤变更
print("\n目录指纹 v1:", skill_fingerprint(v1))
print("目录指纹 v2:", skill_fingerprint(v2), "(步骤变了 → 指纹变了,需 major 版本)")
assert skill_fingerprint(v1) != skill_fingerprint(v2)
print("代码验证通过 ✔")
```

## 实践 / 应用:落地建议与知识库整合

### Skill 版本管理落地 checklist

1. **目录入库**:整个 Skill 目录进 Git,单目录一个版本号;
2. **变更三件套**:提交记录 + 评审人 + 变更说明(写明行为影响);
3. **依赖锁版本**:脚本依赖 pinned(锁精确版本),避免升级漂移;
4. **语义化标记**:兼容改动升 patch、新增升 minor、不兼容(改触发边界/删步骤/变输出)升 major;
5. **生产锁定 + 四道关卡**:评测 → 兼容检查 → 灰度 → 可回滚;开发环境跟随 latest,生产环境钉死版本号;
6. **发布即归档**:每次生产发布记录"Skill 版本 ↔ 评测结果 ↔ 灰度范围 ↔ 回滚点"。

!!! note "与站内其他文章的呼应**
    - [Eval Engineering Skill](eval-engineering-skill.md) / [评估驱动开发](../../03-agents/agent-eval-driven-dev.md):上线前评测是"四道关卡"第一关的理论支撑;
    - [Superpowers v6](mattpocock-skills.md):其 RELEASE-NOTES 机制正是"变更说明 + 版本标记"的实践样本;
    - [企业工程化(二)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md):"回滚后路"与"快速回滚"同一原则;
    - [Gate 模式](../experience/gate-pattern.md):Skill 上线(行为变更上线)正是 gate 的适用场景——不可逆动作前人工确认;
    - [handoff Skill](handoff-skill.md):Skill 目录可继承/可更新,版本管理让"换版本"像换代码一样可控。

## 总结

- **定位**:Skill = 会改变 Agent 行为的可执行资产,不是文档;
- **两层管理**:源代码层(Git,最小单位=整个目录,变更流程+依赖锁定+语义化版本)/ 运行时层(生产锁定版本+评测+兼容检查+灰度+快速回滚);
- **SemVer 映射**:patch=兼容小修 / minor=新增兼容能力 / **major=改触发边界·删步骤·变输出(不兼容)**;
- **开发 vs 生产**:开发跟随最新,生产钉死版本——"Skill 发布是行为变更上线";
- **一句话**:Skill 版本管理回答的是"Agent 行为为何会变、变了找谁、如何安全变回去"——把它当代码管,而不是当文档管。

## 延伸阅读

- 原始素材:大模型工程化面试题拆解(视频,用户提供),存档于 `docs/inbox/skill-versioning-source.md`
- 站内:[Skill 收藏](index.md)、[Eval Engineering Skill](eval-engineering-skill.md)、[Superpowers v6](mattpocock-skills.md)、[Gate 模式](../experience/gate-pattern.md)、[企业工程化(二)](../../06-enterprise/ontology-agent-adoption/enterprise-agent-recovery-handoff.md)、[评估驱动开发](../../03-agents/agent-eval-driven-dev.md)
