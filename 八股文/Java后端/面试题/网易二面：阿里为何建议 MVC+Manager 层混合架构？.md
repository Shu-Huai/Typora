# 网易二面：阿里为何建议 MVC+Manager 层混合架构？

初入编程世界时，前辈们总会教导我们，系统设计应遵循 **MVC（Model - View - Controller）** 架构。MVC 架构就像一个精巧的齿轮组，将整个系统清晰地划分为 Model（模型）、View（视图）和 Controller（控制器）三个层次。它巧妙地把用户视图和业务处理隔离开来，再通过控制器将它们紧密连接，如同搭建起一座沟通的桥梁，实现了表现与逻辑的完美解耦，是软件分层架构中的经典范式。

<img src="Z:/Public/images/640.webp" alt="图片" style="zoom:50%;" />

MVC 分层架构是架构领域中最为基础和简单的分层方式。当我们依据这种架构构建项目时，通常会创建三个关键目录：controller、service 和 dao，它们分别对应着表现层、逻辑层和数据访问层。

<img src="Z:/Public/images/640-1757050682468-1.webp" alt="图片" style="zoom:50%;" />

下面，我们来详细了解一下每层的具体作用：

- **Controller 层** ：它就像是交通枢纽的指挥者，主要负责对访问请求进行转发。同时，它还承担着各类基本参数的校验工作，对于一些无需复用的简单业务，也可以在这里直接处理。
- **Service 层** ：这是业务逻辑处理的核心地带，如同一位技艺精湛的工匠，精心雕琢着每一个业务流程。同时，它还负责管理事务，确保数据的一致性和完整性。
- **Dao 层** ：它是与底层数据库（如 MySQL、Oracle 等）进行数据交互的桥梁，负责将业务逻辑层的请求转化为数据库操作，为系统提供稳定的数据支持。

然而，随着业务的不断发展和代码量的持续增加，这种看似简单明了的三层架构逐渐暴露出一些问题。

## MVC 架构的弊端

传统的 MVC 分层架构存在以下几个较为明显的问题：

1. **Service 层代码臃肿** ：随着业务逻辑的日益复杂，Service 层需要处理的任务越来越多，代码量不断膨胀，在此，我想给大家送个福利，关注工众号：码猿技术专栏，回复关键词：1111 即可获取阿里内部 Java 性能优化手册。导致代码的可读性和可维护性急剧下降。
2. **Service 层事务问题频发** ：在 Service 层，大事务和事务嵌套的情况时有发生。这些问题不仅会导致系统性能下降，还会使问题的排查变得异常困难，给开发和维护工作带来巨大挑战。
3. **Dao 层业务逻辑混杂** ：Dao 层原本应该专注于数据访问，但在实际开发中，往往会掺杂一些业务逻辑，这使得代码的职责不够清晰，增加了代码的耦合度。
4. **Dao 层 SQL 语句复杂** ：随着业务的发展，Dao 层的 SQL 语句变得越来越复杂，关联查询大量增加。这不仅会影响数据库的性能，还会增加代码的维护难度。

为了解决这些问题，我们可以参考《alibaba java 开发手册》，在 Service 层之下新增一个通用业务处理层——Manager 层。

<img src="Z:/Public/images/640-1757050682468-2.webp" alt="图片" style="zoom:50%;" />

在这个新的分层架构中，Manager 层与 Service 层相互协作，各司其职。Manager 层提供原子性的服务接口，就像一个个标准化的零件；而 Service 层则根据业务逻辑的需求，对这些原子接口进行编排组合，构建出完整的业务流程。

## Manager 层的特征

《alibaba java 开发手册》对 Manager 层有如下描述：

Manager 层作为通用业务处理层，具有以下显著特征：

1. **第三方平台封装层** ：负责对第三方平台的接口进行封装，对返回结果进行预处理，并将异常信息进行转化，以适配上层接口的需求。
2. **Service 层通用能力下沉** ：将 Service 层的一些通用能力下沉到 Manager 层，如缓存方案的实现、中间件的通用处理等，提高代码的复用性和可维护性。
3. **DAO 层组合复用** ：与 DAO 层进行交互，对多个 DAO 进行组合复用，实现复杂业务的数据访问需求。

在实际开发中，我们可以按照以下方式使用 Manager 层：

1. **复杂业务处理** ：对于复杂的业务场景，Service 层负责准备好所需的数据，并将其传递给 Manager 层。Manager 层负责业务的编排和事务的处理，并且不允许相互调用，避免出现事务嵌套的问题。
2. **通用业务 DAO 封装** ：Manager 层专注于编写不包含业务逻辑的 SQL 语言，对通用业务进行 DAO 层的封装，提高代码的复用性和可维护性。
3. **复杂查询拆分** ：为了避免复杂的 `join` 查询对数据库造成过大压力，我们可以在 Manager 层对复杂查询进行拆分，将其转化为多个简单的查询，减轻数据库的负担。

需要注意的是，对于简单的业务场景，我们可以不使用 Manager 层，以免增加系统的复杂度。

## Manager 层使用案例

下面，我们通过一个具体的例子来说明 Manager 层的使用场景。

假设我们有一个用户系统，其中有一个获取用户信息的接口。在传统的三层架构中，该接口调用逻辑 Service 层的 `getUser` 方法，`getUser` 方法再与 `User DB` 交互获取数据，具体流程如左图所示。

这时，产品提出了一个新的需求：在 APP 中展示用户信息时，如果用户不存在，需要自动为用户创建一个新用户。同时，HTML5 页面需要保留之前的逻辑，即不需要创建用户。

<img src="Z:/Public/images/640-1757050682468-3.webp" alt="图片" style="zoom:50%;" />

在传统的三层架构下，逻辑层的边界变得模糊不清，表现层也不得不承担一部分业务逻辑。我们通常会在表现层 Controller 中添加业务逻辑处理代码，将获取用户和创建用户的接口进行编排。

而引入 Manager 层之后，情况就大不一样了。Manager 层提供创建用户和获取用户信息的接口，就像提供了两个独立的工具；Service 层则负责将这两个接口进行组装，构建出完整的业务流程。这样一来，原本分散在表现层的业务逻辑就被统一到了 Service 层，每一层的职责更加清晰明确。

接下来，我们通过一段实际代码来看看 Service 层与 Manager 层是如何区分的。

### **传统三层架构代码示**

```java
@Transactional(rollbackFor = Throwable.class)
public Result<String> upOrDown(Long departmentId, Long swapId) {
    // 验证 1
    DepartmentEntity departmentEntity = departmentDao.selectById(departmentId);
    if (departmentEntity == null) {
        return Result.error("部门xxx不存在");
    }
    // 验证 2
    DepartmentEntity swapEntity = departmentDao.selectById(swapId);
    if (swapEntity == null) {
        return Result.error("部门xxx不存在");
    }
    // 验证 3
    Long count = employeeDao.countByDepartmentId(departmentId);
    if (count != null && count > 0) {
        return Result.error("员工不存在");
    }
    // 操作数据库 4
    Long departmentSort = departmentEntity.getSort();
    departmentEntity.setSort(swapEntity.getSort());
    departmentDao.updateById(departmentEntity);
    swapEntity.setSort(departmentSort);
    departmentDao.updateById(swapEntity);
    return Result.OK("success");
}
```

这段代码在传统的三层架构中很常见，但它存在一个明显的问题——长事务问题（类似的情况还包括调用第三方接口）。在这段代码中，前三步的验证操作都使用了同一个数据库连接 `connection`。由于方法上添加了 `@Transactional` 注解，整个验证过程会一直占用该连接，占用时间可能会很长，直到方法执行结束，连接才会被归还给数据库连接池。

对于复杂业务来说，这种长时间占用同一个数据库连接的做法并不是一个好的选择。我们应该尽量缩短连接的占用时间，提高系统的性能和并发处理能力。

*说明：对于@Transactional 注解，当 spring 遇到该注解时，会自动从数据库连接池中获取 connection，并开启事务然后绑定到 ThreadLocal 上，如果业务并没有进入到最终的 操作数据库环节，那么就没有必要获取连接并开启事务，应该直接将 connection 返回给数据库连接池，供其他使用。*

### **引入 Manager 层后的代码示例**

```java
// DepartmentService.java
public Result<String> upOrDown(Long departmentId, Long swapId) {
    // 验证 1
    DepartmentEntity departmentEntity = departmentDao.selectById(departmentId);
    if (departmentEntity == null) {
        return Result.error("部门xxx不存在");
    }
    // 验证 2
    DepartmentEntity swapEntity = departmentDao.selectById(swapId);
    if (swapEntity == null) {
        return Result.error("部门xxx不存在");
    }
    // 验证 3
    Long count = employeeDao.countByDepartmentId(departmentId);
    if (count != null && count > 0) {
        return Result.error("员工不存在");
    }
    // 操作数据库 4
    departmentManager.upOrDown(departmentEntity, swapEntity);
    return Result.OK("success");
}

// DepartmentManager.java
@Transactional(rollbackFor = Throwable.class)
public void upOrDown(DepartmentEntity departmentEntity, DepartmentEntity swapEntity) {
    Long departmentSort = departmentEntity.getSort();
    departmentEntity.setSort(swapEntity.getSort());
    departmentDao.updateById(departmentEntity);
    swapEntity.setSort(departmentSort);
    departmentDao.updateById(swapEntity);
}
```

在引入 Manager 层之后，我们将数据准备工作放在 Service 层，然后将数据传递给 Manager 层。Manager 层添加 `@Transactional` 事务注解，负责进行数据库操作。这样一来，就避免了长事务问题，提高了系统的性能和可维护性。
