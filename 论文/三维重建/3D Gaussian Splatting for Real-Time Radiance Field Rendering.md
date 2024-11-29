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

## 方法

### 输入

一组静态场景的图像以及由 SfM 方法校准的相机

SfM 方法会产生稀疏点云

### 方法概述

根据这些点云数据创建一组 3D 高斯团，然后通过一系列优化步骤创建辐射场表示，并使用基于图块的光栅化器来提高效率

<img src="http://public.file.lvshuhuai.cn/images\image-20241128192248913.png" alt="image-20241128192248913" style="zoom:50%;" />

### 可微分三维高斯溅射

#### 点的颜色

$$
C=\sum_{i=1}^{N} T_{i}\left(1-\exp\left(-\sigma_{i}\delta_{i}\right)\right) c_{i} \text{ with } T_{i}=\exp\left(-\sum_{j=1}^{i-1}\sigma_{j}\delta_{j}\right)
$$

其中密度 $\sigma$、透射率 $T$ 和颜色 $c$ 的样本沿射线以 $\delta_i$ 为间隔进行采样。

#### 高斯表示

$$G(x)=e^{-\frac{1}{2}(x)^{T}\Sigma^{-1}(x)}$$

#### 将 3D 投影到 2D

相机坐标中的协方差矩阵 $\Sigma'=JW\Sigma W^TJ^T$

其中 $W$ 是一个观察变换， $J$​ 是射影变换的仿射近似的雅可比矩阵

#### 高斯团的缩放和旋转

如果使用梯度下降的方法更新协方差矩阵，则会遇到问题：协方差矩阵只有当是半正定的时候才具有物理意义，难以通过梯度下降算法限制得到的协方差矩阵，得到有意义的结果

因此，我们使用缩放和旋转的方法

$$\Sigma=RSS^TR^T$$

其中，$S$ 为缩放矩阵，$R$ 为旋转矩阵

#### 参数梯度的推导

同时，为了避免训练期间自动微分带来的大量开销，我们明确推导所有参数的梯度，附录中给出了精确导数计算。

### 三维高斯自适应密度控制优化

优化目标：高斯团的位置 $p$，透明度 $\alpha$，协方差 $\Sigma$，颜色 $c$​

参数的优化与控制高斯函数密度的步骤交错进行

#### 优化

损失函数：$\mathcal L=(1-\lambda)\mathcal L_1+\lambda\mathcal L_{\mathrm {D-SSIM}}$

#### 高斯自适应控制

从 SfM 中的初始稀疏点集开始，然后自适应地控制高斯函数的数量及其在单位体积 1 上的密度，从而使我们从初始稀疏的高斯函数集转变为更能代表场景且具有正确参数的更密集的函数集。

在优化预热后，每 100 次迭代进行一次密集化，并移除任何本质上透明的高斯函数，即 $\alpha$ 小于阈值 $\epsilon_\alpha$​。

<img src="http://public.file.lvshuhuai.cn/images\image-20241129142816462.png" alt="image-20241129142816462" style="zoom:50%;" />

- 对于重建不足的区域的小高斯函数，克隆，创建大小相同的副本，然后沿位置梯度方向移动
- 对于过度重建的区域，需要将大高斯函数分裂为较小的高斯，用两个新的高斯替换这些高斯，将其按比例因子 $\phi=1.6$ 缩小规模，比例因子从实验中得到。

小问题：高斯的密度可能会不合理地增加，解决方案是每 $N=3000$ 将 $\alpha$​ 值设置为接近零

### 高斯快速可微分光栅化器

基于图块的高斯图块光栅化器

将屏幕分割成 16×16 个图块，根据**只保留与视锥体相交的置信区间为 99% 的高斯**，剔除高斯团

然后根据每个高斯重叠的图块数量对其进行实例化，并为每个实例分配一个结合了视空间深度和图块 ID 的键

使用单个快速 GPU 基数排序，根据这些键对高斯进行排序

## 实验

### 数据集

- Mip-NeRF 360 数据集
- Deep Blending 数据集
- Tanks&Temples 数据集

### 软硬件

- 单张 RTX A6000
- PyTorch

### 定性实验

<img src="http://public.file.lvshuhuai.cn/images\image-20241129145958387.png" alt="image-20241129145958387" style="zoom:50%;" />

### 定量实验

<img src="http://public.file.lvshuhuai.cn/images\image-20241129150204239.png" alt="image-20241129150204239" style="zoom:50%;" />
