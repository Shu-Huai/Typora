# 人类反馈强化学习 RLHF

## 基本介绍

**RLHF** 是一种利用人类反馈对大型语言模型进行“对齐”训练的方法。其核心思想是：  
> **使用人类偏好训练奖励模型，指导语言模型通过强化学习输出更符合人类偏好的内容。**

该方法被 OpenAI 用于 InstructGPT 和 ChatGPT 等模型的训练中。

## 三阶段训练流程

![什么是RLHF？– 基于人类反馈的强化学习简介– AWS](http://public.file.lvshuhuai.cn/images\ML-14874_image001.jpg)

### 监督微调（Supervised Fine-Tuning, SFT）

- 在人类撰写的高质量回答数据上，使用标准交叉熵训练语言模型。
- 得到一个初始可用、略具指令能力的语言模型。

### 训练奖励模型（Reward Model, RM）

- 收集 prompt 下多个回答对（A/B），由人类标注哪一个更好。

- 用这类排序数据训练一个 reward model $R(x, y)$，输出标量评分。

- 通常采用 pairwise Bradley-Terry 模型损失函数：
  $$
  \mathcal{L}_{\text{RM}} = - \log \left( \frac{e^{R(x, y^+)}}{e^{R(x, y^+)} + e^{R(x, y^-)}} \right)
  $$

### 强化学习微调（PPO）

- 让语言模型在训练集 prompt 上生成回答，交给奖励模型打分。
- 用 **PPO（Proximal Policy Optimization）** 算法优化语言模型，使其生成的内容能获得更高奖励。

## 技术细节

### 奖励模型训练（Reward Model）

- 输入：prompt 和回答组合
- 输出：一个实数奖励值（越高表示越符合人类偏好）
- 损失函数：Pairwise Ranking Loss（如 Bradley-Terry）

### 强化学习优化（PPO）

- 奖励来自奖励模型：$r = R(x, y)$
- 优化目标是最大化奖励，同时保持和初始策略的差异不超过某一范围（使用 KL 限制）

PPO 的优化目标近似为：
$$
\max_\theta \mathbb{E} \left[ \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)} A(y) - \lambda \cdot \text{KL}[\pi_\theta || \pi_{\text{ref}}] \right]
$$
其中：
- $\pi_\theta$：当前策略（LLM）
- $\pi_{\text{ref}}$：参考策略（通常是 SFT 模型）
- $A(y)$：优势函数，由奖励减去基线（如平均值）得到

## 关键代码结构（伪代码 + 示例）

### 奖励模型训练伪代码

```python
# 输入: prompt, pos_response, neg_response
def reward_model_loss(pos_score, neg_score):
    return -log(exp(pos_score) / (exp(pos_score) + exp(neg_score)))

# 示例（伪代码）
for batch in dataloader:
    pos_score = reward_model(prompt, pos_resp)
    neg_score = reward_model(prompt, neg_resp)
    loss = reward_model_loss(pos_score, neg_score)
    loss.backward()
```

### PPO 训练伪代码（使用 TRL 库）

```python
from trl import PPOTrainer

ppo_trainer = PPOTrainer(model, ref_model, reward_model, config)

for batch in dataset:
    response = model.generate(batch["prompt"])
    reward = reward_model(batch["prompt"], response)
    ppo_trainer.step(batch["prompt"], response, reward)
```

> 可使用 Hugging Face 的 `trl` 库实现完整 PPO 训练流程。