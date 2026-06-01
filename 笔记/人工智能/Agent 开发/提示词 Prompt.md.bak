# 提示词 Prompt

## 定义

**Prompt 不是一句“问题”，而是模型在这一轮工作时接收到的任务说明。**

在最简单的场景里，Prompt 看起来像一句自然语言，例如：

```text
请用中文总结下面这段文章，控制在 100 字内。
```

但在真实的[[大语言模型 LLM]] 应用里，Prompt 往往不只是这句话。它通常同时包含：

- 任务目标：你要模型做什么
- 上下文：模型依据什么来做
- 约束条件：模型要遵守什么限制
- 输出协议：模型要按什么格式输出
- 行为边界：模型不能做什么，信息不足时怎么办

所以，从应用开发的角度看，**Prompt 更接近“任务协议”而不是“提问技巧”**。

![Prompt Example](http://public.file.lvshuhuai.cn/images\prompt-dair-introduction.png)

## 为什么 Prompt 重要

LLM 本质上是在做下一 token 预测。它并不会天然知道你这轮到底是要它“聊天”、还是“抽取字段”、还是“调用工具”、还是“返回 JSON”。这些都需要由 Prompt 来界定。

Prompt 做得越清楚，模型行为通常越稳定；Prompt 模糊，模型就只能猜。很多人把 Prompt Engineering 想得很玄，其实最核心的原则很朴素：

**把任务说清楚，把边界说清楚，把输出格式说清楚。**

![Few-shot Prompting](http://public.file.lvshuhuai.cn/images\prompt-dair-few-shot.png)

一个好的 Prompt，通常至少回答了下面几个问题：

1. 你是谁？
2. 你现在要完成什么任务？
3. 你可以依赖哪些输入？
4. 你应该输出成什么样？
5. 什么情况下不能乱猜？

## Prompt 的常见组成

### 任务描述

先明确模型这一轮要干什么。

例如：

```text
请从下面的合同文本中提取甲方、乙方、签约日期、合同金额。
```

### 上下文

再告诉模型依据什么来做。

例如：

```text
合同文本如下：...
```

### 输出约束

指定返回的形式。

例如：

```text
请输出为 JSON。若字段缺失，返回 null。
```

### 行为边界

限制它不要乱补。

例如：

```text
不要猜测文本中不存在的信息。
```

把它们拼起来，就比一句泛泛的“帮我看看这份合同”强很多。

![Meta Prompting](http://public.file.lvshuhuai.cn/images\prompt-dair-meta-prompting.png)

## Prompt 不只是纯文本块：消息结构的出现

在现代 API 里，Prompt 常常不是一整块字符串，而是一组带身份的消息。最常见的形式是：

- `system`
- `developer`
- `user`
- `assistant`
- `tool`

这意味着：**Prompt 在应用层已经被结构化了。**

![Chat Templates](http://public.file.lvshuhuai.cn/images\prompt-huggingface-chat-templates.png)

也就是说，你传给模型服务的，不一定是单个字符串，而可能是这样的消息数组：

```json
[
  {"role": "developer", "content": "你是一个严谨的信息抽取助手。输出必须为 JSON。"},
  {"role": "user", "content": "请从下面简历中提取姓名、邮箱和最高学历。"}
]
```

这时就要理解：`role` 到底是什么。

## role 是什么

`role` 的意思可以直接理解为：**这段话是谁说的。**

但它的作用不只是“标注来源”，更重要的是表达**指令层级**。

### developer / system

这类消息通常放高层规则。它不是用户这轮的具体问题，而是模型在整个应用里工作的行为规范。

例如：

```text
你是一个合同信息抽取助手。
输出必须是 JSON。
不要编造原文里没有的信息。
```

### user

这是用户这轮真正想让模型完成的事。

例如：

```text
请提取这份合同中的甲方、乙方、签约日期。
```

### assistant

这是模型前面已经说过的话。多轮对话时，会把历史 assistant 消息也带回去，让模型知道上下文。

### tool

这是外部工具返回的结果，例如搜索结果、数据库查询结果、函数调用返回值等。

## 为什么必须分 role

因为如果把所有内容都混成一个大 Prompt，模型很难稳定地区分：

- 哪些是长期规则
- 哪些是本轮任务
- 哪些是历史输出
- 哪些是工具结果

而一旦拆成 role，模型服务就能把“规则”和“任务”分层表达。这样做的价值在于：

1. 更容易保持行为稳定
2. 更容易做多轮对话
3. 更容易插入工具调用结果
4. 更容易表达优先级

所以，`role` 不是语法糖，也不是为了好看；它是 Prompt 协议的一部分。

## API、Prompt、模型，这三者是什么关系

这里最容易混。

### 模型本体是什么

LLM 本体是模型参数和网络结构本身，例如 GPT、Qwen、Llama。模型真正做的事情是：

**接收输入 token 序列，然后继续预测后续 token。**

### API 是什么

像 [Chat Completions](https://platform.openai.com/docs/guides/text?api-mode=chat)、[Responses API](https://platform.openai.com/docs/guides/text?api-mode=responses)，它们不是模型本体，而是**调用模型的接口协议**。

它们负责做的是：

- 接收应用层输入
- 组织消息结构
- 传入工具定义
- 管理前后轮状态
- 把模型输出包装成程序方便消费的结果

所以，API 决定的是“怎么调用模型”，不是“模型本身是什么”。

### Prompt 在哪里

Prompt 处在应用层和模型层之间。

对开发者来说，Prompt 可能表现为：

- 一段字符串
- 一组 messages
- 一组消息 + 工具定义 + 输出格式约束

对模型来说，最后它仍然只会看到：

**一串 token。**

## Chat Completions 和 Responses API

### Chat Completions

这是较经典的聊天接口。核心输入是 `messages`，模型根据这些消息返回一条回复。

你可以把它理解为：

> 给模型一段聊天记录，让它继续往下接。

### Responses API

这是更新、更适合 agent 应用的一层接口。它除了能做普通生成，还更强调：

- 状态串联
- 工具调用
- 多模态输入
- 更完整的应用型工作流

如果你的目标是学现代 LLM 应用，而不是只学“聊天”，那更值得优先理解 Responses API 这套思路。

![Prompt Chaining](http://public.file.lvshuhuai.cn/images\prompt-dair-prompt-chaining.png)

### 两者的本质关系

- Chat Completions：更像聊天接口
- Responses API：更像应用 / agent 接口

但不管是哪一种，它们都只是**接口层**，不是模型层。

## 最关键的问题：role 是怎么连到 LLM 的

这是理解 Prompt 最底层的地方。

很多人会想：

> LLM 不是只接受纯文本吗？
> 那 API 里的 `role`、`messages`、JSON，到底怎么进入模型？

答案是：

**模型底层不直接接收你代码里的 JSON。**

应用层的消息结构，会先经过一层“模板化”和“序列化”，被转换成模型能识别的输入格式，然后再经过 tokenizer，最终变成 token 序列送进模型。

也就是说，实际链路是：

```text
messages / role
-> chat template
-> tokenization
-> token ids
-> Transformer
```

所以，role 并不是和“模型接受文本”相矛盾。更准确的说法应该是：

**模型接受的是 token 序列；role 只是上层消息协议，它会在下层被转换成控制标记或特殊 token。**

### 什么是 [chat template](https://huggingface.co/docs/transformers/chat_templating)

chat template 可以理解成“把结构化消息翻译成模型输入”的模板。

例如，在应用层你有：

```json
[
  {"role": "developer", "content": "你是一个严谨的助手。"},
  {"role": "user", "content": "解释一下 Transformer。"}
]
```

但模型不会直接看到这段 JSON。服务层会把它渲染成一种特定格式，例如：

```text
<开始标记>developer<消息分隔>你是一个严谨的助手。<结束标记>
<开始标记>user<消息分隔>解释一下 Transformer。<结束标记>
```

再把这串内容送去 tokenizer。

不同模型使用的 chat template 不一定一样，这也是为什么“同一个模型，换了模板，效果会明显不同”。

![Active Prompt](http://public.file.lvshuhuai.cn/images\prompt-dair-active-prompt.png)

### `<|message|>` 这类标记是什么

在某些特定格式里，例如 OpenAI 的 Harmony 格式，`<|message|>` 这样的字符串不是普通文本，而是**单独的特殊 token**。

这说明一件重要的事：

> 聊天模型不仅仅是“看自然语言”，它也在看一套训练时约定好的控制标记。

所以，当你看到：

```text
<|start|>{header}<|message|>{content}<|end|>
```

不要把它理解成“只是为了人看着方便的分隔符”，而要理解成：

**它本身就是模型输入协议的一部分。**

不过要注意，并不是所有模型都一定使用这套格式。`<|message|>` 是否是一个单独 token，要看具体模型的 tokenizer 和 prompt format。

## tool calling 其实仍然属于 Prompt 体系

工具调用看起来很像“模型会操作外部世界”，但底层机制仍然是 Prompt 协议的延伸。

![ReAct Prompting](http://public.file.lvshuhuai.cn/images\prompt-dair-react.png)

典型过程是：

1. 模型根据当前上下文，生成一个“我要调用某个工具”的结构化输出
2. 应用程序读到这个工具调用请求
3. 应用程序真正执行函数 / 搜索 / 查询数据库
4. 把结果作为一条新的 `tool` 消息追加回上下文
5. 再次调用模型，让模型基于工具结果继续生成

所以，tool calling 本质上不是“模型亲自去执行函数”，而是：

**模型生成工具调用意图，外部程序执行，执行结果再回灌给模型。**

从这个角度看，它仍然没有脱离 Prompt 和消息协议。

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

这个 Prompt 已经具备了应用场景里比较重要的四件事：角色、任务、约束、输出格式。

![Chain of Thought Prompting](http://public.file.lvshuhuai.cn/images\prompt-dair-chain-of-thought.png)
