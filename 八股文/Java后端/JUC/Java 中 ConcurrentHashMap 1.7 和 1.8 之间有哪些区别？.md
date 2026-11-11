# Java 中 ConcurrentHashMap 1.7 和 1.8 之间有哪些区别？

## 回答重点

两个版本的核心区别在于**锁的粒度**。

JDK 1.7 采用**分段锁**设计。底层把整个数组分成 16 个 Segment，每个 Segment 里面是一个完整的 `HashMap` 加一把 `ReentrantLock`。不同线程访问不同 Segment 完全不挡，同一 Segment 才有锁竞争，并发度最高 16。

![20220219203435.png](Z:/Public/images/20220219203435_mianshiya.webp)

JDK 1.8 移除了 Segment，锁粒度细化到**数组每个槽位**。数据结构跟 `HashMap` 同步，变成数组 + 链表 + 红黑树。插入时先用 CAS 无锁尝试插到数组位置，真冲突了才用 synchronized，而且只锁链表或树的头节点，其他线程照样可以操作别的 bucket，并发度大大增加。

![20220219203455.png](Z:/Public/images/20220219203455_mianshiya.webp)

两个版本的详细对比：

![concur.jpg](Z:/Public/images/HyJIGhzq_concur_mianshiya.webp)

顺便提一句加分点：

1. 1.7 计算 `size` 要把 16 个 Segment 都锁住再加起来，慢

2. 1.8 用类似 `LongAdder` 的 CounterCells，基本无锁统计

## 扩展知识

### 1.7 分段锁实现细节

先通过 `key` 的 hash 判断得到 Segment 数组的下标，将这个 Segment 上锁，然后再次通过 `key` 的 hash 得到 Segment 里 HashEntry 数组的下标，下面这步其实就是 `HashMap` 一致了。

可以简化理解为：每个 Segment 数组存放的就是一个单独的 `HashMap`。

![20220219203444.png](Z:/Public/images/20220219203444_mianshiya.webp)

图上有 6 个 Segment，等于有六把锁，共可以有六个线程同时操作这个 `ConcurrentHashMap`，并发度就是 6。相比于直接将 `put` 方法上锁，并发度就提高了，这就是分段锁的核心思想。

具体上锁的方式来源于 Segment，这个类继承了 `ReentrantLock`，自身具备加锁功能。

1.7 分段锁的一个缺陷是 Segment 数组一旦初始化之后不会扩容，只有 HashEntry 数组会扩容，这就导致并发度定死在那了，不能随着数据的增加而提高并发度。

### 1.8 细粒度锁实现细节

1.8 做了更细粒度的锁控制，可以理解为数组的每个位置都是一把锁，扩容了锁也会变多，并发度也会增加。

![20220219203455.png](Z:/Public/images/20220219203455_mianshiya.webp)

思想转变就是把粒度更加细化。不分段了，直接把 Node 数组的每个节点分别上一把锁，这样并发度不就更高了吗？

1.8 也不借助 `ReentrantLock` 了，直接用 synchronized，这也侧面证明都到 1.8 了，synchronized 优化后的速度已经不下于 `ReentrantLock`。

具体实现思路：当塞入一个值的时候，先计算 `key` 的 hash 后的下标，如果计算到的下标还未有 Node，就通过 CAS 塞入新的 Node。如果已经有 Node 则通过 synchronized 将这个 Node 上锁，这样别的线程就无法访问这个 Node 及其之后的所有节点。然后判断 `key` 是否相等，相等则是替换 `value`，反之则是新增一个 Node，这个操作和 `HashMap` 一样。

### 扩容的区别

1.7 每个 Segment 中包含一个 `HashMap`，当某个 Segment 内的 `HashMap` 达到扩容阈值时，单独为该 Segment 进行扩容，不会影响其他 Segment。每个 Segment 维护自己的负载因子，整体的 `ConcurrentHashMap` 并不是一次性全部扩容。

1.8 取消了 Segment，变成一个全局的数组。当任意位置的元素超过阈值时，整个数组都会被扩容。扩容时通过 CAS 操作确保线程安全，避免了锁住整个数组。

1.8 引入了**渐进式扩容**机制，多个线程可以同时帮助完成扩容操作。当 `put` 的时候发现当前 Node 的 hash 值是 -1，表明当前节点正在扩容，会触发协助扩容机制：

![image.png](Z:/Public/images/yrjrC1S9_image_mianshiya.webp)

扩容无非就是搬迁 Node，假设当前数组长度为 32，那就可以分着搬迁，31-16 这几个下标的 Node 都由线程 A 来搬迁，然后线程 B 来搬迁 15-0 这几个下标的 Node。

内部会维护一个 transferIndex 变量，来的线程死循环 CAS 争抢下标，如果下标已经分配完了，那自然就不需要搬迁了，如果 CAS 抢到了要搬运的下标，那就去帮忙搬就好了。

### `size` 逻辑的区别

1.7 有个尝试的思想，当调用 `size` 方法的时候不会加锁，先尝试三次不加锁获取 sum。如果三次总数一样，说明当前数量没有变化，直接返回。如果总数不一样，说明有线程在增删 `map`，于是加锁计算，这时候其他线程就操作不了 `map` 了。

```java
if (retries++ == RETRIES_BEFORE_LOCK) {
       for (int j = 0; j < segments.length; ++j)
           ensureSegment(j).lock(); // force creation
}
   ...再累加数量
```

1.8 直接计算返回结果，采用类似 `LongAdder` 的思想。累加不再基于一个成员变量，搞了一个数组，每个线程在自己对应的下标地方进行累加，最后把数组里面的数据统一一下，就是最终的值了。这是分而治之的思想。

![20220219203519.png](Z:/Public/images/20220219203519_mianshiya.webp)

在 `put` 的时候，会通过 addCount 方法维护 counterCells 的数量，`remove` 的时候也会调用。

![20220219203527.png](Z:/Public/images/20220219203527_mianshiya.webp)

平日操作会维护 `map` 里面的节点数量，先通过 CAS 修改 baseCount，如果成功就直接返回，如果失败说明有线程在竞争，那就通过 hash 选择一个 CounterCell 对象进行修改，最终 `size` 的结果就是 baseCount + 所有 CounterCell。这种通过 counterCell 数组来减少并发下场景下对单个成员变量的竞争压力，提高了并发度，提升了性能，这也就是 `LongAdder` 的思想。

### CAS

- [500. 什么是 Java 的 CAS（Compare-And-Swap）操作？](https://www.mianshiya.com/question/1780933295027023873)

## 面试官追问

#### 提问：1.8 为什么用 synchronized 而不是继续用 `ReentrantLock`？

详细解答可以看：[Synchronized 和 `ReentrantLock` 有什么区别？](https://www.mianshiya.com/question/1780933294976692225)

回答：主要是 synchronized 在 1.6 之后做了大量优化，包括偏向锁、轻量级锁、自适应自旋等，性能已经和 `ReentrantLock` 差不多了。用 synchronized 有几个好处：第一是代码更简洁，不用显式加锁解锁；第二是 JVM 可以在运行时做更多优化，比如锁消除、锁粗化；第三是 synchronized 在 JIT 编译后有更好的内存布局。Doug Lea 在设计 1.8 的时候专门测过，synchronized 在这个场景下表现不差。

#### 提问：1.8 的渐进式扩容会不会导致读操作读到不一致的数据？

回答：不会。扩容时 `ConcurrentHashMap` 会同时保留新旧两个数组，读操作要么读到旧数组的数据，要么读到新数组的数据，都是正确的。具体来说，正在迁移的节点会被替换成一个特殊的 ForwardingNode，它的 hash 值是 -1，读操作碰到这个节点会自动去新数组查。已经迁移完的数据在新数组里，没迁移的还在旧数组里，两边都能正确读到。

#### 提问：1.7 的分段锁在计算 `size` 时为什么要先尝试三次不加锁？

回答：因为加锁代价太高了，要把 16 个 Segment 全锁住，等于整个 `map` 暂停服务。大部分情况下 `map` 没有并发写入，三次统计结果一样的概率很高，这时候直接返回就省了加锁的开销。只有真的有并发写入导致统计结果不一致时，才需要加锁来保证准确性。这是一种乐观的思想，先假设没问题，发现有问题再加锁。

#### 提问：`ConcurrentHashMap` 的 `key` 和 `value` 能不能为 null？为什么？

详细解答可以看：[为什么 Java 的 `ConcurrentHashMap` 不支持 `key` 或 `value` 为 null？](https://www.mianshiya.com/question/1780933294834085890)

回答：都不能为 null，会直接抛 NullPointerException。原因是在并发环境下，null 会产生歧义。比如你调用 `get`(`key`) 返回 null，你分不清是 `key` 不存在还是 `key` 对应的 `value` 就是 null。`HashMap` 可以用 containsKey 来区分，但 `ConcurrentHashMap` 不行，因为在你调用 containsKey 和 `get` 之间，可能有另一个线程把 `key` 删了或者加了，导致两次调用结果不一致。Doug Lea 在设计的时候直接禁止 null，避免这种歧义。
