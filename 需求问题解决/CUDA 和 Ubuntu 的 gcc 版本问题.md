# CUDA 和 Ubuntu 的 gcc 版本问题

## 一些版本

- WSL 2
- Ubuntu 24.04.1 LTS
- CUDA 11.8
- Windows NVIDIA Driver 566.03
- Windows CUDA 12.7
- NVIDIA RTX 3090
- PyTorch 2.4.1
- Python 3.10
- PyTorch3D 0.7.8

## 描述

在编译安装 PyTorch3D 时，出现了如下报错

> #error -- unsupported GNU version! gcc versions later than 10 are not supported! The nvcc flag '-allow-unsupported-compiler' can be used to override this version check; however, using an unsupported host compiler may cause compilation failure or incorrect run time execution. Use at your own risk.

这个错误是说，CUDA 不支持高于 10 以上版本的 gcc 编译器

## 解决

首先尝试将 Ubuntu 自带的 gcc 13 卸载，并安装 gcc-10，但在卸载 gcc 后，发现之前安装的 CUDA 也一并消失了，运行 `nvcc -V` 后显示没有该包。

再按照 [WSL2 Ubuntu 中安装 CUDA 11.8 - 殊怀丶](http://blog.lvshuhuai.cn/#/article/48) 重新安装 CUDA，发现 gcc 版本又变回 13 了。

根据 [CUDA与我的gcc版本不兼容 | 码农家园](https://www.codenong.com/6622454/) 给出的方案，进行解决。

文中使用更改软连接的方式

命令：

```bash
# 安装支持的gcc版本
sudo apt-get install gcc-10
sudo apt-get install g++-10

# 更改软连接
cd /usr/bin
sudo rm gcc
sudo rm g++
sudo ln -s /usr/bin/gcc-10 gcc
sudo ln -s /usr/bin/g++-10 g++
```

问题解决