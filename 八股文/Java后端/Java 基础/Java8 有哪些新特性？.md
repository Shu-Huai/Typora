# Java8 有哪些新特性？

## 回答重点

Java 8 是一个里程碑版本，引入了大量实用特性，面试常问的主要有这些：

1. 元空间替代了永久代，永久代回收效率太低，加上 HotSpot 要和 JRockit 合并，JRockit 压根没有永久代，所以干脆去掉了

2. Lambda 表达式，用 `(参数) -> 表达式` 语法实现代码块传递，告别匿名内部类的冗长写法

3. 函数式接口，只有一个抽象方法的接口，比如 Predicate、Function、Consumer，是 Lambda 的载体

4. 新的日期时间 API，LocalDate、LocalDateTime 这些不可变类，替代了线程不安全的 Date 和 Calendar

5. 接口默认方法和静态方法，允许接口用 default 关键字定义方法实现，解决接口升级时对实现类的兼容问题

6. Stream 流式接口，声明式处理集合数据，链式调用实现过滤、映射、排序，还支持 parallelStream 并行处理

7. `Optional` 类，封装可能为 null 的值，提供 orElse、ifPresent 等方法优雅处理空值，减少 NPE

8. 新增了 `CompletableFuture`、`StampedLock` 等并发实现类

![](Z:/Public/images/0grlp5un_g8W0dcPed5_mianshiya.webp)

如果你对 `HashMap`、`ConcurrentHashMap` 面试题有准备的话，这时候也可以抛出来，引导面试官来询问。比如：Java 8 修改了 `HashMap` 和 `ConcurrentHashMap` 的实现。

## 扩展知识

### Java 8 ~ 25 新特性大全

虽然很多公司仍然在用 Java 8，但是建议大家了解更多新版本的 Java 特性，尤其是 Java 17 和 Java 21，如果你要开发 AI 应用，这两个版本的优先级会更高。

详情查阅：[Java 8 ~ 25 新特性大全](https://www.codefather.cn/course/1803988290715377665/section/1962801453192523778)

### 元空间替代了永久代

因为 Java8 要把 JRockit 虚拟机和 Hotspot 虚拟机融合，而 JRockit 没有永久代，所以把 Hotspot 永久代给去了（本质也是永久代回收效率太低）。

详细可看：面试鸭《[为什么 Java8 移除了永久代，加了元空间？](https://www.mianshiya.com/question/1780933295228350466)》 这题。

### Lambda 表达式

#### 什么是 Lambda 表达式？

Lambda 表达式可以说是 Java 8 的杀手级特性。在这个特性出现之前，我们要实现一个简单的回调函数，只能通过匿名内部类的方式，代码又臭又长。

比如给按钮添加点击事件、或者创建一个新线程执行操作，必须要自己 new 接口并且编写接口的定义和实现代码。

```java
// Java 8 之前的写法，给按钮添加点击事件
button.addActionListener(new ActionListener() {
    @Override
    public void actionPerformed(ActionEvent e) {
        System.out.println("按钮被点击了");
    }
});

// 使用线程的传统写法
Thread thread = new Thread(new Runnable() {
    @Override
    public void run() {
        System.out.println("线程正在运行");
    }
});
```

Lambda 表达式的出现，让代码变得简洁优雅，告别匿名内部类！

```java
// Java 8 Lambda 写法
button.addActionListener(e -> System.out.println("按钮被点击了"));
Thread thread = new Thread(() -> System.out.println("线程正在运行"));
```

Lambda 表达式的语法非常灵活，可以根据参数个数和方法代码的复杂度选择不同的写法：

```java
// 无参数的 Lambda
Runnable r = () -> System.out.println("Hello Lambda!");

// 单个参数（可以省略括号）
Consumer<String> printer = s -> System.out.println(s);

// 多个参数
BinaryOperator<Integer> add = (a, b) -> a + b;
Comparator<String> comparator = (a, b) -> a.compareTo(b);

// 复杂的方法体（需要大括号和 return）
Function<String, String> processor = input -> {
    String processed = input.trim().toLowerCase();
    if (processed.isEmpty()) {
        return "空字符串";
    }
    return "处理后的字符串：" + processed;
};
```

#### 方法引用

Lambda 表达式还有一个实用特性叫做**方法引用**，可以看作是 Lambda 表达式的一种简写形式。当 Lambda 表达式只是调用一个已存在的方法时，使用方法引用代码会更简洁。

```java
List<String> names = Arrays.asList("鱼皮", "编程导航", "面试鸭");

// 使用 Lambda 表达式
names.forEach(name -> System.out.println(name));

// 使用方法引用（更简洁）
names.forEach(System.out::println);
```

实际开发中，方法引用经常用于获取某个 Java 对象的属性。比如使用 MyBatis Plus 来构造数据库查询条件时，经常会看到下面这种代码：

```java
LambdaQueryWrapper<User> lambdaQueryWrapper = new LambdaQueryWrapper<>();
lambdaQueryWrapper.eq(User::getName, "鱼皮");
```

方法引用有几种不同的形式，包括静态方法引用、实例方法引用、构造器引用，适用于不同的场景。

```java
// 静态方法引用
List<String> strings = Arrays.asList("1", "2", "3");
List<Integer> numbers = strings.stream()
    .map(Integer::parseInt)  // 等于 s -> Integer.parseInt(s)
    .collect(Collectors.toList());

// 实例方法引用
List<String> words = Arrays.asList("hello", "world", "java");
List<String> upperWords = words.stream()
    .map(String::toUpperCase)  // 等于 s -> s.toUpperCase()
    .collect(Collectors.toList());

// 构造器引用
List<String> nameList = Arrays.asList("鱼皮", "编程导航", "面试鸭");
List<Person> persons = nameList.stream()
    .map(Person::new)  // 等于 name -> new Person(name)
    .collect(Collectors.toList());
```

### 函数式接口

#### 什么是函数式接口？

函数式接口是**只有一个抽象方法的接口**。要玩转 Lambda 表达式，就必须了解函数式接口，因为 Lambda 表达式的本质是函数式接口的匿名实现。

函数式接口定义了 Lambda 表达式的参数和返回值类型，Lambda 表达式提供了这个接口的具体实现。两者相辅相成，让 Java 函数式编程起飞！

#### 常用的函数式接口

Java 8 提供了很多内置的函数式接口，让函数式编程变得简单直观。列举一些常用的：

1. Predicate 用于条件判断：

```java
// Predicate<T> 用于条件判断
Predicate<Integer> isEven = n -> n % 2 == 0;
Predicate<String> isEmpty = String::isEmpty;
Predicate<String> isNotEmpty = isEmpty.negate();  // 取反

List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6);
List<Integer> evenNumbers = numbers.stream()
    .filter(isEven)
    .collect(Collectors.toList());
```

2. Function 接口用于数据转换，支持函数组合，让代码逻辑更清晰：

```java
// Function<T, R> 用于转换
Function<String, Integer> stringLength = String::length;
Function<Integer, String> intToString = Object::toString;

// 函数组合
Function<String, String> addPrefix = s -> "前缀-" + s;
Function<String, String> addSuffix = s -> s + "-后缀";
Function<String, String> combined = addPrefix.andThen(addSuffix);
String result = combined.apply("鱼皮"); // "前缀-鱼皮-后缀"
```

3. Consumer 和 Supplier 接口分别用于消费和提供数据：

```java
// Consumer<T> 用于消费数据（无返回值）
Consumer<String> printer = System.out::println;
Consumer<String> logger = s -> log.info("处理数据：{}", s);
// 组合消费
Consumer<String> combinedConsumer = printer.andThen(logger);

// Supplier<T> 用于提供数据
Supplier<String> randomId = () -> UUID.randomUUID().toString();
Supplier<LocalDateTime> now = LocalDateTime::now;
```

4. BinaryOperator 接口用于二元操作，比如数学运算：

```java
// BinaryOperator<T> 用于二元操作
BinaryOperator<Integer> max = Integer::max;
BinaryOperator<String> concat = (a, b) -> a + b;
```

#### 自定义函数式接口

虽然实际开发中，我们更多的是使用 Java 内置的函数式接口，但大家还是要了解一下自定义函数式接口的写法，有个印象。

```java
// 创建自定义函数式接口
@FunctionalInterface
public interface Calculator {
    double calculate(double a, double b);
}
```

使用自定义函数式接口，代码会更简洁：

```java
// 使用自定义函数式接口
Calculator addition = (a, b) -> a + b;
Calculator subtraction = (a, b) -> a - b;
```

自定义函数式接口时，需要注意：

1. 函数式接口必须是接口类型，不能是类、抽象类或枚举

2. 必须且只能包含一个抽象方法，否则 Lambda 表达式可能无法匹配接口

3. 建议使用 `@FunctionalInterface` 注解，虽然这个注解不是强制的，但加上后编译器会帮你检查是否符合函数式接口的规范，如果不符合会报错

4. 可以包含默认方法 `default` 和静态方法 `static`，它们不是抽象方法，不影响单一抽象方法的要求

```java
// 创建自定义函数式接口
@FunctionalInterface
public interface Calculator {
    double calculate(double a, double b);

    // 可以有默认方法
    default double add(double a, double b) {
        return a + b;
    }
    
    // 可以有静态方法
    static Calculator multiply() {
        return (a, b) -> a * b;
    }
}
```

### 新的日期时间 API

Java 8 引入的新日期时间 API 解决了旧版 Date 和 Calendar 类的很多问题，比如线程安全、可变性、时区处理等等。

传统的日期处理方式：

```java
// 旧版本的复杂日期处理
Calendar cal = Calendar.getInstance();
cal.set(2024, Calendar.JANUARY, 15); // 注意月份从0开始
Date date = cal.getTime();

SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
String dateStr = sdf.format(date); // 线程不安全
```

使用新的日期时间 API，代码会更简洁：

```java
// 当前日期时间
LocalDate today = LocalDate.now(); // 2025-09-01
LocalTime now = LocalTime.now();   // 14:30:25.123
LocalDateTime dateTime = LocalDateTime.now(); // 2025-09-01T14:30:25.123

// 指定的日期时间
LocalDate specificDate = LocalDate.of(2025, 9, 1);
LocalTime specificTime = LocalTime.of(14, 30, 0);
LocalDateTime specificDateTime = LocalDateTime.of(2025, 9, 1, 14, 30, 0);
```

典型的应用场景是从字符串解析日期，一行代码就能搞定：

```java
// 从字符串解析
LocalDate parsedDate = LocalDate.parse("2025-09-01");
LocalDateTime parsedDateTime = LocalDateTime.parse("2025-09-01T14:30:25");

// 自定义格式解析
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm:ss");
LocalDateTime customParsed = LocalDateTime.parse("2025/09/01 14:30:25", formatter);
```

还有日期和时间的计算，也变得更直观、见名知意：

```java
LocalDate today = LocalDate.now();

// 基本的日期计算
LocalDate nextWeek = today.plusWeeks(1);
LocalDate lastMonth = today.minusMonths(1);
LocalDate nextYear = today.plusYears(1);

// 时间段计算
LocalDate startDate = LocalDate.of(2024, 1, 28);
LocalDate endDate = LocalDate.of(2025, 9, 1);
Period period = Period.between(startDate, endDate);
System.out.println("相差 " + period.getMonths() + " 个月 " + period.getDays() + " 天");

// 精确时间差计算
LocalDateTime start = LocalDateTime.now();
LocalDateTime end = LocalDateTime.of(2025, 9, 1, 14, 30, 0);
Duration duration = Duration.between(start, end);
System.out.println("执行时间：" + duration.toMillis() + " 毫秒");
```

还支持时区处理和时间戳处理，不过这段代码就没必要记了，现在有了 AI，直接让它生成时间日期操作就好。

```java
// 带时区的日期时间
ZonedDateTime beijingTime = ZonedDateTime.now(ZoneId.of("Asia/Shanghai"));
ZonedDateTime newYorkTime = ZonedDateTime.now(ZoneId.of("America/New_York"));

// 时区转换
ZonedDateTime beijingToNewYork = beijingTime.withZoneSameInstant(ZoneId.of("America/New_York"));

// 获取所有可用时区
ZoneId.getAvailableZoneIds().stream()
    .filter(zoneId -> zoneId.contains("Shanghai"))
    .forEach(System.out::println);

// 时间戳处理
Instant instant = Instant.now();
long epochSecond = instant.getEpochSecond();
ZonedDateTime fromInstant = instant.atZone(ZoneId.systemDefault());
```

有了这套 API，我们不需要使用第三方的时间日期处理库，也能解决大多数问题。

![](Z:/Public/images/jUPrvHyN_Gbydol71Gq_mianshiya.webp)

### 接口默认方法

Java 8 引入的接口默认方法解决了接口演化的问题。

在默认方法出现之前，如果你想给一个被广泛使用的接口添加新方法，就会影响所有已有的实现类。想象一下，如果要给 Collection 接口添加一个新方法，`ArrayList`、`LinkedList` 等所有的实现类都需要修改，成本很大。

默认方法让接口可以在**不破坏现有代码的情况下添加新功能**。

比如想给接口增加一个 `drawWithBorder` 方法：

```java
public interface Drawable {
    // 已有抽象方法
    void draw();
    
    // 默认方法
    default void drawWithBorder() {
        System.out.println("绘制边框");
        draw();
        System.out.println("边框绘制完成");
    }
}
```

使用默认方法后，实现类可以选择重写默认方法，也可以直接使用：

```java
// 实现类可以选择重写默认方法
public class Circle implements Drawable {
    @Override
    public void draw() {
        System.out.println("绘制圆形");
    }
    
    // 可以重写默认方法
    @Override
    public void drawWithBorder() {
        System.out.println("绘制圆形边框");
        draw();
    }
}
```

Java 8 为 Collection 接口添加了 stream、removeIf 等方法，都是默认方法：

![](Z:/Public/images/macQVcGRUM5Rxjsz_mianshiya.webp)

需要注意的是，如果一个类实现多个接口，并且这些接口有相同的默认方法时，需要显式解决冲突：

```java
interface A {
    default void hello() {
        System.out.println("Hello from A");
    }
}

interface B {
    default void hello() {
        System.out.println("Hello from B");
    }
}

// 实现类必须重写冲突的方法
class C implements A, B {
    @Override
    public void hello() {
        // 可以调用特定接口的默认方法
        A.super.hello();
        B.super.hello();
        // 或者提供自己的实现
        System.out.println("Hello from C");
    }
}
```

类似的，Java 8 还支持接口的静态方法，前面讲函数式接口的时候有提到。

### Stream API

#### 什么是 Stream API？

Stream API 是 Java 8 另一个重量级特性，它让集合处理变得既优雅又高效。学大数据的同学应该对它不陌生。

在 Stream API 出现之前，我们处理集合数据只能通过传统的循环，需要大量的样板代码。

比如过滤列表中的数据、将小写转为大写并排序：

```java
List<String> words = Arrays.asList("apple", "banana", "cherry");

// 传统的处理方式
List<String> result = new ArrayList<>();
for (String word : words) {
    if (word.length() > 5) {
        String upperCase = word.toUpperCase();
        result.add(upperCase);
    }
}
Collections.sort(result);
```

如果使用 Stream API，可以让同样的逻辑变得更简洁直观：

```java
// 使用 Stream 的方式
List<String> result = words.stream()
    .filter(word -> word.length() > 5)    // 过滤长度大于 5 的单词
    .map(String::toUpperCase)             // 转换为大写
    .sorted()                             // 排序
    .collect(Collectors.toList());        // 收集结果
```

Stream 不是数据结构，而是像工厂流水线一样处理数据的工具。数据从一端进入，经历过滤、转换、排序等一系列加工步骤后，最终输出我们想要的结果。这种链式调用让代码读起来就像自然语言一样流畅。

![](Z:/Public/images/2Ui6VWR859ixFbya_mianshiya.webp)

#### Stream 操作类型

Stream 的操作分为中间操作和终端操作。中间操作是“懒惰”的，只有在遇到终端操作时才会真正执行。

filter 过滤和 `map` 映射都是中间操作，比如下面这段代码，并不会对列表进行过滤和转换：

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

numbers.stream()
    .filter(n -> n > 3) // 中间操作：过滤大于3的数字
    .map(n -> n * n)    // 中间操作：平方
```

一些常用的中间操作：

- `filter()` 过滤元素

- `map()` 转换元素

- `sorted()` 排序

- `distinct()` 去重

- `limit()` 限制数量

- `skip()` 跳过元素

给上面的代码加上一个终端操作 collect 后，才会真正执行：

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// 演示中间操作和终端操作
numbers.stream()
    .filter(n -> n > 3)            // 中间操作：过滤大于3的数字
    .map(n -> n * n)               // 中间操作：平方
    .collect(Collectors.toList()); // 终端操作：收集结果
```

一些常用的终端操作：

- `collect()` 收集到集合

- `forEach()` 遍历每个元素

- `count()` 统计数量

- `findFirst()` 查找第一个

- `anyMatch()` 是否有匹配的

- `reduce()` 归约操作

#### 实际应用

分享一些 Stream API 在开发中的典型用例。

1. 对列表进行分组，把 List 转为 Map：

```java
Map<Boolean, List<Integer>> partitioned = numbers.stream()
    .filter(n -> n > 3) // 中间操作：过滤大于3的数字
    .map(n -> n * n)    // 中间操作：平方
    .collect(Collectors.partitioningBy(n -> n % 2 == 0)); // 终端操作：按奇偶分组
```

2. 使用 Stream 内置的统计功能，对数据进行统计：

```java
// 统计操作
IntSummaryStatistics stats = numbers.stream()
    .mapToInt(Integer::intValue)
    .summaryStatistics();

System.out.println("数量：" + stats.getCount());
System.out.println("总和：" + stats.getSum());
System.out.println("平均值：" + stats.getAverage());
System.out.println("最大值：" + stats.getMax());
System.out.println("最小值：" + stats.getMin());
```

3. 按照对象的某个字段进行分组计算：

```java
List<Person> people = Arrays.asList(
    new Person("张三", 25, "北京"),
    new Person("鱼皮", 18, "上海"),
    new Person("李四", 25, "北京"),
    new Person("老二", 35, "上海")
);

// 按城市分组
Map<String, List<Person>> byCity = people.stream()
    .collect(Collectors.groupingBy(Person::getCity));

// 按城市分组并统计年龄
Map<String, Double> avgAgeByCity = people.stream()
    .collect(Collectors.groupingBy(
        Person::getCity,
        Collectors.averagingInt(Person::getAge)
    ));

// 按城市分组并收集姓名
Map<String, List<String>> namesByCity = people.stream()
    .collect(Collectors.groupingBy(
        Person::getCity,
        Collectors.mapping(Person::getName, Collectors.toList())
    ));
```

学过数据库的同学应该对这种操作并不陌生，SQL 语句中的很多操作都可以通过 Stream 实现。这也是 Stream 的典型应用场景，对数据库中查出的数据进行业务层面的运算。

#### 并行流

并行流是 Stream API 的另一个强大特性，它可以自动利用多核 CPU 处理器加速数据处理任务的执行。

在此之前，我们要实现并行处理集合数据，需要手动管理线程池和任务分割，代码复杂且容易出错。

但有了 Stream API，一行代码就能创建并行流，比如过滤并计算数据的总和：

```java
List<Integer> largeList = IntStream.rangeClosed(1, 1000000)
    .boxed()
    .collect(Collectors.toList());

// 并行处理，只需要改一个方法调用
long parallelCount = largeList.parallelStream()
    .filter(n -> isPrime(n))
    .count();
```

并行流底层使用了 Fork/Join 框架，把大任务拆分成小任务，分配给多个线程同时执行，最后把结果合并起来。这个过程对开发者完全透明，只需要调用 `parallelStream()` 即可。

![](Z:/Public/images/YBXFsvLw1CEjNGra_mianshiya.webp)

但也正因如此，实际开发中，要谨慎使用并行流！

因为它使用的是 JVM 全局的 `ForkJoinPool.commonPool()`，默认线程数等于 CPU 核心数减 1。如果某个并行流任务阻塞了线程，会影响其他并行流的性能。

而且并行流不一定就更快，特别是对于简单操作或小数据集，切换线程的开销可能超过并行带来的收益。

并行流更适合大数据量、CPU 密集型任务，比如复杂计算、图像处理，不适合 I/O 密集型任务，比如网络请求。而且只要涉及到并发场景，就要考虑到线程安全问题。

### `Optional`

#### `Optional` 的作用

NullPointerException 一直是 Java 程序员的噩梦，学 Java 的同学应该都被它折磨过。

![](Z:/Public/images/4ClVdtZNksZUa3Z2_mianshiya.webp)

之前，我们只能通过大量的 if 语句检查 null 来避免空指针异常，不仅代码又臭又长，而且稍微不注意就漏掉了。

```java
// 传统的空值检查
public String getDefaultName(User user) {
    if (user != null) {
        String name = user.getName();
        if (name != null && !name.isEmpty()) {
            return name.toUpperCase();
        }
    }
    return "unknown";
}
```

`Optional` 类的引入就是为了优雅地处理可能为空的值，可以先把它理解为“包装器”，把可能为空的对象封装起来。

创建 `Optional` 对象：

```java
// 创建 Optional 对象
Optional<String> optional1 = Optional.of("Hello");          // 不能为 null
Optional<String> optional2 = Optional.ofNullable(getName()); // 可能为 null
Optional<String> optional3 = Optional.empty();              // 空的 Optional
```

`Optional` 提供了多种处理空值的方法：

```java
// 检查是否有值
if (optional.isPresent()) {
    System.out.println(optional.get());
}

// 更优雅的方式，如果对象存在则输出
optional.ifPresent(System.out::println);
```

还可以设置默认值策略，比如空值时抛出异常：

```java
// 提供默认值
String result1 = optional.orElse("默认值");
String result2 = optional.orElseGet(() -> generateDefaultValue());
String result3 = optional.orElseThrow(() -> new IllegalStateException("值不能为空"));
```

除了前面这些基本方法外，`Optional` 甚至提供了一套完整的 API 来处理空值场景！

跟 Stream API 类似，你可以对 `Optional` 封装的数据进行过滤、映射等操作：

```java
optional
    .filter(s -> s.length() > 5)
    .map(String::toUpperCase)
    .ifPresentOrElse(
        System.out::println,                   // 有值时执行
        () -> System.out.println("没有值")      // 无值时执行
    );
```

#### 应用场景

鱼皮经常使用 `Optional` 来简化空值判断：

```java
int pageNum = Optional.ofNullable(params.getPageNum())
    .orElseThrow(() -> new RuntimeException("pageNum不能为空"));
```

如果不用 `Optional`，就要写下面这段代码：

```java
int pageNum;
if (params.getPageNum() != null) {
    pageNum = params.getPageNum();
} else {
    throw new RuntimeException("pageNum不能为空");
}
```

`Optional` 的一个典型应用场景是在集合中进行安全查找：

```java
List<String> names = Arrays.asList("张三", null, "李四", "", "王五");

// 使用 Optional 进行安全的查找
Optional<String> foundName = names.stream()
    .filter(Objects::nonNull)
    .filter(name -> name.startsWith("张"))
    .findFirst();

foundName.ifPresentOrElse(
    name -> System.out.println("找到了：" + name),
    () -> System.out.println("没有找到匹配的名字")
);
```

`Optional` 详细可查看面试鸭[《什么是 `Optional` 类？》 这题](https://www.mianshiya.com/bank/1787463103423897602/question/1800345746421391361)

### `CompletableFuture`

`CompletableFuture` 提供了一个新的异步编程模型，简化了异步任务的编写和管理。

```java
CompletableFuture.supplyAsync(() -> "Hello")
                 .thenApply(s -> s + " World")
                 .thenAccept(System.out::println);
```

- [485. 什么是 Java 的 `CompletableFuture`？](https://www.mianshiya.com/question/1780933294951526402)

### `StampedLock`

`StampedLock` 可查看面试鸭 [《`StampedLock` 用过吗？》](https://www.mianshiya.com/question/1780933294947332098) 这题。

## 面试官追问

#### 提问：Lambda 表达式和匿名内部类有什么区别？性能上有差异吗？

回答：主要有 3 点区别。第一，Lambda 只能实现函数式接口，匿名内部类可以实现任意接口或继承类。第二，匿名内部类每次都会生成一个新的 class 文件，Lambda 用 invokedynamic 指令动态生成，不会产生额外的 class 文件。第三，匿名内部类的 this 指向自身，Lambda 的 this 指向外部类。性能上，Lambda 首次调用会稍慢，因为要做 invokedynamic 的链接，但后续调用和匿名内部类差不多，甚至更快一点，因为 JVM 可以做更多优化。

#### 提问：Stream 的 parallelStream 什么时候用？有什么坑？

回答：parallelStream 适合数据量大、计算密集的场景，比如 100 万条数据做复杂计算。坑有几个：一是它用的是公共的 ForkJoinPool，如果里面有阻塞操作会影响其他并行流；二是小数据量反而更慢，线程切换开销大于并行收益；三是要注意线程安全，不能在 Lambda 里修改共享变量；四是有些操作并行后顺序会乱，比如 forEach，要用 forEachOrdered 才能保证顺序。

#### 提问：`Optional` 应该在什么场景使用？有人说不该用在字段上，你怎么看？

回答：`Optional` 主要用在方法返回值上，表示“这个值可能不存在”，让调用方显式处理空值。不建议用在字段上有几个原因：`Optional` 不能序列化，会影响 JSON、ORM 框架的使用；字段本身就可以是 null，加一层 `Optional` 包装增加复杂度；每次访问都要 `get` 或 orElse，代码反而更啰嗦。方法参数上也不推荐用，直接传 null 然后方法内部判断就行了。

#### 提问：接口默认方法和抽象类有什么区别？什么时候用接口，什么时候用抽象类？

回答：主要区别在于：接口不能有构造方法，抽象类可以有；接口的字段默认是 public static final，抽象类可以有普通字段；一个类可以实现多个接口，但只能继承一个抽象类。选择上，如果是定义一种能力或行为，用接口，比如 Comparable、Serializable；如果是定义一类事物的共性，有状态需要维护，用抽象类，比如 AbstractList、AbstractMap。Java 8 之后接口能力增强了，优先考虑接口，除非确实需要共享状态或构造逻辑。
