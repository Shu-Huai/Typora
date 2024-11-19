# Ubuntu 中安装 Pytorch3D

## 一些版本

- WSL 2
- Ubuntu 24.04.1 LTS
- CUDA 11.8（使用 11.7 以前的版本需要 CUB 库，笔者未尝试）
- Windows NVIDIA Driver 566.03
- Windows CUDA 12.7
- NVIDIA RTX 3090
- PyTorch 2.4.1（截至目前 2024.11.13，使用更新的 2.5 会报错）
- Python 3.10
- PyTorch3D 0.7.8

## 安装步骤

安装基于 Anaconda3 创建的虚拟环境进行。

### 1. 创建虚拟环境，安装先决条件

假设环境中已有Anaconda3

命令：

```
conda create -p ./venv python=3.10 -y
conda actviate ./venv
conda install pytorch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1  pytorch-cuda=11.8 -c pytorch -c nvidia -y
```

这里是在创建虚拟环境、安装PyTorch

### 2. 安装PyTorch3D

官方安装指导：[pytorch3d/INSTALL.md at main · facebookresearch/pytorch3d](https://github.com/facebookresearch/pytorch3d/blob/main/INSTALL.md)

#### Anaconda Cloud

官方给出的`仅在 Linux 系统上从 Anaconda Cloud 安装带有 CUDA 支持的版本。`，`conda install pytorch3d -c pytorch3d` 不可用，会报错

> ```bash
> Collecting package metadata (current_repodata.json): done
> Solving environment: done
> Segmentation fault (core dumped)
> ```

原因未知

根据 [conda报错Segmentation fault (core dumped) - 简书](https://www.jianshu.com/p/5e230ef8a14d) 所说

> 当出现这种报错，证明你之前安装过这软件，但不成功，部分零件只下载了一半就 fail 了。
>
> 所以，你应该先去删除 anaconda3 文件中 pkg 文件夹内，对应的软件 zip 包或 tar.gz 包，再回到 conda 用 clean 命令清除残余。
>
>  -a 用于删除索引缓存、锁定文件、未使用过的包和 tar 包
>
> ```bash
> conda clean -a 
> ```
>
> 再重新安装即可！

未尝试

#### 预购建的 wheels

官方预购建了一些 wheels，但版本不合适，不使用

> 我们为 PyTorch1.11.0、每个受支持的 CUDA 版本以及 Python 3.8 和 3.9 预制了用于 Linux 的 CUDA 轮子。

#### 从源码构建

```bash
pip install "git+https://github.com/facebookresearch/pytorch3d.git@stable"
```

## 可能遇到的错误

### no such file 错误

这可能是由于在 conda 虚拟环境中安装的 CUDA，在 Ubuntu 中安装合适的 CUDA 后解决了这个问题。

### ninja -v 错误

这可能是由于使用了 PyTorch 2.5 级以上版本。截至目前（2024.11.13），报错后改用 2.4.1 解决了这个问题。

### gcc 不兼容错误

详见 [CUDA 和 Ubuntu 的 gcc 版本问题 - 殊怀丶](http://blog.lvshuhuai.cn/#/article/50)。