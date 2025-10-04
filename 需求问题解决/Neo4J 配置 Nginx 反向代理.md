# Neo4J 配置存储目录、IPv6 和 Nginx 反向代理

## 环境

- Windows 11
- Nginx 版本 1.23
- Nginx 已安装 stream

## 配置存储目录

在 `Neo4J/conf/neo4j.conf` 中改写如下配置

```properties
server.directories.data=D:\\Neo4J\data
server.directories.plugins=D:\\Neo4J\plugins
server.directories.logs=D:\\Neo4J\logs
server.directories.lib=D:\\Neo4J\lib
server.directories.run=D:\\Neo4J\run
server.directories.licenses=D:\\Neo4J\licenses
server.directories.transaction.logs.root=D:\\Neo4J\data\transactions
```

## 配置 IPv6

同样在该文件中

```properties
server.default_listen_address=::
```

## 配置 Nginx

在 `Nginx/conf/nginx.conf` 中改写如下配置

```properties
stream {
    # Neo4j BOLT 标准端口（仅 IPv6）
    server {
        listen [::]:17687;          # 外部用 bolt://neo4j.lvshuhuai.cn:7687
        proxy_connect_timeout 10s;
        proxy_timeout 600s;

        # 直转发到本机 Neo4j BOLT（IPv6 回环）
        proxy_pass [::1]:7687;
        # 用 localhost 也可以：proxy_pass localhost:7687;
    }
}
http {
    server {
        listen       [::]:80;
        server_name neo4j.lvshuhuai.cn;
        location / {
            proxy_pass http://localhost:7474;

            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_next_upstream     http_500 http_502 http_503 http_504 error timeout invalid_header;
            proxy_set_header        Host  $http_host;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```