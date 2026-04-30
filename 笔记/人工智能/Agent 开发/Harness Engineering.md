# Harness Engineering

> 本文专注于 AI 语境中的 Harness Engineering。它不是 [Prompt Engineering](https://www.promptingguide.ai/) 的同义词，也不是简单的测试脚手架，而是围绕模型构建一整套“可执行、可验证、可审计、可迭代”的工作环境，使模型从会生成文本的智能核心变成能够稳定完成任务的 Agent。

## 问题域：为什么需要 Harness Engineering

大模型本身并不是完整的[[智能体 Agent]]。一个[[大语言模型 LLM]] 可以生成自然语言、代码、计划、工具调用意图，但它不会天然拥有文件系统、项目知识、运行环境、权限边界、测试反馈、长期状态和审计能力。所谓 Agent，真正落地时通常是一个组合系统：模型负责推理和生成，模型外部的环境负责提供上下文、工具、执行、验证和约束。

可以用一个简化公式理解：

```text
Agent = Model + Harness
```

其中：

- **Model** 是智能核心，负责理解任务、生成方案、选择工具、解释结果。
- **Harness** 是模型外部的工程系统，负责让模型能够看见正确上下文、调用安全工具、在受控环境中执行动作，并根据验证反馈修正结果。

![Augmented LLM 的基础构件](http://public.file.lvshuhuai.cn/images\harness-anthropic-augmented-llm.png)

这也是 Harness Engineering 的基本出发点：**不把可靠性完全寄托在模型“更聪明”上，而是在模型外部构造可靠的工作机制**。

在 AI coding agent 场景中，这个问题尤其明显。你让模型“修复一个 bug”，它可能会写出看似合理的代码，但真实工程中还会遇到许多额外问题：

- 它不知道项目真实目录结构，可能猜测不存在的文件路径。
- 它不知道已有服务类和工具函数，可能重复造轮子。
- 它不知道架构边界，可能让 Controller 直接访问 Repository。
- 它不知道哪些命令能跑，可能运行错误命令。
- 它不知道哪些模块不能动，可能误改认证、权限、支付等高风险代码。
- 它不知道如何验证，可能只给出代码但没有运行测试。
- 它不知道如何从失败中沉淀经验，下次继续犯同样错误。

Harness Engineering 要处理的不是“如何写一句更好的提示词”，而是：

```text
如何设计 Agent 的工作环境，使它更难犯错；
一旦犯错，如何通过测试、日志、权限、状态和规则把错误暴露出来；
暴露出来以后，如何把失败沉淀为下一次自动受益的机制。
```

### 它和 Prompt Engineering 的区别

Prompt Engineering 主要关注“怎么对模型说”。例如：

```text
你是一个资深 Java 后端工程师，请帮我修复这个 [Spring Boot](https://spring.io/projects/spring-boot) 接口错误。
```

这类指令对模型行为有影响，但它本质上仍然是语言层控制。[[提示词 Prompt]] 可以提醒模型“要小心”，却不能真正保证它小心。比如你在 prompt 里写“请不要修改认证模块”，如果工具层仍然允许它写入 `auth/` 目录，它仍然可能改错文件。

Harness Engineering 会把这条约束变成机制：

```text
auth/ 目录默认只读；
涉及 auth/ 的 patch 需要人工确认；
CI 中有架构测试阻止非法依赖；
最终报告必须列出所有改动文件。
```

也就是说，Prompt 是软约束，Harness 追求的是软约束与硬约束结合。

### 它和 Context Engineering 的区别

Context Engineering 关注“模型这次应该看到什么”。比如让模型读取：

```text
docs/ARCHITECTURE.md
docs/API_CONVENTIONS.md
src/main/java/.../MovieController.java
src/main/java/.../MovieService.java
测试失败日志
数据库 schema
```

Context Engineering 是 Harness Engineering 的重要组成部分，但不是全部。Harness 不仅管上下文，还管工具、执行、状态、权限、测试、日志、评估和人工审批。

可以这样理解三者关系：

```text
Prompt Engineering
  关注：怎么说

Context Engineering
  关注：给模型看什么

Harness Engineering
  关注：模型在什么系统中工作、能做什么、怎么验证、怎么纠错、怎么被审计
```

![Prompt chaining 工作流示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-prompt-chaining.png)

### 它和传统 Test Harness 的关系

传统软件工程中的 test harness 指测试夹具、测试驱动环境、模拟对象、测试 runner 等。它围绕被测对象提供输入、执行、观测和断言。

AI 语境中的 harness 借用了这个思想，但范围扩大了。它不只是测试，而是覆盖 Agent 的完整运行环境：

```text
Instruction
Context
Tools
Execution
State
Verification
Permissions
Observability
Evaluation
Human Review
Self-improvement
```

所以，AI Harness Engineering 可以看成“测试夹具思想在 Agent 系统中的扩展”：不仅要测试结果，还要控制 Agent 如何获取信息、如何行动、如何受限、如何修复自己。

## Agent Harness 的总体结构

一个典型的 Agent Harness 可以抽象成下面的流程：

```text
用户任务
  ↓
指令层：读取系统规则、项目规则、任务模板
  ↓
上下文层：检索相关文件、文档、日志、schema
  ↓
编排层：决定计划、步骤、循环和停止条件
  ↓
模型：推理、生成、选择工具
  ↓
工具层：读写文件、搜索代码、运行命令、调用 API
  ↓
执行层：在本地、容器或云端沙箱中执行动作
  ↓
验证层：运行测试、lint、类型检查、结构检查
  ↓
反馈层：把观察结果送回模型，必要时修复
  ↓
审计与人工层：记录行为、控制权限、触发人工 review
  ↓
沉淀层：把失败写入规则、脚本、测试或权限边界
```

这不是一个固定产品架构，而是一种工程分层。不同框架会用不同方式实现这些层：

- [[LangChain]] 更强调 model、tool、middleware、agent runtime 等抽象。
- [[LangGraph]] 更适合实现状态机式的可控流程编排。
- [[模型上下文协议 MCP]] 可以作为工具和资源的标准暴露方式，把外部能力接入 Harness。

扩展阅读：[Anthropic：Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)。
- Codex、Claude Code、Cursor 等 coding agent 会把 AGENTS.md、工具调用、shell 执行、文件编辑、测试反馈等组合成自己的 harness。

关键不是名字，而是：**模型之外必须有一套系统，把模型输出转化为可执行、可检查、可回滚的工程动作**。

![Routing 工作流示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-routing.png)

### 一个没有 Harness 的任务

假设你在一个 Spring Boot + Vue 的媒体系统里让 Agent 实现“按需生成 HLS 分片”：

```text
帮我给项目加一个按需 HLS 分片生成功能。
```

这句话信息太少。Agent 可能会：

- 新建一个已经存在的 `TranscodeService`。
- 绕过已有的 `MoviePlaybackService`。
- 直接把 FFmpeg 命令写死在 Controller。
- 全量预转码整个视频，而不是按时间窗口生成。
- 忽略 Windows 路径和 Docker 挂载差异。
- 没有验证生成的 playlist 是否能播放。
- 没有说明改了哪些文件，也没有跑测试。

这不是模型“不会写代码”这么简单，而是任务环境没有被设计好。

### 一个有 Harness 的任务

更好的做法是先构造环境：

```text
AGENTS.md
docs/ARCHITECTURE.md
docs/MODULES.md
docs/FFMPEG_PIPELINE.md
docs/TESTING.md
scripts/verify.bat
scripts/validate-hls-output.py
```

然后任务描述变成：

```text
目标：在现有 MoviePlaybackService 中实现按需 HLS 分片生成。

必须先读：
- docs/ARCHITECTURE.md
- docs/MODULES.md
- docs/FFMPEG_PIPELINE.md

约束：
- 不允许新建重复的 TranscodeService。
- Controller 不能直接拼接 FFmpeg 命令。
- SOURCE 变体应优先 video copy + audio transcode。
- 不允许预转码整部影片。
- 只允许修改 movie 模块和相关测试。

验证：
- 运行 scripts/verify.bat
- 运行 python scripts/validate-hls-output.py ./test-output/sample-hls

输出：
- 改动文件
- 设计摘要
- 测试结果
- 剩余风险
```

这就是 Harness Engineering 的工作方式。它把一个模糊请求转化为受控任务，把隐性经验转化为显式规则，把“请认真一点”转化为可执行检查。

![Parallelization 工作流示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-parallelization.png)

## 核心组件：把模型包进一个可靠工作系统

Harness 的核心组件不是孤立模块，而是相互配合的闭环。下面按工程作用拆开。

### Instruction Harness：指令与规则层

Instruction Harness 负责告诉 Agent：在这个项目中工作时，应该遵守什么规则。

常见载体包括：

```text
system prompt
developer instruction
AGENTS.md
CLAUDE.md
.cursor/rules
任务模板
Definition of Done
项目规范文档入口
```

它和普通 prompt 的区别在于：普通 prompt 往往是一次性的，而 Instruction Harness 是项目级、可复用、可迭代的工作规则。

一个简洁的 `AGENTS.md` 可以这样写：

```md
# Agent Working Rules

This is a Spring Boot + Vue media-center project.

Before editing code:
1. Read docs/ARCHITECTURE.md.
2. Read docs/MODULES.md.
3. For transcoding tasks, read docs/FFMPEG_PIPELINE.md.
4. Search existing classes before creating new services.

Allowed commands:
- scripts/verify.bat
- mvn test
- npm run lint
- python scripts/validate-hls-output.py <path>

Do not:
- Modify .env files.
- Access production databases.
- Change authentication code without explicit approval.
- Introduce new dependencies without justification.

Before finishing:
1. Run the required verification commands.
2. List changed files.
3. Summarize test results.
4. Report remaining risks.
```

好的 Instruction Harness 应该满足几个条件。

第一，短而明确。它不应该把整个项目知识都塞进去，而应该像目录入口一样指向其他文档。

第二，包含可执行约束。比如“新增接口必须补测试”“Controller 不能依赖 Repository”“完成前必须运行 `scripts/verify.bat`”。

第三，包含负面边界。比如“不要修改 `.env`”“不要访问生产数据库”“不要自动合并 PR”。

第四，能从失败中更新。Agent 如果总是运行错命令，就把正确命令写进规则；如果总是找错 API，就把 API 查找方法写进规则。

常见错误是把 `AGENTS.md` 写成超长百科。过长的规则会污染上下文窗口，也会稀释关键约束。更好的做法是：

```text
AGENTS.md：只放工作入口、强约束、文档路由
docs/：放具体架构、API、数据库、测试、部署说明
scripts/：放可执行验证逻辑
```

### Context Harness：上下文与知识层

Context Harness 负责决定 Agent 看到什么。

模型如果看不到真实代码，就会猜。看到太多无关信息，又会被噪声干扰。因此上下文层的目标不是“越多越好”，而是“任务相关、权威、可检索、可压缩”。

上下文来源通常包括：

```text
项目文档
代码文件
测试文件
错误日志
API schema
数据库 schema
配置文件
历史设计决策
issue / PR / commit 摘要
运行时观测结果
RAG 检索结果
MCP resources
```

一个较好的项目上下文结构可以是：

```text
docs/
  ARCHITECTURE.md
  MODULES.md
  API_CONVENTIONS.md
  DATABASE_SCHEMA.md
  ERROR_HANDLING.md
  TESTING.md
  FFMPEG_PIPELINE.md
  DECISIONS/
    2026-04-30-window-based-hls.md
```

在具体任务中，Agent 不必一次读取所有内容。它应该根据任务类型选择上下文。例如：

```text
接口 bug：
- Controller
- Service
- DTO
- API 约定
- 相关测试
- 错误日志

数据库迁移：
- Entity
- Repository
- migration 文件
- DATABASE_SCHEMA.md
- 测试数据库验证脚本

HLS 转码：
- FFMPEG_PIPELINE.md
- TranscodeService
- MoviePlaybackService
- HLS 输出验证脚本
```

Context Harness 的关键机制包括：

1. **检索**：通过代码搜索、文件索引、[[检索增强生成 RAG]]、MCP resource 找到相关信息。
2. **裁剪**：只把相关片段送给模型，而不是整仓库塞进去。
3. **压缩**：长日志只保留错误摘要、堆栈关键行和失败测试名。
4. **权威性标注**：告诉模型哪些文档是最新规范，哪些只是历史记录。
5. **引用真实对象**：要求 Agent 基于真实文件、真实类名、真实函数名工作。

一个反例是把几千行测试日志直接塞给模型。更好的方式是保存完整日志到文件，只给模型摘要：

```text
Test failed:
- Class: HlsManifestValidatorTest
- Method: shouldRejectMissingInitSegment
- Error: expected false but was true
- Relevant file: src/test/java/.../HlsManifestValidatorTest.java
- Full log: .agent/logs/test-2026-04-30.log
```

### Tool Harness：工具层

Tool Harness 决定 Agent 能做什么。

没有工具时，模型只能说。拥有工具后，模型可以读文件、写文件、运行测试、查询数据库、调用 API、操作浏览器、调用 MCP server。工具层把语言模型和真实世界连接起来，因此它必须受控。

常见工具包括：

```text
read_file
write_file / apply_patch
search_code
list_files
run_shell
run_tests
git_diff
query_database_schema
call_internal_api
browser_screenshot
read_mcp_resource
call_mcp_tool
```

工具设计最重要的不是数量，而是边界。一个危险工具是：

```text
run(command: string)
```

这给了模型任意 shell 执行能力。更安全的设计是把高频动作语义化：

```text
run_maven_tests(module: string)
run_frontend_lint(package: string)
search_code(query: string, file_glob?: string)
apply_patch(patch: string)
read_file(path: string, start_line?: number, end_line?: number)
validate_hls_output(path: string)
```

工具要具备几个属性：

- **参数结构清晰**：最好有 schema，不要靠自然语言拼接。
- **权限边界明确**：哪些路径可写，哪些命令可执行。
- **返回结构稳定**：成功、失败、错误位置、修复建议最好格式化。
- **输出长度受控**：大日志落盘，只返回摘要。
- **错误可修复**：错误信息应该能指导 Agent 下一步。

例如，一个好的工具错误返回可以是：

```text
ERROR: Architecture rule violated.

File:
src/main/java/com/example/movie/MovieController.java

Problem:
Controller layer imported MovieRepository directly.

Rule:
Controller -> Service -> Repository

Fix:
Move database access into MovieService.

Reference:
docs/ARCHITECTURE.md#layering
```

这比单纯返回 `Test failed` 有用得多，因为 Agent 可以根据错误继续修复。

[MCP](https://modelcontextprotocol.io/docs/learn/architecture) 在这一层的定位是：它可以把外部工具、资源、提示模板以标准协议暴露给 Agent。例如数据库 schema 查询、内部文档读取、项目知识库检索、部署平台操作，都可以通过 MCP server 接入。但 MCP 不是 Harness 的全部，它只是 Tool/Resource 层的一种标准化接入方式。

### Execution Harness：执行环境与沙箱层

Execution Harness 决定 Agent 在哪里执行动作，以及执行动作时能访问什么。

常见执行环境包括：

```text
本地工作区
Docker 容器
云端 sandbox
CI runner
临时 workspace
只读代码副本
带快照的容器环境
```

这一层很关键。因为 Agent 一旦能运行命令、编辑文件、访问网络，就不再只是聊天助手，而是一个能够改变系统状态的执行体。

可以按风险划分执行权限：

```text
Level 0：只读分析，只允许读文件和搜索代码。
Level 1：工作区写入，只能修改当前任务相关文件。
Level 2：允许运行测试、lint、构建命令。
Level 3：允许访问测试数据库或 mock 服务。
Level 4：允许创建 PR，但不能合并。
Level 5：允许部署或改生产配置，必须人工审批。
```

对于 Windows + Docker 开发环境，一个相对安全的执行策略是：

```text
代码挂载到 /workspace
网络默认关闭或白名单
不挂载真实 .env
不挂载生产密钥
数据库使用测试实例
只允许固定脚本入口
输出统一写入 /workspace/out 或 .agent/logs
```

例如：

```bat
@echo off
chcp 65001 >nul

echo Running backend verification...
call mvn test
if errorlevel 1 exit /b 1

echo Running style checks...
call mvn checkstyle:check
if errorlevel 1 exit /b 1

echo Verification passed.
```

执行层的常见错误包括：

- 直接让 Agent 在主机上执行任意 shell。
- 把真实 `.env`、SSH key、生产数据库密码暴露给 Agent。
- 没有快照，失败后无法回滚。
- 允许 Agent 自动修改部署脚本、权限配置、生产配置。
- 工具层能执行命令，但没有审计日志。

Execution Harness 的核心原则是：**让 Agent 能做事，但只能在可控边界内做事**。

### Orchestration Harness：流程编排层

Orchestration Harness 决定 Agent loop 如何运转。

最基本的 Agent loop 是：

```text
User request
  ↓
Model reasoning
  ↓
Tool call
  ↓
Observation
  ↓
Model reasoning
  ↓
Final answer
```

这个结构能完成简单任务，但复杂工程任务需要更明确的流程。例如 coding agent 可以采用：

```text
理解任务
  ↓
读取规则
  ↓
检索上下文
  ↓
分析影响范围
  ↓
制定计划
  ↓
修改代码
  ↓
运行验证
  ↓
失败则诊断并修复
  ↓
通过则总结
```

流程编排层要回答：

```text
什么时候继续？
什么时候停止？
什么时候重试？
什么时候重新规划？
什么时候压缩上下文？
什么时候请求人工确认？
什么时候只报告不继续改？
```

例如可以设置：

```text
同一个测试失败超过 2 次：停止并报告。
自动修复最多 3 轮：超过后交给人工。
涉及数据库 migration：必须人工确认。
改动超过 10 个文件：要求重新确认范围。
涉及 auth/payment/security：只生成 patch，不自动应用。
```

这就是 LangGraph 这类状态机框架的价值所在。它能把 Agent 工作流表达成节点和边：

```text
analyze_task
  → retrieve_context
  → plan_changes
  → edit_code
  → run_tests
  → if tests_pass: summarize
  → else: diagnose_failure → edit_code
```

LangChain 的 Agent 抽象更偏“模型 + 工具 + agent loop”的快速组合；LangGraph 更偏“显式状态、显式边、显式控制流”。从 Harness Engineering 的角度看，LangGraph 可以作为 Orchestration Harness 的实现方式之一。

![Orchestrator-workers 工作流示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-orchestrator-workers.png)

### State / Memory Harness：状态与记忆层

State Harness 负责保存 Agent 的中间状态，让任务不会完全依赖聊天上下文。

这里的 memory 不能简单理解成“用户偏好记忆”。在工程 Agent 中，状态至少包括：

```text
任务目标
当前计划
已完成步骤
待办事项
阻塞点
已修改文件
命令运行结果
测试失败日志
设计决策
人工确认记录
```

一个实用做法是让 Agent 把状态写入文件系统：

```text
.agent/
  task.md
  plan.md
  progress.md
  decisions.md
  changed-files.txt
  logs/
    test-2026-04-30.log
```

例如：

```md
# .agent/progress.md

Task:
Implement window-based HLS segment generation.

Done:
- Read docs/ARCHITECTURE.md.
- Located existing TranscodeService.
- Found MoviePlaybackService as the correct integration point.
- Added HlsManifestValidator.

Next:
- Add unit tests.
- Run scripts/verify.bat.

Blocked:
- Need a small HLS fixture for validate-hls-output.py.
```

这种文件化状态有几个优点：

- 人能直接读。
- Agent 下一轮能继续读。
- 另一个 Agent 可以接手。
- 对话上下文丢失后仍能恢复。
- 任务失败时能审计过程。

不要把所有状态都塞进向量数据库。很多时候，普通文件就是最稳定的 Agent memory。向量库适合语义检索，状态文件适合保存任务进度和确定性记录。

![Agent loop 示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-agent-loop.png)

### Verification Harness：验证与反馈层

Verification Harness 是 Harness Engineering 的核心。没有验证，Agent 只是生成“看起来合理”的结果；有验证，Agent 才能进入“生成—执行—观察—修复”的闭环。

验证可以分为几类：

```text
功能验证：单元测试、集成测试、端到端测试
静态验证：类型检查、lint、格式化、编译
架构验证：模块边界、依赖方向、禁止非法 import
安全验证：依赖扫描、敏感信息扫描、权限检查
运行验证：smoke test、API 调用、数据库 migration dry-run
产物验证：HLS playlist 检查、文件格式检查、截图对比
人工验证：PR review、架构评审、风险确认
```

对 Agent 尤其重要的是结构性验证。因为 Agent 很可能写出“能跑但破坏架构”的代码。比如 Spring Boot 项目中，可以用 ArchUnit 检查分层：

```java
@AnalyzeClasses(packages = "com.example.mediacenter")
public class ArchitectureTest {

    @ArchTest
    static final ArchRule controllers_should_not_access_repositories =
            noClasses()
                    .that().resideInAPackage("..controller..")
                    .should().accessClassesThat()
                    .resideInAPackage("..repository..");
}
```

这比在 prompt 里写“请遵守三层架构”更可靠。因为一旦 Agent 违反规则，测试会失败，失败信息会回到下一轮修复。

对 HLS 这类媒体任务，也可以写专门的验证脚本：

```python
from pathlib import Path
import sys

def validate_hls_dir(path: str) -> int:
    root = Path(path)
    playlists = list(root.glob("*.m3u8"))

    if not playlists:
        print("ERROR: no .m3u8 playlist found")
        return 1

    for playlist in playlists:
        text = playlist.read_text(encoding="utf-8", errors="ignore")
        if "#EXTM3U" not in text:
            print(f"ERROR: invalid playlist header: {playlist}")
            return 1
        if "#EXTINF" not in text:
            print(f"ERROR: no media segments in playlist: {playlist}")
            return 1

    print("HLS validation passed")
    return 0

if __name__ == "__main__":
    sys.exit(validate_hls_dir(sys.argv[1]))
```

Verification Harness 的原则是：

```text
能用程序检查的，不要只写进 prompt。
能在 CI 拦住的，不要靠人工记忆。
错误信息要能指导 Agent 修复。
验证命令要固定、可重复、易调用。
```

![Evaluator-optimizer 工作流示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-evaluator-optimizer.png)

### Permission / Guardrail Harness：权限与边界层

Permission Harness 决定 Agent 不能做什么。

它需要明确：

```text
哪些路径可读？
哪些路径可写？
哪些命令可执行？
哪些工具需要审批？
哪些数据不能暴露？
哪些模块默认只读？
哪些操作必须人工确认？
```

一个基本权限策略可以是：

```text
允许：
- 读取项目源码
- 修改当前任务相关模块
- 运行测试脚本
- 查看 git diff
- 读取测试数据库 schema

禁止：
- 修改 .env
- 读取生产密钥
- 访问生产数据库
- 自动执行部署
- 修改认证/权限/支付模块
- git push --force
- 删除大范围文件
```

权限层不是为了限制 Agent 的能力，而是为了让它可以在更安全的边界内自动化。没有权限层，Agent 的每一步都需要人紧张盯着；有权限层后，低风险任务可以自动完成，高风险任务进入人工审批。

一个简单的规则是：

```text
低风险、高可验证任务：允许自动执行。
中风险、可回滚任务：允许生成 patch，人工 review。
高风险、不可逆任务：只允许分析和提出方案。
```

### Observability Harness：观测、日志与审计层

Observability Harness 负责回答：

```text
Agent 做了什么？
调用了哪些工具？
改了哪些文件？
运行了哪些命令？
测试是否通过？
失败在哪里？
是否越权？
成本是多少？
人工介入了几次？
```

对于 coding agent，最低限度的审计输出应该包括：

```text
Changed files
Commands executed
Tests run
Test result
Tool calls
Remaining risks
Manual review required
```

最终报告可以固定成：

```md
## Summary

Implemented window-based HLS segment generation.

## Changed files

- MoviePlaybackController.java
- TranscodeService.java
- HlsManifestValidator.java
- HlsManifestValidatorTest.java

## Verification

- scripts/verify.bat: passed
- python scripts/validate-hls-output.py ./test-output/sample-hls: passed

## Risks

- Large MKV files still need more ffprobe coverage.
- Hardware acceleration behavior differs between local Windows and Docker runtime.
```

观测层的价值不只是“方便看”。它还能反过来改进 Harness。比如你发现：

- Agent 经常误用某个工具，说明工具描述或参数设计有问题。
- Agent 经常忘记测试，说明完成标准和编排逻辑有问题。
- Agent 经常改错模块，说明上下文检索或权限边界有问题。
- Agent 经常在同一类 bug 上失败，说明需要增加专门的验证脚本或文档。

### Human-in-the-loop Harness：人工协作层

Human-in-the-loop Harness 决定哪些地方必须由人介入。

不是所有任务都应该自动完成。Agent 适合处理低风险、可验证、可回滚的工作；涉及业务判断、架构取舍、安全权限、生产部署时，应该设置人工节点。

典型人工节点包括：

```text
需求不清
架构边界变化
数据库 schema 修改
权限模型变化
安全策略变化
删除数据
生产部署
测试连续失败
改动范围超出预期
```

可以按任务类型划分：

```text
可自动完成：
- 修复格式化
- 补单元测试
- 小范围 bug fix
- 文档补充
- 明确的 lint 修复

需要 review：
- 新增接口
- 修改数据库字段
- 重构核心 service
- 引入新依赖
- 调整模块边界

只允许提出方案：
- 删除生产数据
- 修改部署策略
- 修改认证和权限模型
- 安全敏感配置变更
```

人工协作层的目标不是降低自动化，而是把人的注意力从机械操作中解放出来，集中到真正需要判断的位置。

### Evaluation Harness：评估层

Verification 关注“这次任务是否通过”。Evaluation 关注“这个 Harness 长期是否可靠”。

评估对象可以是：

```text
不同模型
不同工具设计
不同 AGENTS.md 版本
不同上下文检索策略
不同编排流程
不同权限策略
```

评估指标可以包括：

```text
任务成功率
一次通过率
平均修复轮数
测试通过率
人工修改比例
越权尝试次数
架构违规次数
token 成本
平均耗时
失败类型分布
```

例如：

```text
Harness v1:
- success rate: 61%
- average repair loops: 3.2
- architecture violations: 9
- manual intervention rate: 42%

Harness v2:
- success rate: 78%
- average repair loops: 1.6
- architecture violations: 2
- manual intervention rate: 24%
```

有了 Evaluation Harness，你就不再凭感觉说“这个 Agent 好像更稳”，而是能衡量：到底是模型变好了、工具变好了、上下文变好了，还是验证机制变好了。

### Self-improvement Harness：失败沉淀层

Self-improvement Harness 是 Harness Engineering 最有价值的部分。

它的原则是：

```text
不要只修复当前输出；
要修复导致错误反复出现的环境。
```

每次 Agent 犯错，都可以问：

```text
这个错误能否通过规则避免？
能否通过上下文避免？
能否通过工具 schema 避免？
能否通过权限避免？
能否通过测试发现？
能否通过脚本自动修复？
能否通过人工 gate 拦住？
```

例如：

```text
错误：
Agent 总是创建重复的 TranscodeService。

归因：
上下文没有让它先搜索已有服务；规则没有禁止重复创建。

Harness 更新：
- AGENTS.md 增加“创建类前必须 search_code”。
- docs/MODULES.md 写清已有服务职责。
- scripts/detect-duplicate-service.py 检查重复命名。
```

再如：

```text
错误：
Agent 总是忘记运行测试。

归因：
最终输出没有强制包含测试结果；流程没有自动执行验证。

Harness 更新：
- 任务模板增加 Verification 字段。
- Orchestration 在 final 前自动调用 scripts/verify.bat。
- 最终报告必须包含命令和结果。
```

再如：

```text
错误：
Agent 修改了认证模块。

归因：
权限边界缺失。

Harness 更新：
- auth/ 默认只读。
- 修改 auth/ 需要人工确认。
- 工具层拒绝直接写入 auth/**。
```

这就是 Harness 的复利：每一次失败都可以变成下一次的系统能力。

![Coding agent 工作流示意](http://public.file.lvshuhuai.cn/images\harness-anthropic-coding-agent.png)

## 工程落地：一个最小可用 Harness

不需要一开始搭很复杂的平台。对于个人项目或研究项目，一个最小可用 Harness 可以由文档、脚本、规则和验证组成。

### 推荐目录结构

```text
project/
  AGENTS.md
  docs/
    ARCHITECTURE.md
    MODULES.md
    API_CONVENTIONS.md
    TESTING.md
    KNOWN_AGENT_FAILURES.md
  scripts/
    verify.bat
    smoke-test.ps1
    validate-hls-output.py
  .agent/
    task.md
    plan.md
    progress.md
    logs/
```

其中：

- `AGENTS.md` 是 Agent 工作入口。
- `docs/` 是权威上下文。
- `scripts/` 是机械验证工具。
- `.agent/` 是任务状态和执行日志。
- `KNOWN_AGENT_FAILURES.md` 是失败沉淀表。

### AGENTS.md 不应写成百科

一个合理的 `AGENTS.md` 更像索引和强约束：

```md
# Agent Rules

Before coding:
1. Read docs/ARCHITECTURE.md.
2. Read docs/MODULES.md.
3. Search existing code before creating new classes.

For backend tasks:
- Run scripts/verify.bat before finishing.

For media/transcoding tasks:
- Read docs/FFMPEG_PIPELINE.md.
- Validate HLS output with scripts/validate-hls-output.py.

Do not:
- Modify .env files.
- Access production databases.
- Change auth module without explicit approval.
- Introduce new dependencies unless necessary.

Final response must include:
1. Changed files
2. Commands run
3. Test results
4. Remaining risks
```

### 任务模板要把模糊需求变成工程任务

一个任务模板可以这样写：

````md
# Task

Implement window-based on-demand HLS segment generation.

## Required context

- docs/ARCHITECTURE.md
- docs/MODULES.md
- docs/FFMPEG_PIPELINE.md
- existing TranscodeService
- existing MoviePlaybackService

## Constraints

- Do not create duplicate service classes.
- Do not put FFmpeg command construction in Controller.
- Do not pre-transcode the entire movie.
- SOURCE variant should prefer video copy + audio transcode.
- Only modify movie module and related tests.

## Verification

Run:

```bash
scripts/verify.bat
python scripts/validate-hls-output.py ./test-output/sample-hls
```

## Output

Return:

1. Changed files
2. Design summary
3. Verification logs
4. Remaining risks
````

这个模板的价值在于，它让 Agent 不必猜“完成”意味着什么。

### 验证脚本是比口头要求更强的约束

不要只告诉 Agent“请确保代码正确”。应该给它一个固定验证入口：

```bat
@echo off
chcp 65001 >nul

echo Running backend tests...
call mvn test
if errorlevel 1 exit /b 1

echo Running style checks...
call mvn checkstyle:check
if errorlevel 1 exit /b 1

echo Verification passed.
```

如果项目是前后端混合，可以扩展：

```bat
@echo off
chcp 65001 >nul

echo [1/3] Backend tests
call mvn test
if errorlevel 1 exit /b 1

echo [2/3] Frontend lint
cd frontend
call npm run lint
if errorlevel 1 exit /b 1
cd ..

echo [3/3] Smoke test
powershell -ExecutionPolicy Bypass -File scripts/smoke-test.ps1
if errorlevel 1 exit /b 1

echo All verification passed.
```

### 失败沉淀表要具体

`KNOWN_AGENT_FAILURES.md` 不要写空泛总结，要写“失败—归因—机制化修复”。

```md
# Known Agent Failures

## Duplicate service creation

Problem:
The agent created VideoTranscodeService although TranscodeService already existed.

Cause:
The agent did not search existing services before implementation.

Prevention:
Before creating a new service class, search:
- Transcode
- Playback
- HLS
- Segment

Harness update:
AGENTS.md now requires code search before creating service classes.
```

再比如：

```md
## Wrong command execution

Problem:
The agent repeatedly ran npm test at the repository root, but frontend commands must run under frontend/.

Prevention:
Use:
- backend: scripts/verify.bat
- frontend: cd frontend && npm run lint

Harness update:
Allowed commands were added to AGENTS.md.
```

这种文档相当于项目的“Agent 免疫系统”。Agent 犯过的错越多，Harness 越成熟。

## 常见误区与判断标准

### 误区一：把 Harness Engineering 等同于写更长的 Prompt

更长的 prompt 不等于更强的 harness。超长 prompt 往往会带来三个问题：

- 占用上下文窗口。
- 关键规则被淹没。
- 无法机械验证。

真正的 Harness 应该把约束分层：

```text
规则写进 AGENTS.md
知识写进 docs/
验证写进 scripts/
权限写进工具和沙箱
风险交给 human review
```

### 误区二：只增加工具，不控制工具

工具越多，Agent 的行动空间越大，也越容易误用。一个没有权限边界的 shell 工具很危险；一个返回几万行日志的测试工具会污染上下文；一个描述模糊的 API 工具会让模型选错。

工具层应该追求：

```text
语义化
受限
结构化
可审计
错误可修复
```

### 误区三：把 Memory 全部做成向量库

向量库适合语义检索，但不适合保存确定性进度。任务状态、测试结果、改动文件、设计决策更适合写入普通文件。

比较合理的分工是：

```text
向量库：检索历史文档、相似问题、知识片段
状态文件：保存当前任务进度、计划、日志、决策
数据库：保存结构化任务记录、评估指标、审计数据
```

### 误区四：只看模型能力，不看环境能力

很多 Agent 失败并不是模型不会，而是环境不给它正确反馈。比如：

- 没有测试，它不知道代码是否正确。
- 没有代码搜索，它只能猜已有 API。
- 没有权限边界，它可能改错模块。
- 没有日志摘要，它被长日志淹没。
- 没有任务状态，它无法持续推进长任务。

因此评估 Agent 时，不能只问“用的是哪个模型”，还要问“它的 Harness 设计如何”。

### 一个成熟 Harness 的判断标准

可以用下面的问题检查：

1. Agent 是否知道当前项目的工作规则？
2. Agent 是否能获取任务相关上下文，而不是凭空猜？
3. Agent 的工具是否语义清晰、权限受控？
4. Agent 是否在隔离环境中执行高风险动作？
5. Agent 是否有固定验证入口？
6. 测试失败后，错误信息是否能指导修复？
7. 长任务是否有状态文件或 checkpoint？
8. 改动是否有日志、diff、命令记录？
9. 高风险操作是否需要人工确认？
10. Agent 犯过的错是否会反向更新规则、文档、测试或权限？

如果大部分答案是否定的，那系统还只是“模型加工具”，不是真正成熟的 Harness。

## 和相关概念的边界

Harness Engineering 会接触很多 Agent 生态术语，但它本身不是某个框架。

### 和 MCP 的关系

MCP 可以被看成 Harness 的 Tool/Resource 接入协议。它让外部系统以统一方式暴露：

```text
Tools
Resources
Prompts
```

例如：

- 数据库 schema 查询工具。
- 内部文档 resource。
- 项目任务模板 prompt。
- 部署平台操作工具。

但 MCP 不负责完整 Agent 可靠性。它不天然解决执行沙箱、测试反馈、状态机、权限策略、评估指标和人工审批。它是 Harness 的一部分，不是 Harness 的全部。

### 和 LangChain 的关系

[LangChain](https://docs.langchain.com/) 提供构建 Agent 的抽象，例如模型调用、工具绑定、结构化输出、middleware、agent loop 等。从 Harness Engineering 的角度看，LangChain 可以帮助实现：

```text
Tool Harness
部分 Orchestration Harness
部分 Context Harness
部分 Observability / Middleware
```

但项目规则、验证脚本、权限边界、CI、沙箱和失败沉淀仍然需要工程设计。

### 和 LangGraph 的关系

[LangGraph](https://langchain-ai.github.io/langgraph/) 更适合显式控制流程。它可以把 Agent 工作流做成状态机：

```text
retrieve_context → plan → act → verify → repair → summarize
```

因此它更像 Orchestration Harness 的实现工具。对于需要多步骤、可恢复、可中断、可人工介入的 Agent，LangGraph 比简单 agent loop 更容易控制。

### 和 RAG 的关系

RAG 是 Context Harness 的常见实现方式之一。它解决“模型如何检索外部知识”的问题。但 RAG 不能替代 Harness，因为 RAG 不负责执行、权限、测试、日志、状态和人工审批。

### 和 CI/CD 的关系

[CI/CD](https://docs.github.com/actions) 可以成为 Verification 和 Governance Harness 的一部分。CI 能机械化执行：

```text
编译
测试
lint
安全扫描
架构检查
构建产物检查
```

对于 Agent-generated code，CI 更重要，因为它是防止“看起来合理但破坏工程质量”的最后一道机器边界。
