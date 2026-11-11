# Redis 中 EMBSTR 对象的阈值设置为何为 44？其调整历史是什么？

## 回答重点

EMBSTR 的 44 字节阈值，本质上由 Redis 使用的内存分配布局决定。Redis 通常使用 jemalloc，64 字节是一个关键分配单元，EMBSTR 需要把 `redisObject`、SDS 头部、字符串内容和结尾 `\0` 一起放进这 64 字节中。

计算如下：

1. `redisObject` 约占 16 字节。
2. `sdshdr8` 头部占 3 字节：`len`、`alloc`、`flags` 各 1 字节。
3. 字符串末尾 `\0` 占 1 字节。
4. 剩余空间为 `64 - 16 - 3 - 1 = 44` 字节。

![EMBSTR 内存布局](Z:/Public/images/Ctg87c8p_embstr.drawio_mianshiya.webp)

EMBSTR 将 `redisObject` 和 SDS 连续存储，只需一次内存分配和释放，CPU 缓存局部性也更好。超过 44 字节后使用 RAW 编码，`redisObject` 与 SDS 分开存放。

```c
typedef struct redisObject {
    unsigned type:4;
    unsigned encoding:4;
    unsigned lru:24;
    int refcount;
    void *ptr;
} robj;

struct __attribute__ ((__packed__)) sdshdr8 {
    uint8_t len;
    uint8_t alloc;
    unsigned char flags;
    char buf[];
};
```

## 扩展知识

### 为什么 Redis 3.2 之前阈值是 39

Redis 3.2 之前使用的 SDS 头部包含两个 4 字节字段：

```c
struct sdshdr {
    unsigned int len;
    unsigned int free;
    char buf[];
};
```

旧结构头部占 8 字节，因此最大 EMBSTR 内容长度为：

```text
64 - 16 - 8 - 1 = 39 字节
```

Redis 3.2 引入 `sdshdr8`、`sdshdr16`、`sdshdr32`、`sdshdr64`，根据字符串长度选择不同头部。短字符串使用仅 3 字节的 `sdshdr8`，因此阈值提升了 5 字节到 44。

![SDS 头部演进](Z:/Public/images/2ekYOANU_STE3vAD5FG_mianshiya.webp)

### jemalloc 的内存分配策略

jemalloc 按 `size` class 分级分配，常见大小包括 8、16、32、48、64、80、96、128 字节等。申请不超过 64 字节的内存时，可以使用 64 字节块；申请 65 字节则通常需要更大的 80 字节块，产生额外浪费。

因此 Redis 将 EMBSTR 内容控制在 64 字节布局内，充分利用该分配单元。

### EMBSTR 和 RAW 的区别

| 特性 | EMBSTR | RAW |
| --- | --- | --- |
| 内存布局 | `redisObject` 与 SDS 连续 | 两者分开 |
| 内存分配 | 一次 `malloc` | 两次 `malloc` |
| 内存释放 | 一次 `free` | 两次 `free` |
| 字符串长度 | ≤ 44 字节 | > 44 字节 |
| 缓存友好性 | 高 | 需要指针跳转 |
| 修改操作 | 修改时转为 RAW | 可以独立扩容 |

EMBSTR 具有只读特性。对其执行 `APPEND`、`SETRANGE` 等修改操作时，Redis 会先转为 RAW，再完成修改：

```bash
127.0.0.1:6379> SET name "hello"
OK
127.0.0.1:6379> OBJECT ENCODING name
"embstr"
127.0.0.1:6379> APPEND name " world"
(integer) 11
127.0.0.1:6379> OBJECT ENCODING name
"raw"
```

### 面试加分点：INT 编码

如果字符串内容是 long 范围内的整数，Redis 会使用 INT 编码，将整数直接放在 `ptr` 中，连 SDS 都不需要：

```bash
127.0.0.1:6379> SET counter 12345
OK
127.0.0.1:6379> OBJECT ENCODING counter
"int"
```

Redis 还会复用 0～9999 的整数对象，进一步减少计数器和小 ID 的内存分配。

![String 编码示例](Z:/Public/images/wnE89xBp_image_mianshiya.webp)

## 面试官追问

### 提问：EMBSTR 是只读的，为什么不直接使用 RAW？

EMBSTR 一次分配、连续存储，读取时缓存命中率更高，创建和释放也更快。用户昵称、配置项、Token 等短字符串通常读多写少，偶尔修改时再转为 RAW 的成本可以接受。

### 提问：44 字节字符串追加一个字符会发生什么？

Redis 会先将 EMBSTR 转换为 RAW，重新分配可以容纳 45 字节内容的 SDS。`ptr` 从指向连续内存改为指向新分配的内存块，原来的连续内存被释放。

### 提问：Redis 7.0 修改了这个阈值吗？

没有，仍然是 44 字节。它与 64 字节分配单元和对象布局相关，除非更换分配器或修改 `redisObject`/SDS 结构，否则不会改变。

### 提问：如果使用 glibc malloc，44 字节阈值还存在吗？

仍然存在，因为 44 是 Redis 源码中的布局阈值。Redis 官方通常推荐 jemalloc；强行使用 glibc 的 ptmalloc2 可能带来更严重的内存碎片，但不会自动改变该阈值。
