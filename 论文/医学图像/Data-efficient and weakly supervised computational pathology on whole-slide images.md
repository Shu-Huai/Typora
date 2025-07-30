# Data-efficient and weakly supervised computational pathology on whole-slide images

## 基本信息

- **作者**：Ming Y. Lu 等
- **期刊**：Nature Biomedical Engineering
- **发表时间**：2021
- **开源地址**：https://github.com/mahmoodlab/CLAM
- **研究领域**：计算病理学、弱监督学习、深度学习、多实例学习（MIL）

## 研究背景与动机

- **Whole-slide images (WSIs)** 是病理诊断中常见的图像形式，但图像体积巨大（gigapixel级别），手动标注成本极高。
- 传统深度学习需 pixel/ROI 级别标注，数据依赖大，可解释性差。
- 弱监督学习（如 MIL）虽降低标注需求，但常常存在如下问题：
    - 训练不稳定
    - max pooling 使用信息有限
    - 不能很好支持多分类任务
    - 泛化能力差

**论文目标**：设计一种弱监督、数据高效、可解释、可推广的病理图像分类方法。

## 方法概述：CLAM（Clustering-constrained Attention MIL）

> CLAM 是一种改进的 attention-based 多实例学习方法，适用于多分类任务。

<img src="http://public.file.lvshuhuai.cn/images\image-20250619010214901.png" alt="image-20250619010214901" style="zoom:50%;" />

### 核心模块

#### Attention-based pooling

- CLAM 利用 **可训练的注意力机制** 为每个 patch 分配一个 attention score，代表其对 slide-level 分类的贡献。
- 相比 max pooling 只利用“最重要的一个 patch”，attention pooling 是一种 **加权平均机制**，使所有 patch 对最终预测都有影响，且权重由 attention 分支学习得出。
- 在多分类任务中，每一类都有一个单独的 attention 分支，分别为该类的 patch 分配权重。
- 注意力得分不仅用于分类聚合，也用于生成可解释的 heatmap。

**公式**（每类一组 attention）：
$$
a_{i,k} = \frac{\exp(w_i \cdot \text{tanh}(Vh_k) \odot \text{sigm}(Uh_k))}{\sum_j \exp(w_i \cdot \text{tanh}(Vh_j) \odot \text{sigm}(Uh_j))}
$$

#### 多分支 attention 模块

**目标**：使模型能够处理多分类任务并识别每类的特定特征区域。

- 每一个类别对应一个独立的 attention 分支和分类器分支。
- 每个分支只聚焦该类别可能出现的关键区域（高 attention score），从而提高类之间的可分性。
- 每个类别最终获得一个独立的 slide-level 表征，这些表征被分类层转化为分类分数。

**优点**：

- 适用于病理图像中的 **亚型识别** 和 **多类别组织分类**；
- 相较于单分支模型，对混合型和不均衡类别的识别更鲁棒。

| Patch ID | 特征向量 $h_k$             | Attention (CCRCC 分支) | Attention (PRCC 分支) | Attention (CRCC 分支) |
| -------- | -------------------------- | ---------------------- | --------------------- | --------------------- |
| Patch_1  | $h_1 \in \mathbb{R}^{512}$ | 0.60                   | 0.10                  | 0.05                  |
| Patch_2  | $h_2$                      | 0.05                   | 0.70                  | 0.02                  |
| Patch_3  | $h_3$                      | 0.20                   | 0.15                  | 0.50                  |
| Patch_4  | $h_4$                      | 0.05                   | 0.05                  | 0.10                  |

#### Instance-level clustering 约束

**目标**：增强特征空间的可区分性，避免 attention 仅仅起到“聚合”的作用，而不优化特征。

- 通过注意力得分对每个类别选出 **高关注度（前B）和低关注度（后B）** 的 patch；
- 高 attention patch 被视为正样本、低 attention patch 被视为负样本，进行 **伪标签聚类监督**；
- 利用额外的全连接层进行二分类（正/负实例聚类）训练；
- 该聚类监督作为辅助任务，与主任务的 slide-level 分类联合训练。

**进一步的监督策略**：

- 如果类别是**互斥**（如 RCC 三亚型），则其他 attention 分支的高分 patch 也视为“伪负例”，用于负向训练；
- 如果是癌/非癌任务（可能混合），则跳过这个额外负向监督。

**损失函数**：

- 使用 **Smooth SVM Loss** 替代 cross-entropy，对伪标签的不确定性更容忍，梯度平滑，更适合深度神经网络优化。

#### 高效特征处理

- 使用预训练 CNN 提取 patch-level 特征（如 ResNet50），减少计算负担；
- 在低维空间完成训练和推理。

## 实验设置与结果

### 任务与数据集

| 任务                        | 类型   | 数据集                    |
| --------------------------- | ------ | ------------------------- |
| 肾细胞癌亚型分类（3类）     | 多分类 | TCGA-KIRC/KIRP/KICH + BWH |
| 非小细胞肺癌亚型分类（2类） | 二分类 | TCGA/CPTAC + BWH          |
| 乳腺癌淋巴结转移检测        | 二分类 | CAMELYON16/17 + BWH       |

### 结果亮点

- **高准确率**：在所有任务上AUC均 > 0.95；
- **数据高效**：使用25%训练数据即可达到 0.9+ AUC；
- **对比优越性**：优于传统 MIL 和“Same Label”方法；
- **泛化性强**：
    - 能适应独立测试集（不同医院、不同扫描仪）；
    - 可直接应用于 biopsy slide 和 手机拍摄显微图（CPIs）；
- **可解释性强**：
    - 可视化 attention 热力图，匹配病理特征；
    - 支持高分辨率、全图级可视化。

## 实验复现

### 数据集

- 硅藻

![AFS_11](http://public.file.lvshuhuai.cn/images\AFS_11.jpg)

### 步骤

#### 分割

将其分割成若干 256*256 的 patch

```bash
python create_patches_fp.py --source DATA_DIRECTORY --save_dir RESULTS_DIRECTORY --patch_size 256 --seg --patch --stitch
```

![image-20250618173948599](http://public.file.lvshuhuai.cn/images\image-20250618173948599.png)

- masks 文件夹保存分割结果示例图片（每个 svs 文件对应一张图片）
- patches 文件夹保存分割结果图片存一个 h5 文件，每一行对应一个 patch 左上角坐标（每个 svs 文件对应一个h5文件）
- stitches 文件夹保存分割后的 patch 整体的可视化示例图（每个 svs 文件对应一张图片）
- 一个 csv 文件，包含被处理的 slide 相关信息，以及分割所涉及的参数

#### 提取特征

```bash
python extract_features_fp.py --data_h5_dir RESULTS_DIRECTORY --data_slide_dir DATA_DIRECTORY --csv_path RESULTS_DIRECTORY/process_list_autogen.csv --feat_dir FEATURES_DIRECTOR/diatom --batch_size 512 --slide_ext .svs
```

- h5 文件中每一行对应一个 patch，保存该 patch 的左上角坐标和经过特征提取后的特征（同时带有降维作用）
- pt 文件只包含 patch 特征，用于快速训练

#### 划分测试集

```bash
python create_splits_seq.py --task diatom --seed 1 --label_frac 0.75 --k 10
```

#### 训练

```python
python main.py --drop_out 0.25 --early_stopping --lr 2e-4 --k 10 --label_frac 0.75 --exp_code diatom_75 --weighted_sample --bag_loss ce --inst_loss svm --task diatom --model_type clam_mb --log_data --data_root_dir FEATURES_DIRECTORY --subtyping --model_size big
```

#### 测试

```python
python eval.py --drop_out 0.25 --k 10 --models_exp_code diatom_75_s1 --save_exp_code diatom_75_s1_CV --task diatom --model_type clam_mb --results_dir results --data_root_dir FEATURES_DIRECTORY --model_size big
```

| test_auc | val_auc | test_acc            | val_acc            |
| -------- | ------- | ------------------- | ------------------ |
| 0.0      | 1.0     | 0.33333333333333337 | 1.0                |
| 0.5      | 1.0     | 0.6666666666666667  | 0.6666666666666667 |
| 1.0      | 0.5     | 0.6666666666666667  | 0.6666666666666667 |
| 1.0      | 0.5     | 1.0                 | 0.6666666666666667 |
| 1.0      | 0.0     | 0.6666666666666667  | 0.6666666666666667 |
| 1.0      | 0.5     | 0.6666666666666667  | 0.6666666666666667 |
| 1.0      | 1.0     | 1.0                 | 0.6666666666666667 |
| 0.5      | 1.0     | 0.6666666666666667  | 1.0                |
| 0.0      | 0.5     | 0.0                 | 0.6666666666666667 |
| 1.0      | 1.0     | 1.0                 | 1.0                |

#### 热力图可视化

```python
python create_heatmaps.py --config config_template.yaml
```

<img src="http://public.file.lvshuhuai.cn/images\image-20250618233253259.png" alt="image-20250618233253259" style="zoom:25%;" />