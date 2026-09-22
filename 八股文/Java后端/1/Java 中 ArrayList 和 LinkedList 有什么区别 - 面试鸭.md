# Java 中 ArrayList 和 LinkedList 有什么区别？ - 面试鸭 | 2026最新面试题+详细答案解析

## 回答重点

ArrayList 和 LinkedList 最核心的区别就是**底层数据结构不同**，一个是动态数组，一个是双向链表。

ArrayList 底层是一块连续的内存空间，元素挨着存。LinkedList 每个节点包含前驱指针、后继指针和数据本身，节点散落在堆内存各处，靠指针串起来。

![arrayliist.drawio.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/mq7RHaoz_arrayliist.drawio_mianshiya.webp)

性能上的差异：

1）ArrayList 随机访问是 O(1)，因为数组支持下标直接定位，`arr[5]` 底层就是首地址加偏移量，一步到位。但中间插入删除是 O(n)，要把后面的元素整体挪动。

2）LinkedList 随机访问是 O(n)，得从头或从尾一个个遍历过去。但在头尾插入删除是 O(1)，改两个指针就完事。

实际开发中，90% 以上的场景都该用 ArrayList，因为现代 CPU 对连续内存的缓存命中率远高于链表这种跳来跳去的结构。

## 扩展知识

### 内存占用差异

ArrayList 每个元素只存一个对象引用，占 4 字节或 8 字节，取决于是否开启指针压缩。LinkedList 每个节点要存 3 个东西：前驱指针、后继指针、数据引用，再加上对象头，一个节点大概占 24 字节起步。存 100 万个 Integer，ArrayList 大概占 4MB，LinkedList 要 24MB 以上，内存开销差了 6 倍。

### ArrayList 中间插入真的慢吗

很多人背结论说"ArrayList 中间插入是 O(n)"，但实际情况要看具体场景。

数组的 System.arraycopy 是 native 方法，底层用的是 memmove，CPU 对这种连续内存块的批量搬运做了大量优化。测试下来，往一个 10 万元素的 ArrayList 中间插入 1 万次，耗时大概 200ms 左右。同样操作换成 LinkedList，光是定位到中间位置就要遍历 5 万次，实际耗时反而更长。

所以除非是频繁在头部插入删除，否则 ArrayList 的综合性能通常更好。

### LinkedList 实现了 Deque 接口

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/zsY86Swf_L1rIDn8Lf8_mianshiya.webp)

代码示例：

```java
LinkedList<String> deque = new LinkedList<>();
// 当队列用
deque.addLast("task1");
deque.addLast("task2");
String first = deque.removeFirst(); // task1

// 当栈用
deque.push("A");
deque.push("B");
String top = deque.pop(); // B
```

### 迭代器删除的性能陷阱

用 for 循环加 list.remove(i) 删除元素，在 ArrayList 里每删一个都要搬运后面的元素。假设要从 10 万元素里删掉 5 万个，时间复杂度接近 O(n²)。

正确做法是用迭代器：

```java
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    if (shouldRemove(it.next())) {
        it.remove();
    }
}
```

或者 JDK 8 之后直接用 removeIf：

```java
list.removeIf(item -> shouldRemove(item));
```

ArrayList 的 removeIf 内部做了优化，先标记要删的元素，最后批量搬运一次，性能比逐个删除好很多。

### 什么场景该用 LinkedList

说实话，LinkedList 适用场景很少。主要就两个：

1）需要频繁在头部插入删除，比如实现 LRU 缓存时配合 HashMap 使用。

2）已经持有节点引用，可以 O(1) 删除。但 Java 的 LinkedList 没有暴露内部节点，做不到这点。

如果只是需要队列语义，ArrayDeque 性能比 LinkedList 更好，因为它也是基于数组实现的，缓存友好。JDK 官方文档都建议优先用 ArrayDeque 而不是 LinkedList 来实现栈和队列。

### ArrayList 的扩容机制

- [9179. Java ArrayList 的扩容机制是什么？](https://www.mianshiya.com/question/1839515038747066370)

## 面试官追问

#### 提问：你说 ArrayList 中间插入不一定比 LinkedList 慢，能展开讲讲吗？

回答：主要原因是 CPU 缓存的影响。ArrayList 的数据在内存里是连续存放的，访问时缓存命中率高，搬运数据用的 System.arraycopy 也是高度优化的原生方法。LinkedList 虽然插入本身是 O(1)，但首先得定位到插入位置，这个遍历过程是 O(n)，而且每访问一个节点就可能触发一次缓存缺失。实测在中间位置插入大量数据，ArrayList 往往比 LinkedList 更快。只有在头部频繁插入删除时，LinkedList 才有优势。

#### 提问：为什么 JDK 官方建议用 ArrayDeque 而不是 LinkedList 实现栈和队列？

回答：ArrayDeque 底层是循环数组，内存连续，CPU 缓存友好。LinkedList 每个节点散落在堆的各个位置，访问时缓存命中率低。另外 ArrayDeque 没有 LinkedList 那么多的指针开销，内存占用也更小。除非需要存 null 值，否则 ArrayDeque 各方面都更优。

#### 提问：ArrayList 和 Vector 有什么区别？

回答：Vector 是 JDK 1.0 就有的老古董，所有方法都加了 synchronized，线程安全但性能差。ArrayList 是 JDK 1.2 引入的，不加锁，性能更好。现在基本没人用 Vector 了，需要线程安全的 List 可以用 Collections.synchronizedList 包装 ArrayList，或者用 CopyOnWriteArrayList。
...
