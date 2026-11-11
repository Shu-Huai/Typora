# Java

## 语言

### JDK、JRE、JVM

- JDK(Java SE Development Kit)，Java 标准开发包，它提供了编译、运行 Java 程序所需的各种工具和资源，包括 Java 编译器、Java 运行时环境，以及常用的 Java 类库等
- JRE( Java Runtime Environment) ，Java 运行环境，用于运行 Java 的字节码文件。JRE 中包括了 JVM 以及 JVM 工作所需要的类库，普通用户而只需要安装 JRE 来运行 Java 程序，而程序开发者必须安装 JDK 来编译、调试程序。
- JVM(Java Virtual Mechinal)，Java 虚拟机，是 JRE 的一部分，它是整个 java 实现跨平台的最核心的部分，负责运行字节码文件。

### `hashCode()`与 `equals()`之间的关系

在 Java 中，每个对象都可以调用自己的 `hashCode()`方法得到自己的哈希值(`hashCode`)，相当于对象的指纹信息，通常来说世界上没有完全相同的两个指纹，但是在 Java 中做不到这么绝对，但是我们仍然可以利用 `hashCode` 来做一些提前的判断，比如：

- 如果两个对象的 `hashCode` 不相同，那么这两个对象肯定不同的两个对象
- 如果两个对象的 `hashCode` 相同，不代表这两个对象一定是同一个对象，也可能是两个对象
- 如果两个对象相等，那么他们的 `hashCode` 就一定相同

### String、`StringBuffer`、`StringBuilder` 的区别

String 是不可变的，如果尝试去修改，会新生成一个字符串对象，`StringBuffer` 和 `StringBuilder` 是可变的

`StringBuffer` 是线程安全的，`StringBuilder` 是线程不安全的，所以在单线程环境下 `StringBuilder` 效率会更高

### 泛型中 extends 和 super 的区别

<? extends T>表示包括 T 在内的任何 T 的子类

<? super T>表示包括 T 在内的任何 T 的父类

### ==和 `equals` 方法的区别

- ==：如果是基本数据类型，比较是值，如果是引用类型，比较的是引用地址
- `equals`：具体看各个类重写 `equals` 方法之后的比较逻辑，比如 String 类，虽然是引用类型，但是 String 类中重写了 `equals` 方法，方法内部比较的是字符串中的各个字符是否全部相等。

### 重载和重写的区别

重载(Overload)： 在一个类中，同名的方法如果有不同的参数列表（比如参数类型不同、参数个数不同）则视为重载。

重写(Override)： 从字面上看，重写就是 重新写一遍的意思。其实就是在子类中把父类本身有的方法重新写一遍。子类继承了父类的方法，但有时子类并不想原封不动的继承父类中的某个方法，所以在方法名，参数列表，返回类型都相同(子类中方法的返回值可以是父类中方法返回值的子类)的情况下， 对方法体进行修改，这就是重写。但要注意子类方法的访问修饰权限不能小于父类的。

### List 和 Set 的区别

- List：有序，按对象插入的顺序保存对象，可重复，允许多个 Null 元素对象，可以使用 Iterator 取出所有元素，在逐一遍历，还可以使用 `get`(int `index`)获取指定下标的元素
- Set：无序，不可重复，最多允许有一个 Null 元素对象，取元素时只能用 Iterator 接口取得所有元素，在逐一遍历各个元素

### `ArrayList` 和 `LinkedList` 区别

1. 首先，他们的底层数据结构不同，`ArrayList` 底层是基于数组实现的，`LinkedList` 底层是基于链表实现的
2. 由于底层数据结构不同，他们所适用的场景也不同，`ArrayList` 更适合随机查找，`LinkedList` 更适合删除和添加，查询、添加、删除的时间复杂度不同
3. 另外 `ArrayList` 和 `LinkedList` 都实现了 List 接口，但是 `LinkedList` 还额外实现了 Deque 接口，所以 `LinkedList` 还可以当做队列来使用

### 深拷贝和浅拷贝

深拷贝和浅拷贝就是指对象的拷贝，一个对象中存在两种类型的属性，一种是基本数据类型，一种是实例对象的引用。
1. 浅拷贝是指，只会拷贝基本数据类型的值，以及实例对象的引用地址，并不会复制一份引用地址所指向的对象，也就是浅拷贝出来的对象，内部的类属性指向的是同一个对象
2. 深拷贝是指，既会拷贝基本数据类型的值，也会针对实例对象的引用地址所指向的对象进行复制，深拷贝出来的对象，内部的属性指向的不是同一个对象

### 什么是字节码？采用字节码的好处是什么？

编译器(javac)将 Java 源文件(*.java)文件编译成为字节码文件(*.class)，可以做到一次编译到处运行，windows 上编译好的 class 文件，可以直接在 linux 上运行，通过这种方式做到跨平台，不过 Java 的跨平台有一个前提条件，就是不同的操作系统上安装的 JDK 或 JRE 是不一样的，虽然字节码是通用的，但是需要把字节码解释成各个操作系统的机器码是需要不同的解释器的，所以针对各个操作系统需要有各自的 JDK 或 JRE。

采用字节码的好处，一方面实现了跨平台，另外一方面也提高了代码执行的性能，编译器在编译源代码时可以做一些编译期的优化，比如锁消除、标量替换、方法内联等。

### Java 中的异常体系是怎样的

Java 中的所有异常都来自顶级父类 Throwable。

Throwable 下有两个子类 Exception 和 Error。

Error 表示非常严重的错误，比如 `java.lang.StackOverFlowError` 和 Java.lang.OutOfMemoryError，通常这些错误出现时，仅仅想靠程序自己是解决不了的，可能是虚拟机、磁盘、操作系统层面出现的问题了，所以通常也不建议在代码中去捕获这些 Error，因为捕获的意义不大，因为程序可能已经根本运行不了了。

Exception 表示异常，表示程序出现 Exception 时，是可以靠程序自己来解决的，比如 NullPointerException、IllegalAccessException 等，我们可以捕获这些异常来做特殊处理

Exception 的子类通常又可以分为 RuntimeException 和非 RuntimeException 两类

RuntimeException 表示运行期异常，表示这个异常是在代码运行过程中抛出的，这些异常是非检查异常，程序中可以选择捕获处理，也可以不处理。这些异常一般是由程序逻辑错误引起的，程序应该从逻辑角度尽可能避免这类异常的发生，比如 NullPointerException、IndexOutOfBoundsException 等。

非 RuntimeException 表示非运行期异常，也就是我们常说的检查异常，是必须进行处理的异常，如果不处理，程序就不能检查异常通过。如 IOException、SQLException 等以及用户自定义的 Exception 异常。

### 在 Java 的异常处理机制中，什么时候应该抛出异常，什么时候捕获异常？

异常相当于一种提示，如果我们抛出异常，就相当于告诉上层方法，我抛了一个异常，我处理不了这个异常，交给你来处理，而对于上层方法来说，它也需要决定自己能不能处理这个异常，是否也需要交给它的上层。

所以我们在写一个方法时，我们需要考虑的就是，本方法能否合理的处理该异常，如果处理不了就继续向上抛出异常，包括本方法中在调用另外一个方法时，发现出现了异常，如果这个异常应该由自己来处理，那就捕获该异常并进行处理。

### Java 中有哪些类加载器

JDK 自带有三个类加载器：bootstrap `ClassLoader`、ExtClassLoader、AppClassLoader。
BootStrapClassLoader 是 ExtClassLoader 的父类加载器，默认负责加载%JAVA_HOME%lib 下的
jar 包和 class 文件。
ExtClassLoader 是 AppClassLoader 的父类加载器，负责加载%JAVA_HOME%/lib/ext 文件夹下的
jar 包和 class 类。
AppClassLoader 是自定义类加载器的父类，负责加载 classpath 下的类文件。
