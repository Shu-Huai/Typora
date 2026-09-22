# Spring 事务有几个隔离级别？ - 面试鸭 | 2026最新27 届校招 Java 热题+详细答案解析

## 回答重点

Spring 定义了 5 种事务隔离级别，本质上是对数据库隔离级别的封装：

- **DEFAULT**（默认）：使用底层数据库的默认隔离级别。如果数据库没有特定的设置，通常默认为 `READ_COMMITTED`。

- **READ_UNCOMMITTED**（读未提交）：最低的隔离级别，允许事务读取尚未提交的数据，可能会导致脏读、不可重复读和幻读。

- **READ_COMMITTED**（读已提交）：仅允许读取已经提交的数据，避免了脏读，但可能会出现不可重复读和幻读问题。

- **REPEATABLE_READ**（可重复读）：确保在同一个事务内的多次读取结果一致，避免脏读和不可重复读，但可能会有幻读问题。

- **SERIALIZABLE**（可串行化）：最高的隔离级别，通过强制事务按顺序执行，完全避免脏读、不可重复读和幻读，代价是性能显著下降。

![](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/7jc0MbTS_8bb08ab2-81c8-47a5-a3a6-3847f872358c_mianshiya.webp)

## 扩展知识

### 三种并发问题

**脏读**是读到了别人还没提交的数据。事务 A 改了一行数据还没提交，事务 B 读到了，结果事务 A 回滚了，事务 B 拿到的数据就是脏的，压根不存在。

**不可重复读**是同一个事务里两次读同一行，结果不一样。事务 A 第一次读 balance=100，事务 B 把 balance 改成 200 并提交了，事务 A 再读就变成 200 了。问题出在读的是同一行数据被别人改了。

**幻读**是同一个事务里两次查询，结果集条数不一样。事务 A 查 age>20 的用户有 10 条，事务 B 插入一条 age=25 的用户并提交，事务 A 再查就变成 11 条了。问题出在别人插了新行进来。

隔离级别脏读不可重复读幻读READ_UNCOMMITTED会出现会出现会出现READ_COMMITTED不会会出现会出现REPEATABLE_READ不会不会可能出现SERIALIZABLE不会不会不会

### Spring 中怎么设置隔离级别

用 `@Transactional` 注解的 isolation 属性：

```java
@Service
public class OrderService {

    // 使用数据库默认级别
    @Transactional
    public void createOrder() { }

    // 指定读已提交
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void queryOrder() { }

    // 指定可重复读
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public void updateStock() { }
}
```

底层是 Spring 拿到数据库连接后调用 `Connection.setTransactionIsolation()` 设置的。如果数据库不支持你指定的级别，行为取决于数据库驱动，有的会降级有的会报错。

### 生产环境怎么选隔离级别

大多数互联网公司用 **READ_COMMITTED**。原因是 REPEATABLE_READ 虽然一致性更好，但间隙锁容易导致锁冲突，高并发场景下死锁概率上升。READ_COMMITTED 只有行锁，锁粒度小，并发性能好。

至于一致性问题，业务层面有很多办法绕过去：

1）乐观锁，用版本号字段 `UPDATE ... WHERE version = ?`

2）分布式锁，用 Redis 或 ZooKeeper 在应用层控制

3）消息队列，把并发操作变成串行

阿里的 MySQL 默认就是 READ_COMMITTED，还专门改了 binlog 格式来配合。

- [1535. 你们生产环境的 MySQL 中使用了什么事务隔离级别？为什么？](https://www.mianshiya.com/question/1805421515868151810)

### 可重复读能完全避免幻读吗

严格说不能。MySQL 的 REPEATABLE_READ 在快照读下不会幻读，但当前读还是可能出现。而且有个边界情况：事务 A 快照读看不到事务 B 新插入的行，但如果事务 A 去 UPDATE 那行，是能更新成功的，再快照读就能看到了，这种情况可以看作一种"变相幻读"。

- [可重复读能完全避免幻读的发生吗](https://www.mianshiya.com/bank/1791003439968264194/question/1780933295484203009#heading-6)

## 面试官追问

#### 提问：SERIALIZABLE 级别具体是怎么实现的，为什么性能这么差？

>

详细解答可以看：[MySQL 中的事务隔离级别有哪些？](https://www.mianshiya.com/question/1780933295492591617)

回答：MySQL 在 SERIALIZABLE 级别下，所有 SELECT 语句都会自动加 LOCK IN SHARE MODE，相当于读也要拿共享锁。这样读和写就互斥了，写事务必须等所有读事务释放锁才能执行。高并发下锁等待时间长，吞吐量直线下降。生产环境几乎不用，除非是银行对账这种对一致性要求极高、并发量又不大的场景。

#### 提问：Spring 设置的隔离级别如果数据库不支持会怎么样？

回答：取决于 JDBC 驱动的实现。MySQL Connector/J 会静默降级到数据库支持的最接近级别。Oracle 只支持 READ_COMMITTED 和 SERIALIZABLE，设置 REPEATABLE_READ 会被当成 SERIALIZABLE 处理。PostgreSQL 比较严格，不支持的级别直接抛异常。所以跨数据库项目最好用 DEFAULT 让数据库自己决定，或者在代码里加个启动检查确认数据库支持。

#### 提问：同一个方法里调用另一个设置了不同隔离级别的方法，隔离级别是哪个？

回答：取决于事务传播行为。如果内层方法是 REQUIRED，它会加入外层事务，用外层的隔离级别，内层设置的隔离级别不生效。如果内层是 REQUIRES_NEW，会挂起外层事务新开一个，这时候内层的隔离级别才生效。所以想让不同隔离级别都生效，必须让它们跑在不同的物理事务里。
...
