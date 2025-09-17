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

以下是目前主流的 PEFT 方法，它们可分为**输入级**和**模型内部级**两大类

![img](Z:\Public\images\94ac5a9fd8a311dab18156f0bb1c83b7.png)

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

<img src="Z:\Public\images\image-20250917164052376.png" alt="image-20250917164052376" style="zoom:50%;" />

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

### 训练流程

1. **冻结**基座权重（Transformer、词嵌入、LayerNorm 等统统不动）。
2. 新建软提示参数 $\mathbf{P}\in\mathbb{R}^{m\times d}$。
    - 初始化常见做法：
        - **从词表中抽样若干真实 token 的 embedding**做初始化（更稳），或
        - 正态/均匀随机（更灵活，但需稍高学习率与 warmup）。
3. **数据打包**：把任务指令/上下文与目标拼成常规监督样本；仅区别在输入前多了 $\mathbf{P}$。
4. **优化器**：只挂 $\mathbf{P}$；学习率通常**高于**全量微调（软提示参数量小，需学得快）；权重衰减多为 0。
5. **长度 m 的选择**：20–200 常见；越长表达力越强但占用上下文长度。
6. **早停**：看验证集困惑度/准确率；小数据很容易收敛。
7. **保存**：只存 $\mathbf{P}$（几十 KB～几 MB），部署时与基座组合即可。

> 组合技：很多实践会把 **Prompt Tuning + LoRA** 一起用——在极少参数的前提下兼顾稳定性与上限。

### 伪代码

```python
# 假设已有 frozen_model, tokenizer
d = frozen_model.config.hidden_size
m = 64  # 虚拟 token 个数
P = torch.nn.Parameter(torch.randn(m, d))  # 软提示参数
optimizer = torch.optim.AdamW([P], lr=lr, weight_decay=0.0)

for batch in dataloader:
    input_ids = batch["input_ids"]                 # [B, n]
    inputs_embeds = frozen_model.embed(input_ids)  # [B, n, d]
    P_expand = P.unsqueeze(0).expand(input_ids.size(0), -1, -1)  # [B, m, d]
    inputs = torch.cat([P_expand, inputs_embeds], dim=1)          # [B, m+n, d]

    out = frozen_model(inputs_embeds=inputs, labels=batch["labels_with_shift"])
    loss = out.loss
    loss.backward()
    optimizer.step(); optimizer.zero_grad()
```

## Prefix Tuning

**冻结**大模型，仅训练一小段、作用在每一层注意力里的“虚拟前缀”（continuous prefix），让模型像带着“隐形上下文”一样完成目标任务。

### 核心思想

在**每一层**自注意力（以及 encoder–decoder 的跨注意力）里，为 **K/V** 拼接一段可训练的前缀向量；等价于给每层的注意力缓存加“任务专属的先验记忆”。

![Towards Adaptive Prefix Tuning for Parameter-Efficient Language Model Fine- tuning](Z:\Public\images\imageurl=https%3A%2F%2Ffigures.semanticscholar.org%2F5193003d574eff310742e6ce94612fc82851fee0%2F1-Figure1-1.png)

### 机制与形状

设模型隐层维度 $d$，多头注意力 $h$ 个头，单头维度 $d_h=\frac{d}{h}$，前缀长度 $m$。

- 训练参数通常采用**再参数化**：

    1. 学一段共享前缀基 $\mathbf{P}\in\mathbb{R}^{m\times d}$（或多层各自一段）。
    2. 过一个小 MLP/线性投影，为**每一层**生成该层的 $\mathbf{K}^{(l)}_{\text{pref}}\in\mathbb{R}^{m\times h\times d_h}$ 和 $\mathbf{V}^{(l)}_{\text{pref}}\in\mathbb{R}^{m\times h\times d_h}$。

- 前向时，第 lll 层的注意力计算把这段前缀**拼到真实序列的 K/V 前面**：

    $K^{(l)}=[K^{(l)}_{\text{pref}}; K^{(l)}_{\text{text}}],\quad V^{(l)}=[V^{(l)}_{\text{pref}}; V^{(l)}_{\text{text}}]$

    Query 仍来自真实 token 的表示；注意力会先“看见”这段任务特定的前缀记忆。

- **训练目标**：和常规模型一样（交叉熵/下一个词预测）；但**只更新前缀相关参数**。

> Encoder–Decoder 模型里，常对三处加前缀：**encoder 自注意力、decoder 自注意力、decoder 的跨注意力（对 encoder 输出）**。

### 计算与开销

- **参数量**：与 $m$、层数、头数线性相关，但远小于全参微调（通常 KB～数十 MB）。
- **推理开销**：自回归解码时，新增的 $m$ 个 K/V 也会进入 KV cache；每步解码多 attend 到 $m$ 个位置，开销增量固定、可控。
- **上下文长度**：不占用明面上的 token 长度（不像 Prompt 会吃输入窗口），但注意力的“有效长度”增至 $n+m$。

### 伪代码

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import PrefixTuningConfig, get_peft_model, TaskType
import datasets

model_name = "meta-llama/Llama-3.1-8B"  # 示例
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 配置 Prefix Tuning（m = num_virtual_tokens）
peft_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=40,     # 前缀长度 m
    # encoder_hidden_size 可用于 seq2seq 映射，这里 decoder-only 不需要
)

model = get_peft_model(model, peft_config)  # 注入到各层 past_key_values
model.print_trainable_parameters()          # 只训练前缀相关参数

# 准备数据（示例）
def format_example(ex):
    prompt = ex["instruction"] + "\n" + ex["input"]
    text = prompt + "\n" + ex["output"]
    ids = tokenizer(text, truncation=True, max_length=2048)
    ids["labels"] = ids["input_ids"].copy()
    return ids

dataset = datasets.load_dataset("tatsu-lab/alpaca", split="train[:1000]").map(format_example)

args = TrainingArguments(
    output_dir="./pt_prefix",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-3,        # 相对偏大
    num_train_epochs=2,
    logging_steps=20,
    fp16=True
)

trainer = Trainer(model=model, args=args, train_dataset=dataset)
trainer.train()
```

## LoRA

