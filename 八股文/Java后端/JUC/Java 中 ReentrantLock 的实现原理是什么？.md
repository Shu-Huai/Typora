# Java 中 ReentrantLock 的实现原理是什么？

## 回答重点

`ReentrantLock` 底层就是 **AQS + CAS** 那套东西。核心是一个 int 类型的 state 变量和一个等待队列。

加锁的时候，线程用 CAS 尝试把 state 从 0 改成 1，改成功了就拿到锁，把 exclusiveOwnerThread 设成自己。改失败了说明锁被别人占着，乖乖去同步队列尾部排队，然后 park 挂起。

解锁的时候，state 减 1，如果减到 0 就唤醒队列里的第一个等待线程。

可重入的实现很简单：同一个线程再次加锁，发现 exclusiveOwnerThread 就是自己，直接把 state 加 1，不用排队。释放的时候每次减 1，减到 0 才真正释放锁。

![image.png](Z:/Public/images/VWa8SBRY_image_mianshiya.webp)

公平锁和非公平锁的区别就在于：非公平锁上来就 CAS 抢一把，抢到了直接用，抢不到再排队；公平锁老老实实先检查队列里有没有人在等，有人等就去排队，没人才 CAS 抢。

```java
// 非公平锁 lock 方法
final void lock() {
    if (compareAndSetState(0, 1))  // 上来就抢
        setExclusiveOwnerThread(Thread.currentThread());
    else
        acquire(1);  // 抢不到再排队
}

// 公平锁 lock 方法  
final void lock() {
    acquire(1);  // 直接走排队逻辑
}
```

## 扩展知识

### 从自旋锁到 CLH 的演进

最原始的自旋锁就是不停地 CAS 同一个变量，抢到了就进，抢不到就一直循环。

```java
public class SpinLock {
    private final AtomicBoolean lock = new AtomicBoolean(false);

    public void lock() {
        while (!lock.compareAndSet(false, true)) {
            // 自旋等待
        }
    }

    public void unlock() {
        lock.set(false);
    }
}
```

问题很明显：100 个线程同时 CAS 同一个变量，CPU 缓存一致性协议会疯狂地在各个核心之间同步，这就是**总线风暴**，性能直接崩掉。而且完全凭运气抢锁，有的线程可能一直抢不到，饿死了。

CLH 锁解决了这两个问题。每个线程不再盯着同一个变量，而是盯着自己前驱节点的状态。排队抢锁，先来后到，不会饿死。

![image.png](Z:/Public/images/sI02tJvg_image_mianshiya.webp)

```java
public class CLHLock {
    private static class CLHNode {
        volatile boolean isLocked = true;
    }

    private final ThreadLocal<CLHNode> currentNode;
    private final ThreadLocal<CLHNode> predecessorNode;
    private final AtomicReference<CLHNode> tail;

    public CLHLock() {
        this.currentNode = ThreadLocal.withInitial(CLHNode::new);
        this.predecessorNode = new ThreadLocal<>();
        this.tail = new AtomicReference<>(new CLHNode());
    }

    public void lock() {
        CLHNode node = currentNode.get();
        CLHNode pred = tail.getAndSet(node);
        predecessorNode.set(pred);
        while (pred.isLocked) {
            // 自旋等待前驱节点释放
        }
    }

    public void unlock() {
        CLHNode node = currentNode.get();
        node.isLocked = false;
        currentNode.set(predecessorNode.get());
    }
}
```

### AQS 对 CLH 的改造

CLH 还是自旋，线程干等着也在耗 CPU。对于锁持有时间比较长的场景，让线程挂起更划算。

AQS 把自旋改成了 park 阻塞。但线程睡着了就没法自己检测前驱状态了，所以得让前驱主动唤醒后继。这就要求队列必须是双向链表，前驱释放锁的时候通过 next 指针找到后继，然后 unpark 唤醒它。

![image.png](Z:/Public/images/G3m5Z1I3_image_mianshiya.webp)

节点状态用 waitStatus 字段表示：

值名称含义0初始状态节点刚入队-1SIGNAL后继节点等着被唤醒1CANCELLED节点被取消，需要从队列移除-2CONDITION在条件队列里等着-3PROPAGATE共享模式下传播唤醒信号

当某个节点超时或者被中断取消后，要从队列里摘掉，后面的节点顶上来。

![image.png](Z:/Public/images/RVehD6XX_image_mianshiya.webp)

### 公平锁 vs 非公平锁的选择

非公平锁是默认选项，性能更好。因为线程被唤醒到真正运行有一段时间，这期间让新来的线程直接抢走锁反而减少了空闲时间。实测非公平锁的吞吐量能比公平锁高 30% 以上。

公平锁适合对延迟敏感的场景，保证先来的请求先处理完，不会出现某个请求等了半天还没被处理的情况。

### Condition 等待队列

`ReentrantLock` 配套的 Condition 其实就是 Object.`wait`/`notify` 的升级版，支持多个等待条件。

调用 condition.await 的时候，线程从同步队列移到条件队列，释放锁。调用 signal 的时候，把条件队列的头节点移回同步队列尾部，等着重新抢锁。

```java
ReentrantLock lock = new ReentrantLock();
Condition notEmpty = lock.newCondition();
Condition notFull = lock.newCondition();

// 生产者
lock.lock();
try {
    while (queue.isFull()) {
        notFull.await();  // 满了就等着
    }
    queue.add(item);
    notEmpty.signal();  // 通知消费者有货了
} finally {
    lock.unlock();
}
```

## 面试官追问

#### 提问：`ReentrantLock` 和 synchronized 怎么选？

详细解答可以看：[Synchronized 和 `ReentrantLock` 有什么区别？](https://www.mianshiya.com/question/1780933294976692225)

回答：大部分场景 synchronized 就够用了，JVM 对它优化得很好，偏向锁、轻量级锁这些机制让无竞争场景几乎零开销。`ReentrantLock` 用在需要高级功能的时候：可中断的锁获取、超时获取、公平锁、多条件等待。性能上两者差不多，synchronized 写起来更简单，不会忘记 unlock。

#### 提问：为什么 AQS 用双向链表而不是单向链表？

详细解答可以看：[说说 AQS 吧？](https://www.mianshiya.com/question/1780933295018635266)

回答：两个原因。第一，释放锁的时候要唤醒后继节点，需要 next 指针。第二，节点取消的时候要从队列里摘掉，单向链表只能从头遍历找前驱，双向链表直接通过 prev 指针就能找到前驱，时间复杂度从 $O(n)$ 降到 $O(1)$。

#### 提问：tryLock 和 lock 有什么区别？

详细解答可以看：[Synchronized 和 `ReentrantLock` 有什么区别？](https://www.mianshiya.com/question/1780933294976692225)

回答：lock 是死等，拿不到锁就一直阻塞。tryLock 是试一下，拿不到立马返回 false，不阻塞。还有带超时参数的 tryLock(time, unit)，等指定时间还拿不到就放弃。tryLock 常用来避免死锁，两把锁都 tryLock，有一把拿不到就全部释放重来。

#### 提问：state 变量为什么用 int 不用 boolean？

回答：因为要支持可重入。同一个线程多次加锁，state 就加多次，解锁的时候也要减同样次数才能真正释放。用 boolean 就只能表示锁定和未锁定两种状态，没法记录重入次数。另外 AQS 是通用框架，`Semaphore` 用 state 表示许可数量，`CountDownLatch` 用 state 表示计数，int 类型更通用。
