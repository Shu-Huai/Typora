# 提示词 Prompt

## 定义

Prompt 不是一句简单的“问题”，而是模型在这一轮里收到的任务说明。

最简单的时候，它看起来就是一句自然语言：

```text
请用中文总结下面这段文章，控制在 100 字内。
```

但在真实的[[大语言模型 LLM]]应用里，Prompt 通常不止这一句话。它可能同时包含：

- 任务目标：让模型做什么。
- 上下文：模型依据什么来做。
- 约束条件：哪些规则必须遵守。
- 输出协议：结果要按什么格式返回。
- 行为边界：什么不能做，信息不足时怎么处理。

所以从应用开发角度看，Prompt 更像“任务协议”，不只是提问技巧。

![Prompt Example](http://public.file.lvshuhuai.cn/images\prompt-dair-introduction.png)

## 为什么 Prompt 重要

LLM 做的是下一 token 预测。它不会天然知道这一轮该聊天、抽取字段、调用工具，还是返回 JSON。你不说清楚，它就只能猜。

Prompt 写得清楚，模型行为通常会稳定得多。Prompt 模糊，模型就会在一堆可能性里摇摆。很多人把 Prompt Engineering 讲得很玄，其实最基本的原则很朴素：

把任务说清楚，把边界说清楚，把输出格式说清楚。

![Few-shot Prompting](http://public.file.lvshuhuai.cn/images\prompt-dair-few-shot.png)

一个好的 Prompt，至少要回答这些问题：

1. 你是谁？
2. 你现在要完成什么任务？
3. 你可以依赖哪些输入？
4. 你应该输出成什么样？
5. 什么情况下不能乱猜？

## Prompt 的常见组成

### 任务描述

先说明模型这一轮要做什么。

例如：

```text
请从下面的合同文本中提取甲方、乙方、签约日期、合同金额。
```

### 上下文

再给出模型可以依据的材料。

例如：

```text
合同文本如下：...
```

### 输出约束

指定返回形式。

例如：

```text
请输出为 JSON。若字段缺失，返回 null。
```

### 行为边界

限制模型不要乱补。

例如：

```text
不要猜测文本中不存在的信息。
```

把这些拼起来，就比一句“帮我看看这份合同”可靠很多。

![Meta Prompting](http://public.file.lvshuhuai.cn/images\prompt-dair-meta-prompting.png)

## Prompt 不只是纯文本块

在现代 API 里，Prompt 往往不是一整块字符串，而是一组带身份的消息。常见 role 有：

- `system`
- `developer`
- `user`
- `assistant`
- `tool`

也就是说，Prompt 在应用层已经被结构化了。

![Chat Templates](http://public.file.lvshuhuai.cn/images\prompt-huggingface-chat-templates.png)

传给模型服务的内容，可能不是单个字符串，而是这样的消息数组：

```json
[
  {"role": "developer", "content": "你是一个严谨的信息抽取助手。输出必须为 JSON。"},
  {"role": "user", "content": "请从下面简历中提取姓名、邮箱和最高学历。"}
]
```

这时就要理解 `role` 是什么。

## role 是什么

`role` 可以直接理解成“这段话是谁说的”。

不过它不只是标注来源，也是在表达指令层级。

### developer / system

这类消息通常放高层规则。它不是用户这一轮的具体问题，而是模型在整个应用里要遵守的行为规范。

例如：

```text
你是一个合同信息抽取助手。
输出必须是 JSON。
不要编造原文里没有的信息。
```

### user

这是用户这一轮真正想让模型做的事。

例如：

```text
请提取这份合同中的甲方、乙方、签约日期。
```

### assistant

这是模型前面已经说过的话。多轮对话时，历史 assistant 消息会被带回上下文，让模型知道前面发生了什么。

### tool

这是外部工具返回的结果，比如搜索结果、数据库查询结果、函数调用返回值。

## 为什么要分 role

如果把所有内容都塞进一个大 Prompt，模型很难稳定区分：

- 哪些是长期规则。
- 哪些是本轮任务。
- 哪些是历史输出。
- 哪些是工具结果。

拆成 role 以后，模型服务可以把规则、任务、历史和工具结果分层表达。这样更容易保持行为稳定，也更适合多轮对话、工具调用和优先级控制。

所以 `role` 不是为了好看，也不是语法糖。它是 Prompt 协议的一部分。

## API、Prompt、模型的关系

这里很容易混在一起。

### 模型本体

LLM 本体是模型参数和网络结构，比如 GPT、Qwen、Llama。模型真正做的事是：接收输入 token 序列，然后预测后续 token。

### API

像 [Chat Completions](https://platform.openai.com/docs/guides/text?api-mode=chat)、[Responses API](https://platform.openai.com/docs/guides/text?api-mode=responses)，它们不是模型本体，而是调用模型的接口协议。

API 负责接收应用层输入，组织消息结构，传入工具定义，管理前后轮状态，再把模型输出包装成程序方便消费的结果。

换句话说，API 决定的是怎么调用模型，不是模型是什么。

### Prompt 在哪里

Prompt 位于应用层和模型层之间。

对开发者来说，Prompt 可能是：

- 一段字符串。
- 一组 messages。
- messages + 工具定义 + 输出格式约束。

对模型来说，最后都要变成一串 token。

## Chat Completions 和 Responses API

### Chat Completions

Chat Completions 是较经典的聊天接口。核心输入是 `messages`，模型根据这些消息返回一条回复。

可以把它理解成：给模型一段聊天记录，让它继续往下接。

### Responses API

Responses API 更适合现代 agent 应用。它除了普通生成，还更强调：

- 状态串联。
- 工具调用。
- 多模态输入。
- 更完整的应用工作流。

如果目标是学习现代 LLM 应用，而不只是做聊天机器人，Responses API 这套思路更值得优先理解。

![Prompt Chaining](http://public.file.lvshuhuai.cn/images\prompt-dair-prompt-chaining.png)

两者可以粗略这样看：

- Chat Completions：更像聊天接口。
- Responses API：更像应用或 agent 接口。

但它们都属于接口层，不是模型层。

## role 是怎么连到 LLM 的

这是理解 Prompt 时最容易卡住的地方。

很多人会问：LLM 不是只接受文本吗？那 API 里的 `role`、`messages`、JSON，最后怎么进入模型？

答案是：模型底层并不会直接接收你代码里的 JSON。

应用层的消息结构会先经过模板化和序列化，转换成模型能识别的输入格式；再经过 tokenizer，变成 token 序列，最后送进模型。

实际链路大概是：

```text
messages / role
-> chat template
-> tokenization
-> token ids
-> Transformer
```

所以 role 和“模型接收文本”并不矛盾。更准确地说，模型接收的是 token 序列；role 是上层消息协议，最后会被转换成控制标记、特殊 token 或模型训练时约定好的格式。

### 什么是 [chat template](https://huggingface.co/docs/transformers/chat_templating)

chat template 可以理解成“把结构化消息翻译成模型输入”的模板。

例如，应用层有这样一组消息：

```json
[
  {"role": "developer", "content": "你是一个严谨的助手。"},
  {"role": "user", "content": "解释一下 Transformer。"}
]
```

模型不会直接看到这段 JSON。服务层会把它渲染成某种特定格式，例如：

```text
<开始标记>developer<消息分隔>你是一个严谨的助手。<结束标记>
<开始标记>user<消息分隔>解释一下 Transformer。<结束标记>
```

然后再送去 tokenizer。

不同模型使用的 chat template 不一定一样。这也是为什么同一个模型换了模板，效果可能明显不同。

![Active Prompt](http://public.file.lvshuhuai.cn/images\prompt-dair-active-prompt.png)

### `<|message|>` 这类标记是什么

在某些格式里，比如 OpenAI 的 Harmony 格式，`<|message|>` 这样的字符串不是普通文本，而是单独的特殊 token。

这说明聊天模型看的不只是自然语言，也包括训练时约定好的控制标记。

所以看到：

```text
<|start|>{header}<|message|>{content}<|end|>
```

不要把它只当成人类阅读用的分隔符。它本身就是模型输入协议的一部分。

不过这要看具体模型。`<|message|>` 是否是单独 token，取决于 tokenizer 和 prompt format。

## tool calling 仍然属于 Prompt 体系

工具调用看起来像是模型在操作外部世界，但底层仍然离不开消息协议。

![ReAct Prompting](http://public.file.lvshuhuai.cn/images\prompt-dair-react.png)

典型流程是：

1. 模型根据当前上下文，生成“我要调用某个工具”的结构化输出。
2. 应用程序读到这个工具调用请求。
3. 应用程序执行函数、搜索或数据库查询。
4. 执行结果作为一条新的 `tool` 消息追加回上下文。
5. 再次调用模型，让模型基于工具结果继续生成。

所以 tool calling 不是模型亲自执行函数，而是模型生成调用意图，外部程序执行，再把结果回灌给模型。

从这个角度看，工具调用仍然没有脱离 Prompt 和消息结构。

## 一个实用的 Prompt 模板

刚入门时，可以先用这个模板：

```text
你是一个[角色]。

你的任务是：[任务目标]。

请基于以下内容完成任务：
[上下文]

要求：
1. [约束 1]
2. [约束 2]
3. [约束 3]

输出格式：
[格式要求]

如果信息不足：
[兜底规则]
```

例如：

```text
你是一个信息抽取助手。

你的任务是：从用户消息中提取订票信息。

请基于以下内容完成任务：
“我下周三想从上海去北京，晚上出发，商务座优先。”

要求：
1. 不要猜测不存在的信息。
2. 保持字段名固定。
3. 缺失字段返回 null。

输出格式：JSON。

如果信息不足：缺失字段返回 null，不要补全。
```

这个模板已经覆盖了应用里最关键的几件事：角色、任务、上下文、约束、输出格式和兜底规则。后面做复杂应用时，可以在这个基础上继续加工具定义、示例、状态信息和错误处理规则。

![Chain of Thought Prompting](http://public.file.lvshuhuai.cn/images\prompt-dair-chain-of-thought.png)
