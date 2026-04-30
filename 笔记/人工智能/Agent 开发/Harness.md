# Harness

## 先把问题说清楚：Harness 到底是什么

在 Agent 工程语境里，**harness 不是编程语言，也不是某个固定工具，更不是某个框架的专属概念**。它首先是一种架构思想，也可以指这种思想被实现出来之后的那套工程代码。

最短定义是：

> **Harness 是包在 LLM 外面、负责驱动模型完成任务的外部运行结构。**

换句话说，LLM 本身只负责生成、推理、选择下一步动作。它不会天然拥有工具，不会天然知道什么时候停止，不会天然保存任务状态，也不会天然负责错误重试、权限控制、日志记录、人工审批。所有这些模型外面的运行机制，都属于 harness 的范畴。

现在很多文章会用一个简化公式：

```text
Agent = Model + Harness
```

![Augmented LLM](http://public.file.lvshuhuai.cn/images\harness-anthropic-augmented-llm.png)

这句话并不是在否定你之前学过的：

```text
Agent = LLM + Tool + Loop + Memory + State + Prompt + ...
```

两者其实是同一件事的两种表达。

更完整地展开：

```text
Agent
= Model + Harness

Harness
= Prompt
  + Tool Schema
  + Tool Executor
  + Agent Loop
  + Memory
  + State
  + Context Management
  + Policy / Guardrails
  + Error Handling
  + Logging / Tracing
  + Human Approval
  + Runtime Environment
  + ...
```

所以：

```text
Agent
= Model
  + Prompt
  + Tool Schema
  + Tool Executor
  + Loop
  + Memory
  + State
  + Policy
  + Logging
  + Error Handling
  + ...
```

你之前说的 “Agent 就是 LLM + tool + loop + memory + 很多东西” 是对的。现在引入 harness，只是为了把“除了模型之外的很多东西”抽象成一个更清晰的工程层。

### 为什么需要 harness 这个词

如果只说 “Agent = LLM + Tools + Memory + Loop”，问题是组件越来越多之后，表达会变得很散。一个真实 Agent 里通常还有：

- prompt 模板；
- 工具定义；
- 工具参数 schema；
- 工具执行器；
- 工具返回值清洗；
- 对话历史压缩；
- 长期记忆；
- 状态持久化；
- 文件系统；
- 沙箱；
- 运行日志；
- trace；
- 错误重试；
- 人工审批；
- 安全策略；
- 成本控制；
- 多 Agent handoff；
- 任务队列；
- 中断与恢复机制。

这些东西不属于模型本体，但又共同决定 Agent 能不能稳定工作。因此，harness 这个词的价值在于：它把这些零散的“模型外部工程结构”统一命名为一个层。

可以这样理解：

```text
LLM 是智能来源。
Harness 是把智能转化为可控行动的结构。
Agent 是 LLM + Harness 之后形成的完整系统。
```

这也是为什么很多工程问题并不能靠“换一个更强模型”解决。模型能力决定上限的一部分，而 harness 决定这个能力能不能被稳定、可控、可观测地转化为任务结果。

## Harness 与 Agent、框架、工具、Workflow 的边界

### Harness 和 Agent：内部结构与外部成品

最容易混淆的是 harness 和 Agent。

**Agent 是对外表现出来的完整系统。**

比如一个论文阅读 Agent、客服 Agent、代码修复 Agent、个人助理 Agent。用户感知到的是“这个东西能做任务”。

**Harness 是 Agent 内部除模型之外的运行外壳。**

它是让模型真正“跑起来、调工具、循环、记状态、停下来”的那套机制。

可以用下面的表来区分：

![LangChain Agent Loop](http://public.file.lvshuhuai.cn/images\harness-langchain-core-agent-loop.png)

| 概念 | 它是什么 | 关注点 |
|---|---|---|
| LLM / Model | 语言模型本体 | 理解、推理、生成、选择动作 |
| Harness | 模型外部运行结构 | 怎么组织上下文、工具、循环、状态、规则 |
| Agent | LLM + Harness 的完整系统 | 对外是否能自主或半自主完成任务 |
| Framework | 帮你构建 harness 的开发框架 | 提供抽象、API、运行时、组件 |
| Tool | Agent 可以调用的外部能力 | 查询、计算、搜索、读写文件、调用 API |
| Workflow | 一种更确定的流程编排方式 | 步骤明确、路径可控、业务规则清晰 |

一句话：

```text
Agent 是“成品系统”。
Harness 是“成品系统内部的运行外壳”。
Framework 是“帮你写这个运行外壳的工具箱”。
Tool 是“这个运行外壳可以调用的外部能力”。
Workflow 是“这个运行外壳的一种编排形态”。
```

### Harness 是思想，还是代码

它两者都是，但要分层看。

```text
思想层：
Harness 是“要在模型外面构建运行结构”的架构思想。

实现层：
Harness 是你实际写出来的 prompt、tool loop、state、memory、executor、policy 等代码。

系统层：
LLM 加上这个 harness 实现，对外形成 Agent。
```

因此，说“用 harness 思想能够建立 Agent”是对的，但更准确的表达是：

> **用 harness 思想设计并实现模型外部运行结构，再与 LLM 组合，就能构建 Agent。**

只有思想不够，必须落到代码和运行机制上。

### 所有 Agent 都用了 harness 思想吗

只要它是真正意义上的 Agent，基本都隐含使用了 harness 思想。区别只在于复杂程度不同，以及开发者是否显式使用 “harness” 这个词。

最小 harness 可能只有：

```text
Prompt + Tool Schema + Tool Executor + 一轮工具调用
```

典型 harness 会有：

```text
Prompt
Tool Schema
Tool Executor
Agent Loop
Memory
State
Stop Condition
Error Handling
Logging
```

生产级 harness 会继续加入：

```text
权限控制
人工审批
长期记忆
任务队列
状态持久化
沙箱运行环境
多 Agent 协作
Trace / Observability
失败重试
成本控制
安全策略
评估系统
```

判断一个系统有没有 harness，可以看它是否在模型外部做了这些事：

1. 是否把用户输入、系统提示词、历史状态组织成模型输入；
2. 是否把工具 schema 注入给模型；
3. 是否能解析模型输出中的工具调用；
4. 是否真正执行工具，而不是让模型“假装执行”；
5. 是否把工具结果回填给模型；
6. 是否能控制循环次数、停止条件、错误重试；
7. 是否维护状态、日志、权限和安全边界。

如果答案是肯定的，那么它已经有 harness，只是可能没有这样命名。

### Harness 和 Workflow 的区别

Workflow 是一种流程组织方式，harness 是更大的运行外壳。

![Prompt Chaining Workflow](http://public.file.lvshuhuai.cn/images\harness-anthropic-prompt-chaining.png)

Workflow 关注的是：

```text
任务先做 A，再做 B；
如果 B 失败，走 C；
如果结果需要审批，暂停；
审批通过后继续 D。
```

Harness 关注的是：

```text
模型怎么接收上下文；
工具怎么暴露给模型；
模型怎么发起工具调用；
工具结果怎么回填；
状态怎么保存；
错误怎么处理；
流程如何被驱动；
日志怎么记录；
权限怎么限制。
```

所以 workflow 可以是 harness 的一部分。一个 Agent harness 里可以有 workflow，也可以有更自由的 agent loop。

典型区别如下：

| 维度 | Workflow | Harness |
|---|---|---|
| 抽象层级 | 流程层 | 运行外壳层 |
| 是否必须有 LLM | 不一定 | 通常围绕 LLM/Agent 建立 |
| 是否包含工具执行 | 可以包含 | 通常包含 |
| 是否包含状态管理 | 可以包含 | 通常包含 |
| 是否包含 prompt/context 管理 | 不一定 | 通常包含 |
| 是否包含安全策略 | 不一定 | 生产级 harness 必须考虑 |
| 作用 | 定义任务路径 | 驱动模型完成任务 |

一个简单说法：

```text
Workflow 是“任务怎么走”。
Harness 是“模型怎么被驱动着走完整个任务”。
```

### Harness 和框架的区别

[LangChain](https://docs.langchain.com/oss/python/langchain/overview)、[LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)、[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)、AutoGen、CrewAI、Coze、OpenClaw 等，都不是 harness 这个词本身。它们是构建 Agent 或 Agent harness 的框架、平台、SDK 或产品。

例如：

```text
LangGraph = 帮你构建有状态、多节点、可恢复 agent/workflow 的框架。
你用 LangGraph 写出来的 graph、state、node、edge、tool loop、checkpoint 组合 = 一个 harness 实现。
这个 harness 加上模型，对外形成的论文助手/客服助手/代码助手 = Agent。
```

再比如：

```text
OpenAI Agents SDK = 构建 agent、tools、handoffs、guardrails 的 SDK。
你基于 SDK 配出来的工具、运行规则、handoff、guardrail、session = harness 的一部分。
对外暴露的任务型助手 = Agent。
```

因此不要把层级混掉：

```text
框架不是 harness 本身。
框架是帮助你构建 harness 的工具。
harness 是你最终形成的运行结构。
Agent 是运行结构与模型组合后的完整系统。
```

## Harness 的核心组件：它到底包住了什么

一个 Agent harness 不一定拥有所有组件，但理解这些组件有助于你判断一个 Agent 系统是否完整。

### Prompt 与上下文组织

Prompt 不是单纯的一段提示词。在 Agent harness 中，prompt 更像是上下文装配系统的一部分。

一个 harness 通常要组织：

- system prompt：Agent 的角色、行为边界、风格、权限；
- developer prompt：开发者约束、业务规则、工具使用规则；
- user message：用户当前请求；
- conversation history：历史对话；
- retrieved context：检索得到的外部资料；
- memory：长期或短期记忆；
- tool descriptions：工具能力说明；
- output schema：要求模型输出的结构；
- state summary：当前任务进展摘要。

裸模型只接受输入。Harness 负责决定“什么信息应该进入输入、以什么顺序进入、压缩到什么程度、哪些信息不能进入”。

例如，论文阅读 Agent 的上下文组织可能是：

```text
System:
你是一个学术论文阅读助手，必须引用原文证据。

State:
当前论文已读到 Method 部分，用户关注模型结构和损失函数。

Retrieved Context:
- Section 3.1: Model Architecture ...
- Section 3.2: Contrastive Loss ...

Tools:
- read_pdf_page(page)
- search_in_paper(keyword)
- summarize_section(section_id)

User:
帮我解释这个方法和 CLIP 的区别。
```

如果没有 harness，模型只会看到用户一句话。

有了 harness，模型看到的是“任务所需的结构化上下文”。

### Tool Schema 与 Tool Executor

Tool calling 的关键不是“模型真的会调用工具”。模型不会直接执行 Python 函数、访问数据库、读取文件。模型只是输出一个结构化意图，比如：

![Routing Workflow](http://public.file.lvshuhuai.cn/images\harness-anthropic-routing.png)

```json
{
  "tool_name": "search_paper",
  "arguments": {
    "keyword": "contrastive loss"
  }
}
```

真正执行工具的是 harness。

因此工具相关部分至少分成两层：

```text
Tool Schema:
告诉模型有哪些工具、每个工具需要什么参数、什么时候适合使用。

Tool Executor:
接收模型发出的工具调用，校验参数，真正执行函数/API/数据库查询，然后把结果返回给模型。
```

典型结构如下：

```text
模型看到：
search_paper(keyword: string) -> SearchResult[]

Harness 内部实际执行：
result = search_paper(keyword="contrastive loss")
```

这就解释了为什么 Tool Calling 是 Agent 的分水岭：模型一旦能通过 harness 调用外部工具，它就不只是文本生成器，而开始具备“行动能力”。

但也要强调：

```text
Tool 是能力。
Tool Schema 是能力说明。
Tool Executor 是能力执行器。
Harness 负责把 schema 给模型看，并在模型请求时执行工具。
Agent 是模型通过 harness 使用工具完成任务的完整系统。
```

### Agent Loop：让任务从一次回答变成多步执行

Agent 和普通 chatbot 的核心差异之一，是是否存在 loop。

普通 chatbot 通常是：

```text
用户输入 -> 模型回答 -> 结束
```

Agent loop 通常是：

```text
用户输入
  -> harness 组织上下文和工具
  -> 模型判断下一步
  -> 如果需要工具，harness 执行工具
  -> 工具结果回填
  -> 模型继续判断
  -> 直到生成最终答案 / 达到限制 / 请求人工审批 / 失败终止
```

用伪代码表示：

```python
def run_agent(user_input):
    state = init_state(user_input)

    for step in range(MAX_STEPS):
        messages = build_context(state)
        response = model.chat(messages=messages, tools=tool_schemas)

        if response.type == "final_answer":
            return response.content

        if response.type == "tool_call":
            tool_result = execute_tool(
                name=response.tool_name,
                arguments=response.arguments
            )
            state.add_tool_result(tool_result)
            continue

        if response.type == "need_human_approval":
            pause_and_request_approval(state)
            return

    raise RuntimeError("Agent exceeded max steps")
```

这里的 `build_context`、`tool_schemas`、`execute_tool`、`state.add_tool_result`、`MAX_STEPS`、`pause_and_request_approval` 都是 harness 的一部分。

![Parallelization Workflow](http://public.file.lvshuhuai.cn/images\harness-anthropic-parallelization.png)

模型只做一件事：根据当前上下文决定下一步输出。

Harness 做的是：把这个决定接到真实世界，并让下一步继续发生。

### Memory 与 State：不要混成一件事

很多人说 Agent 有 memory，但工程上要区分 memory 和 state。

**State 是任务运行中的当前状态。**

它关心的是“当前任务进行到哪一步”。

例如：

```json
{
  "task_id": "paper_reading_001",
  "current_section": "Method",
  "read_pages": [1, 2, 3, 4, 5],
  "pending_question": "explain contrastive loss",
  "tool_calls": [
    {"name": "search_in_pdf", "keyword": "InfoNCE"}
  ]
}
```

**Memory 是跨任务或跨对话保存的信息。**

它关心的是“以后还能不能复用”。

例如：

```json
{
  "user_preference": {
    "language": "Chinese",
    "code_style": "keep hyperparameters at top of script",
    "research_topic": "multi-image long-text alignment"
  }
}
```

二者都可以进入 harness，但用途不同：

| 概念 | 时间范围 | 作用 |
|---|---|---|
| State | 当前 run / 当前任务 | 保证任务能连续执行 |
| Short-term memory | 当前会话 | 保持上下文连续 |
| Long-term memory | 跨会话 | 复用用户偏好、项目背景 |
| External memory | 数据库/向量库/文件 | 保存可检索资料 |

Harness 负责决定：

- 当前 state 怎么更新；
- 哪些 memory 可以写入；
- 哪些 memory 可以读取；
- 读取后的 memory 怎么注入上下文；
- state 太长时怎么压缩；
- 任务中断后如何恢复。

没有 state，Agent 很难多步执行。

没有 memory，Agent 很难长期适配用户。

没有 harness，state 和 memory 都只是散落的数据，不能稳定参与模型运行。

### Policy、Guardrails 与 Human Approval

生产级 Agent 不能只关心“能不能完成任务”，还要关心“能不能安全、合规、可控地完成任务”。

![Evaluator Optimizer Workflow](http://public.file.lvshuhuai.cn/images\harness-anthropic-evaluator-optimizer.png)

Harness 通常需要加入 policy 和 guardrails，例如：

- 输入校验：用户请求是否越权、是否包含危险操作；
- 输出校验：模型输出是否符合格式、是否包含敏感内容；
- 工具校验：工具调用参数是否合法；
- 权限控制：当前用户是否允许调用这个工具；
- 影响范围控制：删除、支付、发邮件、改数据库等操作是否需要审批；
- 人工确认：高风险行为必须暂停，等待用户或管理员确认；
- 失败策略：失败后重试、降级、终止还是请求人工介入。

比如一个邮件 Agent：

```text
低风险：
读取最近 5 封邮件 -> 允许自动执行

中风险：
生成邮件草稿 -> 允许自动执行，但不发送

高风险：
发送邮件给客户 -> 必须人工确认

危险操作：
批量删除邮件 -> 默认禁止或二次确认
```

这部分不属于 LLM 本体，而是 harness 的控制能力。

### Logging、Tracing 与 Evaluation

Agent 系统调试非常依赖日志和追踪。因为一个错误结果可能来自很多地方：

- prompt 写得不清楚；
- 工具 schema 设计不好；
- 模型选择了错误工具；
- 工具参数错误；
- 工具本身返回脏数据；
- 工具结果回填格式不好；
- state 更新错误；
- 循环停止条件错误；
- memory 注入了过期信息；
- guardrail 过强或过弱。

因此 harness 需要记录：

```text
用户输入是什么；
模型看到的上下文是什么；
模型输出了什么；
调用了哪个工具；
工具参数是什么；
工具返回了什么；
状态如何变化；
最终答案是什么；
是否经过人工审批；
花费了多少 token / 时间 / 成本；
是否命中错误或重试。
```

这就是 tracing / observability 的意义。  
它不是锦上添花，而是 Agent 工程可维护性的基础。

![LangChain Middleware](http://public.file.lvshuhuai.cn/images\harness-langchain-middleware.png)

## 最小实现：从代码角度看 harness

下面用一个极简例子说明 harness 的本质。它不是完整生产代码，但能看清边界。

### 裸 LLM：没有 harness 的情况

```python
answer = model.chat("帮我查一下今天新加坡天气")
print(answer)
```

这不是 Agent。因为模型没有真实天气工具，也没有状态、循环、错误处理。它只能根据训练知识或上下文猜。

### 最小 harness：给模型工具、执行工具、回填结果

```python
tools = {
    "get_weather": get_weather,
}

tool_schemas = [
    {
        "name": "get_weather",
        "description": "查询指定城市的实时天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    }
]

def run_agent(user_input):
    messages = [
        {"role": "system", "content": "你是一个可以调用工具的助手。"},
        {"role": "user", "content": user_input},
    ]

    for step in range(5):
        response = model.chat(messages=messages, tools=tool_schemas)

        if response["type"] == "final":
            return response["content"]

        if response["type"] == "tool_call":
            tool_name = response["tool_name"]
            args = response["arguments"]

            result = tools[tool_name](**args)

            messages.append({
                "role": "tool",
                "name": tool_name,
                "content": str(result)
            })

    return "任务未在限定步数内完成。"
```

这里的 harness 包括：

- system prompt；
- tool schema；
- 工具注册表；
- 工具执行器；
- messages 状态；
- loop；
- 最大步数限制；
- 工具结果回填。

模型本身只在 `model.chat(...)` 里。

其余全部是 harness。

### Java 风格的结构拆分

如果用 Java/SpringBoot 思维，可以把 harness 拆成几个类：

```java
public class AgentRunner {

    private final ChatModel model;
    private final ToolRegistry toolRegistry;
    private final ContextBuilder contextBuilder;
    private final AgentStateStore stateStore;

    public AgentResult run(String userInput) {
        AgentState state = stateStore.create(userInput);

        for (int step = 0; step < 5; step++) {
            List<Message> messages = contextBuilder.build(state);
            List<ToolSchema> schemas = toolRegistry.schemas();

            ModelResponse response = model.chat(messages, schemas);

            if (response.isFinalAnswer()) {
                return AgentResult.success(response.content());
            }

            if (response.isToolCall()) {
                ToolCall call = response.toolCall();

                ToolResult result = toolRegistry.execute(
                    call.name(),
                    call.arguments()
                );

                state.addToolResult(call, result);
                stateStore.save(state);
                continue;
            }
        }

        return AgentResult.failed("Exceeded max steps");
    }
}
```

在这个结构里：

```text
ChatModel        = 模型接口
ToolRegistry     = 工具注册与执行
ContextBuilder   = prompt/context 组织
AgentStateStore  = 状态保存
AgentRunner      = agent loop
```

这些共同构成 harness。

`AgentRunner` 不是模型，它是模型外部的运行控制器。

## MCP 放在 Harness 里的什么位置

[MCP](https://modelcontextprotocol.io/introduction)，即 Model Context Protocol，不是 harness 本身。它更像是 harness 连接外部工具、资源和提示模板的一种标准协议。

MCP 服务器通常暴露三类能力：

```text
Tools:
模型可以请求执行的函数或动作。

Resources:
可以提供给模型使用的上下文和数据，例如文件、数据库 schema、文档内容。

Prompts:
可复用的提示模板或交互模板。
```

从 harness 的角度看：

```text
Harness
  -> 连接 MCP Client
  -> 发现 MCP Server 暴露的 tools/resources/prompts
  -> 把 tools schema 提供给模型
  -> 在模型请求工具调用时，通过 MCP 调用 server
  -> 读取 resources 作为上下文
  -> 使用 prompts 作为模板
```

所以 MCP 的位置可以这样理解：

```text
Tool / Resource / Prompt 的标准暴露方式 = MCP

把 MCP 暴露出来的能力组织进模型运行循环 = Harness

模型 + Harness + MCP 能力 = 更完整的 Agent
```

不要把 MCP 和 harness 混成一件事：

| 概念 | 作用 |
|---|---|
| MCP | 标准化连接外部能力 |
| Harness | 组织模型运行、工具调用、状态、流程和控制 |
| Agent | 模型通过 harness 使用这些能力完成任务 |
| MCP Server | 暴露工具、资源、提示模板 |
| MCP Client | 被 harness 或应用使用，用来连接 MCP Server |

举个例子：

```text
你有一个文件系统 MCP Server。
它暴露：
- read_file(path)
- list_dir(path)
- search_files(keyword)

Harness 会：
1. 发现这些工具；
2. 把工具说明提供给模型；
3. 当模型请求 read_file 时，通过 MCP client 调用 MCP server；
4. 把文件内容作为工具结果回填；
5. 让模型继续分析。
```

此时：

```text
文件系统 MCP Server 不是 Agent。
MCP 协议不是 Agent。
Harness 使用 MCP 提供的工具能力。
LLM + Harness + 文件系统工具能力，才形成能读文件的 Agent。
```

## 从工程角度设计一个 Harness

设计 harness 时，不要先问“我要用哪个框架”，而应该先问“模型外面需要哪些机制”。

### 一个基本设计模板

可以按以下结构拆：

```text
1. Model Layer
   - 用哪个模型
   - 是否支持 tool calling
   - 是否支持 structured output
   - 是否支持多模态输入
   - 上下文窗口多大

2. Context Layer
   - system prompt
   - user message
   - history
   - retrieved context
   - memory
   - state summary
   - tool descriptions

3. Tool Layer
   - 工具列表
   - 参数 schema
   - 参数校验
   - 工具执行
   - 返回值规范化
   - 错误处理

4. Loop Layer
   - 最大步数
   - 停止条件
   - 是否允许连续工具调用
   - 是否允许模型自我修正
   - 是否允许任务暂停和恢复

5. State / Memory Layer
   - 当前任务状态
   - 对话历史
   - 长期记忆
   - 外部存储
   - checkpoint

6. Safety Layer
   - 输入 guardrail
   - 输出 guardrail
   - 工具权限
   - 高风险操作审批
   - 敏感信息过滤

7. Observability Layer
   - 日志
   - trace
   - token 成本
   - 工具调用记录
   - 错误统计
   - 评估数据
```

这个模板本身不是学习路线，而是工程拆解表。你设计任何 Agent，都可以用它检查 harness 是否完整。

![Orchestrator Workers Workflow](http://public.file.lvshuhuai.cn/images\harness-anthropic-orchestrator-workers.png)

### 一个论文阅读 Agent 的 harness 示例

假设你要做一个论文阅读 Agent，它的 harness 可能是：

```text
Model:
Qwen / GPT / Claude 等支持长上下文和工具调用的模型。

Tools:
- read_pdf_page(page)
- search_pdf(keyword)
- extract_figures(page)
- summarize_section(section)
- save_note(content)

State:
- 当前论文 ID
- 已读页码
- 当前章节
- 用户当前问题
- 已提取的方法、实验、结论
- 工具调用历史

Memory:
- 用户偏好中文解释
- 用户偏好贴近原文
- 用户研究方向是图文对齐 / Agent / 医学多模态

Loop:
- 模型先判断是否需要读原文
- 如果需要，调用 search_pdf 或 read_pdf_page
- 回填原文片段
- 再生成解释
- 如果证据不足，继续检索
- 最多 6 步

Policy:
- 不允许捏造论文结论
- 必须区分原文内容和自己的推断
- 引用关键段落或页码
- 对公式和实验结果保持谨慎

Logging:
- 记录读取了哪些页
- 记录引用了哪些段落
- 记录生成答案所用上下文
```

这个系统对外叫“论文阅读 Agent”。

内部这套组织方式就是它的 harness。

### 一个代码修复 Agent 的 harness 示例

代码 Agent 的 harness 更强调文件系统、命令执行和安全边界：

```text
Tools:
- read_file(path)
- write_file(path, content)
- search_code(keyword)
- run_tests(command)
- inspect_error(log)

State:
- 当前任务描述
- 已检查文件
- 已修改文件
- 测试结果
- 当前失败原因
- 回滚点

Loop:
1. 读取报错信息
2. 搜索相关代码
3. 修改文件
4. 运行测试
5. 如果失败，分析错误并继续
6. 如果通过，总结修改内容

Safety:
- 禁止删除整个目录
- 写文件前做 diff
- 高风险命令需要确认
- 限制 shell 命令白名单
- 保留回滚快照

Observability:
- 每次文件修改都记录 diff
- 每次测试都记录命令和输出
- 最终输出变更摘要
```

这里模型负责判断要读哪个文件、怎么修改、下一步做什么。

Harness 负责提供文件工具、执行命令、限制危险行为、保存状态、记录日志。

## 一个更精确的心智模型

可以把 Agent 系统分成三层：

```text
第一层：Model
负责推理、生成、选择动作。

第二层：Harness
负责组织上下文、暴露工具、执行动作、维护状态、控制流程、保证安全。

第三层：Environment
真实外部世界，例如文件系统、数据库、浏览器、API、业务系统、用户。
```

运行过程是：

```text
User / Environment
        ↓
Harness 组装上下文
        ↓
Model 生成下一步动作
        ↓
Harness 解析动作并执行
        ↓
Environment 返回结果
        ↓
Harness 更新状态
        ↓
Model 继续推理
```

这个模型能解释大部分 Agent 术语之间的关系：

```text
Tool:
Environment 中可被调用的能力，由 harness 暴露给 model。

MCP:
Tool / Resource / Prompt 暴露给 harness 的标准协议。

Memory:
Harness 管理的一类上下文数据。

State:
Harness 管理的当前运行状态。

Workflow:
Harness 中的一种流程控制方式。

Guardrail:
Harness 中的安全控制机制。

Handoff:
Harness 中的多 Agent 协作机制。

Tracing:
Harness 中的可观测机制。

Framework:
帮助开发者实现 harness 的代码库或平台。
```

### 最核心的一句话

如果只能记一句：

> **Harness 是模型外面的工程外壳；它把模型、工具、状态、流程、规则和环境连接起来，使 LLM 能够作为 Agent 稳定行动。**

这句话里每个词都重要：

- “模型外面”：说明 harness 不是模型；
- “工程外壳”：说明它不是抽象口号，而要落到代码；
- “工具、状态、流程、规则和环境”：说明它不止 tool calling；
- “作为 Agent 稳定行动”：说明它的目标不是聊天，而是完成任务。
