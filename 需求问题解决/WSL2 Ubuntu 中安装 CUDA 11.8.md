# WSL2 Ubuntu 中安装 CUDA 11.8

## 各种版本

- WSL 2
- Ubuntu 24.04.1 LTS
- CUDA 11.8
- Windows NVIDIA Driver 566.03
- Windows CUDA 12.7
- NVIDIA RTX 3090

## 安装

1. 访问[CUDA Toolkit Archive | NVIDIA Developer](https://developer.nvidia.com/cuda-toolkit-archive)网站，找到对应的 CUDA 版本（11.8）[CUDA Toolkit 11.8 Downloads | NVIDIA Developer](https://developer.nvidia.com/cuda-11-8-0-download-archive)。

2. 依次选择 `Linux`、`x86_64`、`WSL-Ubuntu`、`2.0`、`deb(local)`，会得到如图所示的下载命令
   <img src="http://public.file.lvshuhuai.cn/images\image-20241113195452980.png" alt="image-20241113195452980" style="zoom:50%;" />

3. 根据官方给出的命令安装，可能遇到的问题在`问题`中给出
   ```bash
   wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
   sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
   wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-wsl-ubuntu-11-8-local_11.8.0-1_amd64.deb
   sudo dpkg -i cuda-repo-wsl-ubuntu-11-8-local_11.8.0-1_amd64.deb
   sudo cp /var/cuda-repo-wsl-ubuntu-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
   sudo apt-get update
   sudo apt-get -y install cuda
   ```

4. 将 CUDA 添加至环境变量

   1. 用 nano 文本编辑器打开 `~/.bashrc` 文件。
      ```bash
      nano .bashrc
      ```

   2. 在末尾添加如下文本
      ```
      export CUDA_HOME=/usr/local/cuda-11.8
      export PATH=$PATH:$CUDA_HOME/bin
      export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64
      export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/extras/CUPTI/lib64
      ```

      <img src="http://public.file.lvshuhuai.cn/images\image-20241113200804701.png" alt="image-20241113200804701" style="zoom:50%;" />

   3. 按 `ctrl+X` 退出，`Y` 保存，`enter `确定。然后输入：
      ```bash
      source ~/.bashrc
      ```

      环境变量生效。

## 问题

### Depends: libtinfo5 but it is not installable

#### 描述

在执行最后一步 `sudo apt-get -y install cuda` 时可能会出现如下问题

> The following packages have unmet dependencies:
>  nsight-systems-2023.3.3 : Depends: libtinfo5 but it is not installable
> E: Unable to correct problems, you have held broken packages.

尝试手动安装此类库，但提示这个包在包管理器中不存在安装候选。

#### 原因

这是由于软件包在 Ubuntu 高版本的默认存储库中尚不可用，也就是我这里用的 24 版本太高了，根据 [nvidia - 在 Ubuntu 23.10 上安装 CUDA - libt5info 无法安装 - Ask Ubuntu](https://askubuntu.com/questions/1491254/installing-cuda-on-ubuntu-23-10-libt5info-not-installable) 的描述，在 23 版本上也会存在这个问题。

可以通过添加 Ubuntu 的存储库来安装它。

#### 解决

对于 Ubuntu 24.04 或更高版本

1. 打开用于存储源列表的文件（该文件在 Ubuntu 24 中更换了存储位置）

   ```bash
   sudo nano /etc/apt/sources.list.d/ubuntu.sources
   ```

2. 在文件末尾粘贴以下内容：

   ```
   Types: deb
   URIs: http://archive.ubuntu.com/ubuntu/
   Suites: lunar
   Components: universe
   Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
   ```

3. 保存文件并运行 `sudo apt update`。

4. 重新运行 `sudo apt-get -y install cuda`。

### gcc、g++ 版本不匹配问题

这个问题在笔者安装时未出现，但在后续安装编译 PyTorch3D 时出现了，是 CUDA 不支持 Ubuntu 自带的 gcc 版本因此在这里引用记录一下。

[CUDA 和 Ubuntu 的 gcc 版本问题 - 殊怀丶](http://blog.lvshuhuai.cn/#/article/50)

## 检查安装结果

使用命令 `nvcc -V` 检查结果。

<img src="http://public.file.lvshuhuai.cn/images\image-20241113195739319.png" alt="image-20241113195739319" style="zoom:50%;" />