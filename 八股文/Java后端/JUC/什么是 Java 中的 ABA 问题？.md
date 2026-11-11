# 什么是 Java 中的 ABA 问题？

## 回答重点

**ABA 问题**是 CAS 操作的一个经典坑：线程读到变量值是 A，准备用 CAS 更新的时候，发现值还是 A，就以为没人动过。但实际上可能被别的线程改成 B 又改回 A 了，中间状态完全丢失。

因为 CAS 的本质是“比较并交换”，它只看当前值和预期值是否相等，相等就更新，不相等就失败重试。它只比较“值”相不相等，不关心中间发生了什么。

拿银行账户打比方：余额 100 元，线程 A 要扣 50。读到余额 100，准备 CAS 更新成 50。这时线程 B 先扣了 50 变成 50，线程 C 又存了 50 变回 100。线程 A 执行 CAS，发现余额还是 100，更新成功。表面上没问题，但如果业务逻辑依赖“这 100 块钱是原来那 100 块”，就出事了。

![](Z:/Public/images/uMEfhJ91_TSOnABT6j6_mianshiya.webp)

## 扩展知识

### ABA 问题的示例

举个无锁栈的例子：

```java
public class LockFreeStack<T> {
    private AtomicReference<Node<T>> head = new AtomicReference<>();

    public T pop() {
        Node<T> oldHead;
        Node<T> newHead;
        do {
            oldHead = head.get();
            if (oldHead == null) return null;
            newHead = oldHead.next;
        } while (!head.compareAndSet(oldHead, newHead));
        return oldHead.value;
    }
}
```

线程 A 读到栈顶是节点 X，准备把 head 指向 X.next。这时线程 B 连续 pop 了 X 和 Y，又 push 回一个新节点，恰好复用了 X 的内存地址。线程 A 的 CAS 发现 head 还是指向 X，更新成功，但 X.next 早就不是原来那个 Y 了，栈结构直接乱套。

![wusuozhan.drawio.png](Z:/Public/images/0XTakAT5_wusuozhan.drawio_mianshiya.webp)

### 版本号方案：AtomicStampedReference

Java 提供了 AtomicStampedReference 来解决 ABA 问题，思路很简单：给值加个版本号，每次修改版本号加 1。CAS 不光比较值，还比较版本号，两个都对上才更新。

```java
AtomicStampedReference<Integer> ref = new AtomicStampedReference<>(100, 0);

// 获取当前值和版本号
int[] stampHolder = new int[1];
Integer value = ref.get(stampHolder);
int stamp = stampHolder[0];

// CAS 更新，值和版本号都要匹配
boolean success = ref.compareAndSet(value, 50, stamp, stamp + 1);
```

即使值从 100 变成 50 又变回 100，版本号也从 0 变成 1 再变成 2，CAS 比较版本号发现不匹配，更新失败。这就把中间状态的变化捕获到了。

### 标记位方案：AtomicMarkableReference

有时候不需要精确知道修改了多少次，只关心“有没有被改过”。AtomicMarkableReference 用一个 boolean 标记位来记录，比版本号更轻量：

```java
AtomicMarkableReference<Integer> ref = new AtomicMarkableReference<>(100, false);

// 获取当前值和标记
boolean[] markHolder = new boolean[1];
Integer value = ref.get(markHolder);

// 更新时翻转标记位
ref.compareAndSet(value, 50, false, true);
```

标记位的缺点是只能区分“改过/没改过”，如果值被改了偶数次，标记位翻回原来的状态，还是会漏掉。所以更推荐用 AtomicStampedReference。

### 什么时候不用担心 ABA

如果你操作的是不可变值，或者业务逻辑只关心“最终值是什么”而不关心“中间经历了什么”，ABA 就不是问题。比如简单的计数器，只要最终值对就行，中间变来变去无所谓。

`AtomicInteger`、`AtomicLong` 这些原子类没有提供版本号机制，因为对于纯数值操作，ABA 通常不影响正确性。只有涉及到引用、指针、节点这种“身份”敏感的场景，才需要特别处理。

## 面试官追问

#### 提问：AtomicStampedReference 的版本号会不会溢出？溢出了怎么办？

回答：版本号是 int 类型，理论上会溢出。但实际上要溢出得连续修改 21 亿多次，正常业务场景不太可能。就算溢出了，溢出后的值继续递增，只要两次 CAS 之间版本号不一样就行，不影响正确性。除非极端情况下两次操作恰好差了 $2^32$ 次，版本号回到原来的值，概率低到可以忽略。

#### 提问：为什么 JDK 的 `AtomicInteger` 不用版本号来解决 ABA？

回答：因为对于纯数值操作，大部分 ABA 不影响业务正确性。你做 `i`++ 操作，只关心最终值对不对，不关心中间被谁改过。加版本号会增加存储开销和操作复杂度，得不偿失。只有引用类型、指针操作这种场景，对象的“身份”很重要，才需要版本号来区分“同一个值”和“同一个对象”。

#### 提问：除了版本号，还有什么办法解决 ABA 问题？

回答：几个思路：第一是用锁，直接放弃 CAS，简单粗暴但失去了无锁的性能优势。第二是对象不复用，每次都 new 新对象，靠引用地址不同来规避 ABA，但会增加 GC 压力。第三是延迟回收，像 Hazard Pointer 或者 RCU 这种技术，保证在有线程持有引用期间不会真正释放内存，从根源上避免地址复用。Linux 内核的无锁数据结构就大量使用 RCU。

#### 提问：你在项目中遇到过 ABA 问题吗？怎么发现的？

回答：坦白说大部分业务代码用不到这么底层的无锁编程。真要写无锁数据结构，一般直接用 JDK 提供的 `ConcurrentHashMap`、`ConcurrentLinkedQueue` 这些，它们内部已经处理好了。自己造轮子写无锁结构的场景很少，主要是在看源码或者刷题的时候会关注 ABA。如果真遇到了，通常表现是偶发的数据不一致，很难复现，得靠 code review 和压测来发现。
