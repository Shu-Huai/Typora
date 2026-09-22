# @Async 注解的原理是什么？ - 面试鸭 | 2026最新面试题+详细答案解析

## 回答重点

@Async 的核心原理就是 **AOP 动态代理 + 线程池**。

Spring 在启动时扫描到 @Async 注解的方法，会给对应的 Bean 生成一个代理对象。调用这个方法时，代理拦截请求，把实际执行逻辑包装成一个任务丢进线程池，主线程直接返回，任务在后台线程跑。

看个简单例子：

```java
@Service
public class NotifyService {
    @Async
    public void sendEmail(String to) {
        // 耗时操作，比如调用邮件服务器
        mailClient.send(to, "订单确认", body);
    }
}

// 调用方
orderService.createOrder(order);
notifyService.sendEmail(user.getEmail()); // 不阻塞，立即返回
```

调用 sendEmail 时，走的是代理对象，代理会把真正的 sendEmail 逻辑封装成 Runnable 丢给线程池执行，调用方压根不用等邮件发完。

底层执行流程：调用方调用 sendEmail → 代理对象拦截 → 创建任务包装原方法 → 提交到线程池 → 主线程直接返回 → 线程池中的工作线程执行真正的 sendEmail 逻辑

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/tEALstU4_image_mianshiya.webp)

## 扩展知识

### 默认线程池的坑

Spring 默认用的是 SimpleAsyncTaskExecutor，这玩意每次调用都新建一个线程，不做任何复用。高并发场景下，比如每秒 1000 个异步任务，线程数直接爆掉。生产环境必须自定义线程池：

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(200);
        executor.setThreadNamePrefix("async-");
        executor.setRejectedExecutionHandler(new CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

也可以用 @Bean 声明多个线程池，然后 @Async("ioTaskExecutor") 指定用哪个，IO 密集型和 CPU 密集型任务分开配置。

### 同类调用失效问题

@Async 是 AOP 实现的，内部调用会绕过代理，直接走原对象方法，异步失效。这是 Spring AOP 的通病，不光 @Async，@Transactional 也一样。

```java
@Service
public class OrderService {
    public void process() {
        this.asyncTask(); // 直接调自己，不走代理，同步执行！
    }

    @Async
    public void asyncTask() { ... }
}
```

解决办法有两种：

1）自注入，把自己注入进来，用代理对象调用：

```java
@Service
public class OrderService {
    @Lazy
    @Autowired
    private OrderService self;

    public void process() {
        self.asyncTask(); // 走代理，异步生效
    }
}
```

2）暴露代理对象。但 @EnableAsync 生成代理的方式特殊，@EnableAspectJAutoProxy(exposeProxy = true) 对它不生效，需要额外配置：

```java
@Component
public class AsyncProxyExposer implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory factory) {
        BeanDefinition def = factory.getBeanDefinition(
            TaskManagementConfigUtils.ASYNC_ANNOTATION_PROCESSOR_BEAN_NAME);
        def.getPropertyValues().add("exposeProxy", true);
    }
}
// 然后用 AopContext.currentProxy() 获取代理对象
```

### 异常处理

异步方法抛异常，调用方是捕获不到的，因为执行在另一个线程。Spring 提供了 AsyncUncaughtExceptionHandler 来兜底：

```java
@Override
public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
    return (ex, method, params) -> {
        log.error("异步任务异常: method={}, params={}", method.getName(), params, ex);
        // 发告警、写日志等
    };
}
```

如果方法返回 Future/CompletableFuture，异常会包在 Future 里，调用方 get 时能拿到。

**总结图**：

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/AGYyJCE4_DEbcstPOp1_mianshiya.webp)

## 面试官追问

#### 提问：@Async 方法返回 void 和返回 Future 有什么区别？用哪个更好？

回答：返回 void 就是纯异步，调用方完全不关心结果，发完就走。返回 Future 或 CompletableFuture 可以让调用方在需要时 get 拿结果，也能捕获异常。一般业务里如果后续要等结果或者做编排，用 CompletableFuture；纯通知类的场景，比如发邮件、记日志，void 就够了。

#### 提问：为什么说默认的 SimpleAsyncTaskExecutor 不推荐用？

回答：它压根没有线程复用，每次提交任务都 new Thread()，一秒来 1000 个请求就创建 1000 个线程。线程创建销毁本身有开销，更要命的是线程数没有上限，高并发直接 OOM 或者系统线程数打满。生产环境必须用有界线程池，控制核心线程、最大线程、队列容量。

#### 提问：如果异步任务执行时间特别长，线程池队列满了怎么办？

回答：看拒绝策略怎么配的。AbortPolicy 直接抛 RejectedExecutionException，任务丢了；CallerRunsPolicy 会让调用线程自己执行，相当于降级成同步；DiscardPolicy 和 DiscardOldestPolicy 是静默丢弃。推荐用 CallerRunsPolicy，至少任务不会丢，也起到限流作用。更稳妥的做法是监控队列长度，提前扩容或者引入消息队列削峰。 ...
