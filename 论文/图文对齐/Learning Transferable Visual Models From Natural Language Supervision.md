# Learning Transferable Visual Models From Natural Language Supervision

## 基本信息

- 从自然语言监督中学习可迁移的视觉模型
- CLIP
- GitHub：[openai/CLIP: CLIP (Contrastive Language-Image Pretraining), Predict the most relevant text snippet given an image](https://github.com/openai/CLIP)
- ICML 2021
- [Learning Transferable Visual Models From Natural Language Supervision.pdf](https://proceedings.mlr.press/v139/radford21a/radford21a.pdf)

## 摘要

最先进的计算机视觉系统经过训练，可预测一组固定的、预先确定的物体类别。这种受限的监督形式限制了它们的通用性和可用性，因为要确定任何其他视觉概念都需要额外的标记数据。直接从关于图像的原始文本中学习是一种很有前景的替代方法，它利用了更广泛的监督来源。我们证明，预测哪个标题与哪个图像匹配这一简单的预训练任务，是在从互联网收集的 4 亿个（图像、文本）对的数据集上从头开始学习最先进的图像表示的一种高效且可扩展的方式。预训练后，自然语言被用于引用已学习的视觉概念（或描述新的视觉概念），使模型能够零样本迁移到下游任务。我们研究了该模型在 30 多个不同的计算机视觉数据集上的性能，这些数据集涵盖了诸如光学字符识别（OCR）、视频中的动作识别、地理定位以及多种类型的细粒度物体分类等任务。该模型能以非平凡的方式迁移到大多数任务中，并且在不需要任何特定数据集训练的情况下，其性能通常能与完全监督的基线相当。例如，我们在 ImageNet 上实现了与原始 ResNet50 相当的零样本准确率，且无需使用 ResNet50 训练时所用到的 128 万个训练样本中的任何一个。我们在 https://github.com/OpenAI/CLIP 上发布了我们的代码和预训练模型权重。

## 主要方法

### 数据集

- WebImageText
- 采集自互联网上各类公开来源，构建了一个包含 4 亿（图像，文本）对的新数据集
- 通过包含 50 万个查询词集中的词汇来搜索（图像，文本）对，每个查询词最多包含20,000个（图像，文本）对以实现近似类别平衡。

### 对比学习

<img src="http://public.file.lvshuhuai.cn/images\image-20250929153149120.png" alt="image-20250929153149120" style="zoom:50%;" />

- **嵌入与相似度**：图像编码器与文本编码器各自输出向量，经 **L2 归一化** 后进入同一多模态空间；用**余弦相似度**构造配对分数，并乘以**可学习温度**（实现为 $\text{logit\_scale}=\exp(\tau)$）得到 logits。
- **批内配对 / 负样本**：对一个 batch 的 $N$ 个真实图文对 $(x_i, y_i)$，构造 **$N\times N$** 的相似度矩阵；除了对角线是真实配对，其他 $N^2-N$ 个都是**批内负样本**。模型要“在所有候选文本中找到图的那一个、在所有候选图中找到文的那一个”。
- **对称交叉熵损失**（双向检索）：先计算归一化后的相似度 $s_{ij}=\langle \hat{v}*i,\hat{t}*j\rangle$，logits 为 $z*{ij}=\exp(\tau), s*{ij}$。损失为图→文与文→图两个方向的平均：$\mathcal{L}_\text{img}=\frac{1}{N}\sum_{i=1}^N\!-\log\frac{\exp(z_{ii})}{\sum_{j=1}^N\exp(z_{ij})},\quad \mathcal{L}_\text{text}=\frac{1}{N}\sum_{j=1}^N\!-\log\frac{\exp(z_{jj})}{\sum_{i=1}^N\exp(z_{ij})}$，$\mathcal{L}=\tfrac{1}{2}\big(\mathcal{L}_\text{img}+\mathcal{L}_\text{text}\big)$

- 这正是 **InfoNCE / N-pair** 思路在图文上的**对称**版本。
- **实现取舍**：为提升训练效率与稳定性，CLIP **只用线性投影**映射到对比空间（不再用非线性 MLP 头），图像侧仅做**随机方形裁剪**等简洁增广；**温度参数 $\tau$ 直接参与训练**，作为 log-参数化的**可学习标量**。

#### 直观理解

- 学到的空间让“正确图—文”**更近**、其余批内组合**更远**；
- 对称损失 = 同时优化**图检索文**与**文检索图**，让两侧编码器协同对齐；
- 可学习温度控制 softmax 的“锐度”，在大批量训练中尤为关键（类间拉开、更稳定）。

## 实验

<img src="http://public.file.lvshuhuai.cn/images\image-20250929153607368.png" alt="image-20250929153607368" style="zoom:50%;" />

## 复现

```python
from tqdm import tqdm
from torch.utils.data import DataLoader
from sklearn.linear_model import LogisticRegression
import numpy as np
import os
from torchvision.datasets import CIFAR100
import torch
import clip
from PIL import Image


def test_clip():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device, download_root="./checkpoints")

    image = preprocess(Image.open("CLIP.png")).unsqueeze(0).to(device)
    text = clip.tokenize(["a diagram", "a dog", "a cat"]).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)

        logits_per_image, logits_per_text = model(image, text)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()

    # prints: [[0.9927937  0.00421068 0.00299572]]
    print("Label probs:", probs)


def test_zero_shot():
    # Load the model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load('ViT-B/32', device)

    # Download the dataset
    cifar100 = CIFAR100(root="./datas", download=True, train=False)

    # Prepare the inputs
    image, class_id = cifar100[3637]
    image_input = preprocess(image).unsqueeze(0).to(device)
    text_inputs = torch.cat(
        [clip.tokenize(f"a photo of a {c}") for c in cifar100.classes]).to(device)

    # Calculate features
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_inputs)

    # Pick the top 5 most similar labels for the image
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    values, indices = similarity[0].topk(5)

    # Print the result
    print("\nTop predictions:\n")
    for value, index in zip(values, indices):
        print(f"{cifar100.classes[index]:>16s}: {100 * value.item():.2f}%")


def test_linear_probe():
    # Load the model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-L/14@336px", device)

    # Load the dataset
    root = os.path.expanduser("./datas")
    train = CIFAR100(root, download=True, train=True, transform=preprocess)
    test = CIFAR100(root, download=True, train=False, transform=preprocess)


    def get_features(dataset):
        all_features = []
        all_labels = []

        with torch.no_grad():
            for images, labels in tqdm(DataLoader(dataset, batch_size=100)):
                features = model.encode_image(images.to(device))

                all_features.append(features)
                all_labels.append(labels)

        return torch.cat(all_features).cpu().numpy(), torch.cat(all_labels).cpu().numpy()


    # Calculate the image features
    train_features, train_labels = get_features(train)
    test_features, test_labels = get_features(test)

    # Perform logistic regression
    classifier = LogisticRegression(
        random_state=0, C=0.316, max_iter=1000, verbose=1)
    classifier.fit(train_features, train_labels)

    # Evaluate using the logistic regression classifier
    predictions = classifier.predict(test_features)
    accuracy = np.mean((test_labels == predictions).astype(float)) * 100.
    print(f"Accuracy = {accuracy:.3f}")

if __name__ == "__main__":
    test_clip()
    test_zero_shot()
    test_linear_probe()
```
