# Java 注解原理是什么

> 一句话先概括：**注解 = 写在代码上的“配置标签”，本身不执行任何逻辑，真正让它生效的是编译器、字节码工具和运行时框架。**

## 注解的本质：标签 + 元数据

- **注解是标签（Tag）**

    写在类、方法、字段、参数、包等位置上，形如 `@Override`、`@Controller`、`@Test`。

- **注解是元数据（Metadata）**

    它只是对“代码元素的附加信息”，比如：这是一个控制器、这是一个测试方法、这个字段需要校验非空等等。

- **注解本身不执行逻辑**

     JVM 不会因为你写了 `@XXX` 就自动执行什么代码。

    **真正做事情的是“读注解的人”——编译器、IDE 插件、框架、工具。**

- **不直接改变业务逻辑**

    我们写的 if / for / try 才是业务逻辑；注解更像是对这些逻辑的“说明书”和“配置”。

可以把注解理解成：

> 给代码贴上“有含义的便利贴”，后面的工具和框架看到这些便利贴，按照约定做事。

## 注解只是一个标签

注解本身不起功能逻辑上的作用，只是一个标签，真正起作用的是执行器

- 手动管理方式——通过反射，在运行时获取注解，然后添加一些功能
- 框架——SpringBoot 里的 AOP，自动为这些方法生成**代理类**
- 注解处理器——APT 等，能够处理 Lombok 这样的注解，在 `javac` 编译源码时生成额外代码或做校验。

## 注解在代码中的存活周期：SOURCE / CLASS / RUNTIME

注解有 3 个“保留级别”（Retention），由元注解 `@Retention` 控制：

```java
@Retention(RetentionPolicy.SOURCE)   // 只在源码存在
@Retention(RetentionPolicy.CLASS)    // 在 .class 文件存在（默认）
@Retention(RetentionPolicy.RUNTIME)  // 运行时还能通过反射读到
```

### SOURCE 级别

- 只在 **源代码** 中存在，编译后会被 **丢弃**。
- 典型用途：只给 **编译器 / IDE** 看的注解。
     比如：`@Override`、`@SuppressWarnings`。
- 原理：编译器在分析源码时读到这些注解，做检查或发出/忽略告警，之后不再保留。

### CLASS 级别

- 编译后会写进 **.class 文件** 的元数据区域。
- 但 **运行时 JVM 不会通过反射暴露出来**。
- 典型用途：只给 **字节码工具** 或 **编译后处理器** 看的注解。
- 比如某些框架用 ASM、Javassist 在类加载前改字节码。

### RUNTIME 级别

- 注解信息会写入 .class 文件，并在类加载后 **保留到运行时**。
- 可以通过反射 API 读取：

```java
MyAnno anno = clazz.getAnnotation(MyAnno.class);
```

- 典型用途：**运行时框架**（Spring、JPA、JUnit、Dubbo 等）需要根据注解做行为变化，比如：
    - Spring 扫描带 `@Controller` 的类注册到容器；
    - JPA 读取 `@Entity`、`@Column` 生成 SQL；
    - JUnit 执行带 `@Test` 的方法。

> 小结：
>
> - 谁来读？——编译器、字节码工具、运行时框架
> - 什么时候读？——取决于 `@Retention` 是 SOURCE / CLASS / RUNTIME

## 注解是怎样定义和使用的？

### 定义注解：用 `@interface`

```java
import java.lang.annotation.*;

@Retention(RetentionPolicy.RUNTIME)     // 运行时可见
@Target(ElementType.METHOD)             // 只能标在方法上
public @interface LogExecutionTime {
    String value() default "";          // 注解的一个属性
}
```

关键点：

- 使用 `@interface` 而不是 `class` / `interface`。
- 元注解：
    - `@Retention`：控制生命周期（上面讲过）。
    - `@Target`：控制能标在 **类 / 方法 / 字段 / 参数 / 包 / 注解** 等哪里。
- 注解内部定义的是 **属性**（本质是无参方法），可以有默认值。

### 执行器

```java
import java.lang.reflect.Method;

public class LogExecutionRunner {

    public static void runWithLog(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();
        for (Method method : clazz.getDeclaredMethods()) {
            if (method.isAnnotationPresent(LogExecutionTime.class)) {

                LogExecutionTime anno = method.getAnnotation(LogExecutionTime.class);
                String desc = anno.value();

                long start = System.currentTimeMillis();
                method.setAccessible(true);
                // 这里只演示无参方法，有参方法需要自己传参
                method.invoke(obj, 1L);
                long cost = System.currentTimeMillis() - start;

                System.out.println(
                    "方法 " + method.getName() + 
                    " [" + desc + "] 执行耗时: " + cost + "ms");
            }
        }
    }

    public static void main(String[] args) throws Exception {
        UserService service = new UserService();
        runWithLog(service);
    }
}
```

### 使用注解：给代码元素“贴标签”

```java
public class UserService {

    @LogExecutionTime("查询用户耗时")
    public User getUserById(Long id) {
        // 业务逻辑
    }
}
```

此时 `getUserById` 方法上，就多了一条 **“元数据记录”**：

> 这个方法有注解 `@LogExecutionTime(value="查询用户耗时")`

## 注解到底是怎么“起作用”的？

**关键：注解本身是静态的；真正的行为由“处理它的人”决定。**

可以按时间线拆成三种处理方式：

### 编译期：编译器 / 注解处理器（APT）

- Java 提供了 **注解处理器（Annotation Processing Tool）** 机制。
- 在编译时，处理器可以：
    - 扫描特定注解；
    - 校验代码是否符合约定；
    - 自动生成新的 Java 源码或其他资源。

#### 典型例子

- Lombok（`@Getter`/`@Setter`/`@Builder`）

    在编译期修改 AST / 字节码，帮你生成 getter/setter，而源码里看不到这些方法。

- MapStruct 根据注解生成 DTO 转换代码。

**过程（简化理解）：**

1. 编译器读取源码时发现注解；
2. 把这些信息交给注册好的 `Processor`；
3. `Processor` 根据注解生成新的源码 / 报错 / 警告；
4. 编译继续进行。

### 类加载前后：字节码工具处理 CLASS 级注解

- 一些框架使用 ASM、ByteBuddy 等工具在类加载前/加载时，读取 `.class` 文件中的注解信息，然后 **修改字节码**。
- 典型用途：AOP、监控埋点、性能测量等。

### 运行时：框架 + 反射读取 RUNTIME 级注解

这是日常开发最常见的方式，尤其是 Spring 系列：

1. 容器启动时，扫描 classpath 中的类；
2. 通过反射拿到类、方法、字段上的注解；
3. 根据注解内容做各种注册和逻辑：
    - 把 `@Controller`、`@Service` 标记的类放进 IOC 容器；
    - 把 `@RequestMapping("/user")` 注册到路由表；
    - 看到 `@Transactional`，在方法外面织入事务代理；
    - 看到 `@Autowired`，自动注入依赖。

示意代码（框架内部可能类似这样）：

```java
for (Class<?> clazz : allClassesOnClasspath) {
    if (clazz.isAnnotationPresent(Controller.class)) {
        Object bean = clazz.getDeclaredConstructor().newInstance();
        // 注册到容器
    }
}
```

## 注解在 .class 文件里长什么样？

更底层一点，从 JVM 角度看：

- 编译后，注解会被写入到 `.class` 文件中的 **attributes** 区域，比如：
    - `RuntimeVisibleAnnotations`
    - `RuntimeInvisibleAnnotations`
- 当 `RetentionPolicy.RUNTIME` 时，这些信息会在类加载后被 **保留到运行时元数据中**。
- 反射 API（`Class.getAnnotations()` 等）本质就是去读这些元数据。

你可以把它想象成：

> 注解是写在 class 文件里的一个“结构化字段”，JVM 和反射库只是帮你把它解析出来。

## 注解和注释、配置文件有什么区别？

- **注释（`//`、`/\* \*/`）**
    - 只给人看，编译后完全丢弃；
    - 工具一般不会基于注释做逻辑决策。
- **注解（`@XXX`）**
    - 给人看，也给 **工具/框架** 看；
    - 可以在编译期、运行期被读取，从而改变代码生成方式或运行行为。
- **XML / YAML / properties 配置**
    - 一般是外部配置文件；
    - 注解更靠近代码，适合描述类/方法本身的特性；
    - 三者在很多框架里是互补关系（Spring 早期 XML 配置，现在大量用注解）