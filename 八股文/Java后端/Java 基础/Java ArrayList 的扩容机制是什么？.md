# Java ArrayList 的扩容机制是什么？

## 回答重点

`ArrayList` 底层是个 Object 数组，当元素塞满了就得扩容。默认初始容量是 10，扩容时新容量是原来的 **1.5 倍**，计算公式是 `oldCapacity + (oldCapacity >> 1)`。

扩容流程：

- `add` 元素时检查容量是否够用

- 如果不够，计算新容量 = 老容量 * 1.5

- 创建新数组，调用 `Arrays.copyOf()` 把老数据拷过去

- elementData 指向新数组

![kuoronglist.drawio.png](Z:/Public/images/nORww4hv_kuoronglist.drawio_mianshiya.webp)

扩容的核心代码：

```java
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1); // 1.5倍
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

举个例子：初始容量 10，塞第 11 个元素时扩到 15，塞第 16 个时扩到 22，塞第 23 个时扩到 33，以此类推。

## 扩展知识

### 扩容的性能开销

每次扩容都要新建数组然后把老数据全拷一遍，这是 $O(n)$ 的操作。如果一开始容量给小了，从默认容量 10 开始，扩容到能容纳 100 万元素可能需要约 29 次扩容，累计下来性能损耗非常可观。

实际开发中如果能预估数据量，一定要用带参构造函数：

```java
// 预计存 1000 个元素，直接给 1000
List<Integer> list = new ArrayList<>(1000);
```

这样能避免扩容开销，内存也能一次分配到位。

### 为什么是 1.5 倍不是 2 倍

选 1.5 倍是时间和空间的折中。2 倍扩容次数少但太浪费内存，1.5 倍既能减少扩容次数，又不会让内存利用率太低。另外有个有意思的点：1.5 倍扩容时，老数组释放后的内存加上一些零碎空间，往往刚好能容纳新数组，减少内存碎片。

![](Z:/Public/images/h6K9QTEl_5rojsqdw01_mianshiya.webp)

### `ArrayList` 和 `LinkedList` 扩容对比

| 特性 | `ArrayList` | `LinkedList` |
| --- | --- | --- |
| 底层结构 | 数组 | 双向链表 |
| 是否需要扩容 | 需要，1.5 倍 | 不需要，动态增长 |
| 随机访问 | `O(1)`，数组下标直接定位 | `O(n)`，要从头遍历 |
| 尾部插入 | 均摊 `O(1)`，扩容时 `O(n)` | `O(1)`，改指针就行 |
| 中间插入 | `O(n)`，要搬移后面的元素 | `O(n)`，要先找到位置 |
| 内存占用 | 连续内存，有预留空间 | 每个节点额外存两个指针 |

大部分场景用 `ArrayList` 就够了，随机访问快，CPU 缓存命中率高。只有频繁在头部或中间插入删除的场景才考虑 `LinkedList`。

### 源码细节

`add` 方法会先调 ensureCapacityInternal 检查容量：

```java
public boolean add(E e) {
    ensureCapacityInternal(size + 1);  // 检查是否需要扩容
    elementData[size++] = e;
    return true;
}
```

ensureCapacityInternal 内部判断是否需要扩容：

```java
private void ensureExplicitCapacity(int minCapacity) {
    modCount++;  // 修改次数+1，用于快速失败机制
    if (minCapacity - elementData.length > 0)
        grow(minCapacity);
}
```

minCapacity 是所需的最小容量，一般就是 `size` + 1。如果当前数组装不下了，就调 grow 扩容。

还有个边界处理：如果新容量超过 MAX_ARRAY_SIZE，会调 hugeCapacity 兜底：

```java
private static int hugeCapacity(int minCapacity) {
    if (minCapacity < 0) // 溢出了
        throw new OutOfMemoryError();
    return (minCapacity > MAX_ARRAY_SIZE) ?
        Integer.MAX_VALUE :
        MAX_ARRAY_SIZE;
}
```

MAX_ARRAY_SIZE 是 Integer.MAX_VALUE - 8，预留 8 个数组槽位（元素位置）是因为某些 JVM 实现会在数组头部存一些元数据。

### JDK 版本差异

JDK 7 以前，new `ArrayList()` 会立刻分配默认容量 10 的数组。JDK 7 开始改成了懒初始化，new `ArrayList()` 只创建一个空数组，第一次 `add` 时才分配容量 10 的数组。这个优化对创建了 `ArrayList` 但没往里塞数据的场景能省不少内存。

## 面试官追问

#### 提问：`ArrayList` 的 elementData 为什么用 transient 修饰？

回答：因为 elementData 数组的实际长度通常比存储的元素数量大，直接序列化会把那些空位也写进去，浪费空间。`ArrayList` 自己实现了 writeObject 和 readObject 方法，只序列化实际有数据的部分，`size` 是多少就写多少个元素。

#### 提问：`ArrayList` 能存多少个元素？

回答：理论上限是 Integer.MAX_VALUE，大约 21 亿。但实际受 JVM 堆内存限制，每个对象引用在 64 位 JVM 上占 8 字节，不开压缩指针的话光存引用就要 16GB 内存。另外数组头部还有元数据开销，所以实际能存的量取决于你给 JVM 分配多少堆内存。

#### 提问：`Arrays`.copyOf 和 `System`.arraycopy 有什么区别？

回答：`Arrays`.copyOf 内部也是调 `System`.arraycopy，但它会帮你新建目标数组。`System`.arraycopy 是个 native 方法，需要你自己准备好目标数组，性能上两者没区别。用 `Arrays`.copyOf 更方便，用 `System`.arraycopy 更灵活，能指定从哪拷到哪、拷多少。
