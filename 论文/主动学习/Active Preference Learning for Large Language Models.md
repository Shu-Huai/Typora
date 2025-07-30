# Active Preference Learning for Large Language Models

## 信息

- 主题：大语言模型的主动偏好学习（Active Preference Learning, APL）
- 作者：William Muldrew 等，UCL
- 会议：ICML 2024
- 方法核心：在 Direct Preference Optimization (DPO) 框架下引入主动学习策略
- 数据集：IMDB、TLDR
- 模型：GPT-2（IMDB）、Pythia 1B（TLDR）
- 评价方式：GPT-4 提供偏好打分

## 摘要

随着大型语言模型（LLMs）能力不断增强，针对人类意图对齐的微调技术愈发重要。对齐这些模型的核心考量在于如何最有效地利用人力资源，或在以 LLMs 自身作为决策代理时优化模型资源。基于人类或AI偏好的强化学习（RLHF/RLAIF）是该领域最典型的技术，但其流程复杂且稳定性不足。直接偏好优化（DPO）作为更简洁稳定的替代方案近期被提出。本研究为 DPO 开发了一种主动学习策略，以更高效利用偏好标注数据。我们提出了一种基于语言模型预测熵及 DPO 优化的隐式偏好模型确定性度量的提示/补全对采集函数，并通过实验证明该方法能同步提升配对偏好数据的微调学习速率与最终性能。

## 研究动机

- 当前 LLM 的偏好微调主要通过 RLHF 实现：
  1. 收集偏好数据（人类或 AI 判断成对生成结果哪个更优）
  2. 训练奖励模型
  3. 使用 PPO 等强化学习算法微调语言模型参数

- RLHF 存在以下问题：
  - 引入多个模型（奖励模型 + 值函数）复杂度高
  - 对超参数敏感，训练过程不稳定
  - 大模型和人工标注的成本高昂

- DPO（Direct Preference Optimization）是 RLHF 的一种替代方案：
  - 不需要奖励模型和强化学习
  - 仅基于 pairwise 偏好数据直接优化交叉熵损失
  - 更加稳定高效，但也依赖大量偏好数据

- 问题核心：如何在有限偏好标注预算下最大化模型对齐效果？

因此，作者提出了一种基于 DPO 的主动学习框架（Active Preference Learning，APL），以更高效地选择哪些 prompt/completion pair 应该被送去标注，从而提高学习效率和最终性能。

## 方法

### 总体流程：Active Preference Learning for DPO

APL 在 DPO 基础上引入主动学习机制。不同于一次性收集全部偏好数据，APL 采用“边训练边选数据”的迭代流程：

1. 随机采样一批 prompts
2. 使用当前模型生成 completion 对 $(y_0, y_1)$
3. 使用采样函数（acquisition function）对 $(x,y_0, y_1)$ 打分
4. 选出得分最高的 subset，请求 oracle（GPT-4）标注哪个更好 $(y_w, y_l)$
5. 用收集到的新偏好对更新 DPO 模型
6. 重复上述过程直到标注预算耗尽

这一流程被算法 1 形式化，每轮迭代称为一个 acquisition step，共进行 $T$ 轮，直到使用完 $B$ 条偏好标签预算。每轮获取 $M$ 条高分样本，使用全部已有偏好数据进行 DPO 微调，训练出新模型 $$\theta_{t+1}$$。

<img src="http://public.file.lvshuhuai.cn/images\image-20250723161707479.png" alt="image-20250723161707479" style="zoom:50%;" />

### 采样函数（Acquisition Function）

作者提出三类简单但有效的采样函数来评估哪些样本最值得标注：

#### 语言模型预测熵（Predictive Entropy）
- 度量当前模型在生成某 prompt 的不确定性。
- 熵越高，代表模型越“迷茫”，优先采样。
- 用 Monte Carlo 近似：从 $$p_\theta(y|x)$$ 中采样多个 $y$，计算平均 token log-prob。

#### 偏好模型确定性差异（Preference Certainty）
- 基于 DPO 的隐式偏好模型：
  $$
  \hat{r}(x, y) = \beta \log \left[ \frac{p_\theta(y|x)}{p_{\theta_0}(y|x)} \right]
  $$
- 两个生成结果的 $$\hat{r}$$ 差值越大，代表模型偏好越强烈。
- 若模型偏好与 oracle 结果冲突，该样本价值更高。
- 优先选择差值最大的样本用于学习，提升梯度贡献。

#### 混合策略（Entropy + Certainty）
- 先根据 entropy 从 $$J \times S$$ 个 prompts 中选出 top-S
- 对其生成 completions，再按 certainty 排序并选出 top-M

### 偏好判断者（Oracle）的选择

APL 中 oracle 必须能在线判断每一轮生成结果的偏好。

- 使用 GPT-4 作为偏好判断者：
  - 相比 GPT-3.5，GPT-4 自洽性高（>90%）
  - 与人类标注一致性强

- prompt 设计：明确评估标准（如总结质量或正面情绪），并要求输出理由 + "A/B" 二选一。

- 为避免偏序偏见，每轮评估中随机交换 A/B 顺序。

### 微调细节（Fine-tuning Details）

- 每一轮 acquisition 后重新初始化模型参数 $$\theta_0$$，并对累积偏好数据 $$X_P$$ 使用 DPO 训练至收敛。
- 优化细节：
  - Optimizer: Adam，learning rate = 1e-6
  - Batch size = 64
  - 微调 epoch：IMDB 使用 50 轮，TLDR 使用 70 轮

- 重置训练有两点优势：
  1. 可隔离采样策略带来的影响，确保公平对比
  2. 标注开销更大，训练代价可接受

## 实验

