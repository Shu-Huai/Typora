# Response

1. 对于测试用例中的 `username ∈ Users`，这里不符合 SOFL 形式化语言的语法。

   感谢您的指出。在此处，应该是 `username ∈ dom Users`。我们修改了测试用例，并修改了相应的表达式到 Java 语句的解析逻辑。

   我们将 `A ∈ B` 的解析保持不变，解析为 `B.contains(A)`。这将用于集合（set）的运算。

   对于 `A ↦ B ∈ C`，我们解析为 `C.entrySet().contains(pair(A, B))`，其中，`pair(A, B)` 是我们新增的一个静态方法，用于构造键值对：

   ```java
   public static Map.Entry<Object, Object> pair(Object k, Object v) {
       return new AbstractMap.SimpleEntry<>(k, v);
   }
   ```

   该方法已在表达式求值引擎（JEXL）中注册，并可在表达式中直接使用。

   我们在解析过程中做了必要的类型校验，确保 `C` 为 `Map<K, V>` 类型，并保证 `A` 与 `K`、`B` 与 `V` 类型一致。

   我们新增了对 `dom` 和 `ran` 的解析支持。其中，`dom` 表示映射中所有键的集合，`ran` 表示映射中所有值的集合。我们将 `dom M` 解析为 `M.keySet()`，并支持表达式如 `x ∈ dom M` 被转换为 `M.keySet().contains(x)`。`ran M` 被解析为 `M.values()`，并支持表达式如 `x ∈ ran M` 被转换为 `M.values().contains(x)`。

   这项修改将对系统的其他功能保持不变。

2. JEXL 执行引擎能否处理集合的运算（交、并）？

   感谢您的提问。JEXL 是Java 表达式求值的一个引擎，实现的功能是执行一个合法的 Java 表达式语句，对于不能写为一个表达式的复杂语句，需要自定义一个函数，并将该函数注册到 JEXL 执行引擎中。对于集合的交和并的操作，在 Java 的基础 API 中并没有对其的简单实现，我们需要自定义一个函数，例如

   ```java
   public static <T> Set<T> union(Set<T> a, Set<T> b) {
       Set<T> result = new HashSet<>(a);
       result.addAll(b);
       return result;
   }
   ```

   这实现了集合的并运算。

   因此，我们的程序能够实现诸如 `x ∈ A ∩ B`、`x ∈ dom A ∪ dom B` 等 SOFL 表达式。

3. 