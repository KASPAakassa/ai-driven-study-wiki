# Git Worktree:多 Agent 并行开发的隔离底座

> **一句话摘要**:多个 Coding Agent 同时在一个仓库干活,分支只隔离提交历史、不隔离工作目录——冲突发生在提交之前,Git 都来不及介入。Git Worktree 让同一仓库拥有多个相互独立的修改现场:共享对象库、隔离工作目录/HEAD/index,把"不要覆盖别人的文件"从协作约定变成**物理隔离**。本文讲清原理、完整链路、多 Agent 任务契约与常见坑。
>
> **来源**:微信公众号「程序员无隅」《Git Worktree:多任务并行开发为什么不应共用一个工作目录》,https://mp.weixin.qq.com/s/6yq4fdvnkKIHeWf6hGSStw;参考:Git 官方文档 git-worktree、OpenAI《Introducing the Codex app》;原始资料存档于 `docs/inbox/git-worktree-source.md`

## 概念:为什么分支不够用

两个开发任务同时落到一个仓库,很多人第一反应是"多建两个分支"。但**分支只隔离了提交历史,没有提供两个可以同时工作的文件目录**——当前目录里仍然只有一份文件、一份暂存区和一个检出的 HEAD。

人工开发时这通常只是"切分支不方便";到了 **Coding Agent 并行执行**的场景,它变成真实的工程风险:

```
A 修改了接口文件,但尚未提交
B 在同一个目录中读取代码,看到 A 的半成品      ← 中间状态泄漏
B 修改客户端,同时运行测试
A 又调整接口定义,覆盖或破坏 B 的假设          ← 覆盖
最后一次测试只证明"某个瞬间的目录状态可以运行" ← 假绿灯
```

这不是传统意义的 Git 合并冲突——**Git 甚至没有机会介入,因为冲突发生在提交之前**。人工协作可以口头约定"你先别动这个文件";Agent 不会天然拥有这种同步机制。即使给每个 Agent 分配不同文件,接口变化、生成文件、格式化工具和测试缓存仍可能互相影响。

!!! tip "并行之前先回答一个问题"
    **每个任务是否拥有自己的文件系统边界?**

## 原理:Worktree 的本质——共享对象,隔离现场

Git 官方定义:一个仓库可以关联多个工作树,从而**同时检出多个分支**。Worktree 不是重新 `git clone` 一遍——多个工作树**共享对象库、引用和提交历史**,但每个工作树拥有自己的:

- **工作目录**:磁盘上实际可见和可编辑的文件;
- **HEAD**:当前检出的提交或分支;
- **index**:暂存区;
- 未提交修改与未跟踪文件。

实现上,linked worktree 根目录里的 `.git` 通常不是完整目录,而是指向主仓库管理数据的文件;Git 通过 `$GIT_DIR/worktrees/<id>` 保存这个工作树的私有状态,通过公共 Git 目录访问共享对象。

!!! warning "默认约束:同一本地分支不能被多个工作树同时检出"
    这不是故意添麻烦,而是在**阻止两个目录同时推进同一个分支**,避免分支指针和工作区状态失去清晰归属。多 Agent 场景应该为新任务建独立分支,而不是用 `--force` 争用。

## 代码 / 实现:完整使用链路

```bash
# 1. 查看已关联的工作树
git worktree list

# 2. 从 main 创建新分支并检出到相邻目录(一步完成两件事)
git worktree add -b feature/api ../repo-api main

# 3. 进入新目录,开发过程与普通仓库无区别
cd ../repo-api && git add . && git commit -m "feat: update api contract"

# 4. 回到集成工作树,合并整个分支(或只挑选单个提交)
git switch main
git merge --no-ff feature/api
# 或: git cherry-pick <commit-sha>

# 5. 最终测试必须在集成后的工作树运行(子任务测试只能证明局部成立)

# 6. 回收:移除工作树 + 清理失效记录
git worktree remove ../repo-api
git worktree prune --dry-run   # 先看将清理什么
git worktree prune

# 实验用 detached worktree(不保留分支)
git worktree add --detach ../repo-experiment HEAD
```

!!! warning "不要一遇到删除失败就用 --force"
    Git 拒绝删除带有未提交修改或未跟踪文件的工作树,**正是在保护尚未交付的成果**。先 `git status` 确认修改归属(提交/备份/放弃)。

### 多 Agent 任务契约(比"完成接口修改"更可靠)

把任务交给子 Agent 时,契约至少包含六要素:

| 要素 | 内容 |
| --- | --- |
| **目标** | 要得到什么可观察结果 |
| **基线** | 从哪个提交或分支开始 |
| **路径边界** | 允许修改哪些文件 |
| **接口约定** | 输入、输出和依赖不能随意改变的部分 |
| **交付物** | 提交哈希、变更摘要、测试结果 |
| **验收方式** | 主 Agent 如何独立验证 |

### 任务契约的路径边界校验(纯 Python 演示)

路径边界是六要素里最容易被违反的——子 Agent 常常"顺手"改了边界外的文件。一个简单的校验器:

```python
import fnmatch

def validate_contract(files_changed: list[str], allowed_patterns: list[str],
                      interface_files: list[str]) -> dict:
    """校验子 Agent 交付是否符合路径边界契约。"""
    violations = []
    for f in files_changed:
        allowed = any(fnmatch.fnmatch(f, p) for p in allowed_patterns)
        if not allowed:
            violations.append(f"越界修改: {f} 不在允许路径内")
    for f in files_changed:
        if f in interface_files:
            violations.append(f"接口契约变更: {f} 属于'不能随意改变'的文件,需单独确认")
    return {
        "status": "PASS" if not violations else "FAIL",
        "violations": violations,
        "deliverables_ok": True,   # 演示:交付物(提交哈希/测试结果)已齐备
    }

# 演练:任务 A 只允许改 server/ 下文件,接口文件为 server/contract.py
files = ["server/api.py", "server/contract.py", "client/call.py"]  # client/call.py 越界
r = validate_contract(files, ["server/*.py"], ["server/contract.py"])
print(f"校验结果: {r['status']}")
for v in r["violations"]:
    print("  -", v)
```

## 实践 / 应用:多 Agent 并行开发的典型链路

把主工作树看成**集成区**,linked worktree 看成各 Agent 的**独立施工区**:

1. 主 Agent 分析任务依赖,确认哪些子任务可以并行;
2. 为每个写代码的子任务创建独立分支 + Worktree;
3. 将任务目标、允许修改的路径、接口约定、验证命令交给子 Agent;
4. 子 Agent 在自己的 Worktree 中修改、测试并形成提交;
5. 子 Agent 返回**提交哈希、测试结果、修改文件和已知风险**;
6. 主 Agent 依次集成这些提交,并运行最终验证;
7. 确认后删除临时 Worktree 和任务分支。

!!! tip "物理隔离不是最终目的"
    真正有价值的交付物是**可追踪的提交**,而不是留在临时目录里的文件。主 Agent 应当**通过提交进行集成**,避免人工复制文件导致历史、作者和变更边界丢失。OpenAI 在 Codex App 中也内置了 Worktree 支持,用于多个 Agent 在同一仓库并行工作。

### 常见问题 FAQ

| 问题 | 解法 |
| --- | --- |
| 创建时提示"分支已被检出" | 为新任务建独立分支,别用 `--force` 争用同一分支 |
| `worktree remove` 拒绝删除 | 进目录 `git status`;确认修改归属后重试,不要一上来就 `--force` |
| 删了目录但 `worktree list` 仍有记录 | 手动删除绕过了 Git 管理;`git worktree prune --dry-run` 预览后 `prune` |
| 代码隔离了,运行环境却互相影响 | Worktree 不管数据库/端口/容器/环境变量;`.venv`、`node_modules` 不会自动共享,运行目录要单独设计 |
| 移动了 Worktree 目录 | 优先 `git worktree move`;被外部工具移动后用 `git worktree repair` |
| 项目含 submodule | 多工作树与 submodule 组合支持不完整,先小范围验证再自动化 |

### Worktree 能解决 / 不能解决什么

**能解决**:并行任务的**修改现场隔离**——多分支同时检出、独立 HEAD/暂存区、主工作目录保持干净、失败实验可直接丢弃、子任务通过提交形成清晰可回滚的交付边界。

**不能解决**:两个任务最终改同一段代码的合并冲突、上游接口未定下游提前实现的语义冲突、数据库/端口/消息队列等运行时资源竞争、任务拆分错误与验收标准缺失、集成后才出现的跨模块测试失败。

!!! note "什么时候不值得用"
    只有一个短任务,或多个步骤严格前后依赖时,单工作树顺序完成通常更简单。**只有当任务确实可并行、并发收益高于创建和集成成本时,Worktree 才真正产生价值**——它是并行开发的隔离底座,不是调度器;在它之上仍需要任务依赖分析、路径所有权、统一集成和最终验证。

## 总结

- **Worktree 本质**:共享 Git 对象库,隔离工作目录/HEAD/index——把"不要覆盖别人的文件"从约定变成物理隔离;
- **多 Agent 场景**:主工作树 = 集成区,linked worktree = 施工区;通过提交集成,不靠复制文件;
- **任务契约六要素**:目标 / 基线 / 路径边界 / 接口约定 / 交付物 / 验收方式;
- **边界认知**:解决修改现场隔离,不解决合并冲突、运行时资源竞争与任务拆分错误——是底座,不是调度器;
- **落地判断**:只有任务真正可并行时才值得用;短任务和严格依赖场景单工作树更简单。

## 延伸阅读

- Git 官方文档:git-worktree;OpenAI《Introducing the Codex app》(内置 Worktree 支持多 Agent 并行);原文:https://mp.weixin.qq.com/s/6yq4fdvnkKIHeWf6hGSStw
- 站内:[多 Agent 协作](../../03-agents/multi-agent.md)(协调成本与模式)、[Loop Engineering](loop-engineering.md)(无人值守迭代)、[Agent 规划与工作流模式](../../03-agents/agent-planning-patterns.md)(任务拆解)、[Superpowers v6](../skills/mattpocock-skills.md)(并行 worktrees 探索方案的实践案例)
