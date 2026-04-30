# [OpenAI-compatible API](https://platform.openai.com/docs/api-reference)

> 本文只讨论 **OpenAI-compatible API** 本身：它的接口形态、请求/响应结构、流式格式、embedding、tool calls，以及在 [[笔记/开发/Java路线/Java|Java]] 客户端中如何稳定解析和封装。

## OpenAI-compatible API 的核心边界

OpenAI-compatible API 指的是：某个模型服务虽然不一定由 OpenAI 提供，但它尽量按照 OpenAI API 的 HTTP 路径、请求字段和响应字段来实现接口。这样客户端代码可以复用 OpenAI 风格的调用方式，只需要更换 `base_url`、`api_key` 和 `model`，就能连接不同的模型服务。

![vLLM](http://public.file.lvshuhuai.cn/images\openai-compatible-api-vllm-logo.png)

它的本质不是“只能调用 OpenAI”，而是一种事实上的模型服务接口约定。

```text
业务代码 / 客户端代码
    ↓
OpenAI-compatible HTTP API
    ↓
不同模型服务：OpenAI / vLLM / Ollama / 云厂商兼容接口 / 本地推理服务
```

![Ollama](http://public.file.lvshuhuai.cn/images\openai-compatible-api-ollama-logo.png)

一个最小配置通常由三部分构成：

```text
base_url   服务地址，例如 http://localhost:8000/v1
api_key    鉴权 token，本地服务可能可以写 EMPTY
model      模型名，例如 Qwen/Qwen2.5-7B-Instruct、qwen2.5:7b、text-embedding-3-small
```

其中 `base_url` 最容易写错。很多 SDK 或客户端配置中的 `base_url` 已经包含 `/v1`，例如：

```text
http://localhost:8000/v1
```

此时请求聊天接口时拼接的是：

```text
{base_url}/chat/completions
```

最终地址是：

```text
http://localhost:8000/v1/chat/completions
```

不要写成：

```text
http://localhost:8000/v1/v1/chat/completions
```

### OpenAI-compatible API 不是 OpenAPI

这两个名字很像，但不在同一层。

- **OpenAI-compatible API**：[[大语言模型 LLM]] 服务接口格式，讨论的是 `/v1/chat/completions`、`/v1/embeddings`、`stream`、`tool_calls` 等模型调用接口。
- **OpenAPI Specification**：REST API 描述规范，用 YAML/JSON 描述普通业务 API 的路径、参数、响应体等。

本文只讨论前者。

### 常见 endpoint

在 OpenAI-compatible API 中，最常见的 endpoint 是：

```text
GET  /v1/models
POST /v1/chat/completions
POST /v1/embeddings
```

还有一些服务会兼容：

```text
POST /v1/completions
POST /v1/responses
```

但在兼容生态中，`/v1/chat/completions` 和 `/v1/embeddings` 通常更基础、更常见。`/v1/responses` 是更新形态，但不同服务的兼容程度不一定一致。

典型兼容实现可以参考 [vLLM OpenAI-Compatible Server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) 和 [Ollama OpenAI compatibility](https://ollama.readthedocs.io/en/openai/)；具体模型命名则要看服务自身，例如 Qwen 系列通常以服务端暴露的模型名为准。

### 兼容的含义

“compatible” 不等于“完全一样”。它通常只表示核心请求/响应结构相似。

可以按下面的层级理解兼容程度：

1. 能否访问 `POST /v1/chat/completions`。
2. 是否支持 `model`、`messages`、`temperature`、`stream`。
3. 是否支持 `stream: true` 的 SSE 风格响应。
4. 是否返回 `usage`。
5. 是否支持 `/v1/embeddings`。
6. 是否支持 `tools` 与 `tool_calls`。
7. 是否支持 tool calls 的流式增量格式。
8. 是否支持多模态输入、reasoning 字段、Responses API 等高级能力。

开发客户端时应当假设：越靠后的能力，兼容差异越大。

## Chat Completions：对话生成接口

[`POST /v1/chat/completions`](https://platform.openai.com/docs/api-reference/chat) 是 OpenAI-compatible API 中最重要的接口。它接收一组对话消息，返回模型生成的一条 assistant 消息。

![Chat Templates](http://public.file.lvshuhuai.cn/images\openai-compatible-api-chat-templates.png)

### 最小请求结构

完整路径通常是：

```text
POST {base_url}/chat/completions
```

例如：

```text
POST http://localhost:8000/v1/chat/completions
```

最小请求体：

```json
{
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "messages": [
    {
      "role": "user",
      "content": "用一句话解释 OpenAI-compatible API。"
    }
  ]
}
```

更常见的请求体会带上系统设定、温度和是否流式：

```json
{
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "messages": [
    {
      "role": "system",
      "content": "你是一个回答简洁、准确的助手。"
    },
    {
      "role": "user",
      "content": "用一句话解释 OpenAI-compatible API。"
    }
  ],
  "temperature": 0.7,
  "stream": false
}
```

这里的核心字段是：

| 字段 | 含义 |
|---|---|
| `model` | 要调用的模型名。不同服务的模型名格式不同。 |
| `messages` | 对话上下文数组。 |
| `role` | 消息角色，例如 `system`、`user`、`assistant`、`tool`。 |
| `content` | 消息内容。 |
| `temperature` | 控制随机性，越低越稳定，越高越发散。 |
| `stream` | 是否启用流式输出。 |

### 非流式响应结构

当 `stream: false` 时，服务端会一次性返回完整 JSON。典型结构如下：

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "OpenAI-compatible API 是一种让不同模型服务复用 OpenAI 调用格式的接口兼容方式。"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 30,
    "total_tokens": 50
  }
}
```

最常用的读取路径是：

```text
choices[0].message.content
```

`finish_reason` 表示模型为什么停止。常见值包括：

| `finish_reason`  | 含义                    |
| ---------------- | --------------------- |
| `stop`           | 正常停止。                 |
| `length`         | 达到最大生成长度，被截断。         |
| `tool_calls`     | 模型生成了工具调用，需要客户端执行工具。  |
| `content_filter` | 内容被安全策略截断或过滤，具体取决于服务。 |

### messages 的语义

`messages` 不是普通字符串，而是一组有角色的对话记录。常见角色如下：

```text
system      系统设定，通常放在最前面
developer   开发者指令，部分新模型/新接口会使用
user        用户输入
assistant   模型历史回复
tool        工具执行结果
```

在 OpenAI-compatible 生态中，最通用、最稳定的三类是：

```text
system / user / assistant
```

一个简单的单轮请求：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是一个回答简洁的助手。"
    },
    {
      "role": "user",
      "content": "解释一下 embedding。"
    }
  ]
}
```

一个多轮请求：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是一个回答简洁的助手。"
    },
    {
      "role": "user",
      "content": "我叫李明，喜欢 Java。"
    },
    {
      "role": "assistant",
      "content": "好的，我知道了：你叫李明，喜欢 Java。"
    },
    {
      "role": "user",
      "content": "我喜欢什么编程语言？"
    }
  ]
}
```

### 多轮对话不是服务端自动记忆

在普通 Chat Completions 调用中，模型是否知道上下文，取决于你本次请求发了哪些 `messages`。多数 OpenAI-compatible 服务不会替你自动保存上一轮内容。

错误理解：

```text
第一轮告诉模型：我叫李明。
第二轮只发：我叫什么？
模型应该自动知道。
```

正确理解：

```text
第二轮请求必须把第一轮 user 消息和 assistant 回复一起放回 messages。
```

因此，多轮对话的本质是客户端维护上下文：

```text
每次请求 = 系统设定 + 历史 user/assistant 消息 + 当前 user 消息
```

### Java 中维护多轮 messages

定义消息结构：

```java
public record ChatMessage(String role, String content) {
}
```

定义会话结构：

```java
import java.util.ArrayList;
import java.util.List;

public class ChatSession {

    private final List<ChatMessage> messages = new ArrayList<>();

    public ChatSession(String systemPrompt) {
        messages.add(new ChatMessage("system", systemPrompt));
    }

    public void addUserMessage(String content) {
        messages.add(new ChatMessage("user", content));
    }

    public void addAssistantMessage(String content) {
        messages.add(new ChatMessage("assistant", content));
    }

    public List<ChatMessage> getMessages() {
        return messages;
    }
}
```

调用流程：

```java
ChatSession session = new ChatSession("你是一个回答简洁、准确的助手。");
OpenAICompatibleChatClient client = new OpenAICompatibleChatClient();

session.addUserMessage("我叫李明，喜欢 Java。");
String answer1 = client.chat(session.getMessages());
session.addAssistantMessage(answer1);

session.addUserMessage("我喜欢什么编程语言？");
String answer2 = client.chat(session.getMessages());
session.addAssistantMessage(answer2);

System.out.println(answer2);
```

关键点是：模型每次生成后，客户端要把 assistant 回复追加进历史。

```java
session.addAssistantMessage(answer);
```

如果只保存用户消息，不保存 assistant 消息，对话连贯性会明显下降。

## Embeddings：文本向量化接口

[`POST /v1/embeddings`](https://platform.openai.com/docs/api-reference/embeddings) 用来把文本编码成向量。它不生成自然语言回复，而是返回一个浮点数数组。这个数组可以用于语义相似度计算、检索、聚类、去重、推荐等任务。

![Embeddings Indexing](http://public.file.lvshuhuai.cn/images\openai-compatible-api-embeddings-indexing.png)

### 与 chat completions 的区别

```text
/v1/chat/completions
    输入：messages
    输出：assistant 文本回复

/v1/embeddings
    输入：input 文本或文本数组
    输出：embedding 向量数组
```

`/v1/embeddings` 不需要 `messages`、`role`、`system`、`assistant`。它只关心 `model` 和 `input`。

### 最小请求

```json
{
  "model": "text-embedding-3-small",
  "input": "OpenAI-compatible API 是一种统一模型调用格式。"
}
```

完整路径：

```text
POST {base_url}/embeddings
```

例如：

```text
POST https://api.openai.com/v1/embeddings
POST http://localhost:8000/v1/embeddings
```

如果是本地或兼容服务，`model` 必须是该服务实际支持的 embedding 模型。不要把聊天模型名随便传给 embeddings 接口。

### 响应结构

典型响应：

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [
        0.0123,
        -0.0456,
        0.0789
      ]
    }
  ],
  "model": "text-embedding-3-small",
  "usage": {
    "prompt_tokens": 12,
    "total_tokens": 12
  }
}
```

最常用的读取路径是：

```text
data[0].embedding
```

它是一个浮点数组。不同模型的向量维度可能不同。例如有的模型输出 1024 维，有的输出 1536 维，有的输出 3072 维。维度不同的向量不能直接混在同一个向量库中比较。

### 批量输入

`input` 可以是单个字符串：

```json
{
  "model": "text-embedding-3-small",
  "input": "Java 是一门面向对象编程语言。"
}
```

也可以是字符串数组：

```json
{
  "model": "text-embedding-3-small",
  "input": [
    "Java 是一门面向对象编程语言。",
    "Python 常用于数据科学和深度学习。",
    "Spring Boot 常用于构建 Java Web 后端。"
  ]
}
```

响应中的 `data[].index` 对应原始输入数组的位置：

```json
{
  "data": [
    {
      "index": 0,
      "embedding": [0.01, 0.02, 0.03]
    },
    {
      "index": 1,
      "embedding": [0.04, 0.05, 0.06]
    }
  ]
}
```

### Java 最小 embedding 客户端

Maven 依赖：

```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.17.2</version>
</dependency>
```

Java 代码：

```java
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;

public class OpenAICompatibleEmbeddingClient {

    private static final String BASE_URL = "https://api.openai.com/v1";
    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String MODEL = "text-embedding-3-small";

    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    public static void main(String[] args) throws Exception {
        double[] vector = embed("OpenAI-compatible API 是一种统一模型调用格式。");
        System.out.println("dimension = " + vector.length);
        System.out.println("first value = " + vector[0]);
    }

    public static double[] embed(String text) throws Exception {
        Map<String, Object> requestBody = Map.of(
                "model", MODEL,
                "input", text
        );

        String jsonBody = objectMapper.writeValueAsString(requestBody);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/embeddings"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();

        HttpResponse<String> response = httpClient.send(
                request,
                HttpResponse.BodyHandlers.ofString()
        );

        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            throw new RuntimeException(
                    "Embedding request failed, status=" + response.statusCode()
                            + ", body=" + response.body()
            );
        }

        JsonNode embeddingNode = objectMapper
                .readTree(response.body())
                .path("data")
                .path(0)
                .path("embedding");

        double[] vector = new double[embeddingNode.size()];
        for (int i = 0; i < embeddingNode.size(); i++) {
            vector[i] = embeddingNode.get(i).asDouble();
        }
        return vector;
    }
}
```

如果接本地兼容服务，通常只改：

```java
private static final String BASE_URL = "http://localhost:8000/v1";
private static final String API_KEY = "EMPTY";
private static final String MODEL = "your-embedding-model-name";
```

### 向量相似度

embedding 的主要用途不是直接阅读数字，而是比较语义相似度。常见方法是余弦相似度：

```java
public static double cosineSimilarity(double[] a, double[] b) {
    if (a.length != b.length) {
        throw new IllegalArgumentException("Vector dimensions do not match.");
    }

    double dot = 0.0;
    double normA = 0.0;
    double normB = 0.0;

    for (int i = 0; i < a.length; i++) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }

    if (normA == 0.0 || normB == 0.0) {
        return 0.0;
    }

    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}
```

示例：

```java
double[] v1 = embed("Java 是一门面向对象编程语言。");
double[] v2 = embed("Spring Boot 是 Java 后端开发框架。");
double[] v3 = embed("今天晚饭吃番茄炒蛋。");

System.out.println(cosineSimilarity(v1, v2));
System.out.println(cosineSimilarity(v1, v3));
```

通常 `v1` 和 `v2` 的相似度会高于 `v1` 和 `v3`。

## Streaming：流式响应格式

[`stream: true`](https://platform.openai.com/docs/api-reference/chat/create#chat-create-stream) 表示服务端不等完整回答生成完再返回，而是一边生成一边返回多个 chunk。客户端需要逐块读取并拼接。

![Qwen](http://public.file.lvshuhuai.cn/images\openai-compatible-api-qwen-logo.jpg)

### 非流式与流式的根本区别

非流式：

```text
一次性返回完整 JSON
读取 choices[0].message.content
```

流式：

```text
返回多行 data: ...
每个 data 后面是一小段 JSON chunk
读取 choices[0].delta.content
客户端自己拼接完整回答
```

请求体示例：

```json
{
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "messages": [
    {
      "role": "user",
      "content": "用三句话解释 OpenAI-compatible API。"
    }
  ],
  "stream": true
}
```

### SSE 风格响应

流式响应通常类似 Server-Sent Events：

```text
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":"OpenAI"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":"-compatible"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":" API"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

注意几个细节：

- 每个有效数据行通常以 `data: ` 开头。
- 空行用于分隔事件，不能当 JSON 解析。
- `data: [DONE]` 是结束标记，不是 JSON。
- 第一个 chunk 可能只包含 `role`，不包含 `content`。
- 最后一个 chunk 可能只包含 `finish_reason`，不包含 `content`。

### chunk 的典型结构

普通文本 chunk：

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion.chunk",
  "created": 1710000000,
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "你好"
      },
      "finish_reason": null
    }
  ]
}
```

需要读取：

```text
choices[0].delta.content
```

而不是：

```text
choices[0].message.content
```

### Java 流式读取逻辑

Java 中可以用 `BodyHandlers.ofInputStream()`，然后逐行读取。

```java
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

public class OpenAICompatibleStreamingDemo {

    private static final String BASE_URL = "http://localhost:8000/v1";
    private static final String API_KEY = "EMPTY";
    private static final String MODEL = "Qwen/Qwen2.5-7B-Instruct";

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static void main(String[] args) throws Exception {
        streamChat("用三句话解释 OpenAI-compatible API。");
    }

    public static void streamChat(String userMessage) throws Exception {
        String requestBody = """
                {
                  "model": "%s",
                  "messages": [
                    {
                      "role": "system",
                      "content": "你是一个回答准确、简洁的助手。"
                    },
                    {
                      "role": "user",
                      "content": "%s"
                    }
                  ],
                  "temperature": 0.7,
                  "stream": true
                }
                """.formatted(MODEL, escapeJson(userMessage));

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/chat/completions"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();

        HttpClient client = HttpClient.newHttpClient();

        HttpResponse<java.io.InputStream> response = client.send(
                request,
                HttpResponse.BodyHandlers.ofInputStream()
        );

        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            String errorBody = new String(response.body().readAllBytes(), StandardCharsets.UTF_8);
            throw new RuntimeException(
                    "Request failed, status=" + response.statusCode() + ", body=" + errorBody
            );
        }

        StringBuilder fullContent = new StringBuilder();

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(response.body(), StandardCharsets.UTF_8)
        )) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.isBlank()) {
                    continue;
                }

                if (!line.startsWith("data: ")) {
                    continue;
                }

                String data = line.substring("data: ".length()).trim();

                if ("[DONE]".equals(data)) {
                    break;
                }

                JsonNode root = objectMapper.readTree(data);
                JsonNode choice = root.path("choices").path(0);
                JsonNode delta = choice.path("delta");

                String piece = delta.path("content").asText("");
                if (!piece.isEmpty()) {
                    System.out.print(piece);
                    fullContent.append(piece);
                }
            }
        }

        System.out.println();
        System.out.println("完整内容：");
        System.out.println(fullContent);
    }

    private static String escapeJson(String text) {
        return text
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\r", "\\r")
                .replace("\n", "\\n");
    }
}
```

核心处理流程是：

```text
1. 按行读取响应体。
2. 跳过空行。
3. 只处理 data: 开头的行。
4. 去掉 data: 前缀。
5. 如果是 [DONE]，结束。
6. 否则解析 JSON。
7. 读取 choices[0].delta.content。
8. 追加到 StringBuilder。
```

## Tool Calls：工具调用及其流式格式

[`tool_calls`](https://platform.openai.com/docs/guides/function-calling) [[工具调用 Tool Calling]] 是模型生成的“函数调用意图”。它不是模型真的执行了函数，而是模型输出一个结构化对象，告诉客户端：应该调用哪个函数、传哪些参数。真正的函数执行发生在你的程序里。

![Tool Calling Flow](http://public.file.lvshuhuai.cn/images\openai-compatible-api-tool-calling-flow.png)

### 非流式 tool_calls

请求中需要声明可用工具：

```json
{
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "messages": [
    {
      "role": "user",
      "content": "查询一下新加坡今天的天气，单位用摄氏度。"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather for a location.",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name, e.g. Singapore"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"]
            }
          },
          "required": ["location", "unit"]
        }
      }
    }
  ],
  "tool_choice": "auto",
  "stream": false
}
```

如果模型决定调用工具，非流式响应可能是：

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\":\"Singapore\",\"unit\":\"celsius\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

注意：`function.arguments` 是字符串，不是 JSON 对象。它的内容看起来像 JSON，但你必须自己解析和校验。

```java
String argumentsText = "{\"location\":\"Singapore\",\"unit\":\"celsius\"}";
JsonNode args = objectMapper.readTree(argumentsText);
String location = args.path("location").asText();
String unit = args.path("unit").asText();
```

### 流式 tool_calls 与普通文本流的区别

普通文本流拼接的是：

```text
choices[0].delta.content
```

tool calls 流拼接的是：

```text
choices[0].delta.tool_calls[*].function.arguments
```

也就是说：

```text
普通文本流：
    delta.content 一段一段返回
    客户端拼成完整文本

tool_calls 流：
    delta.tool_calls 一段一段返回
    客户端拼成完整工具调用
```

### tool_calls 的流式 chunk 示例

开始时可能只有角色：

```text
data: {"choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}
```

接着出现工具调用的元信息：

```text
data: {"choices":[{"index":0,"delta":{"tool_calls":[{"index":0,"id":"call_abc123","type":"function","function":{"name":"get_weather","arguments":""}}]},"finish_reason":null}]}
```

随后 arguments 被拆成多个片段：

```text
data: {"choices":[{"index":0,"delta":{"tool_calls":[{"index":0,"function":{"arguments":"{\"location\""}}]},"finish_reason":null}]}

data: {"choices":[{"index":0,"delta":{"tool_calls":[{"index":0,"function":{"arguments":":\"Singapore\""}}]},"finish_reason":null}]}

data: {"choices":[{"index":0,"delta":{"tool_calls":[{"index":0,"function":{"arguments":",\"unit\":\"celsius\"}"}}]},"finish_reason":null}]}
```

最后结束：

```text
data: {"choices":[{"index":0,"delta":{},"finish_reason":"tool_calls"}]}

data: [DONE]
```

最终拼出来的是：

```json
{
  "location": "Singapore",
  "unit": "celsius"
}
```

但在流式过程中，任何单个 `arguments` 片段都不一定是合法 JSON。因此不能边收到边解析 JSON，必须先拼接，结束后再解析。

### 用 index 聚合多个工具调用

模型可能一次生成多个工具调用。流式返回中，每个 tool call 都有 `index`。客户端应该按 `index` 分组累计。

```json
"tool_calls": [
  {
    "index": 0,
    "id": "call_weather",
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": "{\"location\":\"Singapore\""
    }
  },
  {
    "index": 1,
    "id": "call_time",
    "type": "function",
    "function": {
      "name": "get_time",
      "arguments": "{\"timezone\":\"Asia/Singapore\""
    }
  }
]
```

后续 chunk 可能继续补：

```json
"tool_calls": [
  {
    "index": 0,
    "function": {
      "arguments": ",\"unit\":\"celsius\"}"
    }
  },
  {
    "index": 1,
    "function": {
      "arguments": "}"
    }
  }
]
```

因此，稳妥的聚合 key 是：

```text
choice.index + tool_call.index
```

在单 choice 场景下，也可以只用：

```text
tool_call.index
```

### Java tool_calls 累积器

定义一个累积器：

```java
import java.util.LinkedHashMap;
import java.util.Map;

public class StreamingToolCallAccumulator {

    public static class ToolCallState {
        public int index;
        public String id;
        public String type;
        public String name;
        public StringBuilder arguments = new StringBuilder();

        public String argumentsText() {
            return arguments.toString();
        }
    }

    private final Map<Integer, ToolCallState> toolCalls = new LinkedHashMap<>();

    public void append(
            int index,
            String id,
            String type,
            String name,
            String argumentsPart
    ) {
        ToolCallState state = toolCalls.computeIfAbsent(index, k -> {
            ToolCallState s = new ToolCallState();
            s.index = k;
            return s;
        });

        if (id != null && !id.isBlank()) {
            state.id = id;
        }

        if (type != null && !type.isBlank()) {
            state.type = type;
        }

        if (name != null && !name.isBlank()) {
            state.name = name;
        }

        if (argumentsPart != null && !argumentsPart.isEmpty()) {
            state.arguments.append(argumentsPart);
        }
    }

    public Map<Integer, ToolCallState> getToolCalls() {
        return toolCalls;
    }
}
```

解析每个 chunk：

```java
JsonNode delta = root
        .path("choices")
        .path(0)
        .path("delta");

JsonNode toolCallsNode = delta.path("tool_calls");

if (toolCallsNode.isArray()) {
    for (JsonNode toolCallNode : toolCallsNode) {
        int toolIndex = toolCallNode.path("index").asInt();

        String id = toolCallNode.path("id").isMissingNode()
                ? null
                : toolCallNode.path("id").asText(null);

        String type = toolCallNode.path("type").isMissingNode()
                ? null
                : toolCallNode.path("type").asText(null);

        JsonNode functionNode = toolCallNode.path("function");

        String name = functionNode.path("name").isMissingNode()
                ? null
                : functionNode.path("name").asText(null);

        String argumentsPart = functionNode.path("arguments").isMissingNode()
                ? null
                : functionNode.path("arguments").asText(null);

        accumulator.append(
                toolIndex,
                id,
                type,
                name,
                argumentsPart
        );
    }
}
```

结束后再解析完整参数：

```java
for (StreamingToolCallAccumulator.ToolCallState toolCall
        : accumulator.getToolCalls().values()) {

    System.out.println("id = " + toolCall.id);
    System.out.println("type = " + toolCall.type);
    System.out.println("name = " + toolCall.name);
    System.out.println("arguments = " + toolCall.argumentsText());

    JsonNode args = objectMapper.readTree(toolCall.argumentsText());
    // 根据 toolCall.name 分发到本地函数
}
```

### 工具执行后的消息回填

模型生成 `tool_calls` 后，客户端要做三件事：

1. 解析模型生成的工具名和参数。
2. 在本地执行对应函数。
3. 把工具执行结果作为 `role: "tool"` 消息追加回 `messages`。

第一步，保留 assistant 的工具调用消息：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\":\"Singapore\",\"unit\":\"celsius\"}"
      }
    }
  ]
}
```

第二步，执行本地函数，例如：

```java
String result = getWeather("Singapore", "celsius");
```

第三步，追加工具结果消息：

```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "Singapore: 30°C, cloudy."
}
```

然后再次调用 `/v1/chat/completions`，让模型基于工具结果生成最终自然语言回答。

完整消息序列会变成：

```json
[
  {
    "role": "user",
    "content": "查询一下新加坡今天的天气，单位用摄氏度。"
  },
  {
    "role": "assistant",
    "content": null,
    "tool_calls": [
      {
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\":\"Singapore\",\"unit\":\"celsius\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_abc123",
    "content": "Singapore: 30°C, cloudy."
  }
]
```

### tool_calls 的最小闭环

```text
1. 请求中声明 tools。
2. 模型返回 assistant.tool_calls。
3. 客户端解析 function.name 和 function.arguments。
4. 客户端校验 arguments。
5. 客户端执行本地函数。
6. 客户端追加 role=tool 的工具结果消息。
7. 再次请求模型。
8. 模型根据工具结果生成最终回复。
```

这就是 OpenAI-compatible API 层面的工具调用闭环。它只定义数据交换格式，不负责执行工具、不负责权限控制、不负责业务逻辑。

![Agent Loop](http://public.file.lvshuhuai.cn/images\openai-compatible-api-agent-loop.png)

## Java 客户端封装与工程细节

如果只写 demo，直接拼 JSON 字符串也能跑。但如果写长期可维护的 OpenAI-compatible 客户端，应当把配置、请求结构、响应解析和错误处理拆开。

![vLLM Design Diagram](http://public.file.lvshuhuai.cn/images\openai-compatible-api-vllm-design-diagram.png)

### 配置对象

```java
public record OpenAICompatibleConfig(
        String baseUrl,
        String apiKey,
        String chatModel,
        String embeddingModel
) {
}
```

示例：

```java
OpenAICompatibleConfig config = new OpenAICompatibleConfig(
        "http://localhost:8000/v1",
        "EMPTY",
        "Qwen/Qwen2.5-7B-Instruct",
        "your-embedding-model"
);
```

### 统一 HTTP 错误处理

OpenAI-compatible 服务常见错误包括：

| 状态码 | 常见原因 |
|---|---|
| `400` | 请求字段不合法、JSON 格式错误、参数不支持。 |
| `401` | API key 缺失或错误。 |
| `404` | endpoint 不存在、base_url 拼错、模型不存在。 |
| `429` | 速率限制或并发限制。 |
| `500` | 服务端推理失败。 |
| `503` | 模型未加载、服务不可用、排队过载。 |

建议封装：

```java
private static void checkStatus(HttpResponse<String> response) {
    int status = response.statusCode();
    if (status < 200 || status >= 300) {
        throw new RuntimeException(
                "Request failed, status=" + status + ", body=" + response.body()
        );
    }
}
```

流式响应由于 body 是 `InputStream`，错误体需要先读出来：

```java
if (response.statusCode() < 200 || response.statusCode() >= 300) {
    String errorBody = new String(response.body().readAllBytes(), StandardCharsets.UTF_8);
    throw new RuntimeException(
            "Request failed, status=" + response.statusCode() + ", body=" + errorBody
    );
}
```

### 不要手写复杂 JSON

简单 demo 可以用字符串模板。但真实项目中，建议用 Java 对象或 `Map` 交给 Jackson 序列化。这样可以避免引号、换行、反斜杠转义错误。

不推荐长期使用：

```java
String requestBody = "{\"model\":\"" + model + "\", ...}";
```

更稳妥：

```java
Map<String, Object> requestBody = Map.of(
        "model", model,
        "messages", messages,
        "temperature", 0.7,
        "stream", false
);

String jsonBody = objectMapper.writeValueAsString(requestBody);
```

### 上下文长度控制

多轮对话时，不能无限追加历史。历史越长：

- 请求体越大；
- token 消耗越多；
- 响应越慢；
- 更容易超过模型上下文窗口；
- 老旧上下文可能干扰当前任务。

简单策略：保留 system 消息和最近 N 轮对话。

```java
public List<ChatMessage> buildRecentMessages(List<ChatMessage> allMessages, int maxMessages) {
    if (allMessages.size() <= maxMessages) {
        return allMessages;
    }

    ChatMessage first = allMessages.get(0); // 通常是 system
    List<ChatMessage> tail = allMessages.subList(
            Math.max(1, allMessages.size() - (maxMessages - 1)),
            allMessages.size()
    );

    List<ChatMessage> result = new java.util.ArrayList<>();
    result.add(first);
    result.addAll(tail);
    return result;
}
```

更复杂的项目可以使用摘要压缩，但这仍然属于客户端上下文管理问题，不是 OpenAI-compatible API 自动完成的事情。

### 兼容性探测

接入一个新的 OpenAI-compatible 服务时，建议先按顺序测试：

1. `GET /v1/models` 是否可用。
2. `POST /v1/chat/completions` 的非流式调用是否可用。
3. `stream: true` 是否可用。
4. `/v1/embeddings` 是否可用。
5. `tools` 与 `tool_calls` 是否可用。
6. tool calls streaming 是否可用。

不要一开始就写完整[[智能体 Agent]] loop。先验证接口层能力，再封装业务逻辑。
