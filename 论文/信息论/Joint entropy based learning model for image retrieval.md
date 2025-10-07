# Joint entropy based learning model for image retrieval

## 基本信息

基于联合熵的图像检索学习模型

一种图像检索的方法

ScienceDirect：[Joint entropy based learning model for image retrieval - ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1047320318301469)

## 摘要

作为计算机视觉的经典技术之一，图像检索可以从成千上万的图像中有效地检索出目标图像。此外，随着深度学习的快速发展，再分类的质量明显提高。然而，在正常情况下，高质量的检索是由大量的学习实例支持的。大量的学习实例不仅在选择过程中需要大量的人力资源，而且在计算过程中需要大量的计算资源。更重要的是，对于一些特殊的类别，很难获得大量的学习实例。针对上述问题，我们提出了一种基于联合熵的学习模型，该模型可以通过优化学习实例的分布来减少学习实例的数量。首先，使用改进的分水岭分割方法预先选择学习实例。然后，使用联合熵模型来减少双重、无用甚至错误实例存在的可能性。在此基础上，建立了一个使用大量图像的数据库。基于该数据库的充分实验表明，我们的模型不仅可以减少学习实例的数量，而且可以保持检索的准确性。

## 研究背景

图像检索是计算机视觉领域的一项经典技术，它允许用户从大型数字图像数据库中检索目标图像。传统的基于内容的图像检索（CBIR）方法依赖于图像的低级特征，如颜色、形状和纹理。随着深度学习的发展，图像检索的质量得到了显著提高，但这些高质量的检索结果通常依赖于大量的学习实例。获取大量学习实例不仅需要大量的人力资源，而且在计算过程中也需要大量的计算资源。对于某些特殊类别，获取大量学习实例尤其困难。因此，如何在减少学习实例数量的同时保持检索的准确性，成为了一个有意义的问题。

## 方法

### 概述

- 使用改进的分水岭分割方法对其进行预选择
- 在预选择的基础上，使用联合熵来优化学习实例的分布

<img src="http://public.file.lvshuhuai.cn/images\image-20241129160644123.png" alt="image-20241129160644123" style="zoom:50%;" />

### 预选步骤

使用改进的分水岭分割方法对图像进行预处理，以选择有效的学习实例。

#### WLS 滤波器

通过 WLS（加权最小二乘）滤波器进行图像的边缘保持分解，以增强图像的边缘特征。

$$\sum_{i} \left( u(x_i) - g(x_i) \right)^2 + k \left( \frac{\partial u}{\partial x}(x_i) \right)^2 + \left( \frac{\partial u}{\partial y}(x_i) \right)^2 = V(i)$$​

其中：

- $u(x_i)$ 是滤波后的图像。
- $g(x_i)$ 是原始图像。

- $k$ 是平衡两项的权重参数。
- $V(i)$ 是一个用于调整平滑度的函数。

#### 分水岭分割

利用分水岭分割技术进一步处理滤波后的图像，以评估目标图像是否适合作为学习实例

$$g(x, y) = - \text{grad}(f(x, y))$$

其中

- $\text{grad}$ 表示梯度算子。
- $f(x,y)$ 是原始图像。
- $g(x,y)$ 是经过分水岭分割处理后的图像。

### 联合熵模型的构建

#### 联合熵

利用联合熵来评估学习实例分布的有效性，通过计算学习实例之间的联合熵来优化实例的选择。

采用一阶熵（First Order Entropy）作为近似，计算每个学习实例的熵值，忽略它们之间的上下文语义关系。

引入二阶近似（Bethe Entropy Approximation），考虑不同学习实例之间的上下文语义关系，以更准确地计算联合熵。

联合熵的计算：$H(I) = -\sum_{n_1, n_2, \ldots, n_N} p(n_1, n_2, \ldots, n_N | I) \log(p(n_1, n_2, \ldots, n_N | I))$

一阶熵的近似：$H_{\text{fo}}(I) = -\sum_{j \in I} \sum_{n_j} p(n_j | I) \log(p(n_j | I))$

Bethe 熵近似：$H_{\text{SO}}(I) = -\sum_{j, k \in I} \left[ p(n_j, n_k | I) \log(p(n_j, n_k | I)) - (1 - \delta_{j, k}) p(n_j | I) \log(p(n_j | I)) \right]$

#### 计算上下文语义关系

使用 SIFT（尺度不变特征变换）描述符和 GIST（场景的几何不变特征）描述符来获取学习实例之间的相似性。

<img src="http://public.file.lvshuhuai.cn/images\image-20241129161611483.png" alt="image-20241129161611483" style="zoom:50%;" />

通过计算基于 GIST 描述符的欧几里得距离和基于 SIFT 描述符的直方图相似度，来定义联合语义概率。

基于 GIST 描述符的相似性：$p_{\text{GIST}}(n_j, n_k) = \exp\left(-\sum_{i=1}^{m} (G_j(i) - G_k(i))^2\right)$

基于SIFT描述符的相似性：$p_{\text{SIFT}}(n_j, n_k) = \sum_{i=1}^{H_1(i)} \sum_{j=1}^{H_2(j)} \left(1 - \frac{H_1(i) \cdot H_2(j)}{H_1 \cdot H_2}\right)^{-1}$

## 实验

论文中进行了一系列的实验来验证所提出模型的有效性。实验使用了来自多个数据库的 198175 张图像，其中包括 112762 张训练图像和 85413 张测试图像。实验结果通过精确率-召回率曲线（Precision-Recall curve）、平均精度值（AP 值）和曲线下面积（AUC 值）来评估。实验结果表明，与基线方法相比，所提出的模型在减少学习实例数量的同时，能够保持甚至提高检索的准确性。此外，当学习实例数量不足时，该模型相比其他基线方法具有明显优势。

<img src="http://public.file.lvshuhuai.cn/images\image-20241129161727585.png" alt="image-20241129161727585" style="zoom:50%;" />

<img src="http://public.file.lvshuhuai.cn/images\image-20241129161747536.png" alt="image-20241129161747536" style="zoom:50%;" />