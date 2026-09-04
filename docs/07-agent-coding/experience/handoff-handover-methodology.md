# Agent 交接方法论:让长任务接力不中断

> **一句话摘要**:AI 协作一旦变成长链路(跨天、跨 agent),真正稀缺的不是"再生成一点内容",而是"让接力不中断"。本文把 handoff 的思路提炼成一套**交接方法论**:六问压缩当前状态、八项清单保证接手方 10 分钟上手、引用路径不复制内容、三类场景与两版提示词,并附一个交接文档完整性校验器。
>
> **来源**:微信公众号「AI普惠」《handoff:把上下文压成接力文档》,https://mp.weixin.qq.com/s/2GmN8lCjbTJLf_bQyd29yw;原始资料存档于 `docs/inbox/handoff-skill-source.md`

## 概念:上下文接力是长任务协作的隐形瓶颈

把 AI 当成"能持续推进任务的同事"后,最常遇到的情况:任务没做完、聊天已经很长;下一轮还要继续、上下文已经散了。你不想重新解释一遍,也不想让下一位 agent 从头爬聊天记录。

!!! tip "把交接想成交班单"
    它像异步工程协作里的交班单:好的 handoff 不是"我做到这里了",而是把当前状态**压缩成下一位 agent 能接住的交接件**。价值不是文书漂亮,而是**形成工作记忆**——任务能不能持续推进,往往不取决于单轮表现,而取决于上下文能不能被稳稳接住。

## 原理:六问 + 三条纪律

### 一个合格的 handoff 至少回答六个问题

| # | 问题 | 反面例子 |
| --- | --- | --- |
| 1 | **目标**是什么 | "继续之前的任务" |
| 2 | **已经确认了哪些事实** | 没列任何已核实结论 |
| 3 | **已经做了哪些改动或验证** | 只说"做了些事" |
| 4 | **还有哪些问题没解** | 隐藏未完成事项 |
| 5 | **哪些风险值得优先注意** | 不提示风险 |
| 6 | **下一步最适合调用什么 skill** | 不给接手方工具提示 |

### 三条纪律(让交接件精简、可信、可追踪)

1. **单独成文**:交接文档独立存在,不埋在线程里;
2. **suggested skills**:告诉下一位 agent 接下来用哪些 skill,而不是让它自己猜;
3. **引用路径,不复制内容**:不要重复已有需求文档、计划、ADR、issue、commit 或 diff——直接引用路径/链接。复制会让文档越长越旧,引用让接手方按需读取最新内容。

!!! warning "交接文档不是聊天摘录"
    如果一份 handoff 连"目标/输入/输出/边界/确认点/权限/来源/下一步清单"八项都不全,那它更像聊天摘录。它还必须告诉接手方:**下一步先读哪个 issue、先看哪个 PR、先对哪段代码和测试做 review、哪些 diff 可以忽略、哪些权限不能越界**——这样它才是接力工具,而不是总结。

## 代码 / 实现:交接文档完整性校验器(纯 Python)

把"八项清单"落成可运行的校验器——提交交接文档,检查八项是否齐全、是否引用了路径而非大段复制:

```python
REQUIRED = ["目标", "输入", "输出", "边界", "确认点", "权限", "来源", "下一步"]

def validate_handoff(doc: str) -> dict:
    missing = [k for k in REQUIRED if k not in doc]
    # 纪律 3:检查是否大段复制了代码/路径内容(启发式:连续代码行或超长引用)
    copied = doc.count("```") >= 4 or any(
        line.strip().startswith(("git ", "def ", "import ")) and len(line) > 40
        for line in doc.splitlines()
    )
    has_paths = ("issues/" in doc or "pull/" in doc or ".py" in doc or ".md" in doc)
    return {
        "status": "PASS" if not missing and has_paths else "FAIL",
        "missing_items": missing,
        "suspicious_copy": copied,
        "has_path_refs": has_paths,
    }

# 演示:一份合格的 handoff(含路径引用)
good = """
目标:修复登录重定向循环
输入:issue #42 复现步骤
输出:PR 到 main 分支
边界:不修改认证模型
确认点:发布前需人工确认
权限:仅 repo 写权限,不碰生产凭证
来源:https://github.com/org/repo/issues/42, tests/test_login.py
下一步:先读 tests/test_login.py 的失败用例,用 code-review skill
"""
print(validate_handoff(good))
```

## 实践 / 应用:三类场景与两版提示词

### 场景(正式交班,不是顺手总结)

1. **PR 未 ready 但有线索**:已有 issue、diff、测试和 review 线索,交给下一位 agent 收尾;
2. **排查做了一半**:已建立复现脚本、排除两个假设、找到可疑模块,明天再接——handoff 把"明天 20 分钟回忆"压缩成 2 分钟;
3. **agent 之间 / agent 交回给人**:多 agent 协作或跨天工作时,交接件是唯一可靠的上下文载体。

### 提示词(两版)

**简短版**(阶段性完成后触发):

> "把当前任务整理成 handoff。面向下一位 agent。列目标、现状、已完成、未完成、风险、建议 skill。不要复制已有计划和 diff,只引用路径。注意脱敏。"

**详细版**(正式交班):

> "把当前线程整理成 handoff。目标是让下一位 agent 10 分钟内接手。请写清目标、输入、输出、边界、确认点、权限和来源。引用现有 issue、PR、diff、review、测试结果和代码路径,不要重复抄写。最后附一份下一步清单和建议 skill。"

!!! tip "与站内其他经验的衔接"
    - [Git Worktree 并行开发](git-worktree-parallel-agents.md) 的"任务契约六要素"(目标/基线/路径边界/接口约定/交付物/验收方式)与 handoff 八项高度同构——契约是交接前的约定,handoff 是交接时的状态压缩,两者配合使用;
    - [Loop Engineering](loop-engineering.md) 的"无人值守迭代"里,handoff 可作为阶段检查点之间的状态载体(尤其 Loop 被中断恢复时);
    - [Graph Engineering 14 步](graph-engineering-14-steps.md) 的节点 contract(有界输入/确定输出)与 handoff 的"有边界的交接文档"是同一原则在节点级与任务级的体现。

## 总结

- **核心**:交接 = 把"下一轮必须知道的内容"压出来,而不是保留全部聊天记录;
- **六问**:目标/事实/改动验证/未解问题/优先风险/下一步 skill;
- **八项清单**:目标/输入/输出/边界/确认点/权限/来源/下一步清单;
- **三纪律**:单独成文、suggested skills、引用路径不复制内容;
- **判断标准**:接手方能否 10 分钟内上手且不越界——能,才是接力文档;不能,只是聊天摘录。

## 延伸阅读

- 原文:https://mp.weixin.qq.com/s/2GmN8lCjbTJLf_bQyd29yw;Skill 源码:https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff
- 站内:[handoff Skill 收藏](../skills/handoff-skill.md)(Skill 角度)、[Git Worktree 并行开发](git-worktree-parallel-agents.md)(任务契约)、[Loop Engineering](loop-engineering.md)、[Graph Engineering 14 步](graph-engineering-14-steps.md)(contract 原则)
