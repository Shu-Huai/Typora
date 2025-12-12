# Let's Encrypt

## Let's Encrypt 是什么

**Let's Encrypt** 是一个**免费、自动化、开放的证书颁发机构（CA, Certificate Authority）**，由 **ISRG（Internet Security Research Group）** 运营。

它的目标只有一个：

> **让整个互联网默认使用 [[HTTPS]]，并且“人人都用得起、用得下、用得久”。**

Let's Encrypt 通过 [[ACME 协议]]实现证书的自动申请与续签，彻底改变了传统 [[HTTPS]] 证书“昂贵 + 繁琐 + 易过期”的问题。

![使用ACME部署HTTPS证书| DARK CODE](http://public.file.lvshuhuai.cn/images\images.png)

## Let's Encrypt 解决了什么问题

在 Let's Encrypt 出现之前，[[HTTPS]] 存在几个现实问题：

1. **证书贵**
    - 商用证书动辄几百到几千元 / 年
2. **申请流程复杂**
    - 人工提交 CSR
    - 邮件 / 文件 / DNS 验证
3. **维护成本高**
    - 证书过期是常见事故
4. **自动化困难**
    - 不适合大规模网站、云环境

Let's Encrypt 的核心改变：

| 传统 CA           | Let's Encrypt     |
| ----------------- | ----------------- |
| 收费              | 免费              |
| 人工流程          | 全自动            |
| 长期证书（1~2年） | 短期证书（90 天） |
| 人工续签          | 强制自动续签      |

## Let's Encrypt 的核心特点

### 免费（Free）

- 所有证书 **永久免费**
- 没有隐藏费用
- 没有“试用期”

这是 [[HTTPS]] 普及的前提条件。

### 自动化（Automated）

Let's Encrypt **不提供网页后台人工申请证书**。

唯一方式：

> 通过 **ACME 客户端** 自动完成申请、验证、签发、续签。

这使得：

- 运维成本极低
- 非常适合 DevOps / 云原生 / 自动化部署

### 开放与标准化（Open）

- 使用 IETF 标准 [[ACME 协议]]（RFC 8555）
- 客户端、服务器、CA 解耦
- 不绑定某个特定软件或平台

### 安全导向（Short-lived Certificates）

- 证书有效期固定为 **90 天**
- 强制用户配置自动续签

优点：

- 私钥泄露风险窗口小
- 减少“多年未更新证书”的安全隐患

## 四、Let's Encrypt 的证书类型与限制

### 证书类型：仅提供 DV 证书

Let's Encrypt **只提供 DV（Domain Validation）证书**：

- 只验证“你是否控制这个域名”
- 不验证公司、组织、个人身份

❌ 不支持：

- OV（组织验证）
- EV（扩展验证）

原因很简单：

> 自动化 + 免费 ≠ 人工审核

### 支持的证书形式

- 单域名证书
     `example.com`
- 多域名证书（SAN）
     `example.com + www.example.com`
- 泛域名证书
     `*.example.com`（必须 DNS-01）

### 速率限制（Rate Limits，必须了解）

Let's Encrypt 对申请频率有限制，防止滥用：

常见限制（大致理解即可）：

- 同一主域名：
    - 每周最多签发 **50 张证书**
- 重复证书：
    - 每周最多 **5 次**
- 失败验证：
    - 连续失败会被暂时封禁

工程建议：

- **测试阶段使用 Staging 环境**
- 生产环境再切换到正式环境

## Let's Encrypt 的技术架构

### 核心组件

| 组件        | 说明                   |
| ----------- | ---------------------- |
| ISRG Root   | 根证书                 |
| 中间证书    | 用于签发最终证书       |
| ACME Server | 提供证书签发接口       |
| ACME Client | 本地工具（Certbot 等） |

### 证书信任链（Chain of Trust）

浏览器信任流程：

```
你的域名证书
   ↓
Let's Encrypt 中间证书
   ↓
ISRG Root X1
   ↓
浏览器 / 操作系统信任库
```

只要系统信任 ISRG Root，就能信任 Let's Encrypt 证书。

## Let's Encrypt 的工作原理（简化版）

1. 客户端生成密钥对
2. 向 Let's Encrypt 提交证书申请（ACME Order）
3. Let's Encrypt 要求完成域名验证（Challenge）
4. 客户端完成验证（HTTP / DNS）
5. Let's Encrypt 签发证书
6. 客户端保存证书并部署到 Web 服务器
7. 定期自动续签

**Let's Encrypt 本身只关心一件事：**

> 你是否真的控制这个域名？