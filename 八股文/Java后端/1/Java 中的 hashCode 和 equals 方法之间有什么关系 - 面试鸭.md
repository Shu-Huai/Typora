# Java 中的 hashCode 和 equals 方法之间有什么关系？ - 面试鸭 | 2026最新面试题+详细答案解析

## 回答重点

一句话总结：**equals 相等的对象，hashCode 必须相等；hashCode 相等的对象，equals 不一定相等**。

这条规则在使用 HashMap、HashSet 这类基于哈希的集合时特别重要。这些集合判断两个对象是否相同，先比 hashCode，hashCode 不等直接认为是两个不同对象，根本不会调 equals。所以如果只重写 equals 不重写 hashCode，集合就废了。

举个例子，有个 User 类只重写了 equals，认为 id 相同就是同一个用户：

```java
public class User {
    private Long id;
    private String name;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return Objects.equals(id, user.id);
    }
    // 没重写 hashCode
}
```

把两个 id 相同的 User 塞进 HashSet：

```java
Set<User> set = new HashSet<>();
set.add(new User(1L, "张三"));
set.add(new User(1L, "李四"));
System.out.println(set.size()); // 输出 2，期望是 1
```

因为两个 User 对象的 hashCode 不同，HashSet 认为它们是不同元素，都存进去了。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/OIgyNKE8_5vnqL2EM6m_mianshiya.webp)

## 扩展知识

### 为什么 HashMap 要先判断 hashCode

HashMap 底层是数组加链表，存元素时先用 hashCode 算出数组下标，再在这个位置的链表里找有没有相同的 key。如果每次都遍历整个链表调 equals，性能会很差。hashCode 就是个快速过滤器，先用 int 值比一下，不相等直接跳过，省了大量 equals 调用。

看 HashMap 的 putVal 源码，判断条件是 `hash == hash && (key == key || key.equals(key))`，hash 不等直接短路，equals 都不用调。

![image-20220123131544363.png](https://pic.code-nav.cn/mianshiya/question_picture/1783397053004488705/image-20220123131544363_mianshiya.webp)

### Object 默认实现

hashCode 是 Object 的 native 方法，默认返回对象的内存地址转成的整数：

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/ag0G48da_image_mianshiya.webp)

equals 默认实现就是 `==`，比较的是引用地址：

![](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/epOMLaLx_image_mianshiya.webp)

两个 new 出来的对象，地址肯定不同，所以默认情况下它们的 hashCode 不同、equals 也返回 false。这就是为什么自定义类要重写这两个方法。

### 重写 equals 的五条规则

1）自反性：x.equals(x) 必须返回 true
2）对称性：x.equals(y) 返回 true，那 y.equals(x) 也必须返回 true
3）传递性：x.equals(y) 返回 true，y.equals(z) 返回 true，那 x.equals(z) 必须返回 true
4）一致性：对象没变的情况下，多次调用 equals 结果要一致
5）非空性：x.equals(null) 必须返回 false

违反对称性的经典坑是继承关系，子类重写 equals 时如果没处理好，可能出现 parent.equals(child) 和 child.equals(parent) 结果不一致的情况。

### 怎么正确重写 hashCode

最简单的方式是用 Objects.hash() 方法，把参与 equals 判断的字段都传进去：

```java
@Override
public int hashCode() {
    return Objects.hash(id, name);
}
```

如果追求性能，可以手写，基本套路是选一个质数作为乘数，通常是 31：

```java
@Override
public int hashCode() {
    int result = 17;
    result = 31 * result + (id != null ? id.hashCode() : 0);
    result = 31 * result + (name != null ? name.hashCode() : 0);
    return result;
}
```

为什么用 31？因为 31 是奇素数，而且 `31 * i` 可以被 JVM 优化成 `(i << 5) - i`，位运算比乘法快。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/xklfvjdR_d55Q5Wce5H_mianshiya.webp)

### IDE 和 Lombok 自动生成

手写容易出错，推荐用 IDE 自动生成或者 Lombok 的 @EqualsAndHashCode 注解。IntelliJ IDEA 里按 Alt+Insert 选 equals() and hashCode() 就能生成。

Lombok 更省事，一个注解搞定：

```java
@EqualsAndHashCode
public class User {
    private Long id;
    private String name;
}
```

注意 Lombok 默认会用所有字段，如果只想用部分字段，可以加 @EqualsAndHashCode.Include 或 @EqualsAndHashCode.Exclude 来控制。

## 面试官追问

#### 提问：两个对象 hashCode 相同但 equals 不相等，这种情况叫什么？会影响 HashMap 性能吗？

回答：这叫哈希冲突。HashMap 里 hashCode 相同的元素会落到同一个数组槽位，JDK 7 用链表串起来，JDK 8 在链表长度超过 8 时会转成红黑树。冲突越多，链表越长，查找就从 O(1) 退化成 O(n)，转成红黑树后能稳定在 O(log n)。极端情况下如果所有 key 的 hashCode 都一样，整个 HashMap 就变成一棵树，性能直线下降。

#### 提问：String 类的 hashCode 是怎么算的？为什么这么设计？

回答：String 的 hashCode 算法是遍历每个字符，`h = 31 * h + c`。第一次调用后会缓存到 hash 字段，后面再调直接返回缓存值，因为 String 是不可变的。用 31 这个乘数是因为它是奇素数，冲突概率相对较低，而且可以被 JVM 优化成位移运算。JDK 1.2 之前用的是别的算法，冲突率更高，后来改成现在这个版本。

#### 提问：HashMap 的 key 用可变对象有什么风险？

回答：如果 key 是可变对象，存进去之后又改了参与 hashCode 计算的字段，那这个 entry 就再也找不到了。因为修改后 hashCode 变了，HashMap 会到新的槽位去找，但数据还在老槽位，get 返回 null，remove 也删不掉，造成内存泄漏。所以 HashMap 的 key 最好用不可变对象，String、Integer 这些都可以，自定义类当 key 要特别小心。

#### 提问：重写 equals 不重写 hashCode，除了集合出问题，还有什么影响？

回答：如果不用 HashMap、HashSet 这些集合，单纯比较两个对象是否相等，不重写 hashCode 倒也没问题。但保不齐哪天代码里突然要把对象放进集合，或者作为缓存的 key，到时候就踩坑了。还有就是一些框架可能依赖 hashCode，比如 Hibernate 的实体对象做集合操作时会用到。所以最佳实践是只要重写 equals 就顺手重写 hashCode，省得埋雷。
...
