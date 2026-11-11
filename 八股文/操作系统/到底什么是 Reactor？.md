# 到底什么是 Reactor？

## 回答重点

Reactor 是一种处理并发 I/O 事件的设计模式，适合网络服务器。核心思想是**将 I/O 事件与处理程序解耦**，由事件分发器监听大量连接，有事件发生时找到对应 Handler 执行。

Reactor 的主要特点：

1. **事件驱动**：监听多个事件源，有事件时调用对应 Handler。
2. **非阻塞 I/O**：少量线程处理大量 I/O，避免一个连接占用一个阻塞线程。
3. **事件分发**：根据连接、读、写等事件类型分派不同处理逻辑。

![Reactor 模式](Z:/Public/images/prDb6hMl_image_mianshiya.webp)

## 扩展知识

### 用生活例子理解 Reactor

可以把网络连接想象成很多按钮：一种方式是每个按钮派一个线程守着；另一种方式是一个线程轮询所有按钮，哪个被点击就执行对应处理逻辑。第二种就是 Reactor：一个线程接待多个连接，根据连接事件调用不同 Handler。

网络 I/O 中常见事件有连接、读和写。Reactor 通过非阻塞 I/O 和多路复用，让少量线程处理大量连接。

### Reactor 的基本组件

- **Reactor 线程**：运行事件循环，等待 I/O 多路复用器返回就绪事件。
- **Demultiplexer**：如 `select`、`poll`、`epoll`，负责监听多个文件描述符。
- **Dispatcher**：根据事件类型和连接找到对应处理器。
- **Handler**：执行读写和业务处理。
- **Acceptor**：接收新连接并将其注册到 Reactor。

![Reactor 组件](Z:/Public/images/neBGId8B_jjFV9iAXNZ_mianshiya.webp)

### Reactor 与 Proactor

- **Reactor** 是同步非阻塞模型：事件就绪后通知应用，应用自己执行读写。
- **Proactor** 是异步非阻塞模型：应用提交异步 I/O，操作系统完成读写后再通知应用。

简单来说，Reactor 是“通知你数据来了，你自己去读”；Proactor 是“数据我已经读好了，直接给你用”。Windows IOCP 是 Proactor 的典型实现。

### 单 Reactor 与多 Reactor

- **单 Reactor 单线程**：事件监听、分发和处理都在一个线程，简单但容易成为瓶颈，Redis 早期采用此模型。
- **单 Reactor 多线程**：主线程监听和分发，工作线程池执行处理逻辑，适合中等并发。
- **多 Reactor 多线程**：多个 Reactor 分担连接，多个 Worker 处理事件，适合大规模并发。Netty 默认采用主从 Reactor 模型，Boss Group 接收连接，Worker Group 处理读写。

### 实际应用

- **Nginx**：使用 epoll、事件驱动和非阻塞 I/O 处理高并发连接。
- **Netty**：通过 EventLoop 和 Channel 实现 Reactor，EventLoopGroup 负责事件监听与分发。
- **Node.js**：通过事件循环和非阻塞 I/O，以少量线程处理大量连接。

## 面试官追问

#### 提问：Netty 的 EventLoop 和 Reactor 是什么关系？

回答：EventLoop 是 Reactor 线程的具体实现，一个 EventLoop 绑定一个线程，负责监听注册到其上的所有 Channel 的 I/O 事件。EventLoopGroup 是一组 EventLoop；Boss Group 接收连接，Worker Group 处理读写，构成多 Reactor 多线程模型。

#### 提问：为什么 Redis 选择单 Reactor 单线程？

回答：Redis 主要是内存读写，瓶颈更多在网络 I/O 和内存带宽。单线程没有锁竞争和上下文切换，代码简单且性能足够。Redis 6 之后增加了多线程 I/O，但命令执行仍保持单线程。

#### 提问：Reactor 模式如何处理耗时业务？

回答：Reactor 线程只做 I/O 监听和分发，耗时业务要提交到独立业务线程池。若在 Reactor 线程执行耗时逻辑，会阻塞事件循环，拖慢所有连接。Netty 可给 Handler 配置独立的 EventExecutorGroup。

#### 提问：主从 Reactor 模型中 Boss 线程应该配置几个？

回答：大多数场景一个就够，接收连接本身很轻量，Netty 默认 Boss Group 只有一个线程。多端口监听或连接建立包含复杂握手逻辑时才考虑多个 Boss，调优重点通常是 Worker 线程数。
