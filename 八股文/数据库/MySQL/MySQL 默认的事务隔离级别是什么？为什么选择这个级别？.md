# MySQL 默认的事务隔离级别是什么？为什么选择这个级别？

## 回答重点

MySQL 默认隔离级别是**可重复读** Repeatable Read，简称 RR。

选择这个级别是历史原因。早期 MySQL 的 binlog 只有 statement 格式，记录的是原始 SQL 语句。在读已提交级别下，并发事务提交顺序和实际执行顺序可能不一致，binlog 重放的时候就会出错，主从数据对不上。可重复读级别有间隙锁兜底，能保证 binlog 记录顺序和执行顺序一致，所以被选为默认值。

现在 binlog 有了 row 格式，记录的是行数据变更而不是 SQL，读已提交级别也不会有主从不一致问题了。但 MySQL 一直没改默认值，向前兼容嘛。

![](Z:/Public/images/SAt3tWDt_nMj2bIEw9g_mianshiya.webp)

## 扩展知识

### binlog statement 格式导致主从不一致的例子

MySQL 主从同步靠 binlog，从库把主库的 binlog 拉过来重放，数据就同步了。

![image.png](Z:/Public/images/VAX1Jk1F_image_mianshiya.webp)

来看个具体场景。两个事务 A 和 B，按下面的时间顺序执行：

![image.png](Z:/Public/images/R6QgSD4v_image_mianshiya.webp)

读已提交级别下，事务 A 的 DELETE 执行的时候，a=5 这条还没插入呢。等事务 B 提交后 a=5 才落盘，然后事务 A 提交。最终主库里 a=5 这条记录是存在的。

问题出在 binlog 记录顺序上。事务 B 先提交，所以 INSERT 先写进 binlog，然后事务 A 提交，DELETE 后写进 binlog。

![image.png](Z:/Public/images/BizHimV7_image_mianshiya.webp)

从库重放的时候，先 INSERT a=5，再 DELETE a < 10，结果 a=5 也被删了。主库有这条记录，从库没有，数据不一致了。

### 可重复读怎么解决这个问题

可重复读级别有间隙锁。事务 A 执行 DELETE a < 10 的时候，会锁住 a < 10 这个范围内的所有间隙。事务 B 想插入 a=5，被间隙锁挡住，只能等事务 A 提交。

这样一来，事务 A 肯定先提交，binlog 里 DELETE 在前 INSERT 在后，从库重放顺序也对，数据就一致了。

![image.png](Z:/Public/images/L2wHwVOP_image_mianshiya.webp)

### 大厂为什么改用读已提交

互联网公司基本都把隔离级别调成读已提交，原因有几个：

1. binlog 现在默认用 row 格式了，记录的是数据变更不是 SQL，不存在主从不一致问题

2. 可重复读的间隙锁范围大，高并发场景锁等待严重，死锁概率也高

3. 可重复读要维护更多的 undo log 版本，长事务内存消耗大

4. 业务上大多数场景不需要“同一事务内读到的数据不变”这个保证

阿里内部规范明确要求用读已提交。用的时候把 binlog 格式改成 row 就行。

![](Z:/Public/images/tXEsMZBg_l6CHzu6MTR_mianshiya.webp)

- [1535. 你们生产环境的 MySQL 中使用了什么事务隔离级别？为什么？](https://www.mianshiya.com/question/1805421515868151810)

## 面试官追问

#### 提问：把隔离级别从可重复读改成读已提交，需要做什么配置？

扩展可以看：[MySQL 中的事务隔离级别有哪些？](https://www.mianshiya.com/question/1780933295492591617)

回答：两步。一是改 transaction_isolation 参数，可以在 my.cnf 里配，也可以 SET GLOBAL 动态改。二是把 binlog_format 改成 ROW，不然还是有主从不一致风险。改完最好重启一下让所有连接生效。

#### 提问：可重复读级别下用 row 格式 binlog，还会有主从不一致问题吗？

回答：不会。row 格式记录的是每一行的变更，不是 SQL 语句。不管事务提交顺序怎样，每一行的最终状态是确定的，从库重放结果肯定和主库一样。

#### 提问：为什么 MySQL 不把默认值改成读已提交？

回答：向前兼容。很多老系统依赖可重复读的行为，贸然改默认值会出问题。MySQL 官方的态度是让用户自己根据场景选择，不替用户做决定。
