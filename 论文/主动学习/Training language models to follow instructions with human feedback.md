# Training language models to follow instructions with human feedback

## 基本信息

- **论文题目**：Training language models to follow instructions with human feedback
- **作者**：Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida 等
- **机构**：OpenAI
- **发表时间**：2022
- **核心模型**：InstructGPT
- **关键技术**：人类反馈强化学习（RLHF）、监督微调（SFT）、奖励模型（Reward Model）

## 摘要

单纯扩大语言模型的规模并不会使其更擅长遵循用户意图。例如，大型语言模型可能生成不真实、有害或对用户毫无帮助的输出。换言之，这些模型与用户需求存在偏差。本文提出了一种通过人类反馈微调来使语言模型与多样化任务中用户意图对齐的方法。我们首先基于标注员编写的提示词及 OpenAI API 提交的提示词，收集了展示理想模型行为的标注员示范数据集，并采用监督学习对 GPT-3 进行微调。随后通过收集模型输出排序数据集，利用人类反馈强化学习（RLHF）进一步优化监督模型。最终产物被命名为 InstructGPT 系列模型。人类评估显示，在我们设计的提示词分布测试中，13 亿参数的 InstructGPT 模型输出比 1750 亿参数的 GPT-3 更受青睐，尽管前者参数量仅为后者的 1%。此外，InstructGPT 在公共 NLP 数据集上保持性能稳定的同时，展现出生成结果真实性提升和有害输出减少的特性。尽管 InstructGPT 仍会犯简单错误，但我们的研究证明，基于人类反馈的微调是实现语言模型与人类意图对齐的重要方向。

## 研究背景

## 方法

### 总体方法（High-level methodology）

1. **收集示范数据，训练监督策略（SFT）**

    研究者组织标注员为一组自然语言提示词撰写理想输出示范，并以此数据监督微调预训练 GPT-3 模型，构建 SFT 模型。

2. **收集偏好比较数据，训练奖励模型（RM）**

    随后收集一组模型输出的比较数据，即给定同一个提示词下多个候选输出，标注员选择更优者。基于此训练奖励模型，使其能够预测人类偏好输出。

3. **使用 PPO 算法在奖励模型上进行强化学习（RL）**

    最后，以奖励模型作为奖励信号，对 SFT 模型进行强化学习微调，使用 Proximal Policy Optimization（PPO）算法优化输出。这个过程可以迭代进行：用当前最优策略生成新输出收集更多比较数据，更新 RM 与策略。

<img src="Z:\Public\images\image-20250722191817049.png" alt="image-20250722191817049" style="zoom:50%;" />

### 数据集（Dataset）

主要使用三类提示词数据：

- 来自 OpenAI API Playground 的提示词（早期 InstructGPT 用户提交）；
- 标注员手写提示词（用于冷启动）；
- 包含三种风格：Plain、Few-shot、User-based。

为训练不同阶段模型构建了三个数据集：

- **SFT 数据集**：13k 条提示词及理想输出；
- **RM 数据集**：33k 条提示词及多个模型输出 + 偏好标注；
- **PPO 数据集**：31k 条提示词用于强化训练（无人工标注）。

为了保护用户隐私，训练数据中去除了包含 PII（个人识别信息）的内容，且训练、验证、测试数据按用户 ID 分开，避免数据泄露。

### 任务类型（Tasks）

任务来源于两部分：

1. 人工编写的 instruction-like 提示词；
2. API 用户提交的自然语言任务。

任务类型非常多样，包括生成、问答、对话、摘要、抽取等自然语言任务。多数任务为英文。对于每条提示，意图可能以显式指令、few-shot 示例或文本延续等方式呈现。标注员被要求尽可能推断用户意图，同时注意输出的真实性和潜在有害性。

### 人类数据采集（Human data collection）

研究招募了约 40 名标注员，通过 Upwork 和 ScaleAI 进行。标注员需通过包含敏感性判断的筛选测试。训练过程中，OpenAI 研究者与标注员保持密切沟通，并提供详细的任务指令文档。

标注员不仅参与数据构建，也用于模型最终输出评价。在最终评价阶段，强调真实性（truthfulness）和无害性（harmlessness）优先于任务帮助性（helpfulness）。

另设立一组 `held-out` 标注员用于测试模型泛化能力，这组人未参与训练数据构建。研究显示 held-out 与训练标注员偏好一致性较高，说明模型未对单一标注者偏好过拟合。

标注一致性表现为：

- 训练标注员间一致率：72.6% ± 1.5%
- held-out 标注员一致率：77.3% ± 1.3%

### 模型（Models）

研究训练了三个阶段的模型：

#### 监督微调（SFT）

在标注员示范数据上微调 GPT-3 模型，使用余弦学习率衰减和 dropout=0.2。尽管验证集 loss 很快过拟合，但 RM 分数和人类偏好持续提升。

#### 奖励模型（Reward Model, RM）

从 SFT 模型去掉最后输出层后构建 RM，其输入为（提示词 + 响应），输出为一个标量分数。使用的损失函数为：

$$
\text{loss}(\theta) = -\frac{1}{\binom{K}{2}} \mathbb{E}_{(x,y^w,y^l) \sim D} \left[\log \sigma(r_\theta(x,y^w) - r_\theta(x,y^l))\right]
$$

| 符号                                 | 含义                                                         |
| ------------------------------------ | ------------------------------------------------------------ |
| $\theta$                             | 奖励模型的参数                                               |
| $x$                                  | 一个提示（prompt）                                           |
| $y^w$，$y^l$                         | 在一个提示下，标注员更喜欢的回答（$w$：winner），和较差的回答（$l$：loser） |
| $r_\theta(x, y)$                     | 奖励模型对提示 `x` 和回答 `y` 的打分（分数越高越偏好）       |
| $\sigma(z)$                          | sigmoid 函数 $\sigma(z) = \frac{1}{1 + e^{-z}}$，将分数差转为概率 |
| $\log \sigma(r(x, y^w) - r(x, y^l))$ | 奖励模型预测“$w$ 比 $l$ 更好”的 log 概率                     |
| $\binom{K}{2}$                       | 对每个提示评估 $K$ 个回答，一共会构成 $\binom{K}{2}$ 对比较（即从 $K$ 个输出中两两配对） |
| $\mathbb{E}_{...}$                   | 对所有比较对取期望（平均损失）                               |
| 最前的负号                           | 因为我们要最小化 loss，相当于最大化对正确偏好的预测概率      |

其中 $y^w$ 和 $y^l$ 是成对偏好中的优劣项，$\sigma$ 为 sigmoid 函数。每次评价使用 $K=4\sim 9$ 个候选输出。

为提升训练效率与稳定性，将所有 $\binom{K}{2}$ 对比较作为同一批次进行训练，避免高相关性带来的过拟合。

RM 输出经归一化处理，使人工示范样本的平均评分为 0。

#### 强化学习（RL with PPO）

在 PPO 强化学习中，模型根据奖励模型分数作为奖励进行优化。每一步使用 KL 惩罚项抑制偏离 SFT 策略，同时尝试加入预训练分布的 log-likelihood 作为正则项，提出 PPO-ptx 模型：

$$
\text{objective}(\phi) = \mathbb{E}_{(x,y) \sim D} \left[ r_\theta(x, y) - \beta \log \left( \frac{\pi_{\text{RL}}(y|x)}{\pi_{\text{SFT}}(y|x)} \right) \right] + \gamma \mathbb{E}_{x \sim D_{\text{pretrain}}} [\log \pi_{\text{RL}}(x)]
$$

| 项目                                                         | 含义                                            |
| ------------------------------------------------------------ | ----------------------------------------------- |
| $\pi_{\text{RL}}(y|x)$                                       | 当前策略                                        |
| $\pi_{\text{SFT}}(y|x)$                                      | SFT 模型策略                                    |
| $r_\theta(x, y)$                                             | 奖励模型对输出的打分                            |
| $\log \left( \frac{\pi_{\text{RL}}}{\pi_{\text{SFT}}} \right)$ | 策略的偏移程度（类似 KL 散度项）                |
| $\beta$                                                      | 控制策略偏移惩罚的强度                          |
| $\gamma$                                                     | 控制预训练分布正则项的强度                      |
| $\log \pi_{\text{RL}}(x)$                                    | 模型在预训练数据上“看懂”的程度（语言建模 loss） |
| $D$                                                          | API prompt 数据集                               |
| $D_{\text{pretrain}}$                                        | 原始预训练语料库（如网页、书籍等）              |

其中：

- $\pi_{\text{RL}}$：当前策略；
- $\pi_{\text{SFT}}$：SFT 模型策略；
- $\beta$ 为 KL 惩罚强度，$\gamma$ 为预训练保留强度。

对于 PPO 模型，$\gamma = 0$；对于 PPO-ptx 模型，$\gamma > 0$，可缓解 NLP benchmark 上的性能下降。

#### 基线模型对比

- GPT-3（无提示）；
- GPT-3（few-shot prompted）；
- GPT-3 微调版本（T0、FLAN）；
- 各种 SFT、PPO、PPO-ptx 模型。

## 实验

<img src="Z:\Public\images\image-20250722193003392.png" alt="image-20250722193003392" style="zoom:50%;" />
