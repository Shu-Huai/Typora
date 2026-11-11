# 如何确保 RabbitMQ 在极端情况下不会丢失消息？

## 回答重点

要确保 RabbitMQ 在极端情况下不会丢失消息，主要要采取以下几项措施：

1. 使用持久化队列和持久化消息。
2. 启用镜像队列。
3. 使用发布确认（Publisher Confirms）。
4. 使用消费者确认（Consumer Acknowledgements）。
5. 设置合理的故障转移策略和集群配置。

## 扩展知识

1. **持久化队列和持久化消息**：消息队列默认情况下有两种类型，持久和非持久。持久队列和持久消息会在服务器重启后依然存在。创建持久队列时，需要指定 `durable=true`。同时，发送的消息也需要设置 `delivery_mode=2`，表示消息持久化：

```python
# 创建持久化队列
channel.queue_declare(queue='my_queue', durable=True)

# 发布持久化消息
channel.basic_publish(exchange='',
                      routing_key='my_queue',
                      body='Hello, world!',
                      properties=pika.BasicProperties(delivery_mode=2))
```

2. **镜像队列**：镜像队列通过在集群中的多个节点上复制队列内容来提高数据的可用性和可靠性。这样即使一个节点宕机，依然可以从另一个节点上读取消息。镜像队列可以通过策略来配置：

```bash
rabbitmqctl set_policy ha-all "^" '{"ha-mode":"all"}'
```

3. **发布确认**：开启发布确认模式后，RabbitMQ 会为每条发送的消息返回确认消息。可以通过这种机制确保消息已经被正确地记录并存储在服务器上。

```python
channel.confirm_delivery()  # 启用发布确认模式

if channel.basic_publish(exchange='',
                         routing_key='my_queue',
                         body='Hello, world!',
                         properties=pika.BasicProperties(delivery_mode=2)):
    print("Message published successfully")
else:
    print("Message could not be published")
```

4. **消费者确认**：确保消息被消费者成功处理后再从队列中删除。消费者需要向 RabbitMQ 发送确认消息（`ack`）来表明消息已被正确处理。

```python
def callback(ch, method, properties, body):
    print(f"Received {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='my_queue', on_message_callback=callback, auto_ack=False)
```

5. **集群配置与故障转移**：为了提高 RabbitMQ 的可用性，可以设置集群并配置自动故障转移。当一个节点发生故障时，其他节点会自动接管其工作。通过 `rabbitmqctl cluster_status` 可以查看集群状态，并使用 `rabbitmqctl join_cluster` 命令来添加新节点。
