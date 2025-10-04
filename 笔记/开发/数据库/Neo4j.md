# Neo4j

Neo4j 是一个世界领先的开源的基于图的数据库。 它是使用Java语言完全开发的。

## 什么是 Neo4j

Neo4j 是一个开源的 NoSQL 图形数据库，2003 年开始开发，使用 scala 和 java 语言，2007 年开始发布。

- 是世界上先进的图数据库之一，提供原生的图数据存储，检索和处理；
- 采用属性图模型（Property graph model），极大的完善和丰富图数据模型；
- 专属查询语言 Cypher，直观，高效；

官网： https://neo4j.com/

### Neo4j 的特性

- SQL 就像简单的查询语言 Neo4j CQL
- 它遵循属性图数据模型
- 它通过使用 Apache Lucence 支持索引
- 它支持 UNIQUE 约束
- 它包含一个用于执行 CQL 命令的 UI：Neo4j 数据浏览器
- 它支持完整的 ACID（原子性，一致性，隔离性和持久性）规则
- 它采用原生图形库与本地 GPE（图形处理引擎）
- 它支持查询的数据导出到 JSON 和 XLS 格式
- 它提供了 REST API，可以被任何编程语言（如 Java，Spring，Scala 等）访问
- 它提供了可以通过任何 UI MVC 框架（如 Node JS）访问的 Java 脚本
- 它支持两种 Java API：Cypher API 和 Native Java API 来开发 Java 应用程序

### Neo4j 的优点

- 它很容易表示连接的数据
- 检索/遍历/导航更多的连接数据是非常容易和快速的
- 非常容易地表示半结构化数据
- Neo4j CQL 查询语句命令是人性化的可读格式，非常容易学习
- 使用简单而强大的数据模型
- 不需要复杂的连接来检索连接的/相关的数据，因为它很容易检索它的相邻节点或关系细节没有连接或索引

## Neo4j 数据模型

### 图论基础

图是一组节点和连接这些节点的关系，图形以属性的形式将数据存储在节点和关系中，属性是用于表示数据的键值对。

在图论中，我们可以表示一个带有圆的节点，节点之间的关系用一个箭头标记表示。

简单的可能图是单个节点：

<img src="http://public.file.lvshuhuai.cn/images\image-20240122173513650.png" alt="image-20240122173513650" style="zoom:67%;" />

我们可以使用节点表示社交网络（如 Google+（GooglePlus）个人资料），它不包含任何属性。向 Google+ 个人资料添加一些属性：

<img src="http://public.file.lvshuhuai.cn/images\image-20240122173535513.png" alt="image-20240122173535513" style="zoom:50%;" />

在两个节点之间建立关系：

<img src="http://public.file.lvshuhuai.cn/images\image-20240122173558022.png" alt="image-20240122173558022" style="zoom:50%;" />

此处在两个配置文件之间创建关系名称“跟随”。 这意味着 Profile 1 跟随 Profile 2。

### 属性图模型

Neo4j 图数据库遵循属性图模型来存储和管理其数据。

属性图模型规则

- 表示节点，关系和属性中的数据
- 节点和关系都包含属性
- 关系连接节点
- 属性是键值对
- 节点用圆圈表示，关系用方向键表示。
- 关系具有方向：单向和双向。
- 每个关系包含“开始节点”或“从节点”和“到节点”或“结束节点”

 在属性图数据模型中，关系应该是定向的。如果我们尝试创建没有方向的关系，那么它将抛出一个错误消息。在 Neo4j 中，关系也应该是有方向性的。如果我们尝试创建没有方向的关系，那么 Neo4j 会抛出一个错误消息，“关系应该是方向性的”。

Neo4j 图数据库将其所有数据存储在节点和关系中，我们不需要任何额外的 RDBMS 数据库或 NoSQL 数据库来存储 Neo4j 数据库数据，它以图的形式存储数据。Neo4j 使用本机 GPE（图形处理引擎）来使用它的本机图存储格式。

图数据库数据模型的主要构建模块是：

- 节点
- 关系
- 属性

简单的属性图的例子：

<img src="http://public.file.lvshuhuai.cn/images\image-20240122174024062.png" alt="image-20240122174024062" style="zoom:50%;" />

这里我们使用圆圈表示节点。 使用箭头表示关系，关系是有方向性的。 我们可以用 Properties（键值对）来表示 Node 的数据。 在这个例子中，我们在 Node 的 Circle 中表示了每个 Node 的 Id 属性。

### Neo4j 的构建元素

Neo4j 图数据库主要有以下构建元素：

- 节点
- 属性
- 关系
- 标签
- 数据浏览器

<img src="http://public.file.lvshuhuai.cn/images\image-20240122174143756.png" alt="image-20240122174143756" style="zoom: 67%;" />

#### 节点

节点（Node）是图数据库中的一个基本元素，用来表示一个实体记录，就像关系数据库中的一条记录一 样。在 Neo4j 中节点可以包含多个属性（Property）和多个标签（Label）。

- 节点是主要的数据元素
- 节点通过**关系**连接到其他节点
- 节点可以具有一个或多个**属性**（即，存储为键/值对的属性）
- 节点有一个或多个**标签**，用于描述其在图表中的作用

#### 属性

属性（Property）是用于描述图节点和关系的键值对。其中 Key 是一个字符串，值可以通过使用任何 Neo4j 数据类型来表示

- 属性是命名值，其中名称（或键）是字符串
- 属性可以被索引和约束
- 可以从多个属性创建复合索引

#### 关系

关系（Relationship）同样是图数据库的基本元素。当数据库中已经存在节点后，需要将节点连接起来 构成图。关系就是用来连接两个节点，关系也称为图论的边（Edge）,其始端和末端都必须是节点，关系不 能指向空也不能从空发起。关系和节点一样可以包含多个属性，但关系只能有一个类型（Type）。

- 关系连接两个节点
- 关系是方向性的
- **节点**可以有多个甚至递归的关系
- 关系可以有一个或多个属性（即存储为键/值对的属性）

基于方向性，Neo4j 关系被分为两种主要类型：

- 单向关系
- 双向关系

#### 标签

标签（Label）将一个公共名称与一组节点或关系相关联， 节点或关系可以包含一个或多个标签。 我们 可以为现有节点或关系创建新标签， 我们可以从现有节点或关系中删除标签。

- 标签用于将**节点**分组
- 一个节点可以具有多个标签
- 对标签进行索引以加速在图中查找节点

- 本机标签索引针对速度进行了优化

## 使用场景

### 欺诈检测

![image-20240122180025445](http://public.file.lvshuhuai.cn/images\image-20240122180025445.png)

### 实时推荐引擎

![image-20240122180002885](http://public.file.lvshuhuai.cn/images\image-20240122180002885.png)

## Neo4j 安装

> 需要依赖 JDK，请提前安装

知识图谱的底层依赖于关键的图数据库，在这里我们选择 Neo4j，它是一款高性能的 NoSQL 图形数据库，能够将结构化的数据存储在**图**而不是**表**中。

### Neo4j 下载

地址：[Neo4j Deployment Center - Graph Database & Analytics](https://neo4j.com/deployment-center/)

<img src="http://public.file.lvshuhuai.cn/images\c20e6434e85b45eed767a7080446d463.png" alt="img" style="zoom: 67%;" />

### Neo4j 解压

解压到自定义英文文件夹

### Neo4j 配置

1. 右键此电脑👉高级系统设置👉环境变量
2. 点击系统变量区的 Path，点击编辑，然后新建 `Neo4j\bin`
3. 确定，退出，OK

### Neo4j 运行 

1. 打开终端
2. `neo4j console`

<img src="http://public.file.lvshuhuai.cn/images\d07513eb646dc701bbea646ab5f3bf0a.png" alt="img" style="zoom: 67%;" />


底部显示 Started，说明配置成功 

### Neo4j 使用 

1. 浏览器输入网址 http://localhost:7474/
2. 登录用户名密码：默认均为 `neo4j`
3. 更改密码

<img src="http://public.file.lvshuhuai.cn/images\039f218e5bb9ddc446c9186df737ab45.png" alt="img" style="zoom:67%;" />

## 简单 CQL 入门

就像我们平常使用关系型数据库中的 SQL 语句一样，Neo4j 中可以使用 Cypher 查询语言（CQL）进行图形数据库的查询，我们简单来看一下增删改查的用法。

### 添加节点

在 CQL 中，可以通过 `CREATE` 命令去创建一个节点，创建不含有属性节点的语法如下：

```CQL
CREATE (<node-name>:<label-name>)
```

在 `CREATE` 语句中，包含两个基础元素，节点名称 `node-name` 和标签名称 `lable-name`。标签名称相当于关系型数据库中的表名，而节点名称则代指这一条数据。

以下面的 `CREATE` 语句为例，就相当于在 `Person` 这张表中创建一条没有属性的空数据。

```CQL
CREATE (索尔:Person)
```

而创建包含属性的节点时，可以在标签名称后面追加一个描绘属性的 `json` 字符串：

```CQL
CREATE (
   <node-name>:<label-name>
   {    
      <key1>:<value1>,
      …
      <keyN>:<valueN>
   }
)
```

用下面的语句创建一个包含属性的节点：

```CQL
CREATE (洛基:Person {name:"洛基",title:"诡计之神"})
```

### 查询节点

在创建完节点后，我们就可以使用 `MATCH` 匹配命令查询已存在的节点及属性的数据，命令的格式如下：

```CQL
MATCH (<node-name>:<label-name>)
```

通常，`MATCH` 命令在后面配合 `RETURN`、`DELETE` 等命令使用，执行具体的返回或删除等操作。

执行下面的命令：

```CQL
MATCH (p:Person) RETURN p
```

查看可视化的显示结果：

<img src="http://public.file.lvshuhuai.cn/images\f6e2daf2700de692dbae40d13bc20377.png" alt="img" style="zoom:67%;" />

可以看到上面添加的两个节点，分别是不包含属性的空节点和包含属性的节点，并且所有节点会有一个默认生成的 `id` 作为唯一标识。

### 删除节点

接下来，我们删除之前创建的不包含属性的无用节点，上面提到过，需要使用 `MATCH` 配合 `DELETE` 进行删除。

```cql
MATCH (p:Person) WHERE id(p)=100 
DELETE p
```

在这条删除语句中，额外使用了 `WHERE` 过滤条件，它与SQL中的 `WHERE` 非常相似，命令中通过节点的 `id` 进行了过滤。

删除完成后，再次执行查询操作，可以看到只保留了`洛基`这一个节点：

![img](http://public.file.lvshuhuai.cn/images\a6d464425d73b97426d790f6c53e2f8b.png)

### 添加关联

在 Neo4j 图数据库中，遵循属性图模型来存储和管理数据，也就是说我们可以维护节点之间的关系。

在上面，我们创建过一个节点，所以还需要再创建一个节点作为关系的两端：

```cql
CREATE (p:Person {name:"索尔",title:"雷神"})
```

创建关系的基本语法如下：

```cql
CREATE (<node-name1>:<label-name1>) 
- [<relation-name>:<relation-label-name>]
-> (<node-name2>:<label-name2>)
```

当然，也可以利用已经存在的节点创建关系，下面我们借助 `MATCH` 先进行查询，再将结果进行关联，创建两个节点之间的关联关系：

```cql
MATCH (m:Person),(n:Person) 
WHERE m.name='索尔' and n.name='洛基' 
CREATE (m)-[r:BROTHER {relation:"无血缘兄弟"}]->(n)
RETURN r
```

添加完成后，可以通过关系查询符合条件的节点及关系：

```cql
MATCH (m:Person)-[re:BROTHER]->(n:Person) 
RETURN m,re,n
```

可以看到两者之间已经添加了关联：

<img src="http://public.file.lvshuhuai.cn/images\74b81a408c4c88442eb11145b86fe6f8.png" alt="img" style="zoom:67%;" />

需要注意的是，如果节点被添加了关联关系后，单纯删除节点的话会报错，：

```xml
Neo.ClientError.Schema.ConstraintValidationFailed
Cannot delete node<85>, because it still has relationships. To delete this node, you must first delete its relationships.
```

这时，需要在删除节点时同时删除关联关系：

```CQL
MATCH (m:Person)-[r:BROTHER]->(n:Person) 
DELETE m,r
```

执行上面的语句，就会在删除节点的同时，删除它所包含的关联关系了。

那么，简单的 CQL 语句入门到此为止，它已经基本能够满足我们的简单业务场景了，下面我们开始在 SpringBoot 中整合 Neo4j。

## 整合 Neo4j

创建一个 SpringBoot 项目，这里使用的是 `2.3.4` 版本，引入 Neo4j 的依赖坐标：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-neo4j</artifactId>
</dependency>
```

在 `application.yml` 中配置 Neo4j 连接信息：

```yml
spring:
  data:
    neo4j:
      uri: bolt://127.0.0.1:7687
      username: neo4j
      password: 123456
```

大家如果对 `jpa` 的应用非常熟练的话，那么接下来的过程可以说是轻车熟路，因为它们基本上是一个模式，同样是构建 model 层、repository 层，然后在此基础上操作自定义或模板方法就可以了。

### 节点实体

我们可以使用基于注解的实体映射来描述图中的节点，通过在实体类上添加 `@NodeEntity` 表明它是图中的一个节点实体，在属性上添加 `@Property` 代表它是节点中的具体属性。

```java
@Data
@NodeEntity(label = "Person")
public class Node {
    @Id
    @GeneratedValue
    private Long id;

    @Property(name = "name")
    private String name;

    @Property(name = "title")
    private String title;
}
```

这样一个实体类，就代表它创建的实例节点的 `<label-name>` 为 `Person`，并且每个节点拥有 `name` 和 `title` 两个属性。

### Repository 持久层

对上面的实体构建持久层接口，继承 `Neo4jRepository` 接口，并在接口上添加 `@Repository` 注解即可。

```java
@Repository
public interface NodeRepository extends Neo4jRepository<Node,Long> {
    @Query("MATCH p=(n:Person) RETURN p")
    List<Node> selectAll();

    @Query("MATCH(p:Person{name:{name}}) return p")
    Node findByName(String name);
}
```

在接口中添加了个两个方法，供后面测试使用，`selectAll()` 用于返回全部数据，`findByName()` 用于根据 `name` 查询特定的节点。

接下来，在 service 层中调用 repository 层的模板方法：

```java
@Service
@AllArgsConstructor
public class NodeServiceImpl implements NodeService {
    private final NodeRepository nodeRepository;
    
    @Override
    public Node save(Node node) {
        Node save = nodeRepository.save(node);
        return save;
    }
}
```

前端调用 `save()` 接口，添加一个节点后，再到控制台用查询语句进行查询，可以看到新的节点已经通过接口方式被添加到了图中：

<img src="http://public.file.lvshuhuai.cn/images\770f0b657a6f62a7a68fa98e53d49ae0.png" alt="img" style="zoom:67%;" />

在 service 中再添加一个方法，用于查询全部节点，直接调用我们在 `NodeRepository` 中定义的 `selectAll()` 方法：

```java
@Override
public List<Node> getAll() {
    List<Node> nodes = nodeRepository.selectAll();
    nodes.forEach(System.out::println);
    return nodes;
}
```

在控制台打印了查询结果：

![img](http://public.file.lvshuhuai.cn/images\34047c118ac1bc3cef1722291449789c.png)

对节点的操作我们就介绍到这里，接下来开始构建节点间的关联关系。

### 关联关系

在 Neo4j 中，关联关系其实也可以看做一种特殊的实体，所以可以用实体类来对其进行描述。与节点不同，需要在类上添加 `@RelationshipEntity` 注解，并通过 `@StartNode` 和 `@EndNode` 指定关联关系的开始和结束节点。

```java
@Data
@RelationshipEntity(type = "Relation")
public class Relation {
    @Id
    @GeneratedValue
    private Long id;

    @StartNode
    private Node startNode;

    @EndNode
    private Node endNode;

    @Property
    private String relation;
}
```

同样，接下来也为它创建一个持久层的接口：

```java
@Repository
public interface RelationRepository extends Neo4jRepository<Relation,Long> {
    @Query("MATCH p=(n:Person)-[r:Relation]->(m:Person) " +
            "WHERE id(n)={startNode} and id(m)={endNode} and r.relation={relation}" +
            "RETURN p")
    List<Relation> findRelation(@Param("startNode") Node startNode,
                                @Param("endNode") Node endNode,
                                @Param("relation") String relation);
}
```

在接口中自定义了一个根据起始节点、结束节点以及关联内容查询关联关系的方法，我们会在后面用到。

### 创建关联

在 service 层中，创建提供一个根据节点名称构建关联关系的方法：

```java
@Override
public void bind(String name1, String name2, String relationName) {
    Node start = nodeRepository.findByName(name1);
    Node end = nodeRepository.findByName(name2);

    Relation relation =new Relation();
    relation.setStartNode(start);
    relation.setEndNode(end);
    relation.setRelation(relationName);
    
    relationRepository.save(relation);
}
```

通过接口调用这个方法，绑定`海拉`和`索尔`之间的关系后，查询结果：

<img src="http://public.file.lvshuhuai.cn/images\b83a3b769d1077416609a0e76ee5a7e2.png" alt="img" style="zoom:67%;" />

## 文本 SPO 抽取

在项目中构建知识图谱时，很大一部分场景是基于非结构化的数据，而不是由我们手动输入确定图谱中的节点或关系。因此，我们需要基于文本进行知识抽取的能力，简单来说就是要在一段文本中抽取出 SPO 主谓宾三元组，来构成图谱中的点和边。

这里我们借助 GitHub 上一个现成的工具类，来进行文本的语义分析和 SPO 三元组的抽取工作，项目地址：

> https://github.com/hankcs/MainPartExtractor

这个项目虽然比较简单一共就两个类两个资源文件，但其中的工具类却能够有效帮助我们完成句子中的主谓宾的提取，使用它前需要先引入依赖的坐标：

```xml
<dependency>
    <groupId>com.hankcs</groupId>
    <artifactId>hanlp</artifactId>
    <version>portable-1.2.4</version>
</dependency>
<dependency>
    <groupId>edu.stanford.nlp</groupId>
    <artifactId>stanford-parser</artifactId>
    <version>3.3.1</version>
</dependency>
```

然后把这个项目中 `com.hankcs.nlp.lex` 包下的两个类拷到我们的项目中，把 `resources` 下的 `models` 目录拷贝到我们的 `resources` 下。

完成上面的步骤后，调用 `MainPartExtractor` 工具类中的方法，进行一下简单的文本 SPO 抽取测试：

```java
public void mpTest(){
    String[] testCaseArray = {
            "我一直很喜欢你",
            "你被我喜欢",
            "美丽又善良的你被卑微的我深深的喜欢着……",
            "小米公司主要生产智能手机",
            "他送给了我一份礼物",
            "这类算法在有限的一段时间内终止",
            "如果大海能够带走我的哀愁",
            "天青色等烟雨，而我在等你",
            "我昨天看见了一个非常可爱的小孩"
    };
    for (String testCase : testCaseArray) {
        MainPart mp = MainPartExtractor.getMainPart(testCase);
        System.out.printf("%s   %s   %s \n",
                GraphUtil.getNodeValue(mp.getSubject()),
                GraphUtil.getNodeValue(mp.getPredicate()),
                GraphUtil.getNodeValue(mp.getObject()));
    }
}
```

在处理结果 `MainPart` 中，比较重要的是其中的 `subject`、`predicate` 和 `object` 三个属性，它们的类型是 `TreeGraphNode`，封装了句子的主谓宾语成分。下面我们看一下测试结果：

![img](http://public.file.lvshuhuai.cn/images\45e17402f41cb563a0efc8c0b3f64eb2.png)

可以看到，如果句子中有明确的主谓宾语，那么则会进行抽取。如果某一项为空，则该项为 `null`，其余句子结构也能够正常抽取。

## 动态构建知识图谱

在上面的基础上，我们就可以在项目中动态构建知识图谱了，新建一个 `TextAnalysisServiceImpl`，其中实现两个关键方法。

首先是根据句子中抽取的主语或宾语在neo4j中创建节点的方法，这里根据节点的 `name` 判断是否为已存在的节点，如果存在则直接返回，不存在则添加：

```java
private Node addNode(TreeGraphNode treeGraphNode){
    String nodeName = GraphUtil.getNodeValue(treeGraphNode);

    Node existNode = nodeRepository.findByName(nodeName);
    if (Objects.nonNull(existNode))
        return existNode;

    Node node =new Node();
    node.setName(nodeName);
    return nodeRepository.save(node);
}
```

然后是核心方法，说白了也很简单，参数传进来一个句子作为文本先进行 SPO 的抽取，对实体进行 `Node` 的保存，再查看是否已经存在同名的关系，如果不存在则创建关联关系，存在的话则不重复创建。下面是关键代码：

```java
@Override
public List<Relation> parseAndBind(String sentence) {
    MainPart mp = MainPartExtractor.getMainPart(sentence);

    TreeGraphNode subject = mp.getSubject();    //主语
    TreeGraphNode predicate = mp.getPredicate();//谓语
    TreeGraphNode object = mp.getObject();      //宾语

    if (Objects.isNull(subject) || Objects.isNull(object))
        return null;

    Node startNode = addNode(subject);
    Node endNode = addNode(object);
    String relationName = GraphUtil.getNodeValue(predicate);//关系词

    List<Relation> oldRelation = relationRepository
            .findRelation(startNode, endNode,relationName);
    if (!oldRelation.isEmpty())
        return oldRelation;

    Relation botRelation=new Relation();
    botRelation.setStartNode(startNode);
    botRelation.setEndNode(endNode);
    botRelation.setRelation(relationName);
    Relation relation = relationRepository.save(botRelation);

    return Arrays.asList(relation);
}
```

创建一个简单的controller接口，用于接收文本：

```java
@GetMapping("parse")
public List<Relation> parse(String sentence) {
    return textAnalysisService.parseAndBind(sentence);
}
```

接下来，我们从前端传入下面几个句子文本进行测试：

```undefined
海拉又被称为死亡女神
死亡女神捏碎了雷神之锤
雷神之锤属于索尔
```

调用完成后，我们再来看看 Neo4j 中的图形关系，可以看到**海拉**、**死亡女神**、**索尔**、**锤**这些实体被关联在了一起：

![img](http://public.file.lvshuhuai.cn/images\725c352a24b1a569445a88ec4c624661.png)

到这里，一个简单的文本处理和图谱创建的流程就被完整的串了起来，但是这个流程还是比较粗糙，之后还需要在下面几个方面继续优化：

- 当前使用的还是单一类型的节点和关联关系，后续可以在代码中丰富更多类型的节点和关联关系实体类
- 文中使用的文本 SPO 抽取效果一般，如果应用于企业项目，那么建议基于更精确的 NLP 算法去做语义分析
- 当前抽取的节点只包含了实体的名称，不包含具体的属性，后续需要继续完善补充实体的属性
- 完善知识融合，主要是添加实体的指代消解以及属性的融合功能