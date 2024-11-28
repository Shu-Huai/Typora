# 3D Gaussian Splatting for Real-Time Radiance Field Rendering

## 基本信息

用于实时辐射场渲染的 3D 高斯散射

一种基于 3D 高斯体进行场景重建的方案

Github：[graphdeco-inria/gaussian-splatting: Original reference implementation of "3D Gaussian Splatting for Real-Time Radiance Field Rendering"](https://github.com/graphdeco-inria/gaussian-splatting)

HomePage：[3D Gaussian Splatting for Real-Time Radiance Field Rendering](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)

Siggraph 2023

arxix：[[2308.04079] 3D Gaussian Splatting for Real-Time Radiance Field Rendering](https://arxiv.org/abs/2308.04079)

## 摘要

辐射场方法最近彻底改变了用多张照片或视频捕捉的场景的新视图合成。然而，实现高视觉质量仍然需要训练和渲染成本高昂的神经网络，而最近更快的方法不可避免地要以速度换取质量。对于无界完整场景（而非孤立物体）和 1080p 分辨率渲染，目前没有任何方法能够实现实时显示速率。 我们引入了三个关键元素，使我们能够在保持有竞争力的训练时间的同时实现最先进的视觉质量，更重要的是允许以 1080p 分辨率实现高质量实时（≥ 30 fps）新视图合成。首先，从相机校准期间产生的稀疏点开始，我们用 3D 高斯表示场景，这些高斯保留了连续体积辐射场的理想属性以进行场景优化，同时避免在空白空间进行不必要的计算；其次，我们对 3D 高斯进行交错优化/密度控制，特别是优化各向异性协方差以实现场景的准确表示；第三，我们开发了一种快速的可视性感知渲染算法，该算法支持各向异性铺展，既能加速训练，又能实现实时渲染。我们在多个已建立的数据集上展示了最先进的视觉质量和实时渲染。

## 研究背景

用多张照片或视频捕捉的场景的新视图合成任务最近受到很多关注。传统方法将输入图像重新投影并混合到新视角相机中，并使用几何图形来指导这种重新投影。这些方法在许多情况下产生了出色的结果，但通常无法从未重建的区域或“过度重建”中完全恢复。基于辐射场的方法建立在连续表示的基础上，能够实现高质量的 3D 重建任务，但渲染所需的随机采样成本高昂，造成训练和推理的时间较长，并且可能导致噪声。一些最近的方法实现了快速训练，但质量较低。

最近的神经辐射场 (NeRF) 方法建立在连续场景表示的基础上，通常使用体积光线行进优化多层感知器 (MLP)，以实现捕获场景的全新视图合成。同样，迄今为止最有效的辐射场解决方案建立在连续表示的基础上，通过插值存储在例如体素 [Fridovich-Keil and Yu et al 2022] 或哈希 [Müller et al 2022] 网格或点 [Xu et al 2022] 中的值。 虽然这些方法的连续性有助于优化，但渲染所需的随机采样成本高昂，并且可能导致噪声。我们引入了一种结合两全其美的新方法：我们的 3D 高斯表示允许以最先进 (SOTA) 的视觉质量和具有竞争力的训练时间进行优化，而我们基于图块的 splatting 解决方案可确保在几个之前发布的数据集上以 SOTA 质量实时渲染 1080p 分辨率 [Barron et al 2022; Hedman et al 2018; Knapitsch et al 2017]（见图 1）。 我们的目标是允许实时渲染使用多张照片捕获的场景，并以与以前最有效的典型真实场景方法一样快的优化时间创建表示。最近的方法实现了快速训练但难以达到当前 SOTA NeRF 方法所获得的视觉质量，该方法需要长达 48 小时的训练时间。速度快但质量较低的辐射场方法可以根据场景实现交互式渲染时间（每秒 10-15 帧），但无法实现高分辨率的实时渲染。

## 方法

### 输入

一组静态场景的图像以及由 SfM 方法校准的相机

SfM 方法会产生稀疏点云

### 方法概述

根据这些点云数据创建一组 3D 高斯团，然后通过一系列优化步骤创建辐射场表示，并使用基于图块的光栅化器来提高效率

<img src="http://public.file.lvshuhuai.cn/images\image-20241128192248913.png" alt="image-20241128192248913" style="zoom:50%;" />



## 实验

