# 如何在 RabbitMQ 中创建一个镜像队列？

## 回答重点

在 RabbitMQ 中，创建一个镜像队列主要是通过在声明队列时设置队列的策略来实现的。具体步骤如下：

1. 首先，启动 RabbitMQ 管理插件。可以通过以下命令启用 RabbitMQ 管理插件：

```bash
rabbitmq-plugins enable rabbitmq_management
```

2. 然后，打开 RabbitMQ 管理界面，默认是 `http://localhost:15672`。登录后，进入“Admin”选项卡。
3. 接着，点击“Policies”标签，并创建一个新策略。策略名称如“mirror_all”，在“Pattern”字段中输入 `.^queue_name$` 表示对哪个队列进行镜像，或者使用 `.*` 表示所有队列。
4. 在“Definition”字段中，输入 `{ "ha-mode": "all" }` 表示所有队列都将被镜像到所有节点上。
5. 最后，点击“Add policy”按钮保存策略。

## 扩展知识

下面可以了解镜像队列以及如何利用代码实现这一过程。

1. 镜像队列的概念
镜像队列是指在 RabbitMQ 中将队列的所有消息备份到其他节点上。这样，即使一个节点宕机，其他节点仍然可以提供服务，从而保证了系统的高可用性。

2. 镜像队列策略参数
“ha-mode”的取值有三个：

- `all`：将队列复制到所有节点上。

- `exactly`：将队列复制到指定数量的节点。

- `nodes`：将队列复制到指定名称的节点。

3. 使用 RabbitMQ CLI 设置策略
我们也可以通过 RabbitMQ 的 CLI（命令行接口）来设置策略，例如：

```bash
rabbitmqctl set_policy ha-all ".*" '{"ha-mode":"all"}' --priority 1
```

4. 通过代码实现镜像队列
可以使用合适的编程语言的库来连接和操作 RabbitMQ，例如 Python 和 Java。以下是一个 Python 示例，利用 `pika` 库：

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

arguments = {
    "x-ha-policy": "all"
}

channel.queue_declare(queue='hello', durable=True, arguments=arguments)

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!',
                      properties=pika.BasicProperties(
                         delivery_mode=2,  # make message persistent
                      ))

print(" [x] Sent 'Hello World!'")
connection.close()
```
