# 线程的生命周期在 Java 中是如何定义的？

## 回答重点

Java 线程的生命周期定义在 `Thread`.State 枚举里，一共 **6 种状态**：

1. **NEW**：线程对象刚 new 出来，还没调用 `start` 方法

2. **RUNNABLE**：调用 `start` 后进入这个状态，注意这里包含了操作系统层面的就绪和运行两个状态，只要没被阻塞就算 RUNNABLE

3. **BLOCKED**：线程想拿 synchronized 锁但是没拿到，被挡在同步块外面等着

4. **WAITING**：调用了 Object.`wait`、`Thread`.`join` 或 `LockSupport`.park，进入无限期等待，必须被别的线程显式唤醒

5. **TIMED_WAITING**：和 WAITING 类似，但是带超时时间，比如 `Thread`.`sleep`、`Object.wait(timeout)`、`Thread.join(timeout)`

6. **TERMINATED**：`run` 方法执行完毕或者抛了未捕获异常，线程挂了

**状态转换流程**：NEW 状态调用 `start` 方法进入 RUNNABLE。RUNNABLE 状态如果抢 synchronized 锁失败进入 BLOCKED，拿到锁回到 RUNNABLE。RUNNABLE 状态调用 `wait`/`join`/park 进入 WAITING，被 `notify`/unpark 唤醒回到 RUNNABLE。RUNNABLE 状态调用 `sleep`/`wait`(timeout)/`join`(timeout) 进入 TIMED_WAITING，超时或被唤醒回到 RUNNABLE。RUNNABLE 状态 `run` 方法结束或异常进入 TERMINATED。

![](Z:/Public/images/dbNlXOG6_7vBsoQpK95_mianshiya.webp)

## 扩展知识

### BLOCKED 和 WAITING 的区别

这俩状态容易混淆，核心区别在于触发原因不同。

BLOCKED 专指抢 synchronized 锁失败，线程想进同步块但锁被别人占着，只能在门口排队。这个状态是被动的，线程自己没法控制，只能等持有锁的线程释放。

WAITING 是线程主动放弃 CPU 进入等待，必须等别的线程来唤醒。Object.`wait` 需要 `notify`/`notifyAll` 唤醒，`Thread`.`join` 需要目标线程执行完，`LockSupport`.park 需要 unpark。

```java
Object lock = new Object();

// 线程 A：拿到锁后 wait，进入 WAITING
new Thread(() -> {
    synchronized (lock) {
        try {
            lock.wait();  // 释放锁，进入 WAITING
        } catch (InterruptedException e) {}
    }
}).start();

// 线程 B：拿不到锁，进入 BLOCKED
new Thread(() -> {
    synchronized (lock) {  // 锁被线程 A 持有，进入 BLOCKED
        // ...
    }
}).start();
```

![](Z:/Public/images/UwNaeudD_llSNUAoEOn_mianshiya.webp)

### Java 线程状态和操作系统线程状态的对应关系

操作系统把线程分成 5 种状态：新建、就绪、运行、阻塞、终止。Java 的 RUNNABLE 其实包含了操作系统的就绪和运行两个状态，因为 JVM 没法精确感知线程到底是在 CPU 上跑着还是在就绪队列里排队。

Java 状态操作系统状态NEW新建RUNNABLE就绪 + 运行BLOCKED阻塞WAITING阻塞TIMED_WAITING阻塞TERMINATED终止

操作系统只有一个阻塞状态，Java 细分成三种是为了让开发者更容易定位问题。看到 BLOCKED 就知道是锁竞争，看到 WAITING 就知道是在等唤醒。

### 状态转换的常见坑点

**`sleep` 不释放锁**：`Thread`.`sleep` 让线程进入 TIMED_WAITING，但如果线程持有 synchronized 锁，`sleep` 期间锁不会释放，其他线程还是拿不到锁。想让出锁要用 `wait`。

**`wait` 必须在同步块里调用**：Object.`wait`/`notify`/`notifyAll` 必须在 synchronized 块里调用，否则抛 IllegalMonitorStateException。因为 `wait` 要释放锁，没持有锁就没法释放。

**`notify` 不保证唤醒哪个线程**：如果有多个线程在 `wait`，`notify` 只随机唤醒一个，不是先等先唤醒。想唤醒全部要用 `notifyAll`，但唤醒后还要竞争锁，只有一个能拿到。

**interrupt 不一定能打断线程**：调用 interrupt 只是设置中断标志位，如果线程在 WAITING 或 TIMED_WAITING 状态会抛 InterruptedException 并清除标志位，但如果线程在 RUNNABLE 状态跑着计算，不会自动停下来，需要代码主动检查 `Thread`.interrupted。

```java
// 错误示范：interrupt 不能打断死循环
Thread t = new Thread(() -> {
    while (true) {
        // 不检查中断标志，interrupt 没用
    }
});
t.start();
t.interrupt();  // 没效果，线程还在跑

// 正确做法
Thread t2 = new Thread(() -> {
    while (!Thread.interrupted()) {
        // 检查中断标志
    }
});
```

### 如何排查线程状态问题

生产环境线程卡住，可以用 jstack 命令导出线程堆栈，或者用 Arthas 的 thread 命令实时查看。重点关注 BLOCKED 和 WAITING 状态的线程：

1. 大量线程 BLOCKED 在同一把锁上，说明锁竞争严重，考虑减小锁粒度或者换成并发容器

2. 线程 WAITING 在 Object.`wait` 上，检查是不是 `notify` 漏调用或者条件判断有 bug

3. 线程 TIMED_WAITING 在 `Thread`.`sleep` 上，可能是代码里写了不必要的 `sleep`

![](Z:/Public/images/lBQzSAij_RfQ6ktkx5L_mianshiya.webp)

## 面试官追问

#### 提问：RUNNABLE 状态的线程一定在执行吗？为什么 Java 不区分就绪和运行状态？

回答：不一定在执行，可能在就绪队列里等 CPU 时间片。Java 不区分是因为 JVM 没法精确感知底层调度，线程在就绪和运行之间切换太快了，查状态的时候可能刚好在切换中间，区分了也不准。另外对应用开发来说，知道线程没被阻塞就够了，具体是不是拿到 CPU 不影响排查问题。

#### 提问：线程从 WAITING 状态被唤醒后是直接变成 RUNNABLE 还是 BLOCKED？

回答：得看情况。如果是 Object.`wait` 被唤醒，线程需要重新竞争 synchronized 锁，如果锁被别人占着就进 BLOCKED，拿到锁才进 RUNNABLE。如果是 `LockSupport`.park 被 unpark，直接进 RUNNABLE，因为 park/unpark 不涉及锁竞争。`Thread`.`join` 被唤醒也是直接进 RUNNABLE。

#### 提问：调用 `Thread`.`yield` 方法线程状态会变化吗？

详细解答可以看：[Java 中 `Thread`.`sleep` 和 `Thread`.`yield` 的区别？](https://www.mianshiya.com/question/1828715607393472514)

回答：不会变，还是 RUNNABLE。`yield` 只是给调度器一个提示，愿意让出当前的时间片，但调度器可以忽略这个提示。即使生效了也只是从运行状态变成就绪状态，在 Java 层面都是 RUNNABLE。`yield` 用的很少，基本只在测试和压测时用来制造线程切换。

#### 提问：线程执行完进入 TERMINATED 状态后还能再调 `start` 吗？

详细解答可以看：[如果一个线程在 Java 中被两次调用 `start()` 方法，会发生什么？](https://www.mianshiya.com/question/1800331617560240129)

回答：不能，会抛 IllegalThreadStateException。线程是一次性的，用完就得 new 新的。想复用执行逻辑可以用线程池，ThreadPoolExecutor 里的工作线程会反复从队列里取任务执行，但每个工作线程本身只 `start` 一次。如果 `start` 之后马上又调一次 `start`，不管线程跑没跑完都会抛异常。
