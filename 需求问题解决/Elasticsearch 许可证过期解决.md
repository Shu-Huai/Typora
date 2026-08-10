# Elasticsearch 许可证过期解决

## 问题描述

启动 Elasticsearch 后，日志中出现如下信息：

```text
CompileCommand: dontinline java/lang/invoke/MethodHandle.setAsTypeCache bool dontinline = true
CompileCommand: dontinline java/lang/invoke/MethodHandle.asTypeUncached bool dontinline = true
```

同时，Elasticsearch 可以正常启动，日志中能看到：

```text
started {MS-7D30}
current.health="YELLOW"
```

但是随后出现许可证相关错误：

```text
LICENSE [EXPIRED] ON [MONDAY, JUNE 08, 2026]
blocking [cluster:monitor/nodes/stats] operation due to expired license
current license is non-compliant for [security]
```

具体表现为：Elasticsearch 节点本身已经启动，但是部分监控、集群状态、节点统计相关接口无法正常访问，例如：

```
GET /_cluster/health
GET /_nodes/stats
GET /_cluster/stats
GET /_cat/indices
```

日志中还可能出现类似错误：

```text
SecurityActionFilter blocking [cluster:monitor/nodes/stats] operation due to expired license.
Cluster health, cluster stats and indices stats operations are blocked on license expiration.
All data operations (read and write) continue to work.
```

这说明 Elasticsearch 并不是启动失败，也不是 Java 参数错误，而是许可证过期导致部分 X-Pack 功能被限制。

## 问题原因

日志中的 `CompileCommand: dontinline ...` 不是错误，而是 Elasticsearch 启动时传给 JVM 的参数输出：

```text
-XX:CompileCommand=dontinline,java/lang/invoke/MethodHandle.setAsTypeCache
-XX:CompileCommand=dontinline,java/lang/invoke/MethodHandle.asTypeUncached
```

这些参数用于控制 JVM JIT 编译行为，属于正常启动信息，不需要处理。

真正的问题是 Elasticsearch 的 trial 许可证已经过期：

```text
LICENSE [EXPIRED] ON [MONDAY, JUNE 08, 2026]
```

Elasticsearch 8.x 默认启用 X-Pack Security。试用许可证过期后，部分商业功能会进入受限状态，其中包括：

- cluster health
- cluster stats
- node stats
- indices stats
- watcher
- monitoring
- graph
- ml
- transform
- sql 等功能

其中比较关键的是，`cluster health`、`cluster stats`、`nodes stats` 这些接口被拦截后，会影响很多客户端、管理工具、MCP 工具、Kibana 或监控组件的正常工作。

因此，当前问题的核心不是：

```text
CompileCommand
```

也不是：

```text
JDK 23
```

也不是：

```text
Elasticsearch 没有启动成功
```

而是：

```text
Elasticsearch trial license 已过期，需要切换到 Basic 许可证，或者重新安装有效许可证。
```

![License Management UI in Kibana.](http://public.file.lvshuhuai.cn/images\License-Management-UI-1-1.png)

## 解决办法

### 查看当前许可证状态

在 PowerShell 中执行：

```powershell
curl.exe -u elastic:<你的elastic密码> -X GET "http://localhost:9200/_license?pretty"
```

如果返回结果中包含类似内容：

```json
{
  "license": {
    "status": "expired",
    "type": "trial"
  }
}
```

说明当前确实是 trial 许可证过期。

### 切换到免费的 Basic 许可证

如果只是个人开发、本地使用、普通搜索、索引、读写数据，一般不需要 trial 许可证，直接切换到 Basic 即可。

执行：

```powershell
curl.exe -u elastic:<你的elastic密码> -X POST "http://localhost:9200/_license/start_basic?acknowledge=true"
```

如果执行成功，一般会返回类似结果：

```json
{
  "acknowledged": true,
  "basic_was_started": true
}
```

这表示 Elasticsearch 已经从过期 trial 许可证切换到了 Basic 许可证。

### 验证许可证是否恢复正常

继续执行：

```powershell
curl.exe -u elastic:<你的elastic密码> -X GET "http://localhost:9200/_license?pretty"
```

正常情况下，应该能看到类似内容：

```json
{
  "license": {
    "status": "active",
    "type": "basic"
  }
}
```

重点看两个字段：

```text
status: active
type: basic
```

如果是 `active + basic`，说明许可证问题已经解决。

### 验证集群接口是否恢复

执行：

```powershell
curl.exe -u elastic:<你的elastic密码> -X GET "http://localhost:9200/_cluster/health?pretty"
```

再执行：

```powershell
curl.exe -u elastic:<你的elastic密码> -X GET "http://localhost:9200/_nodes/stats?pretty"
```

如果不再出现：

```text
current license is non-compliant for [security]
```

说明许可证导致的接口阻塞已经消失。