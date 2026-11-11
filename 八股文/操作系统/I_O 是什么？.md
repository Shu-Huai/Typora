# I/O 是什么？

## 回答重点

**I/O**（Input/Output）就是数据在计算机与外部世界之间的搬运过程：Input 表示数据输入，Output 表示数据输出。

- **输入**：键盘输入、网卡收包、磁盘读文件等，设备通过 I/O 控制器把数据搬到内存，CPU 再读取处理。
- **输出**：CPU 将结果写入内存，I/O 控制器再把数据搬到显示器、网卡或磁盘。

I/O 设备主要分两类：

1. **块设备**：硬盘、SSD 等，按固定大小的块读写，通常支持随机访问。
2. **字符设备**：键盘、鼠标、串口等，以字节流顺序读写，通常不能随机访问。

## 扩展知识

### I/O 为什么是性能瓶颈

CPU、缓存、内存、SSD 和机械硬盘的速度差距很大：CPU 周期约 0.3 纳秒，L1 缓存约 1 纳秒，内存约 100 纳秒，SSD 随机读约 150 微秒，机械硬盘随机读约 10 毫秒。因此程序一旦等待磁盘或网络，CPU 就会空等。

![I/O 性能差异](Z:/Public/images/4eRwN2p6_WmoG4itbpB_mianshiya.webp)

缓存、预读、异步 I/O 和批量处理等技术，都是为了减少 CPU 等待 I/O 的时间。

### 同步 I/O 与异步 I/O

同步 I/O 调用后会阻塞，直到数据搬运完成：

```java
FileInputStream fis = new FileInputStream("data.txt");
byte[] buffer = new byte[1024];
int bytesRead = fis.read(buffer); // 阻塞直到读完
```

异步 I/O 发起请求后立即返回，完成后通过回调、事件或轮询通知：

```java
AsynchronousFileChannel channel = AsynchronousFileChannel.open(path);
ByteBuffer buffer = ByteBuffer.allocate(1024);
channel.read(buffer, 0, null, new CompletionHandler<Integer, Void>() {
    @Override
    public void completed(Integer result, Void attachment) {
        // 读取完成
    }
    @Override
    public void failed(Throwable exc, Void attachment) {
        // 错误处理
    }
});
```

高并发场景中异步事件机制可以让一个进程处理大量连接，避免每个连接都占用一个阻塞线程。

### 缓冲 I/O 与直接 I/O

普通文件读写经过内核 Page Cache：读时先查缓存，写时先写缓存，内核再批量刷盘。数据库通常有自己的缓存管理，因此会使用直接 I/O，绕过 Page Cache，避免同一数据在内存中保存两份。

```c
int fd = open("datafile", O_RDWR | O_DIRECT);
```

直接 I/O 通常要求内存地址、读写大小按块大小（512 字节或 4KB）对齐。

### I/O 调度器

多个进程并发访问磁盘时，I/O 调度器会重新排列请求，减少机械硬盘寻道时间并避免请求长期饥饿。历史上有 CFQ、Deadline、Noop 等调度器；现代多队列块设备常使用 `mq-deadline`、`bfq` 或 `none`。

```bash
# 查看当前调度器
cat /sys/block/sda/queue/scheduler

# 临时修改调度器
echo mq-deadline > /sys/block/sda/queue/scheduler
```

### I/O 模型演进

- **阻塞 I/O**：一个线程处理一个连接，连接多时线程和切换开销巨大。
- **select/`poll`**：一个线程监控多个文件描述符，但 select 有数量限制，`poll` 每次都要遍历和拷贝描述符集合。
- **epoll**：Linux 通过事件通知处理就绪描述符，不必每次遍历全部连接，Nginx、Redis 等高并发服务广泛使用。

## 面试官追问

#### 提问：用户态和内核态之间的数据拷贝如何优化？

回答：传统 I/O 通常有两次拷贝：设备到内核缓冲区、内核缓冲区到用户缓冲区。可以用 `mmap` 将文件映射到用户空间，用 `sendfile` 实现内核缓冲区到 socket 的零拷贝，也可以用 `splice` 在两个文件描述符之间直接搬运数据。

#### 提问：为什么数据库要用直接 I/O？

回答：数据库可以精确控制自己的缓存和刷盘时机，避免 Page Cache 与数据库缓存重复占用内存，也能降低断电丢数据风险。但直接 I/O 没有内核预读优势，顺序扫描大表时可能不如缓冲 I/O，因此应根据访问模式选择。

#### 提问：SSD 和机械硬盘的 I/O 特性有什么区别？

回答：机械硬盘有寻道和旋转延迟，随机 I/O 约为毫秒级，而顺序读写更快；SSD 没有机械部件，随机 I/O 通常是微秒级，随机和顺序性能差距较小。SSD 上不必过度关注寻道调度，但要关注写放大和磨损均衡。

#### 提问：epoll 的水平触发和边缘触发有什么区别？

回答：水平触发只要描述符仍可读写就会持续通知，代码简单；边缘触发只在状态变化时通知一次，必须一次性读完数据，否则可能不再通知。Nginx 常用边缘触发，普通业务程序常用水平触发以降低出错风险。
