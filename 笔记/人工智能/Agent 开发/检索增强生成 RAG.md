# 检索增强生成 RAG

RAG 是[[大语言模型 LLM]] 应用中最常见、也最容易被误解的一层。很多人第一次接触 RAG 时，会把它理解成“向量数据库 + LLM”，或者以为某个框架、某个知识库产品、某个插件就是 RAG 本身。这种理解会导致后续设计混乱：不知道什么时候该用 [[LangChain4j]]，什么时候该用 [[SpringAI]]，什么时候需要 RAG-Anything，什么时候只是需要一个普通的检索器。

更准确地说，RAG 是一种系统模式。它的核心思想是：**在生成答案之前，先从外部知识源中检索相关上下文，再让 LLM 基于这些上下文回答。**

![RAG Process](http://public.file.lvshuhuai.cn/images\rag-dair-process.png)

它解决的不是“模型不会说话”的问题，而是“模型缺少当前、私有、领域相关、可追溯知识”的问题。普通 LLM 只能依靠参数知识和当前上下文；RAG 则把外部文档、数据库、论文、病例、项目说明、业务知识库接入到回答流程中，让模型带着材料回答。

## 先把名词分层：RAG、RAG 系统、RAG 框架和 Agent 不是一类东西

RAG 相关术语最容易混，是因为它们处在不同抽象层。有的是思想，有的是框架，有的是系统，有的是组件，有的是模型，有的是产品。把这些层次分开之后，后续所有技术选型都会清楚很多。

### RAG 是技术范式，不是具体软件

**RAG，全称 Retrieval-Augmented Generation，检索增强生成。**

它是一种技术范式，可以用一句话定义：

```text
RAG = 在生成答案之前，先从外部知识源中检索相关上下文，
      再把检索结果和用户问题一起交给 LLM 生成答案。
```

所以 RAG 本身不是框架、不是数据库、不是某个产品。它类似一种架构模式：

如果用户问：

```text
我们项目里的 CLAM + Qwen 图文对齐方案为什么不用 instance loss？
```

普通 LLM 如果没有看过你的项目材料，只能猜。RAG 系统则会先从项目文档、论文笔记、实验日志中检索相关片段，例如“当前目标是图文语义向量对齐，而非实例级分类，因此不采用 instance loss”，然后再让 LLM 基于这些片段回答。

这就是 RAG 的本质：**不是让模型凭记忆回答，而是让模型基于检索材料回答。**

![RAG Augmentation](http://public.file.lvshuhuai.cn/images\rag-dair-augmentation.png)

### RAG 系统是工程实现

**RAG 系统 = 把 RAG 这种范式真正实现出来的一套可运行系统。**

一个完整的 RAG 系统通常包括：

- 文档解析器：读取 PDF、Word、Markdown、HTML、PPT、Excel、图片等；
- 文本清洗与切块器：把文档处理成可检索片段；
- Embedding 模型：把文本片段转成向量；
- 向量数据库或向量索引：存储 embedding 并支持相似度检索；
- Retriever：根据用户问题找相关片段；
- Reranker：对初步召回结果重新排序；
- Context Builder：把检索结果拼成适合 LLM 阅读的上下文；
- [[提示词 Prompt]] 模板：约束模型只基于资料回答；
- LLM：根据问题和检索材料生成答案；
- 引用来源模块：返回文件名、页码、chunk 位置；
- 权限控制：保证用户只能检索自己有权限的数据；
- 评估模块：衡量检索召回率、答案忠实性、引用准确性。

因此，“RAG”和“RAG 系统”不是完全一样的概念。可以类比：

```text
推荐算法是一类方法；
抖音推荐系统是一个具体工程系统。

RAG 是一种方法；
企业知识库问答后端、论文助手、病理多模态问答服务，是具体 RAG 系统。
```

### RAG 框架是帮助你搭建 RAG 系统的工具

**RAG 框架 = 帮你实现 RAG 系统的代码框架或库。**

常见选择包括：

- [LangChain](https://docs.langchain.com/oss/python/langchain/rag)；
- [LangChain4j](https://docs.langchain4j.dev/tutorials/rag/)；
- [Spring AI](https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html)；
- [LlamaIndex](https://docs.llamaindex.ai/)；
- Haystack；
- RAG-Anything；
- LightRAG。

它们提供的能力不完全相同。有些偏应用编排，有些偏数据索引，有些偏 Java 生态，有些偏复杂多模态文档处理。

例如：

```text
RAG = 技术范式
LangChain4j / Spring AI / LlamaIndex = RAG 开发框架
你写出来的知识库问答服务 = RAG 系统
```

### RAG 组件是系统中的零件

RAG 组件是组成 RAG 系统的单个模块。常见组件包括：

| 组件 | 作用 |
|---|---|
| Document Loader / Reader | 读取原始文档 |
| Text Splitter / Chunker | 把文档切成片段 |
| Embedding Model | 把文本转成向量 |
| Vector Store | 存储向量并支持相似度搜索 |
| Retriever | 根据问题检索相关内容 |
| Reranker | 对召回结果重新排序 |
| Context Builder | 构造给 LLM 的上下文 |
| Prompt Template | 控制 LLM 回答方式 |
| Chat Model / LLM | 生成最终答案 |
| Citation Builder | 生成来源引用 |

拿 LangChain4j 举例，它里面的 `Document`、`TextSegment`、`EmbeddingModel`、`EmbeddingStore`、`ContentRetriever`、`RetrievalAugmentor` 都是 RAG 组件，而不是完整的 RAG 系统。

### Agent 里的 RAG 通常是一个 Tool

[[智能体 Agent]] 和 RAG 也不是同一类东西。

**Agent 是任务执行模式。RAG 是知识增强模式。**

Agent 关注的是：给定一个任务，模型如何决定下一步该做什么、调用哪个工具、是否继续检索、是否执行数据库查询、是否发送请求、是否需要用户确认。

RAG 关注的是：如何从外部知识源中找相关材料，并让模型基于材料回答。

所以在 Agent 系统里，RAG 经常表现为一个工具：

![RAG Tool Calling Flow](http://public.file.lvshuhuai.cn/images\rag-agent-function-calling-flow.png)

```text
Agent 工具列表：
1. searchKnowledgeBase(question)   # RAG 工具
2. queryDatabase(sql)              # SQL 工具
3. callWeatherApi(city)            # API 工具
4. analyzeImage(imageId)           # 图像分析工具
5. sendEmail(to, body)             # 执行动作工具
```

Agent 不一定每次都调用 RAG。更合理的 Agentic RAG 是：Agent 根据任务判断是否需要检索、检索哪个知识库、是否需要二次检索、是否需要调用其他工具。

## 标准 RAG 的内部结构：从入库到问答

标准 RAG 通常可以拆成两条链路：**离线建库链路**和**在线问答链路**。这两个阶段不要混在一起。

### 离线建库：Indexing Pipeline

离线建库负责把原始文档变成可检索索引。

![LangChain RAG Indexing](http://public.file.lvshuhuai.cn/images\rag-langchain-indexing.png)

典型流程是：

```text
原始文档
  → 文档解析
  → 文本清洗
  → 文档切块
  → 生成 embedding
  → 写入向量库
  → 保存 metadata
```

伪代码如下：

```python
# 1. 加载文档
docs = load_documents("./docs")

# 2. 切块
chunks = split_documents(
    docs,
    chunk_size=500,
    overlap=80,
)

# 3. 生成 embedding 并写入向量库
for chunk in chunks:
    embedding = embedding_model.encode(chunk.text)
    vector_store.add(
        embedding=embedding,
        text=chunk.text,
        metadata={
            "file_id": chunk.file_id,
            "file_name": chunk.file_name,
            "page": chunk.page,
            "chunk_index": chunk.index,
        },
    )
```

这里需要注意：**原始文档不等于可检索文本。** PDF 可能有双栏、脚注、图注、表格、公式；Word 可能有标题层级；PPT 可能有图片和备注；Excel 可能有多个 sheet；扫描件还需要 OCR。文档解析质量很差时，后面的 embedding 和检索再强也很难弥补。

### 在线问答：Retrieval + Generation

在线阶段发生在用户提问时。

![LangChain RAG Retrieval Generation](http://public.file.lvshuhuai.cn/images\rag-langchain-retrieval-generation.png)

典型流程是：

```text
用户问题
  → 问题 embedding
  → 向量库相似度检索
  → 取回 top-k chunks
  → 可选 rerank
  → 构造上下文
  → 拼入 prompt
  → LLM 生成答案
```

伪代码如下：

```python
def rag_answer(question: str) -> str:
    query_embedding = embedding_model.encode(question)

    candidates = vector_store.search(
        embedding=query_embedding,
        top_k=30,
    )

    reranked = reranker.rerank(
        query=question,
        documents=candidates,
        top_k=5,
    )

    context = build_context(reranked)

    prompt = f"""
    你是一个严谨的知识库问答助手。
    请只基于参考资料回答问题。
    如果资料不足，请明确说明“资料不足”。

    【参考资料】
    {context}

    【用户问题】
    {question}
    """

    return llm.generate(prompt)
```

这个流程里，embedding 模型负责“找资料”，LLM 负责“读资料并回答”。两者是不同模块。

### Embedding 模型和 LLM 没有强绑定

RAG 里经常有人问：如果生成模型是 Qwen，embedding 是否必须用 Qwen Embedding？如果用 Qwen Embedding，能不能把检索结果交给 GPT / ChatGPT 回答？

答案是：**标准 RAG 中，embedding 模型和最终 LLM 没有强绑定。**

可以有这些组合：

```text
Qwen LLM + Qwen Embedding
Qwen LLM + BGE Embedding
GPT / ChatGPT LLM + Qwen Embedding
GPT / ChatGPT LLM + OpenAI Embedding
GPT / ChatGPT LLM + Jina / E5 / GTE Embedding
```

关键约束只有一个：

```text
同一个向量索引里，文档 chunk 的 embedding 模型
必须和用户 query 的 embedding 模型一致。
```

不能这样做：

```text
文档 chunk 用 Qwen Embedding 入库；
用户问题用 OpenAI Embedding 查询；
然后直接在同一个向量空间里做相似度搜索。
```

这通常是错误的，因为不同 embedding 模型的向量空间不同，维度也可能不同。pgvector、Qdrant、Milvus 等向量库只知道向量和距离，不知道“语义空间是否兼容”。

正确做法是：

```text
建库：文档 chunk → Qwen Embedding → 向量库
查询：用户问题 → Qwen Embedding → 向量检索 → 取回文本 chunk → GPT / Qwen / Claude 生成答案
```

LLM 最终看到的是文本上下文，而不是 embedding 向量。因此，用 Qwen Embedding 检索，再用 GPT 生成，在标准 RAG 里完全可以。

例外情况是：如果你不是标准 RAG，而是把 embedding 向量直接投影进 LLM 的 hidden space 或作为 soft prompt，例如“aligner embedding → projector → Qwen soft prompt”，那 embedding 分布和 LLM 表示空间就相关了。这属于另一类模型适配问题，不是普通 RAG。

## 框架式 RAG 开发：LangChain4j、Spring AI 与 pgvector

实际开发 RAG 时，一般不从零写所有组件。更常见的做法是：选一个编排框架，接一个 embedding 模型，接一个向量库，然后在业务层设计文件管理、权限、引用和评估。

### 不应该手写哪些东西

通常不应该自己从零实现：

- 向量相似度搜索算法；
- 向量索引结构；
- 基础 embedding 调用封装；
- 基础文档 loader；
- 基础 splitter；
- 基础 retriever；
- 基础 LLM client；
- 基础 RAG 上下文注入逻辑。

这些应该复用框架或基础设施。

![RAG Framework](http://public.file.lvshuhuai.cn/images\rag-dair-framework.png)

但你仍然需要自己写：

- 用户上传文件的业务流程；
- 文件和知识库的数据库表；
- 文档属于哪个用户、项目、知识库；
- chunk metadata 设计；
- 检索时的权限过滤；
- 何时启用 reranker；
- 答案如何展示引用来源；
- 文档更新后如何重建索引；
- Agent 什么时候调用 RAG 工具；
- RAG 的测试集和评估逻辑。

这和 Web 开发类似：你不会自己写一个 Tomcat，但你的用户、订单、权限、业务流程仍然要自己写。

### LangChain4j 中的 RAG 抽象

LangChain4j 是 [[笔记/开发/Java路线/Java|Java]] 生态里的 LLM 应用框架。它可以做 RAG，也可以做[[工具调用 Tool Calling]] 和 Agent 相关编排。对 Java / Spring Boot 开发者来说，它比 [[LangChain]] 更容易嵌入现有后端。

LangChain4j 中常见的 RAG 组件包括：

| 类名 / 概念 | 作用 |
|---|---|
| `Document` | 原始文档抽象 |
| `TextSegment` | 文档切块后的片段 |
| `EmbeddingModel` | 生成 embedding |
| `EmbeddingStore` | 存储 embedding 的向量库抽象 |
| `EmbeddingStoreIngestor` | 文档入库器 |
| `ContentRetriever` | 检索器 |
| `EmbeddingStoreContentRetriever` | 基于向量库的检索器 |
| `RetrievalAugmentor` | 将检索内容注入 LLM 上下文 |
| `AiServices` | 将接口包装成 AI 服务 |

一个最小的 LangChain4j RAG 心智模型是：

```text
建库阶段：
Document → TextSegment → Embedding → EmbeddingStore

问答阶段：
Question → ContentRetriever → RetrievalAugmentor → ChatLanguageModel
```

示例代码如下：

```java
EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

EmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();

List<Document> documents = FileSystemDocumentLoader.loadDocuments(
        Path.of("docs")
);

EmbeddingStoreIngestor ingestor = EmbeddingStoreIngestor.builder()
        .documentSplitter(DocumentSplitters.recursive(500, 100))
        .embeddingModel(embeddingModel)
        .embeddingStore(embeddingStore)
        .build();

// 文档切块、embedding、写入向量库
ingestor.ingest(documents);

ContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
        .embeddingStore(embeddingStore)
        .embeddingModel(embeddingModel)
        .maxResults(5)
        .minScore(0.6)
        .build();

RetrievalAugmentor augmentor = DefaultRetrievalAugmentor.builder()
        .contentRetriever(retriever)
        .build();

Assistant assistant = AiServices.builder(Assistant.class)
        .chatLanguageModel(chatModel)
        .retrievalAugmentor(augmentor)
        .build();

String answer = assistant.chat("这批文档里对 RAG 的定义是什么？");
```

这里 `InMemoryEmbeddingStore` 只适合 demo。正式项目一般会换成 pgvector、Qdrant、Milvus、Elasticsearch、OpenSearch、Redis Vector、Pinecone 等。

### LangChain4j 接 PostgreSQL / pgvector

PostgreSQL 本身是关系数据库。要让它做向量检索，通常使用 [**pgvector**](https://github.com/pgvector/pgvector) 扩展。pgvector 让 PostgreSQL 支持 vector 类型和向量相似度检索。

在 LangChain4j 里接 pgvector，本质上是把：

```java
EmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();
```

替换成：

```java
EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.builder()
        .host("localhost")
        .port(5432)
        .database("ragdb")
        .user("rag")
        .password("rag123456")
        .table("document_embeddings")
        .dimension(embeddingModel.dimension())
        .createTable(true)
        .dropTableFirst(false)
        .build();
```

需要特别注意两个点：

1. `dimension` 必须和 embedding 模型输出维度一致。换 embedding 模型时，表结构或 collection 往往要重建。
2. 正式系统不要设置 `dropTableFirst(true)`，否则服务重启会把知识库索引删掉。

一个最小 smoke test 可以这样写：

```java
EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

EmbeddingStore<TextSegment> embeddingStore = PgVectorEmbeddingStore.builder()
        .host("localhost")
        .port(5432)
        .database("ragdb")
        .user("rag")
        .password("rag123456")
        .table("document_embeddings")
        .dimension(embeddingModel.dimension())
        .createTable(true)
        .dropTableFirst(false)
        .build();

TextSegment segment = TextSegment.from("RAG means Retrieval-Augmented Generation.");
Embedding embedding = embeddingModel.embed(segment).content();
embeddingStore.add(embedding, segment);

Embedding queryEmbedding = embeddingModel.embed("What is RAG?").content();

EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .maxResults(3)
        .build();

List<EmbeddingMatch<TextSegment>> matches = embeddingStore.search(request).matches();

for (EmbeddingMatch<TextSegment> match : matches) {
    System.out.println(match.score());
    System.out.println(match.embedded().text());
}
```

如果这个能跑通，说明 LangChain4j 已经能通过 pgvector 做基础向量检索。

### Spring AI 中的 RAG 抽象

Spring AI 是 Spring 生态中的 AI 应用抽象，适合 Spring Boot 项目。它支持 Chat、Embedding、VectorStore、Advisor、RAG 等能力。

Spring AI 中常见 RAG 组件包括：

| 组件 | 作用 |
|---|---|
| `ChatClient` | 调用 LLM |
| `EmbeddingModel` | 生成文本向量 |
| `VectorStore` | 向量数据库统一接口 |
| `DocumentReader` | 读取文档 |
| `TokenTextSplitter` | 文档切块 |
| `QuestionAnswerAdvisor` | 最简单的 Naive RAG |
| `RetrievalAugmentationAdvisor` | 更模块化的 RAG 架构 |

`QuestionAnswerAdvisor` 是入门最容易理解的形式：用户提问时，它会先查询 `VectorStore`，把相关文档追加到 prompt 中，再交给模型回答。

示例：

```java
@RestController
@RequestMapping("/api/rag")
public class RagController {

    private final ChatClient chatClient;

    public RagController(ChatClient.Builder builder, VectorStore vectorStore) {
        this.chatClient = builder
                .defaultSystem("""
                        你是一个严谨的知识库问答助手。
                        优先基于检索到的上下文回答。
                        如果上下文不足，请明确说明资料不足。
                        不要编造知识库中不存在的内容。
                        """)
                .defaultAdvisors(new QuestionAnswerAdvisor(vectorStore))
                .build();
    }

    @PostMapping("/ask")
    public String ask(@RequestBody AskRequest request) {
        return chatClient.prompt()
                .user(request.question())
                .call()
                .content();
    }

    public record AskRequest(String question) {}
}
```

建库部分可以独立成 Service：

```java
@Service
public class DocumentIngestionService {

    private final VectorStore vectorStore;

    public DocumentIngestionService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    public void ingest(List<Document> documents) {
        TokenTextSplitter splitter = new TokenTextSplitter();
        List<Document> chunks = splitter.apply(documents);
        vectorStore.add(chunks);
    }
}
```

这类代码的重点不在“自己实现 RAG 算法”，而是把 Spring AI 提供的 `VectorStore`、`Advisor`、`ChatClient` 组合成一个 Spring Boot API。

### LangChain4j 和 Spring AI 怎么选

如果只从 Java / Spring Boot 角度看：

| 方案 | 更适合的情况 |
|---|---|
| Spring AI | 已经是 Spring Boot 项目，希望风格与 Spring 生态一致 |
| LangChain4j | 想用 Java 版 LangChain 风格抽象，尤其关注 RAG、Tool、Agent 组件 |
| LlamaIndex / Python LangChain | 更偏 Python 生态、数据处理、研究和快速实验 |
| RAG-Anything | 复杂多模态文档，如 PDF、PPT、表格、公式、图片 |

简单文本知识库不需要 RAG-Anything。普通 Markdown、TXT、简单 PDF，用 Spring AI / LangChain4j + pgvector 就够了。

## Agent 中的 RAG：工具化、服务化与系统边界

当你要做一个 Agent，并且希望它能够查询知识库时，不应该把 RAG 看成“Agent 内部的一堆 prompt”。更清晰的做法是：**把 RAG 封装成一个 Tool 或一个独立服务。**

### Agent 调用 RAG 的基本形态

在 Agent 看来，RAG 可以只是一个函数：

```text
searchKnowledgeBase(knowledgeBaseId, question) -> retrieved evidence / answer
```

它背后可以是：

- LangChain4j 的 `ContentRetriever`；
- Spring AI 的 `VectorStore` + `QuestionAnswerAdvisor`；
- Python LlamaIndex 服务；
- RAG-Anything 多模态文档服务；
- LightRAG Server；
- OpenAI File Search；
- [[扣子 Coze]] / Dify / FastGPT 的知识库接口。

Agent 不需要知道底层怎么切 chunk、怎么建向量索引、怎么 rerank。Agent 只需要知道这个工具能返回与问题相关的知识。

LangChain4j 风格的工具可以这样抽象：

```java
@Component
public class KnowledgeBaseTools {

    private final RagService ragService;

    public KnowledgeBaseTools(RagService ragService) {
        this.ragService = ragService;
    }

    @Tool("Search the knowledge base and return relevant evidence")
    public String searchKnowledgeBase(String knowledgeBaseId, String question) {
        return ragService.search(knowledgeBaseId, question);
    }
}
```

这个 `RagService` 可以是本地 LangChain4j 实现，也可以是 HTTP 调用外部 RAG 服务。

### 本地组件式 RAG 与独立服务式 RAG

在工程上有两种主要形态。

第一种：**本地组件式 RAG**。

```text
Spring Boot
  ├── LangChain4j / Spring AI
  ├── pgvector / Qdrant
  ├── RAG Controller
  └── Agent Tool
```

这种方式适合普通文本知识库。优点是架构简单、服务少、Java 生态统一。缺点是复杂文档解析、多模态处理能力有限。

第二种：**独立服务式 RAG**。

```text
Spring Boot 主系统
  ├── 用户 / 权限 / 文件 / 聊天 / Agent
  └── HTTP 调用 Python RAG 服务
          ├── RAG-Anything / LlamaIndex / LightRAG
          ├── 复杂文档解析
          ├── 多模态索引
          └── 检索问答
```

这种方式适合复杂 PDF、论文、PPT、Excel、图片、表格、公式等场景。优点是可以充分利用 Python 文档处理和多模态生态。缺点是多一个服务，需要处理部署、任务队列、日志、错误恢复和接口协议。

### “手写 FastAPI”不是手写 RAG

如果使用 RAG-Anything 这类 Python 库，并希望 Spring Boot 调用它，通常需要写一层 FastAPI 或 Flask wrapper。这个判断是对的，但要区分：

```text
RAG-Anything 负责：文档解析、多模态处理、索引、检索、问答；
FastAPI 负责：把这些 Python 函数暴露成 HTTP API；
Spring Boot 负责：用户、权限、文件、Agent、业务流程。
```

所以你写 FastAPI，不等于从零实现 RAG。你只是把一个 Python RAG 引擎封装成服务，方便 Java 后端调用。

一个合理的 API 设计如下：

```text
POST /api/rag/index
  输入：knowledgeBaseId, fileId, filePath
  输出：jobId 或索引状态

GET /api/rag/jobs/{jobId}
  输出：PENDING / RUNNING / SUCCESS / FAILED

POST /api/rag/query
  输入：knowledgeBaseId, question, mode, topK
  输出：answer, sources, retrievedContents
```

返回结果不要只有答案，最好包含证据：

```json
{
  "answer": "文档认为 RAG 的核心是先检索外部知识，再让模型基于检索内容生成回答。",
  "sources": [
    {
      "fileId": "file_001",
      "fileName": "rag_note.pdf",
      "page": 3,
      "contentType": "text",
      "snippet": "Retrieval-Augmented Generation first retrieves relevant context..."
    }
  ]
}
```

Spring Boot 侧可以用 `WebClient` 调用：

```java
@Service
public class RagAnythingClient {

    private final WebClient ragWebClient;

    public RagAnythingClient(WebClient ragWebClient) {
        this.ragWebClient = ragWebClient;
    }

    public RagQueryResponse query(String knowledgeBaseId, String question) {
        RagQueryRequest request = new RagQueryRequest(
                knowledgeBaseId,
                question,
                "hybrid"
        );

        return ragWebClient.post()
                .uri("/api/rag/query")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(RagQueryResponse.class)
                .block();
    }
}
```

然后 Agent 只把它当成一个工具。

## 复杂文档与多模态 RAG：RAG-Anything、LightRAG 和 Spring Boot 的配合

普通 RAG 多数围绕文本展开，但现实文档经常包含图片、表格、公式、图表、PPT 布局、扫描件等。这时简单的“PDF 读文本 → chunk → embedding”往往不够。

### RAG-Anything 是什么

[RAG-Anything](https://github.com/HKUDS/RAG-Anything) 是一个 Python 生态的多模态文档 RAG 框架，官方定位是 All-in-One Multimodal Document Processing RAG system，底层建立在 LightRAG 之上。

它重点解决的问题是：传统文本 RAG 很难处理现代复杂文档中的非文本元素，例如：

- 图片；
- 表格；
- 公式；
- 图表；
- 多栏 PDF；
- Office 文档；
- 扫描件；
- 图文之间的语义关系。

它适合处理：

```text
论文 PDF
技术报告
PPT
Excel
包含大量表格和公式的文档
带图表的科研材料
多模态知识库
```

不太适合用它的场景：

```text
纯 Markdown 笔记
普通 FAQ
简单 txt 文档
只需要普通文本问答
必须纯 Java 部署的后端
```

### RAG-Anything 本身不是完整 Agent 框架

RAG-Anything 可以独立做“多模态文档处理 + 检索问答”，但严格说它不是完整 Agent 框架。

Agent 通常还需要：

- 多工具选择；
- 多步任务规划；
- 工具调用循环；
- [[状态管理 State Management]]；
- 错误恢复；
- 人工确认；
- 与数据库、API、文件系统等工具协作。

RAG-Anything 主要提供的是 RAG 引擎能力：处理文档、建立索引、检索和回答。因此在 Agent 系统中，它更适合作为一个外部 RAG Tool，而不是替代 LangChain、LangGraph、LangChain4j 或 Spring Boot。

可以这样理解：

```text
RAG-Anything = 多模态文档 RAG 引擎
LangChain / LangChain4j = Agent / LLM 应用框架
Spring Boot = 业务系统后端
FastAPI = Python 服务接口层
```

### Spring Boot + RAG-Anything 的合理架构

最清晰的架构是：

```text
前端
  ↓
Spring Boot 主系统
  ├── 用户登录 / 权限
  ├── 文件上传
  ├── 知识库管理
  ├── Agent 编排
  ├── 聊天记录
  └── 调用 Python RAG 服务
          ↓
      RAG-Anything 服务
          ├── 文档解析
          ├── 图片 / 表格 / 公式处理
          ├── 多模态索引
          ├── 检索
          └── 返回答案 / 证据
```

Spring Boot 做主业务系统，RAG-Anything 做复杂文档 RAG 引擎。

一个教学版 FastAPI 封装可能类似这样：

```python
from fastapi import FastAPI
from pydantic import BaseModel

from raganything import RAGAnything, RAGAnythingConfig

app = FastAPI()

config = RAGAnythingConfig(
    working_dir="./rag_storage",
    parser="mineru",
    parse_method="auto",
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
)

# 实际项目中需要配置 llm_model_func、vision_model_func、embedding_func
rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    vision_model_func=vision_model_func,
    embedding_func=embedding_func,
)

class IndexRequest(BaseModel):
    knowledge_base_id: str
    file_id: str
    file_path: str

class QueryRequest(BaseModel):
    knowledge_base_id: str
    question: str
    mode: str = "hybrid"

@app.post("/api/rag/index")
async def index_document(req: IndexRequest):
    await rag.process_document_complete(
        file_path=req.file_path,
        output_dir=f"./output/{req.knowledge_base_id}/{req.file_id}",
        parse_method="auto",
    )
    return {"status": "success", "fileId": req.file_id}

@app.post("/api/rag/query")
async def query(req: QueryRequest):
    result = await rag.aquery(
        req.question,
        mode=req.mode,
    )
    return {
        "answer": result,
        "knowledgeBaseId": req.knowledge_base_id,
    }
```

生产环境里，`/index` 不应该同步处理大文件，而应该走异步任务：

```text
上传文件
  → Spring Boot 保存文件和 file 记录
  → 创建 indexing job
  → Python 服务异步解析和建索引
  → 更新 job 状态
  → 用户查询索引状态
```

### LightRAG 与 RAG-Anything 的关系

[LightRAG](https://github.com/HKUDS/LightRAG) 是一个偏检索增强和知识图谱检索的 RAG 框架；RAG-Anything 构建在 LightRAG 之上，用来处理更复杂的多模态文档。LightRAG Server 提供 Web UI 和 API 支持，便于文档索引、知识图谱探索和 RAG 查询。

因此，如果你想要“开箱即用的 API / WebUI RAG 服务”，LightRAG Server 更像完整服务；如果你要复杂文档多模态处理，RAG-Anything 更相关，但通常需要你自己包 API 或等官方服务化能力更成熟。

## 让 RAG 变好用：切块、混合检索、重排序、引用与评估

RAG 能跑起来并不难。难的是让它稳定、准确、可验证、可维护。真正影响效果的通常不是 LLM 有多强，而是检索、上下文构造和评估。

### Chunking：切块决定检索基本单位

最基础的切块是固定长度：

```text
每 300~800 token 一个 chunk
chunk overlap 50~150 token
```

但真实系统不应只依赖固定长度。常见切块策略包括：

- Fixed-size Chunking：固定长度切块；
- Recursive Chunking：按段落、句子、标题递归切；
- Semantic Chunking：按语义边界切；
- Markdown Header Chunking：按标题层级切；
- Parent-child Chunking：小块检索，大块返回；
- Table-aware Chunking：表格保持完整；
- Code-aware Chunking：代码按函数、类、模块切。

其中 Parent-child Chunking 很重要。它的思想是：检索时用较小 chunk 提高命中精度，返回给 LLM 时带上较大的父段落，避免上下文碎片化。

例如，用户问：

```text
为什么这个方案不使用 instance loss？
```

如果 chunk 太短，可能只召回：

```text
we do not use instance loss
```

这不能回答原因。如果 chunk 保留了上下文，则可能召回：

```text
当前目标是图文语义向量对齐，而不是实例级分类，
因此不采用 instance loss。
```

这就是切块策略对答案质量的影响。

### Hybrid Search：不要只依赖向量检索

向量检索擅长语义相似，但不一定擅长精确名词。你的项目中会出现很多精确符号和专有名词，例如：

```text
CLAM
Qwen2.5-7B-Instruct
EVID_TOP_M
QuestionAnswerAdvisor
pgvector
instance loss
RetrievalAugmentor
```

这些词用关键词检索往往更稳。因此生产 RAG 常用 hybrid search：

```text
Dense Retrieval（向量检索）
+ Sparse Retrieval / BM25（关键词检索）
+ 融合排序
```

一个典型流程是：

```text
用户问题
  → 向量检索召回 top-30
  → 关键词检索召回 top-30
  → 合并去重
  → Reranker 精排
  → 取 top-5 给 LLM
```

### Reranker：让正确证据排到前面

很多 RAG 错误并不是“没有召回正确片段”，而是“正确片段排在第 12 名，但你只取 top-5”。

Reranker 的作用是：第一阶段宽召回，第二阶段精排序。

典型结构：

```text
问题
  → Retriever 粗召回 top-50
  → Reranker 逐个判断 query-document 相关性
  → 精排 top-5
  → LLM 回答
```

常见 reranker 包括：

- Cross-encoder reranker；
- BGE Reranker；
- Cohere Rerank；
- Jina Reranker；
- LLM-as-reranker。

Reranker 会增加延迟和成本，但经常能显著提升 RAG 答案质量。

### Grounding 与 Citation：不要让模型凭空扩写

RAG 的目标不是让答案“看起来更像真的”，而是让答案能对应到资料。

Prompt 应该明确约束：

```text
请只基于参考资料回答问题。
如果资料不足，请明确说明“资料不足”。
不要编造参考资料中没有的信息。
回答中尽量标注来源。
如果多个资料冲突，请指出冲突。
```

同时，RAG 系统应该返回来源信息：

```json
{
  "file_id": "file_001",
  "file_name": "paper.pdf",
  "page": 12,
  "chunk_index": 38,
  "snippet": "..."
}
```

没有 citation 的 RAG 很难验证，也很难在生产中让人信任。

### RAG Evaluation：必须可评估

不能靠“感觉回答得还行”判断 RAG 是否有效。一个基本测试集至少应包含：

![RAG Metrics](http://public.file.lvshuhuai.cn/images\rag-dair-metrics.png)

```text
question
expected_answer
ground_truth_source
actual_retrieved_chunks
model_answer
score
```

常见评估指标包括：

| 指标 | 关注点 |
|---|---|
| Retrieval Recall | 正确证据有没有被检索出来 |
| Context Precision | 检索上下文中有多少是有用的 |
| Context Recall | 必要证据是否被覆盖 |
| Faithfulness | 答案是否忠实于检索上下文 |
| Answer Relevancy | 答案是否真正回答问题 |
| Citation Accuracy | 引用是否对应原文 |

当 RAG 效果不好时，要分清楚是哪一环坏了：

```text
检索没找到？
找到了但排序太低？
上下文给了但模型没用？
模型用了但编造了？
引用错了？
权限过滤导致资料没进来？
```

只有这样，RAG 调优才不是靠玄学。

## 工程化落地：一个真实 RAG 系统需要哪些表和流程

如果只是 demo，可以手动把文件导入向量库，然后写一个 `/ask` 接口。但真实项目必须处理上传、异步索引、状态、删除、权限和重建。

### 推荐的业务流程

```text
用户上传文件
  → Spring Boot 保存原文件到 MinIO / 本地磁盘 / OSS
  → 写入 file 表，状态为 UPLOADED
  → 创建 document_index_job，状态为 PENDING
  → 后台任务解析文档
  → 切 chunk
  → 生成 embedding
  → 写入向量库
  → 写入 document_chunk 业务表
  → file 状态改为 INDEXED
  → job 状态改为 SUCCESS
```

如果失败：

```text
解析失败 / embedding 失败 / 向量库写入失败
  → job 状态改为 FAILED
  → 保存 error_message
  → 允许用户重试索引
```

### 推荐的基础表

一个最小工程化 RAG 系统可以有：

```text
knowledge_base
file
document_chunk
document_index_job
conversation
message
```

其中 `document_chunk` 可以保存业务侧 metadata，而 embedding 交给 pgvector / Qdrant / Milvus 存储。

示例 metadata：

```json
{
  "user_id": "u001",
  "knowledge_base_id": "kb001",
  "file_id": "file001",
  "file_name": "rag-note.pdf",
  "page": 12,
  "chunk_index": 38,
  "source_type": "pdf",
  "content_type": "text"
}
```

这些 metadata 对权限、引用、删除和重建非常重要。

### 删除和更新必须同步索引

用户删除文件时，不能只删原文件，还要删除对应 chunk 和向量索引。

```text
删除文件
  → 检查权限
  → 删除对象存储中的原文件
  → 删除 file 记录或标记 DELETED
  → 删除 document_chunk
  → 删除向量库中 file_id 对应的 embeddings
```

如果更换 embedding 模型，例如从 OpenAI Embedding 换成 Qwen Embedding，通常需要全量重建索引，因为旧向量空间和新向量空间不兼容。

![RAG vs Fine-tuning](http://public.file.lvshuhuai.cn/images\rag-dair-vs-finetuning.png)

### 不同复杂度的技术选型

可以按文档复杂度选择实现方式：

| 场景 | 推荐方案 |
|---|---|
| 简单 FAQ / Markdown / TXT | Spring AI 或 LangChain4j + pgvector |
| 普通 PDF 文档问答 | Spring AI / LangChain4j + PDF parser + pgvector/Qdrant |
| 需要更强数据索引能力 | LlamaIndex / LangChain + 向量库 |
| 大量表格、图片、公式、PPT | RAG-Anything / Docling / MinerU / LightRAG |
| 需要开箱即用平台 | Dify / FastGPT / Coze / OpenAI File Search |
| 需要 Agent 动态调用知识库 | LangChain / LangGraph / LangChain4j + RAG Tool |

最重要的是不要为了简单文本知识库引入过重的多模态框架，也不要用简单文本 RAG 去硬处理复杂论文 PDF 和图表文档。
