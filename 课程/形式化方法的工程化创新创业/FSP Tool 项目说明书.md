# FSP Tool 项目说明书

## 项目概述

本项目是《形式化方法的工程化创新创业》课程的实践作业，题为：

> **A tool for producing the expected values for a given functional scenario path and input**
>
>  （一个用于根据功能场景路径和输入值自动推导预期输出结果的工具）

该工具基于 SOFL（Structured Object-oriented Formal Language）语言规范，支持对 SOFL 模块中的 **Functional Scenario Path（FSP）路径进行模拟执行与验证**。通过自动或交互式方式输入初始状态和过程参数，系统可对每条路径进行预期结果计算与输出，同时验证路径是否可达、约束条件是否满足，并检查中间状态与最终状态的类型一致性。

项目目标包括：

- 实现对 SOFL module、state、process、pre/post 的解析与建模；
- 支持 Functional Scenario 的条件选择与赋值解析；
- 构建类型安全的表达式求值与状态转移引擎；
- 提供 CLI 与 JavaFX 双交互界面，支持测试路径可执行性；
- 报告无法激活（不可达）路径及对应 precondition 失败原因；
- 自动检查并生成每步执行后的期望状态（Expected State）。

## 核心术语定义

### SOFL（Structured Object-oriented Formal Language）

SOFL 是一种融合了**结构化建模、形式化规格说明与面向对象思想**的形式语言，适用于软件系统的**精确建模、正确性分析与行为验证**。

SOFL 提供：

- **可读性强的语法结构**
- **支持三种建模层次：数据、控制、功能**
- **将形式方法应用于工业可接受的工程实践**

### module

- 表示一个完整的 SOFL 规格说明单元
- 包含：状态变量、过程定义、操作定义（可选）
- 类似于面向对象语言中的类（class）

**作用：** 封装系统的状态与行为描述。

#### 例子

```
module BankSystem

state
  balance: int
  loginSuccess: bool

end_module
```

### process

- 描述系统中一个过程或操作的行为
- 包含：过程名、形参、`pre`（前置条件）和 `post`（后置条件）
- 可包含多个 **功能场景（Functional Scenario）**

**作用：** 是 SOFL 中最基本的行为单位，用于状态变迁的建模。

#### 例子

```
process Login(username: string, password: string)
pre username ∈ Users
post if password == Users[username]
     then loginSuccess = true
     else loginSuccess = false
end_process
```

### functional scenario

- 是 `post` 的语义分支单元，描述在某个 guard 条件成立时系统状态如何变化
- 由：
  - guard（守卫条件）
  - 状态赋值（defines）组成

**作用：** 把 `post` 分解为多个可选的“功能情景”。

#### 例子

```
functional scenario 1:
guard: password == Users[username]
defines: loginSuccess = true

functional scenario 2:
guard: !(password == Users[username])
defines: loginSuccess = false
```

### functional scenario path

- 是多个 `process` 顺序连接形成的路径（类似一个执行 trace）
- 系统按照路径上的每个过程，逐步检查 `pre`，匹配 `functional scenario`，并应用其状态变更

**作用：** 描述系统执行过程中的一个“行为轨迹”

#### 例子

```
Functional Scenario Path:
Login → Withdraw → Logout
```

### 完整例子

```
module PurchaseSystem

state
  Users: map string → string
  stock: map string → int
  cart: map string → int
  success: bool

process Login(username: string, password: string)
pre username ∈ Users
post if password == Users[username] then success = true else success = false
end_process

process AddToCart(product_id: string, quantity: int)
pre success = true ∧ product_id ∈ stock
post if stock[product_id] ≥ quantity then
  cart[product_id] = cart[product_id] + quantity ∧
  stock[product_id] = stock[product_id] - quantity
else
  cart = cart ∧ stock = stock
end_process

end_module
```

## 系统功能说明

本系统是一款面向 SOFL 规范的功能验证与路径测试工具，支持用户输入一个完整的 SOFL 模块规范（含状态定义与过程定义），并基于指定的 **Functional Scenario Path（FSP）** 路径执行自动化模拟，输出每一步的状态变更结果。

系统功能覆盖了从解析 → 验证 → 执行 → 输出的完整流程，主要功能包括：

### SOFL 模块解析

- 支持完整的 `module`、`state`、`process` 结构解析；
- 支持类型包括：`int`、`bool`、`string`、`map`、`set`；
- 参数类型声明格式：`process Add(a: int, b: int)`；
- 支持 `post` 中 `if ... then ... else` 分支自动拆解为多个 `functional scenario`；
- 自动检测格式错误并给出错误提示。

### 状态变量与类型管理

- 系统对每个状态变量维护其类型（SOFLType）与当前值；
- 所有用户输入（初始状态、过程参数）均经过严格类型校验；
  - 例如：声明为 `int` 的变量禁止输入 `5.5`；
  - 输入为 `map` 或 `set` 时支持 JSON 结构解析；
- 在执行期间确保状态变量赋值类型与声明一致，防止类型漂移。

### Functional Scenario Path 执行引擎

- 按用户指定路径依序执行 process；
- 每个过程执行前检查 `pre` 条件是否满足；
- 自动匹配可激活的 `functional scenario` 并应用对应赋值；
- 支持对 map 中键值的更新表达式，例如：`cart[product_id] = ...`；
- 支持 `null + int` 的自动补 0 表达式修复（用于处理未初始化元素）；
- 执行结果可逐步输出每一步状态变更，便于调试与教学展示。

### 输入输出交互方式

- 提供两种运行模式：
  - 命令行模式（CLI）：适用于终端输入、调试；
  - 图形界面模式（JavaFX）：适用于可视化运行、教学演示；
- 在执行前自动提示用户输入缺失的参数或初始状态变量；
- 输出包含：
  - 变量初始化
  - 每一过程激活的场景
  - 每一步状态更新
  - 最终状态

### 错误与异常处理

- 若某个过程的 `precondition` 不满足，将中止执行并给出提示；
- 若路径中某个过程无法激活任何 scenario，则视为“不可达路径”；
- 对非法赋值（如变量未声明、类型错误、表达式出错）均抛出明确异常；
- 用户可以通过异常信息追踪到具体出错的过程、表达式或变量。

### 模块可拓展性

系统各组件（如类型系统、表达式解析器、交互接口）设计为可插拔模块，后续可支持：

- 更丰富的数据结构（如 record、tuple）；
- 更复杂的表达式类型（如嵌套条件）；
- 持久化加载模块文件、保存测试结果等。

## 系统架构与模块设计

本系统遵循**模块化设计原则**，整体架构清晰划分为五大核心模块：解析器模块、类型系统模块、执行引擎模块、用户交互模块和数据模型模块。每个模块职责单一、接口明确，便于后期拓展或重构。

### 系统模块结构图

```
            ┌────────────────────────────┐
            │      用户交互模块 (CLI/GUI) │
            └────────────┬───────────────┘
                         │
                         ▼
             ┌──────────────────────────┐
             │     SOFLModuleParser     │◄─────── 解析器模块
             └──────────────────────────┘
                         │
                         ▼
           ┌─────────────────────────────┐
           │       数据模型模块          │
           │（SOFLModule, Process, etc.）│
           └─────────────────────────────┘
                         │
                         ▼
             ┌──────────────────────────┐
             │      执行引擎模块        │
             │     （SOFLExecutor）     │
             └──────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │    类型系统模块     │
              │  （SOFLType 体系）   │
              └─────────────────────┘
```

### 模块说明与职责

#### SOFLModuleParser（解析器模块）

- 负责将用户输入的 SOFL 文本规范解析为内部数据结构 `SOFLModule`
- 功能包括：
  - 模块名提取
  - 状态变量解析
  - `process` 的头、pre/post 条件分析
  - `post` 表达式解析成 `FunctionalScenario`
- 支持参数类型标注解析，如 `a: int`

#### 数据模型模块（`entity` 包）

- 定义核心数据结构：
  - `SOFLModule`：整个模块结构
  - `SOFLVariable`：状态变量及类型
  - `SOFLProcess`：过程定义及参数、pre/post 条件
  - `FunctionalScenario`：每个过程的分支情形（guard + defines）
- 结构统一，支持类型注解、序列化等操作

#### SOFLExecutor（执行引擎模块）

- 负责执行用户指定的 Functional Scenario Path：
  - 检查每一过程的前置条件
  - 匹配场景的 guard 条件
  - 评估表达式并更新状态
- 具备：
  - 类型安全赋值
  - `map[key]` 更新处理
  - null + int 表达式容错机制
  - 逐步输出每一步状态变更

#### 用户交互模块（CLI & GUI）

- `ConsoleInteraction`：
  - 控制台模式，基于 `Scanner` 与终端输入输出
- `JavaFXInteraction`：
  - 图形化界面，用户可视化输入变量、查看状态更新与场景激活路径

二者共用接口 `SOFLInteraction`，体现**策略模式（Strategy Pattern）**，使得核心逻辑与 UI 解耦。

#### 类型系统模块（`sofltype` 包）

- 支持以下类型表达：
  - `PrimitiveSOFLType`（int, bool, string）
  - `MapSOFLType`（map keyType → valueType）
  - `SetSOFLType`（集合类型）
- 每个 `SOFLVariable` 和参数都与类型绑定，确保输入与执行期间的类型一致性

## 输入与输出说明

本章介绍本系统的输入数据格式要求、用户交互流程，以及系统最终输出的结构与含义。通过标准化输入输出约定，用户可以方便地使用该工具执行和验证任意合法的 SOFL 功能场景路径。

### 输入内容要求

系统要求用户按顺序提供以下两类输入：

#### SOFL 模块规范（纯文本）

- 必须包含以下结构：

  - `module ModuleName`
  - `state` 部分：声明状态变量及其类型（缩进格式）
  - 一个或多个 `process`：包含参数列表、`pre` 条件与 `post` 表达式
  - 每个 `process` 必须以 `end_process` 结尾
  - 模块以 `end_module` 结尾

- 支持的类型包括：

  - 原始类型：`int`, `bool`, `string`
  - 容器类型：`map keyType → valueType`, `set of elementType`

- 过程参数需指定类型，如：

  ```
  process Add(a: int, b: int)
  ```

- 示例输入：

  ```
  module Demo
  
  state
    counter: int
    success: bool
  
  process Inc(x: int)
  pre x > 0
  post counter = counter + x
  end_process
  
  end_module
  ```

**所有功能场景互斥**：

- 每个 `process` 中的不同 `functional scenario` 的 `guard` 条件应互斥；
- 否则只会激活第一个匹配成功的场景，其余忽略。

**`post` 表达式中仅允许单层 `if ... then ... else`**：

- **禁止**在 `then` 或 `else` 块中再嵌套 `if`；

- 不允许链式结构如 `if ... then ... else if ... then ... else`；

- 合法结构示例：

  ```
  post if x ≥ 0 then count = count + 1 else count = count - 1
  ```

- **非法结构示例：**

  ```
  Post if x ≥ 0 then
    if y > 0 then count = count + y else count = count - y
  else ...
  ```

- 此限制简化了 `functional scenario` 的解析和语义匹配，也符合 SOFL 教学工具的目标。

#### 执行路径定义（Functional Scenario Path）

- 用户输入一组按顺序执行的 `process` 名称：

  ```
  请输入要执行的路径（用英文逗号分隔 process 名称）: Login, AddToCart
  ```

#### 运行时交互输入（初始变量与参数值）

- 系统在运行前将提示用户依次输入：

  - 每个状态变量的初始值（若未设定默认）
  - 每个 `process` 的参数值

- 示例输入方式（控制台）：

  ```
  请输入 stock: {"apple": 10, "banana": 5}
  请输入 product_id: apple
  请输入 quantity: 1
  ```

### 输出内容说明

系统将输出全过程的中间状态和最终状态，主要包括：

| 输出内容   | 示例                                       | 说明                       |
| ---------- | ------------------------------------------ | -------------------------- |
| 变量初始化 | `变量初始化: stock = {"apple": 10}`        | 初始化状态变量             |
| 场景激活   | `🌟 激活场景: stock[product_id] ≥ quantity` | 匹配的 Functional Scenario |
| 状态更新   | `集合更新: cart[apple] = 1`                | 执行后的赋值操作           |
| 最终状态   | `最终状态: {...}`                          | 完整变量集                 |

### 错误与异常提示

- 若某 `process` 的 `pre` 不满足：

  ```
  前置条件不满足: username ∈ Users
  ```

- 若无可激活的 FS：

  ```
  No matching scenario for process: AddToCart
  ```

- 若用户输入类型不合法：

  ```
  ❌ 输入 5.5 不是合法整数
  ```

### 支持的输入方式

| 模式         | 实现类               | 特点                               |
| ------------ | -------------------- | ---------------------------------- |
| 控制台 CLI   | `ConsoleInteraction` | 命令行输入、测试灵活               |
| 图形界面 GUI | `JavaFXInteraction`  | 适用于教学演示，输入框提示变量类型 |

此设计确保用户可在 CLI 或 GUI 下进行交互式验证，并对每条路径的中间状态和预期结果进行精确观测。

## 实现原理与关键算法

本章详细介绍系统的关键设计思想与实现机制，包括用户输入解析、路径执行流程、条件匹配逻辑、状态更新规则、表达式求值方法与类型校验机制，展示了系统如何实现对 SOFL 模块的模拟执行与验证。

### 文本解析机制（SOFLModuleParser）

用户输入的 SOFL 模块是纯文本格式，系统使用 `SOFLModuleParser` 类进行解析，支持以下结构：

```
module M
state
  a: int
  b: map string → int
process Add(x: int)
pre true
post a = a + x
end_process
end_module
```

系统通过正则表达式与缩进判断语义块：

- `module` 和 `state` 作为块级结构；
- `process` 支持参数列表 `process Add(x: int)`；
- `post` 中的 `if ... then ... else` 会被拆为两个 `FunctionalScenario`；

关键代码如下：

```java
if (post.startsWith("if ") && post.contains(" then ") && post.contains(" else ")) {
    String condition = post.substring(3, post.indexOf(" then ")).trim();
    String thenPart = ...;
    String elsePart = ...;
    scenarios.add(new FunctionalScenario(...));
    scenarios.add(new FunctionalScenario(...));
}
```

### 功能场景匹配与激活

系统中每个 `process` 的 `post` 条件在解析阶段被转化为一个或多个 `functional scenario`，每个场景包含一个 `guard` 表达式与对应的状态变更。

在执行路径中，系统依次尝试匹配场景条件，选中首个使 guard 成立的场景：

```java
FunctionalScenario selected = null;
for (FunctionalScenario fs : proc.getScenarios()) {
    String expr = SOFLExpressionNormalizer.normalize(fs.getGuard());
    if (evaluateGuard(expr, initialState, params)) {
        selected = fs;
        io.writeOutput("🌟 激活场景: " + fs.getGuard());
        io.writeOutput("定义: " + fs.getDefines());
        break;
    }
}
```

若无任何场景可用，则该路径在该步骤上不可激活，系统会抛出异常提示用户。

### 表达式求值与上下文构建

本系统采用 Apache Commons JEXL 作为表达式求值引擎，JEXL 支持标准布尔表达式、数值运算与 map 取值等操作。

所有表达式执行前，系统构建统一的上下文环境，将当前状态变量与参数值绑定进作用域中：

```java
private JexlContext createContext(Map<String, Object> state, Map<String, Object> params) {
    JexlContext context = new MapContext();
    state.forEach(context::set);
    params.forEach(context::set);
    return context;
}
```

JEXL 表达式如 `stock[product_id] ≥ quantity` 可直接使用该上下文进行求值。

### 状态变量与 Map 元素更新机制

系统支持对普通变量和 `map[key]` 形式的状态变量赋值。

当赋值为 `map[key] = value` 形式时，系统先解析 key 表达式并查找对应容器 Map，然后再执行赋值：

```java
if (rawVar.contains("[")) {
    String container = rawVar.substring(0, rawVar.indexOf("["));
    Object key = evaluateExpression(keyExpr, initialState, params);
    Object containerObj = initialState.get(container);

    if (containerObj instanceof Map<?, ?> rawMap) {
        Map<Object, Object> map = new LinkedHashMap<>(rawMap);
        Object value = safeEvaluateWithNullFix(expr, initialState, params); // 含null+补偿
        map.put(key, value);
        initialState.put(container, map);
    }
}
```

此处调用了 `safeEvaluateWithNullFix()`，用于处理可能的 null 值加法（如 `cart[apple] + 1` 中 `cart[apple] == null` 的情况）。

### null 值加法自动补偿机制

为提升用户体验，系统在执行诸如 `cart[product_id] + quantity` 表达式时，若 `cart[product_id] == null`，将自动视为 `0`，避免执行失败：

```java
private Object safeEvaluateWithNullFix(String expr, Map<String, Object> state, Map<String, Object> params) {
    try {
        return evaluateExpression(expr, state, params);
    } catch (JexlException e) {
        if (e.getMessage().contains("null") && expr.contains("+")) {
            String[] parts = expr.split("\\+");
            Object left = evaluateExpressionSafe(parts[0].trim(), state, params, 0);
            Object right = evaluateExpressionSafe(parts[1].trim(), state, params, 0);
            return toNumberOrZero(left).intValue() + toNumberOrZero(right).intValue();
        } else {
            throw e;
        }
    }
}
```

该机制使得未初始化的 `map` 元素在表达式中默认视为 `0`，符合常见建模习惯，也有助于流程顺利进行。

## 表达式与类型系统支持

本系统内嵌表达式求值引擎和强类型系统，支持用户在 `pre`、`post` 条件与功能场景中使用结构化逻辑表达式，并对所有变量值进行类型约束与校验。

### 支持的类型体系

系统中所有状态变量与参数均需显式声明类型，当前支持以下 SOFL 类型：

| SOFL 类型   | 描述   | Java 类型映射 | 示例输入         |
| ----------- | ------ | ------------- | ---------------- |
| `int`       | 整数   | `Integer`     | `10`             |
| `bool`      | 布尔   | `Boolean`     | `true` / `false` |
| `string`    | 字符串 | `String`      | `"abc"`          |
| `map K → V` | 映射   | `Map<K, V>`   | `{"apple": 10}`  |
| `set of T`  | 集合   | `Set<T>`      | `["a", "b"]`     |

所有变量值在系统运行时将与其声明类型进行一致性校验，任何类型不匹配都将引发错误提示。

### 表达式支持范围

本系统使用 Apache Commons JEXL 表达式引擎，支持以下表达式类型：

#### 比较表达式

- 形式：`x > y`, `x ≥ y`, `x == y`, `x ∈ set`

- 示例：

  ```
  pre quantity > 0
  pre username ∈ Users
  ```

#### 布尔逻辑表达式

- 支持：`∧`（与）、`∨`（或）、`¬`（非）

- 实际解析中将统一替换为 JEXL 标准形式：

  | SOFL 符号 | JEXL 等价      |
  | --------- | -------------- |
  | `∧`       | `&&`           |
  | `∨`       | `              |
  | `¬`       | `!`            |
  | `∈`       | `in`（已扩展） |

#### 算术表达式

- 支持：`+`, `-`, `*`, `/`

- 示例：

  ```
  post counter = counter + x
  post stock[product_id] = stock[product_id] - quantity
  ```

#### 集合与映射操作

- 支持 map 取值表达式，如：`Users[username]`
- 支持判断 key 是否存在：`username ∈ Users`

### 类型解析与校验机制

在用户输入初始变量或参数值时，系统调用统一的类型转换函数 `parseAndValidateValue(...)` 对每个值进行解析并强制校验：

```java
if (expectedType instanceof PrimitiveSOFLType) {
    return Integer.parseInt(rawInput); // 示例：int
}
if (expectedType instanceof MapSOFLType) {
    Map<?, ?> map = objectMapper.readValue(rawInput, Map.class);
    // 遍历每个 key/value 递归解析类型
}
```

- 若用户输入类型不匹配（如：为 `int` 输入了 `5.5`），将报错中止；
- 若 map/set 中元素类型不匹配，将给出 JSON 结构非法提示；
- 所有交互输入均使用 JSON 语法兼容格式。

### null 值处理与自动修复机制

在运行时，若表达式中使用了未初始化变量（例如 `cart[product_id]` 为 `null`），系统将尝试执行自动补偿：

```java
if (expr.contains("+") && e.getMessage().contains("null")) {
    // 将 null 视为 0，补偿执行
}
```

- 默认行为为：**null + number ⇒ 0 + number**
- 仅在加法表达式中生效，其它运算不做容错
- 该设计符合多数业务建模预期，提升健壮性

### 表达式归一化机制

为保证兼容性和求值安全性，系统在表达式求值前执行标准化处理：

```
∧ → &&
∨ → ||
¬ → !
≥ → >=
≤ → <=
∈ → in
```

实现类：`SOFLExpressionNormalizer`
 该步骤确保 SOFL 风格语法能被 JEXL 识别并正确求值。

### 示例

```
pre username ∈ Users ∧ password == Users[username]
post if quantity > 0 then cart[product_id] = cart[product_id] + quantity
```

- 用户只需使用 SOFL 风格表达式书写；
- 系统自动归一化、校验并执行；
- 最终求值与状态更新均由强类型引擎驱动。

## 路径执行与测试机制

本系统核心目标之一，是根据用户提供的功能场景路径（Functional Scenario Path, 简称 FSP）对 SOFL 模块进行模拟执行，自动推导出中间状态与最终状态，并验证该路径是否合法、可达且符合预期。

### 功能场景路径（FSP）定义

FSP 是一个按顺序排列的 `process` 名称列表，表示系统将依次模拟这些过程的执行：

```
Login → AddToCart → SubmitOrder
```

- 每个 `process` 对应一次状态转移；

- 路径中的过程名必须在当前模块中声明存在；

- 用户通过命令行或界面输入：

  ```
  请输入要执行的路径（用英文逗号分隔 process 名称）: Login, AddToCart
  ```

### 路径执行机制

系统会按路径顺序依次处理每个 `process`：

#### 执行流程（每步）：

1. **参数收集**：询问用户输入该 `process` 所需参数；
2. **前置条件判断**：判断 `pre` 是否满足；
3. **匹配 Functional Scenario**：
   - 遍历所有场景的 guard，取第一个成立的场景（first-match）
   - 若多个 guard 同时成立，仅执行第一个
4. **应用状态更新**：根据 scenario 中的 defines 执行赋值
5. **更新状态表**：写入最新状态，供下一个 `process` 使用

#### 核心代码片段（执行一条路径）：

```java
for (String processName : processPath) {
    SOFLProcess proc = module.getProcessByName(processName);
    Map<String, Object> params = collectParams(proc);
    checkPrecondition(proc, state, params);
    FunctionalScenario fs = findFirstMatchingScenario(proc, state, params);
    applyScenario(fs, state, params);
}
```

### 测试用例组织与设计原则

为保证系统正确性与健壮性，项目提供了多组覆盖常见边界情况的测试用例。

#### 每组测试包含：

- 一个合法 SOFL 模块文本（字符串）
- 一条或多条待验证的路径（FSP）
- 对应的初始状态输入与过程参数
- 系统输出期望：
  - 成功路径 → 正确状态更新
  - 不可达路径 → 前置条件失败 / 无匹配 scenario
  - 类型错误 → 明确报错

#### 覆盖场景示例：

| 测试类型     | 用例内容                               |
| ------------ | -------------------------------------- |
| 单路径验证   | `Login → AddToCart`                    |
| 参数类型错误 | `quantity = "abc"`                     |
| 不可达路径   | 未登录状态执行下单                     |
| Map 键不存在 | `cart[pid] + 1` 时 `cart[pid] == null` |
| 多场景匹配   | 多个 guard 同时成立时是否只选第一个    |

### 不可达路径检测机制

若过程的 `precondition` 不满足，或所有 `guard` 条件都不成立，系统会提示该路径在当前输入下不可达：

```
前置条件不满足: username ∈ Users
No matching scenario for process: SubmitOrder
```

该机制用于捕捉用户测试路径中的逻辑死分支或状态配置错误，有助于调试和形式验证。

### 最终状态输出与验证

执行完路径后，系统自动输出完整的最终状态变量：

```
最终状态: {Users=..., cart={"apple":1}, success=true}
```

- 可用于与期望状态进行自动或人工比对；
- GUI 模式下，支持可视化状态面板实时刷新。

## 使用示例

本章提供一个完整的使用流程示例，展示如何在系统中输入 SOFL 模块、指定路径、输入参数并查看输出结果。示例覆盖了常见的数据类型、过程调用及功能场景激活。

### 示例模块：购物系统

```
module PurchaseSystem

state
  Users: map string → string
  stock: map string → int
  cart: map string → int
  success: bool

process Login(username: string, password: string)
pre username ∈ Users
post if password == Users[username] then success = true else success = false
end_process

process AddToCart(product_id: string, quantity: int)
pre success = true ∧ product_id ∈ stock
post if stock[product_id] ≥ quantity then
  cart[product_id] = cart[product_id] + quantity ∧
  stock[product_id] = stock[product_id] - quantity
else
  cart = cart ∧ stock = stock
end_process

end_module
```

### 控制台执行流程（CLI 模式）

用户在命令行中运行程序后，按照提示输入模块、路径与变量值：

#### 输入 SOFL 模块文本：

```
请输入 SOFL 规范（输入完成后请输入 'END' 结束）:
[粘贴上述模块内容]
END
```

#### 输入执行路径：

```
请输入要执行的路径（用英文逗号分隔 process 名称）: Login, AddToCart
```

#### 输入初始状态与参数：

```
请输入 Users: {"alice":"123456"}
请输入 stock: {"apple": 10}
请输入 cart: {}
请输入 success: false

请输入 username: alice
请输入 password: 123456
请输入 product_id: apple
请输入 quantity: 1
```

### 控制台输出（示例）

```
变量初始化: Users = {alice=123456}
变量初始化: stock = {apple=10}
变量初始化: cart = {}
变量初始化: success = false
🌟 激活场景: password == Users[username]
定义: {success=true}
变量更新: success = true
🌟 激活场景: stock[product_id] ≥ quantity
定义: {cart[product_id]=cart[product_id] + quantity, stock[product_id]=stock[product_id] - quantity}
⚠️ 自动补值: cart[product_id] 为 null，默认视为 0
集合更新: cart[apple] = 1
集合更新: stock[apple] = 9
最终状态: {Users={alice=123456}, stock={apple=9}, cart={apple=1}, success=true}
```

### 图形界面模式（JavaFX）

在 JavaFX 图形界面中：

- 用户可通过文本框粘贴模块内容；
- 系统自动弹出对话框请求参数值；
- 所有变量更新和状态变迁会在下方输出框与状态面板中实时显示；
- 场景激活信息以彩色标注展示；
- 可清晰追踪每一步状态转移，非常适用于教学展示。

#### 界面展示

<img src="Z:\Public\images\image-20250508093854787-1746672074984-160.png" alt="image-20250508093854787" style="zoom:50%;" />

#### 输入

<img src="Z:\Public\images\image-20250508093928777-1746672077910-162.png" alt="image-20250508093928777" style="zoom:50%;" />

#### Process 展示

<img src="Z:\Public\images\image-20250508093955470-1746672084720-164.png" alt="image-20250508093955470" style="zoom:50%;" />

#### 执行路径输入

<img src=".\images\image-20250508101006182.png" alt="image-20250508101006182" style="zoom:50%;" />

#### 变量输入

<img src="Z:\Public\images\image-20250508094108788-1746672086421-166.png" alt="image-20250508094108788" style="zoom:50%;" />

#### 变量状态

<img src="Z:\Public\images\image-20250508101149279-1746672088181-168.png" alt="image-20250508101149279" style="zoom:50%;" />

#### 激活场景

<img src="Z:\Public\images\image-20250508101203239-1746670671466-151-1746672092738-172.png" alt="image-20250508101203239" style="zoom:50%;" />

#### 执行日志

<img src="Z:\Public\images\image-20250508101509341-1746672089734-170.png" alt="image-20250508101509341" style="zoom:50%;" />

#### 不满足前置条件

<img src="Z:\Public\images\image-20250508101310725-1746670643424-147-1746672102141-174.png" alt="image-20250508101310725" style="zoom:50%;" />

### 多路径执行与不可达检测

支持多路径测试，例如：

```
Login, AddToCart, SubmitOrder
```

若未登录直接执行 AddToCart：

```
前置条件不满足: success = true ∧ product_id ∈ stock
```

## 如何运行

本章介绍如何在不同环境中运行本工具，包括命令行交互（CLI 模式）和图形用户界面（JavaFX 模式）两种方式。

### 构建

构建项目：

```bash
mvn clean package
```

或使用 IDE（如 IntelliJ IDEA）直接构建。

### CLI 模式（命令行运行）

适用于希望快速输入并测试 SOFL 模块的用户。

进入生成目录：

```bash
cd target
```

运行 jar 包：

```bash
java --module-path C:\javafx\lib --add-modules javafx.controls,javafx.fxml -cp Functional-Scenario-Path-Tool-1.0.jar shuhuai.functionalscenariopathtool.Main cli  
```

### GUI 模式（JavaFX 界面运行）

适用于教学演示和交互可视化需求。

你可将打包好的项目用 JavaFX 启动类运行，例如：

```bash
java --module-path <path_to_javafx_lib> --add-modules javafx.controls,javafx.fxml -cp Functional-Scenario-Path-Tool-1.0.jar shuhuai.functionalscenariopathtool.Main 
```
