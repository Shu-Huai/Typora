# Java 中 volatile 关键字的作用是什么？ - 面试鸭 | 2026最新27 届校招 Java 热题+详细答案解析

## 回答重点

volatile 的核心作用就两个：**可见性**和**禁止指令重排**。

1）可见性：一个线程改了 volatile 变量，其他线程立马能看到最新值。没有 volatile 的话，线程各自在自己的 CPU 缓存里操作，改了也不一定同步到主内存，别的线程可能永远读到的都是旧值。

2）禁止指令重排：编译器和 CPU 为了性能会重排指令，单线程没问题，多线程就可能出幺蛾子。volatile 通过内存屏障把重排限制住，写操作前插 StoreStore 屏障，读操作后插 LoadLoad 屏障，保证代码执行顺序符合预期。

来看个可见性的经典坑：

```java
private static boolean flag = false;

public static void main(String[] args) {
  new Thread(() -> {
      while (!flag) {
          // 空转
      }
      System.out.println("Thread terminated.");
  }).start();

  Thread.sleep(1000);
  flag = true; // 没有 volatile，这个改变对其他线程不可见
}
```

上面代码，子线程可能永远不会退出循环。因为子线程把 flag 缓存到自己的工作内存里了，主线程改了 flag，子线程压根不知道。加上 volatile 后，每次读 flag 都从主内存拿，改了立马能看到。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/puKTBbf3_MrrVtFvzwR_mianshiya.webp)

## 扩展知识

### 可见性问题的根源

Java 内存模型里，每个线程有自己的工作内存，变量操作都在工作内存里进行，不是直接读写主内存。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/AiNnhu94_image_mianshiya.webp)

线程 A 改了变量，什么时候同步回主内存？什么时候其他线程能看到？JVM 规范没强制要求立即同步，所以就出现了可见性问题。volatile 就是强制规定：写完立刻刷回主内存，读的时候必须从主内存拿最新值。

### volatile 的底层实现

volatile 在 JVM 层面是通过**内存屏障**来实现的。编译器和处理器为了优化性能，可能会对指令重排序，内存屏障就是一道"栅栏"，阻止屏障两侧的指令跨越屏障重排。

对 volatile 变量的操作会插入以下屏障：

1）写 volatile 变量之前，插入 StoreStore 屏障，保证前面的普通写操作先完成。

2）写 volatile 变量之后，插入 StoreLoad 屏障，保证 volatile 写对后续的 volatile 读可见。

3）读 volatile 变量之后，插入 LoadLoad 屏障，保证 volatile 读在后续普通读之前。

4）读 volatile 变量之后，插入 LoadStore 屏障，保证 volatile 读在后续普通写之前。

在 x86 架构上，StoreStore、LoadLoad、LoadStore 这三个屏障是空操作，因为 x86 的内存模型本身就保证了这些顺序。只有 StoreLoad 屏障需要一条 `lock` 前缀指令来实现，它会锁住内存总线或使用缓存锁。

### 双重检查锁定和指令重排

指令重排最经典的坑就是 DCL 单例模式：

```java
public class Singleton {
  private static volatile Singleton instance;

  private Singleton() {}

  public static Singleton getInstance() {
      if (instance == null) {
          synchronized (Singleton.class) {
              if (instance == null) {
                  instance = new Singleton();
              }
          }
      }
      return instance;
  }
}
```

`instance = new Singleton()` 这行代码，JVM 层面其实是三步：分配内存、调用构造函数、赋值引用。正常顺序是 1→2→3，但 CPU 可能重排成 1→3→2。要是线程 A 执行到 3 还没执行 2，线程 B 判断 instance != null 直接返回，拿到的就是个半成品对象，构造函数还没跑完呢。

加上 volatile 后，禁止这种重排，保证构造函数执行完才赋值引用。

### volatile 不能保证原子性

很多人以为 volatile 能解决所有并发问题，其实不行。看这个例子：

```java
private static volatile int count = 0;

public static void main(String[] args) throws InterruptedException {
  Thread[] threads = new Thread[1000];
  for (int i = 0; i < 1000; i++) {
      threads[i] = new Thread(() -> count++);
      threads[i].start();
  }
  for (Thread t : threads) t.join();
  System.out.println(count); // 结果大概率不是 1000
}
```

count++ 看起来一行代码，实际上是读取、加 1、写回三步操作。两个线程同时读到 count=5，各自加 1 写回 6，本来应该是 7 的。volatile 只保证每次读都是最新值，不保证读-改-写这个组合操作是原子的。

要保证原子性，得用 AtomicInteger 或者 synchronized。

### volatile 和 synchronized 怎么选

特性volatilesynchronized原子性不保证保证可见性保证保证有序性保证保证阻塞不阻塞可能阻塞性能开销小开销相对大适用场景状态标志、一写多读复杂临界区、读写都要保护

简单说，volatile 适合一个线程写、多个线程读的场景，比如停止标志、配置开关。涉及到 check-then-act 或者 read-modify-write 这种复合操作，必须用 synchronized 或者原子类。

### happens-before 和 volatile

JMM 定义了 happens-before 规则来描述操作之间的可见性关系。volatile 相关的规则是：对 volatile 变量的写操作，happens-before 于后续任意线程对它的读操作。

翻译成人话就是：线程 A 写 volatile 变量之前的所有操作，对线程 B 读这个 volatile 变量之后都可见。这不光是 volatile 变量本身，连带着前面的普通变量修改也能被看到。很多框架利用这个特性来实现轻量级同步。

## 面试官追问

#### 提问：volatile 能保证 64 位 long 和 double 的原子性读写吗？

回答：能。JVM 规范里 32 位虚拟机对 long 和 double 的读写不保证原子性，可能分成两次 32 位操作，中间被其他线程插入就会读到"半个值"。加上 volatile 后，JVM 必须保证 64 位变量的读写是原子的。不过现在主流都是 64 位 JVM，这个问题基本不存在了。

#### 提问：volatile 数组能保证数组元素的可见性吗？

回答：不能。volatile 只保证数组引用本身的可见性，比如你把数组引用指向另一个数组对象，这个改变其他线程能看到。但数组里面元素的修改，volatile 管不着。要保证元素可见性，得用 AtomicIntegerArray 这类原子数组，或者每次修改元素后重新赋值引用触发 volatile 语义。

#### 提问：为什么说 volatile 比 synchronized 轻量？

回答：synchronized 要走 Monitor 那套，涉及用户态和内核态切换，线程可能被挂起和唤醒，重量级锁的情况下开销很大。volatile 只是在读写时加内存屏障，不涉及锁竞争、线程阻塞这些操作，CPU 直接执行屏障指令就行。但 JDK 6 之后 synchronized 做了大量优化，偏向锁、轻量级锁的场景下性能差距没那么大了。

#### 提问：有没有遇到过 volatile 失效的情况？

回答：严格说 volatile 不会"失效"，但有些场景容易误用。比如把 volatile 用在复合操作上，像 count++ 这种，以为加了 volatile 就线程安全了，结果还是有并发问题。还有一种情况是逻辑上依赖多个 volatile 变量的组合状态，单个变量可见了但组合判断还是可能出问题。根本原因是没理解 volatile 只保证单次读写的可见性和有序性，不保证原子性。
...
