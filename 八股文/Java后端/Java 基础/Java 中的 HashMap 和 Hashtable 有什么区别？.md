# Java 中的 HashMap 和 Hashtable 有什么区别？

## 回答重点

`HashMap` 和 `Hashtable` 最核心的区别就是**线程安全性**。`Hashtable` 的方法都加了 synchronized，是线程安全的，但代价是性能差；`HashMap` 没加锁，单线程下跑得快，但多线程环境得自己保证同步。

其他几个关键区别：

1. 对 null 的处理不一样。`HashMap` 允许一个 null 键和多个 null 值，`Hashtable` 不让存 null，往里塞就抛 NullPointerException

2. 继承体系不同。`HashMap` 继承 AbstractMap，是正经的 Map 实现；`Hashtable` 继承的是古早的 Dictionary 类，虽然后来也实现了 Map 接口，但 Dictionary 早就被标记废弃了

3. 迭代器机制有差别。`HashMap` 用的是 fail-fast 的 Iterator，迭代时改结构直接抛 ConcurrentModificationException；`Hashtable` 用的 Enumerator 是弱一致性的，改了也不一定报错

![](Z:/Public/images/ubCkAhZ2_zsWbaY4Ctg_mianshiya.webp)

## 扩展知识

### `Hashtable` 为什么被淘汰

`Hashtable` 是 JDK 1.0 就有的老古董，那时候 Java 还没有完整的集合框架。它用的是全局锁，意思就是不管你读还是写，不管操作的是哪个桶，所有线程都得排队抢同一把锁。10 个线程同时来，9 个得干等着，并发性能可想而知。

到了 JDK 1.2，Java 引入了 `Collections` Framework，`HashMap` 作为新生代替补上场。再到 JDK 1.5，Doug Lea 贡献了 `ConcurrentHashMap`，用分段锁把并发性能拉满，`Hashtable` 彻底没了存在的必要。

### `ConcurrentHashMap` 凭什么取代 `Hashtable`

`ConcurrentHashMap` 的核心思路是把锁的粒度做细。JDK 1.7 用的是分段锁，把整个 Map 分成 16 个 Segment，每个 Segment 独立加锁，理论上能支持 16 个线程同时写不同的段。

JDK 1.8 更激进，直接干掉了 Segment，改用 CAS + synchronized 锁单个桶。读操作完全不加锁，写操作只锁当前桶的头节点，锁粒度从“段”细化到了“桶”，并发度直接拉到数组长度级别。

详细看：

- [461. Java 中 `ConcurrentHashMap` 1.7 和 1.8 之间有哪些区别？](https://www.mianshiya.com/question/1780933294813114369)

### 三者对比

| 特性 | `HashMap` | `Hashtable` | `ConcurrentHashMap` |
| --- | --- | --- | --- |
| 线程安全 | 否 | 是 | 是 |
| 锁机制 | 无 | 全局 `synchronized` | CAS + 桶级锁 |
| `null` 键值 | 允许 | 不允许 | 不允许 |
| 性能 | 最高 | 最低 | 高并发下最优 |
| 推荐场景 | 单线程 | 不推荐使用 | 多线程 |

### 为什么 `ConcurrentHashMap` 也不允许 null

这是 Doug Lea 故意设计的。在并发场景下，`get` 返回 null 有歧义：到底是 `key` 不存在，还是 `value` 本身就是 null？单线程可以用 containsKey 再查一遍，但并发环境下两次调用之间状态可能变了，判断结果不可靠。所以干脆禁止 null，从根源上杜绝这种二义性。

### `ConcurrentHashMap` 相关面试题

- [461. Java 中 `ConcurrentHashMap` 1.7 和 1.8 之间有哪些区别？](https://www.mianshiya.com/bank/1788408712975282177/question/1780933294813114369)

- [462. Java 中 `ConcurrentHashMap` 的 `get` 方法是否需要加锁？](https://www.mianshiya.com/bank/1788408712975282177/question/1780933294829891585)

- [463. 为什么 Java 的 `ConcurrentHashMap` 不支持 `key` 或 `value` 为 null？](https://www.mianshiya.com/bank/1788408712975282177/question/1780933294834085890)

## 面试官追问

#### 提问：你刚才说 `HashMap` 不是线程安全的，那多线程环境下用 `HashMap` 会出什么问题？

回答：最典型的就是 JDK 1.7 的死循环问题。扩容时如果两个线程同时触发 `rehash`，链表迁移可能形成环，后续 `get` 操作会无限循环，CPU 直接打满。JDK 1.8 改成尾插法解决了成环问题，但多线程同时 `put` 还是会丢数据，两个线程算到同一个桶位置，后写的直接覆盖先写的。

#### 提问：既然 `ConcurrentHashMap` 这么好用，为什么不干脆把 `HashMap` 也做成线程安全的？

回答：没必要，单线程场景下加锁纯粹是浪费。每次操作都要获取释放锁，就算是无竞争的 CAS 也有开销。大多数业务场景是单线程局部使用，`HashMap` 不加锁跑得最快。真需要并发就用 `ConcurrentHashMap`，各司其职。

#### 提问：`Collections`.synchronizedMap 和 `ConcurrentHashMap` 有什么区别？

回答：synchronizedMap 本质上是给 `HashMap` 套了一层 synchronized 包装，跟 `Hashtable` 一样的全局锁，并发性能很差。`ConcurrentHashMap` 是从数据结构层面重新设计的，锁粒度细到桶级别，读操作无锁，吞吐量完全不是一个量级。另外 synchronizedMap 的迭代器也不是线程安全的，遍历时还得自己在外面加锁。
