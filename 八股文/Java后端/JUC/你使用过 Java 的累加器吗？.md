# 你使用过 Java 的累加器吗？

## 回答重点

Java 里的累加器主要就是 **`LongAdder`** 和 **DoubleAdder**，它们是 JDK 8 引入的，专门用来解决高并发场景下 `AtomicLong` 性能不够的问题。

`AtomicLong` 底层靠 CAS 实现原子性，但所有线程都在抢同一个变量，并发量一上来就疯狂自旋重试，CPU 白白空转。`LongAdder` 的思路是把热点分散掉，内部维护一个 base 值加上一个 Cell 数组，不同线程尽量更新不同的 Cell，最后求和的时候把 base 和所有 Cell 加起来就行。

`AtomicLong` 所有线程竞争同一个 `value` 变量，CAS 失败就重试。`LongAdder` 内部有一个 base 和多个 Cell，线程先尝试 CAS 更新 base，失败了就根据线程 hash 找到对应的 Cell 去更新，Cell 之间互不干扰。求和时把 base 和所有 Cell 的值加起来。

![long.drawio.png](Z:/Public/images/jc1V6WdT_long.drawio_mianshiya.webp)

来看个典型用法，比如统计接口调用次数：

```java
public class ApiCounter {
    private LongAdder counter = new LongAdder();

    public void recordRequest() {
        counter.increment();  // 无锁累加
    }

    public long getTotal() {
        return counter.sum();  // 汇总所有 Cell
    }
}
```

Prometheus 的 Java 客户端、Micrometer 这些监控框架内部都用 `LongAdder` 来做计数器，就是看中它在高并发下写性能远超 `AtomicLong`。

## 扩展知识

### Cell 数组的扩容机制

`LongAdder` 并不是一开始就创建一堆 Cell，而是按需扩容。刚开始只有 base，第一次 CAS 失败才会初始化 Cell 数组，初始长度是 2。如果某个 Cell 上竞争还是很激烈，就会触发扩容，每次翻倍，但最大不会超过 CPU 核心数。

为什么限制在 CPU 核心数？因为同一时刻真正并行执行的线程数就那么多，Cell 再多也没意义，反而浪费内存。

![](Z:/Public/images/gd1Uxlw5_V4IBBI5NJQ_mianshiya.webp)

### `LongAdder` 和 `AtomicLong` 怎么选

AtomicLongLongAdder写性能高并发下急剧下降高并发下依然稳定读性能O(1)，直接读O(`n`)，要遍历求和内存占用8 字节8 + Cell 数组适用场景低并发或需要精确实时值高并发统计，允许最终一致

关键区别在于 sum 方法不是原子的。调用 sum 的时候，其他线程可能还在更新 Cell，所以拿到的值是“近似值”。如果你的场景是统计 QPS、请求量这种，差个几十几百无所谓，那就用 `LongAdder`。如果是要做精确的序列号生成，还是老老实实用 `AtomicLong`。

### LongAccumulator 更灵活

`LongAdder` 只能做加法，如果你想做乘法、取最大值这种自定义操作，可以用 LongAccumulator：

```java
// 求最大值的累加器
LongAccumulator maxAccumulator = new LongAccumulator(Long::max, Long.MIN_VALUE);
maxAccumulator.accumulate(100);
maxAccumulator.accumulate(50);
maxAccumulator.accumulate(200);
System.out.println(maxAccumulator.get());  // 输出 200
```

底层实现和 `LongAdder` 一样，都是用 Cell 数组分散竞争，只不过累加逻辑可以自定义。

### @Contended 注解防止伪共享

Cell 类上标注了 @Contended 注解，这是为了防止伪共享。CPU 缓存是按缓存行加载的，一行通常 64 字节。如果两个 Cell 挨在一起被加载到同一缓存行，一个线程更新自己的 Cell 会导致另一个线程的缓存行失效，白白增加缓存同步开销。

@Contended 会在对象前后各填充 128 字节，保证每个 Cell 独占缓存行，互不干扰。这也是为什么 `LongAdder` 内存占用比 `AtomicLong` 大不少的原因之一。

## 面试官追问

#### 提问：`LongAdder` 的 sum 方法为什么不是原子的？有没有办法拿到精确值？

回答：sum 方法遍历 base 和所有 Cell 求和，遍历过程中没有加锁，其他线程可以继续更新，所以结果是近似值。想拿精确值只能在业务层自己加锁，或者用 reset 方法，但 reset 会清零，适合周期性统计的场景。

#### 提问：为什么 Cell 数组长度是 2 的幂次？

回答：为了用位运算快速定位 Cell。线程通过 getProbe 拿到一个 hash 值，然后用 hash & (cells.length - 1) 算出下标，这比取模快得多。Cell 扩容也是翻倍，保证长度始终是 2 的幂次。

#### 提问：高并发下 `LongAdder` 一定比 `AtomicLong` 快吗？

回答：写操作是的，读操作不一定。`AtomicLong` 读就是一次 volatile 读，$O(1)$。`LongAdder` 的 sum 要遍历所有 Cell，Cell 越多越慢。所以如果读多写少，`AtomicLong` 可能更合适。

#### 提问：`LongAdder` 能保证可见性吗？

回答：base 和每个 Cell 内部的 `value` 都是 volatile 的，单个变量的可见性没问题。但 sum 不是原子操作，读到的是某个时刻的快照，不保证和其他线程的写操作有严格的 happens-before 关系。
