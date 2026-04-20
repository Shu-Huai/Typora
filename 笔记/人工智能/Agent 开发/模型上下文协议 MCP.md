# 模型上下文协议 MCP

## MCP 的定位：它到底在系统里解决什么问题

MCP（Model Context Protocol）首先是一套**协议**，而不是一个模型、一个 agent 框架，或者某个具体产品的“插件功能”。它处理的是这样一个问题：当一个 AI 应用需要访问外部世界时，外部能力应该如何被标准化地暴露出来，应用又应当如何发现这些能力、读取这些内容、调用这些动作，并在一条连接里维持有状态的会话。

如果只用一句话概括：

> MCP 是 AI 应用连接外部工具、外部上下文和外部提示模板的一套标准接口。

这里有两个词尤其重要：**连接** 和 **标准**。

- 它关注的是“怎么接入外部能力”，不是“模型内部怎么推理”。
- 它关注的是“协议对象怎么统一”，不是“某个业务流程怎么编排”。

因此，MCP 和下面这些概念需要严格区分：

- **不是 LLM 本身**：模型负责理解和生成，MCP 负责把外部世界整理成模型可访问的形式。
- **不是 Agent 本身**：Agent 关注自主决策、循环执行、规划和状态推进；MCP 只提供连接外部能力的协议层。
- **不是 Workflow**：Workflow 关注步骤编排、路由、重试、人工审批；MCP 不负责定义这些业务流转。
- **不是 Function Calling 的简单改名**：Tool 只是 MCP 的一部分，MCP 还同时建模了 Resource、Prompt、Lifecycle、Transport 等内容。

理解这一点非常关键。很多人在刚接触 MCP 时，会误把它理解成“另一种 tool calling 框架”。这种理解太窄了。更准确地说，MCP 是一个围绕 AI 应用外部接入问题建立起来的**协议层系统**。

### 一个最小系统图景

可以先看一个非常具体的场景：

假设你做一个 IDE 里的 AI 编码助手。用户在编辑器中输入：

> 帮我分析支付模块的空指针问题，并给我一个 commit message。

为了完成这件事，AI 应用可能需要同时接入几类外部能力：

- 代码文件和项目目录
- Git 仓库历史
- 公司内部设计文档
- 工单系统

如果没有统一协议，你就需要给每种能力各写一套私有集成。MCP 的意义就在这里：它把这些不同来源的能力整理成统一的协议对象，然后由 AI 应用按统一方式访问。

在这个系统里，可以这样划分：

- IDE 里的 AI 助手层：**Host**
- Host 内部为每个外部能力建立的协议连接器：**Client**
- 文件系统、Git、知识库、工单系统对应的能力服务：**Server**

<img src="http://public.file.lvshuhuai.cn/images\image-20260412183040045.png" alt="image-20260412183040045" style="zoom:50%;" />

Host 负责统筹整体会话，Server 提供某一类边界清晰的能力，而 Client 负责把两边通过 MCP 协议连起来。

## Participants：Host、Client、Server 如何协同

MCP 的参与者只有三类，但这三类一定要分清，否则后面的 Tools、Resources、Transport 都会看乱。

### Host 不是普通界面，而是承载 AI 能力的统筹层

Host 是最外层 AI 应用边界。它负责：

- 维护和用户的会话
- 管理模型上下文
- 决定接入哪些 MCP server
- 为每个 server 建立相应的 client
- 决定哪些资源纳入上下文、哪些工具允许被调用

这里最容易混淆的是“Host 是不是整个软件本体”。答案是不一定。

更准确的判断标准是：

> 谁在管理模型会话、MCP 连接和工具使用，谁就是 Host。

因此：

- ChatGPT 这种本身就是 AI 对话产品的网页界面，可以视为 Host。
- 一个 IDE 里的 AI 助手插件，可以视为 Host。
- 普通 IDE 本身并不自动等于 Host。
- 普通微信聊天界面也不等于 Host；如果微信里内嵌了一个真正负责 AI 会话和工具调用的助手模块，那么那个模块才更接近 Host。

顺便把一个常见误区直接讲清楚：

> **Host 不是 Agent。**
>
> Host 是承载和统筹层，Agent 是其中可能存在的一种智能行为逻辑。Host 里可以有 Agent，但 Host 本身不等于 Agent。

### Client 不是“客户端应用”，而是协议连接器

MCP 里的 Client 很容易望文生义。这里的 Client 不是“用户端软件”，而是 Host 内部的一个协议层组件。

它的职责非常专一：

- 与某一个 MCP server 建立连接
- 按 MCP 协议发送请求、接收响应和通知
- 维护这条连接对应的 session

所以，Client 不是负责展示页面，也不是负责模型推理，它是一个“面向某个 Server 的协议连接器”。

### Server 不是整个后端，而是某类能力的提供者

Server 是 MCP 中最值得用例子讲清楚的角色。

它不是整个 AI 应用，也通常不是整个业务后端。它更像是：

> 一个面向某个领域能力的 MCP 适配器。

也就是说，一个 Server 后面可能连着真正的文件系统、Git 仓库、数据库、知识库、工单系统、浏览器、天气 API，但它对外说的都是 MCP 协议。

在前面的 IDE 场景里，完全可以有这样几个 MCP server：

#### Filesystem Server

它负责把项目文件系统暴露给 AI 应用。里面通常会包含：

- 可读取的项目文件资源，例如 `file:///project/README.md`
- 文件搜索、读取、写入之类的工具
- 可选的提示模板，例如“审查当前文件”

#### Git Server

它负责把 Git 仓库能力暴露出来。里面可以有：

- 提交历史、分支信息、diff 摘要等资源
- 查看 diff、切换分支、生成提交说明等工具
- 如“根据 diff 生成 commit message”之类的 Prompt

#### Company Docs Server

它负责把公司内部知识库暴露给 AI 应用。里面可以有：

- 设计文档资源，例如 `kb://design/auth-service`
- 搜索文档、拉取某个页面、查询某个组件说明的工具
- 如“总结这份设计文档”之类的 Prompt

#### Ticket Server

它负责接入工单系统。里面可以有：

- 某条工单详情资源，例如 `ticket://INC-1024`
- 搜索工单、创建工单、更新备注的工具
- “写事故复盘草稿”这种 Prompt

### 为什么一个 Host 会管理多个 Client，而不是一个 Client 连所有 Server

<img src="http://public.file.lvshuhuai.cn/images\model_context_protocol_components-f.png" alt="How the Model Context Protocol simplifies AI development ..." style="zoom: 67%;" />

这个问题非常关键。

因为 MCP 的 Client 不是“万能总管”，而是“某一条到某个 Server 的协议连接”。之所以这样设计，至少有三个非常实际的原因：

- **隔离性**：一个 Server 崩掉，不应该影响别的 Server。
- **能力协商独立**：不同 Server 支持的 capabilities 可能不同。
- **Transport 独立**：一个 Server 可能是本地 STDIO，另一个可能是远程 Streamable HTTP。

如果把所有连接都塞进一个“大 Client”，那生命周期、权限、安全边界、错误恢复都会非常混乱。

因此更准确的心智模型是：

- Host 是总控台
- Client 是单路连接器
- Server 是某类能力端

## Primitives：Tools、Resources、Prompts 为什么要分开建模

MCP 最核心的对象模型就是三类 primitives：**Tools、Resources、Prompts**。

这三者表面上都和“模型会用到的外部能力”有关，但本质完全不同。如果一开始就把它们混成一类，后面你会不断在 Server 建模时犯错。

<img src="http://public.file.lvshuhuai.cn/images\v2-eec3578e7c52328108ac85b589114988_1440w.gif" alt="LLMs的函数调用（Function Call）和MCP——直观的对比解释- 知乎" style="zoom:50%;" />

### Tool：让模型去做事

Tool 的本质是**动作接口**。它解决的问题是：让模型触发某个可执行操作。

典型例子包括：

- 搜索工单
- 发送邮件
- 查询数据库
- 运行测试
- 写文件
- 调用外部 API

它的重点不是内容本身，而是“执行”。

#### Tool 在协议里长什么样

一个 Tool 至少应该让客户端和模型知道三件事：

- 它叫什么
- 它是干什么的
- 它需要什么参数

也就是说，好的 Tool 定义一定包含：

- `name`
- `description`
- `inputSchema`

不要小看这些字段。很多时候模型能不能稳定调用一个 Tool，和 `inputSchema` 是否清晰、参数命名是否准确、描述是否明确，直接相关。

#### Tool 的完整消息流

Tool 的协议流程可以压成一句话：

> `initialize` → `tools/list` → `tools/call`

也就是说，先建立会话并协商能力，再列出工具清单，最后调用某个具体工具。

如果把它写成一个更贴近真实系统的顺序，就是：

1. Client 与 Server 建立连接
2. 发送 `initialize`
3. 收到 `InitializeResult`
4. 再发 `notifications/initialized`
5. 发送 `tools/list`，查看有哪些 Tool
6. 模型或应用决定使用某个 Tool
7. 发送 `tools/call`
8. 读取执行结果或错误

#### model-controlled 到底是什么意思

对话里专门问过这个词。

它不是一个高深术语，意思其实很朴素：

> Tool 是否调用，主要由模型根据上下文来决定。

例如用户问：“帮我看看纽约今天的天气。”如果系统暴露了一个 `get_weather` Tool，那么模型可以自己判断“这时候应该去调用它”。

但这不等于模型拥有无限执行权。尤其是对有副作用、高风险、高权限的 Tool，实际系统依然应当有人类确认、权限控制和审计机制。

所以要把这两个概念一起记：

- **model-controlled**：模型对是否调用某个 Tool 拥有决策权
- **human-in-the-loop**：真正执行高风险动作时，人仍应当兜底

### Resource：给模型看的上下文对象

Resource 解决的不是“做什么”，而是“看什么”。

如果说 Tool 是动作，那么 Resource 就是**可读取的内容对象**。它通常用 URI 标识，可以被发现、被读取、被纳入模型上下文。

典型例子包括：

- 项目的 README
- 一张数据库表的 schema
- 某个客户的档案页
- 某份日报、周报、月报
- 某个服务的状态说明
- 某条工单的详情页

#### Resource 的核心理解

对 Resource，最准确的理解不是“只读 Tool”，而是：

> 一个适合被 URI 引用、适合被读取、适合作为上下文对象存在的内容。

URI 很重要。它不仅是地址，也是一种协议化的“可引用入口”。这使得 Host 可以围绕 Resource 做缓存、权限控制、上下文注入，甚至订阅更新。

#### Resource 和 Tool 的边界到底在哪里

这个问题是整段对话里最重要的边界问题之一。

不要用“是不是数据库来的”来区分，因为数据库里既可能有 Resource，也可能有 Tool。

更实用的判断法是：

- 如果它更像一个**对象**，优先想 Resource。
- 如果它更像一次**操作**，优先想 Tool。

举几个具体例子：

- `db://schema/orders`：更像 Resource
- `db://customer/123/profile`：更像 Resource
- `search_orders(customer_id, status, date_range)`：更像 Tool
- `execute_sql(sql=...)`：更像 Tool

原因很简单：前两个更像“那里有一个东西，你去读它”；后两个更像“帮我执行一次查询动作”。

#### Resource 的完整消息流

Resource 的基本流程是：

> `initialize` → `resources/list` → `resources/read`

也就是先列出有哪些资源，再根据具体 URI 去读取内容。

一个贴近现实的例子可以这样理解：

用户说：

> 帮我看一下项目 README 和支付模块设计文档。

此时 Host 可能先通过 Filesystem Server 和 Docs Server 分别列出资源，然后读取：

- `file:///project/README.md`
- `kb://design/payment-service`

再把这两个 Resource 的内容纳入模型上下文。

### Resource Templates：为什么“带参数”不自动等于 Tool

这是 Resource 体系里非常值得单独讲的一块。

很多内容对象本身不是固定枚举的，而是按某种规则动态生成的。例如：

- `db://customer/{id}/profile`
- `weather://forecast/{city}/{date}`
- `report://sales/{year}/{month}`

这种时候，Server 不一定要把所有具体实例都暴露在 `resources/list` 中，而可以暴露一个 `uriTemplate`。

这就引出两个概念：

- `resources/list`：列出现成资源实例
- `resources/templates/list`：列出资源 URI 模板

它们的区别可以用一句话记住：

> `resources/list` 是现货清单，`resources/templates/list` 是规格模板清单。

#### 客户端如何把 `uriTemplate` 变成具体 URI

这里没有额外的“instantiate”协议方法。客户端的做法就是：

1. 先拿到 `uriTemplate`
2. 用具体参数填进去
3. 生成真正的 URI
4. 直接对这个 URI 执行 `resources/read`

例如：

- 模板：`db://customer/{id}/profile`
- 参数：`id = 123`
- 展开后：`db://customer/123/profile`
- 接着直接读取这个 URI

也就是说，模板展开属于客户端侧的 URI 构造问题，而不是额外的协议动作。

### Completion 在 Resource Templates 里做什么

对话里还追问过 completion API。这里顺手把它并到 Resource 部分讲清楚。

在 MCP 里，completion 不是“让模型写一段话”，而更像 IDE 式的参数补全。它的作用是：

- 当 Prompt 需要参数时，给参数值候选
- 当 Resource Template 需要参数时，给模板参数候选

例如资源模板是：

```
db://customer/{id}/profile
```

当用户已经输入 `12`，客户端就可以请求 completion，让 Server 返回可能的候选值：

- `123`
- `124`
- `129`

客户端选择一个候选，再将其填回模板，构造最终 URI 去读取。

所以，Completion 在这里不是大模型生成，而是参数填充辅助。

### Prompt：协议级的提示模板，而不是代码里的普通字符串

Prompt 是 MCP 中最容易被低估的 primitive。很多人会下意识地想：我在应用里自己写一段 prompt 文本不就行了，为什么还要把 Prompt 做成协议对象？

答案在于：**发现、复用、参数化、结构化**。

#### 普通 Prompt 文本与 MCP Prompt 的差别

普通应用里的 prompt 往往只是代码中的私有实现细节。它可能是一段字符串，也可能是模板字符串，但它本质上对外不可见，也不能通过协议被发现、列举和调用。

而 MCP Prompt 是 Server 对外暴露的提示模板对象。它：

- 有名字
- 有描述
- 可以带参数
- 可以被列出
- 可以被获取
- 返回的不是一段随便的字符串，而是一组结构化消息

更准确地说：

> 普通 Prompt 文本是应用内部自己写的提示词；MCP Prompt 是 Server 对外公布的一项协议能力。

#### Prompt 更像“任务入口”而不是“动作”

Prompt 既不是读内容，也不是执行动作，它更像一套现成的任务入口。

比如下面这些都非常适合建模成 Prompt：

- “根据当前 diff 生成 commit message”
- “根据某个 incident_id 生成事故复盘草稿”
- “根据一份工单写出技术摘要”
- “对当前代码做审查并指出高风险点”

这些场景的共同点是：

- 它们都需要组织一套给模型的消息结构
- 它们都可能带参数
- 它们都是高频重复任务

#### Prompt 的消息流

Prompt 的流程非常整齐：

> `initialize` → `prompts/list` → `prompts/get`

也就是先看有哪些模板，再根据名称取某个模板展开后的消息内容。

如果模板需要参数，则客户端可以：

1. 先列出 Prompt
2. 获取所需参数定义
3. 必要时用 completion 做参数补全
4. 再通过 `prompts/get` 获取展开后的 messages
5. 把这些 messages 放入模型上下文

## Lifecycle：MCP 会话是如何建立、进入工作、再结束的

Lifecycle 是 MCP 真正的骨架之一。没有它，后面的 Tools、Resources、Prompts 只是散落在空中的对象。

### 为什么 MCP 一定要有 Lifecycle

因为 MCP 不是“发一条 JSON 就完事”的随手接口，而是一种**有状态协议**。既然有状态，就必须回答这几个问题：

- 会话从什么时候开始
- 双方在这条会话里支持什么能力
- 什么阶段可以发什么类型的消息
- 会话何时结束
- 会话失效后如何重建

Lifecycle 就是为这些问题服务的。

![sequence_diagram.drawio.png](http://public.file.lvshuhuai.cn/images\579x465.png)

### Initialization：连接一建立，第一条消息为什么必须是 `initialize`

在 MCP 中，初始化不是可选步骤，而是会话的入口。

`initialize` 的含义不是“调用某个业务功能”，而是：

> 先把这条会话的协议版本、双方能力和基本信息对齐。

所以它发生的时机不是“模型第一次调用 Tool 时”，而是**Client 与 Server 建立新连接/新会话时**。

#### 它到底是在什么时候发生

这个问题在对话里被问得很细，值得明确记下来。

在不同实现策略下，时机会有差异，但本质一样：

- 如果 Host 一启动就主动连接某个 Server，那么 `initialize` 会在启动后的建连时发生。
- 如果 Host 采用懒连接策略，那么第一次真正需要用到某个 Server 时，才会建立连接并执行 `initialize`。
- 如果这个 Server 需要用户授权，则可能在用户确认后才建连并 `initialize`。

因此要记住：

> `initialize` 属于“建立这条 MCP 会话”时做的事，不属于“每次调某个 Tool”时都要做的事。

#### 为什么初始化后还要发 `initialized`

因为 `initialize` 返回成功，并不自动表示“正常业务阶段立刻开始”。

更准确地说：

1. Client 发送 `initialize`
2. Server 返回 `InitializeResult`
3. Client 再发送 `notifications/initialized`
4. 到这里才真正进入正常操作阶段

这个设计的意义在于，把“能力协商完成”和“开始业务交互”明确分开。

### Operation：Primitives 在哪里真正工作

Lifecycle 不是和业务相对立的东西，而是业务发生的前提。

在初始化完成之后，才进入正常操作阶段。也就是从这里开始，你前面学过的这些消息才真正上场：

- `tools/list`
- `tools/call`
- `resources/list`
- `resources/read`
- `resources/templates/list`
- `prompts/list`
- `prompts/get`
- completion 相关请求
- 各种通知和订阅机制

可以说，Operation 阶段是“Primitives 真正开始运作的地方”。

### Capability Negotiation：到底在协商什么

能力协商不是在讨论“任务怎么做”，而是在讨论：

> 本次会话中，双方各自支持哪些协议能力，因此后续哪些消息才是合法可用的。

它至少涉及两类信息：

- **Client 侧能力**：客户端能配合什么
- **Server 侧能力**：服务端能提供什么

例如：

- Server 是否支持 Tools
- 是否支持 Resources
- 是否支持 Prompts
- 某些资源是否支持订阅
- 某些列表是否支持变更通知
- Client 是否支持某些补全或采样相关能力

所以，capability negotiation 的作用不是“控制任务策略”，而是“先把会话边界说清楚”。

这一步非常基础设施化，但正因为如此，它才重要。

## Transport：MCP 消息到底怎么从一边到另一边

到这里，应该把视角再往下切一层。

前面的 Tools、Resources、Prompts、Lifecycle 都属于“消息语义”层；Transport 处理的是：

> 这些消息到底通过什么通道送过去。

MCP 当前最重要的两种 Transport 就是：

- **STDIO**
- **Streamable HTTP**

理解它们时，只要抓住一句话：

> Data layer 决定“说什么”，Transport layer 决定“怎么送”。

### STDIO：本地进程通信的传输方式

STDIO 非常适合本地 Server。它不是 MCP 自己发明的“神秘协议”，而是利用了操作系统里早就存在的标准输入/标准输出通道。

#### 它和 `stdio.h` 的关系

可以这样理解：

- 操作系统/进程模型里本来就有 `stdin` / `stdout` / `stderr`
- C 语言里的 `stdio.h` 只是访问这些通道的一套标准库封装
- MCP 里的 STDIO transport 说的是：两个进程拿这些现成通道来传 JSON-RPC 消息

因此你现在不必把 STDIO 深挖到底层操作系统。现阶段知道它是“本地进程之间传协议消息的一种现成通道”，就够用了。

#### STDIO 在 MCP 里怎么工作

在 STDIO 模式下，典型过程是：

1. Host 需要某个本地 Server
2. Client 将这个 Server 拉成子进程
3. Client 向 Server 的 `stdin` 写 JSON-RPC 消息
4. Server 从 `stdin` 读消息并处理
5. Server 再通过 `stdout` 回 JSON-RPC 响应/通知
6. 日志一般写到 `stderr`

所以，STDIO 最适合的系统感觉就是：

> 一个本地进程直接“接”着另一个本地进程说话。

#### 它适合什么场景

最适合 STDIO 的，通常是：

- filesystem server
- git server
- 本地开发辅助 server
- 桌面端本地能力
- 单机环境下的工具型能力

它简单、直观、无网络开销，天然适合本地单用户场景。

### Streamable HTTP：把 MCP 放到网络上

<img src="http://public.file.lvshuhuai.cn/images\format,webp.webp" alt="1.png" style="zoom:50%;" />

如果说 STDIO 是“本机进程直连”，那么 Streamable HTTP 就是“通过网络连接远程 Server”。

这里最重要的一点是：

> Streamable HTTP 不是视频流协议，也不是媒体播放方案。

虽然名字里有“HTTP”和“Streamable”，但在 MCP 语境下，它传的不是视频分段，而是 JSON-RPC 协议消息。

#### SSE 是什么，它在这里起什么作用

对话里问过 SSE，这里顺手系统化一下。

SSE（Server-Sent Events）本质上是：

> 服务器通过 HTTP 持续向客户端推送事件流的一种机制。

它是单向的，适合让服务器不断把通知或流式消息发回客户端。

放在 MCP 里，SSE 的典型用途是：

- 让 Streamable HTTP 的 Server 流式返回消息
- 让 Server 主动推送通知
- 支持长时间运行请求中的分段返回

#### Streamable HTTP 的完整消息流

这是我们对话里讲得最细的一段，值得保留下来。

一条典型的 Streamable HTTP 会话可以这样理解：

1. Client 对 MCP endpoint 发 `POST /mcp`
2. Body 里放 JSON-RPC 的 `initialize`
3. Server 返回 `InitializeResult`
4. Server 还可能在响应头里分配一个 session id，例如 `MCP-Session-Id`
5. Client 再 `POST` 一个 `notifications/initialized`
6. 后续普通请求都继续用 `POST` 发送 JSON-RPC 消息
7. 如果 Server 返回的是普通 JSON，就直接处理
8. 如果返回的是 `text/event-stream`，就说明这是一个 SSE 流
9. Client 也可以通过 `GET` 打开一个专门的 SSE 流，用来接收 Server 主动推送的消息

这里可以把最核心的三个点记下来：

- `POST`：用于发送 JSON-RPC 消息
- `GET + SSE`：用于接收流式或主动推送消息
- `MCP-Session-Id`：用于维持远程会话

#### Session Header 为什么重要

在 STDIO 模式下，会话往往隐含在进程连接里；进程活着，连接在，会话通常也在。

但在 HTTP 模式下，会话必须更显式。于是 Server 可以在初始化时分配 session id，后续请求都带着它继续通信。如果服务端告诉你 session 失效了，那么客户端就需要重新开始初始化。

因此，Streamable HTTP 不只是“把 JSON 放进 HTTP 请求”那么简单，它还承担了更明确的 session 管理职责。

## 一个完整案例：从用户请求到多个 MCP Server 协同

前面讲了很多概念，现在把它们放回一个完整系统里，看它们如何一起工作。

假设用户在 IDE 里输入：

> 帮我分析支付模块最近一次提交引入的空指针问题，看看文档怎么说，再给我一个 commit message。

Host 可能这样组织整个过程：

### 第一步：决定接入哪些 Server

Host 发现这个任务可能需要：

- Filesystem Server：读代码文件
- Git Server：看最近提交与 diff
- Company Docs Server：看设计文档

如果这些连接尚未建立，就分别创建对应的 Client 并与每个 Server 建连。

### 第二步：分别初始化各条会话

对每个 Server，Client 都要做一次：

1. `initialize`
2. 收到 `InitializeResult`
3. 发 `initialized`

注意，这不是“用户一提问就统一全局只做一次 initialize”，而是**每条 Client–Server 会话各做一次**。

### 第三步：获取需要的对象

对 Filesystem Server：

- `resources/list`
- 读取 `file:///project/src/payment/PaymentService.java`

对 Git Server：

- `tools/list`
- 调用查看最近 diff 的 Tool

对 Company Docs Server：

- `resources/read` 读取 `kb://design/payment-service`

### 第四步：必要时使用 Prompt

如果系统里有一个 Prompt 叫：

- `write_commit_message`

那么 Host 可以先 `prompts/get`，拿到这个 Prompt 模板展开后的消息结构，再把前面得到的上下文一起送给模型。

### 第五步：模型生成结果

到这时，模型拿到的就不是原始世界本身，而是通过 MCP 协议读取和调用后整理好的上下文与能力结果。

这就是 MCP 在系统中的真实价值：

它不是直接替模型思考，而是把模型进入外部世界的路径标准化了。

## Authorization / Security

### MCP 为什么必须把这一层单独讲清楚

到了 Authorization / Security，这里就不能再把 MCP 只看成“工具协议”了。因为一旦 MCP server 不只是提供公开只读内容，而是开始暴露用户数据、组织内部资料、写操作、管理操作，那么问题就不再是“模型能不能调用”，而是“谁可以调用、能调用到什么程度、这条调用链会不会被绕过”。官方规范目前把这部分明确放进 OAuth 2.1 语义里：受保护的 MCP server 作为 resource server，MCP client 作为 OAuth client，必要时再配一个 authorization server 来给 token、做用户同意与权限授予。

先把三个概念分开，不然后面很容易混。Authentication 解决的是“你是谁”；Authorization 解决的是“你被允许做什么”；Security 则更大，它还关心 token 会不会被盗、会话会不会被劫持、客户端会不会被拿去做 SSRF、一个本地 MCP server 会不会其实是在执行恶意命令。这也是为什么 MCP 不只写“怎么拿 token”，还单独写了 security best practices。

### Authorization 在 MCP 里不是必选，但对远程受保护服务几乎是默认必需

规范的口径是：Authorization 对 MCP 实现整体来说是可选的；但如果你走的是 HTTP transport，而且 server 暴露的是受保护资源，那么应当按这套授权规范来做。相反，STDIO 场景通常不建议硬套这套 HTTP/OAuth 授权流程，而是更适合从环境变量、本地凭证库、嵌入式 SDK 等方式获取凭证。官方教程也明确把“本地 STDIO server”和“远程 HTTP server”的授权路径区分开了。

这背后的原因其实很好理解。STDIO server 本质上跑在用户机器上，Host 往往就是把一个本地进程拉起来对话；而远程 HTTP server 则天然跨了网络边界、租户边界、组织边界。前者的核心风险更偏向本地代码执行和权限滥用，后者的核心风险更偏向 OAuth 流程正确性、token 使用边界、会话与网络攻击面。

### 在 MCP 的授权模型里，谁扮演什么角色

如果一个 MCP server 受保护，那么它在授权语义上不是“自己随便验个 token 的服务”，而是一个 OAuth resource server。MCP client 是 OAuth client，代表用户去请求访问这个 resource server；authorization server 负责和用户交互、出具 access token。authorization server 可以和 MCP server 部署在一起，也可以是独立组件，但发现它的位置必须遵循 MCP 规范定义的发现流程。

这个角色划分很重要，因为它直接决定了一个关键原则：

> MCP server 必须只接受“发给自己”的 token，而不是“别人拿来给它转一下”的 token。

这句话看似普通，实际上是 MCP 安全模型最核心的边界之一。后面你会看到，很多高危问题——尤其是 token passthrough——本质上都是因为有人把这个边界做没了。

### 一个受保护的 HTTP MCP server，授权流程大致怎么走

<img src="http://public.file.lvshuhuai.cn/images\imageurl=https%3A%2F%2Fimages.ctfassets.net%2Fxqb1f63q68s1%2F5Ud69swfPVJmDLCHukhzOY%2F47508569d79120dc260b9a4295327578%2FAuthorization_Code_Flow__2_.png" alt="Sequence diagram illustrating the OAuth Authorization Code Flow between four participants: User, Client, AuthZ Server (Descope), and Resource Server. The User clicks a login link, prompting the Client to send an Authorization Code request to the AuthZ Server. The AuthZ Server prompts the User for authentication and consent, and the User provides authentication and consent. The AuthZ Server then provides an Authorization Code to the Client. The Client exchanges the Authorization Code for app credentials with the AuthZ Server, which validates and shares access and ID tokens. Finally, the Client requests user data from the Resource Server and receives the response." style="zoom:40%;" />

这一段最好不要背 RFC 名字，而是先记住 MCP 的实际消息逻辑。

第一步不是立刻跳 OAuth 页面，而是先做“这个 server 受不受保护、它的授权服务器在哪”的发现。当前规范要求 MCP server 实现 Protected Resource Metadata；客户端要么从 `401 Unauthorized` 的 `WWW-Authenticate` 头里拿到 `resource_metadata` 地址，要么按 well-known URI 去找。这个元数据里必须能告诉客户端关联的 `authorization_servers`。

第二步，客户端再去发现 authorization server 的元数据。规范要求客户端既要支持 OAuth Authorization Server Metadata，也要支持 OpenID Connect Discovery，并且在 issuer 带路径和不带路径时都要按规定顺序尝试 well-known 端点。换句话说，MCP 这里不是“写死一个 auth URL”，而是把授权服务器发现也协议化了。

第三步是 client registration。当前规范里有三种路：预注册、Client ID Metadata Documents、Dynamic Client Registration。官方给出的推荐优先级是：有预注册就用预注册；没有预注册，优先用 Client ID Metadata Documents；DCR 更像兼容旧方案或特殊场景的兜底。尤其在“client 和 server 事先没有关系”的 MCP 常见场景里，Client ID Metadata Documents 是官方特别强调的常见做法。

第四步才是真正的授权请求与换 token。这里有个特别值得记住的 MCP 细节：客户端在 authorization request 和 token request 里都必须带 `resource` 参数，而且这个参数必须明确指向目标 MCP server 的 canonical URI。也就是说，客户端不能只说“给我一个 token”，而必须说清楚“我要访问的是哪一个 MCP server”。这一步是后续 audience 校验和最小权限边界的基础。

第五步，客户端拿着 access token 调 MCP server，请求里按标准放 `Authorization: Bearer <access-token>`。服务端收到后不能只看“有没有 token”，而必须校验 token 是否有效、是否发给自己、scope 是否满足当前请求。若权限不够，规范要求服务端通过标准错误和 `WWW-Authenticate` 挑战把需要的 scope 再告诉客户端，客户端可以再走一次 step-up authorization 申请更高权限。

### 把这套流程放回你前面的 Host / Client / Server 视角里

如果你延续前面那套心智模型，那么这里可以这样理解：

- Host 仍然是总控层。
- 某个远程 MCP server 是 protected resource。
- Host 里的 MCP client 发现这个 server 需要授权后，不是直接硬调，而是先走 discovery、registration、authorization。
- 等拿到“面向该 MCP server”的 token 后，才真正进入 `initialize`、`tools/list`、`resources/read`、`tools/call` 这些正常操作。

所以，Authorization 不是替代 Lifecycle，而是给 Lifecycle 增加一个“进入业务前先完成访问控制”的前置层。它控制的是“这条会话是否有资格开始、开始后能看什么、能做什么”。

### 为什么 MCP 一直强调 resource parameter 和 audience validation

这一点必须单独拎出来，因为它几乎是 MCP 授权最容易被轻视、但后果最重的地方。

很多人做系统时会偷懒，觉得“只要 token 是合法的就行”。但对 MCP 来说，这远远不够。规范明确要求：客户端必须在授权和换 token 时携带 `resource` 参数；服务端必须验证传来的 token 就是发给自己的，而不是发给别的服务的。

为什么要这么严？因为如果没有这个约束，你的 MCP server 很容易沦为一个“代转 token 的中间人”，或者让一个本来只该给下游 API 用的 token 被拿来调 MCP server，最终把审计、权限控制和服务边界全部打穿。MCP 官方在规范和安全文档里都把这一点说得非常重，而且明确禁止 token passthrough。

### Token passthrough：这是 MCP 里最典型的反模式之一

所谓 token passthrough，简单说就是：MCP client 带来一个 token，MCP server 不认真校验它是不是发给自己的，就把它继续透传给下游 API，自己充当一个代理。官方文档直接把这件事定义成 anti-pattern，并明确写成 forbidden。

它危险，不只是因为“可能不规范”，而是会带来一串非常实在的问题。第一，安全控制会被绕过，因为很多速率限制、行为检测、权限校验，本来就是按 token audience 或 token 适用对象来做的；第二，审计会变脏，日志里看起来像是别的主体在访问，而不是 MCP server 自己这条链路；第三，trust boundary 会混乱，一个本来只信任某个资源服务器的 token，可能被拿去横着打到别处；第四，即便你今天只是“透明代理”，以后想加安全控制也会非常难。

所以更正确的做法是：MCP server 只接受发给自己的 token；如果它还要去访问上游 API，那么它应当作为 OAuth client 再去拿一张“给上游 API 用的独立 token”，而不是复用用户传给 MCP server 的那张。

### Confused Deputy：代理型 MCP server 为什么更容易出事

MCP 文档专门点名了 confused deputy problem，主要发生在“代理型 MCP server”身上：它一边面向 MCP client 提供统一入口，一边又代表这些 client 去访问第三方 API。如果这里把 OAuth client 身份、用户同意、redirect 处理混在一起，就可能出现“攻击者借你这个代理，骗到本不该拿到的授权结果”的情况。

官方给出的方向很明确：代理型 MCP server 必须做 per-client consent，而不是把所有 client 混成一个大客户端身份；同时要严格处理 OAuth `state`，包括为每次授权请求生成安全随机值、只在用户同意之后才把相关 `state` 追踪信息落到 cookie 或 session、中途任何不匹配都直接拒绝、并让 `state` 一次性且短期有效。这里的重点不是“state 这个参数存在就行”，而是它必须和 consent flow 真正绑定，否则用户看到的授权确认页就可能形同虚设。

### SSRF：为什么连“发现授权服务器”这一步都可能被攻击

![Server Side Request Forgery Prevention - OWASP Cheat Sheet Series](http://public.file.lvshuhuai.cn/images\hlyZL-guupNWwKZM83Cj6n53nOUsULHMjsiW3FVo9L-yf7P6YC4u8qNKCsXpx5N91Pb9SzWLTQigCRuhJ10EsgFzobkyPoM993OlHuj_tHiqtd_2jk86enBpTrH0oZ8tBvPl9w8ykOfIbyaWi91-iw7glo7dMj7Cw4YonttCqKsv5vLfUyByhZB1PGqOJ1jb.jpeg)

这也是 MCP 特别现实的一点。因为在授权发现流程中，客户端会去读取一串由 server 提供或间接提供的 URL：比如 `WWW-Authenticate` 里的 `resource_metadata`、Protected Resource Metadata 里的 `authorization_servers`、Authorization Server Metadata 里的各种 endpoint。如果 MCP client 对这些 URL 太信任，一个恶意 server 就能诱导客户端去请求内网地址、云 metadata 地址、localhost 服务，甚至通过 DNS rebinding 和重定向链把请求引到危险位置。

所以官方建议非常直接：生产环境下 OAuth 相关 URL 应当强制 HTTPS；除开发阶段的 loopback 场景外，不应接受明文 HTTP；客户端应考虑拦截私有和保留地址段，并警惕 localhost、`169.254.169.254`、DNS rebinding、redirect chain 这些典型 SSRF 入口。这里要注意，MCP 的攻击面不只在 tool 调用本身，也在协议发现和授权握手这些“看起来只是元数据”的阶段。

### Session 安全：Session 可以帮助维持状态，但不能拿来代替认证

前面讲 Transport 时提过，HTTP MCP 往往会有 session id，用来维持状态流、SSE、重连、恢复等机制。但官方安全文档明确说了一件事：MCP server 不能把 session 当认证凭证来用。也就是说，session 可以是“把这条连接续起来”的技术对象，但不能因为某人带着一个 session id 来了，就默认他仍然是那个被授权的用户。

文档给出的要求很明确：实现了 authorization 的 MCP server 必须验证所有入站请求；session id 必须是安全随机、不可预测的；最好轮换或过期；而且在队列或共享状态里存 session 时，应该把它和用户标识绑定起来，例如 `<user_id>:<session_id>` 这种形式。这样就算有人撞到了 session id，也不能直接冒充别的用户。

这其实也解释了一个很重要的设计边界：

> Authentication / authorization 决定“你是谁、你能干什么”；session 只是在这个前提下帮你把会话维持住。

如果把二者混成一层，HTTP MCP 很容易在多节点、共享队列、SSE 恢复这些地方出事。

### Local MCP Server：本地并不天然更安全，反而可能更危险

很多人一看到 STDIO 或 local MCP server，就会下意识觉得“这是本地的，所以安全”。实际上，MCP 官方专门提醒：本地 server 的风险恰恰不小，因为它运行在用户机器上，通常直接拥有和客户端差不多的系统权限。恶意配置可能把它变成“帮攻击者执行命令”的入口。

文档里给出的攻击图景非常直白：有人在一键安装配置里塞进恶意 startup command；或者 server 二进制本身就是带 payload 的；或者一个留在 localhost 上的本地服务被 DNS rebinding 间接打到。风险包括任意代码执行、用户看不见真正执行了什么、命令被混淆伪装、数据外流、主机数据损坏。

所以，如果一个 MCP client 支持“一键接入本地 MCP server”，它至少应做到几件事：在执行前展示完整且未截断的命令；明确告诉用户这会在本机执行代码；要求显式同意；允许取消；对含 `sudo`、`rm -rf`、敏感目录访问、异常网络访问的命令做高亮警告；并尽可能在沙箱或最小权限环境里运行 server。官方甚至明确建议对文件系统、网络、系统资源做限制，而不是默认全部放开。

### Scope、日志、密钥管理：这些不是 OAuth 细节，而是 MCP 落地时最容易翻车的地方

官方教程在 “Common Pitfalls” 里给了一组很实用的提醒。第一，不要自己手写 token 校验与授权逻辑，尽量用成熟库；第二，access token 要短寿命；第三，永远校验 token，不要因为“客户端传了一个过来”就默认可用；第四，token 如果要缓存，必须安全存储并有淘汰策略；第五，生产环境强制 HTTPS；第六，坚持 least privilege scope，不要给一把大而全的权限；第七，不要在日志里记录 `Authorization` header、token、code、secret；第八，不要把应用级 secret 和资源服务器侧 secret 混用。

这些建议看上去朴素，但在 MCP 里尤其关键。因为 MCP 的交互不是单一 API，而是一整组可发现、可调用、可订阅的外部能力。一旦 scope 设计过宽、日志打得太多、token 生命周期过长，问题不是“一个接口可能泄露”，而是“整个外部能力面都可能被一起放大”。