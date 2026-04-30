# 智能体 Agent

这份笔记只专注于 **Agent 本身**。它不是对话记录的简单抄写，也不是一份“从零到精通”的学习路线，而是一份围绕 Agent 这一对象重新组织过的系统性知识文档。文中会把我们对话里反复出现、但最容易混淆的几个问题统一起来：什么是 Agent，Agent 和 Workflow 到底差在哪，所谓“工具调用”“状态”“循环”分别是什么，多 Agent 是怎么交互的，工程上一个 Agent 项目通常怎样分层，以及为什么很多看起来很像的问题，其实都落在同一套运行机制上。

需要先明确一点：Agent 不是一种神秘的“更高级模型”，也不是某个框架的专属术语。更准确地说，Agent 是一种 **由语言模型驱动的任务执行系统**。它把模型的自然语言理解与推理能力，同工具、状态、循环控制、错误处理和外部系统连接起来，使模型不再只是一问一答地产生文本，而是在给定目标后，能够在边界内持续推进任务。

![Augmented LLM](http://public.file.lvshuhuai.cn/images\agent-anthropic-augmented-llm.png)

## Agent 的定义、边界与常见误解

### Agent 不是“会聊天的模型”，而是“会推进任务的系统”

在最朴素的聊天场景里，模型通常是一轮一轮地回答问题。用户给一句输入，模型给一句输出，这次交互就结束了。Agent 的不同之处不在于它“更聪明”，而在于它通常处在一个运行时闭环里。用户给它的不是一个瞬时问题，而是一个需要逐步完成的目标；模型给出的不只是自然语言答案，还可能是下一步动作；系统会把这个动作真正执行掉，再把结果返回给模型，让它继续决定后续步骤。

因此，Agent 的核心不在“回答”，而在“推进”。它的关注点不是“这一轮应该说什么”，而是“为了完成目标，下一步该做什么”。

把这层意思压缩成一句工程化的话，就是：

> **Agent = [[大语言模型 LLM]] + [[工具调用 Tool Calling]] + [[状态管理 State Management]] + Loop + Stop Conditions + Guardrails**

其中每个词都很重要。少了任意一块，系统都可能还能“看起来能聊”，但已经不是一个可靠的 Agent。

![Agent Components](http://public.file.lvshuhuai.cn/images\agent-components.png)

### Agent 不是框架，不是平台，也不是某个 SDK 的别名

很多人第一次接触 Agent，会先接触到 [LangChain](https://docs.langchain.com/oss/python/langchain/agents)、[LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)、[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)、Coze 或各种可视化平台，于是容易把 Agent 理解成“某种框架能力”或者“某个节点画布上的产物”。这是倒过来的。

更准确的关系是：

- **Agent 是概念和系统形态**
- **框架是实现 Agent 的工程工具**
- **平台是把 Agent 生产方式产品化后的交付形态**

你换不换框架，不改变 Agent 的本质。你可以用 Python 手写一个最原始的 loop，也可以用 [[LangGraph]] 把状态机画出来，也可以用平台把工具和节点配置出来，它们只是构建方式不同，不会把 Agent 从概念上变成别的东西。

### Agent 的“自主性”不是无限自由，而是边界内的行动选择

工程语境中的“自主”非常容易被误读。很多人会把 Agent 想象成一个能自己决定一切的数字员工，甚至把“自主”理解成某种开放式智能。真正可落地的 Agent 不是这样。

Agent 的所谓自主性，本质上是：

- 你告诉它目标
- 你告诉它可用工具
- 你给它运行边界和行为约束
- 它在这些边界内，自主决定下一步动作

所以，Agent 从来不是“想干什么就干什么”。它只能在系统开放给它的能力空间里行动。你不给天气工具，它就不能稳定查实时天气；你不给代码仓库读写权限，它就不能真正改代码；你不给支付接口，它就不能下订单。它最多只能在文本层面“建议”该怎么做，而不能真的完成动作。

这一点在后面的所有章节都会反复出现：**Agent 的能力边界是系统设计出来的，不是模型自带的。**

## 从 Workflow 到 Agent：区别不在“复杂度”，而在“谁决定下一步”

### 为什么 Agent 和 Workflow 总是被混着说

在今天的工程实践里，[[工作流 Workflow]] 和 Agent 常常同时出现。一个系统可能外层是固定流程，中间某一段是 Agent loop；也可能外层是一个 Agent，内部某些动作又被写成固定子流程。正因为它们经常混合出现，很多人会觉得两者边界模糊。

但从定义上说，它们有一个非常硬的区分标准：

> **下一步主要是谁决定的？**

如果系统下一步做什么，大部分是你在开发时就已经写死的，那它更像 Workflow。

如果系统下一步做什么，主要是在运行时由模型根据当前状态和工具结果决定，那它更像 Agent。

这就是最本质的差别。

### Workflow：预定义路径，模型只是其中一个节点

Workflow 更像流程图。你通常可以在编码前就把大部分路径画出来：先分类，再检索，再生成，再审核，再结束。模型在这种系统里当然仍然可以很重要，但它往往只是某个节点中的能力提供者，而不是整个系统的总调度者。

![Prompt Chaining Workflow](http://public.file.lvshuhuai.cn/images\agent-anthropic-prompt-chaining.png)

例如，“上传票据，识别 OCR，抽取字段，校验字段，写库”这种系统，虽然里面可能用了模型去做字段抽取，但整体路径仍然是程序员预定义的。模型没有真正决定系统主流程，它只是被嵌在一个固定步骤中完成一个局部子任务。

### Agent：目标驱动，路径由运行时动态展开

Agent 则不同。你给它的是目标和边界，而不是完整路径。它可能需要多次调用工具，多轮追问用户，中途改策略，甚至把子任务委派给别的 Agent。你在开发时通常不能完整知道它一定会先做什么、再做什么、做几次、什么时候停。你能规定的是工具集、最大步数、不可触碰的边界、输出格式和错误处理方式；至于具体路径，是运行时才展开的。

这一点决定了 Agent 和 Workflow 在工程实现上的气质完全不同。Workflow 追求的是流程正确性和可控性；Agent 追求的是在不确定问题上的行动弹性。但它们并不是敌对关系，而是两种不同的组织方式。很多成熟系统实际上就是：

- 外层用 Workflow 提供稳定骨架
- 局部用 Agent 提供动态能力

### 一个统一任务下的两种写法

为了避免只停留在概念层面，可以看一个统一任务：“帮用户订明天下午去上海的高铁”。

如果做成 Workflow，代码会长得很像：

```python
def book_ticket_workflow():
    departure = ask_user("你从哪里出发？")
    passenger = ask_user("乘客姓名是什么？")
    seat_type = ask_user("想要什么座位？")
    trains = search_trains(departure, "上海", "明天", "下午", seat_type)
    chosen = ask_user_to_choose(trains)
    return create_order(passenger, chosen, seat_type)
```

这段代码的关键点不是具体业务，而是路径被你写死了：问出发地、问乘客、问座位、查车次、让用户选、下单。它可以很实用，但从组织方式上仍然是 Workflow。

如果做成 Agent，骨架就会变成：

```python
while state["status"] == "running":
    action = llm_decide(state, tools)

    if action["type"] == "ask_user":
        reply = ask_user(action["question"])
        update_state_with_user_reply(state, reply)

    elif action["type"] == "tool_call":
        result = dispatch_tool(action["tool_name"], action["args"])
        update_state_with_tool_result(state, result)

    elif action["type"] == "final_answer":
        return action["content"]
```

这里的关键不在于 `while` 这个语法，而在于 `llm_decide(state, tools)` 这一层：系统下一步是问用户、查联系人、先查车次还是直接结束，不是你事先写死的，而是由模型在当前上下文下动态选择。

## Agent 的最小闭环：Tool Calling、Structured Output、State、Loop

讲清 Agent，本质上就是讲清它的运行闭环。围绕这个闭环，有四个最核心的专有名词：**Tool Calling、Structured Output、State、Loop**。如果只记一个骨架，可以记成：

![LangChain Agent Loop](http://public.file.lvshuhuai.cn/images\agent-langchain-core-agent-loop.png)

1. 读取当前状态  
2. 让模型决定下一步  
3. 若需要，调用工具  
4. 把结果写回状态  
5. 继续下一轮  
6. 直到满足停止条件

下面把这几个词逐个拆开。

### Tool Calling：模型不只是“回答”，还会“发起动作”

没有 Tool Calling，就没有真正意义上的 Agent。因为只要模型仍然只能输出自然语言，它最多只能“建议”做什么，而不能进入“行动”层。Tool Calling 的本质是：模型输出的不再只是文本内容，还会输出一种结构化的动作意图，告诉系统自己下一步需要哪个工具、要传什么参数。

![Tool Calling Flow](http://public.file.lvshuhuai.cn/images\agent-tool-calling-flow.png)

例如，面对“今天上海天气如何，帮我给出穿衣建议”这种请求，普通模型可能会直接给一个凭印象生成的回答。Agent 则更可能先输出一种动作：

```json
{
  "type": "tool_call",
  "tool_name": "get_weather",
  "args": {
    "city": "上海"
  }
}
```

然后由后端系统去执行真实的天气查询，把结果返回给模型，再让模型生成穿衣报告。这样得到的结果才能建立在外部世界的真实数据上，而不是只靠模型内部参数中的模糊记忆。

### Structured Output：系统必须知道“你现在是在回答，还是在请求动作”

Tool Calling 要成立，必须配套 Structured Output。后端不能靠猜测来判断模型当前的输出是在“真的回答用户”，还是“准备调用工具”。如果没有结构化协议，系统就无法可靠地区分这两种行为，也无法做参数校验、错误处理和状态更新。

所以，从工程角度说，Structured Output 不是为了美观，而是为了让模型和程序之间有一个稳定接口。它通常会约束模型输出成几类之一：

- 请求调用工具
- 继续追问用户
- 给出最终回答
- 在多 Agent 系统中转交给其他 Agent

一旦有了这种输出协议，后端才能安全地接管下一步，而不是对着一段自然语言瞎猜。

### State：Agent 真正依赖的不是“聊天记录”，而是“运行时状态”

很多初学者会把“聊天记录”和“状态”混为一谈。它们当然有关联，但不是同一个东西。

聊天记录是原始对话文本，保存了用户说过什么、模型回过什么、工具返回过什么。状态则是系统从这些输入中抽取、组织和维护出来的一份结构化任务上下文。它不仅包含对话历史，还可能包含：

- 当前任务目标
- 已收集到的字段
- 缺失信息清单
- 最近一次工具结果
- 当前所处阶段
- 是否需要人工确认
- 当前步数和预算

例如，用户说“帮我订明天下午去上海的高铁”，状态里可能会是：

```json
{
  "intent": "book_ticket",
  "destination": "上海",
  "date": "明天",
  "time_pref": "下午",
  "departure_city": null,
  "passenger_name": null,
  "seat_type": null,
  "missing_fields": ["departure_city", "passenger_name", "seat_type"],
  "current_step": "collect_missing_info"
}
```

这份状态显然比散落在聊天记录里的自然语言更适合被系统用于后续控制。也正因为如此，真正稳定的 Agent 几乎都需要显式状态层，而不能只靠把整段对话原样塞回模型。

### Loop：Agent 是一个持续决策和更新的运行时，而不是一次 API 调用

Agent 和普通问答系统最大的结构差别，就是它不会“一轮调用结束”。它通常处在一个 loop 里，持续地进行：读取状态、让模型决策、执行动作、更新状态，再回到下一轮。这个 loop 可以是非常简陋的 `while running`，也可以被封装进复杂的运行时引擎里，但本质上不会变。

一个简化的 loop 可以写成：

```python
tools = {
    "weather": get_weather,
    "news": get_news,
    "coding": write_code,
}

state = {
    "messages": [{"role": "user", "content": user_input}],
    "status": "running",
    "steps": 0,
    "max_steps": 8,
}

while state["status"] == "running":
    state["steps"] += 1
    if state["steps"] > state["max_steps"]:
        return "任务终止：超过最大步数"

    action = llm_decide(state, available_tools=list(tools.keys()))

    if action["type"] == "tool_call":
        result = tools[action["tool_name"]](**action["args"])
        state["messages"].append({
            "role": "tool",
            "name": action["tool_name"],
            "content": str(result)
        })

    elif action["type"] == "ask_user":
        return action["question"]

    elif action["type"] == "final_answer":
        state["status"] = "finished"
        return action["content"]
```

这段代码虽然极简，但已经展示了 Agent 的基本运行机制。真正复杂的系统只是在这之上增加了权限校验、手动确认、日志追踪、恢复执行、长任务 checkpoint、预算控制和多 Agent 编排而已。

## 后端到底知道什么，不知道什么

围绕 Agent，有一个很典型的误解：既然下一步是模型决定的，那后端是不是根本不知道 Agent 在干嘛？这个说法只对了一半。

### 后端不知道“下一步会想做什么”，但知道“这一步实际做了什么”

后端通常不会提前知道 Agent 下一轮究竟会选择天气工具、新闻工具、代码工具，还是直接结束。这部分是运行时动态决定的。

但一旦模型产出了结构化动作，例如：

```json
{
  "type": "tool_call",
  "tool_name": "coding",
  "args": {
    "task": "为 FastAPI 项目补一个 health check 接口"
  }
}
```

后端立刻就知道了三件事：

1. 模型这一步选择了哪个动作  
2. 要传给动作什么参数  
3. 执行后的结果是什么

然后，后端还要负责：

- 校验这个工具是否存在
- 判断当前权限是否允许调用
- 真正执行这个工具
- 把结果写回状态
- 记录日志和错误
- 决定是否进入下一轮

所以更准确的说法应该是：

> **后端不预先知道 Agent 会怎么走，但后端定义了它能怎么走，并负责执行它实际走出来的路径。**

### “能做什么”取决于你暴露了什么能力，而不是模型自己会什么

再举一个我们讨论过很多次的例子：一个“每日报告 Agent”可以查天气、生成穿衣建议，也可以查新闻、生成新闻摘要。那么它是不是还能写代码？

答案不是简单的“能”或“不能”，而是要拆成三层看。

第一层是文本层面。即使不给任何代码工具，一个通用模型也能“写一段代码文本”，因为那只是文本生成能力。

第二层是真实动作层面。要想让 Agent 真正修改代码、读仓库、跑测试、执行 shell、提交变更，系统必须明确暴露这些工具与权限。没有这些能力，它就无法成为真正的 Coding Agent。

第三层是职责边界层面。你完全可以在系统设计上规定：某个 Agent 即便从模型能力上“可能会写代码”，也不应该承担代码相关职责。因为职责边界的存在，本身就是工程设计的一部分。

所以，Agent 能做什么，不是由“模型想不想”决定的，而是由 **工具集合、权限集合和职责定义** 共同决定的。

## 一个 Agent 只能做一件事吗

### 从原理上说，不是；从工程上说，通常要控制边界

一个 Agent 当然可以做不止一件事。只要你给它多个工具和合理的任务定义，它完全可以同时覆盖天气报告、新闻报告、日程摘要、邮件摘要等多种功能。在这种情况下，它更像一个“总助理型 Agent”。

例如，用户说“今天穿什么”，它调用天气工具；用户说“今天发生了什么”，它调用新闻工具；用户说“今天的会都在几点”，它再调用日历工具。逻辑上并没有任何问题。

但工程上又不能因此得出结论：一个 Agent 会的越多越好。能力面越广，带来的问题越多，包括但不限于：

- Prompt 会越来越大，角色边界越来越模糊
- 工具数变多后，模型选错工具的概率会上升
- 状态设计会越来越复杂
- 测试成本和评估复杂度大幅上升
- 用户输入语义模糊时，更难判断应该走哪一条路径

因此，一般会有一个很实用的经验判断：

- **流程相近、工具相近、上下文相近的事情，可以合并给一个 Agent**
- **流程差异大、工具差异大、权限边界差异大的事情，更适合拆成多个专长 Agent**

这也是为什么很多系统最后会自然走向“一个 Router / Supervisor + 多个专长 Agent”的结构。不是因为单 Agent 不行，而是因为系统复杂度开始要求职责分离。

## 多 Agent 不是很多模型在群聊，而是可控的任务转交和上下文传递

多 Agent 常被想象成几个模型互相对话、互相讨论、互相启发。但工程里真正常见的交互方式，并不是这样抽象的“多智能体闲聊”，而是 **任务分派、控制权转移、共享状态和结果汇总**。

### Supervisor / Subagents：主 Agent 把子 Agent 当成高阶工具

这是最常见也最容易落地的一种模式。主 Agent 负责把握全局目标，子 Agent 各自只做某一类专长任务。主 Agent 不会把所有细节都留在自己身上，而是把一部分工作委派给子 Agent。做完之后，子 Agent 返回结果，主 Agent 再负责整合。

可以把它想成一个总控加若干专业分工：

- 总控 Agent：理解整体目标、规划子任务、整合结果
- 检索 Agent：负责查资料
- 代码 Agent：负责修改项目
- 总结 Agent：负责整理输出

在这种模式里，子 Agent 很像“高阶工具”。你调用它，不是因为它是一个普通函数，而是因为它自己内部也有状态和推理能力。

![Subagents Pattern](http://public.file.lvshuhuai.cn/images\agent-multi-agent-subagents.png)

### Handoff：控制权真的转给另一个 Agent

还有一种模式不是“总控一直调度”，而是当前 Agent 直接把控制权交给另一个 Agent。例如，一个分诊 Agent 判断当前请求是退款问题，于是把整个会话交给退款 Agent。之后用户的下一轮对话、工具使用和决策都由退款 Agent 主导。这时发生的不是普通工具调用，而是 **控制权转移**。

从实现上看，handoff 常常也会被表示成一种特殊工具，但它的语义不是“去调用一个外部函数”，而是“把当前任务交给另一个更合适的执行者”。

![Handoffs Pattern](http://public.file.lvshuhuai.cn/images\agent-multi-agent-handoffs.png)

### 并行 Fan-out / Fan-in：拆成多个子任务并行跑，再统一汇总

对于信息搜集、研究、批量分析这类任务，多 Agent 还有一种非常常见的模式：主 Agent 先做规划，再把不同子任务拆给多个 Agent 并行执行，最后统一汇总结果。这种结构非常适合复杂研究或大规模文档分析，因为它能够把每个子 Agent 的上下文限制在相对干净的小范围里，降低信息污染和上下文拥挤问题。

### 多 Agent 之间到底传什么

多 Agent 之间真正传递的，通常不是一整段自由闲聊，而是以下几类内容：

- 任务描述
- 必要上下文
- 中间结果
- 结构化摘要
- 控制权信息
- 状态更新

从这个角度看，多 Agent 的关键不在“数量”，而在 **交接机制**。你必须清楚回答这几个问题：

1. 谁决定下一棒交给谁  
2. 交接时带多少上下文  
3. 子 Agent 的结果以什么形式返回  
4. 共享状态由谁维护  
5. 如果结果冲突，谁来裁决

只要这五个问题没有设计好，多 Agent 就会迅速变成无法调试的复杂系统。

## Guardrails、停止条件与错误处理：没有这些，Agent 只是危险的自动机

很多关于 Agent 的介绍都会重点谈工具调用和规划能力，但真正把系统从“能演示”变成“能用”的，往往不是那些炫目的部分，而是约束与防护层。

### 为什么必须有停止条件

只要系统允许模型“自己决定下一步”，就必须同时允许系统“在某些情况下强行让它停下来”。否则一个模型就很容易在不完整信息下反复试探、反复调用工具，或者在失败后陷入无意义循环。

常见的停止条件包括：

- 达到最大步数
- 达到时间或 token 预算
- 工具连续失败超过阈值
- 用户未回复、需要人工确认
- 模型显式产出 `final_answer`
- 命中高风险动作，需要上层审批

停止条件的存在，不是为了让 Agent 变笨，而是为了让系统保持工程上的可控性。

### Guardrails 的本质：把“模型可能做出的危险动作”提前截住

Guardrails 可以非常轻，也可以非常重，但它至少要回答三个问题：

![Evaluator Optimizer Workflow](http://public.file.lvshuhuai.cn/images\agent-anthropic-evaluator-optimizer.png)

1. 当前动作是否合法  
2. 当前参数是否合理  
3. 当前 Agent 是否有权限执行这个动作

例如，模型提出“删除整个项目目录”，即便从输出协议上看它是一个结构合法的 tool call，也不应该真的执行；又如，模型给支付接口传了空金额、给数据库工具传了无约束查询、给代码执行器传了明显越权的命令，这些都应该在进入工具层之前被拦截。

所以从架构上讲，Guardrails 通常位于：

- LLM 输出之后
- 工具执行之前

它既不替代模型决策，也不替代工具逻辑，而是在中间提供最后一道安全检查。

## 工程实现：从 loop、tools 到项目分层

如果只从概念层讲 Agent，很容易让人觉得它只是 Prompt Engineering 的延伸。真正一上手写代码就会发现，Prompt 只是其中一层，真正决定系统质量的，是运行时组织方式。

### loop 的重点不在 while，而在 dispatch

我们在对话里多次提到：Agent loop 看起来常常就是一个 `while running`。这当然没错，但真正的重点不是 `while` 这个关键词，而是：

- 模型输出的动作如何被解析
- 动作如何被分发
- 工具如何统一注册
- 结果如何写回状态

如果你的代码写成：

```python
if tool == "weather":
    ...
elif tool == "news":
    ...
elif tool == "coding":
    ...
```

它也许能工作，但一旦工具多起来，马上会变得臃肿。更常见的做法是把工具做成注册表：

```python
tools = {
    "weather": get_weather,
    "news": get_news,
    "coding": write_code,
}
```

然后让调度层统一执行：

```python
tool = tools[action["tool_name"]]
result = tool(**action["args"])
```

这就是 dispatch 的意义。它把“模型如何选动作”和“系统如何执行动作”拆开了。前者是智能层，后者是运行时层，两者不应该混在一起。

### 一个 Agent 项目，目录应该按“职责”分层，而不是按“功能名字”分层

围绕 Agent 项目，最值得养成的一个习惯是：不要把所有代码都塞进 `main.py`，也不要按业务名复制粘贴一整套小系统。更合理的分法是按职责拆层：

- **app/**：入口层，HTTP、CLI、定时任务
- **agents/**：角色定义层，每个 Agent 的职责、提示词、可用工具
- **runtime/**：loop、dispatcher、state、guardrails
- **tools/**：暴露给 Agent 的动作接口
- **services/**：底层业务能力或第三方 API 封装
- **storage/**：会话、状态、checkpoint 的持久化
- **evals/**：评测数据和自动评测脚本
- **observability/**：日志、trace、事件记录
- **config/**：配置与常量

这种分法的好处是非常直接的：你清楚知道哪一层在“决定下一步”，哪一层在“执行动作”，哪一层在“保存状态”，哪一层在“记录问题”。项目不会因为功能增多而立刻变成一团。

### 一个最小可用目录

如果只是做单 Agent 原型，其实没必要一上来铺满目录。下面这种结构已经足够健康：

```text
my_agent/
├─ app/
│  └─ main.py
├─ agent/
│  ├─ agent.py
│  ├─ loop.py
│  ├─ state.py
│  └─ prompt.md
├─ tools/
│  ├─ weather.py
│  ├─ news.py
│  └─ registry.py
├─ models/
│  ├─ llm_client.py
│  └─ schemas.py
├─ storage/
│  └─ session_store.py
└─ tests/
   └─ test_agent.py
```

这个目录看起来不复杂，但已经把关键责任分开了。真正成熟的系统，只是在这个骨架上逐步增加多 Agent 编排、长任务恢复、评测与追踪。

## 语言与生态：Java 能不能做，为什么大家又总用 Python

关于语言选择，我们也讨论过一个很现实的问题：既然 Python 能做 Agent，Java 能不能做？答案当然是能，而且绝大多数事情 Java 都能做。真正的区别通常不在“能不能”，而在“是否顺手、生态是否集中、样例是否丰富”。

### 从能力范围看，Java 完全可以做 Agent

一个 Agent 项目最核心的需求包括：

- 调用大模型 API
- 设计状态对象
- 跑运行时 loop
- 调第三方工具
- 写 HTTP 服务
- 记录日志和事件
- 接数据库与消息队列

这些事 Java 全都能做，而且在企业后端、分层架构、长时间运行的服务、团队协作等方面，Java 甚至经常更稳、更规范。

### 为什么现实里大量 Agent 示例还是 Python

原因主要不在语言能力，而在生态集中度。当前 Agent 相关的实验、示例、框架、模型 SDK、工具库和教程，大量首先出现在 Python 世界。尤其当你的系统同时需要：

- LLM API 集成
- 各种工具封装
- 数据处理与评测
- 代码解释器或 notebook 验证
- 研究原型快速迭代

Python 的阻力通常更小。

但要注意，这并不意味着 [[笔记/开发/Java路线/Java|Java]] 不适合 Agent。更准确的说法应该是：

- **原理层面，语言无关**
- **工程层面，Java 完全能做**
- **生态与资料层面，Python 更占优势**

所以，真正应该问的不是“Java 行不行”，而是“我的目标是快速做原型，还是构建长期业务系统”。如果你的最终载体本来就是 Spring Boot 后端，那么用 Java 做 Agent runtime 完全合理；只是如果你在跟随当前大多数 Agent 教程或示例，Python 会显得更自然。
