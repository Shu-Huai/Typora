# Direct Preference Optimization: Your Language Model is Secretly a Reward Model

## 基本信息

- **论文标题**：Direct Preference Optimization: Your Language Model is Secretly a Reward Model  
- **作者**：Rafael Rafailov, Archit Sharma, Eric Mitchell 等  
- **机构**：Stanford University  
- **会议**：NeurIPS 2023  
- **关键词**：对齐、偏好学习、DPO、语言模型、强化学习、RLHF  

## 摘要

虽然大规模无监督语言模型（LMs）能够学习广泛的世界知识和一定推理能力，但由于其完全无监督的训练性质，实现对其行为的精确控制十分困难。现有方法通过收集人类对模型生成结果相对质量的标注数据，并利用这些偏好对无监督 LM 进行微调（通常采用基于人类反馈的强化学习 RLHF）来实现可控性。然而 RLHF 流程复杂且不稳定：首先需训练反映人类偏好的奖励模型，随后通过强化学习微调大型无监督 LM 以最大化该估计奖励，同时避免与原始模型偏离过远。本文通过建立奖励函数与最优策略之间的映射关系，证明该带约束的奖励最大化问题可通过单阶段策略训练精确优化，本质上将转化为对人类偏好数据的分类问题。由此得到的算法——我们称之为直接偏好优化（DPO）——具有稳定性强、性能优异、计算轻量的特点，无需训练奖励模型、微调期间从 LM 采样或进行大量超参数调优。实验表明，DPO 在使 LMs 对齐人类偏好方面达到或超越现有方法。值得注意的是，DPO 微调在控制生成内容情感倾向的任务上优于 RLHF，同时在摘要和单轮对话任务中提升响应质量，且实现和训练过程显著简化。

## 研究背景

大规模语言模型（LM）虽然在预训练阶段习得了强大的生成和推理能力，但其行为往往不可控、不可预测，可能生成具有误导性、不安全或不符合人类意图的内容。为增强模型可控性，社区广泛采用**人类反馈强化学习（RLHF）**框架，通过偏好数据间接学习出“好的”行为策略。

然而，RLHF 存在如下挑战：
- **复杂性高**：包括监督微调（SFT）、训练奖励模型、策略微调三阶段；
- **训练代价大**：需频繁从语言模型采样、使用强化学习（如 PPO）优化，计算和调参成本高；
- **不稳定性**：RLHF 中的 actor-critic 结构容易陷入 collapse、偏移等问题。

为此，本文提出 **Direct Preference Optimization（DPO）**，其核心思想是：**语言模型本身隐式定义了一个奖励模型，可以直接从人类偏好中优化策略，而无需 RL**。

## 方法

### DPO

<img src="Z:\Public\images\image-20250722212659151.png" alt="image-20250722212659151" style="zoom:50%;" />

DPO 用一个简单的 **二分类损失** 替代 RLHF 中复杂的策略优化过程，目标是让模型生成更倾向于人类喜欢的输出。

对每一个 prompt $$x$$，人类对两个模型输出 $$y_w$$（胜者）与 $$y_l$$（败者）表示偏好。DPO 的优化目标如下：

$$
\mathcal{L}_{\text{DPO}}(\pi_\theta; \pi_{\text{ref}}) = - \mathbb{E}_{(x, y_w, y_l) \sim D} \left[\log \sigma\left( r(x, y_w) - r(x, y_l) \right) \right]
$$

其中：
- $r(x, y) = \beta \cdot \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)}$，是语言模型隐式定义的 reward；
- $$\pi_{\text{ref}}$$ 是参考策略（通常为 SFT 模型）；
- $$\sigma$$ 是 sigmoid 函数。

这种设计源于 **Bradley-Terry 偏好模型**，利用 reward 差值建模偏好概率。

#### DPO 优势
- 不需要显式训练 reward model；
- 不需要 RL，不需策略采样；
- 损失函数简单易懂，仅用 cross-entropy；
- 可解释性强：语言模型即 reward 模型；
- 实现简单，计算轻量，鲁棒性好。

## DPO 的理论分析

DPO 理论基础是 reward 与策略的映射关系。在 KL 约束下的最优策略有如下闭式解：

$$
\pi^*(y|x) \propto \pi_{\text{ref}}(y|x) \cdot \exp\left( \frac{r(x,y)}{\beta} \right)
$$

从而可以反推 reward 为：

$$
r(x,y) = \beta \cdot \log \frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + \text{常数}
$$

这表明：**策略本身隐式定义了 reward（最多差一个关于 prompt 的常数项）**。DPO 将 reward 参数化为语言模型 log 概率差，直接对策略进行优化。

此外，作者证明该重参数化不会限制 reward 的表达能力，并且在 Bradley-Terry 偏好模型下，**等价的 reward 函数族会诱导相同的最优策略**。

## 实验

### 情感控制生成（IMDb）
- 任务：生成符合正面情感的电影评论；
- 结果：DPO 达到比 PPO 更高的奖励 / KL 效率曲线；
- 结论：**DPO 优化目标更稳健、收敛更快、KL 更小**。

### Reddit TL;DR 摘要生成
- 模型：GPT-J SFT + DPO / PPO / Preferred-FT；
- 评估：使用 GPT-4 对生成摘要与参考摘要进行偏好投票；
- 结果：DPO 的 win rate 高于 PPO 与 Best-of-N baseline，并对温度更鲁棒；
- 结论：**无需调参的 DPO 已能超越经过调参的 PPO**。

### 单轮对话（Anthropic HH）
- 任务：对用户提问生成有帮助、有礼貌的回答；
- 结果：DPO 是唯一能显著优于原始偏好数据的高效方法；
- 结论：**DPO 可扩展至对话生成任务，效果强于 RLHF 和 Few-shot 方法**。

