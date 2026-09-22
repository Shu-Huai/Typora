# 说说 RabbitMQ 的集群模式？ - 面试鸭 | 2026最新RabbitMQ 面试题+详细答案解析

## 回答重点

RabbitMQ 集群主要有三种模式：**标准集群**、**镜像集群**、**联邦集群**。

### 标准集群

多台 RabbitMQ 服务器通过网络组成一个集群，所有节点共享元数据（队列、交换机、绑定），但消息只存在单个节点上，不会自动复制。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/bXOELmwj_image_mianshiya.webp)

客户端可以连任意节点，因为元数据共享，任何节点都知道消息实际存在哪个节点上，请求会被转发过去。这样可以做负载均衡，但有个致命问题：某个节点挂了，它上面的消息就没法消费了，别的节点虽然还能干活，但数据丢了。

### 镜像集群

镜像模式在标准模式基础上加了一层数据冗余。队列会有一个 master 和若干 mirror，消息写入 master 后会同步到所有 mirror 节点。master 挂了，某个 mirror 会自动提升为新 master，服务不中断。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/j1yIFL2u_image_mianshiya.webp)

配置镜像队列需要设置 policy：

```bash
rabbitmqctl set_policy ha-all "^" '{"ha-mode":"all"}'
```

这行命令表示所有队列都做全量镜像，生产环境通常会根据队列名称前缀精细化配置，避免所有队列都全量镜像导致性能下降。

### 联邦集群

联邦模式用于跨地域多活部署。比如北京和上海两个机房各有一套 RabbitMQ 集群，通过 federation 插件实现数据同步。北京机房挂了，上海还能顶上。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/uZZlG9wO_image_mianshiya.webp)

这种模式的核心是 upstream 配置，上海集群配置北京集群为 upstream，消息会自动从北京同步过来。

## 扩展知识

### 镜像队列的同步策略

镜像队列有两种同步模式：

1）**自动同步**：新节点加入时自动从 master 拉取全量数据，期间队列会阻塞，不接受新消息。队列里有 100 万条消息的话，同步过程可能要好几分钟，业务会感知到延迟。

2）**手动同步**：新节点加入后不自动同步，需要运维手动触发。好处是加节点不影响业务，坏处是这个新节点在同步完成前不具备故障接管能力。

生产环境一般选手动同步，然后在业务低峰期执行同步操作。

### 镜像队列的性能代价

镜像队列虽然提高了可用性，但性能会打折扣：

消息每次写入都要同步到所有 mirror 节点，假设配了 3 个 mirror，那一条消息实际要写 4 次。网络延迟也会累加，跨机房部署时这个问题更明显。

官方测试数据显示，3 节点全镜像相比单节点，吞吐量下降约 40%-50%。所以不是所有队列都要配镜像，核心业务队列才值得这个代价。

### 仲裁队列

RabbitMQ 3.8 引入了 **Quorum Queue** 来替代镜像队列。底层用 Raft 协议实现共识，相比镜像队列有几个优势：

1）数据一致性更强，镜像队列在极端场景下可能丢消息，仲裁队列不会。

2）故障恢复更快，选主过程由 Raft 协议保证，通常几秒内完成。

3）性能更好，Raft 只需要多数节点确认即可，不用等所有节点。

创建仲裁队列：

```java
Map<String, Object> args = new HashMap<>();
args.put("x-queue-type", "quorum");
channel.queueDeclare("my-quorum-queue", true, false, false, args);
```

官方已经明确表示镜像队列会被废弃，新项目建议直接用仲裁队列。

### 集群模式选择建议

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/XNXb4UQd_P0Z4n0wGjq_mianshiya.webp)

## 面试官追问

#### 提问：镜像队列和仲裁队列都能实现高可用，生产环境怎么选？

回答：直接选仲裁队列。镜像队列是老方案了，RabbitMQ 官方从 3.8 开始就推仲裁队列，镜像队列在 4.0 会被彻底移除。仲裁队列用 Raft 协议保证一致性，不会出现镜像队列那种极端场景下脑裂丢消息的问题。唯一要注意的是仲裁队列不支持非持久化消息，所有消息都会落盘，对于那种允许丢失的临时消息场景，反而标准队列更合适。

#### 提问：RabbitMQ 集群节点之间是怎么发现对方的？

回答：靠 Erlang Cookie。每个 RabbitMQ 节点启动时会读取一个叫 .erlang.cookie 的文件，集群内所有节点这个文件内容必须一样。节点之间通过 Erlang 分布式协议通信，Cookie 相当于密钥，不一致的话握手会直接失败。部署时最常见的坑就是忘了同步这个 Cookie 文件。

#### 提问：镜像队列的 master 挂了，选新 master 的过程中消息会丢吗？

回答：看具体配置。如果生产者用了 publisher confirm 机制，那 master 挂掉时未确认的消息会被生产者感知到，可以重发。但如果没用 confirm，那些已经发到 master 但还没同步到 mirror 的消息就丢了。仲裁队列就没这个问题，Raft 协议要求多数节点确认才算写入成功，master 挂了新 master 上肯定有完整数据。
...
