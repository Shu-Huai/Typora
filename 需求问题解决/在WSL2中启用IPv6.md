# 在 WSL 2 中启用 IPv6

## 一些环境

- Windows 11
- WSL 2
- Ubuntu 24

## 需求

宿主机中有公网 IPv6 地址，如何在 WSL 2 中启用 IPv6？

## 步骤

### 创建虚拟网络交换机

<img src="http://public.file.lvshuhuai.cn/images\image-1671677315891.png" alt="image-1671677315891" style="zoom:50%;" />

1. 在 `Hyper-V 管理器中`，打开`虚拟交换机管理器`
2. 点击`新建虚机网络交换机`，选择外部，再选择需要连接到的外部网络网卡
3. 输入名称，这里使用 `VMWSL2`

### 创建 WSL 2 配置文件

在 `C:\Users\<用户名>`目录下，打开文件 `.wslconfig`，如果没有就新建一个。

其中涉及到 IPv6 的关键配置项为

```yaml
[wsl2]
networkingMode=bridged    # 启用镜像网络特性支持
vmSwitch="VMWSL2"
```

这里给出我的文件内容

```yaml
# 推荐的一些配置项如下

[wsl2]                      # 核心配置
autoProxy=true             # 是否强制 WSL2/WSLg 子系统使用 Windows 代理设置（请根据实际需要启用）
dnsTunneling=false          # WSL2/WSLg DNS 代理隧道，以便由 Windows 代理转发 DNS 请求（请根据实际需要启用）
firewall=true               # WSL2/WSLg 子系统的 Windows 防火墙集成，以便 Hyper-V 或者 WPF 能过滤子系统流量（请根据实际需要启用）
guiApplications=true        # 启用 WSLg GUI 图形化程序支持
ipv6=true                   # 启用 IPv6 网络支持
localhostForwarding=true    # 启用 localhost 网络转发支持

# memory=64GB                  # 限制 WSL2/WSLg 子系统的最大内存占用

nestedVirtualization=true   # 启用 WSL2/WSLg 子系统嵌套虚拟化功能支持
networkingMode=bridged      # 启用镜像网络特性支持
vmSwitch="VMWSL2"
#pageReporting=true          # 启用 WSL2/WSLg 子系统页面文件通报，以便 Windows 回收已分配但未使用的内存

# processors=8                # 设置 WSL2/WSLg 子系统的逻辑 CPU 核心数为 8（最大肯定没法超过硬件的物理逻辑核心数）

vmIdleTimeout=-1            # WSL2 VM 实例空闲超时关闭时间，-1 为永不关闭，根据参数说明，目前似乎仅适用于 Win11+

[experimental]                  # 实验性功能（按照过往经验，若后续转正，则是配置在上面的 [wsl2] 选节）
autoMemoryReclaim=gradual       # 启用空闲内存自动缓慢回收，其它选项：dropcache / disabled（立即/禁用）
hostAddressLoopback=true        # 启用 WSL2/WSLg 子系统和 Windows 宿主之间的本地回环互通支持
sparseVhd=true                  # 启用 WSL2/WSLg 子系统虚拟硬盘空间自动回收
bestEffortDnsParsing=true       # 和 dnsTunneling 配合使用，Windows 将从 DNS 请求中提取问题并尝试解决该问题，从而忽略未知记录（请根据实际需要启用）
useWindowsDnsCache=false        # 和 dnsTunneling 配合使用，决定是否使用 Windows DNS 缓存池
```

### 重启 WSL 2

```bash
wsl --shutdown
wsl
```

