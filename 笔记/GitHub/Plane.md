# Plane

> 仓库：`https://github.com/makeplane/plane`
>
> 项目分支：GitHub 当前默认展示为 `preview` 分支
>
> 核对时间：2026-05-06
>
> 文档目标：把 Plane 作为一个完整的开源项目管理平台来讲解，而不是只介绍技术栈，也不是逐文件夹机械罗列。

## 项目定位与业务对象模型

![Plane 项目管理界面概览](http://public.file.lvshuhuai.cn/images\plane-open-source-kanban-hero.webp)

[Plane](https://github.com/makeplane/plane) 不是一个简单的任务管理 [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) 项目，也不只是“[React](https://react.dev/) + [Django](https://www.djangoproject.com/)”的组合。它更准确的定位是：一个开源项目管理平台，用于管理团队中的工作项、迭代周期、模块、视图、页面、知识库、统计分析和外部集成。官方 [README](https://github.com/makeplane/plane#readme) 中把它描述为开源的 [Jira](https://www.atlassian.com/software/jira)、[Linear](https://linear.app/)、[Monday](https://monday.com/)、[ClickUp](https://clickup.com/) 替代品，用来跟踪 issues、运行 cycles、管理产品 roadmaps。这个定位决定了讲解 Plane 时，第一层应该从产品对象模型开始，而不是从代码目录开始。

如果只从“技术栈”切入，很容易把 Plane 误解成一个普通的前后端分离项目。但实际上 Plane 的复杂度来自两个方面：

1. 它的业务对象之间存在复杂关系，例如 workspace、project、work item、cycle、module、view、page、analytics、integration；
2. 它的运行结构不是一个 Web 服务，而是多个前端应用、后端 [API](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Client-side_APIs/Introduction)、异步 worker、实时协作服务、反向代理和基础设施组件共同组成。

因此，讲 Plane 的主线应该是：

```text
团队协作中的项目管理问题
  ↓
Workspace / Project / Work Item 等业务对象
  ↓
Web / Admin / Space / API / Worker / Live 等服务边界
  ↓
PostgreSQL / Redis / RabbitMQ / MinIO 等基础设施
  ↓
前端 monorepo、Django 后端、异步任务、实时协作和部署运维
```

### 从项目管理闭环理解 Plane

Plane 的核心业务不是“创建一个任务”，而是围绕团队项目管理形成闭环。一个典型使用场景可以抽象成：

```text
创建 Workspace
  ↓
邀请成员并分配权限
  ↓
创建 Project
  ↓
创建 Work Item
  ↓
把 Work Item 放入 Cycle 或 Module
  ↓
用 View 保存不同筛选视角
  ↓
用 Page / Wiki 记录背景知识
  ↓
用 Analytics 查看项目状态
  ↓
通过 Integration 连接 GitHub、GitLab、Slack、Sentry 等外部系统
```

这条链路比单纯的 issue tracker 更完整。Work Item 是任务粒度，Cycle 是时间粒度，Module 是结构粒度，View 是查询和展示粒度，Page / Wiki 是知识沉淀粒度，Analytics 是管理和反馈粒度，Integration 则把 Plane 接入外部研发系统。

从这个角度看，Plane 的目标不是替代一个待办事项列表，而是把项目执行、团队协作、产品规划和研发过程中的多个工作面合并到同一个平台中。

### 核心业务对象

#### Workspace

Workspace 是组织级空间。它承载用户、成员关系、权限、项目、配置和实例中的协作边界。多个团队或组织可以拥有不同 workspace，不同 workspace 之间的数据和权限需要隔离。

在讲解时可以把 Workspace 理解成“团队或组织容器”。它不是具体项目，而是项目之上的空间。用户进入 Plane 后，通常先进入某个 workspace，然后在 workspace 下访问 project、work item、page 等内容。

Workspace 需要处理的问题包括：

- 成员加入、移除和邀请；
- 角色和权限；
- workspace 级配置；
- 与实例管理、认证方式、外部集成的关系；
- 多租户数据隔离。

对于一个项目管理平台来说，多 workspace 不是 UI 上多一个下拉框，而是后端权限、数据库查询、API 访问控制和前端状态管理都要围绕它展开。

#### Project

Project 是具体项目空间。一个 workspace 下可以有多个 project，每个 project 下有自己的 work items、cycles、modules、views、pages 和配置。

Project 更接近日常意义上的“产品项目”或“研发项目”。例如：

```text
Workspace: 某公司研发部
  ├── Project: 官网改版
  ├── Project: 移动端 App
  ├── Project: 后台管理系统
  └── Project: 数据平台
```

Project 要解决的是局部协作问题：某个项目有哪些工作项，哪些人负责，当前进展如何，哪些任务进入当前 cycle，哪些需求属于某个 module，哪些视图适合研发、产品、测试分别查看。

#### Work Item

![Plane Work Items 列表](http://public.file.lvshuhuai.cn/images\plane-work-items.webp)

Work Item 是 Plane 中最核心的工作单元。它可以对应任务、需求、缺陷、issue、待办事项，也可以承担更广义的“工作条目”含义。README 中明确把 Work Items 作为主要功能之一，强调它支持创建和管理任务、富文本编辑器、文件上传、子属性和相关 issue 引用。

一个 Work Item 通常会包含：

- 标题；
- 描述；
- 状态；
- 优先级；
- 负责人；
- 标签；
- 截止时间；
- 所属 project；
- 所属 cycle 或 module；
- 附件；
- 评论；
- 关联的其他 work item；
- 活动记录。

从系统设计角度看，Work Item 是 Plane 最重要的数据模型之一，因为它连接了绝大多数业务模块：

```text
Work Item
  ├── 属于某个 Project
  ├── 可以进入某个 Cycle
  ├── 可以归入某个 Module
  ├── 可以被 View 筛选出来
  ├── 可以被 Page 引用或转化
  ├── 可以进入 Analytics 统计
  ├── 可以由 Integration 创建或同步
  └── 可以触发 Notification / Activity / Webhook
```

因此，如果讲源码，应该优先围绕 Work Item 的创建、编辑、筛选、权限和异步通知来讲，而不是先讲登录页或 UI 主题。

#### Cycle

![Plane Cycles 进度与燃尽图](http://public.file.lvshuhuai.cn/images\plane-cycles.webp)

Cycle 更接近敏捷迭代或 sprint。Plane 官方 README 中用 Cycles 表示团队可以维持工作节奏，并通过 burn-down charts 等方式跟踪进度。Cycle 的关键不是“分类”，而是“时间窗口”。它回答的问题是：在某一段时间内，团队打算完成哪些 work items。

一个 Cycle 可以理解为：

```text
Cycle: 2026-05 第一迭代
  ├── 起始日期: 2026-05-01
  ├── 结束日期: 2026-05-15
  ├── Work Item A
  ├── Work Item B
  └── Work Item C
```

Cycle 让管理者和团队成员能够围绕时间节奏组织工作。它通常会和统计分析、进度图、燃尽图、状态分布等功能相关联。

#### Module

Module 用来把复杂项目拆成更小的功能块或工作块。它不一定有明确时间边界，更像是结构边界。例如一个“移动端 App”项目可以拆成：

```text
Module: 登录注册
Module: 订单系统
Module: 消息通知
Module: 设置中心
```

Cycle 和 Module 的区别可以这样理解：

```text
Cycle 关注“这段时间做什么”
Module 关注“这个功能块包含什么”
```

同一个 Work Item 可以同时具有时间维度和结构维度。比如“实现短信验证码登录”既可以属于“5 月第一迭代”，也可以属于“登录注册模块”。

#### View

![Plane 多视图布局](http://public.file.lvshuhuai.cn/images\plane-layouts-views.webp)

View 是查询和展示能力。Plane README 中提到 Views 可以创建过滤器，只显示最相关的 issues，并保存和共享这些视图。View 的意义在于：项目中的 work items 很多，不同角色关心的切面不同。

例如：

```text
研发视图：只看分配给我的、状态未完成的 work items
测试视图：只看状态为 Ready for QA 的 work items
产品视图：只看高优先级需求
管理视图：按负责人、状态、cycle 分组查看
```

View 本质上是：

```text
筛选条件 + 排序规则 + 分组方式 + 展示偏好 + 共享范围
```

这类能力在项目管理系统里很重要。它让同一批底层 work items 能够被不同角色以不同方式使用，而不需要复制数据。

#### Pages、Wiki 与知识沉淀

![Plane Pages 与 Wiki 编辑器](http://public.file.lvshuhuai.cn/images\plane-pages-wiki.webp)

Plane 不只是 issue tracker，它还支持 Pages 和 Wiki。官方文档首页也把 Pages and Wiki 单独列为主要入口，用于创建页面、构建 wiki、组织团队知识。

这说明 Plane 的产品边界已经从“任务执行”扩展到“知识管理”。很多团队管理项目时，任务本身只记录“做什么”，但需求背景、方案设计、会议纪要、技术决策、产品文档往往需要页面来承载。

Plane 中 Page / Wiki 的意义可以概括为：

```text
Work Item 负责执行粒度
Page / Wiki 负责知识粒度
```

两者之间可以互相引用。比如一篇需求说明可以拆成多个 work items，一个 work item 也可以引用某篇 page 作为背景资料。

#### Analytics 与 Integration

![Plane Intake 与外部输入](http://public.file.lvshuhuai.cn/images\plane-intake.webp)

Analytics 用于查看项目状态、趋势和瓶颈。它读取 work items、cycles、modules、成员和状态数据，形成统计视图。它不是独立业务实体，而是基于已有业务数据形成反馈层。

Integration 则是外部系统入口。官方文档列出了 [GitHub](https://github.com/)、[GitLab](https://about.gitlab.com/)、[Sentry](https://sentry.io/)、[Slack](https://slack.com/intl/zh-cn/) 等集成。集成能力让 Plane 不只停留在站内使用，而是可以接入研发工具链。例如：

- GitHub issue 或 PR 与 work item 关联；
- Slack 中接收通知；
- Sentry 错误转化为 work item；
- GitLab 数据同步到 Plane；
- 邮件进入 Intake 服务后转化为 work item 或评论。

这类能力会带来额外复杂度：[OAuth](https://oauth.net/2/)、[Webhook](https://en.wikipedia.org/wiki/Webhook)、外部 API、幂等处理、异步任务、失败重试、权限映射等都会进入系统设计。

## 多服务架构与仓库结构

![Plane 自托管架构图](http://public.file.lvshuhuai.cn/images\plane-architecture.webp)

Plane 官方[架构文档](https://developers.plane.so/self-hosting/plane-architecture)明确说明：Plane 由多个服务共同提供项目管理能力。它不是单体应用，也不是只有一个前端和一个后端。它的结构更接近一个可自托管的 [SaaS](https://en.wikipedia.org/wiki/Software_as_a_service) 平台。

### 服务分层

Plane 的服务可以按功能分成四组：

```text
前端服务：
  Web
  Admin
  Space

后端服务：
  API
  Worker
  Beat Worker
  Migrator

支撑服务：
  Proxy
  Live
  Monitor
  Silo
  Intake

基础设施：
  PostgreSQL
  Redis / Valkey
  RabbitMQ
  MinIO / S3
  OpenSearch
```

官方架构文档中，Web 是主应用界面，用户在这里和项目、工作项、页面交互；Space 用于公开分享项目、视图、页面；Admin 是实例管理界面，用于 workspace owners 和 administrators 管理设置、权限和许可相关内容。

API 是核心 REST API，所有前端服务都通过它进行数据操作。Worker 处理文件处理、通知分发、数据导入等异步任务。Beat Worker 运行周期性任务，例如数据清理、报告生成、提醒通知。Migrator 则在部署或升级时执行数据库迁移，运行完成后退出。

支撑服务中，Proxy 负责入口流量和反向代理；Live 提供 [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) 实时协作能力；Silo 负责 GitHub、GitLab、Slack 等集成的 OAuth、Webhook 和外部 API 通信；Intake 把进入系统的邮件转化为 work items 或 comments。

基础设施中，[PostgreSQL](https://www.postgresql.org/) 是主关系数据库，[Redis](https://redis.io/)/[Valkey](https://valkey.io/) 用于缓存、session 和实时协作状态，[RabbitMQ](https://www.rabbitmq.com/) 用于异步任务队列，[MinIO](https://min.io/)/[S3](https://aws.amazon.com/s3/) 用于附件、上传文件和导出文件，[OpenSearch](https://opensearch.org/) 是可选搜索索引服务。

这套结构可以画成：

```text
Browser
  ↓
Proxy / Caddy
  ↓
┌───────────────┬───────────────┬───────────────┐
│ Web           │ Admin         │ Space         │
│ 主应用界面     │ 实例管理界面     │ 公开分享页面     │
└───────┬───────┴───────┬───────┴───────┬───────┘
        ↓               ↓               ↓
                   API Server
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   PostgreSQL     Redis / Valkey    RabbitMQ
        ↓                              ↓
   业务数据存储                    Worker / Beat Worker
        ↓
     MinIO / S3

另一路：
API / Web → Live → WebSocket 实时协作

再一路：
Silo / Intake → Integration / Email → Work Item / Comment
```

### 同步链路与异步链路

Plane 的系统设计必须区分同步请求和异步任务。

当用户打开页面、查看项目、创建 work item、修改状态时，主要是同步链路：

```text
Web / Admin / Space
  ↓
API
  ↓
权限校验、序列化、业务逻辑
  ↓
PostgreSQL / Redis
  ↓
返回响应给前端
```

当系统需要处理通知、导入、导出、文件处理、外部集成事件时，就不能全部放在同步请求中完成。否则用户一次点击可能会等待很久，API 也容易因为外部服务不稳定而阻塞。因此 Plane 使用异步 worker：

```text
API
  ↓
投递任务到 RabbitMQ
  ↓
Worker 消费任务
  ↓
执行通知、文件、导入、导出、外部同步
  ↓
写回数据库或对象存储
```

周期性任务则由 Beat Worker 负责：

```text
Beat Worker
  ↓
按计划触发任务
  ↓
数据清理 / 报告生成 / 提醒通知
  ↓
必要时投递给普通 Worker 或直接执行
```

这也是 Plane 与 ddns-go 这类工具项目的根本区别。ddns-go 的主链路是定时检测和更新 DNS；Plane 的主链路是一个平台内多个服务和多个数据流协同运行。

### Monorepo 的目录结构

Plane 是 [monorepo](https://monorepo.tools/)。[仓库](https://github.com/makeplane/plane)根目录包含 `apps`、`packages`、`deployments`、`docs` 等目录。GitHub 当前展示的 `apps` 目录下有：

```text
apps/
├── admin
├── api
├── live
├── proxy
├── space
└── web
```

这和架构文档里的服务边界基本对应：

- `apps/web`：主应用前端；
- `apps/admin`：实例管理前端；
- `apps/space`：公开分享前端；
- `apps/api`：Django 后端 API；
- `apps/live`：实时协作服务；
- `apps/proxy`：入口代理相关服务。

`packages` 目录则是前端和通用代码的共享包。当前仓库中可以看到：

```text
packages/
├── codemods
├── constants
├── decorators
├── editor
├── hooks
├── i18n
├── logger
├── propel
├── services
├── shared-state
├── tailwind-config
├── types
├── typescript-config
├── ui
└── utils
```

这些包不是业务服务，而是多个应用之间复用的能力。例如：

- `ui`：通用 UI 组件；
- `editor`：富文本编辑器相关能力；
- `services`：前端请求服务封装；
- `types`：[TypeScript](https://www.typescriptlang.org/) 类型定义；
- `constants`：跨应用常量；
- `hooks`：React hooks；
- `i18n`：国际化；
- `utils`：工具函数；
- `shared-state`：共享状态管理；
- `tailwind-config` 和 `typescript-config`：统一配置。

这说明 Plane 的前端不是一个简单页面应用，而是多个前端应用共享组件、类型、服务封装和状态管理能力的 monorepo。

### package.json 反映出的前端工程结构

根目录 `package.json` 可以看到几个关键事实：

```json
{
  "name": "plane",
  "version": "1.3.1",
  "private": true,
    "license": "AGPL-3.0",
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev --concurrency=18",
    "start": "turbo run start",
    "clean": "turbo run clean && rm -rf .turbo && rm -rf .next && rm -rf node_modules && rm -rf dist",
    "fix": "turbo run fix",
    "check": "turbo run check",
    "check:types": "turbo run check:types"
  },
  "devDependencies": {
    "turbo": "2.9.4"
  },
  "engines": {
    "node": ">=22.18.0"
  },
  "packageManager": "pnpm@10.32.1+..."
}
```

这段配置说明：

- Plane 根项目是私有 monorepo，不是发布到 [npm](https://www.npmjs.com/) 的单包；
- 项目许可证是 [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html)；
- 构建和开发使用 [Turborepo](https://turbo.build/repo)；
- 包管理器是 [pnpm](https://pnpm.io/)；
- 当前要求 [Node.js](https://nodejs.org/) `>=22.18.0`；
- `dev` 命令通过 `turbo run dev --concurrency=18` 同时驱动多个子项目；
- `check:types`、`check:lint`、`check:format` 表示类型检查、lint 和格式化都被纳入统一脚本。

如果只是单个 React 项目，通常不会需要这种组织方式。Plane 使用 monorepo，是因为它有多个应用和多个共享包。统一构建可以减少重复配置，也方便在一个 PR 中同时修改 API 类型、前端服务封装、UI 组件和业务页面。

### Django 后端目录

`apps/api/plane` 目录下能看到典型 Django 项目结构，同时也有 Plane 自己的业务模块：

```text
apps/api/plane/
├── analytics
├── api
├── app
├── authentication
├── bgtasks
├── db
├── license
├── middleware
├── seeds/data
├── settings
├── space
├── static
├── tests
├── throttles
├── utils
├── web
├── __init__.py
├── asgi.py
├── celery.py
├── urls.py
└── wsgi.py
```

几个目录含义可以这样理解：

- `api`：REST API 入口、路由、视图或接口层；
- `db`：数据库模型或数据访问相关逻辑；
- `authentication`：认证、登录、token、用户身份；
- `middleware`：请求处理中间件；
- `bgtasks`：后台任务相关逻辑；
- `analytics`：分析统计；
- `space`：公开分享或 Space 相关后端逻辑；
- `settings`：Django 配置；
- `celery.py`：[Celery](https://docs.celeryq.dev/) 配置入口；
- `asgi.py` / `wsgi.py`：Django 应用入口；
- `urls.py`：URL 路由入口。

这里可以看出 Plane 后端不是只提供几个 CRUD API。它包含认证、限流、后台任务、分析、空间分享、许可、测试和中间件等多个后端关注点。

## 核心业务链路与源码阅读入口

讲 Plane 的源码时，不建议先从登录注册讲，也不建议先从目录树逐个文件夹讲。更合适的方式是选一个核心业务动作，例如“创建一个 Work Item”，然后把这个动作从前端页面一直追到 API、数据库、异步任务和通知。

### 创建 Work Item 的逻辑链路

一个用户在 Plane 中创建 work item，大致会经过：

```text
用户在 Web 前端填写标题、描述、状态、负责人、优先级等字段
  ↓
前端组件收集表单状态
  ↓
调用 packages/services 中封装的 API 请求
  ↓
请求进入 Django API
  ↓
认证和权限校验
  ↓
serializer / view / service 层处理请求数据
  ↓
写入 PostgreSQL
  ↓
必要时写入 activity / notification / audit 数据
  ↓
必要时投递 RabbitMQ 异步任务
  ↓
Worker 处理通知、外部集成、索引或后续任务
  ↓
前端刷新列表或通过实时机制收到更新
```

这条链路里有几个重点。

第一，前端不是直接操作数据库，而是通过 API。多个前端服务都要通过 API 完成数据操作，这也是官方架构文档中 “all frontend services communicate with this API” 的含义。

第二，API 不是只做数据落库。它还必须处理 workspace、project、member、role、permission 等权限边界。项目管理平台里，一个用户是否能看见某个 work item、是否能编辑某个 project、是否能管理 workspace，不是简单的登录态判断。

第三，创建 work item 后可能触发副作用。例如：

- 创建 activity log；
- 给负责人发送 notification；
- 触发 Slack 或其他外部通知；
- 更新 analytics 统计；
- 触发搜索索引更新；
- 触发相关 WebSocket 更新；
- 处理附件上传或富文本内容中的文件引用。

这些副作用不一定都应该放在同步 API 请求里，因此 Worker 和 RabbitMQ 很重要。

### 查询和 View 的链路

View 是 Plane 里非常能体现系统复杂度的功能。它不是一个静态列表，而是保存筛选条件、排序、分组和展示偏好的查询入口。

一个 View 的查询链路可以抽象为：

```text
用户打开某个保存的 View
  ↓
前端读取 View 配置
  ↓
把筛选条件、排序、分组、分页参数传给 API
  ↓
API 根据 workspace / project / permission 约束查询 work items
  ↓
数据库返回符合条件的数据
  ↓
前端按 board / list / calendar / spreadsheet 等方式展示
```

这里真正复杂的是查询条件。项目管理工具里的筛选往往很多：

- 状态；
- 优先级；
- 负责人；
- 标签；
- cycle；
- module；
- 创建时间；
- 更新时间；
- 截止时间；
- 关联关系；
- 自定义字段；
- 当前用户相关条件。

因此 View 的本质不是“前端保存一个列表”，而是“可复用的查询定义”。这类功能通常会牵涉到后端查询构造、权限过滤、前端状态同步和性能优化。

### Cycle 和 Module 的链路

Cycle 和 Module 都不是简单标签。它们会影响工作项组织方式、统计视图和团队协作。

Cycle 的链路通常是：

```text
创建 Cycle
  ↓
设置开始时间和结束时间
  ↓
把 Work Item 加入 Cycle
  ↓
按状态、负责人、优先级统计进度
  ↓
生成燃尽图或进展视图
```

Module 的链路通常是：

```text
创建 Module
  ↓
定义模块目标或功能范围
  ↓
把 Work Item 归入 Module
  ↓
按模块查看完成情况和阻塞点
```

两者在数据库中可能都是 Work Item 的关联对象，但业务语义不同。Cycle 是时间组织，Module 是结构组织。讲解时要避免把二者都说成“分类”。

### Page / Wiki 与富文本编辑器

Pages 和 Wiki 需要处理富文本内容、图片、附件、链接、引用、协同编辑等问题。仓库中有 `packages/editor`，说明编辑器能力被抽成了共享包，而不是散落在某个页面组件里。

富文本编辑器带来的工程问题包括：

- 内容存储格式；
- 文本、图片、链接、附件的混合处理；
- 文件上传到 MinIO/S3；
- 页面和 work item 的互相引用；
- 多人编辑时的实时状态；
- 内容渲染安全；
- Markdown、HTML 或编辑器内部 JSON 结构之间的转换。

因此，在讲 Plane 的 Pages 时，不能只说“它可以写文档”。更准确地说，Pages 是项目管理平台里的知识层，背后需要编辑器、文件存储、权限控制、实时协作和引用关系共同支撑。

### 实时协作链路

Plane 架构文档中列出了 Live 服务，说明它负责 WebSocket 实时协作，处理光标位置、实时更新和在线状态。实时协作服务的存在，意味着某些更新不只依赖用户刷新页面或重新请求 API。

一个简化链路可以理解为：

```text
用户 A 修改内容或状态
  ↓
API 或前端把事件传播给 Live
  ↓
Live 通过 WebSocket 通知相关在线用户
  ↓
用户 B 的页面局部更新
```

实时协作常见问题包括：

- 哪些事件需要实时推送；
- 如何限制只推送给有权限的用户；
- 断线重连如何处理；
- Redis / Valkey 是否参与在线状态或事件缓存；
- 多副本部署时 WebSocket 状态如何扩展；
- API 与 Live 之间如何共享鉴权密钥。

环境变量里有 `LIVE_SERVER_SECRET_KEY`，用于 API 和 live 服务之间通信。Live 并不是一个孤立服务，它需要和 API 之间建立可信通信。

### Integration、Silo 与 Intake

Plane 不只服务站内用户，也要和外部系统交互。架构文档中 Silo 是 integration backend，负责 GitHub、GitLab、Slack 连接，处理 OAuth flows、webhook processing 和外部 API 通信。Intake 则是 email ingestion service，把 incoming emails 转换成 work items 或 comments。

这类链路通常是：

```text
外部系统触发 Webhook
  ↓
Silo 接收并校验请求
  ↓
解析外部事件
  ↓
映射到 workspace / project / user / work item
  ↓
写入数据库或投递异步任务
  ↓
Plane 内部产生对应更新
```

邮件链路则可能是：

```text
用户发送邮件
  ↓
Intake 接收邮件
  ↓
解析发件人、主题、正文、附件
  ↓
根据规则创建 Work Item 或 Comment
  ↓
附件进入对象存储
  ↓
通知相关成员
```

这些功能让 Plane 从普通站内应用变成一个“工作流入口”。但同时也带来安全问题：Webhook 签名、OAuth token、外部账号绑定、邮件伪造、重复事件、失败重试都需要处理。

---

## 部署、环境变量与运行实践

Plane 是一个生产级[自托管](https://developers.plane.so/self-hosting/overview)平台。它的部署复杂度明显高于普通前后端项目。不能把它理解成“启动一个容器就行”。它至少涉及入口域名、反向代理、PostgreSQL、Redis/Valkey、RabbitMQ、对象存储、API、Worker、Beat Worker、Live、Migrator、环境变量、备份和升级。

### Docker Compose 中的真实服务

![Plane Docker Compose 安装过程](http://public.file.lvshuhuai.cn/images\plane-docker-compose.webp)

仓库中的 [Docker Compose](https://docs.docker.com/compose/) 配置可以看到多个服务。核心片段可以概括为：

```yaml
services:
  web:
    container_name: web
    build:
      context: .
      dockerfile: ./apps/web/Dockerfile.web
    depends_on:
      - api

  admin:
    container_name: admin
    build:
      context: .
      dockerfile: ./apps/admin/Dockerfile.admin
    depends_on:
      - api
      - web

  space:
    container_name: space
    build:
      context: .
      dockerfile: ./apps/space/Dockerfile.space
    depends_on:
      - api
      - web

  api:
    container_name: api
    build:
      context: ./apps/api
      dockerfile: Dockerfile.api
    command: ./bin/docker-entrypoint-api.sh
    depends_on:
      - plane-db
      - plane-redis

  worker:
    container_name: bgworker
    build:
      context: ./apps/api
      dockerfile: Dockerfile.api
    command: ./bin/docker-entrypoint-worker.sh
    depends_on:
      - api
      - plane-db
      - plane-redis

  beat-worker:
    container_name: beatworker
    build:
      context: ./apps/api
      dockerfile: Dockerfile.api
    command: ./bin/docker-entrypoint-beat.sh

  migrator:
    container_name: plane-migrator
    command: ./bin/docker-entrypoint-migrator.sh
    restart: no

  live:
    container_name: plane-live
    build:
      context: .
      dockerfile: ./apps/live/Dockerfile.live

  plane-db:
    image: postgres:15.7-alpine

  plane-redis:
    image: valkey/valkey:7.2.11-alpine

  plane-mq:
    image: rabbitmq:3.13.6-management-alpine

  plane-minio:
    image: minio/minio
```

这段配置反映出几个关键事实：

- `web`、`admin`、`space` 是三个前端服务；
- `api`、`worker`、`beat-worker`、`migrator` 都基于 `apps/api` 构建，但启动命令不同；
- `worker` 和 `beat-worker` 不是 API 的附属线程，而是独立容器；
- `migrator` 是一次性迁移容器，`restart: no`；
- `live` 是独立实时服务；
- 基础设施包括 PostgreSQL、Valkey、RabbitMQ、MinIO；
- 数据需要通过 volumes 持久化，例如 PostgreSQL 数据、Redis 数据、RabbitMQ 数据、MinIO 上传文件。

这就是为什么 Plane 的部署不能只关注前端端口。真正的稳定运行依赖多个容器之间的健康状态和配置一致性。

### 官方自托管安装流程

官方自托管文档给出的 Community Edition 安装流程大致是：

```bash
mkdir plane-selfhost
cd plane-selfhost
curl -fsSL -o setup.sh https://github.com/makeplane/plane/releases/latest/download/setup.sh
chmod +x setup.sh
./setup.sh
```

执行 `setup.sh` 后，会出现菜单：

```text
Select a Action you want to perform:
1) Install
2) Start
3) Stop
4) Restart
5) Upgrade
6) View Logs
7) Backup Data
8) Exit
```

这种安装方式不是让用户手动 clone 仓库再编译，而是下载 release 中的部署脚本和配置文件。对于自托管用户来说，重点是配置 `plane.env`、域名、端口、数据库、对象存储和 SSL，而不是理解前端如何 build。

官方文档也提醒：生产自托管时建议配置外部数据库和外部存储。原因很直接，项目管理平台的数据很关键，如果数据库和对象存储都放在单台机器本地，一旦机器损坏、磁盘故障或误删 volume，项目数据和附件可能一起丢失。

### 环境变量分类

Plane 的环境变量较多，但可以按功能分组理解。

#### 入口与跨域

```text
WEB_URL
CORS_ALLOWED_ORIGINS
DOMAIN_NAME
SITE_ADDRESS
LISTEN_HTTP_PORT
LISTEN_HTTPS_PORT
```

这些变量决定用户如何访问 Plane、[Caddy](https://caddyserver.com/) 或代理如何接入、API 是否允许某些前端 origin 访问。`WEB_URL` 应该是完整的 Web 应用基础 URL，例如 `https://plane.example.com`。`CORS_ALLOWED_ORIGINS` 通常需要包含 `WEB_URL`。

#### 数据库

```text
PGHOST
PGDATABASE
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
POSTGRES_PORT
DATABASE_URL
```

数据库是 Plane 最核心的状态存储。官方[环境变量文档](https://developers.plane.so/self-hosting/environment-variables)说明，`DATABASE_URL` 可以作为 PostgreSQL 完整连接串，并覆盖单独配置项。生产环境下，`POSTGRES_PASSWORD` 不应该保持默认值。

#### Redis / Valkey

```text
REDIS_HOST
REDIS_PORT
REDIS_URL
```

Redis/Valkey 用于缓存、session 和实时协作状态。它不是可有可无的普通缓存，因为 session 和实时协作状态都可能依赖它。

#### RabbitMQ

```text
RABBITMQ_HOST
RABBITMQ_PORT
RABBITMQ_USER
RABBITMQ_PASSWORD
RABBITMQ_VHOST
AMQP_URL
```

RabbitMQ 负责异步任务队列。Worker 通过它获取任务。如果 RabbitMQ 异常，API 可能仍能处理部分同步请求，但通知、导入导出、外部事件等后台任务会受影响。

#### 安全密钥

```text
SECRET_KEY
MACHINE_SIGNATURE
LIVE_SERVER_SECRET_KEY
PI_INTERNAL_SECRET
```

`SECRET_KEY` 用于加密签名相关操作，`LIVE_SERVER_SECRET_KEY` 用于 API 和 Live 服务之间通信。生产环境中这些值不能使用默认值，也不能泄露到公开仓库或截图中。

#### 对象存储

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_S3_ENDPOINT_URL
AWS_S3_BUCKET_NAME
```

Plane 使用 MinIO/S3 保存文件上传、附件和导出文件。对象存储出问题时，work item 文本可能还在，但附件、图片、导出文件会受到影响。

### 本地开发环境

[贡献文档](https://github.com/makeplane/plane/blob/preview/CONTRIBUTING.md)中给出的开发要求包括：

```text
Docker Engine
Node.js 20+
Python 3.8+
Postgres v14
Redis v6.2.7
至少推荐 12 GB RAM
```

它还明确说明：项目是一个 monorepo，后端 API 和前端在同一仓库中，后端 Django 项目位于 `apps/api`。

本地开发流程可以概括为：

```bash
git clone https://github.com/makeplane/plane.git [folder-name]
cd [folder-name]
chmod +x setup.sh
./setup.sh
docker compose -f docker-compose-local.yml up
pnpm dev
```

然后访问：

```text
http://localhost:3001/god-mode/
```

注册 instance admin，再访问：

```text
http://localhost:3000
```

使用同样凭据登录。

这里要注意，开发模式和生产部署模式不是一回事。开发模式下，Docker Compose 主要用于启动依赖服务和本地环境，`pnpm dev` 用于启动前端 monorepo 的开发服务。生产自托管则更强调 release 安装、环境变量、域名、SSL、数据持久化和备份。

### 部署排查顺序

Plane 部署出错时，不应该只看一个容器日志。应该按服务依赖顺序排查：

```text
1. Proxy / Caddy 是否能接收入口请求
2. Web / Admin / Space 是否正常启动
3. API 是否能连接 PostgreSQL 和 Redis
4. Migrator 是否完成数据库迁移
5. Worker 是否能连接 RabbitMQ
6. Beat Worker 是否正常运行周期任务
7. Live 是否能和 API 使用相同密钥通信
8. MinIO/S3 是否能保存和读取上传文件
9. CORS、WEB_URL、SITE_ADDRESS 是否配置一致
10. 数据卷和外部存储是否持久化
```

更具体地说，如果页面打不开，优先看 Proxy 和 Web；如果页面能打开但登录失败，看 API、数据库、认证配置；如果任务能创建但没有通知或导入导出失败，看 RabbitMQ 和 Worker；如果附件上传失败，看 MinIO/S3；如果多人实时更新失败，看 Live、WebSocket、Redis 和相关密钥。

### 生产环境风险

Plane 是项目管理平台，保存的是团队工作数据、附件、文档、成员信息和外部集成凭据。因此生产部署要特别注意：

- 不要使用默认数据库密码、RabbitMQ 密码和 MinIO 密码；
- 不要把 `.env`、`plane.env`、API key、OAuth secret 上传到公开仓库；
- 生产环境建议使用 [HTTPS](https://developer.mozilla.org/en-US/docs/Glossary/HTTPS)；
- 定期备份 PostgreSQL 和对象存储；
- 如果使用本地 volume，要确认宿主机磁盘可靠性；
- 对外开放前要确认 [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)、域名和反向代理配置；
- 对 GitHub、GitLab、Slack、Sentry 等集成使用最小权限；
- 升级前先备份数据库和对象存储；
- 关注 Migrator 是否执行成功，避免 schema 与应用版本不匹配；
- 如果团队规模较大，应评估 worker、API、PostgreSQL、RabbitMQ 的扩展和监控。
