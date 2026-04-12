# vLLM

## 什么是 vLLM

![vLLM](http://public.file.lvshuhuai.cn/images\vllm-logo-text-light.png)

vLLM 不是模型，也不是“vision LLM”。它是一个**面向[[大语言模型 LLM]] 推理与服务的高吞吐、内存高效的推理引擎**。

你可以把它放在这条链路里理解：

**模型权重（Qwen / Llama / DeepSeek） → vLLM → API 服务 / 批量推理 / 在线推理**

也就是说：

- **LLM/MLLM** 解决“模型会不会”
- **vLLM** 解决“模型怎么高效跑起来”

## 为什么需要 vLLM

如果只用最朴素的推理方式，大模型服务很容易遇到几个问题：

- 显存占用大
- 并发低
- 长[[提示词 Prompt]] 拖慢整体吞吐
- 批处理利用率差

vLLM 的核心价值，就是围绕这些问题做系统级优化。你不要把 vLLM 理解成“另一个 [[Transformer]]”，更准确地说，它是一个**为推理场景重做调度、KV cache 管理、批处理和服务接口的系统**。

## vLLM 最核心的三件事

### PagedAttention

vLLM 最著名的设计是 **PagedAttention**。它的目标是更高效地管理 attention 的 key/value memory，也就是推理阶段最关键的 **KV cache**。

你可以先这样理解：

普通实现里，KV cache 往往像一整块连续大内存，序列长短不一、请求来来去去时，容易浪费显存、产生碎片。 

vLLM 的思路更像“分页管理”，把 KV cache 切成块来管理，这样更适合在线服务这种动态请求场景。

### Continuous Batching

这也是 vLLM 的标志性能力。它的思想是：

**请求是流式进来的，调度器持续把可运行的 token 拼进去，让 GPU 尽量一直忙着。**

一句话理解：

- 传统批处理：按“请求”为单位排队
- continuous batching：更接近按“token 计算机会”来调度

### OpenAI-compatible Server

vLLM 不只会离线推理。它还能启动一个兼容 OpenAI 风格的服务接口，供上层应用直接调用。

这意味着它非常适合做一层“私有模型服务网关”：

- 上层应用按 OpenAI 风格调接口
- 下层真正跑的是你自己的模型

## vLLM 在系统里处在哪一层

一套大模型应用大致可以拆成四层：

1. **模型层**：Qwen、Llama、DeepSeek
2. **推理引擎层**：vLLM
3. **服务接口层**：HTTP API、流式输出、鉴权
4. **应用层**：Agent、RAG、业务系统

所以 vLLM 不负责训练模型，不负责写 Prompt，不负责业务逻辑。它主要负责：

- 加载模型
- 管理显存和 KV cache
- 调度请求
- 提供高吞吐推理
- 暴露服务接口

## vLLM 的基本工作流

### 离线推理

也就是在 Python 里直接调用接口，对一批 prompt 做生成。这适合：

- 批量数据生成
- 评测
- 离线实验
- 数据蒸馏或合成

### 在线服务

也就是启动服务，把模型变成 HTTP API。这适合：

- 给前端或 Agent 提供推理接口
- 替代某些闭源 API 的私有部署层
- 做企业内部统一模型网关

## 几个关键机制

### Prefill 和 Decode

理解 vLLM 必须知道这两个阶段：

- **Prefill**：先把整段输入 prompt 跑一遍，建立初始 KV cache
- **Decode**：然后一个 token 一个 token 地继续生成

这两个阶段的计算性质不同。prefill 更像“先灌入整段输入”，decode 更像“逐步生成”。vLLM 的很多优化，例如 **chunked prefill**，就是围绕这两个阶段的差异做的。

### Prefix Caching

如果很多请求前缀相同，比如同一个 system prompt、同一段长模板、同一个文档前半段，那么没必要每次都重新算一遍。

prefix caching 的直觉就是：

**相同前缀，尽量复用已算过的 KV cache。**

### Chunked Prefill

长 prompt 往往会拖慢系统。chunked prefill 会把长 prefill 拆成更小的块，和其他 decode 请求一起调度，从而更好地兼顾吞吐和延迟。

### Speculative Decoding

这是一类“先猜再验证”的加速思路。它的核心不是改变模型能力，而是争取在保证结果基本一致的前提下，提高生成速度。

## vLLM 支持什么

从工程能力看，vLLM 通常支持：

- OpenAI-compatible API server
- Streaming outputs
- 多种并行方式
- LoRA adapters
- 多模态输入
- Prefix caching
- 量化和推理优化

所以它不只是“让模型跑起来”，而是“让模型在真实服务场景里更好地跑起来”。

## 并行与扩展

vLLM 常见支持的并行方式包括：

- **Tensor Parallelism**
- **Pipeline Parallelism**
- **Data Parallelism**
- **Expert Parallelism**

你现阶段不必一开始就把它们全学透，只要先知道：

- **TP**：把单层权重切到多卡
- **PP**：把不同层分到不同卡
- **DP**：多份副本分摊请求
- **EP**：更偏向 MoE 模型场景

## LoRA 和动态适配

vLLM 支持 LoRA adapters，这意味着你可以在不改动基础模型权重的情况下，挂载一些轻量适配器，用于不同任务或不同领域。

从工程角度看，这很有用，因为它让“一个基础模型 + 多个轻量适配器”的服务方式变得可行。
