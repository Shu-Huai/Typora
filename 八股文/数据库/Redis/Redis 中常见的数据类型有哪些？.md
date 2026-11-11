# Redis 中常见的数据类型有哪些？

## 回答重点

Redis 最常见的五种数据类型是 **String、List、Hash、Set、ZSet**。

| 类型 | 特点 | 常见场景 |
| --- | --- | --- |
| String | 字符串、数字或二进制，最大 512 MB | 缓存、会话、计数器 |
| Hash | field-`value` 集合，可单独修改字段 | 用户、商品等对象属性 |
| List | 有序字符串列表，支持两端操作 | 简单消息队列、时间线 |
| Set | 无序且元素不重复 | 去重、标签、共同关注 |
| ZSet | 元素带 score，按分数排序 | 排行榜、热搜榜 |

String 是最基础的类型，可用 `INCR` 原子递增文章阅读量或点赞数。Hash 适合将商品 ID 作为 `key`，把价格、库存、名称等字段放在同一个对象中。List 支持 `LPUSH` 生产、`RPOP` 消费。Set 擅长去重和集合运算。ZSet 通过 score 排序，适合直接获取 Top N。

![Redis 常见数据类型](Z:/Public/images/cgHkg4ND_BKVXkuxOl0_mianshiya.webp)

## 扩展知识

### 四种高级数据类型

Redis 还提供 BitMap、HyperLogLog、GEO、Stream 四种常用高级类型。

#### BitMap

BitMap 用 bit 保存 0/1 状态，空间利用率很高。例如 1000 万用户的签到状态只需要约 1.2 MB。常用命令：

```redis
SETBIT user:sign:202409 12345 1  # 用户 12345 在 9 月签到
GETBIT user:sign:202409 12345    # 查询签到状态
```

#### HyperLogLog

HyperLogLog 是概率性基数统计结构，无论添加多少数据，固定占用约 12 KB，误差约 0.81%。适合网站 UV 等对精度要求不高但数据量很大的场景：

```redis
PFADD page:uv user1 user2 user3  # 记录访问用户
PFCOUNT page:uv                  # 估算独立用户数
```

多个 HyperLogLog 可以用 `PFMERGE` 合并，误差率不会简单叠加。

#### GEO

GEO 用于保存地理位置并进行空间查询，底层基于 ZSet，将经纬度编码为 score，适合“附近的人”和配送距离计算：

```redis
GEOADD riders 116.403 39.915 "rider001"   # 保存骑手位置
GEORADIUS riders 116.4 39.9 5 km           # 查询 5 公里内骑手
```

#### Stream

Stream 是 Redis 5.0 引入的消息流结构，支持自动生成全局唯一消息 ID 和消费组。相比 List，它支持更完整的消费确认与消息管理；相比 Pub/Sub，消息能够持久化，消费者重启后可以继续消费。

![Redis Stream](Z:/Public/images/DqaRZpFZ_aQfSRNeuuf_mianshiya.webp)

### 数据类型与底层编码

同一种数据类型可能对应多种底层编码，Redis 会根据数据量和元素大小自动切换：

| 数据类型 | 小数据量编码 | 大数据量编码 | 典型切换条件 |
| --- | --- | --- | --- |
| String | `int` / `embstr` | `raw` | 约 44 字节 |
| List | `quicklist` | `quicklist` | — |
| Hash | `listpack` | `hashtable` | 512 个字段或单值超过 64 字节 |
| Set | `intset` / `listpack` | `hashtable` | 512 个元素或出现非整数 |
| ZSet | `listpack` | `skiplist` + `hashtable` | 128 个元素或单值超过 64 字节 |

这些阈值可以通过配置调整，例如 `hash-max-listpack-entries` 控制 Hash 的元素数量阈值。

相关主题：

- [Redis String 类型的底层实现是什么？（SDS）](https://www.mianshiya.com/question/1780933295681335298)
- [Redis 的 Hash 是什么？](https://www.mianshiya.com/question/1780933295601643521)
- [Redis ZSet 的实现原理是什么？](https://www.mianshiya.com/bank/1791375592078610434/question/1861688534670434305)
- [Redis 中的 Ziplist 和 Quicklist 数据结构的特点是什么？](https://www.mianshiya.com/bank/1791375592078610434/question/1799677102985125890)
- [Redis 的 ListPack 数据结构是什么？](https://www.mianshiya.com/bank/1791375592078610434/question/1799678566948216833)

## 面试官追问

### 提问：String 最大能存 512 MB，生产中会存这么大的值吗？

一般不会。Redis 命令执行主要由单线程完成，大 `key` 的读写会阻塞其他请求。通常建议单个 `value` 控制在 10 KB 以内，超过 1 MB 就考虑拆分；大 `key` 还会拖慢集群迁移和主从同步。

### 提问：ZSet 底层为什么使用跳表而不是红黑树？

跳表实现简单，范围查询可以直接沿底层链表顺序遍历；插入和删除主要是调整指针，不需要红黑树的旋转操作，因此更适合 Redis 的实现需求。

### 提问：HyperLogLog 可以合并吗？

可以使用 `PFMERGE` 合并多个 HyperLogLog。例如先统计每天 UV，再合并得到周 UV，整体误差仍在其设计范围内。

### 提问：Stream 能替代 Kafka 吗？

通常不能。Redis Stream 适合轻量级、几千 QPS 左右的内部消息传递；Kafka 面向大规模分布式消息场景，具备更强的吞吐、分区、多副本、消息回溯和企业级容灾能力。
