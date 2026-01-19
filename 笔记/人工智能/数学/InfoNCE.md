# InfoNCE

## InfoNCE 在解决什么问题
### 核心目标：学到“可检索”的表征空间
对比学习希望学习一个特征空间，使得：
- 正样本对（positive pair）：表示相似度高
- 负样本对（negative pair）：表示相似度低

InfoNCE 是最常用的对比损失之一，尤其常见于 CLIP、SimCLR、MoCo、多模态对齐、检索式表征学习等任务。

### 一个统一视角：把“匹配”变成“分类”
给定一个锚点（anchor / query）向量 `q`，在一堆候选 `k0..kN` 中：
- 只有一个是正确匹配 `k+`
- 其余都视为负样本

于是问题变成：从 $N+1$ 个候选里“分类”出正确的那个。InfoNCE 就是这个分类的交叉熵损失。

## 数学定义与关键组件
### 基本符号
- `q`：query（锚点向量）
- `{k_i}`：候选 keys（包含正样本和负样本）
- `sim(q, k)`：相似度函数（常用点积或余弦相似度）
- `τ`：温度（temperature），控制 softmax 分布的尖锐程度

### 单向 InfoNCE（最常见公式）
设 `k+` 是唯一正样本，则
$$
\mathcal{L}_{\text{InfoNCE}}
=
-\log
\frac{\exp(\mathrm{sim}(q, k_+)/\tau)}
{\sum_{i=0}^{N}\exp(\mathrm{sim}(q, k_i)/\tau)}
$$

#### 逐步解释
- 先算 logits：$\ell_i=\mathrm{sim}(q,k_i)/\tau$
- softmax 得到概率：$p_i=\frac{e^{\ell_i}}{\sum_j e^{\ell_j}}$
- 取正样本那一项做交叉熵：$-\log p_{+}$

### 相似度 sim 的典型选择
#### 点积 vs 余弦
- 点积：$\mathrm{sim}(a,b)=a^\top b$
- 余弦：$\mathrm{sim}(a,b)=\frac{a^\top b}{\|a\|\|b\|}$

工程上常见做法是 **先 L2 归一化 embedding**，使点积等价于余弦
$$
\hat{a}=\frac{a}{\|a\|},\quad \hat{b}=\frac{b}{\|b\|},\quad \hat{a}^\top \hat{b}=\cos(\theta)
$$
这样可以避免“向量模长”主导相似度，训练更稳定。

### 温度 τ 的作用
#### 直观理解
- τ 小：softmax 更尖锐，模型更“强硬”地区分正负样本（梯度更大、更激进）
- τ 大：softmax 更平缓，训练更保守

#### 常见实践
- 设一个固定 τ（如 0.07、0.1、0.2）
- 或让模型学习一个 logit_scale（CLIP 常用）：$\ell_{ij}=\mathrm{sim}(x_i,y_j)\cdot s$，其中 $s=\exp(\text{logit\_scale})\approx 1/\tau$

## InfoNCE 与交叉熵（CE）的等价关系
### “对比学习 = batch 内分类”
在 batch 大小为 B 的情形里，常见构造相似度矩阵
$$
S_{ij}=\mathrm{sim}(x_i, y_j)/\tau
$$
其中 $(x_i, y_i)$ 是匹配对。

对每个 `i`，正确类别是 `j=i`，于是：
- 行方向：`x_i` 去分类 `y_j`（image->text 或 query->key）
- 列方向：`y_i` 去分类 `x_j`（text->image 或 key->query）

### 双向 InfoNCE（CLIP 风格）
$$
\mathcal{L}
=\frac{1}{2}\Big(\mathrm{CE}(S,\text{target}=i)+\mathrm{CE}(S^\top,\text{target}=i)\Big)
$$
其中 `target=i` 表示第 i 行的正确列是 i（即对角线）。

### 梯度直觉
对单个 query 来说，softmax 概率为 $p_i$：
- 正样本项梯度与 $(p_{+}-1)$ 成正比：若 $p_{+}$ 不够大，就会强烈推高正样本 logit
- 负样本项梯度与 $p_{neg}$ 成正比：概率越大（越“像正样本”的负样本），被推开的力度越大

这也是为什么“硬负样本”（相似度高的负样本）对训练很重要。

## 数值例子：把公式真正算一遍
### 设定
给定三个候选（1 个正样本 + 2 个负样本）：
- $\mathrm{sim}(q,k_+)=2$
- $\mathrm{sim}(q,k_1)=1$
- $\mathrm{sim}(q,k_2)=0$
取温度 $\tau=0.5$

### 计算 logits
$$
\ell = [2/0.5,\ 1/0.5,\ 0/0.5]=[4,\ 2,\ 0]
$$

### softmax 概率
$$
p_+ = \frac{e^4}{e^4+e^2+e^0}\approx 0.8668
$$
$$
p_1 \approx 0.1173,\quad p_2 \approx 0.0159
$$

### InfoNCE 损失
$$
\mathcal{L}=-\log(p_+)\approx -\log(0.8668)\approx 0.1429
$$
如果正样本相似度更低或 τ 更大，$p_+$ 会变小，损失会变大。

## 常见变体与扩展
### 多正样本（multi-positive）
很多任务里，一个 query 可能对应多个正样本（例如：一张图对应多条 caption；一篇文章对应多张图）。
常见做法是把分子扩展为多个正样本的 log-sum-exp：
$$
\mathcal{L}
=
-\log
\frac{\sum_{k\in \mathcal{P}(q)}\exp(\mathrm{sim}(q,k)/\tau)}
{\sum_{i}\exp(\mathrm{sim}(q,k_i)/\tau)}
$$
其中 $\mathcal{P}(q)$ 是正样本集合。

### 监督式对比学习（Supervised Contrastive）
当有类别标签时，同类样本都可以作为正样本，能显著改善表征聚类结构，但要注意同类内多样性与假正样本问题。

### 负样本来源：in-batch vs 队列/内存库
- in-batch negatives：简单、高效，但受 batch size 限制
- queue/memory bank（MoCo）：扩大负样本数量，但要处理动量编码器、特征滞后等工程细节

### 假负样本（false negatives）与 Mask
当负样本里混入“其实是正样本/同组样本”（如同一文章内的其他 caption），会错误地被推远，导致性能下降。
工程上常用：

- group mask：把同组样本从分母的负样本里排除（但保留对角线正样本）
- 或进行“软多正样本”建模（同组为正，权重不同）

## 实现要点（PyTorch 视角）
### 推荐实现：相似度矩阵 + CrossEntropy
优点：数值稳定、代码短、易于分布式扩展。

#### 双向 InfoNCE（CLIP 风格）参考代码
```python
import torch
import torch.nn.functional as F

def clip_infonce_bidir(x, y, logit_scale):
    """
    x: [B, D]  (e.g., image embeddings)
    y: [B, D]  (e.g., text embeddings)
    logit_scale: scalar, e.g. exp(logit_scale_param) ~ 1/tau
    """
    # L2 normalize (optional but strongly recommended)
    x = F.normalize(x, dim=-1)
    y = F.normalize(y, dim=-1)

    # similarity logits: [B, B]
    logits = logit_scale * (x @ y.t())

    targets = torch.arange(x.size(0), device=x.device)

    loss_i2t = F.cross_entropy(logits, targets)
    loss_t2i = F.cross_entropy(logits.t(), targets)

    return 0.5 * (loss_i2t + loss_t2i)