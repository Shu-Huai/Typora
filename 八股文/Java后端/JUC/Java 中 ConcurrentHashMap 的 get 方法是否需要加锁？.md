# Java 中 ConcurrentHashMap 的 get 方法是否需要加锁？

## 回答重点

**不需要加锁**。`ConcurrentHashMap` 的 `get` 方法完全依赖 volatile 语义来保证线程安全，读取时能拿到最新的数据，不会有并发问题。

具体实现上，数组元素的读取用的是 `Unsafe#getObjectVolatile`，Node 节点的 val 和 next 指针也被 volatile 修饰，这三个关键点保证了整个读取链路的可见性。

`get` 流程分三步：

1. 通过 hash 定位数组下标，用 `getObjectVolatile` 读取数组槽位

2. 如果有 hash 冲突，沿着 `next` 指针遍历链表，`next` 是 `volatile` 的

3. 找到目标节点后读取 `val`，`val` 也是 `volatile` 的

![](Z:/Public/images/xOY3HDVn_ss44uFXOVn_mianshiya.webp)

## 扩展知识

### 写时加锁，读时无锁

写操作如 `put` 和 `remove` 需要加锁来保证一致性，但 `get` 操作完全不需要锁。这种读写分离的设计让读操作不会阻塞写操作，并发性能比 `Hashtable` 高出一个量级。在读多写少的场景下，比如缓存系统，这个优势非常明显。

### `get` 方法源码分析

![image.png](Z:/Public/images/lctBikgm_image_mianshiya.webp)

核心定位逻辑在 `e = tabAt(tab, (n - 1) & h)) != null` 这行。tabAt 内部调用的是 `Unsafe#getObjectVolatile` 来保证可见性。

![image.png](Z:/Public/images/aIl2YPR8_image_mianshiya.webp)

getObjectVolatile 是个 native 方法，底层通过 JNI 调用 C++ 实现。

![image.png](Z:/Public/images/8zT0Nnmz_image_mianshiya.webp)

它的原理是根据对象起始地址加上字段偏移量，直接从内存读取值。关键在于它会插入**内存屏障**：读取前后各插入一个 load barrier，确保不会读到 CPU 缓存里的旧值，从而实现 volatile 语义。

Node 节点的 val 和 next 指针也被 volatile 修饰：

![image.png](Z:/Public/images/gsndtATm_image_mianshiya.webp)

整个 `get` 流程里，不管是定位数组槽位、遍历链表还是取 val 值，每一步都有 volatile 保证可见性，所以压根不需要加锁。

### Unsafe 类

Unsafe 是 Java 提供的一个内部类，从名字就能看出它是用来执行“不安全”操作的，提供了**直接操作内存和线程**的能力。

![](Z:/Public/images/UFZa94oU_JgrQatT27G_mianshiya.webp)

`ConcurrentHashMap`、`AtomicInteger`、`LockSupport` 这些并发工具底层都依赖 Unsafe。不过 Unsafe 属于 sun.misc 包，官方不建议业务代码直接用，JDK 9 之后访问限制更严格了。

## 面试官追问

#### 提问：既然 `get` 不加锁，那 `put` 的时候 `get` 会不会读到中间状态？

回答：不会。`put` 操作是先构造好新的 Node 节点，最后一步才用 CAS 把节点挂到数组或链表上。这个“挂载”动作是原子的，`get` 要么读到旧值，要么读到完整的新节点，不存在读到“半成品”的情况。

#### 提问：`ConcurrentHashMap` 的 `size` 方法是准确的吗？

回答：不保证精确。因为 `size` 统计的时候没有加全局锁，统计过程中可能有其他线程在增删元素。返回的是一个“近似值”，在高并发场景下会有偏差。如果业务需要精确计数，得自己维护一个 `AtomicLong` 计数器。

#### 提问：为什么数组元素不直接用 volatile 修饰，而要用 Unsafe 来读？

回答：Java 的 volatile 只能修饰变量，没法修饰数组的某个元素。`volatile Node[] table` 只能保证 table 引用本身的可见性，但 table[`i`] 这个元素的可见性它管不了。所以只能借助 Unsafe 的 getObjectVolatile 来实现对数组元素的 volatile 读。
