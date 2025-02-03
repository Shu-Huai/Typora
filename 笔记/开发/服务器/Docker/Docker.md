# Docker

## Docker核心概念

### Docker 是什么？

<img src="http://public.file.lvshuhuai.cn/images\01ab3c3dcaddddb368f5f0fa3ace7c27.png" alt="img" style="zoom:50%;" />

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

```bash
sudo apt-get install docker.io
```

### Windows

Docker Desktop

[Docker: Accelerated Container Application Development](https://www.docker.com/)

##  基础操作命令

### 镜像管理

#### 1. 拉取镜像

```bash
docker pull <镜像名>:<标签>        # 例: docker pull ubuntu:20.04
```

#### 2. 查看镜像

```bash
docker images                     # 列出本地所有镜像
docker image ls                   # 同上（新语法）
docker image inspect <镜像ID>     # 查看镜像详细信息
```

#### 3. 构建镜像

```bash
docker build -t <镜像名>:<标签> <上下文目录>  # 例: docker build -t myapp:v1 .
```

**关键参数**：

- **`-t`（全称 `--tag`）**：指定构建后的镜像名称和标签（可省略标签，默认使用 `latest`）。

- `-f`: 指定 Dockerfile 路径（默认是当前目录的 Dockerfile）
- `--no-cache`: 禁用缓存构建
- **`<构建上下文路径>`**：通常是 Dockerfile 所在的目录（常用 `.` 表示当前目录）。

**构建上下文路径**：

- `docker build` 的最后一个参数是构建上下文路径（通常是 Dockerfile 所在目录）。
- Docker 会将此目录下的所有文件发送给 Docker 守护进程（Daemon），因此建议通过 `.dockerignore` 文件忽略无关文件（如 `node_modules`、`.git`）。

#### 4. 删除镜像

```bash
docker rmi <镜像名或ID>           # 删除单个镜像
docker image prune               # 删除未被使用的镜像（悬空镜像）
```

### 容器生命周期

#### 1. 启动容器

```bash
docker run [参数] <镜像名> [命令]
```

**常用参数**：

- `-d`: 后台运行（detached 模式）
- `-it`: 交互式终端（通常与 `/bin/bash` 结合使用）
- `--name`: 指定容器名称
- `-p <主机端口>:<容器端口>`: 端口映射（例: `-p 8080:80`）
- `-v <主机目录>:<容器目录>`: 挂载数据卷（例: `-v /data:/app/data`）
- `--restart=always`: 容器退出时自动重启
- `-e <变量名>=<值>`: 设置环境变量（例: `-e MYSQL_ROOT_PASSWORD=123`）
- `-rm`：当容器停止运行（无论正常退出还是异常终止）时，**自动删除该容器**。避免手动执行 `docker rm` 清理临时容器。**不可与 `--restart` 同时使用**

**restart 支持的策略**

| 参数值                   | 说明                                                         |
| :----------------------- | :----------------------------------------------------------- |
| `no`                     | 默认值，容器退出后不自动重启。                               |
| `on-failure[:max-retry]` | 容器**异常退出时重启**（退出码非0），可选最大重试次数（如 `on-failure:3`）。 |
| `always`                 | 无论容器因何退出（包括手动停止），都会无限次尝试重启。       |
| `unless-stopped`         | 容器退出时自动重启，但**如果容器被手动停止，则需手动启动**。 |

**示例**：

```bash
docker run -d --name my-nginx -p 80:80 nginx
docker run -it --rm ubuntu:20.04 /bin/bash  # 退出后自动删除容器
```

#### 2. 查看容器

```bash
docker ps          # 查看运行中的容器
docker ps -a       # 查看所有容器（包括已停止的）
docker stats       # 实时查看容器资源占用（CPU/内存）
docker top <容器名> # 查看容器内进程
```

#### 3. 操作容器

```bash
docker start <容器名>      # 启动已停止的容器
docker stop <容器名>       # 停止运行中的容器
docker restart <容器名>    # 重启容器
docker rm <容器名>         # 删除容器（需先停止）
docker rm -f <容器名>      # 强制删除运行中的容器
docker container prune    # 删除所有已停止的容器
```

#### 4. 进入容器

```bash
docker exec -it <容器名> <命令>  # 例: docker exec -it my-nginx /bin/bash
```

#### 5. 日志与信息

```bash
docker logs <容器名>        # 查看容器日志
docker logs -f <容器名>     # 实时追踪日志（类似 tail -f）
docker inspect <容器名>     # 查看容器详细信息（IP、挂载等）
```

### 数据卷（Volume）管理

#### 1. 创建/查看数据卷

```bash
docker volume create <卷名>   # 创建数据卷
docker volume ls             # 列出所有数据卷
docker volume inspect <卷名> # 查看卷详细信息
```

#### 2. 挂载数据卷

```bash
docker run -v <卷名>:<容器目录> ...   # 挂载命名卷
docker run -v <主机目录>:<容器目录> ... # 挂载主机目录（Bind Mount）
```

#### 3. 清理数据卷

```bash
docker volume rm <卷名>       # 删除指定卷
docker volume prune          # 删除未被使用的卷
```

### 网络管理

#### 1. 查看网络

```bash
docker network ls          # 列出所有网络
docker network inspect <网络名> # 查看网络详情（如连接的容器）
```

#### 2. 创建/连接网络

```bash
docker network create <网络名>          # 创建自定义网络
docker run --network=<网络名> ...       # 将容器连接到指定网络
```

#### 3. 端口映射检查

```bash
docker port <容器名>       # 查看容器的端口映射关系
```

### Docker Compose 常用命令

#### 1. 启动服务

```bash
docker-compose up -d      # 后台启动所有服务
docker-compose up -d <服务名> # 启动指定服务
```

#### 2. 停止服务

```bash
docker-compose down       # 停止并删除所有容器、网络
docker-compose stop       # 仅停止容器
```

#### 3. 其他操作

```bash
docker-compose logs -f    # 查看所有服务的实时日志
docker-compose ps         # 查看服务状态
docker-compose build      # 重新构建镜像
docker-compose exec <服务名> <命令> # 进入指定服务的容器
```

### 六、实用技巧

#### 1. 清理资源

```bash
docker system prune -a    # 清理所有未使用的镜像、容器、网络、缓存
```

#### 2. 查看容器 IP

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <容器名>
```

#### 3. 复制文件

```bash
docker cp <容器名>:<容器路径> <主机路径>   # 从容器复制到主机
docker cp <主机路径> <容器名>:<容器路径>   # 从主机复制到容器
```

## 数据持久化机制

在 Docker 中，**Bind Mount** 和 **Volume** 是两种数据持久化机制，用于在容器和宿主机之间共享或保存数据。它们的核心区别在于**数据管理方式、生命周期控制**和**使用场景**。

### 核心区别

| **特性**         | **Bind Mount**                                               | **Volume**                                              |
| :--------------- | :----------------------------------------------------------- | :------------------------------------------------------ |
| **数据存储位置** | 直接挂载**宿主机指定目录或文件**到容器。                     | 由 Docker 管理，存储在 `/var/lib/docker/volumes/` 下。  |
| **创建方式**     | 需手动指定宿主机路径（如 `-v /host/path:/container/path`）。 | 通过 `docker volume create` 或自动创建。                |
| **生命周期**     | 与宿主机文件/目录共存亡，手动删除。                          | 独立于容器，需通过 `docker volume rm` 删除。            |
| **数据共享**     | 适合与宿主机共享配置文件或代码（如开发环境）。               | 适合容器间共享数据（如数据库文件）。                    |
| **权限控制**     | 继承宿主机文件权限，可能导致容器内权限问题。                 | Docker 自动管理权限，更安全。                           |
| **备份与迁移**   | 需手动操作宿主机文件。                                       | 通过 `docker volume` 命令或工具（如 `docker cp`）管理。 |
| **性能**         | 直接访问宿主机文件系统，性能较高。                           | 与 Bind Mount 类似，但可能受 Docker 管理开销影响。      |
| **适用场景**     | 开发调试、实时修改代码/配置。                                | 生产环境、持久化数据（如数据库、日志）。                |

### 使用示例

#### Bind Mount

```bash
# 挂载宿主机目录到容器（开发时实时同步代码）
docker run -d -v /path/on/host:/app/src my-app-image

# 挂载单个配置文件（如 Nginx 配置）
docker run -v /host/nginx.conf:/etc/nginx/nginx.conf nginx
```

#### **Volume**

```bash
# 创建命名卷
docker volume create my-data

# 挂载卷到容器
docker run -d -v my-data:/var/lib/mysql mysql:8.0

# 查看卷信息
docker volume inspect my-data
```

------

### 关键细节

#### **Bind Mount 的注意事项**

- **路径必须存在**：若宿主机路径不存在，Docker 会默认创建为目录（可能导致意外行为）。
- **权限问题**：容器进程可能因宿主机文件权限不足而无法访问（如 SELinux 限制）。
- **覆盖容器内文件**：如果宿主机目录为空，容器内目标目录会被覆盖为空。

#### **Volume 的优势**

- **隔离性**：数据由 Docker 管理，与宿主机其他进程解耦。
- **跨容器共享**：多个容器可挂载同一 Volume（如 Web 服务共享静态资源）。
- **备份方便**：支持导出卷数据（如 `docker run --rm -v my-data:/backup busybox tar cvf /backup/backup.tar /data`）。

### 进阶操作

#### **Volume 驱动**

Volume 支持多种存储驱动（如 `local`、`nfs`、`aws`），适合复杂场景：

```bash
# 使用 NFS 驱动创建卷
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/on/nfs \
  nfs-volume
```

#### 只读挂载

无论是 Bind Mount 还是 Volume，均可设置为只读：

```bash
docker run -v /host/config:/app/config:ro my-app
docker run -v my-volume:/data:ro my-app
```

## Docker 架构

Docker 采用 **Client-Server 架构**，核心组件包括：

1. Docker Client（客户端）
2. Docker Daemon（守护进程）
3. Docker Registry（镜像仓库）
4. Docker Objects（Docker 对象）：镜像、容器、网络、卷

### 组成部分

<img src="http://public.file.lvshuhuai.cn/images\ca299fb390d5cfc941d74a01650c5183.jpg" alt="img" style="zoom:50%;" />

#### Docker客户端（CLI）

- **作用**：Docker 客户端是用户与 Docker 交互的接口，用户通过 CLI 命令与 Docker Daemon 进行通信。它通过 Docker API 向 Docker Daemon 发送请求，来管理容器、镜像等资源。
- **工作方式**：你在终端中执行命令（如 `docker run`、`docker build` 等），Docker客户端会将这些命令转化为 API 请求，并通过网络与 Docker Daemon 通信。

#### Docker Daemon（Docker守护进程）

- **作用**：Docker Daemon 是 Docker 的核心进程，负责处理所有的容器管理、镜像管理、网络管理等任务。它持续运行，并监听来自客户端的请求（通常通过REST API）。Daemon 会解析这些请求并执行相应的操作，如创建、启动、停止容器，构建镜像等。
- **工作方式**：Daemon 是一个后台服务，通常作为操作系统的服务运行。它与操作系统内核（特别是 Linux 的命名空间、Cgroup 等）交互，来管理容器的资源。

**Docker Daemon的功能包括**：

- 监听和处理来自Docker客户端的命令请求。
- 管理容器的生命周期（启动、停止、删除容器等）。
- 管理和构建Docker镜像。
- 配置容器的网络和存储卷。

#### Docker镜像（Docker Images）

- **作用**：Docker镜像是容器的构建块，是只读的模板，包含了一个应用程序及其运行时所需的所有依赖、配置和文件。镜像由多个层（Layer）组成，每一层都表示对文件系统的某些更改。镜像作为容器的基础，一旦容器启动，它将使用该镜像的内容。

**镜像的特点**：

- **只读性**：镜像的内容是只读的，容器运行时对其进行修改时，会在镜像上创建一个可写层。
- **层级结构**：镜像是由多个层组成的，每个层代表镜像的一个增量变化。镜像层的共享是Docker节省存储空间的一个关键机制。多个镜像可以共享相同的基础层。

#### Docker容器（Docker Containers）

- **作用**：容器是镜像的运行实例。容器基于镜像创建，在容器启动时，它会拥有镜像中定义的环境和文件系统，但容器的文件系统是可写的。容器本质上是一个独立的进程，它在隔离的环境中运行，拥有自己的进程空间、网络接口、文件系统等。

**容器的特点**：

- **可写性**：容器可以在运行时修改文件系统，这与镜像的只读特性不同。
- **轻量性**：容器共享宿主机的操作系统内核，不需要额外的操作系统，因此启动速度快，资源消耗低。

**容器与镜像的关系**：

- 容器是镜像的运行实例，当你运行一个容器时，Docker Daemon会创建一个容器实例并为其分配一个进程空间、网络和存储。

#### Docker注册中心（Docker Hub / Docker Registry）

- **作用**：Docker Hub 是一个公开的 Docker 镜像仓库，用于存储和共享 Docker 镜像。用户可以从 Docker Hub 中拉取镜像，也可以上传自己的镜像以供他人使用。Docker Registry 则是一个 Docker 镜像的存储库，可以是公开的（如Docker Hub）或私有的。
- **功能**：
    - **镜像拉取与推送**：你可以从 Docker Hub 拉取镜像，也可以将本地的镜像推送到 Docker Hub 或者私有的 Docker Registry。
    - **镜像共享**：通过 Docker Hub，开发者可以分享自己构建的镜像，方便其他人使用和测试。

你可以使用 `docker pull` 命令从 Registry 拉取镜像，也可以使用 `docker push` 将本地镜像推送到 Registry。

#### Docker网络（Docker Networking）

- **作用**：Docker 提供了不同的网络模式，允许容器之间和外部进行通信。容器通过网络来进行交互和访问外部资源。

**常见的Docker网络模式**：

- **bridge（默认）**：容器连接到一个虚拟网桥（bridge），通过网桥与其他容器和宿主机通信。
- **host**：容器直接使用宿主机的网络接口，容器不进行任何网络隔离。
- **overlay**：用于跨多个 Docker 主机（尤其是 Docker Swarm 集群）创建容器间的网络通信。
- **none**：容器没有网络连接。

通过这些网络模式，Docker 提供了灵活的方式来配置容器的网络。

#### Docker存储（Docker Volumes）

- **作用**：Docker 容器的文件系统是临时的，一旦容器停止或删除，容器中的数据就会丢失。为了持久化容器数据，Docker 引入了数据卷（Volumes）。

**数据卷（Volumes）**：

- **持久性存储**：数据卷是独立于容器生命周期的存储，容器可以挂载数据卷以持久化其数据。
- **共享数据**：不同的容器可以挂载同一个数据卷，方便容器之间共享数据。
- **性能优化**：相较于容器内部的文件系统，数据卷通常具有更好的性能。

### Docker架构的工作流程

- 用户通过 **Docker客户端**发送命令（如 `docker run`），Docker 客户端通过 API 向 **Docker Daemon** 发送请求。
- Docker Daemon 根据请求来管理容器、镜像、网络、数据卷等资源。Daemon 可以创建、启动或停止容器，并管理容器的生命周期。
- Docker 容器运行时基于**镜像**，每个容器都是镜像的一个实例，运行时可修改。
- 镜像可以从 **Docker Hub**（或其他私有 Registry）中拉取，并且可以上传（推送）到 Registry 中。

## 原理

### 容器化技术的实现

Docker 的核心技术基于 Linux 的 **Namespace**、**Cgroup**、**UFS** 特性

### 命名空间（Namespace）

**命名空间**是 Linux 内核提供的一种机制，用来实现不同进程之间的隔离。通过命名空间，Linux 内核将不同的资源分配给不同的进程组，确保每个进程在其独立的空间中运行，无法访问到其他进程的资源。Docker 利用命名空间来隔离容器之间的资源，使得每个容器看起来像是在独立的机器上运行。

<img src="http://public.file.lvshuhuai.cn/images\4d1dc984442bc98f0a85a3d3c873cdfa.png" alt="img" style="zoom:50%;" />

#### 命名空间的种类

Docker 使用了 Linux 中的多种命名空间类型来隔离容器中的资源。常见的命名空间类型包括：

1. **PID 命名空间（pid namespace）**：
    - 用于隔离进程 ID（PID）。在不同的 PID 命名空间中，进程 ID 是独立的。容器内部运行的进程只有容器内的 PID 可见，不会与宿主机的进程 ID 冲突。
    - 容器中的进程被赋予一个独立的 PID，容器内的 PID 1 就是容器的主进程，而不是宿主机的 PID 1。
2. **网络命名空间（net namespace）**：
    - 用于隔离网络资源，包括网络接口（如 eth0）、IP 地址、路由、端口等。在不同的网络命名空间中，容器会有自己独立的网络环境。
    - 每个容器都有自己的网络接口和 IP 地址，容器与外部世界和其他容器之间的通信需要通过虚拟网络（如 bridge 网络模式）来实现。
3. **挂载命名空间（mnt namespace）**：
    - 用于隔离文件系统的挂载点。不同的容器可以拥有自己的文件系统结构，容器之间对文件系统的访问是隔离的。
    - 每个容器会挂载自己独立的文件系统视图，并且容器内的文件系统与宿主机的文件系统隔离。
4. **UTS 命名空间（uts namespace）**：
    - 用于隔离主机名和域名。容器可以拥有自己的主机名，而不受宿主机主机名的影响。
    - 容器内的主机名是容器的独立属性，容器内的应用程序只知道自己是一个独立的系统。
5. **IPC 命名空间（ipc namespace）**：
    - 用于隔离进程间通信（IPC）的资源，包括信号量、共享内存和消息队列。
    - 容器内部的进程只能看到容器内的 IPC 资源，无法访问宿主机或其他容器的 IPC 资源。
6. **用户命名空间（user namespace）**：
    - 用于隔离用户和用户组 ID（UID/GID）。容器内的用户和宿主机的用户 ID 是隔离的，容器内的 root 用户可能在宿主机上是一个普通用户。
    - 这种隔离可以增加安全性，防止容器内的 root 用户对宿主机产生权限影响。

通过这些命名空间，Docker 实现了容器之间的高度隔离。每个容器拥有独立的 PID、网络、挂载点等，容器内的进程和资源对外界不可见，增强了容器的安全性和资源独立性。

#### 创建命名空间

与 Docker 无关，在 Linux 中，可以使用 `unshare` 命令创建命名空间。

### 控制组（Cgroup）

**控制组（Cgroup，Control Groups）**是 Linux 内核的一个特性，用来限制、监控和管理进程（或容器）使用的资源（如 CPU、内存、磁盘 I/O 等）。Cgroup 通过为容器分配资源配额，确保容器不会过度使用宿主机的资源，避免资源争用导致系统崩溃或性能下降。

#### Cgroup的功能

1. **资源限制**：Cgroup 允许用户设置资源配额，限制容器可使用的资源。例如，可以限制容器使用的 CPU 时间、内存大小或磁盘 I/O 带宽。
    - **CPU 限制**：限制容器占用的 CPU 资源。例如，可以设置容器最多只能使用宿主机上 50% 的 CPU 时间。
    - **内存限制**：可以限制容器使用的内存量，如果容器超过该限制，它将会被终止或出现 OOM（Out of Memory）错误。
    - **磁盘 I/O 限制**：限制容器使用磁盘的 I/O 带宽，避免单个容器占用过多的磁盘带宽，影响其他容器的性能。
2. **资源监控**：Cgroup 可以监控容器的资源使用情况，并提供相应的统计信息。例如，容器可以实时监控其 CPU 使用情况、内存使用情况等。
3. **资源优先级管理**：Cgroup 可以根据优先级来调度资源，给不同的容器分配不同的资源优先级。例如，某些重要的容器可以获得更多的 CPU 时间或内存资源，而其他不太重要的容器则可以限制资源使用。
4. **资源隔离**：Cgroup 通过将资源限制应用到容器上，防止容器之间资源相互干扰，确保每个容器只能使用其分配的资源量。

#### Cgroup与Docker的关系

Docker通过Cgroup来限制和控制容器的资源使用。例如，Docker 允许用户在运行容器时指定 CPU、内存等资源限制：

`docker run --memory=512m --cpus=2` 限制容器使用的内存为 512MB，最多使用 2 个 CPU。

Cgroup 确保容器的资源使用在预设的限制范围内，避免容器之间相互影响，提高系统的稳定性和资源利用率。

### 联合文件系统（UFS）

**联合文件系统（Union File System，UFS）**是 Docker 实现镜像和容器的关键技术。它允许多个文件系统层进行合并，表现为一个统一的文件系统，从而节省存储空间并提高性能。Docker 的镜像就是由多个层（Layer）组成的，每个层都代表了镜像的一个增量操作。通过联合文件系统，这些层可以高效地共享和复用。

<img src="http://public.file.lvshuhuai.cn/images\44c0081e896da8a6b54eb023e52f33c4.png" alt="img" style="zoom:50%;" />

#### UFS的工作原理

1. **文件系统层叠（Layered File System）**
    - Docker 镜像是由多个只读的层（Layer）组成的，每一层代表了镜像中的一个增量更改。例如，第一层可能是操作系统的基础镜像，第二层可能是安装某个软件包，第三层可能是应用程序代码等。
    - 每一层都是只读的，Docker 在运行容器时会将这些层按顺序叠加，形成一个完整的文件系统视图。
2. **可写层（Writable Layer）**
    - 容器运行时会为每个容器创建一个可写层（Container Layer）。当容器运行时，它会对文件系统进行修改（如创建文件、修改文件、删除文件等），这些更改会被写入容器的可写层，而不会影响镜像中的只读层。
3. **层的共享**
    - 不同的容器可以共享相同的镜像层。例如，如果多个容器使用相同的基础镜像（如Ubuntu或Alpine），这些容器就会共享相同的只读层，节省存储空间。
4. **文件系统驱动（Storage Drivers）**
    - Docker 支持多种联合文件系统驱动（如 **aufs**、**overlay2**、**btrfs** 等）。这些驱动决定了如何实现镜像层的管理和合并。不同的驱动有不同的性能和特点。
    - 例如，`overlay2` 是目前最常用的驱动，它支持较低的存储开销和较高的性能。

#### UFS在Docker中的应用

通过联合文件系统，Docker能够高效地管理镜像层，减少重复的存储和网络传输。例如，当拉取一个镜像时，Docker 只需要下载那些没有本地缓存的层，这样可以加速镜像的传输和存储。

Docker 容器在启动时，只有只读层和一个可写层，因此容器的启动速度非常快，且占用的磁盘空间非常小。
