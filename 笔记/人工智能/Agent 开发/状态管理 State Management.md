# 状态管理 State Management

## Conversation State / Memory / State Management

在[[大语言模型 LLM]] 应用里，`Conversation State`、`Memory`、`State Management` 经常被一起提到，因为它们共同解决的是同一个问题：

> 模型本身不能跨请求天然记住一切，那么系统如何让它在多轮对话、多步骤任务、跨会话场景中持续正确工作？

这三个概念可以先做一个简化区分：

- **Conversation State**：当前这一次会话、当前这一个任务，系统现在处于什么状态。
- **Memory**：系统对用户、历史决策、过去事实、长期偏好的保存。
- **State Management**：系统如何表示、更新、存储、读取、裁剪这些状态和记忆。

它们不是三个孤立名词，而是一个完整系统的三个层面：

- state 解决“**现在**是什么”
- memory 解决“**过去**记住了什么”
- state management 解决“**怎么管**这些东西”

## 为什么 LLM 自己并不真正拥有会话状态

理解这几个概念，最核心的一步，是先把一个误区打掉：

> **LLM 本身并不会跨请求永久记住当前对话状态。**

从推理机制上看，[[Transformer]] 每次推理看到的只是这一次请求里的 token 序列。它会在本次前向计算中产生：

- hidden states
- attention weights
- KV cache
- 中间激活

这些东西都只属于**当前请求**。

请求结束后：

- 中间激活消失
- KV cache 通常也消失
- 模型权重不变
- 下次再来一个请求时，模型并不会自动知道你上次说过什么

所以，大模型跨请求能“记住”的信息，本质上只有两种来源：

<img src="http://public.file.lvshuhuai.cn/images\DbL2RbXFRoMWA5CrOaGB8.png" alt="KV 缓存解析：优化 Transformer 推理效率 - Hugging Face 文档" style="zoom: 25%;" />

### 参数记忆（Parametric Memory）

这是训练阶段写进模型参数里的统计规律和知识。

例如：

- 语言模式
- 一般世界知识
- 某些训练中学到的偏好或任务能力

它不是你当前对话临时写进去的，而是训练阶段形成的。

### 上下文记忆（Contextual / External Memory）

这是系统在新请求里再次喂给模型的内容，例如：

- 聊天历史
- 之前的摘要
- 当前状态 JSON
- 用户长期偏好
- 工具调用结果

模型看起来像“记住了”，本质上只是因为这些信息又被重新输入了一次。

因此，一个很重要的结论是：

> **Conversation State 和大多数工程上的 Memory，通常都不在模型内部，而是在模型外部。**

## Conversation State 是什么

Conversation State 指的是：

> **当前会话、当前任务的运行现场。**

它关注的是：系统现在进行到哪一步了，已经知道了什么，还缺什么，下一步该做什么。

比如用户说：

> 帮我订明天下午去上海的高铁。

这句话如果只作为自然语言聊天内容保存，系统当然也能继续工作。但在工程里，更常见的是把它抽成结构化状态，例如：

```json
{
  "intent": "book_train",
  "from_city": null,
  "to_city": "Shanghai",
  "date": "tomorrow",
  "time_pref": "afternoon",
  "passengers": [],
  "missing_fields": ["from_city", "passenger_count_or_names"],
  "stage": "collecting_required_info"
}
```

这个结构化对象，就比一堆聊天原文更像“状态”。

### 为什么不能只靠原始聊天记录

因为原始聊天记录有几个问题：

#### 冗长

多轮之后历史越来越长，token 成本、延迟、上下文占用都会上升。

#### 不确定

同一句话换个表达方式，模型每次都要重新理解一次。

#### 难以程序化处理

后端不方便直接判断：

- 还缺哪些字段
- 是否满足调用工具的条件
- 当前处于哪个流程阶段

而结构化 state 则可以直接被程序消费。

### Conversation State 典型包含什么

常见字段包括：

- 当前任务类型（intent / task_type）
- 当前流程阶段（stage / workflow_state）
- 已抽取出的槽位信息（slots / fields）
- 缺失字段（missing_fields）
- 最近一次工具调用结果索引（tool_context）
- 是否等待用户确认（awaiting_confirmation）

它通常是**短期的、面向当前任务的**。

## Memory 是什么

Memory 更强调：

> **系统对过去信息的保存与复用能力。**

如果说 Conversation State 关心“当前任务现场”，那么 Memory 更关心“未来回答时可能还会继续有用的信息”。

例如：

- 用户偏好中文回答
- 用户使用 Windows + PowerShell
- 用户主要写 Java
- 用户之前已经确定某个研究方案
- 用户不喜欢 argparse，希望把参数写在脚本顶部

这些信息并不一定属于当前某一个任务流程，但它们会持续影响未来的回答。

### Memory 可以按时间尺度来分

#### 短期记忆

最近几轮对话内容，仍然处于上下文窗口中。

#### 长期记忆

跨很多轮、甚至跨会话仍然保留的信息。

### Memory 可以按性质来分

#### Profile / Semantic Memory

稳定偏好、长期事实、用户画像。

例如：

- 偏好中文
- 常用 Java
- 使用 Windows 11

#### Episodic Memory

过去发生过的事件或讨论过的决定。

例如：

- 上次已经确定 caption 只在训练阶段用
- 某次讨论里决定不采用 instance loss

#### Procedural Memory

偏工作的规则、方法、行为模式。

例如：

- 给代码时不要用 argparse
- 研究脚本喜欢在顶部定义超参数

很多 agent 真正好用，不是因为“模型更聪明”，而是因为这几类记忆被分开管理了。

## State Management 是什么

State Management 不是一个具体字段，也不是某一种存储技术。

它是：

> **围绕 state 和 memory 的整套管理机制。**

它要解决的问题包括：

- 什么信息应该保存
- 什么信息应该丢弃
- 什么信息只在当前会话有效
- 什么信息应该写入长期 memory
- 旧历史太长时怎么办
- 新信息来了如何更新状态
- 多个工具调用之间如何共享中间结果
- 每轮请求前到底把哪些内容喂给模型

也就是说，State Management 涵盖三件事：

### 表示（Representation）

状态用什么结构表示？

- 纯消息列表
- JSON 状态对象
- 状态机节点
- 数据库记录
- 向量记忆条目

### 读写（Read / Write）

什么时候读？什么时候写？

- 请求开始前读取 session state
- [[工具调用 Tool Calling]] 后写回 tool result
- 回答结束后更新摘要
- 满足条件时写入长期 memory

### 裁剪与合成（Selection / Composition）

每次请求时，到底要把哪些内容组合成[[提示词 Prompt]]？

这一步通常是最核心、也最容易做差的部分。

## 一次请求内部到底发生了什么

理解 state management 最好的方式，不是盯着抽象概念，而是看一轮请求的真实流程。

一个典型的 LLM / agent 系统，请求流程通常不是：

> 用户一句话 -> 模型一句话

而更接近：

1. 接收用户输入
2. 读取当前 session state
3. 读取用户长期 memory
4. 读取最近消息和历史摘要
5. 组装 prompt
6. 调用模型
7. 如果模型要调工具，则执行工具
8. 把工具结果写回 state
9. 必要时再次调用模型
10. 返回自然语言回复
11. 更新消息、状态、摘要、长期 memory

一个伪代码示例如下：

```python

def handle_turn(user_id, session_id, user_message):
    session_state = load_session_state(session_id)
    user_profile = load_user_profile(user_id)
    recent_messages = load_recent_messages(session_id)
    history_summary = load_history_summary(session_id)
    retrieved_memories = retrieve_relevant_memories(user_id, user_message)

    prompt = build_prompt(
        system_rules=SYSTEM_RULES,
        user_profile=user_profile,
        session_state=session_state,
        history_summary=history_summary,
        recent_messages=recent_messages,
        retrieved_memories=retrieved_memories,
        current_user_message=user_message,
    )

    llm_output = model.generate(prompt)

    if llm_output.requires_tool:
        tool_result = call_tool(llm_output.tool_name, llm_output.tool_args)
        session_state = update_state_with_tool_result(session_state, tool_result)

        prompt2 = build_prompt(
            system_rules=SYSTEM_RULES,
            user_profile=user_profile,
            session_state=session_state,
            history_summary=history_summary,
            recent_messages=recent_messages,
            retrieved_memories=retrieved_memories,
            current_user_message=user_message,
            tool_result=tool_result,
        )
        final_output = model.generate(prompt2)
    else:
        final_output = llm_output

    persist_message(session_id, "user", user_message)
    persist_message(session_id, "assistant", final_output.text)
    save_session_state(session_id, session_state)
    maybe_update_long_term_memory(user_id, user_message, final_output)
    maybe_refresh_summary(session_id)

    return final_output.text
```

这段流程最重要的观察点是：

> **状态和记忆都在模型外部，模型只是消费它们，再输出新的解释、建议或动作。**

## 理解“状态推进”

我们用订票例子。这个例子很适合说明：

- state 不是聊天原文本身
- state 不是模型内部自动保存的
- state 更新真正由系统完成

### 初始状态

用户说：

> 帮我订明天下午去上海的高铁

系统最初状态可能是空的：

```json
{
  "intent": null,
  "from_city": null,
  "to_city": null,
  "date": null,
  "time_pref": null,
  "passengers": [],
  "missing_fields": [],
  "stage": "init"
}
```

### 模型读取“用户输入 + 当前状态”

LLM 读到这轮输入后，输出的不一定只是自然语言，它更理想的是输出两部分：

1. 给用户看的回复
2. 对状态的更新建议

例如：

```json
{
  "assistant_reply": "请问从哪个城市出发？有几个乘客？",
  "state_patch": {
    "intent": "book_train",
    "to_city": "Shanghai",
    "date": "tomorrow",
    "time_pref": "afternoon"
  },
  "next_action": "ask_user"
}
```

### 外部系统真正更新状态

系统拿到这个结构化结果后，才去真正 merge：

```json
{
  "intent": "book_train",
  "from_city": null,
  "to_city": "Shanghai",
  "date": "tomorrow",
  "time_pref": "afternoon",
  "passengers": [],
  "missing_fields": ["from_city", "passenger_count_or_names"],
  "stage": "collecting_required_info"
}
```

这里很关键：

> **LLM 不是直接改状态，它只是发出更新建议。真正写入 session / Redis / DB 的，是系统。**

### 下一轮继续推进

用户再说：

> 杭州出发，一个乘客，Peter

系统把：

- 新输入
- 当前状态
- 最近消息

再次交给 LLM。模型再输出新的自然语言 + 新的状态 patch。

最后系统继续 merge，直到 `missing_fields` 为空，进入 `ready_for_search`，再开始调用查票工具。

## 状态更新到底是谁在做

这是我们对话中的一个关键问题。

答案是：

> **真正做状态更新的是外部系统，LLM 只负责输出更新意图或更新建议。**

这个“建议”可以有不同表现形式。

### 方式一：普通[[结构化输出 Structured Output]]

例如模型直接返回：

```json
{
  "assistant_reply": "请问有几个乘客？",
  "state_patch": {
    "intent": "book_train",
    "to_city": "Shanghai",
    "date": "tomorrow"
  },
  "next_action": "ask_user"
}
```

然后系统：

- 解析 JSON
- 校验字段
- 合并 patch
- 重新计算状态
- 返回自然语言回复

这是最常见的方式。

### 方式二：内部工具调用

也可以把“更新状态”包装成类似工具调用的形式，例如：

```json
{
  "tool_name": "update_session_state",
  "arguments": {
    "patch": {
      "to_city": "Shanghai",
      "date": "tomorrow"
    }
  }
}
```

这种写法在形态上和[[函数调用 Function Calling]] 很像，但本质上它调用的是**系统内部状态管理模块**，而不是外部世界。

### 方式三：LLM 只提取字段，状态推进由后端控制

这是更稳的做法。

例如模型只负责输出：

```json
{
  "assistant_reply": "请问有几个乘客？",
  "extracted_fields": {
    "intent": "book_train",
    "to_city": "Shanghai",
    "date": "tomorrow",
    "time_pref": "afternoon"
  }
}
```

然后后端根据 schema 计算：

- 哪些必填字段还缺
- 当前阶段是什么
- 是否可以进入工具调用阶段

这个设计的核心思想是：

- **LLM 擅长理解自然语言**
- **后端擅长做确定性控制逻辑**

## LLM 能不能同时输出自然语言和 Structured Output

这个问题在实现上经常让人困惑。

[Structured model outputs | OpenAI API](https://developers.openai.com/api/docs/guides/structured-outputs)

结论是：

> **可以，但通常不是“schema 外自由文本 + 额外独立 JSON”这种形式，而是“一个结构化对象里既有自然语言字段，也有结构化字段”。**

例如：

```json
{
  "assistant_reply": "好的，请问有几个乘客？",
  "state_patch": {
    "intent": "book_train",
    "to_city": "Shanghai",
    "date": "tomorrow",
    "time_pref": "afternoon"
  },
  "next_action": "ask_user"
}
```

这里：

- `assistant_reply` 是自然语言
- `state_patch` 是结构化状态建议
- `next_action` 是控制信号

这仍然是一个 Structured Output。

### 两种常见模式

#### 模式 A：单轮结构化输出

让模型一次性输出：

- 给用户的话
- 结构化 patch
- 下一步动作建议

适合简单 agent。

#### 模式 B：双阶段流程

第一阶段：模型产出工具调用 / 状态更新参数。

第二阶段：系统执行更新或工具后，再让模型产出用户可见的自然语言回复。

适合流程更复杂、控制更强的系统。

## 为什么 `missing_fields`、`stage` 最好由后端算

这是工程里一个非常重要的边界。

通常可以把状态字段分成两类：

### 语义抽取字段：适合 LLM 产出

例如：

- `to_city`
- `date`
- `time_pref`
- `passenger_name`
- `intent`

因为这些字段本质上来自自然语言理解。

### 控制字段：更适合后端产出

例如：

- `missing_fields`
- `stage`
- `ready_for_search`
- `can_call_tool`
- `validation_errors`

因为这些字段更偏业务规则、确定性逻辑、状态机控制。

如果把这类字段完全交给模型，很容易出现：

- 模型误判已具备查票条件
- 模型遗漏某个必填字段
- 阶段跳转不稳定
- 不同说法导致控制逻辑漂移

更稳的方式是：

1. 模型提取业务语义字段
2. 后端根据 schema 和规则计算控制状态

例如：

```json
{
  "required_for_train_search": [
    "from_city",
    "to_city",
    "date",
    "passenger_count"
  ]
}
```

后端就可以自己算出：

- 还缺什么
- 是否可查票
- 当前属于哪个流程阶段

## Session、Conversation State、Memory、Context Window 的关系

这几个词很容易混。

### Session

Session 更像“会话容器”。

它通常会包含：

- message history
- session state
- history summary
- temporary tool context
- maybe some retrieval cache

它是一整包会话数据。

### Conversation State

是 session 里的“当前任务运行态”那一部分。

### Memory

是系统跨 session 或跨很多轮保留的信息。

### Context Window

是当前这次请求真正送进模型的 token 容器。

也就是说：

- 不是所有 memory 都会进入 context window
- 不是所有 session 数据都会进入 context window
- 每轮都要做一次“上下文选择”

这也是 state management 的核心工作之一。

## 为什么不能把所有历史都一直塞给模型

很多初学者会想：

> 那我把全部对话历史一直拼进去不就行了？

理论上可以，实践上通常不合适。

### 上下文窗口有限

再长的上下文窗口也不是无限的。

### 成本和延迟会持续上升

token 越多，调用越慢，花费越高。

### 注意力会被稀释

历史太长时，重要信息容易被淹没。

### 旧信息可能过时或冲突

全部原文无差别送进去，会让模型读到很多：

- 过时约束
- 已被覆盖的偏好
- 无关枝节

所以工程上更常见的是：

- 最近消息保留原文
- 更早历史压缩成 summary
- 长期信息做 memory 检索
- 当前任务抽成结构化 state

## 长期 Memory 常见怎么实现

长期 memory 通常不会只靠一种存储。

### 结构化 Profile Store

适合存：

- 用户偏好
- 明确事实
- 稳定配置

例如：

```json
{
  "language_preference": "zh-CN",
  "coding_preference": "Java",
  "os": "Windows 11",
  "shell": "PowerShell"
}
```

这类信息适合存在：

- [[Redis]]
- PostgreSQL
- MySQL
- MongoDB

优点：精确、可覆盖、可控。缺点：不适合模糊语义召回。

### 向量记忆库

<img src="http://public.file.lvshuhuai.cn/images\878c50ffb2783e0dd8fddc78f40fa4ef444c23a9-2036x820.png" alt="Introducing Canopy: An easy, free, and flexible RAG framework powered by Pinecone | Pinecone" style="zoom: 50%;" />

适合存：

- 历史对话片段
- 过去决策总结
- 项目背景信息

做法通常是：

1. 把历史片段整理为文本条目
2. 编码成 embedding
3. 存入向量数据库
4. 用当前 query 检索相关片段

优点：灵活，适合语义召回。缺点：可能误召回、漏召回。

### 原始文档 / 事件日志

保存最原始的 source of truth，例如：

- 完整对话日志
- 工具调用原始结果
- 用户上传文件
- 会议纪要

平时不全部送给模型，只在需要时检索或摘要。

## Conversation State 常见实现模式

### Message-only

只保存聊天消息，不额外维护结构化 state。

适合最简单的聊天机器人。缺点是多步骤任务容易乱。

### Message + Structured State

同时保留：

- 原始消息
- 结构化 session state

这是最常见、最实用的模式。

### 显式状态机 / Workflow Engine

把任务拆成明确节点：

- INIT
- COLLECT_INFO
- VALIDATE_INFO
- CALL_TOOL
- CONFIRM
- COMPLETE
- FAILED

这种方法适合高确定性业务，例如：

- 保险理赔
- 工单处理
- 审批系统
- 订票、报销等流程化任务

很多企业 agent 的做法是：

- 流程骨架由状态机控制
- 自然语言理解和字段抽取交给 LLM

## 一个最小可行实现方案

如果你想做一个最小的 stateful LLM 应用，可以先只维护四样东西：

1. `messages`：最近若干轮原始消息  
2. `session_state`：当前任务 JSON  
3. `user_profile`：长期偏好 JSON  
4. `history_summary`：更早历史的摘要  

每轮流程：

1. 读取这四样东西
2. 拼 prompt
3. 让模型输出：
   - `assistant_reply`
   - `state_patch` 或 `extracted_fields`
   - `should_call_tool`
   - `tool_name / tool_args`
4. 后端校验并合并状态
5. 如需工具则调用工具
6. 把结果写回状态
7. 保存消息
8. 必要时更新 summary 和 long-term memory

一个示意响应可以是：

```json
{
  "assistant_reply": "请问有几个乘客？",
  "extracted_fields": {
    "intent": "book_train",
    "to_city": "Shanghai",
    "date": "tomorrow",
    "time_pref": "afternoon"
  },
  "next_action": "ask_user",
  "should_call_tool": false
}
```

然后后端：

- merge `extracted_fields`
- 计算 `missing_fields`
- 决定当前 `stage`
- 判断是否允许进入下一步
