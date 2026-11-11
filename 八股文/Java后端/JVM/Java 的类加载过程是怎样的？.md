# Java 的类加载过程是怎样的？

## 回答重点

类加载就是把 .class 文件的二进制数据读进内存，经过校验、转换，最终变成 JVM 能用的 Class 对象。

二进制流不一定非得来自 .class 文件，也可以是字节码工具动态生成的、或者从网络传过来的，只要格式对，JVM 都认。

整个类加载流程分为三大阶段：**加载、连接、初始化**。连接又能拆成**验证、准备、解析**三步，所以细分下来是 5 个阶段：

1. 加载

把二进制流读进内存，在方法区生成类的运行时数据结构，同时在堆里创建一个 Class 对象作为访问入口。

2. 验证

校验二进制流是否符合 Class 文件规范，包括魔数检查、版本号校验、元数据验证、字节码验证、符号引用验证。这一步是为了防止恶意代码搞崩 JVM。

3. 准备

给类变量（static 修饰的变量）分配内存并设置初始零值。注意这里只是零值，比如 `static int a = 123` 在准备阶段 a 的值是 0，不是 123。但如果是 `static final int a = 123`，编译期就确定了，准备阶段直接赋值 123。

4. 解析

把常量池里的符号引用替换成直接引用。符号引用就是一个字符串形式的标识，比如 `java/lang/Object`；直接引用是真正的内存地址或偏移量，能直接定位到目标。

5. 初始化

执行类构造器 `<clinit>()` 方法，这时候才真正执行 `static int a = 123` 这种赋值操作，静态代码块也是在这个阶段跑的。

![](Z:/Public/images/ci6hvukx_W8bJBKN6cF_mianshiya.webp)

看段代码感受一下准备和初始化的区别：

```java
public class LoadingDemo {
    // 准备阶段：value = 0
    // 初始化阶段：value = 100
    private static int value = 100;
    
    // 准备阶段就直接赋值 200，因为是 final 常量
    private static final int CONSTANT = 200;
    
    static {
        System.out.println("静态代码块执行，value = " + value);
    }
}
```

## 扩展知识

### 类加载的触发时机

JVM 规范规定了 6 种情况必须立即对类进行初始化：

1. 遇到 new、getstatic、putstatic、invokestatic 这 4 条字节码指令时。对应的 Java 代码就是 new 对象、读取或设置类的静态字段（被 final 修饰的常量除外）、调用静态方法。

2. 使用 `java.lang.reflect` 包对类进行反射调用时。

3. 初始化子类时发现父类还没初始化，先把父类初始化了。

4. JVM 启动时指定的主类（包含 main 方法的那个类）。

5. JDK 7 开始的动态语言支持，如果 MethodHandle 实例解析结果是 REF_getStatic、REF_putStatic、REF_invokeStatic、REF_newInvokeSpecial 这四种句柄，对应的类要先初始化。

6. 接口中定义了 default 方法，实现类初始化前要先初始化这个接口。

### 类加载器的层次结构

JVM 的类加载采用双亲委派模型，有三种内置的类加载器：

1. Bootstrap `ClassLoader`：最顶层的加载器，C++ 实现的，负责加载 `JAVA_HOME/lib` 目录下的核心类库，比如 rt.jar、tools.jar。在 Java 代码里拿不到它的引用，返回的是 null。

2. Extension `ClassLoader`：负责加载 `JAVA_HOME/lib/ext` 目录下的扩展类库。JDK 9 之后改名叫 Platform `ClassLoader`。

3. Application `ClassLoader`：加载 classpath 下的类，也就是我们自己写的代码和引入的第三方 jar 包。

![](Z:/Public/images/2pwH1JDC_09oInra2z4_mianshiya.webp)

### 打破双亲委派的场景

双亲委派不是强制的，某些场景需要打破它：

1. SPI 机制。JDBC 的 Driver 接口定义在 rt.jar 里，由 Bootstrap `ClassLoader` 加载，但具体实现（比如 MySQL 驱动）在 classpath 下，Bootstrap `ClassLoader` 加载不到。这时候用 `Thread.currentThread()`.getContextClassLoader() 获取线程上下文类加载器来加载。

2. 热部署。Tomcat 为了让不同 Web 应用的同名类互不干扰，每个应用都有自己的 WebAppClassLoader，而且是优先自己加载，加载不到才委派给父加载器。

3. 模块化系统。JDK 9 引入的模块化打破了原来的双亲委派，类加载变成了在模块图中按依赖关系查找。

### 类的卸载

类被卸载需要同时满足三个条件：

1. 这个类的所有实例都被 GC 回收了
2. 加载这个类的 `ClassLoader` 也被回收了
3. 这个类的 Class 对象没有被任何地方引用

Bootstrap `ClassLoader` 和 Extension `ClassLoader` 加载的类基本不会被卸载，因为这两个加载器一直存活。只有自定义类加载器加载的类才有可能被卸载，这在 OSGi 等热部署框架里很常见。

## 面试官追问

#### 提问：准备阶段和初始化阶段对静态变量的处理有什么区别？

回答：准备阶段只是分配内存和设置零值，int 就是 0，引用就是 null，boolean 就是 false。真正执行代码里写的赋值语句是在初始化阶段。但有个例外，static final 修饰的常量如果是编译期就能确定的值，准备阶段就直接赋值了，不用等到初始化。

#### 提问：什么情况下访问静态字段不会触发类初始化？

回答：两种情况。一是通过子类访问父类的静态字段，只会初始化父类，子类不会初始化。二是引用类的常量（static final 且编译期确定），常量在编译阶段就会存入调用方的常量池里，运行时跟定义常量的类没关系了。

#### 提问：能不能自己写一个 `java.lang.String` 类然后加载？

回答：加载是能加载，但用不了。双亲委派机制下，加载 `java.lang.String` 的请求会一路委派到 Bootstrap `ClassLoader`，它在 rt.jar 里找到了就直接返回，你自己写的 String 压根没机会被加载。就算你打破双亲委派自己加载，JVM 也有安全检查，java 开头的包名是受保护的，会直接抛 SecurityException。

#### 提问：Tomcat 的类加载器跟标准的双亲委派有什么不同？

回答：Tomcat 的 WebAppClassLoader 是先自己加载，加载不到才委派给父加载器，跟标准的双亲委派正好反过来。这样设计是为了让不同 Web 应用可以使用不同版本的同名类，比如一个应用用 Spring 4，另一个用 Spring 5，互不干扰。同时 Tomcat 共享的类库还是走双亲委派，避免重复加载。
