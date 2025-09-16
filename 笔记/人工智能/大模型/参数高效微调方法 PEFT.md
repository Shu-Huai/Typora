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