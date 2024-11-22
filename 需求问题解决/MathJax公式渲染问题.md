# MathJax 公式渲染问题

MathJax 是一个开源的 JavaScript 库，主要用于在网页上显示高质量的数学公式。

在博客项目 `WeBlog` 中引入改库以渲染 Latex 格式的数学公式，但在使用中发现了一些问题，遂记录。

## 问题一 大括号不显示

在 MathJax 中 `\{` 这样的大括号不能正确渲染，原因未知

需要改成 `\lbrace` 和 `\rbrace`

<img src="http://public.file.lvshuhuai.cn/images\image-20241122161808866.png" alt="image-20241122161808866" style="zoom:50%;" />

## 问题二 多行公式不换行

一般写 Latex 多行公式会使用 `\\` 来换行，例如

```latex
$$
P(i,j) =\left\lbrace\begin{aligned} \text{true} && 如果子串S_i\cdots S_j 是回文串 \\ \text{false} && 其他情况\end{aligned}\right.
$$
```

应该这样显示

<img src="http://public.file.lvshuhuai.cn/images\image-20241122161937235.png" alt="image-20241122161937235" style="zoom:50%;" />

然而实际渲染出来却不能换行

<img src="http://public.file.lvshuhuai.cn/images\image-20241122162025050.png" alt="image-20241122162025050" style="zoom:50%;" />

查看编译过后的 html 文件发现，其中的 `\\` 都被转义成了 `\`，这样是无法显示换行的。

一种不够优雅的解决方案是直接使用 `\\\\` 来进行转义

```latex
$$
P(i,j) =\left\lbrace\begin{aligned} \text{true} && 如果子串S_i\cdots S_j 是回文串 \\\\ \text{false} && 其他情况\end{aligned}\right.
$$
```

但这样的话在其他地方可能出现问题，如在 Typora 中，这实际上是换了两次行。

<img src="http://public.file.lvshuhuai.cn/images\image-20241122162418962.png" alt="image-20241122162418962" style="zoom:50%;" />

目前没有更好的解决方案，或许可以根据项目代码进行配置，如在读取公式字符串的时候如果有 `\\` 就改成 `\\\\`，但这样需要修改业务代码，暂时不做尝试。

## 问题三 字体标注无法编译、无法正常渲染

在使用 `\mathbf`、`\mathbb` 这样的字体标注时，我的习惯是不论有几个字符需要使用该字体，都使用大括号包装，例如

```latex
$\mathbb{M}$
$\mathcal{Loss}$
```

这样的写法在 Latex 编译器、在 Typora 中都能够正常显示，但在 MathJax 中却渲染失败。

经测试，对于一个字符的使用情况，不能使用大括号包装。

```latex
$\mathbb M$
$\mathcal{Loss}$
```

这样才能正常显示。

这样的写法在其他编辑器中也能够正常显示。
