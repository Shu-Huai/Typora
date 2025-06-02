# Response to Comments

We would like to thank you for your valuable comments, which have been taken into account in the revision.

The major modifications of this version are listed below.

1. We have corrected the syntax errors in our case study and updated the corresponding code implementation to reflect these changes.
2. We have added the ability of handling output variables and utilizes them to verify the validity of Functional Scenario Paths.
3. We have added support for user-defined (custom) types in the parser and execution engine.

We respond to the comments point by point in the following.

## Response to the Comments

1. Regarding the test case `username ∈ Users`, this does not conform to the syntax of the SOFL formal language.

    Thank you for pointing this out. The correct expression should be `username ∈ dom Users`. We have revised the test case and updated the corresponding Java parsing logic accordingly.

    We retain the parsing of expressions like `A ∈ B` as `B.contains(A)`, which is suitable for set operations.

    For expressions such as `A ↦ B ∈ C`, we parse them as `C.entrySet().contains(pair(A, B))`, where `pair(A, B)` is a newly added static method that constructs a key-value pair:

    ```java
    public static Map.Entry<Object, Object> pair(Object k, Object v) {
        return new AbstractMap.SimpleEntry<>(k, v);
    }
    ```

    This method is registered in the expression evaluation engine (JEXL) and can be directly used in expressions.

    We also perform necessary type checks during parsing to ensure that `C` is of type `Map<K, V>`, and that `A` and `B` are of compatible types with `K` and `V` respectively.

    Additionally, we add parsing support for `dom` and `ran`. Specifically, `dom M` is parsed as `M.keySet()`, supporting expressions like `x ∈ dom M`, which is transformed into `M.keySet().contains(x)`. Similarly, `ran M` is parsed as `M.values()`, supporting expressions like `x ∈ ran M` as `M.values().contains(x)`.

    These enhancements do not affect the functionality of other parts of the system.

2. Can the JEXL execution engine handle set operations such as intersection and union?

    Thank you for your question. JEXL is a Java-based expression engine that evaluates valid Java expressions. For more complex logic that cannot be written as a simple expression, the developers need to provide custom functions and register them with the JEXL engine. 

    For example, for set union operations, we define:

    ```java
    public static <T> Set<T> union(Set<T> a, Set<T> b) {
        Set<T> result = new HashSet<>(a);
        result.addAll(b);
        return result;
    }
    ```

    This allows us to handle SOFL expressions like `x ∈ A ∩ B` or `x ∈ dom A ∪ dom B`. For the former, our program converted it into `intersect(A, B).contains(x)` and the latter is converted into `union(A.keySet(), B.keySet()).contains(x)`. These results are then pass to JEXL to execute.

3. Lack of Process outputs.

    Thank you for this valuable comment. We have revisited the definitions of Process in SOFL specification. In SOFL, a Process may include one or more output variables.

    In our project, verifying the validity of a Functional Scenario Path (FSP) involves two levels:

    1. Ensuring that the output of the Process to which the former Functional Scenario belongs and the input of the Process to which the latter Functional Scenario belongs are connectable to the inputs of the subsequent Process.
    2. Dynamically validating that the process can be executed based on the initialized and input variables during runtime.

    Moreover, the concept of the data store and a Process’s output variables is quite different. They should be explicitly separated. For example, in our test case, the `success` variable in the `Login` process should be treated as an output rather than part of the data store.

    In our previous program, we incorrectly ignored the first level of legality and incorrectly confused data stores with output variables. In this revised version, we add the ability to parse and handle the output variables of the Process. Also, we have added code to determine the legitimacy of the Functional Scenario Path at the first level.

    Specifically, we parsed and extracted the output variables from a Process block and saved them. Before program execution, we obtain the output of each Functional Scenario in the given Functional Scenario Path and try to find the output of the Process to which it belongs. After that, we try to check whether at least one of the output variables of the previous Functional Scenario is the same as the input variable of the following Functional Scenario between two neighboring Functional Scenarios on this path. With these check, we ensure the connectivity of the data flow, thus verifying the legitimacy of the first level. If not, an error will be reported.

    <img src="http://public.file.lvshuhuai.cn/images\fe5be2a6c99856af074aea2f29a40733.png" alt="fe5be2a6c99856af074aea2f29a40733" style="zoom:50%;" />

    We have also redesigned the way variables and input are initialized and assigned, and re-factored part of the code so that it can correctly distinguish between data storage and output, and more accurately support the execution logic of the whole process.

    In addition, we added a new area on GUl to show the values of the output variables of each Functional Scenario in the form of a table during the execution of the program.

    After the modification, our test cases are:

    ```
    module PurchaseSystem
    type:
      User = string
      Response = "ok" | "not enough" | "password wrong"
    state
      Users: map User → string
      stock: map string → int
      cart: map string → int
    
    process Login(username: User, password: string)
    success: bool, res: Response
    pre username ∈ dom Users 
    post
      if password == Users[username] then
        success = true ∧ res = "ok"
      if password ≠ Users[username] then
        success = false ∧ res = "password wrong"
    end_process
    
    process AddToCart(success: bool, product_id: string, quantity: int)
    res: Response, success: bool
    pre success = true ∧ product_id ∈ dom stock 
    post
      if stock[product_id] ≥ quantity then
        cart[product_id] = cart[product_id] + quantity ∧
        stock[product_id] = stock[product_id] - quantity ∧ 
        res = "ok"
      if stock[product_id] < quantity then
        cart = cart ∧ stock = stock ∧ 
        res = "not enough"
    end_process
    
    end_module
    ```

4. Can your program handle custom types?

    Thank you for your question. We enhanced our program by adding the ability to handle custom types. In addition to basic data types such as string, int, float, char, boolean, etc., our program also supports compound types including enumeration, map, set and tuple. Among them, the input format of enumeration is like `“Ok” | “Invalid input” | “User not exist”`, the input format of map is like `Users: map User → string`, the type of set is like `Days: set of int`, and the type of tuple is like `Date: int * int * int`. 

    In this revised version, our program supports custom types. For example, if we define a type User as: `User = string`, our program can correctly recognize and handle such type definitions. We implement this by collecting these type definitions uniformly when parsing the SOFL specification, and automatically recognizing and replacing them with the corresponding real types when parsing variables, parameters, and expressions.

    However, it is important to note that our handling of custom types currently only supports the basic and compound types mentioned above, and does not support complex types starting with `composed of` temporarily. We will add support for this in a later improved version.

5.  Your program does not support direct input of Functional Scenario?

    Thank you for your question. Yes, our program does not support direct input of Functional Scenarios, our program takes as input a simplified SOFL specification from which it extracts information about variables (name and type), processes, Functional Scenarios (represented by if-then expressions in post conditions), etc. Then the user specifies the Functional Scenario Path to be executed. For example, an input could be `Login_1,AddToCart_2` in our case study. And the program matches and executes the corresponding Functional Scenario from the parsed SOFL module. By this design, we hope to clearly separate “module definition” and “path execution”, which can help support more complex validation tasks in later stages. Another purpose is to simplify the interaction logic. Users only need to input the module content once, and then they can specify different paths for testing many times, without having to repeat the input.

    We do understand that using `Login_1`, `AddToCart_2` and other Functional Scenario blocks as inputs will bring a more intuitive interaction experience. In a future version we will add a capable parser and update our executor logic to be able to parse and process this kind of input.