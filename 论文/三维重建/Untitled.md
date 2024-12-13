#### **基本信息**

**GaussianAvatar**
一种基于单个视频重建动态可动画 3D 人体头像的方法，通过 3D 高斯表征实现动态人类外观的建模。

**会议**：CVPR 2024
**arXiv**: [2312.02134v3](https://arxiv.org/abs/2312.02134)
**代码**: [GitHub Repository](https://github.com/aipixel/GaussianAvatar)

**BibTeX**:

```
bibtex复制代码@article{hu2024gaussianavatar,
  title={GaussianAvatar: Towards Realistic Human Avatar Modeling from a Single Video via Animatable 3D Gaussians},
  author={Liangxiao Hu, Hongwen Zhang, Yuxiang Zhang, Boyao Zhou, Boning Liu, Shengping Zhang, Liqiang Nie},
  journal={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2024}
}
```

------

#### **摘要**

GaussianAvatar 提出了一种利用可动画的 3D 高斯表征人类动态外观的新方法，从单个视频生成逼真的动态人类头像。通过引入动态外观网络与可优化的特征张量，该方法支持基于姿态的动态外观建模，并能够联合优化运动和外观，有效解决单目视频中运动估计不准确的问题。

------

#### **研究背景**

单目视频重建动态人类头像在虚拟现实、游戏制作等领域具有广泛应用，但由于以下挑战，始终未能实现高效与高质量的模型：

1. **观察不足**：单目视频提供的2D信息不足以完整重建3D人体表面。
2. **运动估计不准确**：单目视频的运动估计误差常导致伪影。
3. **复杂动态外观**：布料皱褶、视角一致性等动态外观建模难度大。

以往方法：

- 基于 **NeRF** 的隐式体积建模虽然在视觉效果上表现优异，但效率较低，且缺乏对动态外观的直接控制能力。
- 显式表征方法如网格、点云等，虽有效处理拓扑变化，但受限于固定拓扑或需大量点。

GaussianAvatar 引入可动画的 3D 高斯，结合显式表征与动态外观网络，同时解决了运动优化和动态外观建模问题。

------

#### **方法**

##### **1. 可动画 3D 高斯**

每个 3D 高斯包含以下参数：位置 x∈R3x \in \mathbb{R}^3x∈R3、颜色 c∈R3c \in \mathbb{R}^3c∈R3、不透明度 α∈R\alpha \in \mathbb{R}α∈R、旋转 q∈R4q \in \mathbb{R}^4q∈R4、缩放因子 s∈R3s \in \mathbb{R}^3s∈R3。通过结合 SMPL 或 SMPL-X 模型实现高斯从模板空间到运动空间的前向绑定：

G(β,θ,D,P)=Splatting(W(D,J(β),θ,ω),P)G(\beta, \theta, D, P) = \text{Splatting}\big(W(D, J(\beta), \theta, \omega), P\big)G(β,θ,D,P)=Splatting(W(D,J(β),θ,ω),P)

其中：

- G(⋅)G(\cdot)G(⋅)：渲染图像。
- DDD：模板空间高斯位置。
- PPP：高斯的其他属性。
- W(⋅)W(\cdot)W(⋅)：标准线性混合绑定。

##### **2. 动态 3D 高斯属性估计**

引入动态外观网络学习姿态到高斯属性的映射，包括点位移 Δx^\Delta \hat{x}Δx^、颜色 c^\hat{c}c^ 和缩放 s^\hat{s}s^：

fϕ:S2→R7f_\phi: \mathbb{S}^2 \to \mathbb{R}^7fϕ:S2→R7

通过 UV 映射将 SMPL 模型表面投影到 2D 空间，使用姿态编码器提取特征并结合可优化的特征张量提升外观建模的细节。

##### **3. 联合运动与外观优化**

为解决运动估计误差，联合优化运动和外观。运动参数更新公式：

Θ^=(θ+Δθ,t+Δt)\hat{\Theta} = (\theta + \Delta \theta, t + \Delta t)Θ^=(θ+Δθ,t+Δt)

采用正向绑定过程改进运动优化的直接性和有效性。

##### **4. 两阶段训练策略**

- **阶段 1**：优化特征张量，获取更准确的运动与粗略外观。
- **阶段 2**：结合姿态特征细化动态外观建模。

------

#### **实验**

##### **数据集**

1. **People-Snapshot**: 旋转视频，姿态简单。
2. **NeuMan**: 室外场景，多运动。
3. **DynVideo**: 动态布料变化。

##### **评估方式**

- 新视角合成
- 动作重现
- 跨身份动作驱动

##### **定量结果**

| 数据集              | PSNR↑     | SSIM↑      | LPIPS↓     |
| ------------------- | --------- | ---------- | ---------- |
| **People-Snapshot** | **30.98** | **0.9791** | **0.0143** |
| **NeuMan**          | **29.94** | **0.9795** | **0.0124** |
| **DynVideo**        | **28.58** | **0.9616** | **0.0169** |

##### **定性结果**

在动态外观和姿态一致性上，GaussianAvatar 显著优于 HumanNeRF 和 InstantAvatar。

------

#### **总结**

GaussianAvatar 使用 3D 高斯动态表征实现了高效、真实的动态人类头像建模，在外观一致性和渲染效率上均有显著提升。局限性包括对前景分割的依赖以及处理宽松衣物的能力有限。