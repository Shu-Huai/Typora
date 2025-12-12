# ACME 协议

## 简介

**ACME**（Automatic Certificate Management Environment）是一套用于**自动化 TLS/[[HTTPS]] 证书申请、验证、签发与续签**的开放标准协议。

它的核心目标是解决传统 [[HTTPS]] 证书管理中的几个痛点：

- 证书申请流程复杂（人工提交 CSR、人工验证）
- 证书更新容易被遗忘（导致网站 [[HTTPS]] 失效）
- 自动化部署困难（不适合大规模、云原生环境）

ACME 由 [[Let's Encrypt]] 主导提出并推动标准化，目前已成为互联网 [[HTTPS]] 证书自动化管理的事实标准，并被写入 **IETF RFC 8555**。

在 ACME 体系中：

- **证书颁发机构（CA）** 提供 ACME Server（如 Let’s Encrypt）
- **客户端程序**（如 Certbot、[[acme.sh]]）通过 ACME 协议与 CA 通信
- 全流程**无需人工介入**，即可完成证书的生命周期管理

![自动化证书管理-ACME-GlobalSign](Z:\Public\images\ACME_graphic.webp)

## ACME 的核心特性（Key Features）

### 全自动证书生命周期管理

ACME 覆盖证书的完整生命周期：

- 账户注册
- 域名所有权验证
- 证书签发
- 证书续签
- 证书吊销

用户只需部署一次客户端，后续几乎“零维护”。

### 标准化、开放协议

- ACME 是 **IETF 标准协议（RFC 8555）**
- 不绑定具体 CA 或客户端
- 理论上任何 CA / 客户端都可以实现 ACME

这避免了厂商锁定问题。

### 自动域名控制权验证（Challenge）

ACME 并不通过人工或邮件确认域名，而是通过 **Challenge（挑战）机制**自动验证：

- 你是否真正控制某个域名
- 你是否有能力在该域名下部署内容 / 修改 DNS

这是 ACME 自动化的核心。

### 短周期证书 + 高频自动续签

以 Let’s Encrypt 为例：

- 单张证书有效期 **90 天**
- 客户端通常在剩余 30 天时自动续签

好处：

- 即使私钥泄露，风险窗口也很短
- 强制推动自动化，减少“过期事故”

## ACME 的整体工作原理

ACME 的本质是：

> **客户端向 CA 证明“我控制这个域名”，CA 就给我发证书**

整体流程如下。

### ACME Account（账户）

- 客户端第一次运行时，会生成一对**账户密钥（Account Key）**
- 该密钥用于：
    - 标识你的 ACME 账户
    - 对后续请求进行签名（防止伪造）

这一步相当于“注册账号”，但完全自动。

### Order（证书申请订单）

客户端向 ACME Server 提交一个 **Order**：

- 声明要申请哪些域名的证书（如 `example.com`、`www.example.com`）
- CA 返回：
    - 需要完成哪些验证（Challenges）

### Challenge（域名验证，核心步骤）

ACME 的验证机制称为 **Challenge**，常见类型如下：

#### HTTP-01 Challenge（最常用）

验证方式：

CA 要求你在：

```
http://example.com/.well-known/acme-challenge/<token>
```

返回指定内容

证明了什么：

- 你能控制该域名的 HTTP 服务
- 你能在服务器上部署指定文件

特点：

- 简单
- 需要 **80 端口公网可访问**
- 不支持泛域名（`*.example.com`）

#### DNS-01 Challenge（泛域名必选）

验证方式：

CA 要求你在 DNS 中添加一条 TXT 记录：

```
_acme-challenge.example.com = <token>
```

证明了什么：

- 你能修改该域名的 DNS 配置
- 即你拥有域名的管理权限

特点：

- 支持 **泛域名证书**
- 可不暴露 80 / 443 端口
- 自动化依赖 DNS API（Cloudflare / 阿里云 / 腾讯云等）

#### TLS-ALPN-01（较少用）

- 通过 443 端口的特殊 TLS 握手完成验证
- 多用于没有 HTTP 服务的场景

### 验证通过，签发证书

当所有 Challenge 验证成功后：

- CA 使用其根证书 / 中间证书
- 为你的域名签发 TLS 证书
- 客户端下载：
    - `cert.pem`
    - `chain.pem`
    - `fullchain.pem`
    - `privkey.pem`

### 自动续签（Renew）

- 客户端周期性运行 `renew`
- 若证书即将过期：
    - 自动重新执行 Challenge
    - 自动签发新证书
    - 覆盖旧证书文件
- 通常会触发：
    - Web 服务器 reload（如 nginx reload）

## ACME 中的角色划分

| 角色             | 说明                                |
| ---------------- | ----------------------------------- |
| ACME Server      | CA 提供的服务端（如 Let’s Encrypt） |
| ACME Client      | 本地客户端（Certbot、acme.sh 等）   |
| Web Server / DNS | 用于完成 Challenge                  |
| CA               | 最终签发证书的机构                  |

## ACME 的常见实现与工具

### Certbot（官方推荐）

- Let’s Encrypt 官方维护
- 支持 Linux / Windows / macOS
- 支持 nginx / apache / webroot / standalone / dns
- 工程级稳定，文档完善

适合：**服务器 / 生产环境**

### [[acme.sh]]

- 纯 Shell 实现
- 非常轻量
- DNS API 支持最全
- 广泛用于路由器、NAS、Docker、嵌入式环境

适合：**高级用户 / 云原生 / 自动化脚本**

### 其他

- lego（Go 实现）
- win-acme（Windows 专用）

## ACME 的使用方式（从使用者角度）

### 常见使用模式总结

| 场景              | 推荐方式               |
| ----------------- | ---------------------- |
| 普通网站 HTTPS    | HTTP-01                |
| Nginx / Apache    | webroot / nginx plugin |
| 泛域名证书        | DNS-01                 |
| 内网 / 无 80 端口 | DNS-01                 |
| 自动化 CI/CD      | DNS-01 + API           |

## ACME 在现代架构中的位置

在现代系统中，ACME 通常作为：

- **基础设施自动化的一部分**
- **DevOps / SRE 标配组件**
- **Kubernetes / Ingress / 网关 [[HTTPS]] 的底座**

例如：

- Kubernetes + cert-manager（本质就是 ACME 客户端）
- CDN / 反向代理自动证书
- NAS / 家庭服务器 [[HTTPS]]