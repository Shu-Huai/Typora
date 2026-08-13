# AI 自动记账

本文说明 AI 记账的完整链路：限流、提示词、调用、解析、匹配、日志。

本文不讨论 AI 服务本身的配置，见 [[开发文档/配置与部署|配置与部署]]。异常分类见 [[总体实现/异常与失败处理|异常与失败处理]]。

源码范围：`service/impl/AiBillServiceImpl.java`、`service/excep/ai/`、`entity/AiBillParseLog.java`。

## 调用链与提示词

### 调用链

```
POST /api/bill/ai/parse (bookId, type, text)
  → 限流：Redis INCR ai:bill:parse:limit:{userId}:{分钟}，超 5 次抛 AiRateLimitException
  → 读用户资产列表 + 账本分类列表
  → 构造系统提示词（当前北京时间、目标账单类型、资产 JSON、分类 JSON）
  → Spring AI ChatClient 调用（base-url opencode.ai 代理，模型 deepseek-v4-flash）
  → extractJson 截取首个 { 到最后一个 } 之间的 JSON
  → fastjson 解析为 LlmParseResult（status/reason/amount/billTime/remark/assetName/...）
  → 资产与分类匹配（精确优先、模糊包含兜底、多候选抛歧义）
  → 返回 AiParseBillResponse 草稿
  → finally 写 ai_bill_parse_log（无论成败）
```

![](http://public.file.lvshuhuai.cn/images\where-money-ai-parse-flow.svg)

### 提示词设计

系统提示词固定包含：

- 当前北京时间（模型不知道"现在"）
- 目标账单类型（收入/支出/转账，退款不走 AI）
- 该用户的资产列表（资产名 + 类型）
- 当前账本的分类列表（分类名 + 类型）

要求模型只输出 JSON，字段按类型不同：支出要 amount/billTime/remark/assetName/billCategoryName；转账要 inAssetName/outAssetName/transferFee；收入类似支出。`extraBody` 强制关闭 thinking 模式（enable_thinking=false），temperature 0.7。

提示词把"资产和分类必须从给定列表里选"作为硬约束，让模型做选择题而不是自由发挥。

## 匹配与歧义

模型返回的名字和库里的名字可能不完全一致：

1. 精确匹配：完全相等直接命中
2. 模糊匹配：库里某个名字包含模型返回的名字（或反之）
3. 多候选：抛 AiAmbiguousMatchException，前端提示用户手选
4. 零候选：抛 AiAssetNotFoundException / AiCategoryNotFoundException

模糊匹配的坑：资产名"中行卡"和"建行卡"都包含"行卡"，模型返回"行卡"会歧义。这是精确匹配优先级在前的原因。

## 状态、日志与并发

### 状态与错误分类

AiStatus 枚举：SUCCESS、IRRELEVANT（无关）、MISSING_INFO（信息不全）、ASSET_NOT_FOUND、CATEGORY_NOT_FOUND。模型自己会判断前两类，后两类由匹配阶段判定。

异常子类（9 个）对应不同的 HTTP code：

- 422：无关、信息不全、资产/分类找不到、歧义（这些是"结果明确但不可用"）
- 429：限流
- 500：调用失败、超时、响应格式错

区分 422 和 500 的意义：422 是业务上可预期的不成功，用户知道换种说法再试；500 是系统问题，用户重试无益。

### 调用日志

每次调用（成功和失败，限流除外）写一条 `ai_bill_parse_log`：

- 输入：user_id、book_id、type、input_text
- 调用：model_name、latency_ms
- 结果：status、error_code、error_message、llm_raw_json

用途：排查提示词问题（看原始 JSON）、评估模型质量（看错误分布）、成本核对（看调用量）。表只增不删。

### 并发与超时

- LLM 调用在虚拟线程执行器上跑（Executors.newVirtualThreadPerTaskExecutor），不占 Tomcat 工作线程
- 超时由 Spring AI 的超时参数控制（配置值 12000000000 毫秒是笔误，代码默认 12000）
- 限流计数 120 秒 TTL，分钟粒度 key（yyyyMMddHHmm），边界时刻实际可超 5 次

## 已知边界

- AI 返回的 billTime 是模型推断的时间，用户必须在提交前核对（前端已把草稿做成可编辑）
- 金额可能被模型算错（如"午饭 15 打车 20"合并成 35），没有二次校验
- 转账类型无分类，模型只需给两个资产名
- 调用日志没有清理机制，长期膨胀
- 前端拿到 422/500 都显示同一句失败提示，用户看不到后端给出的具体原因（提示词输出里有 reason 字段也没用到）
