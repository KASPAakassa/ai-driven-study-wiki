# 循环神经网络 RNN:让网络拥有"记忆"

> **一句话摘要**:RNN(Recurrent Neural Network)是为**序列数据**(文本、语音、时间序列)设计的神经网络——通过**隐藏状态**在时间步之间传递信息,让网络"记住"前面的内容。核心机制是参数共享(每个时间步用同一组权重)与循环连接。LSTM/GRU 用门控机制解决 RNN 的梯度消失问题,是 RNN 家族的实战主力(虽然如今很多序列任务已被 Transformer 取代)。
>
> **来源**:综合公开资料(CS224n 讲义、PyTorch 官方教程 https://pytorch.org/tutorials),由 AI 助手按站内模板整理

## 概念

**RNN** 处理序列数据:输入是一个序列(句子中的词、股票每天的价格、音频帧),输出可以是序列(翻译、生成)或单个值(情感分类、预测)。

**与 [MLP](dl-neural-network-basics.md)/[CNN](dl-cnn.md) 的核心区别**:

- MLP/CNN 把输入当**定长向量**处理,一次前向;
- RNN **逐步处理**序列,每一步都结合**上一步的隐藏状态**——这就是它的"记忆"。

**一句话**:RNN = 在时间维度上展开的、参数共享的小网络,每个时间步的隐藏状态 \(h_t\) 携带前面所有步的压缩信息。

## 原理:隐藏状态与门控

### 基本 RNN 单元

每个时间步 \(t\),输入 \(x_t\) 与上一步隐藏状态 \(h_{t-1}\) 一起计算:

$$h_t = \tanh(W_{hh}h_{t-1} + W_{xh}x_t + b)$$

输出 \(y_t\) 由 \(h_t\) 决定。**所有时间步共享同一组权重**(\(W_{hh}, W_{xh}\))——参数共享使模型能处理任意长度序列,也大幅减少参数量。

**问题:长期依赖与梯度消失**。反传时梯度要穿过很多时间步,**连乘导致梯度指数衰减**(或爆炸)——RNN 很难学会"记住 50 步前的内容"。这就是简单 RNN 的致命短板。

### LSTM:用门控解决记忆问题

**LSTM(Long Short-Term Memory)** 引入**细胞状态 \(c_t\)**(长期记忆带)与三个门:

| 门 | 作用 |
| --- | --- |
| 遗忘门 | 决定从细胞状态**丢弃**什么 |
| 输入门 | 决定把新信息**写入**什么 |
| 输出门 | 决定从细胞状态**输出**什么给隐藏状态 |

门是 sigmoid(0~1)乘以候选值——**梯度可以通过细胞状态的"加法"路径顺畅流动**,缓解梯度消失,让网络能记住长距离依赖。

### GRU:简化版 LSTM

GRU(Gated Recurrent Unit)把遗忘门和输入门合并为**更新门**,参数更少、训练更快,效果与 LSTM 接近——小数据/快速原型常用。

### 变体与双向

- **双向 RNN(BiRNN)**:正反两个方向各跑一遍,拼接——能利用"后文"信息(如 NER 判断"银行"是机构还是河岸);
- **编码器-解码器(Seq2Seq)**:编码器把整个输入压成上下文向量,解码器逐步生成输出——机器翻译的经典框架(注意力机制最初就是为改进它而提出)。

## 代码 / 实现:PyTorch 最小 RNN

```python
import torch
import torch.nn as nn

# LSTM 情感分类(输入:词序列 -> 输出:正/负)
class LSTMSentiment(nn.Module):
    def __init__(self, vocab_size, embed_dim=100, hidden_dim=128, num_classes=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.classifier = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):               # x: (batch, seq_len) 词索引
        emb = self.embedding(x)         # (batch, seq_len, embed_dim)
        out, (h_n, c_n) = self.lstm(emb)
        # 取最后一个时间步的隐藏状态做分类
        return self.classifier(h_n[-1]) # (batch, num_classes)

# 使用:batch=8, 序列长=20
model = LSTMSentiment(vocab_size=10000)
logits = model(torch.randint(0, 10000, (8, 20)))
print(logits.shape)  # (8, 2)
```

**工程要点**:

- 输入先做**词嵌入(embedding)**;序列要**填充/截断**到等长,用 mask 忽略 padding;
- 训练用交叉熵 + Adam;长序列注意梯度裁剪(`clip_grad_norm_`);
- 小数据时 LSTM 常被 Transformer 超越,但 LSTM 参数量小、在**短序列/时间序列预测**仍很实用。

## 实践 / 应用:何时用 RNN

**适合**:

- 时间序列预测(股价、销量、传感器数据)——这是 LSTM/GRU 至今活跃的领域;
- 文本序列建模(情感分析、NER、文本生成)在**数据量不大**时;
- 语音/音频时序处理。

**已被 Transformer 取代的场景**:大数据量的文本任务(机器翻译、大模型)——[Transformer](../02-llm/transformer-architecture.md) 通过自注意力**并行处理整个序列**,捕获长程依赖更强,是 LLM 的核心。

**工程对比**:

| | RNN/LSTM | Transformer |
| --- | --- | --- |
| 处理方式 | 逐步串行 | 全序列并行 |
| 长程依赖 | 门控缓解但仍有限 | 自注意力直接建模 |
| 计算效率 | 串行慢 | 并行快(但 O(n²) 注意力) |
| 适合 | 短序列、时序预测、小数据 | 长文本、大数据、LLM |

## 总结

- **本质**:逐步处理序列 + 隐藏状态传递记忆 + 参数共享,能处理任意长度序列;
- **短板**:梯度消失 → 难以学习长程依赖;
- **解法**:LSTM(细胞状态 + 三门)/ GRU(两门)缓解记忆问题;
- **变体**:双向 RNN(利用后文)、Seq2Seq(编码器-解码器,翻译框架);
- **现状**:大数据文本任务被 Transformer 取代,时序预测与短序列仍是 LSTM/GRU 主场;
- **下一步**:理解注意力如何取代循环 → [Transformer 架构](../02-llm/transformer-architecture.md)(LLM 核心)。

## 延伸阅读

- CS224n 讲义:https://web.stanford.edu/class/cs224n/;PyTorch 序列教程:https://pytorch.org/tutorials
- 站内:[神经网络基础](dl-neural-network-basics.md)、[反向传播与梯度下降](dl-backpropagation.md)(理解梯度消失)、[卷积神经网络](dl-cnn.md)、[Transformer 架构](../02-llm/transformer-architecture.md)(注意力取代循环)
