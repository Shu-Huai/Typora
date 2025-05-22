# SVGDreamer总体架构讲稿

## 中文

接下来让我们看一下本文作者团队所提出的新方法。

我们的目标是从文本生成图像分离的、美观的、多样化的SVG。作者将这个任务进行拆分，总体上形成了五个步骤。

在这个拆分中，我们的期望输入，举例为“a dog in the street, sitting, lovely, high quality, style: iconography”。我们的期望输出为一张SVG图片。

首先，使用预训练的扩散模型，如Stable Diffusion 1.5，生成一张符合提示词的目标图片。请注意，这张图片是用像素组织的图片。

接下来，提取出扩散模型中不同对象的交叉注意力图，将提示词中提到的前景对象和背景进行拆分。对不同的前景对象和背景进行独立的SVG初始化过程，并分别对其进行迭代优化。这个阶段被称为SIVE，Semantic-driven Image VEctorization，这样的初始化和优化方案增强了SVG的可编辑性。

之后，对分解的对象进行统一的迭代优化。

之后根据输入的风格化信息，如iconography，对SVG的基元类型VRP和相关属性进行了限制，这保证了生成结果的风格化和多样性。

之后，对可微分光栅化器进行训练，并在预训练的扩散模型上对SVG的概率分布进行微调，采样后得到我们想要的结果。

如图所示就是该方法的总体pipeline。

## 英语

Next let's look at the new approach proposed by the team of authors of this paper.
Our goal is to generate object-separated, good looking and diverse SVGs from text, and the authors have split this task into five overall steps.
In this approach, our desired input is, for example, “a dog in the street, sitting, lovely, high quality, and a style: iconography”. Our desired output is an SVG.
First, a pretrained diffusion model, such as Stable Diffusion 1.5, is used to generate a target image that matches the prompt. Note that this image is a pixel-organized image, not an SVG.
Next, the cross-attention maps of different objects are extracted from the diffusion model and the foreground objects and backgrounds mentioned in the prompt are split. A separate SVG initialization process is performed for the different foreground objects and backgrounds, and they are iteratively optimized separately. This phase is called SIVE, Semantic-driven Image VEctorization, and this process enhances the editability of the SVG.
After that, a unified iterative optimization of the objects is performed.
Afterwards, the SVG's primitive type VRP and related attributes are restricted based on the input style information, such as iconography, which ensures the stylization and diversity of the generated results.
After that, the differentiable rasterizer is trained and the probability distribution of SVG is fine-tuned on the pretrained diffusion model and after sampling from the distribution , we can get our desired results.
The overall pipeline of the method is shown in Fig.