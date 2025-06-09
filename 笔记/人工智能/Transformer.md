# Transformer

## Transformer 架构详解

Transformer 由两个主要部分组成：Encoder 和 Decoder。在 ViT 和 BERT 等模型中，常用的是 Encoder 或其变种。

![transformer](Z:\Public\images\transformer-1749452689127-14.svg)

![img](Z:\Public\images\v2-4544255f3f24b7af1e520684ae38403f_1440w.jpg)

### Transformer Encoder 架构组成

一个标准的 Transformer Encoder Layer 包括：

1. **多头自注意力（Multi-head Self-Attention）**
2. **前馈网络（Feed Forward Neural Network, FFN）**
3. **残差连接（Residual Connection）+ Layer Normalization**

#### 多头自注意力

在 Transformer Encoder 中，输入的每一个 token 都和其他所有 token 做 attention。

形状总结：

- 输入：$X \in \mathbb{R}^{N \times d_{\text{model}}}$（$N$ 是 token 数，$d_\text{model}$ 是嵌入维度）
- $Q$/$K$/$V$：每个通过线性映射变成 $d_k$ 维，每个 head 独立计算
- 输出：多个 head 拼接后再过线性层回到 $d_\text{model}$ 维

#### 残差连接与 LayerNorm

每一层都采用：

```python
Output = LayerNorm(X + SubLayer(X))
```

这种结构可以让模型训练更稳定、收敛更快。

#### 前馈网络（FFN）

每个 token 单独过一个两层的 MLP（共享参数）：

```python
FFN(x) = max(0, xW1 + b1)W2 + b2
```

隐藏层一般是 `d_ff = 4 × d_model`

#### Positional Encoding（位置编码）

因为 Transformer 完全基于 attention，没有循环或卷积，所以需要加入位置信息。

经典方式是 **正弦位置编码**：

对于位置 $pos$ 和维度 $i$：

- $PE(pos, 2i) = \sin(\frac{pos}{10000^{\frac{2i}{d_{model}}}})$
- $PE(pos, 2i+1) = \cos(\frac{pos}{10000^{\frac{2i}{d_{model}}}})$

#### 整体结构流程（Encoder）

1. Token Embedding + Positional Encoding
2. 多层 Encoder Layer，每层包括：
    - Multi-head self-attention
    - Add & Norm
    - Feed Forward
    - Add & Norm

最终输出可以用于分类（取 `[CLS]` token）或其他下游任务。

### Transformer Decoder 架构详解

Decoder 主要用于生成式任务（如翻译、语言建模、图像生成等）。它的结构相较于 Encoder 多了一个关键部分：**Encoder-Decoder Attention（交叉注意力）**。

每个 Decoder Layer 包含 3 个子层：

1. **Masked Multi-Head Self-Attention（掩码自注意力）**
2. **Encoder-Decoder Cross-Attention（交叉注意力）**
3. **前馈网络（Feed Forward）**

每个子层后都有：

- 残差连接 + LayerNorm

#### Masked Multi-Head Self-Attention

这一层与 Encoder 的自注意力结构几乎一样，**唯一的不同是加入了掩码（mask）**，防止模型看到未来的信息（causal masking）。

掩码是一个上三角矩阵，确保每个位置只能 attend 到它自己及其前面的位置。

用于 **自回归生成**，即生成第 $t$ 个 token 时不能访问第 $t+1$ 及之后的 token。

#### Encoder-Decoder Attention（交叉注意力）

这是 Decoder 特有的结构。

它的作用是：**让 Decoder 的每个位置都可以 attend 到 Encoder 的输出序列**，从而实现“看输入，生成输出”的功能。

形式：

- Query 来自前一层 decoder 的输出
- Key / Value 来自 encoder 的输出

即：

```python
Q = decoder_hidden_state
K, V = encoder_output
```

这个 cross-attention 保留了输入信息，指导 decoder 正确生成。

#### Feed Forward Layer（FFN）

和 Encoder 中一致，逐 token 的两层 MLP。

#### Decoder 整体结构

每个 decoder layer：

```
x -> masked self-attention
  -> add & norm
  -> encoder-decoder attention
  -> add & norm
  -> feed forward
  -> add & norm
```

#### 初始输入与输出

- **输入**：Embedding + Positional Encoding（通常用的是目标序列的 token，训练时为“teacher forcing”）
- **输出**：Decoder 最终的输出再过一个线性层 + softmax，预测下一个 token 的概率

## Transformer 的局限与扩展

这些是后面 ViT / Diffusion / 大模型等用到的基础改进动机

- **计算复杂度：$O(n^2)$**，难以处理长序列
    - **改进方向：**
        - Sparse Attention（如 BigBird）
        - Linear Attention（如 Performer）
        - Memory-based（如 Transformer-XL）
        - Chunking（如 Longformer）
- **多头注意力冗余**：并非所有 head 都有独立功能 → 有些工作试图压缩 head 数量