# OTP 配置与协议

本文说明 OTP 配置的字段语义、TOTP/HOTP 算法、URI 导入和二维码解析。

本文不讨论 secret 的加解密，见 [[模块/密码库/密码库与密钥|密码库]]。数据表结构见 [[数据库/数据模型|数据模型]]。

源码范围：前端 `src/modules/otp/`（totp.ts、hotp.ts、base32.ts、otpUriParser.ts）；后端 `service/impl/OtpEntryServiceImpl.java`。

## 协议参数与验证码计算

### 协议参数

一条 OTP 配置的协议字段：

| 字段 | TOTP 默认 | HOTP 默认 | 校验 |
|---|---|---|---|
| otpType | TOTP | HOTP | 两值白名单 |
| algorithm | SHA1 | SHA1 | SHA1/SHA256/SHA512 |
| digits | 6 | 6 | 6 或 8 |
| period | 30 | — | TOTP 必须 >0 |
| counter | — | 0 | HOTP 必须 ≥0 |

counter 是明文存储（不是秘密），HOTP 每用一次递增一次：前端点"生成下一次"调 PATCH counter，后端 SQL 里带 `otp_type='HOTP'` 条件，TOTP 条目传 counter 不生效。

### 验证码计算

![](Z:\Public\images\key-pulse-otp-flow.svg)

实现是 RFC 4226（HOTP）和 RFC 6238（TOTP）标准算法，代码在 `modules/otp/`：

```
HOTP:  HMAC-SHA{1|256|512}(secret, 8字节大端counter) → 动态截断 → 十进制 digits 位
TOTP:  counter = floor(unixSeconds / period) → 复用 HOTP 计算
```

前端每 1 秒重算全部条目并更新 codes 缓存，倒计时 = period - (now % period)。测试里有 RFC 标准向量验证正确性。

## URI 导入与二维码

### URI 导入

`otpUriParser.ts` 解析 `otpauth://` 链接：

```
otpauth://totp/Example:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Example&algorithm=SHA1&digits=6&period=30
```

解析出：类型、issuer、accountName（label 冒号前后拆分）、secret（Base32）、各协议参数。缺省参数用默认值（SHA1/6 位/30 秒/0）。secret 不是标准 Base32 时会自动补 padding 重试。

### 二维码导入

OtpEntryDrawer 的二维码 tab 三种来源：

- 文件上传：@zxing/browser decodeFromImageUrl
- 剪贴板：nativeBridge.pasteImageFromClipboard（原生壳能力，CustomEvent 回传 dataURL），Web 端降级
- 摄像头：window.keypulseNative.startCamera（原生壳能力），Web 端不可用

扫描结果是一个 otpauth:// URI，再走 URI 解析。二维码解析失败（qrError）和 URI 解析失败（uriError）分别提示。

## 后端存储与隔离

后端不解析 otpauth URI、不识别 QR，只接收解析后的结构化字段。validate 规则：

- issuer/accountName/label/encryptedSecret/secretSalt/secretIv/encryptionAlgorithm/kdfAlgorithm/kdfParams 全部非空
- 协议参数白名单校验（上表）
- 所有 SQL 带 user_id 隔离，查他人的条目按 404 返回

列表排序：pinned DESC → issuer ASC → account_name ASC → id ASC。

## 已知边界

- counter 无上限约束：前端误操作可以把 HOTP counter 推到很大，后端只拒绝负数
- secret 的 Base32 校验在前端做，后端不校验（后端只见密文）
- period 没有上限：传 10 万秒的 TOTP 也能存，显示上倒计时巨大
- 排序不可自定义，sortOrder 字段后端有但前端不暴露
- URI 导入不校验 secret 与 issuer/label 的一致性，任何能解析的 URI 都接受
