# WSL2 安装 Anaconda3 报错

## 描述

>  OSError: [Errno 40] Too many levels of symbolic links

## 原因

这是由于我在安装 Anaconda3 时，在选择安装位置时使用了挂载的虚拟磁盘 `/mnt/f/software/anaconda3`

<img src="http://public.file.lvshuhuai.cn/images\image-20241113213712312.png" alt="image-20241113213712312" style="zoom:50%;" />

["conda update conda" error · Issue #10333 · conda/conda](https://github.com/conda/conda/issues/10333#issuecomment-919739093)、[WSL builds failing with `OSError: [Errno 40] Too many levels of symbolic links` for ncurses-6.3 · Issue #3564 · spinalcordtoolbox/spinalcordtoolbox](https://github.com/spinalcordtoolbox/spinalcordtoolbox/issues/3564) 中似乎也提到了这个问题。

这似乎是 Anaconda 的一个 bug。

## 解决

将安装位置设为默认（`~/anaconda3`）解决。

具体原因并未深究。