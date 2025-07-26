# RadGraph: Extracting Clinical Entities and Relations from Radiology Reports

## 基本信息

- RadGraph：从放射学报告中抽取临床实体与关系的结构化信息系统
- NeurIPS 2021（Datasets and Benchmarks Track）
- 数据集：MIMIC-CXR、CheXpert
- 模型：RadGraph Benchmark（基于 DYGIE++ 的深度学习抽取器）

## 摘要

从自由文本的放射学报告中提取结构化临床信息，可使放射学报告信息应用于多种关键医疗场景。本研究提出 RadGraph——一个基于全新信息抽取框架构建的胸部 X 光放射学报告全文实体关系数据集，该框架专为结构化放射学报告而设计。我们发布了包含 500 份 MIMIC-CXR 数据集放射学报告（含 14,579 个实体与 10,889 组关系）的医师认证标注开发集，以及包含 100 份均分自 MIMIC-CXR 与 CheXpert 数据集的放射学报告（两组独立医师认证标注）的测试集。基于这些数据集，我们训练并测试了深度学习模型 RadGraph Benchmark，该模型在 MIMIC-CXR 和 CheXpert 测试集上的关系抽取微平均 F1 分数分别达到 0.82 和 0.73。此外，我们发布了推理数据集，包含 RadGraph Benchmark 自动生成的 220,763 份 MIMIC-CXR 报告（约 600 万实体与 400 万组关系）和 500 份 CheXpert 报告（13,783 个实体与 9,908 组关系）的标注结果，并与对应胸片建立关联。这一开源数据集不仅能推动医学自然语言处理研究，在关联胸片后还可促进计算机视觉与多模态学习领域的广泛探索。

## 方法

### 任务设定与架构

#### 输入与输出

- 输入：自由文本格式的胸部 X 光报告（来自 MIMIC-CXR、CheXpert）
- 输出：报告中涉及的实体（Entity）和它们之间的关系（Relation）构成的知识图谱（Graph）

#### 抽取任务

作者将放射学报告的信息抽取任务定义为两个子任务：

1. **命名实体识别（NER）**：识别 Anatomical 部位、病灶等实体
2. **关系抽取（RE）**：识别实体间的语义联系，如位置、修饰关系等

使用 BIO 标注方法进行 NER，RE 使用 R-BERT、DYGIE++ 等结构。

### 信息抽取 Schema（RadGraph Schema）

<img src="Z:\Public\images\image-20250722172137491.png" alt="image-20250722172137491" style="zoom:50%;" />

#### 实体类别（Entities）

- **Anatomy**：解剖部位（如肺、心脏）
- **Observation: Definitely Present**：明确存在的症状（如 consolidation）
- **Observation: Uncertain**：不确定的病灶（如 possibly effusion）
- **Observation: Definitely Absent**：明确不存在的症状（如 no pneumothorax）

#### 关系类别（Relations）

- **Located At (Observation, Anatomy)**：症状出现的位置
- **Suggestive Of (Observation, Observation)**：推断或因果关系
- **Modify (Obs→Obs / Anat→Anat)**：修饰、限定或量化关系

该 Schema 设计简洁、覆盖面广，便于标注人员快速一致地识别重要信息。

## 数据集构建

### 标注数据集（Development + Test）

- **开发集**：MIMIC-CXR 中 500 份报告（共 14,579 个实体，10,889 个关系）
- **测试集**：
    - MIMIC-CXR：50 份报告
    - CheXpert：50 份报告
         每份报告由两位资深放射科医生独立标注，评估一致性

### 推理数据集（Inference Set）

- 使用训练好的模型自动标注：
    - MIMIC-CXR：220,763 份报告 → 约 600 万实体，400 万关系
    - CheXpert：500 份报告 → 1.3 万实体，近万关系
         所有报告均可关联到对应图像，适用于多模态学习任务

## 模型与基准（Benchmarks）

### 模型架构

- **基线方法**：
    - BERT + 线性头（NER）
    - R-BERT（RE）
- **进阶方法**：
    - DYGIE++：联合抽取 NER 与 RE（最终选用）
    - PURE：管道式抽取架构（独立建模）

### 预训练模型选择

所有架构都尝试了不同的 BERT 初始化权重：

- BERT
- BioBERT
- ClinicalBERT
- PubMedBERT（效果最佳）
- BlueBERT

最终的 RadGraph Benchmark 使用 **PubMedBERT + DYGIE++**。