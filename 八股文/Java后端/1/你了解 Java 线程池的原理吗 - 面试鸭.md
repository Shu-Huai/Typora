# 你了解 Java 线程池的原理吗？ - 面试鸭 | 2026最新27 届校招 Java 热题+详细答案解析

## 回答重点

线程池是一种池化技术，核心思想就是**复用线程**，避免每来一个任务就 new 一个 Thread。创建销毁线程的开销不小，一个线程起码占用 1MB 左右的栈空间，还有操作系统层面的调度成本。

线程池有几个关键参数：核心线程数、最大线程数、空闲存活时间、工作队列、拒绝策略。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/GnON4IVI_image_mianshiya.webp)

工作流程是这样的：

1）任务来了先看核心线程够不够用，不够就创建新线程处理。默认核心线程是懒创建的，有任务才 new，不过可以通过 prestartAllCoreThreads 预热。

2）核心线程数满了之后，新任务不会立刻创建线程，而是先丢到工作队列里排队。

3）队列也塞满了，这时候才会创建非核心线程，最多创建到最大线程数。

4）队列满了、线程也到顶了，再来任务就触发拒绝策略。

5）线程空闲超过 keepAliveTime，并且当前线程数超过核心线程数，多余的线程会被回收。设置 allowCoreThreadTimeOut 为 true 的话连核心线程也能回收。

## 扩展知识

### 图解线程池执行流程

任务提交，线程池线程数还未达到核心线程数：

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/bXRpAeCu_image_mianshiya.webp)

核心线程数已满，任务队列未满的情况：

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/kFJ4tnHn_image_mianshiya.webp)

核心线程数已满，任务队列已满的情况：

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/Qy8wBV7q_image_mianshiya.webp)

线程池中线程数已达最大线程数的情况：

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/ndOHKdea_image_mianshiya.webp)

注意，核心线程和非核心线程在线程池内部压根没有标识区分，都是普通的 Worker 对象。图中区分只是为了说清创建顺序。

### 为什么先排队而不是先加线程

很多人觉得奇怪，任务多了为啥不直接加线程干活，非要先排队？

原因是线程不是免费的。每创建一个线程起码占用 1MB 栈空间，操作系统还要维护线程上下文、调度开销。如果任务突然来一波就疯狂创建线程，系统资源很快耗尽，CPU 光切换上下文就忙不过来了。

队列的作用是削峰填谷。任务暂时堆在队列里，让现有线程慢慢消化。如果队列都塞满了说明真扛不住了，这时候才加线程救急。

打个比方，餐厅有 5 个服务员正常够用，突然来了 20 桌客人，老板不会立刻招 15 个临时工，而是让客人先排队等位。如果排队都排到门外了，才考虑临时加人。

### 核心参数的实际含义

ThreadPoolExecutor 的 7 个参数：

1）corePoolSize：核心线程数，线程池平时维持的线程数量。即使这些线程空闲也不会被回收，除非设置了 allowCoreThreadTimeOut。

2）maximumPoolSize：最大线程数，线程池能创建的线程上限。核心线程满了、队列满了才会创建到这个数。

3）keepAliveTime 和 unit：空闲线程的存活时间。超过核心线程数的那部分线程，空闲超过这个时间就被回收。

4）workQueue：任务队列，核心线程忙不过来时任务就在这排队。

5）threadFactory：线程工厂，用来创建线程。可以自定义线程名方便排查问题，比如给线程起名叫 order-pool-thread-1。

6）handler：拒绝策略，队列满了、线程也到顶了，新任务怎么处理。

### 工作队列怎么选

常用的几种队列：

1）LinkedBlockingQueue：链表实现，默认无界。Executors.newFixedThreadPool 和 newSingleThreadExecutor 用的就是它。无界队列的风险是任务堆积太多撑爆内存。

2）ArrayBlockingQueue：数组实现，有界。必须指定容量，适合对资源控制严格的场景。

3）SynchronousQueue：不存任务，来一个任务必须有线程接手才能返回。Executors.newCachedThreadPool 用它，任务来了直接创建线程处理。

4）PriorityBlockingQueue：带优先级，任务按优先级排序执行。

生产环境建议用有界队列，避免内存溢出。阿里巴巴开发手册明确禁止使用 Executors 创建线程池，就是因为默认的无界队列有 OOM 风险。

### 四种拒绝策略

[Java 线程池有哪些拒绝策略？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933294909583361)

### 内置线程池类型

[Java 并发库中提供了哪些线程池实现？它们有什么区别？](https://www.mianshiya.com/bank/1789249312885223425/question/1780933294913777665)

### prestartAllCoreThreads 和 processWorkerExit 源码细节

线程池初始化时默认不创建线程，prestartAllCoreThreads 为 false：

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/gxiUEn4D_image_mianshiya.webp)

可以通过 prestartAllCoreThreads 方法预热核心线程：

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/Pn4d1TdM_image_mianshiya.webp)

processWorkerExit 方法控制线程回收逻辑，allowCoreThreadTimeOut 参数决定核心线程是否可回收：

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/jZ4wmNeW_image_mianshiya.webp)

## 面试官追问

#### 提问：线程池的线程是怎么复用的？执行完一个任务后为什么不销毁？

回答：线程池里的线程执行完任务后不会退出，而是进入一个 while 循环不断从队列里 take 任务。take 方法是阻塞的，没任务就挂在那等着。所以线程不是执行完就没了，而是一直活着等下一个任务。核心代码在 Worker.runWorker 方法里，while 循环配合 getTask 方法不断获取任务执行。

#### 提问：submit 和 execute 有什么区别？

回答：execute 只能提交 Runnable，没有返回值；submit 可以提交 Runnable 或 Callable，返回一个 Future 对象可以获取执行结果或异常。另外 execute 执行时抛异常会直接打印堆栈，submit 的异常被封装在 Future 里，调用 get 才能拿到。

#### 提问：线程池里的线程抛异常了会怎样？

>

详细解答可以看：[Java 线程池内部任务出异常后，如何知道是哪个线程出了异常？](https://www.mianshiya.com/question/1828365977491333121)

回答：分两种情况。execute 提交的任务抛异常，线程会终止，线程池会新建一个线程补上。submit 提交的任务抛异常，线程不会终止，异常被吞掉存在 Future 里，调 get 方法才会抛出来。所以用 submit 要记得处理 Future，不然异常就丢了。

#### 提问：shutdown 和 shutdownNow 有什么区别？

>

详细解答可以看：[Java 线程池中 shutdown 与 shutdownNow 的区别是什么？](https://www.mianshiya.com/question/1828628096288522241)

回答：shutdown 温和关闭，不再接受新任务，但会把队列里的任务执行完。shutdownNow 暴力关闭，尝试中断正在执行的线程，并返回队列里未执行的任务列表。实际场景里一般先 shutdown，等一段时间没关完再 shutdownNow。

#### 提问：核心线程数设成 0 会怎样？

回答：核心线程数设为 0 时，任务会先尝试入队。只要入队成功（有界队列未满或使用无界队列），都会触发 recheck：若当前没有工作线程，会创建一个非核心线程来处理队列中的任务。只有有界队列已满导致入队失败时，才会跳过 recheck，直接尝试创建非核心线程
...
