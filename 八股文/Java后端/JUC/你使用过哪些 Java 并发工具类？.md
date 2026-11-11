# 你使用过哪些 Java 并发工具类？

## 回答重点

Java 并发工具类主要分布在 `java.util.concurrent` 包下，按功能可以分成这么几类：

1. 线程安全的集合类：`ConcurrentHashMap`、`CopyOnWriteArrayList`、`ConcurrentLinkedQueue`
2. 原子操作类：`AtomicInteger`、`AtomicLong`、`AtomicReference`、`LongAdder`
3. 同步协调工具：`CountDownLatch`、`CyclicBarrier`、`Semaphore`、`Phaser`
4. 阻塞队列：`ArrayBlockingQueue`、`LinkedBlockingQueue`、`PriorityBlockingQueue`
5. 锁相关：`ReentrantLock`、`ReentrantReadWriteLock`、`StampedLock`

![锁.drawio.png](Z:/Public/images/3PnMSzFO_qnghbthpgU_mianshiya.webp)

面试时不用全说，挑你项目里真正用过的讲就行。面试官大概率会追问其中某一个的实现原理，所以得根据自己的业务场景提前准备。

## 扩展知识

### `ConcurrentHashMap`

这是最常用的并发集合，几乎每个项目都会用到。JDK 7 用分段锁，把整个 Map 切成 16 个 Segment，每个 Segment 单独加锁；JDK 8 改成了 **CAS + synchronized**，锁粒度细化到单个桶，并发度大幅提升。

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("key1", 1);
// 原子性的 compute 操作，避免 get-then-put 的竞态
map.computeIfAbsent("key2", k -> expensiveCompute(k));
```

### `AtomicInteger` 和 `LongAdder`

`AtomicInteger` 底层靠 CAS 实现，适合低竞争场景。但高并发下 CAS 会频繁失败重试，性能急剧下降。

JDK 8 引入的 `LongAdder` 专门解决这个问题。它内部维护一个 base 变量和一个 Cell 数组，不同线程往不同的 Cell 上累加，最后求和。热点分散了，竞争就小了。实测 64 线程并发累加，`LongAdder` 比 `AtomicLong` 快 5-10 倍。

```java
// 低竞争用 AtomicInteger
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();

// 高竞争用 LongAdder
LongAdder adder = new LongAdder();
adder.increment();
long sum = adder.sum(); // 统计时才求和
```

### `CountDownLatch` vs `CyclicBarrier`

这俩经常被问到区别，核心差异在于 **能不能复用**。

`CountDownLatch` 是一次性的，计数器减到 0 就废了。典型场景是主线程等多个子线程完成初始化：

```java
CountDownLatch latch = new CountDownLatch(3);
for (int i = 0; i < 3; i++) {
    executor.execute(() -> {
        doInit();
        latch.countDown();
    });
}
latch.await(); // 主线程阻塞，直到 3 个任务都完成
```

`CyclicBarrier` 可以循环使用，适合分阶段并行计算。比如 MapReduce 场景，每轮计算完大家在屏障点汇合，然后进入下一轮：

```java
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    System.out.println("一轮计算完成，合并结果");
});
for (int i = 0; i < 3; i++) {
    executor.execute(() -> {
        while (hasMoreData()) {
            compute();
            barrier.await(); // 等其他线程
        }
    });
}
```

![](Z:/Public/images/aOlS1Gnk_n5OgECieQA_mianshiya.webp)

### `Semaphore` 限流

`Semaphore` 本质是个许可证管理器，最多同时发出 N 张许可证。拿到许可证才能干活，干完了把许可证还回来。典型用途是限制并发访问某个资源的线程数：

```java
// 最多允许 10 个线程同时访问数据库连接池
Semaphore semaphore = new Semaphore(10);

public Connection getConnection() throws InterruptedException {
    semaphore.acquire();
    try {
        return pool.borrowConnection();
    } finally {
        // 注意：这里不能在 finally 里 release，应该在归还连接时 release
    }
}
```

### BlockingQueue 生产者消费者

阻塞队列是生产者消费者模型的标配。队列满了 `put` 阻塞，队列空了 take 阻塞，天然解决了线程协调问题：

```java
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(1000);

// 生产者
executor.execute(() -> {
    while (running) {
        Task task = createTask();
        queue.put(task); // 队列满了自动阻塞
    }
});

// 消费者
executor.execute(() -> {
    while (running) {
        Task task = queue.take(); // 队列空了自动阻塞
        process(task);
    }
});
```

常见实现有 `ArrayBlockingQueue` 有界数组实现、`LinkedBlockingQueue` 链表实现默认无界、`PriorityBlockingQueue` 支持优先级。线程池的任务队列就是用的 BlockingQueue。

### 关联题目

[什么是 Java 的 `Semaphore`？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933294934749186)

[什么是 Java 的 `CyclicBarrier`？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933294938943489)

[什么是 Java 的 `CountDownLatch`？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933294943137794)

[什么是 Java 的 `StampedLock`？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933294947332098)

[什么是 Java 的 `CompletableFuture`？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933294951526402)

## 面试官追问

#### 提问：`ConcurrentHashMap` 的 `size` 方法是怎么实现的？准确吗？

回答：JDK 8 的 `ConcurrentHashMap` 维护了一个 baseCount 和一个 CounterCell 数组，跟 `LongAdder` 的思路一样。每次 `put`/`remove` 不是直接改 baseCount，而是 CAS 失败后往 CounterCell 里累加。调用 `size` 时把 baseCount 和所有 CounterCell 的值加起来。这个值是个近似值，因为统计过程中其他线程可能还在改，但对于大多数场景够用了。如果需要精确值，得自己加锁。

#### 提问：`LongAdder` 为什么比 `AtomicLong` 快？有什么代价？

详细解答可以看：[你使用过 Java 的累加器吗？](https://www.mianshiya.com/question/1780933294972497922)

回答：快是因为热点分散。`AtomicLong` 所有线程都在抢同一个变量，CAS 失败率高。`LongAdder` 让不同线程往不同的 Cell 上写，冲突少了自然快。代价是两个：一是空间换时间，多了 Cell 数组；二是 sum 不是原子操作，统计过程中值可能变化，只能拿到近似值。所以如果你的场景需要精确读取当前值，比如做序列号生成，还是得用 `AtomicLong`。

#### 提问：`Semaphore` 的公平模式和非公平模式有什么区别？

详细解答可以看：[什么是 Java 的 `Semaphore`？](https://www.mianshiya.com/question/1780933294934749186)

回答：公平模式下先来的线程先拿到许可证，严格按 FIFO 排队；非公平模式下新来的线程可能插队，直接尝试 CAS 抢许可证。非公平模式吞吐量更高，因为省去了排队的开销，但可能导致某些线程饿死。默认是非公平的，构造函数第二个参数传 true 可以开启公平模式。

#### 提问：`CyclicBarrier` 如果其中一个线程挂了会怎样？

详细解答可以看：[什么是 Java 的 `CyclicBarrier`？](https://www.mianshiya.com/question/1780933294938943489)

回答：其他线程会收到 BrokenBarrierException。`CyclicBarrier` 内部有个 broken 标志，任何一个参与者抛异常或者被中断，都会把这个标志设成 true，同时唤醒所有在 await 的线程让它们抛异常退出。这是为了防止其他线程永远等下去。可以调用 reset 方法重置屏障状态，但要小心正在等待的线程也会收到 BrokenBarrierException。
