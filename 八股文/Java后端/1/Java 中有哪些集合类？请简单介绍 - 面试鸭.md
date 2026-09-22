# Java 中有哪些集合类？请简单介绍 - 面试鸭 | 2026最新Java 热门面试题 200 道+详细答案解析

## 回答重点

Java 集合框架分两大阵营：**Collection** 和 **Map**。Collection 存单个元素，Map 存键值对。

![20220219202800.png](https://pic.code-nav.cn/mianshiya/question_picture/1783397053004488705/20220219202800_mianshiya.webp)

Collection 下面又分三条线：

1）List：有序可重复，按下标访问。ArrayList 底层是数组，查询快增删慢；LinkedList 底层是双向链表，增删快查询慢；Vector 是线程安全版的 ArrayList，现在基本没人用了

2）Set：不允许重复元素。HashSet 基于哈希表，元素无序；LinkedHashSet 用链表维护插入顺序；TreeSet 基于红黑树，元素按大小排序。网上说 Set 是无序集合其实不准确，TreeSet 就是有序的

3）Queue：队列，先进先出。PriorityQueue 是优先级队列，按元素大小出队；LinkedList 也实现了 Queue 接口，可以当普通队列用

![kuoronglist.drawio1.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/F5nZIdVO_kuoronglist.drawio1_mianshiya.webp)

Map 这边：

![20220219202845.png](https://pic.code-nav.cn/mianshiya/question_picture/1783397053004488705/20220219202845_mianshiya.webp)

1）HashMap 最常用，基于哈希表，键值对无序，key 不能重复，允许 null 键和 null 值

2）LinkedHashMap 维护插入顺序，遍历时按放入顺序输出

3）TreeMap 基于红黑树，key 按大小排序

4）Hashtable 是远古时代的线程安全 Map，不允许 null，现在被 ConcurrentHashMap 替代了

5）ConcurrentHashMap 是高并发场景的首选，分段锁设计，性能比 Hashtable 强很多

>

这题一般会在面试刚开始的时候被问，主要用于暖场热身，不需要说的那么详细，大致讲下，面试官会根据你回答的点继续挖的。

可尝试结合类图，对常见的实现类关系重点记忆，面试时可对自己擅长的实现类详细介绍或引导，也可做一定的取舍。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1816450440005341186/pLwh6DJV_image_mianshiya.webp)

## 扩展知识

### 集合框架的设计思路

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/OQqcdTTg_5UOCHlLTzy_mianshiya.webp)

### 为什么 Map 不继承 Collection

很多人觉得 Map 也应该属于 Collection，但实际上它们的数据模型完全不同。Collection 存的是单个元素，核心操作是 add、remove；Map 存的是键值对，核心操作是 put、get。如果硬把 Map 塞进 Collection，那 add 方法传什么参数？传 key 还是传 value 还是传 Entry？语义上就说不通。

不过 Map 提供了三个视图方法：keySet 返回所有 key 的 Set，values 返回所有 value 的 Collection，entrySet 返回所有键值对的 Set。通过这些视图，Map 也能用 Collection 的方式遍历。

### 线程安全的选择

早期 Java 提供了 Vector 和 Hashtable 两个线程安全的集合，但它们是在每个方法上加 synchronized，锁粒度太粗，多线程下性能很差。

后来 Collections 工具类提供了 synchronizedList、synchronizedMap 这些包装方法，本质上还是在方法上加锁，性能没啥改进。

JDK 5 引入了 java.util.concurrent 包，ConcurrentHashMap 用分段锁，CopyOnWriteArrayList 用写时复制，ConcurrentLinkedQueue 用 CAS 无锁算法，才算真正解决了并发集合的性能问题。

### 选型速查

场景推荐实现原因随机访问多ArrayList数组下标访问 O(1)频繁增删LinkedList链表增删 O(1)，但要先定位去重不要求顺序HashSet哈希表查找 O(1)去重要保持顺序LinkedHashSet哈希表 + 链表需要排序TreeSet / TreeMap红黑树，O(log n)键值映射HashMap最常用，性能好高并发读写ConcurrentHashMap分段锁，线程安全且快

## 面试官追问

#### 提问：ArrayList 和 LinkedList 到底该怎么选？

>

详细解答可以看：[Java 中 ArrayList 和 LinkedList 有什么区别？](https://www.mianshiya.com/question/1839516705798356994)

回答：90% 的情况选 ArrayList。虽然教科书上说 LinkedList 插入删除快，但实际上 ArrayList 移动元素用的是 System.arraycopy，这是 native 方法，底层做了优化，拷贝起来比想象中快得多。再加上 CPU 缓存友好性，ArrayList 在大多数场景下都更快。LinkedList 唯一的优势是当队列用，频繁操作头部，但这种场景用 ArrayDeque 更好。

#### 提问：HashMap 什么时候会退化成链表？

>

详细解答可以看：[为什么 JDK 1.8 对 HashMap 进行了红黑树的改动？](https://www.mianshiya.com/question/1780933294771171329)

回答：当大量 key 的 hashCode 冲突，都落到同一个桶里，就会形成长链表，查找复杂度从 O(1) 退化到 O(n)。JDK 8 做了优化，当链表长度超过 8 且数组长度超过 64，会把链表转成红黑树，查找复杂度变成 O(log n)。当元素被删到 6 个以下，又会退化回链表。

#### 提问：ConcurrentHashMap 和 Hashtable 都是线程安全的，有什么区别？

>

详细解答可以看：[ConcurrentHashMap 和 Hashtable 的区别是什么？](https://www.mianshiya.com/question/1854745940761190402)

回答：锁粒度不一样。Hashtable 是整个表一把大锁，同一时刻只有一个线程能操作。ConcurrentHashMap 在 JDK 7 用分段锁，把表分成 16 个段，不同段可以并发操作；JDK 8 改成 synchronized + CAS，锁的粒度细到单个桶，并发度更高。另外 Hashtable 不允许 null 键和 null 值，ConcurrentHashMap 也不允许，但 HashMap 允许。 ...
