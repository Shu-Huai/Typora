# Powershell 设置默认 UTF-8

## 问题

在 2024.12.19，Windows 11 中，Powershell 默认使用的是 GBK（936）。这样会导致在终端中一些情况下的乱码。

如在 Git 中，对中文文件名的乱码。

<img src="http://public.file.lvshuhuai.cn/images\image-20241219143559100.png" alt="image-20241219143559100" style="zoom:50%;" />

## 解决

### 设置代码页为 65001

```shell
chcp 65001
```

经测试，这样的方法失败。

或许在一些情况下能够解决乱码问题，但在 Git 中失败。

<img src="http://public.file.lvshuhuai.cn/images\image-20241219143836019.png" alt="image-20241219143836019" style="zoom:50%;" />

### 设置注册表

根据教程 [Powershell改变默认编码_修改powershell默认编码-CSDN博客](https://blog.csdn.net/u014756245/article/details/100536552)所示，尝试修改，但失败

### 修改系统字符编码设置

![img](http://public.file.lvshuhuai.cn/images\image-1024x860.png)

勾选 UTF-8 确认就行。

但这样的方法并不优雅，因为有些软件是使用 GBK 编码的，这样的方式会导致一些软件乱码。

而且修改后还需要重启系统，很麻烦。

### 修改个人配置文件

在打开的 Powershell 中，输入代码

```shell
$PROFILE
```

会显示出个人配置文件的位置

```shell
C:\Users\lvzhi\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

打开这个 ps1 脚本，在最后添加如下行

```shell
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding
```

保存并重启终端，测试有效。

<img src="http://public.file.lvshuhuai.cn/images\image-20241219144446360.png" alt="image-20241219144446360" style="zoom:50%;" />

#### 另外，可能会遇到问题

Windows 上 PowerShell 默认是禁止执行脚本文件的

使用以下命令修改

```shell
Set-Executionpolicy RemoteSigned
```