# IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech

## 基本信息

- IndexTTS2：情感丰富且时长可控的自回归零样本文本转语音领域的突破
- GitHub：[index-tts/index-tts: An Industrial-Level Controllable and Efficient Zero-Shot Text-To-Speech System](https://github.com/index-tts/index-tts)
- Arxiv：[[2506.21619v2] IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech](https://arxiv.org/abs/2506.21619v2)
- 一种文本到语音生成的方法，能够控制音色和感情

## 摘要

现有的自回归大规模文本转语音（TTS）模型在语音自然度方面具有优势，但其逐令牌生成机制使其难以精确控制合成语音的时长。这在需要严格音视频同步的应用中，如视频配音，成为一个显著的局限性。本文介绍了 IndexTTS2，它提出了一种新颖、通用且适合自回归模型的语音时长控制方法。该方法支持两种生成模式：一种是明确指定生成的令牌数量以精确控制语音时长；另一种是在不指定令牌数量的情况下，以自回归方式自由生成语音，同时忠实地再现输入提示的韵律特征。此外，IndexTTS2 实现了情感表达与说话人身份的解耦，能够独立控制音色和情感。在零样本设置下，该模型能够准确重构目标音色（来自音色提示），同时完美再现指定的情感基调（来自风格提示）。为了提高高情感表达中的语音清晰度，我们融入了 GPT 潜在表征，并设计了一种新颖的三阶段训练范式来提升生成语音的稳定性。另外，为了降低情感控制的门槛，我们通过微调 Qwen3 设计了一种基于文本描述的软指令机制，有效引导生成具有期望情感倾向的语音。最后，在多个数据集上的实验结果表明，IndexTTS2 在词错误率、说话人相似度和情感保真度方面优于最先进的零样本 TTS 模型。音频样本可在以下网址获取：this https URL

## 主要方法

### 目标

在自回归（AR）范式下，同时实现**精确时长控制**（按语义 token 计数）与**强情感表达**，并做到**情感与音色解耦**。  

### 三大组件

- **T2S（Text→Semantic, AR）**：语义 token 自回归预测；通过“**时长嵌入=语义位置嵌入**”共享实现**精确控时**；在情感向量上接入 **GRL** 对抗去说话人信息，达成**情感/音色解耦**。
- **S2M（Semantic→Mel，NAR/Flow Matching）**：条件流匹配生成 Mel；**随机融合 GPT 隐状态（50%）**缓解强情感场景“吞字/糊字”。
- **T2E（Text→Emotion）**：把文本映射为 7 维情感分布，进而合成连续情感向量输入 T2S（“自然语言→目标情感”）。

<img src="http://public.file.lvshuhuai.cn/images\image-20250928125318352.png" alt="image-20250928125318352" style="zoom:50%;" />

### T2S：自回归 Text-to-Semantic（控时 + 解耦）

#### 输入序列与拼接
T2S 以“生成语义 token 序列”为目标。训练时使用 teacher forcing。典型输入拼接为：
- 说话人（音色）向量：$c$
- 时长嵌入：$p$
- 情感边界 token：$e_{\langle BT \rangle}, e_{\langle BA \rangle}$
- 文本嵌入序列：$E_{\text{text}}$
- 语义嵌入（来自语义编码器/codec 的 GT 语义 token 嵌入，训练时用）：$E_{\text{sem}}$

> 实践做法：将 $[c, p]$ 作为全局条件通道（broadcast 到每个时间步），其余按序列维拼接送入 Transformer。

#### 精确时长控制的关键约束
设目标语义长度为 $T$，最大上限为 $L_{\text{speech}}$。  
- One-hot 长度向量：$h(T)\in\mathbb{R}^{L_{\text{speech}}}$  
- 时长嵌入查表：$p = W_{\text{num}}\,h(T)$，其中 $W_{\text{num}}\in\mathbb{R}^{L_{\text{speech}}\times D}$  
- **核心共享约束**（对齐）：  
  $$
  W_{\text{sem}} = W_{\text{num}}
  $$
  其中 $W_{\text{sem}}$ 是“语义**位置**嵌入表”。共享使“位置感知”与“目标长度”锚定一致，自回归地“数步数”，从而**精确生成 $T$ 个语义 token**。

> 推理开关：  
> - **控时**：给定 $T$，用 $p=W_{\text{num}}h(T)$。  
> - **自由时长**：令 $p=\mathbf{0}$。为支持该模式，训练第 1 阶段以约 30% 概率将 $p$ 置零。

#### 情感-音色解耦（GRL）

<img src="http://public.file.lvshuhuai.cn/images\image-20250928125355143.png" alt="image-20250928125355143" style="zoom:50%;" />

- 情感向量：$e$（由 Emotion Conditioner 从 style prompt 提取）。  
- 输入改为在前端注入 $c$ 与 $e$：$[c+e,\ p,\ e_{\langle BT \rangle}, E_{\text{text}}, e_{\langle BA \rangle}, E_{\text{sem}}]$。  
- 在 $e$ 上挂接 **GRL + 说话人分类器**，使梯度反向传至情感支路，**去除说话人信息**，保留节律/情感；$c$ 保持音色（timbre）信息。

#### 三阶段训练与损失
- **Stage 1（全量预训练）**：

  输入 $[c,\ p,\ e_{\langle BT \rangle}, E_{\text{text}}, e_{\langle BA \rangle}, E_{\text{sem}}]$；以约 30% 概率置 $p=\mathbf{0}$，兼顾自由时长。

- **Stage 2（情感精炼/解耦）**： 
  
  输入 $[c+e,\ p,\ e_{\langle BT \rangle}, E_{\text{text}}, e_{\langle BA \rangle}, E_{\text{sem}}]$；**冻结 speaker conditioner**，只训 emotion conditioner，并加 **GRL + speaker-clf**。
  
  - 序列交叉熵（AR）：
    $$
    \mathcal L_{\text{AR}}=-\frac{1}{T+1}\sum_{t=0}^{T}\log q(y_t)
    $$
  - 对抗去说话人项（权重 $\alpha$）：
    $$
    \mathcal L_{\text{adv}}=-\alpha\cdot \log q(e)
    $$
  - 总损失：$\mathcal L=\mathcal L_{\text{AR}}+\mathcal L_{\text{adv}}$
  
- **Stage 3（全量微调/稳健性）**： 
  
  冻结两类 conditioner，在全量数据上微调提升泛化与稳定。

> 数据与扰动：同一说话人样本拆分为 prompt/target；对真实语音及 prompt 施加独立速率扰动 $r_1,r_2$，增强对速率变化的鲁棒性。

### S2M：Semantic-to-Mel（Flow Matching + GPT 隐状态增强）

<img src="http://public.file.lvshuhuai.cn/images\image-20250928125409534.png" alt="image-20250928125409534" style="zoom:50%;" />

#### 条件与结构
采用条件 Flow Matching（连续时间生成，ODE 视角）的**非自回归**解码器；条件包括：
- T2S 输出的**语义表示**（语义 token 表示）  
- **说话人嵌入**（保障 timbre 一致）  
- （训练时）**prompt 段 Mel** 作为额外上下文

#### GPT 隐状态随机融合（提高清晰度）

- 取 T2S 最后一层 Transformer 的隐藏态 $H_{\text{GPT}}$ 作为“语义上下文增强”。  
- 以概率 $0.5$ 与语义 token 表示 $Q_{\text{sem}}$ 通过 MLP **随机融合**，得最终条件 $Q_{\text{fin}}$：  
  $$
  Q_{\text{fin}}=
  \begin{cases}
  \text{MLP}([Q_{\text{sem}}; H_{\text{GPT}}]), & \text{概率 }0.5\\
  Q_{\text{sem}}, & \text{否则}
  \end{cases}
  $$
- 经验效果：降低强情感场景下的 WER，改善发音清晰度。

#### 训练与推理
- **训练**：将目标 Mel 完全加噪作为源分布，条件为 $Q_{\text{fin}}$ 与说话人嵌入，进行流匹配训练；重建项通常采用 L1：  
  $$
  \mathcal L_{\text{mel}}=\frac{1}{F\cdot D}\sum_{f=1}^{F}\sum_{d=1}^{D}\left|y^{\text{pred}}-y^{\text{tar}}\right|
  $$
- **推理**：从高斯噪声出发，给定条件用 ODE 解算器生成 Mel。  
- **声码器**：采用 BigVGANv2 将 Mel 还原为波形。

### T2E：Text-to-Emotion（文本到情感向量）

#### 老师-学生蒸馏
- **教师**：将文本 $t$ 映射为 7 维基本情感分布 $p\in\Delta^7$（怒/乐/惧/厌/哀/惊/中性）。  
- **学生**：将若干“文本→分布”对蒸馏到轻量模型（如 Qwen-3-1.7B + LoRA），以交叉熵最小化教师分布。

#### 从分布合成连续情感向量
- 预先为每类情感收集若干参考音频，经 Emotion Conditioner 提取成嵌入集合 $V=\{V_e\}$。  
- 用 $p$ 对各类集合的均值做加权得到情感向量 $e_{\text{input}}$：  
  $$
  e_{\text{input}}=\sum_{e\in E}p_e\cdot\left(\frac{1}{|V_e|}\sum_{v\in V_e}v\right)
  $$
- 将 $e_{\text{input}}$ 直接作为 T2S 的情感条件输入，实现“自然语言→目标情感”的软控制。

### 训练与推理的落地清单（Checklist）

#### 训练
- **T2S**  
  - 设定 $L_{\text{speech}}$（覆盖 99% 语句长度），建立共享表：$W_{\text{sem}}=W_{\text{num}}$。  
  - Stage-1：全量训练，$p$ 以 0.3 概率置零（支持自由时长）。  
  - Stage-2：$[c+e,\ p,\ \cdots]$，冻结 speaker conditioner，仅训 emotion conditioner，启用 GRL+speaker-clf；$\alpha$ 可 warm-up。  
  - Stage-3：全量微调，冻结两类 conditioner。
- **S2M**  
  - 以 $Q_{\text{sem}}$ 与 $H_{\text{GPT}}$ 做 0.5 概率随机融合；  
  - L1 重建 + 流匹配损失；  
  - 验证强情感/高韵律样本上的 WER 与清晰度。
- **T2E**  
  - 组装“文本→7 维分布”训练对，蒸馏轻量学生；  
  - 构造 $e_{\text{input}}$ 并联通到 T2S 的情感接口。

#### 推理
- **控时长**：若需对齐字幕/口型，先估计/指定语义 token 目标数 $T$，取 $p=W_{\text{num}}h(T)$。  
- **自由时长**：$p=\mathbf{0}$，让 AR 自然停在终止符。  
- **情感来源**：  
  1) 参考音频 → Emotion Conditioner → $e$；  
  2) 文本描述 → T2E → $e_{\text{input}}$。两者均输入 T2S。  
- **音色**：timbre prompt → Speaker Conditioner → $c$。  
- **清晰度增强**：保持 S2M 的 0.5 融合策略；英语子集“糊字”明显可适度上调融合概率。

## 实验

<img src="http://public.file.lvshuhuai.cn/images\image-20250928125814198.png" alt="image-20250928125814198" style="zoom:50%;" />

