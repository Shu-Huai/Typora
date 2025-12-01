# Spring Boot 4.0 新特性

2025 年 11 月，Spring Boot 4.0 与 Spring Framework 7 正式 GA，标志着 Spring 生态进入新一代。官方定位很明确：**在未来数年为 Java/Spring 应用提供新的“长期基础平台”**。

结合你截图中的内容 + 官方文档 + 社区文章，可以大致概括为几条主线：

- 平台基线升级：Java 17 起步，拥抱 JDK 25、Jakarta EE 11、Kotlin 2.2
- 模块化与依赖重构：autoconfigure 拆分为更细的模块、Starter 体系重写
- REST 能力增强：**API Versioning**、HTTP Service Client / `@HttpExchange` 强化
- 弹性能力内置：重试、并发限制（限流 / “并发控制”）、更好地配合虚拟线程
- 虚拟线程 + GraalVM 原生镜像更加“一等公民”
- 全面采用 **JSpecify** 做空值标注，实现组合式空值安全
- 与 Spring AI、Observability（OpenTelemetry）等新生态紧密对接
- 提供完备的迁移指南，建议老项目先从 3.5.x 升级再迁至 4.0

下面按主题展开。

## 平台与依赖基线升级（“底层依赖升级”）

### Java / JDK

- **最低要求：Java 17**；官方鼓励直接使用最新 LTS（JDK 21 / 25）。
- Spring Framework 7 保持 **JDK 17 为 baseline**，同时“拥抱” JDK 25 的新特性（包括 Project Loom 虚拟线程）。

### Jakarta EE 11

- Spring Boot 4 **全面切换到 Jakarta EE 11 / Servlet 6.1 baseline**，旧的 `javax.*` 注解完全退出舞台，需要改为 `jakarta.*`。
- 由于 Servlet 6.1 兼容性问题，**Undertow 支持被移除**，嵌入式容器推荐 Tomcat 11 或 Jetty 12。

对应你图中的“全面拥抱 JakartaEE，淘汰老版本依赖”。

### 其他重要依赖升级

Spring Boot 4 默认管理了一批主要三方库的新大版本，例如：

- Jackson **3.x**（包名从 `com.fasterxml.jackson` 迁移到 `tools.jackson`）
- Tomcat 11、Jetty 12
- Hibernate ORM 7.1、Hibernate Validator 9
- Kafka 4.x、Elasticsearch 客户端 9.x、Liquibase 5、Flyway 11 等

迁移时需要重点关注 JSON 序列化行为、序列化特性变更等。

## 完整模块化：更细粒度的 Starter 和 Auto-config

Spring Boot 4 最大的结构性变化之一就是**完全模块化**：

- 原来的“大一统” `spring-boot-autoconfigure` / `spring-boot-test-autoconfigure` 被拆成多个**技术特定模块**：
  - 比如 `spring-boot-starter-webmvc` 背后对应的 auto-config 不再全部堆在一个 jar 里，而是拆散成更小、更聚焦的模块。
- 几乎所有技术都有：
  - 一个“main starter”（例如 `spring-boot-starter-graphql`）
  - 一个对应的“test starter”（如 `spring-boot-starter-graphql-test`）
- 为了兼容现有应用，官方保留了所谓的 **“Classic starters”**，你可以先用经典 starter 过渡，再逐步替换为精细模块。

### 好处

- 应用 jar 更小，类路径更干净，IDE 自动补全也不会抛出大量无关配置项。
- 测试依赖更可控，不会因为一个测试场景而拉一堆额外依赖。

## REST 能力增强：API Versioning + HTTP Service Client / `@HttpExchange`

### API 版本管理（API Versioning）

Spring Framework 7 和 Boot 4 引入了一套**官方 REST API 版本控制机制**：

- 支持路径、请求头、查询参数、MediaType 等多种版本策略。
- 版本通过 `@GetMapping` / `@RequestMapping` 上的 `version` 属性声明
  
- 框架还内置了符合 RFC 规范的**弃用（Deprecation）处理**，可以随版本迁移优雅地提示客户端。

```java
@RestController
@RequestMapping("/api")
public class AccountController {

    @GetMapping(value = "/accounts/{id}", version = "1.0")
    public AccountV1 getV1(@PathVariable Long id) { ... }

    @GetMapping(value = "/accounts/{id}", version = "2.0")
    public AccountV2 getV2(@PathVariable Long id) { ... }
}
```

**Spring REST 层面“官方转正了多版本支持”**，不再需要各种自制版本路由方案。

### HTTP Service Client / `@HttpExchange` “转正”

在 Spring 6 中引入的“HTTP 接口客户端”（`@HttpExchange` + 接口代理）在 Spring 7 / Boot 4 进一步强化：

- 提供 **HTTP Interface Groups** 与 **HttpServiceProxyRegistry** 等改进，便于成组管理多个 HTTP 客户端。
- `RestClient` / `WebClient` / 各种 TestClient 都能无缝使用 API Versioning、HTTP Service Client 等新能力。
- 官方路线图中，`RestTemplate` 在 7.1 里将被标记过时，在后续版本中计划移除，推荐统一迁移到 `RestClient` + `@HttpExchange` 风格。

## 弹性能力内置：重试、限流与并发控制

Spring 之前的重试和限流大多来自 **Spring Retry** 与部分 Spring Cloud 组件。现在，**核心弹性特性被搬进 Spring Framework 7 核心本身**

核心注解包括：

- `@Retryable`
    - 声明式重试，支持固定 / 指数退避、抖动等策略。
    - 对响应式方法也有良好支持。
- `@ConcurrencyLimit`
    - 控制某个方法/端点的**并发执行数**，可以实现类似“限流 / 保护下游服务”的效果。
    - 特别适合配合虚拟线程使用：虚拟线程能拉高吞吐，但如果不限制并发数，后端资源可能被压垮。

Boot 4 在自动配置层面对这些特性做了“开箱即用”的支持

## 虚拟线程：与新并发模型更好地协作

[[虚拟线程]]（Virtual Threads）是 JDK 21 引入的新特性，用来大幅降低线程创建和切换的成本，让“每请求一个线程”重新变得现实。多篇社区文章都在用 **Spring Boot 4 + 虚拟线程** 做实测，证明在 I/O 型业务里能够显著提升并发能力和稳定性。

从 Spring 4 生态的角度看：

- Boot 4 继续支持使用虚拟线程处理 HTTP 请求，在配置层面更推荐把虚拟线程与 `@ConcurrencyLimit` 等弹性特性成对使用，避免“线程很多、后端资源被打爆”。
- 由于虚拟线程依赖 JDK 21+，而 Boot 4 的最低要求是 17，你可以：
    - 老项目先升级到 Java 17 + Boot 3.5；
    - 再升级到 Java 21（或 25）+ Boot 4，并开启虚拟线程相关配置进行压测与调优。

图中“深度集成 JDK21 虚拟线程，提高 RPS”，更准确的理解是：**Boot 4 + Spring 7 提供了一整套“虚拟线程 + 弹性控制”的组合能力**，用于在不改业务代码的情况下提升吞吐并保护系统。

## GraalVM Native Image 与 AOT 的强化

Spring 从 3.x 就开始大量投入 **GraalVM Native Image + Spring AOT**，Boot 4 在这条路线上进一步前进

- 要求 **GraalVM Native Image v25+** 才能与 Boot 4 配合使用。
- Spring Framework 7 切换到 **单文件 reachability metadata** 格式，使得 native-image 构建更简单、维护成本更低。
- Spring Data 等组件在 AOT 阶段会把 repository 查询方法直接编译成源代码，和应用一起编译成 native image，进一步减少启动时的反射与解析开销。

在官方和社区基准测试中，原生镜像通常能带来：

- 冷启动时间从秒级降到几十毫秒级
- 内存占用大幅下降（具体比例因应用而异，很多例子中常能看到“减少到原来的 1/3 甚至更少”）

## 全面 JSpecify：空值安全（Null-safety）

Spring Boot 4 另一个非常关键的变化是：**整个 Spring 生态转向 JSpecify 作为统一的空值注解标准**。

- Spring Framework、Spring Data、Spring Security 等核心项目陆续用 `@Nullable`、`@NonNull` 等 JSpecify 注解标注 API。
- Kotlin 2.2 会将这些注解直接映射为 Kotlin 自身的可空/非空类型，从而在编译期就能发现更多潜在 NPE。
- IntelliJ IDEA 2025.3 对这些注解有完整的流分析支持，调用不规范会在 IDE 中直接提示。

官方博客《Null-safe applications with Spring Boot 4》还列出部分暂未完全完成迁移的项目（如 Spring AI、Spring Session 等），后续也会逐步补齐。

对开发者的意义：

- **IDE 和编译器层面就能发现大量潜在空指针问题**，提高整体代码质量。
- 你的自定义代码也可以采用同样的 JSpecify 注解，与 Spring API 保持一致。

## Spring AI 与大模型生态

从官方定位来看，Spring AI 是一个**独立项目**，但与 Boot 4 的目标是紧密耦合的：

- Spring AI 提供一系列 `spring-boot-starter-ai-*`（如 OpenAI、DeepSeek 等）Starter，使得在 Boot 应用中接入 LLM 变成“引入依赖 + 配置 properties 即可”。
- Spring AI 1.1.0-M1 版本在 2025 年 9 月发布，引入了 MCP（Model Context Protocol）等高级特性，并宣布要同时兼容 Boot 3.5 和 Boot 4。

> Boot 4 所在的 Spring 新一代技术栈，以 Spring AI 为代表，把“AI 能力”当成一个一等公民，通过官方 Starter + Auto-config 进入 Boot 应用，而不再是零散地接第三方 SDK。

## 其他值得关注的改动

摘几条对日常开发影响较大的点：

- **Jackson 3 迁移**
    - 包名变更、默认行为调整（属性排序、日期序列化为 ISO-8601 等）。
    - 可以短期内同时保留 Jackson 2 和 3，但长期建议统一到 3。
- **Observability / OpenTelemetry**
    - 新的 `spring-boot-starter-opentelemetry` starter，一站式打包 OTLP 指标和 trace 输出所需依赖。
    - SSL 健康检查中新增 `expiringChains` 字段，提前预警将要过期的证书。
- **测试 & 内存优化**
    - ApplicationContext 在测试中“闲置时会自动休眠”，用于大型测试套件场景减少内存消耗。
- **多因素认证（MFA）** 与 Spring Security 7
    - Spring Security 7 带来了 MFA 支持，Boot 4 自动配置更易用。

## 升级路径建议

官方 Migration Guide 的建议“先 3.5，再 4.0”

**先升级到最新的 `3.5.x`**

- 清理所有 3.x 的 `@Deprecated` 调用。
- 对齐当前依赖版本（尤其是 Spring Cloud、Spring Security 等）。

**评估系统要求**

- JVM 升级到 Java 17（建议直接 21 / 25）。
- 容器升级到 Servlet 6.1 / Jakarta EE 11 兼容版本（Tomcat 11 / Jetty 12）。
- 如需 Native Image，准备 GraalVM v25+。

**切换到 Spring Boot 4.0**

- 根据 Migration Guide 处理：
    - Undertow、旧 Session 模块、Spock 集成等被移除的特性；
    - Starter 依赖调整（采用新的技术特定 starter + test starter）。

**逐步启用新特性**

- 用 API Versioning 梳理外部接口版本。
- 将核心 HTTP 客户端切换到 `RestClient` + `@HttpExchange`。
- 按需启用 `@Retryable` / `@ConcurrencyLimit` 与虚拟线程，并通过压测寻找合适的并发 / 重试策略。
- 有需要时引入 Spring AI Starter，构建大模型相关功能。