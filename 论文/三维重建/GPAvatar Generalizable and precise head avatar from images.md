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

<img src="Z:\Public\images\image-20241129165120728.png" alt="image-20241129165120728" style="zoom:50%;" />

## 实验

### 定性试验

<img src="Z:\Public\images\image-20241129165049980.png" alt="image-20241129165049980" style="zoom:50%;" />

### 定量实验

<img src="Z:\Public\images\image-20241129165012108.png" alt="image-20241129165012108" style="zoom:50%;" />