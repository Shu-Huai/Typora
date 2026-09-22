# RabbitMQ 怎么实现延迟队列？ - 面试鸭 | 2026最新RabbitMQ 面试题+详细答案解析

## 回答重点

RabbitMQ 原生并不支持延迟消息，但可以通过两个特性组合实现：**TTL（消息存活时间）** 加上 **DLX（死信交换器）**。另外也可以用官方提供的延迟消息插件来实现。

**TTL + DLX 方案的核心思路是这样的**：给正常队列设置消息存活时间，但不配置消费者。消息在队列里待到过期后，会自动转发到绑定的死信交换器，消费者从死信队列里取消息，延迟效果就出来了。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/LRw8yRfg_image_mianshiya.webp)

如果用插件的话更直接，安装 rabbitmq-delayed-message-exchange 插件后，创建一个延迟类型的交换器，发消息时带上延迟时间参数，RabbitMQ 会自动在到期后才投递到队列。

## 扩展知识

### TTL 和 DLX 到底是什么

TTL 就是消息的存活时间，可以给整个队列统一设置，也可以给每条消息单独设置。消息一旦超过 TTL，就会被标记为过期。

DLX 是死信交换器，专门用来兜底那些"出问题"的消息。消息在原队列过期、被消费者拒绝、或者队列满了塞不下，都会被扔到 DLX。

DLX 再把消息路由到死信队列，也就是我们这里说的延迟队列。

### TTL + DLX 的时序坑

这套方案有个坑，跟队列先进先出的特性有关。假设你往同一个队列里先后发了 3 条消息，延迟时间分别是 10 秒、5 秒、2 秒。

理论上第三条消息应该最先被消费，但实际上它得等第一条 10 秒的消息过期后才能出去。只要队头的消息没消费，后面的消息全卡着。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/jmaP4h6C_image_mianshiya.webp)

怎么解决？两个思路：

1）如果延迟时间就那么几档，比如 5 秒、10 秒、30 秒，可以针对每种延迟时间各建一个队列，同一队列里的消息 TTL 一样，就不会互相阻塞了

2）直接上延迟消息插件，插件不走队列排队那套逻辑，压根没有时序问题

### 延迟消息插件的原理

插件提供了一种新的交换器类型 `x-delayed-message`。消息投递到这种交换器后，不会立刻路由到队列，而是先存到 Mnesia 里。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/TAExd436_image_mianshiya.webp)

Mnesia 是 Erlang 自带的数据库，RabbitMQ 用它来存储延迟消息的元数据和内容。

等消息的延迟时间到了，插件才会把消息投递到目标队列。整个过程对消费者透明，消费者只管从队列里取消息就行。

和 TTL + DLX 的对比：

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/MD86p7an_o3pXZIRiwm_mianshiya.webp)

更多关于插件的内容，可以查看 [github：rabbitmq-delayed-message-exchange](https://github.com/rabbitmq/rabbitmq-delayed-message-exchange)。

### TTL + DLX 代码实现

```java
public class DelayedQueueExample {

    private static final String EXCHANGE_NAME = "normal_exchange";
    private static final String DEAD_LETTER_EXCHANGE = "dead_letter_exchange";
    private static final String QUEUE_NAME = "normal_queue";
    private static final String DELAYED_QUEUE_NAME = "delayed_queue";
    private static final String ROUTING_KEY = "routing_key";

    public static void main(String[] args) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        try (Connection connection = factory.newConnection(); Channel channel = connection.createChannel()) {
            // 声明死信交换器
            channel.exchangeDeclare(DEAD_LETTER_EXCHANGE, BuiltinExchangeType.DIRECT);

            // 声明延迟队列（用于接收过期消息）
            channel.queueDeclare(DELAYED_QUEUE_NAME, true, false, false, null);
            channel.queueBind(DELAYED_QUEUE_NAME, DEAD_LETTER_EXCHANGE, ROUTING_KEY);

            // 声明正常交换器
            channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.DIRECT);

            // 配置带有死信交换器的正常队列
            Map<String, Object> argsMap = new HashMap<>();
            argsMap.put("x-dead-letter-exchange", DEAD_LETTER_EXCHANGE);
            argsMap.put("x-dead-letter-routing-key", ROUTING_KEY);
            argsMap.put("x-message-ttl", 5000); // 消息的TTL为5秒

            channel.queueDeclare(QUEUE_NAME, true, false, false, argsMap);
            channel.queueBind(QUEUE_NAME, EXCHANGE_NAME, ROUTING_KEY);

            // 向正常交换器发送消息
            String message = "This is a delayed message!";
            channel.basicPublish(EXCHANGE_NAME, ROUTING_KEY, null, message.getBytes(StandardCharsets.UTF_8));
            System.out.println("Sent message: " + message);
        }
    }
}
```

### 延迟插件代码实现

先启用插件：

```bash
rabbitmq-plugins enable rabbitmq_delayed_message_exchange
```

然后用代码创建延迟交换器并发送消息：

```java
public class RabbitMQDelayedExchange {
    private static final String DELAYED_EXCHANGE = "delayed_exchange";
    private static final String DELAYED_QUEUE = "delayed_queue";

    public static void main(String[] args) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {

            // 声明延迟交换机
            Map<String, Object> argsMap = new HashMap<>();
            argsMap.put("x-delayed-type", BuiltinExchangeType.DIRECT.getType());

            channel.exchangeDeclare(DELAYED_EXCHANGE, "x-delayed-message", true, false, argsMap);
            channel.queueDeclare(DELAYED_QUEUE, true, false, false, null);
            channel.queueBind(DELAYED_QUEUE, DELAYED_EXCHANGE, "");

            // 发送带有延迟时间的消息
            String message = "This is a delayed message";
            Map<String, Object> headers = new HashMap<>();
            headers.put("x-delay", 10000);  // 延迟 10 秒

            AMQP.BasicProperties properties = new AMQP.BasicProperties.Builder()
                    .headers(headers)
                    .build();

            channel.basicPublish(DELAYED_EXCHANGE, "", properties, message.getBytes("UTF-8"));
            System.out.println("Message sent with delay: " + message);
        }
    }
}
```

## 面试官追问

#### 提问：TTL + DLX 方案中，如果消息量很大，死信队列会不会成为瓶颈？

回答：会的，死信队列本质上还是个普通队列，消息量大了一样扛不住。几个缓解思路：把死信队列也做成多个，按业务类型或延迟时间分流；消费者端开多个 channel 并行消费；或者直接换成延迟插件，插件用 Mnesia 存储，不走队列那套机制。

#### 提问：延迟消息插件对性能有什么影响？大量延迟消息堆积会有问题吗？

回答：插件把消息存到 Mnesia 里，Mnesia 是内存 + 磁盘的混合存储，大量消息堆积会占用内存。官方建议延迟消息量控制在百万级以下。如果业务需要更大量级的延迟消息，可以考虑用 RocketMQ 或者基于 Redis 的方案。

#### 提问：除了 RabbitMQ，还有什么消息队列原生支持延迟消息？

回答：RocketMQ 从 4.x 版本开始就原生支持延迟消息，不过早期版本只支持 18 个固定延迟级别，5.0 之后才支持任意时间延迟。Kafka 原生不支持，得靠外部调度器配合实现。Pulsar 也原生支持延迟消息，实现思路和 RocketMQ 类似。
...
