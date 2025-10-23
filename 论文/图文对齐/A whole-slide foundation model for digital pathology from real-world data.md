# A whole-slide foundation model for digital pathology from real-world data

## 基本信息

- 基于真实世界数据的数字病理学全切片基础模型
- Nature
- GitHub：[prov-gigapath/prov-gigapath: Prov-GigaPath: A whole-slide foundation model for digital pathology from real-world data](https://github.com/prov-gigapath/prov-gigapath)

## 摘要

数字病理学带来了独特的计算挑战，因为一张标准千兆像素级玻片可能包含数万张图像区块。先前模型通常仅对每张玻片进行小部分区块的二次采样，因而丢失了关键的玻片级上下文信息。本文提出 Prov-GigaPath——一个基于普罗维登斯医疗系统（美国大型医疗网络，涵盖 28 个癌症中心）171,189 张全玻片、13 亿个 256×256 病理图像区块预训练的全玻片病理基础模型。这些玻片源自超过 3 万名患者的 31 种主要组织类型。为预训练 Prov-GigaPath，我们开发了 GigaPath——专为千兆像素病理玻片预训练设计的新型视觉 Transformer 架构。为实现数万图像区块的玻片级学习，GigaPath 采用新开发的 LongNet 方法适配数字病理学场景。我们构建了包含 9 项癌症亚型分类任务和 17 项病理组学任务的数字病理基准测试（采用普罗维登斯和 TCGA 数据）来评估 Prov-GigaPath。通过大规模预训练和超长上下文建模，Prov-GigaPath 在 26 项任务中的 25 项达到最先进性能，其中 18 项任务较次优方法有显著提升。通过整合病理报告，我们进一步展示了 Prov-GigaPath 在病理学视觉-语言预训练方面的潜力。综上，Prov-GigaPath 作为开源权重的基础模型，在多项数字病理任务中实现最先进性能，印证了真实世界数据和全玻片建模的重要性。

## 研究背景

- 数字病理的整张切片（WSI）常含**数万块 tiles**，以往方法多从中**抽样少量 tiles**，导致**整片级上下文**缺失
- 同时，标注代价高，成为制约因素。
- 作者提出在**海量未标注真实世界数据**上做自监督预训练，以缓解对特定任务标注的依赖。

## 主要方法

- 团队构建 **Prov-Path**（171,189 张 WSI，>30,000 患者，31 个组织类型；共 13.85 亿个 256×256 tiles）
- 并提出两级架构 **Prov-GigaPath / GigaPath**：先用 **DINOv2-ViT** 得到 tile 表征，再用基于 **LongNet** 的**整片级编码器**对**超长序列**进行上下文建模，配合 MAE 式掩码重建进行自监督预训练。
- 整体在 26 个任务（9 个分型 + 17 个 pathomics/分子预测）上评测，**25/26** 达到 SOTA。

<img src="Z:\Public\images\image-20251021184341704.png" alt="image-20251021184341704" style="zoom:50%;" />

### 预处理 WSI 图像

- **组织区域分割**：下采样到约 1024 像素分辨率后做 **Otsu 阈值**以去背景；
- **空间统一**：将 WSI 统一到 **0.5 μm/pixel（20×）**；
- **裁块与筛选**：裁成 **256×256** tiles，按 Otsu 占比 <0.1 的 tiles 丢弃；
- **集群并行**：最多 200 个节点（32 核 CPU/256GB RAM）并行，约 **157 小时**完成，最终得到 **1,384,860,229** 个 tiles。

### Prov-GigaPath 预训练细节

- **Tile 编码器（DINOv2-ViT）**：以单 tile 为样本进行自监督训练；基础学习率 **4×10⁻³**，单卡 batch **12**，有效 batch **384**。
- **Slide 编码器（LongNet）**：将切片序列化为超长 token 序列；坐标离散化网格 **d_grid=256，n_grid=1000**；序列增强含裁剪比 **0.875**、坐标随机移动与**水平翻转**（p=0.5）。
- **MAE 预训练**：学习率 **5×10⁻⁴**，单卡 batch **4**，**30** 个 epoch（首个 epoch 预热）；使用 **16 节点 × 4×80GB A100**，约 **2 天（3,072 GPU-hours）**完成。
- **推理时延**：每张 WSI 平均 **0.7 s**（tile 嵌入 0.4 s + LongNet 0.3 s）。

### 竞争方法与基准测试

- **对比基线**：
    - **HIPT**：在 TCGA 10,678 WSI 上预训练，分层金字塔（256 与 4096 视图），与本工作一样采用 DINO 预训练 tile 编码器，但**聚合方式不同**（其为二阶段 ViT；本工作为 LongNet 超长序列学习）。
    - **CTransPath**：CNN + 多尺度 Swin，语义相关对比学习。
    - **REMEDIS**：ResNet 主干，SimCLR，在 2.9 万张 TCGA 切片的 5,000 万病理图上预训练。
- **评测设置**：下游微调时**冻结 tile 编码器，仅微调 LongNet**；所有模型 **20 epoch**、**十折交叉验证**；Prov-GigaPath 另外加了一条**捷径连接**以加强对 tile 级特征的注意。
- **总体结果**：在 **9 个分型 + 17 个 pathomics/分子预测**共 **26** 任务中，Prov-GigaPath **25/26 SOTA**，其中 **18** 个任务较第二名有显著提升。

### 突变预测

- **范围**：覆盖**泛癌 18 生物标志物**、**LUAD 特定 5 基因**、**泛癌 5 基因**、**TCGA-LUAD 5 基因**与**TMB**等设置。
- **表现**：在各设置下，以 **AUROC/AUPRC** 显著优于 HIPT、CTransPath、REMEDIS；图 2 展示了不同基因维度的提升及显著性（多处 **P<0.001**）。
- **零样本突变预测（视觉-语言）**：用报告对齐后的 Prov-GigaPath，在 LRP1B、KRAS、TP53、SPTA1、FAT1、KMT2D 六个突变的**零样本**预测上，较 MI-Zero、BiomedCLIP、PLIP 均**显著更优**（**P<0.001**）。

### 癌症亚型分型

<img src="Z:\Public\images\image-20251021190255822.png" alt="image-20251021190255822" style="zoom:50%;" />

- **有监督微调**：在 Prov-Path 的 **9 个主要癌种**分型任务上，Prov-GigaPath 全部**优于对手**，其中 **6 个**癌种相对第二名有**显著提升**；改进主要来自**LongNet 的整片级聚合**。
- **消融**：将预训练的 LongNet 换为随机初始化，平均 AUROC **0.903 → 0.886**（**P<2×10⁻³**）；冻结/解冻 LongNet 表现接近，说明**预训练已学到高质量整片表征**。

### 视觉-语言对齐

<img src="Z:\Public\images\image-20251021190235124.png" alt="image-20251021190235124" style="zoom:50%;" />

- **数据与清洗**：构建 **17,383 对**“切片-病理报告”配对；先以少量人工清洗样本为**ICL 模板**，用 **GPT-3.5** 批量清洗，得到聚焦诊断的信息；文本嵌入用 **text-embedding-ada-002**。
- **训练**：采用 OpenCLIP 框架，视觉编码器为继续预训练的 Prov-GigaPath，文本侧用 **PubMedBERT**；学习率 **5×10⁻⁴**、batch **32**、10 个 epoch。
- **评测**：在 **NSCLC、COADREAD** 的**零样本分型**与上述 6 个基因突变的**零样本预测**上，Prov-GigaPath **全面超过** MI-Zero、BiomedCLIP、PLIP；作者将优势归因于**基于报告的整片级对齐**与**真实世界报告信息更丰富**。  

## 实验

<img src="Z:\Public\images\image-20251021190328033.png" alt="image-20251021190328033" style="zoom:50%;" />