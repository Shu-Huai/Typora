# Java 中的 LinkedHashMap 是什么？

## 回答重点

`LinkedHashMap` 继承自 `HashMap`，在 `HashMap` 的基础上用**双向链表**把所有节点串起来，保证遍历顺序和插入顺序一致。

它有两种排序模式：插入顺序和访问顺序。默认是插入顺序，谁先 `put` 谁在前面；如果构造时把 accessOrder 设为 true，每次 `get` 或 `put` 已存在的 `key` 都会把对应节点挪到链表尾部，最近访问的永远在最后。

![test_compressed.jpg](Z:/Public/images/f62qPixX_test_compressed.webp)

访问顺序模式天然适合做 LRU 缓存，只要继承 `LinkedHashMap` 重写 `removeEldestEntry` 方法，就能在插入新元素时自动淘汰最老的节点。Mybatis 的本地缓存 LruCache 就是这么实现的。

## 扩展知识

### 内部实现剖析

`LinkedHashMap` 把 `HashMap` 的 Node 扩展成了 Entry，加了 before 和 after 两个指针：

![20220219203048.png](Z:/Public/images/20220219203048_mianshiya.webp)

这两个指针把所有节点串成了一条双向链表，结构大概长这样：

![20220219203058.png](Z:/Public/images/20220219203058_mianshiya.webp)

红色的箭头就是 before 和 after 指针。哈希表负责快速定位，双向链表负责维护顺序，两套结构各司其职。

### 钩子方法机制

`HashMap` 在 putVal、removeNode、`get` 这些操作里埋了三个空方法：

![20220219203123.png](Z:/Public/images/20220219203123_mianshiya.webp)

`LinkedHashMap` 重写了这三个方法：

1. `afterNodeAccess`：节点被访问后调用，如果 accessOrder 为 true，就把这个节点挪到链表尾部

2. `afterNodeInsertion`：新节点插入后调用，用来判断是否要移除最老的节点

3. `afterNodeRemoval`：节点删除后调用，同步把它从双向链表里摘掉

拿 `afterNodeInsertion` 来说，它在 `HashMap` 的 `put` 流程最后被调用：

![20220219203133.png](Z:/Public/images/20220219203133_mianshiya.webp)

`LinkedHashMap` 的实现是这样的：

![20220219203142.png](Z:/Public/images/20220219203142_mianshiya.webp)

evict 为 true 且 `removeEldestEntry` 返回 true 时，就会把链表头部最老的节点干掉。

### 基于 `LinkedHashMap` 实现 LRU

默认的 `removeEldestEntry` 直接返回 false，永远不删：

![20220219203154.png](Z:/Public/images/20220219203154_mianshiya.webp)

只要继承 `LinkedHashMap`，把 accessOrder 设为 true，然后重写这个方法，就能实现一个 LRU 缓存：

```java
private static final class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int maxCacheSize;

    LRUCache(int initialCapacity, int maxCacheSize) {
        super(initialCapacity, 0.75F, true); // true 表示按访问顺序排序
        this.maxCacheSize = maxCacheSize;
    }

    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return this.size() > this.maxCacheSize;
    }
}
```

几行代码就搞定了一个线程不安全的 LRU，面试手写 LRU 的时候可以先提这个方案。

![](Z:/Public/images/TnaApnUp_2cSodly4o8_mianshiya.webp)

### 手写 LRU 完整实现

如果面试官要求不用 `LinkedHashMap`，就得自己维护一个 `HashMap` 加双向链表：

```java
public class LRUCache<K,V> {
    class Node<K,V> {
        K key;
        V value;
        Node<K,V> prev, next;
        public Node(){}
        public Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }
    private int capacity;
    private HashMap<K,Node> map;
    private Node<K,V> head;
    private Node<K,V> tail;
    public LRUCache(int capacity) {
        this.capacity = capacity;
        map = new HashMap<>(capacity);
        head = new Node<>();
        tail = new Node<>();
        head.next = tail;
        tail.prev = head;
    }

    public V get(K key) {
        Node<K,V> node = map.get(key);
        if (node == null) {
            return null;
        }
        moveNodeToHead(node);
        return node.value;
    }

    public void put(K key, V value) {
         Node<K,V> node = map.get(key);
       if (node == null) {
            if (map.size() >= capacity) {
                map.remove(tail.prev.key);
                removeTailNode();
            }
            Node<K,V> newNode = new Node<>(key, value);
            map.put(key, newNode);
            addToHead(newNode);
        } else {
            node.value = value;
            moveNodeToHead(node);
        }
    }

    private void addToHead(Node<K,V> newNode) {
        newNode.prev = head;
        newNode.next = head.next;
        head.next.prev = newNode;
        head.next = newNode;
    }

    private void moveNodeToHead(Node<K,V> node) {
        removeNode(node);
        addToHead(node);
    }

    private void removeNode(Node<K,V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void removeTailNode() {
        removeNode(tail.prev);
    }
}
```

核心思路：`HashMap` 负责 $O(1)$ 定位节点，双向链表负责维护访问顺序。`get` 和 `put` 已存在的 `key` 都要把节点挪到头部，淘汰时从尾部删。head 和 tail 是哨兵节点，简化边界处理。

## 面试官追问

#### 提问：`LinkedHashMap` 是线程安全的吗？多线程环境下怎么用？

回答：不是线程安全的，和 `HashMap` 一样。多线程环境可以用 `Collections`.synchronizedMap 包一层，或者直接用 `ConcurrentHashMap`。如果非要保持顺序，可以考虑自己加锁或者用 ConcurrentLinkedHashMap 这种第三方库。

#### 提问：`LinkedHashMap` 遍历的时间复杂度是多少？和 `HashMap` 有什么区别？

回答：`LinkedHashMap` 遍历是 $O(n)$，`n` 是实际元素个数。`HashMap` 遍历也是 $O(n)$，但它要遍历整个桶数组，如果负载因子低、桶很多但元素少，会有很多空桶要跳过。`LinkedHashMap` 直接沿着双向链表走，不会遍历空桶，效率更稳定。

#### 提问：accessOrder 为 true 时，哪些操作会触发节点移动？

回答：`get`、getOrDefault、compute、computeIfPresent、merge 这些读写操作，还有 `put` 已存在的 `key`，都会触发 afterNodeAccess 把节点挪到尾部。单纯的 containsKey 不会触发，因为它只是查有没有，不算“访问”。

#### 提问：为什么 LRU 要用双向链表？单向链表行不行？

回答：不行。删除一个节点需要修改前驱节点的 next 指针，单向链表找前驱得从头遍历，$O(n)$ 复杂度。双向链表直接通过 prev 指针拿到前驱，$O(1)$ 就能删除。LRU 每次 `get` 都要把节点挪到头部，频繁删除再插入，必须用双向链表才能保证整体 $O(1)$。
