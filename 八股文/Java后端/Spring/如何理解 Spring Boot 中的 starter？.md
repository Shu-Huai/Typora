# 如何理解 Spring Boot 中的 starter？

## 回答重点

**Starter 本质上是一个依赖打包机制**，把某个功能需要的所有依赖和默认配置捆在一起，引入一个 starter 就能开箱即用。

比如要用 Redis，以前得自己引 jedis 或 lettuce 客户端、spring-data-redis、连接池等一堆依赖，版本还得对得上。现在直接引 spring-boot-starter-data-redis，这些全给你配好了，application.yml 里写个 host 和 port 就能用。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```yaml
spring:
  redis:
    host: localhost
    port: 6379
```

注意：在 Spring Boot 3.`x` 中，配置前缀已改为 `spring.data.redis.*`

就这么几行，`RedisTemplate` 直接注入就能用，连接池、序列化方式都是默认配置好的。

![](Z:/Public/images/dofCiaxj_D1ewDvSbQX_mianshiya.webp)

## 扩展知识

### 自定义 Starter 的完整流程

实际项目中经常需要把公共组件封装成 starter，比如统一的日志、监控、鉴权模块。做一个 starter 分四步。

第一步，创建 Maven 项目，pom.xml 里引入 spring-boot-starter 作为基础依赖：

```xml
<project ...>
    <groupId>com.example</groupId>
    <artifactId>my-starter</artifactId>
    <version>1.0.0</version>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>
```

第二步，定义配置属性类，用 @ConfigurationProperties 绑定配置前缀：

```java
@ConfigurationProperties(prefix = "example.xxx")
@Data
public class XxxProperties {
    private String host;
    private Integer port;
}
```

第三步，写自动配置类，用 @ConditionalOnMissingBean 这类条件注解控制 Bean 的创建：

```java
@Configuration
@EnableConfigurationProperties(XxxProperties.class)
public class MyAutoConfiguration {

    @Autowired
    private XxxProperties properties;
    
    @Bean
    @ConditionalOnMissingBean
    public MyService myService() {
        MyService service = new MyService();
        service.setHost(properties.getHost());
        service.setPort(properties.getPort());
        return service;
    }
}
```

@ConditionalOnMissingBean 的意思是，容器里没有这个 Bean 才创建。用户想自定义实现，直接声明一个同类型的 Bean 就能覆盖默认的。

第四步，注册自动配置类。SpringBoot 2.`x` 是在 META-INF/spring.factories 里写：

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.example.starter.MyAutoConfiguration
```

打包发布后，其他项目引入这个依赖就能直接用了。

### 看看真实的 Starter 长什么样（MyBatisPlus）

拿 MyBatisPlus 的 starter 举例，结构和我们上面说的一模一样：

![image.png](Z:/Public/images/uMF1BX4O_image_mianshiya.webp)

![image.png](Z:/Public/images/FrF7VliT_image_mianshiya.webp)

![image.png](Z:/Public/images/D9Am3711_image_mianshiya.webp)

![image.png](Z:/Public/images/DKBhVwwa_image_mianshiya.webp)

### SpringBoot 3.`x` 的重大变化

升级到 SpringBoot 3.`x` 会发现 spring.factories 不生效了，因为官方把它移除了：

![image.png](Z:/Public/images/8P7Y24Xi_image_mianshiya.webp)

spring.factories 从 2.7 开始标记废弃，3.0 正式移除。这导致很多老版本的第三方 starter 在 SpringBoot 3 上直接失效。

新的注册方式是创建 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 文件，每行写一个自动配置类的全限定名：

```text
com.example.starter.MyAutoConfiguration
```

详情可看[官方 Spring-Boot-3.0-Migration-Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)

SpringBoot 3.`x` 迁移成本不低，因为它强制要求 JDK 17，而且 Jakarta EE 命名空间从 javax 改成了 jakarta，很多老代码都得改。

### 官方 Starter 和第三方 Starter 的命名规范

官方的 starter 都是 spring-boot-starter-xxx 这种格式，比如 spring-boot-starter-web、spring-boot-starter-data-jpa。

第三方的按规范应该是 xxx-spring-boot-starter，比如 mybatis-spring-boot-starter、druid-spring-boot-starter。这样一眼就能区分是官方的还是社区的。

## 面试官追问

#### 提问：@ConditionalOnClass 和 @ConditionalOnMissingBean 有什么区别？分别用在什么场景？

回答：@ConditionalOnClass 是判断类路径下有没有某个类，通常用来检测依赖有没有引入。比如 RedisAutoConfiguration 上标了 @ConditionalOnClass(RedisOperations.class)，只有引了 spring-data-redis 才会生效。@ConditionalOnMissingBean 是判断容器里有没有某个 Bean，用来实现“用户没自定义就用默认的”这种逻辑。两个经常配合用，先判断依赖存在，再判断用户有没有自定义。

#### 提问：自动配置类的加载顺序能控制吗？比如我的配置类要在某个官方配置之后执行？

回答：可以用 @AutoConfigureAfter 和 @AutoConfigureBefore 注解。比如 @AutoConfigureAfter(DataSourceAutoConfiguration.class) 就是让你的配置类在数据源配置之后加载。还有 @AutoConfigureOrder 可以指定数字优先级，数字越小越先加载。实际上 SpringBoot 内部的自动配置类之间也是靠这些注解来保证顺序的。

#### 提问：starter 里的默认配置怎么让用户能覆盖？

回答：两个层面。属性层面，用 @ConfigurationProperties 绑定的属性，用户在 application.yml 里写同样的 `key` 就能覆盖默认值。Bean 层面，用 @ConditionalOnMissingBean，用户自己声明一个同类型的 Bean，自动配置就不会创建默认的了。所以写 starter 的时候，所有 @Bean 方法上都应该加 @ConditionalOnMissingBean，给用户留扩展口子。
