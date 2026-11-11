# Redis 的 ListPack 数据结构是什么？

## 回答重点

ListPack 是 Redis 6.0 引入的**紧凑型序列化结构**，用于替代 ziplist。它按字节连续存储数据，额外元数据少，适合小数据量场景。

Redis 7.0 开始，List、Hash、ZSet 在数据量较小时都使用 ListPack，ziplist 逐步退出底层实现。

ListPack 的整体结构：

1. **Header**：占 6 字节，前 4 字节记录总长度，后 2 字节记录元素数量。
2. **Elements**：多个 element 紧密排列。
3. **结束标记**：末尾使用 `0xFF`。

![ListPack 结构](Z:/Public/images/a8tr0m6N_listpack.drawio_mianshiya.webp)

每个 element 又由三部分组成：`encoding-type`（编码类型）、`element-data`（实际数据）和 `element-tot-len`（前两部分的总长度）。

## 扩展知识

### 为什么用 ListPack 替换 ziplist

ziplist 的每个 `entry` 都保存前一个 `entry` 的长度，用于支持反向遍历。该长度字段是变长的：前一个 `entry` 小于 254 字节时占 1 字节，否则占 5 字节。

假设连续 `entry` 都接近 253 字节，在头部插入一个 260 字节的 `entry` 后，第二个 `entry` 的长度字段需要从 1 字节扩为 5 字节；它的体积变化又可能导致第三个 `entry` 扩容，最终形成连锁更新，最坏时间复杂度达到 $O(N²)$。

![ziplist 连锁更新](Z:/Public/images/tQer0vtL_image_mianshiya.webp)

![ziplist 连锁更新示意](Z:/Public/images/HKBPYXBF_DZCQUd0R78_mianshiya.webp)

### ListPack 如何解决连锁更新

ListPack 的核心改进是：**每个 element 只记录自己的长度，不记录前一个 element 的长度**。

![ListPack element 结构](Z:/Public/images/udzx3DUu_image_mianshiya.webp)

- `encoding-type`：标记整数或字符串，以及具体编码方式。
- `element-data`：保存实际数据。
- `element-tot-len`：记录前两部分的总长度，放在 element 末尾。

反向遍历时，先读取当前 element 末尾的 `element-tot-len`，即可计算当前 element 的起始位置并跳到前一个 element。修改一个 element 只影响自身，不会波及后续元素，因此消除了连锁更新。

### 编码方式

ListPack 使用变长编码压缩数据：

1. 7 位无符号整数：0～127 的整数占 1 字节。
2. 13 位有符号整数：-4096～4095 占 2 字节。
3. 16/24/32/64 位整数：根据数值范围选择编码。
4. 字符串：短字符串使用 6 位长度前缀，长字符串使用 12 位或 32 位长度前缀。

因此小整数和短字符串的存储效率很高。

### 与 ziplist 的性能对比

| 维度 | ziplist | ListPack |
| --- | --- | --- |
| 连锁更新 | 存在，最坏 $O(N²)$ | 不存在 |
| 内存占用 | 略小 | 略大一点 |
| 遍历方向 | 双向 | 双向 |
| 插入复杂度 | 平均 $O(N)$，最坏 $O(N²)$ | $O(N)$ |
| 实现复杂度 | 较复杂 | 更简单 |

ListPack 每个元素都保存自身长度，内存可能比 ziplist 稍大，但换来了稳定的 $O(N)$ 插入性能。

### 什么时候使用 ListPack

Redis 7.0 之后，以下场景在元素较少、单个元素较小时使用 ListPack：

1. **Hash**：field 数量低于 `hash-max-listpack-entries`，且 field/`value` 不超过 `hash-max-listpack-value`。
2. **ZSet**：元素数量低于 `zset-max-listpack-entries`，且元素大小低于 `zset-max-listpack-value`。
3. **List**：quicklist 的每个节点内部使用 ListPack 存储。

默认情况下，`hash-max-listpack-entries` 为 512，`hash-max-listpack-value` 为 64 字节。超过阈值后会自动转为 hashtable 或 skiplist。

相关主题：[Redis 的 Ziplist 和 Quicklist](https://www.mianshiya.com/question/1799677102985125890)

## 面试官追问

### 提问：ListPack 如何支持从后往前遍历？

从末尾的 `0xFF` 开始，读取最后一个 element 的 `element-tot-len`，向前跳过相应字节即可到达该 element 的起点；再继续向前读取上一个 element 的长度字段，以此类推。

### 提问：`element-tot-len` 本身是变长的，如何知道它占几个字节？

它使用类似 UTF-8 的变长编码。每个字节最高位用于标记是否还有后续字节，从后往前读取，直到遇到最高位为 0 的字节即可确定字段边界。

### 提问：Hash 什么时候从 ListPack 转成 hashtable？

只要 field 数量超过 `hash-max-listpack-entries`，或者任意 field/`value` 长度超过 `hash-max-listpack-value`，就会转换。默认阈值分别是 512 和 64 字节。转换后通常不会再退回 ListPack。

### 提问：为什么不直接使用 hashtable？

hashtable 的每个 `entry` 都要保存 `key`、`value` 指针和 `dictEntry` 元数据。对于大量只有几字节的小 field，元数据可能比实际数据还大；ListPack 将数据连续存储，额外开销很小，内存占用可以降低数倍。
