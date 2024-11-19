# Java

## 语言

### JDK、JRE、JVM

- JDK(Java SE Development Kit)，Java标准开发包，它提供了编译、运行Java程序所需的各种工具和资源，包括Java编译器、Java运行时环境，以及常用的Java类库等
- JRE( Java Runtime Environment) ，Java运行环境，用于运行Java的字节码文件。JRE中包括了JVM以及JVM工作所需要的类库，普通用户而只需要安装JRE来运行Java程序，而程序开发者必须安装JDK来编译、调试程序。
- JVM(Java Virtual Mechinal)，Java虚拟机，是JRE的一部分，它是整个java实现跨平台的最核心的部分，负责运行字节码文件。

### hashCode()与equals()之间的关系

在Java中，每个对象都可以调用自己的hashCode()方法得到自己的哈希值(hashCode)，相当于对象的指纹信息，通常来说世界上没有完全相同的两个指纹，但是在Java中做不到这么绝对，但是我们仍然可以利用hashCode来做一些提前的判断，比如：

- 如果两个对象的hashCode不相同，那么这两个对象肯定不同的两个对象
- 如果两个对象的hashCode相同，不代表这两个对象一定是同一个对象，也可能是两个对象
- 如果两个对象相等，那么他们的hashCode就一定相同

### String、StringBuffer、StringBuilder的区别

String是不可变的，如果尝试去修改，会新生成一个字符串对象，StringBuffer和StringBuilder是可变的

StringBuffer是线程安全的，StringBuilder是线程不安全的，所以在单线程环境下StringBuilder效率会更高

### 泛型中extends和super的区别

<? extends T>表示包括T在内的任何T的子类

<? super T>表示包括T在内的任何T的父类

### ==和equals方法的区别

- ==：如果是基本数据类型，比较是值，如果是引用类型，比较的是引用地址
- equals：具体看各个类重写equals方法之后的比较逻辑，比如String类，虽然是引用类型，但是String类中重写了equals方法，方法内部比较的是字符串中的各个字符是否全部相等。

### 重载和重写的区别

重载(Overload)： 在一个类中，同名的方法如果有不同的参数列表（比如参数类型不同、参数个数不同）则视为重载。

重写(Override)： 从字面上看，重写就是 重新写一遍的意思。其实就是在子类中把父类本身有的方法重新写一遍。子类继承了父类的方法，但有时子类并不想原封不动的继承父类中的某个方法，所以在方法名，参数列表，返回类型都相同(子类中方法的返回值可以是父类中方法返回值的子类)的情况下， 对方法体进行修改，这就是重写。但要注意子类方法的访问修饰权限不能小于父类的。

### List和Set的区别

- List：有序，按对象插入的顺序保存对象，可重复，允许多个Null元素对象，可以使用Iterator取出所有元素，在逐一遍历，还可以使用get(int index)获取指定下标的元素
- Set：无序，不可重复，最多允许有一个Null元素对象，取元素时只能用Iterator接口取得所有元素，在逐一遍历各个元素

### ArrayList和LinkedList区别

1. 首先，他们的底层数据结构不同，ArrayList底层是基于数组实现的，LinkedList底层是基于链表实现的
2. 由于底层数据结构不同，他们所适用的场景也不同，ArrayList更适合随机查找，LinkedList更适合删除和添加，查询、添加、删除的时间复杂度不同
3. 另外ArrayList和LinkedList都实现了List接口，但是LinkedList还额外实现了Deque接口，所以LinkedList还可以当做队列来使用

### 深拷贝和浅拷贝

深拷贝和浅拷贝就是指对象的拷贝，一个对象中存在两种类型的属性，一种是基本数据类型，一种是实例对象的引用。
1. 浅拷贝是指，只会拷贝基本数据类型的值，以及实例对象的引用地址，并不会复制一份引用地址所指向的对象，也就是浅拷贝出来的对象，内部的类属性指向的是同一个对象
2. 深拷贝是指，既会拷贝基本数据类型的值，也会针对实例对象的引用地址所指向的对象进行复制，深拷贝出来的对象，内部的属性指向的不是同一个对象

### 什么是字节码？采用字节码的好处是什么？

编译器(javac)将Java源文件(*.java)文件编译成为字节码文件(*.class)，可以做到一次编译到处运行，windows上编译好的class文件，可以直接在linux上运行，通过这种方式做到跨平台，不过Java的跨平台有一个前提条件，就是不同的操作系统上安装的JDK或JRE是不一样的，虽然字节码是通用的，但是需要把字节码解释成各个操作系统的机器码是需要不同的解释器的，所以针对各个操作系统需要有各自的JDK或JRE。

采用字节码的好处，一方面实现了跨平台，另外一方面也提高了代码执行的性能，编译器在编译源代码时可以做一些编译期的优化，比如锁消除、标量替换、方法内联等。

### Java中的异常体系是怎样的

Java中的所有异常都来自顶级父类Throwable。

Throwable下有两个子类Exception和Error。

Error表示非常严重的错误，比如java.lang.StackOverFlowError和Java.lang.OutOfMemoryError，通常这些错误出现时，仅仅想靠程序自己是解决不了的，可能是虚拟机、磁盘、操作系统层面出现的问题了，所以通常也不建议在代码中去捕获这些Error，因为捕获的意义不大，因为程序可能已经根本运行不了了。

Exception表示异常，表示程序出现Exception时，是可以靠程序自己来解决的，比如NullPointerException、IllegalAccessException等，我们可以捕获这些异常来做特殊处理

Exception的子类通常又可以分为RuntimeException和非RuntimeException两类

RuntimeException表示运行期异常，表示这个异常是在代码运行过程中抛出的，这些异常是非检查异常，程序中可以选择捕获处理，也可以不处理。这些异常一般是由程序逻辑错误引起的，程序应该从逻辑角度尽可能避免这类异常的发生，比如NullPointerException、IndexOutOfBoundsException等。

非RuntimeException表示非运行期异常，也就是我们常说的检查异常，是必须进行处理的异常，如果不处理，程序就不能检查异常通过。如IOException、SQLException等以及用户自定义的Exception异常。

### 在Java的异常处理机制中，什么时候应该抛出异常，什么时候捕获异常？

异常相当于一种提示，如果我们抛出异常，就相当于告诉上层方法，我抛了一个异常，我处理不了这个异常，交给你来处理，而对于上层方法来说，它也需要决定自己能不能处理这个异常，是否也需要交给它的上层。

所以我们在写一个方法时，我们需要考虑的就是，本方法能否合理的处理该异常，如果处理不了就继续向上抛出异常，包括本方法中在调用另外一个方法时，发现出现了异常，如果这个异常应该由自己来处理，那就捕获该异常并进行处理。

### Java中有哪些类加载器

JDK自带有三个类加载器：bootstrap ClassLoader、ExtClassLoader、AppClassLoader。
BootStrapClassLoader是ExtClassLoader的父类加载器，默认负责加载%JAVA_HOME%lib下的
jar包和class文件。
ExtClassLoader是AppClassLoader的父类加载器，负责加载%JAVA_HOME%/lib/ext文件夹下的
jar包和class类。
AppClassLoader是自定义类加载器的父类，负责加载classpath下的类文件。