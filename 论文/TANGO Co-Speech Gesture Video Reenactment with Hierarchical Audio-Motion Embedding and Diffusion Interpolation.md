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

