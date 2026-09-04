# 卷积神经网络 CNN:让机器"看见"图像

> **一句话摘要**:CNN(Convolutional Neural Network)是图像领域的基石——用**卷积核**在局部窗口上滑动提取特征,天然契合图像的局部性(相邻像素相关)与平移不变性(猫在图里哪个位置都是猫)。核心机制:卷积层(提特征)+ 池化层(降维)+ 全连接层(分类),现代视觉模型(ResNet、ViT 等)都建立在这套基础上。
>
> **来源**:综合公开资料(CS231n 讲义 https://cs231n.github.io/convolutional-networks/、PyTorch 官方教程),由 AI 助手按站内模板整理

## 概念

**CNN** 是一类专门处理**网格结构数据**(图像是像素网格,也可用于序列/图)的神经网络。与 [MLP](dl-neural-network-basics.md) 的核心区别:**用卷积操作替代全连接**,大幅减少参数、并利用图像的局部结构。

**为什么 MLP 不适合图像**:

- 一张 256×256 的彩色图展平后有 19 万维输入,全连接层参数爆炸;
- 全连接丢失空间结构:像素左右挪一位,输入向量完全不同,但图像语义没变;
- MLP 对"特征出现在哪里"敏感,而 CNN 通过卷积核共享实现**平移不变性**。

## 原理:三大核心层

### 1. 卷积层(Convolution)——特征提取

**卷积核(kernel/filter)** 是一个小窗口(如 3×3×3),在输入上滑动,每个位置做**点积**得到一张**特征图(feature map)**。一个核检测一种模式(边缘、纹理、颜色块),堆叠多个核检测多种模式;深层网络把低层模式组合成高层语义(眼睛→脸→人)。

**关键超参数**:

| 参数 | 含义 | 例子 |
| --- | --- | --- |
| kernel size | 感受野大小 | 3×3、5×5 |
| stride(步幅) | 每次滑动距离 | 1、2 |
| padding(填充) | 边缘补零,保持尺寸 | same/valid |
| 核数量 | 输出通道数 | 32、64、128 |

**权值共享**:同一个核在整个输入上共享权重 → 参数远少于全连接,同时让检测到的模式与位置无关。

### 2. 池化层(Pooling)——降维

在每个小窗口内取最大值(最大池化)或均值(平均池化),**下采样**特征图。作用:

- 减小尺寸与计算量;
- 增加平移鲁棒性(微小位移不影响最大值);
- 逐步扩大感受野。

### 3. 全连接层(FC)——决策

网络末端把特征图展平,接若干全连接层,最后用 softmax 输出类别概率。**卷积+池化 = 自动特征提取器,全连接 = 分类器**。

### 经典架构演进

| 架构 | 年份 | 关键贡献 |
| --- | --- | --- |
| LeNet-5 | 1998 | 首个成功的 CNN(手写数字) |
| **AlexNet** | 2012 | 深度 CNN 复兴(ImageNet 夺冠) |
| VGG | 2014 | 小卷积核(3×3)堆叠,简单统一 |
| **ResNet** | 2015 | **残差连接**解决深层退化,可训练上百层 |
| EfficientNet/ViT | 2019+ | 复合缩放 / 注意力替代卷积 |

## 代码 / 实现:PyTorch 最小 CNN

```python
import torch
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        # 卷积块:conv -> relu -> pool
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),  # 1 通道 -> 32 特征图
            nn.ReLU(),
            nn.MaxPool2d(2),                             # 尺寸减半
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        # 分类头
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),   # 输入 28x28 -> 池化两次 -> 7x7
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))

# 使用:输入 (batch, 1, 28, 28)
model = SimpleCNN()
out = model(torch.randn(8, 1, 28, 28))   # -> (8, 10)
print(out.shape)
```

**训练要点**:用交叉熵损失 + Adam 优化器;小数据集加数据增强(随机翻转/裁剪/颜色扰动)防过拟合;预训练模型(ImageNet 权重)微调比从头训练快得多。

## 实践 / 应用:何时用 CNN

**适合**:

- 图像分类/检测/分割;
- 视频、医学影像、卫星图等网格数据;
- 语音(把频谱当图像)与某些序列任务(1D 卷积)。

**工程要点**:

1. **数据增强**是 CNN 防过拟合的第一利器(翻转/旋转/裁剪/色彩抖动);
2. **迁移学习**:用 ImageNet 预训练模型(ResNet/EfficientNet)微调,小数据集也能有不错效果;
3. **BatchNorm** 放卷积后能加速收敛、稳定训练;
4. 监控训练曲线:训练 loss 降但验证不降 → 过拟合(加增强/正则/减容量)。

**当前趋势**:ViT(Vision Transformer)用注意力替代卷积,在大数据上超越 CNN;但 CNN 仍以高效、易训练、数据需求少著称——**小/中数据集 CNN 往往更实用**。

## 总结

- **为什么 CNN**:卷积核局部滑动 + 权值共享 → 参数少、平移不变、契合图像局部性;
- **三大层**:卷积(提特征)→ 池化(降维)→ 全连接(分类);
- **演进**:AlexNet → VGG → ResNet(残差)是理解现代 CNN 的骨架;
- **实践**:数据增强 + 迁移学习 + BatchNorm 三大件;
- **下一步**:理解 CNN 后进入 [RNN](dl-rnn.md)(序列数据)或 [Transformer](../02-llm/transformer-architecture.md)(注意力,现代 LLM 核心)。

## 延伸阅读

- CS231n 讲义:https://cs231n.github.io/convolutional-networks/;PyTorch 教程:https://pytorch.org/tutorials
- 站内:[神经网络基础](dl-neural-network-basics.md)(MLP 前置)、[反向传播与梯度下降](dl-backpropagation.md)、[深度学习训练技巧](dl-training-techniques.md)、[循环神经网络](dl-rnn.md)、[Transformer 架构](../02-llm/transformer-architecture.md)
