# Redis 字符串类型的最大值大小是多少？

## 回答重点

Redis String 的最大容量是 **512 MB**，这是 Redis 源码中的硬限制。这个值只是理论上限，并不代表生产环境应该存这么大的字符串。

大字符串会增加网络传输、内存分配、持久化和主从同步的负担；`GET`、`SET`、`APPEND`、`STRLEN` 等操作也可能阻塞 Redis 主线程。实践中单个字符串控制在 **10 KB 以内**较健康，超过 100 KB 就应考虑拆分。

![Redis String 大小限制](Z:/Public/images/HYzwEfI0_gTqwBZxWny_mianshiya.webp)

![Redis String 限制说明](Z:/Public/images/20160316161621964_mianshiya.webp)

## 扩展知识

### 大字符串的性能问题

以 100 MB 字符串为例：

1. **网络传输**：千兆网卡传输需要较长时间，期间主线程可能一直处理该请求。
2. **内存分配**：大块连续内存分配效率较低，也容易产生碎片。
3. **持久化影响**：AOF 重写和 RDB 快照都要完整处理该数据。
4. **主从同步**：全量同步需要将大对象传给从节点，加载期间可能阻塞。
5. **过期删除**：大 `key` 过期时同步释放内存，可能造成数百毫秒延迟。

![大字符串影响](Z:/Public/images/6FWEOMHt_zs8HQJDo5s_mianshiya.webp)

### 大字符串的拆分方案

#### 分片存储

把大字符串切成多个小字符串，例如 `key:0`、`key:1`，读取时使用 `MGET` 拼接：

```java
public void setBigString(String key, String value, int chunkSize) {
    int chunks = (value.length() + chunkSize - 1) / chunkSize;
    Pipeline pipeline = jedis.pipelined();
    for (int i = 0; i < chunks; i++) {
        int start = i * chunkSize;
        int end = Math.min(start + chunkSize, value.length());
        pipeline.set(key + ":" + i, value.substring(start, end));
    }
    pipeline.set(key + ":chunks", String.valueOf(chunks));
    pipeline.sync();
}
```

#### 压缩存储

文本数据可以先使用 gzip、Snappy 等压缩，通常能显著降低存储体积和网络开销。

```java
byte[] compressed = Snappy.compress(value.getBytes(StandardCharsets.UTF_8));
jedis.set(key.getBytes(), compressed);
```

#### 外部存储

图片、文档等真正的大文件不应放在 Redis 中，应存到 OSS、对象存储或文件系统，Redis 只保存 URL 或文件路径。

### 其他数据类型的理论上限

| 数据类型 | 单个元素大小限制 | 元素数量限制 |
| --- | --- | --- |
| String | 512 MB | 1 个值 |
| List | 每个元素 512 MB | `2^32 - 1` |
| Set | 每个元素 512 MB | `2^32 - 1` |
| Hash | 每个 field/`value` 512 MB | `2^32 - 1` 个 field |
| Sorted Set | 每个元素 512 MB | `2^32 - 1` |

这些是理论上限，实际生产中集合超过 1 万个元素就应重点评估。

### 如何发现大 Key

```bash
# Redis 4.0+ 内置扫描
redis-cli --bigkeys

# 更精确的检查方式
redis-cli SCAN 0 COUNT 1000
redis-cli DEBUG OBJECT your_key

# 查看实际内存占用
redis-cli MEMORY USAGE your_key
```

云厂商托管 Redis 通常也提供 Big Key 分析功能。

## 面试官追问

### 提问：为什么限制是 512 MB，而不是 1 GB 或 256 MB？

512 MB 是覆盖绝大多数正常场景与控制单 `key` 风险之间的经验折中。该限制在 SDS 相关源码中定义，技术上可以修改，但继续增大没有实际收益，反而会加剧阻塞、内存和同步问题。

### 提问：大 `key` 删除会阻塞 Redis，如何解决？

Redis 4.0 之后使用 `UNLINK` 异步删除，主线程只把 `key` 从键空间摘除，后台线程负责释放内存。List、Set、Hash 等集合也可以通过 `LPOP`、`HSCAN`、`SSCAN` 等方式分批删除；还可以开启 `lazyfree-lazy-expire` 让过期删除异步执行。

### 提问：把图片存到 Redis 是否合理？

通常不合理。图片通常为几百 KB 或几 MB，会浪费内存并拖慢 Redis。更合理的做法是存到 OSS 或 CDN，Redis 只保存 URL；只有极小且高频访问的图标才可能考虑缓存。

### 提问：512 MB 限制能突破吗？

可以修改源码突破，但不建议。超大对象更适合 HBase、MongoDB 或文件存储，Redis 的定位是高速内存数据结构服务，而不是大对象存储。
