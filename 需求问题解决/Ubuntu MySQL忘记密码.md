# Ubuntu MySQL 忘记密码

## 问题描述

我在 `b2080` 上部署项目时，发现服务器中已有 MySQL 服务，但没人知道 `root` 用户的密码。

## 解决方案——重置密码

### 1. 停止MySQL服务

```bash
sudo systemctl stop mysql
```

### 2. 以跳过权限检查模式启动MySQL

```bash
sudo mysqld_safe --skip-grant-tables --skip-networking &
```

- `--skip-grant-tables`: 跳过权限验证。
- `--skip-networking`: 禁用远程连接，增强安全性。

### 3. 无密码登录MySQL

```bash
mysql -u root
```

### 4. 更新root密码

我的版本是 5.7。

```sql
USE mysql;
UPDATE user SET authentication_string=PASSWORD('你的新密码') WHERE User='root';
FLUSH PRIVILEGES;
```

### 5. 退出并重启MySQL

```sql
EXIT;
```

```bash
sudo killall mysqld_safe
sudo systemctl start mysql
```

