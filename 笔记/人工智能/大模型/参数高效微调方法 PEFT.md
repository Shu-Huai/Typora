# 参数高效微调方法 PEFT

## 基本概念

**PEFT（Parameter-Efficient Fine-Tuning）** 是一种微调预训练大模型（如 GPT、BERT、T5 等）的策略，旨在在保持模型主干参数 **冻结** 的同时，通过引入 **少量可训练参数**，实现对新任务的适应。

<img src="Z:\Public\images\thumbnail.png" alt="🤗 PEFT：在低资源硬件上对十亿规模模型进行参数高效微调" style="zoom:50%;" />

它是对传统“全参数微调”（Full Fine-Tuning）的一种更高效替代方式，尤其适用于以下场景：

- 资源受限（计算/内存）设备
- 多任务学习
- 快速原型开发
- 大语言模型（LLM）微调

### 为什么？

- **降低计算成本和显存占用**
- **缩短训练时间**
- **提升迁移学习效率**
- **允许模型共享**：一个主模型可以共享给多个任务，每个任务只加载自己的小参数模块

### 分类

以下是目前主流的 PEFT 方法，它们可分为**输入级**和**模型内部级**两大类：

#### 输入级方法（Input-level）

**Prompt Tuning**

- 训练“软提示”向量（prompt embeddings），附加在输入序列前。
- 不修改模型结构。
- 适合简单或任务单一的场景。

**Prefix Tuning**

- 学习“前缀向量”，注入到每一层 Transformer 的 attention 结构中，作为额外 key/value。
- 更深地影响模型行为。

#### 模型内部参数注入方法（Adapter-based）

**Adapters**

- 在模型每一层插入小型瓶颈结构（如 MLP），仅训练 adapter 部分。
- 主体模型参数保持冻结。
- 模块化强，适合多任务共享。

**LoRA（Low-Rank Adaptation）**

- 对 attention 权重矩阵的更新采用低秩分解（A ≈ AB），只训练这两个小矩阵。
- 高效、轻量，非常流行。
- 可以与其他方法组合使用，如 QLoRA（量化+LoRA）。

#### 混合和衍生方法

| 方法            | 特点                                                         |
| --------------- | ------------------------------------------------------------ |
| **P-Tuning v2** | 类似 Prompt Tuning，但支持更深层的提示插入（所有 Transformer 层） |
| **IA³**         | 在 attention 和 FFN 模块插入三个可学习的缩放因子             |
| **BitFit**      | 只微调 bias 项（其余参数冻结）                               |
| **Compacter**   | 使用哈希和共享结构压缩 Adapter 模块参数                      |

## Prompt Tuning

### 什么是 Prompt Tuning？

**Prompt Tuning** 是一种**参数高效微调（PEFT）方法**，通过在输入文本前添加**可学习的“提示向量”（prompt embeddings）**，引导预训练语言模型完成特定任务，而**不需要调整模型本体参数**。

这是一种“软提示”（Soft Prompt）方法，与传统的自然语言 prompt（例如“请写一封道歉信”）不同，它学习的是连续的、可训练的向量，而不是文字。

### 原理概述

给输入序列的最前面拼一段长度为 $m$ 的“虚拟 token”，每个虚拟 token 对应一个**可训练向量**；训练时只更新这些向量，模型主体完全冻结。

- 基座模型：假设是 decoder-only LLM，词嵌入矩阵 $E\in\mathbb{R}^{V\times d}$，隐藏维度 $d$。
- 软提示：参数 $\mathbf{P}\in\mathbb{R}^{m\times d}$（$m$= 虚拟 token 个数），这是唯一需要学习的参数。
- 前向：
    1. 把输入 token 的 $\mathbf{X}\in\mathbb{R}^{n\times d}$ 取出。
    2. 在时间维上做拼接：$[\mathbf{P}; \mathbf{X}] \in \mathbb{R}^{(m+n)\times d}$
    3. 把拼接后的序列送入**冻结**的 Transformer 堆叠，按常规自回归/seq2seq 目标做训练。
- 损失：和全量微调一致（交叉熵）；但**只有** $\mathbf{P}$ 反向更新。
- 推理：同样把 $\mathbf{P}$ 作为前缀放入上下文，一次加载即可；KV cache 会先为这 $m$ 个位置建缓存，后续解码更快。

> 对 encoder–decoder：
>
> - 可把软提示接到 **encoder 输入**、**decoder 输入**，或两端都加（两端加=参数稍多、表达力更强）。

### 和“硬提示/手写 prompt”的区别

- **硬提示（手写）**：离散的自然语言 token，靠人工调词句；不可训练、可读。
- **软提示（Prompt Tuning）**：连续向量，**可训练、不可读**；能表达到词表外的“中间语义”，对**超大模型**尤为有效。