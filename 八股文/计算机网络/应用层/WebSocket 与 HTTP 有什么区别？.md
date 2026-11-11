# WebSocket 与 HTTP 有什么区别？

## 回答重点

WebSocket 和 HTTP 最本质的区别就在于**通信方向**。HTTP 是单向的，客户端问一句，服务器答一句，答完就断；WebSocket 是双向的，建立连接后，双方都能主动给对方发消息，想什么时候发就什么时候发，不用等对方先开口。

HTTP 的问题在于实时性太差。比如你要做一个在线聊天室或者实时股票行情，用 HTTP 只能靠客户端不停地轮询，每隔 1 秒发一个请求问“有新消息没”，服务器每次都要回“没有”或者“有”。10 万用户同时在线，每秒就是 10 万个请求，服务器扛不住不说，消息延迟还高。

WebSocket 就是为了解决这个痛点。它复用了 HTTP 的握手流程，第一次请求还是走 HTTP，带上 `Upgrade: websocket` 头告诉服务器要升级协议，服务器同意后返回 101 状态码，之后整个 TCP 连接就切到 WebSocket 协议了，双方可以随时推送数据，连接一直保持着，省掉了反复建连的开销。

![](Z:/Public/images/hOilfHBl_XEWH9Oo7cn_mianshiya.webp)

## 扩展知识

### WebSocket 握手过程

WebSocket 握手其实就是借 HTTP 的壳来完成协议切换，整个过程就一个来回。

客户端先发一个 HTTP GET 请求，路径就是 WebSocket 的地址，关键是要带上这几个头：

```http
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

`Sec-WebSocket-Key` 是客户端随机生成的 Base64 字符串，服务器收到后会拿它和一个固定的 GUID 拼接，做一次 SHA-1 哈希再 Base64 编码，得到 `Sec-WebSocket-Accept` 返回给客户端。这个机制的目的是防止一些不支持 WebSocket 的代理服务器误把普通 HTTP 请求当成 WebSocket 连接。

服务器同意升级就返回：

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

![](Z:/Public/images/9LY6LPJs_gig9y5m7mv_mianshiya.webp)

握手完成后，底层 TCP 连接不断，但上层协议已经从 HTTP 切到 WebSocket 了。

### 帧格式和数据传输

WebSocket 的数据传输不是裸的 TCP 流，它有自己的帧格式。每个帧的头部包含几个关键字段：

1. FIN 位表示这是不是消息的最后一帧，WebSocket 支持把大消息拆成多帧发送

2. Opcode 标识帧类型，0x1 是文本帧，0x2 是二进制帧，0x8 是关闭帧，0x9 是 Ping，0xA 是 Pong

3. Mask 位和 Masking-Key 用于数据掩码，规范要求客户端发给服务器的数据必须掩码，服务器发给客户端的不用。这个设计是为了防止恶意客户端构造特定字节序列骗过中间代理的缓存

4. Payload Length 表示数据长度，小于 126 字节直接用 7 位表示，126-65535 用后续 2 字节，更大的用 8 字节

### 心跳保活

WebSocket 连接建立后，如果长时间没有数据传输，中间的 NAT 设备或者防火墙可能会把连接干掉。所以需要心跳机制来保活。

WebSocket 协议内置了 Ping/Pong 帧，客户端或服务器可以定期发 Ping，对方收到后必须回 Pong。实际开发中，很多框架会自动处理这个，比如 Spring WebSocket 默认 25 秒发一次心跳。

业务层也可以自己实现心跳，比如每 30 秒发一个 `{"type":"ping"}` 的业务消息，收到 `{"type":"pong"}` 就认为连接正常。这种方式更灵活，可以顺带传一些业务状态。

### 典型应用场景

1. 即时通讯：微信网页版、Slack、Discord 的消息推送都是 WebSocket

2. 实时行情：股票、加密货币交易所的价格推送，要求延迟在毫秒级

3. 协同编辑：Google Docs、飞书文档的多人实时协作，每个人的操作都要立刻同步给其他人

4. 游戏：H5 游戏的实时交互，玩家位置、战斗状态的同步

5. 监控大屏：运维监控系统的指标实时刷新

### HTTP 长轮询和 SSE 的对比

在 WebSocket 出现之前，实时推送主要靠这两种方案：

**长轮询**：客户端发请求，服务器不立刻响应，而是挂起请求，等有新数据了再返回。客户端收到响应后立刻再发一个请求。这样能减少空轮询，但每条消息还是要一次 HTTP 往返。

**SSE**：Server-Sent Events，服务器单向推送。客户端用 EventSource 建立连接，服务器可以持续推送数据，但客户端想发消息还得走普通 HTTP。适合服务器主动推、客户端只读的场景，比如新闻推送。

| 特性 | HTTP 轮询 | HTTP 长轮询 | SSE | WebSocket |
| --- | --- | --- | --- | --- |
| 通信方向 | 单向 | 单向 | 单向 | 双向 |
| 实时性 | 差 | 中等 | 好 | 好 |
| 服务器压力 | 高 | 中等 | 低 | 低 |
| 浏览器兼容 | 全支持 | 全支持 | IE 不支持 | IE 10+ |
| 断线重连 | 需自己实现 | 需自己实现 | 自动重连 | 需自己实现 |

## 面试官追问

#### 提问：WebSocket 连接断了怎么办？有没有自动重连机制？

回答：WebSocket 协议本身没有自动重连，连接断了就是断了。实际开发中得自己实现重连逻辑，一般的做法是监听 onclose 和 onerror 事件，触发后启动重连。重连策略通常用指数退避，第一次 1 秒后重连，失败了 2 秒，再失败 4 秒，最大退到 30 秒或 1 分钟封顶，避免服务器刚挂掉就被重连请求打爆。如果用 Socket.IO 这类库，重连机制是内置的，开箱即用。

#### 提问：WebSocket 可以跨域吗？

回答：可以，WebSocket 不受浏览器同源策略限制，客户端可以连任意域名的 WebSocket 服务。但服务端通常会校验 Origin 头，防止被恶意网站滥用。Nginx 代理 WebSocket 时要注意配置 `proxy_set_header Upgrade` 和 `proxy_set_header Connection`，不然握手会失败。

#### 提问：为什么客户端发的数据要做掩码处理，服务端发的不用？

回答：这是为了防止缓存投毒攻击。早年有些 HTTP 代理不认识 WebSocket，会把 WebSocket 帧当成普通 HTTP 数据缓存。恶意客户端可以构造特定字节序列，让代理误以为这是一个 HTTP 响应，从而污染代理的缓存。客户端数据掩码后，每次发送的字节都不一样，就没法构造这种攻击了。服务端发的数据不需要掩码，因为攻击者控制不了服务端。

#### 提问：大量 WebSocket 连接怎么做负载均衡？

详细解答可以看：[解释什么是 WebSocket？并描述如何在 Nginx 中配置 WebSocket 代理？](https://www.mianshiya.com/question/1811361112956903425)

回答：WebSocket 是长连接，不能像 HTTP 那样每次请求都负载均衡到不同机器。一般做法是用 Nginx 或 HAProxy 在握手阶段做一次负载均衡，连接建立后就绑定到那台后端机器了。如果用 Nginx，要配置 `ip_hash` 或者 `sticky session` 保证同一个客户端的请求落到同一台机器。更大规模的场景会用专门的网关，比如 Kong、APISIX，或者自研连接层，把连接管理和业务逻辑分开。
