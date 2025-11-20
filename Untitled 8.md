# 10.30 医学多模态小组讨论

## 课题内容和挑战

### 任务内容

从若干张来自心脏不同部位病理切片 WSI 图像（部分含有部位标签） + （器官检验完整描述 + 组织病理学检验描述），生成病理学诊断

#### 示例

**WSI 图像**：

<img src="http://public.file.lvshuhuai.cn/images\image-20251029204034151.png" alt="image-20251029204034151" style="zoom:50%;" />

**器官检验完整描述**：重 330g。心包腔内见淡黄色积液，量约 200mL。心内、外膜光滑，未见出血点，心肌表、切面呈淡红色、贫血状，左、右心室未见扩张。左心室壁厚 1.2cm，右心室壁厚 0.3cm；心脏各瓣膜光滑，未见增生、粘连及赘生物，各瓣膜周径测量如下：二尖瓣 10cm，三尖瓣 11cm，主动脉瓣 7cm，肺动脉瓣 7.5cm。冠状动脉开口畅，左前降支管壁轻度粥样硬化性改变，管腔狭窄程度达 I 级。

**组织病理学检验描述**：心内、外膜未见增厚，心肌纤维排列尚可，局部心肌纤维断裂、嗜伊红染色增强，间质未见出血、炎症细胞浸润。冠状动脉左前降支管壁内膜轻度纤维性增厚，其下可见钙盐沉积。

**诊断**：冠状动脉粥样硬化症。

### 主要挑战

#### 1. 图像尺寸大

常规图像特征提取器接受的像素大约是 10MB 左右的通用图像。WSI 图像大小可能高达 1GB 甚至更高

使用多实例学习 MIL——一种弱监督手段

<img src="http://public.file.lvshuhuai.cn/images\image-20251029204417958.png" alt="image-20251029204417958" style="zoom:50%;" />

使用分层图像特征提取器

<img src="http://public.file.lvshuhuai.cn/images\image-20251029204646422.png" alt="image-20251029204646422" style="zoom:50%;" />

#### 2. 多图长文的统一

CLIP 训练策略针对单图短文本（caption）的模态对齐。

在我们的任务中，文本长，且每一文本对应的有多张可能存在互补信息的图片。

如何运用好每张图片的信息？如何运用好每张图片的部位信息？如何和长文本在特征空间中有效对齐？

#### 3. 基座模型的微调

全参微调大语言模型往往需要 100GB 以上的 VRAM，需要的数据规模也是海量。

如何降低算力和数据需求？

使用 PEFT 技术：LoRA、QLoRA、Prefix/Prompt Learning

是否有更好的方案？

#### 4. 如何准确处理文本中的数值数据

二尖瓣 10cm，三尖瓣 11cm，主动脉瓣 7cm，肺动脉瓣 7.5cm。

大语言模型能否准确从文本数字中提取信息，并加以处理？

TableGPT /2 将表格视为一种新的模态，构建了一个表格语义编码器，对单元格、表结构做层次表征，同时处理文本 token 和表格 token。

能否合理运用？

#### 5. 部位标签不完整

由于精细化的部位标签（左前降支、左冠脉等）的人工标注费时费力，部分数据是没有这些标签的。

如何从部分有标签数据外推到全部数据的自动化标注？

分类器、解码器？标注增强策略？

## Visual Explanations of Image-Text Representations via Multi-Modal Information Bottleneck Attribution

### 基本信息

- 多模态信息瓶颈归因下的图文表征可视化解析
- NIPS 2023
- GitHub：[YingWANGG/M2IB: Code for the paper Visual Explanations of Image–Text Representations via Multi-Modal Information Bottleneck Attribution](https://github.com/YingWANGG/M2IB)
- 一种用于图文多模态对齐的可解释性分析

### 研究背景

- 现有归因方法多针对**单模态**模型，难以解释视觉-语言预训练模型（VLPM）对**图像与文本**的联合决策
- 且常依赖下游标签。
- 论文提出一种**多模态信息瓶颈（M2IB）归因**：基于信息瓶颈原理，在**无标签**的条件下同时为图像与文本生成归因图，从而识别跨模态一致的关键要素，并在多数据集上优于梯度/扰动/注意力基线方法。

### 主要方法

#### 信息瓶颈理论

信息瓶颈（IB）旨在学习一个随机潜表示 $Z$，在**压缩输入** $X$ 的同时，**最大化对目标** $Y$ 的有用信息。标准形式可写为：  
$$
\max_\theta I(Z,Y;\theta)\ \ \text{s.t.}\ \ I(Z,X;\theta)\le \bar I
$$
其中 $I(Z,Y;\theta)$ 表示 $Z$ 和 $Y$ 在 $\theta$ 条件下的互信息，衡量 $Z$ 和 $Y$ 的相关程度。

等价的拉格朗日形式为  
$$
F(\theta)= I(Z,Y;\theta)-\beta\,I(Z,X;\theta),
$$
其中 $\beta$ 控制“保留与 $Y$ 相关信息”与“压缩 $X$”的权衡。

> 为什么对传统任务的归因，如图像分类有用？
>
> $X$ 是一个图片，$Y$ 是他的标签，我们要找一个表征 $Z$，最小化 $Z$ 和 $X$ 的互信息，是说，从 $Z$ 中删除 $X$ 的某些信息，最大化 $Z$ 和 $Y$ 的互信息，是说，保留 $Z$ 的表征能力。如果 $X$ 的某些信息被删除了，却不影响 $Z$ 的表征能力，就说明这些信息不重要，剩下的那些就是归因能力。

#### 多模态信息瓶颈理论

VLPM 往往**没有显式标签 $Y$**，只有成对图文输入。

论文以**跨模态一致性**替代监督 IB 中的“拟合项”：对模态 $m\in\{\text{image},\text{text}\}$，最大化 $Z_m$ 与**对方模态嵌入** $E_{m'}$ 的互信息，并最小化 $Z_m$ 与本模态输入 $X_m$ 的互信息：
$$
F_m(\theta_m)= I(Z_m,E_{m'};\theta_m)-\beta\,I(Z_m,X_m;\theta_m).
$$
这样在**无标签**情形下实现“相关性保留 + 信息压缩”，可直接用于多模态归因。

#### 多模态信息瓶颈归因法和优化目标

> 实际上简单理解：在图像/文本特征里放一排**可学习的阀门**（门控 + 噪声），训练它们：**只要能保持与“另一模态”一致的信息就放行，其他一律压掉**。最后“被保留下来的那部分”就是归因。

<img src="http://public.file.lvshuhuai.cn/images\image-20251029215121009.png" alt="image-20251029215121009" style="zoom:50%;" />

**不看公式版**

1. 拿到冻结的跨模态嵌入

    给一对输入：图像 $x_{\text{img}}$、文本 $x_{\text{txt}}$；用已训练好的 VLPM（如 CLIP）得到对应的嵌入 $e_{\text{img}}$、$e_{\text{txt}}$（不改动它们）。

2. 在中间层插一个“瓶颈”

    - 在图像侧某层特征 $f_{\text{img}}\in\mathbb{R}^J$ 上放一组门控 $h_{\text{img}}\in[0,1]^J$，得到
        $$
        z_{\text{img}} = h_{\text{img}}\odot f_{\text{img}} + (1-h_{\text{img}})\odot \text{noise}
        $$

    - 文本侧同理得 $z_{\text{txt}}$。
    - 直觉：**门开得大** = 保留该通道/patch/token；**门关小** = 用噪声替掉这部分信息。

3. 优化两个目标：对齐 + 压缩

    - **对齐（保留有用）**：让图像瓶颈输出能**预测/对齐文本嵌入**，例如让 $\cos\big(g_{\text{img}}(z_{\text{img}}),\, e_{\text{txt}}\big)$ 变大；文本侧反向亦然。

    - **压缩（丢掉冗余）**：用 KL 散度正则化把 $z$ 推向各向同性高斯分布，等价于**减少 $z$ 对原输入的信息量**（别什么都记）。

    - 两项一起优化，门控会**自动学会**只放行“跨模态必需”的维度。

4. 把门控强度当“归因分数”

    - 图像侧：把每个 patch/通道的门控 $h$ 投影/聚合回像素网格，得到**热力图**。

    - 文本侧：直接把 token 的门控当**词重要性权重**。

> KL 散度？
>
> 直接最小化 $I(Z;X)$ 很难算，于是用一个**上界**替代：
> $$
> I(Z,X)\;=\;\mathbb E_{x}\big[\,\mathrm{KL}\!\big(p(z|x)\,\|\,p(z)\big)\big] \;\le\;\mathbb E_{x}\big[\,\mathrm{KL}\!\big(p(z|x)\,\|\,q(z)\big)\big],
> $$

**一个小例子**

文本：**“a red bus on the street.”**

- “red”“bus”这些词的门会开得大；图像里对应**红色车身、车轮、车身轮廓**的 patch 门也会开大。
- 与句子无关的**天空/路边行人**等区域，因为开了也不提升图像↔文本的一致性，在“压缩”压力下会被关掉。

### 实验

#### 数据集

- **Conceptual Captions（CC）**：来自 Web 的多样图像-文本对，用于主量化评测与退化测试采样。 
- **MS-CXR**：改进标注的胸片—文本数据集，用于零样本定位与退化测试。
- **ROCO**：来自 PubMed Central 的放射学图像-字幕对。
- **RSICD**：从在线地图服务采集的遥感图像与描述。

### 实验

<img src="http://public.file.lvshuhuai.cn/images\image-20251029211554458.png" alt="image-20251029211554458" style="zoom:50%;" />

<img src="http://public.file.lvshuhuai.cn/images\image-20251029220834714.png" alt="image-20251029220834714" style="zoom:50%;" />

## A multimodal generative AI copilot for human pathology

原定删除

## Large-vocabulary forensic pathological analyses via prototypical cross-modal contrastive learning

### 基本信息

- 通过原型跨模态对比学习进行大词汇量法医病理学分析
- **HuggingFace**：[shenxiaochen/SongCi · Hugging Face](https://huggingface.co/shenxiaochen/SongCi)（需申请）
- **GitHub**：[shenxiaochenn/SongCi: Official Code for Large-vocabulary forensic pathological analyses via prototypical cross-modal contrastive learning](https://github.com/shenxiaochenn/SongCi)
- **数据集**：TCGA-LUAD、TCGA-BRCA、CAMELYON-16、CRC-100K、UniToPatho、TCGA-TIL、TCGA Uniform Tumor、PCam 以及自建数据集

### 摘要

法医病理学通过宏观与微观尸检在判定死因及死亡方式中发挥着关键作用。然而该领域面临结果变异性大、流程劳动密集及专业人才短缺等挑战。本文推出专为法医病理学设计的视觉语言模型“宋慈”，该模型采用先进的原型跨模态自监督对比学习技术，显著提升法医分析的准确性、效率与泛化能力。基于包含 1600 万张高分辨率图像切片、2228 组尸检全切片图像与大体关键发现的视觉-语言对，以及 471 种独特诊断结果的多中心大型数据集进行预训练与验证，“宋慈”在法医任务中展现出超越现有多模态模型与计算病理学基础模型的卓越性能，其能力媲美资深法医病理学家，显著优于经验不足的从业者，并提供可靠的多模态可解释性。

### 研究背景

法医病理学在确定死亡原因和方式、医学与法律分析等方面具有重要作用。但该领域存在结果高度依赖专家、主观性强、效率低、人才紧缺等挑战。近年来人工智能特别是自监督学习和多模态模型（视觉+文本）已在临床病理学取得突破，但直接迁移到法医领域效果有限，因为法医样本和任务具备特殊性（如多器官、多样化死亡原因、非癌相关等）。

### 主要贡献

#### 数据集

<img src="http://public.file.lvshuhuai.cn/images\image-20250728155002925.png" alt="image-20250728155002925" style="zoom:50%;" />

收集了来自 3 个权威法医队列的 9 种不同器官的多中心数据集，共包含 2228 组视觉语言对：

- 死后 WSI（图像）
- 器官层面大体关键发现（文本）
- 最终法医诊断结果（文本）

这些数据贡献了超过 1600 万 patch 图像块和 471 种不同诊断结果，其中仅 34 种诊断在所有法医中心间具有一致性

<img src="http://public.file.lvshuhuai.cn/images\image-20250728155254429.png" alt="image-20250728155254429" style="zoom:50%;" />

#### 数据预处理

**对于 WSI**

1. 通过 OpenCV 中的轮廓查找方法提取包含组织的区域
2. 分割区块

**对于大体关键发现**

1. 翻译为英文
2. 将关键发现文本标准化为统一长度以优化基础模型学习：“作为法医医学影像AI领域的教授，请将以下段落英译并压缩至不超过四句，确保符合学术写作规范，仅提供摘要内容”
3. 由两名法医病理学家审核验证处理文本

**对于法医病理学诊断**

汇编为短语

#### 模型

**推理目标**

模型接受多模态数据：来自不同器官的 WSI 和宏观大体发现

法医病理学家可以从不同角度提出多种诊断假设

模型给出可能的诊断结果

<img src="http://public.file.lvshuhuai.cn/images\image-20250731001240442.png" alt="image-20250731001240442" style="zoom:50%;" />

**主要架构**

- 用于 WSI（切片级）特征提取的图像编码器
- 用于嵌入大体关键发现和诊断查询的文本编码器
- 以及一个多模态融合模块，整合了 WSI 和大体关键发现的嵌入，以与诊断查询的嵌入对齐

#### 原型 patch 级编码器

<img src="http://public.file.lvshuhuai.cn/images\image-20250730215243333.png" alt="image-20250730215243333" style="zoom:50%;" />

由实例对比学习部分和原型对比学习部分组成。

这种原型空间建模方式使模型既能精准区分特定器官/病变特征，也能捕捉不同器官间共享的病理学变化，为下游任务（如自动分割、多模态融合）奠定基础。

**实例对比学习**

通过教师-学生方式实现

学生模型：ViT、投影层、预测器

教师模型：ViT、投影层、锐化与中心化模块

对每一个实例，通过数据增强手段生成两个不同的视图，分别输入到学生分支和教师分支中

学生模型通过梯度反向传播更新，教师模型通过 EMA 更新
$$
p_s(X_s^n) = \frac{\exp\left( g_s^{pre}\left( g_s^{pro}(f_s(X_s^n)) \right) / \tau_s \right)}
{\sum_{n=1}^{N} \exp\left( g_s^{pre}\left( g_s^{pro}(f_s(X_s^n)) \right) / \tau_s \right)}
$$

$$
p_t(X_t^n) = \frac{\exp\left( J_t g_t^{pro}\left(f_t(X_t^n)\right) / \tau_t \right)}
{\sum_{n=1}^{N} \exp\left( J_t g_t^{pro}\left(f_t(X_t^n)\right) / \tau_t \right)},
$$

$$
L_{ins} = -\sum_n p_t(X_t^n) \log(p_s(X_s^n)).
$$

**原型对比学习**

通过教师-学生方式实现、ViT、投影层

期望学习一组原型，每个原型是语义中心，代表一个常见的病理结构或状态。

同时要学习到一个从样本 patch 到原型的映射 $C_t$，这可以通过 Sinkhorn-Knopp 算法获得
$$
\hat{C}_t = \text{diag}(\mathbf{u}) \exp\left(\frac{\mathbf{P}^T \mathbf{Z}_t}{\epsilon}\right) \text{diag}(\mathbf{v})
$$
同时将这个 $C_t$ 作为伪标签约束学生分支的预测
$$
C_s = \frac{\exp(\mathbf{P}^T \mathbf{Z}_s / \tau_s^{\text{prototype}})}
{\sum_{m=1}^M \exp(\mathbf{P}^T \mathbf{Z}_s / \tau_s^{\text{prototype}})}
$$
对比学习
$$
L_{\text{prototype}} = -\sum \hat{c}_t \log(C_s)
$$

**正则化项**

1. $L_{ipc}$：防止多个原型学习到**重复的特征模式**，提升原型多样性。
    $$
    L_{\text{ipc}} = -\sum_{i=1}^N \log\left( 
    \frac{\exp(\mathbf{z}_i^T \mathbf{p}_j)}
    {\sum_{j=1}^M \exp(\mathbf{z}_i^T \mathbf{p}_j)}
    \right)
    $$

2. $L_{ipd}$：进一步**拉开原型间距离**，防止原型挤在一起，增加判别能力。
    $$
    L_{\text{ipd}} = \sum_{i=1}^N (\mathbf{z}_i - \mathbf{p}_j^i)^2 = \sum_{i=1}^N \left(2 - 2\mathbf{z}_i^T \mathbf{p}_j^c\right)
    $$

3. $L_{me-max}$：鼓励每个 patch 只和少数几个原型关联，**增加表示的稀疏性和判别性**。
    $$
    L_{\text{me-max}} = \sum_{i=1}^M \bar{C}_s^i \log(\bar{C}_s^i) + \log(M),
    $$

#### 门控注意力增强的多模态融合模块

<img src="http://public.file.lvshuhuai.cn/images\image-20250731001425292.png" alt="image-20250731001425292" style="zoom:50%;" />

**特征**

- 图像特征：patch 对齐到原型特征，多个patch 特征组合成 WSI 的特征，再叠加上 WSI 中每个原型的出现次数
- 文本特征：使用 **PLIP**（一个专门为病理图像设计的多模态大模型）对 Gross key findings（肉眼观察文字）进行编码。
- 对图像和文本特征增加高斯噪声，以提高其对后续跨模态融合的鲁棒性

**门控交叉注意力机制**

- 通过考虑来自另一模态的互补信息来更新每个模态的表示
- 使用 $z^t$ 作为指导，WSI 嵌入 $z^i$ 通过门控知识引导的交叉注意力层和随后的门控 FFN 进行更新
- 使用 $z^i$ 作为指导，$z^t$ 通过门控原型引导的交叉注意力层更新，随后是一个门控 FFN
- 拼接后使用基于门控 Transformer 的编码器
- 投影层

**大词汇量特性**

- 不同的诊断结果与融合后的特征的不同部分相关联
- 使用 **冻结的 PLIP 文本编码器**编码该诊断语句
- 计算余弦相似度、计算注意力分数

### 实验

#### 原型空间可视化

<img src="http://public.file.lvshuhuai.cn/images\image-20250728155751545.png" alt="image-20250728155751545" style="zoom:50%;" />

#### patch 级生成

<img src="http://public.file.lvshuhuai.cn/images\image-20250730234356405.png" alt="image-20250730234356405" style="zoom:50%;" />

#### 对比

<img src="http://public.file.lvshuhuai.cn/images\image-20250731011136764.png" alt="image-20250731011136764" style="zoom:50%;" />
