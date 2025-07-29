# Large-vocabulary forensic pathological analyses via prototypical cross-modal contrastive learning

## 基本信息

- 通过原型跨模态对比学习进行大词汇量法医病理学分析
- **HuggingFace**：[shenxiaochen/SongCi · Hugging Face](https://huggingface.co/shenxiaochen/SongCi)（需申请）
- **GitHub**：[shenxiaochenn/SongCi: Official Code for Large-vocabulary forensic pathological analyses via prototypical cross-modal contrastive learning](https://github.com/shenxiaochenn/SongCi)
- **数据集**：TCGA-LUAD、TCGA-BRCA、CAMELYON-16、CRC-100K、UniToPatho、TCGA-TIL、TCGA Uniform Tumor、PCam以及自建数据集

## 摘要

法医病理学通过宏观与微观尸检在判定死因及死亡方式中发挥着关键作用。然而该领域面临结果变异性大、流程劳动密集及专业人才短缺等挑战。本文推出专为法医病理学设计的视觉语言模型“宋慈”，该模型采用先进的原型跨模态自监督对比学习技术，显著提升法医分析的准确性、效率与泛化能力。基于包含 1600 万张高分辨率图像切片、2228 组尸检全切片图像与大体关键发现的视觉-语言对，以及 471 种独特诊断结果的多中心大型数据集进行预训练与验证，“宋慈”在法医任务中展现出超越现有多模态模型与计算病理学基础模型的卓越性能，其能力媲美资深法医病理学家，显著优于经验不足的从业者，并提供可靠的多模态可解释性。

## 研究背景

法医病理学在确定死亡原因和方式、医学与法律分析等方面具有重要作用。但该领域存在结果高度依赖专家、主观性强、效率低、人才紧缺等挑战。近年来人工智能特别是自监督学习和多模态模型（视觉+文本）已在临床病理学取得突破，但直接迁移到法医领域效果有限，因为法医样本和任务具备特殊性（如多器官、多样化死亡原因、非癌相关等）。

## 主要贡献

### 数据集

<img src="Z:\Public\images\image-20250728155002925.png" alt="image-20250728155002925" style="zoom:50%;" />

收集了来自 3 个权威法医队列的 9 种不同器官的多中心数据集，共包含 2228 组视觉语言对：

- 死后WSI（图像）
- 器官层面大体关键发现（文本）
- 最终法医诊断结果（文本）

这些数据贡献了超过 1600 万张高分辨率图像块和 471 种不同诊断结果，其中仅 34 种诊断在所有法医中心间具有一致性

<img src="Z:\Public\images\image-20250728155254429.png" alt="image-20250728155254429" style="zoom:50%;" />

#### 数据预处理

**对于 WSI**

1. 通过OpenCV中的轮廓查找方法提取包含组织的区域
2. 分割区块

**对于大体关键发现**

1. 翻译为英文
2. 将关键发现文本标准化为统一长度以优化基础模型学习：“作为法医医学影像AI领域的教授，请将以下段落英译并压缩至不超过四句，确保符合学术写作规范，仅提供摘要内容”
3. 由两名法医病理学家审核验证处理文本

**对于法医病理学诊断**

汇编为短语

### 原型 patch 级编码器

### 门控注意力增强的多模态融合块



## 实验

### 原型空间可视化

<img src="Z:\Public\images\image-20250728155751545.png" alt="image-20250728155751545" style="zoom:50%;" />