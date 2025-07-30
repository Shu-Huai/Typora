# Helsinki-NLP/opus-mt-zh-en 推理情况

## 一、已完成

1. **开源模型权重**的下载和**推理代码**的编写
2. 将来源于 `司法鉴定研究院` 的 180 条数据作为测试集进行推理
3. 将结果合并到原表格中左右对照

## 二、效果

<img src="http://public.file.lvshuhuai.cn/images\image-20250706195940700.png" alt="image-20250706195940700" style="zoom:50%;" />

## 三、目前发现的问题

### 1. 通用语言层面

1. 会有奇怪的符号，例如：

    将 `心脏各瓣膜光滑` 翻译为 `♪ The heart of the petals is smooth ♪`

2. 短语处理不佳，例如：

    对于表头 `心内、外膜情况`，翻译为 `He's got a heart condition.`

### 2. 专业名词层面

具体需待专业人员认定，但发现以下问题：

1. 将 `二尖瓣` 翻译为 `2 spires`，将 `三尖瓣` 翻译为 `Trident`。

    查询百度，应分别为 `mitral valve` 和 `tricuspid valve`。

    豆包对这两个单词翻译正确。

2. 断句有问题

    对于 `心肌表、切面呈暗红色、淤血状`，将 `表` 理解为了 `watch`，这句话翻译结果为 `Heart watch, cut, dark red, haemorrhage.`

    豆包翻译为 `The surface and cut surface of the myocardium are dark red and congested.`

## 四、可能的原因

1. 模型使用 MarianMT（2019），较旧
2. 训练数据主要是 OpenSubtitles、JW300 等公开语料，不适合正式/专业文本
3. 不支持上下文，每个句子独立翻译，缺乏上下文语义理解