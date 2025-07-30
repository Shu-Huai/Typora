# Transformer-based Unsupervised Contrastive Learning for Histopathological Image Classification

## 基本信息

- 期刊：Medical Image Analysis
- 时间：2022年
- 作者：Xiyue Wang 等（四川大学 & 腾讯 AI Lab）
- 代码：[Xiyue-Wang/TransPath](https://github.com/Xiyue-Wang/TransPath?tab=readme-ov-file)

## 研究动机与问题

### 背景

- 病理图像（特别是 Whole Slide Images）具有尺寸巨大、类型多样、染色变化复杂等特点；
- 手工标注成本高，限制了监督学习方法在医学图像上的应用；
- 需要一种**自监督学习**方法，能在无需标注的情况下学习有效特征表示。

## 方法

### SRCL（语义相关对比学习）

#### 核心思想

传统对比学习（如 SimCLR）：

- 仅把同一个图像的两个增强视图作为正样本；

- 在病理图像中，这样做会把很多**语义相近的 patch 错误当作负样本**，降低性能。

    普通图像也存在这个问题，但在病理图像中被显著放大其局限性。由于病理切片内部结构高度重复且跨病例共享大量相似组织区域，不同图像之间往往存在大量视觉上相近但语义一致的 patch。例如，来自不同患者或不同 Whole Slide Image (WSI) 的腺体区域、肿瘤组织或血管结构，可能呈现几乎相同的形态学特征。在此背景下，若将这些结构相似的 patch 错误地视为负样本，将导致模型在训练过程中**人为拉远语义相似样本的表征**，损害表征的一致性与判别性。因此，针对病理图像任务的对比学习方法，需要更加细粒度地定义正负样本关系，充分挖掘跨图像的语义正样本。

SRCL 的目标：

- **从内存库中挖掘“语义相关的样本”作为额外正样本**；
- 增加正样本的多样性，提高学习到的特征的判别力与泛化性。

<img src="http://public.file.lvshuhuai.cn/images\image-20250619005703955.png" alt="image-20250619005703955" style="zoom:50%;" />

#### 基本流程

1. 对输入图像进行两次数据增强，得到两个视图；

2. 使用在线网络（online encoder）和目标网络（momentum encoder）提取特征向量；

    - 使用两个网络可以提高训练稳定性；
    - 避免模型“自我对比”时产生崩塌；
    - 目标网络为 memory bank 提供稳定的特征表示。

3. 构建大型 memory bank，记录历史样本特征；

4. 使用当前样本在 memory bank 中寻找 **余弦相似度最高的 S 个 patch**，作为“伪正样本”；

5. 构造多个正样本 vs 大量负样本，计算 **多正样本对比损失 SRCL loss**：
    $$
    \mathcal{L}_{\text{SRCL}} = -\log \frac{\sum_{i=1}^{S+1} \exp(\mathbf{z} \cdot \mathbf{z}_i^+ / \tau)}{\sum_{i=1}^{S+1} \exp(\mathbf{z} \cdot \mathbf{z}_i^+ / \tau) + \sum_{j=1}^{N} \exp(\mathbf{z} \cdot \mathbf{z}_j^- / \tau)}
    $$
    其中 $\mathbf{z}$：当前特征；$\mathbf{z}_i^+$：多个正样本；$\mathbf{z}_j^-$：负样本；$\tau$：温度系数。

### CTransPath（CNN + Swin Transformer 混合架构）

#### 结构组成

<img src="http://public.file.lvshuhuai.cn/images\image-20250619005911208.png" alt="image-20250619005911208" style="zoom:50%;" />

- CNN：三层卷积（3x3, 3x3, 1x1）提取局部特征；
- Swin Transformer：
    - 用于建模局部窗口内的多头注意力（W-MSA）；
    - 引入“Shifted Window”机制（SW-MSA）实现跨窗口的信息交互；
    - 使用层级结构实现类似 ResNet 的多尺度建模。

#### 目标

- CNN 让 Transformer 更稳定训练；
- 提取**局部 + 全局 + 多尺度特征**；
- 适配高分辨率、变异性强的医学图像。

## 实验设置

- **预训练数据**：TCGA + PAIP，1500 万个 1024×1024 patch；
- **下游任务**：
    1. Patch 检索（TissueNet, UniToPatho）
    2. Patch 分类（NCT-CRC-HE, CRC）
    3. 弱监督 WSI 分类（CAMELYON16, TCGA-LUAD, TCGA-RCC）
    4. 有丝分裂检测（MIDOG）
    5. 肠腺体分割（CRAG）

