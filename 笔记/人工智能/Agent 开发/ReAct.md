# [ReAct](https://arxiv.org/abs/2210.03629)

> 本文只讨论 Agent 领域里的 **ReAct**，不是前端框架 React。
>
> ReAct 的核心是 **Reasoning + Acting**：模型在任务执行过程中交替进行“推理”和“行动”，并根据行动得到的观察结果继续调整下一步。

## ReAct 的基本位置：它不是模型，不是框架，而是一种 Agent 执行模式

ReAct 最早可以被理解为一种[[提示词 Prompt]] engineering 方法：让语言模型按照 `Thought → Action → Observation → Final Answer` 的格式解决问题。它的重点不是让模型一次性输出答案，而是让模型在过程中不断做出下一步决策。

但在现代[[智能体 Agent]] 工程里，ReAct 更准确地说是一种 **Agent loop 控制模式**。它通常不再依赖模型直接输出一段类似：

```text
Thought: ...
Action: ...
Action Input: ...
Observation: ...
Final Answer: ...
```

的纯文本格式，而是通过 **[[工具调用 Tool Calling]]、[[状态管理 State Management]]、工具执行器、观察结果回填、循环控制** 等机制实现。

可以先记住一个最核心的循环：

```text
Reason → Act → Observe → Reason → Act → Observe → Final
```

也可以写成更工程化的形式：

```text
用户任务
→ 模型基于当前上下文判断下一步
→ 模型产生工具调用
→ 系统执行工具
→ 工具结果作为 Observation 回填
→ 模型继续判断
→ 直到模型输出最终答案
```

ReAct 的意义在于：模型不再只是“生成答案”，而是参与一个可迭代的执行过程。它可以查资料、读文件、运行命令、调用 API、分析工具结果、修正计划，并最终完成任务。

![ReAct 原始论文中的推理与行动交替示例](http://public.file.lvshuhuai.cn/images\react-dair-react.png)

### ReAct 解决的核心问题

普通[[大语言模型 LLM]] 的典型模式是：

```text
用户问题 → 模型 → 最终回答
```

如果问题依赖外部信息、实时信息、代码执行结果、数据库结果，模型可能会凭记忆或概率分布直接回答。这会带来事实错误、幻觉、过时信息等问题。

Tool Calling 让模型具备了“调用外部工具”的能力：

```text
用户问题 → 模型决定调用工具 → 工具返回结果 → 模型回答
```

但单次 Tool Calling 还不是完整的 ReAct。ReAct 的关键在于 **迭代**：

```text
用户问题
→ 模型判断需要查 A
→ 调用工具 A
→ 观察结果
→ 模型发现还需要查 B
→ 调用工具 B
→ 观察结果
→ 模型整合信息
→ 最终回答
```

也就是说，ReAct 真正强调的是：

- 不是只调用一次工具；
- 不是固定流程；
- 而是模型根据每一步 Observation 动态决定下一步 Action。

![Agent 由模型、工具、记忆和规划等组件共同组成](http://public.file.lvshuhuai.cn/images\react-agent-components.png)

### ReAct 的五个基础名词

ReAct 的经典结构通常包含以下五个概念：

1. **Question / Task**

   用户交给 Agent 的任务。它可以是一个问题，也可以是一个操作目标，例如“帮我查某个 GitHub 仓库的最新 release 并总结”。

2. **Reason / Thought**

   模型对当前任务状态的判断。例如“这个问题需要实时信息，不能凭记忆回答”“当前 release notes 不够，需要继续查 tag 对应的详情”。在现代产品里，完整的内部推理通常不会直接展示给用户。

3. **Action**

   模型决定采取的动作。最常见的 Action 是工具调用，例如搜索、查数据库、读文件、运行 shell、调用 GitHub API、计算表达式。

4. **Observation**

   工具执行后的返回结果。Observation 会被重新放进上下文，供模型下一轮判断使用。

5. **Final Answer**

   模型停止继续调用工具，向用户给出最终回答。

ReAct 的判断标准不在于输出里有没有字面上的 `Thought:`，而在于系统是否真的执行了：

```text
基于当前状态判断 → 采取动作 → 读取观察结果 → 继续判断
```

## Tool Calling 不等于 ReAct

有一次[工具调用](https://platform.openai.com/docs/guides/function-calling)，不等于一定是典型 ReAct。

例如：

```text
HumanMessage
→ AIMessage(tool_call=get_latest_release)
→ ToolMessage(release_info)
→ AIMessage(final_answer)
```

这只是一个最短的工具调用循环。它可以看作“退化的一步 ReAct”，但教学上不够典型。

更典型的 ReAct 应该是：

```text
HumanMessage
→ AIMessage(tool_call=get_latest_release_metadata)
→ ToolMessage(tag_name, published_at, url)
→ AIMessage(tool_call=get_release_notes_by_tag，参数来自上一轮 observation)
→ ToolMessage(release_notes)
→ AIMessage(tool_call=days_since_utc，参数来自上一轮 observation)
→ ToolMessage(days_since)
→ AIMessage(final_answer)
```

关键点在于：

```text
下一步 Action 依赖上一步 Observation。
```

这才体现了 ReAct 的本质。

![工具调用把模型的动作意图转成外部系统可执行的结构化调用](http://public.file.lvshuhuai.cn/images\react-tool-calling-flow.png)

## 什么样的 Agent 可以称为 ReAct Agent

一个 Agent 系统要支持 ReAct，至少需要这些基础设施：

```text
1. 模型能够根据上下文决定下一步行动；
2. 系统能够执行 Action，例如工具调用、API 请求、代码执行；
3. 工具结果能够作为 Observation 回填给模型；
4. 系统能够保存中间状态，不会每一步都丢失上下文；
5. 有循环控制，例如最大步数、终止条件、错误处理。
```

但这只能说明这个系统 **能够支持 ReAct**，不能直接说明它就是 ReAct Agent。

### 支持 ReAct 与正在使用 ReAct 是两回事

可以这样区分：

```text
支持 ReAct 的 Agent Runtime：
    有 tool；
    有 state；
    有 memory；
    有 loop；
    有 observation 回填能力。

ReAct Agent：
    控制流真的按照 Reason → Act → Observe → Reason 的方式运行；
    每一步 action 由模型根据当前 state 和 observation 动态决定。
```

也就是说：

```text
loop + memory + state + tool
```

只是 ReAct 的基础设施，不是充分条件。

判断标准是：

```text
每一轮是否由模型基于当前 state / memory / observation 决定下一步 action？
```

如果答案是是，那么它就是 ReAct-style Agent。  
如果下一步由开发者写死的流程决定，那么它更像[[工作流 Workflow]]。

![现代 Agent loop 中模型、工具执行和 Observation 回填的关系](http://public.file.lvshuhuai.cn/images\react-agent-loop.png)

### 非 ReAct：固定流程的 Workflow

例如：

```python
def workflow(question):
    docs = retriever.search(question)
    answer = llm.generate(question, docs)
    return answer
```

这个系统也有工具，也可能有状态，但流程是固定的：

```text
输入 → 检索 → 生成 → 输出
```

模型没有根据 Observation 动态决定下一步要做什么。因此这不是典型 ReAct。

### ReAct：模型掌握行动决策权

更接近 ReAct 的写法是：

```python
while step < max_steps:
    decision = llm.decide(question, state, observations)

    if decision.is_final_answer():
        return decision.answer

    result = tool_executor.run(
        decision.tool_name,
        decision.arguments
    )

    observations.append(result)
    state.update(result)
```

这里的关键是：

```text
不是开发者写死下一步调用哪个工具；
而是模型根据当前状态决定下一步 action。
```

这才是 ReAct 的控制流。

### ReAct 与 Workflow 的工程取舍

ReAct 并不是在所有场景都更好。它适合：

- 问题路径不确定；
- 需要多步探索；
- 需要根据工具结果调整下一步；
- 需要查外部信息；
- 需要调试代码；
- 需要组合多个工具。

例如：

```text
查 GitHub release → 解析 tag → 查 release notes → 计算发布时间距今 → 总结
```

或者：

```text
运行测试 → 观察报错 → 修改代码 → 再运行测试 → 继续修复
```

但如果业务流程稳定，例如：

```text
参数校验 → 查数据库 → 生成固定格式报告 → 写入日志
```

那么 workflow 往往更适合。它更稳定、更便宜、更容易测试，也更容易审计。

ReAct 的代价是：

- 多轮模型调用，成本更高；
- 多次工具调用，延迟更高；
- 模型可能选错工具；
- 可能陷入循环；
- 需要更严格的终止条件；
- 需要更好的日志和错误处理。

因此，实际工程里常见的做法不是“所有任务都用 ReAct”，而是：

```text
稳定路径用 workflow；
不确定路径用 ReAct；
危险动作加人工确认；
复杂任务加入最大步数、超时、权限控制和日志审计。
```

## 用 LangChain 构建 ReAct Agent：从最小例子到多步工具链

[LangChain](https://docs.langchain.com/oss/python/langchain/agents) v1 的 `create_agent` 可以把模型、工具、状态和循环控制组织成一个 agent。模型决定是否调用工具，[[LangChain]] 执行工具，并把工具结果作为 ToolMessage 回填给模型。

这就是现代 ReAct-style Agent 的常见工程实现。

![编排者和工作者模式展示了复杂任务中动态调度和多步执行的结构](http://public.file.lvshuhuai.cn/images\react-orchestrator-workers.png)

### 环境变量：不要把 API Key 写进代码

建立 `.env` 文件：

```env
# Copy this file to .env and fill in your real API key.
OPENAI_API_KEY=your_real_api_key_here

# OpenAI-compatible model name.
OPENAI_MODEL=qwen3.6-plus

# For Alibaba Cloud DashScope OpenAI-compatible mode.
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

注意：

- 这里变量名叫 `OPENAI_API_KEY`，只是因为 `langchain-openai` 默认读取这个变量；
- 如果使用阿里云百炼 OpenAI-compatible API，需要配置 `OPENAI_BASE_URL`；
- 不要把真实 API Key 提交到 GitHub；
- 如果 key 已经暴露，应当立即重置。

### 安装依赖

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -U langchain langchain-openai langchain-core python-dotenv requests
```

### 多步 ReAct 示例：让后续工具调用依赖前一轮 Observation

为了更清楚地体现 ReAct，可以故意把任务拆成多个工具：

1. `get_latest_release_metadata`

   只查最新 release 的 tag、发布时间、URL，不返回 release notes。

2. `get_release_notes_by_tag`

   根据上一步观察到的 tag，再查 release notes。

3. `days_since_utc`

   根据上一步观察到的发布时间，计算距当前 UTC 时间过去多少天。

完整代码如下：

```python
import os
from datetime import datetime, timezone
from typing import Any

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "qwen3.6-plus")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or None

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in .env")


@tool
def get_latest_release_metadata(repo: str) -> str:
    """
    Get only metadata of the latest GitHub release.

    Args:
        repo: GitHub repository full name, for example "langchain-ai/langchain".

    Returns:
        Latest release tag, name, published_at, and URL.
        This tool intentionally does not return release notes.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"

    response = requests.get(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "langchain-react-demo",
        },
        timeout=20,
    )

    if response.status_code == 404:
        return f"No latest release found for repository: {repo}"

    response.raise_for_status()
    data = response.json()

    return (
        f"repo={repo}\n"
        f"tag_name={data.get('tag_name')}\n"
        f"name={data.get('name')}\n"
        f"published_at={data.get('published_at')}\n"
        f"url={data.get('html_url')}\n"
        f"note=This tool does not include release notes. "
        f"Use get_release_notes_by_tag(repo, tag) to fetch release notes."
    )


@tool
def get_release_notes_by_tag(repo: str, tag: str) -> str:
    """
    Get release notes for a GitHub release by tag.

    Args:
        repo: GitHub repository full name, for example "langchain-ai/langchain".
        tag: Release tag name, for example "langchain-core==1.3.2".

    Returns:
        Release notes excerpt.
    """
    url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"

    response = requests.get(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "langchain-react-demo",
        },
        timeout=20,
    )

    if response.status_code == 404:
        return f"No release found for repository={repo}, tag={tag}"

    response.raise_for_status()
    data = response.json()

    body = data.get("body") or ""

    return (
        f"repo={repo}\n"
        f"tag_name={data.get('tag_name')}\n"
        f"release_notes_excerpt:\n{body[:2000]}"
    )


@tool
def days_since_utc(iso_datetime: str) -> str:
    """
    Calculate how many days have passed from an ISO UTC datetime to now.

    Args:
        iso_datetime: ISO datetime string, for example "2026-04-24T15:49:42Z".
    """
    normalized = iso_datetime.replace("Z", "+00:00")
    start = datetime.fromisoformat(normalized)
    now = datetime.now(timezone.utc)

    delta = now - start

    return (
        f"input_time={iso_datetime}\n"
        f"now_utc={now.isoformat()}\n"
        f"days_since={delta.days}\n"
        f"total_seconds={int(delta.total_seconds())}"
    )


def build_agent():
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0,
        timeout=60,
    )

    tools = [
        get_latest_release_metadata,
        get_release_notes_by_tag,
        days_since_utc,
    ]

    system_prompt = """
You are a ReAct-style agent.

You must solve the task by iteratively using tools and observing their results.

Rules:
1. Do not invent GitHub release versions, dates, URLs, or release notes.
2. First use get_latest_release_metadata when the user asks for the latest GitHub release.
3. If release notes are needed, use get_release_notes_by_tag with the tag observed from get_latest_release_metadata.
4. If the user asks how long ago something was published, use days_since_utc with the observed published_at value.
5. After all required observations are collected, answer in Chinese.
6. In the final answer, summarize the tool-use path briefly, but do not expose hidden chain-of-thought.
"""

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )


def print_messages(result: dict[str, Any]) -> None:
    print("\n========== Agent Messages ==========\n")

    for i, message in enumerate(result.get("messages", []), start=1):
        message_type = getattr(message, "type", message.__class__.__name__)
        content = getattr(message, "content", "")

        print(f"[{i}] {message_type}")

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            print("Tool calls:")
            for tool_call in tool_calls:
                print(tool_call)

        if content:
            print(content)

        print()


def main():
    agent = build_agent()

    user_question = (
        "请查询 langchain-ai/langchain 这个 GitHub 仓库的最新 release。"
        "要求："
        "1. 给出版本号、发布时间、release 链接；"
        "2. 再根据版本号查询 release notes；"
        "3. 计算它距离当前 UTC 时间已经过去多少天；"
        "4. 最后用中文总结。"
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_question,
                }
            ]
        }
    )

    print_messages(result)

    final_message = result["messages"][-1]
    print("\n========== Final Answer ==========\n")
    print(final_message.content)


if __name__ == "__main__":
    main()
```

这个例子的预期消息链更接近典型 ReAct：

```text
[1] human
请查询 langchain-ai/langchain ...

[2] ai
Tool calls:
get_latest_release_metadata(repo="langchain-ai/langchain")

[3] tool
repo=langchain-ai/langchain
tag_name=langchain-core==1.3.2
published_at=2026-04-24T15:49:42Z
url=...

[4] ai
Tool calls:
get_release_notes_by_tag(
    repo="langchain-ai/langchain",
    tag="langchain-core==1.3.2"
)

[5] tool
release_notes_excerpt=...

[6] ai
Tool calls:
days_since_utc(
    iso_datetime="2026-04-24T15:49:42Z"
)

[7] tool
days_since=...

[8] ai
最终中文回答
```

关键在 `[4]` 和 `[6]`：

- `[4]` 的 `tag` 参数来自 `[3]` 的 Observation；
- `[6]` 的 `iso_datetime` 参数来自 `[3]` 的 Observation；
- 模型不是一开始就知道全部参数，而是根据工具结果继续行动。

这就是 ReAct 的核心。

![ReAct 在交互环境中通过行动和观察逐步推进任务](http://public.file.lvshuhuai.cn/images\react-dair-alfworld.png)

## ReAct 的工程边界：提示词、运行时、记忆与安全控制

ReAct 可以从两个层面理解：提示词层和运行时层。

### ReAct 最早像提示词工程，但现在不止是提示词

早期 ReAct 常用 prompt 约束模型输出：

```text
You are an agent. You can use the following tools:

search(query): search the web
calculator(expression): calculate a math expression

Use the following format:

Question: the input question
Thought: think about what to do next
Action: the action to take
Action Input: the input to the action
Observation: the result of the action
... repeat as needed
Final Answer: the final answer
```

这确实是 prompt engineering。

![ReAct 方法在不同任务上的效果对比](http://public.file.lvshuhuai.cn/images\react-dair-table1.png)

但在现代工程里，仅靠 prompt 不够。完整系统还需要：

```text
Prompt / System Instruction
+ Tool Calling
+ Tool Executor
+ Observation 回填
+ State / Memory
+ Agent Loop
+ Stop Condition
+ Error Handling
+ Logging / Tracing
```

因此，ReAct 更准确的分层是：

```text
ReAct 理念：
    推理和行动交替进行。

ReAct Prompt：
    用 Thought / Action / Observation / Final Answer 约束模型输出。

ReAct Runtime：
    系统真正执行工具调用、保存 Observation、继续下一轮模型调用。

ReAct Agent：
    按 ReAct 循环运行的完整 Agent 系统。
```

### Memory 与 State 在 ReAct 中的作用

ReAct 需要状态，但状态不等同于“长期记忆”。

可以分成几类：

1. **当前消息状态**

   包括用户问题、AIMessage、ToolMessage、最终回答等。这是 Agent loop 的基本上下文。

2. **Observation 状态**

   工具调用结果，例如 GitHub release metadata、release notes、计算结果、命令行输出。

3. **短期工作状态**

   当前任务进行到哪一步，哪些信息已经拿到，哪些工具调用失败过。

4. **长期记忆**

   用户偏好、历史项目背景、长期稳定的信息。不是所有 ReAct Agent 都必须有长期记忆。

在 ReAct 里，最关键的是 Observation 必须回填，否则模型无法根据上一轮行动结果决定下一步。

如果每一步都丢失上下文，那么就不是有效的 ReAct loop。

### 终止条件很重要

ReAct Agent 必须有终止机制。否则模型可能一直查、一直调用、一直修正。

常见终止条件包括：

```text
1. 模型输出 final answer；
2. 达到 max_steps；
3. 达到总超时时间；
4. 工具连续失败超过阈值；
5. 用户或人工审批中断；
6. 任务已经满足成功条件；
7. 检测到危险动作，需要停止或请求确认。
```

例如：

```python
max_steps = 8

for step in range(max_steps):
    decision = model(state)

    if decision.is_final:
        return decision.answer

    if decision.is_tool_call:
        observation = run_tool(decision.tool_call)
        state.add(observation)

return "任务未在最大步数内完成。"
```

这类约束是工程上必需的。没有它，Agent 的灵活性会变成不稳定性。

### ReAct 不应该暴露完整隐藏推理

早期 ReAct 格式里有 `Thought:`，但在现代系统中，不应该要求模型把完整内部推理过程展示给用户。

更好的做法是展示：

```text
Plan:
    简短计划

Action:
    调用了哪个工具

Observation:
    工具返回的关键信息摘要

Result:
    最终答案
```

而不是展示完整 chain-of-thought。

对 coding agent，例如 Codex 类系统，更合适的指令是：

```text
请按“计划 → 执行 → 观察 → 修正”的方式处理任务。

要求：
1. 先阅读相关文件，不要立刻改代码；
2. 给出简短计划；
3. 每次修改后运行相关测试或最小验证命令；
4. 如果测试失败，根据错误输出继续修正；
5. 不要一次性大改无关文件；
6. 最后总结改了哪些文件、为什么这样改、验证结果是什么。
```

这实际上就是 ReAct，只是换成了 coding agent 的语言。

### ReAct 的常见失败模式

ReAct 的灵活性来自模型动态决策，但失败也常常来自这里。

常见问题包括：

- 模型选择了错误工具；
- 工具参数构造错误；
- 工具返回结果太长，污染上下文；
- 模型误读 Observation；
- 模型重复调用同一个工具；
- 工具调用链太长，成本和延迟上升；
- 没有明确终止条件；
- 对危险动作缺少人工确认；
- 最终回答没有区分“工具观察到的事实”和“模型推断”。

工程上需要增加约束：

```text
max_steps
allowed_tools
timeout
tool_result_size_limit
retry policy
human approval
logging
structured final answer
error handling
permission boundary
```

![Evaluator-optimizer 模式可以用于为 Agent 的中间结果增加反馈和改进回路](http://public.file.lvshuhuai.cn/images\react-evaluator-optimizer.png)

### 如何判断日志里有没有 ReAct

你可以观察 Agent messages。

如果日志是：

```text
Human
→ AI tool_call
→ Tool
→ AI final
```

这说明发生了一次工具调用。它可以算最短 agent loop，但 ReAct 特征较弱。

如果日志是：

```text
Human
→ AI tool_call A
→ Tool A observation
→ AI tool_call B，参数来自 Tool A observation
→ Tool B observation
→ AI tool_call C，参数来自前面 observation
→ Tool C observation
→ AI final
```

这就是明显的 ReAct。

判断标准不是“出现了 tool_calls JSON”，而是：

```text
后续 Action 是否依赖前一轮 Observation？
```
