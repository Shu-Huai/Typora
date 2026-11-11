# 说一下 RabbitMQ 的事务机制？

## 回答重点

RabbitMQ 的**事务机制**是保证消息发送原子性的手段，一批消息要么全发成功，要么全部回滚。注意，这里说的事务和数据库的 ACID 事务不是一回事，它只管消息发送这一个环节，不涉及消费端，也不是分布式事务。

事务操作就三个命令：

1. `txSelect` 开启事务模式，告诉 Broker 接下来的操作要走事务。
2. `txCommit` 提交事务，Broker 确认收到所有消息后返回成功。
3. `txRollback` 回滚事务，把这次事务里发的消息全部丢弃。

<img src="Z:/Public/images/fxEy4tcM_image_mianshiya.webp" alt="image.png" width="100%" />

代码写起来很简单：

```java
Channel channel = connection.createChannel();
channel.txSelect();  // 开启事务
try {
    channel.basicPublish("exchange", "order.create", null, msg1.getBytes());
    channel.basicPublish("exchange", "order.pay", null, msg2.getBytes());
    channel.txCommit();  // 两条消息一起提交
} catch (Exception e) {
    channel.txRollback();  // 出异常就全部回滚
}
```

但事务机制有个致命问题：太慢了。

开启事务后每次 commit 都要等 Broker 同步刷盘确认，吞吐量直接掉一个数量级。实测普通模式能到 1 万条/秒，开事务可能只剩几百条/秒。所以生产环境基本不用事务，都用 Publisher Confirm 替代。

## 扩展知识

### 为什么事务这么慢

事务模式下，`txCommit` 是同步阻塞的。生产者发完消息调用 commit，要等 Broker 把消息写到内存、可能还要刷到磁盘，然后给生产者回一个确认，生产者才能继续。这一来一回的网络往返加上磁盘 IO，延迟就上去了。

<p align="center"><img src="Z:/Public/images/KC9Yh9nF_DcCMBt8PEf_mianshiya.webp" alt="" /></p>

更要命的是，事务期间 Channel 被锁住，其他操作都得等着。如果一个事务里发 100 条消息，中间某条抛异常了，前面 99 条也得回滚重发。

### Publisher Confirm 为什么更好

Publisher Confirm 是 RabbitMQ 2.1 引入的，设计初衷就是替代事务。它的思路是异步确认：消息发出去后不阻塞，Broker 处理完了异步回调通知你。

三种确认方式：

1. 单条同步确认。发一条调一次 `waitForConfirms()`，和事务差不多慢，但至少省了 txSelect 的开销。

2. 批量同步确认。攒一批消息再调 `waitForConfirms()`，吞吐量上来了，但有条失败整批要重发，定位问题麻烦。

3. 异步确认。注册一个 `ConfirmListener`，Broker 确认后回调 `handleAck` 或 `handleNack`。这种方式吞吐量最高，和非事务模式差不多，还能精确知道哪条消息失败了。

```java
channel.confirmSelect();  // 开启 confirm 模式
channel.addConfirmListener((deliveryTag, multiple) -> {
    // 消息发送成功
}, (deliveryTag, multiple) -> {
    // 消息发送失败，需要重发
});

channel.basicPublish("exchange", "routingKey", null, msg.getBytes());
// 不用等待，继续发下一条
```

### 事务 vs Confirm 对比

| 维度 | 事务模式 | Publisher Confirm |
|------|----------|-------------------|
| 吞吐量 | 约 500 条/秒 | 异步模式可达 10000+ 条/秒 |
| 延迟 | 每批消息同步等待 | 异步模式无阻塞 |
| 失败处理 | 整批回滚 | 精确到单条 nack |
| 批量操作 | 天然支持 | 需要自己维护批次 |
| 使用复杂度 | 简单，try-catch 搞定 | 异步模式需要处理回调 |

什么时候用事务？说实话，几乎没有场景非用事务不可。唯一可能的场景是需要严格的批量原子性，比如一批消息必须全部成功或全部失败，不能有部分成功的情况。但这种需求也可以在业务层面用补偿机制实现。

### Spring AMQP 的封装

Spring AMQP 对事务做了封装，配合 Spring 的事务管理器用起来更顺手：

```java
@Transactional
public void sendBatchMessages() {
    rabbitTemplate.convertAndSend("exchange", "key1", "msg1");
    rabbitTemplate.convertAndSend("exchange", "key2", "msg2");
    // 方法结束自动 commit，异常自动 rollback
}
```

但要注意，RabbitMQ 事务和数据库事务是两回事，不能混在一起期望 ACID 特性。

比如往数据库插数据 + 发消息，数据库回滚了消息可能已经发出去了。要实现这种场景的一致性，得用本地消息表或者 RocketMQ 的事务消息。

## 面试官追问

#### 提问：事务模式和 Confirm 模式可以同时开吗？

回答：不行，互斥的。一个 Channel 要么是事务模式，要么是 Confirm 模式，不能两个都开。调了 `txSelect` 之后再调 `confirmSelect` 会报错。底层实现上，事务用的是同步阻塞机制，Confirm 用的是异步回调机制，两套逻辑没法兼容。

#### 提问：如果 Confirm 模式下 Broker 一直不回 ack，消息会怎样？

回答：消息不会丢，但生产者不知道成功没成功。实际开发要设超时机制，用 `waitForConfirmsOrDie(timeout)` 等待指定时间，超时就当失败处理，重发或者记日志人工处理。异步模式下可以自己维护一个待确认消息的 Map，定期扫描超时的进行重发。

#### 提问：事务回滚后消息去哪了？

回答：直接丢弃，不会进死信队列，也不会有任何痕迹。事务模式下，消息在 commit 之前只是暂存在 Broker 内存里，rollback 就清掉了。所以回滚后如果还需要这些消息，得生产者自己重新发。

#### 提问：RabbitMQ 的事务能保证消费端也成功吗？

回答：保证不了。RabbitMQ 的事务只管生产端到 Broker 这一段，消息进了队列之后，消费者拉走、处理、ack，这些都不在事务范围内。要保证端到端的可靠性，得消费端配合：手动 ack、幂等消费、失败重试机制都得有。
