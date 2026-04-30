# Spring AI 系统学习笔记：在 Spring Boot 中构建 LLM 应用

> 本文聚焦 Spring AI 本身及其必要相关概念。它不是对历史对话的逐字复述，而是将对话中形成的理解重新整理成一份可独立阅读、可落到代码的系统笔记。内容覆盖 Spring AI 的定位、ChatClient、Prompt / Message / Options、Structured Output、Tool Calling、Advisor、Memory、Streaming、RAG，以及它和 OpenAI API、Ollama、vLLM、LangChain4j、MCP 的边界。

截至 2026-04-29，[Spring AI](https://spring.io/projects/spring-ai) 已进入 1.0.x、1.1.x、2.0.x milestone 多条发布线。Spring 官方在 2026-04-27 发布了 Spring AI `1.0.6`、`1.1.5`、`2.0.0-M5`，并说明这些版本已可从 [Maven Central](https://central.sonatype.com/search?q=org.springframework.ai) 获取。对普通 Spring Boot 3.x 项目而言，学习和落地时优先使用稳定发布线更合适；若使用 Spring Boot 3.5.x，可优先考虑 Spring AI 1.1.x。不同版本的包名、starter 名称、API 细节可能发生变化，因此项目代码应以当前 [官方参考文档](https://docs.spring.io/spring-ai/reference/)和 IDE 自动导入为准。

![Spring AI 标识](http://public.file.lvshuhuai.cn/images\spring-ai-logo.png)

## Spring AI 的位置：它不是模型，而是 Spring Boot 的 AI 应用层

Spring AI 的核心定位可以压缩成一句话：**它是 [Spring Boot](https://spring.io/projects/spring-boot) 体系中用于构建 AI 应用的框架，不是模型本体，也不是模型推理服务。** Spring 官方对 Spring AI 的定义是面向 AI engineering 的应用框架，目标是把 Spring 生态中的可移植性、模块化设计、POJO 编程模型带到 AI 应用开发中。

传统 Spring Boot 项目的主链路通常是：

```text
Controller
  ↓
Service
  ↓
Repository / Mapper
  ↓
Database / Redis / MinIO / 外部接口
```

加入 Spring AI 之后，并不是把这条业务链路推翻，而是在业务系统旁边增加一条模型调用与 AI 能力编排链路：

```text
Controller
  ↓
AI Service
  ↓
ChatClient / Advisor / Tool / VectorStore / Memory / MCP Client
  ↓
OpenAI API / Ollama / vLLM / Azure OpenAI / Anthropic / 其他模型服务
  ↓
LLM / Embedding Model
```

也就是说，Spring AI 的价值不是“让模型更聪明”，而是让 [[笔记/开发/Java路线/Java|Java]] 后端工程能够以熟悉的 Spring 方式接入模型、工具、知识库、结构化输出、流式输出和对话状态。

可以类比为：

```text
Spring MVC      把 HTTP 请求接进 Java 应用
Spring Data     把数据库访问接进 Java 应用
Spring Security 把认证授权接进 Java 应用
Spring AI       把 LLM、RAG、Tool Calling、Memory 接进 Java 应用
```

![Spring AI 集成位置](http://public.file.lvshuhuai.cn/images\spring-ai-integration-diagram.svg)

### Spring AI 和 LLM 的边界

[[大语言模型 LLM]] 是模型本体，例如 GPT、Claude、Qwen、Llama、DeepSeek 等。它们本质上是参数化的神经网络，接收上下文，生成 token。LLM 的基本能力是推理和生成，但它默认不知道你的数据库、排队系统、客户系统、产品手册、银行制度文档，也不能直接访问你的 Java Service。

Spring AI 负责的是应用层组织：

```text
用户问题
  ↓
Spring AI 组织 Prompt、Message、Tool、Memory、RAG 上下文
  ↓
模型服务执行推理
  ↓
Spring AI 接收响应并交还给业务系统
```

所以边界是：

```text
LLM：负责生成与推理。
Spring AI：负责把 LLM 放进 Spring Boot 应用的业务流程中。
```

### Spring AI 和 OpenAI API / Ollama / vLLM 的边界

OpenAI API 是远程模型服务接口。你可以直接用 HTTP 调用它，也可以通过 Spring AI 的 OpenAI starter 调用它。直接调 API 时，你需要自己拼 JSON、处理[[工具调用 Tool Calling]]、解析 response、做 streaming、做错误处理；Spring AI 则把这些封装成 `ChatClient`、`ChatModel`、`EmbeddingModel` 等 Spring 风格抽象。

Ollama 更像本地或服务器上的模型运行工具。它可以拉取并运行开源模型，例如 Llama、Qwen、Mistral 等，并提供模型服务接口。Spring AI 可以把 Ollama 作为下游模型服务使用。边界是：

```text
Ollama：把模型跑起来。
Spring AI：让 Spring Boot 项目调用这个模型服务。
```

[[虚拟大型语言模型 vLLM]] 是高性能 LLM 推理和 serving 框架，重点在 GPU 推理效率、批处理、KV cache、OpenAI-compatible server 等。它解决的是“模型如何部署得快、吞吐高、成本低”的问题。Spring AI 解决的是“业务系统如何调用并组织模型能力”的问题。

```text
Spring Boot
  ↓
Spring AI
  ↓
OpenAI-compatible HTTP API
  ↓
vLLM
  ↓
Qwen / Llama / DeepSeek 等开源模型
```

因此，OpenAI API、Ollama、vLLM 都可以处在 Spring AI 的下游；Spring AI 本身不负责训练模型，也不负责高性能模型推理。

![Spring AI 支持的模型类型](http://public.file.lvshuhuai.cn/images\spring-ai-model-types.jpg)

### Spring AI 和 LangChain4j 的边界

Spring AI 和 [[LangChain4j]] 更接近同一层，都是 Java/[[JVM]] 生态里的 LLM 应用开发框架。差别在于工程风格。

```text
Spring AI    = Spring 官方体系里的 AI 应用框架
LangChain4j = JVM 生态中更框架无关的 LLM 应用开发库
```

Spring AI 的中心抽象通常是：

```text
ChatClient
ChatModel
EmbeddingModel
VectorStore
Advisor
Tool Calling
ChatMemory
MCP Client / Server
```

LangChain4j 的高层抽象中很重要的是 AI Services：声明一个 Java interface，由框架为它生成 LLM 驱动的实现。它更像“把 LLM 能力声明成一个 Java 服务接口”。

对 Spring Boot 业务系统而言，Spring AI 更贴合：它天然使用 Bean、Auto Configuration、Properties、Actuator、Observability 等 Spring 体系能力。LangChain4j 不是不能用于 Spring Boot，而是它的身份更像独立 JVM LLM 应用库。

### Spring AI 和 MCP 的边界

[MCP](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html)，全称 Model Context Protocol，是 AI 应用连接外部工具、资源、Prompt 的协议。[[模型上下文协议 MCP]] 不是模型，也不是[[智能体 Agent]] 框架。它关注的是：不同外部系统如何用统一方式向 AI 应用暴露能力。

Spring AI 内部的 Tool Calling 通常是把当前 Spring Boot 应用里的 Java 方法暴露给模型：

```text
模型请求调用 getQueueInfo("丁香路支行")
  ↓
Spring AI 执行当前应用里的 Java 方法
```

MCP 则是把外部进程、外部服务、外部系统中的工具和资源协议化：

```text
Spring Boot + Spring AI 作为 MCP Client
  ↓
连接 MCP Server
  ↓
读取外部 Resources / 调用外部 Tools / 使用外部 Prompts
```

学习顺序上，应先掌握 Spring AI 的 `@Tool` 和 `.tools(...)`，再理解 MCP。否则容易陷入 MCP Client、Server、stdio、SSE、Streamable HTTP、tools、resources、prompts 等术语，而不知道它们解决什么工程问题。

![Spring AI MCP Client 架构](http://public.file.lvshuhuai.cn/images\spring-ai-mcp-client-architecture.jpg)

## ChatClient 与一次模型调用：Prompt、Message、Options、Response

Spring AI 里最常用的入口是 [`ChatClient`](https://docs.spring.io/spring-ai/reference/api/chatclient.html)。它是与 AI Model 通信的 fluent API，支持同步调用和流式调用。你日常写业务代码时，通常不会直接操作底层 HTTP 请求，而是围绕 `ChatClient` 构造一次模型调用。

一个最小调用长这样：

```java
String answer = chatClient.prompt()
        .system("你是一个严谨的 Java 后端开发助手。")
        .user("解释一下 Spring AI 的 ChatClient")
        .call()
        .content();
```

表面上它是一串链式方法，实际构造的是：

```text
Prompt
├── messages
│   ├── SystemMessage: 你是一个严谨的 Java 后端开发助手。
│   └── UserMessage: 解释一下 Spring AI 的 ChatClient
└── chatOptions
    ├── model
    ├── temperature
    ├── maxTokens
    └── ...
```

### Prompt 不是单纯字符串

在 Spring AI 中，`Prompt` 是一次模型请求的输入容器。它由多条 `Message` 和请求级 `ChatOptions` 组成。中文语境里的“提示词”容易让人误以为 prompt 就是一段字符串，但在框架里，它是结构化对象。

```text
Prompt = Message 列表 + 模型参数
```

常见 Message 角色包括：

```text
system    规定模型行为、回答风格、安全边界、业务规则
user      用户本次输入
assistant 模型历史回复，常用于多轮对话
Tool      工具调用结果，常用于 Tool Calling
```

最基础的分层是：

```java
chatClient.prompt()
        .system("你是银行厅堂 AI 助手。回答要简洁，不要编造政策。")
        .user("客户问：定期存款能不能提前支取？")
        .call()
        .content();
```

不要把所有内容都塞进 `user()`：

```java
// 不推荐
.user("你是银行助手。回答要简洁。用户问题是：定期存款能不能提前支取？")
```

更清楚的写法是：

```java
.system("你是银行助手。回答要简洁，不要编造政策。")
.user("定期存款能不能提前支取？")
```

这种分层在后面接入 Memory、[[检索增强生成 RAG]]、Tool Calling 时很重要。

### 模板参数：不要手写一大坨字符串拼接

真实项目里，[[提示词 Prompt]] 往往包含业务变量。不要用字符串乱拼：

```java
String prompt = "客户类型：" + customerType + "，问题：" + question;
```

更合适的写法是使用模板参数：

```java
public String answerBankQuestion(String question, String customerType) {
    return chatClient.prompt()
            .system("""
                    你是银行厅堂 AI 助手。
                    如果问题涉及具体政策但上下文没有依据，不要编造。
                    """)
            .user(user -> user
                    .text("""
                          客户类型：{customerType}
                          用户问题：{question}
                          """)
                    .param("customerType", customerType)
                    .param("question", question))
            .call()
            .content();
}
```

这类似 SQL 参数绑定：模板结构稳定，变量位置清楚，后续更容易抽取、复用和测试。

### ChatOptions：控制模型生成方式

一次模型调用除了 messages，还有模型参数。常见参数包括：

```text
model          使用哪个模型
temperature    输出随机性
topP           采样范围
maxTokens      最大输出 token 数
stop           停止序列
responseFormat 结构化输出格式
toolChoice     工具选择策略
```

全局默认参数通常放在 `application.yml`：

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o-mini
          temperature: 0.2
```

某次调用也可以覆盖参数：

```java
import org.springframework.ai.openai.OpenAiChatOptions;

public String strictAnswer(String message) {
    return chatClient.prompt()
            .system("你是一个严谨的业务规则解释助手。")
            .user(message)
            .options(OpenAiChatOptions.builder()
                    .temperature(0.1)
                    .build())
            .call()
            .content();
}
```

`temperature` 不是“聪明程度”，而是随机性。业务规则解释、结构化输出、意图识别、RAG 问答通常用低温度，例如 `0.0 ~ 0.2`；创意文案可适当提高。

### 最小 Spring Boot + Spring AI 项目

`pom.xml` 的核心依赖可以这样组织。实际版本应以当前官方 BOM 为准：

```xml
<properties>
    <java.version>21</java.version>
    <spring-ai.version>1.1.5</spring-ai.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>${spring-ai.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-starter-model-openai</artifactId>
    </dependency>
</dependencies>
```

`application.yml`：

```yaml
server:
  port: 8080

spring:
  application:
    name: spring-ai-demo

  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o-mini
          temperature: 0.2
```

Service 层：

```java
package com.example.springaidemo.service;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;

@Service
public class AiChatService {

    private final ChatClient chatClient;

    public AiChatService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public String chat(String message) {
        return chatClient.prompt()
                .system("""
                        你是一个严谨的 Java 后端开发助手。
                        回答要清晰、准确、可执行。
                        """)
                .user(message)
                .call()
                .content();
    }
}
```

Controller 层：

```java
package com.example.springaidemo.controller;

import com.example.springaidemo.service.AiChatService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/ai")
public class ChatController {

    private final AiChatService aiChatService;

    public ChatController(AiChatService aiChatService) {
        this.aiChatService = aiChatService;
    }

    @GetMapping("/chat")
    public String chat(@RequestParam String message) {
        return aiChatService.chat(message);
    }
}
```

这条链路是后面所有能力的基础：

```text
HTTP 请求 → Controller → Service → ChatClient → ChatModel → 模型服务 → LLM
```

## 从文本到程序控制流：Structured Output 与 Tool Calling

普通聊天只返回字符串，适合给人看，不适合让后端继续做稳定判断。AI 后端真正进入业务系统时，必须解决两个问题：

1. 模型如何输出 Java 可解析的结构？
2. 模型如何在需要时调用 Java 业务能力？

前者对应 Structured Output，后者对应 Tool Calling。

### Structured Output：让模型返回 record / DTO

`content()` 只返回自然语言文本：

```java
String result = chatClient.prompt()
        .user("帮我查一下人民路支行现在排队多少人")
        .call()
        .content();
```

如果你要根据结果做业务分支，字符串非常脆弱。更合适的是定义 DTO：

```java
package com.example.springaidemo.dto;

public enum IntentType {
    QUERY_QUEUE,
    QUERY_CUSTOMER,
    EXPLAIN_POLICY,
    OTHER
}
package com.example.springaidemo.dto;

public record IntentResult(
        IntentType intent,
        String branchName,
        String customerId,
        Double confidence,
        String reason
) {
}
```

然后用 `.entity(...)`：

```java
public IntentResult classifyIntent(String message) {
    IntentResult result = chatClient.prompt()
            .system("""
                    你是银行厅堂助手的意图识别模块。

                    intent 只能是：
                    QUERY_QUEUE：查询网点排队情况
                    QUERY_CUSTOMER：查询客户信息
                    EXPLAIN_POLICY：咨询业务规则或政策
                    OTHER：其他情况

                    branchName：用户提到支行或网点时填写，否则为 null。
                    customerId：用户提到客户编号时填写，否则为 null。
                    confidence：0 到 1 之间的小数。
                    reason：用一句中文说明判断依据。

                    不要编造用户没有提供的信息。
                    """)
            .user(message)
            .call()
            .entity(IntentResult.class);

    validateIntentResult(result);
    return result;
}
```

Java 侧校验不能省：

```java
private void validateIntentResult(IntentResult result) {
    if (result == null) {
        throw new IllegalStateException("模型未返回可解析的结构化结果");
    }
    if (result.intent() == null) {
        throw new IllegalStateException("intent 不能为空");
    }
    if (result.confidence() == null || result.confidence() < 0 || result.confidence() > 1) {
        throw new IllegalStateException("confidence 必须在 0 到 1 之间");
    }
}
```

Structured Output 的本质不是“让返回值更好看”，而是让模型输出进入后端程序控制流：

```text
用户自然语言输入
  ↓
模型识别意图与参数
  ↓
Spring AI 映射为 Java record / DTO
  ↓
Java 校验
  ↓
业务分支 / Service 调用
```

![Structured Output 架构](http://public.file.lvshuhuai.cn/images\spring-ai-structured-output-architecture.jpg)

如果返回集合类型，需要使用 `ParameterizedTypeReference`，避免泛型丢失：

```java
List<ProductSuggestion> suggestions = chatClient.prompt()
        .system("根据客户画像给出最多 3 个产品建议。")
        .user(customerProfile)
        .call()
        .entity(new ParameterizedTypeReference<List<ProductSuggestion>>() {});
```

需要注意：Structured Output 是 best effort。即使使用了原生 JSON Schema 能力，也不能把模型输出当作业务真理。凡是会进入数据库、权限判断、交易、审批、删除等流程的字段，都必须再次校验。

### Tool Calling：模型请求调用 Java 方法

[Tool Calling](https://docs.spring.io/spring-ai/reference/api/tools.html) 让模型不只是返回答案，而是在需要实时数据或业务能力时请求调用 Java 方法。Spring AI 的关键写法是 `@Tool` 和 `.tools(...)`。

业务 Service 先保持普通 Spring 写法：

```java
package com.example.springaidemo.service;

import org.springframework.stereotype.Service;

@Service
public class BankBusinessService {

    public String queryQueueInfo(String branchName) {
        return switch (branchName) {
            case "人民路支行" -> "人民路支行当前等待人数：12人；预计等待时间：18分钟。";
            case "丁香路支行" -> "丁香路支行当前等待人数：6人；预计等待时间：9分钟。";
            default -> branchName + " 当前暂无排队数据。";
        };
    }

    public String queryCustomerLevel(String customerId) {
        return switch (customerId) {
            case "10001" -> "客户编号：10001；客户等级：财富客户；风险等级：R2。";
            default -> "未查询到客户编号 " + customerId + " 的客户信息。";
        };
    }
}
```

再写给模型看的 Tool 层：

```java
package com.example.springaidemo.service.tool;

import com.example.springaidemo.service.BankBusinessService;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

@Component
public class BankTools {

    private final BankBusinessService bankBusinessService;

    public BankTools(BankBusinessService bankBusinessService) {
        this.bankBusinessService = bankBusinessService;
    }

    @Tool(description = "查询指定银行网点当前排队人数和预计等待时间。适用于用户询问某个支行、网点、营业厅当前排队情况。")
    public String getQueueInfo(
            @ToolParam(description = "银行网点或支行名称，例如：人民路支行、丁香路支行")
            String branchName
    ) {
        return bankBusinessService.queryQueueInfo(branchName);
    }

    @Tool(description = "根据客户编号查询客户等级和风险等级。适用于用户明确要求查询客户信息。")
    public String getCustomerLevel(
            @ToolParam(description = "客户编号，例如：10001")
            String customerId
    ) {
        return bankBusinessService.queryCustomerLevel(customerId);
    }
}
```

调用时挂载工具：

```java
@Service
public class AiToolService {

    private final ChatClient chatClient;
    private final BankTools bankTools;

    public AiToolService(ChatClient.Builder builder, BankTools bankTools) {
        this.chatClient = builder.build();
        this.bankTools = bankTools;
    }

    public String chatWithTools(String message) {
        return chatClient.prompt()
                .system("""
                        你是银行厅堂 AI 助手。
                        当用户询问排队人数、客户等级等实时业务信息时，应优先调用工具，不要编造。
                        """)
                .user(message)
                .tools(bankTools)
                .call()
                .content();
    }
}
```

模型看到用户问“人民路支行现在排队多少人”时，会根据工具描述选择调用 `getQueueInfo("人民路支行")`。实际执行 Java 方法的是 Spring AI，不是模型直接访问数据库。

```text
模型：我需要调用 getQueueInfo，参数是人民路支行。
Spring AI：执行 Java 方法。
Tool：返回排队数据。
模型：基于工具结果组织自然语言回答。
```

![Spring AI Tool Calling 流程](http://public.file.lvshuhuai.cn/images\spring-ai-tool-calling.jpg)

### Tool Calling 的工程化边界

Tool 是给模型看的语义接口，不是把系统后门交给模型。工程上应遵守几条原则。

参数设计要具体，不要写万能工具：

```java
// 不推荐
@Tool(description = "查询业务信息")
public String query(String type, String value, String mode) { ... }
```

更好的方式是拆成明确工具：

```text
getQueueInfo(branchName)
getCustomerInfo(customerId)
getProductBrief(productName)
prepareReservationDraft(...)
```

只读工具和写操作工具必须分开。查询排队人数、查询产品摘要、查询客户等级属于只读工具，可以谨慎开放。创建预约、发送短信、提交申请、修改客户资料、转账等属于写操作或高风险动作，不应让模型直接自由触发。

写操作更安全的设计是“草稿 + 用户确认”：

```text
用户：帮我预约明天上午十点到丁香路支行办理理财咨询。
  ↓
模型调用 prepareReservationDraft，生成预约草稿。
  ↓
前端展示草稿。
  ↓
用户明确点击确认。
  ↓
普通后端接口 confirmReservation 正式提交。
```

权限不能写在 Prompt 里。Prompt 中可以提醒模型不要越权，但真正的权限校验必须在 Java 侧执行。可以通过 ToolContext 传递当前用户、机构、角色等上下文，然后在 Tool 或 Service 中校验。

工具返回值要脱敏。不要直接把数据库 Entity 返回给模型，应该返回专门设计过的 Tool DTO，只包含回答需要的信息。

```java
public record CustomerInfoResult(
        String customerId,
        String customerLevel,
        String riskLevel,
        String lastVisitDate,
        String message
) {
}
```

不要返回身份证号、手机号、银行卡号、内部标签、风控原始字段、SQL 异常、内部服务 URL、token 等敏感内容。

## Advisor 与 Memory：AI 调用链中的上下文机制

在 Spring AI 中，[Advisor](https://docs.spring.io/spring-ai/reference/api/advisors.html) 是非常关键的一层。它不是 RAG 专用组件，而是 ChatClient 调用链上的通用增强机制。你可以把它理解成 AI 调用链中的中间件。

```text
用户请求
  ↓
ChatClient
  ↓
Advisor 1：安全检查
  ↓
Advisor 2：注入 Memory
  ↓
Advisor 3：检索 RAG 上下文
  ↓
Advisor 4：日志记录
  ↓
ChatModel
  ↓
LLM
```

Spring AI 官方对 Advisors API 的定义是：拦截、修改、增强 AI-driven interactions。它可以封装可复用的生成式 AI 模式，转换发给 LLM 的数据，也可以转换 LLM 返回的数据。

![Spring AI Advisor 调用流程](http://public.file.lvshuhuai.cn/images\spring-ai-advisors-flow.jpg)

### Advisor 解决的问题

没有 Advisor 时，AI Service 容易变成巨大的拼装函数：

```java
public String chat(String message) {
    // 查历史对话
    // 查知识库
    // 拼 prompt
    // 做安全检查
    // 调模型
    // 记录日志
    // 处理响应
    // 返回结果
}
```

Advisor 的作用是把这些可复用增强逻辑拆出来：

```text
调用前：
- 注入历史对话
- 注入知识库上下文
- 改写用户问题
- 添加系统规则
- 做安全检查

调用后：
- 记录日志
- 统计 token
- 处理响应
- 做审计
- 做质量评估
```

最简单的日志 Advisor 可以这样使用：

```java
import org.springframework.ai.chat.client.advisor.SimpleLoggerAdvisor;

public String chatWithLogger(String message) {
    return chatClient.prompt()
            .system("你是一个严谨的 Java 后端助手。")
            .user(message)
            .advisors(new SimpleLoggerAdvisor())
            .call()
            .content();
}
```

Advisor 可以单次挂载：

```java
.advisors(new SimpleLoggerAdvisor())
```

也可以作为默认增强挂到 ChatClient 上：

```java
@Bean
public ChatClient chatClient(ChatClient.Builder builder) {
    return builder
            .defaultSystem("你是银行厅堂 AI 助手。")
            .defaultAdvisors(new SimpleLoggerAdvisor())
            .build();
}
```

工程上，通用规则可以放 `defaultAdvisors`；场景相关的 Memory、RAG、日志、审计、实验性增强更适合在调用时按需挂载。

### Advisor 的顺序

多个 Advisor 的执行顺序很重要。低 order 的 Advisor 请求时先执行，响应时后执行。可以理解为栈式结构：

```text
请求方向：A → B → C → ChatModel
响应方向：ChatModel → C → B → A
```

一个常见顺序是：

```text
1. 安全检查 Advisor
2. Memory Advisor
3. RAG Advisor
4. Logger / Audit Advisor
5. ChatModel
```

这样做的原因是：先判断请求是否允许处理；再注入历史对话，让模型和后续 RAG 理解追问；再检索知识库；最后记录接近最终形态的请求和响应。

### Memory：模型不会自动记住上一轮

LLM 本身是无状态的。所谓多轮对话，不是模型真的记住了你上一轮说过什么，而是应用层把历史消息保存起来，并在下一轮请求时重新放回 Prompt。

Spring AI 的 Memory 主要有三层：

```text
ChatMemoryRepository：底层存储，负责保存和读取消息。
ChatMemory：决定取哪些消息，例如最近 N 条。
Memory Advisor：把这些消息注入本次 ChatClient 调用。
```

它和 Chat History 不同：

```text
Chat History：完整聊天记录，适合审计、回看、客服质检。
Chat Memory：给模型维持上下文用的一部分相关消息。
```

完整历史应该自己建业务表保存；Memory 只负责喂给模型的上下文窗口。

### 最小 Memory 示例

配置 ChatMemory 和带 Memory Advisor 的 ChatClient：

```java
package com.example.springaidemo.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AiMemoryConfig {

    @Bean
    public ChatMemory chatMemory() {
        return MessageWindowChatMemory.builder()
                .maxMessages(20)
                .build();
    }

    @Bean
    public ChatClient memoryChatClient(ChatClient.Builder builder, ChatMemory chatMemory) {
        return builder
                .defaultSystem("""
                        你是银行厅堂 AI 助手。
                        回答时要结合当前会话上下文，不要编造银行政策。
                        """)
                .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
                .build();
    }
}
```

调用时传入 `conversationId`：

```java
@Service
public class MemoryChatService {

    private final ChatClient memoryChatClient;

    public MemoryChatService(ChatClient memoryChatClient) {
        this.memoryChatClient = memoryChatClient;
    }

    public String chat(String conversationId, String message) {
        return memoryChatClient.prompt()
                .user(message)
                .advisors(advisor -> advisor.param(ChatMemory.CONVERSATION_ID, conversationId))
                .call()
                .content();
    }
}
```

`conversationId` 是多轮对话隔离的核心键：

```text
同一个 conversationId：共享上下文。
不同 conversationId：不共享上下文。
```

如果第一轮：

```text
conversationId = conv-001
用户：我的名字叫张三，我想咨询数字化取号。
```

第二轮仍使用 `conv-001`：

```text
用户：我刚才说我叫什么？
```

Memory Advisor 会把第一轮历史消息重新注入 Prompt，模型才能回答“张三”。如果第二轮换成 `conv-002`，模型就不应该知道。

### Memory 的工程边界

Memory 不是业务数据库。预约、订单、审批、客户资料等正式业务状态必须存在业务表中，不能只存在 ChatMemory。

例如：

```text
用户：帮我预约明天上午十点到丁香路支行办理理财咨询。
助手：已生成预约草稿，请确认。
```

这段对话可以存在 Memory 里帮助模型理解“确认”指什么，但预约草稿必须存在 `reservation_draft` 或类似业务表中。

Memory 也不等于长期用户画像。长期偏好、客户标签、用户设置、业务状态应独立建模，需要时通过 Tool、RAG 或 Advisor 注入给模型。

## Streaming：让 AI 回答变成产品级交互

普通调用是完整生成后一次性返回：

```java
String answer = chatClient.prompt()
        .user(message)
        .call()
        .content();
```

流式调用是边生成边返回：

```java
Flux<String> stream = chatClient.prompt()
        .user(message)
        .stream()
        .content();
```

Streaming 不会让模型更聪明，它改变的是响应返回方式。对长回答、RAG、工具调用后总结、多轮问答而言，流式输出会明显改善用户体验。

### 后端最小流式接口

Service：

```java
package com.example.springaidemo.service;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class StreamingChatService {

    private final ChatClient chatClient;

    public StreamingChatService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public Flux<String> streamChat(String message) {
        return chatClient.prompt()
                .system("你是一个严谨的 Java 后端开发助手。")
                .user(message)
                .stream()
                .content();
    }
}
```

Controller：

```java
package com.example.springaidemo.controller;

import com.example.springaidemo.service.StreamingChatService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

@RestController
public class StreamingChatController {

    private final StreamingChatService streamingChatService;

    public StreamingChatController(StreamingChatService streamingChatService) {
        this.streamingChatService = streamingChatService;
    }

    @GetMapping(value = "/ai/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> stream(@RequestParam String message) {
        return streamingChatService.streamChat(message);
    }
}
```

浏览器或 curl 调用：

```powershell
curl -N "http://localhost:8080/ai/stream?message=用五句话解释Spring AI的Streaming"
```

`-N` 用来关闭 curl 输出缓冲，否则可能看起来像一次性返回。

### POST + fetch stream 更适合真实前端

EventSource 简单，但只支持 GET。真实 Vue 项目通常需要 POST JSON，因此更常用 `fetch` + `ReadableStream`：

```javascript
async function sendMessage() {
  const response = await fetch("http://localhost:8080/ai/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      conversationId: "conv-001",
      message: "解释一下 Spring AI 的 Streaming"
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    // 如果后端返回 SSE，需要解析 data: 行
    appendToAnswer(parseSseChunk(chunk));
  }
}

function parseSseChunk(chunk) {
  return chunk
    .split("\n")
    .filter(line => line.startsWith("data:"))
    .map(line => line.replace(/^data:\s?/, ""))
    .filter(line => line !== "[DONE]")
    .join("");
}
```

真实项目里，SSE 解析要处理半包、多事件合并、空行、重连、错误等情况。教学阶段先理解“响应体是一段持续到来的流”即可。

### Streaming + Memory

把 Memory 接入流式接口：

```java
@Service
public class StreamingMemoryChatService {

    private final ChatClient memoryStreamingChatClient;

    public StreamingMemoryChatService(ChatClient memoryStreamingChatClient) {
        this.memoryStreamingChatClient = memoryStreamingChatClient;
    }

    public Flux<String> streamChat(String conversationId, String message) {
        return memoryStreamingChatClient.prompt()
                .user(message)
                .advisors(advisor -> advisor.param(ChatMemory.CONVERSATION_ID, conversationId))
                .stream()
                .content()
                .onErrorResume(ex -> Flux.just("\n\n[生成过程中出现错误，请稍后重试。]"));
    }
}
```

此时系统同时具备：

```text
Memory：多轮上下文。
Streaming：逐段返回体验。
```

需要注意：流式输出完成后才代表本轮回答结束。前端应在 stream done 后再把 `loading` 设为 false。用户取消生成时可以用 `AbortController`。

```javascript
const controller = new AbortController();

const response = await fetch(url, {
  method: "POST",
  body: JSON.stringify(request),
  signal: controller.signal
});

function stopGeneration() {
  controller.abort();
}
```

### Streaming 的工程坑

常见问题包括：

- 代理缓冲：Nginx、网关可能默认缓冲响应，导致后端已流式生成但前端仍一次性看到。需要关闭 buffering。
- POST 与 EventSource 不匹配：EventSource 只能 GET，POST JSON 应用 fetch stream。
- SSE 解析不严谨：不能简单把所有 chunk 原样拼接。
- 工具调用导致前置停顿：Tool Calling 时模型可能先请求工具，工具执行完成后才开始输出最终文本。
- RAG 检索导致前置停顿：RAG 通常先检索，再让模型生成，所以用户会先等待检索过程。
- Memory 与完整聊天记录混用：流式生成的最终文本应另存完整 Chat History，不能只依赖 ChatMemory。

更复杂的产品可以设计事件协议：

```text
start             开始生成
retrieval_start   开始检索知识库
retrieval_end     检索完成
tool_start        开始调用工具
tool_end          工具调用完成
delta             一段文本
done              完成
error             错误
```

这样前端就能展示“正在检索知识库”“正在查询业务系统”等状态，而不是一直空白等待。

## RAG：企业知识库问答的综合形态

[RAG](https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html)，全称 Retrieval-Augmented Generation，检索增强生成。它的核心不是把文档“训练进模型”，而是在每次提问时检索相关文档片段，并把这些片段作为上下文传给模型。

```text
离线阶段：
企业文档 → DocumentReader → TextSplitter → EmbeddingModel → VectorStore

在线阶段：
用户问题 → VectorStore 检索 → 相关片段注入 Prompt → LLM 基于上下文回答
```

RAG 是前面几块能力的综合：

```text
EmbeddingModel：把文本转成向量。
VectorStore：保存和检索向量化文档片段。
Advisor：把检索结果插入 ChatClient 调用链。
Memory：帮助理解多轮追问。
Streaming：让长回答逐段返回。
```

![Spring AI RAG 流程](http://public.file.lvshuhuai.cn/images\spring-ai-rag.jpg)

### 文档入库：读取、切分、向量化、写入

先准备知识库文档，例如 `src/main/resources/docs/digital_queue_policy.txt`：

```text
【数字化取号与线上取号操作说明】

数字化取号包含渠道：Pad、手机银行、小程序、智能终端。

线上取号包含渠道：手机银行、小程序。

优先推荐客户扫描“太阳码”进入小程序取号。原因是：小程序取号同时属于数字化取号和线上取号，并且能够拉动当日到店动户提升。

Pad 取号路径：厅堂服务 → 代客预约/取号模块 → 无信息取号。

手机银行取号路径一：客户使用手机银行扫描“厅堂通”二维码 → 点击立即取号。

手机银行取号路径二：客户打开手机银行首页，下滑找到“云网点”模块 → 预约取号。

小程序取号路径：客户微信扫描“太阳码” → 进入预约取号流程。

小程序取号时，如果客户暂不绑定，可以输入姓名和手机号，接收验证码后继续取号。

小程序取号时，如果客户选择去绑定，需要输入姓名、身份证号、卡号末四位等信息完成绑定。
```

学习阶段可以用 `SimpleVectorStore`：

```java
@Configuration
public class VectorStoreConfig {

    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        return SimpleVectorStore.builder(embeddingModel).build();
    }
}
```

`SimpleVectorStore` 适合学习和演示，不适合生产。生产中应考虑 PGvector、Redis Vector、Qdrant、Milvus、Elasticsearch 等持久化向量库。

文档入库 Service：

```java
@Service
public class DocumentIndexService {

    private final VectorStore vectorStore;

    @Value("classpath:/docs/digital_queue_policy.txt")
    private Resource digitalQueuePolicy;

    public DocumentIndexService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    public void indexDocuments() {
        TextReader reader = new TextReader(digitalQueuePolicy);
        reader.getCustomMetadata().put("source", "digital_queue_policy.txt");
        reader.getCustomMetadata().put("type", "queue_policy");

        List<Document> documents = reader.read();

        TokenTextSplitter splitter = TokenTextSplitter.builder()
                .withChunkSize(800)
                .withMinChunkSizeChars(200)
                .withKeepSeparator(true)
                .build();

        List<Document> chunks = splitter.apply(documents);
        vectorStore.add(chunks);
    }
}
```

启动时执行：

```java
@Configuration
public class DocumentIndexRunnerConfig {

    @Bean
    public ApplicationRunner documentIndexRunner(DocumentIndexService service) {
        return args -> service.indexDocuments();
    }
}
```

这里的重点不是 API 名称，而是流程：长文档必须被读取、切分、向量化、存入 VectorStore。不要把整篇文档原封不动塞给模型。

### 先测试检索，再接模型

RAG 出错时，很多人第一反应是怪模型。实际上应先检查检索是否正确。

```java
@RestController
public class VectorSearchController {

    private final VectorStore vectorStore;

    public VectorSearchController(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    @GetMapping("/ai/vector/search")
    public List<String> search(@RequestParam String query) {
        SearchRequest request = SearchRequest.builder()
                .query(query)
                .topK(3)
                .similarityThreshold(0.5)
                .build();

        return vectorStore.similaritySearch(request)
                .stream()
                .map(Document::getText)
                .toList();
    }
}
```

测试：

```powershell
curl "http://localhost:8080/ai/vector/search?query=数字化取号有哪些渠道"
```

如果没有召回“数字化取号包含渠道：Pad、手机银行、小程序、智能终端”，后面模型回答再好也会不稳。RAG 调试要先看召回结果，再看生成结果。

### QuestionAnswerAdvisor：最小 RAG 问答

```java
@Service
public class RagChatService {

    private final ChatClient chatClient;
    private final VectorStore vectorStore;

    public RagChatService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder.build();
        this.vectorStore = vectorStore;
    }

    public String ask(String question) {
        QuestionAnswerAdvisor ragAdvisor = QuestionAnswerAdvisor.builder(vectorStore)
                .searchRequest(SearchRequest.builder()
                        .topK(4)
                        .similarityThreshold(0.55)
                        .build())
                .build();

        return chatClient.prompt()
                .system("""
                        你是银行厅堂知识库问答助手。
                        必须优先依据检索到的知识库上下文回答。
                        如果上下文没有依据，不要编造。
                        涉及正式政策、产品收益、利率时，以正式系统和制度文件为准。
                        """)
                .user(question)
                .advisors(ragAdvisor)
                .call()
                .content();
    }
}
```

这条链路是：

```text
用户问题
  ↓
QuestionAnswerAdvisor 查询 VectorStore
  ↓
取回相关 Document
  ↓
把 Document 内容追加到 Prompt
  ↓
ChatClient 调用模型
  ↓
模型基于上下文回答
```

### RAG + Memory + Streaming

完整聊天形态通常是：

```text
conversationId
  ↓
Memory Advisor 注入历史对话
  ↓
RAG Advisor 检索知识库
  ↓
ChatClient 调用模型
  ↓
Streaming 输出给前端
```

示例：

```java
@Service
public class FullRagChatService {

    private final ChatClient chatClient;
    private final VectorStore vectorStore;

    public FullRagChatService(ChatClient.Builder builder,
                              ChatMemory chatMemory,
                              VectorStore vectorStore) {
        this.vectorStore = vectorStore;

        this.chatClient = builder
                .defaultSystem("""
                        你是银行厅堂知识库问答助手。
                        结合当前会话上下文理解用户追问。
                        优先依据知识库检索结果回答。
                        如果知识库没有依据，不要编造。
                        """)
                .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
                .build();
    }

    public Flux<String> streamAsk(String conversationId, String question) {
        QuestionAnswerAdvisor ragAdvisor = QuestionAnswerAdvisor.builder(vectorStore)
                .searchRequest(SearchRequest.builder()
                        .topK(4)
                        .similarityThreshold(0.55)
                        .build())
                .build();

        return chatClient.prompt()
                .user(question)
                .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
                .advisors(ragAdvisor)
                .stream()
                .content()
                .onErrorResume(ex -> Flux.just("\n\n[生成失败，请稍后重试。]"));
    }
}
```

这时用户可以先问：

```text
小程序取号时客户不想绑定怎么办？
```

再追问：

```text
那这个算线上取号吗？
```

Memory 负责让模型知道“这个”指的是“小程序取号且暂不绑定”，RAG 负责从知识库中找到“小程序属于线上取号渠道”。

### Metadata、topK、threshold

企业知识库必须重视 metadata。文档入库时应写入：

```text
source：文件名或 URL
type：业务类型，例如 queue_policy / product_policy
version：制度版本
updatedAt：更新时间
businessLine：业务线
visibility：可见范围
```

检索时可以过滤：

```java
SearchRequest.builder()
        .query(question)
        .topK(4)
        .similarityThreshold(0.55)
        .filterExpression("type == 'queue_policy'")
        .build();
```

`topK` 太小可能漏掉关键片段，太大则会塞入无关上下文；`similarityThreshold` 太低会召回噪声，太高可能召不回。学习阶段可以从 `topK=4`、`similarityThreshold=0.5~0.6` 起步，真实项目要用测试集调参。

### RAG 常见错误

- 把 RAG 当成模型训练：RAG 不改变模型参数，只是在请求时注入上下文。
- 文档不切分：整篇文档入库会导致召回粒度粗。
- 不加 metadata：后续无法按业务线、版本、权限过滤。
- 不检查召回结果：回答错时先看 VectorStore 召回了什么。
- 用 SimpleVectorStore 上生产：它只适合学习和演示。
- Prompt 不限制模型：必须要求上下文不足时不要编造。
- 混淆 Memory 和 RAG：Memory 解决多轮语境，RAG 解决外部知识依据。

## 工程化边界：如何把 Spring AI 放进真实后端

前面的能力可以组合成一个真实项目结构：

```text
com.example.project
├── controller
│   ├── ChatController
│   ├── ToolController
│   ├── RagController
│   └── StreamController
├── service
│   ├── AiChatService
│   ├── AiToolService
│   ├── RagChatService
│   ├── DocumentIndexService
│   └── business
│       ├── CustomerService
│       ├── QueueService
│       └── ProductService
├── tool
│   ├── CustomerTools
│   ├── QueueTools
│   └── ProductTools
├── advisor
│   ├── BankRuleAdvisor
│   ├── AuditAdvisor
│   └── SafetyAdvisor
├── config
│   ├── AiModelConfig
│   ├── AiMemoryConfig
│   ├── VectorStoreConfig
│   └── CorsConfig
└── dto
    ├── IntentResult
    ├── ProductSuggestion
    └── RagStreamRequest
```

### 最小可用系统的组合方式

一个能用于实际业务雏形的 Spring AI 应用，至少应该具备：

```text
ChatClient：模型调用入口。
Prompt / Message：清晰组织系统规则和用户输入。
Structured Output：用于意图识别、参数抽取、分类等程序控制流。
Tool Calling：用于实时业务查询或动作草稿。
Advisor：封装通用增强逻辑。
Memory：支持多轮追问。
Streaming：改善前端交互体验。
RAG：基于企业文档回答专业问题。
Audit / Logging：记录模型调用、工具调用、检索命中情况。
```

### 安全原则

在企业系统里，不能把模型当成可信执行者。模型可以参与理解、生成、建议、检索、参数草拟，但最终权限、校验、提交、审计必须由后端业务系统掌控。

需要特别注意：

- Tool 不要直接暴露高风险写操作。
- Tool 参数必须 Java 侧校验。
- Tool 返回必须脱敏。
- 权限校验必须在 Service / Tool 内执行，不能只靠 Prompt。
- RAG 文档要区分权限、版本、来源。
- 日志不要记录敏感明文。
- Memory 不要替代业务状态表。
- Streaming 输出中途失败时，要明确记录状态。

### 判断一个问题该用哪种能力

| 场景 | 合适能力 |
|---|---|
| 普通问答、解释概念 | ChatClient + Prompt |
| 意图识别、分类、参数抽取 | Structured Output |
| 查询实时排队人数、客户等级 | Tool Calling |
| 多轮追问“那这个呢” | Memory + Memory Advisor |
| 长回答逐字输出 | Streaming |
| 根据制度文档、产品手册回答 | RAG + VectorStore + Advisor |
| 外部系统标准化接入 | MCP |
| 通用日志、安全、上下文注入 | Advisor |
