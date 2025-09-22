# Powershell 操作任务计划程序

## 查找正在运行的任务

### 命令

```powershell
$running = Get-ScheduledTask | Where-Object { $_.State -eq 'Running' }     
$running | Format-Table TaskPath, TaskName
```

### 效果

<img src="http://public.file.lvshuhuai.cn/images\image-20250920130036980.png" alt="image-20250920130036980" style="zoom:50%;" />

## 停止某个任务并检查

### 命令

```powershell
Stop-ScheduledTask -TaskName 'OwiviOsa-Backend' -TaskPath '\Auto-Start-A\'
Get-ScheduledTask -TaskName 'OwiviOsa-Backend' -TaskPath '\Auto-Start-A\' |  Format-Table TaskPath, TaskName, State
```

### 效果

<img src="http://public.file.lvshuhuai.cn/images\image-20250920130152589.png" alt="image-20250920130152589" style="zoom:50%;" />

## 启动某个任务并检查

### 命令

```powershell
Start-ScheduledTask -TaskName 'OwiviOsa-Backend' -TaskPath '\Auto-Start-A\'
Get-ScheduledTask -TaskName 'OwiviOsa-Backend' -TaskPath '\Auto-Start-A\' |  Format-Table TaskPath, TaskName, State
```

### 效果

<img src="http://public.file.lvshuhuai.cn/images\image-20250920142656721.png" alt="image-20250920142656721" style="zoom:50%;" />