# Lombok

## Lombok 介绍

### Lombok 是什么？

![Lombok 主要作用是什么？它是干嘛的？](http://public.file.lvshuhuai.cn/images\169059305581280.jpeg)

#### 它是什么？

Lombok 是一个超酷的 Java 库，旨在通过**减少样板代码来提升开发效率**。Java 语言中有许多重复且冗长的代码，比如 `getter/setter`、构造方法、`equals` 和 `hashCode` 方法等，这些代码往往是必需的，但会增加代码量，使类变得臃肿、可读性下降。Lombok 提供了各种注解，自动生成这些样板代码，帮助开发者专注于核心业务逻辑。

#### 主要作用

- **减少样板代码**：Lombok 能自动生成很多 Java 类中常见的样板代码，例如 `getter/setter` 方法、构造函数、`toString()`、`equals()` 和 `hashCode()` 等。这些方法通常没有复杂逻辑，却不可或缺，Lombok 通过注解让这些方法自动生成，使代码更简洁。
- **提高代码可读性**：Lombok 避免了大量的重复代码，使类结构更清晰，让开发人员更容易理解类的核心逻辑。
- **节省开发时间**：减少重复性代码编写时间，加快开发流程。
- **减少代码出错的机会**：自动生成的代码不易出错，避免了手动编写 `getter/setter`、构造函数时可能出现的错误，尤其是在较大的项目中。

#### 常用注解

以下是一些 Lombok 中的常用注解，它们分别解决不同类型的样板代码需求：

- **`@Getter` / `@Setter`**：为类中的字段自动生成 `getter` 和 `setter` 方法，减少手动创建这些方法的时间。
- **`@ToString`**：生成 `toString()` 方法，方便打印对象内容，用于调试。
- **`@EqualsAndHashCode`**：自动生成 `equals()` 和 `hashCode()` 方法，尤其适合对集合中的对象进行比较和查找。
- **`@NoArgsConstructor` / `@AllArgsConstructor` / `@RequiredArgsConstructor`**：自动生成无参构造函数、全参构造函数以及包含必要参数的构造函数。
- **`@Data`**：这是一个复合注解，等效于 `@Getter`、`@Setter`、`@ToString`、`@EqualsAndHashCode` 和 `@RequiredArgsConstructor` 的组合，适合需要完整数据操作的简单类。
- **`@Builder`**：实现构建者模式，为类创建复杂对象时提供灵活的方式。
- **`@Value`**：用于创建不可变对象（immutable objects），类似于 `@Data`，但所有字段都是 `final`。
- **`@Slf4j`**：自动为类注入 `Slf4j` 日志对象，方便记录日志。
- **`@SneakyThrows`**：用于 “隐藏” 方法抛出的检查型异常（checked exception），避免显式声明 `throws`。

#### 使用示例

以下是一个使用 Lombok 简化代码的示例。假设我们有一个 `Person` 类：

```java
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Person {
	// 姓名
    private String name;
    // 年龄
    private int age;
}
```

> 上面的代码通过 `@Data` 注解自动生成了 `getter`、`setter`、`toString()`、`equals()`、`hashCode()` 等方法。`@NoArgsConstructor` 和 `@AllArgsConstructor` 则分别生成了无参构造器和包含所有字段的全参构造器。相比于手动编写这些方法，Lombok 让代码变得更加简洁。

以上代码相当于：

```kotlin
public class Person {
    private String name;
    private int age;

    public String getName() {
        return this.name;
    }

    public int getAge() {
        return this.age;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public boolean equals(Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof Person)) {
            return false;
        } else {
            Person other = (Person)o;
            if (!other.canEqual(this)) {
                return false;
            } else if (this.getAge() != other.getAge()) {
                return false;
            } else {
                Object this$name = this.getName();
                Object other$name = other.getName();
                if (this$name == null) {
                    if (other$name != null) {
                        return false;
                    }
                } else if (!this$name.equals(other$name)) {
                    return false;
                }

                return true;
            }
        }
    }

    protected boolean canEqual(Object other) {
        return other instanceof Person;
    }

    public int hashCode() {
        int PRIME = true;
        int result = 1;
        result = result * 59 + this.getAge();
        Object $name = this.getName();
        result = result * 59 + ($name == null ? 43 : $name.hashCode());
        return result;
    }

    public String toString() {
        String var10000 = this.getName();
        return "Person(name=" + var10000 + ", age=" + this.getAge() + ")";
    }

    public Person() {
    }

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

#### 局限性与注意事项

- **学习曲线**：Lombok 注解生成的代码不可见，过度依赖 Lombok 可能会导致新成员理解代码逻辑困难，特别是对未熟悉该工具的团队成员。
- **兼容性问题**：Lombok 基于注解处理器和字节码操作，某些 IDE、框架、Java 版本升级时可能会导致 Lombok 无法正常工作，需要额外的配置或更新。
- **代码调试**：Lombok 自动生成的代码在调试时不可见，可能会影响对代码执行流程的理解。尤其是在调试 `equals`、`hashCode` 或复杂构造器等方法时。

#### 总结

Lombok 是一个非常实用的 Java 工具，通过自动生成样板代码，帮助开发人员提升开发效率和代码简洁性。然而，使用时也需要平衡其便利性与代码可读性之间的关系，确保团队中的每个人都能理解和掌握这些工具带来的影响。

## Lombok 安装与配置

### Lombok 依赖安装

要想在 Java 项目中使用 Lombok，首先，你需要将其添加为项目依赖。本小节中，将详细介绍安装方法，包括 Maven、Gradle 两种构建工具的配置方法。

#### 添加 Lombok 依赖

#### 使用 Maven

在 Maven 项目中，可以通过在 `pom.xml` 文件中添加 Lombok 的依赖：

```xml
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.18.20</version> <!-- 注意查看最新的 Lombok 版本，并替换此处的版本号 -->
    <scope>provided</scope>
</dependency>
```

> **TIP**: `scope` 设置为 `provided`，表示仅编译时使用 Lombok，而在项目打包时，并不会将 Lombok 依赖打包进去，可减少最终项目 `Jar` 包的体积大小。

#### 使用 Gradle

对于 Gradle 项目，可以在 `build.gradle` 文件中添加Lombok 的依赖：

```csharp
dependencies {
    compileOnly 'org.projectlombok:lombok:1.18.20' // 编译时依赖
    annotationProcessor 'org.projectlombok:lombok:1.18.20' // 注解处理
}
```

### Lombok 插件安装

#### IDEA 安装 Lombok 插件

##### 开始安装

根据你的系统依次点击菜单：

- Windows 系统：*File -> Settings... -> Plugins*;
- Mac 系统：*IntelliJ IDEA -> Preferences -> Plugins*;

![img](http://public.file.lvshuhuai.cn/images\169059578851069.jpeg)

点击 `Marketplace` ， 进入插件市场, 输入关键词 `lombok`, 搜索该插件：

![安装 Lombok 插件](http://public.file.lvshuhuai.cn/images\169059594938746.jpeg)

然后，点击 *Install* 按钮开始安装，这里已经安装过了，所以显示的打钩。安装完成后，点击 *Apply* 按钮应用设置即可。

至此，IDEA 中安装 Lombok 插件就大功告成啦，非常简单~

#### Eclipse 安装 Lombok 插件

##### 下载插件

访问 Lombok 官网：https://projectlombok.org/download ，点击下载最新版的 Jar 包到本地，或者点击 [older versions](https://projectlombok.org/all-versions) , 下载自己想要的老版本：

![下载 Lombok 插件](http://public.file.lvshuhuai.cn/images\169060085073147.jpeg)

##### 移动 Jar 包

将下载完成的 `lombok.jar` 移动到 Eclipse 安装目录下，和 `eclipse.ini` 处于统一目录中：

![img](http://public.file.lvshuhuai.cn/images\169060110549539.jpeg)

##### 执行安装命令

打开 `cmd` 命令行，执行如下命令来安装 `lombok.jar` :

```undefined
java -jar D:\DEV_ENV\eclipse\lombok.jar
```

> 上面的路径，请根据自己实际的安装目录自行调整。

![img](http://public.file.lvshuhuai.cn/images\169060128159993.jpeg)

执行完成后，若跳出如下 lombok 弹出框，点击*确定*按钮：

![img](http://public.file.lvshuhuai.cn/images\169060137602835.jpeg)

点击 *Specify location ...* 按钮，选择 eclipse 位置，点击 *Install / Update* 按钮进行更新或者安装：

![img](http://public.file.lvshuhuai.cn/images\169060191209385.jpeg)

安装成功后，点击 *Quit Installer* 按钮退出弹框：

![img](http://public.file.lvshuhuai.cn/images\169060207181427.jpeg)

##### 验证是否安装成功

检验是否安装成功，可打开 `eclipse.ini` 文件，若在配置文件中找到了类似如下配置，表示成功了：

![img](http://public.file.lvshuhuai.cn/images\169060220372520.jpeg)

##### 最后

安装完成后，**重启 eclipse，然后 clean project** 即可正常使用该插件啦~

## Lombok 注解

### Lombok @Getter @Setter 注解: 简化属性操作

Lombok 提供的 `@Getter` 和 `@Setter` 注解是最常用的注解之一，主要用于自动生成类的 `getter` 和 `setter` 方法。这些方法可以大大减少手动编写代码的工作量，让代码更简洁、更易读。

#### 基本用法

- **`@Getter`**：自动为字段生成 getter 方法。
- **`@Setter`**：自动为字段生成 setter 方法。

这两个注解可以单独使用，也可以同时使用。可以直接加在类上，让类中的所有字段都生成 `getter` 和 `setter` 方法；也可以加在具体字段上，仅生成该字段的 `getter` 或 `setter`。

#### 示例代码

```less
import lombok.Getter;
import lombok.Setter;

public class User {
    @Getter @Setter
    private String name;

    @Getter
    private int age;

    // 无需手动编写 getter 和 setter 方法
}
```

上面的代码会自动生成如下方法：

```typescript
public String getName() {
    return name;
}

public void setName(String name) {
    this.name = name;
}

public int getAge() {
    return age;
}

// age 字段没有设置 @Setter 注解，因此没有生成 getter 方法
```

#### 类级别注解

可以在类上直接使用 `@Getter` 和 `@Setter`，为类中的所有字段生成 `getter` 和 `setter` 方法：

```java
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class User {
    private String name;
    private int age;
}
```

此时，`User` 类中的所有字段都会自动生成 `getter` 和 `setter` 方法。

#### 控制访问级别

Lombok 的 `@Getter` 和 `@Setter` 支持控制生成方法的访问级别，例如可以为某些字段生成 `protected` 或 `private` 的 `getter/setter`。可以通过 `AccessLevel` 参数来设置访问级别：

```java
import lombok.Getter;
import lombok.Setter;
import lombok.AccessLevel;

public class User {
    @Getter(AccessLevel.PUBLIC)
    @Setter(AccessLevel.PROTECTED)
    private String name;

    @Getter(AccessLevel.PRIVATE)
    private int age;
}
```

在这个例子中：

- `name` 字段的 getter 方法是 `public` 的，setter 方法是 `protected` 的。
- `age` 字段的 getter 方法是 `private` 的，因此只能在类内部访问。

`AccessLevel` 提供了以下选项：

- `PUBLIC`：公共级别（默认）；
- `PROTECTED`：受保护级别；
- `PACKAGE`：包访问级别；
- `PRIVATE`：私有级别；
- `MODULE`（Java 9+）：模块级别；

#### 使用场景

`@Getter` 和 `@Setter` 通常用于以下场景：

- **数据传输对象（DTO）**：在需要封装数据的类中，自动生成 `getter` 和 `setter` 可以简化代码。
- **实体类**：在数据库实体类中（如使用 JPA 时），使用 `getter` 和 `setter` 可以方便地进行数据操作。
- **简单模型类**：在只存储数据、不包含业务逻辑的模型类中，大量 `getter` 和 `setter` 是常见需求，使用 Lombok 可以提高开发效率。

#### 总结

Lombok 的 `@Getter` 和 `@Setter` 注解简化了数据类的开发，自动生成必要的访问方法，避免了手动编写重复代码。它们非常适合用于 DTO、简单实体类和模型类中，使代码更加简洁和易于维护。

### Lombok @ToString 注解：快速打印对象内容

Lombok 的 `@ToString` 注解用于自动生成 `toString()` 方法，帮助快速打印对象的内容，以便调试或日志记录。默认情况下，`@ToString` 会将类中所有非静态字段包含在 `toString()` 方法中，并按字段声明的顺序显示字段值。

#### 基本用法

`@ToString` 可以直接加在类上，自动生成 `toString()` 方法，包含所有字段的名称和值。

#### 示例

```java
import lombok.ToString;

@ToString
public class User {
    private String name;
    private int age;
}
```

上面的代码会生成以下 `toString()` 方法：

```java
public String toString() {
    return "User(name=" + this.name + ", age=" + this.age + ")";
}
```

这样可以直接使用 `System.out.println(user);` 输出对象的字符串表示。

#### 常见参数

`@ToString` 注解提供了多种配置参数，以便定制 `toString()` 方法的生成方式。

##### `exclude`

`exclude` 参数用于排除不希望包含在 `toString()` 方法中的字段。可以指定一个或多个字段名：

```java
import lombok.ToString;

@ToString(exclude = "password")
public class User {
    private String name;
    private int age;
    private String password;
}
```

此时生成的 `toString()` 方法将不会包含 `password` 字段。

##### `callSuper`

`callSuper` 参数决定是否调用父类的 `toString()` 方法。如果当前类继承了一个父类，且父类的 `toString()` 方法中有重要的信息，可以将 `callSuper` 设置为 `true`，以便将父类的信息包含进来：

```java
import lombok.ToString;

@ToString(callSuper = true)
public class Employee extends User {
    private String position;
}
```

##### `onlyExplicitlyIncluded`

`onlyExplicitlyIncluded` 参数用于控制仅生成包含 `@ToString.Include` 注解的字段。这种方式适合想要手动选择部分字段，而不是默认全部生成的情况。

```java
import lombok.ToString;

@ToString(onlyExplicitlyIncluded = true)
public class User {
    @ToString.Include
    private String name;
    
    @ToString.Include
    private int age;

    private String password; // 未添加 @ToString.Include，不会包含在 toString() 中
}
```

#### 注意事项

- **隐私数据**：`@ToString` 默认包含所有字段，对于敏感信息（如密码、身份证号等），要特别小心，确保使用 `exclude` 或 `onlyExplicitlyIncluded` 排除这些字段。
- **继承关系**：`callSuper` 可以帮助将父类的字段包含在 `toString()` 中，但应根据项目需求合理配置。
- **调试利器**：`@ToString` 能快速生成有用的字符串表示，对于调试和日志记录非常实用。

#### 小结

Lombok 的 `@ToString` 注解极大简化了 `toString()` 方法的编写，特别适用于需要频繁输出对象信息的场景。通过合理配置参数，如 `exclude`、`callSuper` 和 `onlyExplicitlyIncluded`，可以定制 `toString()` 的输出内容。合理地使用 `@ToString`，不仅可以提升开发效率，还能保持代码整洁，减少出错几率。

### Lombok @EqualsAndHashCode 注解：简化对象比较

Lombok 的 `@EqualsAndHashCode` 注解用于自动生成 `equals()` 和 `hashCode()` 方法，这两个方法对于对象比较和在集合中的使用非常重要。`equals()` 方法决定了对象的比较方式，而 `hashCode()` 则影响对象在散列集合（如 `HashSet` 和 `HashMap`）中的表现。

#### 基本用法

默认情况下，`@EqualsAndHashCode` 会使用所有非静态字段来生成 `equals()` 和 `hashCode()` 方法，这意味着两个对象在所有字段的值都相等时会被认为相等。

#### 示例

```java
import lombok.EqualsAndHashCode;

@EqualsAndHashCode
public class User {
    private String name;
    private int age;
}
```

上面的代码会生成如下 `equals()` 和 `hashCode()` 方法：

- `equals()` 方法会逐个比较所有非静态字段的值。
- `hashCode()` 方法则基于这些字段生成哈希码。

这样，当两个 `User` 对象的 `name` 和 `age` 值相同时，它们会被视为相等。

#### 常用参数

`@EqualsAndHashCode` 提供了几个配置参数，允许自定义 `equals()` 和 `hashCode()` 方法的生成方式。

##### `exclude`

`exclude` 参数用于指定不包含在 `equals()` 和 `hashCode()` 方法中的字段。可以排除某些字段来避免它们影响比较结果。

```java
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(exclude = "age")
public class User {
    private String name;
    private int age;
}
```

在这个示例中，`age` 字段不会被包含在 `equals()` 和 `hashCode()` 方法中。因此，只要 `name` 字段的值相同，两个 `User` 对象就会被认为相等。

##### `callSuper`

`callSuper` 参数决定是否调用父类的 `equals()` 和 `hashCode()` 方法。如果当前类继承了一个父类，并且希望在比较时将父类的字段也考虑在内，可以将 `callSuper` 设置为 `true`。

```java
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(callSuper = true)
public class Employee extends User {
    private String position;
}
```

当 `callSuper` 为 `true` 时，`Employee` 类的 `equals()` 和 `hashCode()` 方法会首先调用 `User` 类的对应方法，然后再处理 `Employee` 自己的字段。

##### `onlyExplicitlyIncluded`

`onlyExplicitlyIncluded` 参数用于控制 `equals()` 和 `hashCode()` 方法仅包含那些被 `@EqualsAndHashCode.Include` 标记的字段。可以通过该方式精确选择哪些字段用于比较。

```java
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class User {
    @EqualsAndHashCode.Include
    private String name;

    private int age; // 未添加 @EqualsAndHashCode.Include，不会影响 equals 和 hashCode
}
```

在这个例子中，`age` 字段不会包含在 `equals()` 和 `hashCode()` 方法中。只有 `name` 字段会影响对象的比较结果。

#### 注意事项

- **排除可变字段**：尽量避免使用可变字段（如集合、数组）作为 `equals()` 和 `hashCode()` 的依据，以防止因值变化导致哈希码不一致的问题。
- **继承关系**：如果类涉及继承关系，并且希望子类对象在比较时包含父类的字段，建议设置 `callSuper = true`。
- **性能优化**：在需要频繁比较或存储对象的场景下，合理地定制 `equals()` 和 `hashCode()` 的字段可以提高性能。

#### 小结

Lombok 的 `@EqualsAndHashCode` 注解通过自动生成 `equals()` 和 `hashCode()` 方法，大大简化了对象比较的代码编写。通过使用 `exclude`、`callSuper` 和 `onlyExplicitlyIncluded` 参数，可以灵活控制哪些字段会影响对象的比较结果。

### Lombok @Constructor 系列注解：轻松生成类的构造方法

Lombok 提供了一系列构造器注解，帮助开发者**轻松生成构造方法**。主要包括 `@NoArgsConstructor`、`@AllArgsConstructor` 和 `@RequiredArgsConstructor`，可以根据需要自动生成无参、全参或指定参数的构造器。

#### `@NoArgsConstructor`

`@NoArgsConstructor` 注解用于生成一个无参构造方法。在某些框架中（如 JPA 或 Spring）需要无参构造器，这个注解非常有用。

##### 示例

```java
import lombok.NoArgsConstructor;

@NoArgsConstructor
public class User {
    private String name;
    private int age;
}
```

这段代码会生成一个无参构造方法：

```java
public User() {
    super();
}
```

##### 强制初始化 `final` 字段

如果类中包含 `final` 字段，`@NoArgsConstructor` 默认无法生成构造方法，除非添加 `force=true` 参数，使 `final` 字段自动初始化为默认值：

```java
@NoArgsConstructor(force = true)
public class User {
    private final String name;
    private int age;
}
```

这将生成一个无参构造器，并将 `name` 初始化为空字符串或其他默认值。

#### `@AllArgsConstructor`

`@AllArgsConstructor` 用于生成包含所有字段的构造方法，可以轻松创建带有完整数据的对象。

##### 示例

```java
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class User {
    private String name;
    private int age;
}
```

这段代码会生成如下构造方法：

```java
public User(String name, int age) {
    this.name = name;
    this.age = age;
}
```

使用 `@AllArgsConstructor` 创建对象时，可以一次性指定所有字段的值。

#### `@RequiredArgsConstructor`

`@RequiredArgsConstructor` 用于生成包含 “必需” 字段的构造方法。这里的 “必需” 字段指的是那些 `final` 或带有 `@NonNull` 注解的字段。其他字段不会包含在构造方法中。

##### 示例

```java
import lombok.RequiredArgsConstructor;
import lombok.NonNull;

@RequiredArgsConstructor
public class User {
    @NonNull
    private String name;
    private int age;
}
```

这段代码会生成如下构造方法：

```java
public User(String name) {
    this.name = name;
}
```

只有 `name` 字段会被包含在构造方法中，因为它被 `@NonNull` 标注。未被 `@NonNull` 标注的字段 `age` 将不会包含在 `@RequiredArgsConstructor` 生成的构造方法中。

#### 多个构造器的组合

Lombok 允许将这些注解组合使用，比如同时使用 `@NoArgsConstructor` 和 `@AllArgsConstructor`，这样类会既有无参构造器，也有全参构造器。

```java
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@NoArgsConstructor
@AllArgsConstructor
public class User {
    private String name;
    private int age;
}
```

这样可以根据需求选择不同的构造方式。

#### 小结

Lombok 的构造器注解系列大大简化了构造方法的编写：

- **`@NoArgsConstructor`** 生成无参构造器，适合依赖框架的场景。
- **`@AllArgsConstructor`** 生成全参构造器，便于快速创建对象。
- **`@RequiredArgsConstructor`** 仅生成包含 `final` 和 `@NonNull` 字段的构造器，适合强制要求某些字段必须赋值的场景。

通过合理使用这些注解，可以根据项目需求自动生成所需的构造方法，提升开发效率并减少样板代码。

### Lombok @Data 注解：快速生成类常用方法

#### 什么是 Lombok @Data 注解？

> 在 Lombok 中，`@Data` 是一个**集合注解**，它整合了多个 Lombok 注解，用于快速生成实体类对象所需的常用方法。

一个 `@Data` 注解相当于同时使用了如下注解 ：

- `@Getter` 和 `@Setter`：为每个字段生成 `getter` 和 `setter` 方法；
- `@ToString`：生成 `toString()` 方法，打印对象的所有字段；
- `@EqualsAndHashCode`：生成 `equals()` 和 `hashCode()` 方法，基于字段值实现对象比较；
- `@RequiredArgsConstructor`：生成包含 `final` 和 `@NonNull` 字段的构造方法；

![Lombok @Data 注解](http://public.file.lvshuhuai.cn/images\167575545480437.jpeg)

#### 对比编译后的源码

先来看看下面这两段 Lombok 注解使用示例：

```less
@Getter
@Setter
@RequiredArgsConstructor
@ToString
@EqualsAndHashCode
public class User1 {
    private Long id;
    private String username;
    // 更多字段省略 ...
}
@Data
public class User2 {
    private Long id;
    private String username;
    // 更多字段省略 ...
}
```

编译代码，看看 Lombok 为这两个实体类生成的代码：

![img](http://public.file.lvshuhuai.cn/images\167575604936795.jpeg)

**User1.java** :

```kotlin
//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package com.quanxiaoha.coursefrontend.model;

public class User1 {
    private Long id;
    private String username;

    public Long getId() {
        return this.id;
    }

    public String getUsername() {
        return this.username;
    }

    public void setId(final Long id) {
        this.id = id;
    }

    public void setUsername(final String username) {
        this.username = username;
    }

    public User1() {
    }

    public String toString() {
        return "User1(id=" + this.getId() + ", username=" + this.getUsername() + ")";
    }

    public boolean equals(final Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof User1)) {
            return false;
        } else {
            User1 other = (User1)o;
            if (!other.canEqual(this)) {
                return false;
            } else {
                Object this$id = this.getId();
                Object other$id = other.getId();
                if (this$id == null) {
                    if (other$id != null) {
                        return false;
                    }
                } else if (!this$id.equals(other$id)) {
                    return false;
                }

                Object this$username = this.getUsername();
                Object other$username = other.getUsername();
                if (this$username == null) {
                    if (other$username != null) {
                        return false;
                    }
                } else if (!this$username.equals(other$username)) {
                    return false;
                }

                return true;
            }
        }
    }

    protected boolean canEqual(final Object other) {
        return other instanceof User1;
    }

    public int hashCode() {
        int PRIME = true;
        int result = 1;
        Object $id = this.getId();
        result = result * 59 + ($id == null ? 43 : $id.hashCode());
        Object $username = this.getUsername();
        result = result * 59 + ($username == null ? 43 : $username.hashCode());
        return result;
    }
}
```

**User2.java** :

```kotlin
//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package com.quanxiaoha.coursefrontend.model;

public class User2 {
    private Long id;
    private String username;

    public User2() {
    }

    public Long getId() {
        return this.id;
    }

    public String getUsername() {
        return this.username;
    }

    public void setId(final Long id) {
        this.id = id;
    }

    public void setUsername(final String username) {
        this.username = username;
    }

    public boolean equals(final Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof User2)) {
            return false;
        } else {
            User2 other = (User2)o;
            if (!other.canEqual(this)) {
                return false;
            } else {
                Object this$id = this.getId();
                Object other$id = other.getId();
                if (this$id == null) {
                    if (other$id != null) {
                        return false;
                    }
                } else if (!this$id.equals(other$id)) {
                    return false;
                }

                Object this$username = this.getUsername();
                Object other$username = other.getUsername();
                if (this$username == null) {
                    if (other$username != null) {
                        return false;
                    }
                } else if (!this$username.equals(other$username)) {
                    return false;
                }

                return true;
            }
        }
    }

    protected boolean canEqual(final Object other) {
        return other instanceof User2;
    }

    public int hashCode() {
        int PRIME = true;
        int result = 1;
        Object $id = this.getId();
        result = result * 59 + ($id == null ? 43 : $id.hashCode());
        Object $username = this.getUsername();
        result = result * 59 + ($username == null ? 43 : $username.hashCode());
        return result;
    }

    public String toString() {
        return "User2(id=" + this.getId() + ", username=" + this.getUsername() + ")";
    }
}
```

通过对比，会发现两个类生成的代码一致，包含：

- 生成了所有字段的 `get/set` 方法；
- 实体类的无参构造器；
- `toString()` 方法；
- `hashCode()` 方法；
- `equals()` 方法；

#### Lombok @Data 注解是何时工作的？

Lombok `@Data` 注解会在**代码的编译阶段**，为你静默生成相关样板代码。

#### staticConstructor 参数

先看一段示例代码：

```kotlin
@Data(staticConstructor = "create")
public class User2 {
    private Long id;
    private String username;
    // 更多字段省略 ...
}
```

如果你为 `@Data` 注解指定了 `staticConstructor` 参数，再次编译代码，看看实际生成的代码：

![Lombok staticConstructor](http://public.file.lvshuhuai.cn/images\167575815968795.jpeg)

由图可知，`@Data(staticConstructor = "create")` 生成了一个名为 `create()` 静态实体类生成方法，同时私有化了无参构造器。

#### Lombok @Data 排除指定字段

`@Data` 注解生成的模板方法中，默认会带上所有字段，如果针对某个字段不想生成 `get/set` 方法，或者是 `toString()` 、`equals()` 、`hashCode()` 方法排除某个字段的判断，示例代码如下：

```less
@Data
public class User3 {
	// 不生成此字段的 set 方法
    @Setter(value = AccessLevel.NONE)
    private Long id;
    
    // 不生成此字段的 get 方法
    @Getter(value = AccessLevel.NONE)
    private String username;
    
    // toString() 方法中不打印此字段
    @ToString.Exclude
    private String email;
    
    // 1. equals() 和 hashCode() 方法中排除此字段的判断
    // 2. toString() 方法中不打印此字段
    @EqualsAndHashCode.Exclude
    @ToString.Exclude
    private Integer sex;
}
```

#### 关于 Lombok 参数构造器

如果仅添加 @Data 注解，默认只会生成一个无参的构造器；当同时添加 `@Data` 和 `@Builder` 注解时，仅会生成一个全参构造器。在日常项目中，通常会在实体类上额外添加 `@AllArgsConstructor`、`@NoArgsConstructor` 注解, 示例代码如下：

```less
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class User4 {
    private Long id;
    private String username;

    // 更多字段省略 ...
}
```

这样，该实体类就基本拥有了常用的一些模板方法，包括 `builder` 构造器模式、无参构造器、全参构造器等。

#### 结语

本小节中，我们学习了 Lombok 的 @Data 注解，以及通过简单的代码示例，知道了如何在项目中使用它。总之，Lombok 是一个被广泛应用于生产环境的成熟工具，它可以帮助开发者生成实体类通用的一些样板代码，从而帮助我们节省大量的开发时间，还没有使用它的小伙伴们，可以赶快安排上了。

### Lombok @Builder 注解：流畅的构建者模式

Lombok 的 `@Builder` 注解用于生成建造者（Builder）模式的代码。Builder 模式提供了一种灵活、易读的方式来创建复杂对象，尤其适合需要设置多个可选参数、支持链式调用的场景。`@Builder` 注解自动生成了静态内部类 Builder 及其相关方法，使代码更加简洁、清晰。

#### 基本用法

使用 `@Builder` 注解，Lombok 会自动生成一个静态的内部 Builder 类，包含所有字段的 “链式” `setter` 方法，并生成一个 `build()` 方法用于创建对象实例。

#### 示例

```java
import lombok.Builder;

@Builder
public class User {
    private String name;
    private int age;
    private String email;
}
```

上面的代码将自动生成一个 `User` 类的 Builder，允许使用链式方法来设置字段，并通过 `build()` 方法完成对象的创建，比如像下面这样：

```java
User user = User.builder()
                .name("Alice")
                .age(25)
                .email("alice@example.com")
                .build();
```

生成的代码可以方便地指定所需字段，从而避免长参数列表的问题，代码也更具可读性。

#### `@Builder` 的常用参数

##### `builderMethodName`

通过设置 `builderMethodName`，可以自定义生成的静态 Builder 方法名称。默认情况下，此方法名为 `builder()`。

```java
@Builder(builderMethodName = "newUser")
public class User {
    private String name;
    private int age;
}
```

现在可以使用 `User.newUser()` 来获取一个 Builder 实例：

```java
User user = User.newUser().name("Bob").age(30).build();
```

##### `buildMethodName`

`buildMethodName` 用于自定义生成的构建方法的名称，默认为 `build()`。可根据需求自定义为其他名称。

```java
@Builder(buildMethodName = "create")
public class User {
    private String name;
    private int age;
}
```

生成的 Builder 实例可以调用 `create()` 方法来构建 `User` 对象：

```java
User user = User.builder().name("Charlie").age(40).create();
```

##### `toBuilder`

`toBuilder` 参数允许在已有对象的基础上创建一个新的 Builder。它会为生成的类添加 `toBuilder()` 方法，返回一个带有当前对象状态的 Builder，便于在已有对象的基础上做出小幅修改。

```java
import lombok.Builder;

@Builder(toBuilder = true)
public class User {
    private String name;
    private int age;
}
```

可以使用 `toBuilder()` 方法生成一个新的 Builder，并修改部分字段：

```java
User originalUser = User.builder().name("David").age(20).build();
User updatedUser = originalUser.toBuilder().age(25).build();
```

在上面的例子中，`updatedUser` 基于 `originalUser` 创建，但修改了 `age` 字段。

#### `@Builder` 和构造器的结合

`@Builder` 注解可以与 `@AllArgsConstructor`、`@NoArgsConstructor` 等 Lombok 注解结合使用，用于支持构造器的初始化。这对字段较多且需要构造方法和 Builder 的场景尤其适用。

```java
import lombok.Builder;
import lombok.AllArgsConstructor;

@Builder
@AllArgsConstructor
public class User {
    private String name;
    private int age;
}
```

通过这种方式，可以在类中同时拥有构造方法和 Builder。

#### 使用 `@Builder.Default` 指定默认值

`@Builder` 默认不会使用字段的初始值。如果希望 Builder 生成的对象包含默认值，可以使用 `@Builder.Default` 注解指定。

```java
import lombok.Builder;
import lombok.Builder.Default;

@Builder
public class User {
    private String name;
    @Default
    private int age = 18;
}
```

使用 `@Builder.Default` 后，未在 Builder 中设置 `age` 的情况下，`age` 将默认为 18。

```java
User user = User.builder().name("Eve").build(); // age 默认为 18
```

#### 小结

Lombok 的 `@Builder` 注解通过自动生成 Builder 模式的代码，使得对象创建过程更为清晰、灵活。主要特点包括：

- 生成链式 setter 方法和 `build()` 方法，支持流畅的对象创建方式。
- 提供 `builderMethodName`、`buildMethodName` 等参数，支持自定义。
- `toBuilder` 参数允许基于现有对象轻松创建新的 Builder。
- `@Builder.Default` 支持设置默认值。

通过使用 `@Builder` 注解，可以减少样板代码，提升代码的可读性和维护性。

### Lombok @Value 注解：创建不可变类

Lombok 的 `@Value` 注解用于**简化不可变对象的创建**。不可变对象（Immutable Object）在创建后，其内部状态无法改变，具备线程安全的特性，适合并发环境中共享数据的场景。`@Value` 注解相当于 `@Getter`、`@AllArgsConstructor`、`@ToString`、`@EqualsAndHashCode` 和 `final` 组合，因此非常适合用来定义数据传输对象（DTO）或作为业务逻辑中不可变的核心数据结构。

#### 基本用法

在类上添加 `@Value` 注解后，Lombok 会自动将所有字段设为 `final` 并生成只读的 `getter`，禁止字段的修改方法。`@Value` 类似于 `@Data`，但适用于不可变对象。

#### 示例

```java
import lombok.Value;

@Value
public class User {
    String name;
    int age;
}
```

上述代码自动生成以下内容：

- **`final` 修饰符**：所有字段都自动变为 `final`，只能在构造时赋值。
- **`getter` 方法**：为每个字段生成 `public` 的 `getter` 方法。
- **`toString()` 方法**：生成包含所有字段的 `toString()` 方法。
- **`equals()` 和 `hashCode()` 方法**：基于字段生成对象的 `equals()` 和 `hashCode()` 方法。
- **全参构造方法**：生成一个包含所有字段的构造方法，便于直接赋值。

创建 `User` 对象时可以指定字段的初始值：

```java
User user = new User("Alice", 25);
System.out.println(user.getName()); // 输出: Alice
System.out.println(user.getAge());  // 输出: 25
```

此 `User` 类生成的对象将是不可变的，因为它的所有字段都为 `final`，没有 `setter` 方法。

#### `@Value` 注解的默认特性

1. **不可变性**：所有字段自动设为 `final`，对象创建后其状态不可更改。
2. **私有构造方法**：除非显式定义，`@Value` 会默认生成一个私有的无参构造器。一般情况下不会用到，因为 `@Value` 的对象要求全部字段初始化。
3. **序列化支持**：`@Value` 类默认实现 `Serializable` 接口，非常适合在分布式环境中传输数据。

#### `@Value` 与 `@Data` 的区别

`@Value` 和 `@Data` 都能生成 `getter`、`toString()`、`equals()` 和 `hashCode()` 方法，但 `@Value` 注解的类具有不可变性，不会生成 `setter` 方法。`@Value` 适合不希望被修改的数据对象，而 `@Data` 更适合那些需要修改的普通 Java Bean。

#### `@Value` 与手动创建不可变对象的对比

在没有 Lombok 的情况下，手动创建不可变对象需要将字段设为 `final`，创建全参构造方法，并编写 `getter`、`toString()`、`equals()` 和 `hashCode()` 方法。相比之下，`@Value` 注解大大减少了代码量。

##### 手动实现不可变类示例

```java
public final class User {
    private final String name;
    private final int age;

    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public int getAge() {
        return age;
    }

    @Override
    public boolean equals(Object o) {
        // 实现 equals 逻辑
    }

    @Override
    public int hashCode() {
        // 实现 hashCode 逻辑
    }

    @Override
    public String toString() {
        return "User(name=" + name + ", age=" + age + ")";
    }
}
```

使用 `@Value` 可以简化以上所有操作。

#### `@Value` 与可变集合的组合

虽然 `@Value` 保证了对象的不可变性，但如果字段是集合类型（如 `List`、`Map` 等），则无法保证集合内容的不可变性。为实现完全不可变性，可以使用 `Collections.unmodifiableList()` 等方法将集合转换为不可变的视图。

##### 示例

```java
import lombok.Value;
import java.util.List;
import java.util.Collections;

@Value
public class User {
    String name;
    List<String> hobbies;

    public User(String name, List<String> hobbies) {
        this.name = name;
        this.hobbies = Collections.unmodifiableList(hobbies);
    }
}
```

这段代码确保了 `hobbies` 字段的内容在对象创建后也不可修改。

#### 小结

Lombok 的 `@Value` 注解是创建不可变对象的快捷方式，具备以下优点：

- 自动将字段设为 `final`，生成只读的 `getter`，确保对象不可变。
- 生成 `toString()`、`equals()` 和 `hashCode()` 方法，使对象支持打印和比较。
- 提供全参构造方法，便于快速创建对象。
- 简化了不可变对象的实现，适合数据传输对象（DTO）和并发环境中共享的数据结构。

在多线程和分布式环境中，通过 `@Value` 创建不可变对象，能提升数据安全性和一致性。

### Lombok @Log 系列注解: 简化日志记录

Lombok 提供了一系列 `@Log` 注解，**用于自动生成日志记录器实例，简化 Java 类中日志的定义和使用**。这些注解支持常见的日志框架，比如 `java.util.logging`、`Log4j`、`Log4j2`、`Slf4j` 等。通过 `@Log` 注解，开发者不再需要手动定义 Logger 实例，代码更简洁，同时符合实际需求的日志框架。

#### 可用的 `@Log` 注解

Lombok 支持多个日志框架，每个框架对应一个专门的注解：

- `@Log`：使用 `java.util.logging`（JUL）；
- `@CommonsLog`：使用 Apache Commons Logging；
- `@Log4j`：使用 Log4j；
- `@Log4j2`：使用 Log4j2；
- `@Slf4j`：使用 SLF4J；
- `@XSlf4j`：使用 SLF4J 的扩展（XSLF4J）；
- `@JBossLog`：使用 JBoss Logging；

每个注解都会自动在类中生成一个静态的日志记录器实例，变量名称根据框架的不同，通常是 `log`。

#### 基本用法示例

以下示例展示了使用不同日志注解的代码示例和日志输出方式：

##### 使用 `@Slf4j` 示例

`@Slf4j` 是使用最广泛的注解之一，它基于 SLF4J 日志框架。通过 `@Slf4j` 注解，Lombok 会自动生成一个 `log` 变量。

```java
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ExampleService {

    public void performTask() {
        log.info("信息级别日志.");
        log.warn("警告级别日志.");
        log.error("错误级别日志.");
    }
}
```

在上面的代码中，`log` 对象是由 Lombok 自动生成的 `Logger` 实例，开发者可以直接调用 `info`、`warn`、`error` 等方法输出日志。

##### 使用 `@Log4j2` 示例

如果项目使用 Log4j2 作为日志框架，可以使用 `@Log4j2` 注解。Lombok 会自动生成一个 Log4j2 的 `Logger` 实例：

```java
import lombok.extern.log4j.Log4j2;

@Log4j2
public class ExampleService {

    public void performTask() {
        log.info("Performing task with Log4j2.");
        log.debug("Debugging information.");
    }
}
```

`log` 变量是自动生成的 Log4j2 `Logger` 实例，可以使用所有的 Log4j2 日志级别方法。

##### 使用 `@Log` 示例

`@Log` 注解使用 Java 内置的 `java.util.logging` (JUL) 日志框架，对于不需要第三方日志库的轻量级应用非常适合。

```java
import lombok.extern.java.Log;

@Log
public class ExampleService {

    public void performTask() {
        log.info("Using java.util.logging for task.");
        log.warning("This is a warning message.");
    }
}
```

在这里，`log` 变量是 `java.util.logging.Logger` 实例，可以直接调用 JUL 的日志方法。

#### `@Log` 注解生成的日志对象

每个日志注解生成的 `Logger` 变量都具备以下特性：

- **静态和只读**：日志记录器实例是 `static final` 类型，确保整个类只会生成一个日志记录器实例。
- **命名为 `log`**：生成的变量名称统一为 `log`，便于开发者识别和调用。
- **支持日志级别**：根据日志框架的不同，`log` 变量支持相应的日志级别方法（如 `info`、`warn`、`error` 等）。

#### 小结

Lombok 的 `@Log` 注解系列为 Java 类的日志记录提供了便捷的方式，无需手动定义日志记录器对象。根据不同的日志框架，选择相应的 `@Log` 注解：

- `@Slf4j` 和 `@Log4j2` 是使用最广泛的注解，适合现代 Java 项目。
- `@Log` 适合需要轻量级日志记录的项目，直接使用 `java.util.logging`。

这些注解帮助开发者减少样板代码，提升日志管理的可维护性。

### Lombok @SneakyThrows 注解：简化异常操作

![Lombok @SneakyThrows 注解](http://public.file.lvshuhuai.cn/images\173086350546415.jpeg)

本小节中，我们来学习 Lombok 库中的 `@SneakyThrows` 注解。

#### 什么是 @SneakyThrows ？

> `@SneakyThrows` 用来 “偷偷地” 抛出检查型异常（checked exception），而无需显式地在方法签名中声明 `throws` 或者使用 `try-catch`。对于需要捕获或声明的异常，`@SneakyThrows` 注解可以让方法绕过这一步。

#### 示例代码

为了方便你理解它的作用，先来看一段示例代码：

```typescript
import java.io.UnsupportedEncodingException;

/**
 * @author: 
 * @date: 2024/11/5 23:09
 * @version: v1.0.0
 * @description: TODO
 **/
public class SneakyThrowsExample {

    /**
     * 字节转字符串，且指定了字符编码为 UTF-8
     * @param bytes
     * @return
     */
    public static String utf8ToString(byte[] bytes) {
        try {
            return new String(bytes, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        return null;
    }

    public static void main(String[] args) {
        System.out.println(utf8ToString("教程".getBytes()));
    }
}
```

`new String(bytes, "UTF-8")` 需要显示的进行 `try-catch` 异常捕获，或者如下所示，通过 `throws` 将异常抛出去，让调用者去处理：

```java
    /**
     * 字节转字符串，且指定了字符编码为 UTF-8
     * @param bytes
     * @return
     */
    public static String utf8ToString(byte[] bytes) throws UnsupportedEncodingException {
        return new String(bytes, "UTF-8");
    }
```

有了 Lombok 的 `@SneakyThrows` 注解后，代码就可以精简成下面这样：

```typescript
import lombok.SneakyThrows;

/**
 * @author: 
 * @date: 2024/11/5 23:09
 * @version: v1.0.0
 * @description: TODO
 **/
public class SneakyThrowsExample {

    /**
     * 字节转字符串，且指定了字符编码为 UTF-8
     * @param bytes
     * @return
     */
    @SneakyThrows
    public static String utf8ToString(byte[] bytes) {
        return new String(bytes, "UTF-8");
    }

    public static void main(String[] args) {
        System.out.println(utf8ToString("教程".getBytes()));
    }
}
```

在上面的代码中，方法中没有主动 `try-catch` 异常，也没有在方法签名中声明 `throws` ，而是在方法上添加了`@SneakyThrows` 注解，**此注解会在编译期自动将抛出异常的工作做好，从而让开发者在代码中避免显式的 `try-catch` 块或 `throws` 声明。**

为了验证这一点，可以看看 `/target/classes` 文件夹中编译后的代码，如下：

![查看 @SneakyThrows 编译后的代码](http://public.file.lvshuhuai.cn/images\173086232832090.jpeg)

#### 优缺点

- **优点**：

  - 减少了方法签名中的异常声明，保持代码简洁。

  - 避免了过多的样板代码（如 `try-catch` 块）。

  - 在某些情况下，提升了代码的可读性，尤其是对于 Lambda 表达式，示例代码如下:

    ```kotlin
    List<String> list = Arrays.asList("file1.txt", "file2.txt");
    list.forEach(@SneakyThrows file -> {
        Files.readAllLines(Paths.get(file));
    });
    ```

- **缺点**：

  - **可读性与维护性**：尽管简洁，`@SneakyThrows` 可能会降低代码的可读性，特别是对于团队开发来说，后续维护人员需要了解注解的行为及其影响。
  - **隐式异常抛出**：`@SneakyThrows` 隐藏了异常抛出的细节，可能导致程序在运行时抛出未经预料的异常，增加了调试的复杂性。
  - **错误处理**：这种 “偷懒” 的方式可能导致开发者忽视良好的错误处理实践。如果一个方法默默抛出异常，调用者在使用时无法有效地处理异常。

#### 何时应慎用？

在生产环境中，`@SneakyThrows` 应该谨慎使用。虽然它减少了样板代码，但也容易掩盖程序的潜在问题。对于关键系统，显式声明异常可以帮助程序员更好地理解代码的边界和行为。

例如，在设计公共 API 时，使用 `@SneakyThrows` 可能会使接口使用者难以预料方法可能抛出的异常类型。最好在这种情况下显式声明异常，确保代码的透明度和文档性。

#### 结语

`@SneakyThrows` 是一个便利但有争议的工具，它可以显著减少代码量，提高开发效率，但也容易导致代码不够直观。在日常开发中，建议在清楚其行为及影响的前提下使用它。适度使用 `@SneakyThrows`，在适当的场景下，它是提升代码简洁度的好帮手；但在需要严格控制异常处理的地方，显式声明和处理异常仍然是更好的选择。

## 深入理解 Lombok

### Lombok 实现原理是什么？

前面注解 一章中，我们已经熟悉了 Lombok 相关注解，以及使用方法。你可能会好奇， Lombok 的实现原理是什么？Lombok 是如何魔力般地简化我们的 Java 代码的呢？本小节中，我们就来说说其实现原理。

#### 核心实现原理

Lombok 的核心是利用 **Java 注解处理器** 和 **AST（抽象语法树）修改** 技术，在**编译阶段动态插入代码**。

##### 1. 注解处理器

Java 的 `javax.annotation.processing` 包提供了注解处理器的支持。Lombok 使用该机制，通过实现 `AnnotationProcessor` 接口来处理注解。

Lombok 编译时注解处理的流程如下：

1. **注解扫描**：Java 编译器在编译过程中扫描所有类上的注解，如果找到 Lombok 的注解（如 `@Getter`、`@Setter` 等），会将这些注解交给 Lombok 处理。
2. **注解处理**：Lombok 自定义的注解处理器会在处理阶段解析这些注解，识别哪些注解需要生成代码。
3. **修改 AST**：Lombok 的注解处理器会读取编译器生成的 AST 树，针对特定注解修改或新增相应的代码节点，例如，针对 `@Getter` 注解，Lombok 会在类的 AST 中插入 `get` 方法。
4. **字节码生成**：经过修改的 AST 树会继续传递给 Java 编译器，编译器会根据更新后的 AST 生成新的字节码文件。

##### 2. AST 操作

AST 是源代码结构的树状表达形式。Lombok 使用 Java 编译器中不同阶段的 AST 解析结果来完成代码的插入操作。具体来说，Lombok 通过对 Java 编译器的扩展，直接操作 AST 来实现以下功能：

- **方法添加**：Lombok 通过注解生成 `getter`、`setter` 等方法，将方法节点插入到 AST 树中。
- **构造器生成**：针对 `@AllArgsConstructor` 或 `@NoArgsConstructor` 等注解，Lombok 会自动在 AST 树中创建构造器节点。
- **字段操作**：对于不可变对象的 `@Value` 注解，Lombok 会将字段设置为 `final`。

##### 3. 编译器适配

Lombok 需要对不同的 Java 编译器进行适配，如 Eclipse 的 ECJ 编译器和 javac 编译器。Lombok 提供了适配层，分别处理 Eclipse 和 IDEA 编译环境下的代码生成。Lombok 实现了对这两个编译器的底层 AST 操作，因此无论是在 Eclipse 还是 IDEA 中都能使用 Lombok 功能。

在不同 IDE 下的适配机制如下：

- **Eclipse**：Eclipse 使用 ECJ（Eclipse Compiler for Java）编译器，Lombok 通过操作 Eclipse 的内部编译 API 来修改 AST。
- **IntelliJ IDEA**：IDEA 使用 javac 编译器，Lombok 通过 JavacTreeMaker 操作 javac 的 AST 树节点。

##### 4. 编译期间字节码插桩

Lombok 通过编译器插件机制和字节码插桩实现代码的生成。它不需要依赖类加载器，也不会在运行时修改字节码，因此没有额外的性能开销。Lombok 修改的是 **编译期间的字节码**，因此生成的 `.class` 文件中已包含所有注解生成的代码，不需要在运行时引入 Lombok 依赖。

#### 优缺点

##### 优点

- **减少样板代码**：Lombok 大幅减少了 Java 中大量的样板代码，如 `getter`/`setter`、构造器、`toString`、`equals` 等。
- **提高开发效率**：通过注解简化代码书写，提升了开发效率和代码可读性。
- **编译期优化**：Lombok 的代码生成在编译期完成，不会影响运行时性能。

##### 缺点

- **编译器适配**：Lombok 依赖于对编译器的深度集成和 AST 操作，不同的 IDE 和编译环境可能需要特殊配置和适配。
- **代码可见性差**：Lombok 自动生成代码在 IDE 中不可见，可能会影响代码调试和理解，尤其是对新手而言。
- **依赖限制**：Lombok 是第三方库，尽管已经很成熟，但在某些特定环境下可能会与其他编译器插件或框架发生冲突。

#### 小结

Lombok 通过注解处理器和 AST 修改技术在编译期动态生成代码，帮助开发者减少样板代码的书写，提高开发效率。它在编译期间完成所有代码生成，并不会影响程序运行时的性能。然而，Lombok 的使用也存在一些不足，特别是代码可见性和编译器适配问题。

## 注意事项

### 如何避免 Lombok 的常见陷阱？

尽管 Lombok 是一个强大的工具，可以帮助我们简化代码，提高开发效率，但是如果不恰当地使用，也可能会引入一些问题。本文将为你详述如何避免 Lombok 的常见陷阱。

#### 1. 慎用 @Data

`@Data` 是一个实用的注解，它包含了 `@Getter`、`@Setter`、`@ToString`、`@EqualsAndHashCode` 和 `@RequiredArgsConstructor`。这在一般情况下非常方便，但是当你需要自定义一些方法时，就可能会遇到问题。

例如，你可能需要自定义 `equals` 和 `hashCode` 方法，但是由于 `@Data` 注解自动生成了这些方法，所以你的自定义方法会被覆盖。为了避免这种情况，你可以使用 `@EqualsAndHashCode` 的 `callSuper` 属性。

```java
@EqualsAndHashCode(callSuper = true)
public class MyEntity extends BaseEntity {
    //...
}
```

这样做可以确保父类的 `equals` 和 `hashCode` 方法也被调用。

此外，`@Data` 注解也会生成所有字段的 getter 和 setter 方法，如果你的字段中包含了一些不应该被外部访问或修改的数据，这可能会导致问题。在这种情况下，你可以使用 `@Getter(AccessLevel.NONE)` 和 `@Setter(AccessLevel.NONE)` 来禁止生成特定字段的 getter 和 setter 方法。

```kotlin
@Data
public class MyEntity {
    @Getter(AccessLevel.NONE)
    private String sensitiveData;
    //...
}
```

#### 2. 注意 `@ToString` 的循环引用问题

`@ToString` 注解非常实用，但是在处理含有循环引用的数据结构时，必须要小心。例如，你有一个双向链表或者一个树形结构，其中的元素互相引用。这样的话，当你调用 `toString` 方法时，就可能会出现无限循环的情况，最后导致栈溢出。为了避免这种情况，你可以使用 `@ToString.Exclude` 注解来排除掉会导致循环引用的字段。

```kotlin
public class TreeNode {
    private TreeNode parent;
    private TreeNode child;

    @ToString.Exclude
    public TreeNode getParent() {
        return parent;
    }

    //...
}
```

#### 3. `@EqualsAndHashCode` 与懒加载

当你使用 JPA 或 Hibernate 这样的 ORM 框架时，你可能会使用到懒加载（Lazy Loading）特性。这意味着，某些字段在第一次被访问时才会被加载。而如果你在这样的字段上使用了 `@EqualsAndHashCode` 注解，可能会在你并不希望加载这些字段的情况下触发它们的加载。

为了避免这种情况，你可以使用 `@EqualsAndHashCode(onlyExplicitlyIncluded = true)`，然后在你想要包含在 `equals` 和 `hashCode` 方法中的字段上使用 `@EqualsAndHashCode.Include`。

```kotlin
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class MyEntity {
    @EqualsAndHashCode.Include
    private Long id;

    @OneToMany
    private List<MyOtherEntity> otherEntities;

    //...
}
```

在这个例子中，`otherEntities` 字段不会被包含在 `equals` 和 `hashCode` 方法中，所以在计算这些方法时，不会触发它的加载。

#### 4. 小心 `@SneakyThrows`

`@SneakyThrows` 是一个非常有用的注解，它可以让你 "偷偷" 抛出受检异常，而无需在方法签名中声明它们。但是这也可能会引起一些问题。

首先，你的代码的调用者可能并不知道你的方法可能会抛出哪些受检异常，这可能会导致他们在处理异常时疏忽。为了解决这个问题，你应该在你的方法的文档注释中明确说明可能会抛出哪些异常。

其次，`@SneakyThrows` 会将受检异常包装在 `RuntimeException` 中抛出，如果你的代码的调用者捕获了 `RuntimeException`，并且没有检查它的原因，那么他们可能会错过受检异常。为了解决这个问题，你应该尽量避免在你的方法中直接抛出 `RuntimeException`，而是应该抛出具体的异常类型。

#### 5. 不要滥用 Lombok

虽然 Lombok 的注解可以极大地简化我们的代码，但是这并不意味着我们应该在所有地方都使用它。在一些情况下，手动编写代码可能会更好。

例如，你可能需要自定义某个字段的 getter 或 setter 方法，或者你需要自定义 `equals`、`hashCode` 或 `toString` 方法。在这些情况下，使用 Lombok 的注解可能会导致你的自定义代码被覆盖。

此外，过度使用 Lombok 的注解也可能会使你的代码变得难以理解。你的同事或未来的你可能会对一些自动生成的方法感到困惑，例如，他们可能会不清楚某个方法是从哪里来的，或者为什么某个方法的行为和预期不一致。

因此，虽然 Lombok 是一个强大的工具，但是我们也需要明智地使用它。我们应该始终保持警惕，确保我们的代码不仅简洁，而且易于理解和维护。

#### 总结

**总的来说，Lombok 是一个非常有用的工具，在企业级开发中，它可以极大地提高我们的开发效率，除非有自定义的情况，需要谨慎处理外，它是利大于弊的存在。**