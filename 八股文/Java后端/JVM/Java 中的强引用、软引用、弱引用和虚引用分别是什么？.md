# Java 中的强引用、软引用、弱引用和虚引用分别是什么？

## 回答重点

Java 里的引用按“强度”分成四种，强度越弱，GC 越容易回收。

1. 强引用：平时写的 `Object obj = new Object()` 就是强引用。只要强引用还在，对象就绝对不会被回收，哪怕内存爆了抛 OOM 也不回收。

2. 软引用：通过 `SoftReference` 包装的引用。内存够用的时候不回收，内存吃紧快要 OOM 的时候才回收。天然适合做缓存。

3. 弱引用：通过 `WeakReference` 包装的引用。只要 GC 一运行，不管内存够不够，只被弱引用指着的对象就会被回收。`WeakHashMap` 就是用这个机制实现自动清理的。

4. 虚引用：通过 `PhantomReference` 包装的引用。这玩意压根拿不到对象实例（`get()` 永远返回 `null`），唯一的用途是监控对象什么时候被回收，配合 `ReferenceQueue` 使用。

![](Z:/Public/images/3tsTIAPj_tmtZ5IZcBP_mianshiya.webp)

## 扩展知识

### 软引用的实战用法

软引用最典型的场景是**内存敏感型缓存**。比如一个图片浏览器，图片解码后占内存很大，用软引用缓存起来：内存充裕时能快速复用，内存紧张时自动释放，不用操心缓存淘汰策略。

```java
Map<String, SoftReference<Bitmap>> imageCache = new HashMap<>();

public Bitmap getImage(String path) {
    SoftReference<Bitmap> ref = imageCache.get(path);
    if (ref != null) {
        Bitmap bitmap = ref.get();
        if (bitmap != null) {
            return bitmap;  // 缓存命中
        }
    }
    // 缓存未命中或已被回收，重新加载
    Bitmap bitmap = loadFromDisk(path);
    imageCache.put(path, new SoftReference<>(bitmap));
    return bitmap;
}
```

但软引用缓存有个问题：回收时机不可控。具体什么时候回收、回收多少，不同 JVM 实现差异很大。生产环境更推荐用 Guava Cache 或 Caffeine 这种有明确淘汰策略的缓存框架。

![](Z:/Public/images/dcgdyHUR_HMuCJ63vJW_mianshiya.webp)

### 弱引用与内存泄漏

WeakHashMap 的 `key` 是弱引用，当 `key` 对象没有其他强引用时，整个 `entry` 会在下次 GC 时被清理。这在某些场景下很有用，比如给对象附加一些元数据，对象消亡后元数据自动清理。

```java
WeakHashMap<Object, String> metadata = new WeakHashMap<>();
Object key = new Object();
metadata.put(key, "some metadata");

key = null;  // 没有强引用了
System.gc();
// 此时 metadata 中的 entry 会被清理
```

不过 ThreadLocal 里有个经典的“伪内存泄漏”问题：ThreadLocalMap 的 `key` 是弱引用（指向 ThreadLocal 实例），但 `value` 是强引用。如果 ThreadLocal 实例被回收了，`key` 变成 null，但 `value` 还在，这块内存就泄漏了。所以用完 ThreadLocal 一定要调用 `remove()`。

### 虚引用的版本差异

虚引用必须配合 ReferenceQueue 使用，对象被回收后，虚引用会被放进队列，通过轮询队列就能知道对象什么时候死的。

```java
ReferenceQueue<Object> queue = new ReferenceQueue<>();
Object obj = new Object();
PhantomReference<Object> phantom = new PhantomReference<>(obj, queue);

obj = null;
System.gc();

// 轮询队列
Reference<?> ref = queue.poll();
if (ref != null) {
    // 对象已被回收，可以做清理工作
}
```

JDK 9 对虚引用有个重要改动。JDK 8 及之前，虚引用指向的对象在虚引用本身被清除之前是不会被回收的：

![68747470733a2f2f63646e2e6a7364656c6976722e6e65742f67682f79657373696d6964612f63646e5f696d6167652f696d672f696d6167652d32303231303232383131323634333133352e706e67.png](Z:/Public/images/68747470733a2f2f63646e2e6a7364656c6976722e6e65742f67682f79657373696d6964612f63646e5f696d6167652f696d672f696d6167652d32303231303232383131323634333133352e706e67_mianshiya.webp)

JDK 9 改了这个行为，虚引用不再阻止对象被回收：

![68747470733a2f2f63646e2e6a7364656c6976722e6e65742f67682f79657373696d6964612f63646e5f696d6167652f696d672f696d6167652d32303231303232383131323730323538322e706e67.png](Z:/Public/images/68747470733a2f2f63646e2e6a7364656c6976722e6e65742f67682f79657373696d6964612f63646e5f696d6167652f696d672f696d6167652d32303231303232383131323730323538322e706e67_mianshiya.webp)

相关变更记录：[https://bugs.openjdk.java.net/browse/JDK-8071507](https://bugs.openjdk.java.net/browse/JDK-8071507)

JDK 11 的文档已经删掉了那段话，所以 JDK 9 及之后虚引用对 GC 完全没有影响了。

![68747470733a2f2f63646e2e6a7364656c6976722e6e65742f67682f79657373696d6964612f63646e5f696d6167652f696d672f696d6167652d32303231303232383131323732343135382e706e67.png](Z:/Public/images/68747470733a2f2f63646e2e6a7364656c6976722e6e65742f67682f79657373696d6964612f63646e5f696d6167652f696d672f696d6167652d32303231303232383131323732343135382e706e67_mianshiya.webp)

### 虚引用的实际应用

JDK 9 引入的 Cleaner 就是基于虚引用实现的，用来替代 finalize()。DirectByteBuffer 的堆外内存回收就是靠 Cleaner 触发的：

```java
Cleaner cleaner = Cleaner.create();
Object resource = new Object();
cleaner.register(resource, () -> {
    // 这里做资源清理，比如释放堆外内存
    System.out.println("资源被回收了");
});
```

相比 finalize()，Cleaner 不会拖慢 GC，也不会有对象复活的风险，是更现代的资源清理方式。

## 面试官追问

#### 提问：软引用在什么时候会被回收？是内存不足就立刻回收吗？

回答：不是立刻回收。JVM 规范只保证“在抛 OOM 之前会回收所有软引用”，但具体时机由 JVM 实现决定。HotSpot 有个 `-XX:SoftRefLRUPolicyMSPerMB` 参数，默认 1000，意思是每 MB 空闲堆内存可以让软引用多存活 1 秒。空闲内存越少，软引用存活时间越短。所以软引用不是“内存不足才回收”，是“内存越紧张回收得越积极”。

#### 提问：WeakHashMap 的 `value` 是强引用还是弱引用？会不会内存泄漏？

详细解答可以看：[Java 中的 WeakHashMap 是什么 ？](https://www.mianshiya.com/question/1780933294804725761)

回答：`value` 是强引用。但 WeakHashMap 在每次操作（`get`、`put`、`size`）时都会调用 expungeStaleEntries() 清理已经失效的 `entry`。只要你还在正常使用这个 `map`，泄漏的内存会被逐步清理。但如果你往里面塞了数据然后再也不访问了，那些 `key` 被回收后 `value` 确实会泄漏，直到下次访问才会被清理。

#### 提问：为什么 PhantomReference 的 `get()` 方法永远返回 null？

回答：这是故意设计的。虚引用的目的是监控对象回收时机，不是为了访问对象。如果能通过 `get()` 拿到对象，就可能有人把对象再存到强引用里让它“复活”，这就破坏了虚引用的语义。所以 `get()` 直接写死返回 null，从 API 层面杜绝这种可能。
