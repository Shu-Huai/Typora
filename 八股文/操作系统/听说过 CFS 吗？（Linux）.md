# 听说过 CFS 吗？（Linux）

## 回答重点

CFS（Completely Fair Scheduler，完全公平调度器）是 Linux 从 2.6.23 开始使用的进程调度器，目标是让每个进程公平获得 CPU 时间。

CFS 使用 **vruntime（虚拟运行时间）** 衡量进程的调度优先级：vruntime 越小，表示进程“欠”的 CPU 时间越多，应优先运行。所有可运行进程按 vruntime 排序组织在红黑树中，调度器每次取最左侧节点。

调度流程：

1. 取出 vruntime 最小的进程。
2. 进程运行，vruntime 随运行时间增加。
3. 时间片耗尽或主动让出 CPU。
4. 更新 vruntime，将进程重新插回红黑树。
5. 再次选择最左侧进程。

![CFS 调度](Z:/Public/images/xkDj1Dff_image_mianshiya.webp)

进程优先级通过 `nice` 值体现，nice 越低优先级越高，vruntime 增长越慢，获得的 CPU 时间越多。红黑树插入和删除复杂度为 $O(\log N)$。

## 扩展知识

### 为什么从 $O(1)$ 调度器换成 CFS

$O(1)$ 调度器维护多个优先级队列，但交互式进程识别不够准确，可能把等待用户输入的进程误判为 CPU 密集型，导致桌面卡顿。CFS 不猜测进程类型，而是按“谁欠的 CPU 时间多，谁先运行”调度。交互进程睡眠期间 vruntime 不增加，唤醒后通常能快速获得 CPU。

### vruntime 计算

```text
vruntime 增量 = 实际运行时间 × (NICE_0_WEIGHT / 进程权重)
```

`NICE_0_WEIGHT` 为 1024。nice 值越低，权重越大，vruntime 增长越慢：

| nice 值 | 权重 | 相对 nice 0 的 CPU 时间比 |
| --- | --- | --- |
| -20 | 88761 | 约 87 倍 |
| -10 | 9548 | 约 9 倍 |
| 0 | 1024 | 1 倍 |
| 10 | 110 | 约 1/9 |
| 19 | 15 | 约 1/68 |

### 多核负载均衡

CFS 为每个 CPU 维护独立的运行队列和红黑树。内核会周期性执行负载均衡，把繁忙核心上的进程迁移到空闲核心，但迁移会造成缓存失效，因此只有负载差异超过阈值时才迁移。

![CFS 多核负载均衡](Z:/Public/images/un1Kj6VA_26mLLQDec7_mianshiya.webp)

### CFS 的局限

1. 不适合硬实时任务，实时场景应使用 `SCHED_FIFO` 或 `SCHED_RR`。
2. 大规模容器场景中进程数量极多，$O(\log N)$ 调度开销会变得明显。
3. 频繁上下文切换会带来寄存器保存、缓存和 TLB 失效等开销。

### Linux 6.6 的 EEVDF

Linux 6.6 引入 EEVDF（Earliest Eligible Virtual Deadline First）逐步替代 CFS。EEVDF 在 vruntime 基础上加入虚拟截止时间，让请求时间片较小、对延迟敏感的任务更快得到响应，适合桌面和游戏等场景。

## 面试官追问

#### 提问：进程睡眠很久后醒来，vruntime 很小，会霸占 CPU 吗？

回答：不会。唤醒时内核会根据当前运行队列的最小 vruntime 和调度延迟重新设置该进程的 vruntime，而不是直接使用睡眠前的旧值，因此它只会优先运行一段时间，不会长期霸占 CPU。

#### 提问：nice 值和 priority 有什么区别？

回答：nice 是用户空间可调整的优先级，范围 -20 到 19；priority 是内核内部优先级。普通进程通常可理解为 priority = nice + 120，`top` 的 PR 列显示 priority，NI 列显示 nice。实时进程 priority 通常为 0～99，数值越小优先级越高。

#### 提问：进程死循环会把系统卡死吗？

回答：通常不会。CFS 为每个进程设置运行时间上限，时间片用完就切换，其他进程仍能得到调度。但死循环会持续占满一个 CPU 核心，单核机器可能明显变卡，多核机器影响相对小。
