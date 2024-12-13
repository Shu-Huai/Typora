# GaussianAvatars: Photorealistic Head Avatars with Rigged 3D Gaussians

## 基本信息

GaussianAvatars：带有 3D 高斯模型的逼真头部头像

一种能够实现新视角合成、表情和姿态控制的基于 3D 高斯的头部重建方法

CVPR 2024

arxiv：[[2312.02069] GaussianAvatars: Photorealistic Head Avatars with Rigged 3D Gaussians](https://arxiv.org/abs/2312.02069)

HomePage：[GaussianAvatars: Photorealistic Head Avatars with Rigged 3D Gaussians | Shenhan Qian](https://shenhanqian.github.io/gaussian-avatars)

Github：[ShenhanQian/GaussianAvatars: [CVPR 2024 Highlight] The official repo for "GaussianAvatars: Photorealistic Head Avatars with Rigged 3D Gaussians"](https://github.com/ShenhanQian/GaussianAvatars)

Bibtex：

```tex
@inproceedings{qian2024gaussianavatars,
  title={Gaussianavatars: Photorealistic head avatars with rigged 3d gaussians},
  author={Qian, Shenhan and Kirschstein, Tobias and Schoneveld, Liam and Davoli, Davide and Giebenhain, Simon and Nie{\ss}ner, Matthias},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={20299--20309},
  year={2024}
}
```

## 摘要

我们引入了 GaussianAvatars，这是一种创建照片级逼真头部头像的新方法，这些头像在表情、姿势和视点方面完全可控。其核心思想是基于 3D 高斯条纹的动态 3D 表示，这些条纹被绑定到参数化可变形人脸模型上。这种组合有助于实现照片级逼真的渲染，同时允许通过底层参数模型进行精确的动画控制，例如，通过从驾驶序列进行表情传输或手动更改可变形模型参数。我们通过三角形的局部坐标系参数化每个条纹，并优化显式位移偏移，以获得更精确的几何表示。在头像重建过程中，我们以端到端的方式联合优化可变形模型参数和高斯条纹参数。我们在几个具有挑战性的场景中展示了我们照片级逼真头像的动画能力。例如，我们展示了驾驶视频中的重演，其中我们的方法比现有方法表现得更好。

## 研究背景

创建动态 3D 的人脸头像在计算机视觉和图形学领域受到广泛关注，从任意视角渲染照片级的动态头像对于虚拟现实、游戏制作等许多应用来说非常关键。主要任务是重建一个能够同时捕获外观、几何和动态的三维表征。但该任务约束不足，使得新视角合成的真实性和表情的可控性受到限制，同时，皱纹和头发等面部细节在人类的视觉上影响显著但难以捕捉。基于 NeRF 的方法缺乏控制性，因此难以对姿势和表情进行控制。基于高斯泼溅的方法质量更高，但不支持对重建结果进行动态化。基于此，本文提出一种利用 3D Gaussian 泼溅动态表示人脸头部的方法，基于 FLAME 网格，对每个三角形中心初始化一个高斯函数，使其可以随着父三角形进行平移、旋转和平移，并引入绑定继承策略，这个主要用于对高斯团的密度控制。

## 方法

<img src="http://public.file.lvshuhuai.cn/images\image-20241213001816306.png" alt="image-20241213001816306" style="zoom:50%;" />

### 3D 高斯链接

方法的关键是如何在 FLAME 网格和三维高斯上建立连接。

首先，将网格的每个三角形与 3D 高斯配对，并让 3D 高斯随三角形随时间步骤移动。这里的时间步骤是说输入视频的时间片。

给定三角形的顶点和边，我们将顶点的平均位置 $T$ 取为局部空间的原点.

然后，将其中一条边的方向向量、三角形的法向量及其叉积连接为列向量，以形成旋转矩阵 $R$，该矩阵描述三角形在全局空间中的方向。

通过其中一条边及其垂直线的平均长度计算标量 $k$ 来描述三角形的缩放。

将高斯函数的 $\mu$、$r$ 和 $s$ 定义在三角形的局部空间中，并在渲染时通过三角形的参数转换为全局空间

$$r'=Rr$$

$$\mu'=kR\mu+T$$

$$s'=ks$$

加入缩放 $k$ 的原因是，对不同的三角形大小实现自适应的学习率。

### 绑定继承

自适应密度控制策略根据视空间位置梯度和每个高斯的不透明度添加和删除高斯团。

对于每个具有较大视图空间位置梯度的 3D 高斯，如果其较大，我们将其拆分为两个较小的高斯，如果其较小，我们将其克隆。我们在局部空间中进行此操作，并确保新创建的高斯接近旧的高斯。

对每一个高斯，定义一个绑定到其父三角形的索引。

使用修建操作，定期重置所有不透明度接近零的高斯，并删除不透明度低于阈值的点，以有效抑制伪影。

为了防止出现被遮挡区域的渲染错误，确保每个三角形始终至少有一个高斯团。

### 优化与正则化

使用 $\mathcal L_1$ 和 D-SSIM 作为图像渲染的损失函数，$\mathcal L_{\mathrm{rgb}}=(1-\lambda)\mathcal L_1+\lambda\mathcal L_{\mathrm{D-SSIM}}$。

为了优化高斯和三角形之间的对齐，使用 $\mathcal L_{\mathrm{position}}=|\max{(\mu,\epsilon_{\mathrm{position}})}|_2$，目标是最小化当前位置向量与目标位置向量之间欧氏距离的平方根。

同时，$\mathcal L_{\mathrm{scaling}}=|\max{(s,\epsilon_{\mathrm{scaling}})}|_2$ 控制缩放的优化。

因此，损失函数为 $\mathcal L = \mathcal L_{\mathrm{rgb}} + \lambda_{\text{position}}\mathcal L_{\text{position}} + \lambda_{\text{scaling}}\mathcal L_{\text{scaling}}$

## 实验

### 评估方式

1. 新视角合成：来自训练人物，固定表情和姿势，生成出新的视角
2. 自我重演：来自训练人物，生成出新的表情和姿势
3. 跨身份重演：来自另一个人物的表情和姿势作为驱动，生成目标对象的相同表情

### 数据集

NeRSemble

### 定性实验

<img src="http://public.file.lvshuhuai.cn/images\image-20241213005603189.png" alt="image-20241213005603189" style="zoom:50%;" />

### 定量实验

<img src="http://public.file.lvshuhuai.cn/images\image-20241213005626407.png" alt="image-20241213005626407" style="zoom: 50%;" />

## 复现

![PixPin_2024-12-12_23-22-09](http://public.file.lvshuhuai.cn/images\PixPin_2024-12-12_23-22-09.gif)

<img src="http://public.file.lvshuhuai.cn/images\image-20241213005749241.png" alt="image-20241213005749241" style="zoom:50%;" />
