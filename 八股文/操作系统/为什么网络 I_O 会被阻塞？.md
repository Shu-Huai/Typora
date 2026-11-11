# 为什么网络 I/O 会被阻塞？

## 回答重点

网络 I/O 阻塞的本质是等待：等待数据到达、发送缓冲区有空间或连接建立完成。网络通信跨越物理链路，延迟可能达到毫秒甚至秒级，操作系统会挂起进程，条件满足后再唤醒。

- **读阻塞**：`recv` / `read` 时 socket 接收缓冲区为空，等待对端发送数据。
- **写阻塞**：`send` / `write` 时 socket 发送缓冲区已满，等待对端确认并腾出空间。
- **连接阻塞**：客户端 `connect` 等待 TCP 三次握手，服务端 `accept` 等待已完成连接队列中有连接。

![网络 I/O 阻塞](Z:/Public/images/UauXNNI5_image_mianshiya.webp)

## 扩展知识

### 网络 I/O 的常见阻塞场景

- `accept()`：没有新的客户端连接时阻塞。
- `connect()`：连接不能立即建立时阻塞，直到成功或超时。
- `recv()` / `read()`：接收缓冲区无数据时阻塞。
- `send()` / `write()`：发送缓冲区满时阻塞。

### Socket 服务端流程

1. `socket()` 创建套接字并得到文件描述符。
2. `bind()` 将套接字绑定到 IP 和端口。
3. `listen()` 进入被动监听状态，设置 backlog。
4. `accept()` 从已完成连接队列取出连接；队列为空时阻塞。

TCP 连接建立过程中，半连接表示收到 SYN 但三次握手尚未完成，已完成连接表示握手完成、等待服务端 `accept()` 取走。Linux 通常分别维护半连接队列和已完成连接队列，`backlog` 主要对应已完成连接队列大小。

![TCP 连接队列](Z:/Public/images/anpqmYuy_image_mianshiya.webp)

### Socket 客户端流程

客户端调用 `socket()` 后执行 `connect()`，连接进入 `SYN_SENT`，收到服务端 `SYN+ACK` 并完成握手后进入 `ESTABLISHED`。客户端通常不需要显式 `bind()`，系统会自动选择源 IP 和临时端口。

![客户端连接](Z:/Public/images/K9GEKS1K_image_mianshiya.webp)

### read 与 write 为什么都会阻塞

`read` 没数据时阻塞很好理解；`write` 也可能阻塞，是因为 TCP 要保证可靠、有序传输并执行流量控制。应用数据先写入 TCP 发送缓冲区，由协议栈负责发送和重传。发送过快会填满缓冲区，继续 `write` 时进程就会等待空间释放。

### 非阻塞 I/O 与多路复用

将 socket 设置为非阻塞模式后，条件不满足时不会睡眠，而是立即返回 `EAGAIN` 或 `EWOULDBLOCK`：

```c
int flags = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, flags | O_NONBLOCK);
```

非阻塞模式配合 `select`、`poll`、`epoll` 等 I/O 多路复用，一个线程即可监控大量 socket，哪个连接就绪就处理哪个。Nginx 和 Redis 的高并发能力就依赖这类事件机制。

![网络 I/O 多路复用](Z:/Public/images/6zuQ5zZu_Bl8Ih9vhAG_mianshiya.webp)

## 面试官追问

#### 提问：TCP 发送缓冲区满后，写入操作具体如何阻塞？

回答：`write` 进入内核后发现缓冲区空间不足，内核会把进程放入 socket 等待队列并调度其他任务。收到对端 ACK、缓冲区释放空间后，内核唤醒等待进程，`write` 继续执行。非阻塞模式下不会睡眠，而是直接返回 `EAGAIN`。

#### 提问：半连接队列和已完成连接队列满了分别有什么后果？

回答：半连接队列满时，新 SYN 可能被丢弃，客户端会超时重传，容易被 SYN Flood 利用；已完成连接队列满时，完成握手的连接无处存放，服务端可能丢弃 ACK，客户端后续收到 RST 并重连。可以关注 `netstat -s` 中的溢出统计。

#### 提问：为什么 epoll 比 select 效率高？

回答：select 每次都要在用户态和内核态之间拷贝全部 fd，并遍历检查就绪状态，还有 fd 数量限制；epoll 在内核中维护 fd 集合，就绪 fd 通过回调放入链表，`epoll_wait` 只处理就绪项，避免遍历全部连接。

#### 提问：connect 超时怎么处理？

回答：将 socket 设为非阻塞，`connect` 立即返回 `EINPROGRESS`，再用 select 或 epoll 监控可写事件，并设置几秒级超时；超时后主动关闭连接。也可以尝试使用 `SO_SNDTIMEO`，但不同系统支持情况不同。
