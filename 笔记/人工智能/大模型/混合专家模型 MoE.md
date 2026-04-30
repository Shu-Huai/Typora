# 混合专家模型 MoE

> 本文只讨论 **MoE / Mixture of Experts / 混合专家模型**。MoE 属于模型架构与训练/推理效率问题，不是应用层编排概念。它关心的是：在模型内部如何用“稀疏激活”和“专家路由”扩大参数容量，同时尽量控制每个 token 的实际计算量。

## MoE 的核心问题：为什么要“混合专家”

深度学习模型的一个基本经验是：在数据、训练方法和算力足够的情况下，模型参数规模越大，通常越容易获得更强的表达能力。Dense Transformer 采用的是“所有 token 经过同一套参数”的模式。无论当前 token 是代码、数学公式、英文单词、中文词语，还是普通标点，它都会经过同一个前馈网络层。

这种设计简单、稳定、硬件友好，但它有一个直接问题：如果想继续扩大模型容量，通常就要让更多参数参与每次前向计算。参数越多，训练 FLOPs、推理 FLOPs、显存占用和通信成本都会上升。MoE 的目标不是否定大模型扩展规律，而是换一种扩展方式：

- **总参数量可以很大**，因为模型内部放置了很多 expert；
- **每次计算只激活一部分参数**，因为每个 token 只被路由到少数 expert；
- **模型容量和单次计算量不再严格同步增长**，这是 MoE 相比 dense model 的核心价值。

更精确地说，MoE 是一种 **conditional computation（条件计算）**。模型不是对所有输入使用完全相同的参数路径，而是根据输入内容动态选择一部分参数参与计算。对于语言模型而言，这个选择通常发生在 token 级别：每个 token 在每一层可能被路由到不同的专家。

可以用一个简化类比理解：

```text
Dense Model：
每个 token 都找同一个通用处理器处理。

MoE Model：
模型内部有多个专家处理器。
每个 token 先经过 Router 判断，再交给少数几个专家处理。
```

这不是“多个模型投票”，也不是“多个完整模型 ensemble”。MoE 通常是在一个 Transformer 内部，把某些 FFN/MLP 子层替换成一组专家 FFN，再由 Router 决定每个 token 使用哪些专家。

## MoE 在 Transformer 中放在哪里

标准 Transformer Block 通常可以简化成两部分：

```text
输入 hidden states
↓
Self-Attention
↓
FFN / MLP
↓
输出 hidden states
```

在大多数 LLM 的 MoE 架构中，MoE 主要替换的是 **FFN / MLP 层**，而不是 Attention 层。也就是说，MoE Transformer Block 更像这样：

```text
输入 hidden states
↓
Self-Attention
↓
MoE-FFN：Router + 多个 Expert FFN
↓
输出 hidden states
```

为什么通常替换 FFN？原因有几个：

1. Transformer 中 FFN 参数量通常占比较大，把 FFN 拆成多个 expert 可以明显扩大模型容量。
2. FFN 是逐 token 处理的结构，比较适合做 token-level routing。
3. Attention 涉及 token 与 token 之间的交互，做稀疏专家化会引入更复杂的结构和通信问题。
4. 保持 Attention dense，可以降低架构不稳定性，让 MoE 主要承担“参数容量扩展”的角色。

一个普通 FFN 可以写成：

```python
y = ffn(x)
```

一个 MoE-FFN 可以抽象成：

```python
scores = router(x)
selected_experts = topk(scores, k=2)
y = weighted_sum(expert_i(x) for expert_i in selected_experts)
```

从形状上看，输入和输出仍然是 `[batch_size, seq_len, hidden_dim]`。MoE 不改变 Transformer Block 对外的接口，只是在 Block 内部增加了路由、分发、专家计算和结果合并。

### Dense Model 与 Sparse MoE 的参数口径

讨论 MoE 时经常会看到两个数字：

```text
Total Parameters：模型总参数量
Activated Parameters：每个 token 实际激活的参数量
```

Dense 模型中，这两个数通常比较接近。比如一个 70B dense model，每个 token 前向时大部分参数都会参与计算。

MoE 模型中，这两个数可能相差很大。比如一个模型总参数为 236B，但每个 token 只激活 21B 参数；或者总参数为 671B，每个 token 只激活 37B 参数。这个差异不是文字游戏，而是 MoE 的本质：**容量由总参数体现，计算成本更接近激活参数体现**。

但要注意，Activated Parameters 不等于真实推理成本的全部。真实推理还受以下因素影响：

- KV cache 大小；
- Attention 计算；
- expert 分布在哪些 GPU 上；
- token 到 expert 的 dispatch / combine 通信；
- batch size、sequence length、prefill/decode 阶段差异；
- 专家负载是否均衡。

因此，“MoE 激活参数少，所以一定推理便宜”是不严谨的。MoE 能降低计算密度，但可能提高系统调度复杂度和通信成本。

## Router、Expert 与稀疏路由机制

MoE 的核心组件有三个：**Expert、Router/Gate、Top-K Routing**。

### Expert：专家网络

Expert 通常是一个 FFN/MLP。不同专家结构可以相同，但参数不同。最朴素的 expert 可以理解成：

```python
class Expert(nn.Module):
    def __init__(self, hidden_dim, ffn_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, ffn_dim),
            nn.GELU(),
            nn.Linear(ffn_dim, hidden_dim),
        )

    def forward(self, x):
        return self.net(x)
```

在 Transformer MoE 中，一个 MoE 层可能有 8、16、64、128 个甚至更多 experts。每个 expert 都学习不同的参数子空间。理想情况下，不同专家会形成某种功能分工，例如某些专家更常被代码 token 激活，某些专家更常被数学表达激活，某些专家更常处理通用语言现象。但这种分工不是人为指定的，而是训练过程中由路由机制和数据分布共同形成的。

需要注意的是，expert 并不一定天然具有人类可解释的“职业标签”。不能简单说 Expert 1 是数学专家、Expert 2 是代码专家。实际情况更复杂：专家可能体现的是隐空间中的分布偏好、token 模式、语法/语义特征组合，未必对应人类直观类别。

### Router / Gate：路由器

Router 负责为每个 token 计算专家选择分数。常见做法是对 token hidden state 做一次线性变换，得到每个 expert 的 logit：

```text
router_logits = x @ W_router
```

然后经过 softmax 得到专家概率：

```text
router_probs = softmax(router_logits)
```

再选择概率最高的 Top-K experts。若 `num_experts = 8`，`top_k = 2`，那么每个 token 在当前 MoE 层只会被送到 2 个专家。

数学上可以简化写成：

```text
S(x) = TopK(softmax(W_r x), K)
```

其中：

- `x` 是某个 token 的 hidden state；
- `W_r` 是 router 参数；
- `S(x)` 是该 token 被分配到的专家集合；
- `K` 是每个 token 激活的专家数量。

最终输出可以写成：

```text
MoE(x) = sum_{i in S(x)} p_i(x) * E_i(x)
```

其中：

- `E_i` 是第 i 个专家；
- `p_i(x)` 是 router 给这个专家的权重；
- 输出是多个专家结果的加权和。

### Top-1、Top-2 与 Top-K Routing

不同 MoE 架构会采用不同路由策略。

```text
Top-1 Routing：
每个 token 只交给一个 expert。

Top-2 Routing：
每个 token 交给两个 experts，再加权合并。

Top-K Routing：
每个 token 交给 K 个 experts，K 可以大于 2。
```

Top-1 的优点是简单、计算和通信成本低，Switch Transformer 就是典型代表。Top-2 的优点是更稳，因为一个 token 可以获得两个专家的处理结果，Mixtral 8x7B 就采用每层 8 个 expert 中选 2 个的方式。Top-K 越大，模型表达可能更充分，但专家计算量和跨设备通信也会增加。

从工程角度看，MoE 不是只多了一个 `topk()` 操作。实际执行时要完成：

1. 对所有 token 计算 router 分数；
2. 按专家 ID 对 token 重新分组；
3. 把 token dispatch 到对应 expert 所在设备；
4. 每个 expert 批量处理分配给自己的 token；
5. 将 expert 输出 combine 回原 token 顺序；
6. 继续进入下一层 Transformer。

这也是为什么 MoE 在论文里看起来简洁，但在训练框架和推理引擎里复杂度很高。

## 训练 MoE 的关键难点

MoE 的难点不在“有多个专家”这个想法本身，而在于如何让路由、专家、硬件并行和优化过程稳定协同。

### 负载均衡问题

最典型的问题是 expert load imbalance。Router 可能倾向于把大量 token 分给少数几个专家，导致热门专家过载，冷门专家几乎没有训练信号。

结果是：

- 热门专家计算压力大，成为速度瓶颈；
- 冷门专家更新不足，参数浪费；
- GPU 间通信不均衡；
- 总参数虽大，但有效容量没有充分利用；
- 训练可能不稳定。

因此，很多 MoE 方法会引入 **load balancing loss**。它的目标不是直接提升语言建模损失，而是约束路由分布不要过度集中。直观上，它希望“每个专家被选中的比例”与“每个专家获得的 router probability”不要偏得太厉害。

可以粗略理解成：

```text
主损失：让模型预测下一个 token 更准确。
负载均衡损失：让 expert 使用更均匀，避免少数 expert 被挤爆。
```

不过，负载均衡也不能过强。若强行平均分配 token，Router 的自由度会下降，专家难以形成自然分工。因此，MoE 训练常见矛盾是：

```text
专家要专业化，但不能过度塌缩到少数专家；
路由要自由选择，但不能造成系统负载失衡。
```

### Expert Capacity 与 Token Dropping

真实 MoE 系统通常会限制每个 expert 在一个 batch 内最多接收多少 token，这称为 expert capacity。若分配给某个 expert 的 token 超过容量，就可能发生 token dropping，或者使用备用策略处理溢出的 token。

例如：

```text
batch 中共有 4096 个 token
num_experts = 8
理想平均每个 expert 处理 512 个 token
capacity_factor = 1.25
则每个 expert 容量约为 640 个 token
```

如果 Router 把 900 个 token 分给 Expert 3，那么超出的 token 就必须被处理。常见策略包括：

- 丢弃溢出 token 的 expert 路径，保留残差连接；
- 路由到备选 expert；
- 增大 capacity factor；
- 改进 load balancing；
- 使用更复杂的调度算法。

Token dropping 会影响训练和推理质量，但 capacity 太大又会浪费显存和计算。因此它是质量、效率、稳定性之间的折中。

### 路由抖动与训练不稳定

Router 是一个离散选择机制。虽然 router score 本身可微，但 Top-K 选择会造成稀疏路径。训练早期如果 Router 不稳定，token 分配会频繁变化，专家学习到的分布也会漂移。

常见稳定化手段包括：

- 给 router logits 添加噪声，鼓励探索；
- 使用 auxiliary loss 做负载均衡；
- 控制 router 的 dtype，例如用更高精度计算 router；
- 对 expert capacity、dropout、初始化做约束；
- 分阶段训练或使用更保守的学习率；
- 在某些架构中引入 shared experts，承载通用知识。

DeepSeekMoE 一类架构提出了更细粒度的专家划分和 shared experts 机制，目的就是加强专家专门化，同时减少 routed experts 之间的冗余。

### 分布式通信成本

Dense 模型的主要成本是矩阵乘法。MoE 除了矩阵乘法，还多了 token dispatch 和 combine。这通常涉及跨 GPU 的 all-to-all 通信。

在 expert parallelism 中，不同专家可能放在不同设备上。一个 GPU 上的 token 可能要被发送到另一个 GPU 的 expert 上计算，算完再发回来。这会导致：

- 通信延迟；
- batch 内 token 分布不均；
- 某些 GPU 等待热门 expert；
- 小 batch 或 decode 阶段吞吐不理想。

所以 MoE 的效率不是纯算法问题，而是算法、并行策略、显存布局、网络带宽和推理调度共同决定的系统问题。

## MoE 推理与部署：为什么“参数少激活”仍然不简单

很多人第一次看到 MoE 会以为：既然每次只激活少数专家，那么推理一定像小模型一样便宜。这个理解只对了一半。

MoE 的计算量确实可以接近 activated parameters，而不是 total parameters。但部署时还要考虑几个现实问题。

### 总参数仍然要存储

虽然每个 token 只激活部分专家，但模型服务系统通常需要把所有专家参数放在显存或可快速访问的内存中。否则，如果专家参数频繁从 CPU 或磁盘加载到 GPU，延迟会非常高。

因此，一个 671B 总参数、37B 激活参数的 MoE 模型，单 token 计算不等于 671B dense model，但部署时仍然要处理 671B 参数的存储、切分和调度问题。

可以这样区分：

```text
计算成本：更接近 activated parameters
存储成本：更接近 total parameters
系统复杂度：取决于专家并行、通信和调度
```

### Prefill 和 Decode 阶段差异

LLM 推理通常分成两个阶段：

- **Prefill**：处理用户输入的整段 prompt，批量 token 较多，矩阵乘法更容易吃满 GPU；
- **Decode**：逐 token 生成，batch 和序列维度更小，对延迟、KV cache 和调度更敏感。

MoE 在 prefill 阶段通常更容易发挥吞吐优势，因为有大量 token 可以分配给专家批处理。在 decode 阶段，每次生成的新 token 数量少，专家分发可能变得更零碎，通信和调度开销占比上升。

因此，MoE 推理优化常常需要分别考虑 prefill throughput 和 decode latency。

### Expert Parallelism 与张量并行/流水线并行

MoE 模型常见并行方式包括：

- **Data Parallelism**：复制模型，分不同数据；
- **Tensor Parallelism**：把单个矩阵运算切到多个设备；
- **Pipeline Parallelism**：按层切分模型；
- **Expert Parallelism**：把不同 expert 放到不同设备。

Dense 模型主要关注张量并行和流水线并行。MoE 则必须额外处理 expert parallelism，因为专家天然适合按 expert 维度切分。但 expert parallelism 也带来跨设备 token 分发，这正是 MoE 系统复杂度的来源之一。

### MoE 不等于“低显存魔法”

MoE 是降低单位 token 计算成本的一种结构，但不是免费午餐。它可能带来：

- 更高的模型权重存储需求；
- 更复杂的分布式通信；
- 更难的量化和专家加载策略；
- 更复杂的负载均衡；
- 更高的工程实现门槛。

因此，MoE 更适合在大规模训练和服务场景中发挥优势。对于个人单卡部署，MoE 是否更划算要看具体模型、量化方式、显存容量、推理框架和 batch 场景。

## 典型 MoE 架构与发展脉络

MoE 不是 2024 年才出现的概念，但近几年因为大语言模型扩展而重新变得重要。

### Sparsely-Gated MoE

Shazeer 等人在 2017 年提出的 Sparsely-Gated Mixture-of-Experts Layer 是现代神经网络 MoE 的重要基础。它强调用可训练 gating network 为输入选择少量 feed-forward experts，从而在不线性增加计算量的情况下扩大模型容量。

这一阶段的关键思想是：

```text
条件计算 + 稀疏门控 + 多专家 FFN
```

它证明了 MoE 可以显著扩大模型参数容量，但也暴露了训练稳定性、负载均衡和分布式效率问题。

### GShard

GShard 将 MoE 与大规模自动分片结合起来，用于超大规模 multilingual translation Transformer。它的重要意义在于把 MoE 从“结构想法”推进到“可大规模训练的系统实践”。

GShard 说明，MoE 的核心不只是模型层设计，还包括自动 sharding、跨设备通信和大规模训练编译支持。没有系统层支撑，MoE 很难真正训练到几百亿、几千亿甚至万亿参数规模。

### Switch Transformer

Switch Transformer 采用更简单的 Top-1 routing，每个 token 只选择一个 expert。它的目标是降低 MoE 路由和通信复杂度，同时提升训练稳定性。

Switch Transformer 的关键取向是：

```text
简单路由
降低通信
改善稳定性
用稀疏结构扩展到更大参数规模
```

它也说明了一个重要事实：MoE 不一定要每个 token 走多个专家。为了工程效率，Top-1 routing 可能是非常有吸引力的选择。

### Mixtral 8x7B

Mixtral 8x7B 是近年开源 MoE 语言模型中非常典型的例子。它是 decoder-only sparse MoE，每层有 8 个 feed-forward experts，每个 token 选择 2 个专家处理并加权合并。

它的结构特点可以概括为：

```text
8 experts per layer
Top-2 routing
decoder-only Transformer
每个 token 在每层选择不同专家
```

Mixtral 的意义在于，它把 MoE 从大公司内部训练系统进一步带到开放模型生态中，使更多人开始直观理解 total parameters 与 active parameters 的区别。

### DeepSeekMoE、DeepSeek-V2/V3 与细粒度专家

DeepSeekMoE 关注 expert specialization。传统 MoE 中，专家数量有限、每次选 Top-K，可能导致专家之间冗余较高。DeepSeekMoE 提出更细粒度的专家划分，并引入 shared experts 承载通用知识，试图让 routed experts 更专门化。

DeepSeek-V2 和 DeepSeek-V3 则展示了 MoE 在大型语言模型中的系统化应用。例如 DeepSeek-V2 是 236B total parameters、21B activated parameters；DeepSeek-V3 是 671B total parameters、37B activated parameters。这类模型说明 MoE 已经成为大模型扩展中的主流技术路线之一。

### Qwen3 MoE

Qwen3 系列中也包含 MoE 模型，例如 Qwen3-235B-A22B 和 Qwen3-30B-A3B。这类命名本身就体现了 MoE 的重要口径：

```text
235B-A22B：
总参数约 235B
激活参数约 22B

30B-A3B：
总参数约 30B
激活参数约 3B
```

看到这类命名时，应当立刻意识到它不是普通 dense model 的参数表达方式，而是在区分 total parameters 与 activated parameters。

## 一个极简 PyTorch MoE 示例

下面这个代码只用于理解 MoE 的基本结构，不是高性能实现。真实 MoE 系统不会用这种 for-loop 方式逐 expert 处理，因为它效率较低，也没有处理 expert capacity、all-to-all 通信和 token dropping。

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class Expert(nn.Module):
    def __init__(self, hidden_dim: int, ffn_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, ffn_dim),
            nn.GELU(),
            nn.Linear(ffn_dim, hidden_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SimpleMoE(nn.Module):
    def __init__(
        self,
        hidden_dim: int,
        ffn_dim: int,
        num_experts: int = 8,
        top_k: int = 2,
    ):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k

        self.router = nn.Linear(hidden_dim, num_experts, bias=False)
        self.experts = nn.ModuleList([
            Expert(hidden_dim, ffn_dim)
            for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor):
        """
        x: [batch_size, seq_len, hidden_dim]
        return:
            output: [batch_size, seq_len, hidden_dim]
            aux_info: dict
        """
        batch_size, seq_len, hidden_dim = x.shape
        tokens = x.reshape(-1, hidden_dim)  # [num_tokens, hidden_dim]

        # 1. Router 为每个 token 计算 expert 分数
        router_logits = self.router(tokens)  # [num_tokens, num_experts]
        router_probs = F.softmax(router_logits, dim=-1)

        # 2. Top-K 选择
        topk_probs, topk_ids = torch.topk(
            router_probs,
            k=self.top_k,
            dim=-1,
        )  # [num_tokens, top_k]

        # 3. 为了保持加权稳定，通常会对 Top-K 权重重新归一化
        topk_probs = topk_probs / topk_probs.sum(dim=-1, keepdim=True)

        # 4. 专家计算与结果合并
        output = torch.zeros_like(tokens)

        for expert_id, expert in enumerate(self.experts):
            # mask: 哪些 token 的 Top-K 中包含当前 expert
            token_mask = (topk_ids == expert_id)

            if not token_mask.any():
                continue

            token_indices, slot_indices = token_mask.nonzero(as_tuple=True)

            selected_tokens = tokens[token_indices]
            expert_output = expert(selected_tokens)

            weights = topk_probs[token_indices, slot_indices].unsqueeze(-1)
            output[token_indices] += weights * expert_output

        output = output.reshape(batch_size, seq_len, hidden_dim)

        # 5. 记录一些路由信息，便于观察 expert 使用是否均衡
        with torch.no_grad():
            expert_counts = torch.bincount(
                topk_ids.reshape(-1),
                minlength=self.num_experts,
            )

        aux_info = {
            "router_logits": router_logits,
            "router_probs": router_probs,
            "topk_ids": topk_ids,
            "topk_probs": topk_probs,
            "expert_counts": expert_counts,
        }

        return output, aux_info


if __name__ == "__main__":
    torch.manual_seed(42)

    batch_size = 2
    seq_len = 4
    hidden_dim = 16
    ffn_dim = 64

    moe = SimpleMoE(
        hidden_dim=hidden_dim,
        ffn_dim=ffn_dim,
        num_experts=4,
        top_k=2,
    )

    x = torch.randn(batch_size, seq_len, hidden_dim)
    y, info = moe(x)

    print("input shape:", x.shape)
    print("output shape:", y.shape)
    print("topk expert ids:")
    print(info["topk_ids"])
    print("expert counts:")
    print(info["expert_counts"])
```

这段代码可以帮助理解 MoE 的最小闭环：

1. 输入 token hidden states；
2. Router 输出每个 expert 的概率；
3. Top-K 选择专家；
4. 只对选中的专家执行 FFN；
5. 按 router 权重把 expert 输出加权合并；
6. 统计每个 expert 被使用的次数。

如果运行结果显示某个 expert count 特别高，而其他 expert 几乎为 0，就说明存在明显负载不均衡。在真实训练中，这会通过辅助损失、容量控制或改进路由策略来缓解。
