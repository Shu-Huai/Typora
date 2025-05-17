## 矩阵特征值的估计  
### 考点一：Gerschgorin 盖尔圆定理

#### 盖尔圆定义

盖尔圆 $G_i$：$|z - a_{ii}| \leq R_i$

盖尔圆半径 $R_i = \sum\limits_{\substack{j=1 \\ j \neq i}}^n |a_{ij}|$

设 $A = (a_{ij})_{n \times n}$，以三阶为例 $n = 3$，矩阵 $A$ 形式为：
$$
A = \begin{pmatrix}
a_{11} & a_{12} & a_{13} \\
a_{21} & a_{22} & a_{23} \\
a_{31} & a_{32} & a_{33}
\end{pmatrix}
$$

则三个盖尔圆分别为：
- $G_1$：$|z - a_{11}| \leq |a_{12}| + |a_{13}|$
- $G_2$：$|z - a_{22}| \leq |a_{21}| + |a_{23}|$
- $G_3$：$|z - a_{33}| \leq |a_{31}| + |a_{32}|$

#### 盖尔圆定理

矩阵 $A \in \mathbb{C}^{n \times n}$ 的全体特征值都在它的 $n$ 个盖尔圆构成的并集之中。

#### $A$ 的列盖尔圆

对于 $A \in \mathbb{C}^{n \times n}$，与 $A^T$ 的特征值相同，根据盖尔圆定理，$A$ 的特征值也在 $A^T$ 的 $n$ 个盖尔圆构成的并集之中。

**称 $A^T$ 的盖尔圆为 $A$ 的列盖尔圆。**

#### 例 1

估计矩阵 $A = \begin{pmatrix} -3 & 1 & 0 & 1 \\ 1 & 3 & -2i & 0 \\ 0 & -i & 8 & i \\ 1 & 0 & 0 & 3i \end{pmatrix}$ 的特征值分布。

解：$A$ 的 4 个盖尔圆分别为：

- $G_1$：$|z + 3| \leq 2$
- $G_2$：$|z - 3| \leq 3$
- $G_3$：$|z - 8| \leq 2$
- $G_4$：$|z - 3i| \leq 1$

因此 $A$ 的特征值一定在 $\bigcup_{i=1}^4 G_i$ 之中，如图 1 所示：

<img src="Z:\Public\images\file-3amJbKCFUoHXRfS9SC2GfM" alt="输出图片" style="zoom:25%;" />

矩阵 $A^T = \begin{pmatrix} -3 & 1 & 0 & 1 \\ 1 & 3 & -i & 0 \\ 0 & -2i & 8 & 0 \\ 1 & 0 & i & 3i \end{pmatrix}$

A 的 4 个列盖尔圆分别为：

- $G_1'$：$|z + 3| \leq 2$
- $G_2'$：$|z - 3| \leq 2$
- $G_3'$：$|z - 8| \leq 2$
- $G_4'$：$|z - 3i| \leq 2$

因此，$A$ 的特征值必然位于 $\bigcup_{i=1}^4 G_i'$ 之中，如图 2 所示。

<img src="Z:\Public\images\file-JkvoJ1bRSH39uvR6wWCbvr" alt="输出图片" style="zoom:25%;" />

#### 推论

若 $A$ 为实矩阵，$A \in \mathbb{R}^{n \times n}$，且 $A$ 的 $n$ 个盖尔圆是孤立的，则 $A$ 有 $n$ 个互不相同的实特征值。

#### 根据盖尔圆定理  

对于任意矩阵 $A$，特征值一定满足 $|\lambda - a_{ii}| \leq R_i$。若 $\lambda = 0$，则 $|a_{ii}| \leq R_i$。

若矩阵 $A$ 存在对角占优，即 $|a_{ii}| > R_i$，则 $\lambda \neq 0$，$|A| \neq 0$。

#### $A$ 为实矩阵时的共轭复根

若 $A$ 为实矩阵，特征方程 $|\lambda E - A| = 0$ 为实系数方程，它的复根一定成对出现，且一定是共轭的，即 $\alpha \pm i\beta$ 的形式。
