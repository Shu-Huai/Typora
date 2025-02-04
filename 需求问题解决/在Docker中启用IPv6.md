# 在 Docker 中启用IPv6

## 一些环境

- Windows 11
- Docker
- WSL 2

## 需求

宿主机中有公网 IPv6 地址，如何在 Docker 容器中启用 IPv6？

## 解决

Windows 中的 Docker 可以基于 Hyper V 虚拟机或 WSL 虚拟平台。我这里基于 WSL 2。

### 1. 首先开启 WSL 的IPv6 支持

### 2. 配置 Docker 使用 IPv6

编辑 Docker 守护进程配置文件

在 Docker Desktop 的设置中，找到 `Docker Engine` 选项。在右边的 json 文件中添加如下配置：

```json
{
  "ipv6": true,
  "fixed-cidr-v6": "2409:8a1e:35d0:63c0:0001:0000:0000:0000/80"
}
```

其中，`fixed-cidr-v6` 配置代表想为 Docker 容器分配的子网地址，这个地址应该根据本机来。

例如，我本机的 ip 地址是 `2409:8a1e:35d0:63c0:3efd:feff:feb2:6f18`，网络前缀是 `2409:8a1e:35d0:63c0::/64`。

需要将 `/64` 前缀进一步划分为更小的子网，例如 `/80`，可以从第 65 位开始进行子网划分。例如，将 `2409:8a1e:35d0:63c0::/64` 划分为多个 `/80` 子网，每个子网的范围如下：

- 子网 1：`2409:8a1e:35d0:63c0:0000:0000:0000:0000/80`
- 子网 2：`2409:8a1e:35d0:63c0:0001:0000:0000:0000/80`
- 子网 3：`2409:8a1e:35d0:63c0:0002:0000:0000:0000/80`
- ...

选择其中一个子网分配，请注意，请确保该子网未被其他实例、主机或 Docker 进程分配过。

<img src="http://public.file.lvshuhuai.cn/images\image-20250204163745782.png" alt="image-20250204163745782" style="zoom:50%;" />

### 运行容器

```bash
docker run --network=bridge -it ubuntu /bin/bash
```

并验证配置