# Index TTS

Index TTS 是哔哩哔哩团队开源的工业级零样本文本转语音 [[TTS Text-to-Speech]] 系统。
它采用 **GPT-风格的自回归架构**，在 XTTS、Tortoise 等方案的基础上做了工程化增强：支持**中文发音纠错（基于拼音）**、用**标点控制停顿**、并集成 BigVGAN2 提升音质，适合实际生产场景落地。官方给出了模型卡与在线演示，可上传参考音色做零样本克隆与合成。

## Index TTS 2
**Index TTS 2（IndexTTS2）** 是其新一代版本，核心在于：

1. **精确时长控制**（可显式对齐目标时长，同时保留自回归的自然韵律）
2. **音色-情感解耦**（独立控制 timbre 与 emotion，支持文本/向量/参考音频多种情感输入）；
3. 通过 **GPT 潜表示 + 三阶段训练** 提升强情感场景的清晰度与稳定性。官方论文与展示页提供了大量音频对比与评测。

<img src="http://public.file.lvshuhuai.cn/images\IndexTTS2_banner.png" alt="IndexTTS2" style="zoom: 33%;" />

### 它是什么

IndexTTS2 是一套**自回归、零样本（zero-shot）语音克隆与情感可控的 TTS 模型**。它最大的亮点是提出了**可精确控制时长**的通用方法：既可以显式指定生成的 token 数来严格对齐时长（适合配音对口型/对时），也可以像传统自回归一样自由生成，同时尽量保留提示音频的韵律特征。模型还实现了**“音色—情感”解耦**，能分别由不同提示控制说话人音色与情感风格；为提升高情感语音的清晰度，它引入了 **GPT 潜表示**与**三阶段训练范式**，并用微调后的 Qwen3 做“文本软指令”来用自然语言控制情绪倾向。官方实验显示在 WER、说话人相似度、情感保真度上优于同类零样本 TTS。

### 总体框架

IndexTTS2 是级联的零样本自回归 TTS：

**T2S（Text→Semantic）自回归模块 → S2M（Semantic→Mel）非自回归模块 → BigVGANv2 声码器**。

- T2S 负责从文本、音色提示与（可选的）“目标语义 token 数”生成语义离散码
- S2M 用这些语义码与音色特征生成梅尔谱
- Vocoder 把梅尔谱还原为语音。

<img src="http://public.file.lvshuhuai.cn/images\image-20250928105234438.png" alt="image-20250928105234438" style="zoom:50%;" />

### 时长可控的关键机制

自回归生成很自然，但传统上很难严格控时。

IndexTTS2 在 **T2S 输入里显式注入“时长嵌入” $p$**，并做了一个**位置—时长同化**的小技巧，使得模型能**精确产出指定长度的语义token序列**：

- **输入序列形式**：$c,p,e⟨BT⟩,E_{text},e⟨BA⟩,E_{sem}$。其中 **$c$** 是说话人（音色）向量，**$p$** 是时长向量，**$E_{text}$** 为文本嵌入，**$E_{sem}$** 是由“语义编解码器”从真值语音里抽出的语义 token 嵌入，$e⟨BT⟩/e⟨BA⟩$ 是边界标记。
- **时长嵌入 $p$ 的构造**：先把**目标语义 token 长度 $T$** one-hot 成 **$h(T)$**，再查一个表 **$W_{num}$** 得到 **$p = W_{num}\cdot h(T)$**（相当于“长度索引→向量”）。
- **位置—时长同化 trick**：**把语义位置嵌入表 $W_{sem}$ 与 $W_{num}$ 约束为相等（$W_{sem} = W_{num}$）**。这样自回归解码在每个位置“看到”的位置嵌入，天然和“期望的总长度”对齐，模型就会**恰好解码到指定长度**停下，严格控时。
- **两种生成模式**：
    1. **定长模式**：指定 $T$，送入 $p$（上式）→ 严格控时；
    2. **自由模式**：把 **$p$ 置 0**，按自然时长生成。训练时会以 30% 概率把 $p=0$，以适配自由模式。

> 这套做法的要害是：把“目标长度”直接编码进自回归条件里，并通过 $W_{sem} = W_{num}$ 让“位置信息”承载“时长约束”，从而解决“AR 难控时”的老问题。论文实验显示在多种时长缩放下 T2S 令牌误差极低，WER 也优于或不逊于强基线。

### 情感——音色解耦（怎么做到“同一音色，多种情感”）

<img src="http://public.file.lvshuhuai.cn/images\image-20250928105131105.png" alt="image-20250928105131105" style="zoom:50%;" />

情感来自“风格提示”（style prompt），音色来自“音色提示”（timbre prompt）。T2S 里用**两个感知器（perceiver）**分别提取：**speaker-perceiver→c（音色）**、**emotion-perceiver→e（情感）**，并通过**GRL（梯度反转层）+ 说话人分类器**做对抗式正则：

- 训练时让 **$e$** 在说话人判别器面前“不可分”（梯度反转），逼迫 **$e$ 只携带情感/节奏而不含音色信息**；同时 **$c$** 固定为音色。推理时把 **$c+e$** 一起喂给 T2S，即可获得“某音色 + 指定情感”的组合。

### “文本→情感”软指令（不用参考音频，也能用文字控情感）

为降低使用门槛，IndexTTS2 还做了 **T2E（Text-to-Emotion）**：

- 先定义 7 类基础情感集合（Anger/Happiness/Fear/Disgust/Sadness/Surprise/Neutral）；
- 用 **DeepSeek-r1** 作为 teacher，把提示文本映射到 **7 维情感概率单纯形**，再**蒸馏**到小模型 **Qwen-3-1.7B**（便于部署）；
- 这个情感向量作为 **$e$** 接入 T2S，即可仅靠文字指令控制情感倾向。

### S2M 的“GPT 潜表示”增强（为什么情绪很强时还能听清）

<img src="http://public.file.lvshuhuai.cn/images\image-20250928105303104.png" alt="image-20250928105303104" style="zoom:50%;" />

S2M 不是自回归，而是**基于 Flow Matching 的条件生成**：从噪声到目标梅尔谱的 ODE 轨迹，条件包括音色参考的梅尔、说话人向量、以及来自 T2S 的语义 token 序列。

为减少“强情感时的连读/吐字糊”（slur），S2M 训练时会**以 50% 概率把 T2S 的 GPT 最后一层隐状态 $H_{GPT}$ 与语义 token 特征做向量相加融合**，形成更“语义+上下文”富集的条件信号；消融显示该 **GPT latent 融合**能显著降低高情感语音的 WER，同时主观指标不受损。

> 小结：T2S 侧把“文字→语义 token”学得很强，$H_{GPT}$ 携带清晰的上下文/语义边界；S2M 把它融合进来，能在大起伏的情感里仍保持清楚的吐字。

### 三阶段训练范式（怎么同时学会“控时 + 情感 + 稳定”）

#### 要点（均在 T2S 侧）：

- **Stage 1（打基础）**：全量数据上训练 $c, p, \cdots$ 输入；为兼容两种推理模式，30% 概率令 **$p=0$**。

- **Stage 2（学情感 + 解耦）**：把输入改为 $c+e, p, \cdots$，**冻结说话人感知器**，只训练情感感知器；引入 **GRL+说话人分类器**，并在**高质量情感子集（约 135h）**上优化；联合损失：
    $$
    L_{\text{AR}} = -\frac{1}{T+1}\sum_{t=0}^{T}\log q(y_t)\;-\;\alpha\log q(e),
    $$
    其中第一项是语义 token 的自回归对数似然，第二项通过对抗让 $e$ 脱敏于说话人。

- **Stage 3（稳健微调）**：冻结特征抽取器，在全量数据上微调以增强鲁棒。

### 推理流程（两种模式如何用）

#### 定长模式

1. 给目标时长
2. 折算出目标**语义token数 $T$**（或直接给 $T$）
3. 计算 **$p=W_{num}\cdot h(T)$**
4. T2S 自回归生成**恰好 $T$** 个语义 token
5. S2M+Vocoder 合成。

#### 自由模式

1. **p=0**，T2S 自然停在 \<EA\>（end）
2. 后续同上。

两种模式都可接**音色提示 $c$** 与**情感向量 $e$**（来自参考音频或 T2E 文本指令）。

### 如何使用

> - GitHub：[index-tts/index-tts: An Industrial-Level Controllable and Efficient Zero-Shot Text-To-Speech System](https://github.com/index-tts/index-tts)
> - 项目使用 git lfs 以及 uv，确保已安装
> - 在 Windows 上安装

#### 克隆

```powershell
git lfs install
git clone https://github.com/index-tts/index-tts.git
cd index-tts
git lfs pull
```

> 可能会遇到报错
>
> git clone https://github.com/index-tts/index-tts.git
>
> Cloning into 'index-tts'...
>
> remote: Enumerating objects: 1163, done.
>
> remote: Counting objects: 100% (60/60), done.
>
> remote: Compressing objects: 100% (36/36), done.
>
> remote: Total 1163 (delta 33), reused 24 (delta 24), pack-reused 1103 (from 2)
>
> Receiving objects: 100% (1163/1163), 33.54 MiB | 15.96 MiB/s, done.
>
> Resolving deltas: 100% (573/573), done.
>
> Updating files: 100% (250/250), done.
>
> Downloading examples/emo_hate.wav (145 KB)
>
> Error downloading object: examples/emo_hate.wav (89e6e7e): Smudge error: Error downloading examples/emo_hate.wav (89e6e7eee1a28303776e9cf43971e9505529bd0e669f5fcf47f4d1370f9187c4): batch response: This repository exceeded its LFS budget.The account responsible for the budget should increase it to restore access.
>
> Errors logged to 'D:\index-tts\.git\lfs\logs\20250926T164112.5600093.log'.
>
> Use `git lfs logs last` to view the log.
>
> error: external filter 'git-lfs filter-process' failed
>
> fatal: examples/emo_hate.wav: smudge filter lfs failed
>
> warning: Clone succeeded, but checkout failed.
>
> You can inspect what was checked out with 'git status' and retry with 'git restore --source=HEAD :/'
>
> 这是由于 GitHub 对 git lfs 的使用有限制，项目太火爆了下载的人太多了超限了。
>
> 忽略它并手动下载示例文件 [This repository exceeded its LFS budget. The account responsible for the budget should increase it to restore access. · Issue #407 · index-tts/index-tts](https://github.com/index-tts/index-tts/issues/407)

#### 环境

```powershell
uv sync
uv add gradio
```

#### 模型

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
uv run hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints
```

#### 可选修改

将所有的模型都下载到当前目录

```python
# semantic_code_ckpt = hf_hub_download("amphion/MaskGCT", filename="semantic_codec/model.safetensors")
semantic_code_ckpt = hf_hub_download(
    "amphion/MaskGCT",
    filename="semantic_codec/model.safetensors", 
    cache_dir="./checkpoints"
)
```

```python
campplus_ckpt_path = hf_hub_download(
    "funasr/campplus",
    filename="campplus_cn_common.bin",
    cache_dir="./checkpoints",  # 👈 下载/缓存到当前目录 ./checkpoints
)
```

```python
# self.bigvgan = bigvgan.BigVGAN.from_pretrained(bigvgan_name, use_cuda_kernel=self.use_cuda_kernel)
self.bigvgan = bigvgan.BigVGAN.from_pretrained(
    bigvgan_name,
    use_cuda_kernel=self.use_cuda_kernel,
    cache_dir="./checkpoints",         # 👈 下载到 ./checkpoints 缓存目录
)
```

```python
# self.extract_features = SeamlessM4TFeatureExtractor.from_pretrained("facebook/w2v-bert-2.0")
self.extract_features = SeamlessM4TFeatureExtractor.from_pretrained(
    "facebook/w2v-bert-2.0",
    cache_dir="./models",  # 👈 缓存到当前目录 ./models
)
```

```python
# semantic_model = Wav2Vec2BertModel.from_pretrained("facebook/w2v-bert-2.0")
semantic_model = Wav2Vec2BertModel.from_pretrained(
    "facebook/w2v-bert-2.0",
    cache_dir="./checkpoints",  # 👈 缓存到当前目录 ./checkpoints
)
```

```python
# self.extract_features = SeamlessM4TFeatureExtractor.from_pretrained("facebook/w2v-bert-2.0")
self.extract_features = SeamlessM4TFeatureExtractor.from_pretrained(
    "facebook/w2v-bert-2.0",
    cache_dir="./checkpoints",  # 👈 缓存到当前目录 ./checkpoints
)
```

#### 运行

```powershell
uv run webui.py
```

<img src="http://public.file.lvshuhuai.cn/images\image-20250928144541664.png" alt="image-20250928144541664" style="zoom:50%;" />
