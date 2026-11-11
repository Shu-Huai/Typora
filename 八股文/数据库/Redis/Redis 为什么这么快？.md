# Redis 为什么这么快？

## 回答重点

Redis 快的核心原因主要有三个：纯内存操作、单线程执行命令配合 I/O 多路复用，以及高效的数据结构设计。

1. **数据主要驻留内存**：内存访问约为纳秒级，SSD 通常为微秒级，机械硬盘更慢。Redis 把热数据放在内存中，除持久化外基本不与磁盘交互。
2. **单线程 + I/O 多路复用**：命令执行没有锁竞争和线程上下文切换；通过 epoll 等机制，一个线程可以同时监听大量连接，哪个连接就绪就处理哪个。
3. **数据结构经过优化**：例如 SDS 获取字符串长度为 $O(1)$，Hash 根据数据规模选择紧凑结构或哈希表，ZSet 使用跳表支持 $O(\log N)$ 的查询和更新。

![Redis 高性能原因](Z:/Public/images/fqZF6wHH_image_mianshiya.webp)

![Redis 单线程与 I/O 多路复用](Z:/Public/images/ORAKydva_image_mianshiya.webp)

![Redis 数据结构](Z:/Public/images/cV4cxcan_image_mianshiya.webp)

> 上图来自 [ByteByteGo](https://blog.bytebytego.com/p/why-is-redis-so-fast*)。

## 扩展知识

### 内存访问为什么这么快

CPU 访问内存通过总线把数据从 DRAM 读入 CPU 缓存，主要是电信号传输，延迟处于纳秒级。机械硬盘需要寻道和等待盘片旋转，SSD 也需要经过主控、闪存寻址以及 PCIe/SATA 协议处理，因此都比内存慢很多。Redis 利用这种速度差，将热数据放入内存，冷数据再通过持久化落盘。

![内存与磁盘访问速度](Z:/Public/images/M0AkDrxv_WU801n9KNe_mianshiya.webp)

### I/O 多路复用的原理

传统阻塞 I/O 通常一个线程对应一个连接，连接数增多后线程切换开销会明显增加。I/O 多路复用让一个线程同时监听多个文件描述符，Linux 下常用 epoll：

1. 将需要监听的 socket 注册到 epoll 实例。
2. 调用 `epoll_wait` 阻塞等待事件。
3. 有事件就绪时返回就绪 socket 列表。
4. 依次处理这些 socket 的读写。

Redis 在 Linux 下使用 epoll，在 macOS 下使用 kqueue，在 Windows 下使用 select；底层实现虽不同，但都是用事件驱动替代线程轮询。

相关知识：

- [说说你知道的几种 I/O 模型](https://www.mianshiya.com/question/1804476796656885762)
- [Select、Poll、Epoll 之间有什么区别？](https://www.mianshiya.com/question/1780933295857496065)

### 单线程为什么不是瓶颈

Redis 的瓶颈通常在网络带宽和内存带宽，而不是 CPU。一条简单 GET/SET 命令的 CPU 执行时间很短，网络往返往往才是主要耗时。

单线程的优势：

1. 没有锁竞争，代码更简单。
2. 没有线程上下文切换开销。
3. 数据结构不会被其他线程同时修改，CPU 缓存命中率较高。

单机单线程在简单命令场景下可以达到 10 万级 QPS，通常能够满足大多数业务需求。

### Redis 6.0 的多线程

Redis 6.0 引入多线程后，主要并行处理网络 I/O，命令执行仍由主线程串行完成：

```text
Redis 5.x：单线程读取网络数据 → 解析命令 → 执行命令 → 写响应
Redis 6.0：多线程读取网络数据 → 单线程执行命令 → 多线程写响应
```

在大量小包请求导致网络 I/O 成为瓶颈时，多线程可以提升吞吐量，同时保留命令执行的串行一致性。典型配置如下：

```bash
# redis.conf
io-threads 4
io-threads-do-reads yes
```

### 数据结构的精妙设计

- **SDS**：在 C 字符串基础上保存长度字段，获取长度为 $O(1)$，并且二进制安全。
- **ziplist**：连续紧凑的内存结构，节省空间，但查询为 $O(N)$，适合小数据量。
- **quicklist**：将多个 ziplist 通过双向链表连接，兼顾内存占用和访问性能。
- **skiplist**：ZSet 的底层结构之一，查询、插入和删除平均为 $O(\log N)$，范围查询方便。

### 性能边界与持久化影响

大 `key` 操作（例如删除几百 MB 的 Hash）和 CPU 密集型命令（如 `KEYS *`、复杂 Lua 脚本）会阻塞单线程，应使用 `SCAN` 替代 `KEYS`，使用 `UNLINK` 替代 `DEL`。

持久化也会影响性能：RDB 的 fork 在数据量大时可能耗时；AOF 使用 `always` 会等待每次刷盘。生产环境通常使用 `everysec`，在性能与数据安全之间折中。

## 面试官追问

### 提问：epoll 和 select 有什么区别？为什么 Redis 选 epoll？

`select` 存在文件描述符数量上限，并且每次调用都需要复制并遍历整个 fd 集合；`epoll` 用红黑树管理 fd，只返回就绪 fd 列表，连接数较多时效率更高。

### 提问：Redis 4.0 的 `UNLINK` 命令有什么作用？

`DEL` 删除大 `key` 时会阻塞主线程；`UNLINK` 先从 keyspace 中摘除 `key`，再由后台线程异步回收内存，因此能显著降低主线程阻塞。

### 提问：Redis 的持久化会影响性能吗？

会。RDB fork 和 AOF 刷盘都有额外开销。通常将 AOF 刷盘策略设置为 `everysec`，在可接受的数据丢失窗口内获得更好的吞吐量。
