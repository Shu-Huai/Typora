# 为什么 Java 的 ConcurrentHashMap 不支持 key 或 value 为 null？

## 回答重点

核心原因是**消除歧义**。`ConcurrentHashMap` 是为并发环境设计的，如果允许 `value` 为 null，调用 `get`(`key`) 返回 null 时，你没法判断是 `key` 不存在还是 `value` 本身就是 null。

单线程下这个问题可以用 containsKey 来区分，但在并发环境下，这两步操作之间可能有其他线程在修改 `map`，导致判断失效。Doug Lea 设计时直接禁止 null，从根源上避免了这种歧义。

并发场景下的歧义问题：

- 线程 A 调用 `get`(`key`) 返回 null

- 线程 A 调用 containsKey(`key`) 想确认 `key` 是否存在

- 在这两步之间，线程 B 可能执行了 `put`(`key`, `value`) 或 `remove`(`key`)

- 导致线程 A 的判断结果不可靠

![](Z:/Public/images/eG8W4Nen_lIbsHKGAWy_mianshiya.webp)

另一个原因是**简化实现**。如果允许 null，`put`、`get`、containsKey 这些方法都得加额外逻辑去处理空值情况，代码复杂度上升，出 bug 的概率也会增加。

## 扩展知识

### 其他并发集合的做法

Java 里的并发集合基本都遵循这个设计：ConcurrentSkipListMap、`ConcurrentLinkedQueue` 都不允许 null。设计一致性让开发者不用记忆“哪个集合允许 null 哪个不允许”，减少心智负担。

对比一下各种 Map 对 null 的支持：

| Map 类型 | `key` 允许 `null` | `value` 允许 `null` |
| --- | --- | --- |
| `HashMap` | 允许 | 允许 |
| `Hashtable` | 不允许 | 不允许 |
| `ConcurrentHashMap` | 不允许 | 不允许 |
| `TreeMap` | 不允许 | 允许 |
| `LinkedHashMap` | 允许 | 允许 |

`HashMap` 允许 null 是因为它设计给单线程场景用，没有并发歧义问题。`Hashtable` 虽然是线程安全的，但它诞生于 JDK 1.0，当时设计就不允许 null，`ConcurrentHashMap` 沿用了这个约定。

![](Z:/Public/images/ZtbOTXDn_eM1CNVAZgW_mianshiya.webp)

### 源码验证（基于 JDK 1.8）

`ConcurrentHashMap` 的 `put` 方法开头就做了空值校验，尝试插入 null 直接抛 NullPointerException：

```java
public V put(K key, V value) {
    if (key == null || value == null) throw new NullPointerException();
    return putVal(key, value, false);
}
```

`get` 方法的实现：

```java
public V get(Object key) {
    Node<K,V>[] tab; Node<K,V> e, p; int n, eh; K ek;
    int h = spread(key.hashCode());
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (e = tabAt(tab, (n - 1) & h)) != null) {
        if ((eh = e.hash) == h) {
            if ((ek = e.key) == key || (ek != null && key.equals(ek)))
                return e.val;
        }
        else if (eh < 0)
            return (p = e.find(h, key)) != null ? p.val : null;
        while ((e = e.next) != null) {
            if (e.hash == h &&
                ((ek = e.key) == key || (ek != null && key.equals(ek))))
                return e.val;
        }
    }
    return null;
}
```

`get` 方法内部不需要判断 `value` 是否为 null，因为 `value` 压根不可能是 null。返回 null 就代表 `key` 不存在，语义非常清晰。

### Doug Lea 的解释

`ConcurrentHashMap` 的作者 Doug Lea 在邮件列表里解释过这个设计决策：主要考虑的是并发场景下 null 会带来歧义，而消除歧义带来的收益远大于支持 null 的便利性。如果业务上确实需要表达“值不存在”的语义，应该用 `Optional` 或者特殊的占位对象来代替 null。

## 面试官追问

#### 提问：如果业务上必须存 null 值怎么办？

回答：可以用一个特殊的占位对象来代替 null，比如定义一个 `private static final Object NULL_VALUE = new Object()`，存的时候存这个对象，取的时候判断是不是它再转成 null 返回。或者直接用 `Optional` 包装一层，`Optional.empty()` 表示空值。

#### 提问：`HashMap` 为什么可以存 null？

回答：`HashMap` 设计给单线程场景用，`get` 返回 null 后可以紧接着调 containsKey 来区分，这两步操作之间不会有其他线程插一脚，所以不存在歧义问题。另外 `HashMap` 对 null `key` 做了特殊处理，hash 值固定为 0，放在数组第一个槽位。

#### 提问：`Hashtable` 也不支持 null，是因为并发问题吗？

回答：`Hashtable` 是 JDK 1.0 就有的老古董，当时的设计就是不允许 null，没有留下文档说明具体原因。不过它确实是线程安全的，Doug Lea 设计 `ConcurrentHashMap` 时沿用了这个约定，并给出了明确的理由。从实践角度看，禁止 null 确实让 API 语义更清晰。
