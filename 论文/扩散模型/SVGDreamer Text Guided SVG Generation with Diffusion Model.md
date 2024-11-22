# SVGDreamer: Text Guided SVG Generation with Diffusion Model

## 基本信息

SVGDreamer：具有扩散模型的文本引导 SVG 生成

一种用于文本到SVG生成的扩散模型方法

CVPR 2024

源码：[ximinng/SVGDreamer: CVPR 2024 Official implementation for "SVGDreamer: Text Guided SVG Generation with Diffusion Model" https://arxiv.org/abs/2312.16476 (github.com)](https://github.com/ximinng/SVGDreamer)

项目主页：[SVGDreamer: Text Guided SVG Generation with Diffusion Model (ximinng.github.io)](https://ximinng.github.io/SVGDreamer-project/)

## 研究背景

可缩放矢量图形（SVG）因其可编辑性、文件小，很适合视觉设计应用。文本引导的 SVG 图像生成在设计领域展现出良好的前景。然而，现阶段的文本到 SVG 生成模型可能存在对象纠缠、可编辑性差等问题，也存在着图像过饱和、过平滑等问题。基于此，论文提出了一种名为 SVGDreamer 的新模型，对预训练的扩散模型进行优化，生成高质量的 SVG。

## 核心方法

如图所示，论文提出的方法由语义驱动的图像矢量化（SIVE）和通过VPSD优化的SVG合成两部分组成。

![image-20241010230249882](http://public.file.lvshuhuai.cn/images\image-20241010230249882.png)

### 语义驱动的图像矢量化

SIVE 分为两个阶段。

在原始初始化阶段，论文根据文本提示中不同对象对应的交叉注意力图初始化 $O$ 组对象级控制点，并将它们表示为前景 $\mathcal M^i_{FG}$，其中$i$表示文本提示中的第 $i$ 个 token。相应地，其余的将被视为背景。然后，使用 softmax 对注意力图进行归一化，并将其视为分布图，以对每个贝塞尔曲线的控制点采样，以定义初始路径集。

在语义感知优化阶段，论文利用基于注意力的掩码损失分别优化前景和背景中的对象。这确保控制点保持在各自的区域内，有助于对象分解。使用到的损失函数为
$$\mathcal L_\mathbf{SIVE}=\sum_i^O{(\hat{\mathcal M}_i\odot I-\hat{\mathcal M}_i\odot\mathbf x)^2}$$

### 基于矢量粒子的分数蒸馏

为了解决生成图像过度平滑和过饱和等问题，VPSD将SVG图像建模为控制点和颜色分布的集合，并使用粒子变分推理方法对控制点进行建模，从而提高生成图像的多样性和视觉质量。

给定一个文本提示 $y$，存在所有可能的矢量形状表示的概率分布 $\mu$。在由 $\theta$ 参数化的矢量表示下，可以将这种分布建模为概率密度 $\mu(\theta│y)$。VPSD 针对整个分布进行优化，并从中采样 $\theta$。VPSD 用预训练的扩散模型计算加噪的真实图像的得分，用另一个噪声预测网络计算加噪的生成图像的得分。

此外，VPSD 使用了低秩适配（LoRA）作为另一个噪声预测网络，对模型进行高效更新，并引入了奖励反馈机制以加速收敛。因此，其最终的损失函数为
$$\mathcal L=\min_\theta{\nabla_\theta\mathcal L_\mathbf{VPSD}}+\mathcal L_\mathbf{lora}+\lambda_r\mathcal L_\mathbf{reward}$$
$$\nabla_\theta\mathcal L_\mathbf{VPSD}=\mathbb E_{t,\epsilon,p,c}[w(t)(\epsilon_\phi(\mathbf z_t;y,t)-\epsilon_{\phi_{est}}(\mathbf z_t;y,p,c,t))\frac{\partial\mathbf z}{\partial\theta}]$$
$$\mathcal L_{\text{LoRA}}=\mathbb E_{t, \epsilon, p, c}{|\epsilon_{\phi_{\text{est}}}(\mathbf z_t; y, p, c, t) - \epsilon|}_ 2^2$$
$$\mathcal L_{\text{reward}} = \lambda \, \mathbb E_y \left[ \psi \left( r(y, g_{\phi_{\text{est}}}(y)) \right) \right]$$

整个的过程可以概括总结为：更新图像的同时更新生成器。

## 实验

论文实验使用了多种定量指标：FID、峰值信噪比 PSNR、CLIPScore、BLIPScore、审美分数和人类偏好分数来衡量模型在图像多样性、文本对齐度、视觉质量及美学效果上的表现。

结果显示，SVGDreamer 在 FID 和 PSNR 指标上的得分表明其生成的 SVG 图像具有更高的多样性和视觉质量；在 CLIPScore 和 BLIPScore 的分数展示了更强的文本语义一致性；在审美分数和人类偏好分数上也表现出色，生成的图像更符合人类的美学偏好。

## 复现

根据官方给出的开源代码进行了复现

![iter11950](http://public.file.lvshuhuai.cn/images\iter11950.png)

![iter21950](http://public.file.lvshuhuai.cn/images\iter21950.png)

![iter950](http://public.file.lvshuhuai.cn/images\iter950.png)

<img src="http://public.file.lvshuhuai.cn/images\iter18950.png" alt="iter18950"  />

## 问题

由于这个推理过程实际上也是一个训练 LoRA 的过程，每次生成都在不断优化扩散模型，生成的速度非常慢，在 RTX 2080 Ti 上，使用完成的 pipeline 进行生成大约需要 30 至 40 分钟