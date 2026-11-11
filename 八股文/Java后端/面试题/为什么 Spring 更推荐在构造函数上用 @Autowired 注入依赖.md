# 为什么 Spring 更推荐在构造函数上用 @Autowired 注入依赖

> 说明：严格来说，**Spring 推荐的是“构造函数注入”这一模式**；在 Spring 4.3+ 且只有一个构造函数时，可以**不写** `@Autowired`，但在很多团队规范里依旧会**显式写在构造函数上**，以便可读性与兼容性。

## 依赖注入的几种方式对比

Spring 中常见的依赖注入方式：

### 字段注入

```java
@Service
public class UserService {
    @Autowired
    private OrderService orderService;
}
```

### Setter 注入

```java
@Service
public class UserService {
    private OrderService orderService;

    @Autowired
    public void setOrderService(OrderService orderService) {
        this.orderService = orderService;
    }
}
```

### 构造函数注入（推荐）

```java
@Service
public class UserService {
    private final OrderService orderService;

    @Autowired  // Spring 4.3+ 且只有一个构造函数时，可以省略
    public UserService(OrderService orderService) {
        this.orderService = orderService;
    }
}
```

三种都能用，但 Spring 官方文档、社区最佳实践和很多架构指南，都把**构造函数注入**作为首选方式。

## 为什么更推荐“构造函数注入”

### 依赖显式、强制完整：防止“残缺对象”

构造函数注入的本质：**一个 Bean 想要被创建，必须把所有依赖通过构造函数传进来**。

- 字段 / Setter 注入：Spring 可以先 `new` 出对象，再逐个注入依赖，中间会有一个**“部分初始化”状态**；
- 构造函数注入：如果某个必须依赖缺失，**对象根本创建不出来**，启动就失败。

这会带来几个好处：

- 强制你思考：**哪些是“必需依赖”**，哪些可以是可选；
- 避免在运行中出现 `NullPointerException`，因为“某个依赖没注入就被用”；
- 出问题时，**启动时就爆炸**，而不是线上跑了一半才出错。

一句话：

> **构造函数注入等价于“编译期/启动期强约束依赖完整性”。**

### 更支持不可变设计：`final` 让依赖更安全

构造函数注入天然支持：

```java
@Service
public class UserService {
    private final OrderService orderService;

    @Autowired
    public UserService(OrderService orderService) {
        this.orderService = orderService;
    }

    // 从此之后，不会再被修改
}
```

使用 `final` 修饰依赖字段：

- 明确表达语义：**依赖在对象生命周期内不会变化**；
- 避免被误改（无意间在某个 setter 里又重新赋值）；
- 在多线程环境下更安全（结合不可变对象思想）。

字段注入通常写成：

```java
@Autowired
private OrderService orderService;
```

- 不能是 `final`；
- 理论上可以被后续代码修改；
- 可变状态多了，Bug 空间也随之变大。

对于偏“函数式”、“DDD 实践”、“强类型 + 不可变”风格的团队，**构造函数注入 + `final`** 几乎是默认标配。

### 单元测试更友好：无需容器也能 new

**构造函数注入最大的工程优势之一：方便测试。**

- 字段注入写法：

  ```java
  @Service
  public class UserService {
      @Autowired
      private OrderService orderService;
  }
  ```

  在单元测试中，你想测试 `UserService`：

  - 要么启动一个 Spring 容器（`@SpringBootTest`），让 Spring 帮你注入；
  - 要么用反射去塞字段，很丑。

- 构造函数注入写法：

  ```java
  public class UserServiceTest {
  
      @Test
      void testSomething() {
          OrderService mockOrderService = Mockito.mock(OrderService.class);
          UserService userService = new UserService(mockOrderService);
          // 直接调用方法测试
      }
  }
  ```

你可以 **只测试这一个类**，不必启动整套容器，测试更快、更精确：

- 非常契合 “**依赖倒置 + 依赖注入 + 可替代实现（Mock）**” 这一整套思想；
- 更像纯 Java 代码，而不是“必须跑在 Spring 上的魔法类”。

### 类结构清晰、可读性强：一眼看出依赖列表

构造函数参数本身就是一个“依赖清单”：

```java
public UserService(UserRepository userRepository,
                   OrderService orderService,
                   SmsService smsService) { ... }
```

你一眼就能看出来：

- 这个类依赖了哪些 Bean；
- 有多少依赖，是否过于臃肿（构造函数太长，提醒你需要拆分类/职责）。

相对来看：

- 字段注入：依赖散落在类中的不同位置；
- Setter 注入：依赖分布在多个方法上，不一眼明显。

在做代码 review、重构时，**构造函数就是天然的“依赖收敛点”**，利于识别上帝类 / 过多职责。

### 生命周期更明确：创建即“可用”

字段 / Setter 注入：

- 对象先 `new` 出来；
- 再由 Spring 容器执行依赖注入；
- 在某些生命周期回调或构造器里，依赖可能还没有注入完成（如果你误用，就容易 NPE / 逻辑错误）。

构造函数注入：

- 所有依赖在构造期间就已经准备好；
- 构造函数结束后，对象就是“可用状态”。

这与很多人习惯的 OOP 认知一致：

> **对象一旦构造完成就处于“就绪”状态，不需要再额外“激活”步骤。**

### 配合 Lombok、Kotlin 等工具更优雅

在 Java 中写多参数构造函数会有点啰嗦，但常见组合是：

```java
@Service
@RequiredArgsConstructor  // Lombok
public class UserService {

    private final UserRepository userRepository;
    private final OrderService orderService;
    private final SmsService smsService;
}
```

- Lombok 自动生成带所有 `final` 字段的构造函数；
- Spring 4.3+：单构造器可以省略 `@Autowired`，依赖自动注入；
- 代码既**简洁**又**符合最佳实践**。

在 Kotlin 中（Spring 很多新项目会用）：

```java
@Service
class UserService(
    private val userRepository: UserRepository,
    private val orderService: OrderService,
    private val smsService: SmsService
)
```

- 构造函数注入是 Kotlin “默认姿势”，字段注入反而很不自然；
- 与 Spring 的推荐实践高度契合。

## 为什么是在“构造函数上”用 `@Autowired`

严格地说：

- Spring 4.3 之前：
  - **如果你希望用构造函数注入，基本必须在构造函数上标 `@Autowired`；**
- Spring 4.3 及之后：
  - 如果一个类只有**一个构造函数**，即使不写 `@Autowired`，Spring 也会自动按构造函数注入；
  - 如果有**多个构造函数**，你必须在要用于注入的那个构造函数上标注 `@Autowired`，否则 Spring 不知道该选哪一个。

所以，“推荐在构造函数上用 `@Autowired`”背后有几个考虑：

### 语义明确：告诉 Spring “用我这个构造函数注入”

尤其是多构造函数时：

```java
@Service
public class UserService {

    private final OrderService orderService;

    public UserService() {
        this.orderService = null; // 可能给框架/工具用
    }

    @Autowired
    public UserService(OrderService orderService) {
        this.orderService = orderService;
    }
}
```

- 明确告诉容器：**这个带参数的构造函数用于依赖注入**；
- 其他构造函数可能用于测试、反射库、序列化框架等，不希望 Spring 误用。

### 兼容历史版本和统一编码规范

很多团队会有这样的编码规范：

- 不管是 Spring 4.3+ 还是旧项目，**统一要求在构造函数上显式加 `@Autowired`**；
- 这样不会因为 Spring 版本差异 / IDE 提示不同，导致风格不一致；
- 新人看到 `@Autowired` 在构造器上，也容易立刻理解：**“这是注入用的构造函数。”**

### 对比字段注入的 `@Autowired`

- 字段注入把 `@Autowired` 写在字段上，让人以为“这个注解和字段强绑定”；
- 但从 DI 思想来说，“创建对象 + 提供依赖”本身应该是一个整体动作，而**构造函数正是“创建动作”的入口**；
- 把 `@Autowired` 放在构造函数上，更符合“**通过构造器获得完整依赖后再使用对象**”的理念，而不是“先 new 半成品，再填坑”。

## `@Autowired` vs `@Resource`，在构造函数场景下的考虑

你之前问过 `@Autowired` 和 `@Resource`：

- `@Autowired`
  - Spring 自家注解；
  - 默认按类型注入，可结合 `@Qualifier` 指定 Bean；
  - 支持构造函数注入，是构造函数注入的主流组合。
- `@Resource`
  - JSR-250 标准注解；
  - 默认**按名称**注入，不指定时用字段名 / 参数名；
  - 常用于字段 / Setter 注入，在构造函数上用得少。

在构造函数注入场景：

```java
@Autowired
public UserService(OrderService orderService) { ... }
```

相比：

```java
@Resource
public UserService(OrderService orderService) { ... }
```

- `@Autowired` 更契合 Spring 的类型匹配、容器特性以及各种扩展（如 `@Qualifier`）；
- `@Resource` 虽然能用，但在“构造函数 + 多 Bean + 条件装配”等高级玩法中，不如 `@Autowired` 生态成熟、示例丰富。

因此综合下来：

> **Spring 场景下，构造函数注入 + `@Autowired` 是最自然、最主流、可读性与可维护性都最好的组合。**

## 实践建议总结

如果你在写 Spring / Spring Boot 项目，可以直接按下面这套习惯来：

1. **默认使用构造函数注入**，不要字段注入；
2. 依赖字段全部用 `private final`；
3. 配合 Lombok：
   - Spring 4.3+ 可不写 `@Autowired`；
   - 如果你们团队要求显式，也可以在生成的构造上加
4. 只有在需要**可选依赖**（某些 Bean 可能不存在）或**运行时替换依赖**时，再考虑 Setter 注入；
5. 需要与 Java 标准/其他容器兼容时，可以灵活使用 `@Resource`，但主线仍以 `@Autowired` 为主。
