# Prefix-Tuning: Optimizing Continuous Prompts for Generation

## 基本信息

- 前缀调优：面向生成的连续提示优化
- 一种大模型微调技术
- ACL-IJCNLP 2021
- GitHub：[XiangLi1999/PrefixTuning: Prefix-Tuning: Optimizing Continuous Prompts for Generation](https://github.com/XiangLi1999/PrefixTuning)

## 摘要

微调是利用大规模预训练语言模型处理下游任务的实际标准方法。然而，微调会修改语言模型的所有参数，因此需要为每个任务存储完整副本。本文提出前缀调优——一种面向自然语言生成任务的轻量级微调替代方案，该方法冻结语言模型参数，转而优化一系列连续的特定任务向量（我们称之为前缀）。前缀调优从语言模型提示技术中汲取灵感，使后续标记能够像处理“虚拟标记”一样关注此前缀。我们将前缀调优应用于 GPT-2 进行表格到文本生成，并应用于 BART 实现摘要生成。实验表明：仅调整 0.1% 参数时，前缀调优在完整数据环境下可获得与微调相当的性能，在低数据环境下优于微调，且对训练期间未见过主题的样本具有更好的泛化能力。

## 关键方法

### 问题设定
对自回归 LM（或编解码器模型），把输入/输出拼成序列：
- 解码式：`z = [PREFIX; x; y]`
- 编解码式：`z = [PREFIX; x; PREFIX′; y]`（分别给编码器与解码器加前缀）

<img src="Z:\Public\images\image-20251007212348530.png" alt="image-20251007212348530" style="zoom:50%;" />

### 核心思想
用**可训练的“前缀激活”**替换前缀位置的隐藏表示（而非只调词嵌入）。设前缀索引集为 $P_{\text{idx}}$，隐藏表示为 $h_i$：
$$
h_i=
\begin{cases}
P_\theta[i,:], & i\in P_{\text{idx}}\\
\mathrm{LM}_\phi(z_i, h_{<i}), & \text{否则}
\end{cases}
$$
其中 $P_\theta\in \mathbb{R}^{|P_{\text{idx}}|\times \mathrm{dim}(h_i)}$ 为**可训练前缀矩阵**，而预训练 LM 的参数 $\phi$ **保持冻结**。这样能**直接修改更深层表示**，无需依赖自底向上的长传播路径。

### 训练目标
与标准条件语言建模相同：最大化 $\log p_\phi(y\mid x, P_\theta)$。**仅更新 $\theta$**（前缀参数），$\phi$ 固定。即使 $i\notin P_{\text{idx}}$，其激活仍受左侧前缀影响，因而 $h_i$ 也依赖 $P_\theta$。

### 参数化与稳定性
直接优化 $P_\theta$ 可能不稳定，采用**低维码本 + MLP** 的重参数化：
$$
P_\theta[i,:] \;=\; \mathrm{MLP}_\theta\!\big(P'_\theta[i,:]\big),
$$
其中 $P'_\theta\in\mathbb{R}^{|P_{\text{idx}}|\times k}$（如 $k\approx 512$ 或 $800$），$\mathrm{MLP}_\theta$ 将其映射到 $\mathrm{dim}(h_i)$。训练后可仅保存展开后的 $P_\theta$。

## 实验

<img src="Z:\Public\images\image-20251007212410960.png" alt="image-20251007212410960" style="zoom:50%;" />

## 使用方法

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import PrefixTuningConfig, get_peft_model, TaskType
from datasets import load_dataset

model_name = "facebook/opt-350m"
tok = AutoTokenizer.from_pretrained(model_name, use_fast=True)
tok.pad_token = tok.eos_token

ds = load_dataset("imdb", split="train[:2000]")
def format_fn(ex):
    text = f"Summarize the sentiment of the following review.\n\n{ex['text']}\n\nAnswer:"
    return {"input_ids": tok(text, truncation=True, max_length=512)["input_ids"]}
ds = ds.map(format_fn).remove_columns([c for c in ds.column_names if c != "input_ids"])

model = AutoModelForCausalLM.from_pretrained(model_name)

prefix_cfg = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=30  # prefix 长度
)
model = get_peft_model(model, prefix_cfg)

args = TrainingArguments(
    output_dir="out-prefix", per_device_train_batch_size=4, num_train_epochs=1,
    learning_rate=1e-3, logging_steps=50, fp16=True
)
collator = DataCollatorForLanguageModeling(tok, mlm=False)
trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collator)
trainer.train()

model.save_pretrained("out-prefix/adapter")
```

