# Redis 中的 Big Key 问题是什么？如何解决？

## 回答重点

Redis 中的 Big Key 是指内存占用较大的 `key`。它的主要危害包括：

- **数据分布不均**：集群中大 `key` 可能集中映射到某个 slot 和节点。
- **阻塞单线程**：读取、修改或删除大 `key` 耗时较长，会阻塞其他命令。
- **网络开销大**：大 `value` 在高并发下会产生大量网络流量和传输延迟。
- **客户端超时**：命令执行时间过长，客户端可能等待超时。

解决 Big Key 可以从三个层面入手：

1. **开发层面**：拆分大对象、压缩数据，并选择合适的数据结构。例如将一个拥有百万 field 的 Hash 按 ID 取模拆成多个 Hash。
2. **业务层面**：只缓存必要和高频数据，避免把详细地址、历史订单等低频信息全部放入 Redis；列表只缓存前 100 条热门数据。
3. **架构层面**：使用 Redis Cluster，并将拆分后的数据分散到不同节点。

## 扩展知识

### 怎样判断 Big Key

没有绝对统一的标准，需要结合业务和实例配置。常见参考值：

- String 的 `value` 超过 1 MB。
- Hash、List、Set、ZSet 元素超过 5000 个。

![Big Key 参考](Z:/Public/images/8pbjTAgo_image_mianshiya.webp)

生产环境可以设置更严格的标准，例如 String 超过 10 KB 就重点关注，因为高并发下会快速放大网络和内存开销。

```redis
# 巨大的字符串
SET article:content:12345 "这里是一篇十几万字的文章内容..."

# 包含数百万成员的集合
SADD hot_users user:1 user:2 user:3 ... user:5000000
```

![Big Key 示例](Z:/Public/images/MUJb4AeF_f7ViBoYFXO_mianshiya.webp)

### 如何发现 Big Key

Redis 自带的 `redis-cli --bigkeys` 可以扫描每种数据类型中元素数量最多的 `key`：

```bash
redis-cli --bigkeys -i 0.1
```

`-i 0.1` 表示每扫描 100 个 `key` 休息 0.1 秒，降低线上扫描压力。该命令底层使用 `SCAN` 以及 `STRLEN`、`HLEN`、`SCARD` 等命令统计信息。

![bigkeys 扫描结果](Z:/Public/images/Snipaste_2024-05-09_15-03-43_mianshiya.webp)

注意，元素数量多不一定代表内存占用大。一个 Hash 有 1 万个 field、每个 `value` 只有 10 字节，可能与只有 100 个 field 但每个 `value` 为 1 KB 的 Hash 占用相近。因此还要结合实际内存查看：

```redis
MEMORY USAGE key
```

也可以使用 `redis-rdb-tools` 等工具离线分析 RDB，生成包含所有大 `key` 的 CSV 报告。

### 删除 Big Key 的正确方式

直接对包含百万元素的 Hash 执行 `DEL`，Redis 需要逐个释放内存，可能阻塞主线程数秒。

Redis 4.0 之后推荐使用 `UNLINK`：主线程只负责将 `key` 从键空间摘除，实际内存释放交给后台线程异步完成。

Redis 4.0 之前则应分批删除：

- Hash：`HSCAN` + `HDEL`
- Set：`SSCAN` + `SREM`
- List：分批 `LTRIM`

每次只处理几百个元素，分多轮完成，避免长时间阻塞。

## 面试官追问

### 提问：线上如何监控 Big Key？

可以在 Redis Proxy 层记录命令响应大小，超过阈值就告警；也可以通过定时任务用 `SCAN` 抽样，再配合 `MEMORY USAGE` 统计实际内存。异常 `key` 可推送到钉钉或飞书。云厂商托管 Redis 通常也提供 Big Key 分析和 Top N 列表。

### 提问：Big Key 导致主从同步延迟怎么处理？

主库写入大 `key` 的命令会完整传给从库，从库单线程回放时同样可能阻塞。根本方案是拆分 `key`；临时可以适当调大 `slave-output-buffer-limit`，避免复制缓冲区溢出触发全量同步。

### 提问：删除大 `key` 时使用 `UNLINK`，如果它正在被读取怎么办？

`UNLINK` 执行后 `key` 会立即从键空间消失，后续读请求返回 nil。已经开始处理的读操作仍可完成，因为它们持有对象引用；内存释放在后台异步进行。
