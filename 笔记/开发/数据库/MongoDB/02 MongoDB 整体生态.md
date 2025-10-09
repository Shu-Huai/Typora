# MongoDB 整体生态

## 整体生态

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-11-1757226456616-31.png)

## MongoDB Server

MongoDB 数据库，包含如下核心功能：

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-4-1757226468287-34.png)

### [社区版本](https://www.mongodb.com/try/download/community)

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-10-1757226479589-37.png)

### [企业版本](https://www.mongodb.com/try/download/enterprise)

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-9-1757226524001-40.png)

## MongoDB Cloud

[MongoDB Cloud](https://docs.mongodb.com/cloud/)

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-8-1757226539763-43.png)

## MongoDB Drivers

[MongoDB Drivers](https://docs.mongodb.com/ecosystem/drivers/)

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-6-1757226559707-46.png)

[驱动相关的文档](https://docs.mongodb.com/drivers/java/)

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-7-1757226564343-49.png)

## 工具相关

[MongoDB Tools](https://docs.mongodb.com/tools/)

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-5-1757226589050-52.png)

### MongoDB Atlas Open Service Broker

[Open Service Broker](https://www.openservicebrokerapi.org/)

https://www.jdon.com/49640

### MongoDB Connector for BI

[MongoDB Connector for BI](https://docs.mongodb.com/bi-connector/current/)

BI 是指 Business Intelligence，众所周知的 BI 工具有 Tableau、MicroStrategy 和 Qlik 等；而 MongoDB BI Connector 充当在 mongod 或 mongos 实例与 BI 工具之间转换查询和数据的层， 这样用户就可以使用 SQL 创建查询，可视化，图形化和报告等方式来展示 MongoDB 中的数据。

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-1-1757226685506-55.png)

- `MongoDB DB`：数据的存储
- `BI Connector`：提供一个关系模式（Schema），以及 BI 工具和 MongoDB 之间转换 SQL 查询
- `ODBC data source name (DSN)`：连接配置数据和认证等.
- `BI Tool`：数据分析和展示工具.

### MongoDB Charts

[MongoDB Charts](https://docs.mongodb.com/charts/saas/)

负责 MongoDB 数据可视化的一个工具。

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-2-1757226779147-58.png)

### MongoDB Command Line Interface（mongocli）

[MongoDB Command Line Interface（mongocli）](https://docs.mongodb.com/mongocli/stable/)

通过命令行进行管理 Mongo 的工具，支持 Cloud 和 On-premises，Cloud 通过 MongoDB Atlas 支持；On-premises 通过 MongoDB Cloud Manager 和 MongoDB Ops Manager 支持。

### MongoDB Kubernetes Operator

[MongoDB Community Kubernetes Operator](https://github.com/mongodb/mongodb-kubernetes-operator)

将 MongoDB 部署到 Kubernetes 集群的工具。

### MongoDB Compass

[MongoDB Compass](https://docs.mongodb.com/compass/current/)

提供的对 MongoDB 进行界面化管理的工具。

> 需要注意：MongoDB 3.6+ 版本才支持这个工具；对于聚合操作的可视化是它的优势。

### MongoDB VsCode 插件

[MongoDB for VS Code](https://docs.mongodb.com/mongodb-vscode/)

MongoDB VsCode 插件

![http://public.file.lvshuhuai.cn/](http://public.file.lvshuhuai.cn/images\mongo-y-echo-3-1757226945874-61.png)

### MongoDB Shell

[MongoDB Shell](https://docs.mongodb.com/mongodb-shell/)

mongosh 是一个 MongoDB 的 shell 工具。

### MongoDB Kafka Connector

[MongoDB Kafka Connector](https://docs.mongodb.com/kafka-connector/current/)

MongoDB 连接 kafka 的工具。

### MongoDB Spark Connector

[MongoDB Spark Connector](https://docs.mongodb.com/spark-connector/current/)

MongoDB 连接 Spark 的工具。

### MongoDB Database Tools

[MongoDB Database Tools](https://docs.mongodb.com/database-tools/)

#### 二进制导入导出 

- `mongodump` Creates a binary export of the contents of a mongod database.
- `mongorestore` Restores data from a mongodump database dump into a mongod or mongos
- `bsondump` Converts BSON dump files into JSON.

#### 数据导入导出 

- `mongoimport` Imports content from an Extended JSON, CSV, or TSV export file.
- `mongoexport` Produces a JSON or CSV export of data stored in a mongod instance.

#### 诊断工具 

- `mongostat` Provides a quick overview of the status of a currently running mongod or mongos instance.
- `mongotop` Provides an overview of the time a mongod instance spends reading and writing data.

#### GridFS 工具 

- `mongofiles` Supports manipulating files stored in your MongoDB instance in GridFS objects.