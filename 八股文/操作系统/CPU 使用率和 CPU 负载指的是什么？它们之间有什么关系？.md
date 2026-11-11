# CPU 使用率和 CPU 负载指的是什么？它们之间有什么关系？

## 回答重点

**CPU 使用率**是在某个时间窗口内 CPU 实际工作的时间占比。例如使用率 70%，表示 CPU 有 70% 的时间运行用户进程或内核任务，其余时间空闲。通常分为用户态（user）、内核态（system）和空闲（idle）时间。

**CPU 负载**表示系统中等待 CPU 处理的任务数量，包括正在运行和排队等待 CPU 时间片的任务。常见的 1 分钟、5 分钟、15 分钟平均负载就是该指标。

- 负载 ≤ CPU 核心数：任务通常能及时处理。
- 负载 > CPU 核心数：有任务排队等待，系统开始出现压力。

使用率反映 CPU 当前忙不忙，负载反映有多少任务在等待。负载还会统计 I/O 等待任务，因此低使用率也可能伴随高负载。

常见组合：

- **高使用率 + 高负载**：CPU 计算能力不足。
- **低使用率 + 高负载**：通常是 I/O 等待或锁竞争。
- **高使用率 + 低负载**：CPU 较忙但没有明显积压。
- **低使用率 + 低负载**：系统较空闲。

![CPU 使用率与负载](Z:/Public/images/0wgloEJX_image_mianshiya.webp)

## 扩展知识

### CPU 使用率的计算

Linux 会在 `/proc/stat` 中统计 CPU 各状态时间：

```bash
cat /proc/stat
cpu  12345 678 9012 345678 1234 0 567 0 0 0
```

字段依次包括 user、nice、system、idle、iowait、irq、softirq、steal、guest 和 guest_nice。使用率通常用两个采样点之间的非空闲时间除以总时间：

```java
long totalTime1 = user1 + system1 + idle1 + iowait1;
long totalTime2 = user2 + system2 + idle2 + iowait2;
long idleDiff = idle2 - idle1;
long totalDiff = totalTime2 - totalTime1;
double cpuUsage = 100.0 * (totalDiff - idleDiff) / totalDiff;
```

`top`、`htop` 等工具本质上都是周期采样后计算差值。

### CPU 负载的计算

Linux 负载不是简单统计队列长度，而是对活跃任务数做指数平滑平均。内核大约每 5 秒采样一次：

```c
load = load * exp(-5/60) + active_tasks * (1 - exp(-5/60));
```

1 分钟、5 分钟和 15 分钟负载分别使用不同衰减因子，用于平滑瞬时尖峰并反映长期趋势。

### 多核场景

判断系统是否过载要将负载除以 CPU 核心数。例如 8 核机器负载 8 表示平均每个核心一个任务，负载 16 表示平均每个核心前还有一个任务排队。可用 `nproc` 查看核心数：

```bash
nproc  # 输出 8
uptime # load average: 6.23, 5.67, 4.89
```

### 低使用率但高负载的排查

这类情况通常是 I/O 问题，可用 `vmstat` 查看：

```bash
vmstat 1 5
```

重点关注 `b`（等待 I/O 的进程数）和 `wa`（I/O 等待时间占比）。还可以用 `iostat -x 1` 查看磁盘 `await` 和 `%util`，用 `iotop` 定位具体读写进程。

![CPU 负载排查](Z:/Public/images/hRu6MjAj_KRnxvTNqPJ_mianshiya.webp)

## 面试官追问

#### 提问：负载达到多少算高？

回答：没有绝对阈值，要结合核心数和业务类型。经验上负载长期不要超过核心数的 70%，例如 8 核机器长期 5～6 以下较健康。计算密集型应用达到 80%～90% 也可能正常，更重要的是观察趋势：如果 15 分钟负载高于 1 分钟负载，说明系统正在恶化。

#### 提问：iowait 高但 CPU 使用率低，怎么定位？

回答：先用 `iostat -x 1` 看磁盘，重点检查 `await` 和 `%util`。`await` 达到几十甚至几百毫秒说明磁盘响应慢，`%util` 接近 100% 说明磁盘带宽打满；再用 `iotop` 找出高读写进程，分析日志、数据库扫描等原因。

#### 提问：top 和 vmstat 中的 CPU 使用率有什么区别？

回答：`top` 默认显示所有核心的平均瞬时使用率，按 1 可切换到单核心；`vmstat` 按指定采样间隔计算平均值，并同时展示内存、Swap、I/O 和上下文切换等指标，更适合整体诊断。
