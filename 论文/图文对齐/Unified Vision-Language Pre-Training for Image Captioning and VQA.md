# Unified Vision-Language Pre-Training for Image Captioning and VQA

## 基本信息

- 统一视觉-语言预训练用于图像描述与视觉问答
- AAAI 2020
- GitHub：[LuoweiZhou/VLP: Vision-Language Pre-training for Image Captioning and Question Answering](https://github.com/LuoweiZhou/VLP)

## 摘要

本文提出了一种统一的视觉-语言预训练（Vision-Language Pre-training, VLP）模型。其统一性体现在：（1）该模型可通过微调同时适用于视觉-语言生成任务（如图像描述生成）和理解任务（如视觉问答）；（2）采用共享的多层 Transformer 网络进行编码和解码，不同于现有多数方法中编码器与解码器分离的架构。该统一 VLP 模型通过双向掩码视觉-语言预测和序列到序列（seq2seq）掩码视觉-语言预测两项无监督学习目标，在大规模图文对上完成预训练。两项任务仅通过共享 Transformer 网络的自注意力掩码机制来区分预测所依赖的上下文条件。据我们所知，VLP 是首个在视觉-语言生成（图像描述）与理解（视觉问答）这两类差异显著的任务上均达到最先进性能的模型，并在三大基准数据集 COCO Captions、Flickr30k Captions 和 VQA 2.0 上验证了有效性。代码及预训练模型发布于 https://github.com/LuoweiZhou/VLP。

## 研究背景

- **前人工作**：基于大规模图文对做预训练，多用跨模态 Transformer 面向理解类任务（VQA、检索等），少数方法再接解码器做描述生成。
- **主要问题**：编码器/解码器往往分离训练，或需两套模型；只能覆盖理解或生成其一，迁移与工程成本高，表示在理解与生成间易“错位”。
- **本文做法**：用**同一套 Transformer**，仅通过**不同自注意力掩码**在**双向**与 **seq2seq** 间切换，统一预训练后**一模多用**，同时支持图片标注（生成）与 VQA（理解），降低复杂度并提升泛化。

## 主要方法

### 视觉-语言预训练

#### 视觉-语言变换器网络

模型将**编码器与解码器统一为单一 Transformer**。图像侧先抽取 **$N$ 个 RoI**，构造**“类感知”的区域嵌入**：
$$
r_i = W_r R_i + W_p\,[\mathrm{LayerNorm}(W_c C_i)\,|\,\mathrm{LayerNorm}(W_g G_i)]
$$
其中 $R_i$ 为外观特征，$C_i$ 为区域类别概率，$G_i$ 为几何信息；再加 segment embedding。文本侧与 BERT 相同（词嵌入+位置+segment）。输入序列为
$$
H^0=[r_{[\text{CLS}]}, r_1,\dots,r_N, y_{[\text{SEP}]}, y_1,\dots,y_T,y_{[\text{STOP}]}]
$$
整个网络由多层 Transformer 组成，自注意力掩码控制可见上下文。

<img src="Z:\Public\images\image-20251022154706519.png" alt="image-20251022154706519" style="zoom:50%;" />

#### 预训练目标

遵循 BERT 的**遮蔽语言建模**策略（随机将约 15% 文本 token 替换为 `[MASK]`/随机词/原词），在输出端预测被遮蔽词。论文采用两种目标并**按批交替训练**：

- **Bidirectional（双向）**：允许视觉与文本间**不受限的信息传递**；

- **Seq2seq（自回归）**：待预测词**不可访问未来词**（自回归）。

    二者**唯一差别**在于自注意力掩码矩阵 MMM 的可见性规则。作者发现**将区域类别概率 $C_i$​ 直接并入区域嵌入**，比“遮蔽区域分类”更有效与稳健；并且不采用 NSP/图文对应预测。

### 微调下游任务

#### 图片标注

微调时使用 **seq2seq 目标**。推断流程：输入图像 RoI 与 `[CLS]/[SEP]`，以一个 `[MASK]` 开始**逐词生成**（贪心或 beam search）；每次用新预测词替换先前的 `[MASK]` 并在序列末尾再追加一个 `[MASK]` 触发下一步；选择到 `[STOP]` 结束。

#### 视觉问答

将开放域 VQA 设为**多标签分类**：选取**最常见的 k=3129k=3129k=3129 个答案**为类别。以 `[CLS]` 与 `[SEP]` 的**最后隐状态逐元素乘**作输入，接 **MLP（Linear+ReLU+Linear+Sigmoid）** 得到各类得分；

用**soft 标签**与交叉熵优化。与部分工作在预训练中混入目标数据不同，本文**预训练不依赖下游标注**。

## 实验

### 数据集

- **预训练**：**Conceptual Captions（CC）**，约 **300 万**图文对。
- **下游**：**COCO Captions**、**Flickr30k**、**VQA 2.0**。COCO/Flickr30k 采用 Karpathy 划分（COCO 113.2k/5k/5k，Flickr30k 29.8k/1k/1k）；VQA 2.0 使用官方划分并在 Test-Standard 上评测。文本按 BERT 规范分词、截断/填充到 20 词。

### 结果

<img src="Z:\Public\images\image-20251022154955924.png" alt="image-20251022154955924" style="zoom:50%;" />