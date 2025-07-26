# 直接偏好优化 DPO

## 基本介绍

**DPO（Direct Preference Optimization）** 是一种轻量、稳定、无强化学习的对齐方法，它直接利用人类偏好数据训练语言模型，**不需要奖励模型、也不使用强化学习算法（如 PPO）**。

> - 训练简单
> - 更稳定
> - 效果媲美甚至超过 RLHF

## 背景与动机

### RLHF 的痛点
- 需要训练一个奖励模型（Reward Model）
- 使用 PPO 强化学习，训练复杂、收敛不稳定
- 存在 reward hacking 等问题

### DPO 的目标
用简单的分类目标函数，**直接训练语言模型去偏好人类更喜欢的回答**，完全跳过奖励建模与策略优化环节。

## 训练流程

<img src="Z:\Public\images\1lK6iJMz5CGh2fo7TsDn15A.png" alt="Direct Preference Optimization (DPO) of LLMs: A Paradigm Shift | by LM Po |  Medium" style="zoom:50%;" />

### 输入数据
- prompt（输入）
- pos_response（人类偏好回答）
- neg_response（被淘汰的回答）

### 模型目标
- 让模型偏向生成 $y^+$，远离 $y^-$

## 损失函数（核心公式）

令：
- $\pi$：当前语言模型
- $\pi_0$：初始模型（SFT 后模型）
- $y^+$：人类偏好回答
- $y^-$：较差回答
- $\beta$：温度系数（控制对偏好的重视程度）

DPO 的目标函数为：

$$
\mathcal{L}_{\text{DPO}} = - \log \left( \frac{\exp(\beta(\log \pi(y^+) - \log \pi_0(y^+)))}{\exp(\beta(\log \pi(y^+) - \log \pi_0(y^+))) + \exp(\beta(\log \pi(y^-) - \log \pi_0(y^-)))} \right)
$$

> 这是一个 softmax 二分类损失，鼓励模型更倾向于人类偏好的回答。

## 伪代码实现

```python
# 输入: prompt, pos_response, neg_response

logp_pos = model.log_prob(prompt, pos_response)
logp_neg = model.log_prob(prompt, neg_response)
logp_pos_ref = ref_model.log_prob(prompt, pos_response)
logp_neg_ref = ref_model.log_prob(prompt, neg_response)

# 温度参数
beta = 0.1

# 差值计算
delta_pos = beta * (logp_pos - logp_pos_ref)
delta_neg = beta * (logp_neg - logp_neg_ref)

# DPO 损失
loss = -log( exp(delta_pos) / (exp(delta_pos) + exp(delta_neg)) )
