# 什么是 Java 的 Semaphore？

## 回答重点

`Semaphore` 是 Java 并发包里的**计数信号量**，本质上维护了一个许可计数器，用来控制同时访问某个资源的线程数量。比如数据库连接池最多允许 10 个连接，就可以用 `new Semaphore(10)` 来限流。

线程调用 `acquire()` 时，如果许可数大于 0，计数器减 1，线程继续执行；如果许可数等于 0，线程就会阻塞等待。线程完成任务后调用 `release()`，计数器加 1，同时唤醒一个等待的线程。

![](Z:/Public/images/dn32m38j_cNFqvNSFEQ_mianshiya.webp)

底层实现依赖 AQS，许可数就是 AQS 的 state 值。`acquire()` 对应 AQS 的共享式获取，通过 CAS 操作扣减 state；`release()` 则是 CAS 增加 state 并唤醒等待队列中的线程。

```java
// 限制最多 5 个线程同时访问数据库
Semaphore semaphore = new Semaphore(5);

public void accessDatabase() throws InterruptedException {
    semaphore.acquire();  // 获取许可，许可不足则阻塞
    try {
        // 执行数据库操作
    } finally {
        semaphore.release();  // 释放许可
    }
}
```

## 扩展知识

### 公平与非公平策略

`Semaphore` 构造函数可以指定是否公平：`new Semaphore(5, true)` 表示公平模式。

公平模式下，等待时间最长的线程优先获得许可，底层用 FIFO 队列排队。好处是不会饿死任何线程，坏处是吞吐量下降，因为每次释放许可都要从队列头唤醒线程，多了一次上下文切换。

非公平模式下，新来的线程可以直接抢许可，如果刚好有许可就拿走，不用排队。吞吐量高，但可能有线程一直抢不到。生产环境大部分场景用默认的非公平模式就够了，除非对公平性有明确要求，比如任务必须按提交顺序执行。

![](Z:/Public/images/fARhr1OA_lQ93emJWwr_mianshiya.webp)

### 与 synchronized、Lock 的区别

synchronized 和 `ReentrantLock` 是互斥锁，同一时刻只有 1 个线程能进入临界区。`Semaphore` 的许可数可以大于 1，允许多个线程同时访问，适用场景完全不同。

典型用法对比：synchronized 保护共享变量的读写，保证原子性；`Semaphore` 控制连接池、线程池的并发度，做限流。

### 常见使用场景

1. 数据库连接池限流：Druid、HikariCP 内部都有类似机制，控制最大连接数

2. 接口限流：配合 Guava RateLimiter 或单独使用，限制 API 的并发请求数

3. 资源池控制：对象池、文件句柄池等，避免资源耗尽

### 常见坑点

1. `acquire()` 和 `release()` 必须成对出现，漏了 `release()` 会导致许可永久丢失，其他线程永远阻塞

2. `release()` 没有校验当前线程是否持有许可，调用多次会凭空增加许可数，破坏限流语义

3. `tryAcquire()` 返回 false 时别忘了处理，不能当没事发生直接往下走

## 面试官追问

#### 提问：`Semaphore` 能实现互斥锁的效果吗？怎么做？

回答：可以，把许可数设成 1 就行了，`new Semaphore(1)`。任何时刻只有一个线程能获取许可，效果等同于互斥锁。不过和 `ReentrantLock` 比，`Semaphore` 不支持重入，同一个线程连续调用两次 `acquire()` 会死锁。

#### 提问：如果我 `release` 调用次数比 `acquire` 多会怎样？

回答：许可数会超过初始值。`Semaphore` 不校验释放者身份，`release()` 单纯做加法。比如初始 5 个许可，多 `release` 两次就变成 7 个，限流就失效了。生产环境要用 try-finally 保证成对调用。

#### 提问：`Semaphore` 的 `acquire` 方法有几种变体？各自什么场景用？

回答：主要有四种：
1. `acquire()`：阻塞等待，可被中断
2. `acquireUninterruptibly()`：阻塞等待，忽略中断信号
3. `tryAcquire()`：非阻塞，立刻返回成功或失败
4. `tryAcquire(timeout, unit)`：带超时的阻塞，超时返回 false

高并发限流一般用 `tryAcquire()` 快速失败，避免线程堆积；后台任务可以用带超时的版本，超时就放弃或重试。
