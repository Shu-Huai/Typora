# 说下你常用的 Linux 命令？

## 回答重点

### 文件与目录操作

- `ls`：列出目录内容，`-l` 显示详细信息，`-a` 显示隐藏文件。
- `cd`：切换目录。
- `mkdir`：创建目录。
- `rm`：删除文件或目录，`-f` 强制删除，`-r` 递归删除目录。
- `cp`：复制文件或目录，`cp -r` 递归复制。
- `mv`：移动或重命名文件。

### 文件内容查看

- `cat`：查看小文件。
- `more` / `less`：分页查看，`less` 支持向上翻页，适合大文件。
- `head`：查看文件开头。
- `tail`：查看文件末尾，`tail -f` 实时追踪日志。

### 系统管理

- `ps`：查看进程，`ps aux` 查看所有用户进程。
- `top` / `htop`：实时查看进程和资源使用。
- `kill` / `killall`：按 PID 或进程名终止进程。
- `df`：查看文件系统磁盘使用率。
- `du`：统计文件或目录大小，`du -h` 使用易读单位。

### 网络配置与调试

- `ping`：测试主机连通性。
- `ifconfig` / `ip`：查看和配置网络接口，`ip` 是现代替代方案。
- `netstat` / `ss`：查看连接和端口，`ss` 更快。
- `curl` / `wget`：发送 HTTP 请求和下载文件。

### 权限与用户管理

- `chmod`：修改权限，如 `chmod 755`。
- `chown`：修改文件所有者。
- `useradd` / `userdel`：添加或删除用户。
- `passwd`：修改密码。

## 扩展知识

### 查找与搜索

```bash
# 找 7 天内修改过的日志文件
find . -name "*.log" -mtime -7

# 找大于 100MB 的文件
find . -size +100M

# 递归搜索包含 Exception 的行
grep -rn "Exception" /var/log/

# 忽略大小写搜索
grep -i "error" app.log
```

`find` 和 `grep` 可以组合使用，例如：

```bash
find . -name "*.java" | xargs grep "@Deprecated"
```

### 压缩与解压

```bash
# tar + gzip 压缩
tar -czvf backup.tar.gz /data/logs

# 解压
tar -xzvf backup.tar.gz

# 查看压缩包内容
tar -tzvf backup.tar.gz
```

### 进程管理

```bash
ps aux
# USER 用户，PID 进程号，%CPU/%MEM 资源占用，VSZ/RSS 内存，STAT 状态

kill 1234                 # 发送 SIGTERM，优雅停止
kill -9 1234              # 发送 SIGKILL，强制停止
killall java
pkill -f "java.*MyApp"

nice -n 10 ./heavy_task.sh # 低优先级启动
renice +5 -p 1234         # 调整运行中进程优先级
```

### 网络调试

```bash
ss -tlnp                         # TCP 监听端口
ss -tan state established        # 已建立的 TCP 连接
tcpdump -i eth0 port 80          # 抓取 80 端口流量
tcpdump host 192.168.1.100 -w capture.pcap

curl -v http://api.example.com/users
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"test"}' http://api.example.com/users
curl -I http://example.com
```

### 定时任务

`crontab` 的时间格式是“分 时 日 月 周”：

```bash
crontab -e  # 编辑
crontab -l  # 查看

0 2 * * * /scripts/backup.sh
*/5 * * * * /scripts/health_check.sh
0 9 * * 1 /scripts/weekly_report.sh
```

注意 cron 的环境变量和登录 Shell 不同，脚本中最好使用绝对路径或主动加载环境变量。

### 日志排查

```bash
journalctl -u nginx                  # 服务日志
journalctl -f                        # 实时追踪
journalctl --since today             # 今天的日志
dmesg | tail -50                     # 最近内核消息
dmesg | grep -i memory               # 内存相关内核日志
```

### 文本处理

```bash
awk '{print $1, $3}' data.txt
awk -F: '{print $1}' /etc/passwd
sed -i 's/old/new/g' file.txt
sed -i '/^$/d' file.txt

# 统计日志中各类错误次数
cat app.log | grep ERROR | awk '{print $4}' | sort | uniq -c | sort -rn
```

## 面试官追问

#### 提问：磁盘快满了，怎么定位哪个目录或文件最大？

回答：先用 `df -h` 找出快满的挂载点，再进入目录用 `du -sh *` 逐层定位。也可以用 `find / -type f -size +100M` 找大文件，或使用交互式工具 `ncdu`。

#### 提问：怎么找 CPU 占用最高的进程？

回答：运行 `top` 后按 `P` 按 CPU 排序；脚本中可用 `ps aux --sort=-%cpu | head -10`；`htop` 还支持进程树和交互操作。

#### 提问：tail -f 追日志时如何过滤关键词？

回答：使用 `tail -f app.log | grep --line-buffered ERROR`，`--line-buffered` 可让匹配结果立即输出。多个关键词可用 `grep -E "ERROR|WARN"`。

#### 提问：进程变成僵尸进程怎么处理？

回答：僵尸进程已经结束，直接 kill 无效。应找到其父进程（通过 `ps -ef | grep Z` 查看 PPID），让父进程调用 `wait` 回收，或终止父进程让 init 接管清理，必要时重启服务。
