# LangChain

这份笔记围绕 [LangChain](https://docs.langchain.com/oss/python/langchain/overview) 本体展开，目标是把一套经常被混用的概念拆清楚：`Model` 是什么，`Message` 是什么，`Tool` 与通用意义上的[[工具调用 Tool Calling]] 是什么关系，`Agent` 到底做了什么，[[结构化输出 Structured Output]]、[[状态管理 State Management]]、`Middleware`、`Context engineering`、`Retrieval`、`Multi-agent` 又分别处在什么层次。文中会尽量用统一的术语、完整的段落解释和可运行代码，把这些对象放回同一个运行时里理解。

需要先给一个边界判断。LangChain 不是模型，不是推理引擎，不是数据库，也不是协议标准。它更接近一套 **[[大语言模型 LLM]] application framework / agent framework**：一方面把不同模型供应商的接口收敛成相对统一的调用方式，另一方面把消息、工具、状态、上下文、结构化输出等对象放进同一个执行语义里。它解决的是“如何把模型接进应用”，而不是“如何训练模型”或“如何替代所有底层基础设施”。

因此，理解 LangChain 的核心，不在于背多少 provider 名称，而在于搞清楚这几个对象之间的关系：

- [Model](https://docs.langchain.com/oss/python/langchain/models) 是推理接口，也是[[智能体 Agent]] 的决策核心。
- [Messages](https://docs.langchain.com/oss/python/langchain/messages) 是模型输入输出的标准载体。
- [Tool](https://docs.langchain.com/oss/python/langchain/tools) 是给模型可见的外部能力接口。
- [Agent](https://docs.langchain.com/oss/python/langchain/agents) 是把模型与工具接进循环执行的运行时。
- [Structured Output](https://docs.langchain.com/oss/python/langchain/structured-output) 解决输出契约问题。
- [State](https://docs.langchain.com/oss/python/langchain/short-term-memory) 解决短期运行数据和会话延续问题。
- [Middleware](https://docs.langchain.com/oss/python/langchain/middleware) 解决运行时拦截、控制和改写问题。
- [Context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering) 解决“在什么时候给模型/工具什么信息”的问题。
- [Retrieval](https://docs.langchain.com/oss/python/langchain/rag) 负责把外部知识带入上下文。
- [Multi-agent](https://docs.langchain.com/oss/python/langchain/multi-agent) 则是在上下文和职责无法由单 Agent 有效承载时的一种组织形式。

这些概念如果分开背，会显得很碎；但如果把它们放进一条实际执行链里，就会自然很多：用户输入被组织成 `messages`，`model` 读取消息做判断，必要时发起 `tool call`，运行时执行 `tool` 并把结果写回 `state`，`middleware` 可以在每一步拦截和改写，最终 `agent` 以自由文本或结构化结果结束。这才是 LangChain 真正的主线。

## LangChain 的对象体系：不是一堆 API，而是一套运行语义

### Model：不是“厂商模型名”，而是统一的推理接口

很多人在一开始会把 LangChain 里的 `Model` 理解成“OpenAI 的模型”“Anthropic 的模型”这种实体。这个理解不算错，但不完整。对 LangChain 而言，`Model` 更重要的身份，是一个 **统一的聊天模型接口**。你可以通过它调用不同 provider 的 chat model，但在应用层，模型对象的职责相对稳定：接收消息、生成响应、在需要时返回工具调用意图、支持流式输出、支持批量调用、支持多模态输入等。

在 Agent 语境里，Model 还承担了另一个关键角色：**决策者**。工具不会自己决定什么时候被调用，消息也不会自己推进流程。真正决定“这一步要不要调用工具”“该不该停下来给最终答案”的，是模型。换句话说，Tool 是 capability，Message 是 carrier，Model 才是 reasoning engine。

下面是最小的模型初始化示例。注意这里的重点不是 provider 细节，而是 LangChain 统一接口的用法。

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4.1-mini")
```

在很多简单任务里，模型可以直接单独使用：

```python
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage

model = init_chat_model("openai:gpt-4.1-mini")

response = model.invoke([
    SystemMessage("You are a concise assistant."),
    HumanMessage("Explain what a LangChain model is."),
])

print(type(response).__name__)
print(response.content)
```

这个例子已经透露出一个非常重要的事实：LangChain 的 chat model 主线，默认不是“吃字符串、吐字符串”，而是“吃消息、吐消息”。这就引出了下一部分。

### Messages：模型上下文的基本单位

`Messages` 是 LangChain 中非常基础、但也最容易被忽略的对象。它的作用不是把聊天记录换个名字，而是把模型交互从“一个[[提示词 Prompt]]  字符串”提升为“一个带角色、内容和元数据的上下文序列”。

最核心的几类消息有四种：

- `SystemMessage`：系统级行为约束。
- `HumanMessage`：用户输入。
- `AIMessage`：模型输出。
- `ToolMessage`：工具执行结果回传给模型。

这四种消息串起来，才是一轮完整的 Agent 交互链。最简单的用法如下：

```python
from langchain.messages import SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4.1-mini")

messages = [
    SystemMessage("You are a helpful coding assistant."),
    HumanMessage("Write a Python function to add two integers."),
]

response = model.invoke(messages)
print(response.content)
```

为什么要用消息，而不是一直用字符串？因为一旦进入这些场景，字符串就会很别扭：

- 多轮对话，需要保留历史；
- 有系统角色和用户角色之分；
- 有工具调用往返；
- 有多模态输入；
- 有运行元数据和 token usage 统计。

如果只靠拼接 prompt 字符串，后续几乎所有高级能力都会变得混乱。Message 的意义，就在于为这些能力准备统一承载结构。

### AIMessage：不只是文本答案

`model.invoke(...)` 返回的标准对象通常是 `AIMessage`。很多初学者会把它当成“最终回答的壳”，但它其实还承载了很多额外信息。最常用的几个字段包括：

- `content`：消息内容；
- `tool_calls`：模型发起的工具调用请求；
- `id`：消息标识；
- `usage_metadata`：token 使用情况；
- `response_metadata`：provider 响应附带信息。

例如：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4.1-mini")
response = model.invoke("Say hello")

print(type(response).__name__)
print(response.content)
print(response.usage_metadata)
```

一旦模型发起工具调用，`AIMessage` 里就不再只是最终答案，而会出现 `tool_calls`。这说明模型此时不是在“回答”，而是在“请求运行时执行某个工具”。

一个典型的 `tool_calls` 结构大致长这样：

```python
[
    {
        "name": "get_weather",
        "args": {"city": "Tokyo"},
        "id": "call_xxx",
        "type": "tool_call"
    }
]
```

所以要记住：`AIMessage` 不只是自然语言输出，它还是 Agent 运行时协议里非常关键的一个节点。

### Tool：LangChain 对 Tool Calling 的工程化落地

在通用的 Agent 开发语境里，tool calling 是模型返回一个“我要调用某个外部能力”的意图；而在 LangChain 里，`Tool` 则是对这种能力做出的正式工程封装。

更准确地说，LangChain 的 Tool 主要做了四件事：

1. 把普通函数包装成模型可见能力；
2. 给工具附上名称、描述和参数 schema；
3. 帮助把工具转换成底层 provider 可理解的 function/tool calling 规格；
4. 将工具接入 Agent loop，使执行结果可以回流到上下文里。

最常见的定义工具方式是 `@tool`：

```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get current weather information for a city."""
    fake_weather_db = {
        "beijing": "Beijing: sunny, 26C",
        "tokyo": "Tokyo: rainy, 19C",
    }
    return fake_weather_db.get(city.strip().lower(), f"No data for {city}")
```

这里最重要的不是函数体有多复杂，而是以下三件事是否清晰：

- 工具名字是否有辨识度；
- docstring 是否准确描述用途；
- 参数 schema 是否让模型容易构造输入。

一个糟糕的工具往往不是“跑不起来”，而是“模型不知道什么时候该调它，或者不会正确填参数”。例如下面这种宽泛工具，就非常不利于模型判断：

```python
@tool
def do_everything(text: str) -> str:
    """Handle many kinds of requests."""
    ...
```

而像 `get_weather(city: str)`、`calculate(expression: str)` 这种职责单一的工具，则更容易被模型正确使用。

### Agent：不是神秘智能体，而是一个模型/工具循环

讲到这里，LangChain 里的 `Agent` 就可以比较准确地理解了。它不是“会自动思考的对象”，也不是“比模型更高级的某种生命体”。更实际的说法是：

**Agent 是把 model、tools、messages/state、middleware 等对象接进一个 loop 的运行时。**

这个 loop 很朴素：

1. 接收用户输入；
2. 调模型；
3. 模型要么直接回答，要么返回 tool calls；
4. 如果有工具调用，运行时执行对应工具；
5. 把工具结果写回消息/状态；
6. 再调模型；
7. 直到模型给出最终答案。

LangChain 1.0 的主入口就是 `create_agent(...)`。最小骨架如下：

![LangChain Agent Loop](http://public.file.lvshuhuai.cn/images\langchain-core-agent-loop.png)

```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get current weather information for a city."""
    return f"{city}: sunny, 25C"

model = init_chat_model("openai:gpt-4.1-mini")

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant. Use tools when needed.",
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "东京天气怎么样？"}
    ]
})

print(result["messages"][-1].content)
```

这个例子里，真正值得观察的是 `result["messages"]` 整条轨迹，而不只是最后一句话。把全部消息打印出来，你通常能看到：用户消息、模型 tool call、工具执行结果、模型最终答复。

## 输出、状态与控制：Agent 为什么能跑成一个系统

如果说前一部分讲的是“LangChain 里有哪些核心对象”，那么这一部分讲的是“为什么这些对象能被组织成一个稳定的运行时”。重点包括 `Structured Output`、`State` 和 `Middleware`。这三者分别对应：输出契约、短期运行数据、运行时拦截控制。

### Structured Output：别再用自然语言硬解析结果

很多初学者会默认让模型输出一段自然语言，然后自己再从中提取字段。这在 demo 里可以勉强成立，但一旦进入工程环境，就会非常脆弱。LangChain 提供的 `Structured Output`，目的就是让 Agent 最终返回**可校验、可直接被程序消费**的数据，而不是“看起来像 JSON 的一段话”。

最常见的做法，是给 `create_agent(...)` 加 `response_format`。下面用 Pydantic 举一个最小例子：

```python
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

class ContactInfo(BaseModel):
    name: str = Field(description="The person's name")
    email: str = Field(description="The email address")
    phone: str = Field(description="The phone number")

model = init_chat_model("openai:gpt-4.1-mini")

agent = create_agent(
    model=model,
    tools=[],
    response_format=ContactInfo,
)

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"
        }
    ]
})

print(result["structured_response"])
```

这里最重要的不是 Pydantic 本身，而是你要理解 LangChain 的语义：

- 结构化输出通过 `response_format` 声明；
- 最终结果不再只落在普通 `content` 里；
- 正式的结构化结果会进入 `structured_response`。

也就是说，`structured_response` 才是你应该交给程序后续逻辑处理的对象。普通文本消息更多是执行轨迹的一部分。

从工程角度看，Structured Output 的价值有三个：

- 让输出格式有契约；
- 减少后续手工解析；
- 让模型错误更早暴露在 schema 校验阶段。

### State：短期记忆不是模型在“记”，而是运行时在管

在 LangChain 的当前主线里，`State` 是理解 Agent 运行方式时非常关键的概念。它常常和 `memory` 混着说，但更准确的说法是：

**State 就是 Agent 在当前线程中的短期运行数据。**

默认最重要的 state 字段是 `messages`，也就是当前会话的消息历史。但这只是起点。你还可以往 state 里加很多业务字段，比如：

- `user_id`
- `authenticated`
- `preferences`
- `current_task`
- 某个中间检索结果
- 某个审批状态

下面是一个自定义 `AgentState` 的最小例子：

```python
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model

class CustomAgentState(AgentState):
    user_id: str
    authenticated: bool = False
    preferences: dict = {}

model = init_chat_model("openai:gpt-4.1-mini")

agent = create_agent(
    model=model,
    tools=[],
    state_schema=CustomAgentState,
    checkpointer=InMemorySaver(),
)
```

这里需要特别澄清一个常见误解：State 不是由 LLM 直接持有和写回的。更准确地说，State 的控制权在运行时。你可以把参与者分成四层：

- **LangChain runtime**：负责 state 的读取、更新、合并和持久化；
- **LLM**：只会看到 runtime 给它的那部分上下文，比如 messages；它不会直接操作 Python 里的 state；
- **tools / middleware**：可以通过正式接口读取 state，或者在受控位置更新 state；
- **checkpointer**：负责把 state 保存下来，在同一 thread 继续时再恢复。

所以，“模型有记忆”在 LangChain 里通常只是一个表面说法。更精确的说法应该是：**运行时在管理会话状态，模型只是在每次调用时消费其中的一部分上下文。**

![LangChain Short-term Memory](http://public.file.lvshuhuai.cn/images\langchain-short-term-memory-summary.png)

下面这个例子展示了同一个 `thread_id` 下 state 如何被持续复用：

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4.1-mini")

agent = create_agent(
    model=model,
    tools=[],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "thread-1"}}

result1 = agent.invoke(
    {"messages": [{"role": "user", "content": "My name is Alice."}]},
    config,
)

result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "What is my name?"}]},
    config,
)

print(result2["messages"][-1].content)
```

这段代码真正想说明的不是“模型好像记住了名字”，而是：

- 这两次调用使用了同一个 `thread_id`；
- 运行时通过 `checkpointer` 保存并恢复了状态；
- 第二次调用时，messages 历史仍然存在于当前线程 state 中。

### Middleware：横切控制不要塞进工具函数里

如果说 Tool 提供的是业务能力，那么 `Middleware` 提供的就是运行时控制能力。它的本质不是“再写一个函数”，而是把原本会散落在工具函数和主流程里的横切逻辑，集中放到正式拦截点里。

典型的 middleware 职责包括：

- 日志和调试；
- prompt 动态改写；
- 动态筛选工具；
- 输出格式调整；
- 重试和 fallback；
- 限流、权限控制、审批；
- guardrails；
- 状态更新。

最简单的例子，是包一层模型调用日志：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model

@wrap_model_call
def log_model_call(request: ModelRequest, handler) -> ModelResponse:
    print("Before model call")
    response = handler(request)
    print("After model call")
    return response

model = init_chat_model("openai:gpt-4.1-mini")
agent = create_agent(
    model=model,
    tools=[],
    middleware=[log_model_call],
)
```

这段代码虽然简单，但已经体现了 middleware 的核心：它不是在“替代模型”，而是在模型调用前后插入控制。

![LangChain Middleware](http://public.file.lvshuhuai.cn/images\langchain-middleware-final.png)

如果要做更有代表性的事情，可以让 middleware 基于 state 动态裁剪工具集：

```python
from typing import Callable
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.tools import tool
from langchain.chat_models import init_chat_model

@tool
def public_search(query: str) -> str:
    """Search public information."""
    return f"public results for {query}"

@tool
def private_search(query: str) -> str:
    """Search private internal information."""
    return f"private results for {query}"

@wrap_model_call
def filter_tools_by_auth(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    state = request.state
    authenticated = state.get("authenticated", False)

    if not authenticated:
        tools = [t for t in request.tools if t.name == "public_search"]
        request = request.override(tools=tools)

    return handler(request)

model = init_chat_model("openai:gpt-4.1-mini")
agent = create_agent(
    model=model,
    tools=[public_search, private_search],
    middleware=[filter_tools_by_auth],
)
```

这个例子非常接近真实项目：

- Tool 本身仍然各自职责清晰；
- 权限控制不写死在每个工具函数里；
- Runtime 在模型调用前，根据 state 决定哪些工具对模型可见。

这就是中大型 Agent 应用里 middleware 的真实价值所在。

## Context engineering：不是写 prompt，而是管理上下文流动

很多人会把 prompt engineering 当作“与模型交互的全部艺术”，但在 LangChain 里，这个理解明显太窄。因为真正决定系统是否稳定的，常常不是一段 prompt 写得多华丽，而是：

- 模型这次调用前看见了什么；
- 工具这次调用时读到了什么；
- 哪些信息只是本次临时使用，哪些要持久写回状态。

这就是 `Context engineering` 的核心问题。

更准确地说，Context engineering 可以拆成三层：

- **Model Context**：模型调用时看到的 prompt、messages、tools、response format 等；
- **Tool Context**：工具调用时能访问的 state、store、runtime context；
- **Life-cycle Context**：调用前后以及调用之间，对上下文进行压缩、审查、记录、总结、改写等控制。

一个很简单但极其有代表性的例子，是根据 state 动态改 system prompt：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.chat_models import init_chat_model

@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    message_count = len(request.messages)
    base = "You are a helpful assistant."

    if message_count > 10:
        base += "\nThis is a long conversation. Be extra concise."

    return base

model = init_chat_model("openai:gpt-4.1-mini")
agent = create_agent(
    model=model,
    tools=[],
    middleware=[state_aware_prompt],
)
```

这个例子看似只是“动态 prompt”，但它已经包含了 Context engineering 的关键思想：

- 不同调用轮次，不该给模型完全相同的上下文；
- 某些变化只作用于当前 model call；
- 这些变化未必要写回持久 state。

再进一步，如果你需要基于用户角色或环境变量调整模型行为，可以通过 runtime context 注入调用时配置：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.chat_models import init_chat_model

@dataclass
class AppContext:
    user_role: str
    deployment_env: str

@dynamic_prompt
def context_aware_prompt(request: ModelRequest) -> str:
    role = request.runtime.context.user_role
    env = request.runtime.context.deployment_env

    prompt = "You are a helpful assistant."

    if role == "admin":
        prompt += "\nYou may discuss admin-level operations."
    else:
        prompt += "\nDo not suggest privileged operations."

    if env == "production":
        prompt += "\nBe conservative about destructive actions."

    return prompt

model = init_chat_model("openai:gpt-4.1-mini")
agent = create_agent(
    model=model,
    tools=[],
    middleware=[context_aware_prompt],
    context_schema=AppContext,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Delete the record."}]},
    context=AppContext(user_role="viewer", deployment_env="production"),
)
```

这个例子说明：**上下文不仅是对话内容，还包括调用时的静态环境、角色、权限信息。**

还可以做得更实际一点：根据 state 中的文件列表，在模型调用前临时注入“当前可用资料摘要”。这类做法比“永远把所有文件说明塞进 prompt”更像真正的工程实现。

## 把外部知识接进来：Retrieval 与 Multi-agent

LangChain 的很多 Agent 之所以有用，并不是因为模型本身知道一切，而是因为它们能够在运行时访问外部知识或把任务拆给更合适的组件。在这方面，最重要的两个主题就是 `Retrieval` 和 `Multi-agent`。

### Retrieval：不是“向量库”，而是一整条知识接入链

`Retrieval` 的核心目标，是根据当前问题，从外部知识中检索出最相关的信息片段，再把这些片段交给模型使用。向量检索只是最常见的一种底层手段，真正要掌握的，是这条完整链路：

1. 原始数据变成 `Document`；
2. 文档切块；
3. 通过 embedding 建立可搜索表示；
4. 存进 vector store；
5. 通过 `Retriever` 按 query 取回最相关的 chunks；
6. 将这些结果纳入 prompt 或 Agent 执行过程。

![LangChain RAG Indexing](http://public.file.lvshuhuai.cn/images\langchain-rag-indexing.png)

![LangChain RAG Retrieval and Generation](http://public.file.lvshuhuai.cn/images\langchain-rag-retrieval-generation.png)

最小骨架如下：

```python
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 1. 准备文档
raw_docs = [
    Document(page_content="LangChain retrieval finds relevant information for a query.", metadata={"source": "note-1"}),
    Document(page_content="A retriever returns documents for downstream generation.", metadata={"source": "note-2"}),
]

# 2. 切块
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
chunks = splitter.split_documents(raw_docs)

# 3. 向量化并建立存储
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = Chroma.from_documents(chunks, embedding=embeddings)

# 4. 构造 retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# 5. 检索
results = retriever.invoke("What is retrieval?")
for doc in results:
    print(doc.metadata, doc.page_content)
```

这里真正应该记住的，是 Retriever 的抽象地位：

- vector store 是底层存储和搜索能力；
- retriever 是上层统一检索接口；
- 应用层大多数时候应该围绕 retriever 写逻辑，而不是把自己绑死在某个具体向量库 API 上。

在 LangChain 中，最常见的 Retrieval 用法，是 [[检索增强生成 RAG]]。RAG 又有两种主线形态：

- **2-step RAG chain**：固定先检索，再生成；
- **RAG agent**：把检索包装成 tool，让 Agent 自己决定何时检索。

先看 2-step RAG：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4.1-mini")

question = "What is retrieval?"
docs = retriever.invoke(question)
context = "\n\n".join(doc.page_content for doc in docs)

prompt = f"""Answer the question using only the context below.

Context:
{context}

Question:
{question}
"""

response = model.invoke(prompt)
print(response.content)
```

这种方式简单、可预测、延迟低，适合“几乎每次都要查资料”的固定知识问答场景。

如果你希望模型自己决定什么时候查资料，就把检索包装成工具，交给 Agent：

```python
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    docs = retriever.invoke(query)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in docs
    )
    return serialized, docs

model = init_chat_model("openai:gpt-4.1-mini")
agent = create_agent(
    model=model,
    tools=[retrieve_context],
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What is task decomposition?"}
    ]
})

print(result["messages"][-1].content)
```

这时 retrieval 已经不再是固定步骤，而是 Agent 决策过程的一部分了。

### Multi-agent：不是“更多模型”，而是更细的职责与上下文分工

单 Agent 并不是总能优雅承载所有复杂任务。如果工具越来越多、领域越来越杂、上下文越来越大，一个大而全的 Agent 往往会开始变笨。`Multi-agent` 的意义就在于：把一个难以由单 Agent 稳定完成的任务，拆成多个更窄、更专门的组成部分。

不过，这里必须先强调一个判断：**不是任务复杂，就一定要上 Multi-agent。** 很多场景下，先做好单 Agent 的工具设计、状态设计和上下文裁剪，比直接拆多 Agent 更有效。真正适合 Multi-agent 的情形，通常包括：

- 工具集合太大，模型选工具开始明显漂移；
- 不同领域需要完全不同的上下文和系统约束；
- 子任务天然可并行；
- 不同模块由不同团队维护，想降低耦合。

在 LangChain 主线里，常见的 Multi-agent 组织方式有四种：

- **Subagents**：主 Agent 把子 Agent 当工具调用；
- **Handoffs**：当前活跃 Agent 真正发生切换；
- **[[Skills]]**：还是一个 Agent，但按需加载专业上下文；
- **Router**：先做路由，再分发给专门 Agent。

![LangChain Subagents Pattern](http://public.file.lvshuhuai.cn/images\langchain-multi-agent-subagents.png)

![LangChain Handoffs Pattern](http://public.file.lvshuhuai.cn/images\langchain-multi-agent-handoffs.png)

![LangChain Router Pattern](http://public.file.lvshuhuai.cn/images\langchain-multi-agent-router.png)

对大多数初学者而言，最适合先掌握的是 Subagents，因为它最接近你已经学过的 Tool 和 Agent 模型。下面是一个 supervisor + specialists 的最小骨架：

```python
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4.1-mini")

calendar_agent = create_agent(
    model=model,
    tools=[],
    system_prompt="You handle calendar and scheduling tasks only."
)

email_agent = create_agent(
    model=model,
    tools=[],
    system_prompt="You handle email drafting tasks only."
)

@tool
def ask_calendar_agent(query: str) -> str:
    """Delegate calendar-related tasks to the calendar specialist."""
    result = calendar_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    return result["messages"][-1].content

@tool
def ask_email_agent(query: str) -> str:
    """Delegate email-related tasks to the email specialist."""
    result = email_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    return result["messages"][-1].content

supervisor = create_agent(
    model=model,
    tools=[ask_calendar_agent, ask_email_agent],
    system_prompt="Delegate tasks to the correct specialist and synthesize the final answer."
)

result = supervisor.invoke({
    "messages": [
        {"role": "user", "content": "Check my schedule tomorrow and draft a follow-up email."}
    ]
})

print(result["messages"][-1].content)
```

这个例子非常适合作为 Multi-agent 的起点，因为它把核心思想暴露得很清楚：

- 子 Agent 不直接面向用户；
- 它们被“工具化”；
- 主 Agent 作为监督者进行调度；
- 最终结果仍由主 Agent 统一组织输出。

## 一个最小可运行的 LangChain Agent：从配置到执行完整走一遍

前面讲了很多对象和机制，但如果没有一个完整、可运行、稍微像样的例子，知识很容易停留在“看懂了名词”。下面给一个最小但完整的 Agent 示例，满足几个要求：

- 使用 `.env` 管理配置；
- 显式通过[[OpenAI-compatible API]] 初始化模型；
- 提供两个工具：天气查询和简单计算；
- 使用 `create_agent(...)` 构建一个真实可跑的 Agent。

### .env` 配置

```env
OPENAI_API_KEY=你的真实APIKey
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=
```

如果你使用的是 OpenAI 官方接口，`OPENAI_BASE_URL` 可以留空；如果你使用兼容 OpenAI API 的网关，就把它填成对应的 base URL，例如：

```env
OPENAI_API_KEY=你的真实APIKey
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=https://your-provider.example.com/v1
```

### 安装依赖

```powershell
uv add langchain langchain-openai python-dotenv
```

### 完整代码

```python
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI


def load_config() -> tuple[str, str, str | None]:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None

    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in .env")
    if not model:
        raise ValueError("Missing OPENAI_MODEL in .env")

    return api_key, model, base_url


def build_model() -> ChatOpenAI:
    api_key, model, base_url = load_config()

    kwargs: dict[str, Any] = {
        "model": model,
        "api_key": api_key,
        "temperature": 0,
    }

    if base_url:
        kwargs["base_url"] = base_url

    return ChatOpenAI(**kwargs)


@tool
def get_weather(city: str) -> str:
    """Get current weather information for a city."""
    fake_weather_db = {
        "beijing": "Beijing: sunny, 26C",
        "shanghai": "Shanghai: cloudy, 23C",
        "tokyo": "Tokyo: rainy, 19C",
        "new york": "New York: windy, 17C",
    }

    key = city.strip().lower()
    return fake_weather_db.get(key, f"No weather data found for {city}.")


@tool
def calculate(expression: str) -> str:
    """Evaluate a simple arithmetic expression like '12 * (3 + 4)'."""
    allowed_chars = set("0123456789+-*/(). %")
    if not set(expression) <= allowed_chars:
        return "Error: expression contains unsupported characters."

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def main() -> None:
    model = build_model()

    agent = create_agent(
        model=model,
        tools=[get_weather, calculate],
        system_prompt=(
            "You are a helpful assistant. "
            "Use tools when needed. "
            "For weather questions, use get_weather. "
            "For arithmetic, use calculate."
        ),
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "北京天气怎么样？顺便算一下 12 * (3 + 4)。"
                }
            ]
        }
    )

    print("=== Final answer ===")
    print(result["messages"][-1].content)

    print("\n=== Trace ===")
    for i, msg in enumerate(result["messages"], start=1):
        print(f"[{i}] {type(msg).__name__}")
        print(getattr(msg, "content", None))
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            print("tool_calls =", tool_calls)
        print("------")


if __name__ == "__main__":
    main()
```

### 这份代码到底在做什么

这份示例虽然不大，但完整地覆盖了 LangChain 主线里最值得掌握的几个点：

- 用 `dotenv` 管理环境变量，而不是把密钥写死在代码里；
- 用 `ChatOpenAI` 明确构造模型对象；
- 用 `@tool` 定义清晰的工具接口；
- 用 `create_agent(...)` 将模型、工具和 system prompt 接成 Agent；
- 用 `messages` 作为输入载体，而不是直接传一个裸字符串；
- 打印完整执行轨迹，而不仅是最终答案。

如果你现在要做自己的第一个 LangChain 项目，这个例子就是一个非常合适的骨架。接下来通常有三种自然扩展方向：

1. 把 `fake_weather_db` 换成真实 API；
2. 给 Agent 加 `response_format`，让结果结构化；
3. 加 `checkpointer` 和 `thread_id`，让对话状态真正延续。
