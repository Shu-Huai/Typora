# Java 中的序列化和反序列化是什么？

## 回答重点

**序列化**就是把内存中的 Java 对象转成二进制字节流，这样才能存到硬盘或者通过网络发给别的机器。**反序列化**就是反过来，把字节流还原成 Java 对象。硬盘和网络只认 0 和 1，不认 Java 对象，所以必须有这么一层转换。

面试官最爱问的 3 个细节：

1. 怎么做：类必须实现 `Serializable` 接口，这玩意儿就是个许可证，没它 JDK 序列化机制压根不让你序列化
2. 怎么防：敏感字段比如密码，加个 `transient` 关键字，序列化的时候自动跳过
3. 怎么稳：显式定义 `serialVersionUID`，相当于给类打个版本戳，防止改了类结构后反序列化旧数据时报错

```java
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    private String username;
    private transient String password; // 不参与序列化
    private int age;
}
```

![序列化与反序列化示意图](Z:/Public/images/serialization-overview.webp)

## 扩展知识

### 为什么对象不能直接传输

对象在 JVM 里是"立体"的，到处都是引用关系。比如某个字段指向内存地址 0x1234 处的另一个对象，这地址只在当前 JVM 有效，传到网络另一端，人家的 0x1234 地址上根本不是同一个东西。

序列化要干的活就是把这些引用关系"压扁"，把整个对象图递归地转成一段自包含的字节序列。接收端拿到后，反序列化时在自己的堆上重建整个对象图，引用关系照样能还原回来。

![对象图压扁为字节序列](Z:/Public/images/serialization-object-graph.webp)

### Serializable 接口的真相

这接口是个空接口，一行代码都没有，纯粹就是个标记。JDK 序列化源码里有这么一段逻辑：除了 String、数组和枚举这几个特殊类型，其他对象要序列化必须实现 Serializable，否则直接抛 `NotSerializableException`。

![Serializable 校验逻辑源码](Z:/Public/images/serialization-serializable-interface.webp)

### serialVersionUID 的作用

```java
private static final long serialVersionUID = 1L;
```

这行代码几乎每个实现 Serializable 的类都有。它的作用是在反序列化时校验类版本：序列化时把这个 ID 写进字节流，反序列化时比对当前类的 ID，不一致就抛 `InvalidClassException`。

ID 的具体数值不重要，1L 还是 IDEA 自动生成的一长串数字都行，关键是保持一致。如果你没显式定义，编译器会根据类的结构自动生成一个，但这带来一个坑：你只是加了个字段，自动生成的 ID 就变了，之前序列化的数据就废了。

所以最佳实践是：**显式定义 serialVersionUID**，改类结构时想清楚要不要兼容旧数据，要兼容就别改这个值。

![serialVersionUID 校验流程](Z:/Public/images/serialization-serialversionuid.webp)

### 静态变量不参与序列化

序列化存的是对象的状态，静态变量属于类，不属于对象，所以不会被序列化。反序列化后静态变量的值取决于当前 JVM 里这个类的静态变量是什么值，跟序列化时的值没关系。

![静态变量不参与序列化](Z:/Public/images/serialization-static-field.webp)

### JDK 序列化的问题

JDK 自带的序列化虽然用起来简单，但生产环境很少直接用，主要有这几个硬伤：

1. 性能差：序列化后的字节流体积大，序列化/反序列化速度慢
2. 跨语言不友好：只有 Java 能读懂，和 Go、Python 这些语言没法直接互通

所以实际项目里，RPC 框架一般用 Protobuf、Hessian、Kryo 这类专门的序列化框架，性能更好、体积更小。JSON 序列化虽然性能一般，但可读性好，HTTP API 场景用得多。

| 序列化方式 | 优点 | 缺点 | 典型场景 |
| --- | --- | --- | --- |
| JDK 原生 | 使用简单 | 性能差、体积大 | 小项目、临时方案 |
| JSON | 可读性好、跨语言 | 性能一般 | HTTP API、配置文件 |
| Protobuf | 性能好、体积小 | 需要写 proto 文件 | gRPC、高性能 RPC |
| Hessian | 性能较好、使用简单 | 跨语言支持有限 | Dubbo 默认序列化 |

## 面试官追问

### 提问：transient 和 static 修饰的字段都不会被序列化，它们有什么区别？

回答：本质不同。static 字段属于类，压根就不是对象状态的一部分，所以不存在"序列化不序列化"的问题，它就不在序列化的范畴内。transient 是专门告诉序列化机制"这个实例字段我不想存"，比如密码、缓存这类不适合持久化的数据。一个是"不归你管"，一个是"归你管但我不让你存"。

### 提问：如果父类没有实现 Serializable，子类实现了，序列化子类对象时父类的字段会怎样？

回答：父类字段不会被序列化。反序列化时，子类字段正常恢复，但父类字段会调用父类的无参构造器重新初始化。如果父类没有无参构造器，反序列化直接报错。所以如果需要父类字段也参与序列化，父类也得实现 Serializable。

### 提问：Externalizable 接口和 Serializable 有什么区别？

回答：Serializable 是自动序列化，JDK 帮你搞定所有字段。Externalizable 是手动挡，必须自己实现 writeExternal 和 readExternal 方法，一个字段一个字段地写出去、读进来。好处是完全可控，可以做定制优化；坏处是麻烦，漏写一个字段就丢数据。性能要求高的场景可以考虑，一般业务代码用 Serializable 就够了。

### 提问：为什么说反序列化是 Java 安全漏洞的重灾区？

回答：反序列化会触发对象的构造过程，如果恶意构造的字节流能让某些类的特定方法被执行，就可能造成远程代码执行。典型的就是利用 Commons-Collections、Fastjson 这些库里的 gadget chain，攻击者只要找到一条能从反序列化入口通往危险方法的调用链，就能在服务器上执行任意代码。防御手段包括：升级有漏洞的依赖库、配置反序列化白名单、用 JSON 替代 Java 原生序列化。
