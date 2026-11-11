# 什么是 Java 的 StampedLock？

## 回答重点

`StampedLock` 是 Java 8 引入的一种锁机制，相比 `ReentrantReadWriteLock` 最大的改进是引入了**乐观读锁**。传统的读写锁在读的时候也要加锁，而 `StampedLock` 的乐观读压根不加锁，只是拿一个时间戳，读完再校验一下这期间有没有写操作。如果没有，读就成功了；如果有写操作介入，再降级成悲观读锁重试。

这种设计在读多写少的场景下性能提升非常明显，因为大部分读操作都不用真正竞争锁。

`StampedLock` 提供三种锁模式：

1. 写锁：独占模式，和 `ReentrantLock` 一样，同一时刻只能有一个线程持有写锁

2. 悲观读锁：共享模式，多个线程可以同时持有读锁，但写锁必须等所有读锁释放

3. 乐观读锁：不是真正的锁，只是获取一个 stamp 时间戳，读完后通过 validate 方法校验期间有没有写操作

![](Z:/Public/images/sOQiPSgY_uS25oGpC7u_mianshiya.webp)

核心代码示例：

```java
public class StampedLockExample {
    private double x, y;
    private final StampedLock lock = new StampedLock();

    // 写操作
    public void move(double deltaX, double deltaY) {
        long stamp = lock.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            lock.unlockWrite(stamp);
        }
    }

    // 乐观读操作
    public double optimisticDistanceFromOrigin() {
        long stamp = lock.tryOptimisticRead();  // 拿时间戳，不加锁
        double currentX = x, currentY = y;
        if (!lock.validate(stamp)) {  // 校验期间有没有写操作
            stamp = lock.readLock();  // 有的话降级成悲观读
            try {
                currentX = x;
                currentY = y;
            } finally {
                lock.unlockRead(stamp);
            }
        }
        return Math.sqrt(currentX * currentX + currentY * currentY);
    }
}
```

## 扩展知识

### 内部实现原理

`StampedLock` 用一个 64 位的 long 值来管理状态。低 7 位表示读锁的持有数量，第 8 位是写锁标志位，高 56 位是版本号。每次写锁释放，版本号就加 1。

乐观读的 validate 方法其实就是对比当前版本号和拿到的 stamp 是否一致，不一致说明中间有写操作发生过。

![](Z:/Public/images/BoM3FqeD_A3c5Hdj6OI_mianshiya.webp)

### 和 `ReentrantReadWriteLock` 的区别

| 特性 | `StampedLock` | `ReentrantReadWriteLock` |
| --- | --- | --- |
| 乐观读 | 支持，无锁读取 | 不支持 |
| 可重入 | 不支持 | 支持 |
| 条件变量 | 不支持 | `Condition` 支持 |
| 公平模式 | 不支持 | 支持 |
| 锁升级 | 支持读锁升级为写锁 | 不支持 |

### 使用时的坑

1. **不可重入**：同一个线程拿着写锁再去拿写锁会直接死锁，这点和 `ReentrantLock` 不一样

2. **中断问题**：如果线程用 writeLock 或 readLock 等待获取锁时被 interrupt，会导致 CPU 飙升。解决办法是用 readLockInterruptibly 或 writeLockInterruptibly

[CPU 飙升示例代码](http://ifeve.com/stampedlock-bug-cpu)

我本地跑了下复现了：

![pic.jpg](Z:/Public/images/6Eag6VXp_pic_mianshiya.webp)

3. **不支持 Condition**：如果业务需要等待通知机制，老老实实用 `ReentrantLock`

### 适用场景

`StampedLock` 最适合读操作占绝大多数、写操作很少的场景，比如缓存、配置中心这类。如果写操作频繁，乐观读老是失败然后降级，反而不如直接用悲观锁。

另外如果需要可重入特性，或者需要 Condition 做线程协调，就别用 `StampedLock` 了。

## 面试官追问

#### 提问：乐观读的 validate 方法底层是怎么判断有没有写操作的？

回答：validate 就是对比当前 state 的高 56 位版本号和传入的 stamp 是否一致。如果一致说明期间没有写锁被获取和释放过，数据没被改过。这里面还有个细节，validate 会先做一次 loadFence 内存屏障，保证之前读到的数据不会被 CPU 缓存坑了。

#### 提问：`StampedLock` 的锁升级是怎么实现的？

回答：`StampedLock` 支持把读锁升级成写锁，用 tryConvertToWriteLock 方法。传入当前持有的读锁 stamp，如果此时没有其他线程持有读锁，就能升级成功返回新的写锁 stamp；如果有其他读者，升级失败返回 0。这比 `ReentrantReadWriteLock` 强，后者只能先释放读锁再拿写锁，中间有窗口期。

#### 提问：为什么 `StampedLock` 不支持可重入？

回答：设计上的取舍。`StampedLock` 用一个 long 值管理所有状态，要支持可重入就得记录每个线程的重入次数，要么用 ThreadLocal 要么用额外的数据结构，会增加复杂度和开销。Doug Lea 认为对于大多数场景，不可重入是可以接受的，换来的是更简洁的实现和更好的性能。

#### 提问：高并发写的场景下 `StampedLock` 表现怎么样？

回答：表现一般，甚至不如 synchronized。因为乐观读老是校验失败，每次都要降级成悲观读重试，白白浪费 CPU。而且 `StampedLock` 的写锁竞争激烈时也没什么优势。所以写多的场景还是用 `ReentrantLock` 或者 synchronized，别硬上 `StampedLock`。
