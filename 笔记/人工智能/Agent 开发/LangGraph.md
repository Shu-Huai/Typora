# LangGraph

## LangGraph 的定位：它不是模型，也不是 MCP，而是 Agent Runtime

[LangGraph overview - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/overview)

LangGraph 更准确的定位是：**用于构建有状态、多步骤、可恢复 [[智能体 Agent]] / [[工作流 Workflow]] 的编排运行时**。

如果把你已经学过的东西放在同一张图里，大概是这样：

```text
LLM / MLLM
负责理解、生成、推理、多模态输入输出

vLLM
负责模型推理加速、部署、服务化

Tool Calling
让模型能选择和调用外部函数、工具、API

MCP
让外部工具、资源、提示模板以标准协议暴露给 AI 应用

LangGraph
把多步调用、状态流转、分支、循环、人工介入、失败恢复组织成一个可运行系统
```

所以，LangGraph 解决的问题不是“怎么写[[提示词 Prompt]]”，而是：

**当一个 AI 应用不再是一次模型调用，而是一个多步骤、可中断、可恢复的任务系统时，应该怎么组织它的运行过程。**

## 核心直觉：节点、状态、边

LangGraph 最核心的抽象是三个词：

```text
State
Node
Edge
```

更直接地说：

```text
State = 当前任务的所有上下文
Node = 一个处理步骤
Edge = 从一个步骤走到另一个步骤的规则
Conditional Edge = 根据状态判断下一步去哪，本质上就是结构化 if-else
```

比如一个客服 agent 可以这样拆：

```text
read_email
    ↓
classify_email
    ├── 普通问题 -> search_docs
    ├── 投诉问题 -> escalate_to_human
    └── 信息不完整 -> ask_user_more_info

search_docs
    ↓
draft_reply
    ↓
final_review
```

这里每个方框都是一个 node；中间的箭头是 edge；分叉处就是 conditional edge。

你前面说“流转实际上就是 if-else”，这个理解是对的。但 LangGraph 的价值在于：它不是让你把所有 `if else` 堆在一个大函数里，而是把这些判断变成图结构，让流程显式化、可追踪、可恢复。

普通代码可能是这样：

```python
state = parse_input(state)

if state["missing_fields"]:
    state = ask_user(state)
else:
    state = call_tool(state)

if state["tool_error"]:
    state = retry(state)
else:
    state = generate_answer(state)
```

LangGraph 的思路是这样：

```text
parse_input 节点
    ├── missing_fields=True  -> ask_user 节点
    └── missing_fields=False -> call_tool 节点

call_tool 节点
    ├── tool_error=True  -> retry 节点
    └── tool_error=False -> generate_answer 节点
```

也就是说，LangGraph 并没有把控制流变成什么神秘东西。它只是把：

```text
函数调用
if-else
while loop
状态更新
工具调用
人工暂停
失败恢复
```

统一放进一个图运行时里管理。

## Graph API 的基本工作方式

使用 LangGraph 的 Graph API 时，一般是这个顺序：

```text
1. 定义 State
2. 定义 Node
3. 定义 Edge
4. 编译 graph
5. 执行 graph
```

一个简化的伪代码大概是：

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    user_input: str
    intent: str
    answer: str

def classify(state: AgentState):
    text = state["user_input"]
    if "报销" in text:
        return {"intent": "expense"}
    else:
        return {"intent": "general"}

def route(state: AgentState) -> Literal["expense_node", "general_node"]:
    if state["intent"] == "expense":
        return "expense_node"
    return "general_node"

def expense_node(state: AgentState):
    return {"answer": "这是报销相关回答"}

def general_node(state: AgentState):
    return {"answer": "这是普通回答"}

builder = StateGraph(AgentState)

builder.add_node("classify", classify)
builder.add_node("expense_node", expense_node)
builder.add_node("general_node", general_node)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route)
builder.add_edge("expense_node", END)
builder.add_edge("general_node", END)

graph = builder.compile()
```

这段代码表达的东西很简单：

```text
开始
  ↓
分类
  ├── 报销问题 -> 报销节点 -> 结束
  └── 普通问题 -> 普通节点 -> 结束
```

所以你学 LangGraph 时，不要先被各种术语绕进去。最底层就是：

**节点做事，边决定下一步，状态贯穿整个过程。**

## State：LangGraph 的中心，不是附属品

![Short vs long](Z:\Public\images\short-vs-long.png)

在普通脚本里，状态经常是零散的变量：

```python
messages = []
retrieved_docs = []
tool_result = None
final_answer = None
```

但在 LangGraph 里，这些东西通常会被组织成一个统一的 `State`。每个 node 读取 state，然后返回对 state 的更新。这实际上是[[状态管理 State Management]]。

这点很关键。LangGraph 不是简单地帮你“画流程图”，而是强迫你把 agent 运行时的上下文显式化。

比如一个[[检索增强生成 RAG]] agent 的 state 可以是：

```python
class RAGState(TypedDict):
    question: str
    rewritten_query: str
    retrieved_docs: list[str]
    answer: str
    needs_retrieval: bool
    retry_count: int
```

一个[[工具调用 Tool Calling]] agent 的 state 可以是：

```python
class ToolAgentState(TypedDict):
    messages: list
    tool_calls: list
    tool_results: list
    final_answer: str
    error: str | None
```

一个审批流 agent 的 state 可以是：

```python
class ApprovalState(TypedDict):
    request_text: str
    extracted_fields: dict
    risk_level: str
    human_decision: str | None
    final_result: str
```

你会发现，State 其实就是 agent 的“内存快照”。LangGraph 之所以能恢复、调试、中断、回放，本质上就是因为它把这些状态结构化地保存下来了。

## Node：节点就是函数，可以包含 LLM，也可以只是普通代码

Node 不一定是[[大语言模型 LLM]] 调用。一个 node 可以是：

```text
调用 LLM 分类
调用搜索工具
调用数据库
解析 JSON
检查字段是否齐全
计算风险分数
发邮件
写入日志
等待人工审批
```

也就是说，LangGraph 不是“LLM 节点编排器”，而是“任务步骤编排器”。LLM 只是其中一种节点逻辑。

比如：

```python
def check_missing_fields(state):
    required = ["name", "amount", "reason"]
    missing = []

    for field in required:
        if field not in state["expense_form"]:
            missing.append(field)

    return {"missing_fields": missing}
```

这个节点完全不需要 LLM，但它在 agent 系统里很重要。因为真实业务里，很多步骤应该是确定性代码，而不是都交给模型判断。

这也是 LangGraph 适合生产系统的原因之一：它允许你把确定性流程和模型决策混在一起。

## Edge：固定边和条件边

Edge 分两种。

第一种是固定边：

```text
A 执行完，一定去 B
```

比如：

```python
builder.add_edge("retrieve_docs", "generate_answer")
```

第二种是条件边：

```text
A 执行完，根据当前 state 判断去 B、C、D 还是结束
```

比如：

```python
def should_continue(state):
    if state["missing_fields"]:
        return "ask_user"
    if state["risk_level"] == "high":
        return "human_review"
    return "finalize"
```

这就是你说的 if-else。

所以 LangGraph 的 agent loop 可以写成这样：

```text
llm_call
    ├── 有 tool_calls -> tool_node -> llm_call
    └── 没有 tool_calls -> END
```

这其实就是经典 agent 循环：

```python
while True:
    response = call_llm(messages)

    if response.has_tool_call:
        result = call_tool(response.tool_call)
        messages.append(result)
    else:
        break
```

LangGraph 只是把这个 `while + if` 变成了显式图结构。

## Workflow 和 Agent 的区别

workflow 是预先确定的代码路径，按既定顺序运行；agent 是动态的，可以自己决定流程和工具使用。

你可以这样理解：

```text
Workflow
开发者提前规定步骤：
A -> B -> C -> D

Agent
模型根据状态动态决定下一步：
A -> 模型判断 -> 可能去 B / C / D / 工具调用 / 追问用户 / 结束
```

但真实系统里，二者经常混合。

例如一个“报销审核 AI”：

```text
1. 固定步骤：抽取报销字段
2. 固定步骤：检查字段完整性
3. 条件分支：字段不全则追问用户
4. 固定步骤：查公司制度
5. LLM 判断：是否违反制度
6. 条件分支：高风险进入人工审批
7. 固定步骤：生成最终意见
```

这里既有 workflow，也有 agent。

所以不要把 workflow 和 agent 对立起来。更准确地说：

**workflow 是确定性骨架，agent 是其中某些需要动态决策的节点。LangGraph 可以同时表达两者。**

## Persistence：LangGraph 真正重要的工程能力

如果 LangGraph 只是把 if-else 画成图，那它价值不大。它真正重要的能力是 persistence，也就是状态持久化。

![Checkpoints](Z:\Public\images\checkpoints.jpg)

这里有几个核心词：

```text
checkpointer
负责保存状态快照的组件

checkpoint
某一步执行之后保存下来的状态快照

thread
一次会话或一次任务实例的持久化 ID

thread_id
运行 graph 时指定的会话标识
```

你可以把它理解成：

```text
thread_id = 当前任务编号
checkpoint = 当前任务跑到某一步时的存档
checkpointer = 存档系统
```

比如一个用户和客服 agent 聊天：

```text
thread_id = user_123_session_456
```

这条 thread 下面可能有很多 checkpoint：

```text
checkpoint_1: 用户刚发来问题
checkpoint_2: agent 完成分类
checkpoint_3: agent 检索了文档
checkpoint_4: agent 草拟了回复
checkpoint_5: 人工修改了回复
checkpoint_6: agent 发出最终回复
```

如果执行到 checkpoint_4 时服务崩了，恢复后就不需要从头开始，而可以从最近的 checkpoint 继续。

这就是 durable execution 的实际含义：不是“模型更耐用”，而是“agent 的运行过程可以保存、恢复和审计”。

## Interrupt：人工介入不是外挂，而是运行时能力

很多真实业务不能让 agent 直接做完。比如：

```text
发送邮件前需要人确认
执行退款前需要人审批
修改数据库前需要人批准
高风险结论需要人工复核
```

LangGraph 的 interrupt 机制就是为这类 human-in-the-loop 场景准备的。

例如：

```text
draft_email
    ↓
interrupt: 等待人工确认
    ↓
send_email
```

这件事如果手写，也能做，但你要自己处理：

```text
当前跑到哪一步
状态保存在哪里
人修改了什么
如何继续执行
如何避免重复发送
如何记录审批轨迹
```

LangGraph 把这部分做成运行时能力，所以它更适合真实业务系统，而不是只适合 demo。

![img](Z:\Public\images\69cbb0374cf06727c05d6a53_opengpts-authorize-1.png)

## Memory：短期记忆和长期记忆

LangGraph 里的 memory 不应该简单理解成“把聊天记录塞进 prompt”。它更适合拆成两类：短期记忆和长期记忆。

```text
短期记忆
当前会话里的东西：
messages、retrieved_docs、uploaded_files、intermediate_results

长期记忆
跨会话保留的东西：
用户偏好、历史事实、长期档案、业务配置
```

比如：

```text
短期记忆：
用户这一轮问了什么
agent 刚才查到了哪些文档
上一步工具返回了什么

长期记忆：
用户喜欢中文回答
用户常用 Java
用户的项目默认用 PostgreSQL
```

短期记忆依赖 thread。长期记忆不应该直接混在普通 messages 里，而应该作为应用层存储的一部分，在需要时检索出来。

这点和普通 chatbot 的区别很大。普通 chatbot 往往只是把历史消息拼接进上下文；LangGraph 关注的是：

```text
哪些状态属于当前任务？
哪些记忆属于当前会话？
哪些信息应该跨会话长期保存？
什么时候读取？
什么时候更新？
如何避免上下文爆炸？
```

## Time Travel 和 Debugging

checkpoint 还有一个很实用的副作用：可以做 time travel debugging，也就是查看或回放历史执行状态。

这在 agent 开发里很重要。

因为 agent 错误往往不是单点错误，而是链式错误：

```text
用户输入理解错
    ↓
分类错
    ↓
检索错
    ↓
工具参数错
    ↓
最终回答错
```

如果没有状态快照，你很难知道到底是哪一步开始偏了。

有了 checkpoint，你可以查看：

```text
分类节点之前的 state 是什么
分类节点输出了什么
检索 query 是怎么生成的
工具参数是什么
工具返回了什么
最终回答基于哪些中间结果
```

所以 LangGraph 不只是运行 agent，也方便你调试 agent。

## Subgraph：把复杂系统拆成子图

当一个图越来越大时，你不应该把所有节点堆在一个 graph 里。LangGraph 支持 subgraph，也就是“把一个 graph 当作另一个 graph 的节点”。

<img src="https://mintcdn.com/langchain-5e9cc07a/ybiAaBfoBvFquMDz/oss/images/subgraph.png?fit=max&auto=format&n=ybiAaBfoBvFquMDz&q=85&s=c280df5c968cd4237b0b5d03823d8946" alt="SQL agent graph" style="zoom:50%;" />

例如一个企业客服系统可以拆成：

```text
总控 graph
    ├── 订单问题 subgraph
    ├── 退款问题 subgraph
    ├── 技术支持 subgraph
    └── 投诉升级 subgraph
```

每个 subgraph 内部又有自己的流程：

```text
退款问题 subgraph
    ↓
识别订单
    ↓
检查退款规则
    ↓
判断是否需要人工审批
    ↓
生成退款结论
```

这种结构比一个超大的 graph 更容易维护。

你可以把 subgraph 理解成：

```text
函数是代码复用单位
subgraph 是 agent/workflow 的复用单位
```

## Graph API 和 Functional API

LangGraph 不只有 Graph API，还有 Functional API。Functional API 允许你在更接近普通 Python 函数、if 语句、for 循环和函数调用的代码里加入 persistence、memory、human-in-the-loop、streaming 等能力。

你可以这样选：

```text
Graph API
适合复杂分支、多节点、多路径、需要显式可视化的 agent/workflow

Functional API
适合已有代码已经是普通函数流程，只想加 checkpoint、interrupt、streaming、memory
```

所以不是所有 LangGraph 项目都必须画一个很复杂的图。

如果你的流程本来就很像普通代码，用 Functional API 可能更自然。

如果你的流程确实有复杂路由、循环、多 agent、人工审批，用 Graph API 更清楚。

## Streaming：不是核心逻辑，但对产品体验很重要

LangGraph 也支持 streaming。这里的 streaming 不只是“模型 token 一个个吐出来”，还可以包括：

```text
当前执行到哪个节点
某个节点产生了什么中间结果
工具调用开始
工具调用结束
最终回答逐步生成
```

真实产品里，用户不喜欢等一个黑盒系统跑几十秒。你可以把执行状态显示出来：

```text
正在分析问题...
正在检索知识库...
正在调用订单系统...
正在生成回复...
等待人工确认...
```

这会显著改善 agent 产品体验。

## LangGraph 和 LangChain 的关系

不要把 LangGraph 和 [[LangChain]] 看成互相替代。

更准确的关系是：

```text
LangChain
偏高层应用框架，提供模型、工具、agent、RAG 等封装

LangGraph
偏底层运行时，提供状态、图、持久化、恢复、人工介入、复杂流程控制
```

所以你的理解可以是：

```text
简单 agent：用 LangChain 高层封装更快
复杂 agent：下沉到 LangGraph 自己控制流程
生产级 agent：通常需要 LangGraph 这类 runtime 能力
```

## LangGraph 和 MCP 的关系

[[模型上下文协议 MCP]] 和 LangGraph 不在同一层。

MCP 解决的是：

```text
外部工具、资源、提示模板如何标准化暴露给 AI 应用
```

LangGraph 解决的是：

```text
这些外部能力接进来之后，整个 agent 如何编排、执行、暂停、恢复、调试
```

举例：

```text
MCP Server 提供一个 search_docs 工具
LangGraph 的某个 node 调用 search_docs
LangGraph 的 edge 根据搜索结果决定下一步是生成回答、继续检索，还是追问用户
```

所以 MCP 更像“能力接入层”，LangGraph 更像“执行编排层”。

## 一个最小 Agent Loop 的 LangGraph 思维

经典 tool-calling agent 本质上是一个循环：

```text
用户输入
    ↓
LLM 判断
    ├── 需要工具 -> 调工具 -> 把结果放回 messages -> 再问 LLM
    └── 不需要工具 -> 直接回答 -> 结束
```

用普通伪代码表示：

```python
while True:
    response = call_llm(messages)

    if response.tool_calls:
        tool_result = call_tool(response.tool_calls)
        messages.append(tool_result)
    else:
        return response.content
```

用 LangGraph 表示：

```text
llm_call
    ├── 有 tool_call -> tool_node -> llm_call
    └── 无 tool_call -> END
```

这个例子非常重要。它说明 LangGraph 并不是发明了什么全新的“智能体逻辑”。它只是把 agent loop 变成了一个可以持久化、可恢复、可观察、可扩展的图结构。

## 常见误解

### 误解一：LangGraph 就是可视化流程图

不是。图只是表达形式。它真正重要的是运行时能力，包括 persistence、interrupt、memory、streaming、debugging、recovery。

### 误解二：每个节点都要调用 LLM

不是。Node 可以只是普通函数。它可以调用 LLM，也可以调用数据库、校验字段、计算分数、解析 JSON、写日志。

### 误解三：LangGraph 比 if-else 更“智能”

不是。很多 conditional edge 本质上就是 if-else。LangGraph 的优势不是让分支判断更智能，而是让这些分支、状态和执行过程更工程化。

### 误解四：用了 LangGraph 就等于做了 agent

不是。你完全可以用 LangGraph 写一个确定性的 workflow。是否是 agent，取决于流程里是否存在由模型动态决定下一步行动的部分。

### 误解五：MCP 和 LangGraph 只能选一个

不是。MCP 管能力接入，LangGraph 管执行编排。实际系统里可以同时使用。

## 什么时候应该用 LangGraph

适合用 LangGraph 的场景：

```text
任务有多个步骤
流程有条件分支
需要循环调用工具
需要人工审批
需要中途暂停和恢复
需要保存会话状态
需要审计 agent 每一步做了什么
需要多 agent 或 subgraph
需要生产级容错和调试能力
```

不一定需要 LangGraph 的场景：

```text
单轮问答
简单 prompt 调用
一次性 RAG
简单 function calling
没有复杂状态和恢复需求的小 demo
```

如果你只是写：

```text
用户问题 -> 检索 -> 生成回答
```

普通 LangChain 或自己手写代码就够了。

如果你写的是：

```text
用户问题
  -> 判断意图
  -> 检查缺失字段
  -> 多轮追问
  -> 调多个工具
  -> 失败重试
  -> 人工审批
  -> 保存状态
  -> 断点恢复
  -> 生成最终结果
```

这时候 LangGraph 的价值才明显。

## 最终心智模型

你可以把 LangGraph 记成这句话：

**LangGraph 是把 agent 的 while loop、if-else、状态更新、工具调用、人工介入、持久化恢复，组织成图状运行时的框架。**

再压缩一点：

```text
State 记录当前任务
Node 执行具体步骤
Edge 决定下一步
Checkpointer 保存过程
Thread 区分会话
Interrupt 暂停等待外部输入
Memory 让状态跨步骤或跨会话存在
Subgraph 拆分复杂系统
```

所以 LangGraph 并不玄。

它的底层直觉就是：

**很多节点，每个节点读写状态，然后根据状态流转。流转大部分时候就是 if-else。**

真正的区别在于，LangGraph 把这套东西变成了一个适合真实 agent 工程的 runtime。

## LangGraph 报销审核项目：从零到可运行的分步教程

这份教程不是泛泛介绍 LangGraph，而是**严格围绕你现在这份报销审核代码**来讲。目标不是“知道概念”，而是让你能顺着步骤，一步一步把代码写出来，并理解每一步为什么要这样写、这样写会得到什么效果。

这份项目最后会实现下面这件事：

- 用户输入一句话，比如“我要报销打车 15 元”
- 程序调用真实大模型
- 大模型返回[[结构化输出 Structured Output]]：是不是报销、金额是多少、判断理由是什么
- LangGraph 根据结构化结果做条件分流
- 如果金额缺失，就追问用户
- 如果金额不超过 5000，自动通过
- 如果金额超过 5000，进入人工审核
- 如果用户分两轮说“报销” → “1元”，系统也能接上上下文

### 先明确这个项目到底在做什么

在开始写代码之前，你先不要急着装库。先把项目的“运行模型”想清楚。

这个项目不是一个普通的 `if else` 脚本，也不是一个单纯的聊天机器人。它实际上是：

1. **一个有状态的流程**
2. **一个接入真实 LLM 的业务判断器**
3. **一个最小 LangGraph 工作流**

你可以把整个流程理解成这样：

```text
START
  ↓
analyze_request
  ├── not_expense   -> END
  ├── ask_amount    -> END
  ├── auto_approve  -> END
  └── human_review  -> END
```

这里的关键点是：

- `analyze_request`：用大模型做结构化判断
- `route_after_analysis`：根据 state 决定走哪条边
- 后面几个节点：生成业务回复

所以你真正要学的是三层东西：

- **LLM 层**：怎么接 API Key，怎么真正调用模型
- **Structured Output 层**：怎么让模型返回结构化数据，而不是一段随意自然语言
- **LangGraph 层**：怎么把结构化结果放进图里流转

### 第一步：创建项目并安装依赖

#### 这一步要做什么

先创建一个最小 Python 项目，并安装会用到的库。

#### 为什么先做这一步

因为你的代码不是纯 Python 标准库项目，它依赖：

- `langgraph`：图运行时
- `langchain-openai`：接 OpenAI / OpenAI-compatible 模型
- `python-dotenv`：从 `.env` 里读取 API Key
- `pydantic`：定义结构化输出 schema

#### 推荐命令

如果你用 `uv`：

```powershell
mkdir langgraph-expense-demo
cd langgraph-expense-demo
uv init
uv add langgraph langchain-openai python-dotenv pydantic
```

如果你用 `pip`：

```powershell
mkdir langgraph-expense-demo
cd langgraph-expense-demo
python -m venv .venv
.\.venv\Scripts\activate
pip install langgraph langchain-openai python-dotenv pydantic
```

#### 这一步完成后的效果

你会得到一个能运行 Python 项目的目录，并且依赖已经装好。接下来你就可以真正写代码了。

### 第二步：创建 `.env`，把 API Key 放到环境变量里

#### 这一步要做什么

新建一个 `.env` 文件，把模型访问配置写进去。

#### 为什么这样做

因为 API Key 不能写死在代码里。写死有几个问题：

- 不安全
- 不方便切换模型和服务商
- 换环境时容易出错

#### 新建 `.env`

```env
OPENAI_API_KEY=你的真实APIKey
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=
```

如果你用的是 OpenAI-compatible 服务，比如某个第三方平台，就把 `OPENAI_BASE_URL` 填成对应的 `/v1` 地址，例如：

```env
OPENAI_BASE_URL=https://your-provider.example.com/v1
```

#### 这一步完成后的效果

你的程序可以从环境变量里读到：

- API Key
- 模型名
- 可选的 base_url

以后切换模型时，不用改 Python 代码，只改 `.env` 就够了。

### 第三步：先搭起文件骨架和 import

#### 这一步要做什么

先把 `main.py` 的最外层骨架写出来，包括 import。

#### 代码

```python
import os
from typing import Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

try:
    from langgraph.checkpoint.memory import InMemorySaver
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver as InMemorySaver
```

#### 为什么这样写

这里每个 import 都不是随便写的。

- `os`：读取环境变量
- `Literal`、`Optional`、`TypedDict`：定义严格类型
- `load_dotenv`：加载 `.env`
- `ChatOpenAI`：接真实模型
- `StateGraph`、`START`、`END`：构图
- `BaseModel`、`Field`：定义结构化输出 schema
- `InMemorySaver`：后面做多轮会话持久化

#### 这一步完成后的效果

你已经把“接真实模型”和“构建图”的依赖准备好了。

### 第四步：定义结构化输出模型 `ExpenseAnalysis`

#### 这一步要做什么

让大模型返回结构化对象，而不是自然语言段落。

#### 为什么这样做

如果模型只返回一句“用户应该是在报销，金额是 15 元”，那你还得自己再解析。更稳定的做法是让模型直接返回：

```json
{
  "intent": "expense",
  "amount": 15,
  "reason": "用户明确表达了报销意图，并给出了金额。"
}
```

#### 代码

```python
class ExpenseAnalysis(BaseModel):
    intent: Literal["expense", "other"] = Field(
        description=(
            "用户意图。只能是 expense 或 other。"
            "expense 表示报销申请，other 表示其他问题。"
        )
    )

    amount: int | None = Field(
        description=(
            "用户明确给出的人民币金额，单位元。"
            "如果用户没有明确给出金额，必须是 null。"
        )
    )

    reason: str = Field(
        description="一句中文判断理由。"
    )
```

#### 为什么字段这么设计

- `intent`：决定是不是报销
- `amount`：决定走哪个审核分支
- `reason`：用于解释模型为什么这么判断

#### 这一步完成后的效果

后面模型返回的不是自由文本，而是一个带字段的对象。

### 第五步：定义 LangGraph 共享状态 `ExpenseState`

#### 这一步要做什么

定义整个图运行时共享的数据结构。

#### 代码

```python
class ExpenseState(TypedDict, total=False):
    user_input: str
    intent: str
    amount: Optional[int]
    analysis_reason: str
    awaiting_amount: bool
    final_answer: str
```

#### 为什么必须有 State

LangGraph 的核心不是“节点一个个执行”，而是“节点通过共享 state 传递信息”。

#### 字段解释

- `user_input`：当前输入
- `intent`：模型识别到的意图
- `amount`：模型识别到的金额
- `analysis_reason`：模型给的理由
- `awaiting_amount`：上一轮是否已经确认报销但缺金额
- `final_answer`：最后要回复给用户的话

#### 这一步完成后的效果

你把整个图在运行时需要维护的数据明确了。

### 第六步：写 `create_llm()`，真正接入模型

#### 代码

```python
def create_llm() -> ChatOpenAI:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-api-key-here":
        raise RuntimeError(
            "没有找到有效的 OPENAI_API_KEY。\n"
            "请先复制 .env.example 为 .env，然后在 .env 中填写真实 API Key。"
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()

    kwargs = {
        "model": model,
        "temperature": 0,
        "extra_body": {"enable_thinking": False},
    }

    if base_url:
        kwargs["base_url"] = base_url

    return ChatOpenAI(**kwargs)
```

#### 为什么这样写

- `load_dotenv()`：加载 `.env`
- API Key 校验：没配就立刻报错
- `temperature=0`：降低随机性，适合业务判断
- `base_url`：兼容 OpenAI-compatible 服务
- `extra_body`：某些服务商需要关闭 thinking 输出；不支持就删掉

#### 这一步完成后的效果

你已经不再是在写假代码，而是在真的接一个可调用的大模型。

### 第七步：在 `build_graph()` 里先创建结构化 LLM

#### 代码

```python
def build_graph():
    llm = create_llm()

    structured_llm = llm.with_structured_output(
        ExpenseAnalysis,
        method="json_schema",
        strict=True,
    )
```

#### 为什么这样写

这一步把普通模型包装成“按 schema 输出”的模型。

#### 为什么不用普通自然语言输出

因为后面路由要直接依赖：

- `intent`
- `amount`

如果模型返回一大段自然语言，你还得自己再解析，会很脆弱。

#### 这一步完成后的效果

你后面在节点里能直接拿到 `ExpenseAnalysis` 对象。

### 第八步：写第一个真正的节点 `analyze_request`

#### 代码

```python
    def analyze_request(state: ExpenseState) -> ExpenseState:
        user_input = state["user_input"]
        awaiting_amount = state.get("awaiting_amount", False)

        analysis = structured_llm.invoke(
            [
                (
                    "system",
                    "你是一个企业报销申请分析器。"
                    "你必须按照给定 JSON Schema 返回结构化结果。"
                    "intent 只能是 expense 或 other。"
                    "如果 previous_state.awaiting_amount 为 true，"
                    "说明上一轮已经确认用户正在申请报销，只是缺少金额。"
                    "这时如果当前用户输入里有明确金额，"
                    "intent 必须是 expense，amount 必须提取该金额。"
                    "如果 previous_state.awaiting_amount 为 false，"
                    "则根据当前用户输入独立判断。"
                    "如果用户表达的是报销、费用报销、差旅报销、打车报销、餐费报销等含义，intent 必须是 expense。"
                    "如果用户不是在申请报销，intent 必须是 other。"
                    "amount 是用户明确给出的人民币金额，单位元；如果没有明确金额，amount 必须是 null。"
                    "reason 必须用一句中文说明判断理由。"
                    "不要猜测用户没有说出的金额。"
                ),
                (
                    "user",
                    f"previous_state.awaiting_amount={awaiting_amount}\n"
                    f"当前用户输入：{user_input}",
                ),
            ]
        )

        return {
            "intent": analysis.intent,
            "amount": analysis.amount,
            "analysis_reason": analysis.reason,
        }
```

#### 为什么这一段最重要

这是整个项目的分析入口。

它解决的是：

第一轮：

```text
报销
```

第二轮：

```text
1元
```

如果不把 `awaiting_amount` 这个业务状态带给模型，第二轮就会把“1元”当成一条孤立输入。

#### 这一步完成后的效果

这个节点执行后，state 里会多出：

- `intent`
- `amount`
- `analysis_reason`

后面的条件边就能用这些字段路由了。

### 第九步：写条件边函数 `route_after_analysis`

#### 代码

```python
    def route_after_analysis(
        state: ExpenseState,
    ) -> Literal["not_expense", "ask_amount", "auto_approve", "human_review"]:
        if state.get("intent") != "expense":
            return "not_expense"

        amount = state.get("amount")
        if amount is None:
            return "ask_amount"

        if amount > 5000:
            return "human_review"

        return "auto_approve"
```

#### 为什么这就是 LangGraph 的核心

这就是最典型的“节点更新状态，边根据状态做 if-else 路由”。

- 不是报销 → `not_expense`
- 是报销但没金额 → `ask_amount`
- 金额超过 5000 → `human_review`
- 其他情况 → `auto_approve`

#### 这一步完成后的效果

你的图第一次真正有了分支逻辑。

### 第十步：写四个业务节点

#### `not_expense`

```python
    def not_expense(state: ExpenseState) -> ExpenseState:
        response = llm.invoke(
            [
                (
                    "system",
                    "你是一个简洁的中文助手。"
                    "用户当前问题不是报销申请。"
                    "请说明你只能处理报销申请，并让用户重新输入。",
                ),
                ("user", state["user_input"]),
            ]
        )

        return {
            "awaiting_amount": False,
            "final_answer": str(response.content),
        }
```

这里要重置 `awaiting_amount`，因为当前报销上下文结束了。

#### `ask_amount`

```python
    def ask_amount(state: ExpenseState) -> ExpenseState:
        response = llm.invoke(
            [
                (
                    "system",
                    "你是企业报销助手。"
                    "用户想申请报销，但没有提供金额。"
                    "请用一句自然中文要求用户补充报销金额。",
                ),
                ("user", state["user_input"]),
            ]
        )

        return {
            "awaiting_amount": True,
            "final_answer": str(response.content),
        }
```

这里必须把 `awaiting_amount` 设成 `True`，否则下一轮“1元”接不上。

#### `auto_approve`

```python
    def auto_approve(state: ExpenseState) -> ExpenseState:
        response = llm.invoke(
            [
                (
                    "system",
                    "你是企业报销助手。"
                    "规则：报销金额不超过 5000 元，可以自动通过。"
                    "请基于 state 给出简洁、明确的中文审核结论。",
                ),
                (
                    "user",
                    f"用户原文：{state['user_input']}\n"
                    f"识别金额：{state.get('amount')} 元\n"
                    f"分析理由：{state.get('analysis_reason')}",
                ),
            ]
        )

        return {
            "awaiting_amount": False,
            "final_answer": str(response.content),
        }
```

#### `human_review`

```python
    def human_review(state: ExpenseState) -> ExpenseState:
        response = llm.invoke(
            [
                (
                    "system",
                    "你是企业报销助手。"
                    "规则：报销金额超过 5000 元，必须进入人工审核。"
                    "请基于 state 给出简洁、明确的中文审核结论。",
                ),
                (
                    "user",
                    f"用户原文：{state['user_input']}\n"
                    f"识别金额：{state.get('amount')} 元\n"
                    f"分析理由：{state.get('analysis_reason')}",
                ),
            ]
        )

        return {
            "awaiting_amount": False,
            "final_answer": str(response.content),
        }
```

#### 这一步完成后的效果

你已经拥有了一套完整的业务节点集合。前面的分析节点负责“判断”，这里的节点负责“回复”。

### 第十一步：把节点和边真正组装成图

#### 代码

```python
    builder = StateGraph(ExpenseState)

    builder.add_node("analyze_request", analyze_request)
    builder.add_node("not_expense", not_expense)
    builder.add_node("ask_amount", ask_amount)
    builder.add_node("auto_approve", auto_approve)
    builder.add_node("human_review", human_review)

    builder.add_edge(START, "analyze_request")

    builder.add_conditional_edges(
        "analyze_request",
        route_after_analysis,
        {
            "not_expense": "not_expense",
            "ask_amount": "ask_amount",
            "auto_approve": "auto_approve",
            "human_review": "human_review",
        },
    )

    builder.add_edge("not_expense", END)
    builder.add_edge("ask_amount", END)
    builder.add_edge("auto_approve", END)
    builder.add_edge("human_review", END)
```

#### 为什么要这样组装

- `StateGraph(ExpenseState)`：规定共享状态结构
- `add_node()`：注册节点
- `add_edge(START, ...)`：指定入口
- `add_conditional_edges(...)`：根据 state 分流
- `add_edge(..., END)`：指定终点

#### 这一步完成后的效果

你的代码第一次真正变成了一张图。

### 第十二步：加入 checkpointer，让多轮状态能保存下来

#### 代码

```python
    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)
```

#### 为什么必须加它

如果你只写：

```python
return builder.compile()
```

那每次 `graph.invoke()` 都会被当成全新执行。

这就会导致：

第一轮：

```text
报销
```

第二轮：

```text
1元
```

系统会把“1元”当成一条新的孤立输入。

#### 为什么这里先用 `InMemorySaver`

因为它最适合 demo：

- 简单
- 不用数据库
- 程序退出后状态会丢失，但足够教学

#### 这一步完成后的效果

只要你后面调用时使用相同的 `thread_id`，LangGraph 就能把之前的状态接上。

### 第十三步：写 `run_once()`，并传入固定 `thread_id`

#### 代码

```python
def run_once(graph, user_input: str, thread_id: str) -> None:
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = graph.invoke(
        {"user_input": user_input},
        config=config,
    )

    print("\n" + "=" * 80)
    print("用户输入：")
    print(user_input)

    print("\nLangGraph 最终 State：")
    print(result)

    print("\nAI 回复：")
    print(result["final_answer"])
```

#### 为什么 `thread_id` 这么关键

因为 checkpointer 不是自动猜“哪几轮属于同一会话”的。它需要一个会话标识。

只要多次调用用的是同一个 `thread_id`，它们就会共享同一条状态链。

#### 这一步完成后的效果

你第一次拥有了真正的多轮延续能力。

### 第十四步：写 `main()`，做一个可交互命令行 demo

#### 代码

```python
def main() -> None:
    graph = build_graph()
    thread_id = "demo-user-1"

    print("LangGraph 报销审核 Demo")
    print("输入 exit 退出。")
    print("示例：我今天打车去客户公司，申请报销 120 元。")
    print("示例：我参加外部培训，申请报销 8000 元。")
    print("示例：我想申请一次差旅报销。")
    print("示例多轮：先输入“报销”，再输入“1元”。")

    while True:
        user_input = input("\n请输入：").strip()

        if user_input.lower() in {"exit", "quit", "q"}:
            print("已退出。")
            break

        if not user_input:
            continue

        try:
            run_once(graph, user_input, thread_id)
        except Exception as exc:
            print("\n运行出错：")
            print(type(exc).__name__, exc)
```

#### 为什么先固定一个 `thread_id`

因为这是教学 demo。你现在不是在做多用户系统，而是在验证同一个会话里的多轮状态是否能接上。

#### 这一步完成后的效果

你可以直接在命令行里和这个 LangGraph 项目交互了。

### 第十五步：完整 `main.py`

```python
import os
from typing import Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

try:
    from langgraph.checkpoint.memory import InMemorySaver
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver as InMemorySaver


class ExpenseAnalysis(BaseModel):
    intent: Literal["expense", "other"] = Field(
        description=(
            "用户意图。只能是 expense 或 other。"
            "expense 表示报销申请，other 表示其他问题。"
        )
    )

    amount: int | None = Field(
        description=(
            "用户明确给出的人民币金额，单位元。"
            "如果用户没有明确给出金额，必须是 null。"
        )
    )

    reason: str = Field(
        description="一句中文判断理由。"
    )


class ExpenseState(TypedDict, total=False):
    user_input: str
    intent: str
    amount: Optional[int]
    analysis_reason: str
    awaiting_amount: bool
    final_answer: str


def create_llm() -> ChatOpenAI:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-api-key-here":
        raise RuntimeError(
            "没有找到有效的 OPENAI_API_KEY。\n"
            "请先复制 .env.example 为 .env，然后在 .env 中填写真实 API Key。"
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()

    kwargs = {
        "model": model,
        "temperature": 0,
        "extra_body": {"enable_thinking": False},
    }

    if base_url:
        kwargs["base_url"] = base_url

    return ChatOpenAI(**kwargs)


def build_graph():
    llm = create_llm()

    structured_llm = llm.with_structured_output(
        ExpenseAnalysis,
        method="json_schema",
        strict=True,
    )

    def analyze_request(state: ExpenseState) -> ExpenseState:
        user_input = state["user_input"]
        awaiting_amount = state.get("awaiting_amount", False)

        analysis = structured_llm.invoke(
            [
                (
                    "system",
                    "你是一个企业报销申请分析器。"
                    "你必须按照给定 JSON Schema 返回结构化结果。"
                    "intent 只能是 expense 或 other。"
                    "如果 previous_state.awaiting_amount 为 true，"
                    "说明上一轮已经确认用户正在申请报销，只是缺少金额。"
                    "这时如果当前用户输入里有明确金额，"
                    "intent 必须是 expense，amount 必须提取该金额。"
                    "如果 previous_state.awaiting_amount 为 false，"
                    "则根据当前用户输入独立判断。"
                    "如果用户表达的是报销、费用报销、差旅报销、打车报销、餐费报销等含义，intent 必须是 expense。"
                    "如果用户不是在申请报销，intent 必须是 other。"
                    "amount 是用户明确给出的人民币金额，单位元；如果没有明确金额，amount 必须是 null。"
                    "reason 必须用一句中文说明判断理由。"
                    "不要猜测用户没有说出的金额。"
                ),
                (
                    "user",
                    f"previous_state.awaiting_amount={awaiting_amount}\n"
                    f"当前用户输入：{user_input}",
                ),
            ]
        )

        return {
            "intent": analysis.intent,
            "amount": analysis.amount,
            "analysis_reason": analysis.reason,
        }

    def route_after_analysis(
        state: ExpenseState,
    ) -> Literal["not_expense", "ask_amount", "auto_approve", "human_review"]:
        if state.get("intent") != "expense":
            return "not_expense"

        amount = state.get("amount")
        if amount is None:
            return "ask_amount"

        if amount > 5000:
            return "human_review"

        return "auto_approve"

    def not_expense(state: ExpenseState) -> ExpenseState:
        response = llm.invoke(
            [
                (
                    "system",
                    "你是一个简洁的中文助手。"
                    "用户当前问题不是报销申请。"
                    "请说明你只能处理报销申请，并让用户重新输入。",
                ),
                ("user", state["user_input"]),
            ]
        )

        return {
            "awaiting_amount": False,
            "final_answer": str(response.content),
        }

    def ask_amount(state: ExpenseState) -> ExpenseState:
        response = llm.invoke(
            [
                (
                    "system",
                    "你是企业报销助手。"
                    "用户想申请报销，但没有提供金额。"
                    "请用一句自然中文要求用户补充报销金额。",
                ),
                ("user", state["user_input"]),
            ]
        )

        return {
            "awaiting_amount": True,
            "final_answer": str(response.content),
        }

    def auto_approve(state: ExpenseState) -> ExpenseState:
        response = llm.invoke(
            [
                (
                    "system",
                    "你是企业报销助手。"
                    "规则：报销金额不超过 5000 元，可以自动通过。"
                    "请基于 state 给出简洁、明确的中文审核结论。",
                ),
                (
                    "user",
                    f"用户原文：{state['user_input']}\n"
                    f"识别金额：{state.get('amount')} 元\n"
                    f"分析理由：{state.get('analysis_reason')}",
                ),
            ]
        )

        return {
            "awaiting_amount": False,
            "final_answer": str(response.content),
        }

    def human_review(state: ExpenseState) -> ExpenseState:
        response = llm.invoke(
            [
                (
                    "system",
                    "你是企业报销助手。"
                    "规则：报销金额超过 5000 元，必须进入人工审核。"
                    "请基于 state 给出简洁、明确的中文审核结论。",
                ),
                (
                    "user",
                    f"用户原文：{state['user_input']}\n"
                    f"识别金额：{state.get('amount')} 元\n"
                    f"分析理由：{state.get('analysis_reason')}",
                ),
            ]
        )

        return {
            "awaiting_amount": False,
            "final_answer": str(response.content),
        }

    builder = StateGraph(ExpenseState)

    builder.add_node("analyze_request", analyze_request)
    builder.add_node("not_expense", not_expense)
    builder.add_node("ask_amount", ask_amount)
    builder.add_node("auto_approve", auto_approve)
    builder.add_node("human_review", human_review)

    builder.add_edge(START, "analyze_request")

    builder.add_conditional_edges(
        "analyze_request",
        route_after_analysis,
        {
            "not_expense": "not_expense",
            "ask_amount": "ask_amount",
            "auto_approve": "auto_approve",
            "human_review": "human_review",
        },
    )

    builder.add_edge("not_expense", END)
    builder.add_edge("ask_amount", END)
    builder.add_edge("auto_approve", END)
    builder.add_edge("human_review", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)


def run_once(graph, user_input: str, thread_id: str) -> None:
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = graph.invoke(
        {"user_input": user_input},
        config=config,
    )

    print("\n" + "=" * 80)
    print("用户输入：")
    print(user_input)

    print("\nLangGraph 最终 State：")
    print(result)

    print("\nAI 回复：")
    print(result["final_answer"])


def main() -> None:
    graph = build_graph()
    thread_id = "demo-user-1"

    print("LangGraph 报销审核 Demo")
    print("输入 exit 退出。")
    print("示例：我今天打车去客户公司，申请报销 120 元。")
    print("示例：我参加外部培训，申请报销 8000 元。")
    print("示例：我想申请一次差旅报销。")
    print("示例多轮：先输入“报销”，再输入“1元”。")

    while True:
        user_input = input("\n请输入：").strip()

        if user_input.lower() in {"exit", "quit", "q"}:
            print("已退出。")
            break

        if not user_input:
            continue

        try:
            run_once(graph, user_input, thread_id)
        except Exception as exc:
            print("\n运行出错：")
            print(type(exc).__name__, exc)


if __name__ == "__main__":
    main()
```
