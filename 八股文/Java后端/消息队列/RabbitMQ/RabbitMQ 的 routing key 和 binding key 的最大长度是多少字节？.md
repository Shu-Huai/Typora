# RabbitMQ 的 routing key 和 binding key 的最大长度是多少字节？

## 回答重点

RabbitMQ 里 routing `key` 和 binding `key` 的最大长度都是 **255 字节**，这是 AMQP 0-9-1 协议规范定死的。超过这个长度，broker 直接拒绝，生产者会收到 channel 级别的异常。

routing `key` 是生产者发消息时带的，告诉交换机这条消息该往哪走。binding `key` 是建立绑定关系时指定的，定义交换机按什么规则把消息路由到队列。两者的匹配逻辑取决于交换机类型：Direct 要求完全一致，Topic 支持通配符匹配。

<img src="Z:/Public/images/vvp4PiPG_froKiOMP7v_mianshiya.webp" alt="" />

实际开发中 255 字节绰绰有余，一般按 `{业务域}.{模块}.{事件}` 这种格式命名，比如 `order.payment.success`，几十个字符就够了。

## 扩展知识

### 为什么是 255 字节

这个限制来自 AMQP 0-9-1 协议的设计。

协议帧里用 1 个字节存储 short string 的长度，1 字节最大能表示的值就是 255。routing `key` 和 binding `key` 都属于 short string 类型，所以上限就是 255 字节。

注意是字节不是字符，如果 `key` 里用了中文，一个 UTF-8 编码的汉字占 3 字节，很容易超限。

所以命名规范里一般建议只用英文、数字、点号和下划线。

### Topic 模式下的 `key` 设计

Topic 交换机的 binding `key` 支持两个通配符：

- `*` 匹配一个单词
- `#` 匹配零到多个单词，单词之间用点号分隔。

比如日志系统的设计：

```
# 生产者发送时的 routing key
log.error.payment
log.warn.order
log.info.user

# 消费者绑定时的 binding key
log.error.*     # 只收 error 级别的日志
log.*.payment   # 只收 payment 模块的日志
log.#           # 收所有日志
```

设计 `key` 的时候要考虑扩展性，层级太少后期加字段不方便，层级太多又显得啰嗦。3 到 4 层是比较舒服的粒度。

Topic 交换机的匹配过程：生产者发消息带 routing `key` 为 log.error.payment，交换机遍历所有绑定，binding `key` 为 log.error.* 的队列能匹配上，binding `key` 为 log.info.* 的队列匹配不上。

<img src="Z:/Public/images/RGp6a554_image_mianshiya.webp" alt="image.png" width="100%" />

### 常见踩坑点

1. routing `key` 写错了消息会静默丢弃。Direct 和 Topic 交换机在找不到匹配队列时，默认行为是直接丢掉消息，不会报错。生产环境一定要配置备用交换机 alternate-exchange，把路由失败的消息兜住。

2. Topic 模式下 `#` 要谨慎使用。`#` 能匹配任意层级，绑定 `order.#` 的队列会收到 order.create、order.pay.success、order.refund.apply 所有消息。如果只想收一层，应该用 `order.*`。

3. binding `key` 里不能用 `*` 和 `#` 的地方别乱用。只有 Topic 交换机才解析通配符，Direct 交换机里 `order.*` 就是字面值，要求 routing `key` 也得是 `order.*` 才能匹配。

## 面试官追问

#### 提问：消息发出去了但消费者收不到，怎么排查？

回答：先确认交换机、队列、绑定关系都建好了，Management UI 里能看到。然后检查 routing `key` 和 binding `key` 是否匹配，Topic 模式下通配符容易写错。还要看消息有没有被路由到队列，如果队列的消息数是 0，说明路由环节就出问题了。可以临时绑一个 `#` 通配符的队列验证消息确实发到了交换机。

#### 提问：routing `key` 设计有什么最佳实践？

回答：遵循 `{业务域}.{模块}.{动作}` 的三段式命名，比如 `order.payment.success`。好处是层级清晰，Topic 模式下可以灵活订阅。避免用中文，避免太长的单词，保持整个团队命名风格一致。最好维护一份 `key` 的字典文档，新增 `key` 要 review。

#### 提问：如果业务上确实需要超过 255 字节的路由信息怎么办？

回答：routing `key` 本身不适合塞太多信息，超长一般是设计问题。真有复杂路由需求可以用 Headers 交换机，把路由信息放消息头里，消息头没有 255 字节的限制。或者把详细信息放消息体里，routing `key` 只保留核心标识，消费者拿到消息后再根据消息体内容做二次分发。
