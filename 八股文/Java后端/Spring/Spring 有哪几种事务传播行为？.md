# Spring 有哪几种事务传播行为？

## 回答重点

Spring 事务传播行为一共有 **7 种**，定义在 `Propagation` 枚举里，用来控制一个事务方法被另一个事务方法调用时，事务该怎么处理。

1. `REQUIRED`：默认行为，有事务就加入，没有就新建一个。90% 的场景用它就够了

2. `SUPPORTS`：有事务就跟着跑，没有就裸奔，适合那些“可事务可不事务”的只读操作

3. `MANDATORY`：必须在已有事务里执行，外面没事务直接抛 `IllegalTransactionStateException`

4. `REQUIRES_NEW`：不管外面有没有事务，都新开一个独立事务，原来的事务挂起等着

5. `NOT_SUPPORTED`：明确不要事务，有事务就挂起，自己以非事务方式执行

6. `NEVER`：绝对不能有事务，发现外面有事务直接报错

7. `NESTED`：在当前事务里开一个嵌套子事务，用 `Savepoint` 实现，子事务回滚不影响外层

![](Z:/Public/images/CUD4GhOH_3zf4K2kkEi_mianshiya.webp)

代码里通过 `@Transactional` 注解指定：

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void logAudit(String action) {
    // 审计日志独立事务，主业务失败也要记下来
}
```

## 扩展知识

### 为什么需要这么多传播行为

最初大家写代码都是一个 Service 方法一个事务，简单直接。但业务复杂起来后，方法之间互相调用就出问题了：订单服务调库存服务，库存服务调日志服务，到底谁开事务、谁加入谁、日志失败要不要把订单也回滚？

传统 JDBC 没法优雅处理这种“事务嵌套”问题，Spring 就抽象出传播行为这套机制，让开发者用声明式的方式告诉框架：我这个方法对事务有什么要求。

### 最常用的三种场景

**REQUIRED** 占绝大多数场景。比如订单创建调库存扣减，两个操作必须在同一个事务里，要么一起成功要么一起回滚。OrderService 开了事务，InventoryService 用 REQUIRED 就会自动加入进来，不会再开新的。

**REQUIRES_NEW** 用在“不管主流程成败，我这步必须独立提交”的场景。典型的就是审计日志、操作记录。用户转账失败了没关系，但“转账失败”这条日志必须写进去，不能因为主事务回滚把日志也吞了。还有发送通知、积分变更这类“尽力而为”的操作也适合用它。

**NESTED** 适合“部分失败可以接受”的批量处理。比如导入 1000 条数据，每条数据开一个嵌套子事务，某条失败就回滚那条，其他的继续。外层事务负责整体控制，发现失败太多可以整体回滚。

![image.png](Z:/Public/images/q4Jr5D0s_image_mianshiya.webp)

### 事务传播行为使用示例

**REQUIRED（默认行为）** `REQUIRED` 是 Spring 的默认事务传播行为，意味着方法会加入现有事务中，如果没有事务就创建一个新事务。通常用于大多数业务逻辑中，确保整个业务过程处于同一个事务中。

```java
@Service
public class OrderService {

    @Autowired
    private InventoryService inventoryService;

    @Transactional(propagation = Propagation.REQUIRED)
    public void placeOrder(Order order) {
        // 保存订单
        saveOrder(order);
        
        // 调用库存减少操作，使用同一个事务
        inventoryService.reduceInventory(order);
    }

    private void saveOrder(Order order) {
        // 保存订单逻辑
    }
}

@Service
public class InventoryService {

    @Transactional(propagation = Propagation.REQUIRED)
    public void reduceInventory(Order order) {
        // 减少库存的逻辑
    }
}
```

在这个例子中，`OrderService` 和 `InventoryService` 使用了 `REQUIRED`，意味着 `reduceInventory()` 方法和 `placeOrder()` 方法运行在同一个事务中。如果其中一个方法抛出异常，整个事务都会回滚。

**REQUIRES_NEW** `REQUIRES_NEW` 强制启动一个新事务，无论是否存在当前事务。如果有现有事务，它将被挂起，直到新事务完成。

```java
@Service
public class PaymentService {

    @Autowired
    private LogService logService;

    @Transactional(propagation = Propagation.REQUIRED)
    public void processPayment(Order order) {
        // 执行支付逻辑
        process(order);
        
        // 记录日志，独立事务
        logService.logPayment(order);
    }

    private void process(Order order) {
        // 支付处理逻辑
    }
}

@Service
public class LogService {

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logPayment(Order order) {
        // 记录支付日志逻辑，使用独立事务
    }
}
```

在这个例子中，`PaymentService` 的 `processPayment()` 和 `LogService` 的 `logPayment()` 在不同的事务中执行。如果 `processPayment()` 方法抛出异常，`logPayment()` 仍然会提交，因为它运行在独立的事务中。

**SUPPORTS** `SUPPORTS` 表示方法可以支持事务，但不强制要求。如果当前有事务，它将在事务中执行；如果没有事务，它将以非事务方式执行。

```java
@Service
public class AccountService {

    @Transactional(propagation = Propagation.REQUIRED)
    public void transferFunds(Account fromAccount, Account toAccount, BigDecimal amount) {
        // 转账逻辑
        withdraw(fromAccount, amount);
        deposit(toAccount, amount);
    }

    @Transactional(propagation = Propagation.SUPPORTS)
    public BigDecimal getBalance(Account account) {
        // 获取余额，如果存在事务，则在事务中执行；否则无事务执行
        return account.getBalance();
    }

    private void withdraw(Account fromAccount, BigDecimal amount) {
        // 扣款逻辑
    }

    private void deposit(Account toAccount, BigDecimal amount) {
        // 存款逻辑
    }
}
```

`getBalance()` 方法可以在事务内或非事务中执行。如果 `transferFunds()` 调用了 `getBalance()`，它将在 `REQUIRED` 事务中执行；否则，它以非事务方式执行。

**NOT_SUPPORTED** `NOT_SUPPORTED` 表示该方法不支持事务，如果当前有事务，它将挂起该事务，并在非事务环境中执行。

```java
@Service
public class ReportService {

    @Transactional(propagation = Propagation.REQUIRED)
    public void generateMonthlyReport() {
        // 生成月度报告，支持事务
        generateReportData();
        
        // 发送报告邮件，无事务
        sendReportEmail();
    }

    private void generateReportData() {
        // 生成报告数据逻辑
    }

    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    public void sendReportEmail() {
        // 发送邮件逻辑，挂起现有事务
    }
}
```

在这个例子中，`generateMonthlyReport()` 方法中的 `generateReportData()` 运行在事务中，而 `sendReportEmail()` 运行在非事务环境中，即使 `generateMonthlyReport()` 已经有事务，它也会挂起现有事务。

**MANDATORY** `MANDATORY` 表示该方法必须在已有事务中运行，如果没有现有事务则抛出异常。

```java
@Service
public class TransactionalService {

    @Transactional(propagation = Propagation.REQUIRED)
    public void performAction() {
        // 执行主要操作
        performSecondaryAction();
    }

    @Transactional(propagation = Propagation.MANDATORY)
    public void performSecondaryAction() {
        // 必须在事务内执行
    }
}
```

在这个例子中，`performSecondaryAction()` 必须在一个事务中运行。如果它被独立调用而没有事务，则抛出异常。如果 `performAction()` 方法已经启动了一个事务，那么 `performSecondaryAction()` 可以正常运行。

**NEVER** `NEVER` 表示该方法不允许在事务中运行，如果当前存在事务，则抛出异常。

```java
@Service
public class TransactionFreeService {

    @Transactional(propagation = Propagation.NEVER)
    public void executeWithoutTransaction() {
        // 执行逻辑，不能在事务中执行
    }
}
```

如果在事务上下文中调用 `executeWithoutTransaction()` 方法，会抛出异常，因为它要求不在任何事务中执行。

**NESTED** `NESTED` 表示如果当前存在事务，则在该事务中创建一个嵌套事务（支持保存点），子事务可以独立回滚而不影响主事务。

```java
@Service
public class NestedTransactionService {

    @Transactional(propagation = Propagation.REQUIRED)
    public void mainOperation() {
        // 执行主操作
        try {
            nestedOperation();
        } catch (Exception e) {
            // 嵌套事务回滚，不影响主事务
        }
    }

    @Transactional(propagation = Propagation.NESTED)
    public void nestedOperation() {
        // 嵌套事务操作
        // 可以在这里回滚嵌套事务
        throw new RuntimeException("嵌套事务回滚");
    }
}
```

在这个例子中，`mainOperation()` 是主事务，而 `nestedOperation()` 是嵌套事务。如果 `nestedOperation()` 失败，它只会回滚嵌套事务，主事务 `mainOperation()` 不会受影响。

## 面试官追问

#### 提问：REQUIRES_NEW 会不会有性能问题？什么时候该用什么时候不该用？

回答：会有。每次 REQUIRES_NEW 都要新开一个数据库连接，连接池就那么大，高并发下容易耗尽。比如一个请求里调了 5 次 REQUIRES_NEW 的方法，就同时占用 6 个连接。所以只在“必须独立提交”的场景用，像审计日志、消息发送确认这种。普通的业务逻辑老老实实用 REQUIRED，共享连接就够了。

#### 提问：NESTED 需要数据库支持，如果数据库不支持 Savepoint 会怎样？

回答：Spring 会检测，如果底层不支持 Savepoint，会抛 NestedTransactionNotSupportedException。不过主流数据库基本都支持，MySQL InnoDB、PostgreSQL、Oracle 都没问题。真正容易出问题的是用 JTA 分布式事务管理器的时候，很多 JTA 实现不支持 Savepoint，这时候只能改用 REQUIRES_NEW 或者业务上做补偿。

#### 提问：事务传播行为在分布式事务里还有用吗？

详细解答可以看：[Spring 事务传播行为有什么用?](https://www.mianshiya.com/question/1780933295421288449)

回答：传统意义上的传播行为是针对单数据源的，分布式事务场景下基本没用。Seata 这类分布式事务框架有自己的一套传播机制，通过 XID 在服务间传递来串联全局事务。不过思想是相通的，REQUIRED 对应加入全局事务，REQUIRES_NEW 对应开启新的全局事务分支。

#### 提问：为什么说 NESTED 子事务回滚不影响外层，但外层回滚会把子事务带走？

详细解答可以看：[Spring 事务传播行为有什么用?](https://www.mianshiya.com/question/1780933295421288449)

回答：因为 NESTED 底层是 Savepoint，子事务并没有真正提交，只是在当前事务里打了个标记。子事务“提交”其实只是释放 Savepoint，数据还在外层事务的控制下。外层最终 commit，子事务的数据才真正落盘；外层 rollback，整个事务包括所有 Savepoint 的修改全部撤销。所以说 NESTED 是“假独立”，REQUIRES_NEW 才是“真独立”。
