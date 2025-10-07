# QLoRA: Efficient Finetuning of Quantized LLMs

## 基本信息

- NeurIPS 2023
- 一种大模型微调技术
- QLoRA：量化大语言模型的高效微调
- GitHub：[artidoro/qlora: QLoRA: Efficient Finetuning of Quantized LLMs](https://github.com/artidoro/qlora)

## 摘要

我们推出 QLoRA——一种高效微调方法，该方法能将内存使用量降低至可在单块 48GB GPU 上微调 650 亿参数模型，同时保持全 16 位微调任务性能。QLoRA 通过冻结的 4 位量化预训练语言模型将梯度反向传播至低秩适配器（LoRA）。我们将其性能最优的模型系列命名为 Guanaco，在 Vicuna 基准测试中超越此前所有公开模型，仅需单 GPU 微调 24 小时即可达到 ChatGPT 性能水平的 99.3%。QLoRA 引入多项创新技术实现内存节省且不牺牲性能：（a）4 位标准浮点数（NF4）——该新型数据类型在信息理论上对正态分布权重最优；（b）二次量化——通过量化量化常数来降低平均内存占用；（c）分页优化器——用于管理内存峰值。我们使用 QLoRA 微调超过 1,000 个模型，基于 8 个指令数据集、多种模型类型（LLaMA、T5）及常规微调难以运行的模型规模（如 330 亿和 650 亿参数模型），对指令跟随和聊天机器人性能进行详细分析。结果表明，即使采用比先前最优模型更小的架构，在小规模高质量数据集上进行 QLoRA 微调仍能取得最先进成果。我们基于人类评估和 GPT-4 评估对聊天机器人性能展开详细分析，证明 GPT-4 评估可作为人类评估的经济有效替代方案。此外，我们发现当前聊天机器人基准测试无法准确评估性能水平。通过选择性分析揭示了 Guanaco 相较 ChatGPT 的不足。我们开源全部模型和代码，包括用于 4 位训练的 CUDA 内核。

## 主要方法

### 总体思路

<img src="Z:\Public\images\image-20251007194140079.png" alt="image-20251007194140079" style="zoom:50%;" />

- **存储**：将预训练基座权重 $W$ 以 **4-bit**（默认 **NF4**）量化后存储。  
- **计算**：用到时将 $W$ **解量化到 BF16**，前向/反向均在 **BF16** 中完成。  
- **训练**：**冻结**量化后的基座参数，仅训练 **LoRA 适配器**（低秩增量）。  
- **内存管理**：使用 **Paged Optimizers**（基于统一内存）缓解显存峰值与 OOM。

### LoRA 适配器（基础形式）

对线性层 $Y=XW$，LoRA 引入低秩增量：
$$
Y = XW + s\,X L_1 L_2,
$$
其中 $L_1\in\mathbb{R}^{h\times r},\ L_2\in\mathbb{R}^{r\times o}$ 为唯一可训练参数，$W$ 冻结，$s$ 为缩放因子。

### 存储 dtype 与计算 dtype 分离
- **权重存储**（4-bit，NF4）：极小显存占用。  
- **算子计算**（BF16）：矩阵乘等算子在 BF16 中执行以保证数值稳定。  
- **梯度路径**：仅对 $L_1,L_2$ 求梯度；对量化权重不求梯度，但反向仍需穿过“解量化 $\to$ BF16”的计算图以获得对 $X$ 的梯度贡献。

### NF4（NormalFloat 4-bit）
动机：预训练权重常近似零均值正态分布。若已知分布形态，可**预先**用该分布的分位点设计“信息论最优”的量化刻度。

做法：将张量及 dtype 统一到 $[-1,1]$ 规范域；以标准正态 $X\sim \mathcal{N}(0,1)$ 的分位函数 $Q_X(\cdot)$ 生成刻度（确保零点精确可表），并采用非对称拼接保证正负各 $2^{k-1}$ 个刻度（$k=4$）。

### 双重量化（Double Quantization, DQ）
4-bit 权重需按块记录比例尺/偏置等“量化常数”。若这些常数用 32-bit 存储，开销约为：
$$
\text{overhead} \approx \frac{32}{\text{blocksize}}\ \text{bit/参数}.
$$
**双重量化**将这些常数再量化（论文使用 **FP8**，更大块大小，如 256），把总开销降到：
$$
\frac{8}{64}+\frac{32}{64\cdot 256} \approx 0.127\ \text{bit/参数},
$$
显著低于原来的 $\approx 0.5\ \text{bit/参数}$。

### Paged Optimizers
利用 GPU/CPU 统一虚拟内存，将优化器状态按需换入/换出，以**分页**方式平滑瞬时内存峰值（长序列、梯度检查点等情形下尤为明显），减少 OOM。

### 一层线性的 QLoRA 前向（形式化）
记 $\operatorname{dequant}(\cdot)$ 为一次解量化，$\operatorname{doubleDequant}(\cdot)$ 为对“被双重量化的常数 + 4-bit 权重”的两级解量化。设：
- $W_{4\text{bit}}$ 是按 **NF4**（如 blocksize=64）量化的权重；
- $c^{\text{FP32}}_1$ 为一级常数，$c^{k\text{-bit}}_2$（如 FP8，blocksize=256）为其再量化结果。

则前向为：
$$
\begin{aligned}
Y_{\text{BF16}} &= X_{\text{BF16}}\ \operatorname{doubleDequant}\!\left(c^{\text{FP32}}_{1},\ c^{k\text{-bit}}_{2},\ W_{4\text{bit}}\right)\ +\ X_{\text{BF16}} L^{\text{BF16}}_{1} L^{\text{BF16}}_{2},\\
\operatorname{doubleDequant}(c^{\text{FP32}}_{1},c^{k\text{-bit}}_{2},W_{4\text{bit}})
&= \operatorname{dequant}\!\big(\ \operatorname{dequant}(c^{\text{FP32}}_{1},c^{k\text{-bit}}_{2})\ ,\ W_{4\text{bit}}\ \big)\ =\ W_{\text{BF16}}.
\end{aligned}
$$

## 使用方法

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset

model_name = "facebook/opt-350m"
bnb_cfg = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

tok = AutoTokenizer.from_pretrained(model_name, use_fast=True)
tok.pad_token = tok.eos_token

ds = load_dataset("imdb", split="train[:2000]")
def format_fn(ex):
    text = f"Review: {ex['text']}\nSentiment: "
    return {"input_ids": tok(text, truncation=True, max_length=512)["input_ids"]}
ds = ds.map(format_fn).remove_columns([c for c in ds.column_names if c != "input_ids"])

model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_cfg, device_map="auto")

peft_cfg = LoraConfig(
    task_type=TaskType.CAUSAL_LM, r=16, lora_alpha=32, lora_dropout=0.05,
    target_modules=["q_proj","v_proj"]
)
model = get_peft_model(model, peft_cfg)

args = TrainingArguments(
    output_dir="out-qlora", per_device_train_batch_size=4, gradient_accumulation_steps=2,
    num_train_epochs=1, learning_rate=2e-4, logging_steps=50, bf16=True
)
data_collator = DataCollatorForLanguageModeling(tok, mlm=False)
trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=data_collator)
trainer.train()

model.save_pretrained("out-qlora/adapter")
```

