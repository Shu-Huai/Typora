# REST与SSE契约

## 文档范围

本文列出当前前后端直接使用的接口与 SSE 事件。字段细节以 Knife4j/OpenAPI 为准；本文不复制全部 Schema。

- 源码范围：`backend/.../controller`、DTO/VO、`frontend/src/api`、`frontend/src/utils/sse.ts`
- 描述状态：[已实现]。
- 相关文档：[[前端/对话界面]]、[[后端/Agent运行与工具]]、[[模型服务/网关与模型接口]]。

## REST 接口

除登录、后端健康检查、SSE 订阅和 OpenAPI 页面外，后端接口均要求 JWT。管理员接口还要求 `ROLE_ADMIN`。

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| `POST` | `/api/auth/login` | 公开 | 返回访问 Token 与当前用户 |
| `GET` | `/api/health` | 公开 | 后端存活检查 |
| `POST` | `/api/conversations` | 登录 | 创建会话，可带初始消息 |
| `GET` | `/api/conversations` | 登录 | 普通用户只看自己的会话；管理员可见全部 |
| `GET` | `/api/conversations/{id}` | 登录 | 返回消息、运行、工具和证据轨迹 |
| `POST` | `/api/conversations/{id}/messages` | 登录 | 创建用户消息并返回 `runId` |
| `POST` | `/api/conversations/{id}/event-ticket?runId=` | 登录 | 申请一次性短效 SSE 票据 |
| `GET` | `/api/conversations/{id}/events?ticket=` | 票据 | 订阅对应 Run 的 SSE |
| `GET/POST/PATCH` | `/api/users...` | 管理员 | 用户列表、创建、启停 |
| `GET/POST/PATCH/DELETE` | `/api/knowledge...` | 管理员 | PDF 上传、状态、检索、重建、删除 |

所有普通 JSON 接口使用 `Response<T>` 包装，成功码为 `0`。`BaseException` 映射到约定业务码，例如 `BAD_REQUEST`、`UNAUTHORIZED`、`FORBIDDEN`、`NOT_FOUND`、`CONFLICT`、`MODEL_ERROR` 和 `INTERNAL_ERROR`。

## SSE 事件

客户端先申请票据，再通过原生 `EventSource` 订阅。票据只可消费一次，默认一分钟过期；连接默认最长 30 分钟，默认每 15 秒发送心跳。

| 事件 | 数据 | 前端处理 |
| --- | --- | --- |
| `RUN_STATUS` | 无或运行状态信息 | 标记运行中 |
| `MODEL_TURN_STARTED` | 无 | 当前界面未单独渲染 |
| `MODEL_PUBLIC_SUMMARY` | `AnalysisUpdateVO` | 追加公开摘要 |
| `TOOL_START` | `ToolEventVO` | 创建/更新运行中的工具卡片 |
| `TOOL_RESULT` | `ToolEventVO` | 更新成功或失败摘要 |
| `MESSAGE_START` | 无 | 清空临时增量文本 |
| `MESSAGE_DELTA` | `{ delta }` | 追加流式回答 |
| `MESSAGE_COMPLETE` | `AgentMessageVO` | 入库消息显示为正式回答 |
| `ERROR` | 错误文本 | 标记运行失败 |
| `DONE` | 无 | 关闭 EventSource 并刷新详情 |
| `HEARTBEAT` | 无 | 保活，不显示 |

[已知边界] SSE 事件缓冲在后端内存中，适用于当前单实例。页面断线时会刷新数据库中持久化的结果，但不能恢复未持久化的中间增量字符。

