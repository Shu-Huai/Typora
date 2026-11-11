# Redis 中的缓存击穿、缓存穿透和缓存雪崩是什么？

## 回答重点

三者都是缓存失效后请求大量访问数据库的场景，但原因和影响范围不同：

| 问题 | 含义 | 典型解决方案 |
| --- | --- | --- |
| 缓存穿透 | 查询的数据不存在，缓存和数据库都没有 | 参数校验、布隆过滤器、缓存空值 |
| 缓存击穿 | 某个热点 `key` 过期瞬间，大量请求同时访问数据库 | 互斥锁、热点数据逻辑过期 |
| 缓存雪崩 | 大量 `key` 同时过期或 Redis 整体不可用 | TTL 加随机值、高可用、本地缓存、熔断降级 |

![缓存穿透、击穿与雪崩](Z:/Public/images/jro2uzCs_Hf6TgnBTI6_mianshiya.webp)

## 扩展知识

### 缓存穿透

攻击者不断请求不存在的 ID 或随机 `key`，例如用户 ID 为负数。缓存中没有，数据库中也没有，每次请求都会打到数据库，严重时可将数据库压垮。

防御可以分三层：

1. **入口校验**：校验参数格式和范围，非法 ID 直接拒绝。
2. **布隆过滤器**：预先加载所有合法 `key`。布隆过滤器说“不存在”时一定不存在，说“存在”时可能误判。
3. **缓存空值**：数据库确认不存在后缓存特殊空标识，并设置较短 TTL（例如 2～5 分钟）。

```java
public String getData(String key) {
    String value = redis.get(key);
    if (value != null) {
        return "NULL".equals(value) ? null : value;
    }
    if (!bloomFilter.mightContain(key)) {
        return null;
    }
    String dbValue = queryDatabase(key);
    if (dbValue == null) {
        redis.setex(key, 300, "NULL");
    } else {
        redis.setex(key, 3600, dbValue);
    }
    return dbValue;
}
```

![缓存穿透](Z:/Public/images/Snipaste_2024-06-11_14-36-38_mianshiya.webp)

### 缓存击穿

缓存击穿针对单个热点 `key`。例如秒杀商品缓存刚好过期，瞬间几十万请求同时访问数据库。

#### 互斥锁重建缓存

只允许一个请求查询数据库并重建缓存，其他请求等待或返回旧值。分布式环境可使用 Redis `SETNX`/带过期时间的锁：

```java
public String getWithMutex(String key) {
    String value = redis.get(key);
    if (value == null) {
        String lockKey = "lock:" + key;
        if (redis.setnx(lockKey, "1", 3)) {
            try {
                value = redis.get(key); // 双重检查
                if (value == null) {
                    value = queryDatabase(key);
                    redis.setex(key, 3600, value);
                }
            } finally {
                redis.del(lockKey);
            }
        } else {
            Thread.sleep(50);
            return getWithMutex(key);
        }
    }
    return value;
}
```

![缓存击穿](Z:/Public/images/Snipaste_2024-06-11_14-36-32_mianshiya.webp)

#### 热点数据逻辑过期

物理上不设置 Redis 过期时间，而是在 `value` 中保存逻辑过期时间戳。后台线程提前刷新，用户请求发现逻辑过期时仍可先返回旧值，避免大量请求阻塞。

### 缓存雪崩

缓存雪崩通常有两种原因：大量 `key` 同时过期，或 Redis 服务整体不可用。

批量预热时不要让所有 `key` 使用相同 TTL，可以增加随机偏移：

```java
int baseExpire = 3600;
int randomExpire = new Random().nextInt(600);
redis.setex(key, baseExpire + randomExpire, value);
```

Redis 整体故障时，需要架构层防御：

1. 使用主从 + 哨兵或 Redis Cluster 提供高可用。
2. 使用 Caffeine、Guava Cache 等本地缓存兜底。
3. 使用 Sentinel、Hystrix 等进行熔断降级，保护数据库。
4. 启动或发布后主动预热热点数据。

![缓存雪崩](Z:/Public/images/Snipaste_2024-06-11_14-36-10_mianshiya.webp)

## 面试官追问

### 提问：布隆过滤器的误判率如何控制？

误判率主要取决于位数组大小和哈希函数数量。位数组越大、哈希函数越多，误判率越低，但内存和计算开销也越高。工程上通常将误判率控制在 1% 以内，并根据数据量选择参数。

### 提问：互斥锁下没拿到锁的请求应该等待还是直接返回？

如果业务允许旧数据或空数据，直接返回响应更快；如果必须拿到最新数据，可以每隔 50～100 ms 重试，但响应时间会增加。高并发场景通常优先返回旧值或降级结果。

### 提问：缓存空值会不会占满 Redis？

有这种风险，因此空值 TTL 要设置得短，并配合布隆过滤器拦截大部分非法请求，避免缓存大量无效 `key`。

### 提问：热点数据逻辑永不过期，数据更新怎么办？

更新数据时主动删除或更新缓存。删除方式实现简单，下次请求自动重建；直接更新要注意并发下的数据一致性，同时可由后台线程定期刷新，防止长期返回旧值。
