# 什么是 Java 的 SPI（Service Provider Interface）机制？

## 回答重点

SPI 是 JDK 内置的一套**服务发现机制**，核心思想是接口定义在调用方，实现类放在服务提供方，运行时通过配置文件动态加载。调用方完全不用知道具体实现类是什么，只要实现方按规矩在 META-INF/services 目录下放个配置文件，`ServiceLoader` 就能自动发现并加载。

SPI 的工作流程：

1. 调用方定义服务接口，比如 java.sql.Driver
2. 服务提供方实现接口，比如 MySQL 驱动的 com.mysql.cj.jdbc.Driver
3. 服务提供方在 jar 包的 META-INF/services/ 目录下创建以接口全限定名命名的文件
4. 文件内容写实现类的全限定名，一行一个
5. 调用方通过 `ServiceLoader.load()` 加载所有实现类

![spi.drawio.png](Z:/Public/images/Q5kKCrcz_spi.drawio_mianshiya.webp)

JDBC 就是 SPI 最经典的应用场景。JDK 只定义了 java.sql.Driver 接口，MySQL、Oracle、PostgreSQL 各自实现自己的驱动。你引入哪个 jar 包，DriverManager 就自动加载哪个驱动，代码里完全不用写死驱动类名。

完整的 SPI 使用示例：

```java
// 1. 定义服务接口
public interface PaymentService {
    void pay(BigDecimal amount);
}

// 2. 实现类
public class AlipayService implements PaymentService {
    @Override
    public void pay(BigDecimal amount) {
        System.out.println("支付宝支付: " + amount);
    }
}

// 3. 配置文件 META-INF/services/com.example.PaymentService
// 内容：com.example.AlipayService

// 4. 加载使用
ServiceLoader<PaymentService> loader = ServiceLoader.load(PaymentService.class);
for (PaymentService service : loader) {
    service.pay(new BigDecimal("100"));
}
```

## 扩展知识

### SPI 的设计动机

没有 SPI 的时代，想做个可插拔的架构只能靠反射硬写 `Class.forName()`，类名还得写死在代码里或者配置文件里，换一个实现就得改代码重新编译。SPI 把这套流程标准化了，只要服务提供方按约定放好配置文件，调用方一行代码就能加载所有实现，想换实现只需要换个 jar 包。

这种设计在 JDK 里到处都是。除了 JDBC，还有 Servlet 容器发现、日志门面选择具体实现、XML 解析器选择等，都是靠 SPI 机制实现的。

![](Z:/Public/images/t4bZor21_A9UaTawb34_mianshiya.webp)

### `ServiceLoader` 底层实现

`ServiceLoader.load()` 干的活其实很简单：

1. 拼接路径 META-INF/services/ + 接口全限定名
2. 用当前线程的 `ClassLoader` 扫描 classpath 下所有匹配的文件
3. 逐行读取实现类名，通过 `Class.forName()` 加载
4. 调用无参构造器创建实例

```java
// ServiceLoader 的核心加载逻辑简化版
String fullName = "META-INF/services/" + service.getName();
Enumeration<URL> configs = loader.getResources(fullName);
while (configs.hasMoreElements()) {
    URL url = configs.nextElement();
    // 读取文件内容，每行是一个实现类全限定名
    // 通过 Class.forName() 加载并实例化
}
```

这套机制有个明显的问题：**全量加载**。假设配置文件里写了 10 个实现类，`ServiceLoader` 会把 10 个全部实例化，哪怕你只需要其中 1 个。这在实现类初始化开销大的场景下很浪费。

### JDK9 模块化后的变化

JDK9 引入模块系统后，SPI 有了新玩法。除了传统的 META-INF/services 配置文件，还可以在 module-info.java 里声明：

```java
// 服务提供方的 module-info.java
module mysql.driver {
    provides java.sql.Driver with com.mysql.cj.jdbc.Driver;
}

// 服务调用方的 module-info.java
module my.app {
    uses java.sql.Driver;
}
```

这种方式比配置文件更规范，编译期就能检查接口和实现是否匹配，不用等到运行时才发现配置写错了。

### SPI 的缺陷

1. **无法按需加载**：`ServiceLoader` 会加载所有实现类，没法指定只要哪一个
2. **没有依赖注入**：实现类只能通过无参构造器创建，想注入依赖得自己想办法
3. **扩展性有限**：没法给实现类排序、分组、加条件判断

这些痛点催生了各种增强方案。Dubbo 的 ExtensionLoader 就是典型的 SPI 增强版，支持按 `key` 获取指定实现、自动注入依赖、支持 AOP 包装。Spring 也有自己的 spring.factories 机制，思路和 SPI 一样，但功能更强大。

### Dubbo SPI 对比原生 SPI

| 特性 | JDK SPI | Dubbo SPI |
| --- | --- | --- |
| 配置位置 | `META-INF/services/` | `META-INF/dubbo/` |
| 配置格式 | 每行一个类名 | `key=全限定类名` |
| 加载方式 | 全量加载 | 按需加载，通过 `key` 获取 |
| 依赖注入 | 不支持 | 支持 setter 注入 |
| AOP 支持 | 不支持 | 支持 Wrapper 自动包装 |
| 自适应扩展 | 不支持 | 支持 `@Adaptive` 注解 |

Dubbo 的配置文件长这样，`key`-`value` 格式：

```text
# META-INF/dubbo/org.apache.dubbo.rpc.Protocol
dubbo=org.apache.dubbo.rpc.protocol.dubbo.DubboProtocol
http=org.apache.dubbo.rpc.protocol.http.HttpProtocol
```

加载时可以直接 getExtension(“dubbo”) 只拿 Dubbo 协议实现，不用把所有协议都加载一遍。

## 面试官追问

#### 提问：为什么 JDBC 4.0 之后不用写 `Class.forName()` 加载驱动了？

回答：JDBC 4.0 开始 DriverManager 在初始化时会自动调用 `ServiceLoader` 扫描 classpath 下所有 META-INF/services/java.sql.Driver 文件，找到的驱动类自动注册。以前手动写 `Class.forName("com.mysql.jdbc.Driver")` 是因为驱动类的静态代码块里会调用 `DriverManager.registerDriver()` 完成注册，现在这步自动化了。

#### 提问：Spring 的 spring.factories 和 JDK SPI 有什么区别？

回答：核心思路一样，都是通过配置文件声明实现类。区别在于 spring.factories 支持一个文件里配置多种接口的实现，格式是 interface=impl1,impl2，JDK SPI 每个接口需要单独一个文件。Spring Boot 的自动配置就是靠 spring.factories 里配置的 EnableAutoConfiguration 实现类来触发的。

#### 提问：SPI 能不能实现热插拔，运行时动态加载新实现？

回答：原生 `ServiceLoader` 做不到，它只在 load() 时扫描一次 classpath。想热插拔得自己实现类加载器，监听 jar 包变化，手动触发重新加载。OSGi 框架能做到真正的热插拔，但引入成本太高，一般项目用不上。

#### 提问：`ServiceLoader` 是线程安全的吗？

回答：`ServiceLoader` 实例本身不是线程安全的，多线程并发迭代会出问题。每次调用 `ServiceLoader.load()` 都会返回新实例，内部状态不共享。如果要在多线程环境用，要么每个线程各自 load 一份，要么把加载结果缓存到线程安全的容器里。
