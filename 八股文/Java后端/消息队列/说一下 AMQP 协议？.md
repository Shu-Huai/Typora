# 说一下 AMQP 协议？

## 回答重点

**AMQP**（Advanced Message Queuing Protocol）是应用层消息传输协议，定义了消息如何发送、路由和存储，就像 HTTP 定义 Web 请求格式一样。RabbitMQ、ActiveMQ、Qpid 等中间件都实现了 AMQP。

AMQP 支持跨语言、跨平台通信。Java 生产者、Python 消费者和 .NET 服务只要遵循同一协议就能互相通信，不局限于 Java 生态。

核心模型包括：

1. **Connection**：客户端与 Broker 之间的 TCP 长连接。
2. **Channel**：Connection 上的逻辑连接。TCP 连接建立成本高，一个 Connection 可以复用多个 Channel，适合多线程收发消息。
3. **Exchange**：交换机，生产者先把消息发到 Exchange，再由 Exchange 按路由规则分发到队列。
4. **Queue**：真正存储消息的地方，消费者从 Queue 消费。
5. **Binding**：Exchange 与 Queue 的绑定关系，通常带有 routing `key`。

![AMQP 核心模型](Z:/Public/images/9lRmuoQ6_image_mianshiya.webp)

## 扩展知识

### 四种交换机类型

![Exchange 类型](Z:/Public/images/78l44Vzk_kZqqQjcHbE_mianshiya.webp)

- **Direct**：按 routing `key` 精确匹配。例如 `order.create` 只发送给绑定了该 `key` 的队列。
- **Fanout**：忽略 routing `key`，广播给所有绑定队列。日志存储、监控和告警等场景常用。
- **Topic**：支持通配符，`*` 匹配一个单词，`#` 匹配零个或多个单词。例如 `order.#` 可匹配 `order.create`、`order.pay` 和 `order.cancel.timeout`。
- **Headers**：根据消息头键值对匹配，可配置 `all` 或 `any`。灵活但性能较差，实际使用较少。

### 消息可靠性保障

AMQP 在协议层面提供了多种可靠性机制：

**消息确认**分为两种：

- Publisher Confirm：生产者发送后，Broker 返回确认表示消息已接收。
- Consumer Acknowledge：消费者处理完成后返回 ack，Broker 才删除消息；消费者宕机未确认时，消息会重新投递。

**持久化**也分两层：队列持久化使用 `durable=true`，消息持久化使用 `deliveryMode=2`。两者都开启才能在 Broker 重启后尽可能保证消息不丢失。

**事务机制**可以将多条消息作为一个原子操作：`txSelect` 开启事务，`txCommit` 提交，`txRollback` 回滚。但事务会显著降低吞吐量，生产环境通常使用 Publisher Confirm 替代。

### AMQP 0-9-1 与 AMQP 1.0

两个版本差别较大且不兼容：

- **AMQP 0-9-1**：RabbitMQ 使用的版本，包含 Exchange、Queue、Binding 等模型。
- **AMQP 1.0**：由 OASIS 标准化，简化了模型，主要定义消息格式和传输协议，路由逻辑交给具体实现。Azure Service Bus、Apache ActiveMQ Artemis 使用该版本。

面试中默认提到 AMQP 通常指 0-9-1；如果追问版本差异，可以说明 1.0 去掉了 Exchange 和 Binding 的具体概念，保留消息容器和传输能力。

## 面试官追问

#### 提问：Channel 和 Connection 是什么关系，为什么不直接用 Connection？

回答：Connection 是 TCP 连接，建立成本高；Channel 是 Connection 上的虚拟连接，创建和销毁更轻量。一个应用有多个线程时，为每个线程建立 Connection 会浪费资源，复用一个 Connection、为线程创建 Channel 更合适。Channel 之间相互隔离，一个 Channel 出问题通常不影响其他 Channel。RabbitMQ 一般建议一个线程使用一个 Channel，不要多线程共享同一个 Channel。

#### 提问：消息确认机制中的 ack 和 nack 有什么区别？

回答：ack 表示消费成功，Broker 可以删除消息；nack 表示消费失败，可以通过 `requeue` 参数决定重新入队还是进入死信队列。`reject` 也表示拒绝，但只能拒绝单条消息，nack 可以批量拒绝，实际开发通常使用 nack。

#### 提问：RabbitMQ 的 Publisher Confirm 模式和事务模式怎么选？

回答：优先使用 Confirm 模式。事务模式同步等待 Broker 确认，吞吐量可能降到原来的十分之一；Confirm 模式是异步回调，生产者可以持续发送消息。如果需要等待确认，可使用 `waitForConfirms`，通常也比事务模式性能更好。事务模式的批量回滚能力很少成为必须需求。
