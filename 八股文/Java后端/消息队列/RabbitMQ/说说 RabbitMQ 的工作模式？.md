# 说说 RabbitMQ 的工作模式？

## 回答重点

RabbitMQ 的工作模式本质上是对 **生产者、交换机、队列、消费者** 这几个角色的不同组合方式。

官方文档里列了 7 种常见模式：

1. **简单模式（Simple Queue）**：生产者向一个队列发送消息，单个消费者从该队列中消费消息，是最基本的点对点模式。
2. **工作队列模式（Work Queue）**：一个生产者将消息发送到队列中，多个消费者可以同时监听该队列，实现消息的负载均衡，常用于任务分发。
3. **发布/订阅模式（Publish/Subscribe）**：生产者将消息发送到交换机（通常为 Fanout 类型），所有绑定到该交换机的队列都会接收到消息，适合广播消息的场景。
4. **路由模式（Routing）**：生产者将消息发送到带有路由键的 Direct 交换机，不同路由键的消息会被路由到不同的队列，消费者可以选择性订阅感兴趣的消息。
5. **主题模式（Topic）**：使用 Topic 交换机，支持基于路由键的模糊匹配，将消息路由到匹配的队列中，适用于复杂的多条件路由需求。
6. **RPC 模式（Remote Procedure Call）**：实现远程过程调用，通常用于客户端请求服务器的响应，实现双向通信。
7. **发布确认模式（Publisher Confirms）**：确保生产者消息发送的可靠性，适合需要确保消息成功到达队列的场景。

<p align="center"><img src="Z:/Public/images/jXBvz3zS_u9Hlvlhhd0_mianshiya.webp" alt="" /></p>

## 扩展知识

### 简单模式

最基础的模式，一个生产者往队列里扔消息，一个消费者从队列里取消息处理。适合消息量小、逻辑简单的场景，比如发送验证码、单个任务触发。

<img src="Z:/Public/images/oN04D5bu_image_mianshiya.webp" alt="image.png" width="820px" />

### 工作队列模式

多个消费者监听同一个队列，消息默认按轮询方式分发。这个模式天然支持水平扩展，任务堆积时加消费者实例就能提升处理能力。

<img src="Z:/Public/images/fLDuMXnW_image_mianshiya.webp" alt="image.png" width="824px" />

实际使用中要注意 prefetch 参数的设置。默认情况下 RabbitMQ 会尽可能多地把消息推给消费者，如果某个消费者处理慢，会导致消息堆积在它那里，其他空闲的消费者反而没活干。设置 `prefetch=1` 可以保证每个消费者手里最多只有一条未确认的消息，实现真正的能者多劳。

```java
// 设置每次只取一条消息
channel.basicQos(1);
```

### 发布订阅模式

Fanout 交换机不看 routing `key`，直接把消息广播给所有绑定的队列。典型场景是用户注册后要同时发短信、发邮件、送积分，一条消息广播给三个队列，三个服务各取所需互不干扰。

<img src="Z:/Public/images/ndKUytoh_image_mianshiya.webp" alt="image.png" width="796px" />

### 路由模式

Direct 交换机按 routing `key` 精确匹配。日志系统是典型场景，error 级别的日志路由到告警队列触发通知，info 级别的路由到存储队列只做归档，通过不同的 routing `key` 分流处理。

<img src="Z:/Public/images/NcAuRMIi_image_mianshiya.webp" alt="image.png" width="782px" />

### 主题模式

Topic 交换机支持通配符，比 Direct 更灵活。binding `key` 里 `*` 匹配一个单词，`#` 匹配零到多个单词。比如 `log.error.*` 能匹配 log.error.payment、log.error.order，`log.#` 能匹配所有 log 开头的消息。

<img src="Z:/Public/images/xbmaRdts_image_mianshiya.webp" alt="image.png" width="810px" />

Topic 模式是最灵活的，Direct 和 Fanout 能实现的场景 Topic 都能覆盖。但通配符匹配有性能开销，如果只需要精确匹配还是用 Direct 更高效。

### RPC 模式

用消息队列实现同步调用的效果。客户端发请求时带上 correlation_id 和 reply_to 队列，服务端处理完把结果发到 reply_to 队列，客户端根据 correlation_id 找到对应的响应。

<img src="Z:/Public/images/fRaOoGek_image_mianshiya.webp" alt="image.png" width="822px" />

这个模式在微服务场景下用得不多，因为有 Dubbo、gRPC 这些专门的 RPC 框架更好用。RabbitMQ 的 RPC 模式更适合跨语言调用或者已有 RabbitMQ 基础设施想复用的场景。

### 发布确认模式

这个严格说不是独立的工作模式，而是生产者端的可靠性保障机制。

开启 confirm 模式后，每条消息发出去 broker 都会异步回调告诉你成功还是失败。金融、交易类场景必开，普通业务消息可以根据丢消息的容忍度决定是否开启。

```java
// 开启发布确认
channel.confirmSelect();
// 异步确认回调
channel.addConfirmListener((deliveryTag, multiple) -> {
    // 消息确认成功
}, (deliveryTag, multiple) -> {
    // 消息确认失败，需要重发
});
```

## 面试官追问

#### 提问：Work Queue 模式下，如果一个消费者处理到一半挂了，消息会丢吗？

回答：看 ack 机制怎么配的。如果是自动 ack，消息推给消费者就从队列删了，消费者挂了消息就丢了。生产环境一定要用手动 ack，消费者处理完再确认。如果处理到一半挂了，RabbitMQ 检测到连接断开会把消息重新放回队列，分发给其他消费者。当然业务侧要做好幂等，防止重复消费。

#### 提问：Fanout 和 Topic 都能实现广播，什么时候用哪个？

回答：Fanout 是无差别广播，绑了多少队列就发多少份，不看 routing `key`。Topic 可以做条件广播，消费者通过 binding `key` 的通配符选择性订阅。如果所有消费者都要收全量消息，用 Fanout 更简单高效。如果不同消费者要收不同类型的消息，用 Topic 更灵活。

#### 提问：RPC 模式相比直接用 HTTP 调用有什么优势？

回答：RPC over MQ 的好处是解耦和削峰。调用方不需要知道服务方的地址，服务方可以水平扩展多个实例竞争消费请求。请求量大的时候队列能起到缓冲作用，不会把服务方打挂。缺点是链路变长了，延迟比直连高，排查问题也更麻烦。对实时性要求高的场景还是直接 RPC 更合适。
