# Ubuntu 18.04 与 VSCode 的 glibc 兼容问题

## 问题描述

使用 VSCode 中的 Remote SSH 插件连接 Ubuntu 18.04 服务器时，报错`远程主机可能不符合 glibc 和 libstdc++ VS Code 服务器的先决条件`

使用终端命令行的方式连接能够正常运行

![img](http://public.file.lvshuhuai.cn/images\nzuolu5zc5w3p8hn6d.png)

## 问题原因

- 从 VS Code 1.99 版本（2025 年 3 月）开始， 由VS Code 发布的预构建服务器只兼容基于 glibc 2.28 或更高版本的 Linux 发行版。
- 但服务器是 Ubuntu 18.04，glibc 版本 2.27

## 解决方案

### 方案

用户级编译 glibc 2.28

### 步骤

#### 创建用户级编译的目录

这里选择 `~/.local/opt`

  ```bash
  cd ~
  mkdir -p ~/.local/src/opt
  mkdir -p ~/.local/opt
  cd ~/.local/src/opt
  ```

#### 下载源代码

```bash
# 升级glibc需要的依赖(我不清楚除了make之外的是否必要，但是我都安装了)
wget https://ftp.gnu.org/gnu/binutils/binutils-2.32.tar.gz
wget https://ftp.gnu.org/gnu/bison/bison-3.2.1.tar.gz
wget https://ftp.gnu.org/pub/gnu/make/make-4.3.tar.gz

# glibc-2.28安装包
wget https://ftp.gnu.org/gnu/glibc/glibc-2.28.tar.gz
```

#### 安装 binutils

```bash
# 进入目录
cd ~/.local/src/opt
# 解压
tar -xzvf binutils-2.32.tar.gz
# 安装
cd binutils-2.32
./configure --prefix=$HOME/.local/opt/binutils-2.32
make -j16  # 根据CPU核心自行设置，用于并行加速
make install
```

#### 使其生效

```bash
vim ~/.bashrc
# 在文件中加上（按i开启输入，粘贴以下命令，完成后按Esc，然后输入:wq，最后Enter就好啦）
# 注意，如果你不清楚你在做什么，请把export放在整个~/.bashrc的最前方
export PATH="$HOME/.local/opt/binutils-2.32/bin:$PATH"  # binutils 2.32
# 使其生效
source ~/.bashrc
# 测试
ld --version
```

#### 安装 bison

```bash
# 进入目录
cd ~/.local/src/opt
# 解压
tar -xzvf bison-3.2.1.tar.gz
# 安装
cd bison-3.2.1
./configure --prefix=$HOME/.local/opt/bison-3.2.1
make -j16  # 根据CPU核心自行设置，用于并行加速
make install
```

#### 使其生效

```bash
vim ~/.bashrc
# 在文件中加上（按i开启输入，粘贴以下命令，完成后按Esc，然后输入:wq，最后Enter就好啦）
# 注意，如果你不清楚你在做什么，请把export放在整个~/.bashrc的最前方
export PATH="$HOME/.local/opt/bison-3.2.1/bin:$PATH"  # bison 3.2.1
# 使其生效
source ~/.bashrc
# 测试
bison --version
```

#### 安装 make

```bash
# 进入目录
cd ~/.local/src/opt
# 解压
tar -zxvf make-4.3.tar.gz
# 安装
cd make-4.3
./configure --prefix=$HOME/.local/opt/make-4.3
make -j16  # 根据CPU核心自行设置，用于并行加速
make install
```

#### 使其生效

```bash
vim ~/.bashrc
# 在文件中加上（按i开启输入，粘贴以下命令，完成后按Esc，然后输入:wq，最后Enter就好啦）
# 注意，如果你不清楚你在做什么，请把export放在整个~/.bashrc的最前方
export PATH="$HOME/.local/opt/make-4.3/bin:$PATH"  # make 4.3
# 使其生效
source ~/.bashrc
# 测试
make --version
```

#### 创建链接

```bash
# 创建符号链接
ln -s "$HOME/.local/opt/make-4.3/bin/make" "$HOME/.local/opt/make-4.3/bin/gmake"
# 使其生效
source ~/.bashrc
# 测试
gmake --version
```

#### 安装 glibc

```bash
# 进入目录
cd ~/.local/src/opt
# 解压
tar -zxvf glibc-2.28.tar.gz
# 安装
cd glibc-2.28
mkdir build && cd build  # 注意多了一步创建build文件夹，其实上述安装步骤也可以执行这一步，使得源代码目录更干净，但是我懒，不过这里必须创建
../configure --prefix=$HOME/.local/opt/glibc-2.28 --disable-profile --enable-add-ons --disable-werror  # 注意需要关闭-Werror
make -j16  # 根据CPU核心自行设置，用于并行加速
make install
```

#### 安装 patchelf

```bash
# 进入目录
cd ~/.local/src
# 下载，如果不能访问github，自己找镜像
wget https://github.com/NixOS/patchelf/releases/download/0.18.0/patchelf-0.18.0.tar.bz2
# 解压
tar -jxvf patchelf-0.18.0.tar.bz2
# 安装
cd patchelf-0.18.0
./configure --prefix=$HOME/.local/
make -j16  # 根据CPU核心自行设置，用于并行加速
make install
```

#### 使其生效

```bash
vim ~/.bashrc
# 在文件中加上（按i开启输入，粘贴以下命令，完成后按Esc，然后输入:wq，最后Enter就好啦）
# 注意，如果你不清楚你在做什么，请把export放在整个~/.bashrc的最前方
export PATH="$HOME/.local/bin:$PATH"
# 使其生效
source ~/.bashrc
# 测试
patchelf --version
```

#### 设置自动运行 patchelf

```bash
# 注意，如果你不清楚你在做什么，请把以下3条export放在整个~/.bashrc的最前方
# 注意，如果你不清楚你在做什么，请把以下3条export放在整个~/.bashrc的最前方
# 注意，如果你不清楚你在做什么，请把以下3条export放在整个~/.bashrc的最前方
# vscode
export VSCODE_SERVER_CUSTOM_GLIBC_LINKER="$HOME/.local/opt/glibc-2.28/lib/ld-linux-x86-64.so.2"
# 注意，这里不同系统一般不同
# rpath需要包含系统库，否则报错找不到libstdc++.so.6： error while loading shared libraries: libstdc++.so.6: cannot open shared object file: No such file or directory
# 请把 /usr/lib64 换成你的 libstdc++.so.6 所在路径 （find / -name libstdc++.so.6 2>/dev/null，一般可以将命令中的/换为/usr/lib*）
# 若继续报错其他库找不到，将库所在路径添加到最后面即可，使用":"分隔
export VSCODE_SERVER_CUSTOM_GLIBC_PATH="$HOME/.local/opt/glibc-2.28/lib:/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu:/usr/lib:/lib"
export VSCODE_SERVER_PATCHELF_PATH="$HOME/.local/bin/patchelf"
```

## 修复结果

完美运行

<img src="http://public.file.lvshuhuai.cn/images\image-20251120154339507.png" alt="image-20251120154339507" style="zoom:50%;" />