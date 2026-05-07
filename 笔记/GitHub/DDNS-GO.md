# DDNS-GO 项目系统性讲解笔记

> 仓库：`https://github.com/jeessy2/ddns-go`
>
> 核对时间：2026-05-06
>
> 文档目标：把 ddns-go 当作一个完整的 Go 运维工具项目来讲解，而不是只介绍 README 的使用命令，也不是机械逐文件读源码。

## 项目定位与 DDNS 闭环

![DDNS 自动更新闭环](http://public.file.lvshuhuai.cn/images\ddns-go-ddns-workflow.png)

[ddns-go](https://github.com/jeessy2/ddns-go) 的核心目标很明确：自动获得当前机器或网络出口的公网 [IPv4](https://en.wikipedia.org/wiki/IPv4) / [IPv6](https://en.wikipedia.org/wiki/IPv6) 地址，并把这个地址同步到域名解析服务商中对应的解析记录。它解决的不是“如何购买域名”或“如何搭建服务器”，而是[动态 DNS（DDNS）](https://en.wikipedia.org/wiki/Dynamic_DNS) 场景下的域名记录自动更新问题。

很多家庭宽带、[NAS](https://en.wikipedia.org/wiki/Network-attached_storage)、软路由、个人服务器、实验室服务器都会遇到类似问题：

- 机器本身可以对外提供服务；
- 域名也已经购买并托管到某个 [DNS](https://www.cloudflare.com/learning/dns/what-is-dns/) 服务商；
- 但是公网 IP 可能变化，尤其是家宽、动态 IPv6、运营商重新分配地址、路由器重启之后；
- 一旦 IP 变化，旧的 A / AAAA 记录就失效，域名仍然指向旧地址。

ddns-go 的作用就是把这件事自动化。它不是代理服务器，也不是内网穿透工具，它并不帮你打通 [NAT](https://en.wikipedia.org/wiki/Network_address_translation)，也不帮你绕过运营商没有公网地址的问题。它假设你至少有一个能被外部访问的公网 IPv4 或 IPv6，然后负责把这个地址同步到 DNS 记录。

可以把它的业务闭环抽象成下面这条链路：

```text
定时触发
  ↓
获取当前公网 IPv4 / IPv6
  ↓
和本地缓存、远端解析记录进行比较
  ↓
如果 IP 没变，跳过更新
  ↓
如果 IP 变化，调用 DNS 服务商 API
  ↓
新增或更新 A / AAAA 记录
  ↓
执行 Webhook 通知
  ↓
等待下一次定时检查
```

这条链路看上去简单，但它背后涉及几个典型工程问题：后台服务如何长期运行、配置如何持久化、不同 DNS 服务商 [API](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Client-side_APIs/Introduction) 如何适配、IP 获取如何兼容 IPv4/IPv6、失败后如何恢复、Web 管理界面如何保护密钥。这些点组合起来，ddns-go 就不只是一个“脚本”，而是一个轻量级 [Go](https://go.dev/) 运维自动化项目。

### A 记录、AAAA 记录与 DDNS 的关系

![DNS 记录类型示意](http://public.file.lvshuhuai.cn/images\ddns-go-network-architecture.png)

域名解析里，[A 记录](https://www.cloudflare.com/learning/dns/dns-records/dns-a-record/) 通常对应 IPv4 地址，[AAAA 记录](https://www.cloudflare.com/learning/dns/dns-records/dns-aaaa-record/) 通常对应 IPv6 地址。ddns-go 的配置也自然分成 IPv4 和 IPv6 两组：IPv4 可以启用或关闭，IPv6 也可以启用或关闭，每组都可以配置获取方式和域名列表。

一个典型场景如下：

```text
home.example.com  A     1.2.3.4
home.example.com  AAAA  2409:xxxx:xxxx::1234
```

如果用户的 IPv4 或 IPv6 地址发生变化，ddns-go 就会尝试把上述记录更新成新地址。这里的“动态”不是 DNS 协议本身动态，而是由程序定时检测并调用 DNS 服务商的 [HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview) API 来完成更新。

### 它适合的部署场景

ddns-go 最常见的运行环境包括：

- 家庭 NAS，例如群晖、威联通、Linux 小主机；
- 软路由或旁路由；
- 有公网 IPv6 的 Windows / macOS / Linux 机器；
- 云服务器上需要同步某些动态网络地址的特殊场景；
- [OpenWrt](https://openwrt.org/)、[Docker](https://docs.docker.com/get-started/docker-overview/)、系统服务等后台运行环境。

其中最典型的是家庭或实验室网络。比如用户在家里放了一台 NAS，希望通过 `nas.example.com` 访问。只要公网 IP 变化，ddns-go 就自动更新解析记录，用户无需登录阿里云、腾讯云、Cloudflare 控制台手动修改。

但要注意，ddns-go 不解决以下问题：

- 没有公网 IPv4，也没有可入站访问 IPv6；
- 光猫、路由器、防火墙没有放行端口；
- DNS 服务商 API 权限错误；
- 域名没有正确托管到对应 DNS 服务商；
- 运营商封锁了常见服务端口。

因此，在讲这个项目时，不应该把它说成“远程访问神器”，而应该准确定位为“动态公网 IP 到 DNS 解析记录的自动同步器”。

## 运行、部署与配置入口

ddns-go 是一个长期运行型程序。它既可以直接以前台进程方式运行，也可以安装成系统服务，还可以放进 Docker 容器中。[README](https://github.com/jeessy2/ddns-go#readme) 中明确给出了系统运行、Docker 运行、IPv6 使用、[Webhook](https://en.wikipedia.org/wiki/Webhook)、[Callback](https://en.wikipedia.org/wiki/Callback_%28computer_programming%29) 等配置入口。项目支持 Mac、Windows、Linux，也支持 ARM、x86、RISC-V 架构；支持阿里云、腾讯云、Dnspod、Cloudflare、华为云、Callback、百度云、Porkbun、GoDaddy、Namecheap、NameSilo、Dynadot、DNSLA、EdgeOne、IBM NS1 Connect、雨云等多种服务商。

### 系统服务方式

系统服务方式适合 Windows、macOS、Linux，尤其适合需要稳定长期运行的场景。安装服务后，ddns-go 会跟随系统启动，在后台定期执行 DDNS 更新。

常用命令如下：

```bash
# Linux / macOS
sudo ./ddns-go -s install

# Windows 管理员 cmd
.\ddns-go.exe -s install
```

安装成功后，默认访问：

```text
http://localhost:9876
```

进行初始化配置。

这种方式的优势是对 IPv6 更友好，尤其是 Windows / macOS。README 中特别说明，Windows/Mac 桌面版 Docker 不支持 `--net=host`，因此如果重点使用 IPv6，Windows/Mac 更推荐系统方式运行。

系统服务方式还支持带参数安装。例如：

```bash
./ddns-go -s install -f 600 -c /Users/name/.ddns_go_config.yaml
```

含义是：以系统服务方式安装，更新间隔设置为 600 秒，并指定配置文件路径。

另一个更有工程意义的例子是：

```bash
./ddns-go -s install -f 10 -cacheTimes 180
```

这表示每 10 秒检查一次本地 IP 变化，但每隔 180 次才强制和服务商比对一次。实际效果是：本地 IP 变化时可以较快触发更新，同时避免频繁调用 DNS 服务商 API 导致限流。

### Docker 方式

![Docker 镜像层示意](http://public.file.lvshuhuai.cn/images\ddns-go-docker-image-layers.webp)

Docker 方式适合 Linux 主机、群晖、软路由等环境。最常见写法是：

```bash
docker run -d \
  --name ddns-go \
  --restart=always \
  --net=host \
  -v /opt/ddns-go:/root \
  jeessy/ddns-go
```

这里有几个关键点：

- `--restart=always`：容器异常退出或主机重启后自动恢复；
- `--net=host`：容器直接使用宿主机网络栈；
- `-v /opt/ddns-go:/root`：把配置文件持久化到宿主机目录；
- 默认 Web 端口仍然是 `9876`。

如果不使用 host 网络，也可以这样：

```bash
docker run -d \
  --name ddns-go \
  --restart=always \
  -p 9876:9876 \
  -v /opt/ddns-go:/root \
  jeessy/ddns-go
```

但在 IPv6 场景下，host 网络通常更合适。因为 DDNS 程序关心的是“宿主机真实看到的公网地址”，非 host 网络可能让容器看到的是 Docker 网络环境，而不是宿主机真实网络状态。

### 配置项不是简单表单，而是运行时模型

![ddns-go DNS 服务商配置界面](http://public.file.lvshuhuai.cn/images\ddns-go-provider-config.png)

ddns-go 的 Web 页面看起来是一个配置表单，但从源码角度看，它实际对应一个配置模型。核心配置在 `config/config.go` 中。`DnsConfig` 被拆成 IPv4、IPv6、DNS 服务商、TTL、HTTP 请求网卡等部分。

源码中的结构可以概括为：

```go
type DnsConfig struct {
    Name string
    Ipv4 struct { Enable bool; GetType string; URL string; NetInterface string; Cmd string; Domains []string }
    Ipv6 struct { Enable bool; GetType string; URL string; NetInterface string; Cmd string; Ipv6Reg string; Domains []string }
    DNS DNS
    TTL string
    HttpInterface string
}
```

这个结构说明 ddns-go 的设计重点不是“一个服务商 + 一个域名”，而是允许一个配置块同时控制 IPv4 和 IPv6，并且让二者有不同的获取方式。IPv4 可以通过接口获取，IPv6 可以通过网卡获取；IPv4 和 IPv6 也可以绑定不同域名列表。

`DNS` 结构则保存服务商相关信息：

```go
type DNS struct {
    Name string
    ID string
    Secret string
    ExtParam string
}
```

其中 `Name` 决定使用哪个 DNS 服务商适配器，`ID` 和 `Secret` 通常是 API 凭据，`ExtParam` 用于某些服务商的扩展参数。

### IPv4 / IPv6 获取方式

![ddns-go IPv6 网卡获取配置](http://public.file.lvshuhuai.cn/images\ddns-go-ipv6-network-card.png)

ddns-go 支持多种 IP 获取方式。一般可以理解为三类：

1. 通过外部 URL 获取

    程序访问一个“返回当前公网 IP”的接口，从 HTTP 响应中提取 IP。这种方式适合普通 IPv4 公网地址检测。

2. 通过本机网卡获取

    程序直接读取指定网卡上的 IP 地址。这种方式常用于 IPv6，因为很多 IPv6 地址直接分配在本机网卡上。

3. 通过命令获取

    用户自定义命令，程序从命令输出中提取 IP。这种方式适合高级场景，例如从路由器、脚本、特定网络工具中获取地址。

URL 获取简单，但依赖外部接口；网卡获取更贴近本机真实网络，但要求用户知道目标网卡；命令获取自由度最高，但也最容易因为脚本输出格式、权限、编码等问题出错。

### Webhook 与 Callback 的区别

![Callback 更新链路示意](http://public.file.lvshuhuai.cn/images\ddns-go-callback-update.png)

这两个概念容易混淆，但它们在 ddns-go 里的语义不同。

Webhook 是“更新之后通知别人”。也就是说，ddns-go 已经完成了 IP 检测和 DNS 更新，然后把结果推送到外部服务，比如 Server 酱、Bark、钉钉、飞书、Telegram、Discord 等。README 中列出的变量包括：

- `#{ipv4Addr}`：新的 IPv4 地址；
- `#{ipv4Result}`：IPv4 更新结果；
- `#{ipv4Domains}`：IPv4 域名列表；
- `#{ipv6Addr}`：新的 IPv6 地址；
- `#{ipv6Result}`：IPv6 更新结果；
- `#{ipv6Domains}`：IPv6 域名列表；
- `#{timestamp}`：当前 UTC 时间戳。

Callback 则是“把 DNS 更新动作交给自定义回调”。它更像一个自定义 DNS 服务商适配器。README 中说明，配置了几行域名就会回调几次，变量包括：

- `#{ip}`：新的 IPv4 / IPv6 地址；
- `#{domain}`：当前域名；
- `#{recordType}`：记录类型，A 或 AAAA；
- `#{ttl}`：TTL。

所以可以直接记成：

```text
Webhook = DDNS 更新结果通知
Callback = 自定义 DNS 更新实现
```

如果只是想收到“IP 变了”的消息，用 Webhook；如果某个 DNS 服务商没有内置适配器，但你可以通过 HTTP 接口更新记录，则可以考虑 Callback。

## 源码结构与主链路

ddns-go 的源码组织比较适合拿来讲 Go 运维工具项目。它没有复杂的微服务分层，也不是典型的 CRUD Web 后端，而是由几个功能模块围绕一个定时任务闭环组织起来。

可以把项目结构抽象成：

```text
ddns-go
├── main.go          程序入口、命令行参数、服务安装、Web 服务启动、定时任务启动
├── config/          配置模型、配置文件读写、兼容旧配置、Webhook 执行
├── dns/             DNS 服务商适配器，核心 DDNS 更新逻辑
├── web/             Web 管理页面、登录认证、配置保存、日志查看
├── util/            IP 获取、HTTP 客户端、缓存、网络检测、密码、日志、系统工具
├── static/          前端静态资源
├── Dockerfile       容器构建
├── Makefile         本地构建
└── .goreleaser.yml  发布配置
```

这套结构体现了一个轻量工具项目的典型组织方式：入口负责运行形态，配置层负责状态持久化，业务层负责 DDNS 更新，Web 层负责人机交互，工具层负责系统和网络细节。

### main.go：运行形态的总入口

`main.go` 首先解析命令行参数。项目支持的参数包括版本查看、自更新、监听地址、同步间隔、缓存次数、服务安装/卸载/重启、配置文件路径、是否禁用 Web、是否跳过证书验证、自定义 DNS、重置密码、后台运行等。

入口逻辑可以概括成：

```text
解析命令行参数
  ↓
处理版本查看 / 自更新 / 后台运行 / Android 时区修正
  ↓
检查监听地址
  ↓
设置配置文件路径、跳过证书验证、自定义 DNS、缓存次数
  ↓
如果是 install / uninstall / restart，则执行服务管理
  ↓
否则判断当前是否在 Docker 或系统服务环境中
  ↓
进入 run()
```

`run()` 是真正启动运行时逻辑的地方。它做了几件关键事：

1. 读取并兼容旧配置；
2. 初始化日志语言；
3. 如果没有指定 `-noweb`，则启动 Web 服务；
4. 初始化备用 DNS；
5. 等待网络可用；
6. 启动 DNS 定时任务。

源码中的关键调用可以简化成：

```go
conf, _ := config.GetConfigCached()
conf.CompatibleConfig()
go runWebServer()
util.InitBackupDNS(...)
util.WaitInternet(dns.Addresses)
dns.RunTimer(time.Duration(*every) * time.Second)
```

这个顺序很重要。DDNS 不是程序启动后立刻盲目调用服务商 API，而是先处理配置，再启动 Web，再确认网络，再进入定时任务。对于这种网络工具，等待网络可用是必要的，否则开机自启时很容易在网络尚未就绪时失败。

### Web 服务不是主业务，但它是配置入口

![ddns-go Web 配置界面](http://public.file.lvshuhuai.cn/images\ddns-go-web-ui.png)

`main.go` 中的 `runWebServer()` 注册了多个 HTTP 路由，包括：

- `/login`：登录页面；
- `/loginFunc`：登录逻辑；
- `/`：配置页面；
- `/save`：保存配置；
- `/setLang`：设置语言；
- `/logs`：查看日志；
- `/clearLog`：清空日志；
- `/webhookTest`：测试 Webhook；
- `/logout`：退出登录；
- `/static/` 和 `/favicon.ico`：静态资源。

这些路由说明 Web 层主要承担“配置管理”和“状态查看”的职责，而不是业务主循环。DDNS 主任务在 `dns.RunTimer()` 中，Web 页面只是修改配置和查看结果。

这类设计在运维工具中很常见：程序需要长期运行，但用户并不需要命令行编辑 YAML，所以提供一个轻量 Web UI 作为配置入口。

### dns/index.go：DDNS 主循环

`dns/index.go` 是项目业务链路的关键文件。它定义了统一的 DNS 接口：

```go
type DNS interface {
    Init(...)
    AddUpdateDomainRecords(...)
}
```

从设计角度看，这就是服务商适配器的统一入口。主流程不关心阿里云、腾讯云、Cloudflare 的 API 细节，只关心某个适配器是否能初始化并执行“添加或更新解析记录”。

定时任务的结构也很直接：

```go
func RunTimer(delay time.Duration) {
    for {
        RunOnce()
        time.Sleep(delay)
    }
}
```

`RunTimer` 只是循环调度，真正的一轮更新在 `RunOnce()` 中完成。`RunOnce()` 的逻辑可以概括为：

```text
读取配置
  ↓
如果配置读取失败，直接返回
  ↓
根据 DNS 配置数量初始化 IPv4 / IPv6 cache
  ↓
遍历每一个 DNS 配置块
  ↓
根据 dc.DNS.Name 选择具体服务商适配器
  ↓
调用 Init()
  ↓
调用 AddUpdateDomainRecords()
  ↓
执行 Webhook
  ↓
如果 IPv4 或 IPv6 更新失败，则清理对应 cache
  ↓
本轮结束，取消 ForceCompareGlobal
```

源码中可以看到一个较长的 `switch dc.DNS.Name`，它把配置中的服务商名称映射到具体实现。例如：

```go
case "alidns":
    dnsSelected = &Alidns{}
case "cloudflare":
    dnsSelected = &Cloudflare{}
case "callback":
    dnsSelected = &Callback{}
```

这个 `switch` 是当前项目的服务商注册表。它不是动态插件机制，而是静态编译进二进制的适配器集合。好处是简单直接，二进制部署方便；缺点是新增服务商需要改源码并重新编译。

### config/config.go：配置不是临时变量，而是持久化状态

配置文件由 `config/config.go` 处理。`Config` 中包含多个 `DnsConfig`：

```go
type Config struct {
    DnsConf []DnsConfig
    User
    Webhook
    NotAllowWanAccess bool
    Lang string
}
```

`DnsConf []DnsConfig` 是一个重要设计点。它说明 ddns-go 支持同时配置多个 DNS 服务商，而不是全局只有一个服务商。比如一个用户可以同时维护阿里云上的一个域名和 Cloudflare 上的另一个域名。

配置读取函数 `GetConfigCached()` 做了缓存：

```text
加锁
  ↓
如果内存中已有配置，直接返回
  ↓
读取配置文件
  ↓
YAML 反序列化
  ↓
如果用户名和密码为空，强制禁止公网访问
  ↓
缓存配置并返回
```

这里有两个工程细节值得注意。

第一，配置读取加锁并缓存，避免每次定时任务、Web 请求都重复读取磁盘。对于这种小工具来说，性能不是主要矛盾，但缓存可以减少 I/O，同时让配置访问更一致。

第二，如果配置文件里没有用户名和密码，源码会设置 `NotAllowWanAccess = true`。这是一种安全兜底：未初始化的 Web 配置界面不应该直接暴露在公网。

保存配置时，源码使用 [YAML](https://yaml.org/) 序列化，并以 `0600` 权限写入配置文件。这个权限设置也很合理，因为配置文件里包含 DNS API 凭据，理论上只应该被当前运行用户读取和写入。

### web/auth.go：Web 配置界面的安全边界

ddns-go 的 Web 页面会暴露敏感配置，所以认证逻辑必须单独讲。`web/auth.go` 里的 `Auth` 函数会检查浏览器 Cookie，如果没有 Cookie，就重定向到登录页面；如果配置禁止公网访问，并且请求不是私有网络来源，则直接返回 403。

可以概括为：

```text
读取 cookie
  ↓
没有 cookie：跳转登录
  ↓
读取配置
  ↓
如果禁止公网访问且来源不是私网：403
  ↓
校验系统内保存的 cookie token
  ↓
通过则执行被保护的 handler
```

静态资源也不是完全裸奔的。`AuthAssert` 会保护静态文件等资源；如果配置文件为空且程序启动超过 3 小时，又有公网来源访问，就返回 403。这体现了项目对“初始化阶段被公网扫到”的风险有所考虑。

但这不代表可以随意把 ddns-go 暴露到公网。README 也提醒，如果启用公网访问，建议通过 [Nginx](https://nginx.org/) 等反向代理启用 [HTTPS](https://developer.mozilla.org/en-US/docs/Glossary/HTTPS)。原因很直接：DNS 服务商凭据、登录 Cookie、Web 配置内容都属于敏感信息，裸 HTTP 暴露在公网有被截获和爆破的风险。

## 关键设计：适配器、缓存、失败恢复与扩展点

ddns-go 的代码量不算巨大，但几个设计点很典型，适合从工程角度拆解。

### DNS 服务商适配器

不同 DNS 服务商 API 差异很大：

- 鉴权方式不同；
- 请求签名不同；
- 查询记录接口不同；
- 新增记录和更新记录的请求体不同；
- TTL、线路、代理状态、区域解析等扩展参数不同。

如果主流程直接写满各种服务商 API 细节，代码会迅速变得不可维护。因此 ddns-go 用统一接口把主流程和服务商实现分离。主流程只需要：

```text
选择适配器
  ↓
初始化适配器
  ↓
调用添加/更新记录
```

每个服务商文件，例如 `alidns.go`、`cloudflare.go`、`dnspod.go`、`tencent_cloud.go`，则负责具体 API 细节。这是典型的[适配器模式](https://refactoring.guru/design-patterns/adapter)。

它的优点是：

- 主流程保持稳定；
- 新增服务商有明确位置；
- 各服务商签名和请求逻辑互不污染；
- Callback 可以作为特殊适配器，绕过内置服务商限制。

它的不足是：

- 服务商注册依赖 `switch`，不是插件化注册；
- 每新增一个服务商都要修改 `dns/index.go`；
- 适配器之间可能存在相似逻辑，但复用程度有限。

对于 ddns-go 这种单二进制工具，这个权衡是合理的。它不追求运行时插件动态加载，而是追求构建和部署简单。

### 本地缓存与服务商 API 限流

DDNS 程序不能每隔几秒就无脑调用 DNS 服务商 API。服务商 API 通常有限流，频繁查询和更新没有意义，还可能导致账号被限制。

ddns-go 的缓存设计体现在 `dns/index.go` 的 `Ipcache` 上。它为每个 DNS 配置维护 IPv4 和 IPv6 两个 cache：

```text
Ipcache[i][0] = 第 i 个 DNS 配置的 IPv4 cache
Ipcache[i][1] = 第 i 个 DNS 配置的 IPv6 cache
```

当配置数量变化，或者触发强制比对时，缓存会重新初始化。更新失败时，源码会清理对应 cache：

```go
if v4Status == config.UpdatedFailed {
    Ipcache[i][0] = util.IpCache{}
}
```

这背后的含义是：如果某次 IPv4 更新失败，下一轮不能继续相信旧缓存，否则可能误判“IP 没变”而跳过修复。清理 cache 可以促使下一轮重新比较和更新。

`-cacheTimes` 参数则提供了另一个控制维度。它允许程序更频繁地检查本地 IP，但较低频率地强制与服务商比对，从而兼顾响应速度和 API 调用频率。

### Webhook 的执行位置

Webhook 在 `RunOnce()` 中出现在 `AddUpdateDomainRecords()` 之后。这很合理，因为 Webhook 通知的是本轮 DDNS 操作结果，而不是操作前状态。

链路可以理解为：

```text
服务商适配器返回 domains 结果
  ↓
config.ExecWebhook(&domains, &conf)
  ↓
得到 IPv4 / IPv6 更新状态
  ↓
失败则清理对应 cache
```

也就是说，Webhook 不只是通知模块，它的返回状态还参与了后续缓存处理。这个细节说明 Webhook 结果和主流程之间并非完全隔离。

### 配置兼容与版本演进

`run()` 中调用了 `conf.CompatibleConfig()`。配置兼容是这类长期维护工具中很重要的部分。用户可能从旧版本升级到新版本，如果配置结构变化，程序需要尽量兼容旧格式，而不是要求用户手动迁移。

源码中可以看到它处理了两类兼容：

- 旧密码如果不是 [bcrypt](https://en.wikipedia.org/wiki/Bcrypt) 哈希，则进行哈希后保存；
- 兼容 v5.0.0 之前的配置文件，把旧结构迁移到新的 `DnsConf` 数组结构中。

这说明 ddns-go 的配置模型经历过演进：从单配置逐渐变成支持多个 DNS 配置块。项目讲解时不应该只说“它有配置文件”，而应该说明配置文件也是项目版本演进的一部分。

## 部署风险、调试方法与实践建议

ddns-go 的使用看起来很简单，但真实部署中常见问题通常不在 Go 代码本身，而在网络环境、DNS 服务商配置、IPv6、Docker 网络、权限和安全暴露。

### IPv6 场景的判断顺序

IPv6 问题不能只看 ddns-go 页面里有没有检测到地址。应该按顺序判断：

1. 本机是否真的有全局 IPv6 地址；
2. 本机是否能访问 IPv6 网络；
3. 外部网络是否能访问该 IPv6；
4. 防火墙是否放行对应端口；
5. 域名 AAAA 记录是否已经更新；
6. DNS 递归解析是否已经刷新；
7. 访问端是否也支持 IPv6。

常见误区是：本机网卡上有 IPv6 地址，就认为外部一定能访问。实际上，防火墙、路由器、运营商策略、系统入站规则都会影响访问结果。

在 Docker 场景下还要额外确认容器网络。Linux 上使用 `--net=host` 通常更接近真实宿主机网络；Windows/Mac Docker Desktop 则不适合依赖 host 网络做 IPv6 检测。

### DNS 更新失败的排查顺序

当域名没有更新成功时，不要直接怀疑 ddns-go。可以按下面顺序排查：

```text
检查 ddns-go 日志
  ↓
确认是否获取到了正确 IP
  ↓
确认 DNS 服务商选择是否正确
  ↓
确认 ID / Secret / Token 权限是否正确
  ↓
确认域名是否托管在该服务商
  ↓
确认记录类型 A / AAAA 是否匹配
  ↓
确认主域名、子域名填写是否符合项目要求
  ↓
确认服务商 API 是否限流或报错
  ↓
使用 dig / nslookup 查询解析结果
```

在命令行中可以这样查：

```bash
nslookup home.example.com
nslookup -type=AAAA home.example.com
```

或：

```bash
dig home.example.com A
dig home.example.com AAAA
```

如果服务商控制台里已经更新成功，但本地查询仍然是旧 IP，可能是 DNS 缓存或 TTL 尚未过期，不一定是 ddns-go 的问题。

### 安全建议

![通过 DNS Challenge 申请 HTTPS 证书](http://public.file.lvshuhuai.cn/images\ddns-go-https-dns-challenge.png)

ddns-go 的 Web 页面里保存了 DNS 服务商凭据，因此安全边界要格外清楚。

建议遵守以下原则：

- 不要随意把 `9876` 端口暴露到公网；
- 如果必须公网访问，使用 Nginx / [Caddy](https://caddyserver.com/) / [Traefik](https://traefik.io/traefik/) 等反向代理加 HTTPS；
- 登录密码不要使用弱密码；
- DNS API 凭据尽量使用最小权限；
- 配置文件目录不要给过宽权限；
- Docker 挂载目录中保存的配置文件要避免被其他用户读取；
- 不要在公开截图、日志、教程中暴露 ID、Secret、Token；
- 使用 `-noweb` 可以在配置完成后关闭 Web 服务，只保留后台 DDNS 任务。

其中“最小权限”很重要。比如 [Cloudflare API Token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/) 可以只授权某个 Zone 的 DNS 编辑权限，而不是给全账号全局权限。阿里云、腾讯云等也应尽量使用受限策略，而不是主账号 AK/SK。

### 新增一个 DNS 服务商应该怎么做

如果要扩展 ddns-go，最直接的方式是新增一个服务商适配器。整体步骤是：

1. 在 `dns/` 目录下新增一个服务商文件，例如 `exampledns.go`；
2. 定义一个结构体，例如 `type ExampleDNS struct { ... }`；
3. 实现 `Init(...)`，读取配置、初始化凭据、保存 IPv4 / IPv6 cache；
4. 实现 `AddUpdateDomainRecords()`，完成查询、新增、更新记录；
5. 在 `dns/index.go` 的 `switch dc.DNS.Name` 中加入分支；
6. 在 Web 配置页面中加入服务商选项；
7. 补充 README 或 Wiki 中的配置说明；
8. 本地编译并测试 A / AAAA 记录更新。

这里最核心的是第 3 和第 4 步。一般服务商适配器内部还需要拆分出几个动作：

```text
查询已有解析记录
  ↓
判断记录是否存在
  ↓
不存在：创建记录
  ↓
存在但 IP 不同：更新记录
  ↓
存在且 IP 相同：跳过
  ↓
返回 domains 结果给主流程和 Webhook
```

如果只是个人使用，不想改源码，也可以使用 Callback。Callback 的优点是不需要重新编译 ddns-go；缺点是复杂逻辑要放到外部 HTTP 服务中维护。

### 这个项目适合学什么

ddns-go 适合用来学习以下工程主题：

- Go 单二进制运维工具如何组织；
- 命令行参数、系统服务、Docker 运行方式如何统一；
- Web 配置界面和后台定时任务如何共存；
- YAML 配置如何缓存、保存、兼容旧版本；
- 多服务商 API 如何用适配器模式收敛；
- 网络工具如何处理 IPv4 / IPv6、网卡、外部接口、命令输出；
- 后台任务如何做缓存、失败恢复和限流规避；
- 运维工具如何处理公网访问安全边界。

不太适合把它当作传统 Web 后端模板。它没有复杂数据库、没有 ORM、没有业务表、没有分布式队列，也不是微服务结构。它更像是一个“系统工具 + Web UI + API 适配器 + 定时任务”的组合。

## 一份可复述的项目总结

ddns-go 是一个用 Go 编写的轻量级 DDNS 客户端。它通过定时获取当前机器或网络出口的公网 IPv4 / IPv6 地址，调用 DNS 服务商 API 更新对应域名的 A / AAAA 记录，从而解决动态公网 IP 导致域名解析失效的问题。

从运行形态看，它支持系统服务、Docker、Web 配置界面和命令行参数；从业务结构看，它的核心链路是 `main.go` 启动运行时环境，`config` 读取配置，`dns.RunTimer()` 定时调用 `RunOnce()`，再通过 `DNS` 接口选择具体服务商适配器完成记录更新；从工程设计看，它使用适配器模式隔离不同 DNS 服务商 API，用 IP cache 和 `cacheTimes` 降低无效调用，用 Webhook 完成结果通知，用 `NotAllowWanAccess` 和认证逻辑保护 Web 配置界面。

讲解这个项目时，最重要的不是 Go 语法，也不是把每个文件逐行读完，而是抓住这条主线：

```text
动态公网 IP
  → IP 检测
  → 缓存比较
  → DNS 服务商适配
  → A / AAAA 记录更新
  → Webhook 通知
  → 长期后台运行
```

这条主线贯穿了项目的业务目标、部署方式、源码结构和安全风险。围绕这条线讲，ddns-go 就能被解释成一个完整的、可部署的、具备实际工程价值的 Go 运维工具项目。
