# Redis 中的 Ziplist 和 Quicklist 数据结构的特点是什么？

## 回答重点

**Ziplist** 是一块连续内存，将所有元素紧凑排列，节省内存，但不适合大量数据。

**Quicklist** 是 Redis 3.2 之后 List 的默认实现，本质是双向链表连接多个小 Ziplist，在内存利用率和操作性能之间取得平衡。

Ziplist 的布局为：`zlbytes`（总字节数）、`zltail`（尾节点偏移）、`zllen`（节点数量）、多个 `entry`，最后以 `zlend`（`0xFF`）结束。每个 `entry` 包含：

- `prev_entry_length`：前一个节点长度，用于反向遍历。
- `encoding`：当前节点的数据类型和长度。
- `content`：实际数据。

![Ziplist 结构](Z:/Public/images/0I8lKBz2_image_mianshiya.webp)

Ziplist 的问题是连锁更新：前一个节点变大后，后续 `entry` 的 `prev_entry_length` 可能从 1 字节扩展到 5 字节，导致后面的节点不断移动，极端情况下整条 Ziplist 都要重写。Quicklist 将数据拆成多个小 Ziplist，连锁更新最多影响一个小节点。

## 扩展知识

### Ziplist 的应用

Redis 3.2 之前，小规模 List 和 Hash 会使用 Ziplist：

- List 元素少于 512 个且每个元素小于 64 字节。
- Hash 键值对少于 512 对且每个 `key`/`value` 小于 64 字节。

相关配置：

```text
list-max-ziplist-entries 512
list-max-ziplist-value 64
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
```

超过阈值后，List 和 Hash 会升级为更适合大数据量的结构。

### Quicklist 的设计细节

Quicklist 是双向链表，但每个链表节点存放一整个 Ziplist，而不是单个元素。这样既保留链表节点操作的灵活性，又利用 Ziplist 的紧凑存储。

Redis 还支持对 Quicklist 中间节点使用 LZF 压缩，因为两端访问频繁、中间节点访问较少。

![Quicklist 结构](Z:/Public/images/dCNHJ06V_image_mianshiya.webp)

配置示例：

```text
list-max-ziplist-size -2
list-compress-depth 0
```

`list-max-ziplist-size` 控制每个节点的大小：正数表示最大元素数，`-1` 表示 4KB，`-2` 表示 8KB（默认），`-3/-4/-5` 表示 16KB/32KB/64KB。`list-compress-depth` 控制两端保留多少个不压缩节点。

![Quicklist 压缩](Z:/Public/images/Q4zCw9Vq_l2M0ZRsBc8_mianshiya.webp)

### Redis 7.0 的 Listpack

Redis 7.0 引入 Listpack 逐步替代 Ziplist。Listpack 不再记录前一个节点的长度，而是记录自身长度，从根本上避免了 Ziplist 的连锁更新。现在小数据量的 Hash、Set、Sorted Set，以及 Quicklist 内部节点，都可能使用 Listpack。

### 为什么不直接用普通链表

普通双向链表每个节点需要两个指针，64 位系统通常占 16 字节。如果元素本身只有几个字节，指针开销反而超过数据。Quicklist 将多个元素集中存储，能显著降低指针和节点管理开销。

### Ziplist 与 Quicklist 对比

| 特性 | Ziplist | Quicklist |
| --- | --- | --- |
| 内存布局 | 单块连续内存 | 双向链表 + 多个小 Ziplist |
| 内存利用率 | 很高 | 较高 |
| 随机访问 | $O(N)$ | 节点定位后仍需遍历 |
| 连锁更新 | 可能影响整条列表 | 通常限制在单个小节点 |
| 适用场景 | 少量小元素 | 较大 List、兼顾性能与内存 |

## 面试官追问

#### 提问：Ziplist 的连锁更新具体怎么发生？

回答：每个节点用 1～5 字节记录前一个节点长度。当前一个节点从小于 254 字节变成至少 254 字节时，后续节点的 `prevlen` 需要从 1 字节扩展到 5 字节；节点变长又可能触发下一个节点扩展，最终形成连锁反应。

#### 提问：Quicklist 中间节点压缩用什么算法？

回答：使用 LZF。它压缩和解压速度快、压缩率适中，适合中间节点访问较少但偶尔仍需快速解压的场景。

#### 提问：Ziplist 查找某个元素的时间复杂度是多少？

回答：$O(N)$。Ziplist 本质是紧凑的顺序结构，没有索引，查找元素只能从头遍历 `entry`，因此只适合少量数据。
