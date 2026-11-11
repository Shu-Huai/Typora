# Select、Poll、Epoll 之间有什么区别？

## 回答重点

`select`、`poll` 和 `epoll` 都是 I/O 多路复用机制，让一个线程同时监控多个文件描述符。

1. **select**：用固定长度位图表示 fd 集合。每次调用都要把位图从用户态拷贝到内核，内核线性扫描全部 fd，通常有 1024 个 fd 的限制。
2. **`poll`**：用动态 `pollfd` 数组，突破固定数量限制，但每次仍要拷贝整个数组并线性遍历所有 fd。
3. **epoll**：Linux 专用优化机制，用红黑树管理注册 fd，用就绪链表保存触发事件。fd 注册一次，`epoll_wait` 只返回就绪 fd，支持 LT/ET，适合高并发。

![select poll epoll](Z:/Public/images/VE09udN6_UnL1AK5z9E_mianshiya.webp)

| 特性 | select | `poll` | epoll |
| --- | --- | --- | --- |
| 数据结构 | 位图 | 动态数组 | 红黑树 + 就绪链表 |
| fd 数量 | 通常 1024 | 无固定限制 | 无固定限制 |
| fd 传递 | 每次调用都拷贝 | 每次调用都拷贝 | 注册时拷贝一次 |
| 检测方式 | 线性扫描 | 线性扫描 | 事件回调，仅处理就绪项 |
| 复杂度 | $O(n)$ | $O(n)$ | 等待就绪项近似 $O(1)$ |

## 扩展知识

### select

`select` 使用 `fd_set` 位图分别表示可读、可写和异常事件。调用时重新构建集合并传给内核，内核扫描 `[0, nfds)` 的所有 fd，返回后应用再次遍历集合查找就绪描述符。固定 fd 数量和线性扫描使它不适合大规模并发。

```c
int select(int nfds, fd_set *readfds, fd_set *writefds,
           fd_set *exceptfds, struct timeval *timeout);
```

### `poll`

`poll` 使用 `pollfd` 结构体数组：

```c
struct pollfd {
    int fd;
    short events;
    short revents;
};
```

它没有 `select` 的固定数量限制，`events` 表示关注事件，`revents` 由内核返回实际发生的事件。但每次调用仍需拷贝和遍历整个数组。

### epoll

`epoll` 通过 `epoll_ctl` 注册、修改和删除 fd，通过红黑树管理注册关系；事件就绪时由回调将 fd 放入就绪链表。`epoll_wait` 只需读取就绪链表，避免扫描所有注册 fd。

- **LT（水平触发）**：只要 fd 仍有未处理数据，每次 `epoll_wait` 都会通知，默认模式，使用简单。
- **ET（边缘触发）**：只有状态变化时通知一次，必须配合非阻塞 I/O 循环读取到 `EAGAIN`，效率高但编程复杂。

### epoll 的基本流程

1. `epoll_create` 创建实例。
2. `epoll_ctl(EPOLL_CTL_ADD/MOD/DEL)` 管理 fd 和关注事件。
3. `epoll_wait` 等待就绪事件；就绪链表为空时线程可以阻塞到事件发生或超时。

## 面试官追问

#### 提问：10 万个连接中只有 100 个活跃，select 和 epoll 有什么差距？

回答：select 每次要扫描 10 万个 fd，epoll 只处理 100 个就绪 fd；select 还要每次拷贝 10 万个 fd 集合，epoll 注册后无需反复拷贝，因此连接多而活跃少时 epoll 优势明显。

#### 提问：epoll 的边缘触发为什么要配合非阻塞 I/O？

回答：ET 只通知一次，必须循环读取直到 `EAGAIN`。如果使用阻塞 I/O，读完数据后下一次 `read` 会阻塞，整个线程无法处理其他连接；非阻塞 I/O 会返回 `EAGAIN`，循环即可退出。

#### 提问：为什么 Redis 用单线程加 epoll 也能有高性能？

回答：Redis 命令主要是内存操作，单次执行很快；epoll 让一个线程高效管理大量连接，同时避免线程切换和锁竞争。Redis 6 之后增加了多线程网络 I/O，但命令执行仍主要保持单线程。

#### 提问：epoll 有哪些不适用场景？

回答：连接数少或短连接频繁创建销毁时，反复 `epoll_ctl` 的注册和删除开销可能抵消优势；epoll 还是 Linux 专有机制，跨平台程序需要适配其他系统。早期内核还存在惊群等问题，需要额外规避。
