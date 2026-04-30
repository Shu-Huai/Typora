# 结构化输出 Structured Output

## 从一个很自然的疑问开始

在学习[[大语言模型 LLM]] 应用时，很多人第一次接触 Structured Output，都会有一个非常自然的疑问：模型底层不是一直都只是在“预测下一个 token”吗？既然它本质上只是不断生成 token，为什么最后却能返回一个看起来很规整的 JSON，甚至还能稳定地符合某种固定的数据结构？这个问题如果不想清楚，后面学 API、[[函数调用 Function Calling]]、[[工具调用 Tool Calling]]、Agent 这些东西时，就很容易一直带着一种模糊感，觉得“好像会用”，但没有真正理解它为什么成立。

这个问题的答案是，模型的本质并没有变。它仍然是在生成 token，并没有在底层突然变成某种数据库引擎，也没有突然开始“理解对象”或者“理解 JSON Schema”到类似编译器那样的程度。变化发生在应用接口这一层。也就是说，API 会把任务包装成一种更明确的约束：你不是在自由地生成一段自然语言，而是在一个指定结构的边界内完成输出。OpenAI 官方把这种能力称为 Structured Outputs，它的核心目标不是让模型“尽量输出 JSON”，而是让模型输出遵守你提供的 JSON Schema。这个差别非常关键，因为它决定了 Structured Output 不是一种单纯的提示技巧，而是一种明确的接口能力。

所以，从工程角度去理解，Structured Output 并不神秘。它并不是在改变模型“生成文本”的本质，而是在改变“你希望模型生成什么样的文本”以及“系统如何约束和解释这些文本”。过去你可能让模型自由回答一个问题，现在你要求它必须按某种结构返回结果；过去结果主要是给人看的，现在结果更多是给程序消费的。这个转变，正是从普通聊天式调用走向应用开发时最重要的一步之一。

## 什么是 Structured Output

Structured Output，核心就是一句话：

> **让模型按你预先规定的数据结构返回结果，而不是随意返回一段自然语言。**

<img src="http://public.file.lvshuhuai.cn/images\structured-outputs-process.png" alt="Structured Outputs: Everything You Should Know" style="zoom:50%;" />

这里的“结构”，通常用 **JSON Schema** 来描述。也就是说，你不只是告诉模型“请返回 JSON”，而是进一步规定：

- 返回值是对象还是数组
- 有哪些字段
- 每个字段是什么类型
- 哪些字段必须出现
- 是否允许额外字段
- 某些字段是否只能取固定枚举值

所以，Structured Output 关注的不是“看起来像 JSON”，而是“结果是否符合指定结构”。

## 为什么需要它

如果只用普通[[提示词 Prompt]]，比如：

> 请严格返回 JSON，不要输出别的内容

模型很多时候确实会配合，但它仍然可能出现这些问题：

- 在 JSON 前后多写一句解释
- 漏掉某个字段
- 把数字写成字符串
- 把字段名改掉
- 输出了你根本没定义过的字段

这些问题对人来说通常能看懂，但对程序来说往往会直接报错。

所以，Structured Output 的价值主要有两个：

### 可机读

- 后端可以直接解析
- 前端可以直接渲染
- 不需要从自然语言里二次提取字段

### 更稳定

- 结构约束不再只写在 prompt 里
- 而是正式写进 API 请求参数里
- 输出更适合进入程序逻辑

可以把它理解成

- 普通输出：写作文
- Structured Output：按表单填空

从这个角度看，Structured Output 其实是 LLM 应用工程化的一部分。它不是为了“让回答更整齐”，而是为了让模型输出真正能进入你的程序逻辑里，成为数据库字段、前端组件数据、[[工作流 Workflow]] 节点参数或者工具调用参数。很多人学 LLM API 时会觉得“为什么不能直接用 prompt 解决”，本质上是因为他们还停留在“把模型当聊天机器人”的视角；而一旦进入应用视角，就会发现，数据结构约束是绕不过去的。

## 它和普通输出、JSON mode、Function Calling 的区别

这几个概念很容易混。

### 普通输出

最普通的调用方式就是

- 你给模型一个问题
- 模型返回一段自然语言

特点

- 灵活
- 适合解释、写作、总结
- 不适合直接接程序解析

### JSON mode

JSON mode 的目标是：

- **保证输出是合法 JSON**

但它不保证：

- 字段名一定对
- 字段类型一定对
- 结构一定符合你的业务要求

也就是说，JSON mode 解决的是：

- “是不是合法 JSON”

而不是：

- “是不是我想要的那个 JSON”

举例来说，你要的是一个包含 `name`、`age`、`city` 三个字段的对象，而 JSON mode 可能会给你一个合法 JSON，但字段名写成了 `username`、`years_old`、`location`。从 JSON 语法角度看没有错，但从你的业务 schema 看已经错了。OpenAI 官方文档明确强调，JSON mode 只保证 valid JSON，而 Structured Outputs 则保证遵守你定义的 schema。

### Structured Output

Structured Output 更进一步，解决的是：

- “输出是否符合我给定的 schema”

也就是：

- 不只是 JSON
- 而且要符合指定结构

这是它和 JSON mode 最关键的差别。

### Function Calling

Function Calling 和 Structured Output 很像，因为它们都依赖 schema。

但区别在于：

- **Structured Output**：重点是“结构化回答”
- **Function Calling**：重点是“结构化动作”

更直白一点：

- Structured Output：模型直接返回结构化结果
- Function Calling：模型先生成某个工具调用及其参数，然后由程序执行这个工具

所以可以这样记：

- 想让模型直接给你一个结构化答案，用 Structured Output
- 想让模型驱动系统去做事，用 Function Calling

## 它是怎么做到的

从工程角度看，Structured Output 的逻辑并不复杂，大致就是 4 步。

### 先定义 schema

你先明确结果应该长什么样。

例如：

- 返回一个对象
- 包含 `name`、`age`、`city`
- `age` 必须是整数
- 三个字段都必须出现
- 不允许额外字段

### 把 schema 放进请求里

重点来了：

Structured Output 不是单靠 prompt 实现的。

它真正的关键是：

- 你把 schema 作为 **API 参数** 提交给模型

也就是说，结构要求不是“建议”，而是“正式请求的一部分”。

### 模型按这个结构生成

这个时候模型仍然是在生成 token。

但是它不再是在自由写一段自然语言，而是在受约束地生成符合 schema 的结果。

这时常会看到一个参数：

- `strict: true`

它的含义可以简单理解为：

- 不要“差不多”
- 要尽量严格按 schema 来

### 应用侧解析结果

模型返回后，你的程序就可以：

- 直接解析 JSON
- 映射为对象
- 写入数据库
- 传给前端
- 传给其他工作流节点

到这里，模型输出就真正从“文本”变成了“结构化数据”。

## Strict 的本质

**`strict: true` 的本质，不是让模型自己变成 JSON 编译器，而是在模型生成 next token 时，外部推理引擎根据 schema 编译出的 CFG，动态裁掉所有不合法 token；模型只在合法轨道内继续生成。** 训练让它更会“往这条轨道上走”，约束解码让它“走不出轨道”。

OpenAI 公开讲过，它是“两段式”实现：一段是**训练层**，让模型更理解复杂 schema、知道什么样的输出更符合结构；另一段是**推理/解码层**，用一个确定性的工程机制把不合法 token 直接屏蔽掉。官方明确说，单靠模型能力提升后，在他们的基准上也只有 93% 左右，还不够，所以又加了一个“deterministic, engineering-based approach”来做到 100% 可靠。

所以，从“模型侧”严格来说，`strict: true` **不是**“给模型内部某层加一个开关，然后它自己就会老老实实输出”。更接近真实情况的说法是：**模型仍然像平常一样产生 next-token 的概率分布，但推理引擎在每一步只允许那些符合当前 schema 状态的 token 被选中**。OpenAI 把这件事称为 **constrained decoding / constrained sampling**。

它的核心过程可以概括成这样。首先，系统把你给的 JSON Schema 转成一个 **context-free grammar，CFG，上下文无关文法**。这个文法描述的是：什么样的 JSON 串在这个 schema 下是合法的。然后，在生成时，每出一个 token，系统都会根据“已经生成的前缀 + 这份 CFG”计算出“下一步哪些 token 还是合法的”。最后，把所有不合法 token 的概率直接压成 0，只在合法集合里继续采样。官方原话就是：他们会在每一步根据 grammar 算出 valid tokens，然后对下一步采样做 mask，使 invalid tokens 的概率降为 0。

<img src="http://public.file.lvshuhuai.cn/images\hq720.jpg" alt="Structured Output from LLMs: Grammars, Regex, and State Machines" style="zoom: 80%;" />

这意味着，`strict: true` 的关键实现点，其实在**解码器外围的约束层**，而不是单纯在模型权重内部。模型负责“在合法候选里，哪个更像它想说的”；约束层负责“哪些候选压根不允许出现”。你可以把它理解成：模型像一个会写字的人，`strict: true` 像一个实时语法警察，站在旁边，每写一个 token 就检查一下，凡是不可能通向合法 schema 的 token，一律不准写。

这也解释了为什么 OpenAI 说**第一次用一个新 schema 会有额外延迟**。因为系统要先把 schema 预处理成一个便于推理时快速查询的文法/缓存结构。官方明确写到：首次请求有 latency penalty，就是因为要 preprocess schema，生成后续采样时高效使用的 artifact。

你如果更关心“具体到 logits 层发生了什么”，可以把它想成下面这件事。通常模型会输出整个词表上每个 token 的 logits；而在 `strict: true` 下，推理系统会先算出当前允许的 token 集合 `V_valid`，然后把不在 `V_valid` 里的 token 全部 mask 掉。等价地说，就是把这些 token 的 logits 视为 `-inf`，使 softmax 后它们的概率变成 0。于是最终采样只会发生在合法 token 里面。这个“mask next-token distribution”的思路，正是 OpenAI 公开描述的 constrained decoding 机制。

再往深一点说，为什么要用 CFG，而不是简单正则或有限状态机。OpenAI 给的解释是，很多替代方案会用 FSM 或 regex，但 CFG 能表达更广的一类语言，尤其对**嵌套和递归 schema**更有优势。对于简单平面 JSON，这个差别不一定明显；但一旦 schema 里有递归结构、深层嵌套、`$ref` 之类，FSM 通常就不如 CFG 好表达。OpenAI 还专门举了递归 UI schema 作为例子，说明这类结构更适合 CFG 方案。

还有一个很重要的边界要说清楚：`strict: true` **保证的是结构合法**，不是“值一定正确”。官方明确提醒，Structured Outputs 不能防止所有模型错误。比如数学步骤里算错了、字段值语义上错了、日期理解错了，这些都仍然可能发生。它保证的是“长得对”，不是“内容一定真”。

## 一个最重要的认识：它不是只靠 prompt

这是最容易误解的一点。

很多人会觉得：

> Structured Output 不就是 prompt 写得更严格一点吗？

不是。

两者的本质区别在于：

### 只用 prompt 时

你是在说：

- “请你尽量按这个格式输出”

### 用 Structured Output 时

你是在说：

- “这是本次请求要求的正式结构，请按这个 schema 返回”

所以，最值得记住的一句话是：

> **Structured Output = prompt + schema + API 约束，而不是只有 prompt。**

这里三者的职责分别是：

- **prompt**：决定说什么
- **schema**：决定长什么样
- **API 约束**：决定这不是建议，而是正式要求

##  为什么 `required` 和 `additionalProperties: false` 很重要

在 schema 设计里，有两个东西非常常见：

- `required`
- `additionalProperties: false`

它们看上去像小细节，实际上非常重要。

### `required`

它表示哪些字段必须存在。

如果一个字段对业务来说是必需的，比如：

- 用户名
- 订单号
- 分类标签

那就不应该只是“希望模型输出”，而应该明确写进 `required`。

### `additionalProperties: false`

它表示：

- 不允许模型额外补出你没定义的字段

为什么这很重要？

因为如果不限制，模型可能会加一些“看起来合理但业务里没定义过”的字段，导致：

- 解析逻辑变复杂
- 前后端字段不一致
- 类型系统不稳定

所以，这两个配置其实体现的是同一种工程思路：

> **能明确规定的，就不要留给模型自由发挥。**

## 在 Responses API 里怎么用

当前学习 OpenAI 新接口时，一个关键点是：

- 新项目通常更推荐用 **Responses API**

在这个接口里，Structured Output 的核心入口是：

- `text.format`

也就是说，结构化输出不是旁门左道，而是正式文本生成接口的一部分。

你可以把它理解成下面这个请求形状：

1. 先正常传入：
   - `model`
   - `input`

2. 然后额外传入：
   - `text.format`
   - `type: "json_schema"`
   - schema 名称
   - `strict`
   - schema 本身

这样，这次调用就不再是“生成一段普通文本”，而是“生成一个符合 schema 的结构化结果”。

## 一个最小例子

下面是一个很小的示意：

```json
{
  "model": "gpt-5.4",
  "input": [
    { "role": "system", "content": "从用户输入中提取结构化信息。" },
    { "role": "user", "content": "我叫张三，28岁，在上海工作。" }
  ],
  "text": {
    "format": {
      "type": "json_schema",
      "name": "user_profile",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "age": { "type": "integer" },
          "city": { "type": "string" }
        },
        "required": ["name", "age", "city"],
        "additionalProperties": false
      }
    }
  }
}
```

这段例子的重点不是语法细节，而是结构：

- `model`
- `input`
- `text.format`
- `json_schema`
- `strict`
- `schema`

你只要先把这个骨架记住，后面换成自己的业务字段就行。

