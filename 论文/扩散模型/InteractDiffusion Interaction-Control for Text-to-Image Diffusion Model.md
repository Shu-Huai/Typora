# InteractDiffusion: Interaction-Control for Text-to-Image Diffusion Model

## 基本信息

文本到图像扩散模型的交互控制

一种能够基于给定交互控制信息实现对生成图片中对象交互关系的控制的扩散模型

CVPR 2024

论文：[InteractDiffusion Interaction Control in Text-to-Image Diffusion Models.pdf](http://public.file.lvshuhuai.cn/InteractDiffusion Interaction Control in Text-to-Image Diffusion Models.pdf)

arxiv：[InteractDiffusion: Interaction Control in Text-to-Image Diffusion Models (arxiv.org)](https://arxiv.org/abs/2312.05849)

项目主页：[InteractionDiffusion: Interaction Control in Text-to-Image Diffusion Models (jiuntian.github.io)](https://jiuntian.github.io/interactdiffusion/)

源码：[https://github.com/jiuntian/interactdiffusion](https://github.com/jiuntian/interactdiffusion)

## 研究背景

文本到图像扩散模型能够根据文本描述生成连贯的图像，在内容创作领域具有广泛的应用。随着研究的不断深入，扩散模型的可控性被越来越多的研究人员所关注。现有的扩散模型在静态图像（如绘画或风景照片）上效果很好，但在生成涉及交互的图像方面面临巨大挑战。已有研究通过控制对象定位、姿态和图像轮廓等因素来控制生成的图像，但在控制生成内容中对象之间的交互方面仍有待提高。如何在当前性能优秀的扩散模型中加入对能够理解并生成交互对象的模块是一个亟待解决的问题。

## 研究方法

为了在文本到图像扩散模型中实现对对象间交互的控制，论文提出了InteractDiffusion模型。该模型通过将交互信息作为额外的条件信息整合到现有的预训练模型中，以增强生成图像中交互的准确性和可控性。

### 交互标记化

在这一步骤中，论文将每个交互对定义为一个包含主体（subject）、动作（action）和对象（object）的三元组，以及对应的边界框。为了获得动作的边界框，定义了一个“between”操作，用于计算主体和对象边界框之间的中间区域。然后，使用CLIP文本编码器将文本标签和边界框编码成中间表示，并通过多层感知机（MLP）生成主体、动作和对象的标记。

### 交互嵌入

为了有效地捕获复杂的交互关系，论文引入了实例嵌入和角色嵌入。实例嵌入将同一交互实例中的标记分组，而角色嵌入则在语义上嵌入不同交互实例中标记的不同角色。通过向标记中添加实例和角色嵌入，可以对交互实体进行编码，从而在生成图像中精确控制交互和位置。

### 交互变换器（Interaction Transformer）

论文在现有的Transformer块中引入了一个新的交互自注意力层，该层在自注意力层和交叉注意力层之间进行操作，以整合交互标记，如图所示。

![img](http://public.file.lvshuhuai.cn/images/PixPin_2024-10-03_18-47-52.png)

这一层帮助将交互信息（包括交互、主体和对象的边界框）转换为视觉标记，同时在训练过程中保留原始模型的知识，同时整合额外的交互条件信息。

### 交互条件扩散模型

通过结合交互标记化、交互嵌入和交互变换器，形成了一个可插拔的交互模块，该模块能够使现有的文本到图像扩散模型实现交互控制。

## 实验

论文使用HICODET数据集对提出的模型进行了训练和评估。该数据集包括大量的人物交互注释。

实验结果表明，InteractDiffusion在人物交互检测分数上显著优于现有基线方法，并且在图像质量的FID（Fréchet Inception Distance）和KID（Kernel Inception Distance）指标上也略有提高。