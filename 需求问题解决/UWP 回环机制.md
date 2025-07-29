# UWP 回环机制

## 什么是 UWP？

- **UWP（Universal Windows Platform）** 是微软在 Windows 10/11（含各种 Windows 设备）上提供的统一应用平台，支持使用 C#, C++, VB.NET 或 JavaScript 编写跨设备应用。
- UWP 应用运行在 **App Container** 沙箱环境中，为系统安全提供隔离。

![開發適用於通用Windows 平台(UWP) 的應用程式- Visual Studio (Windows) | Microsoft Learn](http://public.file.lvshuhuai.cn/images\uwp_coreextensions.png)

## 为什么存在本地回环限制？

- UWP 应用默认**禁止访问本机回环地址（127.0.0.1 或 localhost）**，这是为加强安全与网络隔离所设的默认策略。
- 如果 UWP 应用尝试访问本地代理服务器或本机 HTTP 服务，会因隔离策略而被阻止。

## 为什么要解除该限制？

以下情况通常需要解除回环限制：

- **开发调试过程中**：需要 UWP 应用访问本地调试服务或代理。
- **使用本地代理翻墙**：如 Fiddler、V2rayN、Clash 等，需要 UWP 应用流量走本地代理才能联网。
- **第三方认证流程**：如 Okta Verify 的 UWP 客户端通过本地回环通信实现身份验证。

<img src="http://public.file.lvshuhuai.cn/images\image-20250728140432286.png" alt="image-20250728140432286" style="zoom:50%;" />

## 如何解除 UWP 回环限制？

### 方法一：使用 `CheckNetIsolation.exe`

微软官方命令行工具，用于给指定应用添加或移除回环豁免：

```powershell
# 列出已有豁免
CheckNetIsolation.exe LoopbackExempt -s

# 添加豁免：按应用包家族名
CheckNetIsolation.exe LoopbackExempt -a -n=<PackageFamilyName>

# 添加豁免：按 SID
CheckNetIsolation.exe LoopbackExempt -a -p=<AppContainerSID>

# 删除豁免
CheckNetIsolation.exe LoopbackExempt -d -n=<PackageFamilyName>

# 清除所有豁免（重置状态）
CheckNetIsolation.exe LoopbackExempt -c
```

- 包家族名（PackageFamilyName）可在 `Package.appxmanifest` 或 PowerShell 的 `Get-AppxPackage` 输出中找到。
- 全局清除（`-c`）有助于修复豁免表错误或失效。

### 方法二：使用图形化工具

- **Fiddler 的 Enable Loopback Utility** 插件，或
- 开源项目 **Loopback Exemption Manager**（Richasy 维护的 Windows 11 版本）提供可视化操作界面，只需勾选应用并保存即可批量设置。

<img src="http://public.file.lvshuhuai.cn/images\image-20250728140506907.png" alt="image-20250728140506907" style="zoom:50%;" />

### 方法三：脚本自动化批量设置

利用注册表或 PowerShell：

- 注册表路径：
     `HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppContainer\Mappings`，可获取所有应用 SID。
- 示例 PowerShell（为所有用户应用批量添加豁免）：

```powershell
Get-AppxPackage -AllUsers |
  ForEach-Object { CheckNetIsolation.exe LoopbackExempt -a -n=$_.PackageFamilyName }
```

或结合 Registry：

```powershell
FOR /F "tokens=11 delims=\" %p IN (
  'REG QUERY "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppContainer\Mappings"'
) DO CheckNetIsolation.exe LoopbackExempt -a -p=%p
```

## 使用注意事项与常见问题

- **Visual Studio 调试设置**：Visual Studio 默认会自动为调试部署的 UWP 应用添加回环豁免，但发布前需取消，否则不符合商店提交要求。
- **“Allow Local Network Loopback” 设置**：仅调试时部分生效，并不等同于完全解除豁免。
- **豁免列表可能损坏**：若发现某个应用豁免失效，建议使用 `-c` 清除后重新逐个添加。
- **解除豁免后可能影响商店访问**：部分用户报告豁免后无法正常从 Microsoft Store 下载新应用，提示许可错误或连接问题（如 0x80072EFD）。