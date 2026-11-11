# 什么是 Java 中的常量池？

## 回答重点

**常量池**是 JVM 用来存储编译期确定的字面量和符号引用的地方，核心目的是复用，避免重复创建相同的常量对象。

Java 里其实有两个常量池概念要分清楚：

1. **Class 文件常量池**：编译后的 .class 文件里有一张常量表，存着字符串字面量、类名、方法名、字段名这些符号引用。用 `javap -v` 就能看到
2. **运行时常量池**：类加载时，Class 文件常量池的内容被加载到方法区，动态链接的时候把符号引用解析成直接引用

![chanliang.drawio.png](Z:/Public/images/0tW6Jv0I_chanliang.drawio_mianshiya.webp)

还有个经常被单独拎出来说的**字符串常量池**，JDK 7 之后被移到堆里了，专门存字符串对象的引用，`String.intern()` 操作的就是它。

```java
String s1 = "hello";              // 字面量，直接放进字符串常量池
String s2 = new String("hello");  // 堆上新建对象，常量池里也有一份 "hello"
String s3 = s2.intern();          // 返回常量池里的引用
System.out.println(s1 == s3);     // true，都指向常量池
System.out.println(s1 == s2);     // false，s2 指向堆上的新对象
```

## 扩展知识

### Class 文件常量池的结构

每个 .class 文件的开头都有一个常量池计数器和常量池表。常量池里的每一项都有一个 tag 标识类型：

1. CONSTANT_Utf8：UTF-8 编码的字符串
2. CONSTANT_Integer/Float/Long/Double：基本类型字面量
3. CONSTANT_Class：类或接口的符号引用
4. CONSTANT_Fieldref/Methodref：字段和方法的符号引用
5. CONSTANT_String：字符串字面量的引用

![](Z:/Public/images/w0AMl2iG_KYqdN4c8MP_mianshiya.webp)

执行 `javap -v Test.class` 就能看到完整的常量池内容，面试时能说出这个命令会加分。

### 字符串常量池的位置变迁

这是个高频考点，不同 JDK 版本差别很大：

![企业微信截图_fd863e4d-646b-4b69-8c91-ead9144b9f07.png](Z:/Public/images/nWAagDCv_fd863e4d-646b-4b69-8c91-ead9144b9f07_mianshiya.webp)

JDK 6 及之前，字符串常量池在永久代里，和运行时常量池放一起。永久代大小固定，`-XX:MaxPermSize` 设小了，字符串多了直接 OOM。

JDK 7 把字符串常量池挪到了堆里。原因很简单：字符串对象太多了，放堆里能享受 GC 回收，不用和方法区一起管理。

JDK 8 干掉了永久代，换成 Metaspace，运行时常量池跟着去了本地内存。但字符串常量池还在堆里，没变。

### intern() 方法的底层实现

`String.intern()` 是个 native 方法，底层用 StringTable 实现，本质是个 HashTable。JDK 7 之前，调用 intern() 会把字符串对象复制一份放进常量池；JDK 7 之后，只存堆上字符串的引用，不再复制。

```java
// JDK 7+ 的行为
String s1 = new String("a") + new String("b");  // 堆上创建 "ab"，常量池没有
s1.intern();                                     // 常量池存 s1 的引用
String s2 = "ab";                                // 从常量池拿，就是 s1 的引用
System.out.println(s1 == s2);                    // true
```

StringTable 默认大小是 60013，可以通过 `-XX:StringTableSize` 调整。字符串多的应用建议调大，减少 hash 冲突。

### 基本类型的包装类缓存

除了字符串，Integer、Long 这些包装类也有类似的缓存机制：

1. Integer 缓存 -128 到 127，可以通过 `-XX:AutoBoxCacheMax` 调大上限
2. Long 缓存 -128 到 127，不可调
3. Boolean 缓存 TRUE 和 FALSE
4. Character 缓存 0 到 127

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true，都从缓存拿

Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // false，超出缓存范围，各自 new
```

这些缓存在类加载时就初始化好了，存在堆里。

### 常量折叠优化

编译器会在编译期对常量表达式做**常量折叠**，直接算出结果存进常量池：

```java
String s1 = "a" + "b" + "c";  // 编译后直接是 "abc"，存常量池
String s2 = "abc";
System.out.println(s1 == s2); // true

final String x = "a";
String s3 = x + "bc";         // x 是 final，编译期能确定，也会折叠
System.out.println(s2 == s3); // true

String y = "a";
String s4 = y + "bc";         // y 不是 final，编译期不确定，用 StringBuilder 拼接
System.out.println(s2 == s4); // false
```

## 面试官追问

#### 提问：new String(“abc”) 创建了几个对象？

详细解答可以看：[使用 new String(“yupi”) 语句在 Java 中会创建多少个对象？](https://www.mianshiya.com/question/1780933294678896641)

回答：最多 2 个，最少 1 个。如果常量池里没有 “abc”，先在常量池创建一个字符串对象，再在堆上 new 一个，一共 2 个。如果常量池已经有 “abc” 了，只在堆上 new 一个，就 1 个。

#### 提问：字符串拼接底层是怎么实现的？

回答：看情况。如果都是字面量或 final 变量，编译期直接折叠成一个字符串。如果有变量参与，JDK 8 用 `StringBuilder` 的 append 拼，JDK 9 之后改成 invokedynamic 指令，底层还是 `StringBuilder`，但字节码更简洁。循环里拼字符串最好自己建 `StringBuilder`，不然每次循环都 new 一个。

#### 提问：StringTable 会被 GC 回收吗？

回答：会的。JDK 7 之后字符串常量池在堆里，和普通对象一样参与 GC。如果字符串没有任何引用指向它，Full GC 时会被回收。可以通过 `-XX:+PrintStringTableStatistics` 在 JVM 退出时打印 StringTable 的统计信息，看看有多少字符串、有没有 hash 冲突。

#### 提问：运行时常量池可以动态添加内容吗？

回答：可以。`String.intern()` 就是动态往字符串常量池里加东西。还有反射、动态代理生成的类，它们的符号引用也会动态加到运行时常量池。Lambda 表达式在第一次调用时通过 invokedynamic 生成的 CallSite 也会缓存起来。
