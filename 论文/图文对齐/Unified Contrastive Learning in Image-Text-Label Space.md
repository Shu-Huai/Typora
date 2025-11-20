# Unified Contrastive Learning in Image-Text-Label Space

## 基本信息

- 图像-文本-标签空间中的统一对比学习
- CVPR 2022
- GitHub：[microsoft/UniCL: [CVPR 2022] Official code for "Unified Contrastive Learning in Image-Text-Label Space"](https://github.com/microsoft/UniCL)
- 微软团队

## 摘要

视觉识别技术目前主要通过两种方式实现：基于人工标注图像-标签数据的监督学习，或利用网络爬取的图像-文本对进行语言-图像对比学习。监督学习虽能产生更具判别性的表征，但语言-图像预训练展现出前所未有的零样本识别能力，这主要源于数据源与学习目标的本质差异。本研究提出一种新范式，将两类数据源整合至统一的图像-文本-标签空间，并在此空间中提出“统一对比学习”（UniCL）框架，通过单一学习目标无缝融合两种数据类型。大量实验表明，UniCL 能有效学习语义丰富且判别性强的表征，在零样本识别、线性探测、全微调和迁移学习等场景中均表现优异。具体而言，其在零样本识别基准测试中平均超越语言-图像对比学习方法 9.2%，超越监督学习方法 14.5%；在线性探测任务中分别提升 7.3% 和 3.4%。研究还发现，UniCL 仅使用纯图像-标签数据时，在 ResNet 和 Swin Transformer 两种视觉骨干网络上，其性能与监督学习方法相当。代码已开源：https://github.com/microsoft/UniCL。

## 研究背景

- 视觉表示学习主要有两条路线：**监督学习（image–label）** 与 **图文对比学习（image–text）**。前者依赖高质量标注，判别性强；后者来自大规模网络图文对，覆盖概念广、具零样本泛化，但判别性常不足。作者提出将两类数据统一到一个**图像–文本–标签空间**，以单一目标同时学习“广覆盖 + 强判别”的表征。  
- 在该空间中，每个监督标签都可对应到一个**文本概念**，而每个图文对天然带有**唯一标签**，从而两类数据可在同一框架下处理。基于此提出 **Unified Contrastive Learning (UniCL)**，用统一的双向对比学习目标联合训练视觉与文本编码器，获得语义丰富且判别性强的表示，适用于零样本、线性探针、全量微调与迁移设置。  

<img src="http://public.file.lvshuhuai.cn/images\image-20251013210142319.png" alt="image-20251013210142319" style="zoom:50%;" />

## 主要方法

### 预备知识

- **统一三元组表示**：数据被写成
  $$
  \mathcal{S}=\{(x_n, t_n, y_n)\}_{n=1}^N
  $$
  其中 $x$ 为图像，$t$ 为语言描述（从类别名到自由文本），$y$ 为将“同义/同类文本”归并后的**标签索引**。  

  - 对于**图文对**：一图一文一标签，$\mathcal{S}=\{(x_n, t_n, y_n\equiv n)\}$；  
  - 对于**图像-标签**：将类别名当作文本 $t\equiv C[y]$，即 $\mathcal{S}=\{(x_n, C[y_n], y_n)\}$。  
  
- **编码与相似度**：视觉编码器 $f_\theta$、文本编码器 $f_\phi$；对一个 batch 中第 $i$ 个图像与第 $j$ 个文本，先做 $\ell_2$ 归一化
  $$
  u_i=\frac{f_\theta(x_i)}{\lVert f_\theta(x_i)\rVert},\quad v_j=\frac{f_\phi(t_j)}{\lVert f_\phi(t_j)\rVert},
  $$
  相似度
  $$
  s_{ij}=u_i^\top v_j.
  $$
  
- **正样本集合**：设 batch 索引集合为 $B$，以标签一致性定义图像（或文本）的正样本集合
  $$
  P(i)=\{k\in B\mid y_k=y_i\},\qquad P(j)=\{k\in B\mid y_k=y_j\}.
  $$

<img src="http://public.file.lvshuhuai.cn/images\image-20251013210323497.png" alt="image-20251013210323497" style="zoom:50%;" />

### 统一图像-文本-标签对比

#### 双向对比总体目标（Bi-directional Contrast）

$$
\min_{\theta,\phi}\; \mathcal{L}_{\mathrm{BiC}}=\mathcal{L}_{i\to t}+\mathcal{L}_{t\to i}
$$

温度系数 $\tau$ 控制对困难负样本的惩罚强度。

#### 图像→文本（行方向）

$$
\mathcal{L}_{i\to t}=-\sum_{i\in B}\frac{1}{|P(i)|}\sum_{k\in P(i)} 
\log\frac{\exp\big(\tau\,u_i^\top v_k\big)}{\sum_{j\in B}\exp\big(\tau\,u_i^\top v_j\big)}
$$

#### 文本→图像（列方向）

$$
\mathcal{L}_{t\to i}=-\sum_{j\in B}\frac{1}{|P(j)|}\sum_{k\in P(j)} 
\log\frac{\exp\big(\tau\,u_k^\top v_j\big)}{\sum_{i\in B}\exp\big(\tau\,u_i^\top v_j\big)}
$$

#### 与现有范式的等价/联系

- **退化为 CLIP/ALIGN**：若 batch 内图文一一对应，则 $P(i)=\{i\},P(j)=\{j\}$，上式退化为 CLIP 的双向 InfoNCE：
  $$
  \mathcal{L}_{i\to t}=-\sum_{i\in B}\log\frac{\exp(\tau\,u_i^\top v_i)}{\sum_{j\in B}\exp(\tau\,u_i^\top v_j)},\quad
  \mathcal{L}_{t\to i}=-\sum_{j\in B}\log\frac{\exp(\tau\,u_j^\top v_j)}{\sum_{i\in B}\exp(\tau\,u_i^\top v_j)}
  $$
  
- **与交叉熵（CE）的关系**：当仅用 $\mathcal{L}_{t\to i}$，并将文本编码器设为线性分类器（$f_\phi(t)=W^\top t + b$），在适当条件下可化为标准 CE：  
  $$
  \min_{\theta,W}\; \mathcal{L}_{\mathrm{CE}}=\sum_{j\in B}
  \log\frac{\exp(w_{\,\hat y}^\top \tilde v_j + b_{\hat y})}{\sum_{k=1}^K \exp(w_k^\top \tilde v_j + b_k)}
  $$
  
- **与 SupCon 的关系**：两者都使用**标签引导的对比**（同标签计入分子为正样本），但 SupCon 属于**同模态图像-图像**对比、共享一个图像编码器；UniCL 则是**跨模态图像-文本**双编码器。

- **“软目标”视角**：按 $\frac{1}{|P(\cdot)|}$ 对同标签正样本求均值，等价于使用**软目标分布**（同标签均匀分配到正样本），对 logits 施加**软目标交叉熵**。

### 讨论与属性

- **统一性**：在图像–文本–标签空间中，**image–label 可视作“带文本的监督样本”**（标签名即文本），**image–text 可视作“唯一标签样本”**；因此两类数据可被同一损失无缝处理。  
- **正则化效应**：相较只用 CE，加入 $i\to t$ 项会把**同一语义的多张图像**聚到其文本特征附近，缓解过拟合。  
- **可扩展的文本侧**：文本编码器可采用更强大的 Transformer/BERT，且能处理**自由文本**，不仅限于类别名。  
- **性质对比**：  
  - 对比 **SupCon**：UniCL 的查询/键是**跨模态**（图像↔文本），并行学习语义对齐；  
  - 对比 **CLIP**：当存在**类内多图像对应同一文本/标签**时，UniCL 会把这些样本都计为正样本进入分子，显式利用**类内多正样本**结构。  

### 模型训练与适配

#### 训练流程（要点）

1) 数据加载时将图文对的初始标签设为 $y=0$，图像-标签对的标签为 $y\in[1,\dots,K]$；  
2) **TargetM** 函数在每个 batch 内为**每条唯一文本**分配一个**唯一标签索引**，从而把图文对也映射到统一标签空间；  
3) 计算 $u=\mathrm{norm}(f_\theta(x))$、$v=\mathrm{norm}(f_\phi(t))$，logits 为 $\exp(\tau)\cdot u v^\top$；  
4) 使用**软目标交叉熵**分别计算 $\mathcal{L}_{i\to t}$ 与 $\mathcal{L}_{t\to i}$，总损失为两者均值回传；  
5) 训练后得到的 $\{f_\theta,f_\phi\}$ 可直接用于**开放词表识别（零样本）**；仅用 $f_\theta$ 亦可做**线性探针**或**检测微调**。  

#### 下游评测设定（概览）

零样本（ImageNet-1K + 14 数据集平均）、线性探针（18 数据集平均，自动调参保证公平）、检测（Mask R-CNN，COCO 上 box/mask mAP）。  

## 实验

<img src="http://public.file.lvshuhuai.cn/images\image-20251013210432825.png" alt="image-20251013210432825" style="zoom:50%;" />