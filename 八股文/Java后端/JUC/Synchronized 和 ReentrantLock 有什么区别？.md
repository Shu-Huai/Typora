# Synchronized 和 ReentrantLock 有什么区别？

## 回答重点

**synchronized** 是 Java 内置的关键字，用起来最简单，锁的获取和释放由 JVM 自动管理，不用操心忘记解锁的问题。`ReentrantLock` 是 JDK 1.5 引入的显式锁，功能更丰富，但必须手动 lock/unlock，一般配合 try-finally 使用。

核心区别用一张表说清楚：

| 特性 | `synchronized` | `ReentrantLock` |
| --- | --- | --- |
| 锁类型 | JVM 内置，隐式锁 | JUC 类库，显式锁 |
| 获取/释放 | 自动 | 手动，必须在 `finally` 中 `unlock` |
| 公平性 | 只支持非公平 | 支持公平/非公平 |
| 可中断 | 不支持 | `lockInterruptibly` 可响应中断 |
| 超时获取 | 不支持 | `tryLock(timeout)` 可避免死锁 |
| 条件变量 | 只有一个隐式等待队列 | 可创建多个 `Condition` |
| 可重入 | 支持 | 支持 |

![](Z:/Public/images/HpmqKeOE_pyjf7vZH3S_mianshiya.webp)

性能方面，很多年前 synchronized 确实比 `ReentrantLock` 慢不少，但 JDK 1.6 之后引入了偏向锁、轻量级锁、锁消除等优化，现在两者性能基本持平。选型主要看功能需求，不用纠结性能。

## 扩展知识

### 可重入锁的实现原理

两者都是可重入锁，同一个线程持有锁的时候可以再次获取，不会把自己锁死。实现方式都是靠计数器：

```java
public class ReentrantLockExample {
    private final ReentrantLock lock = new ReentrantLock();

    public void outer() {
        lock.lock();  // 计数器 = 1
        try {
            inner();
        } finally {
            lock.unlock();  // 计数器 = 0，真正释放锁
        }
    }

    public void inner() {
        lock.lock();  // 同一线程，计数器 = 2
        try {
            // 临界区
        } finally {
            lock.unlock();  // 计数器 = 1
        }
    }
}
```

每次加锁计数器加 1，每次解锁计数器减 1，减到 0 才真正释放锁让其他线程竞争。递归调用或者嵌套加锁的时候，可重入就很关键了，不然分分钟死锁。

### `ReentrantLock` 的高级用法

1. **tryLock 防死锁**

```java
if (lock.tryLock(3, TimeUnit.SECONDS)) {
    try {
        // 临界区
    } finally {
        lock.unlock();
    }
} else {
    // 3 秒没拿到锁，走降级逻辑
}
```

2. **lockInterruptibly 响应中断**

```java
try {
    lock.lockInterruptibly();
    // 临界区
} catch (InterruptedException e) {
    // 等待过程中被中断，可以做清理
} finally {
    if (lock.isHeldByCurrentThread()) {
        lock.unlock();
    }
}
```

3. **多 Condition 精细唤醒**

经典的生产者消费者模型，用两个 Condition 分别控制“队列满”和“队列空”的等待唤醒，比 synchronized 的 `wait`/`notify` 精准得多：

```java
private final Condition notFull = lock.newCondition();
private final Condition notEmpty = lock.newCondition();

// 生产者等待队列不满
notFull.await();
// 生产完唤醒消费者
notEmpty.signal();
```

### Synchronized 的实现

- [Java 的 synchronized 是怎么实现的？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933294980886530)

### `ReentrantLock` 的实现

- [Java 中 `ReentrantLock` 的实现原理是什么？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933295014440961)

## 面试官追问

#### 提问：公平锁和非公平锁有什么区别？为什么默认是非公平锁？

详细解答可以看：[Java 中 `ReentrantLock` 的实现原理是什么？](https://www.mianshiya.com/question/1780933295014440961)

回答：公平锁按照线程等待的先后顺序获取锁，先来先得。非公平锁允许插队，新来的线程可以直接尝试 CAS 抢锁，抢不到再排队。默认非公平是因为性能更好，减少了线程切换开销。公平锁每次都要唤醒队列头部线程，上下文切换多，吞吐量会下降。除非业务上要求严格排队，否则用非公平锁就行。

#### 提问：`ReentrantLock` 的 lock 方法忘记 unlock 会怎样？

回答：锁永远不释放，其他线程全部阻塞等待，程序卡死。所以必须用 try-finally 包起来，finally 里面 unlock，保证无论正常返回还是抛异常都能释放锁。synchronized 不存在这个问题，JVM 自动管理。

#### 提问：为什么 JDK 15 要废弃偏向锁？

详细解答可以看：[Java 的 synchronized 是怎么实现的？](https://www.mianshiya.com/question/1780933294980886530)

回答：偏向锁是为了优化单线程重复获取锁的场景，但现代应用普遍高并发，偏向锁命中率很低。更麻烦的是偏向锁撤销需要 Stop-The-World，在安全点暂停所有线程，代价不小。权衡之后发现偏向锁带来的收益抵不过撤销的开销，干脆移除了。

#### 提问：`ReentrantLock` 底层是怎么实现的？

详细解答可以看：[Java 中 `ReentrantLock` 的实现原理是什么？](https://www.mianshiya.com/question/1780933295014440961)

回答：基于 AQS，也就是 AbstractQueuedSynchronizer。AQS 内部维护一个 volatile 的 state 变量表示锁状态，还有一个 FIFO 双向队列存放等待线程。加锁就是 CAS 修改 state，修改成功就拿到锁，失败就入队等待。解锁把 state 减 1，减到 0 就唤醒队列头部线程。
