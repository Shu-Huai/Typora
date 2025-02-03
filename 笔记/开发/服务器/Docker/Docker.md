# Docker

## Docker核心概念

### Docker 是什么？

- Docker 是一个容器化平台，可以将应用及其依赖打包成一个轻量级、可移植的容器。
- 容器共享宿主机的操作系统内核，启动更快，资源占用更少。

### 容器 vs 虚拟机

- **虚拟机**：需要完整的操作系统，占用资源多，启动慢。
- **容器**：共享宿主机内核，轻量级，秒级启动。

### 镜像和容器

- **镜像**：类似“安装包”，是一个静态的模板（例如：Ubuntu 镜像、MySQL 镜像）。
- **容器**：镜像运行后的实例，是一个隔离的进程环境。

## 安装

### Linux

使用包管理器安装

```shell
sudo apt-get install docker.io
```

### Windows

Docker Desktop

[Docker: Accelerated Container Application Development](https://www.docker.com/)

##  基础操作命令

### 镜像管理

- 拉取镜像：`docker pull nginx`（从仓库下载镜像）。
- 查看本地镜像：`docker images`。
- 删除镜像：`docker rmi <镜像名>`。

### 容器管理

- 运行容器：`docker run -d -p 80:80 --name my-nginx nginx`（`-d` 后台运行，`-p` 端口映射，`--name` 自定义名称）。
- 查看运行中的容器：`docker ps`。
- 停止/启动容器：`docker stop <容器名>` / `docker start <容器名>`。
- 进入容器终端：`docker exec -it <容器名> /bin/bash`。
- 删除容器：`docker rm <容器名>`。

#### 一些选项

在 Docker 命令中，`-i` 和 `-t` 是常用的选项，用于控制容器的交互模式和终端分配。

- **`-i`（`--interactive`）**：使容器保持标准输入（STDIN）打开，以便您可以与容器进行交互。
- **`-t`（`--tty`）**：为容器分配一个伪终端（TTY），这对于需要终端支持的应用程序或命令（如 Bash）是必要的。

通常，这两个选项一起使用，写作 `-it`，以便在启动容器时既保持交互性，又提供终端支持。例如：

```bash
docker run -it ubuntu /bin/bash
```

这条命令启动一个基于 Ubuntu 镜像的容器，并在其中运行 Bash shell，使您能够直接在容器内输入命令。

需要注意的是，`-i` 和 `-t` 选项的组合主要用于需要与容器进行交互的场景，如调试或手动配置。对于在后台运行的容器，这些选项通常不需要使用。