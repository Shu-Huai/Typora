# Gaussian Splatting: 3D Reconstruction and Novel View Synthesis: A Review

## 基本信息

高斯溅射：3D重建与新视角合成综述

## 摘要

基于图像的3D重建是一项具有挑战性的任务，涉及从一组输入图像中推断出对象或场景的3D形状。基于学习的方法因其直接估计3D形状的能力而备受关注。这篇评论论文重点介绍3D重建的最新技术，包括生成新的、看不见的视图。概述了高斯Splatting方法的最新发展，涵盖了输入类型、模型结构、输出表示和训练策略。还讨论了尚未解决的挑战和未来方向。鉴于该领域的快速发展和增强3D重建方法的众多机会，全面研究算法似乎至关重要。因此，本研究全面概述了高斯Splatting的最新进展。

## **3D数据表示**

### 传统方法

![image-20241010104347732](http://public.file.lvshuhuai.cn/images\image-20241010104347732.png)

#### 点云

- 点云是一种由一系列在三维空间中离散点组成的数据结构。每个点包含其在三维空间中的坐标（x, y, z），通常由三维扫描得到。
- 点云提供了物体或场景的几何形状的直接表示，但不包含任何关于点之间如何连接或相互关系的信息。

#### 网格

- 网格是通过连接顶点（vertices）形成多边形（如三角形或四边形）来构建的3D数据表示。顶点集合定义了物体的表面，并且每个顶点包含其三维坐标。
- 网格提供了丰富的几何细节，并且可以编码拓扑信息。它非常适合用于3D建模和渲染，但在处理大规模数据时可能会变得复杂。

#### 体素

- 体素是三维空间中的像素，是一种用于表示体积数据的立方体元素。体素模型将三维空间划分为网格，并为每个立方体单元分配属性，如颜色和密度。
- 体素表示提供了一种在三维空间内进行精确表示和操作的方法，尤其适合于医学成像和体积渲染。

### 新方法

![image-20241010104510449](http://public.file.lvshuhuai.cn/images\image-20241010104510449.png)

#### 神经网络/多层感知器 (MLP)

- NeRF（Neural Radiance Fields）是一种基于深度学习的3D表示方法，它使用多层感知器（MLP）来学习和表示场景的连续体积。NeRF模型将3D空间中的位置映射到颜色和密度值。
- NeRF能够生成高质量的新视角图像，并且能够处理复杂的光照和遮挡。但是，它需要大量的图像数据来训练，并且计算成本较高。

#### 高斯溅射

- 高斯溅射是一种新颖的3D表示方法，它使用一组3D高斯函数（或称为splats）来表示场景。每个高斯splat包含位置、尺度、颜色和不透明度等参数，这些参数共同定义了splat在三维空间中的分布。
- 高斯溅射提供了一种灵活且高效的3D场景表示方法，适合于实时渲染和动态场景的重建。它允许通过调整高斯参数来控制渲染的细节和质量。

## 数据集

- COLMAP
- Mip-NeRF360
- Tanks&Temples
- Deep Blending

## 高斯泼溅

高斯溅射使用大量3D高斯或粒子描绘3D场景，每个粒子都配备位置、方向、比例、不透明度和颜色信息。

### 步骤

1. 从运动构建结构：SFM方法，使用COLMAP库从图像中创建点云。
2. 换为高斯图块：将每个点转换为高斯图块可实现栅格化。
3. 训练：采用了类似于神经网络的随机梯度下降法。 
   1. 使用可微分高斯栅格化将图像中的高斯栅格化
   2. 根据栅格和实际地形图像之间的差异计算损失
   3. 根据产生的损失修改高斯参数。
4. 可微分高斯栅格化：每个2D高斯都需要从相机的视点投影可微分高斯光栅化，根据深度进行排序，然后对每个像素进行前后组合重复。

### 结构

![image-20241010105558555](http://public.file.lvshuhuai.cn/images\image-20241010105558555.png)

### 数学表示

#### 3D高斯函数

由其均值$$\mu\in\mathbb{R}^3$$，协方差矩阵$$\Sigma\in\mathbb{R}^{3\times 3},$$，颜色$$c\in\mathbb{R}^3$$，和不透明度$$o\in\mathbb{R}$$参数化。

#### 投影

- 将3D高斯函数的均值$$\mu$$通过透视投影转换到摄像机坐标系中，得到$$t'\in\mathbb{R}^4$$。
- 将$$t'$$转换到像素坐标系中，得到$$\mu'\in\mathbb{R}^2$$。
- 为了近似地计算高斯函数的协方差$$\Sigma$$在像素空间中的转换，使用泰勒级数的一阶展开。

#### 深度合成

$$C_i = \sum_{n} c_n \alpha_n
\alpha_n = o_n \exp\left(-\frac{1}{2} \Delta_n^T \Sigma'^{-1} \Delta_n\right)$$

## 质量评估

### 峰值信噪比PSNR

$$\text{PSNR}(I) = 10 \cdot \log_{10} \left( \frac{\text{MAX}(I)^2}{\text{MSE}(I)} \right)$$

### 结构相似性指数度量SSIM

$$\text{SSIM}(x, y) = \frac{(2\mu_x \mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}$$

### 学习感知图像补丁相似性

$$\text{LPIPS}(x, y) = \sqrt{\sum_{l} \left\| f_l(x) - f_l(y) \right\|^2_2}$$

## 功能进展

- 动态和变形建模
- 扩散模型和文本到3D生成
- 优化和速度提升
- 渲染和着色方法

## 应用

- 化身
- 同步定位和绘图
- 网格提取与物理
- 可编辑性
