# RabbitMQ

## RabbitMQ 的概念

RabbitMQ 是一个消息中间件：它接受并转发消息。你可以把它当做一个快递站点，当你要发送一个包时，你把你的包裹放到快递站，快递员最终会把你的快递送到收件人那里，按照这种逻辑 RabbitMQ 是 一个快递站，一个快递员帮你传递快件。RabbitMQ 与快递站的主要区别在于，它不处理快件而是接收，存储和转发消息数据。

![image-20211230172733814](http://public.file.lvshuhuai.cn/images\image-20211230172733814.png)

RabbitMQ 是一个开源的，在 AMQP 基础上完整的，可复用的企业消息系统。

AMQP，即 Advanced Message Queuing Protocol（高级消息队列协议），是一个网络协议，是应用层协议的一个开放标准，为面向消息的中间件设计。基于此协议的客户端与消息中间件可传递消息，并不受客户端/中间件不同产品，不同的开发语言等条件的限制。2006 年，AMQP 规范发布。

## 核心概念

![image-20211230172747783](http://public.file.lvshuhuai.cn/images\image-20211230172747783.png)

**Broker**：接收和分发消息的应用，RabbitMQ Server 就是 Message Broker。

**Virtual host**：虚拟主机，出于多租户和安全因素设计的，把 AMQP 的基本组件划分到一个虚拟的分组中，类似于网络中的 namespace 概念。当多个不同的用户使用同一个 RabbitMQ server 提供的服务时，可以划分出多个 vhost，每个用户在自己的 vhost 创建 exchange／queue 等，每一个虚拟主机都有 AMQP 的全套基础组件，并且可以针对每个虚拟主机进行权限以及数据分配，并且不同虚拟主机之间是完全隔离的。

**Connection**：客户端与 RabbitMQ 进行交互，首先就需要建立一个 TCP 连接。RabbitMQ 为了减少性能开销，也会在一个 Connection 中建立多个 Channel，这样便于客户端进行多线程连接，这些连接会复用同一个 Connection 的 TCP 通道，提高性能。

**Channel**：客户端与 RabbitMQ 建立了连接，就会分配一个 AMQP 信道 Channel。每个信道都会被分配一个唯一的 ID。

**Exchange**：消息队列交换机，消息发送到 RabbitMQ 中后，会首先进入一个交换机，然后由交换机负责将数据转发到不同的队列中。RabbitMQ 中有多种不同类型的交换机来支持不同的路由策略。交换机多用来与生产者打交道。生产者发送的消息通过 Exchange 交换机分配到各个不同的 Queue 队列上，而对于消息消费者来说，通常只需要关注自己的队列就可以了。

**Queue**：消息队列，队列是实际保存数据的最小单位。队列结构天生就具有 FIFO 的顺序。

**Producer**：消息生产者，即生产方客户端，生产方客户端将消息发送

**Consumer**：消息消费者，即消费方客户端，接收 MQ 转发的消息。

**Binding**：exchange 和 queue 之间的虚拟连接，binding 中可以包含 routing key，Binding 信息被保存到 exchange 中的查询表中，用于 message 的分发依据。

## 交换机和交换机类型

**服务器发送消息不会直接发送到队列中（Queue），只能将消息发送给交换机（Exchange）**，然后根据确定的规则，RabbitMQ 将会决定消息该投递到哪个队列。这些规则称为**路由键（routing key）**，队列通过路由键绑定到交换机上。消息发送到服务器端（broker），消息也有自己的路由键（也可以是空），RabbitMQ 也会将消息和消息指定发送的交换机的绑定（binding，就是队列和交互机的根据路由键映射的关系）的路由键进行匹配。

如果匹配的话，就会将消息投递到相应的队列。交换机工作的内容非常简单，一方面它接收来自生产者的消息，另一方面将它们推入队列。交换机必须确切知道如何处理收到的消息。是应该把这些消息放到特定队列还是说把他们到许多队列中还是说应该丢弃它们。这就的由交换机的类型来决定。

交换机是用来发送消息的 AMQP 实体。交换机拿到一个消息之后将它路由给一个或零个队列。它使用哪种路由算法是由交换机类型和被称作绑定（bindings）的规则所决定的。AMQP 0-9-1 的代理提供了四种交换机。

| **Name（交换机类型）**           | **Default pre-declared names（预声明的默认名称）** |
| -------------------------------- | -------------------------------------------------- |
| Direct exchange（直连交换机）    | (Empty string) and amq.direct                      |
| Fanout exchange（扇型交换机）    | amq.fanout                                         |
| **Topic exchange（主题交换机）** | amq.topic                                          |
| Headers exchange（头交换机）     | amq.match (and amq.headers in RabbitMQ)            |

除交换机类型外，在声明交换机时还可以附带许多其他的属性，其中最重要的几个分别是：

- Name
- Durability （消息代理重启后，交换机是否还存在）
- Auto-delete （当所有与之绑定的消息队列都完成了对此交换机的使用后，删掉它）
- Arguments（依赖代理本身）

交换机可以有两个状态：持久（durable）、暂存（transient）。持久化的交换机会在消息代理（broker）重启后依旧存在，而暂存的交换机则不会（它们需要在代理再次上线后重新被声明）。然而并不是所有的应用场景都需要持久化的交换机。

### Direct Exchange

将消息中的 Routing key 与该 Exchange 关联的所有 Binding 中的 Routing key 进行比较，**如果相等**，则发送到该 Binding 对应的 Queue 中。

![image-20211230172801166](http://public.file.lvshuhuai.cn/images\image-20211230172801166.png)

### Topic Exchange

将消息中的 Routing key 与该 Exchange 关联的所有 Binding 中的 Routing key 进行对比，**如果匹配上了**，则发送到该 Binding 对应的 Queue 中。

![image-20211230172811483](http://public.file.lvshuhuai.cn/images\image-20211230172811483.png)

#### topic 要求

发送到类型是 topic 交换机的消息的 routing_key 不能随意写，必须满足一定的要求，**它必须是一个单词列表，以点号分隔开。**这些单词可以是任意单词，比如说：`stock.usd.nyse`，`nyse.vmw`，`quick.orange.rabbit` 这种类型的。**当然这个单词列表最多不能超过 255 个字节。**

#### 规则

在这个规则列表中，其中有两个替换符是大家需要注意的。

`*`**（星号）可以代替一个单词**

`#`**（井号）可以替代零个或多个单词**

#### 注意

- 当一个队列绑定键是 `#`，那么这个队列将接收所有数据，就有点像 fanout 了
- 如果队列绑定键当中没有 `#` 和 `*` 出现，那么该队列绑定类型就是 direct 了

### Fanout Exchange

直接将消息转发到所有 binding 的对应 queue 中，这种 exchange 在路由转发的时候，**忽略 Routing key**。

![image-20211230172824713](http://public.file.lvshuhuai.cn/images\image-20211230172824713.png)

### Headers Exchange

**将消息中的 headers 与该 Exchange 相关联的所有 Binging 中的参数进行匹配**，如果匹配上了，则发送到该 Binding 对应的 Queue 中。

### 六大模式

#### 简单模式

![image-20211230172833658](http://public.file.lvshuhuai.cn/images\image-20211230172833658.png)

最直接的方式，P 端发送一个消息到一个指定的 queue，中间不需要任何 exchange 规则。C 端按 queue 方式进行消费。

在上图的模型中，有以下概念：

- P：生产者，也就是要发送消息的程序
- C：消费者，消息的接受者。
- queue：消息队列，图中红色部分。可以缓存消息；生产者向其中投递消息，消费者从其中取出消息。
- 一个生产者、一个消费者，不需要设置交换机（使用默认的交换机）。

**producer**

```java
channel.queueDeclare(QUEUE_NAME, false, false, false, null);
channel.basicPublish("", QUEUE_NAME, null, message.getBytes("UTF-8"));
```

**consumer**

```java
channel.queueDeclare(QUEUE_NAME, false, false, false, null);
```

#### 工作模式

![image-20211230172845711](http://public.file.lvshuhuai.cn/images\image-20211230172845711.png)

Work Queues 与简单模式相比，多了一个或一些消费端，多个消费端共同消费同一个队列中的消息。**一个消息只会被一个消费者消费**。

一个生产者、多个消费者（竞争关系），不需要设置交换机（使用默认的交换机）。

应用场景：对于任务过重或任务较多情况使用工作队列可以提高任务处理的速度。

**producer**

```java
channel.queueDeclare(TASK_QUEUE_NAME, true, false, false, null); 
channel.basicPublish("", TASK_QUEUE_NAME, MessageProperties.PERSISTENT_TEXT_PLAIN,
        message.getBytes("UTF-8"));
```

**consumer**

```java
channel.queueDeclare(TASK_QUEUE_NAME, true, false, false, null);
channel.basicQos(1);
channel.basicConsume(TASK_QUEUE_NAME, false, consumer);
```

#### 发布订阅模式

![image-20211230172957861](http://public.file.lvshuhuai.cn/images\image-20211230172957861.png)

**exchange type 是 fanout** 。

在订阅模型中，多了一个 Exchange 角色，而且过程略有变化：

- P：生产者，也就是要发送消息的程序，但是不再发送到队列中，而是发给X（交换机）
- C：消费者，消息的接收者
- Queue：消息队列，接收消息、缓存消息
- Exchange：交换机（X）。一方面，接收生产者发送的消息。另一方面，知道如何处理消息，例如递交给某个特别队列、递交给所有队列、或是将消息丢弃。到底如何操作，取决于 Exchange 的类型。

Exchange（交换机）只负责转发消息，不具备存储消息的能力，因此如果没有任何队列与 Exchange 绑定，或者没有符合路由规则的队列，那么消息会丢失！producer 只负责发送消息，至于消息进入哪个 queue，由 exchange 来分配。

**使用场景**：所有消费者获得相同的消息，例如天气预报。

**producer**

```java
channel.exchangeDeclare(EXCHANGE_NAME, "fanout");
channel.basicPublish(EXCHANGE_NAME, "", null, message.getBytes("UTF-8"));
```

**consumer**

```java
channel.exchangeDeclare(EXCHANGE_NAME, "fanout");
String queueName = channel.queueDeclare().getQueue();
channel.queueBind(queueName, EXCHANGE_NAME, "");
```

发布订阅模式与工作队列模式的区别：

工作队列模式不用定义交换机，而发布/订阅模式需要定义交换机

发布 / 订阅模式的生产方是面向交换机发送消息，工作队列模式的生产方是面向队列发送消息（底层使用默认交换机）

发布 / 订阅模式需要设置队列和交换机的绑定，工作队列模式不需要设置，实际上工作队列模式会将队列绑定到默认的交换机

#### 路由模式

![image-20211230173014717](http://public.file.lvshuhuai.cn/images\image-20211230173014717.png)

**exchange type 是 direct**

- P：生产者，向 Exchange 发送消息，发送消息时，会指定一个 routing key
- X：Exchange（交换机），接收生产者的消息，然后把消息递交给与 routing key 完全匹配的队列
- C1：消费者，其所在队列指定了需要 routing key 为 error 的消息
- C2：消费者，其所在队列指定了需要 routing key 为 info、error、warning 的消息

路由模式要求队列在绑定交换机时要指定 routing key，消息会转发到符合 routing key 的队列。

**producer**

```java
channel.exchangeDeclare(EXCHANGE_NAME, "direct");
channel.basicPublish(EXCHANGE_NAME, routingKey, null, message.getBytes("UTF-8"));
```

**consumer**

```java
channel.exchangeDeclare(EXCHANGE_NAME, "direct");
channel.queueBind(queueName, EXCHANGE_NAME, routingKey1);
channel.queueBind(queueName, EXCHANGE_NAME, routingKey2);
channel.basicConsume(queueName, true, consumer);
```

#### 主题模式

![image-20211230173025614](http://public.file.lvshuhuai.cn/images\image-20211230173025614.png)

![image-20211230173036138](http://public.file.lvshuhuai.cn/images\image-20211230173036138.png)

**exchange type 是 topic**

- 红色 Queue：绑定的是 usa.# ，因此凡是以 usa. 开头的 routing key 都会被匹配到
- 黄色 Queue：绑定的是 #.news ，因此凡是以 .news 结尾的 routing key 都会被匹配
- 对 routingKey 进行了模糊匹配单词之间用,隔开，* 代表一个具体的单词。# 代表 0 个或多个单词

Topic 主题模式可以实现 Pub / Sub 发布与订阅模式和 Routing 路由模式的功能，只是 Topic 在配置 routing key 的时候可以使用通配符，显得更加灵活。

**producer**

```java
channel.exchangeDeclare(EXCHANGE_NAME, "topic");
channel.basicPublish(EXCHANGE_NAME, routingKey, null, message.getBytes("UTF-8"));
```

**receiver**

```java
channel.exchangeDeclare(EXCHANGE_NAME, "topic");
channel.queueBind(queueName, EXCHANGE_NAME, routingKey1);
channel.queueBind(queueName, EXCHANGE_NAME, routingKey2);
channel.basicConsume(queueName, true, consumer);
```

## 绑定

binding 其实是 **exchange 和 queue 之间的桥梁**，它告诉我们 exchange 和那个 queue 进行了绑定关系。如果要指示交换机 E 将消息路由给队列 Q，那么 Q 就需要与 E 进行绑定。绑定操作需要定义一个可选的路由键（routing key）属性给某些类型的交换机。路由键的意义在于从发送给交换机的众多消息中选择出某些消息，将其路由给绑定的队列。

![image-20211230173046913](http://public.file.lvshuhuai.cn/images\image-20211230173046913.png)

如果 AMQP 的消息无法路由到队列（例如，发送到的交换机没有绑定队列），消息会被就地销毁或者返还给发布者。如何处理取决于发布者设置的消息属性。

## 消息分发

### 轮训分发

RabbitMQ 默认分发消息采用的轮训分发的，如果同一队列有多个消费节点，则会按照**消息顺序进行轮训消费。**

### 不公平分发

RabbitMQ **默认分发消息采用的轮训分发**，但是在某种场景下这种策略并不是很好，比方说有两个消费者在处理务，其中有个消费者 1 处理任务的速度非常快，而另外一个消费者 2 处理速度却很慢，这个时候我们还是采用轮训分发的化就会到这处理速度快的这个消费者很大一部分时间处于空闲状态，而处理慢的那个消费者一直在干活，这种分配方式在这种情况下其实就不太好，但是RabbitMQ 并不知道这种情况它依然很公平的进行分发。

为了避免这种情况，我们可以设置参数 `channel.basicQos(1);` 意思就是如果这个任务我还没有处理完或者我还没有应答你，你先别分配给我，我目前只能处理一个任务，然后 rabbitmq 就会把该任务分配给没有那么忙的那个空闲消费者，当然如果所有的消费者都没有完成手上任务，队列还在不停的添加新任务，队列有可能就会遇到队列被撑满的情况，这个时候就只能添加新的 worker 或者改变其他存储任务的策略。

### 限流

通过使用 basic.qos 方法设置“**预取计数**”值来完成的。该值定义通道上允许的未确认消息的最大数量。**100 到 300** 范围内的值通常可提供最佳的吞吐量，并且不会给消费者带来太大的风险。预取值为 1 是最保守的。

## 消息确认

### 发布确认

#### 原理

生产者将信道设置成 **confirm** 模式，一旦信道进入 confirm 模式，所有在**该信道上面发布的消息都将会被指派一个唯一的 ID（从 1 开始）**，一旦**消息被投递到所有匹配的队列**之后，broker 就会发送一个确认给生产者（包含消息的唯一 ID），这就使得生产者知道消息已经正确到达目的队列了，**如果消息和队列是可持久化的，那么确认消息会在将消息写入磁盘之后发出**，broker 回传给生产者的确认消息中 delivery-tag 域包含了确认消息的序列号，此外 broker 也可以设置 basic.ack 的 multiple 域，表示到这个序列号之前的所有消息都已经得到了处理。

#### 开启发布确认

发布确认默认是没有开启的，如果要开启需要调用方法 **confirmSelect**，每当你要想使用发布确认，都需要在 channel 上调用该方法。

```java
//创建 channel实例
channel = connection.createChannel();

// 开启发布确认
channel.confirmSelect();
```

#### 单个确认发布

这是一种简单的确认方式，它是一种**同步确认发布**的方式，也就是发布一个消息之后只有它被确认发布，后续的消息才能继续发布，`waitForConfirmsOrDie(long)` 这个方法只有在消息被确认的时候才返回，如果在指定时间范围内这个消息没有被确认那么它将抛出异常。一个最大的缺点就是：发布速度特别的慢，因为如果没有确认发布的消息就会阻塞所有后续消息的发布，这种方式最多提供**每秒不超过数百条**发布消息的吞吐量。

```java
// 默认0L
channel.waitForConfirmsOrDie();
// 时间内
channel.waitForConfirmsOrDie(1000L);
```

#### 批量确认发布

与单个等待确认消息相比，先发布一批消息然后一起确认 `waitForConfirms()` 可以**极大地提高吞吐量**，当然这种方式的缺点就是：**当发生故障导致发布出现问题时，不知道是哪个消息出现问题了**，我们必须将整个批处理保存在内存中，以记录重要的信息而后重新发布消息。当然这种方案**仍然是同步的**，也一样阻塞消息的发布。

```java
for (int i = 0; i < MESSAGE_COUNT; i++) {
    String message = i + "";
    channel.basicPublish("", queueName, null, message.getBytes());
    outstandingMessageCount++;
    if (outstandingMessageCount == batchSize) {
        channel.waitForConfirms();
        outstandingMessageCount = 0;
    }
}

//为了确保还有剩余没有确认消息 再次确认
if (outstandingMessageCount > 0) {
    channel.waitForConfirms();
}
```

#### 异步确认发布

**利用回调函数来达到消息可靠性传递的**，这个中间件也是通过函数回调来保证是否投递成功。把未确认的消息放到一个**基于内存的能被发布线程访问的队列**，比如说用 `ConcurrentLinkedQueue` 这个队列在 confirm callbacks 与发布线程之间进行消息的传递。

```java
//开启发布确认
channel.confirmSelect();
/**
 * 线程安全有序的一个跳表，适用于高并发的情况
 * 1.轻松的将序号与消息进行关联
 * 2.轻松批量删除条目 只要给到序列号
 * 3.支持并发访问
 */
ConcurrentSkipListMap<Long, String> outstandingConfirms = new ConcurrentSkipListMap<>();

/**
 * 确认监听器
 * 1. 消息序列号
 * 2. true 可以确认小于等于当前序列号的消息
 * 3. false 确认当前序列号消息
 */
ConfirmListener confirmListener = new ConfirmListener() {
    @Override
    public void handleAck(long deliveryTag, boolean multiple) throws IOException {
         // 是否批量
    	if (multiple) {
       	 	//返回的是小于等于当前序列号的未确认消息 是一个 map
        	ConcurrentNavigableMap<Long, String> confirmed = outstandingConfirms.headMap(deliveryTag, true);
      	 	//清除该部分未确认消息
       		confirmed.clear();
    	}else{
        	//只清除当前序列号的消息
        	outstandingConfirms.remove(deliveryTag);
    	}
    }
    @Override
    public void handleNack(long deliveryTag, boolean multiple) throws IOException {
         String message = outstandingConfirms.get(deliveryTag);
    	logger.error("发布的消息" + message + "未被确认，序列号" + sequenceNumber);
    }
};


/**
 * 添加一个异步确认的监听器
 * 1.确认收到消息的回调
 * 2.未收到消息的回调
 */
channel.addConfirmListener(confirmListener);

for (int i = 0; i < MESSAGE_COUNT; i++) {
    String message = "消息" + i;
    /**
     * channel.getNextPublishSeqNo()获取下一个消息的序列号
     * 通过序列号与消息体进行一个关联
     * 全部都是未确认的消息体
     */
    outstandingConfirms.put(channel.getNextPublishSeqNo(), message);
    channel.basicPublish("", queueName, null, message.getBytes());
}
```

#### 回退消息

在仅开启了生产者确认机制的情况下，交换机接收到消息后，会直接给消息生产者发送确认消息，如果发现该消息不可路由，那么消息会被直接丢弃，此时生产者是不知道消息被丢弃这个事件的。

通过设置 **mandatory** 参数可以在当消息传递过程中不可达目的地时将消息返回给生产者。

```java
// mandatory true 强制推送到一个队列中 
public abstract void publish(String topic,boolean mandatory, boolean immediate,boolean durable,Object data) throws Exception;

ReturnListener returnListener = new ReturnListener() {
    @Override
    public void handleReturn(int replyCode, String replyText, String exchange, String routingKey, BasicProperties properties, byte[] body) throws IOException {
        
    }
};
// 添加回退监听器
channel.addReturnListener(returnListener);
```

### 消息应答

为了保证消息在发送过程中不丢失，rabbitmq 引入消息应答机制，消息应答就是：**消费者在接收到消息并且处理该消息之后，告诉 rabbitmq 它已经处理了，rabbitmq 可以把该消息删除了。**

#### 自动应答

消息发送后立即被认为已经传送成功，**这种模式需要在高吞吐量和数据传输安全性方面做权衡**，因为这种模式如果消息在接收到之前，消费者那边出现连接或者 channel 关闭，那么消息就丢失了，当然另一方面这种模式消费者那边可以传递过载的消息，没有对传递的消息数量进行限制，当然这样有可能使得消费者这边由于接收太多还来不及处理的消息，导致这些消息的积压，最终使得内存耗尽，最终这些消费者线程被操作系统杀死，所以这种模式**仅适用在消费者可以高效并以某种速率能够处理这些消息的情况下使用。**

#### 手动应答

- Channel.basicAck：用于肯定确认，RabbitMQ 已知道该消息并且成功的处理消息，可以将其丢弃了
- Channel.basicNack：用于否定确认
- Channel.basicReject：用于否定确认，与 Channel.basicNack 相比少一个参数不处理该消息了直接拒绝，可以将其丢弃了

#### 批量应答

在手动应答时，**指定 multiple 为 true，**可以进行批量应答，从而减少网络拥堵。

```java
channel.basicAck(envelope.getDeliveryTag(), true);
```

#### 重新入队

如果消费者由于某些原因失去连接（其通道已关闭，连接已关闭或 TCP 连接丢失），导致消息未发送 ACK 确认，RabbitMQ 将了解到消息未完全处理，并将对其重新排队。如果此时其他消费者可以处理，它将很快将其重新分发给另一个消费者。这样，即使某个消费者偶尔死亡，也可以确保不会丢失任何消息。在手动应答时，**指定 requeue 为 true，可以进行重新入队。**

```java
// requeue ? 重新入队 : 丢弃
channel.basicReject(envelope.getDeliveryTag(), true);
```

## 持久化

我们需要将**队列和消息都标记为持久化**。来保障当 RabbitMQ 服务停掉或奔溃以后消息生产者发送过来的消息不丢失。

### 队列持久化

默认我们创建的队列都是非持久化的。rabbitmq 如果重启的话，该队列就会被删除掉，如果要队列实现持久化 需要在声明队列的时候把 durable 参数设置为持久化。

```java
boolean queue_durable = true;
channel.queueDeclare(queue_name, queue_durable, false, false, getQueueArgs(queueLength,queueByteLength));
```

**注意：如果之前声明的队列不是持久化的，需要把原先队列先删除，或者重新创建一个持久化的队列，不然就会出现错误**

### 消息持久化

要想让消息实现持久化，需要在生产者发布消息时 **指定 deliveryMode 为 2。**

```java
public abstract void publish(String topic,boolean mandatory, boolean immediate,boolean durable,Object data) throws Exception;

BasicProperties.Builder propsBuilder = new BasicProperties.Builder();

//是否持久化
propsBuilder.deliveryMode(durable ? 2 : 1);
```

注意：**将消息标记为持久化并不能完全保证不会丢失消息**。尽管它告诉 RabbitMQ 将消息保存到磁盘，但是这里依然存在当消息刚准备存储在磁盘的时候 但是还没有存储完，消息还在缓存的一个间隔点。此时并没有真正写入磁盘。持久性保证并不强。**如果需要更强有力的持久化策略，可以增加发布确认**。

## 队列

### 死信队列

死信，顾名思义就是无法被消费的消息，字面意思可以这样理解，一般来说，producer 将消息投递到 broker 或者直接到 queue 里了，consumer 从 queue 取出消息进行消费，但某些时候**由于特定的原因导致 queue 中的某些消息无法被消费**，这样的消息如果没有后续的处理，就变成了死信，有死信自然就有了死信队列。

#### 死信来源

- 消息 TTL 过期
- 队列达到最大长度（队列满了，无法再添加数据到 mq 中）
- 消息被拒绝（basic.reject 或 basic.nack）并且 requeue=false

#### 设置死信队列

![image-20211230173628371](http://public.file.lvshuhuai.cn/images\image-20211230173628371.png)

```java
//声明死信和普通交换机 类型为 direct
channel.exchangeDeclare(NORMAL_EXCHANGE, BuiltinExchangeType.DIRECT);
channel.exchangeDeclare(DEAD_EXCHANGE, BuiltinExchangeType.DIRECT);

//声明死信队列
String deadQueue = "dead-queue";
channel.queueDeclare(deadQueue, false, false, false, null);

// 死信队列绑定死信交换机与 routingkey
channel.queueBind(deadQueue, DEAD_EXCHANGE, "dead_routingkey");

// 正常队列绑定死信队列信息
Map<String, Object> params = new HashMap<>();
// 正常队列设置死信交换机 参数 key 是固定值
params.put("x-dead-letter-exchange", DEAD_EXCHANGE);
// 正常队列设置死信 routing-key 参数 key 是固定值
params.put("x-dead-letter-routing-key", "dead_routingkey");
String normalQueue = "normal-queue";
// 声明正常队列
channel.queueDeclare(normalQueue, false, false, false, params);
// 正常队列绑定
channel.queueBind(normalQueue, NORMAL_EXCHANGE, "normal_routingkey");
```

### 延迟队列

延时队列，**队列内部是有序的**，最重要的特性就体现在它的延时属性上，延时队列中的元素是希望在指定时间到了以后或之前取出和处理，简单来说，延时队列就是**用来存放需要在指定时间被处理的元素的队列**。

#### 实现方式

- 基于消息 TTL 和队列 TTL 转换入死信队列，消费死信队列中的消息
- 基于延迟插件，该类型消息支持延迟投递机制 消息传递后并不会立即投递到目标队列中，而是存储在 mnesia（一个分布式数据系统）表中，当达到投递时间时，才投递到目标队列中
- 用 Java 的 DelayQueue
- 利用 Redis 的 zset

### 优先队列

要让队列实现优先级需要做的事情有如下事情：**队列需要设置为优先级队列**，**消息需要设置消息的优先级**，消费者需要等待消息已经发送到队列中才去消费，因为这样才有机会对消息进行排序。

```java
// 队列
Map args = MapUtils.toMap(new Object[][]{{"x-max-priority", 10}});
channel.queueDeclare(queue_name, queue_durable, false, false, args);

// 消息
BasicProperties.Builder propsBuilder = new BasicProperties.Builder();
propsBuilder.priority(5);
channel.basicPublish(exchange_name, topic, null, str_msg.getBytes("UTF-8"));
```

### 惰性队列

RabbitMQ 从 **3.6.0** 版本开始引入了惰性队列的概念。**惰性队列会尽可能的将消息存入磁盘中**，而在消费者消费到相应的消息时才会被加载到内存中，它的一个重要的设计目标是能够**支持更长的队列**，即支持更多的消息存储。当消费者由于各种各样的原因（比如消费者下线、宕机亦或者是由于维护而关闭等）而致使长时间内不能消费消息造成堆积时，惰性队列就很有必要了。

默认情况下，当生产者将消息发送到 RabbitMQ 的时候，**队列中的消息会尽可能的存储在内存之中**，这样可以更加快速的将消息发送给消费者。即使是持久化的消息，在被写入磁盘的同时也会在内存中驻留一份备份。当 RabbitMQ 需要释放内存的时候，会将内存中的消息换页至磁盘中，这个操作会耗费较长的时间，也会阻塞队列的操作，进而无法接收新的消息。

#### 队列声明

```java
// 队列
Map args = MapUtils.toMap(new Object[][]{{"x-queue-mode", "lazy"}});
channel.queueDeclare(queue_name, queue_durable, false, false, args);
```

#### 内存开销对比

![image-20211230173648687](http://public.file.lvshuhuai.cn/images\image-20211230173648687.png)

在发送 1 百万条消息，每条消息大概占 1KB 的情况下，普通队列占用内存是 1.2GB，而惰性队列仅仅占用 1.5MB。

## TTL

TTL 是 RabbitMQ 中一个消息或者队列的属性，**表明一条消息或者该队列中的所有消息的最大存活时间**，单位是**毫秒**。换句话说，如果一条消息设置了 TTL 属性或者进入了设置 TTL 属性的队列，那么这条消息如果在 TTL 设置的时间内没有被消费，则会成为”死信”。**如果同时配置了队列的 TTL 和消息的 TTL，那么较小的那个值将会被使用**。

### 队列 TTL

```java
Map args = MapUtils.toMap(new Object[][]{{"x-message-ttl", 2000}});
channel.queueDeclare(queue_name, queue_durable, false, false, args);
```

### 消息 TTL

```java
BasicProperties.Builder basicProperties = new BasicProperties.Builder();
basicProperties.expiration("1000");
```

## 幂等性

### 消息重复消费

消费者在消费 MQ 中的消息时，MQ 已把消息发送给消费者，消费者在给 MQ 返回 ack 时网络中断，故 MQ 未收到确认信息，该条消息会重新发给其他的消费者，或者在网络重连后再次发送给该消费者，但实际上该消费者已成功消费了该条消息，造成消费者消费了重复的消息。

### 解决思路

MQ 消费者的幂等性的解决一般使用全局 ID 或者写个唯一标识比如时间戳 或者 UUID 或者可按自己的规则生成一个全局唯一 id，每次消费消息时用该 id 先判断该消息是否已消费过。

### 幂等性保障

#### 唯一 ID+ 指纹码机制

指纹码:我们的一些规则或者时间戳加别的服务给到的唯一信息码,它并不一定是我们系统生成的，基本都是由我们的业务规则拼接而来，但是一定要保证唯一性，然后就利用查询语句进行判断这个 id 是否存在数据库中,优势就是实现简单就一个拼接，然后查询判断是否重复；劣势就是在高并发时，如果是单个数据库就会有写入性能瓶颈当然也可以采用分库分表提升性能，但也不是我们最推荐的方式。

#### Redis 原子性

利用 redis 执行 setnx 命令，天然具有幂等性。从而实现不重复消费。

## SpringBoot 集成 RabbitMQ

### **添加依赖**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

### **配置文件**

```yml
server:
  port: 8081
spring:
  application:
    name: test-rabbitmq-producer
  rabbitmq:
    host: 127.0.0.1
    port: 5672
    username: guest
    password: guest
    virtualHost: /
```

### RabbitMQ 配置类

配置 Exchange、Queue、及绑定交换机，下面配置 Topic 交换机。

```java
package com.example.config;

import org.springframework.amqp.core.*;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * RabbitmqConfig
 */
@Configuration
public class RabbitmqConfig {

    public static final String QUEUE_INFORM_EMAIL = "queue_inform_email";
    public static final String QUEUE_INFORM_SMS = "queue_inform_sms";
    public static final String EXCHANGE_TOPICS_INFORM="exchange_topics_inform";
    public static final String ROUTINGKEY_EMAIL="inform.#.email.#";
    public static final String ROUTINGKEY_SMS="inform.#.sms.#";

    //声明交换机
    @Bean(EXCHANGE_TOPICS_INFORM)
    public Exchange EXCHANGE_TOPICS_INFORM(){
        //durable(true) 持久化，mq重启之后交换机还在
        return ExchangeBuilder.topicExchange(EXCHANGE_TOPICS_INFORM).durable(true).build();
    }

    //声明QUEUE_INFORM_EMAIL队列
    @Bean(QUEUE_INFORM_EMAIL)
    public Queue QUEUE_INFORM_EMAIL(){
        return new Queue(QUEUE_INFORM_EMAIL);
    }
    //声明QUEUE_INFORM_SMS队列
    @Bean(QUEUE_INFORM_SMS)
    public Queue QUEUE_INFORM_SMS(){
        return new Queue(QUEUE_INFORM_SMS);
    }

    //ROUTINGKEY_EMAIL队列绑定交换机，指定routingKey
    @Bean
    public Binding BINDING_QUEUE_INFORM_EMAIL(@Qualifier(QUEUE_INFORM_EMAIL) Queue queue,
                                              @Qualifier(EXCHANGE_TOPICS_INFORM) Exchange exchange){
        return BindingBuilder.bind(queue).to(exchange).with(ROUTINGKEY_EMAIL).noargs();
    }
    //ROUTINGKEY_SMS队列绑定交换机，指定routingKey
    @Bean
    public Binding BINDING_ROUTINGKEY_SMS(@Qualifier(QUEUE_INFORM_SMS) Queue queue,
                                          @Qualifier(EXCHANGE_TOPICS_INFORM) Exchange exchange){
        return BindingBuilder.bind(queue).to(exchange).with(ROUTINGKEY_SMS).noargs();
    }

}
```

### 发送消息

```java
String message = "hello world";
rabbitTemplate.convertAndSend(RabbitmqTopicConfig.EXCHANGE_TOPICS_INFORM, "inform.email", message);
```

### 消费消息

消费者都是通过 @RabbitListener 注解来声明。在 @RabbitMQListener 注解中包含了非常多对 Queue 进行定制的属性，大部分的属性都是有默认值的。

```java
//监听email队列
@RabbitListener(queues = {RabbitmqTopicConfig.QUEUE_INFORM_EMAIL})
public void receive_email(Object msg, Message message, Channel channel){
    System.out.println("QUEUE_INFORM_EMAIL msg"+msg);
}
//监听sms队列
@RabbitListener(queues = {RabbitmqTopicConfig.QUEUE_INFORM_SMS})
public void receive_sms(Object msg, Message message, Channel channel){
    System.out.println("QUEUE_INFORM_SMS msg"+msg);
}
```