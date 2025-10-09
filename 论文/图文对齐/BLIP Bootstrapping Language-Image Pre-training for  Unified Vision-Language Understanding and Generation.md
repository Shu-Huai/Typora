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

### 多模态编码器-解码器混合模型 MED

<img src="http://public.file.lvshuhuai.cn/images\image-20251006145546743.png" alt="image-20251006145546743" style="zoom:50%;" />

**总体思路**：用一个统一的多任务架构，在**三种功能形态**间切换：

1. **Unimodal encoder（纯编码）**：分别编码图像与文本（文本侧同 BERT，句首加 `[CLS]` 表征语义）。用于对比学习。
2. **Image-grounded text encoder（图像引导的文本编码器）**：在文本 Transformer 的每个 block 中，在自注意力（SA）与前馈层（FFN）之间**插入一层跨模态交互的 Cross-Attention（CA）**，并在文本前加任务标记 `[Encode]`，取其输出嵌入作为图文对的**多模态表示**。用于图文匹配。
3. **Image-grounded text decoder（图像引导的文本解码器）**：把上面的双向自注意力**替换为因果自注意力**（Causal SA），用 `[Decode]` 作为起始标记，末尾有结束标记。用于图像条件的自回归生?成。

**视觉与文本主干**：图像侧采用 ViT，把图像切成 patch 序列并加 `[CLS]`；文本侧采用 BERT。论文指出直接用 ViT 比“基于检测器的特征”更高效，且符合最新趋势。

**参数共享策略**：文本**编码器与解码器共享除自注意力（SA）外的所有参数**（包括嵌入层、CA 层、FFN），原因是编码与解码的差异**主要体现在自注意力的方向性**（双向 vs. 因果）；共享其它层能提高效率并利于多任务学习。

> 小结：一个 ViT + 文本 Transformer，通过切换“是否插 CA、SA 是否因果、是否取 `[Encode]`/自回归输出”，即能“一模多用”地完成理解与生成两类任务。论文的图 2 对这三种形态及对应目标有直观示意。

### 预训练目标（联合三种损失）

BLIP 在预训练时**联合优化三种目标**：**ITC（对比）+ ITM（匹配）+ LM（语言建模）**。一次样本前向中，图像只过 ViT **1 次**，文本在三种功能下各前向一次，分别计算三种损失，从而在保持效率的同时实现多任务学习。

#### Image–Text Contrastive Loss（ITC）

- **激活形态**：Unimodal encoder（图像编码 + 文本编码，互不交互）。
- **目标**：把正样图文表征拉近、负样推远，统一表征空间。
- **实现要点**：**动量编码器**产生特征；从动量分支产生**软标签**作为训练目标，以缓解“负样中潜在正样”问题（即 InfoNCE 的 false negatives）。

### Image–Text Matching Loss（ITM）

- **激活形态**：Image-grounded text encoder（文本每层插 CA，与图像交互）。
- **目标**：**二分类**判别图文是否匹配，用 ITM 头（线性层）基于多模态表征输出 matched/unmatched 概率。
- **困难负样本挖掘**：选取**对比相似度更高**的负对来计算损失，更具信息量。

### Language Modeling Loss（LM）

- **激活形态**：Image-grounded text decoder（因果 SA，自回归）。
- **目标**：在图像条件下最大化文本似然（交叉熵），**标签平滑 0.1**；相较常见的 MLM，LM 能更好地学习**从视觉到连贯文本**的生成能力。

### CapFilt：“生成 + 过滤”的数据自举

<img src="http://public.file.lvshuhuai.cn/images\image-20251006173755661.png" alt="image-20251006173755661" style="zoom:50%;" />

**动机**：网页图文（alt-text）**嘈杂**且不总描述图像本身；单纯扩数据规模次优。CapFilt 通过**补充信息**与**去噪**把弱监督变强监督。

**两个模块（均由同一个预训练好的 MED 轻量微调得到）**：

- **Captioner（图像引导的文本解码器）**：在 COCO 上用 LM 目标**微调**，对每张网页图像生成**合成描述**（每图一条）。
- **Filter（图像引导的文本编码器）**：在 COCO 上用 ITC + ITM **微调**；用其 ITM 头判断文本是否与图像匹配，对**原网页文本**和**合成文本**一起打分，**剔除**不匹配（噪声）样本。

### 完整流程

1. 先有一个预训练 MED；
2. 分别在 COCO 上微调出 **Captioner** 与 **Filter**（代价很小）；
3. Captioner 对网页图像生成合成描述；Filter 对“原网页文本 + 合成文本”逐一判别并去噪；
4. 把**过滤后的网页图文**与**人工标注图文**混合成新语料，**重新预训练**新的 BLIP。

> 论文实验表明：Captioner 与 Filter **协同**能显著提升各类下游任务；而且**更“多样化”的生成描述**（相对束搜索，更偏采样型解码）往往进一步提升预训练收益。

## 实验

<img src="http://public.file.lvshuhuai.cn/images\image-20251006173710345.png" alt="image-20251006173710345" style="zoom:50%;" />

<img src="http://public.file.lvshuhuai.cn/images\image-20251006173623607.png" alt="image-20251006173623607" style="zoom:50%;" />

## 实验复现

<img src="http://public.file.lvshuhuai.cn/images\image-20251007133831940.png" alt="image-20251007133831940" style="zoom:50%;" />
