# 论文精读 22 篇，代码复现 8 篇

| 名字                                                         | 来源                          | 内容                                                         | 代码                                                         | 标签                               | 复现 |
| ------------------------------------------------------------ | ----------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------------- | ---- |
| Decomposing Disease Descriptions for Enhanced Pathology Detection: A  Multi-Aspect Vision-Language Pre-training Framework | CVPR 2024                     | 利用病理先验知识将疾病文本描述转为结构化数据，然后和图片对齐 | [HieuPhan33/CVPR2024_MAVL: Multi-Aspect Vision Language Pretraining - CVPR2024](https://github.com/HieuPhan33/CVPR2024_MAVL) | 图文对齐、Transformer              |      |
| Large-vocabulary forensic pathological analyses via prototypical cross-modal contrastive learning | Nature Communications         | 用实例对比学习和原型对比学习做图文对齐                       | [shenxiaochenn/SongCi: Official Code for Large-vocabulary forensic pathological analyses via prototypical cross-modal contrastive learning](https://github.com/shenxiaochenn/SongCi) | SongCi、图文对齐、大模型、对比学习 | ✓    |
| RadGraph: Extracting Clinical Entities and Relations from Radiology Reports | NeurIPS 2021                  | 主要是一个 X 光影像数据集，还有一些实体关系抽取算法          | [Stanford-AIMI/radgraph](https://github.com/Stanford-AIMI/radgraph) | 数据集、医学图像                   |      |
| Data-efficient and weakly supervised computational pathology on whole-slide images | Nature Biomedical Engineering | CLAM                                                         | [https://github.com/mahmoodlab/CLAM](https://github.com/mahmoodlab/CLAM) | 多实例学习、医学图像               | ✓    |
| Scaling Vision Transformers to Gigapixel Images via  Hierarchical Self-Supervised Learning | CVPR 2022                     | 分层 ViT 建模，用于解决医学图像尺寸大的问题                  | https://github.com/mahmoodlab/HIPT                           | 医学图像、ViT                      | ✓    |
| Transformer-based Unsupervised Contrastive Learning for Histopathological Image Classification | Medical Image Analysis        | 选取语义相关的样本作为对比学习的正样本，拉近正样本的特征距离 + Swin Transformer | [Xiyue-Wang/TransPath](https://github.com/Xiyue-Wang/TransPath?tab=readme-ov-file) | 医学图像、对比学习                 |      |
| Swin Transformer: Hierarchical Vision Transformer using Shifted Windows | ICCV2021                      | 用滑动窗口做局部注意力，构建金字塔结构的特征                 | [microsoft/Swin-Transformer: This is an official implementation for "Swin Transformer: Hierarchical Vision Transformer using Shifted Windows".](https://github.com/microsoft/Swin-Transformer) | Transformer                        |      |
| Training language models to follow instructions with human feedback | NeurIPS 2022                  | 用人类反馈的关于大模型回答的偏好信息对大模型微调             |                                                              | 大模型、强化学习、RLHF、微调       |      |
| Direct Preference Optimization: Your Language Model is Secretly a Reward Model | NeurIPS 2023                  | RLHF 是一种强化学习，DPO 用一种损失函数简化了这个强化学习步骤 | [eric-mitchell/direct-preference-optimization: Reference implementation for DPO (Direct Preference Optimization)](https://github.com/eric-mitchell/direct-preference-optimization) | 大模型、DPO、微调                  |      |
| Active Preference Learning for Large Language Models         | ICML 2024                     | 在 DPO 上引入主动学习，度量是语言模型预测的熵 + 偏好模型的确定性差异 |                                                              | 大模型、主动学习、微调             |      |
| Learning Transferable Visual Models From  Natural Language Supervision | ICML 2021                     | CLIP，构造正负样本对，用对比学习联合训练图像和文本 encoder   | [openai/CLIP: CLIP (Contrastive Language-Image Pretraining), Predict the most relevant text snippet given an image](https://github.com/openai/CLIP) | 对比学习、图文对齐                 | ✓    |
| BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation | ICML 2021                     | BLIP，在 CLIP 的基础上引入一个自举式的 Caption 生成 + 过滤   | [salesforce/BLIP: PyTorch code for BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation](https://github.com/salesforce/BLIP) | 对比学习、图文对齐                 | ✓    |
| TinyCLIP: CLIP Distillation via Affinity Mimicking and Weight Inheritance | ICCV 2023                     | TinyCLIP，在 CLIP 的基础上做一个蒸馏模型                     | [wkcn/TinyCLIP: [ICCV2023] TinyCLIP: CLIP Distillation via Affinity Mimicking and Weight Inheritance](https://github.com/wkcn/TinyCLIP) | 蒸馏、图文对齐、对比学习           |      |
| Unified Vision-Language Pre-Training for Image Captioning and VQA | AAAI 2020                     | 用一个共享的 Transformer 结构提取图文特征                    | [LuoweiZhou/VLP: Vision-Language Pre-training for Image Captioning and Question Answering](https://github.com/LuoweiZhou/VLP) | Transformer、图文对齐              |      |
| TransMIL: Transformer-based Correlated Multiple Instance Learning for Whole Slide Image Classification | NeurIPS 2021                  | 基于多实例学习，引入 Transfomer 架构建模全局依赖             | [szc19990412/TransMIL: TransMIL: Transformer based Correlated Multiple Instance Learning for Whole Slide Image Classification](https://github.com/szc19990412/TransMIL) | 多实例学习、Transformer、医学图像  |      |
| Balancing Visual Context Understanding in Dialogue for Image Retrieval | ACL 2024                      | 在大模型上下文对话中找到和图像相关的描述，增强视觉表征       |                                                              | 图像检索、大模型                   |      |
| FG-CLIP: Fine-Grained Visual and Textual Alignment           | ICML 2025                     | 解决了 CLIP 对细粒度特征的近视问题、FineHARD数据集           | [360CVGroup/FG-CLIP: New generation of CLIP with fine grained discrimination capability, ICML2025](https://github.com/360CVGroup/FG-CLIP) | 图文对齐、数据集                   |      |
| The Power of Scale for Parameter-Efficient Prompt Tuning     | ACL 2021                      | Prompt Tuning，在输入文本前添加可学习的向量，引导预训练语言模型完成特定任务 | [mkshing/Prompt-Tuning: Implementation of "The Power of Scale for Parameter-Efficient Prompt Tuning"](https://github.com/mkshing/Prompt-Tuning) | 大模型、微调                       | ✓    |
| Prefix-Tuning: Optimizing Continuous Prompts for Generation  | ACL 2021                      | 在每一层自注意力里，为 K/V 拼接一段可训练的前缀向量          | [XiangLi1999/PrefixTuning: Prefix-Tuning: Optimizing Continuous Prompts for Generation](https://github.com/XiangLi1999/PrefixTuning) | 大模型、微调                       | ✓    |
| LoRA: Low-Rank Adaptation of Large Language Models           | ICLR 2022                     | LoRA 微调，把 $W$ 低秩分解为 $A\times B$，以节省参数         | [microsoft/LoRA: Code for loralib, an implementation of "LoRA: Low-Rank Adaptation of Large Language Models"](https://github.com/microsoft/LoRA) | 大模型、微调                       | ✓    |
| Multimodal Representation Learning via Maximization of Local Mutual Information | MICCAI 2021                   | 用互信息做，最大化图文局部信息                               |                                                              | 图文对齐、互信息                   |      |
| What to align in multimodal contrastive learning?            | ICLR 2025                     | 把多模态融合后的表示当作学习对象，互信息最大化               | [Duplums/CoMM: [ICLR 2025] Multi-modal representation learning of shared, unique and synergistic features between modalities](https://github.com/Duplums/CoMM) | 图文对齐、互信息                   | ✓    |

## 完成时间

以上所有论文均为在 2025 年 4 月至今阅读和复现，在这之前看的一些论文是关于 **3D 重建**、**扩散模型**、**图像生成**、**数字人**等方面的论文，跟开题方向相关性不大，没有写在这里面

## 复现工作对自己论文的作用

- CLIP：这个是最初始的图文对齐，只有普通的对比损失，提供对比学习的思路
- BLIP：这个能够生成一个 Caption，提供多尺度的特征进行图文对齐的思路
- Prompt Tuning：用于大模型的微调，可以是主动学习的一个优化方向
- Prefix-Tuning：用于大模型的微调，可以是主动学习的一个优化方向
- SongCi：医学图像多模态大模型的参考
- CLAM：医学图像侧的特征提取器
- Scaling Vision Transformers：医学图像的特征提取器
- LoRA：用于大模型的微调，可以是主动学习的一个优化方向
- CoMM：在对比学习里融了互信息，我也想用互信息做我的图文对齐

## 复现结果

### 图文对齐

这个我是放在多模态大模型代码里面的，没有单独整理过

| 模型     | Avg Sim   |
| -------- | --------- |
| CLIP     | 70.47     |
| BLIP     | 76.12     |
| **CoMM** | **78.26** |

### 大模型微调

| 方法          | 基座模型        | 数据量（条） | 平均相似度分数 | BERTScore F1 |
| ------------- | --------------- | ------------ | -------------- | ------------ |
| **lora**      | **Qwen 2.5-7B** | **≈ 1300**   | **0.8696**     | **0.8844**   |
| prompt tuning | Qwen 2.5-7B     | ≈ 1300       | 0.7801         | 0.7352       |
| prefix tuning | Qwen 2.5-7B     | ≈ 1300       | 0.7592         | 0.7487       |

### 医学图像

| 模型                            | Acc       | Std       |
| ------------------------------- | --------- | --------- |
| CLAM                            | 0.846     | 0.213     |
| **Scaling Vision Transformers** | **0.871** | **0.167** |

### SongCi

这个只做了推理的复现
