# 如何使用 Redis 快速实现排行榜？

## 回答重点

使用 Redis 的 **Sorted Set（ZSet）** 实现排行榜最合适。每个成员绑定一个 score，Redis 自动按 score 排序，底层跳表支持插入、删除和排名查询，复杂度通常为 $O(\log N)$。

核心命令：

```redis
ZADD leaderboard 1000 user1
ZREVRANK leaderboard user1
ZREVRANGE leaderboard 0 9 WITHSCORES
ZINCRBY leaderboard 500 user1
```

- `ZADD`：添加或更新用户分数。
- `ZREVRANK`：查询用户排名，返回值从 0 开始。
- `ZREVRANGE`：按分数从高到低获取榜单区间。
- `ZINCRBY`：原子增加或减少用户分数。

![Redis 排行榜实现](Z:/Public/images/ugxybpGb_hexin.drawio_mianshiya.webp)

```java
Jedis jedis = new Jedis("localhost", 6379);
jedis.zadd("game:rank:202601", 8500, "player_10086");
Long rank = jedis.zrevrank("game:rank:202601", "player_10086");
System.out.println("当前排名：" + (rank + 1));
Set<Tuple> top100 = jedis.zrevrangeWithScores("game:rank:202601", 0, 99);
```

## 扩展知识

### 同分排名问题

ZSet 的 score 相同时默认按 member 字典序排序。如果业务要求先达到分数者排名靠前，可以将时间因子编码进 score：

```java
long maxTimestamp = 4102444800000L;
double score = realScore + (1 - System.currentTimeMillis() * 1.0 / maxTimestamp);
jedis.zadd("leaderboard", score, "user1");
long realScore = (long) Math.floor(score);
```

![排行榜同分处理](Z:/Public/images/GkBJa3hJ_4g3po1BK6t_mianshiya.webp)

### 大规模排行榜的分片

单个 ZSet 可以保存数千万用户；达到上亿用户或需要多维榜单时，可以分片：

1. **按时间分片**：每天、每周、每月一个 `key`，例如 `rank:daily:20260115`。
2. **按分数区间分片**：不同分数段使用不同 `key`，查询总榜时聚合。
3. **按用户分片**：按用户 ID 取模，适合只查询用户附近排名而非全局排名。

```java
String todayKey = "rank:daily:" + LocalDate.now().format(DateTimeFormatter.BASIC_ISO_DATE);
jedis.zadd(todayKey, score, playerId);
jedis.expire(todayKey, 7 * 24 * 3600);
```

周榜可以通过定时任务使用 `ZUNIONSTORE` 聚合多个日榜。

### 实时排名与附近排名

如果只需要展示用户附近的名次，无需查询整个排行榜：

```java
Long myRank = jedis.zrevrank("leaderboard", myId);
long start = Math.max(0, myRank - 5);
long end = myRank + 5;
Set<Tuple> nearbyPlayers = jedis.zrevrangeWithScores("leaderboard", start, end);
```

无论总榜有多少用户，每次只获取约 11 条数据。

### 常用命令对比

| 命令 | 功能 | 时间复杂度 | 使用场景 |
| --- | --- | --- | --- |
| `ZADD` | 添加或更新成员 | $O(\log N)$ | 用户得分变化 |
| `ZINCRBY` | 增减分数 | $O(\log N)$ | 增量更新 |
| `ZREVRANK` | 查询排名 | $O(\log N)$ | 展示我的排名 |
| `ZREVRANGE` | 区间查询 | $O(\log N + M)$ | 榜单分页 |
| `ZRANGEBYSCORE` | 按分数范围查询 | $O(\log N + M)$ | 查询分数段 |
| `ZCARD` | 获取成员数 | $O(1)$ | 统计参与人数 |
| `ZREM` | 删除成员 | $O(\log N)$ | 用户注销 |

### 持久化与缓存穿透

排行榜不应只依赖 Redis：用户得分更新时先写数据库，再更新 Redis；Redis 重启后根据数据库恢复 ZSet；同时可开启 RDB/AOF，但要评估恢复时间。对于查询不存在用户导致的缓存穿透，可以使用布隆过滤器或缓存空结果。

## 面试官追问

### 提问：Sorted Set 为什么使用跳表而不是红黑树？

跳表实现简单，范围查询可以直接沿底层链表遍历；平均复杂度与红黑树相同，都是 $O(\log N)$，但代码和维护成本更低。

### 提问：实时更新时如何保证一致性？

单条 `ZADD` 或 `ZINCRBY` 是原子操作。批量更新可以用 `MULTI/EXEC` 或 Lua 脚本；多个服务更新同一用户时，优先使用 `ZINCRBY` 避免覆盖，也可以配合分布式锁。

### 提问：排行榜达到上亿用户如何优化？

可以分层：活跃用户保存在 Redis，非活跃用户落库；同时按分数区间或用户 ID 分片，需要全局排名时再聚合。

### 提问：同分时如何保证先达到者排名靠前？

Redis 默认按 member 字典序排序。可以将归一化时间因子加入 score，例如 `真实分数 + (1 - 时间戳 / 最大时间戳)`，使更早达到分数的用户拥有更大的附加值。
