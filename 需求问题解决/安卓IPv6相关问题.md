# 安卓 IPv6 相关问题

## 安卓支持 IPv6 吗？

支持的。

使用移动数据流量可以获取到 IPv6 地址。

连接到特定 WLAN 也可以获取到 IPv6 地址。

## 安卓支持 DHCPv6 吗？

不支持。

Google 的开发团队明确决定不在 Android 系统中实现对 DHCPv6 的支持，而是依赖 **SLAAC（Stateless Address Autoconfiguration，无状态地址自动配置）** 来获取 IPv6 地址。

### 为什么？

Google 认为在 IPv6 网络中，SLAAC 已经足够满足移动设备的自动配置需求。SLAAC 能通过路由器通告（RA）为设备分配地址，而无需依赖 DHCPv6。

Android 主要面向移动设备，简化网络配置、减少复杂性是其设计目标之一。因此，Google 选择不支持 DHCPv6，认为这有助于网络的无缝配置。

## 问题描述

在了解到安卓不支持 DHCPv6 后，我在路由器中配置了关闭 DHCPv6，并打开了 SLAAC。

<img src="http://public.file.lvshuhuai.cn/images\image-20250203142851317.png" alt="image-20250203142851317" style="zoom:50%;" />

<img src="http://public.file.lvshuhuai.cn/images\image-20250203143214723.png" alt="image-20250203143214723" style="zoom:50%;" />

在手机上成功获取到了全球 IPv6 地址，也能够正常上网。

但过了几小时后，IPv6 地址正常，但无法访问基于 IPv6 的资源，打开浏览器访问，显示 `DNS_PROBE_FINISHED_NXDOMAIN`。

## 问题原因

我在路由器的配置中，DNS 的配置方式选择了 DHCPv6，虽然 IP 地址是通过 SLAAC 获取的，但 DNS 无法获取到。

## 问题解决

使用 RDNSS 以便 Android 设备可以自动获取 DNS 信息。

**RDNSS（Router Advertisement DNS Server）** 是 IPv6 中的一种机制，用于通过 **路由器通告（Router Advertisement, RA）** 向设备提供 DNS 服务器地址。它是 **无状态地址自动配置**（SLAAC）的一部分，允许设备在没有依赖 DHCPv6 服务器的情况下，自动获取 DNS 服务器信息。

<img src="http://public.file.lvshuhuai.cn/images\image-20250203142935706.png" alt="image-20250203142935706" style="zoom:50%;" />