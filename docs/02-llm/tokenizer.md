# Tokenizer 与词表:模型认识世界的第一个窗口

> **一句话摘要**:大模型不认字,只认 **token 编号**。Tokenizer 把文本切成词表符号再编码成数字。本文讲三种粒度、BPE 训练与编码、特殊 token 与中文注意点。
>
> **来源**:论文《Neural Machine Translation of Rare Words with Subword Units》(Sennrich et al., 2016)、OpenAI GPT-2 论文、Hugging Face tokenizers 文档。

## 概念

- **定义**:Tokenizer(分词器)把原始文本切分成一个个 **token**,映射成整数 id 供模型输入;全部 token 构成**词表**,大小记为 $V$,语言模型输出层就是 $V$ 类分类器。
- **为什么需要分词**:神经网络只吃数值向量,不吃字符串;分词确定"最小语义单位",决定**模型能说什么、要花多少算力**。
- **三种粒度**:字符级、词级、子词级。LLM 主流是**子词**(BPE/Unigram/WordPiece),平衡了**词表大小**与**未登录词覆盖**。

| 粒度 | 词表大小 | 未登录词 | 序列长度 | 代表 |
|---|---|---|---|---|
| 字符级 | 很小(几百) | 无 OOV | 很长(算力浪费) | 早期 RNN |
| 词级 | 很大(百万级) | 严重 OOV | 短 | 统计翻译 |
| 子词 BPE | 适中(3 万~15 万) | 任意新词可拼出 | 中等 | GPT、Llama |

## 原理

### 1. 子词思想的由来

语言里大量形态变化与复合词(英语 `-ing/-ed`、德语复合词;中文"人工智能"由"人工""智能"组成)。与其整词存,不如把词拆成**可复用的子词单元**:`lower` → `low` + `er`。好处:词表小、覆盖面大、任何生词都能用已有子词拼出来。

### 2. BPE 算法:训练与编码

BPE(Byte Pair Encoding)来自数据压缩,分两步:

**训练(从字符出发,反复合并最频繁的相邻对):**

1. 初始化:每个词拆成字符序列,词尾加 `</w>` 边界标记,带上词频;
2. 统计所有**相邻符号对**的出现次数(按词频加权);
3. 选出现次数最多的相邻对,合并成一个新符号,加入词表;
4. 重复 2~3 步,直到词表达到目标大小(如 32k、50k)。

**编码(新文本按学到的 merge 顺序切分):** 从字符序列开始,按训练时的合并顺序从左到右应用,能并则并。于是**训练时没见过的词**(`lowest`)也能被拆成 `low` + `est` ——这就是 BPE 解决未登录词的机制。

### 3. 词表大小与未登录词

- **OOV(out-of-vocabulary)**:词级分词下,不在词表里的词变成 `<unk>`,信息直接丢失。BPE 的子词粒度几乎消灭了 `<unk>`——总能用字符兜底。
- **词表大小的权衡**:$V$ 太大 → 输出层 softmax 计算贵、嵌入表占显存;$V$ 太小 → 一个词被拆太碎,序列变长、信息分散。经验区间 3 万~15 万。

### 4. 特殊 token

词表里除了普通子词,还预留**控制符号**:

| token | 作用 |
|---|---|
| `<s>` / `</s>` | 句首 / 句尾(GPT 用 `<|endoftext|>` 分隔文档) |
| `<unk>` | 未知符号(子词时代基本用不到) |
| `<pad>` | 批量训练时对齐长度 |
| `<|user|>` `<|assistant|>` | 对话角色标记(微调时教会模型"谁在说话") |

特殊 token **不在普通文本中分词**,训练与推理必须保持一致。

### 5. 中文场景注意

中文**没有天然空格分词**,词边界模糊("机器学习/机器/学习")。常见做法:

- **按字符/字拆分**,让 BPE 在数据上自动发现"人工""智能"这类高频组合;
- **中文一个汉字约 1~2 个 token**,同义内容常比英文 token 更多,影响成本与上下文窗口占用;
- 标点、数字、英文混排需统一规则,避免碎片化。

!!! tip "直观感受 token 数"
    拿一段中文到 API 的 usage 字段或 tiktoken Playground 数一数:20 个字的一句话往往被切成 30+ token。记着"4k token ≈ 3000 汉字",写长提示词时心里有数。

## 代码 / 实现

用纯 Python 演示 **BPE 训练(合并)** 与 **编码(应用 merge)** 的完整流程:

```python
from collections import Counter

# 训练语料:每个词带出现次数(真实场景来自大规模文本的词频统计)
corpus = {"low": 5, "lower": 2, "newest": 6, "widest": 3}

# 初始词表:每个词拆成字符序列,词尾加 </w> 边界标记
vocab = {" ".join(list(word)) + " </w>": freq for word, freq in corpus.items()}
print("初始词表:")
for w, f in vocab.items():
    print(f"  {w!r:>16} x{f}")


def get_stats(vocab):
    """统计所有相邻符号对的共现次数(乘上词频)"""
    pairs = Counter()
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i + 1])] += freq
    return pairs


def merge_vocab(pair, vocab):
    """把最频繁的相邻对合并成一个新符号(如 'l o' -> 'lo')"""
    bigram = " ".join(pair)
    merged = "".join(pair)
    return {word.replace(bigram, merged): freq for word, freq in vocab.items()}


# BPE 训练:迭代合并最频繁的相邻符号对
merges = []
for step in range(8):
    pairs = get_stats(vocab)
    if not pairs:
        break
    best = max(pairs, key=pairs.get)          # 出现次数最多的相邻对
    merges.append(best)
    vocab = merge_vocab(best, vocab)
    top = sorted(pairs.items(), key=lambda kv: -kv[1])[:3]
    print(f"merge {step+1}: 最频繁 {' '.join(best)!r:>10} -> {''.join(best)!r:<5} "
          f"(频率 {pairs[best]})  | 前三: {[(a[0]+a[1], n) for a, n in top]}")

# 编码新词:按训练得到的 merge 顺序,从左到右依次应用
def bpe_encode(word, merges):
    symbols = list(word) + ["</w>"]
    for pair in merges:
        new_symbols, i = [], 0
        while i < len(symbols):
            if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) == pair:
                new_symbols.append(symbols[i] + symbols[i + 1])
                i += 2
            else:
                new_symbols.append(symbols[i])
                i += 1
        symbols = new_symbols
    return symbols

for w in ("lowest", "newer", "wide"):
    print(f"编码 {w!r}: {bpe_encode(w, merges)}")
```

- **训练段**即 BPE 核心:第 1 轮合并 `e s`(频率 9),逐步拼出 `est`、`low`、`new`——高频子词被"凝聚"进词表。
- **编码段**演示 OOV:训练语料没有 `lowest`,仍被拆成 `['low', 'est</w>']`;`wide` 拆成字符兜底,保证**生词都能编码**。
- 真实实现(Hugging Face `tokenizers`、OpenAI `tiktoken`)还有字节级处理、正则预切分、Unigram 等细节,核心思想一致。

运行:`python3 bpe_demo.py`(仅标准库)。**实际工程**:`pip install tokenizers`,`tokenizers.BPE().train_from_iterator(...)` 可在自建语料上训练。

## 实践 / 应用

- **词表大小**:英文通用模型 32k~50k(GPT-2 50257、Llama 32000);中英混合或中文为主常到 50k~150k。
- **token 就是钱**:API 按 token 计费,`1 token ≈ 0.75 英文单词 ≈ 0.6~1 汉字`;精简提示词能降本。
- **对齐问题**:上下文窗口、KV Cache 都以 token 计;中文长文要预留余量。
- **常见坑**:特殊 token 与文本内容冲突;训练/推理 tokenizer 版本不一致致乱码;换词表需重新训练(嵌入层维度 = V)。

## 总结

- Tokenizer 决定**最小语义单位**:字符太碎、词级有 OOV,子词(BPE)是主流。
- BPE 训练 = 反复合并**最频繁相邻对**;编码 = 按 merge 顺序切分,天然抗未登录词。
- 词表要留**特殊 token**(句界、对话角色、填充)。
- 中文无空格分词,注意 token 数与成本放大效应。
- 训练/推理 tokenizer 必须一致,词表大小要权衡显存与序列长度。

**下一步**:进入 [预训练与规模定律](pretraining.md),看模型在切好的 token 上如何被训练出来。

## 延伸阅读

- 站内:[Transformer 架构](transformer-architecture.md)、[预训练与规模定律](pretraining.md)、[大语言模型概述](llm-intro.md)
- 外部:论文《Neural Machine Translation of Rare Words with Subword Units》(BPE 原始出处)、Hugging Face tokenizers 文档、OpenAI tiktoken 仓库
