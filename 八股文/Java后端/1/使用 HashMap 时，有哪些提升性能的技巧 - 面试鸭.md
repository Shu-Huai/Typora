# 使用 HashMap 时，有哪些提升性能的技巧？ - 面试鸭 | 2026最新27 届校招 Java 热题+详细答案解析

## 回答重点

提升 HashMap 性能，核心就俩字：**少扩容、少冲突**。

1）初始容量一定要给够

业务代码尽量别写 `new HashMap<>()`，而是 `new HashMap<>((int)((size/0.75f)+1))`，size 是业务上能预估的最大元素数。HashMap 默认初始容量才 16，你往里塞 10 万条数据，得扩容十几次，每次扩容都是 O(n) 的全量 rehash，性能很差。

2）负载因子别乱调

默认负载因子 0.75 是官方精心调的，时间复杂度和空间利用率的最佳平衡点。调低了虽然冲突少、查得快，但内存占用会飙上去；调高了省内存但冲突概率上升，查找性能下降。没有特殊场景，就用默认的。

3）确保 hashCode 均匀分布

key 的 hashCode() 方法生成的哈希值必须均匀分布，不然大量 key 都落到同一个槽位上，链表或红黑树会变得很长，查找效率从 O(1) 退化到 O(n)（链表）或 O(log n)（红黑树）。

![map.drawio.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/pCVu6MfP_map.drawio_mianshiya.webp)

还有个遍历场景值得注意：优先用 entrySet 或 keySet

错误写法：

```java
for (String key : map.keySet()) {
    Object v = map.get(key); // 这里会再次 hash，一次 keySet + 一次 get
}
```

推荐写法：

```java
for (Map.Entry<String, Object> entry : map.entrySet()) {
    var k = entry.getKey();
    var v = entry.getValue(); // 不需要再次 hash
}
```

## 扩展知识

### rehash 的代价到底有多大

每次扩容 HashMap 会新建一个 2 倍大的数组，然后把所有旧 entry 重新计算位置放到新表里。这个过程是 O(n) 的，如果一开始容量给小了，插入 10 万条数据会触发 log₂(100000/16) ≈ 13 次扩容，每次扩容都要遍历整个表，累计下来性能损耗非常可观。

### JDK 8 的 rehash 优化

JDK 7 扩容时每个元素都要重新计算 hash 定位，JDK 8 做了个巧妙的优化：因为数组长度是 2 的幂次，扩容为 2 倍后，元素的新位置只有两种可能，要么在原位置，要么在原位置 + 老数组长度。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/T51qBTiv_yR0gJU3Vjb_mianshiya.webp)

这样一来，链表中的元素可以直接通过位运算判断该去哪，不用每个都重新取模，计算开销大大减少。

详细看：

- [451. Java 中 HashMap 的扩容机制是怎样的？](https://www.mianshiya.com/question/1780933294750199809)

### 什么时候该用其他 Map 实现

场景推荐实现原因需要保持插入顺序LinkedHashMap内部维护双向链表，遍历顺序和插入顺序一致需要按 key 排序TreeMap底层红黑树，key 天然有序高并发读写ConcurrentHashMap分段锁/CAS，线程安全且性能好key 是枚举类型EnumMap底层数组直接按枚举序号定位，极快

### 容量计算的坑

很多人直接 `new HashMap<>(100)` 以为容量就是 100，其实 HashMap 会把它向上取整到最近的 2 的幂次，也就是 128。然后 128 * 0.75 = 96，插入第 97 个元素就触发扩容了。

正确做法是用 Guava 的 `Maps.newHashMapWithExpectedSize(100)` 或者自己算 `(int)(100/0.75f)+1`，确保实际元素数不会触发扩容。

## 面试官追问

#### 提问：你说初始容量要给够，那给太大会有什么问题？

回答：主要是内存浪费。HashMap 创建时就会分配数组空间，如果业务只存 100 个元素你给了 10 万的容量，这块内存就白占着了。另外数组太大还可能影响 CPU 缓存命中率，遍历时性能反而下降。所以容量要根据实际业务量来估，不是越大越好。

#### 提问：ConcurrentHashMap 和 Collections.synchronizedMap 有什么区别？

回答：synchronizedMap 就是给所有方法套了一把大锁，任何操作都互斥，高并发下性能很差。ConcurrentHashMap 在 JDK 7 用分段锁把数据分成 16 个 Segment，不同段可以并发操作；JDK 8 改成 CAS + synchronized 锁单个桶，粒度更细，并发度更高。实际场景下 ConcurrentHashMap 吞吐量能比 synchronizedMap 高好几倍。

#### 提问：为什么 HashMap 的容量必须是 2 的幂次？

>

详细解答可以看：[为什么 HashMap 在 Java 中扩容时采用 2 的 n 次方倍？](https://www.mianshiya.com/question/1780933294754394113)

回答：为了用位运算替代取模。定位桶的公式是 `(n-1) & hash`，n 是 2 的幂次时，n-1 的二进制全是 1，这时候 `& hash` 等价于 `hash % n`，但位运算比取模快得多。另外扩容时也能利用这个特性快速判断元素该去哪，不用重新计算 hash。 ...
