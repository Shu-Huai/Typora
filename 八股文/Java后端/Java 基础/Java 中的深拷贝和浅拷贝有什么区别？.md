# Java 中的深拷贝和浅拷贝有什么区别？

## 回答重点

**浅拷贝**只复制对象本身，引用类型字段仍指向原来的对象，因此新旧对象共享内部引用，修改一方可能影响另一方。

**深拷贝**会递归复制对象及其内部引用对象，新旧对象完全独立，互不影响。

例如 `Teacher` 对象包含一个 `Student` 列表：浅拷贝后两个 Teacher 共用同一份列表；深拷贝后各自拥有独立列表。

![深拷贝与浅拷贝](Z:/Public/images/LlvKvoA9_IhqchQOrum_mianshiya.webp)

![对象引用关系](Z:/Public/images/image-20210303201307397_mianshiya.webp)

## 扩展知识

### 浅拷贝的实现

最常见的是 `Object.clone()`。默认 clone 是浅拷贝：基本类型复制值，引用类型只复制引用地址。

```java
class Person implements Cloneable {
    String name;
    int age;
    Address address;

    @Override
    public Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}
```

也可以使用拷贝构造方法或工厂方法：

```java
public Person(Person other) {
    this.name = other.name;
    this.age = other.age;
    this.address = other.address; // 仍是浅拷贝
}
```

### 深拷贝的实现

#### 手动递归克隆

性能最好，但代码量较大，对象结构变化时需要同步修改：

```java
@Override
public Object clone() throws CloneNotSupportedException {
    Person cloned = (Person) super.clone();
    cloned.address = (Address) address.clone();
    return cloned;
}
```

#### 序列化与反序列化

实现简单，但对象图中的类型都需要实现 `Serializable`，并且大对象或深层嵌套时性能较差：

```java
public static <T extends Serializable> T deepCopy(T object) {
    try {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bos);
        oos.writeObject(object);
        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        ObjectInputStream ois = new ObjectInputStream(bis);
        return (T) ois.readObject();
    } catch (Exception e) {
        throw new RuntimeException(e);
    }
}
```

#### JSON 序列化

可以使用 Jackson 或 Gson 将对象转成 JSON 再解析回来，不要求实现 `Serializable`，但存在序列化和反序列化开销：

```java
ObjectMapper mapper = new ObjectMapper();
Person copy = mapper.readValue(
        mapper.writeValueAsString(original), Person.class);
```

![深拷贝实现方式](Z:/Public/images/5VC1CLeK_PYQgo6UHw7_mianshiya.webp)

### Cloneable 接口的缺陷

`Cloneable` 是标记接口，本身没有方法；`clone()` 定义在 `Object` 中且是 `protected`。使用 clone 需要：

1. 实现 `Cloneable`，否则会抛出 `CloneNotSupportedException`。
2. 重写 `clone()` 并扩大访问权限，通常改为 `public`。

由于契约松散、容易漏拷贝内部引用，现在更推荐拷贝构造方法或静态工厂方法。

### 不可变对象不需要深拷贝

`String`、`Integer` 等不可变对象创建后状态不会改变，共享引用是安全的：

```java
String s1 = "hello";
String s2 = s1;
```

将对象内部状态设计为不可变，可以减少深拷贝需求。

### 常见问题

1. **循环引用**：A 引用 B、B 又引用 A，递归拷贝可能无限循环，应使用 Map 记录已经拷贝过的对象。
2. **`transient` 字段**：序列化深拷贝不会复制 transient 字段，拷贝后会恢复默认值。
3. **单例对象**：深拷贝单例引用可能破坏单例约束，需要特殊处理。

## 面试官追问

### 提问：数组的 `clone()` 是深拷贝还是浅拷贝？

是浅拷贝。基本类型数组看起来独立，是因为元素本身按值复制；对象数组只复制对象引用，数组中的对象仍然共享。例如 `int[]` 克隆后元素独立，而 `Person[]` 中的 Person 实例仍是同一批。

### 提问：`BeanUtils.copyProperties` 是深拷贝还是浅拷贝？

是浅拷贝。Spring 和 Apache Commons 的 BeanUtils 只复制属性值，引用类型字段复制的是引用地址，不会递归复制对象。

### 提问：为什么《Effective Java》不推荐使用 clone？

`Cloneable` 只是标记接口，clone 方法却在 Object 中；clone 契约松散，没有强制返回类型，也没有要求必须调用 `super.clone()`，还可能与 final 字段初始化产生冲突。拷贝构造方法和静态工厂更清晰可控。

### 提问：如何高效实现深拷贝？

结构简单且固定时手写递归拷贝性能最好；结构复杂或经常变化时可用 Jackson 等 JSON 方案；性能极敏感的场景可考虑 Kryo、Protobuf 等二进制序列化框架。
