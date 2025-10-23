下面这些数据集都满足“**多张图片 + 一条文本**”的图文对齐（或可轻松整理成这种形式），按场景分类给你——每条都附上权威出处，方便获取与确认规模/任务设置：

## 明确“多图一文”的推理/描述任务

- **NLVR2**：每个样本由**两张图片 + 一句自然语言**陈述组成，任务是判断陈述对这对图片是否为真（True/False）。非常标准的“多图一文”对齐。可在官方与 Hugging Face 获取。[LIL Lab+2Hugging Face+2](https://lil.nlp.cornell.edu/nlvr/?utm_source=chatgpt.com)
- **Spot-the-Diff**：每个样本是**两张相近图片 + 一段文本**，文本要**描述两图差异**（差异字幕/差异描述）。[ACL Anthology+1](https://aclanthology.org/D18-1436.pdf?utm_source=chatgpt.com)

## “多图成组 + 一段叙述/描述”的故事与商品场景

- **VIST（Visual Storytelling）**：数据单元是**5 张同一相册的照片 + 一段人写的故事**（通常每图一句，整体可视为一段文本绑定多图）。[toolbox.google.com+2service.tib.eu+2](https://toolbox.google.com/datasetsearch/search?query=Visual+Storytelling+-site%3Akaggle.com&utm_source=chatgpt.com)
- **Recipe1M+**：每个“食谱文本”（配料+步骤）对应**多张菜品图片**，平均**约 13 图/食谱**，天然是“一文多图”。[arXiv+1](https://arxiv.org/abs/1810.06553?utm_source=chatgpt.com)
- **Fashion-Gen**：每个商品条目有**多视角高分辨率图片**和**专业文字描述**（多图对单条商品描述）。[arXiv+1](https://arxiv.org/abs/1806.08317?utm_source=chatgpt.com)

## 新闻场景（文章文本 + 多图/至少一图）

- **VisualNews**：超过**百万**新闻图像，配有**完整新闻文章、标题/说明**等元信息；常用于新闻图文对齐与生成，可整理为“**文章（文本）⇄ 多图**”样式。[arXiv+2GitHub+2](https://arxiv.org/abs/2010.03743?utm_source=chatgpt.com)
- **BreakingNews**：约**10 万**新闻文章，均带**至少一张图**、标题、地理信息等，可用于图文配对、检索与地理定位等任务（不少文章含多图）。[arXiv+2iri.upc.edu+2](https://arxiv.org/pdf/1603.07141?utm_source=chatgpt.com)

## 多模态检索/问答（单条文本查询 + 多图证据）

> 这类任务里，**一条文本**（问题/查询）需要在候选中找**一张或多张图片**作为证据，天然是“**一文对多图**”的监督或评测形式。

- **WebQA**：开放域**多跳**多模态问答；每个问题配有**图片与文本的正/负检索候选**，要求找出**1–2 张相关图片**与文本共同作证并作答。[arXiv+2CVF开放获取+2](https://arxiv.org/abs/2109.00590?utm_source=chatgpt.com)
- **TVQA / TVQA+**（视频 QA）：每个问题对应**视频片段（可视作多帧图像集）+ 字幕文本**；TVQA+ 还提供帧级标注。虽是视频，但数据组织就是“**一问（文本）⇄ 多帧图像**”。[ACL Anthology+1](https://aclanthology.org/D18-1167.pdf?utm_source=chatgpt.com)

------

### 选型建议

- 想要**最标准的“多图一文”自然语言理解**：从 **NLVR2** 开始。
- 需要**差异描述**（两图一段话）：选 **Spot-the-Diff**。
- 做**叙事/故事生成或理解**：选 **VIST**。
- 做**商品/菜谱**类“多视角或多实例对单文本”检索/匹配：选 **Fashion-Gen**、**Recipe1M+**。
- 做**新闻配图/检索/生成**：选 **VisualNews**、**BreakingNews**。
- 做**检索+推理**、从候选中挑**多图证据**：选 **WebQA**；视频场景可看 **TVQA/TVQA+**。

需要的话我可以按你要的格式（如：`image_paths` 列表 + `text` 字段 + 标签/分割）给你写个**统一的数据清洗脚本**，把以上任一数据集转换成“多图一文”的通用 JSON/CSV 结构。