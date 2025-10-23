# 在 DDNS-GO 中解决 IPv6 重连后无法更新的问题

## 需求和前提

### 环境

- 运营商：移动宽带（前缀会在断线重连后变化 /64）
- 系统：Windows（网卡别名示例为“以太网 4”）
- DDNS 客户端：DDNS-GO（或同类仅支持“一行命令，读取 stdout 第一行 IPv6”的工具）
- 目标：为**局域网内指定主机**上报一个**稳定的 IPv6**——IPv6 = **当前生效的 /64 前缀** + **该主机固定 IID（后 64 位）**

### 需求描述

<img src="Z:\Public\images\image-20251021145621022.png" alt="image-20251021145621022" style="zoom:50%;" />

- 断线重连时，Windows 网卡可能同时保留“旧前缀+新前缀”两条**全局 IPv6**；
- DDNS-GO 若按“列表第一个/第 n 个地址”上报，容易把**旧前缀**上报，导致解析失效；
- 必须使用“**前缀 + 固定后缀(IID)**”的方式生成**目标主机**的地址（DDNS-GO 运行在哪台机器都行）；
- DDNS-GO 只接受**一行命令**，并取**标准输出的第一个匹配结果**作为上报 IP。

### 当前方案的问题

- 直接从网卡取“第 1 个 IPv6”不可靠：显示顺序不稳定；
- 仅按路由/前缀“首条匹配”也不稳：多条 /64 并存时，未必命中新前缀；
- 早先的拼接实现存在十六进制段格式化问题（未做 4 位零填充或高低字节拼接不当），会得到诸如 `9:1e:c1:b0:...` 这类错误格式。

## 解决方案

### 思路

在一行 PowerShell 中完成三步

1. 定位**目标网卡**上**处于 Preferred 状态**且 **/64** 的**全局 IPv6**；
2. 按 **PreferredLifetime / ValidLifetime** 由大到小排序，取**最“新/首选”的那条**，抽取其**前 64 位前缀**；
3. 将该前缀与**固定 IID（后 64 位）**拼接，输出一个最终 IPv6 供 DDNS-GO 使用。

> 其中固定 IID（后 64 位）为**目标主机**的稳定后缀（如其 EUI-64 或你指定的 `92e2:baff:fe8b:dea4`）。

### 一行命令（按网卡别名）

```powershell
$IID='92e2:baff:fe8b:dea4';$IF='以太网 4';(Get-NetIPAddress -InterfaceAlias $IF -AddressFamily IPv6 | ?{ $_.PrefixLength -eq 64 -and $_.IPAddress -like '2409:*' -and $_.AddressState -eq 'Preferred' } | Sort-Object @{Expression='PreferredLifetime';Descending=$true}, @{Expression='ValidLifetime';Descending=$true} | Select-Object -First 1 | %{$b=[Net.IPAddress]::Parse($_.IPAddress).GetAddressBytes();$h=for($i=0;$i -lt 8;$i++){ '{0:x4}' -f ([uint16]($b[$i*2]*256 + $b[$i*2+1]))};($h[0..3]-join ':')+':'+$IID})
```

### 关键点说明

- `-like '2409:*'`：根据你运营商段精确过滤（如需更宽可用 `'240*'`）；
- `AddressState -eq 'Preferred'`：避免选到 Deprecated/Valid 但非首选的旧地址；
- `Sort-Object PreferredLifetime, ValidLifetime`：更可能命中新下发前缀；
- 通过 `GetAddressBytes()` + `'{0:x4}'` **严格输出 8 段 4位十六进制**，再取前 4 段为 /64 前缀，最后拼接 `$IID`；
- 输出只有**一个** IPv6，满足 DDNS-GO“取 stdout 第一行”的约束。

> 若默认出网口（接口）可能切换，也可改为“自动按默认路由(::/0)选接口”的版本；本次已验证按网卡别名的版本可用，故不再赘述。

## 结果

<img src="Z:\Public\images\image-20251021150244006.png" alt="image-20251021150244006" style="zoom:50%;" />

- 将上述一行命令填入 DDNS-GO 的“通过命令获取 IP（仅用 stdout 第一匹配）”后，**每次断线重连**都能稳定生成：

    ```
    <当前生效的2409:* /64 前缀> : 92e2:baff:fe8b:dea4
    ```

- 由于前缀来自**最新/首选/Preferred** 的全局地址，DDNS 上报始终与**当前可达的公网前缀**一致，**不再受“网卡同时存在多条全局 IPv6”与显示顺序的影响**；

- 实测输出示例（形如）：

    ```
    2409:8a1e:35c1:b8d0:92e2:baff:fe8b:dea4
    ```

- DDNS 解析更新日志提示“更新成功”，外网解析连通性恢复稳定。

> 如需进一步加固（可选）：可在计划任务中定期将旧前缀地址标记为 `SkipAsSource=1`，减少系统源地址选择歧义，但对本次“前缀+IID 拼接”的方案不是必须条件。