# acme.sh

## 介绍

acme.sh 是一个基于 [[ACME 协议]]的轻量级证书自动化管理工具，用于申请、安装和续签 [[HTTPS]] 证书。它完全由 Shell 编写，无需 Python、Go 等运行环境，因此适用于 Linux、macOS、BSD、[[Docker]]、路由器等各种系统。acme.sh 默认支持 [[Let's Encrypt]]、ZeroSSL、Buypass 等证书机构，通过简单命令即可完成从验证域名到生成证书的全过程，并能自动处理续期，是目前最易用、最通用的 ACME 客户端之一。

## 主要特性

acme.sh 的优势在轻量化、强兼容性和高度自动化：

- **纯 Shell 实现**：无第三方依赖，不改动系统环境，安装后即可用。
- **支持多家 CA**：[[Let's Encrypt]]（默认）、ZeroSSL、Buypass 等。
- **验证方式丰富**：HTTP-01、DNS-01、TLS-ALPN 全支持。
- **强大的 DNS 自动验证**：内置数十家 DNS 服务商 API，支持自动生成 TXT 记录，特别适合申请泛域名证书。
- **自动续期机制**：会创建 cron 定时任务，每日检查证书是否需要续签。
- **便捷的证书部署**：可自动复制证书到 Nginx、Apache、HAProxy 等目录，并执行 reload 脚本。
- **安全隔离**：所有文件存放在 `~/.acme.sh`，不干扰系统 openssl 或系统证书目录。

## 基本使用方法

acme.sh 的使用逻辑非常简单，申请证书 → 安装证书 → 自动续期。

### 安装 acme.sh

```bash
curl https://get.acme.sh | sh
```

### 申请证书（HTTP 验证）

```bash
acme.sh --issue -d example.com -w /var/www/html
```

### 申请泛域名证书（DNS API 验证）

 以 Cloudflare 为例：

```bash
export CF_Token="你的TOKEN"
acme.sh --issue -d example.com -d '*.example.com' --dns dns_cf
```

### 安装证书到 Nginx

```bash
acme.sh --install-cert -d example.com \
--key-file       /etc/nginx/ssl/example.com.key \
--fullchain-file /etc/nginx/ssl/example.com.pem \
--reloadcmd     "systemctl reload nginx"
```

之后续期会自动执行，无需人工操作。

## 工作原理（ACME 协议机制）

acme.sh 本质上是对 [[ACME 协议]]的自动化实现。其核心过程如下：

- **创建账户**：与 CA 建立 ACME 账户，生成密钥。
- **创建订单**：向 CA 请求签发证书，CA 返回需要完成的挑战（Challenges）。
- **完成验证**：
    - HTTP 验证：在目标域名的 `.well-known/acme-challenge/` 下生成验证文件；
    - DNS 验证：自动或手动创建 TXT 记录；
    - TLS-ALPN 验证：在 443 上返回特殊证书。
- **CA 远程检查**：CA 访问验证文件或解析 DNS，确认域名控制权。
- **签发证书**：验证通过后，acme.sh 请求证书并保存到本地。
- **自动续期**：每日检测证书是否接近过期，接近时重复验证与签发流程。