# 参数高效微调方法 PEFT

## 基本概念

**PEFT（Parameter-Efficient Fine-Tuning）** 是一种微调预训练大模型（如 GPT、BERT、T5 等）的策略，旨在在保持模型主干参数 **冻结** 的同时，通过引入 **少量可训练参数**，实现对新任务的适应。

<img src="http://public.file.lvshuhuai.cn/images\thumbnail.png" alt="🤗 PEFT：在低资源硬件上对十亿规模模型进行参数高效微调" style="zoom:50%;" />

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

![img](http://public.file.lvshuhuai.cn/images\94ac5a9fd8a311dab18156f0bb1c83b7.png)

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

论文：[The Power of Scale for Parameter-Efficient Prompt Tuning](https://aclanthology.org/2021.emnlp-main.243.pdf)

**Prompt Tuning** 是一种**参数高效微调（PEFT）方法**，通过在输入文本前添加**可学习的“提示向量”（prompt embeddings）**，引导预训练语言模型完成特定任务，而**不需要调整模型本体参数**。

这是一种“软提示”（Soft Prompt）方法，与传统的自然语言 prompt（例如“请写一封道歉信”）不同，它学习的是连续的、可训练的向量，而不是文字。

<img src="http://public.file.lvshuhuai.cn/images\image-20250917164052376.png" alt="image-20250917164052376" style="zoom:50%;" />

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

论文：[Prefix-Tuning: Optimizing Continuous Prompts for Generation](https://aclanthology.org/2021.acl-long.353.pdf)

**冻结**大模型，仅训练一小段、作用在每一层注意力里的“虚拟前缀”（continuous prefix），让模型像带着“隐形上下文”一样完成目标任务。

### 核心思想

在**每一层**自注意力（以及 encoder–decoder 的跨注意力）里，为 **K/V** 拼接一段可训练的前缀向量；等价于给每层的注意力缓存加“任务专属的先验记忆”。

![Towards Adaptive Prefix Tuning for Parameter-Efficient Language Model Fine- tuning](http://public.file.lvshuhuai.cn/images\aaaa.png)

### 机制与形状

设模型隐层维度 $d$，多头注意力 $h$ 个头，单头维度 $d_h=\frac{d}{h}$，前缀长度 $m$。

- 训练参数通常采用**再参数化**：

    1. 学一段共享前缀基 $\mathbf{P}\in\mathbb{R}^{m\times d}$（或多层各自一段）。
    2. 过一个小 MLP/线性投影，为**每一层**生成该层的 $\mathbf K^{(l)}_{\text{pref}}\in\mathbb{R}^{m\times h\times d_h}$ 和 $\mathbf V^{(l)}_{\text{pref}}\in\mathbb{R}^{m\times h\times d_h}$。

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

论文：[LoRA: Low-Rank Adaptation of Large Language Models | OpenReview](https://openreview.net/forum?id=nZeVKeeFYf9)

在**不改动原始大模型权重**的前提下，只为若干线性层（常见是注意力里的 $W_Q, W_K, W_V, W_O$）添加一个**低秩可训练增量**，从而以很少参数完成适配。

### 核心思想

- 令原权重 $W\in\mathbb{R}^{d_{\text{out}}\times d_{\text{in}}}$ 冻结，**只训练**一个低秩增量 $\Delta W$。
- 用低秩分解表示：$\Delta W = B A$，其中 $A\in\mathbb{R}^{r\times d_{\text{in}}}$、$B\in\mathbb{R}^{d_{\text{out}}\times r}$，秩 $r \ll \min(d_{\text{in}}, d_{\text{out}})$。
- 前向变为：$y = (W + \alpha/r \cdot BA)x$。这里 $\alpha$ 是缩放系数（稳定训练）。

> 只新增参数量 $\sim r(d_{\text{in}}+d_{\text{out}})$，远小于全参微调。

<img src="http://public.file.lvshuhuai.cn/images\b61abc72654e13f6548940ad4435db29.png" alt="img" style="zoom:50%;" />

#### 例子

**设定**

- 输入维度（in）：1024
- 输出维度（out）：1024
- 原始权重 $W$：$1024\times1024$
- LoRA 秩 $r$：**4**

**LoRA 参数形状**

- $A \in \mathbb{R}^{r \times d_{in}} = \mathbb{R}^{4 \times 1024}$
- $B \in \mathbb{R}^{d_{out} \times r} = \mathbb{R}^{1024 \times 4}$
- 增量矩阵 $\Delta W = BA \in \mathbb{R}^{1024 \times 1024}$（低秩，$\mathrm{rank}\le 4$）

**参数量对比**

| 项目         | 形状               | 参数个数  |
| ------------ | ------------------ | --------- |
| 全量增量 DDD | $1024 \times 1024$ | 1,048,576 |
| LoRA $A$     | $4 \times 1024$    | 4,096     |
| LoRA $B$     | $1024 \times 4$    | 4,096     |
| LoRA 合计    | —                  | 8,192     |

### 放在哪些层？（LLM 实践）

- **最常见**：注意力的 $W_Q$ 与 $W_V$（对生成最敏感）；有时也加到 $W_O$ 与 $W_K$。
- 有些模型把 LoRA 也加到 **FFN（MLP）** 的上投/下投层（如 `gate_proj`、`up_proj`、`down_proj`）。
- 选择越多，参数越大、效果通常更强；常见搭配：`q_proj + v_proj` 或 `q_proj + k_proj + v_proj + o_proj`。

### 为什么稳定好用？

- **表达力强**：直接改动线性映射的子空间，能学到任务所需的“方向”。
- **参数/显存省**：只训练 A/B 两个小矩阵；多任务时每个任务只需保存一份增量。
- **易部署**：推理时可选择**合并**（merge）进原权重变单次矩阵乘，或**不合并**（在线叠加），对吞吐影响小。
- **可组合**：与 Prompt/Prefix、Adapter 搭配常见；也能做多 Adapter 选择/融合。

#### 关键超参怎么选？

- **rank $r$**：常用 4/8/16/32；数据/任务复杂度越高可适当增大。
- **lora_alpha $\alpha$**：常 8/16/32/64；$\alpha/r$ 决定实际缩放，一般取 1～8 附近。
- **lora_dropout**：0～0.1 常见，样本少/过拟合时更有用。
- **学习率**：只训 LoRA 时可稍大（如 1e-3～5e-4 区间）；`weight_decay=0` 或很小。
- **目标模块**：先从 `q_proj,v_proj` 起步，指标不够再扩展到 `k_proj,o_proj` 或 MLP。

### 伪代码

```python
# -*- coding: utf-8 -*-
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 可删
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType

# ==== 常量 ====
BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"   # 或 Llama/Mistral 等
DATA_PATH  = "./DATA/train.jsonl"         # 你的 JSONL 数据
OUT_DIR    = "./OUTPUT/lora-qwen"
MAX_LEN    = 1024
EPOCHS     = 3
LR         = 5e-4
BATCH_SIZE = 1
GRAD_ACC   = 16

# ==== 加载基座 ====
tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token

model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

# ==== 注入 LoRA ====
peft_cfg = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                 # rank
    lora_alpha=32,        # 缩放
    lora_dropout=0.05,
    bias="none",
    target_modules=["q_proj","v_proj"]  # 需要时再加 "k_proj","o_proj" 或 MLP 层
)
model = get_peft_model(model, peft_cfg)
model.print_trainable_parameters()

# ==== 数据集（支持 chat 或 text 两种字段）====
def format_example(ex):
    if "messages" in ex:
        text = tok.apply_chat_template(ex["messages"], tokenize=False, add_generation_prompt=False)
    else:
        text = ex.get("text", "")
    enc = tok(text, truncation=True, max_length=MAX_LEN)
    enc["labels"] = enc["input_ids"].copy()
    return enc

ds = load_dataset("json", data_files=DATA_PATH, split="train").map(format_example, remove_columns=["messages","text"], fn_kwargs={})
collator = DataCollatorForLanguageModeling(tok, mlm=False)

# ==== 训练参数 ====
args = TrainingArguments(
    output_dir=OUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACC,
    learning_rate=LR,
    num_train_epochs=EPOCHS,
    logging_steps=20,
    save_strategy="epoch",
    fp16=True
)

# ==== 训练 ====
trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collator)
trainer.train()

# 常规保存 LoRA 适配器
model.save_pretrained(OUT_DIR + "/lora")
tok.save_pretrained(OUT_DIR + "/lora")
```

## QLoRA

论文：[QLoRA: Efficient Finetuning of Quantized LLMs | OpenReview](https://openreview.net/forum?id=OUIFPHEgJU&referrer=[the profile of Ari Holtzman](%2Fprofile%3Fid%3D~Ari_Holtzman1))

**把基座大模型用 4bit 量化后冻结，只训练少量 LoRA 适配器参数。**

这样能在很少显存下微调几十亿参数的模型，效果接近全参或普通 LoRA。

### 量化

把神经网络里用 **浮点数（FP32/FP16）** 表示的权重/激活，近似成**低比特整数**（如 INT8、INT4）来存储与计算，从而**省显存、降带宽、提吞吐**，以少量精度损失换取大幅效率提升。

#### 核心做法

把实数 $x$ 压缩成整数 $q$：
$$
q=\text{round}\Big(\frac{x}{s}\Big)+z,\quad x\approx s\,(q-z)
$$

- $s$：**scale**（缩放因子）
- $z$：**zero-point**（零点，偏移量）
-  推理时用 $s$ 和 $z$ 把整数还原到近似的实数域。

#### 常见类型

- **按位数**：INT8、INT4（QLoRA 常用 4bit 权重 + 高精度计算）
- **按范围**：对称/非对称（是否用零点 $z$）
- **按粒度**：per-tensor / **per-channel**（通道级更准）
- **按时机**：
    - **PTQ**（Post-Training）：训练后量化，最快；
    - **QAT**（Quantization-Aware Training）：训练时模拟量化，更准。
- **按对象**：只量化**权重**，或同时量化**激活**。

### 关键机制

#### 4bit 权重量化（常用 NF4 + double-quant）

- 将模型权重从 FP16/BF16 压到 4bit 存储（推理/训练时再以 FP16/BF16 参与计算）。
- **只量化“冻结的主干权重”**；参与训练的 LoRA 参数保持高精度（FP16/BF16/FP32）。

#### LoRA 适配

- 在线性层（最常见是 `q_proj`、`v_proj`）注入 $\Delta W = BA$ 的**低秩增量**，只训练 $A$、$B$。
- 前向：$y=(W_{\text{4bit}}+\alpha/r\cdot BA)x$
- 训练与优化器状态只覆盖 LoRA 参数，显存压力极小。

#### 冻结主干 + 只训少量参数

- 避免灾难性遗忘；每个任务只保存一小份 LoRA 权重（MB 级）。

### 伪代码

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
from datasets import load_dataset

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"  # 例：与你之前一致
MAX_LEN  = 1024

# 1) 4bit 量化加载（冻结主干）
bnb_cfg = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype="float16"  # or "bfloat16" 如果卡支持更好
)
tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
tok.pad_token = tok.eos_token  # 常见做法：对 Causal LM 复用 eos 作 pad

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_cfg,
    device_map="auto"
)

# 2) 做好 k-bit 训练准备（处理 LN/精度等）
model = prepare_model_for_kbit_training(model)

# 3) 注入 LoRA
peft_cfg = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    target_modules=["q_proj","v_proj"]  # 需要时再加 k/o/MLP
)
model = get_peft_model(model, peft_cfg)
model.print_trainable_parameters()  # 检查仅 LoRA 可训

# 4) 数据（示例：alpaca 格式）
def format_example(ex):
    # 简单拼接；你也可以用 tok.apply_chat_template
    prompt = (ex.get("instruction","") + "\n" + ex.get("input","")).strip()
    text = (prompt + ("\n" if prompt else "") + ex.get("output","")).strip()
    enc = tok(text, truncation=True, max_length=MAX_LEN)
    enc["labels"] = enc["input_ids"].copy()
    return enc

ds = load_dataset("tatsu-lab/alpaca", split="train[:2000]").map(format_example, remove_columns=["instruction","input","output"])
collator = DataCollatorForLanguageModeling(tok, mlm=False)

# 5) 训练参数
args = TrainingArguments(
    output_dir="./qlora_out",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,   # 小 batch + 大累积
    learning_rate=5e-4,
    num_train_epochs=2,
    logging_steps=20,
    fp16=True,                        # 或 bf16=True（若支持）
    save_strategy="epoch",
    optim="paged_adamw_8bit",         # 进一步省显存
    gradient_checkpointing=True
)

trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collator)
trainer.train()
```

## Adapter

论文：[Parameter-Efficient Transfer Learning for NLP](https://proceedings.mlr.press/v97/houlsby19a/houlsby19a.pdf)

### 核心概念

**Adapter Tuning**：在 Transformer 的每一层**插入一个很小的可训练模块**（Adapter），主干参数 **冻结不动**；训练时**只更新这些小模块**（通常还有少数 LayerNorm/bias）。

典型结构是“**瓶颈 MLP**”：先把隐藏维 $d$ 压到 $r$（$r \ll d$），非线性后再投回 $d$，并通过**残差**回到主干：
$$
\text{Adapter}(x)=x+W_\text{up}\,\sigma\left(W_\text{down}\,\text{LN}(x)\right)
$$

- $W_\text{down}\in\mathbb{R}^{r\times d}$，$W_\text{up}\in\mathbb{R}^{d\times r}$，$r$ 称为**reduction factor**（bottleneck）。
- 常把 $W_\text{up}$ 初始化为接近 0，使初期几乎不扰动原模型。

**要点**：

- 只增少量参数：$\mathcal{O}(2dr)$ 每层。
- 多任务时，每个任务一套 adapter 权重（MB 级），**热插拔**切换。

### 放在 Transformer 的哪个位置？

两种经典放置（都保留残差）：

- **Houlsby Adapter（最原始）**：
    - 每层两个 adapter：**注意力块后** + **FFN 块后**（都在残差里）。
    - 表达力强、参数略多。
- **Pfeiffer Adapter（更轻）**：
    - 每层只放一个：**FFN 块后**。
    - 更省参数、实现简单，常见默认。

也有 **Parallel Adapter**（与 FFN 并联）、**Compacter**（共享低秩核）、**AdapterDrop**（在高层省略以提速）等工程变体。

> 在 **encoder–decoder** 里，encoder/decoder/cross-attn 三处都能插；在 **decoder-only** 里，每个 block（自注意力 + MLP）后插一个/两个最常见。

<img src="http://public.file.lvshuhuai.cn/images\img1.jpg" alt="img" style="zoom:50%;" />

### 关键超参与训练细节

- **reduction factor $r$**：常用 8/16/32/64。$r$ 越大，参数越多、容量越强。
- **nonlinearity**：GELU/ReLU 常见。
- **init**：$W_\text{up}$ 近 0，$W_\text{down}$ 小随机；可加一个缩放系数 $\alpha$（类似 LoRA 里的 scaling）。
- **LR**：只训小模块，学习率可比全参更大（如 1e-3～5e-4），`weight_decay` 可设 0 或很小。
- **冻结策略**：主干全冻；可选“解冻 LayerNorm/bias”微调。
- **多任务**：每任务一套 adapter；**AdapterFusion** 可以学习若干适配器的加权组合；**MAD-X**（语言 adapter + 任务 adapter）适合多语多任务迁移。
- **推理**：激活对应任务的 adapter 即可；不需要改分词或上下文窗口。

### 伪代码

```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, TrainingArguments, Trainer
from adapters import AdapterConfig

MODEL = "t5-small"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)

# 新建并激活一个 adapter（Pfeiffer，r=16）
config = AdapterConfig.load("pfeiffer", reduction_factor=16, non_linearity="relu")
model.add_adapter("my_task", config=config)
model.train_adapter("my_task")
model.set_active_adapters("my_task")

# 准备数据与 Trainer（略）
# trainer = Trainer(model=model, args=..., train_dataset=..., eval_dataset=...)
# trainer.train()

# 导出：只保存 adapter 权重（体积小）
model.save_adapter("./adapters/my_task", "my_task")
```

## 更多方法

![4ca394530382c20146f22661bb34d060.png](http://public.file.lvshuhuai.cn/images\c99378736d661904c17b948671baf804.png)

## 对比

| 方法                        | 核心思路                                       | 插入位置 / 形式                | 需训练参数量（相对）          | 对基座权重               | 训练显存             | 推理开销                   | 典型超参（示例）                           | 优点                           | 局限/注意                          | 适用场景                | 与量化配合                 |
| --------------------------- | ---------------------------------------------- | ------------------------------ | ----------------------------- | ------------------------ | -------------------- | -------------------------- | ------------------------------------------ | ------------------------------ | ---------------------------------- | ----------------------- | -------------------------- |
| **Adapter**                 | 在层间插入小瓶颈模块（下投影→非线性→上投影）   | Transformer 各层子层之间       | 中（比全参少，通常百万级）    | 不改动基座参数           | 中                   | 低-中（需经过适配器）      | bottleneck 维度：8–64；插入层比例：1.0/0.5 | 稳定、可拔插、易多任务         | 轻微延迟；需选层与 $d_b$           | 企业与多任务可控部署    | 可；与 8/4bit 常配合       |
| **LoRA**                    | 以低秩分解近似权重增量：$\Delta W \approx B A$ | 线性层（如 $Q/K/V$、MLP 投影） | 低（与 $r$ 成正比）           | 冻结基座，仅注入增量     | 低                   | 低（推理仅多两次小矩阵乘） | $r$：4-16，$\alpha$：8-32，按头/层选择     | 高效、省参、效果强             | 对 $r$ 与注入位置敏感              | 指令/领域微调首选       | 可；常与 8/4bit 一起       |
| **QLoRA**                   | 基座权重 $4$bit 量化（如 NF4/FP4）+ LoRA 训练  | 同 LoRA（在线性层注入）        | 很低（与 LoRA 相当）          | 不改动基座（量化后读取） | **很低**（显存最省） | 低-中（量化解码略有代价）  | 4bit + fp16 优化器；$r$：8-16              | **极省显存**，单卡可训 7B/13B+ | 量化误差；实现需注意 block size 等 | 资源受限、单机微调      | **强配合场景**（方法本身） |
| **Prefix Tuning**           | 给每层注意力注入可训练“前缀键值”向量           | 每层自注意力 KV 前缀           | 低-中（与层数和前缀长度相关） | 不改动基座               | 低                   | 低-中（前缀会参与注意力）  | 前缀长度 8-64；全层/部分层                 | 参量少、收敛稳、可复用         | 前缀过长增延迟；层位敏感           | 对话/生成类，结构化引导 | 可；与 8/4bit 常用         |
| **Prompt Tuning（软提示）** | 仅在**输入嵌入前**加可训练“虚拟token”          | 词嵌入层（输入侧）             | **极低**                      | 不改动基座               | **极低**             | 极低                       | 虚拟token数 8-64                           | 最轻量、实现简单、切任务快     | 上限偏低，难以大分布迁移           | 少样本快速适配          | 可，最易与量化配合         |
