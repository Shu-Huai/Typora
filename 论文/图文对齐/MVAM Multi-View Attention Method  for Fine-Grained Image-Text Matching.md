# MVAM: Multi-View Attention Method  for Fine-Grained Image-Text Matching

## 基本信息

- MVAM：面向细粒度图文匹配的多视角注意力方法
- ECIR 2025（CCF C）

## 摘要

现有双流模型（如CLIP）通过独立表征编码图像与文本，在保证检索速度的同时展现出良好性能，已受到工业界与学术界关注。然而单一表征往往难以完整捕捉复杂内容，此类模型在匹配时可能忽略细粒度信息，导致检索结果欠佳。为突破这一局限并提升双流模型性能，我们提出面向图文匹配的多视角注意力方法（MVAM）。该方法利用具有独特视角编码的多样化注意力头来学习图像与文本的多重表征，继而进行拼接匹配。我们还引入多样性目标函数，显式促使各注意力头关注输入数据的不同方面，从而捕捉互补的细粒度细节。这种多样性使模型能从多角度表征图文对，确保对关键内容更全面的理解与对齐。我们的方法使模型能从不同视角编码图像与文本，并聚焦更关键的细节，从而获得更优的匹配性能。在 MSCOCO 和 Flickr30K 数据集上的实验表明本方法优于现有模型，进一步案例研究表明不同注意力头可聚焦差异化内容，实现更全面的表征。

## 研究背景

- 两路（two-stream）图文匹配模型将图像与文本分别编码成向量，再用相似度做对比学习，具备**检索高效**与**实现简单**的优势
- 但单一全局向量往往难以覆盖复杂样本的细粒度信息
- MVAM 的核心思想是：为同一样本学习**多视角（multi-view）表示**，通过注意力在图像/文本的隐藏状态上生成多份互补特征并用于匹配。

<img src="http://public.file.lvshuhuai.cn/images\image-20251013172046332.png" alt="image-20251013172046332" style="zoom:50%;" />

## 主要方法

### 双流图文匹配模型

#### 图像编码器（标准 ViT）

输入图像切成 patch 序列并在前置入 `[IMG]`，经 Transformer 得到隐藏状态 $H_v=\{h_{\text{[IMG]}},h^v_1,\dots,h^v_N\}$，再对 `[IMG]` 的隐藏向量做池化得到图像表示
$$
H_v=\text{Transformer}([\text{[IMG]};V_p]),\quad R_v=\text{Pool}(h_{\text{[IMG]}}).
$$

#### 文本编码器（标准 BERT）

句子标上 `[CLS],[SEP]`，经 Transformer 得到隐藏状态 $H_t=\{h_{\text{[CLS]}},h^t_1,\dots,h^t_L,h_{\text{[SEP]}}\}$，以 `[CLS]` 的隐藏向量池化为文本表示
$$
H_t=\text{Transformer}([\text{[CLS]};T;\text{[SEP]}]),\quad R_t=\text{Pool}(h_{\text{[CLS]}})
$$

### 训练目标

- **匹配分数**：余弦相似度 $\cos(R_v,R_t)$。批内对比学习包含 i2t 与 t2i 两个方向。设 batch 大小为 $B$，第 $i$ 个正配对为 $(R^i_v,R^i_t)$，则

    图像→文本（i2t）：
    $$
    \text{loss}_{\text{i2t}}=-\frac{1}{B}\sum_{i=1}^{B}\log\frac{e^{\cos(R^i_v,R^i_t)}}{\sum_{j=1}^{B}e^{\cos(R^i_v,R^j_t)}}
    $$

- 文本→图像（t2i）同理定义 $\text{loss}_{\text{t2i}}$。

- **最终对比损失**：
    $$
    \text{loss}_{\text{cl}}=\tfrac{1}{2}\big(\text{loss}_{\text{i2t}}+\text{loss}_{\text{t2i}}\big)
    $$

### 使用多视角注意力方法（MVAM）进行编码

<img src="http://public.file.lvshuhuai.cn/images\image-20251013172845166.png" alt="image-20251013172845166" style="zoom:50%;" />

- **思路**：在编码器输出的隐藏状态上，引入 $m$ 个可学习**视角代码** $c^1_v,\dots,c^m_v \in\mathbb{R}^D$（文本端同理），作为查询计算注意力，得到 $m$ 个视角特征并拼接为最终表示。 

- **图像端公式**（文本端同构）：
    $$
    a^i_v=\text{softmax}(H_v * c^i_v)\\
    F^i_v=\sum_{j=0}^{N} a^{(i,j)}_v \cdot H^j_v\\
    R^{*}_v=[F^1_v;F^2_v;\dots;F^m_v]
    $$
    其中 $H_v=\{H^0_v{=}h_{\text{[IMG]}},H^1_v,\dots,H^N_v\}$

#### 多视图多样性损失

- 令各视角的注意力权重按列组成 $A_v=[a^1_v,\dots,a^m_v]$（文本端记为 $A_t$）。为鼓励视角之间关注互补区域，引入多样性损失（Frobenius 范数）：
    $$
    \text{loss}^{v}_{\text{div}}=\left\|A_vA_v^{\top}-I\right\|_F^{2}\ ,\qquad  \text{loss}^{t}_{\text{div}}=\left\|A_tA_t^{\top}-I\right\|_F^{2}
    $$

- **平方根变体**：设 $E=\sqrt{A_v}$（按元素或矩阵意义在文中给出），可写为
    $$
    \text{loss}^{v\prime}_{\text{div}}=\left\|EE^{\top}-I\right\|_F^{2}
    $$

- **总损失**（把图像与文本两端的多样性损失相加，并与对比损失加权求和）：
    $$
    \text{loss}_{\text{div}}=\text{loss}^{v}_{\text{div}}+\text{loss}^{t}_{\text{div}},\qquad \text{loss}=\text{loss}_{\text{cl}}+\beta\cdot \text{loss}_{\text{div}}
    $$

## 实验

### 数据集

评测于 **MSCOCO** 与 **Flickr30K**，每张图像配 5 条人工描述；任务为 i2t 与 t2i 双向检索，报告 MSCOCO-1K/5K 与 Flickr30K 的 Recall@K。 

### 结果

<img src="http://public.file.lvshuhuai.cn/images\image-20251013174709691.png" alt="image-20251013174709691" style="zoom:50%;" />