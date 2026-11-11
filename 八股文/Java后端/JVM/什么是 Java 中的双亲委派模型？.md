# 什么是 Java 中的双亲委派模型？

## 回答重点

双亲委派模型是 Java 类加载的核心机制：当一个类加载器收到加载请求时，不会自己先去加载，而是把请求**向上委派给父加载器**，一直委派到最顶层的 Bootstrap `ClassLoader`。如果父加载器加载不了，才轮到自己加载。

举个例子，你写了个类叫 MyService，Application `ClassLoader` 收到加载请求后不会立刻加载，而是问 Extension `ClassLoader`：“你能加载吗？”

Extension `ClassLoader` 又去问 Bootstrap `ClassLoader`，Bootstrap `ClassLoader` 在 rt.jar 里找不到这个类，说“我搞不定”，请求就退回给 Extension `ClassLoader`。

Extension `ClassLoader` 在 ext 目录也找不到，再退回给 Application `ClassLoader`，最终由 Application `ClassLoader` 从 classpath 里找到并加载。

![](Z:/Public/images/c6PvNqS1_YFl3khhK0r_mianshiya.webp)

双亲委派的好处很直接：

1. 保证核心类库安全。`java.lang.Object` 永远由 Bootstrap `ClassLoader` 加载，就算有人恶意写了个同名的 Object 类放到 classpath 下，也不会被加载，因为请求先委派给 Bootstrap，Bootstrap 在 rt.jar 里找到了就直接返回。

2. 避免类重复加载。同一个类在 JVM 中只会被加载一次，保证类的唯一性。

## 扩展知识

### 三种内置类加载器

JDK 8 及之前，Java 提供了 3 种类加载器：

1. Bootstrap `ClassLoader`：C++ 实现的，负责加载 `<JAVA_HOME>/lib` 目录下的核心类库，比如 rt.jar、resources.jar。在 Java 代码里获取它的引用会返回 null。

2. Extension `ClassLoader`：Java 实现的，负责加载 `<JAVA_HOME>/lib/ext` 目录下的扩展类库，或者被 java.ext.dirs 系统变量指定的路径。

3. Application `ClassLoader`：Java 实现的，负责加载 classpath 下的类，包括我们自己写的代码和引入的第三方 jar 包。没有自定义类加载器的话，它就是程序的默认加载器。

![image-20210228112334820.png](Z:/Public/images/image-20210228112334820_mianshiya.webp)

双亲委派模型不是强制规定，你不遵守也不会报错，只是 Java 设计者推荐的一种类加载器实现方式。

JDK 9 对类加载器做了比较大的改动，Extension `ClassLoader` 改名叫 Platform `ClassLoader`，整体变成了模块化的类加载方式。详细可以看面试鸭：《[类加载器有了解过吗？](https://www.mianshiya.com/question/1780933295186407425)》这题。

### 打破双亲委派的典型场景

双亲委派虽然好，但某些场景下必须打破它：

**JDBC 和 SPI 机制**

JDBC 的 Driver 接口定义在 rt.jar 里，由 Bootstrap `ClassLoader` 加载。但具体的驱动实现，比如 MySQL 的 com.mysql.cj.jdbc.Driver 在 classpath 下的 jar 包里，Bootstrap `ClassLoader` 压根加载不到。

解决办法是用线程上下文类加载器。DriverManager 在初始化时会调用 `Thread.currentThread().getContextClassLoader()` 拿到 Application `ClassLoader`，用它来加载具体的驱动实现。这就打破了“父加载器加载的类不能使用子加载器加载的类”这个限制。

所有 Java SPI 机制都是这个套路：接口定义在核心类库，实现在 classpath 下，通过线程上下文类加载器来加载实现类。

**Web 容器的隔离需求**

Tomcat、WebLogic 这些容器，每个 Web 应用都有自己的 WebAppClassLoader，而且加载顺序跟标准双亲委派反过来：优先自己加载，加载不到才委派给父加载器。

为什么要这么搞？假设两个应用分别依赖 Spring 4 和 Spring 5，如果走双亲委派，Spring 类会被共享的父加载器加载，那两个应用就只能用同一个版本，这显然不行。每个应用用自己的类加载器，就能实现版本隔离。

### 自定义类加载器

想自定义类加载器很简单，继承 `ClassLoader` 重写 findClass 方法就行：

```java
public class MyClassLoader extends ClassLoader {
    private String classPath;
    
    public MyClassLoader(String classPath) {
        this.classPath = classPath;
    }
    
    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        byte[] data = loadClassData(name);
        if (data == null) {
            throw new ClassNotFoundException(name);
        }
        return defineClass(name, data, 0, data.length);
    }
    
    private byte[] loadClassData(String name) {
        String fileName = classPath + "/" + name.replace(".", "/") + ".class";
        try (FileInputStream fis = new FileInputStream(fileName);
             ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[1024];
            int len;
            while ((len = fis.read(buffer)) != -1) {
                baos.write(buffer, 0, len);
            }
            return baos.toByteArray();
        } catch (IOException e) {
            return null;
        }
    }
}
```

如果想打破双亲委派，重写 loadClass 方法，不调用 `super.loadClass()` 就行。但一般不建议这么干，除非你很清楚自己在做什么。

### 为什么不从顶层往下加载

有人会问：既然最终可能是父加载器加载，为什么不直接从 Bootstrap `ClassLoader` 开始往下找？

原因有两个：

1. 类加载器之间是组合关系，子加载器持有父加载器的引用，但父加载器不知道有哪些子加载器。如果从上往下找，父加载器都不知道该把请求传给谁。

2. 假设有 5 个平级的自定义类加载器，从上往下的话，Bootstrap `ClassLoader` 加载不了就得挨个问这 5 个子加载器，效率太低。从下往上的话，谁发起的请求最终就由谁兜底加载，路径清晰。

## 面试官追问

#### 提问：如果我自己写一个 `java.lang.String` 类，能被加载吗？

回答：不能。双亲委派机制下，加载 `java.lang.String` 的请求会一路委派到 Bootstrap `ClassLoader`，它在 rt.jar 里找到了 String 就直接返回。你自己写的压根没机会被加载。就算你打破双亲委派强行加载，JVM 也有安全检查，java 开头的包名是受保护的，会直接抛 SecurityException。

#### 提问：同一个类被不同的类加载器加载，在 JVM 里是同一个类吗？

回答：不是。在 JVM 里，判断两个类是否相同，除了类的全限定名要一样，加载它们的类加载器也必须是同一个。也就是说，com.example.User 被 `ClassLoader` A 和 `ClassLoader` B 分别加载后，在 JVM 里是两个不同的类，它们之间的对象不能互相赋值，强转会抛 ClassCastException。

#### 提问：线程上下文类加载器是怎么回事？

回答：线程上下文类加载器是 `Thread` 类的一个属性，通过 setContextClassLoader 和 getContextClassLoader 来设置和获取。它的存在就是为了解决双亲委派模型的局限性。默认情况下，线程的上下文类加载器是 Application `ClassLoader`。当核心类库需要加载 SPI 实现类时，就通过这个方法拿到能加载 classpath 下类的加载器。本质上是一种“父加载器借用子加载器”的机制。

#### 提问：Tomcat 的类加载器具体是怎么设计的？

回答：Tomcat 有好几层类加载器。最上面是 Common `ClassLoader`，加载 Tomcat 和所有应用共享的类。往下是 Catalina `ClassLoader` 和 Shared `ClassLoader`，分别加载 Tomcat 自身的类和应用共享的类。最下面每个 Web 应用都有自己的 WebApp `ClassLoader`，加载 WEB-INF/classes 和 WEB-INF/lib 下的类。WebApp `ClassLoader` 打破了双亲委派，优先自己加载，保证不同应用可以用不同版本的同名类。
