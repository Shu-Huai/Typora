# The Power of Scale for Parameter-Efficient Prompt Tuning

## 基本信息

- 规模的力量：参数高效提示调优
- 一种大模型微调技术
- EMNLP 2021
- GitHub：[google-research/prompt-tuning: Original Implementation of Prompt Tuning from Lester, et al, 2021](https://github.com/google-research/prompt-tuning)

## 摘要

在本研究中，我们探索了“提示调优”（prompt tuning）这一简单而高效的机制，通过训练“软提示”来使冻结的语言模型适应特定下游任务。与 GPT-3 使用的离散文本提示不同，软提示通过反向传播学习，可调整以融入任意数量标注样本的信号。我们的端到端学习方法大幅超越了 GPT-3 的小样本学习性能。更显著的是，通过对 T5 模型进行尺寸消融实验，我们发现提示调优的竞争力随模型规模提升而增强：当参数规模超过十亿级时，我们的方法“弥合差距”，达到了全参数调优（model tuning）的强劲性能。这一发现尤为重要，因为大模型共享和服务成本高昂，而冻结模型的多任务复用能力可有效缓解这一负担。我们的方法可视为 Li 和 Liang（2021）近期提出的“前缀调优”（prefix tuning）的简化版本，并提供了与该技术及其他类似方法的对比。最后，我们证明使用软提示条件化冻结模型能增强领域迁移的鲁棒性，并实现高效的“提示集成”。我们公开了代码和模型检查点以复现实验。

## 关键方法

<img src="http://public.file.lvshuhuai.cn/images\image-20251008180733222.png" alt="image-20251008180733222" style="zoom:50%;" />

### 问题设定与基本思想

- 采用 **text-to-text** 范式：把下游任务统一为条件生成 $\Pr(Y \mid X)$。在常规 prompting 中，向输入前拼接离散提示 $P$，并在**冻结模型参数 $\theta$** 的前提下最大化 $\Pr_\theta(Y\mid [P;X])$。
- **Prompt Tuning** 将提示从“离散词表选择”改为一段**可训练的软提示**，为提示单独引入参数 $\theta_P$。训练时最大化 $\Pr_{\theta;\theta_P}(Y\mid [P;X])$，并**只**对 $\theta_P$ 反传更新。直观地，把固定数量的“特殊提示 token”接在输入前，**仅它们的嵌入可更新**。

### 前向构造与训练目标

- 设输入 token 序列长度为 $n$，其嵌入为 $X_e\in\mathbb{R}^{n\times e}$；软提示为可训练矩阵 $P_e\in\mathbb{R}^{p\times e}$（$p=提示长度$）。
- 将二者按行拼接为 $[P_e;X_e]\in\mathbb{R}^{(p+n)\times e}$，送入冻结的 encoder–decoder；**损失**为对 $Y$ 的条件似然/交叉熵，仅更新 $P_e$。

### 训练与推理流程

- **训练**：冻结全部预训练权重 $\theta$；初始化 $P_e$；以标准自回归目标训练，只更新 $P_e$。
- **推理**：针对每个任务加载其学习好的 $P_e$，拼接到输入前生成 $Y$；同一份冻结底模可服务多任务。

### Design Decisions（设计抉择）

#### 提示初始化

三种方案：

1. **随机初始化**（如均匀分布）；
2. **词表初始化**：每个提示位用词表嵌入初始化（“软提示像输入前缀文本”，词样式的初始嵌入更贴近模型分布）；
3. **类别名初始化（分类）**：用**合法类名**的嵌入（多 token 取平均）初始化若干提示位，**引导**模型生成合法目标。 

> 实证：小模型对初始化更敏感，“类别名初始化”最好；随模型变大，差异收敛。实现细节：随机采样范围、词表采样高频词、ReCoRD/WSC 等生成式任务用与任务相关的词进行初始化回填。

### 提示长度

- 新增参数量为 **$E\times P$**（嵌入维 $E$ × 长度 $P$）；应在**尽量短**的 $P$ 下获得良好效果。
- 经验规律：多数规模下 **20+** token 带来显著提升，超过 **20** 收益递减；对 **XXL** 级模型，**单 token** 也能有强表现，>100 token 对大模型略有害。 

### Unlearning Span Corruption（从 Span Corruption “反学习”）

#### 背景

- T5 预训练目标为 **Span Corruption**：输入以 sentinel 标注掩蔽片段；目标是将被掩蔽内容按 sentinel 串联输出，**每个目标都以 sentinel 开头**。这与自然的输入/输出分布有偏差。 
- 这种“偏好输出 sentinel”的先验，对**只调提示**的方案尤为不利，因为**解码器先验不可更新**。

### 三种设置

1. **Span Corruption**：直接用原 T5 作为冻结底模做 Prompt Tuning；
2. **Span Corruption + Sentinel**：给**下游目标**强行加 sentinel，使其更像预训练目标形态；
3. **LM Adaptation**：先对 T5 做少量**继续自监督训练**，但把目标改为标准 **语言建模（LM）**，再进行 Prompt Tuning。

### 结论与做法

- 仅向下游目标添加 sentinel 的收益很有限；
- **LM Adaptation 明显更优**：将模型从“带 sentinel 的重构”分布迁移到“自然文本 LM”分布，更匹配 Prompt Tuning；**适配越久越有益**（论文中持续到 100k steps 仍有增益）；超大模型对该环节更鲁棒。

## 实验

<img src="http://public.file.lvshuhuai.cn/images\image-20251008180752055.png" alt="image-20251008180752055" style="zoom:50%;" />