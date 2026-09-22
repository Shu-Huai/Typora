# JDK 动态代理和 CGLIB 动态代理有什么区别？ - 面试鸭 | 2026最新27 届校招 Java 热题+详细答案解析

## 回答重点

**JDK 动态代理**基于接口，代理类必须实现至少一个接口，通过 `Proxy.newProxyInstance()` 生成代理对象，底层靠反射调用目标方法。

**CGLIB** 基于 ASM 字节码生成工具，通过继承目标类生成子类来实现代理，所以不需要接口，但 final 类和 final 方法没法代理。

JDK 动态代理：代理类实现目标接口，持有目标对象引用，方法调用时通过 InvocationHandler 转发，最终用反射调用目标方法。

CGLIB 代理：代理类继承目标类，重写非 final 方法，方法调用时通过 MethodInterceptor 拦截，可以用 invokeSuper 直接调用父类方法，不走反射。

![jdkdaili.drawio.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/l3Gp7nSS_jdkdaili.drawio_mianshiya.webp)

性能方面，随着 JDK 版本演进差距已经很小了。以下内容取自：[haiq的博客](https://www.cnblogs.com/haiq/p/4304615.html)

>

- jdk6 下，在运行次数较少的情况下，jdk动态代理与 cglib 差距不明显，甚至更快一些；而当调用次数增加之后， cglib 表现稍微更快一些

- jdk7 下，情况发生了逆转！在运行次数较少（1,000,000）的情况下，jdk动态代理比 cglib 快了差不多30%；而当调用次数增加之后(50,000,000)， 动态代理比 cglib 快了接近1倍

- jdk8 表现和 jdk7 基本一致

## 扩展知识

### JDK 动态代理原理

JDK 动态代理用 `java.lang.reflect.Proxy` 类和 `InvocationHandler` 接口实现，核心流程是这样的：

1）通过实现 InvocationHandler 接口得到一个切面类
2）利用 Proxy 根据目标类的类加载器、接口和切面类得到一个代理类
3）代理类把所有接口方法的调用转发到切面类的 invoke() 方法上，然后根据反射调用目标方法

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/7Kq9cyjO_image_mianshiya.webp)

再深一点点，代理类会在静态块中通过反射把所有方法都拿到存在静态变量中，大致长这样：

![image-20210228112223174.png](https://pic.code-nav.cn/mianshiya/question_picture/1783397053004488705/image-20210228112223174_mianshiya.webp)

来看个完整示例：

```java
// 接口
public interface Service {
    void perform();
}

// 需要被代理的实现类
public class ServiceImpl implements Service {
    @Override
    public void perform() {
        System.out.println("执行业务逻辑");
    }
}

// InvocationHandler 实现
public class ServiceInvocationHandler implements InvocationHandler {
    private final Object target;

    public ServiceInvocationHandler(Object target) {
        this.target = target;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("Before method invoke");
        Object result = method.invoke(target, args);
        System.out.println("After method invoke");
        return result;
    }
}

// 创建代理
Service target = new ServiceImpl();
Service proxy = (Service) Proxy.newProxyInstance(
        target.getClass().getClassLoader(),
        target.getClass().getInterfaces(),
        new ServiceInvocationHandler(target)
);
proxy.perform();
```

### CGLIB 代理原理

CGLIB 基于 ASM 字节码操作库，通过继承目标类生成子类来实现代理。因为是继承，所以不需要目标类实现接口，但 final 类、final 方法、private 方法都没法代理。

CGLIB 生成的代理类会为每个方法创建两个方法：一个是重写的方法用来拦截调用，一个是 `CGLIB$xxx$0` 这种命名的方法用来调用父类原始方法。`MethodProxy.invokeSuper()` 就是调用后者，绕过了反射，直接方法调用，所以早期版本 CGLIB 调用性能比 JDK 动态代理好。

```java
// 目标类，不需要接口
public class Service {
    public void perform() {
        System.out.println("执行业务逻辑");
    }
}

// MethodInterceptor 实现
public class ServiceMethodInterceptor implements MethodInterceptor {
    @Override
    public Object intercept(Object obj, Method method, Object[] args, MethodProxy proxy) throws Throwable {
        System.out.println("Before method invoke");
        Object result = proxy.invokeSuper(obj, args);  // 直接调用父类方法，不走反射
        System.out.println("After method invoke");
        return result;
    }
}

// 创建代理
Enhancer enhancer = new Enhancer();
enhancer.setSuperclass(Service.class);
enhancer.setCallback(new ServiceMethodInterceptor());
Service proxy = (Service) enhancer.create();
proxy.perform();
```

### 核心区别对比

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/Pp7fME63_eyoXZgDWdG_mianshiya.webp)

### Spring 中的选择策略

Spring AOP 会根据目标类自动选择代理方式：

1）目标类实现了接口，默认用 JDK 动态代理
2）目标类没有接口，自动切换到 CGLIB
3）强制使用 CGLIB 可以配置 `@EnableAspectJAutoProxy(proxyTargetClass = true)`

Spring Boot 2.x 之后默认全用 CGLIB，原因是不用强制写接口，开发体验更好。如果想切回 JDK 代理：

```yaml
spring:
  aop:
    proxy-target-class: false
```

### 常见坑点

1）JDK 代理返回的对象只能转成接口类型，写成 `(ServiceImpl) proxy` 会抛 ClassCastException

2）CGLIB 代理的类必须有无参构造器，因为要实例化子类

3）被代理对象内部 this 调用不走代理。比如 A 方法里调 this.B()，B 方法上的切面不生效

4）CGLIB 在 JDK 17+ 因为模块化限制，需要额外的启动参数才能正常工作

## 面试官追问

#### 提问：为什么 JDK 动态代理必须要有接口？

回答：因为 JDK 动态代理生成的代理类已经继承了 `java.lang.reflect.Proxy` 这个类，Java 又不支持多继承，所以只能通过实现接口的方式来代理目标类。代理类和目标类之间唯一的纽带就是共同实现的接口。

#### 提问：CGLIB 的 MethodProxy.invoke 和 invokeSuper 有什么区别？

回答：`invoke(target, args)` 是调用传入对象的方法，如果传的是代理对象自己就会死循环；`invokeSuper(obj, args)` 是调用代理类生成的那个直接调父类方法的 `CGLIB$xxx$0` 方法，不会触发拦截器，也不走反射，性能最好。正常增强逻辑都用 invokeSuper。

#### 提问：JDK 17 以后 CGLIB 会有什么问题？

回答：JDK 9 引入了模块化系统，对反射和字节码操作做了更严格的限制。CGLIB 需要访问 `java.lang` 等核心模块的内部 API，从 JDK 16 开始默认禁止非法反射访问。运行时需要加 `--add-opens java.base/java.lang=ALL-UNNAMED` 这类参数，否则会报 InaccessibleObjectException。Spring 6 已经把内嵌的 CGLIB 升级到兼容版本了。

#### 提问：在性能敏感场景怎么选？

回答：现在两者性能差距已经很小了。JDK 8 以后反射调用做了大量优化，100 万次调用的耗时差距在毫秒级。真正性能敏感的场景根本不该用动态代理，应该在编译期用字节码增强工具，比如 AspectJ 的编译时织入，生成的代码和手写的一样，零运行时开销。
...
