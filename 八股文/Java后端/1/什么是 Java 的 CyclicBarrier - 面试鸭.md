# 什么是 Java 的 CyclicBarrier？ - 面试鸭 | 2026最新Java 并发面试题+详细答案解析

## 回答重点

CyclicBarrier 是一个**循环屏障**，允许一组线程互相等待，直到所有线程都到达屏障点后再一起继续执行。和 CountDownLatch 的区别在于它可以重复使用，适合多轮同步的场景。

比如有 3 个线程需要分阶段处理数据，每个阶段结束后必须等其他线程处理完才能进入下一阶段。第一个线程完成后调用 `await()` 阻塞，第二个线程完成后也调用 `await()` 阻塞，第三个线程调用 `await()` 时计数器归零，三个线程同时被唤醒进入下一阶段，屏障自动重置。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/8Nx9y1XC_9nFV0ffBYa_mianshiya.webp)

```java
// 3 个线程分阶段计算，每阶段结束后汇总
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    System.out.println("所有线程完成当前阶段，开始汇总");
});

for (int i = 0; i < 3; i++) {
    int taskId = i;
    new Thread(() -> {
        try {
            System.out.println("线程 " + taskId + " 完成第一阶段");
            barrier.await();  // 等待其他线程
            System.out.println("线程 " + taskId + " 完成第二阶段");
            barrier.await();  // 屏障可重复使用
        } catch (Exception e) {
            e.printStackTrace();
        }
    }).start();
}
```

## 扩展知识

### 底层实现原理

CyclicBarrier 基于 ReentrantLock 和 Condition 实现，不依赖 AQS 的共享模式。

![](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/cxYBXIj7_74e49a4c-81cb-494b-99c5-4dbf5ccaf073_mianshiya.webp)

内部维护一个 count 计数器和一个 generation 代。线程调用 `await()` 时先获取锁，然后 count 减 1。如果减完不等于 0，调用 `condition.await()` 阻塞当前线程。如果减完等于 0，说明最后一个线程到达，先执行 barrierAction 回调，再调用 `condition.signalAll()` 唤醒所有等待线程，最后重置 count 并更新 generation 开启下一轮。

![](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/gpCZG7AX_5c937bfd-20f3-4e6a-a9d3-9c1395553168_mianshiya.webp)

### 与 CountDownLatch 对比

特性CyclicBarrierCountDownLatch复用性可重复使用一次性，归零后失效等待方参与者互相等待一个或多个线程等待其他线程完成回调支持支持 barrierAction不支持计数方式await 递减countDown 递减典型场景多线程分阶段任务主线程等待子任务完成

简单理解：CountDownLatch 是「一群人干活，一个人等结果」，CyclicBarrier 是「一群人互相等，到齐了一起走」。

### 常见使用场景

1）并行计算分阶段汇总：MapReduce 风格的任务，每个阶段结束需要汇总中间结果

2）游戏匹配系统：5 个玩家都点击准备后才开始游戏

3）压测工具：所有线程准备就绪后同时发起请求，模拟并发峰值

### BrokenBarrierException 机制

如果等待过程中有线程被中断或超时，屏障会被打破，其他等待线程会收到 BrokenBarrierException。这时候需要调用 `reset()` 重置屏障才能继续使用。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/MC9giYKK_DEl39Sq9Hs_mianshiya.webp)

### 常见坑点

1）parties 数量和实际线程数必须匹配，少了会永远阻塞，多了也永远阻塞

2）barrierAction 由最后一个到达的线程执行，执行期间其他线程还在阻塞，别在里面搞耗时操作

3）屏障被打破后必须 reset 才能复用，否则后续 await 直接抛 BrokenBarrierException

## 面试官追问

#### 提问：CyclicBarrier 和 CountDownLatch 都能实现线程同步，实际项目中怎么选？

>

详细解答可以看：[什么是 Java 的 CountDownLatch？](https://www.mianshiya.com/question/1780933294943137794)

回答：看两个点。第一，任务是否分阶段，需要反复同步，选 CyclicBarrier。第二，是否需要回调，所有线程到齐后执行汇总逻辑，选 CyclicBarrier。如果只是主线程等一批子任务跑完，用完就扔，CountDownLatch 更简单直接。

#### 提问：如果我把 CyclicBarrier 的 parties 设成 5，但只有 4 个线程调用 await，会发生什么？

回答：4 个线程全部阻塞，永远等不到第 5 个。这是用 CyclicBarrier 最容易踩的坑，parties 必须和实际参与线程数严格一致。实际开发中一般用线程池的 invokeAll 配合 Future 更稳妥。

#### 提问：CyclicBarrier 的 barrierAction 在哪个线程执行？

回答：最后一个调用 await 到达屏障的线程执行。不是新起线程，也不是固定某个线程，谁最后到谁干这活。所以 barrierAction 里不能有太重的逻辑，不然会拖慢整体进度。
...
