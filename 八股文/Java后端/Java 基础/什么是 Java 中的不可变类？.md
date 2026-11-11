# 什么是 Java 中的不可变类？

## 回答重点

**不可变类**就是对象一旦创建完成，状态就定死在那了，后面没法再改。Java 里最典型的就是 String，还有 Integer、Long、Boolean 这些基本类型的包装类。

要实现一个真正的不可变类，必须同时满足 5 个条件：

1. 类声明为 final，防止子类继承后搞出可变行为

2. 所有字段都是 private final，只能在构造阶段赋值一次

3. 通过构造函数初始化所有字段

4. 不提供任何 setter 或修改状态的方法

5. 如果字段引用了可变对象，getter 必须返回副本，不能把原对象暴露出去

![](Z:/Public/images/Zx0fnLaP_rkTj9K6Q8b_mianshiya.webp)

```java
public final class ImmutablePerson {
    private final String name;
    private final List<String> hobbies;
    
    public ImmutablePerson(String name, List<String> hobbies) {
        this.name = name;
        // 防御性拷贝，不直接引用外部传入的可变对象
        this.hobbies = new ArrayList<>(hobbies);
    }
    
    public String getName() {
        return name; // String 本身不可变，直接返回
    }
    
    public List<String> getHobbies() {
        // 返回副本，保护内部状态
        return new ArrayList<>(hobbies);
    }
}
```

不可变类有两个核心价值：

1. 天生线程安全：状态不能改，多线程随便访问，根本不用加锁

2. 适合做缓存 `key`：比如 `HashMap` 的 `key` 要求 `hashCode` 稳定，不可变对象天然满足

当然也有代价：每次“修改”都得创建新对象，String 拼接频繁的场景内存压力不小，所以才有 `StringBuilder`。

## 扩展知识

### String 的不可变设计

String 是教科书级别的不可变类实现，来拆解一下它的设计：

![](Z:/Public/images/image-20210228112501169_mianshiya.webp)

1. 类用 final 修饰，没法被继承，堵死了子类破坏不可变性的可能

2. 底层的 char 数组用 private final 修饰。不过要注意，final 只能保证引用不变，数组内容还是能改的

3. 关键在于 `value` 数组是 private 的，而且 String 没暴露任何能修改数组内容的方法

当你执行 `s += "a"` 这样的操作，返回的是全新的 String 对象，原来的 s 指向的对象纹丝不动，只是 s 这个引用指向了新对象。

看 replace 方法的实现，修改操作全都是 new 一个新对象返回，从不动原对象。

![](Z:/Public/images/image-20210228112521363_mianshiya.webp)

### 防御性拷贝的坑

很多人实现不可变类时会漏掉防御性拷贝，导致不可变性被破坏：

```java
// 错误示范
public final class BrokenImmutable {
    private final List<String> items;
    
    public BrokenImmutable(List<String> items) {
        this.items = items; // 危险！外部持有同一个引用
    }
    
    public List<String> getItems() {
        return items; // 危险！外部能直接修改
    }
}

// 外部可以这样破坏
List<String> list = new ArrayList<>();
list.add("a");
BrokenImmutable obj = new BrokenImmutable(list);
list.add("b"); // 对象内部状态被改了！
obj.getItems().add("c"); // 又被改了！
```

正确做法是构造时拷贝一份，返回时也拷贝一份。Java 9 之后可以用 `List.of()` 或 `List.copyOf()` 直接创建不可变集合，更简洁。

![](Z:/Public/images/qwhZohsl_UmwLedyx9U_mianshiya.webp)

### JDK 中的不可变集合

Java 9 引入了真正的不可变集合工厂方法：

```java
List<String> list = List.of("a", "b", "c");
Set<String> set = Set.of("x", "y", "z");
Map<String, Integer> map = Map.of("one", 1, "two", 2);

list.add("d"); // 直接抛 UnsupportedOperationException
```

这些集合不仅不能改，内部实现还做了优化，比如小规模集合用专门的 ImmutableCollections.List12 这种特化实现，省内存。

注意和 `Collections.unmodifiableList()` 的区别：unmodifiableList 只是个视图，原集合改了它也跟着变；`List.of()` 是真正的不可变，和原集合没有任何关系。

### 不可变对象的性能考量

不可变对象“每次修改都创建新对象”听起来性能很差，但实际上有几个因素能缓解：

1. 现代 JVM 对短生命周期对象的 GC 非常高效，大部分在 Young GC 就被回收了

2. JIT 编译器有逃逸分析，能把一些不逃逸的对象直接在栈上分配，连堆都不走

3. 不可变对象可以安全地共享，很多场景反而能减少对象创建。比如 Integer 缓存了 -128 到 127，String 有字符串常量池

真正需要频繁修改的场景，用 `StringBuilder`、`ArrayList` 这些可变类就行，不可变类主要用在需要安全共享状态的地方。

## 面试官追问

#### 提问：String 真的完全不可能被修改吗？

回答：正常使用确实改不了，但通过反射可以强行改底层的 char 数组。拿到 String 对象的 `value` 字段，setAccessible(true) 打开权限，然后直接改数组内容。不过这是在搞破坏，正常代码不应该这么干。Java 9 之后模块系统加强了封装，非法反射访问会有警告，以后版本可能直接禁止。

#### 提问：为什么 String 要设计成不可变的？

回答：主要三个原因。第一是安全，String 大量用于类加载、网络连接这些敏感场景，不可变能防止被恶意篡改。第二是字符串常量池能存在的前提就是不可变，多个变量指向同一个字符串对象才安全。第三是 `hashCode` 可以缓存，String 作为 `HashMap` 的 `key` 非常频繁，第一次算完 `hashCode` 后面就不用再算了。

#### 提问：Integer 缓存是怎么回事？和不可变有什么关系？

回答：Integer 内部有个 IntegerCache，预先创建了 -128 到 127 的 Integer 对象。用 valueOf 方法或者自动装箱时，如果值在这个范围内就直接返回缓存对象，不创建新的。正因为 Integer 不可变，多个地方共用同一个对象才安全，否则一个地方改了值，其他地方全乱套。这个范围可以通过 JVM 参数 `-XX:AutoBoxCacheMax` 调大。

#### 提问：Record 类是不可变的吗？

回答：Java 14 引入的 Record 默认就是不可变的。它自动帮你把字段声明为 private final，自动生成 getter、`equals`、`hashCode`、toString。但要注意，如果字段是可变对象的引用，比如 List，Record 本身不会帮你做防御性拷贝，你得自己在紧凑构造器里处理。所以 Record 是“浅不可变”，要实现深度不可变还得自己下功夫。
