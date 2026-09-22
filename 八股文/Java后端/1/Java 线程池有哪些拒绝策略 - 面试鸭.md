# Java 线程池有哪些拒绝策略？ - 面试鸭 | 2026最新Java 并发面试题+详细答案解析

## 回答重点

线程池的拒绝策略是在任务队列满且线程数达到最大值时触发的兜底机制。JDK 内置了 4 种策略：

1）AbortPolicy，直接抛 RejectedExecutionException，这是默认策略。调用方能立即感知任务被拒，适合核心业务场景，比如订单支付必须让上游知道这单没处理。

2）CallerRunsPolicy，谁提交的任务谁执行。调用者线程被拉去干活，自然就提交不了新任务，相当于一个反压机制。适合允许短暂阻塞调用线程的场景，比如后台日志异步写入。

3）DiscardOldestPolicy，踢掉队列里排队最久的那个任务，把当前任务塞进去。用的时候要小心，老任务可能比新任务更重要。

4）DiscardPolicy，静默丢弃，不抛异常也不执行。只适合那些丢了也无所谓的场景，比如埋点上报。

![task.drawio.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/5r5dm8Gq_task.drawio_mianshiya.webp)

## 扩展知识

### 拒绝策略的触发时机

很多人以为队列满了就触发拒绝策略，其实不完全对。完整的判断链路是：核心线程满了 → 队列满了 → 最大线程也满了 → 触发拒绝策略。

用 ThreadPoolExecutor 的 execute 方法举例，源码里的逻辑是：

```java
public void execute(Runnable command) {
    int c = ctl.get();
    // 1. 工作线程数 < corePoolSize，创建核心线程
    if (workerCountOf(c) < corePoolSize) {
        if (addWorker(command, true)) return;
        c = ctl.get();
    }
    // 2. 核心线程满了，尝试入队
    if (isRunning(c) && workQueue.offer(command)) {
        // 入队成功，再检查一次状态
        int recheck = ctl.get();
        if (!isRunning(recheck) && remove(command))
            reject(command);
        else if (workerCountOf(recheck) == 0)
            addWorker(null, false);
    }
    // 3. 队列也满了，尝试创建非核心线程
    else if (!addWorker(command, false))
        // 4. 都满了，执行拒绝策略
        reject(command);
}
```

### 自定义拒绝策略

生产环境很少直接用内置策略，更多是实现 RejectedExecutionHandler 接口做定制。常见的做法：

```java
public class LogAndRetryHandler implements RejectedExecutionHandler {
    private static final Logger log = LoggerFactory.getLogger(LogAndRetryHandler.class);

    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
        log.warn("任务被拒绝, 队列大小: {}, 活跃线程: {}",
                 executor.getQueue().size(), executor.getActiveCount());
        // 方案1: 阻塞等待队列有空位
        try {
            executor.getQueue().put(r);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/P2xhI0hQ_H9pEsRiClu_mianshiya.webp)

### 常见坑点

1）CallerRunsPolicy 的陷阱：如果调用者是 Tomcat 的 Worker 线程，任务执行太久会导致 HTTP 请求超时。曾经有个线上事故，接口 P99 从 50ms 飙到 30 秒，最后发现是线程池满了，Tomcat 线程被拉去执行慢任务。

2）DiscardPolicy 和 DiscardOldestPolicy 的坑：任务被静默丢弃，业务上完全感知不到。曾经有团队用 DiscardPolicy 处理消息消费，结果丢了几万条消息，日志里一点痕迹都没有。

3）拒绝策略抛异常的影响：如果提交任务的地方没有 try-catch，AbortPolicy 抛出的异常可能导致调用链路中断。

## 面试官追问

#### 提问：如果我想在任务被拒绝时把它持久化到 Redis 或数据库，后续再补偿执行，怎么设计？

回答：在自定义 RejectedExecutionHandler 里做持久化，核心要解决三个问题。第一个是任务序列化，Runnable 本身不能直接序列化，需要把任务参数抽出来存，恢复时再重建任务对象。第二个是幂等设计，补偿执行可能跟正常执行重复，任务本身要支持幂等。第三个是补偿时机，可以用定时任务扫表，或者监听线程池空闲事件。美团的动态线程池组件 DynamicTp 就有类似的实现，被拒任务可以选择写入 MQ 或者本地文件。

#### 提问：CallerRunsPolicy 会导致什么问题？有没有更好的替代方案？

回答：最大的问题是调用者线程被阻塞。如果调用者是 Web 容器的 IO 线程，整个请求会被卡住。替代方案有两种思路：一种是用有界阻塞队列配合超时机制，任务提交时设置最大等待时间，超时就走降级逻辑；另一种是在拒绝策略里做异步转发，把任务扔到 Kafka 或者 RocketMQ，让消费者慢慢处理。

#### 提问：线程池 shutdown 之后再提交任务，走的是什么拒绝策略？

回答：走的也是配置的拒绝策略，但触发条件不一样。shutdown 之后线程池状态变成 SHUTDOWN，不再接受新任务，execute 方法里会检查状态，直接调 reject 方法。所以哪怕队列没满、线程数没达到最大值，只要线程池关了，新任务一律被拒。 ...
