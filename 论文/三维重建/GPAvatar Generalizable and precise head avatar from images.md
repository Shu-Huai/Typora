# GPAvatar: Generalizable and precise head avatar from images

## 基本信息

- GPAvatar：从图像中生成通用且精确的头部头像
- 一种从图像或视频（连续的多张图片）中提取人物表情，并合成到另一张给定任务的面部图像上的方法
- Github：[xg-chu/GPAvatar: [ICLR 2024] Generalizable and Precise Head Avatar from Image(s)](https://github.com/xg-chu/GPAvatar)

- ICLR 2024
- arxiv：[[2401.10215] GPAvatar: Generalizable and Precise Head Avatar from Image(s)](https://arxiv.org/abs/2401.10215)
- HomePage：[GPAvatar: Generalizable and Precise Head Avatar from Image(s)](https://xg-chu.site/project_gpavatar/)

## 摘要

头部虚拟形象重建在虚拟现实、在线会议、游戏和电影行业等应用中至关重要，在计算机视觉领域引起了广泛关注。该领域的基本目标是真实地重建头部虚拟形象，并精确控制表情和姿势。现有的方法分为基于 2D 变形、基于网格和神经渲染等方法，在保持多视图一致性、整合非面部信息以及推广到新身份方面存在挑战。在本文中，我们提出了一个名为 GPAvatar 的框架，它可以在一次前向传递中从一张或几张图像中重建 3D 头部虚拟形象。这项工作的关键思想是引入一个由点云驱动的动态基于点的表情场，以精确有效地捕捉表情。此外，我们在三平面规范场中使用多三平面注意力（MTA）融合模块，以利用来自多个输入图像的信息。所提出的方法实现了真实的身份重建、精确的表情控制和多视图一致性，在自由视点渲染和新视图合成方面展示出了有前景的结果。

## 研究背景

头部头像重建在包括虚拟现实、在线会议、游戏和电影行业等领域中有着巨大的潜力，其目标在于准确地再现源头部，同时实现对表情和姿势的精确控制。目前已有的一些方法包括基于 2D 的方法、基于网格的方法和神经渲染方法。**基于 2D 的方法**通过稀疏标记将原始图像表情转换到新的表情，但缺少 3D 信息，当头部姿势发生重大变化时很难保持多视角一致性，也不能将表情与人脸身份信息分离。**基于网格的方法**使用 3D 可变形模型，但重建的头部通常缺少头发等非面部信息，表情往往不自然。**基于 NeRF 的方法**泛化性不强，难以推广到新的身份。基于上述研究和问题，本文提出一个在单次前向传播中重建源肖像的框架，实现从单张图像准确地重建头部头像并实现对表情的精确控制。

## 方法

### 方法概述

总体上包含两个分支，一个使用基于点的表达领域（Point-based Expression Field，PEF）捕获细粒度表情，另一个通过多三平面注意力（Multi Tri-planes Attention，MTA）整合来自多个输入的信息

$$I_t = R(\text{MTA}(E(I_i)), \text{PEF}(\text{FLAME}(s_i, e_t, p_t), \theta), p_{\text{cam}})$$

<img src="http://public.file.lvshuhuai.cn/images\image-20241129165120728.png" alt="image-20241129165120728" style="zoom:50%;" />

### 规范特征编码器（Canonical Feature Encoder）

使用三平面表示作为标准特征空间，因为它在合成质量和速度之间取得了良好的平衡。

编码器遵循 U-Net 结构，在上采样过程中使用 StyleGAN 结构。

### 基于点的表情场（Point-Based Expression Field, PEF）

直接使用 3DMM 点云构建基于点的表情场，避免过度处理，保留表情细节。

为 PEF 中的每个 FLAME 顶点绑定可学习的权重，这些权重在不同身份间共享，因为它们具有稳定的语义。

在 NeRF 采样过程中，通过查询最近的几个点来计算样本位置的最终特征，并使用相对位置编码提供方向和距离信息。

$$f_{\text{exp}, x} = \sum_{i=1}^{K} \frac{w_i}{\sum_{j=1}^{K} w_j} L_p(f_i, F_{\text{pos}}(p_i - x)), \quad w_i = \frac{1}{\|p_i - x\|}$$

### 多三角平面注意力（Multi Tri-planes Attention, MTA）

用于融合多个图像的三平面特征，特别适用于源图像中可能存在的遮挡或闭眼等挑战性场景。

$$P = \sum_{i=1}^{N} \frac{w_i}{\sum_{j=1}^{N} w_j} E(I_i), \quad w_i = L_q(Q) \cdot L_k(E(I_i))$$

使用可学习的三平面查询多个三平面，生成特征融合的权重。

### 体积渲染和超分辨率（Volume Rendering and Super Resolution）

给定相机的内外参数，沿着这些射线进行两遍分层采样，然后进行体积渲染以获得 2D 结果。

由于高分辨率体积渲染需要大量计算资源，因此使用轻量级超分辨率模块，先以 128x128 分辨率渲染低分辨率图像，然后通过超分辨率模块提升到高分辨率。

### 训练策略和损失函数

使用端到端的训练方法，通过从同一视频中采样原始和目标图像来构建具有相同身份但不同表情和姿态的图像对。

使用 L1 和感知损失（perceptual loss）在低分辨率和高分辨率重演图像上实现目标，同时添加基于密度的范数损失以鼓励NeRF的总密度尽可能低，从而避免伪影。

$$L_{\text{rec}} = \|I_{\text{lr}} - I_t\| + \|I_{\text{hr}} - I_t\| + \lambda_p (\|\phi(I_{\text{lr}}) - \phi(I_t)\| + \|\phi(I_{\text{hr}}) - \phi(I_t)\|)$$

$$L_{\text{overall}} = \lambda_r L_{\text{rec}} + \lambda_n L_{\text{norm}}$$

## 实验

### 定性试验

<img src="http://public.file.lvshuhuai.cn/images\image-20241129165049980.png" alt="image-20241129165049980" style="zoom:50%;" />

### 定量实验

<img src="http://public.file.lvshuhuai.cn/images\image-20241129165012108.png" alt="image-20241129165012108" style="zoom:50%;" />

## 复现

<img src="http://public.file.lvshuhuai.cn/images\PixPin_2024-12-13_01-14-01.gif" alt="PixPin_2024-12-13_01-14-01" style="zoom:50%;" />