# BLIP: Bootstrapping Language-Image Pre-training for  Unified Vision-Language Understanding and Generation

- ICML 2022
- BLIP：通过自举语言-图像预训练实现统一视觉-语言理解与生成
- GitHub：[salesforce/BLIP: PyTorch code for BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation](https://github.com/salesforce/BLIP#)

## 摘要

视觉-语言预训练（VLP）技术显著提升了多模态任务的性能。然而现有预训练模型大多仅擅长理解型或生成型任务中的一类。此外，性能提升主要依赖网络爬取的噪声图像-文本对进行数据扩增，这种监督信号源并非最优。本文提出新型 VLP 框架 BLIP，可灵活迁移至视觉-语言理解与生成双类型任务。该框架通过标题引导策略高效利用噪声网络数据：标题生成器创建合成描述，过滤器剔除低质量样本。我们在图像-文本检索（平均召回率 @1 提升 2.7%）、图像描述生成（CIDEr 指标提升 2.8%）和视觉问答（VQA 分数提升 1.6%）等任务中实现最先进性能。BLIP 在零样本条件下直接迁移至视频-语言任务时亦展现出强大泛化能力。代码与模型详见 https://github.com/salesforce/BLIP。

## 研究背景

- 视觉语言预训练（VLP）在下游任务中获得成功
- 现有架构基于编码器，使其不能用于文本生成任务，要么基于编码器-解码器结构，使其不能用于图文检索任务
- 现有数据集基于网络上爬取的大规模数据集，这些数据集含有噪声，并非最优选（本文证明）

## 关键方法

BLIP 提出一个同时擅长“理解”和“生成”的视觉-语言预训练框架：用统一的**混合编码-解码器（MED）**学三种目标（对比、匹配、条件语言建模），再用 **CapFilt** 把嘈杂的网页图文数据“自举”成更干净、更有信息量的语料，因此在检索、描述、VQA 等多任务上拿到 SOTA。

### 多模态编码器-解码器混合模型

