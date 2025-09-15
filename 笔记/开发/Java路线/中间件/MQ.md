# MQ

## 基础概念

**消息队列（Message Queue，MQ）** 是一种在分布式系统中广泛使用的组件，用于跨系统、跨进程传递消息。它本质上是一个「先进先出」的数据结构，但在工程上扩展出了丰富的特性。

- **消息（Message）**：数据的载体，可能是一条订单信息、日志、事件通知等。
- **队列（Queue）**：存放消息的容器，保证消息在传输和存储中的有序性与可控性。

### 为什么需要 MQ
1. **系统解耦**：生产者只需关心消息的发送，不关心消费者的实现。  
2. **异步处理**：不需要所有任务实时返回，例如下单后短信通知。  
3. **流量削峰**：应对突发高并发，队列起到「缓冲池」作用（常见于秒杀场景）。  
4. **扩展性和容错性**：可以通过 MQ 实现水平扩展和失败重试。  

消息（Message）是指在应用之间传送的数据，消息可以非常简单，比如只包含文本字符串，也可以更复杂，可能包含嵌入对象。

下图便是消息队列的基本模型，向消息队列中存放数据的叫做生产者，从消息队列中获取数据的叫做消费者。

![img](http://public.file.lvshuhuai.cn/images\v2-495fa7b08f6659e24fc25d1255ba8b8a_1440w.jpg)

## 消息队列MQ应用场景

![img](http://public.file.lvshuhuai.cn/images\v2-7d0c6873c9552d6118f51e9bc31860f9_1440w.jpg)

### 异步处理

**消息队列的主要特点是异步处理，主要目的是减少求响应时间]，实现非核心流程异步化，提高系统响应性能。**

举一个用户注册的例子，用户注册成功后，系统需要发送注短信注册成功通知，以及赠送注册成功的积分。

#### 同步

![img](http://public.file.lvshuhuai.cn/images\v2-ecfd36d9de5f7836c87ffe1f81f65a0f_1440w.jpg)

同步的总耗时：$10ms+100ms+100ms=210ms$

由于短信通知与增加积分为非核心流程，为了提升系统响应性能，从而我把它改造为异步。

#### 异步

![img](http://public.file.lvshuhuai.cn/images\v2-aebcdb13bd239282d6930a34c7232470_1440w.jpg)

改造后就变成上图，之前需要等用户注册 10ms + 短信通知 100ms + 增加积分 100ms 才能返回，现在把短信通知和增加积分改为异步的形式，用户注册后写入消息 10ms 左右立即返回成功给客户端，无需等待耗时较久的同步（短信 + 积分）就可以返回，从而极大的提升了系统的吞吐量。

**所以异步的典型场景就是将比较耗时而且不需要即时（同步）返回结果的操作，通过消息队列来实现异步化。**

### 应用解耦

使用了消息队列后，只要保证消息格式不变，消息的发送方和接收方并不需要彼此联系，也不需要受对方的影响，即解耦。

每个成员不必受其他成员影响，可以更独立自主，只通过消息队列MQ来联系，典型的上下游解耦如下图所示：

![img](http://public.file.lvshuhuai.cn/images\v2-5beb4bac3d180365b2d4bcad94d47452_1440w.jpg)

### 流量削锋

流量削锋也是消息队列中的常用场景，一般在秒杀或团抢活动中使用广泛。

**这种场景中系统的峰值流量往往集中于一小段时间内，所以为了防止系统在短时间内的峰值流量冲垮，往往采用消息队列来削弱峰值流量，相当于消息队列做了一次缓冲。**

![img](http://public.file.lvshuhuai.cn/images\v2-1ea47e8d6ebd5f1a99287e592a2dab13_1440w.jpg)

### 日志处理

日志处理是指将消息队列用在日志处理中，比如 Kafka 的应用，解决大量日志传输的问题。

![img](http://public.file.lvshuhuai.cn/images\v2-f8c4c94203877624f2eb9206ff045e15_1440w.jpg)

## 消息队列MQ设计

### 整体架构

![img](http://public.file.lvshuhuai.cn/images\v2-d72d5ae69fc1185bc8ba00a55d1a6da2_1440w.jpg)

**上图为整体架构，会涉及三类角色：**

1. **Producer 消息生产者** ：负责产生和发送消息到 Broker；
2. **Broker 消息处理中心** ：负责消息存储、确认、重试等，一般其中会包含多个 queue；
3. **Consumer 消息消费者** ：负责从 Broker 中获取消息，并进行相应处理；

### 详细设计

![img](http://public.file.lvshuhuai.cn/images\v2-17aaeed519de32f9d99a6c902a755d08_1440w.jpg)

详细的流程如上图，producer 发送给 broker，broker 发送给 consumer，consumer 回复消费确认，broker 删除 / 备份消息等。

#### RPC 通信

图上的**第一个步骤：Producer 生产消息**向 Broker 发送会涉及到通信的问题，同样 Consumer 消费消息也会涉及到通信的问题。

上图中的 Producer，Broker，Consumer 最后就通过 RPC 将数据流串起来了，所以需要解决通信的问题。

你可以基于 Netty 来做底层通信，用 Zookeeper、Euraka 等来做注册中心，然后自定义一套新的通信协议。

也可以直接利用成熟的 RPC 框架 Dubbo 或者 Thrift 实现即可，这样不需要考虑服务注册与发现、负载均衡、通信协议、序列化方式等一系列问题了。

#### Broker 存储

**图上第二个步骤，消息到达服务端后需要存储到 Broker。**

大家关注的流量削峰、最终一致性等需求都是需要 Broker 先存储下来，然后选择时机投递，这才达到流量削峰、泄洪的目的，所以 Broker 一个非常重要的功能就是存储。

存储可以做成很多方式，比如存储在内存里，存储在分布式 KV 里，存储在磁盘里，存储在数据库里等等，存储的选型需要**综合考虑性能 / 高可用和开发维护成本** 等诸多因素。

目前主流的方案：追加写日志文件（数据部分） + 索引文件的方式，索引设计上可以考虑稠密索引或者稀疏索引，查找消息可以利用跳转表、二份查找等，还可以通过操作系统的页缓存、零拷贝等技术来提升磁盘文件的读写性能。

#### 消费模型

**图上第三个步骤，消息到达 Broker 后，最终还是需要 Consumer 去消费消息，这里就会涉及到到消费模型。**

这里的消费模型，目前主要就两种：单播和广播。所谓单播，就是点到点；而广播，是一点对多点。

详细的单播和广播消费模型，下面我会图文详解。

#### 高级特性

图上第四个步骤，如果 Consumer 端把消息消费了，除了需要消息确认，还会涉及到比如：重复消息、顺序消息、消息延迟、事务消息等需要考虑的高级特性。

## 消息队列 MQ 模型

消息队列 MQ 主要包含两种模型：点对点与发布订阅两种模型。

### 点对点模型

![img](http://public.file.lvshuhuai.cn/images\v2-23aa72c854cb97734d7b111137b7c1e6_1440w.jpg)

**点对点模型用于消息生产者和消息消费者之间点到点的通信，包含三个角色：**

- 消息队列（Queue）
- 发送者（Sender）
- 接收者（Receiver）

每个消息都被发送到一个特定的队列，接收者从队列中获取消息。队列保留着消息，可以放在内存中也可以持久化，直到他们被消费或超时。

#### 特点

- 每个消息只有一个消费者（Consumer）(即一旦被消费，消息就不再在消息队列中)
- 发送者和接收者之间在时间上没有依赖性
- 接收者在成功接收消息之后需向队列应答成功

### 发布订阅消息模型 Topic

![img](http://public.file.lvshuhuai.cn/images\v2-94f2132b80065f9d67106fb9b6188813_1440w.jpg)

**发布订阅模型包含三个角色：**

- 主题（Topic）
- 发布者（Publisher）
- 订阅者（Subscriber）

多个发布者将消息发送到 Topic，系统将这些消息传递给多个订阅者。

#### 特点

- 每个消息可以有多个消费者：和点对点方式不同，发布消息可以被所有订阅者消费
- 发布者和订阅者之间有时间上的依赖性。
- 针对某个主题（Topic）的订阅者，它必须创建一个订阅者之后，才能消费发布者的消息。
- 为了消费消息，订阅者必须保持运行的状态。

## 消息队列 MQ 产品选型

### ActiveMQ

![img](http://public.file.lvshuhuai.cn/images\v2-4aaa9e16eb1d1d56987ced8d98439686_1440w.jpg)

ActiveMQ 官网地址：[http://activemq.apache.org](https://link.zhihu.com/?target=http%3A//activemq.apache.org)

Apache 出品，最早使用的消息队列产品，时间比较长了，最近版本更新比较缓慢，性能在万级 / 秒。

### RabbitMQ

![img](http://public.file.lvshuhuai.cn/images\v2-b495a9cea45852e87f0cf21dab64ccd5_1440w.jpg)

RabbitMQ 官网地址：[www.rabbitmq.com](https://link.zhihu.com/?target=http%3A//www.rabbitmq.com/)

RabbitMQ 是 erlang 语言开发，结合 erlang 语言本身的并发优势，支持很多的协议：AMQP，XMPP, SMTP, STOMP，性能在万级 / 秒，其整体架构图如下所示：

![img](http://public.file.lvshuhuai.cn/images\v2-3bff07097e0255d06a29a8b58eb6c149_1440w.jpg)

### Kafka

![img](http://public.file.lvshuhuai.cn/images\v2-4a6cb87f37e2ec5caedd2eb781653c28_1440w.jpg)

Kafka 官网地址：[http://kafka.apache.org](https://link.zhihu.com/?target=http%3A//kafka.apache.org)

Kafka 是由 Apache 软件基金会开发的一个开源消息系统项目，由 Scala 写成。Kafka 最初是由 LinkedIn 开发，并于 2011 年初开源。Kafka 是一个分布式的、分区的、多复本的日志提交服务，性能在百万级 / 秒，其整体架构图如下所示：

![img](http://public.file.lvshuhuai.cn/images\v2-6496947b8d816b77b60089ba1ade77c7_1440w.jpg)

### RocketMQ

![img](http://public.file.lvshuhuai.cn/images\v2-06b4b082a4fc070804e82388e18d184a_1440w.jpg)

RocketMQ 官网地址：[http://rocketmq.apache.org](https://link.zhihu.com/?target=http%3A//rocketmq.apache.org)

阿里开源的消息中间件，纯 Java 开发，具有高吞吐量、高可用性、适合大规模分布式系统应用的特点，参考 Kafka 而设计的，性能在十万级/秒，其整体架构图如下所示：

![img](http://public.file.lvshuhuai.cn/images\v2-1fafdb61172e91cd638b4798af56310d_1440w.jpg)

### Pulsar

![img](http://public.file.lvshuhuai.cn/images\v2-8d3630502358d34f81d70540672bf36d_1440w.jpg)

Pulsar 官网地址：[http://pulsar.apache.org](https://link.zhihu.com/?target=http%3A//pulsar.apache.org)

Apache Pulsar 是 Apache 软件基金会顶级项目，是下一代云原生分布式消息流平台，集消息、存储、轻量化函数式计算为一体，采用计算与存储分离架构设计，支持多租户、持久化存储、多机房跨区域数据复制，具有强一致性、高吞吐、低延时及高可扩展性等流数据存储特性，被看作是云原生时代实时消息流传输、存储和计算最佳解决方案，其整体架构图如下所示：

![img](http://public.file.lvshuhuai.cn/images\v2-1a10cc8f9da1c87cada5ef571fe28d0a_1440w.jpg)

### 消息队列选型

广泛来说，电商、金融等对事务性要求很高的，可以考虑 RocketMQ，技术挑战不是特别高，用 RabbitMQ 是不错的选择，如果是大数据领域的实时计算、日志采集等场景可以考虑 Kafka。