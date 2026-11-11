# 如果一个线程在 Java 中被两次调用 start 方法，会发生什么？

## 回答重点

直接抛 **IllegalThreadStateException**。Java 规定一个 `Thread` 对象只能调用一次 `start()`，第二次调用时线程状态已经不是 NEW 了，JVM 会拒绝启动并抛异常。

看下 `start()` 的源码就明白了：

```java
public synchronized void start() {
    // threadStatus != 0 说明不是 NEW 状态
    if (threadStatus != 0)
        throw new IllegalThreadStateException();
    
    group.add(this);
    boolean started = false;
    try {
        start0();  // native 方法，真正创建操作系统线程
        started = true;
    } finally {
        // ...
    }
}
```

线程调用 `start()` 后状态从 NEW 变成 RUNNABLE，执行完 `run()` 方法后变成 TERMINATED。不管是 RUNNABLE 还是 TERMINATED，再调 `start()` 都会因为 threadStatus != 0 而抛异常。

![](Z:/Public/images/8dy8u2Fe_nG43GQipbd_mianshiya.webp)

线程状态是**单向流转**的，一旦离开 NEW 状态就回不去了。这跟操作系统线程的设计有关：一个线程执行完毕后，它的栈空间、寄存器上下文都被回收了，没法复活。

## 扩展知识

### Java 线程的 6 种状态

Java 在 `Thread`.State 枚举里定义了 6 种线程状态：

1. **NEW**：线程对象刚创建，还没调 `start()`

2. **RUNNABLE**：调了 `start()` 之后进入，包含了操作系统层面的 Ready 和 Running 两种状态。因为 JVM 不区分“等待 CPU 时间片”和“正在执行”，统一叫 RUNNABLE

3. **BLOCKED**：等待获取 synchronized 锁时进入，拿到锁就回到 RUNNABLE

4. **WAITING**：调用 `Object.wait()`、`Thread.join()`、`LockSupport.park()` 后进入，必须被其他线程显式唤醒

5. **TIMED_WAITING**：和 WAITING 类似，但指定了超时时间，比如 `Thread.sleep(1000)`、`Object.wait(1000)`，时间到了自动醒

6. **TERMINATED**：`run()` 执行完毕或者抛了未捕获异常，线程生命周期结束

![](Z:/Public/images/dbNlXOG6_7vBsoQpK95_mianshiya.webp)

这里有个细节：Blocked、Waiting、Timed_Waiting 在操作系统层面都是休眠状态，区别只是唤醒条件不同。

![c09d2476b6792db9ff27d3a863e2c72.png](Z:/Public/images/FFGIyzbE_c09d2476b6792db9ff27d3a863e2c72_mianshiya.webp)

### 操作系统线程 vs Java 线程状态

操作系统的线程只有 5 种状态：New、Ready、Running、Blocked、Terminated。

Java 把 Ready 和 Running 合并成了 RUNNABLE，原因是 JVM 跑在用户态，根本感知不到线程有没有真正拿到 CPU。一个线程从就绪变成运行再被抢占回就绪，这些切换发生在操作系统内核，JVM 层面看到的始终是“可以跑”。

另外 Java 把 Blocked 细分成了 BLOCKED、WAITING、TIMED_WAITING 三种，方便开发者排查问题。jstack 打出来的线程堆栈，一眼就能看出线程卡在哪了。

### 想复用线程怎么办

既然 `Thread` 对象不能重复 `start()`，那想复用线程该怎么办？用**线程池**。

线程池里的工作线程不是执行完一个任务就销毁，而是在一个 while 循环里不断从任务队列取任务执行。这些线程始终处于 RUNNABLE 状态，执行完任务后不会变成 TERMINATED，而是继续等待下一个任务。

```java
// 线程池工作线程的核心逻辑（简化版）
public void run() {
    while (true) {
        Runnable task = taskQueue.take();  // 阻塞等待任务
        task.run();  // 执行任务
    }
}
```

所以线程池本质上是绕过了“一个 `Thread` 只能 `start` 一次”的限制，让同一个线程反复执行不同的 `Runnable`。

## 面试官追问

#### 提问：线程池里的线程执行任务时抛了异常，这个线程会怎样？

回答：要看用的是 `execute()` 还是 `submit()`。`execute()` 提交的任务如果抛异常，工作线程会终止，线程池会创建一个新线程补上。`submit()` 提交的任务，异常会被吞掉存在 `Future` 里，调 `get()` 时才抛出来，工作线程不会挂。所以用 `submit()` 更稳妥，但一定要记得处理 `Future` 的异常。

#### 提问：为什么 Java 要把操作系统的 Ready 和 Running 合并成 RUNNABLE？

回答：因为 JVM 跑在用户态，压根感知不到线程有没有真正占用 CPU。操作系统的线程调度发生在内核态，一个线程被抢占、恢复这些事情对 JVM 是透明的。与其暴露一个不准确的状态，不如直接合并成 RUNNABLE，意思就是“这个线程随时可以跑”。

#### 提问：怎么让一个已经 TERMINATED 的线程“复活”？

回答：没法复活。线程对象的状态是单向的，一旦走到 TERMINATED 就定死在那了。想要执行同样的逻辑，只能 new 一个新的 `Thread` 对象重新 `start()`。真要复用线程，老老实实用线程池，它的工作线程一直活着不会 TERMINATED。
