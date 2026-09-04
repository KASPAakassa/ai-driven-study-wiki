# Prompt 工程:用提示词约束与引导大模型

> **一句话摘要**:Prompt 是人与 LLM 的"编程接口":指令清不清晰、有没有示例、要不要分步推理,输出质量天差地别。
>
> **来源**:综合公开资料(OpenAI/Anthropic Prompt Engineering 指南、CoT 论文等)。

## 概念

- **Prompt 工程**:设计输入给 LLM 的指令文本(系统提示词、示例、格式约束),使输出**稳定**满足需求;是 Agent 的"大脑接口"([Agent 开发实践](agent-practice.md))。
- **为什么重要**:① LLM 是概率模型,提示词决定输出分布;② 成本与长度成正比;③ 输出格式决定下游能否解析。

## 原理

### 五项基础技巧

| 技巧 | 做法 | 效果 |
| --- | --- | --- |
| **清晰指令** | 动词开头、明确输入输出 | 减少歧义跑题 |
| **角色扮演** | "你是资深 Python 工程师" | 激活领域知识 |
| **Few-shot** | 给 2-5 个输入→输出示例 | 约束输出格式 |
| **CoT** | 先写推理步骤再给答案 | 显著提升逻辑/数学准确率 |
| **格式约束** | 指定 JSON/字数/步骤数 | 输出可解析自动化 |

**CoT 为何有效**:把中间推理"说出来",减少一步跳到结论的误差;零样本版即"Let's think step by step"。

### 结构化输出(JSON)

- 约束:prompt 给**目标 schema + 示例**,明确"只输出 JSON";开启 JSON 模式(`response_format`)。
- **必须容错解析**:模型常套代码围栏、加废话——剥围栏、提取 `{...}`、校验必填字段(见代码)。
- 只写"请输出 JSON"不够:要定义字段名与类型。

!!! warning "JSON 模式 ≠ schema 正确"
    语法合法不等于字段齐全——校验必填字段永远要做。

### 进阶:自我反思与多轮

- **自我反思(Reflexion)**:输出→自查→修正,2-3 轮显著提质量,代价是成倍 token(即 [多 Agent 协作](multi-agent.md) 的"批评型 Agent")。
- **多轮结构**:prompt 是 `system/user/assistant` 消息序列;历史即上下文,长任务要裁剪/摘要。

## 代码 / 实现

```python
"""Prompt 模板构造演示:zero-shot / few-shot / CoT / JSON 结构化输出。仅标准库。"""
import json
import re

def build_zero_shot(task, query):
    return f"{task}\n\n请回答:{query}"

def build_few_shot(task, examples, query):
    blocks = [f"示例 {i+1}:\n输入: {q}\n输出: {a}\n" for i, (q, a) in enumerate(examples)]
    return f"{task}\n\n" + "\n".join(blocks) + f"输入: {query}\n输出: "

def build_cot(task, examples, query):
    blocks = []
    for i, (q, a, steps) in enumerate(examples):
        step_text = "\n".join(f"步骤{j+1}: {s}" for j, s in enumerate(steps))
        blocks.append(f"示例 {i+1}:\n输入: {q}\n输出:\n{step_text}\n答案: {a}\n")
    return f"{task}\n\n" + "\n".join(blocks) + f"输入: {query}\n输出: "

def approx_tokens(text):
    zh = len(re.findall(r"[一-鿿]", text))
    en = len(re.findall(r"[A-Za-z0-9]+", text))
    return zh + en

class MockModel:
    """可解释的模拟模型:有示例就模仿格式,有 CoT 就分步。"""
    def generate(self, prompt):
        if "步骤1:" in prompt:
            return "步骤1: 已知 速度=60千米/小时, 时间=2.5小时\n步骤2: 列式 60 * 2.5 = 150\n答案: 150 千米"
        if "示例 1:" in prompt:
            return "答案: 150 千米"
        return "150"        # zero-shot:无格式约束,直接给数字

def parse_answer(text):
    m = re.search(r"答案:\s*([\d.]+)", text)
    return m.group(1) if m else None

def build_json_prompt(task, schema, query):
    return (f"{task}\n请严格输出 JSON,不要输出其他内容,格式如下:\n"
            f"{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n输入: {query}\n输出:")

def parse_json_response(text, required_keys):
    tick = chr(96) * 3   # 代码围栏
    text = re.sub(r"^" + tick + r"(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*" + tick + r"$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("输出中未找到 JSON 对象")
    data = json.loads(text[start:end+1])
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(f"缺少必填字段: {missing}")
    return data

if __name__ == "__main__":
    task = "你是小学数学老师,用中文回答下面的应用题。"
    query = "一辆汽车以 60 千米/小时的速度行驶 2.5 小时,求行驶距离。"

    few_examples = [("小明有 3 个苹果,又买了 5 个,一共几个?", "答案: 8 个")]
    cot_examples = [("小明有 3 个苹果,又买了 5 个,一共几个?", "8 个",
                     ["提取数量: 3 和 5", "列式: 3 + 5 = 8"])]

    model = MockModel()
    prompts = {
        "zero-shot": build_zero_shot(task, query),
        "few-shot":  build_few_shot(task, few_examples, query),
        "CoT":       build_cot(task, cot_examples, query),
    }
    print(f"问题: {query}\n")
    print("=== 三种模板的 prompt 差异 ===")
    for name, p in prompts.items():
        print(f"[{name}] token 数(近似): {approx_tokens(p)}, 字符数: {len(p)}")

    print("\n=== 模型输出与可解析性 ===")
    for name, p in prompts.items():
        out = model.generate(p)
        print(f"[{name}]\n  输出: {out!r}\n  提取答案: {parse_answer(out)}")

    print("\n=== JSON 结构化输出 ===")
    schema = {"answer": 0, "unit": "千米", "steps": []}
    raw = (chr(96)*3 + "json\n" + '{"answer": 150, "unit": "千米", "steps": ["60 * 2.5 = 150"]}' + "\n" + chr(96)*3)
    data = parse_json_response(raw, required_keys=["answer", "unit"])
    print("容错解析结果:", data)
```

**逐段解释**:

1. **模板构造**:`build_*` 拼任务、示例与查询;CoT 显式写步骤。
2. **差异量化**:`approx_tokens` 估算成本——示例与思维链线性增加输入。
3. **模拟模型**:zero-shot 只给数字(不可解析),few-shot 模仿格式,CoT 分步。
4. **JSON 容错**:`parse_json_response` 剥围栏、提取、校验。

**运行结果**(`python3` 直跑):token 数 zero(46) < few(74) < CoT(92);zero-shot 提取失败,few-shot/CoT 成功;围栏 JSON 解析成功。

## 实践 / 应用

### 常见误区

| 误区 | 后果 | 正确做法 |
| --- | --- | --- |
| 提示词越详细越好 | 指令过载矛盾 | 目标-约束-风格组织 |
| 只加"请小心" | 无实际约束力 | 给出格式与示例 |
| 一个 prompt 跑所有任务 | 任务互相干扰 | 拆成专用 prompt |
| 不看输出就上线 | 格式不可解析 | 先抓真实输出校验 |
| 幻觉靠提示词根治 | 压不住本质缺陷 | 给工具/RAG 提供事实 |

### 不同模型差异

| 维度 | 小/旧模型 | 大/新模型 |
| --- | --- | --- |
| 指令遵循 | 差,要 few-shot | 强,零样本也行 |
| CoT 增益 | 显著(尤其数学) | 有效但变小 |
| JSON 输出 | 常带废话/自创 schema | 原生 JSON 模式 |
| 上下文长度 | 4K-8K | 128K+ |

**启示**:① 先在最弱模型上写好 prompt 保证兼容;② 换模型必重测(提示词不可移植);③ 成本与效果一起评测(见 [Agent 开发实践](agent-practice.md))。

## 总结

- Prompt 工程 = 用**指令 + 角色 + 示例 + 格式约束**稳定化 LLM 输出。
- 五项技巧中 CoT 对逻辑/数学提升最明显;结构化输出要做容错解析。
- 误区:过度冗长、空喊"小心"、任务混杂;幻觉靠工具/RAG 而非提示词根治。
- 不同模型差异大,先按最弱模型设计、换模型必重测。
- 下一步:模板接进 [Agent 开发实践](agent-practice.md),或用 [多 Agent 协作](multi-agent.md) 做自我反思。

## 延伸阅读

- 站内:[Agent 开发实践](agent-practice.md)、[多 Agent 协作](multi-agent.md)、[LLM 基础](../02-llm/index.md)
- 外部:OpenAI《Prompt Engineering Guide》;Wei et al.《Chain-of-Thought Prompting Elicits Reasoning in Large Language Models》;Shinn et al.《Reflexion: Language Agents with Verbal Reinforcement Learning》
