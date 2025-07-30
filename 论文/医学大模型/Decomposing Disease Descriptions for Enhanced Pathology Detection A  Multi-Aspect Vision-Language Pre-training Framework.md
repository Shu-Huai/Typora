# Decomposing Disease Descriptions for Enhanced Pathology Detection: A  Multi-Aspect Vision-Language Pre-training Framework

## 基本信息

- 分解疾病描述以增强病理检测：一种多维度视觉语言预训练框架
- CVPR 2024
- GitHub: [HieuPhan33/CVPR2024_MAVL: Multi-Aspect Vision Language Pretraining - CVPR2024](https://github.com/HieuPhan33/CVPR2024_MAVL)
- 数据集：ChestX-ray14、CheXpert、PadChest、RSNA Pneumonia、SIIM-ACR Pneumothorax、COVIDx CXR-2、COVID Rural

## 摘要

医学视觉语言预训练（VLP）已成为前沿研究领域，其通过将查询图像与各类疾病的文本描述进行比对，实现了零样本病理识别。由于生物医学文本的复杂语义性，现有方法难以将医学图像与非结构化报告中的关键病理发现对齐，导致与目标疾病的文本表征失配。本文提出了一种新型 VLP 框架，通过咨询大语言模型和医学专家，利用病理视觉表现的先验知识将疾病描述解构为基本维度。结合 Transformer 模块，我们的方法将输入图像与疾病多维要素对齐，生成以维度为中心的图像表征。通过整合各维度匹配结果，显著提升了图像与对应疾病的兼容性。此外，基于维度导向表征，我们设计了双头 Transformer 架构，分别处理已知与未知疾病，优化综合检测效能。在七个下游数据集上的实验表明，本方法对已知和未知类别的识别准确率较现有技术最高提升 8.56% 和 17.26%。代码已发布于 [https://github.com/HieuPhan33/MAVL](https://github.com/HieuPhan33/MAVL)。

## 方法

### 问题设定与基本架构

#### 任务设定

- 输入：图像 $I \in \mathbb{R}^{H \times W \times 3}$，以及疾病文本描述 $T_c$
- 输出：
  - 疾病概率预测 $\hat{p}$
  - 疾病在图像中的定位热图 $\hat{m}$

论文将传统 VLP 的图像-文本匹配任务重新表述为 **多标签分类问题**，借助 RadGraph 提取报告中的医学实体 $\varphi(R)$，构建监督标签 $Y$。

#### 数学定义

图像-文本融合预测

$$
\hat{p}, \hat{m} = \Phi_{\text{fusion}}(f_{\text{vision}}(I), f_{\text{text}}(T_c))
$$

- $f_{\text{vision}}$：图像编码器（如 ResNet-50 或 ViT）
- $f_{\text{text}}$：文本编码器（ClinicalBERT，冻结）
- $\Phi_{\text{fusion}}$：Transformer 融合模块

### Multi-Aspect Vision-Language Matching（多维度视觉语言匹配）

#### 动机

医学文本复杂，现有方法直接使用疾病定义或报告内容进行匹配，难以对齐图像特征。

#### 解决方案

将每个疾病 $c_j$ 的定义解构为 $K$ 个视觉要素：

$$
S_j = \{ s_{j1}, s_{j2}, \dots, s_{jK} \}
$$

这些要素包括：
- Shape（形状）
- Texture（纹理）
- Opacity（不透明度）
- Location（位置）
- Border（边界）
- Fluid presence（积液）
- Pattern（形态）
- Other（其他）

#### 数据构建流程

<img src="http://public.file.lvshuhuai.cn/images\image-20250722162332598.png" alt="image-20250722162332598" style="zoom:50%;" />

1. **实体提取**：使用 RadGraph 提取实体与位置；
2. **专家注释**：两位医生独立标注 23 个维度，筛选出 7 个一致维度 + Other；
3. **GPT-4 生成描述**：每个维度由 GPT-4 生成详细描述，并经专家审校；
4. **最终表征**：每个疾病的文本特征表示为：

$$
A_j = \left\{ f_{\text{text}}(\text{Description}(s_{jk})) \mid k = 0 \dots K \right\}
$$

### 双头 Transformer 模块（Dual-Head Transformer）

<img src="http://public.file.lvshuhuai.cn/images\image-20250722163103685.png" alt="image-20250722163103685" style="zoom:50%;" />

整个 MAVL 网络包含两个分支：

#### 对比学习头（Contrastive Head）

- 目标：识别未见类别（unseen diseases）
- 图像特征 $f$ 使用 Attention Pooling 得到：

$$
f = \text{AttentionPool}(V), \quad V \in \mathbb{R}^{h \times w \times d}
$$

- 对比损失函数：

$$
\mathcal{L}_{\text{cl}} = \sum_{k=1}^{K} \log \frac{\sum_{j \in \mathcal{P}(i)} \exp(f_i^\top a_{jk})}{\sum_t \exp(f_i^\top a_{tk})}
$$

其中 $\mathcal{P}(i)$ 表示图像 $i$ 中存在的疾病集合。

#### 监督学习头（Supervised Head）

- 目标：识别已知类别（seen diseases）
- 将文本维度嵌入 $Q_j$ 作为查询，图像特征 $V$ 作为键值，进行 cross-attention：

$$
F_j, \tilde{m}_j = \Theta_{\text{ground}}(Q_j, V)
$$

- 分类预测通过全连接层 $W \in \mathbb{R}^{Kd \times 2}$ 得到：

$$
\hat{p}_j = \text{FC}(F_j)
$$

- 若有位置信息，加入位置对比损失：

$$
\mathcal{L}_{\text{loc}} = \text{contrast}(\tilde{e}_j, f_{\text{text}}(\text{"It is located at } l_j \text{"}))
$$

### 总损失函数

训练时使用三重损失加权求和：

$$
\mathcal{L}_{\text{total}} = \alpha \mathcal{L}_{\text{cl}} + \beta \mathcal{L}_{\text{sup}} + \gamma \mathcal{L}_{\text{loc}}
$$

其中：
- $\mathcal{L}_{\text{cl}}$：对比损失（unseen）
- $\mathcal{L}_{\text{sup}}$：监督分类损失（seen）
- $\mathcal{L}_{\text{loc}}$：位置对比损失（可选）

## 实验

### 数据集

- **训练集**：MIMIC-CXR v2（22 万个图文对）
- **测试集**（7 个）：
    - 已知疾病：ChestX-ray14、CheXpert、PadChest-seen、RSNA、SIIM-ACR
    - 未知疾病：PadChest-unseen、COVIDx、COVID Rural

### 任务与指标

- 任务：Zero-shot classification、Zero-shot segmentation、Fine-tuning classification/segmentation
- 指标：AUC、F1、Accuracy、Dice、IoU、Pixel-wise Accuracy

### 结果

在全部任务上有提升