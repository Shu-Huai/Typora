# Java 中什么情况会导致死锁？如何避免？ - 面试鸭 | 2026最新27 届校招 Java 热题+详细答案解析

## 回答重点

死锁就是两个或多个线程互相持有对方需要的锁，谁都不肯放手，结果全卡住了。发生死锁必须同时满足四个条件：

1）**互斥**：资源同一时刻只能被一个线程占用
2）**持有并等待**：线程拿着一个锁的同时，还想要另一个锁
3）**不可剥夺**：线程拿到的锁不能被强行抢走
4）**循环等待**：线程之间形成环形的锁依赖链

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/V5EaAbsj_3j5v4Z3nLc_mianshiya.webp)

打破任意一个条件就能避免死锁。

最经典的死锁场景：

```java
Object lockA = new Object();
Object lockB = new Object();

// 线程 1：先拿 A 再拿 B
new Thread(() -> {
    synchronized (lockA) {
        sleep(100);  // 给线程 2 机会拿到 lockB
        synchronized (lockB) {
            // 永远执行不到这里
        }
    }
}).start();

// 线程 2：先拿 B 再拿 A
new Thread(() -> {
    synchronized (lockB) {
        sleep(100);
        synchronized (lockA) {
            // 永远执行不到这里
        }
    }
}).start();
```

线程 1 持有 lockA 并等待 lockB，线程 2 持有 lockB 并等待 lockA，形成循环等待，两个线程都无法继续执行

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/tzzrbl1J_xZvGsXvKk6_mianshiya.webp)

### 避免/降低死锁的常用方法

1）**固定加锁顺序**：所有线程都按照 A→B→C 的顺序获取锁，就不会形成环路。上面的例子如果线程 2 也改成先拿 A 再拿 B，死锁就消失了。

2）**使用 tryLock 超时机制**：ReentrantLock 的 tryLock(timeout) 尝试获取锁，超时就放弃，避免无限等待。

```java
if (lockA.tryLock(1, TimeUnit.SECONDS)) {
    try {
        if (lockB.tryLock(1, TimeUnit.SECONDS)) {
            try {
                // 业务逻辑
            } finally {
                lockB.unlock();
            }
        }
    } finally {
        lockA.unlock();
    }
}
```

3）**缩小锁的粒度**：锁的范围越小，持有时间越短，发生死锁的概率越低。

4）**避免嵌套锁**：能用一把锁搞定就别用两把，嵌套越深越容易出问题。

## 扩展知识

### 死锁检测与排查

线上系统怀疑死锁时，可以用 jstack 命令抓取线程堆栈：

```bash
jstack <pid> > thread_dump.txt
```

jstack 会自动分析死锁，输出类似这样的信息：

```
Found one Java-level deadlock:
=============================
"Thread-1":
  waiting to lock monitor 0x00007f8b4c003c58 (object 0x000000076ab24c68)
  which is held by "Thread-0"
"Thread-0":
  waiting to lock monitor 0x00007f8b4c0062c8 (object 0x000000076ab24c78)
  which is held by "Thread-1"
```

JDK 自带的 VisualVM、JConsole 都能图形化展示线程状态，排查死锁更直观。

### 数据库死锁

Java 代码里的死锁好排查，数据库层面的死锁更隐蔽。两个事务分别锁住对方需要的行，也会形成死锁：

```sql
-- 事务 1
UPDATE account SET balance = balance - 100 WHERE id = 1;  -- 锁住 id=1
UPDATE account SET balance = balance + 100 WHERE id = 2;  -- 等 id=2

-- 事务 2
UPDATE account SET balance = balance - 100 WHERE id = 2;  -- 锁住 id=2
UPDATE account SET balance = balance + 100 WHERE id = 1;  -- 等 id=1
```

MySQL InnoDB 有死锁检测机制，发现死锁会自动回滚代价较小的事务。可以通过 `SHOW ENGINE INNODB STATUS` 查看最近的死锁日志。

### 活锁与饥饿

和死锁相关的还有两个概念：

**活锁**：线程没有阻塞，但一直在做无用功。就像两个人在走廊相遇，都想给对方让路，结果一起往左、一起往右，谁也过不去。解决办法是引入随机等待时间。

**饥饿**：某个线程长期得不到资源。比如低优先级线程一直被高优先级线程抢占，永远轮不到执行。解决办法是使用公平锁，ReentrantLock 构造时传入 true 就是公平锁。

### 银行家算法

操作系统课本里经典的死锁避免算法。核心思想是在分配资源前先模拟一遍，看分配后系统是否还处于安全状态。如果模拟发现可能死锁，就拒绝这次分配。实际工程中很少用，因为需要预先知道线程最大资源需求，而且计算开销大。了解原理即可，面试偶尔会问。

## 面试官追问

#### 提问：生产环境发现死锁了，重启之外还有什么办法临时恢复？

回答：如果是 ReentrantLock 这种可中断的锁，可以用 jstack 找到死锁线程，然后通过 JMX 或者写个 Agent 调用 thread.interrupt() 中断其中一个线程，让它释放锁。synchronized 的锁没法中断，只能重启。MySQL 数据库层面的死锁会自动处理，不需要人工干预。长远来看还是得改代码，光靠运维手段治标不治本。

#### 提问：为什么 synchronized 没有 tryLock 这种超时机制？

>

详细解答可以看：[Synchronized 和 ReentrantLock 有什么区别？](https://www.mianshiya.com/question/1780933294976692225)

回答：这是 synchronized 的设计局限。它是 JVM 内置的关键字，追求简单易用，功能自然就少。Java 5 引入 ReentrantLock 就是为了补这个短板，除了 tryLock 还支持公平锁、可中断、多 Condition。不过 synchronized 在 JDK 6 之后做了大量优化，偏向锁、轻量级锁这些，性能已经很好了，简单场景还是首选。

#### 提问：有没有遇到过实际项目中的死锁？怎么解决的？

回答：常见的一种是转账场景，A 给 B 转钱和 B 给 A 转钱同时发生，两边都按"先锁转出账户再锁转入账户"的逻辑，就死锁了。解决方案是按账户 ID 排序，ID 小的先锁，这样所有转账操作的加锁顺序就一致了。另一种是数据库事务里更新多行，顺序不一致导致死锁，解决办法是业务层面保证更新顺序，或者把多个小事务合并成一个。

#### 提问：ThreadMXBean 能检测死锁吗？代码里怎么写？

回答：能。JDK 提供了 ThreadMXBean 接口，调用 findDeadlockedThreads() 方法就能拿到死锁线程的 ID 数组。可以写个定时任务每隔几秒检测一次，发现死锁就报警。不过这个方法只能检测 synchronized 和 ReentrantLock 造成的死锁，Lock.lock() 之外的阻塞它检测不了。 ...
