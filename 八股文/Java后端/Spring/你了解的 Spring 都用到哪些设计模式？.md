# 你了解的 Spring 都用到哪些设计模式？

## 回答重点

Spring 框架用了十几种设计模式，挑几个核心的说：

**工厂模式**用得最广，整个 IoC 容器就是个大工厂。BeanFactory 和 `ApplicationContext` 的 `getBean()` 方法隐藏了 Bean 的创建细节，调用方不用关心 Bean 是怎么实例化、怎么注入依赖的。

**单例模式**体现在 Bean 的默认作用域上。Spring 容器里相同 ID 的 Bean 默认只创建一份，存在单例池里复用。不过要注意，这和 GoF 定义的单例模式不完全一样，Spring 的单例是容器级别的，多个容器可以有多个实例。

**代理模式**是 AOP 的核心。Spring 通过 JDK 动态代理或 CGLIB 生成代理对象，在不改原代码的情况下织入事务、日志、权限校验这些横切逻辑。

**模板方法模式**体现在 JdbcTemplate、`RestTemplate`、TransactionTemplate 这些类上。它们定义好了操作的骨架流程，把变化的部分抽成回调让使用者实现。

**观察者模式**用在事件机制上。ApplicationEvent 是事件，ApplicationListener 是监听器，ApplicationEventMulticaster 负责广播，典型的发布-订阅实现。

**责任链模式**在 Spring MVC 的拦截器里用到。多个 HandlerInterceptor 串成链，请求按顺序经过每个拦截器处理。

![](Z:/Public/images/NF9Z2wKz_DATcHTTxOZ_mianshiya.webp)

## 扩展知识

### 工厂模式的多层次实现

Spring 里的工厂不只是 BeanFactory 一个，实际上有好几层：

1. BeanFactory 是最底层的容器接口，`getBean()` 方法根据名称或类型返回 Bean 实例，内部根据 BeanDefinition 决定是 new 还是从缓存拿

2. FactoryBean 是用户可以自定义的工厂。如果某个 Bean 的创建过程特别复杂，比如需要读配置文件、调远程接口，直接写在 @Bean 方法里太乱，就可以实现 FactoryBean 接口把创建逻辑封装起来。MyBatis 的 SqlSessionFactoryBean 就是典型例子

3. ObjectFactory 和 ObjectProvider 是延迟创建工厂。注入的时候不立即创建 Bean，调用 `getObject()` 的时候才真正创建。这两个主要用来解决循环依赖和单例注入多例的问题

```java
// FactoryBean 示例
public class DataSourceFactoryBean implements FactoryBean<DataSource> {
    @Override
    public DataSource getObject() {
        HikariDataSource ds = new HikariDataSource();
        // 复杂的初始化逻辑...
        return ds;
    }
    
    @Override
    public Class<?> getObjectType() {
        return DataSource.class;
    }
}

// ObjectProvider 解决单例注入多例
@Component
public class SingletonService {
    @Autowired
    private ObjectProvider<PrototypeBean> prototypeBeanProvider;
    
    public void doSomething() {
        // 每次调用都拿到新的实例
        PrototypeBean bean = prototypeBeanProvider.getObject();
    }
}
```

### 适配器模式在 Spring MVC 的妙用

Spring MVC 支持好几种 Controller 写法：用 @RequestMapping 注解的、实现 Controller 接口的、实现 HttpRequestHandler 的。这些 Controller 的方法签名完全不一样，DispatcherServlet 没法直接调用。

HandlerAdapter 就是来解决这个问题的。每种 Controller 对应一个适配器：

![](Z:/Public/images/UrMa9dzx_TxzrepyT0M_mianshiya.webp)

DispatcherServlet 拿到 Handler 后，遍历所有 HandlerAdapter 问“你能处理这个 Handler 吗”，能处理的就让它调用。这样不管 Controller 怎么写，DispatcherServlet 的代码都不用改。

AOP 里也有类似的设计。@Before、@After、@AfterReturning 这些通知内部实现不一样，但最终都得适配成 MethodInterceptor 才能放进拦截器链统一执行。MethodBeforeAdviceAdapter 把前置通知适配成 MethodBeforeAdviceInterceptor，AfterReturningAdviceAdapter 把返回通知适配成 AfterReturningAdviceInterceptor。

### 组合模式集中管理同类组件

Spring MVC 处理请求参数的时候，有几十种 HandlerMethodArgumentResolver 实现，处理 @RequestParam、@PathVariable、@RequestBody 等不同注解。如果每次都遍历所有 Resolver 挨个问，代码会很乱。

Spring 搞了个 HandlerMethodArgumentResolverComposite，把所有 Resolver 装进去统一管理。外部调用 Composite 的方法，内部再委托给具体的 Resolver 处理。

```java
// 组合模式的核心思想
public class HandlerMethodArgumentResolverComposite 
        implements HandlerMethodArgumentResolver {
    
    private final List<HandlerMethodArgumentResolver> resolvers = new ArrayList<>();
    
    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return getArgumentResolver(parameter) != null;
    }
    
    @Override
    public Object resolveArgument(...) {
        HandlerMethodArgumentResolver resolver = getArgumentResolver(parameter);
        return resolver.resolveArgument(...);
    }
}
```

同样的套路还有 ViewResolverComposite、HandlerExceptionResolverComposite。组合模式的好处是调用方只跟 Composite 打交道，具体有多少个实现、怎么选择，全封装在里面了。

### 模板方法和回调的配合

JdbcTemplate 是模板方法的经典案例。数据库操作的套路是固定的：获取连接、创建 Statement、执行 SQL、处理结果集、释放资源。变化的只是具体执行什么 SQL、怎么处理结果。

```java
// JdbcTemplate 内部的模板方法
public <T> T execute(ConnectionCallback<T> action) {
    Connection con = DataSourceUtils.getConnection(dataSource);  // 固定步骤
    try {
        return action.doInConnection(con);  // 可变部分：回调
    } catch (SQLException ex) {
        throw translateException(ex);  // 固定步骤
    } finally {
        DataSourceUtils.releaseConnection(con, dataSource);  // 固定步骤
    }
}
```

使用者只需要传个 Lambda 告诉 JdbcTemplate 具体要干啥，连接管理、异常处理、资源释放全不用操心。AbstractApplicationContext 的 `refresh()` 方法也是一样，定义了容器启动的 12 个步骤，子类可以重写其中某些步骤来定制行为。

## 面试官追问

#### 提问：Spring 的单例 Bean 和设计模式里的单例模式有什么区别？

回答：设计模式的单例是类级别的，一个 JVM 里只有一个实例，通常通过私有构造器加静态方法实现。Spring 的单例是容器级别的，同一个容器里相同 ID 的 Bean 只有一个，但不同容器可以各有一份。多数据源场景下同一个 DataSource 类可能有好几个实例，每个对应不同的数据库。真正的单例模式在 Spring 里也有，比如 TruePointcut.INSTANCE、OrderComparator.INSTANCE，这些是类内部用 static final 定死的。

#### 提问：装饰器和代理模式看着很像，Spring 里怎么区分它们？

回答：核心区别在意图。装饰器是给对象加功能，代理是控制对象的访问。Spring 里 ContentCachingRequestWrapper 是装饰器，它包装了原始 Request，加了缓存请求体的功能，但不限制你访问原始 Request。JdkDynamicAopProxy 是代理，它拦截方法调用来插入切面逻辑，你根本接触不到真正的目标对象。简单说，装饰器是“我帮你做更多”，代理是“你得通过我才能访问”。

#### 提问：责任链模式在 Spring 里除了拦截器还有哪里用到？

回答：AOP 的拦截器链也是责任链。多个切面作用在同一个方法上时，Spring 把它们组织成 MethodInterceptor 链，通过 MethodInvocation 的 proceed() 方法依次调用。还有 Spring Security 的过滤器链，十几个 Filter 串成 FilterChainProxy，每个负责一种安全检查。这些场景的共同点是，多个处理者都可能处理请求，但最终只需要一个统一的入口来触发整条链。
