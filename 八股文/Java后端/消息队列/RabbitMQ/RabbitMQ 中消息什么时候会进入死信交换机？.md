# RabbitMQ 中消息什么时候会进入死信交换机？

## 回答重点

消息进入**死信交换机**主要有三种情况：

1. **消费者主动拒绝消息**。调用 `basic.reject` 或 `basic.nack` 时把 `requeue` 设为 false，消息就不会重新入队，直接丢给死信交换机。

2. **消息过期了还没被消费**。RabbitMQ 支持给消息或队列设置 TTL，比如设置 30 秒，30 秒内没人消费，这条消息就变成死信被转走。

3. **队列满了装不下**。队列设置了 `x-max-length` 或 `x-max-length-bytes` 限制后，新消息进来时如果超出容量，队头最老的消息会被挤到死信交换机。

<img src="Z:/Public/images/TbOKZaUP_image_mianshiya.webp" alt="image.png" width="100%" />

这些死信消息转到死信队列后，可以做日志记录、告警监控，或者人工介入重新处理。

配置死信交换机很简单，声明队列时加两个参数就行：

```java
Map<String, Object> args = new HashMap<>();
args.put("x-dead-letter-exchange", "dlx-exchange");
args.put("x-dead-letter-routing-key", "dlx-routing-key");

channel.queueDeclare("order-queue", true, false, false, args);
channel.exchangeDeclare("dlx-exchange", "direct");
channel.queueBind("dlx-queue", "dlx-exchange", "dlx-routing-key");
```

## 扩展知识

### 为什么需要死信机制

早期消息队列对处理失败的消息很粗暴，要么丢弃要么无限重试。丢弃会造成数据丢失，无限重试又会拖垮系统。死信机制就是给这些“问题消息”一个缓冲区，先存起来不影响正常业务，后续再集中处理。

电商订单场景最典型：用户下单后 30 分钟不支付就要自动取消。传统做法是定时任务扫表，订单量大了效率很差。

用死信队列就优雅多了，下单时把消息扔进设置了 30 分钟 TTL 的队列，到期自动进死信队列触发取消逻辑，不用轮询数据库。

<p align="center"><img src="Z:/Public/images/zCljPxXT_WioKq2OUXU_mianshiya.webp" alt="" /></p>

### 三种死信条件的细节

**消息被拒绝**这个场景，关键在 `requeue` 参数。设成 true 消息会重新回到队头等待再次消费，设成 false 才会进死信。实际开发中一般会配合重试次数用，比如重试 3 次都失败了再 reject 掉：

```java
// 伪代码：重试3次后进死信
if (retryCount >= 3) {
    channel.basicReject(deliveryTag, false);  // 不重入队，进死信
} else {
    channel.basicNack(deliveryTag, false, true);  // 重入队重试
}
```

**消息过期**有两种设置方式：一种是给队列设置 `x-message-ttl`，队列里所有消息共用一个过期时间；另一种是发消息时单独设置 `expiration` 属性，每条消息有自己的过期时间。两个都设的话取较小的那个。

注意一个坑：单条消息设置 TTL 时，RabbitMQ 只会检查队头消息是否过期。如果队头消息 TTL 是 1 小时，后面有条消息 TTL 是 1 分钟，这条 1 分钟的消息不会按时进死信，得等前面的消息消费掉或过期才行。队列级别的 TTL 就没这个问题。

**队列容量限制**这块，`x-max-length` 限制消息条数，`x-max-length-bytes` 限制总字节数。超出后默认丢弃队头消息，配了死信交换机才会转发。RabbitMQ 3.1.0 之后还支持 `overflow` 参数，设成 `reject-publish` 可以拒绝新消息而不是丢老消息。

### 死信消息的元数据

消息进入死信队列时，RabbitMQ 会在 header 里加一些有用的信息：

| 字段 | 含义 |
|------|------|
| `x`-death | 死信历史记录，包含原队列名、死信原因、时间戳 |
| `x`-first-death-reason | 第一次变成死信的原因：rejected、expired、maxlen |
| `x`-first-death-`queue` | 第一次变成死信时所在的队列 |
| `x`-first-death-exchange | 第一次变成死信时绑定的交换机 |

这些信息对排查问题很有帮助。消费死信队列时可以解析这些 header，区分是超时死信还是消费失败死信，走不同的处理逻辑。

### 避免死信循环

配置死信交换机时有个容易踩的坑：千万别把死信队列的死信交换机又指回原队列，否则消息会在两个队列之间无限循环，系统资源很快耗尽。正确做法是死信队列要么不设死信交换机，要么指向一个专门的“终极死信队列”用于人工兜底。

## 面试官追问

#### 提问：如果我想实现延迟队列功能，用死信队列和用 RabbitMQ 的延迟插件有什么区别？

回答：死信队列实现延迟是利用 TTL 过期机制，消息先进一个没有消费者的队列，到期后转到死信队列才被消费。这种方式有个问题，消息必须按顺序过期，后进的消息就算 TTL 更短也得等前面的消息处理完。延迟插件用的是另一套机制，消息存在 Mnesia 表里按延迟时间排序，到期精确投递，不存在顺序问题。插件方案更灵活，但要额外安装，而且重启时会有短暂的消息加载延迟。

#### 提问：死信队列的消费者挂了，消息会不会丢？

回答：不会丢，死信队列本质上也是普通队列，消息持久化的话断电重启都还在。只是会积压，积压太多可能把磁盘撑爆。生产环境死信队列一般会配监控告警，积压超过一定数量就报警，人工介入处理。

#### 提问：消息被 reject 后直接进死信，有没有办法先重试几次再进？

回答：RabbitMQ 原生不支持自动重试次数控制，得自己在消费端实现。常见做法是消息 header 里记一个重试计数器，每次消费失败就加一，超过阈值再 reject 进死信。Spring AMQP 的 `RetryTemplate` 封装了这个逻辑，配置 `maxAttempts` 就行，底层帮你处理计数和最终 reject。
