# Java

## 基本介绍
Java 是一门面向对象（OOP）、强类型、跨平台的通用编程语言，由 Sun Microsystems 在 1995 年发布（后由 Oracle 维护与发展）。

它的核心优势是 **“一次编写，到处运行”**：Java 代码通常会先编译成 **字节码（.class）**，再由 **JVM（Java Virtual Machine）** 在不同操作系统上执行，从而实现跨平台。

Java 生态非常成熟，拥有：
- **JDK**：Java 开发工具包（包含编译器、运行时、工具链等）
- **JRE**：Java 运行环境（主要用于运行 Java 程序）
- **JVM**：Java 虚拟机（负责字节码执行、内存管理、垃圾回收等）
- 大量工业级框架与库：Spring / Spring Boot、MyBatis、Netty、Hadoop、Kafka 等

## 版本迭代
Java 版本迭代中，最关键的分界通常是 **LTS（长期支持版）**。企业生产环境常优先选择 LTS 版本（例如 8、11、17、21）。

- **Java 5**：泛型、注解、枚举、自动装箱/拆箱  
- **Java 7**：try-with-resources、switch 支持 String  
- **Java 8（里程碑/LTS）**：Lambda、Stream API、Optional、新日期时间 API（java.time）  
- **Java 9**：模块化系统（JPMS）、JShell  
- **Java 10**：局部变量类型推断 `var`  
- **Java 11（LTS）**：HttpClient（标准化）、一些 API 清理与增强  
- **Java 14**：switch 表达式（预览/逐步完善）  
- **Java 15**：文本块 Text Blocks `"""`  
- **Java 16**：Records（数据载体类）  
- **Java 17（LTS）**：sealed class（密封类）、模式匹配相关特性逐步成熟  
- **Java 21（LTS）**：虚拟线程（Virtual Threads，Project Loom）成为重要并发能力之一

建议学习路线（偏后端/工程）：
- 入门：Java 8 语法 + 集合 + IO + 异常 + 面向对象
- 进阶：并发（JUC）+ JVM（内存模型/GC）+ 反射/注解
- 工程：Spring Boot + 数据库 + 缓存 + 消息队列 + 微服务

## 数据类型
Java 是强类型语言，变量必须声明类型。数据类型分为 **基本类型（primitive）** 与 **引用类型（reference）**。

### 基本类型（8 种）
- **整数**：`byte`（8位）、`short`（16位）、`int`（32位）、`long`（64位）
- **浮点数**：`float`（32位）、`double`（64位）
- **字符**：`char`（16位，UTF-16 编码单元）
- **布尔**：`boolean`（true/false）

特点：
- 基本类型存储的是值本身
- 参与运算快，适合数值计算与底层性能敏感场景

### 引用类型
常见引用类型：
- 类：`String`、自定义 `class`
- 接口：`List`、`Map`
- 数组：`int[]`、`String[]`
- 枚举：`enum`
- 注解：`@interface`

特点：
- 引用类型变量存储的是“对象引用”（指向堆内存中的对象）
- `null` 是引用类型常见的空值状态，需要注意 NPE（NullPointerException）

### 自动装箱与拆箱
- 装箱：`int -> Integer`
- 拆箱：`Integer -> int`
常用于集合（`List<Integer>`）等泛型场景。

## 应用场景
Java 的应用非常广泛，尤其在企业级与服务端场景长期占主导地位：

### 企业后端开发
- Web 应用、REST API、管理系统
- 常用框架：Spring / Spring Boot / Spring Cloud、MyBatis、Hibernate

### 高并发与网络编程
- 即时通讯、网关、推送、RPC
- 常用技术：Netty、NIO、JUC、（新）虚拟线程

### 大数据与分布式系统生态
- Hadoop、HBase、Kafka、Flink、Spark（部分组件）
- 适用于数据处理、流式计算、消息系统等

### Android 开发（历史与现状）
- 早期 Android 主力语言之一  
- 目前 Kotlin 更主流，但 Java 仍大量存在于存量项目与生态中

### 金融、政企、传统行业核心系统
- 这些行业重视稳定性、可维护性与生态成熟度，Java 仍是长期选择



