# 如何使用 Redis 快速实现布隆过滤器？

## 回答重点

布隆过滤器是判断元素是否可能存在于集合中的概率型结构：**判断不存在时一定不存在，判断存在时可能误判**。Redis 中有两种实现方式：使用 `SETBIT/GETBIT` 手动维护位图，或使用官方 RedisBloom 模块。

布隆过滤器由一个位数组和 k 个哈希函数组成。添加元素时，将 k 个哈希结果对应的位设为 1；查询时只要有一位为 0，就能确定元素不存在；如果全部为 1，只能说明可能存在。

![布隆过滤器原理](Z:/Public/images/INHxTtcx_bulong.drawio_mianshiya.webp)

### 使用 Redis 位图手动实现

```java
public class RedisBloomFilter {
    private static final int BITMAP_SIZE = 1000000;
    private static final int[] SEEDS = {3, 5, 7, 11, 13, 17};
    private Jedis jedis;

    public void add(String key, String value) {
        for (int seed : SEEDS) {
            int offset = hash(value, seed) % BITMAP_SIZE;
            jedis.setbit(key, offset, true);
        }
    }

    public boolean mightContain(String key, String value) {
        for (int seed : SEEDS) {
            int offset = hash(value, seed) % BITMAP_SIZE;
            if (!jedis.getbit(key, offset)) return false;
        }
        return true;
    }
}
```

### 使用 RedisBloom 模块

```bash
# 误判率 1%，容量 100 万
BF.RESERVE user_filter 0.01 1000000
BF.ADD user_filter "user:10086"
BF.EXISTS user_filter "user:10086"  # 1：可能存在
BF.EXISTS user_filter "user:99999"  # 0：一定不存在
```

## 扩展知识

### 误判率和参数选择

误判率取决于位数组大小 `m`、哈希函数数量 `k` 和元素数量 `n`。理论上最优哈希函数数量为：

```text
k = (m / n) × ln2
```

工程上可粗略估算：误判率 1% 时每个元素约需 10 bit，0.1% 约需 15 bit，0.01% 约需 20 bit。存储 1000 万个元素且误判率为 1% 时，位数组约需 1 亿 bit，即约 12 MB。

![误判率参数](Z:/Public/images/tFTPc0lN_vU47WcPgNf_mianshiya.webp)

### 解决缓存穿透

布隆过滤器可以放在缓存之前，拦截数据库中不存在的 ID：

```java
public User getUser(Long userId) {
    String key = "user:" + userId;
    if (!bloomFilter.mightContain("user_bloom", String.valueOf(userId))) {
        return null;
    }

    User user = cache.get(key);
    if (user != null) return user;

    user = userDao.findById(userId);
    if (user != null) cache.set(key, user);
    return user;
}
```

### RedisBloom 模块详解

RedisBloom 会根据预期容量和误判率自动选择参数：

```bash
BF.RESERVE myfilter 0.001 10000000
BF.MADD myfilter item1 item2 item3
BF.MEXISTS myfilter item1 item2 item3
BF.INFO myfilter
```

生产环境建议显式执行 `BF.RESERVE`，不要依赖默认容量和误判率。Java 中也可以通过 Redisson 使用：

```java
RBloomFilter<String> filter = redisson.getBloomFilter("user_bloom");
filter.tryInit(50000000L, 0.03);
filter.add("user:10086");
boolean exists = filter.contains("user:10086");
```

### 适用场景

布隆过滤器适合数据量大、允许小概率误判、只需判断存在性的场景：

- 爬虫 URL 去重。
- 垃圾邮件或黑名单过滤。
- 推荐系统去重。
- HBase、Cassandra 等存储引擎减少磁盘 I/O。

### 布隆过滤器的变种

原始布隆过滤器不支持删除，因为一个位可能由多个元素共同设置。常见变种：

1. **Counting Bloom Filter**：用计数器替代 bit，支持删除，但空间开销更大。
2. **Cuckoo Filter**：支持删除，空间效率接近原版。
3. **Scalable Bloom Filter**：支持动态扩容。

RedisBloom 还提供 Cuckoo Filter，可使用 `CF.ADD`、`CF.EXISTS` 等命令。

## 面试官追问

### 提问：布隆过滤器的误判率能降到 0 吗？

不能。有限位数组和哈希映射必然存在冲突，只能通过增大位数组、优化哈希函数数量来降低误判率。如果需要精确判断，应使用 Set 等结构，但空间成本会明显增加。

### 提问：为什么布隆过滤器不支持删除？

多个元素可能共享同一位，删除其中一个时将该位置置 0 会误伤其他元素。需要支持删除时可使用 Counting Bloom Filter，用计数器记录每个位被设置的次数。

### 提问：位图实现和 RedisBloom 模块有什么区别？

手动位图需要自行设计哈希函数、计算位数组大小并处理扩容，容易出错。RedisBloom 封装了参数计算、批量操作和动态扩容，生产环境通常更推荐使用模块。

### 提问：布隆过滤器和 HyperLogLog 有什么区别？

布隆过滤器判断某个元素是否可能存在；HyperLogLog 估算集合中不重复元素的数量。前者可以查询单个元素，后者只能给出整体基数估计。
