# FSI 准备情况

## 前期修改

根据审稿人的意见，主要修改了以下内容：

1. 参考文献的增补
2. 语言使用的规范化
3. 论述的逻辑性完善
4. 模型细节的补充
5. 创新点的突出

## 近期主要修改内容

近期对论文创新点进一步做了强调和突出，从

> The objectives of this study are twofold: first, to assess the feasibility of employing a CNN architecture, DenseNet, for adult age estimation using RGB images derived from CT reconstructions of five osteological landmarks, specifically the ventral, dorsal, and unified surfaces of the pubic symphysis, the pubic tubercle, and the ischial tuberosity. Second, to propose and evaluate the effectiveness of a novel data augmentation strategy, R-Mixup, designed to generate enhanced training data by linearly interpolating both input features and their associated labels. This study examines whether R-Mixup can further optimize the generalization performance of DenseNet in predicting adult age.

修改并扩增为

>Inspired by this work, we propose Dynamic Sampling Mixup (DS-Mixup),  a Mixup-based augmentation strategy that employs a dynamically guided neighbor sampling mechanism guided by Gaussian Kernel Density Estimation (KDE). DS-Mixup performs selective interpolation between training samples with similar chronological ages by leveraging a KDE-guided probability distribution that is updated within each training batch. This dynamic distribution captures local sample density and age proximity, guiding the pairing process to produce biologically plausible combinations. In addition, we introduce an age difference threshold to prevent interpolation between samples with excessively large age gaps, thereby avoiding the generation of unrealistic pseudo-samples that may violate biological constraints.
>
>In practice, different regions of interest (ROIs) have different importance in inference. To further enhance robustness in practical forensic scenarios, we develop a multi-ROI weighted fusion strategy. Instead of simply splicing the result of five ROIs, region-specific predictions are adaptively aggregated based on their reliability.
>
>The main contributions of this study are as follows:
>
>- We propose DS-Mixup, a data augmentation strategy for regression tasks that performs dynamic sample pairing based on a neighbor sampling module guided by Gaussian Kernel Density Estimation (KDE), and introduces an age difference threshold to ensure biologically plausible interpolation between samples with similar chronological ages.
>- We conduct a systematic analysis of five pelvic regions of interest (ROIs) to evaluate the contribution of each region to age estimation. Based on this analysis, we design a multi-ROI weighted fusion strategy that adaptively aggregates region-specific predictions according to the estimated reliability of each ROI, thereby improving the robustness and interpretability in realistic forensic scenarios.
>- Extensive experiments demonstrate the feasibility of using a CNN architecture, DenseNet, for adult age estimation based on RGB images reconstructed from CT scans. The results show that the proposed DS-Mixup significantly improves the generalization of DenseNet in adult age prediction tasks compared to standard Mixup and other augmentation baselines.

并重命名模型从 `R-Mixup` 到 `DS-Mixup`。

## 投稿安排

计划全文检查一遍语法和拼写错误，然后提交投稿。