# CLIP

传统视觉预训练（如 ImageNet 分类）学到的是“类别监督”，泛化到开放世界、长尾概念与细粒度语义时往往吃力。CLIP用**自然语言**当监督，把“文本描述 ↔ 图片”对齐到同一嵌入空间里，于是：

- 任何能写成一句话的概念，都能成为“类别”；
- 训练时见过的语言分布极广（网络配图），零样本/少样本迁移变强。

> 长尾概念：在数据或类别里，**出现频率很低但数量很多**的一大堆“冷门项”。虽然每个都少见，但**加起来占很大比例**。
>
> 例子：电商里热卖的前几十种商品是“头部”，几万种小众商品是“长尾”；图像分类里常见的“猫狗人”是头部，罕见的“雪中折叠自行车”是长尾。

## 总体架构

- **双编码器（Dual Encoder）**：图像编码器 $f_\theta(\cdot)$（ResNet 或 ViT）、文本编码器 $g_\phi(\cdot)$（Transformer）。
- **投影与归一化**：把各自输出映射到同一维度的向量空间，并做 $L_2$ 归一化，保证余弦相似度可用。
- **对比学习目标**：同一对 (image, text) 拉近，不匹配的都推远；用大批量做“廉价负样本”。

## 任务与数据形态

- **样本单位**：配对 (image, text)。可一图多文/一文多图，训练时打平成多对。
- **数据质量**：
    - **弱配对/含噪**允许，通过**大批量对比**与**负样本**学习抵消噪声。
    - 文本宜**短、名词密度高、可视觉落地**；过长句会稀释关键信号。
- **常用清洗流程**：
    1. 去重（感知哈希/向量相似阈值）；
    2. 文本正则化（去链接、表情、站位符）；
    3. 低质过滤（用预先 CLIPScore/图文相似度阈值）。

## 训练目标（公式）

给定批量 ${(x_i, y_i)}*{i=1}^N$，图像特征 $\mathbf{v}*i = \frac{f*\theta(x_i)}{|f*\theta(x_i)|}$，文本特征 $\mathbf{t}*i = \frac{g*\phi(y_i)}{|g_\phi(y_i)|}$，相似度 $s_{ij}=\mathbf{v}_i^\top \mathbf{t}_j$。CLIP 使用**对称 InfoNCE**：
$$
\mathcal{L} = \frac{1}{2}\left( \underbrace{\frac{1}{N}\sum_{i=1}^N -\log \frac{\exp(s_{ii}/\tau)}{\sum_{j=1}^N \exp(s_{ij}/\tau)}}_{\text{图像→文本}} + \underbrace{\frac{1}{N}\sum_{i=1}^N -\log \frac{\exp(s_{ii}/\tau)}{\sum_{j=1}^N \exp(s_{ji}/\tau)}}_{\text{文本→图像}} \right)
$$

- $\tau$ 是**温度参数**（可学习），控制分布“尖锐度”。$\tau$ 越小，模型越“挑剔”，梯度更集中在最难负样本上。
- 归一化使 $s_{ij}$ 成为余弦相似度，训练更稳定。
- **多阳性（Multi-Positive）**：若一图多文或一文多图，可将“正确列/行”做 soft label（如平均分配到 K 个正样本），缓解假负影响。
- **硬负采样（Hard Negatives）**：从队列/内存库中为每个正对挑选最相似但不配对的样本并加入分母，显著提升判别力。

## 训练策略

### 有效批量与分布式

- 对比学习的关键在**负样本数量**。
- 做法：
    1. **多卡 all-gather** 拼更大的有效批量（常见 > 8k）；
    2. **特征队列（memory bank）** 持续缓存前几批 ${\mathbf{v},\mathbf{t}}$ 作为额外负样本。

### 优化与调度

- **优化器**：AdamW，$\text{lr}\approx 5\times10^{-4}$，$\text{betas}=(0.9,0.98)$，$\epsilon=10^{-6}$，weight decay 0.2 左右。
- **学习率策略**：Cosine decay + warmup（2k–10k steps）。
- **混合精度**：AMP（fp16/bf16）+ GradScaler；大模型配合 Gradient Checkpointing。

### 数据增强

- **图像**：RandomResizedCrop（比例 0.5–1.0）、随机水平翻转、轻量 ColorJitter；不过度增强避免语义漂移。
- **文本**：最长 77/128 tokens；**短、具体、名词密度高**；可做 **Text Dropout**（随机保留关键短语）。

## 推理与零样本（Inference & Zero-shot）

### 零样本分类

1. 写出类别模板（prompts），如 `"a photo of a {label}."`、`"一张{label}的照片"`；

2. 每类使用**多模板**（10–30 条）并**平均/加权融合**文本向量 $\mathbf{t}_k$；

3. 给定图像向量 $\mathbf{v}$，做：
    $$
    P(y=k\mid x)=\frac{\exp(\alpha,\cos(\mathbf{v},\mathbf{t}*k))}{\sum*{k'}\exp(\alpha,\cos(\mathbf{v},\mathbf{t}_{k'}))}
    $$

### 图文检索

- 离线抽取向量，$L_2$ 归一化；在线利用 ANN（Faiss/HNSW）做余弦近邻查询。
- 双向评测：图搜文、文搜图。

### 提示工程（Prompting）

- **口语化/多样化**：加入同义词、场景、材质、视角等；
- **跨语言**：中文任务优先中文模板或中英混合模板；
- **去偏融合**：对每类模板设权重（可用验证集或 CLIPScore 学习权重）。

## 评测指标与基准（Eval）

- **零样本分类**：Top-1/Top-5；建议加跨域集（ImageNet-V2/A/O 等）验证鲁棒性。
- **检索**：R@1/5/10、mAP、MRR，图文双向都报。
- **线性探针（Linear Probe）**：冻结双塔，只训线性分类头，观察“零样本↔监督”差距。
- **少样本（Few-shot）**：1/2/4/8-shot；对比 Tip-Adapter/CoOp/LoRA。

## 代码参考（PyTorch 骨架）

> 说明：省略 DDP 样板；`logit_scale` 做指数并适度 clamp；支持 AMP；可扩展特征队列。

```python
import math, torch, torch.nn as nn, torch.nn.functional as F

class CLIPDualEncoder(nn.Module):
    def __init__(self, img_encoder, txt_encoder, d_proj=768, init_temp=0.07):
        super().__init__()
        self.img = img_encoder   # e.g., ViT-B/32 backbone, outputs (B, H)
        self.txt = txt_encoder   # e.g., 12-layer Transformer, outputs (B, H)
        self.Wi  = nn.Linear(self.img.width, d_proj, bias=False)
        self.Wt  = nn.Linear(self.txt.width, d_proj, bias=False)
        self.logit_log_temp = nn.Parameter(torch.tensor(math.log(1.0/init_temp)))

    def encode_image(self, x):
        h = self.img(x)                 # (B, H)
        z = F.normalize(self.Wi(h), dim=-1)  # (B, D)
        return z

    def encode_text(self, ids, attn):
        h = self.txt(ids, attn)         # (B, H) 取 [EOS] 或 pooled 输出
        z = F.normalize(self.Wt(h), dim=-1)
        return z

    def forward(self, img, ids, attn):
        v = self.encode_image(img)
        t = self.encode_text(ids, attn)
        logit_scale = self.logit_log_temp.exp().clamp(max=100.)
        logits_i2t = logit_scale * v @ t.t()  # (B, B)
        logits_t2i = logits_i2t.t()
        labels = torch.arange(v.size(0), device=v.device)
        loss = 0.5 * (F.cross_entropy(logits_i2t, labels) +
                      F.cross_entropy(logits_t2i, labels))
        return loss, (v, t), logit_scale
```

**训练要点（伪代码）**：

```python
# optimizer = AdamW(model.parameters(), lr=5e-4, betas=(0.9,0.98), eps=1e-6, weight_decay=0.2)
# lr schedule = cosine + warmup(2k~10k)
# use torch.cuda.amp.autocast + GradScaler
# DDP: all_gather features across GPUs before computing logits for larger effective batch.

scaler = torch.cuda.amp.GradScaler()
for step, batch in enumerate(loader):
    img, ids, attn = batch
    with torch.cuda.amp.autocast():
        loss, _, _ = model(img, ids, attn)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
    optimizer.zero_grad(set_to_none=True)
```

**特征队列（思路）**：维护长度 K 的 FIFO 队列 `queue_v/queue_t`；在构造 logits 时将当前批与队列拼接，扩大负样本集合；注意梯度仅回传到当前批。