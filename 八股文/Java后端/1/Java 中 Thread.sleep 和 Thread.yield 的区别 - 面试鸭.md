# Java 中 Thread.sleep 和 Thread.yield 的区别？ - 面试鸭 | 2026最新面试题+详细答案解析

## 回答重点

sleep 和 yield 都能让当前线程暂停执行，但机制完全不同。

**Thread.sleep()** 会让线程进入 TIMED_WAITING 状态，老老实实睡指定的毫秒数。在睡眠期间线程不会占用 CPU 时间片，就像设了个闹钟，时间一到再醒来重新竞争 CPU。睡眠时间受操作系统计时器精度影响，可能有几毫秒的误差。

Thread.yield() 则只是"客气一下"，告诉调度器我愿意让出当前的 CPU 时间片。调用后线程依然是 RUNNABLE 状态，压根没阻塞。调度器会尝试把时间片给同优先级的其他线程，但如果没有合适的线程，当前线程可能立马又继续跑。yield 只是个提示，操作系统完全可以选择忽略。

两者最直观的区别在于线程状态变化：

1）sleep 调用后，线程从 RUNNABLE 变成 TIMED_WAITING，时间到了再回到 RUNNABLE 等待调度
2）yield 调用后，线程始终保持 RUNNABLE 状态，只是主动放弃当前时间片

![sleep.drawio.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/hHTeQR5q_sleep.drawio_mianshiya.webp)

简单来说，sleep 是"我要睡 5 分钟谁都别叫我"，yield 是"我歇会儿，有人要用就先让给他"。

## 扩展知识

### 底层实现差异

sleep 底层调用的是操作系统的定时器机制。在 Linux 上会调用 nanosleep 系统调用，把线程挂起放到等待队列里，内核设好定时器，时间到了再把线程唤醒放回就绪队列。整个过程线程是真的停下来了，不会被调度。

yield 的实现就简单多了，它只是触发一次重新调度。在 Linux 上对应 sched_yield 系统调用，把当前线程移到就绪队列末尾，然后调度器重新选一个线程执行。如果就绪队列里没别人，或者当前线程优先级最高，那可能刚让出去又轮回来了。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/Uq4gXHQ0_vQZqTpKP54_mianshiya.webp)

### 实际使用场景

sleep 用得比较多的场景：

1）轮询等待，比如等某个条件成立，每隔 100ms 检查一次
2）限流控制，处理完一批数据后睡一会儿，避免把下游打挂
3）模拟延迟，测试代码里模拟网络延迟或慢操作

yield 实际生产中用得很少，原因是它的行为太不确定了，你没法保证它真的能让出去。偶尔会在这些地方见到：

1）自旋锁的优化，在 CAS 失败后调一下 yield，给竞争者一点机会
2）调试并发问题，故意打乱线程执行顺序来复现 bug
3）CPU 密集型任务，定期 yield 一下防止某个线程霸占 CPU 太久

但说实话，现代 JVM 和操作系统的调度已经很智能了，显式调用 yield 的收益越来越小。

### sleep(0) 的特殊含义

sleep(0) 看起来是睡 0 毫秒，但实际效果跟 yield 很像，都是触发一次重新调度。不过有个细微差别：sleep(0) 会让线程放弃剩余时间片，触发一次上下文切换，而 yield 只是个建议，调度器可能直接忽略。

在一些自旋等待的场景，用 sleep(0) 或者 Thread.onSpinWait()（Java 9+）会比空转更友好，能让出 CPU 给其他线程，也能降低功耗。

更多细节可以参考：[516.Java 中 Thread.sleep(0) 的作用是什么？](https://www.mianshiya.com/question/1780933295102521345)

### 与 wait 和 park 的对比

方法所属类释放锁状态唤醒方式sleepThread不释放TIMED_WAITING时间到或 interruptyieldThread不释放RUNNABLE自动继续waitObject释放WAITING/TIMED_WAITINGnotify 或时间到parkLockSupport不释放WAITING/TIMED_WAITINGunpark 或 interrupt

一个常见的坑是以为 sleep 会释放锁，其实不会。线程拿着锁睡着了，别的线程就得干等着。想睡觉又想释放锁，得用 wait。

## 面试官追问

#### 提问：sleep 能被中断吗？中断后会发生什么？

回答：能被中断。如果线程在 sleep 期间被其他线程调用了 interrupt()，sleep 会立即抛出 InterruptedException 并清除中断标志位。所以 sleep 必须放在 try-catch 里，捕获到异常后要决定是继续执行还是退出。很多人习惯捕获后什么都不做，这是个坏习惯，至少应该重新设置中断标志，让上层代码知道发生了中断。

#### 提问：为什么说 yield 在生产环境用得少？

回答：主要是因为它的行为完全不可预测。调度器可以选择忽略 yield 的提示，而且不同操作系统、不同 JVM 实现的效果都不一样。你写的代码在自己机器上测试正常，换个环境可能完全不一样。生产环境需要的是确定性的行为，与其用 yield 瞎猜，不如用 sleep、wait 或者 LockSupport.park 这些行为明确的方法。

#### 提问：如果想让线程精确地暂停一段时间，有什么好办法？

回答：普通的 Thread.sleep 精度受操作系统影响，误差可能有几毫秒甚至十几毫秒。如果需要更高精度，可以用 LockSupport.parkNanos()，精度能到纳秒级别。再高的话就得用忙等待配合 System.nanoTime() 了，但这样会占用 CPU。实际上大部分业务场景毫秒级精度够用了，真需要微秒级精度的场景，比如高频交易，一般会上专门的实时系统或者硬件时钟。 ...
