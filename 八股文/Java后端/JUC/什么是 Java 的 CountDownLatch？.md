# 什么是 Java 的 CountDownLatch？

## 回答重点

`CountDownLatch` 是 JUC 中的一个**倒计时门闩**，允许一个或多个线程等待其他线程完成操作后再继续执行。本质上就是一个计数器，初始值由构造函数指定，每调用一次 `countDown()` 减 1，减到 0 时所有调用 `await()` 的线程被唤醒。

典型场景：主线程需要等 3 个子任务都跑完才能汇总结果。创建 `new CountDownLatch(3)`，3 个子线程分别执行任务，完成后调用 `countDown()`。主线程调用 `await()` 阻塞，直到计数器归零被唤醒。

![image.png](Z:/Public/images/bNBpwdhX_image_mianshiya.webp)

```java
CountDownLatch latch = new CountDownLatch(3);

// 启动 3 个子任务
for (int i = 0; i < 3; i++) {
    int taskId = i;
    new Thread(() -> {
        System.out.println("任务 " + taskId + " 完成");
        latch.countDown();  // 计数器减 1
    }).start();
}

System.out.println("等待子任务完成...");
latch.await();  // 阻塞直到计数器归零
System.out.println("所有子任务完成，开始汇总");
```

## 扩展知识

### AQS 实现原理

`CountDownLatch` 底层基于 AQS 的**共享模式**实现。计数器值就是 AQS 的 state。

`countDown()` 通过 CAS 将 state 减 1，减到 0 时调用 `doReleaseShared()` 唤醒等待队列中的所有线程。`await()` 检查 state 是否为 0，不为 0 就入队阻塞。

关键点：state 只能从初始值往下减，减到 0 后不能重置。这就是 `CountDownLatch` 不可复用的根本原因。

![image.png](Z:/Public/images/0dXQWFY7_image_mianshiya.webp)

### 两种典型用法

1. 主线程等待多个子任务完成

这是最常见的用法，比如服务启动时需要等数据库连接池、缓存预热、配置加载都完成后才能对外提供服务。

2. 多线程同时起跑

让多个线程在同一时刻开始执行，模拟并发压测。

```java
CountDownLatch startSignal = new CountDownLatch(1);

for (int i = 0; i < 10; i++) {
    new Thread(() -> {
        try {
            startSignal.await();  // 所有线程在这里等待
            // 执行压测请求
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }).start();
}

Thread.sleep(1000);  // 等线程都就绪
startSignal.countDown();  // 发令枪响，10 个线程同时冲
```

### 与 `CyclicBarrier` 对比

| 特性 | `CountDownLatch` | `CyclicBarrier` |
| --- | --- | --- |
| 复用性 | 一次性 | 可重复使用 |
| 计数方式 | `countDown` 减 1 | `await` 减 1 |
| 等待关系 | 等待者和计数者可以不同 | 所有参与者互相等待 |
| 底层实现 | AQS 共享模式 | `ReentrantLock` + `Condition` |

![](Z:/Public/images/baRyMPWR_m23Rp0xMkM_mianshiya.webp)

### 常见坑点

1. 计数器只能用一次，归零后再调用 `await()` 不会阻塞，直接通过

2. `countDown()` 调用次数超过初始值不会报错，但没有任何效果

3. 如果某个子任务异常退出没调用 `countDown()`，主线程会永远阻塞。生产环境要用 `await(timeout, unit)` 加超时保护

4. `await()` 可以被中断，中断后抛 InterruptedException，计数器值不变

## 面试官追问

#### 提问：`CountDownLatch` 的 countDown 调用次数超过初始值会怎样？

回答：啥事没有。state 已经是 0 了，继续减还是 0，CAS 操作直接返回。不会抛异常也不会有副作用，但说明代码逻辑有问题，应该检查为什么会多调用。

#### 提问：如果子任务抛异常了，没调用 countDown，怎么办？

回答：主线程会永远阻塞。正确做法是 countDown 放 finally 块里，或者用 `await(5, TimeUnit.SECONDS)` 带超时。更稳妥的方案是用 `CompletableFuture` 的 allOf，异常会自动传播。

#### 提问：能不能让 `CountDownLatch` 的计数器重置？比如用反射改 state？

回答：技术上可以，但别这么干。直接修改 state 不会触发 doReleaseShared() 方法来唤醒等待队列中的线程，可能导致等待线程永远不被唤醒。需要复用就老老实实用 `CyclicBarrier` 或者新建一个 `CountDownLatch`。

#### 提问：await 方法可以被多个线程同时调用吗？

回答：可以。`CountDownLatch` 基于 AQS 共享模式，支持多个线程同时 await。计数器归零时，所有等待线程都会被唤醒。这个特性可以实现“多个消费者等待多个生产者”的场景。
