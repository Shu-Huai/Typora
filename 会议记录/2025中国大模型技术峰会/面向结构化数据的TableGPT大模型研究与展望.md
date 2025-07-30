# 面向结构化数据的 TableGPT 大模型研究与展望

## 现有解决方案——指令微调

### 指令微调

- 收集现有 Table 数据，构造指令，微调大模型
- 代表工作：TableLlama、TableLLM、TablebenchLLM

<img src="http://public.file.lvshuhuai.cn/images\overview1_yifei_1114-v13.png" alt="An overview of TableInstruct and TableLlama" style="zoom:50%;" />

### 问题

- 通用能力丢失
- 数据配比和训练模式不合理
- 表格理解能力差，基本依赖列明信息

## TableGPT

表格编码——特征对齐——指令微调

构造列名预测和向量对比学习任务编码表格

<img src="http://public.file.lvshuhuai.cn/images\image-20250729154014240.png" alt="image-20250729154014240" style="zoom:50%;" />

## TableGPT 2

- 表格模态集成——指令微调——Agent 系统架构
- Encoder-Decoder 架构

<img src="http://public.file.lvshuhuai.cn/images\image-20250729154359971.png" alt="image-20250729154359971" style="zoom:50%;" />

### Agent 系统架构

<img src="http://public.file.lvshuhuai.cn/images\image-20250729154807141.png" alt="image-20250729154807141" style="zoom:50%;" />

- 系统 Prompt——转换异形数据表、模糊问题
- CodeSandbox——Python、SQL 代码生成，调用工具精准求解
- VLM 解析图表——解决图表理解问题
- RAG 体系——解决领域知识注入问题