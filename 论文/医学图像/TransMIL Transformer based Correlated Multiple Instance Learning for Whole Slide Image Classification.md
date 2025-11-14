# TransMIL: Transformer based Correlated Multiple Instance Learning for Whole Slide Image Classification

## 基本信息

- TransMIL: Transformer 基相关多实例学习用于全切片图像分类
- NeurIPS 2021
- GitHub：[szc19990412/TransMIL: TransMIL: Transformer based Correlated Multiple Instance Learning for Whole Slide Image Classification](https://github.com/szc19990412/TransMIL)
- 一种基于 Transformer 架构的 WSI 分类

## 摘要

多示例学习（MIL）是基于全切片图像（WSI）的病理诊断中解决弱监督分类问题的有力工具。然而，现有 MIL 方法通常基于独立同分布假设，因而忽略了不同实例间的相关性。针对此问题，我们提出了一种称为“相关多示例学习”的新框架，并提供了收敛性证明。基于该框架，我们设计了一种基于 Transformer 的 MIL 方法（TransMIL），同时利用形态学与空间信息。所提出的 TransMIL 能有效处理不平衡/平衡及二分类/多分类任务，兼具优异的可视化与可解释性。我们在三种不同计算病理学问题上进行了大量实验，相比现有最优方法，实现了更高性能与更快收敛速度。在 CAMELYON16 数据集上，二分类肿瘤检测的测试 AUC 最高达 93.09%；在 TCGA-NSCLC 和 TCGA-RCC 数据集上，癌症亚型分类的 AUC 分别达到 96.03% 和 98.82%。代码实现详见：https://github.com/szc19990412/TransMIL。

## 研究背景

- WSI（全幅切片）是千兆像素级图像，病理弱监督分类常用 **MIL**（袋级有标签、实例级无标签）。但许多深度MIL方法默认袋内实例 **i.i.d.**，忽略区域之间的**上下文与相关性**。病理医生做决策时会综合邻域上下文与跨区域相关，这与 i.i.d. 假设相悖。
- Transformer 的**自注意力**天然刻画序列各 token 间的**成对相关**，很适合建模“实例相关”；但标准注意力是 $O(n^2)$，难以直接处理 WSI 动辄上万 patch 的长序列。

## 主要方法

### 相关多实例学习

#### 逼近推论（Inference）
给定关于 Hausdorff 距离连续的集合函数 $S: \mathcal{X}\to \mathbb{R}$，对任意 $\varepsilon>0$，存在函数 $g,h$ 与可逆映射 $P$，使得
$$
\bigl|S(X)-g\!\left(\,P_{X\in\mathcal X}\{\,f(x)+h(x):x\in X\,\}\right)\bigr|<\varepsilon
$$


这说明 $S(X)$ 可被形如 $g(P\{\!f(x)+h(x)\!\})$ 的结构任意逼近（把形态信息 $f$ 与空间/相关信息 $h$ 分拆）。

#### 信息熵不等式（Theorem 2）

若袋内实例为随机变量 $\Theta_1,\dots,\Theta_n$，相关假设下的信息熵为 $H(\Theta_1,\dots,\Theta_n)$，i.i.d. 假设下为 $\sum_{t=1}^n H(\Theta_t)$，则
$$
H(\Theta_1,\dots,\Theta_n)=\sum_{t=2}^{n} H(\Theta_t\mid \Theta_1,\dots,\Theta_{t-1})+H(\Theta_1)\le \sum_{t=1}^n H(\Theta_t).
$$
相关假设可能降低不确定性并为 MIL 问题带来更多有用信息。

<img src="Z:\Public\images\image-20251113154649245.png" alt="image-20251113154649245" style="zoom:50%;" />

#### 三步算法

1. 形态与空间信息抽取并相加：
$$
  X_f\leftarrow f(X_i),\quad X_h\leftarrow h(X_i),\quad X_{fh}\leftarrow X_f+X_h\in\mathbb{R}^{n\times d}.
$$

2. 用**Pooling 矩阵**聚合（允许**非对角项**表示实例间相关）：
$$
  X_P\leftarrow P\,X_{fh},\quad P\in\mathbb{R}^{n\times n}.
$$

3. 映射得到袋级预测：
$$
  \hat Y_i \leftarrow g(X_P).
$$

<img src="Z:\Public\images\image-20251113154839416.png" alt="image-20251113154839416" style="zoom:50%;" />

### 如何将 Transformer 应用于相关多实例学习

#### 基于 Transformer 的多示例学习

论文把任务形式化为两段映射：
$$
X \;\xrightarrow{\;\;T\;\;}\; Y,\quad \text{其中 } X \text{为袋空间，}T \text{为 Transformer 空间。}
$$
自注意力承担“非对角 Pooling 矩阵 $P$”以聚合信息，位置编码承担 $h$（注入空间/顺序关系）。

### 用于弱监督 WSI 分类的 TransMIL

<img src="Z:\Public\images\image-20251113154933048.png" alt="image-20251113154933048" style="zoom:50%;" />

#### 使用 TPT 的长实例序列建模

<img src="Z:\Public\images\image-20251113155826437.png" alt="image-20251113155826437" style="zoom:50%;" />

标准自注意力的时间/显存复杂度为 $O(n^2)$。TPT 采用 Nyström 近似，将 **row-wise softmax** 的注意力写成：
$$
\hat S
=\operatorname{softmax}\!\left(\frac{Q\tilde K^\top}{\sqrt{d_q}}\right)
\Bigl(\operatorname{softmax}\!\left(\frac{\tilde Q\tilde K^\top}{\sqrt{d_q}}\right)\Bigr)^{+}
\operatorname{softmax}\!\left(\frac{\tilde Q K^\top}{\sqrt{d_q}}\right),
$$
其中 $\tilde Q,\tilde K$ 为从长度 $n$ 序列中选取的 $m$ 个 **landmarks**；$(\cdot)^+$ 表示 **Moore–Penrose** 伪逆。复杂度由 $O(n^2)$ 降至近似 $O(n)$。

#### 使用 PPEG 的位置编码

<img src="Z:\Public\images\image-20251113160951703.png" alt="image-20251113160951703" style="zoom:50%;" />

**动机**：WSI 的 token 数随组织面积变化，需能适配**可变长度**并注入**空间上下文**。

**PPEG** 的流程

1. **分离**：将序列分成 patch tokens $H_f$ 与 class token $H_c$：
$$
  H_f,H_c\leftarrow \mathrm{Split}(H_S^{(\ell)}),\quad H_f\in\mathbb{R}^{N\times d},\ H_c\in\mathbb{R}^{1\times d}.
$$

2. **空间还原**：把 $H_f$ 还原到 2D：
$$
  H^S_f\leftarrow \mathrm{Restore}(H_f),\quad H^S_f\in\mathbb{R}^{\sqrt N\times \sqrt N\times d}.
$$

3. **组卷积**：在同一层使用不同核大小（论文图例为 3/5/7，并带零填充）做组卷积，编码不同粒度位置与上下文；随后**融合**多尺度特征。

4. **摊平并拼接**：把增强后的 patch tokens 摊平成序列并与 $H_c$ 拼接，得到 $H_S^{P}\in\mathbb{R}^{(N+1)\times d}$。

## 实验

### 数据集

- CAMELYON16
- TCGA-NSCLC
- TCGA-RCC

#### CAMELYON16

CAMELYON16 是一个用于乳腺癌转移检测的公开数据集，包含 270 个训练集和 130 个测试集。

经过预处理后，共获得约 350 万个 20 倍放大的切片，平均每个样本袋约含 8800 个切片。

### 结果

<img src="Z:\Public\images\image-20251113161229758.png" alt="image-20251113161229758" style="zoom:50%;" />

