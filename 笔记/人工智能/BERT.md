# BERT

## BERT 是什么？

**BERT（Bidirectional Encoder Representations from Transformers）** 是一种基于 Transformer **Encoder** 的预训练语言模型，特点是：

- **只用 Transformer Encoder**（没有 Decoder）
- **双向上下文理解**（不同于 GPT 的单向）
- **预训练 + 微调（fine-tune）范式**

BERT 改变了 NLP 任务的做法：从“每个任务单独训练模型” → “一个模型预训练 + 所有任务共享”。

BERT 实际上是一个特征提取器。

![LeeMeng - 進擊的BERT：NLP 界的巨人之力與遷移學習](Z:\Public\images\bert-intro.jpg)

## BERT 结构概览

- 完全由多个 Transformer Encoder 层堆叠而成
- 输入长度：最多 512 tokens
- 每个 token 对应一个向量，最终拿 `[CLS]` 向量做分类等任务

### 输入格式（token sequence）：

```
[CLS] token1 token2 ... tokenN [SEP]
```

- `[CLS]`：专门用于分类任务
- `[SEP]`：句子分隔符（如句子对任务）

## 输入嵌入（Embedding）

BERT 的输入 embedding 是三部分之和：

```python
InputEmbedding = TokenEmbedding + SegmentEmbedding + PositionEmbedding
```

- **TokenEmbedding**：词向量（wordpiece 分词）
- **SegmentEmbedding**：标记属于句子 A or B（句子对任务时）
- **PositionEmbedding**：**可学习**的位置编码（不同于 Transformer 原始正弦）

## BERT 的两个预训练任务

### Masked Language Modeling（MLM）

随机遮住输入中的部分 token（15%），训练模型预测原始词。

例子：

```
Input:    the cat [MASK] on the mat
Target:                       sat
```

特点：

- 模型需要利用左、右文同时预测 → 实现**双向上下文建模**

### Next Sentence Prediction（NSP）

任务：判断句子 B 是否是句子 A 的下一句

训练时：

- 50% 是真实的下一句（IsNext）
- 50% 是随机一句（NotNext）

目的：帮助 BERT 理解句间关系（如问答、自然推理任务）

## 下游任务怎么用 BERT？

BERT 的输出是每个 token 的向量，可以做很多事：

| NLP 任务     | 方法                            |
| ------------ | ------------------------------- |
| 文本分类     | 使用 `[CLS]` 向量接全连接层     |
| 命名实体识别 | 每个 token 向量接分类层         |
| 句子对判断   | 输入 `[CLS] 句子A [SEP] 句子B`  |
| 问答         | 找出起始/结束位置（用 softmax） |
| 文本生成     | ❌（不能，BERT 是非自回归的）    |

## 模型参数（以 BERT-base 为例）：

| 结构        | 数值  |
| ----------- | ----- |
| Layers      | 12    |
| Hidden size | 768   |
| Heads       | 12    |
| 参数量      | ~110M |