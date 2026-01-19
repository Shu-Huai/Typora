# KL 散度

## KL 散度是什么

KL 散度（Kullback–Leibler Divergence）用于衡量两个概率分布之间的“差异”。给定真实分布 $p$ 与近似分布 $q$，KL 散度定义为：

**离散情形：**
$$
D_{\mathrm{KL}}(p\|q)=\sum_x p(x)\log\frac{p(x)}{q(x)}
$$

**连续情形：**
$$
D_{\mathrm{KL}}(p\|q)=\int p(x)\log\frac{p(x)}{q(x)}\,dx
$$

直观含义（信息论视角）：

如果数据真实来自 $p$，你却用 $q$ 来编码/解释它，会比用 $p$ 多付出多少“平均编码代价”（额外的负对数似然）。

## KL 散度的关键性质

### 非负性（Gibbs 不等式）

$$
D_{\mathrm{KL}}(p\|q)\ge 0
$$
且当且仅当 $p=q$（几乎处处）时取 0。

### 不对称

$$
D_{\mathrm{KL}}(p\|q)\neq D_{\mathrm{KL}}(q\|p)
$$
因此 KL 不是距离（distance），不满足对称性与三角不等式。

### 支持集要求

若存在某点 $x$ 使得 $p(x)>0$ 但 $q(x)=0$，则：
$$
D_{\mathrm{KL}}(p\|q)=+\infty
$$
这意味着：用 KL 做对齐时必须保证 $q$ 不把 $p$ 的“概率质量”压成 0。

## 两种方向的直觉差异：$D_{\mathrm{KL}}(p\|q)$ vs $D_{\mathrm{KL}}(q\|p)$

在连续分布的常见直觉中（工程上经常用）：

- **$D_{\mathrm{KL}}(p\|q)$**：更倾向于“覆盖” $p$ 的支撑区域（mode-covering）。  
  因为 $p$ 在哪里有质量，$q$ 如果不给概率会被严重惩罚（甚至无穷大）。

- **$D_{\mathrm{KL}}(q\|p)$**：更倾向于“找峰”而不是覆盖（mode-seeking）。  
  $q$ 会更愿意集中到 $p$ 的高概率区域，忽略其他模式也可能代价不大。

注意：这不是严格定理，而是非常有用的经验直觉，尤其在 VI（变分推断）和生成模型中常被提及。

## KL 散度的常见变体与相关概念

### Jensen–Shannon (JS) 散度
JS 是对称且有界的分布差异度量：
$$
D_{\mathrm{JS}}(p\|q)=\frac12 D_{\mathrm{KL}}(p\|m)+\frac12 D_{\mathrm{KL}}(q\|m)
$$
其中 $m=\frac12(p+q)$。

JS 更稳定、更“像距离”，在对抗学习里也常出现。

## 深度学习中的典型用法

### 知识蒸馏（Knowledge Distillation）
教师分布 $p$，学生分布 $q$，常最小化：
$$
D_{\mathrm{KL}}(p\|q)
$$
或等价地最小化交叉熵 $H(p,q)$（因为 $H(p)$ 常数）。

实践中经常引入温度 $T$ 让分布变“软”，再做 KL。

### VAE（变分自编码器）
VAE 的 ELBO 中包含一个 KL 正则项：
$$
D_{\mathrm{KL}}\big(q_\phi(z|x)\ \|\ p(z)\big)
$$
让后验近似 $q_\phi(z|x)$ 不要偏离先验 $p(z)$ 太远。

### 分布对齐 / 正则化
比如让预测分布接近某个先验、或让两种模型输出一致，都会出现 KL 项。

## 计算形式与数值稳定

### 离散概率形式
$$
D_{\mathrm{KL}}(p\|q)=\sum_i p_i(\log p_i-\log q_i)
$$

工程建议：
- 避免 $q_i=0$（可加 epsilon：$q_i\leftarrow \max(q_i,\epsilon)$）
- 更常用的是在 **log-prob** 空间计算（更稳）

### logits 与 log-softmax
若你手里是 logits，先做：
- `logp = log_softmax(logits_p)`
- `logq = log_softmax(logits_q)`
再用 logp/logq 算 KL，通常最稳定。

## 简单例子

设 $p=(0.5,0.5)$，$q=(0.9,0.1)$：
$$
D_{\mathrm{KL}}(p\|q)=0.5\log\frac{0.5}{0.9}+0.5\log\frac{0.5}{0.1}
$$
第二项会很大，因为 $q$ 把第二类概率压得太低，导致“用 $q$ 解释 $p$”代价大。

## PyTorch 示例

### 9.1 用 log-prob 计算 KL
```python
import torch
import torch.nn.functional as F

logits_p = torch.randn(4, 10)   # teacher / target distribution logits
logits_q = torch.randn(4, 10)   # student / predicted distribution logits

logp = F.log_softmax(logits_p, dim=-1)
logq = F.log_softmax(logits_q, dim=-1)

# PyTorch 的 kl_div 默认形式是 KL(p || q) 的“交叉熵型”写法：
# kl_div(input=logq, target=p, reduction=...) 其中 input 是 log-prob，target 是 prob
p = logp.exp()
kl = F.kl_div(logq, p, reduction="batchmean")  # batch 平均 KL
print(kl.item())