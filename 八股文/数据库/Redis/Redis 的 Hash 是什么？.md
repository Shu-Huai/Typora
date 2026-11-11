# Redis 的 Hash 是什么？

## 回答重点

Redis 的 Hash 是一种**键值对集合**，可以在同一个 Redis `key` 下保存多个 field-`value`，适合表示用户、商品等对象的属性。例如使用 `user:1001` 作为 `key`，保存 `name`、`age`、`city` 等字段，修改单个字段时不需要整体覆盖 JSON。

Hash 有两种主要编码：数据量较小时使用紧凑、省内存的 listpack；数据量较大时自动切换为查询效率为 $O(1)$ 的 hashtable。默认字段数超过 512，或任意字段名/值超过 64 字节时会触发切换。

![Redis Hash 结构](Z:/Public/images/eVexIs3Y_hash.drawio_mianshiya.webp)

常用命令：

```shell
HSET user:1001 name "mianshiya" age 18
HGET user:1001 name
HINCRBY user:1001 age 1
```

常见操作还包括 `HMSET` 批量写入、`HMGET` 批量读取、`HDEL` 删除字段，以及 `HINCRBY` 对数值字段进行原子加减。

## 扩展知识

### Hash 底层编码的演进

Redis 6 及之前主要使用 ziplist + hashtable，Redis 7 之后改为 listpack + hashtable。ziplist 和 listpack 都是紧凑型结构，查找复杂度为 $O(N)$，但 listpack 解决了 ziplist 的级联更新问题：ziplist 记录前一个节点的长度，节点变化可能导致后续节点连续更新；listpack 只记录当前节点长度，因此避免了这种连锁开销。

| 参数 | 默认值 | 含义 |
| --- | ---: | --- |
| `hash-max-listpack-entries` | 512 | 字段数上限 |
| `hash-max-listpack-value` | 64 | 单个字段或值的字节上限 |

只要字段数超过 512，或者任意 field/`value` 超过 64 字节，就会从 listpack 转为 hashtable。该转换通常是单向的，不会自动退回 listpack。

![Hash 编码转换](Z:/Public/images/Snipaste_2024-05-15_21-42-23_mianshiya.webp)

### `Hashtable` 的内部结构

`Hashtable` 是标准哈希表，平均查询复杂度为 $O(1)$：

```c
typedef struct dictht {
    dictEntry **table;      // 哈希桶数组
    unsigned long size;     // 哈希表大小
    unsigned long sizemask; // 大小掩码，值是 size-1
    unsigned long used;     // 已使用的节点数
} dictht;

typedef struct dictEntry {
    void *key;              // 键
    union {
        void *val;
        uint64_t u64;
        int64_t s64;
        double d;
    } v;                    // 值，用联合体节省内存
    struct dictEntry *next; // 链表指针，解决哈希冲突
} dictEntry;
```

设计细节：

1. `sizemask` 永远等于 `size - 1`，使用 `hash & sizemask` 计算桶下标，比取模更快。
2. 值使用联合体存储，整数或浮点数可以直接放入，减少指针跳转。
3. 哈希冲突使用链地址法，冲突元素挂在同一桶的链表上。

![Hashtable 结构](Z:/Public/images/Snipaste_2024-05-15_22-27-32_mianshiya.webp)

### 渐进式 `rehash`

Redis 不会一次性完成哈希表扩容，而是分多次渐进迁移。原因是 Redis 命令执行主要由单线程完成，一次搬迁几十万个 `key` 会阻塞其他请求。

![Hash 渐进式 rehash](Z:/Public/images/U1DZgn3d_r0J74EMvoo_mianshiya.webp)

流程如下：

1. 为 `ht[1]` 分配空间，大小取第一个大于等于 `ht[0].used * 2` 的 2 的幂次方。
2. 将 `rehashidx` 从 `-1` 设置为 `0`，标记开始 `rehash`。
3. 每次对 Hash 增删改查时，顺便把 `rehashidx` 对应的桶从 `ht[0]` 搬到 `ht[1]`，然后递增 `rehashidx`。
4. 新数据直接写入 `ht[1]`，查询时同时检查两张表。
5. 搬迁完成后交换 `ht[0]` 和 `ht[1]`，并将 `rehashidx` 重置为 `-1`。

![Hash rehash 过程](Z:/Public/images/fi0youIX_wecom-temp-170726-8d24749bd759fb281def9afc0a25e3f2_mianshiya.webp)

### 扩容和缩容的触发条件

负载因子计算公式为 `used / size`：

- 负载因子 `>= 1` 且当前没有进行 RDB/AOF 持久化时，触发扩容。
- 负载因子 `>= 5` 时，说明冲突严重，无论是否持久化都强制扩容。
- 负载因子 `< 0.1` 时触发缩容，新表大小取第一个大于等于 `used` 的 2 的幂次方。

持久化期间尽量不扩容或缩容，因为 RDB/AOF 重写会 fork 子进程并使用写时复制，大量修改会产生额外内存拷贝。

## 面试官追问

### 提问：Hash 和 String 存 JSON 各有什么优缺点？

Hash 可以单独修改字段，不必将整个对象读出后再写回，节省网络和 CPU；缺点是不支持嵌套结构。String 存 JSON 支持复杂嵌套，但修改单个字段需要整体覆盖。属性扁平的对象适合 Hash，结构复杂的对象适合 JSON。

### 提问：渐进式 `rehash` 期间读写如何处理？

写操作直接写入新表 `ht[1]`；读操作先查 `ht[0]`，找不到再查 `ht[1]`；删除和更新需要检查两张表。每次操作顺便迁移一个或一批桶，因此不会出现长时间阻塞。

### 提问：为什么扩容是 2 倍而不是 1.5 倍？

哈希表大小保持为 2 的幂次方后，可以用 `hash & (size - 1)` 代替取模。扩容为 2 倍仍满足该条件，而且迁移时原元素要么留在原下标，要么移动到“原下标 + 原表大小”，实现更简单。

### 提问：Hash 的大 `key` 问题如何处理？

一个 Hash 保存几十万个字段就属于大 `key`，删除时可能长时间阻塞。可以按字段名哈希取模拆分成多个小 Hash，或使用 `HSCAN` 分批删除；Redis 4.0 之后还可以使用 `UNLINK` 异步回收内存，降低主线程阻塞。
