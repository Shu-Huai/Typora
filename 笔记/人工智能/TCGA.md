# TCGA

## 数据集介绍

#### 基本信息

TCGA（癌症基因组图谱，The Cancer Genome Atlas）是由美国国立癌症研究所（NCI）和国家人类基因组研究所（NHGRI）共同发起的大型癌症研究项目。它致力于通过基因组测序等高通量生物技术手段，系统性地收集、分析和共享多种癌症类型的临床和组学数据。

TCGA 数据集覆盖了 30 多种癌症类型，包括肺癌、乳腺癌、肝癌、结直肠癌等，包含以下类型的数据：

- 临床信息（如生存时间、治疗方案）
- 转录组（RNA-seq）
- 表观遗传组（如 DNA 甲基化）
- 突变信息（SNV、CNV 等）
- 病理切片图像（WSI）

该数据集广泛用于癌症分类、预后预测、基因突变分析、机器学习建模等研究。

### 分类

| 缩写     | 全称（英文）                                                 | 中文名称               |
| -------- | ------------------------------------------------------------ | ---------------------- |
| **ACC**  | Adrenocortical Carcinoma                                     | 肾上腺皮质癌           |
| **BLCA** | Bladder Urothelial Carcinoma                                 | 膀胱尿路上皮癌         |
| **BRCA** | Breast Invasive Carcinoma                                    | 乳腺浸润性癌           |
| **CESC** | Cervical Squamous Cell Carcinoma and Endocervical Adenocarcinoma | 宫颈鳞癌及内宫颈腺癌   |
| **CHOL** | Cholangiocarcinoma                                           | 胆管癌                 |
| **COAD** | Colon Adenocarcinoma                                         | 结肠腺癌               |
| **DLBC** | Lymphoid Neoplasm Diffuse Large B-cell Lymphoma              | 弥漫性大B细胞淋巴瘤    |
| **ESCA** | Esophageal Carcinoma                                         | 食管癌                 |
| **GBM**  | Glioblastoma Multiforme                                      | 多形性胶质母细胞瘤     |
| **HNSC** | Head and Neck Squamous Cell Carcinoma                        | 头颈鳞状细胞癌         |
| **KICH** | Kidney Chromophobe                                           | 肾嗜酸细胞癌           |
| **KIRC** | Kidney Renal Clear Cell Carcinoma                            | 肾透明细胞癌           |
| **KIRP** | Kidney Renal Papillary Cell Carcinoma                        | 肾乳头状细胞癌         |
| **LAML** | Acute Myeloid Leukemia                                       | 急性髓性白血病         |
| **LGG**  | Brain Lower Grade Glioma                                     | 低级别神经胶质瘤       |
| **LIHC** | Liver Hepatocellular Carcinoma                               | 肝细胞癌               |
| **LUAD** | Lung Adenocarcinoma                                          | 肺腺癌                 |
| **LUSC** | Lung Squamous Cell Carcinoma                                 | 肺鳞癌                 |
| **MESO** | Mesothelioma                                                 | 间皮瘤                 |
| **OV**   | Ovarian Serous Cystadenocarcinoma                            | 卵巢浆液性囊腺癌       |
| **PAAD** | Pancreatic Adenocarcinoma                                    | 胰腺腺癌               |
| **PCPG** | Pheochromocytoma and Paraganglioma                           | 嗜铬细胞瘤与副神经节瘤 |
| **PRAD** | Prostate Adenocarcinoma                                      | 前列腺腺癌             |
| **READ** | Rectum Adenocarcinoma                                        | 直肠腺癌               |
| **SARC** | Sarcoma                                                      | 肉瘤                   |
| **SKCM** | Skin Cutaneous Melanoma                                      | 皮肤黑色素瘤           |
| **STAD** | Stomach Adenocarcinoma                                       | 胃腺癌                 |
| **TGCT** | Testicular Germ Cell Tumors                                  | 睾丸生殖细胞瘤         |
| **THCA** | Thyroid Carcinoma                                            | 甲状腺癌               |
| **THYM** | Thymoma                                                      | 胸腺瘤                 |
| **UCEC** | Uterine Corpus Endometrial Carcinoma                         | 子宫内膜癌             |
| **UCS**  | Uterine Carcinosarcoma                                       | 子宫癌肉瘤             |
| **UVM**  | Uveal Melanoma                                               | 葡萄膜黑色素瘤         |

## 获取方式

TCGA 数据的访问主要通过 GDC（Genomic Data Commons）平台，网址如下：**https://portal.gdc.cancer.gov/**

### 通过 Web 下载

#### 主页面

<img src="Z:\Public\images\image-20250619132312680.png" alt="image-20250619132312680" style="zoom:50%;" />

点击 Cohort Builder

#### Cohort Builder

![image-20250619132555042](Z:\Public\images\image-20250619132555042.png)

选中要下载的分类，并保存一个新的 Cohort。

#### Repository

然后进入 Repository

我们要下载 SVS 文件

<img src="Z:\Public\images\image-20250619132658143.png" alt="image-20250619132658143" style="zoom:50%;" />

在左边筛选出 Diagnostic Slide，右边出现的就是所有的 SVS 文件。

Annatations 项，记录的是对应该 SVS 文件是否有标签。

## 示例

![TCGA-55-8203-01Z-00-DX1.f530d261-be19-4ff0-98d0-27b789dffb23](Z:\Public\images\TCGA-55-8203-01Z-00-DX1.f530d261-be19-4ff0-98d0-27b789dffb23.jpg)

| id                                   | submitter_id | entity_type | entity_id                             | category         | classification | created_datetime    | status   | notes                                                        |
| ------------------------------------ | ------------ | ----------- | ------------------------------------- | ---------------- | -------------- | ------------------- | -------- | ------------------------------------------------------------ |
| fb4b01ad-035d-5967-ad35-3fe7030db5f5 | 11745        | case        | 9a9bd705-1ef1-4a6c-bb1e-bdd34 6dc01c0 | Prior malignancy | Notification   | 2012-10-31T00:00:00 | Approved | Prior malignancy chronic lymphocytic leukemia. Prior malignancy skin cancer. No systemic chemotherapy or radiation. |

Prior malignancy chronic lymphocytic leukemia. Prior malignancy skin cancer. No systemic chemotherapy or radiation.

既往恶性肿瘤为慢性淋巴细胞白血病。既往恶性肿瘤为皮肤癌。未进行全身化疗或放疗。