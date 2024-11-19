# 03 Spring Boot 后端工程搭建（2）

## Spring Boot 通过 MDC 实现日志跟踪

![img](http://public.file.lvshuhuai.cn/图床\169167740895427.jpeg)

本小节中，我们将在 Spring Boot 中通过 MDC 实现日志追踪功能。

### 什么是 MDC ? 为什么需要它？

MDC（Mapped Diagnostic Context）是 SLF4J 和 log4j 等日志框架提供的一种方案，它允许开发者将一些特定的数据（如用户ID、请求ID等）存储到当前线程的上下文中，使得这些数据可以在日志消息中使用。这对于跟踪多线程或高并发应用中的单个请求非常有用。

**在高并发环境中，由于多个请求可能同时处理，日志消息可能会交错在一起**。使用MDC，我们可以*为每个请求分配一个唯一的标识，并将该标识添加到每条日志消息中，从而方便地区分和跟踪每个请求的日志*。

### 开始动手

#### 日志切面中设置 MDC 值

编辑 `ApiOperationLogAspect` 日志切面类，在 `doAround()` 方法中处理请求开始的时候, 将请求的跟踪标识放入MDC 中：

```less
// traceId 表示跟踪 ID， 值这里直接用的 UUID
MDC.put("traceId", UUID.randomUUID().toString());
```

#### 配置日志框架

在 `logback-weblog.xml` 配置文件中，可以使用 `%X` 来引用MDC中的值。例如，要引用上述的 `traceId`，你可以这样配置：

```perl
[TraceId: %X{traceId}] %d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n
```

完整内容如下 ：

> ⚠️ 注意，这里日志输出路径改成了 Windows 系统路径，目的是为了等下测试日志是否能够正常输出 `traceId` 。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration >
    <jmxConfigurator/>
    <include resource="org/springframework/boot/logging/logback/defaults.xml" />

    <!-- 应用名称 -->
    <property scope="context" name="appName" value="weblog" />
    <!-- 自定义日志输出路径，以及日志名称前缀 -->
    <property name="LOG_FILE" value="D:\\IDEA_Projects\\weblog\\logs\\${appName}.%d{yyyy-MM-dd}"/>
    <property name="FILE_LOG_PATTERN" value="[TraceId: %X{traceId}] %d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n"/>
    <!--<property name="CONSOLE_LOG_PATTERN" value="${FILE_LOG_PATTERN}"/>-->

    <!-- 按照每天生成日志文件 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
        <!-- 日志文件输出的文件名 -->
        <FileNamePattern>${LOG_FILE}-%i.log</FileNamePattern>
        <!-- 日志文件保留天数 -->
        <MaxHistory>30</MaxHistory>
        <!-- 日志文件最大的大小 -->
        <TimeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
        <maxFileSize>10MB</maxFileSize>
        </TimeBasedFileNamingAndTriggeringPolicy>
        </rollingPolicy>
        <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
        <!-- 格式化输出：%d 表示日期，%thread 表示线程名，%-5level：级别从左显示 5 个字符宽度 %errorMessage：日志消息，%n 是换行符-->
        <pattern>${FILE_LOG_PATTERN}</pattern>
        </encoder>
    </appender>

    <!-- dev 环境（仅输出到控制台） -->
    <springProfile name="dev">
        <include resource="org/springframework/boot/logging/logback/console-appender.xml" />
        <root level="INFO">
            <appender-ref ref="CONSOLE" />
        </root>
    </springProfile>

    <!-- prod 环境（仅输出到文件中） -->
    <springProfile name="prod">
        <include resource="org/springframework/boot/logging/logback/console-appender.xml" />
        <root level="INFO">
            <appender-ref ref="FILE" />
        </root>
    </springProfile>
</configuration>
```

#### 清除 MDC 值

在请求结束时，为了避免污染其他请求，还需要清除 MDC 中的值：

```scss
MDC.clear();
```

#### 与 AOP 切面结合

所以，`ApiOperationLogAspect` 切面类中需添加的代码如下：

```java
 /**
     * 环绕
     * @param joinPoint
     * @return
     * @throws Throwable
     */
    @Around("apiOperationLog()")
    public Object doAround(ProceedingJoinPoint joinPoint) throws Throwable {
        try {
            MDC.put("traceId", UUID.randomUUID().toString());

            ... 省略
        } finally {
            MDC.clear();
        }
    }
```

### 测试看看

我们将 `application.yml` 中的 `profile` 改为 `prod` 环境，来测试一波日志文件是否含有 `traceId`。 重启项目，再次请求 `/test` 接口，然后查看日志：

![img](http://public.file.lvshuhuai.cn/图床\169167638168455.jpeg)

可以看到请求日志中正确打印了 `traceId` ，有了它，就可以在查询日志的时候通过 `traceId` 来过滤出同一个请求的所有日志了。

### 本小节对应源码

https://t.zsxq.com/11Q9JlpMF

### 结语

本小节中，我们在 Spring Boot 中通过 MDC 添加 `traceId` 跟踪 ID, 它可以显著提高高并发应用的日志可读性和可追踪性。但是，你需要确保正确地设置和清除 MDC 值，以避免意外地污染日志消息。

## Spring Boot 实现优雅的参数校验

![img](http://public.file.lvshuhuai.cn/图床\169174494690971.jpeg)

### 前言

在日常的 Web 开发中，请求参数校验是一个非常基础且重要的环节。通过校验，我们可以确保每次接口请求中，入参的数据是有效、安全且合规的，避免数据库中出现脏数据。

### 手动校验参数

原始的手动校验参数代码如下：

```less
	@PostMapping("/test")
    @ApiOperationLog(description = "测试接口")
    public ResponseEntity<String> test(@RequestBody User user) {
        // 参数校验
        if (user.getName() == null || user.getName().trim().isEmpty()) {
            return ResponseEntity.badRequest().body("姓名不能为空");
        }

        if (user.getAge() < 18 || user.getAge() > 100) {
            return ResponseEntity.badRequest().body("年龄必须在18到100之间");
        }

        if (user.getEmail() == null || !isValidEmail(user.getEmail())) {
            return ResponseEntity.badRequest().body("邮箱格式不正确");
        }

        // 更多的校验...

        // 返参
        return ResponseEntity.ok("参数没有任何问题");
    }
```

这还是只有 3 个字段需要校验的情况，如果更多呢？一堆的 `if else` 是不是又臭又长！有没有什么优雅的解决方案呢？

### JSR 380 参数校验注解

Spring Boot 提供了简洁的方法，让我们能够利用 Java 校验 API (JSR 380) 中定义的注解进行参数校验。JSR 380，也被称为 Bean Validation 2.0，是 Java Bean 验证规范的一个版本。该规范定义了一系列注解，用于验证 Java Bean 对象的属性，确保它们满足某些条件或限制。

以下是 JSR 380 中提供的主要验证注解及其描述：

1. **@NotNull**: 验证对象值不应为 null。
2. **@AssertTrue**: 验证布尔值是否为 true。
3. **@AssertFalse**: 验证布尔值是否为 false。
4. **@Min(value)**: 验证数字是否不小于指定的最小值。
5. **@Max(value)**: 验证数字是否不大于指定的最大值。
6. **@DecimalMin(value)**: 验证数字值（可以是浮点数）是否不小于指定的最小值。
7. **@DecimalMax(value)**: 验证数字值（可以是浮点数）是否不大于指定的最大值。
8. **@Positive**: 验证数字值是否为正数。
9. **@PositiveOrZero**: 验证数字值是否为正数或零。
10. **@Negative**: 验证数字值是否为负数。
11. **@NegativeOrZero**: 验证数字值是否为负数或零。
12. **@Size(min, max)**: 验证元素（如字符串、集合或数组）的大小是否在给定的最小值和最大值之间。
13. **@Digits(integer, fraction)**: 验证数字是否在指定的位数范围内。例如，可以验证一个数字是否有两位整数和三位小数。
14. **@Past**: 验证日期或时间是否在当前时间之前。
15. **@PastOrPresent**: 验证日期或时间是否在当前时间或之前。
16. **@Future**: 验证日期或时间是否在当前时间之后。
17. **@FutureOrPresent**: 验证日期或时间是否在当前时间或之后。
18. **@Pattern(regexp)**: 验证字符串是否与给定的正则表达式匹配。
19. **@NotEmpty**: 验证元素（如字符串、集合、Map 或数组）不为 null，并且其大小/长度大于0。
20. **@NotBlank**: 验证字符串不为 null，且至少包含一个非空白字符。
21. **@Email**: 验证字符串是否符合有效的电子邮件格式。

除了上述的标准注解，JSR 380 也支持开发者定义和使用自己的自定义验证注解。此外，这个规范还提供了一系列的APIs和工具，用于执行验证和处理验证结果。大部分现代Java框架（如 Spring 和 Jakarta EE）都与 JSR 380 兼容，并支持其验证功能。

### 开始动手

本小节中，小哈将介绍如何在 `weblog` 项目中通过 JSR 380 实现参数校验功能。

#### 引入依赖

首先，我们需要在 `weblog-web` 模块中的 `pom.xml` 文件添加参数校验依赖：

```php-template
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

#### 实体类参数校验

[上小节](https://www.quanxiaoha.com/column/10009.html#新增测试接口) 中，为了测试日志切面，我们已经新增了一个用户 `User` 实体类，这次再多添加两个字段，用于测试参数校验，代码如下：

```less
package com.quanxiaoha.weblog.web.model;

import lombok.Data;

import javax.validation.constraints.*;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-10 10:35
 * @description: TODO
 **/
@Data
public class User {
    // 用户名
    @NotBlank(message = "用户名不能为空") // 注解确保用户名不为空
    private String username;
    // 性别
    @NotNull(message = "性别不能为空") // 注解确保性别不为空
    private Integer sex;

    // 年龄
    @NotNull(message = "年龄不能为空")
    @Min(value = 18, message = "年龄必须大于或等于 18")  // 注解确保年龄大于等于 18
    @Max(value = 100, message = "年龄必须小于或等于 100")  // 注解确保年龄小于等于 100
    private Integer age;

    // 邮箱
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")  // 注解确保邮箱格式正确
    private String email;
}
```

上述代码说明：

- `@NotBlank`: 此注解确保字符串不为空并且不能为空字符串，且去掉前后空格后的长度必须大于 0。它常用于字符串字段验证。`message` 属性用于指定提示信息；
- `@NotNull`: 此注解确保整数类型不能为 `null`；
- `@Min` 和 `@Max`: 这两个注解用于验证数字值是否在指定的范围内。例如，在上面的示例中，我们想要确保 `age` 的值在 18 到 100 之间；
- `@Email`: 此注解用于验证字符串值是否是有效的电子邮件地址格式。

#### Controller 参数校验

针对每个字段的校验注解添加完成后，还需要在 `controller` 层进行捕获，并将错误信息返回。编辑 `TestController` 类，代码如下：

```kotlin
@RestController
@Slf4j
public class TestController {

    @PostMapping("/test")
    @ApiOperationLog(description = "测试接口")
        public ResponseEntity<String> test(@RequestBody @Validated User user, BindingResult bindingResult) {
        // 是否存在校验错误
        if (bindingResult.hasErrors()) {
            // 获取校验不通过字段的提示信息
            String errorMsg = bindingResult.getFieldErrors()
                    .stream()
                    .map(FieldError::getDefaultMessage)
                    .collect(Collectors.joining(", "));

            return ResponseEntity.badRequest().body(errorMsg);
        }

        // 返参
        return ResponseEntity.ok("参数没有任何问题");
    }

}
```

解释一下上面代码中的关键部分：

- `@Validated`: 告诉 Spring 需要对 `User` 对象执行校验;
- `BindingResult` : 验证的结果对象，其中包含所有验证错误信息；

#### 测试一下效果

使用 Postman 工具请求 `/test` 接口测试一下，请求入参如下：

##### 入参正确的情况

入参：

```perl
{
    "username": "犬小哈",
    "sex": 1,
    "age": 32,
    "email": "123124@qq.com"
}
```

![img](http://public.file.lvshuhuai.cn/图床\169165648162349.jpeg)

![img](http://public.file.lvshuhuai.cn/图床\169174350542525.jpeg)

##### 入参不正确的情况

入参数据：

```json
{
    "username": "",
    "sex": null,
    "age": 120,
    "email": "123124qq.com"
}
```

![img](http://public.file.lvshuhuai.cn/图床\169174368662151.jpeg)

可以看到，在字段不符合校验规则的情况下，正确返回了每个字段的提示信息。参数校验功能正常执行。

### 还不够优雅？

虽然实现了以添加注解的方式搞定了参数校验功能，但是 `controller` 层的代码也太不优雅美观了：

![img](http://public.file.lvshuhuai.cn/图床\169174391942266.jpeg)

总不能每次定义一个接口，都要写上面这么一坨吧！*别急，后面小节中，我们将通过自定义响应工具类 + 全局异常管理来干掉这一坨丑陋的代码，无需再手动返回。*

### 本小节对应源码

https://t.zsxq.com/11DK09Zwm

### 结语

本小节中，我们在 `weblog` 项目中搞定了 1.0 版本的参数校验功能，但是它还不完美，后面小节中，我们继续优化它，实现企业级的终极解决方案。

## Spring Boot 自定义响应工具类

![img](http://public.file.lvshuhuai.cn/图床\169175763177015.jpeg)

在开发 RESTful API 时，为了保持响应结构的一致性，公司内部一般都有标准化的响应格式。这不仅可以提高代码的可维护性，还可以帮助前端开发者更容易地处理和解析 API 响应。在本小节中，小哈将展示如何在 Spring Boot 中创建一个自定义响应参数工具类，然后使用它进行返参给前端。

### 设计响应模型

在前后端分离项目中，前端和后端一般都是以 JSON 格式进行数据交互。而在数据格式设计上，每个公司基本大同小异，小哈习惯这样设计，如下：

#### 接口执行成功返参格式

```json
{
	"success": true,
	"data": null
}
```

- `success` : 是否请求成功，布尔型，`true` 表示接口请求成功，`false` 表示执行失败；
- `data` : 服务端响应数据，对象类型；

#### 接口执行异常返参格式

```json
{
	"success": false,
	"errorCode": "10000"
	"message": "用户名不能为空"
}
```

- `message`: 服务端响应消息，字符串类型，当 `success` 为 `false` 时，此字段才会不为空，用于后端返回失败的原因，方便前端弹出提示消息；
- `errorCode`: 异常码，字符串类型，微服务中用的比较多，通常格式为服务的唯一标识 + 异常码进行返回，如 `QMS100000`, 这样做的好处是，当发生问题时，用于快速锁定是链路上的哪个服务出现了问题。因为本项目是单体项目，其实用处不大，小伙伴们知道有这样的规范就行;

### 创建响应参数工具类

确定了格式以后，我们开始着手写响应参数工具类。在 `weblog-module-common` 模块下新建 `utils` 包，然后创建 `Response` 工具类：

![img](http://public.file.lvshuhuai.cn/图床\169175486514738.jpeg)

代码如下：

```typescript
package com.quanxiaoha.weblog.common.utils;

import lombok.Data;

import java.io.Serializable;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-11 19:50
 * @description: 响应参数工具类
 **/
@Data
public class Response<T> implements Serializable {

    // 是否成功，默认为 true
    private boolean success = true;
    // 响应消息
    private String message;
    // 异常码
    private String errorCode;
    // 响应数据
    private T data;

    // =================================== 成功响应 ===================================
    public static <T> Response<T> success() {
        Response<T> response = new Response<>();
        return response;
    }

    public static <T> Response<T> success(T data) {
        Response<T> response = new Response<>();
        response.setData(data);
        return response;
    }

    // =================================== 失败响应 ===================================
    public static <T> Response<T> fail() {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        return response;
    }

    public static <T> Response<T> fail(String errorMessage) {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        response.setMessage(errorMessage);
        return response;
    }

    public static <T> Response<T> fail(String errorCode, String errorMessage) {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        response.setErrorCode(errorCode);
        response.setMessage(errorMessage);
        return response;
    }
}
```

按照之前定义好的 JSON 格式，我们定义了 4 个字段，并添加了 `success()` 和 `fail()` 方法，分别用于快速生成执行成功的响应参数，和执行失败的响应参数，重载了的多个方法，用于适配不同场景。

### 在控制器中使用

有了 `Response` 工具类，再配合 Spring Boot 的 `@RestController` 或者 `@ResponseBody` 注解， 就可以快速生成 JSON 格式的响应数据了。重写前面小节中 `TestController` 中 `/test` 接口的返参：

```kotlin
	@PostMapping("/test")
    @ApiOperationLog(description = "测试接口")
    public Response test(@RequestBody @Validated User user, BindingResult bindingResult) {
        // 是否存在校验错误
        if (bindingResult.hasErrors()) {
            // 获取校验不通过字段的提示信息
            String errorMsg = bindingResult.getFieldErrors()
                    .stream()
                    .map(FieldError::getDefaultMessage)
                    .collect(Collectors.joining(", "));

            return Response.fail(errorMsg);
        }

        // 返参
        return Response.success();
    }
```

### 扩展响应工具类

上面的工具类功能相对基础。随着后续功能的增加，我们还需要添加更多的辅助方法，例如支持传入异常枚举、分页数据等。这些功能，等后面小节中我们再一一实现它们。本小节暂时不做讲解。

### 测试看下效果

重启项目，通过 Postman 工具对 `/test` 进行 Post 请求，看下现在的接口是否是以 JSON 格式数据进行返回了。

#### 接口响应失败

![img](http://public.file.lvshuhuai.cn/图床\169175663495434.jpeg)

#### 接口响应成功

![img](http://public.file.lvshuhuai.cn/图床\169175675613657.jpeg)

可以看到现在的接口都以 JSON 格式进行返回了，改造成功！！

### 美化：不返回 null 值的字段

细心的小伙伴应该发现了，在接口的返参中，有很多 `null` 值的字段也返回了，有木有办法自动去掉呢？当然是可以的，只需在 `applicaiton.yml` 文件中对 `jackson` 添加相关配置即可，如下：

```yaml
spring:
  jackson:
    # 设置后台返参，若字段值为 null, 则不返回
    default-property-inclusion: non_null
    # 设置日期字段格式
    date-format: yyyy-MM-dd HH:mm:ss
```

再次重启项目，测试一下接口，效果图如下：

![img](http://public.file.lvshuhuai.cn/图床\169175721714270.jpeg)

可以看到，值为 `null` 的字段全都没有返回了, 简洁很多。要说不返回 `null` 值的字段的好处，可以省一些流量，但是不方便的地方是，前端在获取字段值时，需要先判断字段是否存在，是否开启该功能小伙伴们可自行取舍。

> 提示：`weblog` 这个项目中，依然会返回 `null` 值，因为本身这个项目访问量不会很大，更多的是讲究前端开发更方便一点。

### 本小节对应源码

https://t.zsxq.com/11znT2IYk

### 总结

标准化的 API 响应有助于维护一致性，并提高前后端开发的效率。通过创建自定义的响应工具类，我们可以确保应用程序的每个响应都遵循相同的格式，从而提供更好的开发和用户体验。

## Spring Boot 实现全局异常管理

![img](http://public.file.lvshuhuai.cn/图床\169207196002211.jpeg)

### 前言

在开发大型 Web 应用时，统一的异常处理是保持代码整洁和维护性的关键所在。Spring Boot 提供了方便的方法来帮助我们实现全局的异常管理。在本小节中，小哈将带着大家学习如何在 Spring Boot 中实现全局的异常处理。

### 为什么需要全局异常管理？

以下是一段没有全局异常管理的示例代码：

```kotlin
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProductController {

    @GetMapping("/product/{id}")
    public ResponseEntity<String> getProduct(@PathVariable String id) {
        try {
            int productId = Integer.parseInt(id);
            
            // 判断产品 ID 是否合规
            if (productId <= 0) {
                throw new IllegalArgumentException("Product ID must be greater than 0");
            }
            
            // 假设这里是一个查找产品的逻辑
            String productInfo = "Product Info for ID: " + id;
            
            return ResponseEntity.ok(productInfo);
        } catch (NumberFormatException e) {
            // 捕获 ID 不是数字的情况
            return ResponseEntity.badRequest().body("Invalid Product ID format");
        } catch (IllegalArgumentException e) {
            // 捕获产品 ID 小于等于0的情况
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            // 捕获所有其他类型的异常
            return ResponseEntity.status(500).body("An unexpected error occurred");
        }
    }
}
```

在没有全局异常管理的情况下，每个控制器或 `service` 服务中可能都会有各种 `try-catch` 代码块来捕获和处理异常。这样会导致以下问题：

- **代码重复**：相同的异常处理逻辑会在多处重复出现。
- **不一致的响应格式**：不同的开发人员可能采用不同的方式来处理同一种异常，从而导致响应格式不统一。
- **增加维护成本**：未来对异常处理逻辑的任何更改都需要在多个地方进行修改。
- **可读性差**：`try-catch` 块使得主要的业务逻辑被异常处理代码包围，这可能会让代码的主要逻辑不够明显，降低代码的可读性。

通过实现全局异常管理，我们可以避免上述问题，确保应用在出现异常时始终有一致和统一的行为。

### 自定义业务异常

在企业级应用中，除了系统异常，很多时候我们还需要处理业务异常。与系统异常不同，业务异常通常表示一个预期的、合理的错误，例如用户输入的数据无效、所请求的资源不存在等。我们需要区分这些异常，并为它们给调用者提供友好的错误提示。通常来说，比较推荐的做法是，将自定义业务异常整合到全局异常管理中，使其更加统一且易于维护。

#### 自定义一个基础异常接口

首先，在 `weblog-module-common` 模块中新建 `exception` 包，用于统一放置和异常相关的代码。然后，创建一个 `BaseExceptionInterface` 基础异常接口，方便后面做拓展，代码如下：

```java
package com.quanxiaoha.weblog.common.exception;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-15 9:54
 * @description: 通用异常接口
 **/
public interface BaseExceptionInterface {
    String getErrorCode();

    String getErrorMessage();
}
```

上面的接口中，定义了两个方法，`getErrorCode()` 用于获取异常码，`getErrorMessage()` 用于获取异常信息。

#### 自定义错误码枚举

新建 `enums` 包，用于统一放置枚举类，在该包中，创建 `ResponseCodeEnum` 异常码枚举类，代码如下：

```typescript
package com.quanxiaoha.weblog.common.enums;

import com.quanxiaoha.weblog.common.exception.BaseExceptionInterface;
import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-15 10:33
 * @description: 响应异常码
 **/
@Getter
@AllArgsConstructor
public enum ResponseCodeEnum implements BaseExceptionInterface {

    // ----------- 通用异常状态码 -----------
    SYSTEM_ERROR("10000", "出错啦，后台小哥正在努力修复中..."),

    // ----------- 业务异常状态码 -----------
    PRODUCT_NOT_FOUND("20000", "该产品不存在（测试使用）"),
    ;

    // 异常码
    private String errorCode;
    // 错误信息
    private String errorMessage;

}
```

在上述代码中，我们定义了**异常码**和**错误信息**两个字段，并实现了 `BaseExceptionInterface` 接口，同时，还定义了一个 `SYSTEM_ERROR` 枚举值，它属于系统通用异常，通常是未知的异常，为了对调用者表示友好性，统一提示 *出错啦，后台小哥正在努力修复中...*。

除了通用异常外就是业务异常了, 这里定义了一个供测试使用的 `PRODUCT_NOT_FOUND` 枚举值，表示产品不存在，后面会演示如何使用。

#### 自定义业务异常 BizException

然后，创建 `BizException` ， `Biz` 是业务英文 `Business` 的缩写:

```kotlin
package com.quanxiaoha.weblog.common.exception;

import lombok.Getter;
import lombok.Setter;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-15 9:52
 * @description: 业务异常
 **/
@Getter
@Setter
public class BizException extends RuntimeException {
    // 异常码
    private String errorCode;
    // 错误信息
    private String errorMessage;

    public BizException(BaseExceptionInterface baseExceptionInterface) {
        this.errorCode = baseExceptionInterface.getErrorCode();
        this.errorMessage = baseExceptionInterface.getErrorMessage();
    }
}
```

我们让 `BizException` 继承自运行时异常 `RuntimeException`, 同时定义了两个基本字段：

- `errorCode` : 异常码；
- `errorMessage`: 错误信息，用于提供给调用者；

另外，还定义了一个构造器，入参是前面创建的 `BaseExceptionInterface`，通过它可以方便的构造一个业务异常。

### 使用 `@ControllerAdvice`

Spring Boot 提供了 `@ControllerAdvice` 注解，它允许我们定义一个全局的异常处理类。这个类可以捕获应用中抛出的所有异常，并根据需要进行处理。

#### 添加依赖

在 `weblog-module-common` 模块中的 `pom.xml` 中添加如下依赖，因为 `@ControllerAdvice` 注解在这个依赖中：

```php-template
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

#### 拓展响应工具类

在 `Response` 响应工具类中，添加一个新的方法：

```swift
public static <T> Response<T> fail(BizException bizException) {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        response.setErrorCode(bizException.getErrorCode());
        response.setMessage(bizException.getErrorMessage());
        return response;
}
```

可以看到入参是 `BizException` 自定义业务异常，等下在全局异常处理类中会用到它。

#### 创建全局异常处理类

在 `exception` 包下，创建全局异常处理类 `GlobalExceptionHandler` ，代码如下：

```kotlin
package com.quanxiaoha.weblog.common.exception;

import com.quanxiaoha.weblog.common.utils.Response;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;

import javax.servlet.http.HttpServletRequest;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-15 10:14
 * @description: 全局异常处理
 **/
@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    /**
     * 捕获自定义业务异常
     * @return
     */
    @ExceptionHandler({ BizException.class })
    @ResponseBody
    public Response<Object> handleBizException(HttpServletRequest request, BizException e) {
        log.warn("{} request fail, errorCode: {}, errorMessage: {}", request.getRequestURI(), e.getErrorCode(), e.getErrorMessage());
        return Response.fail(e);
    }
}
```

上述代码中，通过 `@ControllerAdvice` 注解，我们将 `GlobalExceptionHandler` 声明为了全局异常处理类。在其中，定义了一个 `handleBizException()` 方法，并通过 `@ExceptionHandler` 注解指定只捕获 `BizException` 自定义业务异常。然后，打印了相关错误日志，并组合了统一的响应格式返回。

#### 试试好不好使

完成上面工作后，我们在 `TestConroller` 中的 `/test` 接口中，手动抛一个自定义业务异常，看看能不能被处理器捕获，并返回统一的出参格式：

```less
@PostMapping("/test")
@ApiOperationLog(description = "测试接口")
public Response test(@RequestBody @Validated User user, BindingResult bindingResult) {
    // 手动抛异常，入参是前面定义好的异常码枚举，返参统一交给全局异常处理器搞定
    throw new BizException(ResponseCodeEnum.PRODUCT_NOT_FOUND);
}
```

重启项目，用 Postman 请求一下 `/test` 接口，看下效果：

![img](http://public.file.lvshuhuai.cn/图床\169207001435685.jpeg)

这样，在后续的业务层开发中，如果有相关逻辑校验等功能，需要提供给调用者提示信息的，就可以直接抛异常就 OK 了，代码层面看上去也更加整洁、好维护。

#### 支持通用异常捕获

在以上的全局异常处理器中，我们只捕获了 `BizException` 业务级的异常，通常来说，还有其他未知类型的运行时异常，可能会发生在程序执行过程中。所以也要捕获一下，给调用者一个友好的提示信息。

##### 拓展全局异常处理器

编辑 `GlobalExceptionHandler` 类，添加如下方法：

```less
    /**
     * 其他类型异常
     * @param request
     * @param e
     * @return
     */
    @ExceptionHandler({ Exception.class })
    @ResponseBody
    public Response<Object> handleOtherException(HttpServletRequest request, Exception e) {
        log.error("{} request error, ", request.getRequestURI(), e);
        return Response.fail(ResponseCodeEnum.SYSTEM_ERROR);
    }
```

上述代码中，通过 `@ExceptionHandler({ Exception.class })` , 捕获的是通用的 `Exception` 异常，你可能会好奇，处理器最终会使用哪个方法进行捕获呢？举个栗子，比如你定义了捕获具体的异常的方法，如 `BizException`，假设抛出的异常也与之对应，则优先使用它来处理，否则使用 `@ExceptionHandler({ Exception.class })` 定义的方法。

##### 拓展响应工具类

还需要对 `Response` 响参工具类拓展一下方法，以支持直接传入异常码枚举：

```swift
public static <T> Response<T> fail(BaseExceptionInterface baseExceptionInterface) {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        response.setErrorCode(baseExceptionInterface.getErrorCode());
        response.setMessage(baseExceptionInterface.getErrorMessage());
        return response;
}
```

##### 看看效果

重写一下 `TestController` 中的 `/test` 接口，主动定义一个运行时异常，分母不能为零：

```kotlin
	@PostMapping("/test")
    @ApiOperationLog(description = "测试接口")
    public Response test(@RequestBody @Validated User user, BindingResult bindingResult) {
        // 主动定义一个运行时异常，分母不能为零
        int i = 1 / 0;
        return Response.success();
    }
```

重启项目，再次请求 `/test` 接口，看下通用类的运行时异常能不能够被正常捕获，并响应错误信息：

![img](http://public.file.lvshuhuai.cn/图床\169207229408910.jpeg)

OK, 正常被捕获了，并返回了 `出错啦，后台小哥正在努力修复中...`的友好提示信息。

### 核心代码目录结构

本小节中，`weblog` 项目需要完成的核心代码目录结构如下：

![img](http://public.file.lvshuhuai.cn/图床\169209169971749.jpeg)

### 最后

至此，一个基本通用的异常处理器的功能就搞定了。全局异常管理不仅仅是捕获和响应异常，它还与整个系统的健壮性和用户体验紧密相关。通过自定义业务异常和全局异常处理，我们可以确保应用在面对各种错误时都能优雅地应对，为用户提供有意义的反馈，同时确保开发团队能够迅速定位并处理问题。

但是，本小节中的全局异常管理器还有不完美的地方，还记得[前面小节](https://www.quanxiaoha.com/column/10011.html) 中的参数校验吗？也是需要手动获取校验错误信息，再手动返回参数，这块的代码比较通用，一坨一坨的，每次都要手动写未免太难看了。能不能在全局异常中统一处理一下呢？答案是肯定的，下小节中，我们将来支持一下这个功能。

## 全局异常处理器+参数校验（最佳实践）

上小节最后提到，之前的参数校验还不够优雅！每次都需要在 `controller` 层手动获取校验错误，然后再返回参数，一坨一坨的，每次都要手动写未免太难看了。本小节中，我们将使用全局异常管理器来优化这块，告别每次手动获取校验错误信息再返回。

### 参数校验不通过，会抛出什么异常？

会了弄清楚 `validation` 在参数校验不通过时，会抛出具体什么异常，需要将 `TestController` 中的 `/test` 接口中的 `BindingResult` 参数去掉，代码如下：

```less
    @PostMapping("/test")
    @ApiOperationLog(description = "测试接口")
    public Response test(@RequestBody @Validated User user) {
        return Response.success();
    }
```

重启项目，通过 Postman 再次请求该接口，就能在控制台看到具体的异常信息了：

![img](http://public.file.lvshuhuai.cn/图床\169208605296173.jpeg)

可以看到异常类名为 `MethodArgumentNotValidException` , 我们可以通过它来获取参数校验相关的错误信息。

### 全局异常处理器捕获该异常

为了解放双手，我们可以通过全局异常处理器来捕获该异常，统一返回错误信息，改造 `GlobalExceptionHandler` 类，添加 `handleMethodArgumentNotValidException()` 方法，代码如下：

```go
    /**
     * 捕获参数校验异常
     * @return
     */
    @ExceptionHandler({ MethodArgumentNotValidException.class })
    @ResponseBody
    public Response<Object> handleMethodArgumentNotValidException(HttpServletRequest request, MethodArgumentNotValidException e) {
        // 参数错误异常码
        String errorCode = ResponseCodeEnum.PARAM_NOT_VALID.getErrorCode();

        // 获取 BindingResult
        BindingResult bindingResult = e.getBindingResult();

        StringBuilder sb = new StringBuilder();

        // 获取校验不通过的字段，并组合错误信息，格式为： email 邮箱格式不正确, 当前值: '123124qq.com';
        Optional.ofNullable(bindingResult.getFieldErrors()).ifPresent(errors -> {
            errors.forEach(error ->
                    sb.append(error.getField())
                            .append(" ")
                            .append(error.getDefaultMessage())
                            .append(", 当前值: '")
                            .append(error.getRejectedValue())
                            .append("'; ")

            );
        });

        // 错误信息
        String errorMessage = sb.toString();

        log.warn("{} request error, errorCode: {}, errorMessage: {}", request.getRequestURI(), errorCode, errorMessage);

        return Response.fail(errorCode, errorMessage);
    }
```

上述代码中，我们通过 `@ExceptionHandler` 注解捕获了 `MethodArgumentNotValidException.class` 类型的异常，并从异常实体类中获取了 `BindingResult` 对象，从而获取到具体哪些字段校验不通过，最终组合错误信息并返回。

#### 添加参数错误枚举

上面代码中，还需要添加一个 `PARAM_NOT_VALID` 枚举值，表示*参数错误*：

```java
package com.quanxiaoha.weblog.common.enums;

import com.quanxiaoha.weblog.common.exception.BaseExceptionInterface;
import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-15 10:33
 * @description: 响应异常码
 **/
@Getter
@AllArgsConstructor
public enum ResponseCodeEnum implements BaseExceptionInterface {

    // ----------- 通用异常状态码 -----------
	...省略
    PARAM_NOT_VALID("10001", "参数错误"),


	...省略
}
```

### 测试看下最终效果

修改 `TestController` 中的 `/test` 接口，记住不要添加参数 `BindingResult`, 将 `MethodArgumentNotValidException` 异常统一抛给全局异常管理器来处理：

```less
    @PostMapping("/test")
    @ApiOperationLog(description = "测试接口")
    public Response test(@RequestBody @Validated User user) {
        return Response.success();
    }
```

重启项目，通过 Postman 调用 `/test` 接口，看看返参效果：

![img](http://public.file.lvshuhuai.cn/图床\169208856227750.jpeg)

可以看到，返参明确返回了哪些字段校验不通过、当前值、以及注解中填写的提示信息，这样返回的好处是，当和前端联调接口时，前端小伙伴可根据提示信息就知道哪个字段出现了问题，避免扯皮。

### 本小节对应源码

https://t.zsxq.com/11CcIzf6z

### 结语

本小节中，小哈带着大家优化了参数校验功能模块，搭配上全局异常管理器，让代码看上去更加整洁，后续开发新功能也更加方便了。

## 整合 Knife4j：提升接口调试效率

![img](http://public.file.lvshuhuai.cn/图床\169223710202949.jpeg)

### Knife4j 是什么？

Knife4j 是一个为 Java 项目生成和管理 API 文档的工具。实际上，它是 Swagger UI 的一个增强工具集，旨在让 Swagger 生成的 API 文档更优雅、更强大。

### Knife4j 主要功能

- **美观的 UI**：相比于原生 Swagger UI，Knife4j 提供了更加人性化和美观的界面设计。
- **丰富的文档交互功能**：支持在线调试、请求参数动态输入、接口排序等。
- **个性化配置**：可自定义 API 文档的界面风格，实现文档界面的个性化展示。

### 为什么要用它？

小伙伴们可能会疑惑，咱这不是一个人就把前后端包办吗？还搞啥 API 文档，是不是多此一举了。其实，我们主要想用的是它的在线调试功能，在前面小节中，小哈在调试接口这块，都是通过 Postman 来进行的，每当测试一个新的接口时，就不得不手动填写请求路径，组装 JSON 入参格式，其实还是比较繁琐的。

有了 Knife4j，因为它支持在线调试，这块的时间就可以省下来了。本小节中，我们就来看看，如何通过 Knife4j 提升接口调试效率。

### 整合 Knife4j

#### 添加依赖

在父项目 `weblog-springboot` 中的 `pom.xml` 文件中，添加 Knife4j 依赖版本号：

```php-template
	<!-- 版本号统一管理 -->
    <properties>

        <!-- 依赖包版本 -->
		省略...        
        <knife4j.version>4.3.0</knife4j.version>
    </properties>
    
    <!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>
            省略...        

            <!-- knife4j（API 文档工具） -->
            <dependency>
                <groupId>com.github.xiaoymin</groupId>
                <artifactId>knife4j-openapi2-spring-boot-starter</artifactId>
                <version>${knife4j.version}</version>
            </dependency>

        </dependencies>
    </dependencyManagement>
```

因为 `admin` 后台管理模块和博客前台模块都需要调试接口，所以，我们需要在 `weblog-web` 和 `weblog-module-admin` 两个模块中，都需要引入该依赖：

```php-template
		<!-- knife4j -->
		<dependency>
			<groupId>com.github.xiaoymin</groupId>
			<artifactId>knife4j-openapi2-spring-boot-starter</artifactId>
		</dependency>
```

#### 添加配置类

在 `weblog-web` 模块中添加包 `config` , 用于统一放置配置类。在该包下新建名为 `Knife4jConfig` 配置类：

![img](http://public.file.lvshuhuai.cn/图床\169223253275814.jpeg)

配置类完整代码如下：

```java
package com.quanxiaoha.weblog.web.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springfox.documentation.builders.ApiInfoBuilder;
import springfox.documentation.builders.PathSelectors;
import springfox.documentation.builders.RequestHandlerSelectors;
import springfox.documentation.service.ApiInfo;
import springfox.documentation.service.Contact;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2WebMvc;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-16 7:53
 * @description: Knife4j 配置
 **/
@Configuration
@EnableSwagger2WebMvc
public class Knife4jConfig {

    @Bean("webApi")
    public Docket createApiDoc() {
        Docket docket = new Docket(DocumentationType.SWAGGER_2)
                .apiInfo(buildApiInfo())
                // 分组名称
                .groupName("Web 前台接口")
                .select()
                // 这里指定 Controller 扫描包路径
                .apis(RequestHandlerSelectors.basePackage("com.quanxiaoha.weblog.web.controller"))
                .paths(PathSelectors.any())
                .build();
        return docket;
    }

    /**
     * 构建 API 信息
     * @return
     */
    private ApiInfo buildApiInfo() {
        return new ApiInfoBuilder()
                .title("Weblog 博客前台接口文档") // 标题
                .description("Weblog 是一款由 Spring Boot + Vue 3.2 + Vite 4.3 开发的前后端分离博客。") // 描述
                .termsOfServiceUrl("https://www.quanxiaoha.com/") // API 服务条款
                .contact(new Contact("犬小哈", "https://www.quanxiaoha.com", "871361652@qq.com")) // 联系人
                .version("1.0") // 版本号
                .build();
    }
}
```

> **注意**： `RequestHandlerSelectors.basePackage("com.quanxiaoha.weblog.web.controller")` 中的包路径，需要改成你实际的 `controller` 包路径，否则会导致接口扫描不到。

上述代码中，通过 `@Configuration` 指定了 `Knife4jConfig` 这个类为配置类，同时添加了 `@EnableSwagger2WebMvc` 注解，该注解作用是启用 Swagger2，定义了一个 `Docket` Bean 包含了 Swagger 相关的配置信息。

#### 看看效果

完成上面配置后，重启项目，若控制台出现如下红线标注的日志，则表示 `Knife4j` 配置完成了：

![img](http://public.file.lvshuhuai.cn/图床\169219700620432.jpeg)

浏览器访问路径 `http://localhost:8080/doc.html` , 就可以看到 `api` 管理界面了，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\169223292635679.jpeg)

大概解释一下 UI 界面的功能点：

- **主页**： 文档整体信息一览，包括文档标题、简介、作者、接口统计信息等，也就是 `Knife4jConfig` 类中 `buildApiInfo()` 方法配置的相关信息；

- **分组**：实际企业级项目中，可能会分为多个模块、或者很多微服务，分组用于对接口进行分类。

    ![img](http://public.file.lvshuhuai.cn/图床\169223300349228.jpeg)

- **Swagger Models** : 服务端接口相关的领域模型；

- **文档管理**： 这个模块里面可以设置全局参数，比如每次请求在 header 头中统一添加某个参数等；导出 `API` 文档到本地，以及个性化设置，有兴趣的小伙伴可以自己点进去体验一波：

    ![img](http://public.file.lvshuhuai.cn/图床\169223320674952.jpeg)

- **项目接口**：左侧导航栏中会列举出本项目中的所有 `controller` 类，以及其中的接口。因为当前 `weblog` 项目只有一个供测试的 `TestController`，效果如下:

    ![img](http://public.file.lvshuhuai.cn/图床\169223352695250.jpeg)

可以看到 Knife4j 自动根据我们的 `controller` 代码，将所有的接口列出来了，包括请求示例、请求参数等。

#### 如何调试接口

假设说，你刚刚开发好了一个新的接口，需要本地调试一下接口是否正常。只需点击左侧 *调试* 选项，然后填写字段值，在点击发送按钮即可：

![img](http://public.file.lvshuhuai.cn/图床\169223382165960.jpeg)

返参效果图：

![img](http://public.file.lvshuhuai.cn/图床\169223389202020.jpeg)

怎么样，是不是相较于使用 Postman, 调试接口的效率大大地提升了~

#### 给 controller 添加 Swagger 相关注解

痛点：目前在左侧显示的模块类名，以及接口名称都是代码中本身的英文，也许你当前调试中，能够清晰的知道哪个 `controller` 类、哪个接口都是干啥的，但是时间一长，接口多了起来，你就会一脸懵逼了，挨，这个 `controller` 是管理那块的功能的？

为了解决这个问题，Swagger 提供了相关的注解，可以标识模块名称，以及接口名称，并方便的展示在管理界面中。添加方式如下：

![img](http://public.file.lvshuhuai.cn/图床\169223431498414.jpeg)

- `@Api` : 此注解作用于 `controller` 之上，用于描述相关职责；
- `@ApiOperation` : 此注解作用于接口上，用于描述接口干啥的；

添加完上面两个注解后，管理界面的效果图如下：

![img](http://public.file.lvshuhuai.cn/图床\169223480793233.jpeg)

明显感觉到管理上更加清晰明了了。

除上面两个注解外，我们还可以给入参对象添加 Swagger 相关注解，如下所示：

![img](http://public.file.lvshuhuai.cn/图床\169223503011945.jpeg)

- `@ApiModel` : 此注解作用于实体类上，用于描述类；
- `@ApiModelProperty` : 此注解作用于字段上，用于描述字段；

最终效果如下：

![img](http://public.file.lvshuhuai.cn/图床\169223525516797.jpeg)

每个字段对应的说明也有了。

### 生产环境如何屏蔽 Knife4j

很多时候，我们不想项目在生产环境中暴露出所有接口信息，只想在测试环境中联调使用，那么要如何屏蔽该功能呢?

#### Spring Boot Profile 特性

Profile 是 Spring Boot 中的一项特性，允许你在不同环境中使用不同的配置。这种机制使得我们可以轻松地在不同环境（如开发、测试和生产环境）中使用不同的配置参数。

#### `@Profile` 注解

你可以在配置类上添加 `@Profile` 注解，来控制 Knife4j 是否生效 。只有当指定的 Profile 处于激活状态时，该配置类才会被创建和被使用。代码如下：

```less
@Configuration
@EnableSwagger2WebMvc
@Profile("dev") // 只在 dev 环境中开启
public class Knife4jConfig {
	省略...
}
```

### 分组功能

前面小节中说到，`weblog` 项目接口分为前台和 Admin 后台，所以，除了在 `weblog-web` 模块中配置 Knife4j 外，还需要在 `web-module-admin` 也配置一份，并使用 Knife4j 分组功能将各自的接口隔离开来。

#### 添加依赖、配置类

`weblog-module-admin` 模块和前面的步骤一样，在 `pom.xml` 添加依赖：

```php-template
		<!-- knife4j -->
		<dependency>
			<groupId>com.github.xiaoymin</groupId>
			<artifactId>knife4j-openapi2-spring-boot-starter</artifactId>
		</dependency>
```

建包 `config`, 并创建 `Knife4jAdminConfig` 配置类，代码如下：

```kotlin
package com.quanxiaoha.weblog.admin.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springfox.documentation.builders.ApiInfoBuilder;
import springfox.documentation.builders.PathSelectors;
import springfox.documentation.builders.RequestHandlerSelectors;
import springfox.documentation.service.ApiInfo;
import springfox.documentation.service.Contact;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2WebMvc;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-16 7:53
 * @description: Knife4j 配置
 **/
@Configuration
@EnableSwagger2WebMvc
@Profile("dev") // 只在 dev 环境中开启
public class Knife4jAdminConfig {

    @Bean("adminApi")
    public Docket createApiDoc() {
        Docket docket = new Docket(DocumentationType.SWAGGER_2)
                .apiInfo(buildApiInfo())
                // 分组名称
                .groupName("Admin 后台接口")
                .select()
                // 这里指定 Controller 扫描包路径
                .apis(RequestHandlerSelectors.basePackage("com.quanxiaoha.weblog.admin.controller"))
                .paths(PathSelectors.any())
                .build();
        return docket;
    }

    /**
     * 构建 API 信息
     * @return
     */
    private ApiInfo buildApiInfo() {
        return new ApiInfoBuilder()
                .title("Weblog 博客 Admin 后台接口文档") // 标题
                .description("Weblog 是一款由 Spring Boot + Vue 3.2 + Vite 4.3 开发的前后端分离博客。") // 描述
                .termsOfServiceUrl("https://www.quanxiaoha.com/") // API 服务条款
                .contact(new Contact("犬小哈", "https://www.quanxiaoha.com", "871361652@qq.com")) // 联系人
                .version("1.0") // 版本号
                .build();
    }
}
```

注意类名，和 `@Bean` 的名称不能和 `weblog-web` 中的一样，否则会冲突。然后，改写分组名称，以及包扫描路径，还有 API 相关信息。

完成上述工作后，重启项目，再次访问 `API` 管理界面，即可看到分组勾选栏中，有*前台接口*和 *Admin 后台接口*了，后面查找相关接口，只需先确定是属于前台，还是后台，然后再对应的去查找相关接口，也方便很多：

![img](http://public.file.lvshuhuai.cn/图床\169223669693251.jpeg)

### 本小节对应源码

https://t.zsxq.com/11FPmsWXz

### 结语

本小节中，小哈带着大家了解了什么是 knife4j， 它的主要功能，以及相较于 Swagger 它的优势在哪里？最后，在 `weblog` 项目中整合了 knife4j ，可以在后续的功能开发中，很方便的进行本地接口的调试，提升调试效率。

## 自定义 Jackson 序列化、反序列化，支持 Java 8 日期新特性

Java 8 中，引入了新的时间和日期 API，相比较老旧的 `Date` , 它使用起来更加便捷，用过的都懂。本小节中，小哈将带着大家自定义 Spring Boot 内置的 JSON 框架 Jackson，让出入参支持序列化、反序列化 Java 8 中新的日期 API : `LocalDateTime`、`LocalDate`、`LocalTime`, 废话不多说，开整~

### 为什么要用 Java 8 新的日期 API

假设有个需求，需要对当前日期进行 `加 7 天` 操作，我们来看看使用 `Date` 要如何计算，示例代码如下：

```csharp
        // 获取当前日期
        Date today = new Date();
        System.out.println("今天的日期: " + today);
        
        // 创建 Calendar 实例
        Calendar calendar = Calendar.getInstance();
        
        // 设置当前日期
        calendar.setTime(today);
        
        // 当前日期加 7 天
        calendar.add(Calendar.DATE, 7);
        
        // 获取加 7 天后的日期
        Date sevenDaysLater = calendar.getTime();
        
        System.out.println("7 天后的日期: " + sevenDaysLater);
```

再来看看使用新的日期 `LocalDate` 完成同样功能的示例代码：

```csharp
        // 获取当前日期
        LocalDate today = LocalDate.now();
        System.out.println("今天的日期: " + today);
        
        // 当前日期加 7 天
        LocalDate sevenDaysLater = today.plusDays(7);
        
        System.out.println("7 天后的日期: " + sevenDaysLater);
```

看完两者之间的对比，你就应该知道，为什么小哈要推荐使用 Java 8 新的日期 API 了。

### 自定义 Jackson 配置类

由于 Spring Boot 内置使用的就是 `Jackson` JSON 框架，所以，无需引入新的依赖，仅需添加自定义配置类即可，让其支持新的日期 `API`。

在 `weblog-module-common` 模块中，新建 `config` 配置包，并创建 `JacksonConfig` 配置类，代码如下：

![img](http://public.file.lvshuhuai.cn/图床\169226317827651.jpeg)

```java
package com.quanxiaoha.weblog.common.config;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserializer;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateSerializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalTimeSerializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.TimeZone;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2023-08-17 16:08
 * @description: 自定义 Jackson
 **/
@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper() {
        // 初始化一个 ObjectMapper 对象，用于自定义 Jackson 的行为
        ObjectMapper objectMapper = new ObjectMapper();
		
		// 忽略未知字段（前端有传入某个字段，但是后端未定义接受该字段值，则一律忽略掉）
        objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
		
        // JavaTimeModule 用于指定序列化和反序列化规则
        JavaTimeModule javaTimeModule = new JavaTimeModule();

        // 支持 LocalDateTime、LocalDate、LocalTime
        javaTimeModule.addSerializer(LocalDateTime.class, new LocalDateTimeSerializer(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        javaTimeModule.addDeserializer(LocalDateTime.class, new LocalDateTimeDeserializer(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        javaTimeModule.addSerializer(LocalDate.class, new LocalDateSerializer(DateTimeFormatter.ofPattern("yyyy-MM-dd")));
        javaTimeModule.addDeserializer(LocalDate.class, new LocalDateDeserializer(DateTimeFormatter.ofPattern("yyyy-MM-dd")));
        javaTimeModule.addSerializer(LocalTime.class, new LocalTimeSerializer(DateTimeFormatter.ofPattern("HH:mm:ss")));
        javaTimeModule.addDeserializer(LocalTime.class, new LocalTimeDeserializer(DateTimeFormatter.ofPattern("HH:mm:ss")));

        objectMapper.registerModule(javaTimeModule);

        // 设置时区
        objectMapper.setTimeZone(TimeZone.getTimeZone("Asia/Shanghai"));

        // 设置凡是为 null 的字段，返参中均不返回，请根据项目组约定是否开启
        // objectMapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);

        return objectMapper;
    }
}
```

上述代码中，我们定义了一个 `ObjectMapper` Bean，它用于自定义 `Jackson` 的行为，然后，通过 `JavaTimeModule` 添加了 `LocalDateTime、LocalDate、LocalTime` 的序列化、反序列化规则，搞定这些后，再设置时区、以及序列化中是否包含值为 `null` 的字段。仅仅数行代码，我们就支持了新的日期 `API`， 是不是很简单。

### 清除 applicaiton.yml 中无用的 jackson 配置

之前在搭建 `weblog` 多模块项目时，有针对 `jackson` 添加了一些配置，如今已经不再需要。后面，我们将统一使用新日期 `API`。

![img](http://public.file.lvshuhuai.cn/图床\169226616273163.jpeg)

最终，`application.yml` 配置内容如下：

```yaml
spring:
  profiles:
    # 默认激活 dev 环境
    active: dev
```

### 测试一波

接下来，我们来测试一下是否真的支持了新的日期 `API`。在 `User` 对象中，添加如下三个字段，用以测试三种类型的日期类是否能够正常序列化、反序列化：

```less
@Data
@ApiModel(value = "用户实体类")
public class User {
	省略...

    // 创建时间
    private LocalDateTime createTime;
    // 更新日期
    private LocalDate updateDate;
    // 时间
    private LocalTime time;
}
```

修改 `TestController` 中的 `/test` 接口：

```less
    @PostMapping("/test")
    @ApiOperationLog(description = "测试接口")
    @ApiOperation(value = "测试接口")
    public Response test(@RequestBody @Validated User user) {
        // 打印入参
        log.info(JsonUtil.toJsonString(user));

        // 设置三种日期字段值
        user.setCreateTime(LocalDateTime.now());
        user.setUpdateDate(LocalDate.now());
        user.setTime(LocalTime.now());
        
        return Response.success(user);
    }
```

重启项目，请求 `/test` 接口，看下接口是否能够正常被请求：

![img](http://public.file.lvshuhuai.cn/图床\169226679290023.jpeg)

入参如下：

```perl
{
  "age": 22,
  "email": "123@qq.com",
  "sex": 0,
  "username": "犬小哈",
  "createTime": "2022-09-02 12:00:00",
  "updateDate": "2022-09-11",
  "time": "12:00:00"
}
```

我们设置了类型为新日期的三个字段的值，若自定义 `Jackson` 生效了，则能够被正常序列化，则日志中会正常打印 `user` 对象参数：

![img](http://public.file.lvshuhuai.cn/图床\169226696524250.jpeg)

再来看看出参，也是正常的：

![img](http://public.file.lvshuhuai.cn/图床\169226710253137.jpeg)

OK, 到这里，让 `Jackson` 支持 `LocalDateTime` 等新的日期 `API` 就完成了。

### 本小节对应源码

https://t.zsxq.com/114bcVOM3

### 结语

本小节中，小哈带着大家自定义了 Jackson 序列化、反序列化，让其支持了 Java 8 新的日期 API , 这些日期新特性相比较 `Date`, 使用起来会更加方便，在后面小节的学习中，你就能切身体会到了。

## 小结

到这里，《Spring Boot 后端工程搭建》一章就算是结束了，`weblog` 后端项目的基本工程骨架也搭建好了，还有诸如整合 Mybatis Plus 、Elasticsearch 、Minio 等，我们放到后面具体小节中，真正用到的地方再集成进来，这种方式，相对比初学者也更加友好。

那么，我们来回忆一下本章节的内容：

- [3.1 搭建 Spring Boot 多模块工程](https://www.quanxiaoha.com/column/10005.html)
- [3.2【补充】搭建 Spring Boot 多模块工程（通过 Maven Archetype）](https://www.quanxiaoha.com/column/10161.html)
- [3.3 Spring Boot 多环境配置](https://www.quanxiaoha.com/column/10006.html)
- [3.4 配置 Lombok](https://www.quanxiaoha.com/column/10007.html)
- [3.5 Spring Boot 整合 Lockback 日志](https://www.quanxiaoha.com/column/10008.html)
- [3.6 Spring Boot 自定义注解，实现 API 请求日志切面](https://www.quanxiaoha.com/column/10009.html)
- [3.7 Spring Boot 通过 MDC 实现日志跟踪](https://www.quanxiaoha.com/column/10010.html)
- [3.8 Spring Boot 实现优雅的参数校验](https://www.quanxiaoha.com/column/10011.html)
- [3.9 Spring Boot 自定义响应工具类](https://www.quanxiaoha.com/column/10012.html)
- [3.10 Spring Boot 实现全局异常管理](https://www.quanxiaoha.com/column/10013.html)
- [3.11 全局异常处理器+参数校验（最佳实践）](https://www.quanxiaoha.com/column/10014.html)
- [3.12 整合 Knife4j：提升接口调试效率](https://www.quanxiaoha.com/column/10015.html)
- [3.13 自定义 Jackson 序列化、反序列化，支持 Java 8 日期新特性](https://www.quanxiaoha.com/column/10016.html)

本章中，已经搭建好的工程骨架中，很多基础功能，如《自定义注解，API 请求日志》、《优雅参数校验》、《全局异常管理》、《自定义 Jackson 序列化》等，也是小哈在企业开发中，凡是搭建新项目，必整合的功能组件，可以显著提升开发效率。希望小伙伴们学完后，能够有所收获~
