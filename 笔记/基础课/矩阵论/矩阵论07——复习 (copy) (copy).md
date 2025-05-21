## 内积空间

### 考点一：内积空间的定义

#### 定义

设 $V$ 是实数域或 $\mathbb{R}$ 上的线性空间，如果对于 $V$ 中的任意两个元素 $\alpha, \beta$ 都有一个实数 $(\alpha, \beta)$ 与之对应，并且满足下面 4 个条件，则称 $(\alpha, \beta)$ 称为元素 $\alpha, \beta$ 的内积：

1. $(\alpha, \beta) = (\beta, \alpha)$
2. $(\alpha + \beta, r) = (\alpha, r) + (\beta, r)$
3. $(k \alpha, \beta) = k (\alpha, \beta)$
4. $(\alpha, \alpha) \geq 0$，当且仅当 $\alpha = 0$ 时等号成立。

此时线性空间 $V$ 叫作实内积空间。

#### 元素大小

元素大小：$\lvert \alpha \rvert = \sqrt{ (\alpha, \alpha) }$

### 考点二：标准正交基

#### 标准正交基

由正交的单位向量 $a_1, a_2, \ldots, a_n$ 组成的基底叫作标准正交基。此时：
$$
(a_i, a_j) = \begin{cases} 1, & i = j \\ 0, & i \neq j \end{cases} \quad (i,j = 1,2,\ldots,n)
$$

#### 求标准正交基

用施密特（Schmidt）正交化的方法求标准正交基。

设 $a_1, a_2, \ldots, a_n$ 是 $V$ 的一组基，$a_1, a_2, \ldots, a_n$ 线性无关。

1. 正交化：

    $B_1 = a_1$

    $B_2 = a_2 - \dfrac{(a_2, B_1)}{(B_1, B_1)} B_1$

    $B_3 = a_3 - \dfrac{(a_3, B_1)}{(B_1, B_1)} B_1 - \dfrac{(a_3, B_2)}{(B_2, B_2)} B_2$

2. 单位化：

    $B_1' = \dfrac{B_1}{\lvert B_1 \rvert}$，$B_2' = \dfrac{B_2}{\lvert B_2 \rvert}$，$B_3' = \dfrac{B_3}{\lvert B_3 \rvert}$

#### 例 1

在 $R^{2 \times 2}$ 中定义内积 $(A, B) = \sum_{i,j} a_{ij} b_{ij}$，基底：
$$
G_1 = \begin{pmatrix} 0 & 1 \\ 1 & 1 \end{pmatrix}, \quad
G_2 = \begin{pmatrix} 1 & 0 \\ 1 & 1 \end{pmatrix}, \quad
G_3 = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad
G_4 = \begin{pmatrix} 1 & 1 \\ 1 & 0 \end{pmatrix}
$$
构造一个标准正交基。

1. 正交化：

    $B_1 = G_1$

    $B_2 = G_2 - \dfrac{(G_2, B_1)}{(B_1, B_1)} B_1 = \dfrac{1}{3} \begin{pmatrix} 3 & -2 \\ 1 & 1 \end{pmatrix}$

    $B_3 = G_3 - \dfrac{(G_3, B_1)}{(B_1, B_1)} B_1 - \dfrac{(G_3, B_2)}{(B_2, B_2)} B_2 = \dfrac{1}{5} \begin{pmatrix} -3 & 3 \\ -4 & 1 \end{pmatrix}$

    $B_4 = G_4 - \dfrac{(G_4, B_1)}{(B_1, B_1)} B_1 - \dfrac{(G_4, B_2)}{(B_2, B_2)} B_2 - \dfrac{(G_4, B_3)}{(B_3, B_3)} B_3 = \dfrac{1}{7} \begin{pmatrix} 3 & 3 \\ 3 & -6 \end{pmatrix}$

2. 单位化：

    $B_1' = \dfrac{B_1}{\lvert B_1 \rvert} = \dfrac{1}{\sqrt{3}} \begin{pmatrix} 0 & 1 \\ 1 & 1 \end{pmatrix}$

    $B_2' = \dfrac{B_2}{\lvert B_2 \rvert} = \dfrac{1}{\sqrt{15}} \begin{pmatrix} 3 & -2 \\ 1 & 1 \end{pmatrix}$

    $B_3' = \dfrac{B_3}{\lvert B_3 \rvert} = \dfrac{1}{\sqrt{35}} \begin{pmatrix} -3 & 3 \\ -4 & 1 \end{pmatrix}$

    $B_4' = \dfrac{B_4}{\lvert B_4 \rvert} = \dfrac{1}{\sqrt{63}} \begin{pmatrix} 3 & 3 \\ 3 & -6 \end{pmatrix}$

### 考点三：正规矩阵对角化

#### 定义

设 $V$ 是复数域或 $\mathbb{C}$ 上的线性空间，如果对于 $V$ 中的任意两个向量 $\alpha, \beta$ 都有一个复数 $(\alpha, \beta)$ 与之对应，并且满足：

1. $(\alpha, \beta) = \overline{(\beta, \alpha)}$
2. $(\alpha + \beta, r) = (\alpha, r) + (\beta, r)$
3. $(k \alpha, \beta) = k (\alpha, \beta)$
4. $(\alpha, \alpha) \geq 0$，且仅当 $\alpha = 0$ 时等号成立。

此时 $V$ 叫作复内积空间或酉空间。

#### 酉矩阵的定义

设 $A \in \mathbb{C}^{n \times n}$ 且 $A^H A = A A^H = E$，则称 $A$ 为酉矩阵。

#### 正规矩阵的定义

设 $A \in \mathbb{C}^{n \times n}$ 且 $A^H A = A A^H$，则称 $A$ 为正规矩阵。

#### 对称矩阵、实对称矩阵、厄米特矩阵、反厄米特矩阵、反对称矩阵、酉矩阵等都是正规矩阵。

#### 正规矩阵对角化

正规矩阵一定可以对角化（可与`向量和矩阵的范数`结合出题），即存在酉矩阵 $U$ 使得 $U^H A U = \Lambda$，$\Lambda$ 的对角线元素为 $A$ 的特征值。

## 向量和矩阵的范数

### 考点一：证明向量范数

#### 向量范数的定义

若对于任意的 $x \in \mathbb{C}^n$ 都有一个实数 $\left\lVert x \right\rVert$ 与之对应，且满足：

1. **非负性**：$x \neq 0$ 时，$\left\lVert x \right\rVert > 0$，当 $x = 0$ 时，$\left\lVert x \right\rVert = 0$。
2. **齐次性**：对于任意的 $k \in \mathbb{C}$，$\left\lVert kx \right\rVert = \lvert k \rvert \left\lVert x \right\rVert$。
3. **三角不等式**：对于任意的 $x, y \in \mathbb{C}^n$，都有：$\left\lVert x + y \right\rVert \leq \left\lVert x \right\rVert + \left\lVert y \right\rVert$

则称 $\left\lVert \cdot \right\rVert$ 为 $\mathbb{C}^n$ 上的向量范数，简称向量范数。

#### 常用的向量范数

1. 向量的 2 范数：$\left\lVert x \right\rVert_2 = \sqrt{ \displaystyle \sum_{i=1}^{n} \lvert x_i \rvert^2 } = \sqrt{ x^H x }$
2. 向量的 1 范数：$\left\lVert x \right\rVert_1 = \displaystyle \sum_{i=1}^{n} \lvert x_i \rvert$
3. 向量的 $\infty$ 范数：$\left\lVert x \right\rVert_\infty = \displaystyle \max_i \lvert x_i \rvert$

#### 例 1

设 $\left\lVert \cdot \right\rVert_a$，$\left\lVert \cdot \right\rVert_b$ 是线性空间 $\mathbb{C}^n$ 上的两种向量范数，又 $k_1, k_2$ 是大于零的常数，证明函数 $k_1 \left\lVert x \right\rVert_a + k_2 \left\lVert x \right\rVert_b$ 是向量范数。

证明：

1. **非负性**：

    - 当 $x = 0$ 时，$k_1 \left\lVert 0 \right\rVert_a + k_2 \left\lVert 0 \right\rVert_b = 0$

    - 当 $x \neq 0$ 时，$k_1 \left\lVert x \right\rVert_a + k_2 \left\lVert x \right\rVert_b > 0$

2. **齐次性**：

    $k_1 \left\lVert kx \right\rVert_a + k_2 \left\lVert kx \right\rVert_b = k_1 \lvert k \rvert \left\lVert x \right\rVert_a + k_2 \lvert k \rvert \left\lVert x \right\rVert_b = \lvert k \rvert \left( k_1 \left\lVert x \right\rVert_a + k_2 \left\lVert x \right\rVert_b \right)$

3. **三角不等式**：

    $k_1 \left\lVert x + y \right\rVert_a + k_2 \left\lVert x + y \right\rVert_b \leq k_1 \left( \left\lVert x \right\rVert_a + \left\lVert y \right\rVert_a \right) + k_2 \left( \left\lVert x \right\rVert_b + \left\lVert y \right\rVert_b \right)= k_1 \left\lVert x \right\rVert_a + k_1 \left\lVert y \right\rVert_a + k_2 \left\lVert x \right\rVert_b + k_2 \left\lVert y \right\rVert_b$

故函数 $k_1 \left\lVert x \right\rVert_a + k_2 \left\lVert x \right\rVert_b$ 是向量范数。

### 考点二：证明矩阵范数

#### 矩阵范数的定义

若对于任意的 $A \in \mathbb{C}^{n \times m}$ 都有一个实数 $\left\lVert A \right\rVert$ 与之对应，且满足：

1. **非负性**：$A \neq 0$ 时，$\left\lVert A \right\rVert > 0$；当 $A = 0$ 时，$\left\lVert A \right\rVert = 0$。
2. **齐次性**：对于任意的 $k \in \mathbb{C}$，$\left\lVert kA \right\rVert = \lvert k \rvert \left\lVert A \right\rVert$。
3. **三角不等式**：对于任意的 $A, B \in \mathbb{C}^{n \times m}$，$\left\lVert A + B \right\rVert \leq \left\lVert A \right\rVert + \left\lVert B \right\rVert$。
4. **相容性**：对于任意的 $A, B \in \mathbb{C}^{n \times m}$，都有 $\left\lVert AB \right\rVert \leq \left\lVert A \right\rVert \cdot \left\lVert B \right\rVert$。

#### 常用的矩阵范数

1. 矩阵的 F 范数：$\left\lVert A \right\rVert_F = \sqrt{ \displaystyle \sum_{i,j} \lvert a_{ij} \rvert^2 } = \sqrt{ \displaystyle \text{tr} \left( A^H A \right) }$

    与向量的 2 范数（$l_2$ 范数）吻合。

    这里的 $\text{tr} \left( A^H A \right)$ 是取矩阵 $A^H A$ 的迹，即 $A^H A$ 对角线元素之和。

    $\text{tr} \left( AB \right) = \text{tr} \left( BA \right)$。

2. 矩阵的 1 范数：$\left\lVert A \right\rVert_1 = \displaystyle \max_j \sum_i \lvert a_{ij} \rvert$（列最大）
3. 矩阵的 $\infty$ 范数：$\left\lVert A \right\rVert_\infty = \displaystyle \max_i \sum_j \lvert a_{ij} \rvert$（行最大）
4. 矩阵的 2 范数：$\left\lVert A \right\rVert_2 = \sqrt{\lambda_1}$，$\lambda_1$ 为 $A^H A$ 的最大特征值。

#### 相容性

设 $\left\lVert \cdot \right\rVert_m$ 是 $\mathbb{C}^{n \times m}$ 上的矩阵范数，$\left\lVert \cdot \right\rVert$ 是 $\mathbb{C}^n$ 上的向量范数，对任意 $A \in \mathbb{C}^{n \times m}$，$x \in \mathbb{C}^m$，都有：
$$
\left\lVert A x \right\rVert \leq \left\lVert A \right\rVert_m \left\lVert x \right\rVert
$$
则称矩阵范数 $\left\lVert \cdot \right\rVert_m$ 与向量范数 $\left\lVert \cdot \right\rVert$ 是相容性。

#### 谱半径

设 $A \in \mathbb{C}^{n \times n}$，$\lambda_1, \lambda_2, \ldots, \lambda_n$ 是 $A$ 的 $n$ 个特征值，称：
$$
\rho (A) = \displaystyle \max \lvert \lambda_i \rvert
$$
为 $A$ 的谱半径。

（即 $A$ 的谱半径是 $A$ 的特征值的模的最大值）

#### 谱半径与范数

设 $A \in \mathbb{C}^{n \times n}$，则对 $\mathbb{C}^{n \times n}$ 上任何一个范数 $\left\lVert \cdot \right\rVert_m$ 都有：
$$
\rho (A) \leq \left\lVert A \right\rVert_m
$$

#### 例 2

设 $\mathbb{C}^{n \times n}$ 上的矩阵范数 $\left\lVert \cdot \right\rVert_m$，$S$ 为 $n$ 阶可逆矩阵，对任意的矩阵 $A \in \mathbb{C}^{n \times n}$，定义 $\left\lVert A \right\rVert = \left\lVert S^{-1} A S \right\rVert_m$。证明：$\left\lVert A \right\rVert$ 是空间 $\mathbb{C}^{n \times n}$ 里的矩阵范数。

证明：

1. **非负性**：

    - $A = 0$ 时，$\left\lVert A \right\rVert = \left\lVert S^{-1} A S \right\rVert_m = 0$

    - $A \neq 0$时，$\left\lVert A \right\rVert = \left\lVert S^{-1} A S \right\rVert_m > 0$

2. **齐次性**：$\left\lVert kA \right\rVert = \left\lVert S^{-1} kA S \right\rVert_m = \lvert k \rvert \left\lVert S^{-1} A S \right\rVert_m = \lvert k \rvert \left\lVert A \right\rVert$。
3. **三角不等式**：$\left\lVert A + B \right\rVert = \left\lVert S^{-1} (A + B) S \right\rVert_m = \left\lVert S^{-1} A S + S^{-1} B S \right\rVert_m \leq \left\lVert S^{-1} A S \right\rVert_m + \left\lVert S^{-1} B S \right\rVert_m = \left\lVert A \right\rVert + \left\lVert B \right\rVert$。
4. **相容性**：$\left\lVert AB \right\rVert = \left\lVert S^{-1} A B S \right\rVert_m = \left\lVert S^{-1} A S \cdot S^{-1} B S \right\rVert_m \leq \left\lVert S^{-1} A S \right\rVert_m \cdot \left\lVert S^{-1} B S \right\rVert_m = \left\lVert A \right\rVert \cdot \left\lVert B \right\rVert$。

故 $\left\lVert A \right\rVert$ 是空间 $\mathbb{C}^{n \times n}$ 里的矩阵范数。

### 考点三：范数与正规矩阵的证明题

#### 正规矩阵的对角化

正规矩阵一定可以**对角化**（可与`向量和矩阵的范数`结合出题）。 

即存在酉矩阵 $U$ 使得 $U^H A U = \Lambda$，$\Lambda$ 的对角线元素为 $A$ 的特征值。

#### 例 3

证明：若正规矩阵 $A \in \mathbb{C}^{n \times n}$ 的特征值为 $\lambda_1, \lambda_2, \ldots, \lambda_n$，则 $\lvert \lambda_1 \rvert^2 + \lvert \lambda_2 \rvert^2 + \cdots + \lvert \lambda_n \rvert^2 = \left\lVert A \right\rVert_F^2$

（其中 $\left\lVert A \right\rVert_F = \sqrt{ \sum_{i,j} \lvert a_{ij} \rvert^2 } = \sqrt{ \text{tr} ( A^H A ) }$ 是矩阵的 Frobenius 范数）

证明：

因为 $A$ 是正规矩阵，正规矩阵一定可以对角化。

所以存在酉矩阵 $Q$ 使得 $Q^H A Q = \Lambda$，$\Lambda$ 的对角线元素为 $A$ 的特征值，即 $A = Q \Lambda Q^H$。

则：
$$
\left\lVert A \right\rVert_F^2 = \left\lVert Q \Lambda Q^H \right\rVert_F^2 = \text{tr} \left( Q \Lambda Q^H Q \Lambda^H Q^H \right)
$$

$$
= \text{tr} \left( Q \Lambda \Lambda^H Q^H \right) = \text{tr} \left( \Lambda \Lambda^H Q^H Q \right) = \text{tr} \left( \Lambda \Lambda^H \right)
$$

- 其中利用了 $\text{tr} (AB) = \text{tr} (BA)$ 。
- 又 $\text{tr} ( \Lambda \Lambda^H ) = \lvert \lambda_1 \rvert^2 + \lvert \lambda_2 \rvert^2 + \cdots + \lvert \lambda_n \rvert^2$。

故 $\left\lVert A \right\rVert_F^2 = \lvert \lambda_1 \rvert^2 + \lvert \lambda_2 \rvert^2 + \cdots + \lvert \lambda_n \rvert^2$。

## 矩阵的导数  
### 考点一：矩阵的导数（对一个变量的导数）

#### 函数矩阵

以实变量 $t$ 的实函数 $a_{ij}(t)$ 为元素的矩阵
$$
A(t) = \begin{pmatrix}
a_{11}(t) & a_{12}(t) & \cdots & a_{1n}(t) \\
a_{21}(t) & a_{22}(t) & \cdots & a_{2n}(t) \\
\vdots & \vdots & \ddots & \vdots \\
a_{m1}(t) & a_{m2}(t) & \cdots & a_{mn}(t)
\end{pmatrix}
$$
称为函数矩阵。

#### 函数矩阵对一个变量的导数

函数矩阵 $A(t)$ 对变量 $t$ 的导数定义为
$$
A'(t) = \frac{d A(t)}{dt} = \begin{pmatrix}
a_{11}'(t) & a_{12}'(t) & \cdots & a_{1n}'(t) \\
a_{21}'(t) & a_{22}'(t) & \cdots & a_{2n}'(t) \\
\vdots & \vdots & \ddots & \vdots \\
a_{m1}'(t) & a_{m2}'(t) & \cdots & a_{mn}'(t)
\end{pmatrix}
$$

#### 例 1
设矩阵 $A = \begin{pmatrix} \sin t & t & 2t \\ e^t & t^2 & t \\ 1 & 1 & t^3 \end{pmatrix}$，求 $\dfrac{dA}{dt}$。

**解：**

根据逐元素求导，得：
$$
\dfrac{dA}{dt} = \begin{pmatrix}
\cos t & 1 & 2 \\
e^t & 2t & 1 \\
0 & 0 & 3t^2
\end{pmatrix}
$$

### 考点二：矩阵的幂级数（收敛性的判断）

#### 矩阵幂级数  

设 $A = (a_{ij}) \in \mathbb{C}^{n \times n}$，形如  
$$
\sum_{k=0}^{\infty} a_k A^k = a_0 E + a_1 A + a_2 A^2 + \cdots + a_k A^k + \cdots
$$
的矩阵级数称为矩阵幂级数。

#### 收敛性

设幂级数 $\sum_{k=0}^{\infty} a_k x^k$ 的收敛半径为 $R$，$A \in \mathbb{C}^{n \times n}$，则：

1. 当 $\rho(A) < R$ 时，$\sum_{k=0}^{\infty} a_k A^k$ 绝对收敛；
2. 当 $\rho(A) > R$ 时，$\sum_{k=0}^{\infty} a_k A^k$ 发散。

#### 收敛半径  

收敛半径 $R = \dfrac{1}{\rho}$，其中  
$$
\rho = \lim_{k \to \infty} \left| \dfrac{a_{k+1}}{a_k} \right|
$$

#### 例 2
判断矩阵幂级数 $\sum_{k=0}^{\infty} \begin{pmatrix} 0.1 & 0.7 \\ 0.3 & 0.6 \end{pmatrix}^k$ 的收敛性，若收敛，计算其基和。

**解：**

令 $A = \begin{pmatrix} 0.1 & 0.7 \\ 0.3 & 0.6 \end{pmatrix}$。

特征方程：
$$
|\lambda E - A| = \begin{vmatrix} \lambda - 0.1 & -0.7 \\ -0.3 & \lambda - 0.6 \end{vmatrix} = \lambda^2 - 0.7\lambda - 0.15
$$

解得：
$$
\lambda_{1} = \frac{0.7 + \sqrt{1.09}}{2}, \quad \lambda_{2} = \frac{0.7 - \sqrt{1.09}}{2}
$$
显然 $\lambda_1 > \lambda_2$。

因此 $\rho(A) = |\lambda_{\max}| = \lambda_1 = \frac{0.7 + \sqrt{1.09}}{2}$。

幂级数系数 $a_k = 1$，收敛判别：
$$
\rho = \lim_{k \to \infty} \left| \frac{a_{k+1}}{a_k} \right| = 1
$$
所以收敛半径：
$$
R = \frac{1}{\rho} = 1
$$

由于 $\rho(A) < R$，故矩阵幂级数绝对收敛。

### 考点三：矩阵函数（$A \to f(At)$）  
常见：$A \to e^{At}$

#### 计算矩阵函数的方法  

常用：最小多项式法。

#### 计算矩阵函数的一般步骤  

1. 设 $n$ 阶矩阵 $A$ 的最小多项式为 $m$ 次多项式：
    $$
    m(\lambda) = (\lambda - \lambda_1)^{s_1} (\lambda - \lambda_2)^{s_2} \cdots (\lambda - \lambda_s)^{s_s}
    $$
    其中，$\lambda_1, \lambda_2, \ldots, \lambda_s$ 是 $A$ 的所有不同的特征值。

2. 设 $f(A t)$（对参数 $t$ 的矩阵函数）
    $$
    f(A t) = a_0(t) E + a_1(t) A + \cdots + a_{m-1}(t) A^{m-1}
    $$

3. **待定系数法**

    求解系数 $a_0(t), a_1(t), \ldots, a_{m-1}(t)$，使其满足下列方程组：
    $$
    f(\lambda_i t) = a_0(t) + a_1(t) \lambda_i + \cdots + a_{m-1}(t) \lambda_i^{m-1}
    $$
    若有需要，还可对上述方程组求导：
    $$
    f'(\lambda_i t) = a_1(t) + 2 a_2(t) \lambda_i + \cdots + (m-1) a_{m-1}(t) \lambda_i^{m-2}
    $$
    最终可求出 $a_0(t), a_1(t), \ldots, a_{m-1}(t)$。

4. **将系数回代至 $f(A t)$**  
    $$
    f(A t) = a_0(t) E + a_1(t) A + \cdots + a_{m-1}(t) A^{m-1}
    $$

#### 例 3
设矩阵 $A = \begin{pmatrix} -2 & 1 & 3 \\ 0 & -3 & 0 \\ 0 & 2 & -2 \end{pmatrix}$，求矩阵函数 $e^{At}$。

**解：**

**最小多项式**

特征方程：
$$
|\lambda E - A| = \begin{vmatrix} \lambda + 2 & -1 & -3 \\ 0 & \lambda + 3 & 0 \\ 0 & -2 & \lambda + 2 \end{vmatrix} = (\lambda + 2)^2 (\lambda + 3)
$$

此时最小多项式可能为 $(\lambda + 2)(\lambda + 3)$ 或 $(\lambda + 2)^2 (\lambda + 3)$。

检验：
$$
(A + 2E)(A + 3E) \neq 0
$$

故最小多项式为：
$$
(\lambda + 2)^2 (\lambda + 3)
$$

最小多项式次数 $m = 3$。

**设矩阵函数形式**

设：
$$
e^{At} = a_0 E + a_1 A + a_2 A^2
$$

**求系数**

根据矩阵函数定义：
$$
e^{\lambda t} = a_0 + a_1 \lambda + a_2 \lambda^2
$$
对 $\lambda$ 求导得：
$$
t e^{\lambda t} = a_1 + 2 a_2 \lambda
$$

代入特征值：
- 特征值 $\lambda_1 = \lambda_2 = -2$（重根）
- 特征值 $\lambda_3 = -3$

得到方程组：
$$
\begin{cases}
e^{-2t} = a_0 - 2 a_1 + 4 a_2 \\
e^{-3t} = a_0 - 3 a_1 + 9 a_2 \\
t e^{-2t} = a_1 - 4 a_2
\end{cases}
$$

解得：
$$
\begin{aligned}
a_0 &= (6t - 3)e^{-2t} + 4 e^{-3t} \\
a_1 &= (1 - 5t - 4)e^{-2t} + 4 e^{-3t} \\
a_2 &= (t - 1)e^{-2t} + e^{-3t}
\end{aligned}
$$

### 考点四：矩阵函数在微分方程组中的应用

#### 一阶线性常系数齐次微分方程组  

$$
\begin{cases}
\frac{dX}{dt} = A X \\
X(0) = X_0
\end{cases}
$$
它的解为：
$$
X(t) = e^{At} X(0)
$$

#### 一阶线性常系数非齐次微分方程组  

$$
\begin{cases}
\frac{dX}{dt} = A X + F(t) \\
X(0) = X_0
\end{cases}
$$
它的解为：
$$
X(t) = e^{At} X(0) + \int_0^t e^{A(t-\tau)} F(\tau) d\tau
$$

### 考点五：矩阵函数的性质（$e^{At} \to A$）

$$
\frac{d}{dt} e^{At} = A e^{At} = e^{At} A
$$

特别地，当 $t = 0$ 时：
$$
\left. \frac{d}{dt} e^{At} \right|_{t=0} = A e^{A \cdot 0} = A e^{0} = A
$$

## 矩阵的分解  
### 考点一：矩阵的三角分解

#### Doolittle 分解法（$A = LR$）

矩阵特点（以三阶为例）：

$$
\displaystyle
A = \begin{pmatrix}
a_{11} & a_{12} & a_{13} \\
a_{21} & a_{22} & a_{23} \\
a_{31} & a_{32} & a_{33}
\end{pmatrix}
=
\begin{pmatrix}
1 & 0 & 0 \\
l_{21} & 1 & 0 \\
l_{31} & l_{32} & 1
\end{pmatrix}
\begin{pmatrix}
r_{11} & r_{12} & r_{13} \\
0 & r_{22} & r_{23} \\
0 & 0 & r_{33}
\end{pmatrix}
$$

其中：
- $L$ 是**单位下三角矩阵**（红色标注：单位下三角矩阵）；
- $R$ 是**普通上三角矩阵**（红色标注：普通上三角矩阵）；

$$
a_{1j} = \gamma_{1j} \quad (\text{即 } a_{11} = \gamma_{11}，a_{12} = \gamma_{12}，a_{13} = \gamma_{13})
$$

#### 例 1

对矩阵 $A = \begin{pmatrix} 2 & -1 & 3 \\ 1 & 2 & 1 \\ 2 & 4 & 3 \end{pmatrix}$ 的 Doolittle 分解：

解：
$$
\displaystyle
A = 
\begin{pmatrix}
2 & -1 & 3 \\
1 & 2 & 1 \\
2 & 4 & 3
\end{pmatrix}
=
\begin{pmatrix}
1 & 0 & 0 \\
\underline{\tfrac{1}{2}} & 1 & 0 \\
\underline{1} & \underline{2} & 1
\end{pmatrix}
\begin{pmatrix}
2 & -1 & 3 \\
0 & \underline{2} & \underline{-1} \\
0 & 0 & \underline{1}
\end{pmatrix}
$$

其中：
- $L$ 为单位下三角矩阵；
- $R$ 为普通上三角矩阵。

根据定义，有：

$$
a_{ij} = \text{L 的第 } i \text{ 行} \times \text{R 的第 } j \text{ 列}
$$

例如：

$$
a_{21} = 1 = \square \times 2 + 1 \times 0 + 0 \times 0 \Rightarrow \square = \tfrac{1}{2}
$$

然后按顺序依次计算未知部分：

$$
a_{11},\ a_{12},\ a_{13},\ a_{22},\ a_{23},\ a_{33}
$$

**注**

1. $L$ 和 $R$ 矩阵特点要牢记；
2. $a_{1j} = r_{1j}$；
3. 按顺序求未知部分。

