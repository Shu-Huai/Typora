# 为什么 Redis Zset 用跳表实现而不是红黑树？B+树？

## 回答重点

Redis 的 ZSet 选择跳表，主要因为实现简单、范围查询高效，并且索引层级灵活可调。

### 为什么不用红黑树？

1. **实现简单**：跳表是多层有序链表，通过随机概率生成索引，不需要维护旋转和颜色平衡；红黑树的插入、删除需要复杂的旋转和重新着色。
2. **范围查询高效**：ZSet 常用 `ZRANGE`、`ZREVRANGE`。跳表定位到起点后，可沿底层链表顺序遍历；红黑树进行范围查询通常需要中序遍历，访问路径不如链表直观。
3. **结构灵活**：跳表层数由概率动态决定，可以随数据规模调整；红黑树结构相对固定。

![跳表与平衡树](Z:/Public/images/OiykrqFQ_LDR9sm7oNi_mianshiya.webp)

### 为什么不用 B+ 树？

B+ 树主要为磁盘场景设计，放在 Redis 的纯内存场景中优势不明显：

1. 插入、删除需要处理节点分裂、合并和重新平衡，复杂度高于跳表。
2. B+ 树高扇出的核心价值是减少磁盘 I/O 和寻道次数，而 Redis 数据都在内存中，不需要这种优化。

## 扩展知识

### 跳表的核心原理

跳表本质上是带多级索引的有序链表。最底层保存全部元素，上层是逐级稀疏的快速通道。查找时从最高层开始，能向右就向右，无法继续时下降一层，平均时间复杂度为 $O(\log N)$。

![跳表查找示例](Z:/Public/images/HRBQFRMh_4DHdDJYvQ1_mianshiya.webp)

### Redis 跳表的实现细节

1. 最大层数通常为 32 层。
2. 节点升层概率为 1/4，而不是教材常见的 1/2，以获得更稀疏的索引并节省内存。
3. 底层链表是双向链表，节点维护 `backward` 指针，支持 `ZREVRANGE` 反向遍历。
4. 节点保存 `score`、`member` 和 `span`。`span` 用于累计跨度，从而支持 `ZRANK` 的 $O(\log N)$ 查询。

Redis 作者认为，跳表通过调整节点升层概率可以控制内存占用；ZSet 经常执行 `ZRANGE`/`ZREVRANGE`，底层链表遍历的缓存局部性并不差；同时跳表更容易实现、调试和扩展。

### 小数据量时的底层结构

ZSet 并非始终使用跳表。数据量较小时使用紧凑的 ziplist（Redis 7.0 之后为 listpack）：元素数量不超过 `zset-max-ziplist-entries`（默认 128），且每个元素不超过 `zset-max-ziplist-value`（默认 64 字节）时，优先使用该结构。超过阈值后才转换为跳表。

### 跳表与其他实现的区别

Java 的 `ConcurrentSkipListMap` 需要通过 CAS 等机制处理并发；Redis 命令执行主要由单线程完成，因此跳表不需要并发控制。`ConcurrentSkipListMap` 按 `key` 排序，而 Redis 跳表按 score 排序，并额外维护 `span` 用于计算排名。

相关主题：

- [Redis 中跳表的实现原理是什么？](https://www.mianshiya.com/question/1780933295597449217)
- [为什么 JDK 1.8 对 `HashMap` 进行了红黑树的改动？](https://www.mianshiya.com/question/1780933294771171329)
- [说说平衡树的基本实现，与红黑树的区别是什么？](https://www.mianshiya.com/question/1834502383884423170)

## 面试官追问

### 提问：ZSet 底层只使用跳表吗？

不是。小数据量使用 ziplist 或 listpack，元素数量和单元素大小超过阈值后才转换为跳表，同时通常还会维护哈希表以便根据 member 快速定位。

### 提问：跳表层数如何决定？为什么 Redis 使用 1/4 概率？

节点插入时从第一层开始，以固定概率决定是否继续升层，直到停止或达到最大层数。Redis 使用 1/4 可以让索引更稀疏、节省内存；虽然查找路径略长，但整体权衡更适合 Redis。

### 提问：ConcurrentSkipListMap 与 Redis 跳表有什么区别？

ConcurrentSkipListMap 面向多线程并发，使用 CAS 保证线程安全；Redis 是单线程执行命令，跳表实现更简单。此外 Java 结构按 `key` 排序，而 Redis 按 score 排序，并维护 `span` 计算排名。
