# Java 并发库中提供了哪些线程池实现？它们有什么区别？

## 回答重点

Executors 工具类提供了 5 种开箱即用的线程池，本质上都是 ThreadPoolExecutor 或 ForkJoinPool 的不同参数配置。

1. FixedThreadPool，核心线程数和最大线程数相等，队列用的无界 `LinkedBlockingQueue`。线程数固定，多余任务在队列里排队。适合负载稳定、任务量可预估的场景，比如后台批量数据处理。

2. CachedThreadPool，核心线程数是 0，最大线程数是 Integer.MAX_VALUE，队列用的 SynchronousQueue。来一个任务就创建一个线程，空闲 60 秒后回收。适合突发性短任务，比如 HTTP 异步回调处理。

3. SingleThreadExecutor，只有 1 个线程，队列也是无界 `LinkedBlockingQueue`。任务严格按提交顺序执行。适合需要保证顺序性的场景，比如日志写入、消息顺序消费。

4. ScheduledThreadPool，核心线程数由参数指定，最大线程数是 Integer.MAX_VALUE，队列用的 DelayedWorkQueue。支持延迟执行和周期执行。适合定时任务场景，比如心跳检测、定时报表生成。

5. WorkStealingPool，底层是 ForkJoinPool，默认线程数等于 CPU 核心数。每个线程有自己的任务队列，空闲时会去其他线程的队列里偷任务。适合大量可拆分的小任务，比如递归计算、并行流处理。

![image.png](Z:/Public/images/SSzkFr7z_image_mianshiya.webp)

## 扩展知识

### 底层参数对比

5 种线程池看着不一样，但除了 WorkStealingPool，其他 4 种本质上都是 ThreadPoolExecutor，只是构造参数不同：

| 线程池类型 | `corePoolSize` | `maxPoolSize` | `keepAliveTime` | `workQueue` |
| --- | ---: | ---: | ---: | --- |
| `FixedThreadPool` | `n` | `n` | 0 | `LinkedBlockingQueue` |
| `CachedThreadPool` | 0 | `MAX_VALUE` | 60 s | `SynchronousQueue` |
| `SingleThreadExecutor` | 1 | 1 | 0 | `LinkedBlockingQueue` |
| `ScheduledThreadPool` | `n` | `MAX_VALUE` | 0 | `DelayedWorkQueue` |

理解这张表就能明白它们的行为差异：FixedThreadPool 线程数定死、任务排队；CachedThreadPool 来多少活创建多少线程；SingleThreadExecutor 永远只有 1 个干活的。

### 为什么阿里规范禁止用 Executors

阿里 Java 开发手册明确禁止直接用 Executors 创建线程池，核心原因是 OOM 风险：

1. FixedThreadPool 和 SingleThreadExecutor 的队列是无界的 `LinkedBlockingQueue`，任务堆积过多会撑爆内存。曾经有线上事故，单机内存 8G，队列里积压了 200 万个任务对象，直接 OOM。

2. CachedThreadPool 的最大线程数是 Integer.MAX_VALUE，高并发下会创建大量线程。每个线程默认栈空间 1MB，1000 个线程就是 1GB，几千个线程就能把系统打挂。

正确做法是手动创建 ThreadPoolExecutor，明确指定核心参数：

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    10,                      // 核心线程数
    20,                      // 最大线程数
    60, TimeUnit.SECONDS,    // 空闲线程存活时间
    new LinkedBlockingQueue<>(1000),  // 有界队列
    new ThreadFactoryBuilder().setNameFormat("biz-pool-%d").build(),
    new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略
);
```

![](Z:/Public/images/rRYRiEUD_C3RgkSaBm5_mianshiya.webp)

### WorkStealingPool 的工作窃取机制

WorkStealingPool 底层是 ForkJoinPool，它的特点是每个工作线程维护一个双端队列。自己的任务从队头取，窃取别人的任务从队尾取，这样能减少竞争。

典型使用场景是 Java 8 的并行流。比如 `list.parallelStream()`.`map`(...).collect(...) 底层就是用的 ForkJoinPool.commonPool，默认线程数是 CPU 核心数减 1。

注意一个坑：整个 JVM 共享一个 commonPool，如果你的并行流任务执行时间长，会影响其他用并行流的地方。解决办法是用自定义的 ForkJoinPool：

```java
ForkJoinPool customPool = new ForkJoinPool(4);
customPool.submit(() -> 
    list.parallelStream().map(...).collect(...)
).get();
```

## 面试官追问

#### 提问：线程池的核心线程数和最大线程数应该怎么设置？有什么经验公式吗？

详细解答可以看：[如何合理地设置 Java 线程池的线程数？](https://www.mianshiya.com/question/1780933294905389057)

回答：经典公式是 CPU 密集型设置成 CPU 核心数加 1，IO 密集型设置成核心数的 2 倍。但这公式太粗糙，实际要看任务的等待时间占比。比如一个任务总耗时 100ms，其中 80ms 在等数据库返回，那理论上线程数可以是核心数乘以 100/20 也就是 5 倍。[美团技术团队有篇文章](https://tech.meituan.com/2020/04/02/java-pooling-pratice-in-meituan.html)专门讲动态调整线程池参数，核心思路是先设置一个保守值，然后根据监控数据动态调整。

#### 提问：ScheduledThreadPool 和 Timer 有什么区别？为什么推荐用 ScheduledThreadPool？

回答：Timer 是单线程的，一个任务卡住后面全得等着。而且 Timer 里某个任务抛异常会导致整个 Timer 挂掉，其他任务也跟着完蛋。ScheduledThreadPool 用多线程，任务之间相互隔离，一个挂了不影响其他的。Spring 的 @Scheduled 注解底层就是用的 ScheduledThreadPoolExecutor。

#### 提问：CachedThreadPool 适合什么场景？我在高并发接口里用它可以吗？

回答：不建议。CachedThreadPool 的最大线程数是 Integer.MAX_VALUE，高并发下会无限制创建线程，很容易把系统打挂。它适合的是那种偶发性的、短时间大量请求的场景，比如某个定时任务每天跑一次，瞬间要处理几百个小任务，处理完线程就回收了。真正的高并发接口应该用 FixedThreadPool 或者手动创建有界的 ThreadPoolExecutor，配合有界队列和合理的拒绝策略。

#### 提问：我看到有人在 Spring Boot 里用 @Async 异步执行任务，底层用的是什么线程池？

详细解答可以看：[@Async 注解的原理是什么？](https://www.mianshiya.com/question/1799247492220788737)

回答：默认用的是 SimpleAsyncTaskExecutor，这货压根不是池化的，每次调用都创建新线程，非常坑。生产环境必须自己配置一个 ThreadPoolTaskExecutor 作为 @Async 的执行器，在配置类里定义一个 Bean，然后用 @Async 注解的 `value` 属性指定。
