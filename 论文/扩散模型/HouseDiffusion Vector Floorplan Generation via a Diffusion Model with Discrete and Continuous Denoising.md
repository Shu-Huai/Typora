# HouseDiffusion: Vector Floorplan Generation via a Diffusion Model with Discrete and Continuous Denoising

## 基本信息

基于离散和连续去噪扩散模型的矢量平面图生成

CVPR 2023

项目主页：[HouseDiffusion (aminshabani.github.io)](https://aminshabani.github.io/housediffusion/)

项目代码：[aminshabani/house_diffusion: The implementation of "HouseDiffusion: Vector Floorplan Generation via a Diffusion Model with Discrete and Continuous Denoising", https://arxiv.org/abs/2211.13287 (github.com)](https://github.com/aminshabani/house_diffusion)

arxiv：[[2211.13287\] HouseDiffusion: Vector Floorplan Generation via a Diffusion Model with Discrete and Continuous Denoising (arxiv.org)](https://arxiv.org/abs/2211.13287)

## 研究背景

自动化房屋平面图生成在过去几年取得了巨大进步，最新技术已经帮助建筑师快速探索可能的设计空间。但现有的平面图生成模型存在与输入约束不兼容、缺乏变化或看起来不像平面图的问题。现有模型通常使用光栅几何分析，通过卷积表示房间，这种方式擅长局部形状细化，但缺乏全局推理能力，并且需要复杂的后处理才能矢量化。

基于此，论文提出了一种基于扩散模型的新方法。

## 核心方法

论文提出了HouseDiffusion，该方法通过两个推理目标去噪2D坐标。首先，将单步噪声作为连续量，以精确地逆转连续的前向过程；然后，将最终的2D坐标作为离散量，建立几何关系，如平行性、正交性和角共享。这种结合使得HouseDiffusion能够在生成过程中同时考虑局部细节和全局结构，生成既精确又符合建筑规范的平面图。

HouseDiffusion的架构基于Transformer网络，该网络能够处理复杂的关系，并根据输入的气泡图约束动态调整注意力掩码。这种基于注意力的机制允许模型在生成过程中同时考虑局部和全局的几何关系，从而提高平面图的质量和多样性。

在特征嵌入方面，HouseDiffusion采用了一种增强的表示方法，通过对墙角坐标的周围点进行采样和增强，来帮助模型更好地理解和生成精确的几何结构。此外，模型在训练过程中使用了一种简单的L2范数回归损失函数，对连续和离散的预测都给予相同的权重，从而实现了端到端的训练。

## 实验

论文使用基于GuidedDiffusion的公共实现，在RPLAN数据集中挑选的60,000个矢量平面图上训练，并与House-GAN++和HouseGAN等其他图约束平面图生成模型进行了比较。

定性试验和定量实验表明，论文提出的方法在多样性、兼容性和现实性等指标上显著优于现有技术，并且能够直接生成非曼哈顿结构并精确控制每个房间的角落数。