# MCP 配置

![Make MCP Client | Make](http://public.file.lvshuhuai.cn/images\imageurl=https%3A%2F%2Fimages.ctfassets.net%2Fun655fb9wln6%2FO1jb0qQ6xvOJBCkbFGIpX%2F1e2e6cdf8c1f4b7603e7fc857d5a1e1a%2Fhero.jpeg)

## Redis

```json
{
  "mcpServers": {
    "RedisMCPServer": {
      "command": "uvx",
      "args": [
        "--from",
        "redis-mcp-server@latest",
        "redis-mcp-server",
        "--url",
        "redis://redis.lvshuhuai.cn:6379/"
      ]
    }
  }
}
```

## Neo4J

```json
{
  "mcpServers": {
    "neo4j": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "-q",
        "--from",
        "neo4j-mcp-server",
        "python",
        "-m",
        "neo4j_mcp_server"
      ],
      "env": {
        "NEO4J_URI": "bolt://neo4j.lvshuhuai.cn:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "你的密码",
        "NEO4J_DATABASE": "neo4j",
        "NEO4J_READ_ONLY": "false",
        "NEO4J_TELEMETRY": "false",
        "NEO4J_LOG_LEVEL": "error",
        "NEO4J_LOG_FORMAT": "text",
        "NEO4J_SCHEMA_SAMPLE_SIZE": "100"
      }
    }
  }
}
```

## PostgreSQL

```json
{
  "mcpServers": {
    "postgres": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "-q",
        "postgres-mcp",
        "--access-mode=unrestricted"
      ],
      "env": {
        "DATABASE_URI": "postgresql://postgres:<你的密码>@postgres.lvshuhuai.cn:5432/postgres"
      }
    }
  }
}
```

## MongoDB

```json
{
  "mcpServers": {
    "MongoDB": {
      "command": "npx",
      "args": ["-y", "mongodb-mcp-server@latest"],
      "env": {
        "MDB_MCP_CONNECTION_STRING": "mongodb://mongodb.lvshuhuai.cn:27017/"
      }
    }
  }
}
```

## ElasticSearch

```json
{
  "mcpServers": {
    "elasticsearch-mcp-server": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "ES_URL",
        "-e", "ES_API_KEY",
        "-e", "ES_USERNAME",
        "-e", "ES_PASSWORD",
        "docker.elastic.co/mcp/elasticsearch",
        "stdio"
      ],
      "env": {
        "ES_URL": "<elasticsearch-cluster-url>",
        "ES_API_KEY": "<elasticsearch-API-key>",
        "ES_USERNAME": "elastic",
        "ES_PASSWORD": "<你的密码>"
      }
    }
  }
}
```

## MySQL

```json
{
  "mcpServers": {
    "mysql": {
      "name": "MySQL 数据库",
      "description": "通用 MySQL MCP 连接，可访问多个数据库并执行读写、DDL 等操作",
      "enabled": true,
      "transport": "stdio",
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@benborla29/mcp-server-mysql"
      ],
      "env": {
        "MYSQL_HOST": "mysql.lvshuhuai.cn",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "lvzhi",
        "MYSQL_PASS": "你的密码",
        "MYSQL_DB": "",

        "ALLOW_INSERT_OPERATION": "true",
        "ALLOW_UPDATE_OPERATION": "true",
        "ALLOW_DELETE_OPERATION": "true",
        "ALLOW_DDL_OPERATION": "true",
        "MULTI_DB_WRITE_MODE": "true",

        "MYSQL_DISABLE_READ_ONLY_TRANSACTIONS": "true",
        "MYSQL_QUERY_TIMEOUT": "30000",
        "MYSQL_RATE_LIMIT": "60"
      }
    }
  }
}
```

