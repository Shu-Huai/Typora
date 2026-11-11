# SpringBoot（Spring）中为什么不推荐使用 @Autowired

## 回答重点

准确说不是不推荐用 `@Autowired`，而是不推荐用 **`@Autowired` 字段注入**。Spring 官方文档明确推荐的是构造器注入。

因为字段注入可能会触发空指针问题、且对单元测试不友好，并且会掩盖循环依赖问题。

还有，`@Autowired` 是 Spring 提供的注解，导致业务代码和框架强绑定；如果更换为其他 IOC 框架则不适用。而 `@Resource` 是 JSR-250 提供的 Java 标准注解，因此如果非要使用字段注入，也应该使用 `@Resource`。

字段注入的问题在于：依赖是在对象创建之后才被“偷偷”塞进去的，所以会带来一些问题（详细看扩展知识）。

![](Z:/Public/images/vbcQE12N_mdE8bpmK7n_mianshiya.webp)

## 扩展知识

### 字段注入的几个坑

**构造器里访问注入字段会空指针**

```java
@Service
public class OrderService {
    
    @Autowired
    private UserService userService;
    
    private String defaultUser;

    public OrderService() {
        // 这里 userService 还是 null，直接炸
        this.defaultUser = userService.getDefaultUser();
    }
}
```

字段注入发生在构造器执行之后，所以构造器里访问被注入的字段必定是 null。构造器注入就没这个问题，依赖在构造器参数里直接传进来，随便用。

**单元测试变得很麻烦**

字段注入的依赖是 `private` 的，外部没法直接设置。想写单元测试就得启动整个 Spring 容器，或者用反射去塞 mock 对象，很别扭。

```java
// 字段注入，测试很难搞
@Test
void testOrder() {
    OrderService service = new OrderService();
    // userService 是 null，没法测
}

// 构造器注入，直接 new 就能测
@Test
void testOrder() {
    UserService mockUser = Mockito.mock(UserService.class);
    OrderService service = new OrderService(mockUser, mockProduct);
    // 正常测试
}
```

**掩盖循环依赖问题**

Spring 的三级缓存能解决字段注入的循环依赖，但这其实是在“纵容”不良设计。构造器注入遇到循环依赖直接启动失败，逼着你去重构设计。

- [578. Spring 如何解决循环依赖？](https://www.mianshiya.com/question/1780933295383539714)

**容易违反单一职责原则**

字段注入太方便了，加个 `@Autowired` 就行，不知不觉一个类就注入了十几个依赖。构造器注入的话，参数列表一长你自己就觉得难受，会主动考虑是不是该拆分职责了。

![](Z:/Public/images/w8dd7TFf_TZBzqxLGel_mianshiya.webp)

### `@Autowired` 和 `@Resource` 的区别

`@Autowired` 是 Spring 自己的注解，按类型匹配。`@Resource` 是 Java 标准 JSR-250 定义的，按名称匹配。

```java
// @Autowired 按类型，多个实现要配合 @Qualifier
@Autowired
@Qualifier("mysqlUserService")
private UserService userService;

// @Resource 默认按名称
@Resource(name = "mysqlUserService")
private UserService userService;
```

如果团队坚持用字段注入，用 `@Resource` 比 `@Autowired` 好一点，至少代码没有和 Spring 框架强绑定，换成其他 IOC 容器理论上也能跑。

### 用 Lombok 简化构造器注入

构造器注入的缺点就是代码多，依赖一多构造器很长。用 Lombok 的 `@RequiredArgsConstructor` 可以省掉样板代码：

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    
    private final UserService userService;
    private final ProductService productService;
    
    // Lombok 自动生成构造器
}
```

只要把依赖字段声明为 final，Lombok 会自动生成包含这些字段的构造器。代码量和字段注入差不多，但享受构造器注入的所有好处。

### Spring 4.3 以后的隐式构造器注入

Spring 4.3 开始，如果类只有一个构造器，`@Autowired` 可以省略不写，Spring 自动用这个构造器注入：

```java
@Service
public class OrderService {
    
    private final UserService userService;

    // 不用写 @Autowired，Spring 自动识别
    public OrderService(UserService userService) {
        this.userService = userService;
    }
}
```

如果有多个构造器，需要在想用的那个上面加 `@Autowired` 告诉 Spring。

## 面试官追问

#### 提问：构造器注入遇到循环依赖怎么办？

回答：构造器注入的循环依赖没法用三级缓存解决，应用直接启动失败。解决办法要么重构设计打破循环，要么在其中一个依赖上加 `@Lazy` 延迟加载，等到真正调用时才创建。但 `@Lazy` 只是绕过问题，循环依赖本身说明设计有问题，最好还是拆分职责。

#### 提问：Setter 注入和构造器注入怎么选？

回答：优先构造器注入，强制依赖在对象创建时就必须提供，保证对象始终处于完整可用状态。Setter 注入适合可选依赖，就是那种有就用、没有也能跑的场景。Spring 官方也是推荐构造器注入处理必需依赖，Setter 注入处理可选依赖。

#### 提问：为什么说构造器注入保证了不可变性？

回答：构造器注入配合 final 字段，依赖在对象创建时就定死了，后续没法改。字段注入的依赖不能声明 final，理论上运行时还能被反射修改。不可变性对并发安全很重要，一个对象的依赖在整个生命周期都不会变，就不用担心多线程下依赖被换掉的问题。

#### 提问：有的老项目全是字段注入，要不要改成构造器注入？

回答：看情况，别为了改而改。字段注入能跑就行，没出问题不用大规模重构。新写的代码用构造器注入就好。如果要改，配合 Lombok 的 `@RequiredArgsConstructor` 改起来很快，但要注意测试覆盖，别改出问题来。
