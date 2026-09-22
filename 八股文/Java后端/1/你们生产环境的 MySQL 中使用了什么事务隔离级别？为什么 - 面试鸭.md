# 你们生产环境的 MySQL 中使用了什么事务隔离级别？为什么？ - 面试鸭 | 2026最新面试题+详细答案解析

## 回答重点

MySQL 默认隔离级别是 RR，但很多互联网公司生产环境用的是 **RC**。主要原因是为了**提高并发**和**降低死锁概率**。

RR 级别下为了防止幻读，引入了间隙锁和临键锁，锁的范围更大。RC 只用行锁，锁定范围更小，并发能力更强。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/78Nq7WtY_f42ge6g756_mianshiya.webp)

## 扩展知识

### RC 和 RR 锁行为的实际对比

创建如下的表，并插入一些记录（[以下例子参考 MySQL 官网](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)）：

```sql
CREATE TABLE t (a INT NOT NULL, b INT) ENGINE = InnoDB;
INSERT INTO t VALUES (1,2),(2,3),(3,2),(4,3),(5,2);
```

执行 SQL-A，且不提交事务：

```sql
UPDATE t SET b = 5 WHERE b = 3;
```

在 RR 隔离级别下，会锁哪几条数据？

```
x-lock(1,2); 保留 x-lock
x-lock(2,3); update(2,3) to (2,5); 保留 x-lock
x-lock(3,2); 保留 x-lock
x-lock(4,3); update(4,3) to (4,5); 保留 x-lock
x-lock(5,2); 保留 x-lock
```

可以看到 5 行数据全锁了。这时候执行 SQL-B：

```sql
UPDATE t SET b = 4 WHERE b = 2;
```

直接被阻塞，因为要锁的行已经被 SQL-A 占了。

换成 RC 隔离级别，执行同样的 SQL-A 会锁哪几条？

```
x-lock(1,2); unlock(1,2)
x-lock(2,3); update(2,3) to (2,5); 保留 x-lock
x-lock(3,2); unlock(3,2)
x-lock(4,3); update(4,3) to (4,5); 保留 x-lock
x-lock(5,2); unlock(5,2)
```

RC 下只锁了真正要更新的 2 行。这时候执行 SQL-B：

```
x-lock(1,2); update(1,2) to (1,4); 保留 x-lock
x-lock(2,3); unlock(2,3)
x-lock(3,2); update(3,2) to (3,4); 保留 x-lock
x-lock(4,3); unlock(4,3)
x-lock(5,2); update(5,2) to (5,4); 保留 x-lock
```

SQL-B 顺利执行，锁了 b = 2 的 3 行数据，完美避开了 SQL-A 加的锁。

### 半一致性读优化

有同学可能会问：SQL-B 不是应该被 (2,3) 这行的锁给阻塞吗？

这里涉及到 InnoDB 的一个优化，叫**半一致性读**。

在 RC 级别下执行 UPDATE 时，扫描到某行发现被锁了，InnoDB 不会傻等，而是去读这行数据的最新已提交版本，判断是否满足 WHERE 条件。如果不满足，说明这行跟当前 UPDATE 没关系，直接跳过不等锁了。

上面的例子里，(2,3) 被 SQL-A 改成了 (2,5)，SQL-B 要更新的是 b = 2 的行，读最新版本发现 b = 5 不满足条件，所以不用等这把锁。

半一致性读只在 RC 级别生效，RR 级别下不会触发。这也是 RC 并发更高的一个重要原因。

### RC 级别幻读问题怎么处理

RC 没有间隙锁，确实可能出现幻读。处理方式有几种：

1）大部分业务场景下幻读影响不大，直接忽略。比如查用户列表，多查出一条刚插入的数据，业务上通常是可以接受的

2）对于有影响的场景，用乐观锁解决。加个 version 字段，更新时带上版本号校验

3）极少数需要强一致的场景，可以手动加锁 SELECT ... FOR UPDATE，或者把这个事务临时改成 RR 级别

### 大厂实践

阿里、美团、字节这些公司基本都是用 RC 级别。原因很简单：

1）互联网业务并发量大，RC 的锁粒度小，能扛更多 QPS

2）死锁风险低，运维成本小。RR 下间隙锁很容易造成死锁，排查起来头疼

3）binlog 用 ROW 格式做主从复制，不依赖 RR 来保证复制一致性

4）幻读问题业务层面好解决，不需要数据库层面强保证

当然如果是银行、证券这类金融系统，对一致性要求极高，还是会用 RR 甚至 SERIALIZABLE。

### MySQL 可重复读能完全避免幻读吗

- [可重复读能完全避免幻读的发生吗？](https://www.mianshiya.com/bank/1791003439968264194/question/1780933295484203009#heading-8)

## 面试官追问

#### 提问：间隙锁具体是怎么加的？能举个例子吗？

>

详细解答可以看：[MySQL 中有哪些锁类型？](https://www.mianshiya.com/question/1780933295500980225)

回答：间隙锁锁的是索引记录之间的间隙。比如表里有 id = 1, 5, 10 三条记录，在 RR 下执行 SELECT * FROM t WHERE id > 3 FOR UPDATE，会锁住 (3, 5]、(5, 10]、(10, +∞) 这几个区间。这时候另一个事务想插入 id = 4 就会被阻塞，即使这行数据还不存在。间隙锁是为了防止幻读，但代价就是锁的范围变大了。

#### 提问：RC 级别下 binlog 必须用什么格式？为什么？

回答：必须用 ROW 格式。因为 STATEMENT 格式记录的是 SQL 原文，在 RC 下由于没有间隙锁，主从执行顺序可能不一样，导致数据不一致。比如主库两个事务并发插入，从库回放时顺序可能变了，自增 ID 就对不上。ROW 格式记录的是具体改了哪些行，数据是什么值，不管执行顺序如何，最终结果一定一致。

#### 提问：生产环境怎么改隔离级别？需要重启 MySQL 吗？

回答：不需要重启。可以在线改全局参数 SET GLOBAL transaction_isolation = 'READ-COMMITTED'，新建立的连接就会用新的隔离级别。已有连接不受影响，需要断开重连才能生效。也可以写到 my.cnf 配置文件里，下次重启后生效。改之前最好确认 binlog 是 ROW 格式，否则可能出问题。

#### 提问：什么情况下 RC 级别会退化成表锁？

回答：UPDATE 或 DELETE 的 WHERE 条件没走索引的时候。InnoDB 的行锁是加在索引上的，如果没走索引，就得扫全表，每扫一行就锁一行。虽然最后会释放不需要的锁，但扫描期间整个表基本处于锁定状态。所以即使用了 RC 级别，也要保证 UPDATE、DELETE 语句走索引，否则并发优势就没了。

...
