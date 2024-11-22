# TANGO: Co-Speech Gesture Video Reenactment with Hierarchical Audio-Motion Embedding and Diffusion Interpolation

## 基本信息

TANGO：具有分层音频运动嵌入和扩散插值的共语音手势视频再现

从一段演讲音频和一段人物视频合成符合演讲音频的手势、表情、动作的人物视频

项目主页：[TANGO](https://pantomatrix.github.io/TANGO/)

arxiv：[[2410.04221] TANGO: Co-Speech Gesture Video Reenactment with Hierarchical Audio Motion Embedding and Diffusion Interpolation](https://arxiv.org/abs/2410.04221)

Github：[CyberAgentAILab/TANGO: Official implementation of the paper "TANGO: Co-Speech Gesture Video Reenactment with Hierarchical Audio-Motion Embedding and Diffusion Interpolation"](https://github.com/CyberAgentAILab/TANGO)

## 摘要

我们介绍了 TANGO，这是一个用于生成共同语音身体手势视频的框架。给定几分钟的单说话人参考视频和目标语音音频，TANGO 可以生成具有同步身体手势的高保真视频。TANGO 建立在手势视频重演（GVR）的基础上，该重演使用有向图结构拆分和检索视频拆条 —— 将视频帧表示为节点，将有效过渡表示为边缘。我们解决了 GVR 的两个关键限制：音频运动失准和 GAN 生成的过渡帧中的视觉伪影。特别是，（i）我们建议使用潜在特征距离来检索手势以改善跨模态对齐。为了确保潜在特征能够有效地模拟语音音频和运动手势之间的关系，我们实现了分层联合嵌入空间（AuMoCLIP）；（ii）我们引入了基于扩散的模型来生成高质量的过渡帧。我们的扩散模型外观一致插值（ACInterp）建立在 AnimateAny 之上，包括一个参考运动模块和单应性背景流，以保持生成视频和参考视频之间的外观一致性。通过将这些组件集成到基于图形的检索框架中，TANGO 可靠地生成逼真的音频同步视频，并优于所有现有的生成和检索方法。我们的代码和预训练模型可用：\url {[这个 https URL](https://pantomatrix.github.io/TANGO/)}

## 主要贡献

TANGO 是一个基于运动图的框架，主要包括三个步骤

<img src="http://public.file.lvshuhuai.cn/images\image-20241121230733184.png" alt="image-20241121230733184" style="zoom:50%;" />

### 创建视频运动图

使用一个图（Graph）

图的节点定义为参考视频中的4帧非重叠剪辑，包含 RGB 图像帧和音频波形

边基于3D运动空间和2D图像空间的相似性来确定：使用 SMPL-X 估计 3D 姿势，并计算 3D 空间中的姿势不相似度。2D 图像空间的相似性通过身体分割和手部边界框的交集比（IoU）来估计。

### 音频条件手势检索

论文提出了一个 AuMoCLIP，层次化的音频-运动联合嵌入空间，用于编码配对的音频和运动模态数据到一个接近的潜在空间中。这个空间允许基于目标语音音频检索手势。

<img src="http://public.file.lvshuhuai.cn/images\image-20241121231627336.png" alt="image-20241121231627336" style="zoom:50%;" />

采用双塔架构，每个编码器分为低级和高级子编码器。音频编码器使用 Wav2Vec2 和 BERT 特征，而运动编码器使用 CNN 和 Transformer。

使用帧级和剪辑级对比损失来训练局部和全局跨模态对齐。

训练后，使用这些特征通过动态规划（DP）在目标音频和运动之间找到最佳匹配路径

### 扩散式视频帧插值

论文提出了 ACInterp，一个基于扩散的插值网络，用于生成高质量的过渡帧，以确保生成的视频与参考视频在外观上保持一致。

<img src="http://public.file.lvshuhuai.cn/images\image-20241121232152185.png" alt="image-20241121232152185" style="zoom:50%;" />

生成过渡帧的过程分为两个阶段。

- **Pose2Image 阶段**：在这一阶段，通过预训练的 VAE 编码器和解码器，以及 PoseGuider 和 ReferenceNet，从噪声中估计图像潜在表示。
- **Image2Video 阶段**：这一阶段捕捉视频帧之间的时间依赖性，以减少 Pose2Image 阶段中的抖动效应。通过引入起始和结束帧作为时间优先级，确保人物身份的一致性。

## 实验

论文在 Show-Oliver 和 YouTube Video 数据集上评估 TANGO，证明了其在生成逼真视频方面优于现有的生成和检索方法。

<img src="http://public.file.lvshuhuai.cn/images\image-20241121232502927.png" alt="image-20241121232502927" style="zoom:50%;" />
