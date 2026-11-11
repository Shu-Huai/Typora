# 什么是 Restful 风格的接口？

## 回答重点

RESTful 风格的核心思想是**用 URL 定位资源，用 HTTP 动词描述操作**。

URL 里只放资源名词，不放动词。想对资源做什么操作，全靠 HTTP 方法来表达：

![](Z:/Public/images/bWQT9cxR_NOum3IGcDY_mianshiya.webp)

比如用户资源 `/users`，RESTful 的写法：

```java
@RestController
@RequestMapping("/users")
public class UserController {
    
    @GetMapping           // GET /users - 获取所有用户
    public List<User> list() { ... }
    
    @GetMapping("/{id}")  // GET /users/1 - 获取单个用户
    public User get(@PathVariable Long id) { ... }
    
    @PostMapping          // POST /users - 创建用户
    public User create(@RequestBody User user) { ... }
    
    @PutMapping("/{id}")  // PUT /users/1 - 更新用户
    public User update(@PathVariable Long id, @RequestBody User user) { ... }
    
    @DeleteMapping("/{id}") // DELETE /users/1 - 删除用户
    public void delete(@PathVariable Long id) { ... }
}
```

## 扩展知识

### REST 到底是什么

REST 是 Representational State Transfer 的缩写，直译是“表述性状态转移”，前面还有个隐含的主语 Resource，完整意思是“资源的表述性状态转移”。

听着挺玄乎，其实核心就一句话：HTTP 协议本身就定义好了各种动词的含义，GET 是获取、POST 是创建、PUT 是更新、DELETE 是删除。

既然协议都约定好了，那 URL 里就别再重复写什么 getXxx、addXxx 了，URL 只用来标识资源就行。

比如获取一个 user：

- 错误姿势：`GET /getUserById?userId=1`。

- 正确姿势：`GET /users/1`。

再比如新增 user：

- 错误姿势：`POST /addUser （省略body）`。

- 正确姿势：`POST /users （省略body）`。

说白了 RESTful 就是要求你正确使用 HTTP 协议，把 HTTP 当协议用，不是当传输管道用。

### HTTP 方法的语义和幂等性

在 RESTful 风格中，HTTP 方法应该遵循其语义：

- **GET**：用于获取资源，不会修改资源的状态。是幂等的（多次请求返回结果相同）。

- **POST**：用于创建资源，向服务器发送新数据，可能改变服务器端的状态。非幂等的。

- **PUT**：用于更新资源（如果资源不存在，则可以根据需要创建），是幂等的。

- **PATCH**：用于部分更新，是非幂等的。

- **DELETE**：用于删除资源，是幂等的。

![](Z:/Public/images/tN3O9MWr_KVlABVptht_mianshiya.webp)

幂等性在分布式系统里特别重要。比如网络抖动导致请求重发，幂等的操作重发多少次结果都一样，不会出问题。

GET 请求查 100 遍结果都一样；DELETE 删 100 遍，资源第一次就没了，后面 99 次啥也不干。

但 POST 不行，每调一次可能就多创建一条数据。

### URI 设计规范

1. 用名词复数表示资源集合，不要用动词

```text
正确：GET /users、POST /orders
错误：GET /getUsers、POST /createOrder
```

2. 用路径表示资源层级关系

```text
GET /users/1/orders      // 用户 1 的所有订单
GET /users/1/orders/5    // 用户 1 的第 5 号订单
```

3. 查询参数用于过滤、分页、排序

```text
GET /users?status=active&page=2&size=20&sort=createTime,desc
```

4. 不要在 URL 里加文件扩展名，用 Accept 头指定返回格式

```text
正确：GET /users/1，配合 Accept: application/json
错误：GET /users/1.json
```

### 状态码要用对

RESTful 接口应该正确使用 HTTP 状态码，别啥都返回 200：

| 状态码 | 含义 | 使用场景 |
| --- | --- | --- |
| `200 OK` | 成功 | GET 请求成功返回数据 |
| `201 Created` | 已创建 | POST 创建资源成功 |
| `204 No Content` | 无内容 | DELETE 成功，不返回数据 |
| `400 Bad Request` | 请求错误 | 参数校验失败 |
| `401 Unauthorized` | 未认证 | 没登录或 token 过期 |
| `403 Forbidden` | 无权限 | 登录了但没权限访问 |
| `404 Not Found` | 不存在 | 找不到 |
| `500 Internal Server Error` | 服务器错误 | 代码抛异常了 |

### HATEOAS：理想很丰满现实很骨灰

HATEOAS 是 REST 提出的一个进阶概念，全称 Hypermedia as the Engine of Application State。

简单说就是接口返回结果里要带上链接，告诉客户端接下来能干什么。

比如查用户列表，返回结果除了用户数据，还要带上相关操作的链接：

```json
{
    "users": [
        {
            "id": 1,
            "name": "张三",
            "links": [
                {"href": "/users/1", "rel": "self", "method": "GET"},
                {"href": "/users/1", "rel": "edit", "method": "PUT"},
                {"href": "/users/1", "rel": "delete", "method": "DELETE"}
            ]
        }
    ],
    "links": [
        {"href": "/users", "rel": "create", "method": "POST"}
    ]
}
```

links 里没返回的操作，说明客户端当前不能执行。比如没返回 DELETE 链接，就表示当前用户没权限删。

听起来挺美好，客户端不用硬编码 URL 了，服务端改 URL 也不怕。

但现实中基本没人这么干，返回体太臃肿，实现成本高，收益又不明显。知道有这么个概念就行。

### RESTful vs SOAP vs GraphQL

| 维度 | RESTful | SOAP | GraphQL |
| --- | --- | --- | --- |
| 协议 | HTTP | HTTP/SMTP/TCP 都行 | HTTP |
| 数据格式 | JSON 为主 | 只能 XML | JSON |
| 灵活性 | URL 固定，返回固定 | 固定 | 客户端定义返回字段 |
| 学习成本 | 低 | 高 | 中等 |
| 适用场景 | 通用 Web API | 企业级、银行、保险 | 复杂查询、移动端 |

GraphQL 解决了 RESTful 的一个痛点：获取数据要么多了要么少了。比如首页需要用户名和头像，列表页需要用户全部信息，RESTful 要么返回全部字段浪费带宽，要么搞两个接口麻烦。GraphQL 让客户端自己定义要哪些字段，精准获取。但 GraphQL 的缓存比 RESTful 难做，各有取舍。

## 面试官追问

#### 提问：PUT 和 PATCH 有什么区别？实际项目中你们怎么用的？

回答：PUT 是全量替换，要把资源的所有字段都传过去；PATCH 是部分更新，只传要改的字段。实际项目中用 PATCH 更多，因为大部分场景就是改某几个字段，没必要把整个对象都传一遍。不过很多团队图省事，全都用 POST 带个 body，也能跑，就是不够规范。

#### 提问：RESTful 接口怎么做版本控制？

回答：常见三种方式。一是 URL 路径里带版本号，比如 /v1/users、/v2/users，简单直观但 URL 会变。二是用 Header，比如 Accept: application/vnd.myapi.v1+json，URL 干净但调试不方便。三是用查询参数 /users?version=1，不太推荐因为查询参数本意是过滤用的。大部分公司选第一种，简单好理解。

#### 提问：如果一个操作不是简单的增删改查，比如“审批通过”，RESTful 怎么设计？

回答：有两种思路。一种是把操作建模成资源，比如 POST /orders/1/approval 表示创建一条审批记录。另一种是用 PATCH 修改状态，比如 PATCH /orders/1 body 里带 {“status”: “approved”}。第一种更符合 REST 理念，第二种更简单直接。实际中看团队习惯，别太教条。

#### 提问：RESTful 接口返回的错误信息应该怎么设计？

回答：首先状态码要用对，400 系列表示客户端错误，500 系列表示服务端错误。然后响应体里要有错误码和错误描述，方便前端展示和排查问题。比如 {“code”: “USER_NOT_FOUND”, “message”: “用户不存在”, “detail”: “userId=123”}。有些公司还会加 traceId 方便查日志。别啥错误都返回 200 然后 body 里塞个 success: false，状态码就是干这事的。
