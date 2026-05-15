# MySQL 字符集详解

MySQL 字符编码集中有两套 UTF-8 编码实现：**`utf8`** 和 **`utf8mb4`**。

如果使用 **`utf8`** 的话，存储 emoji 符号和一些比较复杂的汉字、繁体字就会出错。

为什么会这样呢？这篇文章可以从源头给你解答。

## MySQL 字符集

MySQL 支持很多种[[字符集]]的方式，比如 GB2312、GBK、BIG5、多种 Unicode 字符集（UTF-8 编码、UTF-16 编码、UCS-2 编码、UTF-32 编码等等）。

### 查看支持的字符集

你可以通过 `SHOW CHARSET` 命令来查看，支持 like 和 where 子句。

![img](http://public.file.lvshuhuai.cn/images\image-20211008164229671.png)

### 默认字符集

在 MySQL5.7 中，默认字符集是 `latin1`；在 MySQL8.0 中，默认字符集是 `utf8mb4`

### 字符集的层次级别

MySQL 中的字符集有以下的层次级别：

- `server`（MySQL 实例级别）
- `database`（库级别）
- `table`（表级别）
- `column`（字段级别）

它们的优先级可以简单的认为是从上往下依次增大，也即 `column` 的优先级会大于 `table` 等其余层次的。如指定 MySQL 实例级别字符集是 `utf8mb4`，指定某个表字符集是 `latin1`，那么这个表的所有字段如果不指定的话，编码就是 `latin1`。

#### server

不同版本的 MySQL 其 `server` 级别的字符集默认值不同，在 MySQL5.7 中，其默认值是 `latin1`；在 MySQL8.0 中，其默认值是 `utf8mb4`。

当然也可以通过在启动 `mysqld` 时指定 `--character-set-server` 来设置 `server` 级别的字符集。

```bash
mysqld
mysqld --character-set-server=utf8mb4
mysqld --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_0900_ai_ci
```

或者如果你是通过源码构建的方式启动的 MySQL，你可以在 `cmake` 命令中指定选项：

```sh
cmake . -DDEFAULT_CHARSET=latin1
或者
cmake . -DDEFAULT_CHARSET=latin1 \
  -DDEFAULT_COLLATION=latin1_german1_ci
```

此外，你也可以在运行时改变 `character_set_server` 的值，从而达到修改 `server` 级别的字符集的目的。

`server` 级别的字符集是 MySQL 服务器的全局设置，它不仅会作为创建或修改数据库时的默认字符集（如果没有指定其他字符集），还会影响到客户端和服务器之间的连接字符集，具体可以查看 [MySQL Connector/J 8.0 - 6.7 Using Character Sets and Unicode](https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-charsets.html)。

#### database

`database` 级别的字符集是我们在创建数据库和修改数据库时指定的：

```sql
CREATE DATABASE db_name
    [[DEFAULT] CHARACTER SET charset_name]
    [[DEFAULT] COLLATE collation_name]

ALTER DATABASE db_name
    [[DEFAULT] CHARACTER SET charset_name]
    [[DEFAULT] COLLATE collation_name]
```

如前面所说，如果在执行上述语句时未指定字符集，那么 MySQL 将会使用 `server` 级别的字符集。

可以通过下面的方式查看某个数据库的字符集：

```sql
USE db_name;
SELECT @@character_set_database, @@collation_database;
```

```sql
SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'db_name';
```

#### table

`table` 级别的字符集是在创建表和修改表时指定的：

```sql
CREATE TABLE tbl_name (column_list)
    [[DEFAULT] CHARACTER SET charset_name]
    [COLLATE collation_name]]

ALTER TABLE tbl_name
    [[DEFAULT] CHARACTER SET charset_name]
    [COLLATE collation_name]
```

如果在创建表和修改表时未指定字符集，那么将会使用 `database` 级别的字符集。

#### column

`column` 级别的字符集同样是在创建表和修改表时指定的，只不过它是定义在列中。下面是个例子：

```sql
CREATE TABLE t1
(
    col1 VARCHAR(5)
      CHARACTER SET latin1
      COLLATE latin1_german1_ci
);
```

如果未指定列级别的字符集，那么将会使用表级别的字符集。

### 连接字符集

前面说到了字符集的层次级别，它们是和存储相关的。而连接字符集涉及的是和 MySQL 服务器的通信。

连接字符集与下面这几个变量息息相关：

- `character_set_client`：描述了客户端发送给服务器的 SQL 语句使用的是什么字符集。
- `character_set_connection`：描述了服务器接收到 SQL 语句时使用什么字符集进行翻译。
- `character_set_results`：描述了服务器返回给客户端的结果使用的是什么字符集。

它们的值可以通过下面的 SQL 语句查询：

```sql
SELECT * FROM performance_schema.session_variables
WHERE VARIABLE_NAME IN (
'character_set_client', 'character_set_connection',
'character_set_results', 'collation_connection'
) ORDER BY VARIABLE_NAME;
```

```sql
SHOW SESSION VARIABLES LIKE 'character\_set\_%';
```

如果要想修改前面提到的几个变量的值，有以下方式：

修改配置文件

```properties
[mysql]
# 只针对MySQL客户端程序
default-character-set=utf8mb4
```

使用 SQL 语句

```sql
set names utf8mb4
# 或者一个个进行修改
# SET character_set_client = utf8mb4;
# SET character_set_results = utf8mb4;
# SET collation_connection = utf8mb4;
```

### JDBC 对连接字符集的影响

不知道你们有没有碰到过存储 emoji 表情正常，但是使用类似 Navicat 之类的软件的进行查询的时候，发现 emoji 表情变成了问号的情况。这个问题很有可能就是 JDBC 驱动引起的。

根据前面的内容，我们知道连接字符集也是会影响我们存储的数据的，而 JDBC 驱动会影响连接字符集。

`mysql-connector-java`（JDBC 驱动）主要通过这几个属性影响连接字符集：

- `characterEncoding`
- `characterSetResults`

以 `DataGrip 2023.1.2` 来说，在它配置数据源的高级对话框中，可以看到 `characterSetResults` 的默认值是 `utf8`，在使用 `mysql-connector-java 8.0.25` 时，连接字符集最后会被设置成 `utf8mb3`。那么这种情况下 emoji 表情就会被显示为问号，并且当前版本驱动还不支持把 `characterSetResults` 设置为 `utf8mb4`，不过换成 `mysql-connector-java driver 8.0.29` 却是允许的。

具体可以看一下 StackOverflow 的 [DataGrip MySQL stores emojis correctly but displays them as?](https://stackoverflow.com/questions/54815419/datagrip-mysql-stores-emojis-correctly-but-displays-them-as) 这个回答。

### UTF-8 使用

通常情况下，我们建议使用 UTF-8 作为默认的字符编码方式。

不过，这里有一个小坑。

MySQL 字符编码集中有两套 UTF-8 编码实现：

- **`utf8`**：`utf8` 编码只支持 `1-3` 个字节。在 `utf8` 编码中，中文是占 3 个字节，其他数字、英文、符号占一个字节。但 emoji 符号占 4 个字节，一些较复杂的文字、繁体字也是 4 个字节。
- **`utf8mb4`**：UTF-8 的完整实现，正版！最多支持使用 4 个字节表示字符，因此，可以用来存储 emoji 符号。

**为什么有两套 UTF-8 编码实现呢？** 原因如下：

![img](http://public.file.lvshuhuai.cn/images\image-20211008164542347.png)

因此，如果你需要存储 `emoji` 类型的数据或者一些比较复杂的文字、繁体字到 MySQL 数据库的话，数据库的编码一定要指定为 `utf8mb4` 而不是 `utf8`，要不然存储的时候就会报错了。

演示一下吧！（环境：MySQL 5.7+）

建表语句如下，我们指定数据库 CHARSET 为 `utf8`。

```sql
CREATE TABLE `user` (
  `id` varchar(66) CHARACTER SET utf8mb3 NOT NULL,
  `name` varchar(33) CHARACTER SET utf8mb3 NOT NULL,
  `phone` varchar(33) CHARACTER SET utf8mb3 DEFAULT NULL,
  `password` varchar(100) CHARACTER SET utf8mb3 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

当我们执行下面的 insert 语句插入数据到数据库时，果然报错！

```sql
INSERT INTO `user` (`id`, `name`, `phone`, `password`)
VALUES
 ('A00003', 'guide哥😘😘😘', '181631312312', '123456');

```

报错信息如下：

```plain
Incorrect string value: '\xF0\x9F\x98\x98\xF0\x9F...' for column 'name' at row 1
```
