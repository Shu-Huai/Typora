# RabbitMQ 中无法路由的消息会去到哪里？

## 回答重点

RabbitMQ 中消息无法路由时，默认行为是直接丢弃，不会有任何提示。

但实际生产环境肯定不能让消息悄悄消失，所以有三种机制来处理这种情况：

1. **备份交换机**：给主交换机配一个 Alternate Exchange，无法路由的消息会自动转发到备份交换机，再由备份交换机根据它的绑定关系决定怎么处理。比如备份交换机用 fanout 类型，绑一个专门存储未路由消息的队列。

2. **消息回退机制**：生产者发消息时设置 mandatory=true，如果消息无法路由，RabbitMQ 会把消息退回给生产者。生产者通过 Return Listener 监听这些退回的消息，可以自己决定是重发、记日志还是报警。

3. **死信队列**：严格来说死信队列处理的不是“无法路由”的消息，而是被拒绝、过期或队列满了被挤掉的消息。但在某些场景下可以配合使用，作为兜底方案。

> 强调下：死信队列处理的是消息已经进入队列之后发生的问题，严格来说和“无法路由”是两个不同阶段的事情，仅作兜底补充。

<img src="Z:/Public/images/ZH6wj24c_image_mianshiya.webp" alt="image.png" width="100%" />

## 扩展知识

### 备份交换机的配置和原理

备份交换机是 RabbitMQ 处理未路由消息最常用的方式。

配置时需要在声明主交换机时通过 alternate-exchange 参数指定：

```java
Map<String, Object> args = new HashMap<>();
args.put("alternate-exchange", "my-alternate-exchange");
channel.exchangeDeclare("main-exchange", "direct", true, false, args);
channel.exchangeDeclare("my-alternate-exchange", "fanout", true);
channel.queueDeclare("unrouted-messages", true, false, false, null);
channel.queueBind("unrouted-messages", "my-alternate-exchange", "");
```

备份交换机一般用 fanout 类型，因为它不关心 routing `key`，能确保所有转发过来的消息都能进到绑定的队列里。

<p align="center"><img src="Z:/Public/images/Mc20dxNy_pXGUsmZC4v_mianshiya.webp" alt="" /></p>

有个细节要注意：如果备份交换机也找不到匹配的队列，消息还是会丢。所以备份交换机用 fanout 类型加一个兜底队列是最稳妥的配置。

### 消息回退机制的使用场景

mandatory 参数控制的是消息在交换机层面无法路由时的行为。设置为 true 时，无法路由的消息会通过 Basic.Return 命令返回给生产者：

```java
channel.addReturnListener((replyCode, replyText, exchange, routingKey, properties, body) -> {
    System.out.println("消息被退回: " + new String(body));
    System.out.println("原因: " + replyText);
    // 可以在这里做重发、记录日志或报警
});

// mandatory 参数为 true
channel.basicPublish("exchange", "routing-key", true, MessageProperties.PERSISTENT_TEXT_PLAIN, "message".getBytes());
```

这种方式的好处是生产者能感知到消息没有被成功路由，可以做针对性处理。

缺点是增加了生产者的复杂度，而且如果生产者挂了，退回的消息也就丢了。

### 死信队列触发的三种场景

死信队列和备份交换机是两个不同的概念，很多人容易搞混。

死信是消息已经进入队列之后，因为某些原因被“判死刑”：

1. 消息被消费者拒绝，并且 requeue=false
2. 消息 TTL 过期
3. 队列达到最大长度，新消息把老消息挤掉

配置死信队列需要在声明队列时指定 `x`-dead-letter-exchange：

```java
Map<String, Object> args = new HashMap<>();
args.put("x-dead-letter-exchange", "dlx-exchange");
args.put("x-dead-letter-routing-key", "dlx-key");
channel.queueDeclare("business-queue", true, false, false, args);
```

### 三种机制的选择

| 机制 | 处理时机 | 适用场景 |
|------|----------|----------|
| 备份交换机 | 消息在交换机层面无法路由 | 需要统一收集未路由消息、后续批量处理 |
| Return Listener | 消息在交换机层面无法路由 | 生产者需要实时感知并自行处理 |
| 死信队列 | 消息进入队列后被拒绝/过期/溢出 | 消费失败的消息需要重试或人工介入 |

实际项目中这三种机制经常组合使用。比如用备份交换机兜底未路由消息，用死信队列处理消费失败的消息，用 Return Listener 做实时监控报警。

## 面试官追问

#### 提问：备份交换机和死信队列能同时配置吗？它们会冲突吗？

回答：可以同时配置，不会冲突，因为它们作用在不同阶段。备份交换机处理的是消息在交换机层面无法路由的情况，消息压根没进到队列。死信队列处理的是消息已经进入队列后被拒绝、过期或被挤掉的情况。一条消息不可能同时触发这两个机制，要么在交换机层面就被转发到备份交换机了，要么进了队列之后才可能变成死信。

#### 提问：mandatory 和备份交换机都配置了，消息无法路由时走哪个？

回答：备份交换机优先级更高。如果配置了备份交换机，无法路由的消息会直接转发到备份交换机，不会触发 Return Listener。只有在没有配置备份交换机，或者备份交换机也路由失败的情况下，才会触发 Return Listener 把消息退回给生产者。

#### 提问：死信队列的消息格式和原消息有什么区别？

回答：死信消息会被 RabbitMQ 自动添加一些 header 信息，包括 `x`-death 数组，里面记录了消息成为死信的原因、原队列名、原交换机名、原 routing `key`、死亡时间和重试次数。通过这些信息可以追溯消息的来源和死亡原因，方便排查问题或者做重试逻辑。
