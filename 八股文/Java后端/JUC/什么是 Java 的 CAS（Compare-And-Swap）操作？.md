# 什么是 Java 的 CAS（Compare-And-Swap）操作？

## 回答重点

CAS 是一种**硬件级别的原子操作**，它比较内存中的某个值是否为预期值，如果是就更新为新值，不是就不动。整个比较和交换的过程是一条 CPU 指令完成的，不可能被打断。

CAS 需要三个操作数：变量的内存地址、旧的预期值、新值。CPU 根据内存地址拿到当前值，和预期值比较，相等就替换成新值，不相等就返回失败。失败了一般会自旋重试，直到成功为止。

![](Z:/Public/images/ERVZWfe7_Vkzl9uqPTL_mianshiya.webp)

## 扩展知识

### 为什么需要 CAS

我们经常有累加需求，比如一个值是 1，想把它加到 2，再加到 3。

这种比较在多线程的情况下就不安全，比如两个线程同时发现值等于 1，然后都把它改成了 2，明明加了两次，结果却只变成了 2。

![image.png](Z:/Public/images/q7ICGVwa_image_mianshiya.webp)

加锁可以解决，但是锁的开销大，线程要排队等待。硬件层面就提供了 CAS 指令，把比较和交换封装成一条原子指令，不需要加锁也能保证线程安全。

### CAS 的优缺点

优点很明显，无锁并发，线程不会阻塞，不会有死锁问题，吞吐量高。Java 里的原子类、`ConcurrentHashMap`、AQS 底层都大量使用 CAS。

缺点也有几个：

1. ABA 问题，值从 A 变成 B 又变回 A，CAS 检测不出来，以为没变过
2. 自旋开销，高并发时大量线程反复重试，CPU 空转浪费资源
3. 只能保证单个变量的原子性，多个变量的复合操作搞不定

### ABA 问题

ABA 问题是指变量值从 A 变为 B 再变回 A，CAS 操作无法检测到这种变化。解决思路是引入版本号，每次更新变量时同时更新版本号，这样即使值相同，版本号不同也能发现变化。

Java 中的 AtomicStampedReference 就提供了版本号解决方案，它内部有一个 Pair 封装了引用和版本号，利用 volatile 保证可见性。

![image.png](Z:/Public/images/mvcA75wT_image_mianshiya.webp)

在内部 CAS 中，添加了版本号的对比：

![image.png](Z:/Public/images/Ph924xai_image_mianshiya.webp)

使用示例：

```java
private AtomicStampedReference<Integer> atomicStampedReference = new AtomicStampedReference<>(0, 0);

public void updateValue(int expected, int newValue) {
    int[] stampHolder = new int[1];
    Integer currentValue = atomicStampedReference.get(stampHolder);
    int currentStamp = stampHolder[0];

    boolean updated = atomicStampedReference.compareAndSet(expected, newValue, currentStamp, currentStamp + 1);
    if (updated) {
        System.out.println("Value updated to " + newValue);
    } else {
        System.out.println("Update failed");
    }
}
```

Java 还提供了 AtomicMarkableReference 类。

![image.png](Z:/Public/images/XBpKXTks_image_mianshiya.webp)

原理类似，差别是内部只有一个 boolean 值，只能表示数据是否被修改过，不像 AtomicStampedReference 的 int 可以表示被修改了几次。

![](Z:/Public/images/spVjGUak_gGKLojolZb_mianshiya.webp)

### CAS 在 Java 中的实现

CAS 操作由 sun.misc.Unsafe 类提供，通过 JNI 调用底层硬件指令实现。Unsafe 是内部类，不推荐直接使用。

![image.png](Z:/Public/images/sGcSIEVy_image_mianshiya.webp)

实际开发中用 `java.util.concurrent.atomic` 包下的原子类就行，比如 `AtomicInteger`、`AtomicLong`、`AtomicReference` 等，它们封装了 CAS 操作：

```java
AtomicInteger atomicInteger = new AtomicInteger(1);
boolean updated = atomicInteger.compareAndSet(1, 2);
if (updated) {
    System.out.println("Value updated to 2");
} else {
    System.out.println("Update failed");
}
```

CAS 底层依赖硬件原子指令，x86 架构上是 cmpxchg 指令。JDK 9 之前会判断是不是多处理器，多处理器才在 cmpxchg 前加 lock 前缀。JDK 9 之后直接加 lock 前缀，因为现在基本都是多核处理器了。

### CAS 总线风暴

lock 前缀指令会把写缓冲区的数据立即刷新到主内存。在多处理器架构下，每个 CPU 通过嗅探总线来检查自己的缓存是否过期，某个 CPU 刷新数据到主存时会通过总线通知其它 CPU 让对应缓存失效。

![image.png](Z:/Public/images/AiNnhu94_image_mianshiya.webp)

如果大量线程高并发 CAS 修改同一个变量，总线上的缓存一致性流量会暴涨，总线成为瓶颈，这就是**总线风暴**。`LongAdder` 就是为了解决这个问题设计的，它把一个值拆成多个 Cell，每个线程更新不同的 Cell，最后汇总，减少对同一个内存地址的竞争。

## 面试官追问

#### 提问：`LongAdder` 是怎么解决 `AtomicLong` 高并发下的性能问题的？

详细解答可以看：[你使用过 Java 的累加器吗？](https://www.mianshiya.com/question/1780933294972497922)

回答：`AtomicLong` 所有线程都在 CAS 抢同一个变量，冲突激烈。`LongAdder` 内部维护一个 base 值和一个 Cell 数组，低并发时直接 CAS 更新 base，高并发时把线程哈希到不同的 Cell 上更新，最后 sum 的时候把 base 和所有 Cell 加起来。相当于把热点分散了，大大减少了 CAS 失败的概率。

#### 提问：为什么说 Unsafe 类不推荐直接使用？

回答：Unsafe 可以直接操作内存、绕过 JVM 的类型检查，用不好容易导致内存泄漏、JVM 崩溃这种严重问题。而且它是 sun 包下的内部类，不在 Java 标准 API 里，不同 JDK 实现可能不一样，随时可能被改掉。JDK 9 之后引入了 VarHandle 作为更安全的替代方案。

#### 提问：CAS 自旋失败次数太多怎么办？

详细解答可以看：[什么是 Java 中的锁自适应自旋？](https://www.mianshiya.com/question/1780933295006052353)

回答：可以设置自旋次数上限，超过就放弃或者改用锁。JDK 里的自旋锁一般自旋几十到几百次就会升级为重量级锁。另外也可以用退避策略，每次失败后等待一小段随机时间再重试，避免所有线程同时抢。`LongAdder` 的思路更好，直接减少竞争热点，比优化自旋策略更治本。
