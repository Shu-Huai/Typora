# 解决 PyTorch No such Process 问题

## 问题描述

在 `nvtop / nvitop`（或类似 GPU 进程监控工具）中，某张 GPU 卡（例如 GPU1）上显示某个进程条目为 `No Such Process`，并且看起来占用了大量显存（例如 14GB）。

<img src="Z:\Public\images\256ad12e-aa2c-4564-9d19-304c6b004b01.png" alt="256ad12e-aa2c-4564-9d19-304c6b004b01" style="zoom:50%;" />

用户希望“精准 kill 掉它”。

典型现象包括：

- 监控工具里出现：`PID=xxxx  No Such Process`
- 想 `kill -9 PID` 却无效 / 找不到进程
- 或者 `ps` 能看到该 PID，但显示为 `<defunct>`（僵尸进程）

## 原因分析

### `No Such Process` 不一定代表“能 kill 的活进程”
`nvtop/nvitop` 通过 NVML 获取 PID，有时会出现：

- **进程已退出**，但监控工具显示残留条目
- 你在 **容器 / 不同 PID namespace** 中查看，导致 `/proc/<pid>` 不可见
- **GPU context 残留** 或驱动/显示进程（Xorg）仍占用设备文件

因此第一步必须确认该 PID 在当前环境中是否真实存在。

### 本次排查的真实原因：这是僵尸进程（Zombie）
用户执行后确认：

```bash
PID=3258630
ls -ld /proc/$PID
ps -p $PID -o pid,ppid,user,cmd
```

得到：

- `/proc/3258630` 存在
- `ps` 显示：`[pt_main_thread] <defunct>`，`STAT=Z`

这说明 `3258630` 是 **僵尸进程**：

- 僵尸进程已经“死了”，只剩进程表记录
- **无法通过 kill 杀死**（`kill -9` 也无效）
- 它需要 **父进程调用 wait() 回收** 才会消失

#### 排查中遇到的坑：`PPID` 是 bash 内置只读变量

用户尝试：

```bash
PPID=$(ps -o ppid= -p 3258630 | tr -d ' ')
```

报错：

```bash
bash: PPID: readonly variable
```

这是因为 `PPID` 在 bash 里是只读变量（代表当前 shell 的父 PID），不能拿来当普通变量名。

### 最终定位到父进程：`uv run ./mil_sim.py`

用正确变量名后定位：

```bash
ZPID=3258630
PARENT=$(ps -o ppid= -p $ZPID | tr -d ' ')
ps -p $PARENT -o pid,ppid,user,stat,cmd
```

得到：

- 僵尸：`3258630`（`STAT=Z`）
- 父进程：`3258627`，命令：`uv run ./mil_sim.py`

也就是说：**要消灭僵尸，必须让父进程回收或结束父进程。**

### 为什么 `kill -TERM 父进程` 后僵尸还在？

用户对父进程执行：

```bash
sudo kill -TERM 3258627
sleep 2
ps -p 3258630 -o pid,ppid,stat,cmd
```

发现僵尸仍然存在，进一步查看父进程状态：

```bash
ps -p 3258627 -o pid,ppid,user,stat,wchan,cmd
```

结果：

- `STAT=Tl`
    - **T**：stopped（被暂停/挂起）
    - **l**：多线程进程（lightweight process/threads）
- `WCHAN=do_sig`：在信号相关路径等待/停住

结论：**父进程处于 stopped 状态**（例如被 Ctrl+Z、调试器、ptrace 等挂起），所以它不会继续执行 `wait()`，僵尸也就不会被回收。

## 解决方案

> 核心原则：
>  **僵尸进程本体 kill 不掉，必须处理父进程（或 tracer）。**

### 确认 PID 是否真实存在

```bash
PID=3258630
ls -ld /proc/$PID 2>/dev/null || echo "PROC_NOT_FOUND"
ps -p $PID -o pid,ppid,user,stat,cmd
```

- `PROC_NOT_FOUND`：可能是容器 PID namespace 或条目残留，需到宿主机查/或用 `nvidia-smi` 查真实占用者
- `STAT=Z` 或 `<defunct>`：进入僵尸处理流程（下面）

### 正确找父进程（不要用 PPID 变量名）

```bash
ZPID=3258630
PARENT=$(ps -o ppid= -p $ZPID | tr -d ' ')
echo "zombie=$ZPID parent=$PARENT"

ps -p $ZPID   -o pid,ppid,stat,cmd
ps -p $PARENT -o pid,ppid,user,stat,wchan,cmd
pstree -ap $PARENT | head -n 30
```

本次定位结果：

- `PARENT=3258627`
- `CMD=uv run ./mil_sim.py`

### 如果父进程是 stopped（STAT 含 T），先 CONT 再 KILL

父进程显示 `STAT=Tl` 时，按以下顺序：

#### 检查是否被跟踪（ptrace/gdb/strace 等）

```bash
cat /proc/3258627/status | egrep 'State|TracerPid'
```

#### 先恢复运行，再强制结束父进程

```bash
sudo kill -CONT 3258627
sudo kill -KILL 3258627
```

#### 验证父进程、僵尸是否消失

```bash
ps -p 3258627 -o pid,stat,cmd || echo "parent gone"
ps -p 3258630 -o pid,ppid,stat,cmd || echo "zombie gone"
```

### 如果 TracerPid 非 0，先处理 tracer

假设输出为 `TracerPid: 12345`：

```bash
TR=12345
ps -p $TR -o pid,user,stat,cmd
sudo kill -KILL $TR

# 然后再杀父进程
sudo kill -KILL 3258627
```

### 确认显存占用是否真的来自该 PID（避免监控工具假象）

用 `nvidia-smi` 与设备文件占用者确认：

```bash
nvidia-smi -i 1 --query-compute-apps=pid,process_name,used_memory --format=csv
sudo fuser -v /dev/nvidia1
```

> 说明：僵尸进程通常不再真正占用 GPU 显存；
>  如果显存仍高，往往是其他活进程占用、或驱动残留/Xorg 占用导致。

## 小结

- `No Such Process` 不等于“有一个活进程能 kill”
- 如果 `ps` 显示 `<defunct>` / `STAT=Z`：这是僵尸进程，**kill 本体无效**
- 解决关键是：**找到父进程并让它回收（wait）或结束父进程**
- 本次最终方案：父进程 `STAT=Tl`（stopped），因此需要：

```
sudo kill -CONT 3258627
sudo kill -KILL 3258627
```

然后僵尸会随之消失（被 init/systemd 接管回收）。