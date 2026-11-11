# Redis String 类型的底层实现是什么？（SDS）

## 回答重点

Redis 的 String 底层主要使用 **SDS（Simple Dynamic String，简单动态字符串）**，而不是直接使用 C 原生字符数组。

C 字符串存在三个问题：

1. 获取长度需要遍历，复杂度为 $O(N)$。
2. 遇到 `\0` 就认为结束，无法安全保存二进制数据。
3. 扩容需要手动处理，容易发生缓冲区溢出。

SDS 在字符数组前保存长度和已分配空间：

```c
struct sdshdr {
    int len;      // 当前长度
    int free;     // 剩余空间
    char buf[];   // 实际数据
};
```

因此获取长度直接读取 `len`，复杂度为 $O(1)$；扩容前检查 `alloc - len`，避免溢出；字符串内容不依赖 `\0` 结束，可以保存图片、音频等二进制数据；缩短字符串后还可以保留空闲空间，减少后续分配。

![SDS 结构](Z:/Public/images/8xBJtKau_bianli.drawio_mianshiya.webp)

Redis 还会根据内容选择不同编码：

1. 能表示为整数的值使用 **int 编码**，数字直接保存在指针位置，不需要分配 SDS。
2. 不超过 44 字节的短字符串使用 **embstr 编码**，`redisObject` 与 SDS 一次性连续分配。
3. 超过 44 字节的字符串使用 **raw 编码**，`redisObject` 与 SDS 分开分配，便于独立扩容。

![String 编码](Z:/Public/images/wnE89xBp_image_mianshiya.webp)

```java
Jedis jedis = new Jedis("localhost", 6379);

jedis.set("counter", "12345");                  // int 编码
jedis.set("name", "zhangsan");                  // embstr 编码
jedis.set("article", "这是一篇超过44字节的文章内容..."); // raw 编码

// DEBUG OBJECT counter  -> encoding:int
// DEBUG OBJECT name     -> encoding:embstr
// DEBUG OBJECT article  -> encoding:raw
```

## 扩展知识

### SDS 的内存预分配策略

SDS 扩容时会预留额外空间，以减少频繁 `realloc`：

1. 字符串长度小于 1 MB 时，扩容后的 `alloc` 通常为新长度的 2 倍。
2. 字符串长度大于等于 1 MB 时，每次额外分配约 1 MB。

该策略特别适合日志收集、消息拼接等频繁追加场景。

### `sdshdr` 的多版本设计

Redis 3.2 之后会根据字符串长度选择不同的头部结构：

```c
// sdshdr5：长度 0～31 字节
// sdshdr8：长度 32～255 字节
// sdshdr16：长度 256～65535 字节
// sdshdr32/64：更长字符串

struct __attribute__ ((__packed__)) sdshdr8 {
    uint8_t len;
    uint8_t alloc;
    unsigned char flags;
    char buf[];
};

struct __attribute__ ((__packed__)) sdshdr32 {
    uint32_t len;
    uint32_t alloc;
    unsigned char flags;
    char buf[];
};
```

短字符串使用更小的头部，长字符串才使用 `sdshdr32/64`，可以节省大量短 `key` 的内存。

### 三种编码的内存布局

| 编码 | 触发条件 | 内存分配次数 | 适用场景 |
| --- | --- | ---: | --- |
| `int` | 值是 long 范围内的整数 | 0 次 | 计数器、ID |
| `embstr` | 字符串不超过 44 字节 | 1 次 | 短字符串、缓存 `key` |
| `raw` | 字符串超过 44 字节 | 2 次 | 长文本、序列化数据 |

44 字节的分界线与 jemalloc 的 64 字节分配单元有关：`redisObject` 约占 16 字节，`sdshdr8` 头部约占 3 字节，末尾 `\0` 占 1 字节，剩余 `64 - 16 - 3 - 1 = 44` 字节用于存储内容。

![embstr 阈值](Z:/Public/images/SoFWOkd3_kmY4Uz2sUb_mianshiya.webp)

### embstr 的只读特性

`embstr` 将 `redisObject` 和 SDS 放在一块连续内存中，修改内容可能导致整块内存重新分配，因此它本身按只读方式处理。需要修改时，Redis 会先转为 `raw` 编码：

```bash
127.0.0.1:6379> SET name "hello"
OK
127.0.0.1:6379> DEBUG OBJECT name
Value at:0x7f... encoding:embstr ...

127.0.0.1:6379> APPEND name " world"
(integer) 11
127.0.0.1:6379> DEBUG OBJECT name
Value at:0x7f... encoding:raw ...
```

### 二进制安全

C 字符串把 `\0` 当作结束符，`"hello\0world"` 只能读取到 `hello`。SDS 使用 `len` 判断长度，`buf` 中的 `\0` 只是普通数据，可以安全保存：

- Protocol Buffers、MessagePack 等序列化结果。
- 图片缩略图和小文件。
- gzip 等压缩后的二进制内容。

## 面试官追问

### 提问：SDS 为什么小于 1 MB 时翻倍，大于 1 MB 时只增加 1 MB？

小字符串翻倍可以减少扩容次数，即使浪费一部分空间，绝对值也不大。大字符串继续翻倍会造成很大的空间浪费，例如 10 MB 扩成 20 MB，因此改为固定增加约 1 MB，在扩容次数和内存浪费之间折中。

### 提问：embstr 和 raw 的 44 字节分界线如何计算？

jemalloc 的分配单元按 64 字节计算，`redisObject` 占 16 字节，`sdshdr8` 占 3 字节，末尾 `\0` 占 1 字节，剩余 44 字节可以保存字符串。超过该长度就使用 raw 分开分配。

### 提问：为什么 Redis 不直接使用 C++ 的 `std::string`？

Redis 使用 C 编写，SDS 没有 C++ 运行时依赖，而且 Redis 可以完全控制内存布局、预分配策略和多版本头部结构，更适合其短字符串、大量 `key` 和高性能场景。

### 提问：SDS 末尾为什么还保留 `\0`？

为了兼容 `printf`、`strcmp` 等依赖 `\0` 的 C 标准库函数。SDS 自身并不依靠它判断长度，真正的长度始终由 `len` 字段记录。
