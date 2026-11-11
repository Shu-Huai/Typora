# Redis 主从复制的实现原理是什么？

## 回答重点

Redis 主从复制就是让从节点复制主节点的数据，既能实现读写分离、分摊主节点压力，也能提供数据备份。

整个过程可分为三个阶段：

1. **建立连接与全量同步**：从节点首次连接主节点后发送 `PSYNC`，主节点生成 RDB 快照并发送给从节点。从节点清空旧数据并加载快照；快照生成期间主节点收到的新写命令会暂存到 `replication buffer`，快照加载完成后再发送给从节点。
2. **命令传播**：全量同步完成后，主从保持长连接，主节点收到写命令后异步发送给从节点执行，并通过 Ping/Ack 心跳确认连接状态。
3. **断线重连与增量同步**：从节点短暂断线重连时，主节点根据复制偏移量从 `repl_backlog_buffer` 中补发缺失命令，避免重新进行全量同步。

![主从复制流程](Z:/Public/images/X9Ax9GXb_image_mianshiya.webp)

## 扩展知识

### Redis 主从架构

主节点负责写入，从节点通过复制同步数据并提供读服务。将读请求分散到多个从节点可以提高吞吐量，但从节点读取到的可能是稍旧的数据。

![Redis 主从架构](Z:/Public/images/Ry6PqUac_image_mianshiya.webp)

### 全量同步

首次同步时，从节点发送 `PSYNC ? -1`：

1. 主节点发现 runid 不存在，返回 `FULLRESYNC`，同时返回主节点 runid 和当前复制偏移量。
2. 主节点执行 `BGSAVE` 生成 RDB，期间的新写命令保存到 `replication buffer`。
3. 主节点将 RDB 发送给从节点，从节点清空旧数据并加载快照。
4. RDB 加载完成后，主节点发送 replication buffer 中的增量命令。
5. 后续通过长连接持续传播新的写命令。

![全量同步](Z:/Public/images/zQyotf09_image_mianshiya.webp)

### 增量同步

Redis 2.8 引入 `PSYNC` 和部分重同步能力。主节点维护一个默认约 1 MB 的环形 `repl_backlog_buffer`，写命令超过容量后会覆盖旧数据。

从节点重连时上报自己的 runid 和 offset。若 runid 一致且 offset 之后的数据仍在 backlog 中，主节点只发送缺失命令；若数据已经被覆盖，只能重新执行全量同步。

![增量同步](Z:/Public/images/9GIJIcHv_image_mianshiya.webp)

可以适当调大 backlog，降低全量同步概率：

```bash
repl-backlog-size 100mb
```

### 两个缓冲区的区别

- **`replication buffer`**：为在线从节点保存待发送命令，每个从节点一个；大小受 `client-output-buffer-limit` 控制。
- **`repl_backlog_buffer`**：为断线重连的从节点保存历史写命令，所有从节点共用一个环形缓冲区，写满后覆盖最早数据。

```bash
client-output-buffer-limit slave 256mb 64mb 60
repl-backlog-size 100mb
```

如果从节点输出缓冲区超过 256 MB，或超过 64 MB 持续 60 秒，主节点会断开连接，重连后可能触发全量同步。backlog 大小应根据写入速率和可接受的断线时长估算：每秒写入 1 MB、希望支持 100 秒断线，可设置约 100 MB。

### 全量同步的性能开销

全量同步会：

1. fork 子进程生成 RDB，数据量大时短暂阻塞主线程。
2. 通过网络传输整个 RDB 文件。
3. 让从节点在加载 RDB 期间无法正常提供服务。
4. 加载完成后重放 replication buffer 中的命令。

生产环境应调大 `repl_backlog_buffer`，并控制单个实例的数据量，通常建议不超过 10 GB。

### 主从复制是异步的

主节点执行写命令后通常立即向客户端返回成功，不等待从节点同步，因此性能高但可能丢失刚写入的数据。Redis 3.0 提供 `WAIT`，客户端可等待指定数量从节点确认：

```bash
SET key value
WAIT 1 1000
```

`WAIT` 只是客户端等待行为，Redis 的底层复制机制仍然是异步的。

## 面试官追问

### 提问：从节点能不能再挂从节点？

可以形成级联复制。主节点只需连接少数一级从节点，一级从节点再向下游传播，从而减少主节点维护的复制连接和缓冲区数量。缺点是复制链路越长，底层从节点延迟越高。

### 提问：复制期间从节点还能提供读服务吗？

默认可以，但可能读到旧数据。若配置 `slave-serve-stale-data no`，从节点同步未完成前会拒绝读请求，但会降低可用性。

### 提问：主节点挂了从节点会自动升级吗？

不会。单纯主从复制没有自动故障转移能力，需要使用哨兵或 Redis Cluster 监控并完成主从切换。

### 提问：所有从节点共用一个 backlog，如何知道各自同步到哪里？

每个从节点维护自己的复制偏移量 offset，主节点也维护当前 offset。从节点重连时上报自己的 offset，主节点根据 backlog 中的 offset 范围判断能否增量补发；找不到对应数据时才执行全量同步。
