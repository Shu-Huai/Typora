# Agent运行与工具

## 文档范围

本文说明 Spring Boot 如何驱动 Agent、工具和审计，不展开 PDF 文件处理或 FastAPI 内部实现。

- 源码范围：`backend/src/main/java/shuhuai/cardiacagent/client`、`service`、`tool`、`aspect`
- 描述状态：[已实现]；真实诊断能力的限制见 [[模型服务/网关与模型接口]]。
- 相关文档：[[接口/REST与SSE契约]]、[[后端/知识库与切片资源]]、[[数据库/持久化数据]]。

## Controller 与工具注册

`SpringAiControllerLlmClient` 从 `prompts/cardiac-agent-system.md` 读取系统提示词，向 Spring AI 注册下列工具对象。每次运行使用 `InvocationBoundToolCallback` 将 `AgentInvocationContext` 绑定到当前调用线程，避免不同会话互相污染。

| 工具对象 | 关键方法 | 作用 | 硬边界 |
| --- | --- | --- | --- |
| `ConversationStateTools` | `updateCaseContext`、`declareTextOnly`、`askUser` | 写入明确给出的病例事实、记录仅文本授权、暂停追问 | 不允许模型编造字段 |
| `SlideTools` | 校验、登记、枚举、读取元数据、按器官分组 | 操作会话内 SVS 引用 | 只接受唯一共享目录下相对路径 |
| `DiagnosisTools` | `textDiagnosis`、`multimodalDiagnosis` | 根据策略调用模型服务 | 输入适用性由策略判断 |
| `MedicalRagTool` | `medicalRagSearch` | 检索已启用 PDF | 只返回 Qdrant 已索引内容 |
| `MedicalInternetSearchTool` | `medicalInternetSearch` | 搜索公开心脏病理证据 | 领域守卫在 HTTP 请求前执行 |

[已实现] Java 不预设“先登记再切片再诊断”的工具路线；Controller 是否调用、调用何种工具和何时停止由模型在每轮观察后决定。

## 工具治理与公开轨迹

`ToolExecutionAspect` 环绕所有 `@Tool` 方法，负责以下与 LLM 无关的行为：

1. 调用 `AgentInvocationContext.nextStep`，超过上限立即终止本次工具调用。
2. 创建 `tool_execution`，先发送 `TOOL_START`，结束后更新耗时、状态、公开摘要和错误码。
3. 将成功的文本模型、多模态模型、RAG、SVS 与互联网结果写入 `agent_evidence`；被领域守卫拒绝的互联网请求不作为证据保存。
4. 将 `TOOL_RESULT` 推送给 SSE。前端只显示公开摘要和结果摘要，不显示原始私有推理。

| 工具异常 | Controller 可获得的语义 | 用户界面 | 后续动作 |
| --- | --- | --- | --- |
| 参数、路径或状态不合法 | `BaseException` 的业务码和中文消息 | 失败工具卡片 | 追问、换工具或说明限制 |
| 外部模型/检索故障 | 工具失败或结构化不可用结果 | 失败/完成摘要 | 可重试或不使用该来源 |
| Agent 总时限超时 | Run 标记 `FAILED` | 错误事件后 `DONE` | 用户重新发送消息 |

## 诊断策略与互联网检索

`DiagnosisStrategySelector` 与 `DiagnosisModelStrategy` 用策略模式选择文本或多模态诊断，而不是根据前端表单决定。文本诊断要求会话已明确为 `TEXT_ONLY`；多模态诊断读取已验证的 SVS 引用，SVS 仅提供视觉 softprompt，不生成组织病理文字。

`MedicalInternetSearchGuard` 的授权规则如下：

- 包含明确心脏病理词（如心脏、心肌、冠状动脉、瓣膜、心包）的查询，可没有病例状态直接检索；
- “最新指南”“研究进展”等泛化词，只有当前会话已有心脏病理事实时才会补全检索词后检索；
- 天气、EEG、财经、购物等排除词直接拒绝，不访问 SearXNG；
- SearXNG 的返回结果按配置上限保留，不按来源或观点进行二次筛选。

[已知边界] 领域词表是规则边界而不是医学本体；新的心脏病理术语应同时增加自动化测试，防止把非医疗主题意外放行。

