# 什么是 Java 的 CompletableFuture？

## 回答重点

`CompletableFuture` 是 Java 8 引入的异步编程工具，解决了老版 `Future` 的两个痛点：一是 `get` 方法会阻塞线程，二是没法把多个异步任务串起来。

`CompletableFuture` 支持**链式调用**，可以用 thenApply、thenCompose 这些方法把多个异步操作像流水线一样串起来，前一个任务完成自动触发下一个，不用手动阻塞等结果。

基本用法是这样的：

1. 用 supplyAsync 提交一个有返回值的异步任务，或者 runAsync 提交一个无返回值的任务

2. 用 thenApply 对结果做转换，thenAccept 消费结果，thenRun 单纯执行后续动作

3. 用 exceptionally 或 handle 处理异常

4. 用 thenCombine 合并两个任务的结果，用 allOf 等待多个任务全部完成

![comple.drawio.png](Z:/Public/images/MxLL1b8l_comple.drawio_mianshiya.webp)

核心代码示例：

```java
CompletableFuture.supplyAsync(() -> queryUser(userId))    // 异步查用户
    .thenApply(user -> queryOrders(user))                 // 查订单
    .thenApply(orders -> calculateTotal(orders))          // 算总价
    .exceptionally(ex -> {                                // 异常兜底
        log.error("查询失败", ex);
        return BigDecimal.ZERO;
    });
```

## 扩展知识

### 和 `Future` 的区别

`Future` 是 Java 5 引入的，只能通过 `get` 阻塞拿结果，没法链式组合，异常处理也很麻烦。

| 特性 | `Future` | `CompletableFuture` |
| --- | --- | --- |
| 获取结果 | `get` 阻塞 | 回调，不阻塞 |
| 链式调用 | 不支持 | 支持 |
| 组合多任务 | 手动循环 | `allOf`/`anyOf` |
| 异常处理 | `try-catch` 包 `get` | `exceptionally`/`handle` |
| 手动完成 | 不支持 | `complete`/`completeExceptionally` |

![](Z:/Public/images/0qxOCB6U_N9fovIdK59_mianshiya.webp)

### 线程池的选择

默认情况下 `CompletableFuture` 用的是 ForkJoinPool.commonPool，这个池子是整个 JVM 共享的，核心线程数等于 CPU 核心数减 1。如果任务里有 IO 操作或者阻塞调用，很容易把公共池打满，影响其他用到 commonPool 的地方。

生产环境建议传自定义线程池：

```java
ExecutorService bizPool = new ThreadPoolExecutor(
    10, 50, 60, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(1000),
    new ThreadFactoryBuilder().setNameFormat("biz-async-%d").build()
);

CompletableFuture.supplyAsync(() -> doSomething(), bizPool);
```

### 常见的坑

1. **忘了处理异常**：如果不加 exceptionally 或 handle，异常会被吞掉，调试的时候一脸懵

2. **`get` 超时**：虽然 `CompletableFuture` 主打不阻塞，但有时候还是得等结果。用 `get`(timeout, unit) 而不是 `get()`，避免无限等待

3. **回调里阻塞**：在 thenApply 这些回调里搞阻塞操作，会拖慢整个线程池。如果必须阻塞，用 thenApplyAsync 把后续操作扔到独立线程池

4. **allOf 拿不到结果**：allOf 返回的是 `CompletableFuture<Void>`，拿结果得用 `join` 逐个取

```java
List<CompletableFuture<String>> futures = ids.stream()
    .map(id -> CompletableFuture.supplyAsync(() -> query(id)))
    .collect(toList());

CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
    .thenApply(v -> futures.stream()
        .map(CompletableFuture::join)
        .collect(toList()));
```

### Java 9+ 的增强

Java 9 加了几个实用方法：

1. completeOnTimeout：超时自动用默认值完成
2. orTimeout：超时抛 TimeoutException
3. copy：创建一个不能被外部 complete 的副本

```java
// 3秒没返回就用默认值
future.completeOnTimeout("default", 3, TimeUnit.SECONDS);

// 3秒没返回就抛异常
future.orTimeout(3, TimeUnit.SECONDS);
```

## 面试官追问

#### 提问：thenApply 和 thenApplyAsync 有什么区别？

回答：thenApply 用的是上一个任务的执行线程，如果上一个任务已经完成，就用当前调用 thenApply 的线程。thenApplyAsync 会把后续操作提交到线程池，默认是 commonPool，也可以传自定义线程池。如果回调里有耗时操作，用 Async 版本避免阻塞。

#### 提问：怎么实现多个异步任务，任意一个成功就返回？

详细解答可以看：[如何使用 Java 的 `CompletableFuture` 实现异步编排？](https://www.mianshiya.com/question/1776559515135643650)

回答：用 anyOf，但它有个问题，异常也算完成。如果想要第一个成功的结果，得自己写逻辑，用一个 `CompletableFuture` 作为结果容器，每个任务完成时调 complete，因为 complete 只有第一次调用生效，后面的会被忽略。

#### 提问：`CompletableFuture` 的 `join` 和 `get` 有什么区别？

回答：功能一样都是阻塞拿结果，区别是 `get` 抛的是受检异常 ExecutionException 和 InterruptedException，必须 try-catch 或者 throws。`join` 抛的是非受检异常 CompletionException，代码写起来简洁一些。在 Stream 的 lambda 里用 `join` 更方便，不用处理受检异常。

#### 提问：生产环境用 `CompletableFuture` 有什么注意事项？

回答：几个关键点：一是必须用自定义线程池，不要用 commonPool；二是必须处理异常，不然异常会被吞；三是设置合理的超时，避免无限等待；四是监控线程池状态，队列堆积要报警。另外日志里要打印任务执行线程名，方便排查问题。
