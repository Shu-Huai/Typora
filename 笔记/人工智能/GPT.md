# GPT

## GPT 是什么？

**GPT（Generative Pre-trained Transformer）** 是一个基于 Transformer **Decoder** 的自回归语言模型。

- 使用 **Transformer Decoder 堆叠结构**
- 训练目标：**左到右预测下一个 token**
- 核心思想：**预训练一个生成器模型，再在下游任务中直接用或微调**

> 自回归（autoregressive）：模型每次生成一个 token，基于之前生成的所有 token。

------

## 📦 GPT 架构结构概览

- 完全由多层 **Transformer Decoder Layer** 组成（没有 Encoder）
- 每层 Decoder 包含：
    1. **Masked Multi-head Self-Attention**（只看左边）
    2. **Feed Forward Network**
    3. **残差连接 + LayerNorm**

### 🔐 注意：GPT **没有 cross-attention**，因为没有 Encoder，它是纯生成。

------

## 🔄 输入格式

```
plaintext


复制编辑
token1 token2 token3 ...
```

每个 token 只能看到它前面的 token：

```
plaintext


复制编辑
预测 token3 时，只能用 token1 和 token2
```

这通过 **masking**（上三角掩码）实现。

------

## 🧪 GPT 的训练目标

### 自回归语言建模：

模型学的是条件概率链：

P(x1,x2,...,xn)=∏t=1nP(xt∣x<t)P(x_1, x_2, ..., x_n) = \prod_{t=1}^{n} P(x_t \mid x_{<t})P(x1,x2,...,xn)=t=1∏nP(xt∣x<t)

训练时，每个位置预测它后面的词：

```
plaintext复制编辑输入：      I   love    deep    [MASK]
预测目标：      love    deep    learning
```

注意：

- 不像 BERT 的 MLM 是双向的、填空式的
- GPT 的训练是生成式的、单向的

------

## 🔧 嵌入方式

GPT 的输入嵌入由两部分组成：

```
plaintext


复制编辑
InputEmbedding = TokenEmbedding + PositionEmbedding
```

- TokenEmbedding：词向量
- PositionEmbedding：**可学习**的位置编码（不是正弦）

------

## 🤖 GPT 的使用方式：直接生成

- 预训练后可以直接用于生成任务（如文本续写、对话、代码补全等）
- 不需要下游任务特定结构，只需设计好 prompt（这就是 prompt engineering）

------

## 📈 GPT 模型规模演进（以 OpenAI 系列为例）

| 模型          | 层数 | 维度  | 头数 | 参数量 |
| ------------- | ---- | ----- | ---- | ------ |
| GPT-1         | 12   | 768   | 12   | 117M   |
| GPT-2         | 48   | 1600  | 25   | 1.5B   |
| GPT-3         | 96   | 12288 | 96   | 175B   |
| GPT-4（估计） | —    | —     | —    | >500B  |



------

## 🔁 GPT 与 BERT 的关键对比

| 对比项   | BERT                   | GPT                           |
| -------- | ---------------------- | ----------------------------- |
| 架构     | Transformer Encoder    | Transformer Decoder           |
| 方向性   | 双向                   | 单向                          |
| 训练目标 | MLM + NSP              | 自回归预测                    |
| 应用领域 | 理解任务（分类、问答） | 生成任务（对话、续写、代码）  |
| 输入掩码 | 任意 token 可见        | 使用 causal mask 限制未来信息 |
| 输出结构 | 每个 token 输出        | 一个 token 一个 token 生成    |



------

## 🔥 GPT 的关键进化点（特别是 GPT-2 之后）

- 使用 **Byte Pair Encoding（BPE）** 分词器
- **更深更宽的模型**，提升泛化能力
- 去掉 NSP（不像 BERT 需要句子对）
- 用 **Transformer Decoder** 处理长上下文（up to 2048, 4096, 32k tokens）

------

## 总结

GPT 是一个非常纯粹的 Transformer Decoder 堆叠结构：

- 利用 Masked Attention 实现自回归生成
- 不需要 cross-attention，不看输入句子，是完全“自己写自己”
- 预训练后直接生成，或者用 prompt 引导做任务（例如 InstructGPT）