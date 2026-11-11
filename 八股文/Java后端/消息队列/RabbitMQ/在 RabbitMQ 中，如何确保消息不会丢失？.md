# 在 RabbitMQ 中，如何确保消息不会丢失？

## 回答重点

在 RabbitMQ 中，为了确保消息不会丢失，可以从以下几个方面入手：

1. **消息持久化**：确保队列和消息都是持久的，即使 RabbitMQ 服务器重启也不会丢失消息。创建队列的时候设置 `durable` 为 `true`，发布消息时设置 `delivery_mode` 为 `2`。

2. **发布确认**：开启发布确认模式（Publisher Confirms）。这种模式下，生产者会等待服务器的确认响应，确保消息已经成功存储。

3. **消费者确认**：使用明确的消费者确认机制（Acknowledgements）。消费者在处理完消息后，向 RabbitMQ 发送确认，RabbitMQ 在收到确认后才会将消息从队列中删除。

## 扩展知识

下面详细了解一下如何具体实现上面提到的这些策略。

1. **消息持久化**

- **持久化队列**：在声明队列时设置 `durable` 属性为 `true`。

```python
channel.queue_declare(queue='task_queue', durable=True)
```

- **持久化消息**：在发送消息时设置 `persistent` 属性。

```python
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode=2,  # make message persistent
                      ))
```

坚固的队列加上持久化的消息能够大大减少消息丢失的可能。

2. **发布确认**
在生产者代码中，先开启发布确认模式，再发布消息。使用异步或同步的方法等待确认。

```python
channel.confirm_delivery()
try:
   channel.basic_publish(exchange='',
                         routing_key='task_queue',
                         body='Hello World!',
                         properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                         ))
   print(" [x] Sent 'Hello World!'")
except pika.exceptions.UnroutableError:
   print(" [x] Message could not be confirmed")
```

在这种模式下，RabbitMQ 会返回确认（ack），表示消息已经被接收到和持久化。

3. **消费者确认**
消费者处理消息后显式发送 ack（确认）。

```python
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    # Processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='task_queue',
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
```

如果消费者在处理完消息后没有确认（ack），消息会重新返回队列中并分派给其他消费者。

另外，还有一些其他策略可以帮助确保消息不丢失：

- **合理设置重试策略**：如果消费者无法处理消息，一定要有适当的重试机制，避免消息未处理就删除。

- **消息复制**：将消息复制到多个节点，提高容错性。我们可以利用 RabbitMQ 的集群功能来实现这一点。
