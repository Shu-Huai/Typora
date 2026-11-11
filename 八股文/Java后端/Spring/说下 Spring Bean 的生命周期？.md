# 说下 Spring Bean 的生命周期？

## 回答重点

Spring Bean 的生命周期核心就是 **从创建到销毁的整个过程**，Spring 在这个过程中预留了大量扩展点，让我们能在各个阶段插入自定义逻辑。

一幅图总结：

![](Z:/Public/images/zNxXrxM1_60913d46-9305-41c6-adc6-7787e078b188_mianshiya.webp)

再细分的话，整个流程可以分成这么几个阶段：

1. 实例化：Spring 通过反射调用构造方法创建 Bean 对象，这时候只是个空壳子，属性都还没填

2. 属性注入：通过 setter 方法或字段反射把依赖的其他 Bean 塞进去

3. Aware 接口回调：如果 Bean 实现了 BeanNameAware、BeanFactoryAware、ApplicationContextAware 这些接口，Spring 会把对应的容器信息注入进来

4. BeanPostProcessor 前置处理：所有 BeanPostProcessor 的 postProcessBeforeInitialization 方法会被调用

5. 初始化：按顺序执行 @PostConstruct 注解方法、InitializingBean 的 afterPropertiesSet 方法、@Bean 指定的 initMethod

6. BeanPostProcessor 后置处理：所有 BeanPostProcessor 的 postProcessAfterInitialization 方法会被调用，AOP 代理通常就在这一步生成

7. Bean 就绪：可以被其他组件使用了

8. 销毁：容器关闭时按顺序执行 @PreDestroy 注解方法、DisposableBean 的 destroy 方法、@Bean 指定的 destroyMethod

![image.png](Z:/Public/images/h8wztNqQ_image_mianshiya.webp)

**注意细节，这幅图的颜色和上面那副有对应关系的**。

## 扩展知识

### 为什么要设计这么多扩展点

Spring 之所以把 Bean 创建过程拆得这么细，就是为了让框架有足够的灵活性。比如 AOP 要给 Bean 包一层代理、事务管理器要在方法前后插入逻辑、配置中心要在 Bean 初始化前把配置值注入进去，这些功能都依赖于生命周期扩展点。

如果没有这些扩展点，每个框架都得自己魔改 Spring 源码，那就乱套了。

### BeanPostProcessor 的威力

BeanPostProcessor 是最常用的扩展点，几乎所有 Spring 高级特性都靠它实现：

1. @Autowired 注解的处理是 AutowiredAnnotationBeanPostProcessor 干的

2. @Value 注解从配置文件取值也是通过 BeanPostProcessor

3. AOP 代理对象的创建是 AbstractAutoProxyCreator 在 postProcessAfterInitialization 阶段完成的

写个自定义的 BeanPostProcessor 体验一下：

```java
public class MyBeanPostProcessor implements BeanPostProcessor {

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        if ("circleBean".equals(beanName)) {
            System.out.println("4.初始化之前执行，返回值会替换掉原本的 bean");
        }
        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        if ("circleBean".equals(beanName)) {
            System.out.println("6.初始化之后执行，AOP 代理通常在这里生成");
        }
        return bean;
    }
}
```

![](Z:/Public/images/VRVNWNsT_pWcgluGOWS_mianshiya.webp)

### Bean 作用域对生命周期的影响

不同作用域的 Bean 生命周期管理策略完全不一样：

作用域创建时机销毁时机Spring 是否管理销毁singleton容器启动时容器关闭时是prototype每次 getBean不管否requestHTTP 请求开始请求结束是sessionSession 创建Session 过期是

prototype 作用域比较坑，Spring 只负责创建不负责销毁，如果 Bean 持有数据库连接之类的资源，得自己想办法释放，不然就内存泄漏了。

### 初始化方法的执行顺序

如果一个 Bean 同时配置了多种初始化方式，执行顺序是固定的：

1. @PostConstruct 注解的方法最先执行

2. InitializingBean 接口的 afterPropertiesSet 方法其次

3. @Bean 注解的 initMethod 属性指定的方法最后

销毁方法的顺序也是一样的：@PreDestroy → DisposableBean.destroy → destroyMethod。

这个顺序在 Spring 3.0 之后就没变过，可以放心依赖。

## 面试官追问

#### 提问：BeanFactoryPostProcessor 和 BeanPostProcessor 有什么区别？

回答：执行时机完全不一样。BeanFactoryPostProcessor 是在所有 Bean 定义加载完成后、Bean 实例化之前执行的，它操作的是 BeanDefinition，可以修改 Bean 的元数据，比如 PropertyPlaceholderConfigurer 就是用它来替换配置文件中的占位符。BeanPostProcessor 是在 Bean 实例化之后执行的，它操作的是已经创建好的 Bean 实例，主要用于初始化前后的增强处理。

#### 提问：prototype 作用域的 Bean 为什么 Spring 不管销毁？

回答：设计上的取舍。prototype 每次 getBean 都创建新实例，Spring 不持有这些实例的引用，也就没法在容器关闭时挨个调用销毁方法。如果要管理，Spring 就得额外维护一个集合来跟踪所有 prototype 实例，这样内存开销太大了。官方的建议是让 prototype Bean 的调用方自己负责释放资源，或者用自定义的 BeanPostProcessor 来处理。

#### 提问：@PostConstruct 注解是 Spring 的还是 Java 标准的？

回答：是 Java 标准的，属于 JSR-250 规范，包名是 javax.annotation.PostConstruct。Spring 只是通过 CommonAnnotationBeanPostProcessor 来识别和处理这个注解。不过 Java 9 开始这个包被标记为 deprecated，Java 11 直接移除了，用 Spring Boot 2.`x` 以上版本得自己加 javax.annotation-api 依赖，或者换成 jakarta.annotation-api。

#### 提问：能不能让某个 Bean 在其他所有 Bean 之前初始化？

回答：可以用 @DependsOn 注解反向控制，但这个方法比较笨。更优雅的做法是让这个 Bean 实现 BeanFactoryPostProcessor 接口，因为 BeanFactoryPostProcessor 会在所有普通 Bean 实例化之前被创建和执行。还有一种办法是实现 SmartInitializingSingleton 接口，不过这个是所有单例 Bean 都初始化完之后才回调，跟需求相反。如果是配置类的场景，可以用 @Order 或 Ordered 接口来控制 @Configuration 类的加载顺序。
