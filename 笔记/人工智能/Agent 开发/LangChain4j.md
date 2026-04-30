# LangChain4j

## LangChain4j 的定位：它不是模型，也不是 vLLM

[LangChain4j](https://docs.langchain4j.dev/) 是 [[JVM]] 生态中的[[大语言模型 LLM]] 应用开发库。它解决的问题不是“模型怎么训练”，也不是“模型怎么部署”，而是：**在 [[笔记/开发/Java路线/Java|Java]] / [Spring Boot](https://spring.io/projects/spring-boot) 项目中，如何把 LLM、记忆、[[工具调用 Tool Calling]]、[[结构化输出 Structured Output]]、[[检索增强生成 RAG]] 等能力组织成可维护的业务组件**。

![LangChain4j 标识](http://public.file.lvshuhuai.cn/images\langchain4j-logo.jpg)

可以先把几个层次区分开：

```text
LLM / MLLM
    真实模型本体，例如 GPT、Qwen、DeepSeek、Gemini、Claude 等。

vLLM / Ollama / OpenAI-compatible Server
    推理服务层，负责加载模型、暴露接口、处理并发、管理显存。

LangChain4j
    Java 应用层抽象，负责把模型调用、工具、记忆、RAG、结构化输出封装成 Java 对象体系。

Spring Boot / Java 业务系统
    Controller、Service、Repository、权限、数据库、业务流程。
```

所以，LangChain4j 不应该和 [vLLM](https://docs.vllm.ai/) 放在同一层比较。[[虚拟大型语言模型 vLLM]] 更像“模型服务器”，LangChain4j 更像“Java 侧的 LLM 应用组织层”。一个典型组合是：用 vLLM 部署 Qwen，并暴露 [[OpenAI-compatible API]]；Java 后端通过 LangChain4j 的 `OpenAiChatModel` 连接这个 API；业务层再通过 `AiServices`、`@Tool`、RAG 等能力构造应用。

![Spring Framework 模块概览](http://public.file.lvshuhuai.cn/images\spring-framework-overview.png)

如果不用 LangChain4j，最原始的写法可能是自己拼 HTTP 请求：

```java
String requestJson = """
{
  "model": "qwen2.5-7b-instruct",
  "messages": [
    {"role": "user", "content": "你好"}
  ]
}
""";

String responseJson = httpClient.post("/v1/chat/completions", requestJson);
String answer = parseJson(responseJson);
```

这个写法能跑，但一旦业务复杂起来，就会暴露很多问题：

- 历史消息要自己维护；
- system / user / assistant / tool 消息要自己拼；
- 工具调用的 JSON 参数要自己解析；
- 结构化输出要自己约束和反序列化；
- RAG 的文档切块、embedding、向量库、检索、注入要自己串；
- 不同模型 provider 的 API 差异要自己适配；
- Spring Boot 中的 Bean 管理、配置、工具注入要自己组织。

LangChain4j 的价值就在这里：它不替代底层模型服务，而是把常见 LLM 应用模式抽象成 Java 开发者熟悉的对象、接口、注解和 Spring Bean。

### 核心对象概览

初学 LangChain4j 时，先不要被所有类名淹没。核心对象可以先压缩为下面几个：

```text
ChatModel
    聊天模型调用抽象。它负责把消息发给模型并拿回回答。

AiServices
    高层 AI Service 代理生成器。它把 Java interface 变成由 LLM 驱动的实现类。

ChatMemory
    当前会话上下文管理器。它决定每次调用模型时带哪些历史消息。

@Tool
    工具方法标注。它把某些 Java 方法暴露给模型，让模型可以请求调用这些方法。

Structured Output
    结构化输出机制。它让 AI Service 方法不只返回 String，也可以返回 boolean、enum、List、record、POJO。

RAG
    检索增强生成。它让模型回答前从知识库检索相关片段，再基于片段回答。

@AiService
    Spring Boot 集成中的声明式 AI Service 注解。它让 interface 自动成为 Spring Bean。
```

这些对象之间的关系可以理解为：

```text
用户请求
    ↓
AI Service interface 方法
    ↓
AiServices / @AiService 代理对象
    ↓
ChatMemory 追加和读取上下文
    ↓
ContentRetriever 检索 RAG 片段
    ↓
ChatModel 调用模型
    ↓
模型可能发起 Tool Calling
    ↓
Java @Tool 方法执行
    ↓
模型整理最终回答
    ↓
结构化输出解析成 Java 返回类型
```

这条链路就是 LangChain4j 应用的主干。

![Augmented LLM 的基础构件](http://public.file.lvshuhuai.cn/images\harness-anthropic-augmented-llm.png)

## ChatModel 与 AiServices：低层模型调用与高层业务接口

LangChain4j 里最容易混淆的一组概念是 `ChatModel` 和 `AiServices`。它们都能导致一次模型调用，但抽象层级不同。

一句话区分：

```text
ChatModel：我直接给模型发消息。
AiServices：我调用一个 Java 业务方法，由框架把方法调用翻译成模型请求。
```

### 裸 ChatModel：直接操作模型调用

最简单的 `ChatModel` 调用如下：

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;

public class RawChatModelDemo {

    public static void main(String[] args) {
        ChatModel model = OpenAiChatModel.builder()
                .baseUrl(System.getenv("OPENAI_BASE_URL"))
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .modelName(System.getenv("OPENAI_MODEL"))
                .build();

        String answer = model.chat("用一句话解释什么是 JVM。");
        System.out.println(answer);
    }
}
```

这很像“模型客户端”。你给模型一句话，模型返回一句话。它适合做连通性测试、简单问答、[[提示词 Prompt]] 临时验证。

如果要更明确地控制 system message 和 user message，可以显式构造消息：

```java
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.openai.OpenAiChatModel;

import java.util.List;

public class RawChatModelWithMessagesDemo {

    public static void main(String[] args) {
        ChatModel model = OpenAiChatModel.builder()
                .baseUrl(System.getenv("OPENAI_BASE_URL"))
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .modelName(System.getenv("OPENAI_MODEL"))
                .build();

        List<ChatMessage> messages = List.of(
                SystemMessage.from("你是一个简洁的 Java 教学助手。"),
                UserMessage.from("用三句话解释 interface 和 abstract class 的区别。")
        );

        ChatResponse response = model.chat(messages);
        System.out.println(response.aiMessage().text());
    }
}
```

这个写法的特点是自由、直接，但所有细节都需要你自己管理：消息顺序、历史上下文、工具调用、结构化解析、RAG 注入等。

### AiServices：把 Java interface 变成 AI 服务

`AiServices` 是 LangChain4j 很有 Java 风格的设计。它的核心思路是：**你声明一个 Java interface，LangChain4j 在运行时生成一个代理实现，这里用到了[[设计模式（12）——代理模式]]。你调用 interface 方法，背后实际触发 LLM 调用。**

最小例子：

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.service.AiServices;

public class AiServiceMinimalDemo {

    interface Assistant {
        String chat(String userMessage);
    }

    public static void main(String[] args) {
        ChatModel model = OpenAiChatModel.builder()
                .baseUrl(System.getenv("OPENAI_BASE_URL"))
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .modelName(System.getenv("OPENAI_MODEL"))
                .build();

        Assistant assistant = AiServices.create(Assistant.class, model);

        String answer = assistant.chat("用一句话解释 LangChain4j 是什么。");
        System.out.println(answer);
    }
}
```

最关键的是这一句：

```java
Assistant assistant = AiServices.create(Assistant.class, model);
```

它的意思不是“调用一个叫 chat 的特殊方法”，而是：

```text
基于 Assistant 这个 Java interface，
使用这个 ChatModel，
生成一个实现了 Assistant 的代理对象。
```

然后你调用：

```java
assistant.chat("...");
```

实际发生的是：

```text
Java 方法调用
    ↓
代理对象拦截方法调用
    ↓
读取方法参数、注解、返回类型
    ↓
构造 ChatMessage / ChatRequest
    ↓
调用 ChatModel
    ↓
解析模型输出
    ↓
返回 Java 方法声明的类型
```

![Prompt chaining 工作流示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-prompt-chaining.png)

### 方法名必须叫 chat 吗

不必须。

`chat` 只是示例里常用的方法名。只要方法属于 AI Service interface，并且签名符合 LangChain4j 的 AI Service 方法规则，它就可以被代理成 LLM 调用。例如：

```java
interface Teacher {
    String explain(String concept);
}
```

或者：

```java
interface Translator {
    String translate(String text);
}
```

甚至方法名写得很差，机制上也能工作：

```java
interface BadNamingAssistant {
    String fuck(String message);
    String shit(String message);
}
```

这两个方法都可以被代理为 LLM 调用。框架不是因为方法名叫 `chat` 才调用模型，而是因为你把整个 interface 交给了 `AiServices`，生成出来的代理会拦截这个 interface 上的方法调用。

不过，工程上不应该这样命名。方法名应该表达业务语义，例如：

```java
interface WritingAssistant {

    String polishAcademicText(String text);

    String reviewJavaCode(String code);

    String summarize(String article);
}
```

真正有价值的写法是把 prompt、参数和返回类型声明清楚：

```java
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

interface TextAssistant {

    @SystemMessage("你是一个专业翻译器。")
    @UserMessage("把下面文本翻译成 {{language}}：{{text}}")
    String translate(@V("text") String text, @V("language") String language);

    @SystemMessage("你是一个摘要助手。")
    @UserMessage("把下面文本总结成 {{n}} 个要点：{{text}}")
    List<String> summarize(@V("text") String text, @V("n") int n);
}
```

这样设计的意义不是省掉一个 HTTP 请求，而是让 AI 能力变成稳定的 Java 服务接口。业务代码可以写成：

```java
String english = textAssistant.translate(chineseText, "English");
List<String> points = textAssistant.summarize(article, 5);
```

而不是到处拼字符串：

```java
model.chat("请把下面文本翻译成英文：" + chineseText);
model.chat("请把下面文章总结成 5 点：" + article);
```

前者是类型化 API，后者是 prompt 脚本。

### 什么时候用 ChatModel，什么时候用 AiServices

`ChatModel` 适合低层控制：

- 测试模型连通性；
- 临时验证 prompt；
- 想直接控制 `ChatMessage` / `ChatRequest`；
- 想查看原始 `ChatResponse`、token usage、finish reason；
- 正在封装自己的上层逻辑。

`AiServices` 适合业务封装：

- 要把 LLM 能力做成 Java service；
- 一个接口里有多个 AI 能力方法；
- 需要 prompt 模板和参数绑定；
- 需要 ChatMemory、Tools、RAG；
- 需要结构化返回，例如 `enum`、`boolean`、`List`、record、POJO；
- 准备接 Spring Boot，让它像普通 service 一样被注入。

可以用数据库框架类比：

```text
ChatModel : AiServices
≈
JDBC : Spring Data Repository
```

JDBC 更底层、更直接；Repository 更高层、更适合业务抽象。`ChatModel` 与 `AiServices` 的关系也是如此。

![Routing 工作流示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-routing.png)

## ChatMemory 与 Tool Calling：状态与行动能力

模型调用默认是无状态的。你第一次告诉模型“我叫 Zhihe”，第二次单独问“我叫什么”，模型并不会自动知道上一轮内容。所谓多轮对话，本质上是应用层每次把必要的历史消息重新发给模型。

工具调用也是类似的：模型不能真的进入 JVM 执行 Java 方法。它只能生成“我想调用某个工具，参数是什么”的请求，真正执行 Java 方法的是 LangChain4j 运行时。

这一节把“[[状态管理 State Management]]”和“行动能力”放在一起讲，因为它们是从普通问答进入[[智能体 Agent]] 应用的关键。

### 裸 ChatModel 的多轮对话

如果直接这样写：

```java
String answer1 = model.chat("你好，我叫 Zhihe。");
String answer2 = model.chat("我叫什么？");
```

第二次请求只包含“我叫什么？”，模型看不到第一轮。正确的裸写法需要自己维护消息列表：

```java
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.SystemMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;

import java.util.ArrayList;
import java.util.List;

public class RawMemoryDemo {

    public static void main(String[] args) {
        ChatModel model = buildModel();

        List<ChatMessage> messages = new ArrayList<>();
        messages.add(SystemMessage.from("你是一个简洁的助手。"));

        messages.add(UserMessage.from("你好，我叫 Zhihe。"));
        ChatResponse response1 = model.chat(messages);
        AiMessage aiMessage1 = response1.aiMessage();
        messages.add(aiMessage1);

        messages.add(UserMessage.from("我叫什么？"));
        ChatResponse response2 = model.chat(messages);
        AiMessage aiMessage2 = response2.aiMessage();
        messages.add(aiMessage2);

        System.out.println(aiMessage2.text());
    }
}
```

这个版本能让模型“看起来记得”，原因不是模型服务器保存了状态，而是你第二次请求时把历史消息又发了一遍。

裸写法的问题在于：

- 消息列表会无限增长；
- 旧消息如何淘汰需要自己处理；
- system message 是否永久保留需要自己处理；
- tool message 不能随便删，否则可能出现孤立工具结果；
- 多用户场景下要自己隔离会话；
- 持久化和完整历史记录也要自己设计。

### ChatMemory 的定位

`ChatMemory` 更准确地说是：**当前会话要提供给 LLM 的上下文消息管理器**。

它不是完整聊天历史表。完整 `history` 是 UI 展示、审计、历史查询需要保存的全部消息；`memory` 是下一次调用模型时要带给模型的上下文窗口。两者应该分开设计。

```text
chat_history 表
    保存完整对话记录：用于 UI、审计、历史查询。

ChatMemory / ChatMemoryStore
    保存当前要喂给模型的上下文窗口：用于下一次 LLM 调用。
```

最简单的 memory 是消息窗口：

```java
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;

ChatMemory memory = MessageWindowChatMemory.withMaxMessages(10);
```

它表示最多保留最近 N 条消息。注意这是“消息条数”，不是“轮数”。一轮对话通常至少有一条 `UserMessage` 和一条 `AiMessage`，如果涉及工具调用，还会有工具相关消息。

低层用法如下：

```java
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.response.ChatResponse;

memory.add(UserMessage.from("你好，我叫 Zhihe。"));
ChatResponse response1 = model.chat(memory.messages());
memory.add(response1.aiMessage());

memory.add(UserMessage.from("我叫什么？"));
ChatResponse response2 = model.chat(memory.messages());
memory.add(response2.aiMessage());
```

这比自己维护 `ArrayList<ChatMessage>` 好，但仍然要手动 add 用户消息和 AI 消息。

### AiServices + ChatMemory

接到 `AiServices` 后，调用会简化很多：

```java
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.service.AiServices;

interface Assistant {
    String chat(String message);
}

ChatMemory memory = MessageWindowChatMemory.withMaxMessages(10);

Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(model)
        .chatMemory(memory)
        .build();

System.out.println(assistant.chat("你好，我叫 Zhihe。"));
System.out.println(assistant.chat("我叫什么？"));
```

背后发生的是：

```text
第一次调用：
    用户输入 → UserMessage → 写入 ChatMemory → 调 ChatModel → AiMessage 写回 ChatMemory

第二次调用：
    新用户输入 → 写入 ChatMemory → 带上历史上下文调 ChatModel → 新回复写回 ChatMemory
```

单个 `ChatMemory` 只适合单用户单会话 demo。真实 Web 项目里必须按用户或会话隔离：

```java
import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.UserMessage;

interface Assistant {
    String chat(@MemoryId String conversationId, @UserMessage String message);
}

Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(model)
        .chatMemoryProvider(memoryId ->
                MessageWindowChatMemory.builder()
                        .id(memoryId)
                        .maxMessages(20)
                        .build())
        .build();
```

`@MemoryId` 标记的参数不会作为用户消息进入 prompt，而是用来区分不同会话。生产项目里，`memoryId` 通常应该是 `conversationId`，而不是简单的 `userId`，因为一个用户可能有多个独立会话。

### `@Tool`：让模型请求调用 Java 方法

Tool Calling 的核心不是“模型执行代码”，而是：

```text
1. 你把某些 Java 方法注册为工具；
2. LangChain4j 把工具名、描述、参数结构发送给模型；
3. 模型判断是否需要调用工具；
4. 模型返回 ToolExecutionRequest；
5. LangChain4j 根据请求调用 Java 方法；
6. 工具结果返回给模型；
7. 模型生成最终回答。
```

最小工具示例：

```java
import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.service.AiServices;

public class ToolCallingDemo {

    interface Assistant {
        String chat(String message);
    }

    static class CalculatorTools {

        @Tool("计算两个整数的和")
        int add(
                @P(name = "a", description = "第一个整数") int a,
                @P(name = "b", description = "第二个整数") int b
        ) {
            return a + b;
        }

        @Tool("计算一个数字的平方根")
        double squareRoot(
                @P(name = "x", description = "需要开平方根的数字") double x
        ) {
            return Math.sqrt(x);
        }
    }

    public static void main(String[] args) {
        Assistant assistant = AiServices.builder(Assistant.class)
                .chatModel(model)
                .tools(new CalculatorTools())
                .build();

        System.out.println(assistant.chat("9 加 16 的和的平方根是多少？"));
    }
}
```

这里有两个必要条件：

- 方法必须用 `@Tool` 标注；
- 工具对象必须通过 `.tools(...)` 或 Spring Bean 显式暴露给 AI Service。

模型不能调用你项目里的任意 Java 方法。它只能看到你暴露给它的工具说明。

### `@P` 参数说明的重要性

工具设计的质量，主要取决于工具名、工具描述、参数名、参数描述。不要写这种工具：

```java
@Tool
String handle(String x) {
    return "...";
}
```

模型很难判断 `handle` 是干什么的，`x` 应该传什么。

更好的写法是：

```java
@Tool("根据电影名称搜索本地媒体库中的电影信息")
String searchMovie(
        @P(name = "movieName", description = "电影名称，可以是中文名、英文名或别名")
        String movieName
) {
    return movieService.search(movieName);
}
```

这样模型看到的是一个明确的工具规格，而不是模糊的 Java 方法名。

### 工具调用调试：`Result<T>`

普通方法返回 `String` 时，你只能看到最终回答。如果想看模型到底调用了什么工具，可以返回 `Result<String>`：

```java
import dev.langchain4j.service.Result;
import dev.langchain4j.service.tool.ToolExecution;

interface Assistant {
    Result<String> chat(String message);
}

Result<String> result = assistant.chat("9 加 16 的和的平方根是多少？");

System.out.println("最终回答：" + result.content());

for (ToolExecution execution : result.toolExecutions()) {
    System.out.println("请求：" + execution.request());
    System.out.println("结果：" + execution.result());
    System.out.println("原始对象：" + execution.resultObject());
}
```

调试工具调用时，不要只看最终自然语言回答。工具是否被调用、调用参数是否正确、工具结果是否正确，通常要看 `toolExecutions()`。

### 工具安全边界

工具调用很强，也很危险。只读工具和计算工具相对安全，例如查天气、查库存、查资料、计算数值。但写操作工具必须谨慎，例如：

- 删除用户；
- 发邮件；
- 修改数据库；
- 支付；
- 执行 shell 命令；
- 改权限；
- 调用外部系统产生副作用。

高风险工具至少要有：

1. 权限校验；
2. 参数校验；
3. 二次确认；
4. 审计日志；
5. 幂等设计；
6. 失败回滚或补偿机制。

更稳的模式是两阶段：模型只能生成“待确认操作”，真正执行由传统后端在用户确认后完成。

## 结构化输出：让 LLM 输出 Java 类型，而不是一段文本

`String` 是最自由的返回类型，但也是最不稳定的业务返回类型。如果后续代码要做判断、分支、查询、入库，就不应该依赖自然语言字符串。

结构化输出的核心是：**AI Service 方法可以声明返回 `boolean`、`enum`、`List<T>`、record、POJO，LangChain4j 会尝试让模型按对应结构输出，并把结果解析为 Java 类型。**

### `String` 的局限

例如：

```java
interface Assistant {
    String chat(String message);
}

String answer = assistant.chat("判断这句话是不是正面情绪：这部电影太好看了");
```

模型可能返回：

```text
是的，这是正面情绪。
```

也可能返回：

```text
正面
```

还可能返回：

```text
这句话表达了积极评价，因此属于正面情绪。
```

人能看懂，程序不好处理。不要让业务代码写成：

```java
if (answer.contains("正面") || answer.contains("积极")) {
    // ...
}
```

这是字符串解析地狱。

### `boolean`：二分类

如果任务就是是/否判断，可以返回 `boolean`：

```java
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

interface TextClassifier {

    @UserMessage("""
            判断下面评论是否为正面情绪。
            只根据文本含义判断。

            评论：{{text}}
            """)
    boolean isPositive(@V("text") String text);
}
```

调用方拿到的是 Java 布尔值：

```java
boolean positive = classifier.isPositive("这部电影太好看了，我还想再看一遍。");
```

如果任务有三类以上，不要硬塞成 `boolean`。

### `enum`：固定类别分类

多分类任务适合 enum：

```java
enum Sentiment {
    POSITIVE,
    NEUTRAL,
    NEGATIVE
}

interface SentimentAnalyzer {

    @UserMessage("""
            判断下面评论的情绪。

            评论：{{text}}
            """)
    Sentiment analyze(@V("text") String text);
}
```

这样业务代码可以稳定分支：

```java
Sentiment sentiment = analyzer.analyze("剧情一般，但演员表现还可以。");

switch (sentiment) {
    case POSITIVE -> handlePositive();
    case NEUTRAL -> handleNeutral();
    case NEGATIVE -> handleNegative();
}
```

固定类别任务优先用 `enum`，不要返回 `String` 再解析。

### `List<T>`：多个结果

如果需要多个要点、标题、关键词，可以返回列表：

```java
import java.util.List;

interface OutlineGenerator {

    @UserMessage("""
            请为下面主题生成 {{n}} 个文章大纲要点。

            主题：{{topic}}
            """)
    List<String> generateOutline(@V("topic") String topic, @V("n") int n);
}
```

调用：

```java
List<String> outline = generator.generateOutline("LangChain4j 的 Tool Calling", 5);
outline.forEach(System.out::println);
```

复杂场景更推荐用一个 record 包起来，而不是直接返回顶层列表，因为后续可能要加元数据、说明、置信度、警告信息。

### `record` / POJO：业务系统最常用

例如从用户自然语言中抽取电影搜索条件：

```java
import java.util.List;

record MovieQuery(
        String keyword,
        Integer afterYear,
        Quality quality,
        Boolean requireBluRay,
        List<String> genres
) {}

enum Quality {
    ANY,
    HD_1080P,
    UHD_4K
}

interface MovieQueryExtractor {

    @SystemMessage("""
            你是一个电影搜索参数抽取器。
            你只负责从用户输入中抽取搜索条件，不负责编造电影资源。
            没有提到的信息保持为空，或者使用最保守的默认值。
            """)
    @UserMessage("""
            从下面用户需求中抽取电影搜索条件：

            {{text}}
            """)
    MovieQuery extract(@V("text") String text);
}
```

调用：

```java
MovieQuery query = extractor.extract("帮我找 2016 年之后的 4K 科幻电影，最好是蓝光的。");

System.out.println(query.afterYear());      // 2016
System.out.println(query.quality());        // UHD_4K
System.out.println(query.requireBluRay());  // true
System.out.println(query.genres());         // [科幻]
```

然后由 Java 执行确定性业务逻辑：

```java
List<Movie> movies = movieRepository.search(
        query.keyword(),
        query.afterYear(),
        query.quality(),
        query.requireBluRay(),
        query.genres()
);
```

这就是结构化输出最好的位置：

```text
LLM 负责理解自然语言并抽取结构；
Java 负责确定性查询、校验、权限和业务执行。
```

### `Optional` 字段与 primitive 陷阱

结构化输出中，不要轻易用 primitive 类型表达可空字段：

```java
record BadMovieQuery(
        int year,
        boolean require4K
) {}
```

如果用户没提年份，`int year` 可能变成 `0`；如果用户没提是否 4K，`boolean require4K` 可能变成 `false`。这会让你无法区分“未提及”和“明确为 false”。

更推荐：

```java
record MovieQuery(
        Integer year,
        Boolean require4K
) {}
```

必要字段可以通过 Jackson 注解表达：

```java
import com.fasterxml.jackson.annotation.JsonProperty;

record Person(
        @JsonProperty(required = true)
        String name,
        String surname
) {}
```

但 required 要慎用。如果输入资料本身不完整，强制 required 可能诱导模型编造字段。

### `Result<T>`：结果加元数据

结构化结果也可以包在 `Result<T>` 里：

```java
import dev.langchain4j.service.Result;

interface MovieQueryExtractor {
    Result<MovieQuery> extract(String text);
}

Result<MovieQuery> result = extractor.extract("帮我找 2016 年之后的 4K 科幻电影。");
MovieQuery query = result.content();

System.out.println(result.tokenUsage());
System.out.println(result.finishReason());
System.out.println(result.toolExecutions());
```

`T` 只关心最终业务对象；`Result<T>` 同时保留调用元数据，适合调试、审计、观察 token 消耗、工具调用和 RAG 来源。

### 结构化输出的边界

结构化输出不是 100% 正确。它只是比自然语言文本更可控。业务系统仍然要做 Java 层校验：

```java
MovieQuery query = extractor.extract(input);

if (query.afterYear() != null && query.afterYear() < 1888) {
    throw new IllegalArgumentException("电影年份不合法");
}
```

不要把模型输出直接当作可信事实。尤其是金额、权限、医学、法律、数据库写操作，都必须经过确定性校验。

## RAG：从文档到知识问答闭环

[RAG](https://docs.langchain4j.dev/tutorials/rag) 是 Retrieval-Augmented Generation，检索增强生成。它不是 fine-tuning，也不是让模型永久学会你的资料，而是在每次回答前，从外部知识库检索相关片段，再把片段临时注入给模型。

最小流程是：

```text
原始文档
    ↓
切成 TextSegment
    ↓
EmbeddingModel 转成向量
    ↓
存入 EmbeddingStore

用户提问
    ↓
EmbeddingModel 把问题转成向量
    ↓
EmbeddingStore 相似度检索
    ↓
取回相关 TextSegment
    ↓
注入 prompt
    ↓
ChatModel 基于上下文回答
```

![RAG 文档入库流程](http://public.file.lvshuhuai.cn/images\langchain4j-rag-ingestion.png)

![RAG 检索生成流程](http://public.file.lvshuhuai.cn/images\langchain4j-rag-retrieval.png)

### 核心对象

RAG 最小闭环先认这几个对象：

```text
Document
    一整篇文档。

TextSegment
    文档切出来的小片段。

EmbeddingModel
    把文本转成向量的模型。

EmbeddingStore
    向量存储，也就是向量库。

EmbeddingStoreIngestor
    负责把 Document 切块、向量化、写入 EmbeddingStore。

ContentRetriever
    用户提问时，从 EmbeddingStore 中检索相关内容。
```

它们的关系：

```text
入库阶段：
    Document → TextSegment → EmbeddingModel → EmbeddingStore

检索阶段：
    用户问题 → EmbeddingModel → EmbeddingStoreContentRetriever → 相关 TextSegment

生成阶段：
    用户问题 + 检索片段 → ChatModel → Answer
```

### 为什么要切块

假设有一份很长的业务手册，用户只问“数字化取号有哪些渠道”。你不应该把整份手册都塞给模型。原因包括：

- 上下文窗口有限；
- token 成本和延迟更高；
- 无关内容会干扰回答；
- 整篇长文压成一个向量会降低检索质量；
- 难以追踪回答到底依据哪部分内容。

切块的目的不是把文档切得越碎越好，而是在语义完整性和检索精度之间取平衡。常见做法是：每块固定字数或 token 数，并设置 overlap，避免切断关键上下文。

### 最小 RAG 示例

下面用内存向量库做一个教学版知识库。生产环境不要使用 `InMemoryEmbeddingStore` 保存正式数据。

```java
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

import java.util.List;

public class MinimalRagDemo {

    interface Assistant {

        @SystemMessage("""
                你是一个严谨的知识库问答助手。
                你必须优先依据检索到的资料回答。
                如果资料中没有答案，就明确说：资料中没有提供相关信息。
                不要编造资料外的事实。
                """)
        String chat(String userMessage);
    }

    public static void main(String[] args) {
        ChatModel chatModel = OpenAiChatModel.builder()
                .baseUrl(System.getenv("OPENAI_BASE_URL"))
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .modelName(System.getenv("OPENAI_MODEL"))
                .build();

        EmbeddingModel embeddingModel = OpenAiEmbeddingModel.builder()
                .baseUrl(System.getenv("OPENAI_BASE_URL"))
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .modelName(System.getenv("OPENAI_EMBEDDING_MODEL"))
                .build();

        List<Document> documents = List.of(
                Document.from("""
                        数字化取号包含渠道：pad、手机银行、小程序、智能终端。
                        线上取号包含渠道：手机银行、小程序。
                        优先推荐客户扫“太阳码”，通过小程序取号。
                        小程序取号同时属于数字化取号和线上取号，并能拉动当日到店动户提升。
                        """),
                Document.from("""
                        Pad 取号路径：厅堂服务 → 代客预约/取号模块 → 无信息取号。
                        手机银行取号路径一：客户手机银行扫描“厅堂通”二维码 → 立即取号。
                        手机银行取号路径二：客户手机银行首页下滑，找到“云网点”模块 → 预约取号。
                        """),
                Document.from("""
                        小程序取号路径：客户微信扫描“太阳码” → 预约取号。
                        暂不绑定：输入姓名手机号，接收验证码。
                        去绑定：输入姓名、身份证号、卡号末四位等信息。
                        """)
        );

        InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();

        EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
                .documentSplitter(DocumentSplitters.recursive(300, 30))
                .embeddingModel(embeddingModel)
                .embeddingStore(embeddingStore)
                .build();

        ingestor.ingest(documents);

        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(3)
                .minScore(0.6)
                .build();

        Assistant assistant = AiServices.builder(Assistant.class)
                .chatModel(chatModel)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .contentRetriever(contentRetriever)
                .build();

        System.out.println(assistant.chat("数字化取号有哪些渠道？"));
        System.out.println(assistant.chat("为什么优先推荐太阳码？"));
        System.out.println(assistant.chat("这个资料里有没有提到贷款利率？"));
    }
}
```

这段代码分三部分：

1. 入库阶段：`EmbeddingStoreIngestor` 把 `Document` 切块、向量化、写入 `EmbeddingStore`；
2. 检索阶段：`EmbeddingStoreContentRetriever` 根据用户问题检索相关片段；
3. 问答阶段：`AiServices` 把 `ContentRetriever` 接入模型调用，让回答基于检索资料。

### RAG 和 ChatMemory 的区别

`ChatMemory` 与 RAG 解决的是不同问题：

```text
ChatMemory
    保存对话上下文。解决“上一轮说过什么”的问题。

RAG
    检索外部知识。解决“模型不知道你的私有资料”的问题。
```

例如：

```text
用户第一轮：数字化取号有哪些渠道？
RAG 检索业务资料。
模型回答：pad、手机银行、小程序、智能终端。

用户第二轮：哪些属于线上取号？
ChatMemory 让模型知道“哪些”指上一轮的渠道。
RAG 再检索线上取号资料。
模型回答：手机银行、小程序。
```

所以完整结构是：

```text
ChatMemory 提供对话上下文；
ContentRetriever 提供知识库证据；
ChatModel 负责最终生成；
AiServices 把它们串起来。
```

![Advanced RAG 流程](http://public.file.lvshuhuai.cn/images\langchain4j-advanced-rag.png)

### maxResults 与 minScore

```java
.maxResults(3)
.minScore(0.6)
```

`maxResults` 控制最多取几个片段。太少可能漏资料，太多会引入噪声和成本。

`minScore` 控制最低相似度。太高可能检索不到，太低可能引入无关内容。

这些参数没有固定最优值。真实项目要准备一批标准问题，观察检索命中率、回答质量和误答率。

### RAG 常见坑

常见问题不一定是模型问题，而是检索问题：

- 文档切块过大或过小；
- embedding 模型不适合中文或业务领域；
- `topK` / `maxResults` 设置不合理；
- `minScore` 太高或太低；
- 文档本身没有答案；
- 用户问题太模糊，需要 query rewrite；
- 没有 metadata filter，导致跨用户或跨权限检索；
- 没有展示来源，难以审计。

教学版使用 `InMemoryEmbeddingStore` 可以，但生产中应该使用持久化向量库，例如 pgvector、Milvus、Qdrant、Elasticsearch / OpenSearch 等。

## Spring Boot 集成：把能力串成可交互服务

前面的例子都是 `main()` 控制台程序。真正项目里要把它变成 Spring Boot 服务。Spring Boot 集成的本质是：**把 ChatModel、EmbeddingModel、ChatMemoryProvider、ContentRetriever、@Tool 方法、AI Service interface 都交给 Spring 容器管理。**

### 控制台写法与 Spring Boot 写法

控制台里通常手动创建：

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .chatMemoryProvider(memoryProvider)
        .contentRetriever(contentRetriever)
        .tools(new BusinessTools())
        .build();
```

Spring Boot 里更希望：

```java
@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final Assistant assistant;

    public ChatController(Assistant assistant) {
        this.assistant = assistant;
    }

    @PostMapping
    public ChatResponse chat(@RequestBody ChatRequest request) {
        return new ChatResponse(
                assistant.chat(request.conversationId(), request.message())
        );
    }
}
```

`Assistant` 没有手写实现类，但它能被注入，因为 `@AiService` 会让 LangChain4j 的 Spring Boot starter 自动生成代理实现并注册成 Spring Bean。

### Maven 依赖

示例依赖如下，版本请以实际官方文档和 [Maven Central](https://central.sonatype.com/search?q=dev.langchain4j) 为准：

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-spring-boot-starter</artifactId>
        <version>1.13.1-beta23</version>
    </dependency>

    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-open-ai</artifactId>
        <version>1.13.1</version>
    </dependency>
</dependencies>
```

也可以使用 provider-specific Spring Boot starter，通过 `application.yml` 自动配置模型 Bean。教学阶段手写 `@Bean` 更容易看清对象关系。

### application.yml

```yaml
server:
  port: 8080

llm:
  base-url: ${OPENAI_BASE_URL:https://api.openai.com/v1}
  api-key: ${OPENAI_API_KEY}
  chat-model: ${OPENAI_MODEL:gpt-4o-mini}
  embedding-model: ${OPENAI_EMBEDDING_MODEL:text-embedding-3-small}
```

如果你接本地 OpenAI-compatible 服务，比如 vLLM：

```powershell
$env:OPENAI_BASE_URL="http://127.0.0.1:8000/v1"
$env:OPENAI_API_KEY="EMPTY"
$env:OPENAI_MODEL="你的 chat 模型名"
$env:OPENAI_EMBEDDING_MODEL="你的 embedding 模型名"
```

注意：很多本地推理服务只提供 chat/completions，不一定提供 embeddings。RAG 必须有 embedding 模型。

### AI Service interface

```java
package com.example.demo.ai;

import dev.langchain4j.service.MemoryId;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.spring.AiService;

@AiService
public interface Assistant {

    @SystemMessage("""
            你是一个严谨的业务知识库助手。
            回答时优先依据检索到的知识库资料。
            如果资料中没有答案，就明确说“资料中没有提供相关信息”。
            你可以在需要时调用工具，但不要编造工具结果。
            """)
    String chat(@MemoryId String conversationId, @UserMessage String message);
}
```

`@MemoryId` 用于区分不同会话；`@UserMessage` 表示该参数是用户消息；`@SystemMessage` 定义 AI Service 的系统规则。

### 配置 ChatModel、EmbeddingModel、Memory、RAG

```java
package com.example.demo.config;

import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.memory.chat.ChatMemoryProvider;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class LangChain4jConfig {

    @Bean
    ChatModel chatModel(
            @Value("${llm.base-url}") String baseUrl,
            @Value("${llm.api-key}") String apiKey,
            @Value("${llm.chat-model}") String modelName
    ) {
        return OpenAiChatModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName(modelName)
                .build();
    }

    @Bean
    EmbeddingModel embeddingModel(
            @Value("${llm.base-url}") String baseUrl,
            @Value("${llm.api-key}") String apiKey,
            @Value("${llm.embedding-model}") String modelName
    ) {
        return OpenAiEmbeddingModel.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .modelName(modelName)
                .build();
    }

    @Bean
    ChatMemoryProvider chatMemoryProvider() {
        return memoryId -> MessageWindowChatMemory.builder()
                .id(memoryId)
                .maxMessages(20)
                .build();
    }

    @Bean
    ContentRetriever contentRetriever(EmbeddingModel embeddingModel) {
        InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();

        List<Document> documents = List.of(
                Document.from("""
                        数字化取号包含渠道：pad、手机银行、小程序、智能终端。
                        线上取号包含渠道：手机银行、小程序。
                        优先推荐客户扫“太阳码”，通过小程序取号。
                        小程序取号同时属于数字化取号和线上取号，并能拉动当日到店动户提升。
                        """),
                Document.from("""
                        Pad 取号路径：厅堂服务 → 代客预约/取号模块 → 无信息取号。
                        手机银行取号路径一：客户手机银行扫描“厅堂通”二维码 → 立即取号。
                        手机银行取号路径二：客户手机银行首页下滑，找到“云网点”模块 → 预约取号。
                        """)
        );

        EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
                .documentSplitter(DocumentSplitters.recursive(300, 30))
                .embeddingModel(embeddingModel)
                .embeddingStore(embeddingStore)
                .build();

        ingestor.ingest(documents);

        return EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .maxResults(3)
                .minScore(0.6)
                .build();
    }
}
```

教学版把文档硬编码在 `@Bean` 里，只是为了演示闭环。生产项目里，文档导入应该是独立流程：上传文件、解析、切块、embedding、写入向量库、记录文档版本、处理权限和租户隔离。

### 工具组件

Spring Boot 集成中，工具可以写成普通 Spring Bean：

```java
package com.example.demo.tool;

import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;
import org.springframework.stereotype.Component;

import java.time.LocalDate;

@Component
public class BusinessTools {

    @Tool("获取今天的日期")
    public String today() {
        return LocalDate.now().toString();
    }

    @Tool("计算两个整数的和")
    public int add(
            @P(name = "a", description = "第一个整数") int a,
            @P(name = "b", description = "第二个整数") int b
    ) {
        return a + b;
    }

    @Tool("根据取号渠道名称判断是否属于线上取号")
    public boolean isOnlineTicketChannel(
            @P(name = "channel", description = "取号渠道名称，例如手机银行、小程序、pad、智能终端")
            String channel
    ) {
        return "手机银行".equals(channel) || "小程序".equals(channel);
    }
}
```

在 Spring Boot 集成中，只要工具类是 Spring Bean，且方法上有 `@Tool`，AI Service 就可以自动使用这些工具。复杂项目中，如果有多个工具 Bean 或多个 AI Service，建议显式装配，避免框架猜错。

### Controller 与 DTO

```java
package com.example.demo.dto;

public record ChatRequest(
        String conversationId,
        String message
) {}
package com.example.demo.dto;

public record ChatResponse(
        String answer
) {}
package com.example.demo.controller;

import com.example.demo.ai.Assistant;
import com.example.demo.dto.ChatRequest;
import com.example.demo.dto.ChatResponse;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final Assistant assistant;

    public ChatController(Assistant assistant) {
        this.assistant = assistant;
    }

    @PostMapping
    public ChatResponse chat(@RequestBody ChatRequest request) {
        if (request.conversationId() == null || request.conversationId().isBlank()) {
            throw new IllegalArgumentException("conversationId 不能为空");
        }
        if (request.message() == null || request.message().isBlank()) {
            throw new IllegalArgumentException("message 不能为空");
        }

        String answer = assistant.chat(request.conversationId(), request.message());
        return new ChatResponse(answer);
    }
}
```

测试：

```powershell
curl.exe -X POST "http://localhost:8080/api/chat" `
  -H "Content-Type: application/json" `
  -d "{\"conversationId\":\"conv-001\",\"message\":\"数字化取号有哪些渠道？\"}"
```

继续同一个会话：

```powershell
curl.exe -X POST "http://localhost:8080/api/chat" `
  -H "Content-Type: application/json" `
  -d "{\"conversationId\":\"conv-001\",\"message\":\"哪些属于线上取号？\"}"
```

这时完整调用链是：

```text
HTTP POST /api/chat
    ↓
ChatController
    ↓
Assistant.chat(conversationId, message)
    ↓
@AiService 代理对象
    ↓
ChatMemoryProvider 根据 conversationId 找 memory
    ↓
ContentRetriever 检索知识库
    ↓
ChatModel 生成回答或请求调用工具
    ↓
@Tool 方法执行
    ↓
模型整理最终回答
    ↓
Controller 返回 JSON
```

## 工程化判断：从 demo 到可维护系统

LangChain4j 的核心不是“写几个能跑的 demo”，而是把 LLM 能力放进 Java 工程体系。真实项目里需要格外注意以下设计边界。

### 不要把所有东西都写成 assistant.chat

`assistant.chat(String)` 适合通用对话，但不适合所有业务。更好的写法是按业务能力定义 interface：

```java
interface MovieAiService {

    MovieQuery extractMovieQuery(String userInput);

    List<String> generateSearchKeywords(String title);

    String summarizeMovieDescription(String description);
}
```

这样 AI 能力就像普通 Java 服务一样，有清晰的方法名、参数和返回类型。

### LLM 负责理解，Java 负责执行

比较稳的架构是：

```text
用户自然语言
    ↓
LLM 抽取结构化参数
    ↓
Java 校验参数
    ↓
Java 查询数据库 / 调业务服务
    ↓
必要时再让 LLM 总结结果
```

不要让 LLM 一步包办所有事情。尤其是数据库查询、权限判断、付款、删除、外部 API 调用，都应该由 Java 确定性逻辑控制。

### Memory 与 History 必须分离

`ChatMemory` 是喂给模型的上下文窗口，不是完整聊天记录。真实系统至少应有两套机制：

```text
chat_history
    保存完整消息，供 UI 展示、审计、搜索、回放。

chat_memory
    保存当前模型上下文窗口，可能被裁剪、总结、替换。
```

如果只依赖 `ChatMemory`，旧消息被淘汰后就没法完整恢复历史。

### RAG 要做权限和来源管理

生产 RAG 不只是“把文档塞进向量库”。至少要考虑：

- 文档所属用户、组织、租户；
- 文档版本；
- 片段来源位置；
- metadata filter；
- 检索来源展示；
- 文档删除后的向量清理；
- embedding 模型升级后的重建索引；
- 敏感内容过滤。

如果没有权限过滤，RAG 很容易出现跨用户、跨租户的信息泄露。

### Tools 要分级管理

工具可以分成：

```text
只读工具
    查询天气、查询库存、查询用户资料、查询订单状态。

计算工具
    数学计算、格式转换、统计分析。

写操作工具
    删除、支付、发邮件、改数据库、执行命令。
```

只读和计算工具适合自动调用；写操作工具必须经过权限、确认、审计和幂等控制。不要把高危工具无脑暴露给模型。

### 结构化输出要做校验

即使用了 JSON Schema 或 POJO 返回值，也不能完全相信模型。业务层仍然要校验：

- 数字范围是否合法；
- 必填字段是否存在；
- enum 是否符合预期；
- ID 是否属于当前用户；
- 日期是否合理；
- 金额是否超过权限；
- 是否存在 prompt injection 导致的异常指令。

结构化输出提高了可解析性，不等于事实正确性。

### 最小可维护架构

一个较稳的 Spring Boot + LangChain4j 项目，可以按下面结构组织：

```text
controller
    HTTP 接口，处理请求和响应 DTO。

ai
    @AiService interface，定义 AI 能力边界。

config
    ChatModel、EmbeddingModel、ChatMemoryProvider、ContentRetriever 等 Bean。

tool
    @Tool 工具类，封装只读查询、计算、可控业务动作。

rag
    文档解析、切块、embedding、向量库写入和检索配置。

service
    普通业务服务，负责确定性逻辑。

repository
    数据库访问。

dto / model
    请求、响应、结构化输出 record / POJO。
```

最终目标不是让 LangChain4j 接管你的业务系统，而是让它成为业务系统中的一组 AI 能力组件。
