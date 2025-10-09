# A visual–language foundation model for pathology image analysis using medical Twitter

## 基本信息

- 一种基于视觉-语言基础模型的病理图像分析工具，利用医学推特数据
- PLIP
- Nature Medicine
- GitHub：[PathologyFoundation/plip: Pathology Language and Image Pre-Training (PLIP) is the first vision and language foundation model for Pathology AI (Nature Medicine). PLIP is a large-scale pre-trained model that can be used to extract visual and language features from pathology images and text description. The model is a fine-tuned version of the original CLIP model.](https://github.com/PathologyFoundation/plip)
- 实际上就是在医疗推特上搜集图文对，构建数据集，然后在 CLIP 上微调，以获得在医学领域的效果提升

## 摘要

公开可用的标注医学图像数据匮乏是计算研究与教育创新的主要障碍。与此同时，临床医师常在医学推特等公共论坛分享大量去标识化图像与专业知识。本研究利用此类众包平台构建了 OpenPath 数据集——包含 208,414 张病理图像及对应自然语言描述的大规模数据集。我们通过训练多模态人工智能“病理语言-图像预训练模型（PLIP）”验证该资源价值，该模型具备图像与文本双重理解能力。PLIP 在四个外部数据集的新病理图像分类任务中表现卓越：零样本分类的 F1 分数达 0.565–0.832，显著优于此前对比式语言-图像预训练模型的 0.030–0.481。基于 PLIP 嵌入向量训练的简易监督分类器，其 F1 分数相较其他监督模型嵌入也提升2.5%。此外，PLIP 支持通过图像或自然语言检索相似病例，极大促进知识共享。本研究表明，公开共享的医学信息可作为开发医疗人工智能的宝贵资源，助力诊断提升、知识传播与医学教育。

## 主要方法

### 数据集

#### 数据来源与时间窗口

<img src="http://public.file.lvshuhuai.cn/images\image-20251007152929472.png" alt="image-20251007152929472" style="zoom:50%;" />

- **Twitter（X）主语料**：依据 32 个病理子专科话题标签与相关关键词，收集英文推文与配图。
    - 推文本体时间：**2006-03-21 — 2022-11-15**。
    - 会话回复时间：**2006-03-21 — 2022-11-22**。
- **Twitter 验证集**（仅用于检索评估）：**2022-11-16 — 2023-01-15** 的新增样本。
- **PathLAION 子集**：以 Twitter 病理图像为“查询”，从 LAION-5B 中检索相似病理图像及其配文，构成病理相关的外部补充语料。

#### 初始规模（去重前的抓取）

- 推文本体：**232,067** 条推文，**243,375** 个图文对。
- 高赞回复：在含回复的推文中，筛得 **88,250** 条“最高点赞且含 ICD‑11 关键词”的回复配图。

#### 纳入与排除（严格过滤）

- 排除：含敏感/识别性信息、重复图文对、无法下载/损坏图片、被病理图像分类器判定为“非病理”的图片、以及**问号文本**（疑问句通常不提供确定性的图像描述）。
- 保留：语义明确、与图像强相关的文本描述；仅保留英文。

#### 过滤后的 Twitter 语料

- 推文本体：**116,504** 个图像—文本对。
- 高赞回复：**59,869** 个图像—文本对。

#### PathLAION（病理子集）的构建

- 以 Twitter 中的病理图像作为查询，按 **CLIP 图像嵌入的余弦相似度**，为每张图像检索前若干千张相似图；在约 **1,000** 张示例图上重复并合并，严格**去重**（与 Twitter 集合不重叠）。
- 得到 **32,041** 张病理相关图像及配文。

#### OpenPath 的最终规模

<img src="http://public.file.lvshuhuai.cn/images\image-20251007153005150.png" alt="image-20251007153005150" style="zoom:50%;" />

- 将“推文本体 + 高赞回复 + PathLAION”合并、去重与合规性检查后，形成 **OpenPath：208,414** 个病理图像—文本配对样本。

#### 发布与合规

- 以 **Tweet ID / 原始链接** 的方式发布可复现清单；用户需基于原始来源判断与遵循平台政策。

### 模型

<img src="http://public.file.lvshuhuai.cn/images\image-20251007153325499.png" alt="image-20251007153325499" style="zoom:50%;" />

#### 总体框架

- 模型名称：**PLIP（Pathology Language–Image Pretraining）**。
- 训练范式：**CLIP 式对比学习**，在统一嵌入空间对齐图像与文本，使匹配对相似度更高、不匹配对更低。

#### 编码器与嵌入空间

- **图像编码器**：Vision Transformer **ViT‑B/32**，输入统一为 **224×224**。
- **文本编码器**：Transformer；文本长度上限 **76 tokens**（超过将截断）。
- **投影与表示**：图像/文本分别映射为 **512 维**向量，用于相似度与下游任务。

#### 图像与文本预处理

- **图像**：将最短边限制在不超过 512 像素，随机裁剪至 **224×224**，常规增广后送入 ViT‑B/32。
- **文本**：清理 URL/表情/冗余标注与明显无关内容，保持与图像内容直接相关的描述。

#### 训练目标与损失

- **批内对比损失（InfoNCE/softmax 形式）**：最大化配对样本的余弦相似度，最小化非配对样本；包含**可学习温度**/缩放参数以稳定训练。

### 训练与模型选择

- **数据组合搜索**：在（推文本体 / 高赞回复 / PathLAION / 全量）等组合上进行比较，
    - 结果：**全量数据组合**最优。
- **超参选择**：以**线性探测**在多数据集上的宏 F1 为目标做网格搜索，
    - 训练 **12 个 epoch**，每 **1/4 epoch** 评估一次，累计 **10** 次评估；
    - 最优学习率 **1e‑5**（其余训练细节按论文默认设置执行）。

### 推理与任务化接口

- **零样本分类**：将各候选标签转成提示句（templates）并编码，与图像嵌入做余弦相似度，取最大者为预测。
- **线性探测**：冻结图像编码器，仅在嵌入上训练线性分类器以适配新数据集。
- **跨模态检索**：
    - 文本→图像：文本嵌入检索图库图像嵌入；
    - 图像→图像：查询图像嵌入检索相似图像嵌入。

## 实验

<img src="http://public.file.lvshuhuai.cn/images\image-20251007153607405.png" alt="image-20251007153607405" style="zoom:50%;" />