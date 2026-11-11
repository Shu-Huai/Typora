# 你了解 Java 的类加载器吗？
## 回答重点

类加载器是 JVM 用来把 .class 字节码文件加载到内存、转换成 Class 对象的组件。它最核心的两个职责：一是**动态加载**，程序运行时按需加载类，不用编译期就把所有类都塞进来；二是**隔离命名空间**，不同类加载器加载的同名类互不干扰，Tomcat 能同时跑多个版本相同依赖的 Web 应用就靠这个。

![](Z:/Public/images/WH5ikKlS_307e24c7-83be-4597-a181-011224aa7b34_mianshiya.webp)

JDK 8 有三层类加载器：最顶层是启动类加载器，负责加载 `<JAVA_HOME>/lib` 下的核心类库；中间是扩展类加载器，加载 `<JAVA_HOME>/lib/ext` 下的扩展库；最底层是应用程序类加载器，加载我们写的业务代码和第三方 jar 包。

![leijiazai.drawio.png](Z:/Public/images/EqdhvtHm_leijiazai.drawio_mianshiya.webp)

## 扩展知识

### 类加载器的层次结构

JDK 8 的时候一共有三种类加载器：
1. 启动类加载器（Bootstrap `ClassLoader`），它是属于虚拟机自身的一部分，主要负责加载<JAVA_HOME>\lib 目录中或被 -Xbootclasspath 指定的路径中的并且文件名是被虚拟机识别的文件，它是所有类加载器的父亲。
2. 扩展类加载器（Extension `ClassLoader`），它是 Java 实现的，独立于虚拟机，主要负责加载<JAVA_HOME>\lib\ext 目录中或被 java.ext.dirs 系统变量所指定的路径的类库。
3. 应用程序类加载器（Application `ClassLoader`），它是 Java 实现的，独立于虚拟机。主要负责加载用户类路径（classPath）上的类库，如果我们没有实现自定义的类加载器那这个加载器就是我们程序中的默认加载器。

![](Z:/Public/images/W8ylN5Ac_78f53bd2-1515-4dc7-8d17-ff727829a223_mianshiya.webp)

### JDK 9 模块化后的变化

JDK 9 引入了模块化系统 Jigsaw，原来的 rt.jar、tool.jar 被拆成了几十个 jmod 文件。既然已经满足可扩展需求，就没必要保留 `<JAVA_HOME>/lib/ext` 这个目录了，所以扩展类加载器被重命名为**平台类加载器**（PlatformClassLoader），主要加载被 module-info.java 中定义的类。

双亲委派的路径也做了调整：

![企业微信截图_356498bd-8c60-4b0e-b599-999b047d4376.png](Z:/Public/images/JsOSPBN2_356498bd-8c60-4b0e-b599-999b047d4376_mianshiya.webp)

在平台和应用类加载器受到加载请求时，会先判断该类是否属于一个系统模块，如果属于则委派给对应的模块类加载器加载，反之才委派给父类加载器。

JDK 9 之后类加载器负责模块（图来自网络）：

![企业微信截图_c43e2b11-4eb9-4a0f-b07b-4326341a1b6e.png](Z:/Public/images/7eFjm18m_c43e2b11-4eb9-4a0f-b07b-4326341a1b6e_mianshiya.webp)

![企业微信截图_a2c32e43-ee8a-42cc-a07d-52ccc862fc85.png](Z:/Public/images/rXCGcXjj_a2c32e43-ee8a-42cc-a07d-52ccc862fc85_mianshiya.webp)

![企业微信截图_eab6eed5-fc23-462b-9e0d-6dd3c2131ec7.png](Z:/Public/images/5fXoFl9v_eab6eed5-fc23-462b-9e0d-6dd3c2131ec7_mianshiya.webp)

### Java 的类加载过程

- [438. Java 的类加载过程是怎样的？](https://www.mianshiya.com/question/1780933294662119426)

### 双亲委派模型

在类加载过程中，类加载器会优先将加载请求委托给父类加载器，只有当父类加载器无法加载时，才会由当前加载器尝试加载。这种机制保证了 Java 核心类库的安全性，避免核心类库被篡改或替换。

- [什么是 Java 中的双亲委派模型？](https://www.mianshiya.com/question/1780933294670508033)

### 自定义类加载器

通过继承 `ClassLoader` 类并重写 findClass 方法，可以自定义类加载器。典型场景包括 Tomcat 的 WebAppClassLoader、OSGi 的模块隔离、JRebel 的热加载等。

```java
public class CustomClassLoader extends ClassLoader {
    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        // 从指定路径读取字节码
        byte[] classData = getClassData(name);
return defineClass(name, classData, 0, classData.length);
}
}
```

![](Z:/Public/images/LphOamhq_pegLrnvWL0_mianshiya.webp)

## 面试官追问

#### 提问：双亲委派模型有没有被打破过？什么场景下需要打破？

>详细解答可以看：[什么是 Java 中的双亲委派模型？](https://www.mianshiya.com/question/1780933294670508033)

回答：打破的场景不少。最经典的就是 JNDI、JDBC 这种 SPI 机制，核心接口定义在 rt.jar 里由启动类加载器加载，但实现类是第三方厂商提供的放在 classpath 下，启动类加载器压根看不到。所以引入了**线程上下文类加载器**，让父加载器能“回调”子加载器去加载实现类。另外 Tomcat 为了实现应用隔离和热部署，也打破了双亲委派：WebAppClassLoader 优先加载应用自己的类，加载不到才委派给父加载器。

#### 提问：同一个 Class 被不同类加载器加载两次，JVM 会认为是同一个类吗？

回答：不会。JVM 判断两个类是否相同，看的是**全限定名 + 类加载器实例**，两者缺一不可。同一个 .class 文件被两个不同的 `ClassLoader` 实例加载，产生的是两个完全独立的 Class 对象，它们之间不能互相赋值、不能 instanceof 判断。Tomcat 正是利用这一点实现不同 Web 应用的类隔离。

#### 提问：类加载器能不能卸载已经加载的类？

回答：能，但条件很苛刻。一个类要被卸载，必须同时满足三个条件：这个类的所有实例都被回收了、加载这个类的 `ClassLoader` 实例被回收了、这个类的 Class 对象没有被引用。启动类加载器、扩展类加载器这些系统级的加载器基本不可能被回收，所以它们加载的类也不会被卸载。自定义类加载器加载的类在满足条件后可以被 GC 回收掉。

#### 提问：为什么 Tomcat 要自己实现一套类加载器，不直接用 JDK 默认的？

回答：Tomcat 有三个核心诉求 JDK 默认的满足不了。一是多应用隔离，跑在同一个 Tomcat 里的 10 个 Web 应用可能用了不同版本的 Spring，必须互不干扰；二是热部署，应用更新后不用重启整个 Tomcat，直接干掉旧的 WebAppClassLoader、创建新的重新加载；三是共享公共库，比如 Tomcat 自己的 servlet-api.jar 只需要加载一份，所有应用共用。所以 Tomcat 设计了 Common、Catalina、Shared、WebApp 这一套层次结构的类加载器来满足这些需求。
