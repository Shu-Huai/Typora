# NCE

## NCE（Noise-Contrastive Estimation）要解决的问题：归一化常数难计算

### 未归一化密度与归一化常数
很多模型只能方便地给出“未归一化”的打分（或能量）
$$
\tilde{p}_\theta(x)\ge 0
$$
对应的归一化概率为：
$$
p_\theta(x)=\frac{\tilde{p}_\theta(x)}{Z_\theta}
$$
其中归一化常数（partition function）：

- 连续情形：$\displaystyle Z_\theta=\int \tilde{p}_\theta(x)\,dx$
- 离散情形：$\displaystyle Z_\theta=\sum_x \tilde{p}_\theta(x)$

最大似然（MLE）需要优化 $\log p_\theta(x)$，势必出现 $\log Z_\theta$。当 $x$ 的空间巨大（例如大词表语言模型、能量模型）时，$Z_\theta$ 计算代价极高甚至不可行。

### NCE 的总体思路
NCE 不直接做“生成式似然最大化”，而是把密度估计转化为一个判别式任务：
- 真实样本（data） vs 噪声样本（noise）
- 训练一个二分类器来区分二者
- 通过这个判别任务间接学习 $\tilde{p}_\theta(x)$ 以及（可选）$Z_\theta$

## 核心构造：data-noise 二分类

### 两个来源：数据分布与噪声分布
设：
- 真实数据来自 $p_{\text{data}}(x)$（未知，只能采样）
- 选择一个噪声分布 $q(x)$（要求：可采样、可计算密度/概率）

训练时，对每个真实样本 $x\sim p_{\text{data}}$，采样 $k$ 个噪声样本 $\tilde{x}_1,\ldots,\tilde{x}_k \sim q$。

### 混合采样比例（先验）
在“1 个真实 + k 个噪声”的采样机制下，有：
$$
P(D=1)=\frac{1}{k+1},\quad P(D=0)=\frac{k}{k+1}
$$
其中 $D$ 表示样本来源标签：
- $D=1$：来自 data
- $D=0$：来自 noise

## 关键推导：后验 $P(D=1\mid x)$ 的闭式形式

### 贝叶斯推导
由贝叶斯公式：
$$
P(D=1\mid x)=\frac{P(x\mid D=1)P(D=1)}{P(x\mid D=1)P(D=1)+P(x\mid D=0)P(D=0)}
$$
设：
- $P(x\mid D=1)=p_\theta(x)$（模型分布，目标拟合数据）
- $P(x\mid D=0)=q(x)$

代入并化简（利用先验比例）得到 NCE 的核心后验：
$$
P(D=1\mid x)=\frac{p_\theta(x)}{p_\theta(x)+k\,q(x)}
$$
同理：
$$
P(D=0\mid x)=\frac{k\,q(x)}{p_\theta(x)+k\,q(x)}
$$

### 这个形式的直觉
#### “竞争分母”的意义
分母 $p_\theta(x)+kq(x)$ 表示“x 既可能是 data，也可能是 noise”的总解释力。

若 $p_\theta(x)$ 相对 $kq(x)$ 更大，则 $x$ 更像 data。

#### $k$ 的作用
$k$ 越大，噪声在混合样本中占比越大，模型要把正样本“拉出噪声海洋”就更难，但估计更接近 MLE（后面会解释）。

## 绕开归一化常数：把 $Z_\theta$ 吸收进参数

### 常见打分参数化
很多模型使用能量/打分形式：
$$
\tilde{p}_\theta(x)=\exp(s_\theta(x))
$$
因此：
$$
p_\theta(x)=\frac{\exp(s_\theta(x))}{Z_\theta}
$$

令 $c=\log Z_\theta$，则：
$$
p_\theta(x)=\exp(s_\theta(x)-c)
$$
此时 $c$ 可以：
- 作为可学习的标量参数（NCE 经典做法之一）
- 或在某些任务中固定/近似处理（若只关心排序而非概率刻度）

### 将其带回后验
得到可训练的判别后验：
$$
P(D=1\mid x)=\frac{\exp(s_\theta(x)-c)}{\exp(s_\theta(x)-c)+k\,q(x)}
$$
这一步的关键是：不需要显式计算 $Z_\theta$，只需学习 $c$。

## NCE 损失：二元交叉熵（logistic loss）

### 每个“1 正 + k 负”样本组的目标
对真实样本 $x\sim p_{\text{data}}$，希望判为 data：
$$
\log P(D=1\mid x)
$$
对噪声样本 $\tilde{x}\sim q$，希望判为 noise：
$$
\log P(D=0\mid \tilde{x})
$$

综合（每个正样本配 $k$ 个噪声样本）：
$$
\mathcal{L}_{\text{NCE}}(\theta,c)=
\mathbb{E}_{x\sim p_{\text{data}}}\Big[
\log P(D=1\mid x)
+
k\cdot \mathbb{E}_{\tilde{x}\sim q}\log P(D=0\mid \tilde{x})
\Big]
$$
训练时通常最小化负号：
$$
\text{loss}=-\mathcal{L}_{\text{NCE}}
$$

### 显式写出正负项
#### 正样本项
$$
\log \frac{p_\theta(x)}{p_\theta(x)+kq(x)}
$$

#### 负样本项
$$
\log \frac{kq(\tilde{x})}{p_\theta(\tilde{x})+kq(\tilde{x})}
$$

#### 只依赖哪些量
实现上只需要：
- 模型打分 $s_\theta(\cdot)$
- 噪声概率 $q(\cdot)$
- 噪声数 $k$
- 可学习常数 $c$（或其等价形式）

不需要对全空间求和或积分。

## 理论性质与直觉理解

### 与最大似然（MLE）的关系
经典结论：在一定条件下，当 $k\to\infty$ 时，NCE 的估计会趋近于最大似然估计（MLE）。

#### 直觉解释
- $k$ 越大，噪声对比越充分，判别边界越“贴近真实密度差异”
- 判别任务逼迫模型把 data 的高密度区域与 noise 彻底区分开
- 从而间接逼近“真实的生成式分布”

#### 工程权衡
- $k$ 大：更接近 MLE，但更耗算力
- $k$ 小：更快，但偏差/方差可能更大

### 噪声分布 $q(x)$ 的影响
#### $q$ 太“简单”
若噪声与数据差异很大，判别任务过于容易，模型可能学不到细粒度结构。

#### $q$ 太“接近数据”
判别更难，训练信号更“硬”，可能需要更大 $k$ 或更强模型，但学到的边界更精细。

#### 语言模型中的常见 $q$
常见选法（要求能算 $q(x)$）：
- unigram（词频分布）
- 平滑 unigram（例如 $q(w)\propto \text{freq}(w)^{3/4}$）
- 结合 alias sampling 的快速采样
