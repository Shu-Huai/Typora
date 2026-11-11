# Large-vocabulary forensic pathological analyses via prototypical cross-modal contrastive learning

## 基本信息

- 通过原型跨模态对比学习进行大词汇量法医病理学分析
- **HuggingFace**：[shenxiaochen/SongCi · Hugging Face](https://huggingface.co/shenxiaochen/SongCi)（需申请）
- **GitHub**：[shenxiaochenn/SongCi: Official Code for Large-vocabulary forensic pathological analyses via prototypical cross-modal contrastive learning](https://github.com/shenxiaochenn/SongCi)
- **数据集**：TCGA-LUAD、TCGA-BRCA、CAMELYON-16、CRC-100K、UniToPatho、TCGA-TIL、TCGA Uniform Tumor、PCam 以及自建数据集

## 摘要

法医病理学通过宏观与微观尸检在判定死因及死亡方式中发挥着关键作用。然而该领域面临结果变异性大、流程劳动密集及专业人才短缺等挑战。本文推出专为法医病理学设计的视觉语言模型“宋慈”，该模型采用先进的原型跨模态自监督对比学习技术，显著提升法医分析的准确性、效率与泛化能力。基于包含 1600 万张高分辨率图像切片、2228 组尸检全切片图像与大体关键发现的视觉-语言对，以及 471 种独特诊断结果的多中心大型数据集进行预训练与验证，“宋慈”在法医任务中展现出超越现有多模态模型与计算病理学基础模型的卓越性能，其能力媲美资深法医病理学家，显著优于经验不足的从业者，并提供可靠的多模态可解释性。

## 研究背景

法医病理学在确定死亡原因和方式、医学与法律分析等方面具有重要作用。但该领域存在结果高度依赖专家、主观性强、效率低、人才紧缺等挑战。近年来人工智能特别是自监督学习和多模态模型（视觉+文本）已在临床病理学取得突破，但直接迁移到法医领域效果有限，因为法医样本和任务具备特殊性（如多器官、多样化死亡原因、非癌相关等）。

## 主要贡献

### 数据集

<img src="http://public.file.lvshuhuai.cn/images\image-20250728155002925.png" alt="image-20250728155002925" style="zoom:50%;" />

收集了来自 3 个权威法医队列的 9 种不同器官的多中心数据集，共包含 2228 组视觉语言对：

- 死后 WSI（图像）
- 器官层面大体关键发现（文本）
- 最终法医诊断结果（文本）

这些数据贡献了超过 1600 万 patch 图像块和 471 种不同诊断结果，其中仅 34 种诊断在所有法医中心间具有一致性

<img src="http://public.file.lvshuhuai.cn/images\image-20250728155254429.png" alt="image-20250728155254429" style="zoom:50%;" />

#### 数据预处理

**对于 WSI**

1. 通过 OpenCV 中的轮廓查找方法提取包含组织的区域
2. 分割区块

**对于大体关键发现**

1. 翻译为英文
2. 将关键发现文本标准化为统一长度以优化基础模型学习：“作为法医医学影像AI领域的教授，请将以下段落英译并压缩至不超过四句，确保符合学术写作规范，仅提供摘要内容”
3. 由两名法医病理学家审核验证处理文本

**对于法医病理学诊断**

汇编为短语

### 模型

#### 推理目标

模型接受多模态数据：来自不同器官的 WSI 和宏观大体发现

法医病理学家可以从不同角度提出多种诊断假设

模型给出可能的诊断结果

<img src="http://public.file.lvshuhuai.cn/images\image-20250731001240442.png" alt="image-20250731001240442" style="zoom:50%;" />

#### 主要架构

- 用于 WSI（切片级）特征提取的图像编码器
- 用于嵌入大体关键发现和诊断查询的文本编码器
- 以及一个多模态融合模块，整合了 WSI 和大体关键发现的嵌入，以与诊断查询的嵌入对齐

### 原型 patch 级编码器

<img src="http://public.file.lvshuhuai.cn/images\image-20250730215243333.png" alt="image-20250730215243333" style="zoom:50%;" />

由实例对比学习部分和原型对比学习部分组成。

这种原型空间建模方式使模型既能精准区分特定器官/病变特征，也能捕捉不同器官间共享的病理学变化，为下游任务（如自动分割、多模态融合）奠定基础。

#### 实例对比学习

通过教师-学生方式实现

学生模型：ViT、投影层、预测器

教师模型：ViT、投影层、锐化与中心化模块

对每一个实例，通过数据增强手段生成两个不同的视图，分别输入到学生分支和教师分支中

学生模型通过梯度反向传播更新，教师模型通过 EMA 更新
$$
p_s(X_s^n) = \frac{\exp\left( g_s^{pre}\left( g_s^{pro}(f_s(X_s^n)) \right) / \tau_s \right)}
{\sum_{n=1}^{N} \exp\left( g_s^{pre}\left( g_s^{pro}(f_s(X_s^n)) \right) / \tau_s \right)}
$$

$$
p_t(X_t^n) = \frac{\exp\left( J_t g_t^{pro}\left(f_t(X_t^n)\right) / \tau_t \right)}
{\sum_{n=1}^{N} \exp\left( J_t g_t^{pro}\left(f_t(X_t^n)\right) / \tau_t \right)},
$$

$$
L_{ins} = -\sum_n p_t(X_t^n) \log(p_s(X_s^n)).
$$

#### 原型对比学习

通过教师-学生方式实现、ViT、投影层

期望学习一组原型，每个原型是语义中心，代表一个常见的病理结构或状态。

同时要学习到一个从样本 patch 到原型的映射 $C_t$，这可以通过 Sinkhorn-Knopp 算法获得
$$
\hat{C}_t = \text{diag}(\mathbf{u}) \exp\left(\frac{\mathbf{P}^T \mathbf{Z}_t}{\epsilon}\right) \text{diag}(\mathbf{v})
$$
同时将这个 $C_t$ 作为伪标签约束学生分支的预测
$$
C_s = \frac{\exp(\mathbf{P}^T \mathbf{Z}_s / \tau_s^{\text{prototype}})}
{\sum_{m=1}^M \exp(\mathbf{P}^T \mathbf{Z}_s / \tau_s^{\text{prototype}})}
$$
对比学习
$$
L_{\text{prototype}} = -\sum \hat{c}_t \log(C_s)
$$

#### 正则化项

1. $L_{ipc}$：防止多个原型学习到**重复的特征模式**，提升原型多样性。
    $$
    L_{\text{ipc}} = -\sum_{i=1}^N \log\left( 
    \frac{\exp(\mathbf{z}_i^T \mathbf{p}_j)}
    {\sum_{j=1}^M \exp(\mathbf{z}_i^T \mathbf{p}_j)}
    \right)
    $$

2. $L_{ipd}$：进一步**拉开原型间距离**，防止原型挤在一起，增加判别能力。
    $$
    L_{\text{ipd}} = \sum_{i=1}^N (\mathbf{z}_i - \mathbf{p}_j^i)^2 = \sum_{i=1}^N \left(2 - 2\mathbf{z}_i^T \mathbf{p}_j^c\right)
    $$

3. $L_{me-max}$：鼓励每个 patch 只和少数几个原型关联，**增加表示的稀疏性和判别性**。
    $$
    L_{\text{me-max}} = \sum_{i=1}^M \bar{C}_s^i \log(\bar{C}_s^i) + \log(M),
    $$

### 门控注意力增强的多模态融合模块

<img src="http://public.file.lvshuhuai.cn/images\image-20250731001425292.png" alt="image-20250731001425292" style="zoom:50%;" />

#### 特征

- 图像特征：patch 对齐到原型特征，多个patch 特征组合成 WSI 的特征，再叠加上 WSI 中每个原型的出现次数
- 文本特征：使用 **PLIP**（一个专门为病理图像设计的多模态大模型）对 Gross key findings（肉眼观察文字）进行编码。
- 对图像和文本特征增加高斯噪声，以提高其对后续跨模态融合的鲁棒性

#### 门控交叉注意力机制

- 通过考虑来自另一模态的互补信息来更新每个模态的表示
- 使用 $z^t$ 作为指导，WSI 嵌入 $z^i$ 通过门控知识引导的交叉注意力层和随后的门控 FFN 进行更新
- 使用 $z^i$ 作为指导，$z^t$ 通过门控原型引导的交叉注意力层更新，随后是一个门控 FFN
- 拼接后使用基于门控 Transformer 的编码器
- 投影层

#### 大词汇量特性

- 不同的诊断结果与融合后的特征的不同部分相关联
- 使用 **冻结的 PLIP 文本编码器**编码该诊断语句
- 计算余弦相似度、计算注意力分数

## 实验

### 原型空间可视化

<img src="http://public.file.lvshuhuai.cn/images\image-20250728155751545.png" alt="image-20250728155751545" style="zoom:50%;" />

### patch 级生成

<img src="http://public.file.lvshuhuai.cn/images\image-20250730234356405.png" alt="image-20250730234356405" style="zoom:50%;" />

### 对比

<img src="http://public.file.lvshuhuai.cn/images\image-20250731011136764.png" alt="image-20250731011136764" style="zoom:50%;" />

## 实验复现

### SVS 图片

<img src="http://public.file.lvshuhuai.cn/images\image-20250731154256113.png" alt="image-20250731154256113" style="zoom:50%;" />

### patch 切分

![image-20250731154351353](http://public.file.lvshuhuai.cn/images\image-20250731154351353.png)

### 原型匹配

<img src="http://public.file.lvshuhuai.cn/images\image-20250731154442585.png" alt="image-20250731154442585" style="zoom:50%;" />

并统计其原型数量信息，形成

| name                | prototype                                                    | pro_num |
| ------------------- | ------------------------------------------------------------ | ------- |
| a21-1884_brain0.csv | {830: 1259, 555: 567, 786: 504, 535: 497, 857: 357, 965: 337, 771: 305, 286: 239, 1018: 220, 264: 189, 430: 164, 2: 148, 685: 144, 17: 140, 318: 115, 557: 114, 242: 102, 598: 101, 882: 100, 164: 91, 834: 85, 754: 83, 766: 80, 762: 79, 274: 77, 960: 74, 545: 72, 154: 61, 248: 57, 748: 51, 533: 49, 306: 47, 14: 41, 732: 41, 107: 37, 599: 35, 764: 31, 62: 29, 793: 28, 559: 27, 592: 27, 33: 23, 746: 22, 724: 20, 163: 19, 116: 19, 376: 17, 190: 15, 64: 14, 410: 13, 1002: 12, 991: 12, 787: 12, 297: 11, 715: 7, 747: 7, 988: 6, 484: 6, 739: 5, 360: 5, 435: 4, 756: 3, 877: 3, 760: 2, 485: 2, 999: 2, 478: 2, 147: 2, 367: 2, 621: 1, 424: 1, 623: 1, 120: 1, 139: 1, 922: 1, 976: 1, 401: 1, 556: 1, 768: 1, 433: 1} | 80      |

### 大体描述

Scattered punctate hemorrhage is observed under the occipital subcutaneous area, the dura and arachnoid are intact, and the surface and section of the brain are grayish white.

枕部皮下可见散在点状出血，硬脑膜及蛛网膜完整，脑表面及切面呈灰白色。

### 推理

#### 如有候选诊断

The hemorrhage under the scalp

头皮下出血

可以输出一个相似度

```python
tensor(0.8989),
```

#### 如无候选诊断

他给出了共 471 个常见诊断

<img src="http://public.file.lvshuhuai.cn/images\image-20250731155647877.png" alt="image-20250731155647877" style="zoom:50%;" />

计算每个的概率，得到最可能的诊断结果

```python
['The hemorrhage under the scalp',
 'Cerebral hemorrhage',
 'Cerebral congestion']
```