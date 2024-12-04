# Radiative Gaussian Splatting for Efficient X-ray Novel View Synthesis

## 基本信息

用于高效 X 射线新视图合成的辐射高斯散射

一种基于 3D 高斯泼溅的 X 光扫描物体的新视角合成方法

Github：[caiyuanhao1998/X-Gaussian: "Radiative Gaussian Splatting for Efficient X-ray Novel View Synthesis" (ECCV 2024)](https://github.com/caiyuanhao1998/X-Gaussian)

ECCV 2024

arxiv：[[2403.04116] Radiative Gaussian Splatting for Efficient X-ray Novel View Synthesis](https://arxiv.org/abs/2403.04116#)

## 摘要

X 射线因穿透力比自然光强而被广泛应用于透射成像。在渲染新视图 X 射线投影时，现有的主要基于 NeRF 的方法存在训练时间长、推理速度慢的问题。本文提出了一种基于 3D 高斯溅射的 X 射线新视图合成框架，即 X-Gaussian。首先，我们受 X 射线成像的各向同性启发，重新设计了一个辐射高斯点云模型。我们的模型在学习预测 3D 点的辐射强度时排除了视角方向的影响。基于该模型，我们开发了一种可微分辐射光栅化（DRR）并采用 CUDA 实现。其次，我们定制了一个角度姿势长方体均匀初始化（ACUI）策略，该策略直接使用 X 射线扫描仪的参数来计算相机信息，然后在包围被扫描物体的长方体内均匀采样点位置。实验表明，我们的 X-Gaussian 比最先进的方法高出 6.5 dB，同时训练时间减少 15%，推理速度提高 73 倍以上。在稀疏视图 CT 重建上的应用也揭示了我们的方法的实用价值。https://github.com/caiyuanhao1998/X-Gaussian

## 研究背景

X 射线因其较强的穿透能力在医学成像中广泛应用，但对人体有害。提高 X 射线新视角合成（NVS）技术有助于减少 X 射线暴露并为医生提供更全面的成像视角，对 CT 重建等下游任务也具有重要意义。现有方法主要基于神经辐射场（NeRF），其射线追踪和体绘制方案耗时，限制了训练和推理速度。3D 高斯溅射（3DGS）在 RGB 领域取得了较好的重建质量和推理速度，但直接应用于 X 射线 NVS 存在问题，如 RGB 3DGS 中的球形谐波（SH）不适合建模 X 射线辐射强度，原始点云初始化算法（SfM）不适用于 X 射线成像。基于此，本文提出了基于高斯泼溅的方法的改进。

## 方法

### 主要贡献

- 提出了一种基于 3D 高斯溅射的新型框架 X-Gaussian
- 根据 X 射线成像的各向同性特性，设计了一种具有可微辐射光栅化的辐射高斯点云模型
- 提出了一种用于高斯点云的角度姿势长方体均匀初始化策略，并在圆锥束 X 射线扫描中进行了相机校准
- 该方法 SOTA

<img src="Z:\Public\images\image-20241204180201515.png" alt="image-20241204180201515" style="zoom:50%;" />

### 辐射高斯点云模型

一个物体可以用一组基本的高斯点云 $\mathcal G$ 来表示。$\mathcal G=\lbrace\mathcal G_i(\mu_i,\Sigma_i,\alpha_i)|i=1,2,\cdots,N_p\rbrace$，其中 $\mathcal G_i$ 表示第 $i$ 个高斯点云。其中心位置、协方差和不透明度定义为 $\mu_i\in \mathbb R^3$、$\Sigma_i\in\mathbb R^{3\times 3}$ 和 $\alpha_i\in\mathbb R$。$\Sigma_i$ 通过旋转矩阵 $R_i\in\mathbb R^3$ 和缩放矩阵  $S_i\in\mathbb R^3$ 表示：$\Sigma_i=R_iS_iS_i^TR_i^T$。$\mu_i$、$\Sigma_i$、$\alpha_i$、$R_i$ 和 $S_i$ 是可学习的参数。 

除了这些基本属性外，每个高斯点云还采用其他可学习参数来适应不同的成像场景。

在 X 光任务中，X 射线成像基于穿透物体时的衰减，衰减程度取决于各向同性的辐射密度特性，3D 点的辐射强度与视图无关。

我们的模型引入了辐射强度响应函数（RIRF）来预测 3D 点的辐射强度。

<img src="Z:\Public\images\image-20241204204428437.png" alt="image-20241204204428437" style="zoom:50%;" />

每个高斯点云学习一个特征向量 $f\in\mathbb R^{N_f}$ 来表示其固有的辐射特性，任意视角方向的三维高斯中心点的辐射强度 $i\in\mathbb R$ 由 RIRF 建模为 $i(f)=RIRF(f)-Sigmoid(\lambda\odot f)$。$\mathcal G=\lbrace\mathcal G_i(\mu_i,\Sigma_i,\alpha_i,f_i)|i=1,2,\cdots,N_p\rbrace$

### 可微分辐射光栅化

损失函数 $\mathcal L=(1-\gamma)\mathcal L_1+\gamma\mathcal L_{\mathrm{SSIM}}$

### 角度姿势长方体统一初始化

SfM 算法不适合 X 射线任务

ACUI 使用 X 射线扫描仪的参数计算外部矩阵 $M_{ext}$ 和内部矩阵 $M_{int}$

<img src="Z:\Public\images\image-20241204214334471.png" alt="image-20241204214334471" style="zoom:50%;" />

其中 $L_{SO}$ 表示 X 射线源与被扫描物体之间的距离。X 射线源的仰角设置为零，保持不变

ACUI 的下一步是初始化 3D 高斯函数的中心位置。

我们设置一个大小为 $S_1\times S_2\times S_3$（mm）的长方体，可以完全包围物体。这个长方体的中心也是物体的中心和世界坐标系的原点。我们将这个长方体用一个大小为 $M_1\times M_2\times M_3$（体素）的网格划分。然后我们在网格内以间隔 $d\in R$ 均匀采样点

## 实验

### 数据集

人体器官 CT 的公共数据集

### 定性试验

<img src="Z:\Public\images\image-20241204214842824.png" alt="image-20241204214842824" style="zoom:50%;" />

### 协方差分析

训练视图数量的增加，控制高斯点云大小的 3D 高斯的平均协方差减小。这表明 3D 高斯点云逐渐由粗变细，从而更能表示细粒度结构，例如腹部的小肿瘤。