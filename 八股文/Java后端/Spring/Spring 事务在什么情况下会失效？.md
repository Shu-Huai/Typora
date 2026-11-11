# Spring 事务在什么情况下会失效？

## 回答重点

Spring 事务失效的场景主要围绕声明式事务，即使用 `@Transactional` 注解。

事务失效的核心原因就一个：**事务是靠 AOP 代理实现的**，**凡是绕过代理或者代理机制本身搞不定的情况，事务就会失效**。

常见的失效场景有 8 种：

1. rollbackFor 没设置对，比如默认没有任何设置（RuntimeException 或者 Error 才能捕获），则方法内抛出 IOException 则不会回滚，需要配置 `@Transactional(rollbackFor = Exception.class)`。

2. 异常被捕获了，比如代码抛错，但是被 catch 了，仅打了 log 没有抛出异常，这样事务无法正常获取到错误，因此不会回滚。

3. 同一个类中方法调用，因此事务是基于动态代理实现的，同类的方法调用不会走代理方法，因此事务自然就失效了。

4. @Transactional 应用在非 public 修饰的方法上，Spring 事务管理器判断非公共方法则不应用事务。

![image.png](Z:/Public/images/CQfM5yy7_image_mianshiya.webp)

5. @Transactional 应用在 final 和 static 方法上，因为 aop （Spring Boot2.x版本默认是 cglib，Spring 自身默认是 jdk，一般现在用的都是 SpringBoot）默认是 cglib 代理，无法对 final 方法子类化。static 是静态方法，属于类，不属于实例对象，无法被代理！

6. propagation 传播机制配置错误，例如以下的代码（伪代码，忽略同一个类中的方法调用影响代理的情况）

```java
@Transactional(propagation = Propagation.REQUIRES_NEW, rollbackFor = Exception.class)
public void addUserAndAddress(User user,Address address) throws Exception {
    userMapper.save(user);
    addAddress(address);
}

@Transactional(propagation = Propagation.REQUIRES_NEW, rollbackFor = Exception.class)
public void addAddress(Address address) {
    addressMapper.save(address);
}
```

因为配置了 Propagation.REQUIRES_NEW，是新起了一个事务，即 addAddress 的事务和 addUserAndAddress 其实不是一个事务，因此两个事务之间当然就无法保证数据的一致性了。

7. 多线程环境，因为 @Transactional 是基于 ThreadLocal 存储上下文的，多线程情况下每个线程都有自己的上下文，那么之间如何保持事务同步？保持不了，因此事务失效。

8. 用的是 MySQL MyISAM，这个引擎本身不支持事务!

## 扩展知识

### 同类方法调用的解决方案

这个坑太常见了，写个 Service 类，A 方法调 B 方法，B 上面加了 @Transactional，结果事务不生效。

```java
@Service
public class OrderService {
    public void createOrder(Order order) {
        // 直接调用，不走代理
        this.saveOrder(order);
    }
    
    @Transactional
    public void saveOrder(Order order) {
        orderMapper.insert(order);
        // 这里抛异常不会回滚
    }
}
```

解决方案有 3 种：

1. **注入自己**：把 OrderService 注入到自己里面，通过注入的引用调用

```java
@Service
public class OrderService {
    @Autowired
    private OrderService self;  // 注入代理对象
    
    public void createOrder(Order order) {
        self.saveOrder(order);  // 走代理
    }
}
```

2. 从 `ApplicationContext` 里手动获取 Bean

3. 用 `AopContext.currentProxy()` 获取当前代理对象，需要配置 exposeProxy = true

```java
@EnableAspectJAutoProxy(exposeProxy = true)
@SpringBootApplication
public class Application { }

// 使用
((OrderService) AopContext.currentProxy()).saveOrder(order);
```

### rollbackFor 的默认行为

Spring 事务默认只回滚 **RuntimeException** 和 **Error**，受检异常不回滚。这个设计是故意的，Spring 认为受检异常是业务预期内的情况，需要开发者自己决定怎么处理。

```java
// 不会回滚，IOException 是受检异常
@Transactional
public void uploadFile() throws IOException {
    saveRecord();
    throw new IOException("上传失败");
}

// 会回滚
@Transactional(rollbackFor = Exception.class)
public void uploadFile() throws IOException {
    saveRecord();
    throw new IOException("上传失败");
}
```

实际项目建议统一配置 rollbackFor = Exception.class，省得某天漏了受检异常导致数据不一致。也可以在全局配置：

```java
@Configuration
public class TransactionConfig {
    @Bean
    public TransactionAttributeSource transactionAttributeSource() {
        RuleBasedTransactionAttribute attr = new RuleBasedTransactionAttribute();
        attr.setRollbackRules(List.of(new RollbackRuleAttribute(Exception.class)));
        
        MatchAlwaysTransactionAttributeSource source = new MatchAlwaysTransactionAttributeSource();
        source.setTransactionAttribute(attr);
        return source;
    }
}
```

### 传播机制的坑

![](Z:/Public/images/zkyazPSe_aJIcFFAQ2V_mianshiya.webp)

最容易出问题的是 REQUIRES_NEW：

```java
@Transactional
public void outer() {
    userMapper.insert(user);
    
    try {
        inner();  // 伪代码，忽略同一个类中的方法调用影响代理的情况
    } catch (Exception e) {
        // 内层回滚了，外层捕获异常继续执行
    }
    
    orderMapper.insert(order);  // 这行还会执行
}

@Transactional(propagation = Propagation.REQUIRES_NEW)
public void inner() {
    pointMapper.insert(point);
    throw new RuntimeException();  // 只回滚 inner 事务
}
```

user 和 order 会插入成功，point 会回滚。如果你期望三个一起成功或一起失败，那这个设计就是有问题的。

### 多线程事务的处理

@Transactional 靠 ThreadLocal 传递事务上下文，新线程拿不到：

```java
@Transactional
public void batchProcess(List<Order> orders) {
    orders.parallelStream().forEach(order -> {
        // 这里是新线程，没有事务上下文
        orderMapper.insert(order);
    });
}
```

解决方案：

1. 不用多线程，老老实实单线程处理

2. 用编程式事务，手动在每个线程里开事务

3. 用分布式事务框架，比如 Seata

实际上大部分需要多线程的场景，往往也意味着数据量大，这时候更应该考虑批量操作或者分批次处理，而不是在一个事务里塞几万条数据。

### 事务超时

@Transactional 有个 timeout 参数，单位是秒：

```java
@Transactional(timeout = 30)
public void longRunningTask() {
    // 超过 30 秒会抛 TransactionTimedOutException
}
```

注意这个超时只在事务开始时生效，如果 SQL 执行时间超过了，得靠数据库的锁超时机制来处理。而且只有在执行下一个 SQL 或者提交时才会检查超时，不是精确卡点的。

## 面试官追问

#### 提问：同类方法调用为什么会绕过代理？

回答：Spring 的事务是通过 AOP 代理实现的，调用方拿到的是代理对象，代理对象拦截方法调用后织入事务逻辑。但是在类内部用 this 调用另一个方法时，this 指向的是原始对象不是代理对象，直接走了原始方法，代理压根没机会介入。这是 AOP 代理模式的固有限制，不单是事务，所有 AOP 功能在同类调用时都有这个问题。

#### 提问：CGLIB 和 JDK 动态代理在事务上有什么区别？

回答：JDK 代理只能代理接口，CGLIB 代理是通过继承目标类生成子类。Spring Boot 2.`x` 默认用 CGLIB。区别主要在于：JDK 代理要求目标类必须实现接口，CGLIB 不需要；CGLIB 代理不了 final 方法和 final 类，JDK 代理不受这个限制因为它代理的是接口。事务行为上两者没本质区别，都是在方法调用前后织入事务管理逻辑。

#### 提问：@Transactional 加在接口上有效吗？

回答：有效，但不推荐。Spring 官方文档明确建议只在具体类和方法上加 @Transactional。原因是如果用 CGLIB 代理，接口上的注解可能不会被识别，导致行为不一致。另外接口可能有多个实现类，事务配置应该跟着具体实现走，放接口上容易造成混乱。

#### 提问：事务回滚后，自增 ID 会回退吗？

回答：不会。MySQL 的自增 ID 分配发生在插入时，即使事务回滚，已经分配的 ID 也不会回收。这是为了避免并发场景下的 ID 冲突。所以回滚后 ID 会出现空洞，比如插了 1、2、3，回滚后再插就是 4，3 这个 ID 永远没了。高并发系统如果频繁回滚，ID 增长会比实际数据量快很多，需要评估 bigint 够不够用。
