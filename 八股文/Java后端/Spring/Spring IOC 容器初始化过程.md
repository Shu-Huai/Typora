# Spring IOC 容器初始化过程

## 回答重点

先和面试官说一共有四个阶段，分别是启动、Bean 定义注册、实例化和依赖注入、初始化，然后停顿下，如果面试官示意你继续，然后再细化讲解每个阶段的细节。

1. **启动阶段**

加载配置文件或配置类，可以是 XML、JavaConfig 或注解。

然后创建 `ApplicationContext` 容器实例，比如 AnnotationConfigApplicationContext 或 ClassPathXmlApplicationContext，调用它的 refresh() 方法启动整个容器。

2. **Bean 定义注册阶段**

BeanDefinitionReader 读取配置，把每个 Bean 的元信息解析成 BeanDefinition 对象，包含类名、作用域、依赖关系、初始化方法等。

然后注册到 `BeanDefinitionRegistry` 里，形成一个 Bean 定义的注册表。这个阶段只是“登记”，还没真正创建对象。

3. **实例化和依赖注入阶段**

根据 BeanDefinition 创建 Bean 实例。如果是单例且非懒加载，容器启动时就创建；如果是原型或懒加载，用到的时候才创建。

实例化完成后，根据 BeanDefinition 里的依赖关系，通过构造函数注入、Setter 注入或字段注入把依赖塞进去。

4. **初始化阶段**

依赖注入完成后进入初始化阶段，执行顺序是：

- 如果实现了 `Aware` 接口，回调对应方法（如 `BeanNameAware`、`BeanFactoryAware`）

- `BeanPostProcessor` 的 `postProcessBeforeInitialization`

- `@PostConstruct` 标注的方法

- `InitializingBean` 的 `afterPropertiesSet` 方法

- 配置里指定的 `initMethod`

- `BeanPostProcessor` 的 `postProcessAfterInitialization`

![image.png](Z:/Public/images/OOYVtQdx_image_mianshiya.webp)

## 扩展知识

### refresh() 方法详解

整个容器初始化的核心就是 `AbstractApplicationContext` 的 `refresh()` 方法，这是 Spring 框架最重要的方法之一，面试被问到概率很高。

```java
public void refresh() throws BeansException, IllegalStateException {
    // 1. 准备刷新上下文
    prepareRefresh();
    // 2. 获取 BeanFactory，加载 BeanDefinition
    ConfigurableListableBeanFactory beanFactory = obtainFreshBeanFactory();
    // 3. 配置 BeanFactory
    prepareBeanFactory(beanFactory);
    // 4. 子类扩展点
    postProcessBeanFactory(beanFactory);
    // 5. 执行 BeanFactoryPostProcessor
    invokeBeanFactoryPostProcessors(beanFactory);
    // 6. 注册 BeanPostProcessor
    registerBeanPostProcessors(beanFactory);
    // 7. 初始化消息源
    initMessageSource();
    // 8. 初始化事件广播器
    initApplicationEventMulticaster();
    // 9. 子类扩展点，SpringBoot 在这里启动内嵌 Tomcat
    onRefresh();
    // 10. 注册监听器
    registerListeners();
    // 11. 实例化所有非懒加载的单例 Bean
    finishBeanFactoryInitialization(beanFactory);
    // 12. 发布容器刷新完成事件
    finishRefresh();
}
```

关键步骤解释：

**obtainFreshBeanFactory**：创建 BeanFactory，加载所有 BeanDefinition。如果是 XML 配置就用 XmlBeanDefinitionReader 解析，如果是注解配置就用 AnnotatedBeanDefinitionReader。

**invokeBeanFactoryPostProcessors**：执行所有 BeanFactoryPostProcessor，这是容器级别的扩展点。最重要的是 ConfigurationClassPostProcessor，它负责解析 @Configuration、@ComponentScan、@Import 等注解，把扫描到的类注册成 BeanDefinition。

**registerBeanPostProcessors**：把所有 BeanPostProcessor 注册到容器，为后面 Bean 的初始化做准备。AOP 的 AnnotationAwareAspectJAutoProxyCreator 就是在这里注册的。

**finishBeanFactoryInitialization**：实例化所有非懒加载的单例 Bean，这一步干的活最多，依赖注入和初始化都在这里完成。

![](Z:/Public/images/e4hEjGCO_qDXVDqEDeJ_mianshiya.webp)

### BeanDefinition 包含哪些信息

BeanDefinition 是 Bean 的元数据描述，理解它对理解 IOC 容器很重要。

| 属性 | 说明 |
| --- | --- |
| `beanClassName` | Bean 的全限定类名 |
| `scope` | 作用域，如 `singleton` 或 `prototype` |
| `lazyInit` | 是否懒加载 |
| `dependsOn` | 依赖的 Bean 名称 |
| `autowireCandidate` | 是否作为自动装配的候选 |
| `primary` | 是否是首选 Bean |
| `initMethodName` | 初始化方法名 |
| `destroyMethodName` | 销毁方法名 |
| `constructorArgumentValues` | 构造函数参数 |
| `propertyValues` | 属性值 |

### Aware 接口回调顺序

如果 Bean 实现了多个 Aware 接口，回调顺序是固定的：

1. `BeanNameAware`：拿到 Bean 在容器中的名字
2. `BeanClassLoaderAware`：拿到加载 Bean 的 `ClassLoader`
3. `BeanFactoryAware`：拿到 `BeanFactory` 实例
4. `EnvironmentAware`：拿到 `Environment`，能读配置
5. `ApplicationContextAware`：拿到 `ApplicationContext`

前 3 个在 AbstractAutowireCapableBeanFactory 里回调，后面的通过 ApplicationContextAwareProcessor 这个 BeanPostProcessor 回调。

### 循环依赖是在哪个阶段解决的

循环依赖发生在实例化和依赖注入阶段。Spring 用三级缓存来解决单例 Bean 的循环依赖：

1. `singletonObjects`：一级缓存，存放完全初始化好的单例 Bean
2. `earlySingletonObjects`：二级缓存，存放提前曝光的 Bean，已实例化但未初始化
3. `singletonFactories`：三级缓存，存放 Bean 的工厂对象，用于创建代理

流程是这样的：A 依赖 B，B 依赖 A。创建 A 时先实例化，把工厂放进三级缓存，然后注入依赖发现需要 B。创建 B，实例化后注入依赖发现需要 A，从三级缓存拿到 A 的工厂，创建早期引用放进二级缓存，B 就能完成初始化了。然后回到 A，从一级缓存拿到完整的 B，A 也能完成初始化。

## 面试官追问

#### 提问：BeanFactoryPostProcessor 和 BeanPostProcessor 有什么区别？

回答：BeanFactoryPostProcessor 在所有 BeanDefinition 加载完成后、Bean 实例化之前执行，能修改 BeanDefinition，比如 PropertySourcesPlaceholderConfigurer 就是用它来替换 ${} 占位符的。BeanPostProcessor 在 Bean 实例化之后执行，能修改 Bean 实例，AOP 的代理就是通过它实现的。一个改配置，一个改实例。

#### 提问：@PostConstruct 为什么比 afterPropertiesSet 先执行？

回答：因为 @PostConstruct 是通过 CommonAnnotationBeanPostProcessor 这个 BeanPostProcessor 处理的，它在 postProcessBeforeInitialization 阶段执行。而 afterPropertiesSet 是在 invokeInitMethods 阶段执行，在 postProcessBeforeInitialization 之后。所以 @PostConstruct 先执行。

#### 提问：容器启动时 Bean 创建的顺序是怎么确定的？

回答：主要看依赖关系。Spring 会按拓扑排序来创建 Bean，被依赖的先创建。如果 A 依赖 B，那 B 先创建。可以用 @DependsOn 注解显式指定依赖顺序。另外 @Order 注解只影响同类型 Bean 注入到集合时的顺序，不影响创建顺序。
