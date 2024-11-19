# DEADiff: An Efficient Stylization Diffusion Model with Disentangled Representations

## 基本信息

DEADiff：一种具有分离表示的高效风格化扩散模型

将参考图中的风格和语义解耦，保留风格信息参与到图像生成中

CVPR 2024

项目地址：[DEADiff: An Efficient Stylization Diffusion Model with Disentangled Representations (tianhao-qi.github.io)](https://tianhao-qi.github.io/DEADiff/)

arxiv：[DEADiff: An Efficient Stylization Diffusion Model with Disentangled Representations (arxiv.org)](https://arxiv.org/abs/2403.06951)

代码地址：[bytedance/DEADiff: CVPR 2024 Official implementation of "DEADiff: An Efficient Stylization Diffusion Model with Disentangled Representations" (github.com)](https://github.com/bytedance/DEADiff)

论文地址：[DEADiff An Efficient Stylization Diffusion Model with Disentangled Representations.pdf](http://public.file.lvshuhuai.cn/DEADiff An Efficient Stylization Diffusion Model with Disentangled Representations.pdf)

## 摘要

基于扩散的文本到图像模型在传递参考风格方面具有巨大的潜力。然而，当前基于编码器的方法在传递风格的同时显着削弱了文本到图像模型的文本可控性。在本文中，我们引入DEADiff来使用以下两种策略来解决这个问题：1）一种解耦参考图像的风格和语义学的机制。解耦后的特征表示首先由Q-Formers提取，这些Q-Formers由不同的文本描述指示。然后它们被注入到交叉注意力层的互斥子集中，以便更好地解开纠缠。2）一种非重构学习方法。Q-Formers使用配对图像而不是相同的目标进行训练，其中参考图像和真实图像具有相同的风格或义语学。我们证明DEADiff获得了最佳的视觉风格化结果，并在文本到图像模型中固有的文本可控性和与参考图像的样式相似性之间取得了最佳平衡，这在定量和定性上都得到了证明。

## 研究背景

近年来，扩散模型（Diffusion Models）在文本到图像生成任务中取得了巨大的成功。然而，因其加噪和降噪的机制，其可控性很难在实践中得到保证。最近的一些研究常常聚焦于如何稳定可靠地引导模型遵循由参考图像定义的预定风格生成图像。

一种方法是基于优化的方法，通过微调扩散模型来更好地捕捉参考图像风格，同时保留提示文本的语义信息，然而由于需要为每个输入参考图像微调模型计算代价高昂。另一种方法是基于编码器的方法，通过训练编码器将参考图像编码为信息特征，但降低了模型在理解文本条件的语义上下文方面的能力。

基于此，论文提出了一种有效的风格迁移方案，目的是在参考图像风格迁移的同时，保持对文本语义的控制能力。

## 研究方法

为了实现同时保留风格和文本语义这一目标，论文采用了双重解耦表示提取机制（Dual Decoupling Representation Extraction Mechanism）和非重建训练策略。

### 双重解耦表示提取

论文通过引入Q-Former模型\cite{li2023blip2bootstrappinglanguageimagepretraining}，一种基于查询（query）机制的Transformer模型，通过与文本描述配合来引导解耦任务，分别从参考图像中提取“风格”和“语义”表示。

具体而言，如图\ref{fig3}所示，在风格解耦任务中，使用参考图像对进行训练。每对图像包含两张具有相同风格但不同语义内容的图像。Q-Former被指导仅从参考图像中提取“风格”信息，而忽略语义内容。为了实现这一目标，模型会引入“风格”条件文本描述作为输入，使Q-Former能专注于从参考图像中捕捉颜色、纹理、笔触等风格特征。类似地，语义解耦任务使用另一对参考图像进行训练，这些图像具有相同的内容（即语义相同），但风格不同。在训练时使用“语义”条件文本作为输入。

![](http://public.file.lvshuhuai.cn/images/PixPin_2024-10-03_16-20-04.png)

该机制可以显著减少语义与风格之间的干扰。

### 解耦条件机制

去噪U-Net中的不同交叉注意力层主导合成图像的不同属性。U-Net的粗层主要用于处理图像的全局特征和对象语义信息，而细层通常用于调整图像的局部细节和纹理。因此，仅将具有“语义”条件的Q-Former输出查询注入到粗层，而将具有“风格”条件的Q-Former输出查询注入到细层，能够更有效地分离风格和语义特征。

同时，论文引入联合文本图像交叉注意力机制，使用独立的投影层来处理文本和图像特征，并将它们分别输入到注意力计算中，避免了传统方法中风格与语义之间的相互干扰。

## 实验

论文通过组合主题词和风格词手动创建文本提示列表，并利用文本转图片生成产品Midjourney合成相应的图片，并经过人工筛选后确保配对图像的高质量，构建了风格配对数据集和语义配对数据集，分别包含16万对具有相同风格、不同语义的图像对和106万对具有相同语义、不同风格的图像对。

经过训练和推理，并将实验数据和目前最先进的方法进行比较，论文提出的方法在风格相似度、文本对齐能力、图像质量、主观偏好等评价尺度上取得了最优的结果。定性试验如图所示。

![](http://public.file.lvshuhuai.cn/images/PixPin_2024-10-03_17-05-55.png)

## 局限