# [扣子 Coze](https://www.coze.cn/)

### Coze 是什么

一句话定义：

**Coze 是一个 AI application / agent development platform。**

![Coze Studio](http://public.file.lvshuhuai.cn/images\coze-studio-overview.png)

它把[[智能体 Agent]] 产品开发里常见的组件——模型、工作流、插件、知识库、变量、数据库、UI 卡片、发布分发——做成了一个更高层、更产品化的一站式平台。Coze 官方将其定位为面向不同技能水平用户的 AI 应用开发平台，并提供 agent 创建、编排、知识管理和多平台部署等能力。

## 把 Coze 放到整个技术栈里看

如果用已经熟悉的术语对齐，LangGraph 更接近：

- orchestration runtime 编排运行时
- stateful workflow engine 有状态工作流引擎
- durable execution infrastructure 持久化执行基础设施

它强调的是 long-running、stateful、durable execution、human-in-the-loop，而且明确偏向底层编排能力。

而 Coze 更接近：

- integrated agent product platform 集成智能体产品平台
- application assembly platform 应用程序组装平台
- higher-level agent development environment 高级智能体开发环境

它的重点不是让你从零实现 agent runtime，而是把很多原本要自己搭的外围系统内建好，让你更快拼出一个可上线、可分发的 agent application。

因此可以这样分层理解：

- **LLM / MLLM**：模型层
- **vLLM / serving stack**：推理服务层
- **LangGraph**：低层 agent / workflow orchestration 层
- **Coze**：高层 agent application platform / product assembly 层

## Coze 的核心抽象

Coze 的真正价值，不在于“能不能搭聊天机器人”，而在于它把 agent 产品化过程中常见的对象都提升成了平台原语。

### Bot / App / Agent

Coze 的核心对象，本质上就是一个面向最终用户交互的 AI 应用容器。

在这个容器里，你会挂载：

- 模型
- 提示词
- 工作流
- 知识库
- 插件
- 变量
- UI 组件
- 数据能力

所以在 Coze 里，你不是单纯写一个 prompt，而是在拼一个完整的 AI 应用。

### Workflow

[[工作流 Workflow]] 是 Coze 中非常核心的概念。官方将其描述为一组可执行指令，用来实现业务逻辑并完成特定任务。

![Coze Workflow](http://public.file.lvshuhuai.cn/images\coze-default-workflow-icon.png)

这个抽象和 [[LangGraph]] 的 workflow 很接近，本质上都属于 **deterministic orchestration**，即：

- 路径是预定义的
- 流程由节点和连线组成
- 重点是控制执行逻辑，而不是让模型无限自由发挥

差别在于：

- 在 LangGraph 中，你更多面对的是 graph、state、edge、conditional edge 这样的底层编程原语
- 在 Coze 中，你更多面对的是产品化节点编排环境，很多逻辑通过配置和节点组合来表达

### Plugin

Plugin 在 Coze 中对应的就是 agent 体系里的 **tools**。

![Coze Plugin](http://public.file.lvshuhuai.cn/images\coze-plugin-icon.png)

它的作用是把外部 API 或外部系统能力，以平台可管理的方式接入进来。对已经学过[[工具调用 Tool Calling]] 的人来说，Plugin 并不是什么新理论，它更像是工具抽象在平台中的产品化实现。

从 agent architecture 的角度看，Plugin 可以理解为：

- tool abstraction layer
- external capability layer
- managed API integration surface

### Knowledge Base

Knowledge Base 是 Coze 内建的知识管理与[[检索增强生成 RAG]] 能力。

![Coze Knowledge Base](http://public.file.lvshuhuai.cn/images\coze-knowledge-icon.png)

它的意义不在于“能上传文件”，而在于它实际上提供了一个平台内建的 **managed RAG substrate**。也就是说，在 LangGraph 里你可能要自己接向量库、自己设计 retriever、自己写 routing；而在 Coze 里，这些能力已经被包装成平台组件。

所以 Knowledge Base 的本质是：

- external knowledge ingestion
- retrieval infrastructure
- managed RAG component

### Variable

Variable 用来在运行时保存动态变化的信息。

![Coze Variable](http://public.file.lvshuhuai.cn/images\coze-variable-icon.jpg)

这和你已经学过的 state management 是同一类问题，只不过在 Coze 里，它被做成了平台显式支持的数据槽位。你可以把它理解为把原来在代码里维护的部分 state，变成了平台中的一等公民。

它本质对应的是：

- runtime state slots
- context variables
- execution-time data binding

### Database

Coze 提供 Database 功能来管理结构化数据，并支持增删改查。

![Coze Database](http://public.file.lvshuhuai.cn/images\coze-database-icon.png)

这一点说明 Coze 不只是想做一个“聊天平台”，而是在向 application backend substrate 延伸。它希望 agent 不仅能调用模型和知识，还能直接操作一定范围内的业务数据。

所以 Database 在 Coze 中更接近：

- lightweight application data layer
- structured storage capability
- platform-managed business data component

### Code Node

Code Node 允许你在 workflow 中插入编程式逻辑。

![Coze Code Node](http://public.file.lvshuhuai.cn/images\coze-code-node-icon.jpg)

这个能力很关键，因为现实业务里，仅靠 prompt、知识库和插件往往不够，你还需要：

- 数据清洗
- 规则判断
- 格式转换
- 路由控制
- 中间结果构造

Code Node 可以理解为：

- programmable logic escape hatch
- custom business logic node
- workflow 中的代码执行点

它说明 Coze 并不是一个只能“拖拉拽”的玩具，而是保留了必要的编程扩展口。

### Conversation History

Coze 提供和会话历史相关的节点能力，用于读取、查询和操作某个 conversation 中存储的上下文消息。

![Coze Conversation History](http://public.file.lvshuhuai.cn/images\coze-conversation-history-icon.jpg)

这说明在 Coze 里，多轮上下文并不只是拼进模型输入的字符串，而是平台可查询、可管理的会话资源。

这个能力本质对应的是：

- managed conversational persistence
- dialogue history access
- thread-level context store

### Card / UI Surface

Coze 有 card builder 一类能力，说明它不只关心 agent 的后端逻辑，还关心 agent 输出如何以交互化形式呈现给用户。

这和纯框架思维很不一样。像 LangGraph 不负责你的最终 UI 形态，而 Coze 会把一部分前端交互层也纳入平台语义。

所以从产品角度看，Card 更接近：

- agent-facing interaction surface
- result presentation layer
- structured response UI container

## Coze 的整体抽象

把前面的概念收拢起来，Coze 可以被概括为：

**Coze = Model + Prompt + Workflow + Plugins + Knowledge + Variables + Data + UI + Distribution**

而 LangGraph 的抽象更像：

**LangGraph = State + Nodes + Edges + Tool Calls + Persistence + Control Flow**

这两种抽象的差别非常关键。

前者是**应用平台抽象**。

后者是**运行时编排抽象**。

这也是为什么 Coze 和 LangGraph 不应该被看成互相替代的关系。

[Coze Studio](https://github.com/coze-dev/coze-studio) 的开源版本也能帮助理解这个分层：仓库说明中把 prompt、RAG、plugin、workflow 视为 AI agent development 的核心技术，并把 workflows、plugins、databases、knowledge bases、variables 等统一称为 resources。

## Coze 在做哪三层事情

如果进一步从系统功能上拆，Coze 实际上在同时做三层事情。

### 第一层：Agent Assembly

它允许你把模型、提示、知识、工具、变量和节点逻辑组装成一个 agent。

这是最直接的一层，也是很多人最先看到的一层。

### 第二层：Applicationization

它不满足于“能跑一个 agent”，而是要让这个 agent 成为一个真正的应用。于是它加入了：

- 数据层
- UI 卡片
- 变量系统
- 会话历史
- 平台配置能力

这意味着它试图把 agent 从“实验性逻辑”推向“可交付产品”。

### 第三层：Distribution / Platformization

Coze 还承担了模板、分发、复用、发布等职责。这部分能力说明它不仅是开发环境，也是平台生态的一部分。

也就是说，Coze 不只是帮你“做出来”，还试图帮你“发出去、复用起来、被别人发现”。

## Coze 和 LangGraph 的核心区别

如果只抓最重要的区别，可以记下面三点。

### 第一，Coze 不是 LangGraph 的替代品

它们不在同一抽象层。

- LangGraph 解决的是：如何以低层可控的方式构建 stateful workflow / agent runtime
- Coze 解决的是：如何更快把 agent 能力拼成可用产品

### 第二，Coze 更适合看“agent 产品长什么样”

如果你想理解 agent runtime 原理、状态如何流动、失败如何恢复、边如何控制、线程如何持久化，那么 LangGraph 更直接。

如果你想理解一个现实中的 AI 应用通常会有哪些部件，以及这些部件在平台里是如何被组织成一个产品的，那么 Coze 更直观。

### 第三，Coze 的价值在于把“非模型问题”平台化

很多人一提 agent，就只盯着模型和 prompt。但一个真实产品是否成立，往往更取决于这些问题：

- 外部知识怎么接
- 工具怎么管
- 变量怎么传
- 数据怎么存
- UI 怎么展示
- 多平台怎么发

Coze 的平台价值，恰恰在于把这些问题纳入统一环境。

## 如何把 Coze 映射到你脑中的知识体系里

为了避免把 Coze 学成“平台操作说明书”，最好把它的对象映射到更通用的 agent engineering 概念里。

- **Workflow**：deterministic orchestration
- **Plugin**：tool abstraction / API capability layer
- **Knowledge Base**：managed RAG substrate
- **Variable**：runtime state slots
- **Database**：lightweight application data layer
- **Code Node**：programmable business logic escape hatch
- **Conversation History**：managed conversational persistence
- **Card**：agent-facing interaction surface

这样学，你就不会把 Coze 误认为某种全新理论，而能清楚地看到它只是把已有 agent 体系里的多个部分做成了平台对象。
