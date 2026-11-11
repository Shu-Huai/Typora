# RabbitMQ 中主要有哪几个角色或者说概念？

## 回答重点

在 **RabbitMQ** 中，主要有以下几个关键角色或概念，它们构成了消息的发布和消费过程：

1. **生产者（Producer）**：负责向 RabbitMQ 发送消息的应用程序，消息会发送到交换机并最终路由到队列中。
2. **消费者（Consumer）**：从 RabbitMQ 的队列中接收消息并处理的应用程序，通常在客户端中实现。
3. **交换机（Exchange）**：用于接收生产者的消息并根据特定的路由规则，将消息转发到一个或多个队列。RabbitMQ 提供了几种不同类型的交换机，如 `Direct`、`Fanout`、`Topic` 和 `Headers`。
4. **队列（Queue）**：消息最终被路由到的存储载体，是消息暂时存放的地方，消费者从队列中取出消息并进行处理。
5. **绑定（Binding）**：将交换机和队列连接起来的桥梁，定义了交换机和队列之间的消息传递关系，可以通过路由键进一步控制消息的流向。
6. **路由键（Routing Key）**：用于确定消息的路由路径，特别是在 `Direct` 和 `Topic` 类型的交换机中，通过路由键选择性地将消息发送到符合条件的队列。

在 RabbitMQ 中还有一个 VHost（虚拟主机）概念，它其实就是一个命名空间，将资源分组，使得不同虚拟主机之间的资源互不干涉，每个 VHost 拥有自己的交换机、队列、权限设置等。

整体架构图如下：

<img src="Z:/Public/images/cX5qUkBv_image_mianshiya.webp" alt="image.png" width="100%" />

## 扩展知识

### 角色之间数据流转流程

1. **生产者发送消息**：生产者创建一个消息，并指定将消息发送到某个交换机，通常会附带一个路由键。
2. **交换机路由消息**：交换机根据绑定的路由规则决定将消息路由到哪个队列。不同类型的交换机会有不同的路由逻辑。
3. **队列存储消息**：消息被路由到指定的队列。队列负责存储消息，直到消费者来消费。
4. **消费者消费消息**：消费者监听某个队列，并从中获取消息进行处理。消费者可以是同步的也可以是异步的。

### 各角色的细分与作用

**生产者和消费者的异步解耦**：RabbitMQ 将生产者和消费者解耦，使得生产者无需关心消费者的数量、状态以及处理速度，生产和消费过程可以独立进行。

**交换机类型**：

- **Direct Exchange**：用得最多，一个 routing `key` 精确匹配一个队列，订单系统里订单创建消息走 order.create 这个 `key` 路由到订单处理队列就是典型场景。
- **Fanout Exchange**：是广播模式，压根不看 routing `key`，绑了多少队列就全部投一份。用户注册后要同时发短信、发邮件、送积分，一条消息广播给三个队列各自处理就行。
- **Topic Exchange**：支持通配符，`*` 匹配一个单词，`#` 匹配零到多个单词。日志系统里 `log.error.*` 可以匹配 log.error.payment、log.error.order，灵活订阅。
- **Headers Exchange**：看 routing `key`，根据消息头的键值对做匹配，适合复杂路由但性能差点，实际用得少。

<p align="center"><img src="Z:/Public/images/fF2sqcPu_t663Imfeer_mianshiya.webp" alt="" /></p>

### 消息可靠性保障机制

RabbitMQ 在三个环节保障消息不丢：

**生产端确认**：开启 publisher confirm 模式，消息写入队列后 broker 会回调确认。如果网络抖动导致确认丢失，生产者可以重发，业务侧做好幂等就行。

**消费端确认**：默认是自动 ack，消息一推给消费者就从队列删了。生产环境一定要改成手动 ack，业务处理完再确认，处理失败可以 nack 让消息重回队列。

```java
// 手动确认示例
channel.basicConsume(queueName, false, (consumerTag, delivery) -> {
    try {
        // 业务处理
        processMessage(delivery.getBody());
        // 处理成功，手动确认
        channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
    } catch (Exception e) {
        // 处理失败，拒绝并重新入队
        channel.basicNack(delivery.getEnvelope().getDeliveryTag(), false, true);
    }
}, consumerTag -> {});
```

**持久化配置**：队列声明时设置 durable=true，发消息时设置 deliveryMode=2，这样 broker 重启消息也不会丢。但持久化有磁盘 IO 开销，吞吐量敏感的场景要权衡。

### Connection 和 Channel 的关系

一个 TCP 连接 Connection 可以开多个 Channel，Channel 是轻量级的逻辑连接。建立 TCP 连接开销大，频繁创建销毁很浪费，所以一般复用一个 Connection，业务线程各用各的 Channel。Spring AMQP 的 CachingConnectionFactory 就是这个思路，连接池管理 Connection，按需分配 Channel。

## 面试官追问

#### 提问：如果消费者处理消息太慢导致队列堆积怎么办？

回答：堆积问题本质是消费速度跟不上生产速度。短期可以增加消费者实例数量，RabbitMQ 支持多消费者竞争消费同一个队列。长期要分析慢的原因，是业务逻辑复杂还是依赖的下游服务慢。还可以考虑开启消费者预取 prefetch，控制每个消费者手里最多持有多少条未确认消息，避免一个慢消费者拖垮整个队列。

#### 提问：RabbitMQ 的队列有长度限制吗？堆积太多会怎样？

回答：队列本身没有硬性长度限制，但可以通过 `x`-max-length 参数设置最大消息数，超出后默认丢弃队头消息。还有 `x`-max-length-bytes 限制队列总字节数。如果不设限制，消息堆积太多会把内存撑爆，触发 RabbitMQ 的流控机制，生产者会被阻塞。生产环境建议配合监控告警，堆积到阈值就扩消费者或者排查问题。

#### 提问：VHost 除了资源隔离还有什么作用？

回答：VHost 主要就是做多租户隔离，每个 VHost 有独立的权限体系，可以给不同用户分配不同 VHost 的读写权限。运维上也方便，按业务线划分 VHost 后，出问题定位范围更小，某个业务线的队列堆积不会影响其他业务线的监控指标。另外不同 VHost 可以配置不同的策略，比如消息 TTL、队列长度限制这些。
