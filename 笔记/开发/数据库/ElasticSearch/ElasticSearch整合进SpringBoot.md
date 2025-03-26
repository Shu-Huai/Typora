# ElasticSearch 整合进 SpringBoot

官方有两个整合方式，一种是Spring封装的，一种是原生的（官方推荐)，本人工作时用的也是原生的，原因是spring封装的使用起来有点局限性，反正我认为不好用。本文就以原生引入方式整合Elasticsearch。

## 原生方式

### maven 导入

```xml
 <dependency>
    <groupId>org.elasticsearch.client</groupId>
    <artifactId>elasticsearch-rest-client</artifactId>
    <version>7.10.1</version>
</dependency>
<dependency>
    <groupId>org.elasticsearch.client</groupId>
    <artifactId>elasticsearch-rest-high-level-client</artifactId>
    <version>7.10.1</version>
</dependency>
<dependency>
    <groupId>org.elasticsearch</groupId>
    <artifactId>elasticsearch</artifactId>
    <version>7.10.1</version>
</dependency>
```

### 编写 application.yml 文件配置 ES

ip 和端口号根据自己而定

```yaml
elasticsearch:
  host: xxxx
  port: 9200
  scheme: http
```

### 编写一个 ES 的配置类进行配置 ES 客户端

#### EsProperties 映射类

用处是读取上述的配置文件映射

```java
@ConfigurationProperties(prefix = "elasticsearch")
@Component
@Data
public class EsProperties {
    private String host;
    private Integer port;
    private String scheme;
}
@Configuration
public class EsConfig {
    @Autowired
    private EsProperties esProperties;

    @Bean
    public RestHighLevelClient restHighLevelClient(){
        RestClientBuilder builder = RestClient.builder(
            new HttpHost(esProperties.getHost(),
                esProperties.getPort(), esProperties.getScheme()));
        System.out.println(esProperties);
        return new RestHighLevelClient(builder);
     
    }

}
```

以上操作完成后基本框架基本完成

现在就测试一下结果。

### 使用

首先我的 Es 中已经有了下图的索引（可视化工具为 Kibana 有兴趣的可以去网上搜搜，我就不教怎么部署它了)

![img](http://public.file.lvshuhuai.cn/images\1a02a4367d5649caa472a7393037b957.png)

接着在 idea 上新建实体类来映射上图字段，如下图。

```java
@Data
public class User implements Serializable {
    private Long id;
    private String username;
    private String phone;
    private String headUrl;
    private Long deptId;
    private String description;
    private  String status;
    private  String createTime;
    private Long isDeleted;
    private String sex;
    private String email;
}
```

这样基本条件已经满足，现在写一个 http 接口去验证。这是我测试的案例，完全可以按着你们来，

核心代码就是 RestHignLevelClient 的调用

```java
@RestController
@Slf4j
public class NacosProviderController {
    @Autowired
    private RestHighLevelClient restHighLevelClient;
    @GetMapping("/hello1/test")
    public String testNacosHello(@RequestParam(defaultValue = "我是生者") String value) throws IOException {
        String port = "8090";
        SearchRequest request = new SearchRequest();
        //设置索引
        request.indices("smart_water_user");
        //封装查询条件
        request.source(new SearchSourceBuilder().query(QueryBuilders.matchAllQuery()));
        //执行
        SearchResponse response = restHighLevelClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();
        for (SearchHit hit : hits) {
            User user = JSON.parseObject(hit.getSourceAsString(), User.class);
            System.out.println(user);
        }
        System.out.println();
        return value+"+"+port;
    }

}
```

值得注意的一点因为 es 存储的数据是 json 形式的，所以需要采用 JsonObject，Json，Gson，ObjectMapper 等json 解析工具进行 java 对象的转换。当 Java 类没有 Es 内存储的数据映射不一致（字段多或少）可能会出现 json 解析异常，具体得看使用的是哪个 json 解析工具。下图使用的 json 解析不会出现这种错误，我工作的时候确实出现了。 

触发接口，已经响应成功，并且没有报错。看看控制台是否输出了结果。

![img](http://public.file.lvshuhuai.cn/images\df5a348e336644ceaca46c512a42a22c.png)

 很明显已经查出了结果并且输出了

![img](http://public.file.lvshuhuai.cn/images\68d7fa4197a2463c900a5fcb73360b1b.png)

上述案例只是查询该索引的所有数据，更多 crud 请自行查找，但是基本逃不开上述测试的步骤（设置索引，封装查询，调用 search 方法。


