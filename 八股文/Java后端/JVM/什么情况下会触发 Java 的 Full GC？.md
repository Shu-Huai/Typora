# 什么情况下会触发 Java 的 Full GC？

## 回答重点

Full GC 的触发场景可以归纳为六种：

1. 老年代空间不足。这是最常见的触发原因。Young GC 后存活对象要晋升到老年代，老年代装不下就只能 Full GC 腾空间。

2. 元空间不够用。Java 8 之后永久代被元空间取代，类的元数据存在元空间里。如果加载的类太多，元空间设置的上限又不够大，也会触发 Full GC。

3. 显式调用 `System.gc()` 或者执行 `jmap -dump` 命令。虽然 `System.gc()` 只是建议 JVM 回收，不保证立即执行，但大多数情况下 JVM 会响应这个请求。

4. 空间分配担保失败。Young GC 前 JVM 会检查老年代剩余空间够不够装下年轻代所有对象。如果不够且担保失败，就直接触发 Full GC。

5. 晋升失败。Survivor 区装不下存活对象，需要往老年代塞，但老年代也满了，这时候就是 **Promotion Failed**，接着就是 Full GC。

6. 悲观策略触发。每次 Young GC 前，JVM 会统计历史晋升数据。如果发现平均晋升大小比老年代剩余空间还大，直接跳过 Young GC，先来一次 Full GC。

![](Z:/Public/images/tA0NfYHe_JZhcM66aXy_mianshiya.webp)

## 扩展知识

### 空间分配担保机制详解

Young GC 之前，JVM 要做一个风险评估。年轻代的存活对象理论上可能全部晋升到老年代，所以先检查老年代最大可用连续空间是否大于年轻代所有对象总和。

如果大于，Young GC 安全执行。如果小于，JVM 会看 `-XX:HandlePromotionFailure` 参数是否允许担保失败。允许的话，再比较老年代剩余空间和历次晋升平均值，够用就冒险执行 Young GC，不够就直接 Full GC。

JDK 6 Update 24 之后，这个参数被废弃，JVM 默认只比较历次平均晋升大小，简化了判断逻辑。

### 如何减少 Full GC

1. 合理设置堆大小。`-Xms` 和 `-Xmx` 设成一样可以避免堆动态扩缩容带来的 Full GC。老年代太小容易满，太大又会拉长单次 Full GC 时间，得根据实际监控数据调整。

2. 增大年轻代比例。年轻代越大，对象在年轻代待的时间越长，晋升到老年代的数量就越少。可以通过 `-XX:NewRatio` 或 `-Xmn` 调整。

3. 排查内存泄漏。如果 Full GC 后老年代使用率依然居高不下，大概率是有对象该释放没释放。用 MAT 或 JProfiler 分析堆 dump，找出泄漏点。

4. 设置合理的元空间大小。`-XX:MetaspaceSize` 设置初始阈值，`-XX:MaxMetaspaceSize` 设置上限。如果应用动态加载类比较多，这两个值要给足。

5. 避免显式调用 `System.gc()`。生产代码里不要写这个，很多框架用 `-XX:+DisableExplicitGC` 直接禁掉。但要注意，如果用了 DirectByteBuffer，禁掉可能会导致堆外内存回收不及时。

### 永久代与元空间

Java 8 把永久代干掉了，类元数据改存到元空间，用的是本地内存而不是堆内存。这样做的好处是不用再纠结永久代该设多大，元空间默认可以自动扩展。

更多细节可以参考：[536. 为什么 Java 8 移除了永久代（PermGen）并引入了元空间（Metaspace）？](https://www.mianshiya.com/bank/1789931432793948162/question/1780933295228350466)

### CMS 的 Concurrent Mode Failure

CMS 收集器有个特殊情况。CMS 的并发清理阶段，应用线程还在跑，新对象还在往老年代分配。如果并发清理来不及腾出空间，老年代被塞满了，就会发生 Concurrent Mode Failure，CMS 降级为 Serial Old 收集器，执行一次 Full GC。

这种情况的停顿时间特别长，因为 Serial Old 是单线程的。解决办法是调低 CMS 启动阈值 `-XX:CMSInitiatingOccupancyFraction`，让 CMS 提前启动，留足并发清理的空间。

## 面试官追问

#### 提问：Full GC 和 Major GC 是一回事吗？

回答：严格来说不是。Major GC 只清理老年代，Full GC 是清理整个堆加元空间。但实际上很多人混用这两个概念，不同收集器的 GC 日志命名也不统一。面试时如果被追问，最好先确认对方的定义。HotSpot 的官方文档里，Full GC 明确包含年轻代、老年代和元空间的回收。

#### 提问：怎么通过 GC 日志判断是不是触发了 Full GC？

回答：看日志里有没有 “Full GC” 字样。用 `-XX:+PrintGCDetails` 打印详细日志，Full GC 会清晰标出来。还可以看回收范围，如果同时出现年轻代和老年代的回收数据，基本就是 Full GC。G1 的日志稍微不同，会标注 “Full GC (Allocation Failure)” 或者 “Full GC (Metadata GC Threshold)”，直接告诉你触发原因。

#### 提问：如果 Full GC 后老年代使用率几乎没下降，说明什么问题？

回答：大概率是内存泄漏。老年代里的对象都是强引用，GC 回收不掉。常见场景是静态集合一直往里塞数据不清理、缓存没有过期策略、监听器注册了没注销。需要用 `jmap -dump` 导出堆快照，用 MAT 分析大对象和引用链，找到泄漏源头。

#### 提问：生产环境 Full GC 停顿太长怎么优化？

回答：首先看用的什么收集器。如果是 Parallel Old，换成 CMS 或 G1 能显著降低停顿。G1 在大堆场景下效果更好。其次检查堆是不是太大，堆越大单次 Full GC 扫描时间越长。如果业务允许，可以把应用拆成多个实例，每个实例堆小一点。还有就是排查是不是有大量 Finalizer 对象，finalize 方法会拖慢回收速度。
