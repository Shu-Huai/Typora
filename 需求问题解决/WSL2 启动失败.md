# WSL2 启动失败

## 问题描述

> 由于未安装所需的特性，无法启动操作。
>
> Error code: Wsl/Service/CreateInstance/CreateVm/HCS_E_SERVICE_NOT_AVAILABLE

<img src="http://public.file.lvshuhuai.cn/images\image-20241113213147758.png" alt="image-20241113213147758" style="zoom:50%;" />

## 失败的解决

有人说是因为 Windows 功能中的虚拟机平台功能被禁用了，但是我尝试禁用、重启、启用、重启后未解决。

有人说是因为 Hyper-V 功能被禁用了，但事实上 WSL2 并不一定要求启用 Hyper-V 功能。

尝试重新安装 Ubuntu 分发也未解决。

## 成功的解决

[WSL无法启动解决记录："由于未安装所需的特性，无法启动操作。""Windows无法启动Hyper-V主机计算服务服务(位于 本地计算机 上)。错误1053:服务没有及时响应启动或控制请求。" - 进击的嘎嘣脆 - 博客园](https://www.cnblogs.com/liqiujiong/p/16802007.html)

根据该文章所说，由于 Windows Defender 的安全策略问题，我之前因为不知道什么原因对 `Windows 安全中心`中的`应用和浏览器控制`中的 `Exploit Protection` 进行了一些修改。

出现问题后，将全部选项改为使用默认值，解决了这个问题。

<img src="http://public.file.lvshuhuai.cn/images\image-20241113212936005.png" alt="image-20241113212936005" style="zoom:50%;" />

文中提到，`修改代码流保护(CFG)并取消选中覆盖系统设置`，未单独尝试。