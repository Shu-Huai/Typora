# IDEA 搭建 Spring Cloud Alibaba 微服务项目骨架

## 搭建微服务项目骨架：通过 Maven 多模块方式

![img](http://public.file.lvshuhuai.cn/图床\171464831063691.jpeg)

之前章节中，我们已经将开发小哈书所需的[本地环境搭建](https://www.quanxiaoha.com/column/10248.html) 完毕了，包括 JDK 17、MySQL 8.0 等等。本小节开始，正式进入到项目搭建环节。和[星球第一个项目](https://www.quanxiaoha.com/column/10000.html) 一样，依旧是采用 Maven 多模块的方式来管理微服务项目。

### 相关概念

> 在搭建项目之前，先了解一下相关概念。

#### 什么是单体架构

![img](http://public.file.lvshuhuai.cn/图床\171464981441263.jpeg)

单体架构是一种传统的软件架构模式，**通常将整个应用作为一个单一的、独立部署的单元来开发、构建和部署**。在单体架构中，所有的功能模块和业务逻辑都打包在同一个应用程序中，比如 `weblog` 项目，最终是打包成一个 `Jar` 包来部署。这包括业务逻辑、数据访问和数据存储等。整个应用程序通常部署在一个应用服务器上，与外部系统通过接口进行通信。**单体架构开发简单，部署方便，适合流量不大的应用。但随着应用规模的增长，往往会遇到可扩展性差、维护困难、部署风险高等问题。**

#### 什么是微服务架构

![img](http://public.file.lvshuhuai.cn/图床\171377814542065.png)

**微服务架构是一种将应用程序拆分为多个小型、自治的服务的架构模式**。可以通过上图本项目的架构图来理解。每个服务都专注于实现一个特定的业务功能，并通过轻量级的通信机制（如 HTTP 或 RPC）与其他服务进行通信。微服务架构将整个应用程序拆分成多个松耦合的服务单元，每个服务单元都可以独立开发、测试、部署和扩展。**微服务架构有助于提高灵活性、可扩展性和可维护性，适合大流量型应用。但也增加了部署和运维的复杂性，需要考虑服务间通信、服务注册与发现、服务监控等方面的问题。**

#### Spring Cloud

![img](http://public.file.lvshuhuai.cn/图床\171465110620877.jpeg)

Spring Cloud 是基于 Spring Boot 的微服务架构开发工具包，提供了一系列开发工具和库，用于快速构建、部署和管理分布式系统中的微服务应用。Spring Cloud提供了诸如服务发现、服务注册、负载均衡、断路器、配置管理、消息总线等功能，帮助开发人员解决了微服务架构中的常见问题，简化了微服务应用的开发和部署流程。

#### Spring Cloud Alibaba

Spring Cloud Alibaba 是 Spring Cloud 生态的一部分，提供了一系列基于阿里巴巴开源产品的分布式解决方案和工具，用于构建和管理基于 Spring Cloud 的微服务应用。Spring Cloud Alibaba 集成了阿里巴巴开源的服务，如 Nacos（服务注册与发现）、Sentinel（流量控制和熔断降级）、Dubbo（远程服务调用）、RocketMQ（消息队列）等，为开发人员提供了一站式的微服务解决方案。Spring Cloud Alibaba 与 Spring Cloud 兼容，并且提供了额外的功能和工具，帮助开发人员更轻松地构建、部署和管理微服务应用。

#### 多模块项目

##### 什么是多模块项目？

多模块项目是项目构建中的概念。拿 Maven 来说，多模块项目（Multi-Module Project）是其一个重要特性，**它允许我们在一个项目中管理多个子模块。**

在一个 Maven 多模块项目中，每个模块都是一个独立的项目，拥有自己的 POM 文件（Project Object Model，项目对象模型）。这些模块可以互相依赖，也可以被其他项目依赖。但是，所有的模块都会被统一管理，它们共享同一套构建系统和依赖管理。

Maven 多模块项目的结构大概是下面这样的：

```perl
my-app/  (父项目)
  |- pom.xml
  |- my-module1/  (子模块1)
  |    |- pom.xml
  |- my-module2/  (子模块2)
       |- pom.xml
  | ... (实际企业级项目中，会分非常多的模块)     
```

在这个例子中，`my-app` 是父项目，`my-module1` 和 `my-module2` 是它的子模块。每个模块都有自己的 `pom.xml` 文件。

##### 为什么需要多模块项目？

主要有以下几个原因：

- **代码组织**：在大型项目中，我们经常需要把代码分成多个模块，以便更好地组织代码。每个模块可以聚焦于一个特定的功能或领域，这样可以提高代码的可读性和可维护性。
- **依赖管理**：Maven 多模块项目可以帮助我们更好地管理项目的依赖。在父项目的 POM 文件中，我们可以定义所有模块共享的依赖，这样可以避免重复的依赖定义，也方便我们管理和升级依赖。
- **构建和部署**：Maven 多模块项目的另一个优点是它可以统一管理项目的构建和部署。我们只需要在父项目中执行 Maven 命令，就可以对所有模块进行构建和部署。这大大简化了开发者的工作。

### IDEA 搭建微服务多模块工程骨架

#### 创建父模块

打开 IDEA, 这里小哈使用的是 2024 版本。依次点击左上角菜单 *File | New | Project* , 开始创建项目：

![img](http://public.file.lvshuhuai.cn/图床\171456334191835.jpeg)

填写相关选项，操作如下：

![img](http://public.file.lvshuhuai.cn/图床\171456553078193.jpeg)

> 解释一下标注的地方:
>
> - ①：选择 `Maven Archetype` 来创建一个 `Maven` 项目;
> - ②：项目名称，小哈书的拼音；
> - ③：项目创建的位置；
> - ④：项目使用的 `JDK` 版本，本项目使用的是 `JDK 17` ；
> - ⑤：IDEA 需要知道 Maven Archetype Catalog 的位置，以便从中获取可用的 Archetype 列表。这个 Catalog 文件通常包含了 Maven 官方仓库或其他远程仓库中可用的 Archetype 信息。选择 `Internal` 即可。
> - ⑥：通过使用 Archetype，你可以基于已有的项目模板创建一个新项目。这里选择 `maven-archetype-quickstart`。
> - ⑦：填写 Group 组织名称，通常为公司域名倒写，如 `com.quanxiaoha`；
> - ⑧：项目的唯一标识符；
> - ⑨：项目版本号，默认就行；

然后，点击 *Create* 创建项目， 创建完成后，项目结构大致如下：

![img](http://public.file.lvshuhuai.cn/图床\171456713461068.jpeg)

> **TIP** : 如果生成了 `/src` 文件夹，将其删除掉，父模块仅需要保留一个 `pom.xml` 文件，用于统一管理依赖、插件等。如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171456562314945.jpeg)

修改父模块的 `pom.xml` 文件， 内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.quanxiaoha</groupId>
    <artifactId>xiaohashu</artifactId>
    <version>${revision}</version>

    <!-- 项目名称 -->
    <name>${project.artifactId}</name>
    <!-- 项目描述 -->
    <description>小哈书（仿小红书），基于 Spring Cloud Alibaba 微服务架构</description>

    <!-- 多模块项目需要配置打包方式为 pom -->
    <packaging>pom</packaging>

    <!-- 子模块管理 -->
    <modules>
    </modules>

    <properties>
        <!-- 项目版本号 -->
        <revision>0.0.1-SNAPSHOT</revision>
        <!-- JDK 版本 -->
        <java.version>17</java.version>
        <maven.compiler.source>${java.version}</maven.compiler.source>
        <maven.compiler.target>${java.version}</maven.compiler.target>
        <!-- 项目编码 -->
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <!-- Maven 相关版本号 -->
        <maven-compiler-plugin.version>3.8.1</maven-compiler-plugin.version>

        <!-- 依赖包版本 -->
        <lombok.version>1.18.30</lombok.version>
    </properties>

    <!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>

            <!-- 避免编写那些冗余的 Java 样板式代码，如 get、set 等 -->
            <dependency>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>${lombok.version}</version>
            </dependency>
            
        </dependencies>
    </dependencyManagement>

    <build>
        <!-- 统一插件管理 -->
        <pluginManagement>
            <plugins>
                <plugin>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-maven-plugin</artifactId>
                    <version>${spring-boot.version}</version>
                    <executions>
                        <execution>
                            <id>repackage</id>
                            <goals>
                                <goal>repackage</goal> <!-- 将依赖的 Jar 一起打包 -->
                            </goals>
                        </execution>
                    </executions>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>${maven-compiler-plugin.version}</version>
                    <configuration>
                        <source>${java.version}</source>
                        <target>${java.version}</target>
                        <encoding>${project.build.sourceEncoding}</encoding>
                        <annotationProcessorPaths>
                            <path>
                                <groupId>org.projectlombok</groupId>
                                <artifactId>lombok</artifactId>
                                <version>${lombok.version}</version>
                            </path>
                        </annotationProcessorPaths>
                    </configuration>
                </plugin>
            </plugins>
        </pluginManagement>

    </build>

    <!-- 添加华为云、阿里云 maven 中央仓库，提升依赖下载速度 -->
    <repositories>
        <repository>
            <id>huaweicloud</id>
            <name>huawei</name>
            <url>https://mirrors.huaweicloud.com/repository/maven/</url>
        </repository>
        <repository>
            <id>aliyunmaven</id>
            <name>aliyun</name>
            <url>https://maven.aliyun.com/repository/public</url>
        </repository>
    </repositories>

</project>
```

> 解释一波：
>
> 1. `<groupId>`,`<artifactId>`,`<version>`: 分别指定了项目的 groupId 、artifactId 和 version，用于唯一标识项目和版本管理。
> 2. `<name>`,`<description>`: 分别指定了项目的名称和描述。
> 3. `<packaging>`: 指定项目的打包方式，这里是`pom`，表示该项目是一个多模块项目，不会产生可执行的 Jar 包。
> 4. `<properties>`: 定义了项目的属性，包括项目版本号、JDK 版本、项目编码和依赖包版本等。
> 5. `<dependencyManagement>`: 统一管理项目的依赖版本，这里定义了 lombok 的版本。
> 6. `<build>`: 定义了项目的构建配置，包括插件管理和插件配置。这里配置了 Spring Boot Maven 插件和 Maven 编译插件，指定了 Java 版本和编码方式，并且配置了 Lombok 的注解处理器。
> 7. `<repositories>`: 配置了项目的仓库，包括华为云和阿里云的 Maven 中央仓库，用于提升依赖下载速度。

#### Spring Cloud Alibaba 版本选择

接下来，我们将为项目添加微服务框架。Spring Cloud Alibaba 的版本很多，考虑到最新版本 2023.0.x 使用人数还不多，可能存在坑，这里小哈降低一个版本，选择 *2022.0.x* 版本。小伙伴们可访问 Spring Cloud Alibaba 官网：[https://sca.aliyun.com](https://sca.aliyun.com/) , 点击导航栏中的 2022 版本，来查看对应的文档：

![img](http://public.file.lvshuhuai.cn/图床\171456805394556.jpeg)

点击查看左侧栏中的[版本发布声明](https://sca.aliyun.com/docs/2022/overview/version-explain/?spm=5176.29160081.0.0.748065cbt4crL0) ，可以查看 `Spring Boot` 、`Spring Cloud Alibaba` 、`Spring Cloud` ，以及各组件的依赖关系：

![img](http://public.file.lvshuhuai.cn/图床\171456819015366.jpeg)

参考官方文档，我们选择 `Spring Cloud Alibaba` 2022 最新的版本，即 `2022.0.0.0` 。在父模块的 `pom.xml` 中，添加三者的版本号，以及引入对应的依赖，内容如下：

```php-template
    <properties>
		// 省略...

        <!-- 依赖包版本 -->
        <spring-boot.version>3.0.2</spring-boot.version>
        <spring-cloud-alibaba.version>2022.0.0.0</spring-cloud-alibaba.version>
        <spring-cloud.version>2022.0.0</spring-cloud.version>

		// 省略...
    </properties>
    
    // 省略...
    
    <!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>
            <!-- Spring Boot 官方依赖管理 -->
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring-boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- Spring Cloud Alibaba 官方依赖管理 -->
            <dependency>
                <groupId>com.alibaba.cloud</groupId>
                <artifactId>spring-cloud-alibaba-dependencies</artifactId>
                <version>${spring-cloud-alibaba.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- Spring Cloud 官方依赖管理 -->
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

			// 省略...
        </dependencies>
    </dependencyManagement>
    
    // 省略...
```

#### 创建 auth 认证服务

接下来，我们来创建小哈书的第一个微服务 —— **认证服务**：专门负责用户登录、注册、账号注销等后端功能。

![img](http://public.file.lvshuhuai.cn/图床\171465023756832.jpeg)

在父项目*右键 | New | Module...* ， 来创建一个子模块：

![img](http://public.file.lvshuhuai.cn/图床\171463044690294.jpeg)

填写相关选项，操作如下：

![img](http://public.file.lvshuhuai.cn/图床\171463242894068.jpeg)

> 解释一下红线标注的地方：
>
> - 选择 Spring Boot 项目初始化器来创建项目;
> - 将 `Server URL` 更改为阿里云的 Spring Boot 初始化器：[http://start.aliyun.com](http://start.aliyun.com/) ；
> - 填写项目名称：`xiaohashu-auth` ，`auth` 表示认证的意思；
> - `Type` : 使用 Maven 来构建项目；
> - `Package name` : 包名称，修改为 `com.quanxiaoha.xiaohashu.auth`；
> - `JDK` 和 `Java` 版本均选择 17 ;

相关选项填写完毕后，点击 *Next* 按钮 ， 进入到下一步：

![img](http://public.file.lvshuhuai.cn/图床\171463249012842.jpeg)

> 按照前面说的 Spring Cloud Alibaba 官网指定的版本依赖关系，这里 Spring Boot 版本选择 *3.0.2* ， 顺便把 `Spring Web` 依赖勾选上。最后，点击 *Create* 按钮创建项目。

等待项目创建完成，结构如下，将一些不需要的文件、文件夹删除掉，如 `/static` 、`.gitignore` 、`HELP.me` ：

![img](http://public.file.lvshuhuai.cn/图床\171463256266364.jpeg)

> **TIP** : 使用阿里云 `Spring Boot` 初始化来创建的项目，会自动在你的项目中生成 `demos.web` 包，默认创建了一些接口使用示例，有兴趣的小伙伴，可以看看。

修改 `xiaohashu-auth` 认证服务的 `pom.xml` 文件，内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 指定父项目 -->
    <parent>
        <groupId>com.quanxiaoha</groupId>
        <artifactId>xiaohashu</artifactId>
        <version>${revision}</version>
    </parent>

    <!-- 指定打包方式 -->
    <packaging>jar</packaging>

    <artifactId>xiaohashu-auth</artifactId>
    <name>${project.artifactId}</name>
    <description>小哈书：认证服务（负责处理用户登录、注册、账号注销等）</description>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

接着，在父项目的 `pom.xml` 中的 `<modules>` 节点下，添加子模块， `xiaohashu-auth` 认证服务：

```php-template
    // 省略...
    
    <!-- 子模块管理 -->
    <modules>
        <!-- 认证服务 -->
        <module>xiaohashu-auth</module>
    </modules>
    
    // 省略...
```

添加完成后，点击右侧的 *Reload 图标*， 刷新一下 Maven 依赖，观察项目是否有爆红情况，正常情况下，应该都是正常的：

![img](http://public.file.lvshuhuai.cn/图床\171464202781996.jpeg)

#### 测试打包是否正常

接下来，我们测试一下多模块项目打包是否正常。对右侧栏中的*父项目*进行 `clean package` , 观察控制台日志，确认一下项目打包是否正常：

![img](http://public.file.lvshuhuai.cn/图床\171464681121569.jpeg)

#### 启动认证服务

打包没问题后，再来测试一下认证服务是否能够正常运行。点击 `XiaohashuAuthApplication` 启动类的 `main` 方法左侧的运行按钮，来启动服务：

![img](http://public.file.lvshuhuai.cn/图床\171463342932272.jpeg)

若看到控制台输出 `Tomcat started on port(s): 8080` 信息，则表示服务成功运行在了 `8080` 端口上。打开浏览器，访问地址 `localhost:8080` ，即可看到 `Spring Boot` 项目的页面提示信息了，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171463318036412.jpeg)

### 结语

本小结中，我们了解了什么是单体架构、微服务架构，以及 Spring Cloud 、Spring Cloud Alibaba 之间的关系。然后，上手搭建了一个 Maven 多模块项目，并引入了 Spring Cloud Alibaba 2022.0.x 依赖， 还创建了一个子模块 —— 认证服务，并成功运行了起来。但是，目前还只是简单的多模块的项目，还没实际使用到微服务，后续小节中，将一点一点引入 Spring Cloud Alibaba 相关组件，将整个微服务体系渐进式的搭建起来。

### 本小节源码下载

https://t.zsxq.com/tRw9Y

## 添加 framework 平台基础设施模块

本小节中，我们继续完善后端项目骨架 —— *抽取一个 `framework` 平台基础设施模块*。如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171480515122461)

### 为什么要抽取一个 framework 基础设施模块？

![img](http://public.file.lvshuhuai.cn/图床\171481643617744)

1. **代码复用和减少重复开发**：将通用的功能、组件抽取到一个独立的 `framework` 模块中，可以实现代码的复用，减少不同业务线之间的重复开发。这样，各个业务线可以专注于自身的业务逻辑实现，而不需要从头开始构建基础功能。
2. **统一管理和维护**：大一点的公司中，公司内部通常会成立一个基础平台小组，小组中均是经验丰富的高级工程师，由它们来开发并维护相关基础组件，编写使用文档。开发完成后，会将这些组件提交到公司内部的 `Maven` 私服，可以实现对该模块的统一管理和维护。一旦 `framework` 模块有更新或修复，所有业务线都可以通过更新依赖来获取最新的功能和修复，而不需要每个业务线都单独进行更新。
3. **版本控制和依赖管理**：`Maven` 私服可以提供版本控制和依赖管理的功能。通过在 `Maven` 私服中维护 `framework` 模块的版本信息，可以确保各个业务线使用到的是正确和兼容的版本，避免版本冲突和依赖问题。
4. **提高开发效率和质量**：通过提供一个稳定、可靠的 `framework` 模块，可以提高开发效率和质量。业务线开发人员可以更加专注于业务逻辑的实现，而不需要过多关注底层技术的实现细节。

### 新建 framework 模块

在项目上*右键 | New | Module...* , 新建一个子模块：

![img](http://public.file.lvshuhuai.cn/图床\171480151096436)

填写相关选项，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171480213661436)

> 解释一下标注的部分：
>
> - ①：选择 `Maven Archetype` 来创建一个 `Maven` 子模块;
> - ②：项目名称填写 `xiaoha-framework`；
> - ③：项目使用的 `JDK` 版本，本项目使用的是 `JDK 17` ；
> - ④：父模块选择 `xiaohashu` ；
> - ⑤：选择 `Internal` 。
> - ⑥：选择 `maven-archetype-quickstart`。
> - ⑦：填写 Group 组织名称，通常为公司域名倒写，如 `com.quanxiaoha`；
> - ⑧：项目的唯一标识符；

点击 *Create* 按钮开始创建 `framework` 子模块, 成功创建后，查看父模块的 `pom.xml` 文件，内容如下，可以看到 `<modules>` 节点中，自动添加上了该模块：

```php-template
    // 省略...

	<!-- 子模块管理 -->
    <modules>
        <!-- 平台基础框架 -->
        <module>xiaoha-framework</module>
        
		// 省略...
    </modules>
    
    // 省略...
```

编辑 `xiaoha-framework` 模块中的 `pom.xml` , 内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 指定父项目 -->
    <parent>
        <groupId>com.quanxiaoha</groupId>
        <artifactId>xiaohashu</artifactId>
        <version>${revision}</version>
    </parent>

    <!-- 多模块项目需要配置打包方式为 pom -->
    <packaging>pom</packaging>

    <artifactId>xiaoha-framework</artifactId>
    <name>${project.artifactId}</name>
    <description>平台基础设施层：封装一些常用功能，供各个业务线拿来即用</description>

    <modules>
        
    </modules>

</project>
```

> - 指定了父项目是谁；
> - 打包方式和父模块一样，都是 `pom` 形式, 因为后续要在 `framework` 基础设施层中，添加很多个子模（封装各种业务组件）。

项目结构如下图所示：

> **注意** : 如果自动生成了 `/src` 目录，需要删除掉。

![img](https://img.quanxiaoha.com/quanxiaoha/171480202461961)

### 添加 common 通用子模块

在 `xiaoha-framewrok` 模块上，继续*右键 | New | Module...* , 为基础设施层添加第一个子模块 —— `xiaoha-common` , 此模块为平台**通用模块**，主要放置一些通用枚举、工具类等等：

![img](http://public.file.lvshuhuai.cn/图床\171480218767057)

填写相关选项，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171480227470784)

> 解释一下标注的部分：
>
> - ①：选择 `Maven Archetype` 来创建一个 `Maven` 子模块;
> - ②：项目名称填写 `xiaoha-common`；
> - ③：项目使用的 `JDK` 版本，本项目使用的是 `JDK 17` ；
> - ④：父模块选择 `xiaohashu-framework` ；
> - ⑤：选择 `Internal` 。
> - ⑥：选择 `maven-archetype-quickstart`。
> - ⑦：组织 ID : `com.quanxiaoha.framework.common`；
> - ⑧：项目的唯一标识符；

点击 *Create* 按钮创建子模块。同样的，创建完成以后，查看 `xiaoha-framework` 模块的 `pom.xml` 文件，确认一下 `<modules>` 节点是否有自动添加该通用工具组件：

```php-template
    // 省略...
    
    <modules>
        <!-- 通用工具组件 -->
        <module>xiaoha-common</module>
    </modules>
    
    // 省略...
```

接着，编辑 `xiaoha-common` 模块的 `pom.xml` , 内容如下：

```php-template
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <!-- 指定父项目 -->
    <parent>
        <groupId>com.quanxiaoha</groupId>
        <artifactId>xiaoha-framework</artifactId>
        <version>${revision}</version>
    </parent>

    <!-- 指定打包方式 -->
    <packaging>jar</packaging>

    <artifactId>xiaoha-common</artifactId>
    <name>${project.artifactId}</name>
    <description>平台通用模块，如一些通用枚举、工具类等等</description>

    <dependencies>
        <!-- 避免编写那些冗余的 Java 样板式代码，如 get、set 方法等 -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
        </dependency>
    </dependencies>
</project>
```

> - 注意，这里指定了父项目为 `xiaoha-framework`， 打包方式为 `Jar` 包，添加一些模块描述性文字；
> - 然后添加了 `Lombok` 依赖。

编辑完毕后，将不需要的类删除掉，如 `App` 、`AppTest` :

![img](http://public.file.lvshuhuai.cn/图床\171480256178426)

### 添加 Response 工具类

在 `com.quanxiaoha.framework.common` 包下，添加一个封装好的 `Response` 响参工具类，以及相关异常类：

> **TIP** : 关于自定义响参工具类，可翻阅星球[第一个项目](https://www.quanxiaoha.com/column/10000.html) 专栏的相关小节，这里不做重复讲解，直接复制，拿过来用了:
>
> - [《Spring Boot 自定义响应工具类》](https://www.quanxiaoha.com/column/10012.html) ；

![img](http://public.file.lvshuhuai.cn/图床\171480283452733)

定义基础异常接口：

```csharp
package com.quanxiaoha.framework.common.exception;

public interface BaseExceptionInterface {

	// 获取异常码
    String getErrorCode();

	// 获取异常信息
    String getErrorMessage();
}
```

定义业务异常类：

> **TIP** : *Biz* 是 *Business* 英文的缩写，代表*业务*的意思。

```kotlin
package com.quanxiaoha.framework.common.exception;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class BizException extends RuntimeException {
    // 异常码
    private String errorCode;
    // 错误信息
    private String errorMessage;

    public BizException(BaseExceptionInterface baseExceptionInterface) {
        this.errorCode = baseExceptionInterface.getErrorCode();
        this.errorMessage = baseExceptionInterface.getErrorMessage();
    }
}
```

封装响参工具类：

```typescript
package com.quanxiaoha.framework.common.response;

import com.quanxiaoha.framework.common.exception.BaseExceptionInterface;
import com.quanxiaoha.framework.common.exception.BizException;
import lombok.Data;

import java.io.Serializable;

@Data
public class Response<T> implements Serializable {

    // 是否成功，默认为 true
    private boolean success = true;
    // 响应消息
    private String message;
    // 异常码
    private String errorCode;
    // 响应数据
    private T data;

    // =================================== 成功响应 ===================================
    public static <T> Response<T> success() {
        Response<T> response = new Response<>();
        return response;
    }

    public static <T> Response<T> success(T data) {
        Response<T> response = new Response<>();
        response.setData(data);
        return response;
    }

    // =================================== 失败响应 ===================================
    public static <T> Response<T> fail() {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        return response;
    }

    public static <T> Response<T> fail(String errorMessage) {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        response.setMessage(errorMessage);
        return response;
    }

    public static <T> Response<T> fail(String errorCode, String errorMessage) {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        response.setErrorCode(errorCode);
        response.setMessage(errorMessage);
        return response;
    }

    public static <T> Response<T> fail(BizException bizException) {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        response.setErrorCode(bizException.getErrorCode());
        response.setMessage(bizException.getErrorMessage());
        return response;
    }

    public static <T> Response<T> fail(BaseExceptionInterface baseExceptionInterface) {
        Response<T> response = new Response<>();
        response.setSuccess(false);
        response.setErrorCode(baseExceptionInterface.getErrorCode());
        response.setMessage(baseExceptionInterface.getErrorMessage());
        return response;
    }

}
```

至此，我们已经在 `xiaoha-common` 通用模块中，成功添加了响参工具类。这个功能是后续各个服务中，都需要用到的。

### 父模块中管理 common 模块版本号

接下来，我们将在 `xiaohashu-auth` 认证服务中，引入 `xiaoha-common` 模块，并测试一下是否能够正常使用 `Response` 响参工具类。首先，需要在最外层的 `pom` 文件中，声明一下 `xiaoha-common` 依赖以及其版本号，如下：

```php-template
    // 省略..
    
    <!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>
            
            <dependency>
                <groupId>com.quanxiaoha</groupId>
                <artifactId>xiaoha-common</artifactId>
                <version>${revision}</version>
            </dependency>

            // 省略...
        </dependencies>
    </dependencyManagement>
    
    // 省略..
```

然后，编辑 `xiaohashu-auth` 认证服务的 `pom.xml` 文件，引入该依赖：

```php-template
	<dependencies>
        <dependency>
            <groupId>com.quanxiaoha</groupId>
            <artifactId>xiaoha-common</artifactId>
        </dependency>

		// 省略...
    </dependencies>
```

### 添加一个测试接口

将认证服务中自动生成的 `demos.web` 包删除掉，另添加一个 `controller` 包，并创建一个 `TestController` 用于测试：

![img](http://public.file.lvshuhuai.cn/图床\171480334047679)

添加一个 `/test` 接口，并使用 `Response` 响参工具类进行成功响应，代码如下：

```kotlin
package com.quanxiaoha.xiaohashu.auth.controller;

import com.quanxiaoha.framework.common.response.Response;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author: 犬小哈
 * @url: www.quanxiaoha.com
 * @date: 2024/5/4 12:53
 * @description: TODO
 **/
@RestController
public class TestController {

    @GetMapping("/test")
    public Response<String> test() {
        return Response.success("Hello, 犬小哈专栏");
    }
}
```

重启认证服务，打开浏览器，访问 `localhost:8080/test` 接口，可以看到响应参数都是 OK 的：

![img](https://img.quanxiaoha.com/quanxiaoha/171480343197810)

### 结语

本小节中，我们继续完善了小哈书的工程骨架，添加了 `framework` 基础设施模块，接着，在该模块中添加了 `xiaoha-common`通用模块，后续如一些业务上通用的枚举、工具类等等，都可以放置此模块中。最后，我们在认证服务的 `pom.xml` 中，引入了 `common` 模块，并创建了一个测试接口，通过 `Response` 工具类，对前端成功返回了响应参数。

### 本小节源码下载

https://t.zsxq.com/2DtdH

## 自定义 Spring Boot 3.x Starter: 封装 API 请求日志切面业务组件

![img](http://public.file.lvshuhuai.cn/图床\171489621438128)

本小节中，我们将自定义一个 `Spring Boot Starter` 组件，将 API 请求日志切面功能封装进去，后续新建新的服务时，只需添加这个 `starter` , 即可拿来即用。关于接口日志切面，不清楚的小伙伴，可翻阅星球第一个项目：[《Spring Boot 自定义注解，实现 API 请求日志切面》](https://www.quanxiaoha.com/column/10009.html) 小节。

### 1. 什么是 Spring Boot Starter ?

Spring Boot Starter 就像是一个“工具包”，里面已经包含了你所需要的东西。它们把一些常用的功能和技术打包好了，比如处理数据库、处理 Web 请求等等。你只需要在你的项目中引入这些 Starter，它们就会自动帮你配置好所需的依赖项和参数。这样，你就可以省去很多繁琐的配置工作。

举个栗子，当你想要使用 Spring Boot 开发一个 Web 应用时，只需要引入 `spring-boot-starter-web` Starter。这个 Starter 包含了一系列依赖项和配置，使得开发 Web 应用变得更加简单。

具体来说，引入 `spring-boot-starter-web` Starter 后，你可以享受到以下好处：

1. **内嵌的 Web 服务器支持**：Spring Boot 内置了多种 Web 服务器支持，比如 Tomcat、Jetty、Undertow。`spring-boot-starter-web` 会自动配置一个默认的 Web 服务器，你无需手动配置即可启动你的应用。
2. **Spring MVC 框架支持**：Spring Boot 基于 Spring MVC 构建了强大的 Web 开发框架，包括了控制器、视图解析器等。引入 `spring-boot-starter-web` 后，你可以直接使用 Spring MVC 来处理 Web 请求。
3. **静态资源支持**：`spring-boot-starter-web` Starter 自动配置了对静态资源（如 HTML、CSS、JavaScript 文件）的处理，你可以直接在项目中放置这些文件，Spring Boot 就能够正确地访问它们。
4. **自动配置**：Spring Boot 会根据你的 classpath 自动配置应用程序。比如，如果你引入了 `spring-boot-starter-web`，Spring Boot 就会自动配置 DispatcherServlet、ViewResolver 等关键组件，从而让你的 Web 应用能够顺利地工作起来。

简而言之，Spring Boot Starter 是一种方便的方式，让你能够更快、更轻松地开始使用 Spring Boot 框架，并集成各种常用功能和技术。

### 2. 自定义 Spring Boot Starter

在 `xiaoha-framewrok` 模块上，继续*右键 | New | Module...* , 为基础设施层添加新的子模块 —— **业务日志切面组件**：

![img](http://public.file.lvshuhuai.cn/图床\171480218767057)img

填写相关选项，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171489242975618)

> 解释一下标注的部分：
>
> - ①：选择 `Maven Archetype` 来创建一个 `Maven` 子模块;
> - ②：项目名称填写 `xiaoha-spring-boot-starter-biz-operationlog`；
> - ③：项目使用的 `JDK` 版本，本项目使用的是 `JDK 17` ；
> - ④：父模块选择 `xiaoha-framework` ；
> - ⑤：选择 `Internal` 。
> - ⑥：选择 `maven-archetype-quickstart`。
> - ⑦：填写 `com.quanxiaoha.framework.biz.operationlog`；

点击 *Create* 按钮，开始创建子模块，创建完成后，查看 `xiaoha-framework` 模块的 `pom.xml` 文件，可以看到 `<modules>` 节点下自动添加好了该子模块：

```php-template
    <modules>
        <!-- 通用工具模块 -->
        <module>xiaoha-common</module>
        <!-- 接口日志组件 -->
        <module>xiaoha-spring-boot-starter-biz-operationlog</module>
    </modules>
```

编辑切面日志组件的 `pom.xml` 文件，内容如下：

```php-template
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <!-- 指定父项目 -->
    <parent>
        <groupId>com.quanxiaoha</groupId>
        <artifactId>xiaoha-framework</artifactId>
        <version>${revision}</version>
    </parent>

    <!-- 指定打包方式 -->
    <packaging>jar</packaging>

    <artifactId>xiaoha-spring-boot-starter-biz-operationlog</artifactId>
    <name>${project.artifactId}</name>
    <description>接口日志组件</description>

    <dependencies>
        <dependency>
            <groupId>com.quanxiaoha</groupId>
            <artifactId>xiaoha-common</artifactId>
        </dependency>

        <!-- AOP 切面 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-aop</artifactId>
        </dependency>
    </dependencies>
</project>
```

> - 指定父项目为 `xiaoha-framework`；
> - 指定打包方式为 `Jar` ，以及填写此模块的功能描述 ;
> - 添加 `xiaoha-common` 通用模块依赖，以及 AOP 切面依赖；

接着，将一些不需要的类删除掉：

![img](http://public.file.lvshuhuai.cn/图床\171489261456082)

### 3. 添加 JSON 工具类

由于在日志切面 `starter` 组件中，需要以 `json` 的格式打印出参，所以，我们需要先封装一个 `Json` 工具类。编辑最外层的 `pom.xml` , 声明 `Jackson` 相关依赖，统一管理版本号：

```php-template
   <properties>
        // 省略...

        <!-- 依赖包版本 -->
		// 省略...
        <jackson.version>2.16.1</jackson.version>
    </properties>
    
        <!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>
            // 省略...

            <!-- Jackson -->
            <dependency>
                <groupId>com.fasterxml.jackson.core</groupId>
                <artifactId>jackson-databind</artifactId>
                <version>${jackson.version}</version>
            </dependency>

            <dependency>
                <groupId>com.fasterxml.jackson.core</groupId>
                <artifactId>jackson-core</artifactId>
                <version>${jackson.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
```

添加完成后，编辑 `xiaoha-common` 公共模块的 `pom.xml`, 添加 `Jackson` 相关依赖：

```php-template
   <dependencies>
		// 省略...

        <!-- Jackson -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>

        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-core</artifactId>
        </dependency>

        <!-- 解决 Jackson Java 8 新日期 API 的序列化问题 -->
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
        </dependency>
    </dependencies>
```

> **TIP** : 在开发[星球第一个项目](https://www.quanxiaoha.com/column/10000.html) 中，日志切面打印出参时，如果出参中含有 `Java 8` 新的日期 `API`, 如 `LocalDateTime` , 你可能遇到过下面这个异常：
>
> ```sql
> com.fasterxml.jackson.databind.exc.InvalidDefinitionException: Java 8 date/time type `java.time.LocalDateTime` not supported by default: add Module "com.fasterxml.jackson.datatype:jackson-datatype-jsr310" to enable handling (through reference chain: com.quanxiaoha.framework.common.response.Response["data"]->com.quanxiaoha.xiaohashu.auth.controller.User["createTime"])
> ```
>
> 这是由于 `Jackson` 本身不支持新的日期 `API` , 需要使用 `jackson-datatype-jsr310` 库来解决此问题。

在 `xiaoha-common` 模块中，新建一个 `util` 工具包，用于统一放置相关工具类，并创建 `JsonUtils` , 如下图所示:

![img](http://public.file.lvshuhuai.cn/图床\171489744419092.jpeg)

代码如下：

```java
package com.quanxiaoha.framework.common.util;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import lombok.SneakyThrows;

public class JsonUtils {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    static {
        OBJECT_MAPPER.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        OBJECT_MAPPER.configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);
        OBJECT_MAPPER.registerModules(new JavaTimeModule()); // 解决 LocalDateTime 的序列化问题
    }

    /**
     *  将对象转换为 JSON 字符串
     * @param obj
     * @return
     */
    @SneakyThrows
    public static String toJsonString(Object obj) {
       return OBJECT_MAPPER.writeValueAsString(obj);
    }

}
```

> 解释一波：
>
> 1. `private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();`: 创建了一个私有的静态不可变的 `ObjectMapper` 实例，`ObjectMapper` 是 Jackson 库中用于序列化和反序列化 JSON 的核心类。
> 2. `static { ... }`: 这是一个静态初始化块，用于在类加载时执行一些初始化操作。在这里，`OBJECT_MAPPER` 被配置以在反序列化时忽略未知属性和在序列化时忽略空的 Java Bean 属性，并且注册了一个 `JavaTimeModule` 模块，用于解决 `LocalDateTime` 类型的序列化问题。
> 3. `public static String toJsonString(Object obj) { ... }`: 这是一个公共静态方法，用于将给定的 Java 对象序列化为 JSON 字符串。它接受一个 `Object` 类型的参数 `obj`，并使用 `OBJECT_MAPPER` 将其转换为 JSON 字符串并返回。
> 4. `@SneakyThrows`: 这是 Lombok 提供的一个注解，用于简化异常处理。它会将被标注的方法中的受检异常转换为不受检异常，使得代码看起来更加简洁。

### 4. 添加日志切面

`Json` 工具类编写完成后，回到日志切面 `starter` 组件中，创建 `/aspect` 包，用于放置切面相关的类，在里面添加自定义注解以及切面，这块的代码在第一个项目中已经讲解过了，不做赘述，直接拿过用就行:

![img](http://public.file.lvshuhuai.cn/图床\171489307180027.jpeg)

代码如下：

```java
package com.quanxiaoha.framework.biz.operationlog.aspect;

import java.lang.annotation.*;

@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD})
@Documented
public @interface ApiOperationLog {
    /**
     * API 功能描述
     *
     * @return
     */
    String description() default "";

}
package com.quanxiaoha.framework.biz.operationlog.aspect;

import com.quanxiaoha.framework.common.util.JsonUtils;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;

import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.function.Function;
import java.util.stream.Collectors;

@Aspect
@Slf4j
public class ApiOperationLogAspect {

    /** 以自定义 @ApiOperationLog 注解为切点，凡是添加 @ApiOperationLog 的方法，都会执行环绕中的代码 */
    @Pointcut("@annotation(com.quanxiaoha.framework.biz.operationlog.aspect.ApiOperationLog)")
    public void apiOperationLog() {}

    /**
     * 环绕
     * @param joinPoint
     * @return
     * @throws Throwable
     */
    @Around("apiOperationLog()")
    public Object doAround(ProceedingJoinPoint joinPoint) throws Throwable {
        // 请求开始时间
        long startTime = System.currentTimeMillis();

        // 获取被请求的类和方法
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();

        // 请求入参
        Object[] args = joinPoint.getArgs();
        // 入参转 JSON 字符串
        String argsJsonStr = Arrays.stream(args).map(toJsonStr()).collect(Collectors.joining(", "));

        // 功能描述信息
        String description = getApiOperationLogDescription(joinPoint);

        // 打印请求相关参数
        log.info("====== 请求开始: [{}], 入参: {}, 请求类: {}, 请求方法: {} =================================== ",
                description, argsJsonStr, className, methodName);

        // 执行切点方法
        Object result = joinPoint.proceed();

        // 执行耗时
        long executionTime = System.currentTimeMillis() - startTime;

        // 打印出参等相关信息
        log.info("====== 请求结束: [{}], 耗时: {}ms, 出参: {} =================================== ",
                description, executionTime, JsonUtils.toJsonString(result));

        return result;
    }

    /**
     * 获取注解的描述信息
     * @param joinPoint
     * @return
     */
    private String getApiOperationLogDescription(ProceedingJoinPoint joinPoint) {
        // 1. 从 ProceedingJoinPoint 获取 MethodSignature
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();

        // 2. 使用 MethodSignature 获取当前被注解的 Method
        Method method = signature.getMethod();

        // 3. 从 Method 中提取 LogExecution 注解
        ApiOperationLog apiOperationLog = method.getAnnotation(ApiOperationLog.class);

        // 4. 从 LogExecution 注解中获取 description 属性
        return apiOperationLog.description();
    }

    /**
     * 转 JSON 字符串
     * @return
     */
    private Function<Object, String> toJsonStr() {
        return JsonUtils::toJsonString;
    }

}
```

> **注意**：这个类和前一个项目区别是，去除掉了 `TraceId` 以及 `@Component` 注解。

### 5. starter 自动配置

接下来，就是自定义 `starter` 的重头戏 —— **自动配置**。新建一个 `/config` 包，并创建日志切面自动配置类，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171489314784469.jpeg)

代码如下：

```kotlin
package com.quanxiaoha.framework.biz.operationlog.config;

import com.quanxiaoha.framework.biz.operationlog.aspect.ApiOperationLogAspect;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.context.annotation.Bean;

@AutoConfiguration
public class ApiOperationLogAutoConfiguration {

    @Bean
    public ApiOperationLogAspect apiOperationLogAspect() {
        return new ApiOperationLogAspect();
    }
}
```

> 这是一个**自动配置类**，用于配置 API 操作日志记录功能，并且通过 `@Bean` 注解的 `apiOperationLogAspect()` 方法来创建一个 `ApiOperationLogAspect` 实例，以实现注入到 Spring 容器中。

接着，在 `/main` 文件夹下，创建 `/resources` 包，再创建 `/META-INF` 文件夹，再在里面创建 `/spring` 文件夹 , 以及 `org.springframework.boot.autoconfigure.AutoConfiguration.imports` 文件，**注意，这是自定义 `starter` 固定步骤，需要严格按照此格式来书写**，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171489323452091.jpeg)

`imports` 文件中内容如下，填写 `ApiOperationLogAutoConfiguration` 配置类的完整包路径：

```lua
com.quanxiaoha.framework.biz.operationlog.config.ApiOperationLogAutoConfiguration
```

> **TIP** : 创建的 `imports` 文件，必须保证前面有*小绿叶*标识，如果不是，可能导致自定义 `starter` 被 IDEA 无法识别的问题：
>
> ![img](http://public.file.lvshuhuai.cn/图床\171489328321798.png)
>
> 如果你手动创建的文件，没有小绿叶标识，可以下载本小节的源码，通过 IDEA 打开后，直接将 `/resouces` 目录复制到你的项目中，正常都会有小绿叶的。

至此，自定义 `starter` 步骤就完成了。

### 6. 统一版本控制

接下来，我们想在 `xiaoha-auth` 认证服务中使用刚刚封装好的 `starter` 组件。回到最外层的 `pom.xml` , 声明该组件依赖以及版本号：

```php-template
	// 省略...

	<!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>
			// 省略...

            <!-- 业务接口日志组件 -->
            <dependency>
                <groupId>com.quanxiaoha</groupId>
                <artifactId>xiaoha-spring-boot-starter-biz-operationlog</artifactId>
                <version>${revision}</version>
            </dependency>

        </dependencies>
    </dependencyManagement>
    
    // 省略...
```

### 7. 使用 starter

接着，编辑 `xiaoha-auth` 认证服务的 `pom.xml` , 添加日志切面 `starter` 的依赖, 代码如下：

```php-template
 <dependencies>
		// 省略...

        <!-- 业务接口日志组件 -->
        <dependency>
            <groupId>com.quanxiaoha</groupId>
            <artifactId>xiaoha-spring-boot-starter-biz-operationlog</artifactId>
        </dependency>

    </dependencies>
```

若出现爆红问题，点击右侧 *Reload* 按钮，重新刷新一下 Maven 依赖。最后，为 `/test` 接口添加 `@ApiOperationLog` 日志切面注解：

```kotlin
package com.quanxiaoha.xiaohashu.auth.controller;

import com.quanxiaoha.framework.biz.operationlog.aspect.ApiOperationLog;
import com.quanxiaoha.framework.common.response.Response;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {

    @GetMapping("/test")
    @ApiOperationLog(description = "测试接口")
    public Response<String> test() {
        return Response.success("Hello, 犬小哈专栏");
    }
}
```

重启项目， 浏览器访问 `localhost:8080/test` 接口，自测一波，看看日志切面是否能够正常工作：

![img](http://public.file.lvshuhuai.cn/图床\171489365129336.jpeg)

OK , 没有任何问题，自定义的日志切面 `starter` 工作良好！

### 8. 测试一下，切面打印出参中包含 Java 8 新日期 API

上面我们讲到，通过 `jackson-datatype-jsr310` 适配了 `Jackson` 不支持 Java 8 新日志 API 问题。这块也需要单独测试一下：

![img](http://public.file.lvshuhuai.cn/图床\171489379343297.jpeg)

创建一个 `User` 用户实体类，并添加两个字段，包含一个 `LocalDateTime` 日期字段，代码如下：

```java
package com.quanxiaoha.xiaohashu.auth.controller;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class User {
    /**
     * 昵称
     */
    private String nickName;

    /**
     * 创建时间
     */
    private LocalDateTime createTime;
}
```

编辑 `TestController` 控制器，新增一个 `/test2` 接口，代码如下：

```kotlin
package com.quanxiaoha.xiaohashu.auth.controller;

import com.quanxiaoha.framework.biz.operationlog.aspect.ApiOperationLog;
import com.quanxiaoha.framework.common.response.Response;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;

@RestController
public class TestController {

	// 省略..

    @GetMapping("/test2")
    @ApiOperationLog(description = "测试接口2")
    public Response<User> test2() {
        return Response.success(User.builder()
                        .nickName("犬小哈")
                        .createTime(LocalDateTime.now())
                        .build());
    }
}
```

重启项目，浏览器访问: http://localhost:8080/test2 , 观察控制台日志，如下：

![img](http://public.file.lvshuhuai.cn/图床\171489528246065.jpeg)

可以看到，即使出参对象中包含 Java 8 新日期 API 字段, 也是正常的，没有出现报异常情况。就是日期序列化格式不太友好，如上图所示。

### 9. 适配日期序列化格式

![img](http://public.file.lvshuhuai.cn/图床\171490342655267.jpeg)

为了解决上述问题，我们需要手动指定 `Jackson` 日期的序列化和反序列化规则。在 `xiaoha-common` 通用模块中，新建包 `/constant` 全局常量包, 并创建 `DateConstants` 日期常量接口，代码如下：

```csharp
public interface DateConstants {

    /**
     * 年-月-日 时：分：秒
     */
    String Y_M_D_H_M_S_FORMAT = "yyyy-MM-dd HH:mm:ss";
}
```

接着，编辑 `JsonUtils` 工具类，手动配置 `LocalDateTime` 日期格式化规则：

```cpp
    static {
        OBJECT_MAPPER.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        OBJECT_MAPPER.configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);

        // JavaTimeModule 用于指定序列化和反序列化规则
        JavaTimeModule javaTimeModule = new JavaTimeModule();
        
        // 支持 LocalDateTime
        javaTimeModule.addSerializer(LocalDateTime.class, new LocalDateTimeSerializer(DateTimeFormatter.ofPattern(DateConstants.Y_M_D_H_M_S_FORMAT)));
        javaTimeModule.addDeserializer(LocalDateTime.class, new LocalDateTimeDeserializer(DateTimeFormatter.ofPattern(DateConstants.Y_M_D_H_M_S_FORMAT)));

        OBJECT_MAPPER.registerModules(javaTimeModule); // 解决 LocalDateTime 的序列化问题
    }
```

再次重启项目，测试 `/test2` 接口，观察控制台日志，现在看到日期打印格式就友好多了~

![img](http://public.file.lvshuhuai.cn/图床\171489537890945.jpeg)

### 10. 结语

本小节中，我们了解了什么是 `Spring Boot Starter` , 并自己动手实现了一个日志切面 `starter` 组件，后续创建新的服务时，只需添加该 `starter` 组件, 然后，为想要打印接口出入参的接口，添加 `@ApiOperationLog` 注解，即可快速使用上日志切面功能了，非常方便，有木有！

### 11. 本小节源码下载

https://t.zsxq.com/wvKaU

## Spring Boot 3.x 整合 MyBatis

![img](http://public.file.lvshuhuai.cn/图床\171507530321363.jpeg)

本小节中，我们来为后端服务整合数据库持久层框架 —— **MyBatis** ，实现对数据库的增删改查。

### 1. 什么是 MyBatis ？

MyBatis 是一个用 Java 编写的持久层框架，它简化了数据库交互的过程，将 SQL 语句与 Java 方法相映射，从而使得开发者能够更轻松地操作数据库。

MyBatis 的优点包括：

- **简化的 SQL 语句：** MyBatis 允许开发者使用简单的 XML 文件或者注解来编写 SQL 语句，而不需要手动拼接 SQL 语句，大大简化了数据库操作的流程。
- **灵活性：** MyBatis 提供了丰富的配置选项和灵活的映射方式，开发者可以根据需求自定义映射关系，适应各种复杂的业务场景。
- **与 SQL 的紧密结合：** MyBatis 将 SQL 语句与 Java 代码紧密结合，开发者可以直观地理解代码的执行逻辑，同时也方便了 SQL 优化和调试。
- **良好的性能：** MyBatis 通过预编译 SQL 语句和数据库连接池等机制，提升了数据库操作的性能，使得系统能够更高效地处理大量数据。
- **与现有项目的兼容性：** MyBatis 不会对现有的项目结构和代码产生太大的影响，易于集成到已有的项目中，并且可以与其他框架（如 Spring）无缝整合，提高了开发效率。

总的来说，MyBatis 是一个功能强大且易于使用的持久层框架，适用于各种规模的项目，能够帮助开发者简化数据库操作，提高开发效率。

### 2. 新建库与表

为了等会演示通过 MyBatis 操作数据库，首先，我们先来建一个测试库。打开 Navicat, 连接上[之前小节](https://www.quanxiaoha.com/column/10249.html) 中搭建的 MySQL 8.0 数据库，*右键 | 新建数据库*：

![img](http://public.file.lvshuhuai.cn/图床\171506306696899.jpeg)

填写相关选项，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171506319202211.jpeg)

> - 填写新建的数据库名称；
>
> - 字符集选择 `utf8mb4` ；
>
>     > **拓展**： utf8mb4 是 utf8 的超集，支持更广泛的字符范围，包括一些不常见的表情符号、特殊符号以及辅助性的 Unicode 字符。这样可以确保你的数据库能够存储和处理各种语言的文本信息，而不会出现乱码或字符截断等问题。
>
> - 排序规则选择 `utf8mb4_unicode_ci` ,

数据库新建完成后，添加一张*用户测试表*，建表语句如下：

```sql
CREATE TABLE `t_user` (
	`id` BIGINT (20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键id',
	`username` VARCHAR (32) NOT NULL COMMENT '用户名',
	`create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
	`update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
	PRIMARY KEY (`id`) USING BTREE 
) ENGINE = INNODB COMMENT = '用户测试表';
```

![img](http://public.file.lvshuhuai.cn/图床\171506571897730.jpeg)

### 3. 整合 MyBatis

环境准备好了以后，准备开始为 `xiaohashu-auth` 认证服务整合 MyBatis 框架。编辑项目最外层的 `pom.xml` ， 声明 MySQL 驱动版本，以及 `mybatis-spring-boot-starter` , 代码如下：

```php-template
    <properties>

        // 省略...
        <mysql-connector-java.version>8.0.29</mysql-connector-java.version>
    </properties>

    <!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>
            // 省略...

            <!-- Mybatis -->
            <dependency>
                <groupId>org.mybatis.spring.boot</groupId>
                <artifactId>mybatis-spring-boot-starter</artifactId>
                <version>${spring-boot.version}</version>
            </dependency>

			<!-- MySQL 驱动 -->
            <dependency>
                <groupId>mysql</groupId>
                <artifactId>mysql-connector-java</artifactId>
                <version>${mysql-connector-java.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
```

接着，编辑 `xiaohashu-auth` 服务的 `pom.xml` ， 引入上面的依赖：

```php-template
 <dependencies>
		// 省略...

        <!-- Mybatis -->
        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
        </dependency>

        <!-- MySQL 驱动 -->
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
        </dependency>
    </dependencies>
```

别忘了最后刷新一下 Maven 依赖，将依赖包下载到本地仓库中：

![img](http://public.file.lvshuhuai.cn/图床\171506849842132.jpeg)

### 4. 项目多环境配置

关于 Spring Boot 项目如何配置多环境，可翻阅星球第一个项目中的《[Spring Boot 项目多环境配置](https://www.quanxiaoha.com/column/10006.html) 》小节，这里不再赘述，直接上代码。

![img](http://public.file.lvshuhuai.cn/图床\171506805069016.jpeg)

> **注意**：这里在 `/resources` 目录下，新建一个 `/config` 配置文件夹，统一放置 `applicaiton` 多环境配置文件。

编辑 `application.yml` 父配置，内容如下:

```yaml
server:
  port: 8080 # 项目启动的端口
  
spring:
  profiles:
    active: dev # 默认激活 dev 本地开发环境
```

编辑 `application-dev.yml` 本地开发环境配置文件，配置本地的数据库链接相关信息，如下：

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver # 指定数据库驱动类
    # 数据库连接信息
    url: jdbc:mysql://127.0.0.1:3306/xiaohashu?useUnicode=true&characterEncoding=utf-8&autoReconnect=true&useSSL=false&serverTimezone=Asia/Shanghai
    username: root # 数据库用户名
    password: 123456 # 数据库密码
```

> **TIP** : 数据库连接池暂时不做配置，直接用默认的，后续单独开一小节讲这一块。

### 5. 新建相关文件夹

编辑 `xiaohashu-auth` 服务，创建以下文件夹：

- `/domain/dataobject` : 用于统一放置 `DO` 类，对应数据库表；
- `/domain/mapper` : 用于放置 `Mapper` 接口；
- `/resources/mapper` : 用于放置 MyBatis `XML` 文件；

![img](http://public.file.lvshuhuai.cn/图床\171506842520165.jpeg)

### 6. 配置 MyBatis

接着，在 `Application` 启动类的头部，添加 `@MapperScan` 注解，值填写 `mapper` 接口所处的包路径，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171506860637091.jpeg)

```less
@SpringBootApplication
@MapperScan("com.quanxiaoha.xiaohashu.auth.domain.mapper")
public class XiaohashuAuthApplication {

    public static void main(String[] args) {
        SpringApplication.run(XiaohashuAuthApplication.class, args);
    }

}
```

另外，编辑 `application.yml` , 为 MyBatis 配置 `xml` 文件所在位置：

![img](http://public.file.lvshuhuai.cn/图床\171506867745596.jpeg)

```yaml
mybatis:
  # MyBatis xml 配置文件路径
  mapper-locations: classpath:/mapper/**/*.xml
```

> 解释：`classpath`: 表示 `/resources` 目录; `/mapper/**/*.xml` 表示在 mapper 目录及其所有子目录下查找以 `.xml` 结尾的文件。这种表达式允许你指定一个包含通配符的路径模式，以方便地匹配多个文件。

### 7. 新建 DO 类、 Mapper 接口、Xml 文件

文章开头的时候，我们创建了一个简单的 `t_user` 用户测试表，接下来，创建对应的 DO 类、Mapper 接口、Xml 文件，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171506942140296.jpeg)

#### **UserDO 类：**

```java
package com.quanxiaoha.xiaohashu.auth.domain.dataobject;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class UserDO {

    private Long id;

    private String username;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
```

#### **UserDOMapper 接口：**

```java
package com.quanxiaoha.xiaohashu.auth.domain.mapper;

import com.quanxiaoha.xiaohashu.auth.domain.dataobject.UserDO;

public interface UserDOMapper {

    /**
     * 根据主键 ID 查询
     * @param id
     * @return
     */
    UserDO selectByPrimaryKey(Long id);

    /**
     * 根据主键 ID 删除
     * @param id
     * @return
     */
    int deleteByPrimaryKey(Long id);

    /**
     * 插入记录
     * @param record
     * @return
     */
    int insert(UserDO record);

    /**
     * 更新记录
     * @param record
     * @return
     */
    int updateByPrimaryKey(UserDO record);
}
```

**UserDOMapper.xml 文件：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.quanxiaoha.xiaohashu.auth.domain.mapper.UserDOMapper">
  <resultMap id="BaseResultMap" type="com.quanxiaoha.xiaohashu.auth.domain.dataobject.UserDO">
    <id column="id" jdbcType="BIGINT" property="id" />
    <result column="username" jdbcType="VARCHAR" property="username" />
    <result column="create_time" jdbcType="TIMESTAMP" property="createTime" />
    <result column="update_time" jdbcType="TIMESTAMP" property="updateTime" />
  </resultMap>

  <select id="selectByPrimaryKey" parameterType="java.lang.Long" resultMap="BaseResultMap">
    select * from t_user where id = #{id}
  </select>

  <delete id="deleteByPrimaryKey" parameterType="java.lang.Long">
    delete from t_user where id = #{id}
  </delete>

  <insert id="insert" parameterType="com.quanxiaoha.xiaohashu.auth.domain.dataobject.UserDO">
    insert into t_user (username, create_time, update_time)
    values (#{username}, #{createTime}, #{updateTime})
  </insert>

  <update id="updateByPrimaryKey" parameterType="com.quanxiaoha.xiaohashu.auth.domain.dataobject.UserDO">
    update t_user
    set username = #{username},
      create_time = #{createTime},
      update_time = #{updateTime}
    where id = #{id}
  </update>
</mapper>
```

### 8. MyBatis 插件安装

如果你的持久层框架是 MyBatis, 那么经常需要在 `Mapper` 接口与 `xml` 文件之间互相跳转，如果手动跳转，会非常影响开发效率。这里推荐一个 MyBatis 插件：*Free MyBatis Tool* , 可以从 IDEA 的插件市场来搜索并安装，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171506959520420.jpeg)

安装完成后，在 `Mapper` 接口和 `xml` 文件中，就会出现对应的小箭头，点击箭头，即可快捷的跳转到对应的位置, 如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171506978255630.jpeg)

> **TIP** : 类似的插件有很多，不一定需要和我用同一款，可自行选择，满足跳转需求即可。

### 9. 配置 SQL 日志打印

开发中为了方便调试，想要打印实际执行的 SQL 语句, 可编辑 `application-dev.yml` 配置文件，配置 `mapper` 接口所在包的日志级别为 `debug` , 即可实现此功能：

```yaml
logging:
  level:
    com.quanxiaoha.xiaohashu.auth.domain.mapper: debug
```

![img](http://public.file.lvshuhuai.cn/图床\171507050840570.jpeg)

### 10. 编写单元测试

以上内容均配置完毕后，我们来编辑 `XiaohashuAuthApplicationTests` 单元测试类，编写几个单元测试，来测试一下通过 MyBatis 来操作数据库好不好使：

![img](http://public.file.lvshuhuai.cn/图床\171508495255927.jpeg)

#### 10.1 新增数据

单元测试方法如下：

```\
package com.quanxiaoha.xiaohashu.auth;

import com.quanxiaoha.framework.common.util.JsonUtils;
import com.quanxiaoha.xiaohashu.auth.domain.dataobject.UserDO;
import com.quanxiaoha.xiaohashu.auth.domain.mapper.UserDOMapper;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDateTime;

@SpringBootTest
@Slf4j
class XiaohashuAuthApplicationTests {

    @Resource
    private UserDOMapper userDOMapper;

    /**
     * 测试插入数据
     */
    @Test
    void testInsert() {
        UserDO userDO = UserDO.builder()
                .username("犬小哈")
                .createTime(LocalDateTime.now())
                .updateTime(LocalDateTime.now())
                .build();

        userDOMapper.insert(userDO);
    }

}
```

点击左侧的*运行按钮*， 来运行此测试方法：

![img](http://public.file.lvshuhuai.cn/图床\171507015505269.jpeg)

观察控制台日志，确认没有任何报错，然后再查看 `t_user` 表，看看数据是否插入成功：

![img](http://public.file.lvshuhuai.cn/图床\171507020314867.jpeg)

#### 10.2 查询数据

再编写一个查询数据的测试方法：

```java
package com.quanxiaoha.xiaohashu.auth;

import com.quanxiaoha.framework.common.util.JsonUtils;
import com.quanxiaoha.xiaohashu.auth.domain.dataobject.UserDO;
import com.quanxiaoha.xiaohashu.auth.domain.mapper.UserDOMapper;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDateTime;

@SpringBootTest
@Slf4j
class XiaohashuAuthApplicationTests {

    @Resource
    private UserDOMapper userDOMapper;

	// 省略...

    /**
     * 查询数据
     */
    @Test
    void testSelect() {
    	// 查询主键 ID 为 4 的记录
        UserDO userDO = userDOMapper.selectByPrimaryKey(4L);
        log.info("User: {}", JsonUtils.toJsonString(userDO));
    }
}
```

如下图所示，实际执行的 SQL 成功被打印了出来，同时，查询出来的数据也是正确的：

![img](http://public.file.lvshuhuai.cn/图床\171507062267581.jpeg)

#### 10.3 更新、删除数据

最后是更新、删除数据，这里直接贴具体代码，小伙伴们可自行测试一下，就不再截图了：

```csharp
    // 省略...
    
    /**
     * 更新数据
     */
    @Test
    void testUpdate() {
        UserDO userDO = UserDO.builder()
                .id(4L)
                .username("犬小哈教程")
                .updateTime(LocalDateTime.now())
                .build();

		// 根据主键 ID 更新记录
        userDOMapper.updateByPrimaryKey(userDO);
    }
    
    // 省略...
    // 省略...
    
    /**
     * 删除数据
     */
    @Test
    void testDelete() {
    	// 删除主键 ID 为 4 的记录
        userDOMapper.deleteByPrimaryKey(4L);
    }
    
    // 省略...
```

### 11. 结语

本小结中，我们为 `xiaohashu-auth` 认证服务整合完成了 MyBatis 持久层框架，最后，编写了增删改查共 4 个单元测试方法，成功通过 MyBatis 框架操作了数据库。

### 本小节源码下载

https://t.zsxq.com/6WaAs

## Spring Boot 3.x 整合 Druid 数据库连接池（含密码加密）

[上小节](https://www.quanxiaoha.com/column/10262.html) 中，我们已经把 MyBatis 数据库持久层框架整合完成了，但是数据库连接池这块，还没有做配置。和[星球第一个项目](https://www.quanxiaoha.com/column/10000.html) 不同的是，这次的数据库连接池，我们将选型国内比较火的 —— *阿里开源的 Druid 德鲁伊*。

### 1. 为什么需要数据库连接池？

![img](http://public.file.lvshuhuai.cn/图床\171524095073599.jpeg)

**数据库连接池是一种用于管理数据库连接的技术**。在传统的数据库连接方式中，每次与数据库建立连接都需要经过一系列的网络通信和身份验证过程，这会消耗大量的系统资源和时间。而数据库连接池则通过预先创建一定数量的数据库连接并将其保存在池中，以供需要时复用，从而避免了重复建立和关闭连接的开销。

使用数据库连接池有如下优点：

- **提高性能和效率**：数据库连接池可以复用已经建立的数据库连接，减少了每次连接数据库的开销，提高了系统的性能和响应速度。
- **资源管理**：数据库连接池可以限制系统中同时存在的连接数量，防止数据库连接过多导致系统资源不足或性能下降。
- **连接复用**：数据库连接池可以管理连接的生命周期，确保连接在需要时处于可用状态，并在不再需要时释放资源，从而减少了系统资源的浪费。
- **连接池监控**：数据库连接池通常提供了监控和管理功能，可以实时监控连接的使用情况、连接的状态和性能指标，帮助管理员及时发现和解决问题。

### 2. 什么是 Druid 连接池？

![img](http://public.file.lvshuhuai.cn/图床\171523995762043.jpeg)

**Druid 是阿里巴巴开源的一个高性能的数据库连接池**，GitHub 地址：https://github.com/alibaba/druid 。它不仅提供了传统数据库连接池的连接管理功能，还提供了一系列强大的监控和扩展功能。Druid 的优势主要体现在以下几个方面：

- **高性能**：Druid 是基于 Java 平台开发的，使用了高效的连接池算法和多线程技术，能够提供高性能的数据库连接管理服务。
- **丰富的监控功能**：Druid 提供了丰富的监控功能，包括连接池状态监控、SQL 执行性能监控、SQL 执行分析等，可以实时监控数据库连接的使用情况和性能指标，并生成详细的报表和图表。
- **安全性**：Druid 内置了防 SQL 注入功能和黑名单功能，能够有效防止恶意 SQL 注入攻击和非法访问。
- **灵活的配置**：Druid 提供了丰富的配置选项，可以灵活地配置连接池的参数和行为，满足不同场景下的需求。
- **可扩展性**：Druid 提供了插件机制，支持自定义插件和扩展功能，开发人员可以根据需要自定义监控指标、扩展连接池的功能等。
- **完善的文档和社区支持**：Druid 有完善的官方文档和活跃的社区支持，开发人员可以方便地获取帮助和解决问题。

### 3. 开始整合

#### 3.1 添加依赖

编辑小哈书项目最外层的 `pom.xml` ， 声明 Druid 版本号以及依赖：

```php-template
    // 省略...
    
    <properties>
		// 省略...
		
        <druid.version>1.2.21</druid.version>
    </properties>

    <!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>
    		// 省略...

            <!-- Druid 数据库连接池 -->
            <dependency>
                <groupId>com.alibaba</groupId>
                <artifactId>druid-spring-boot-3-starter</artifactId>
                <version>${druid.version}</version>
            </dependency>
            
        </dependencies>
    </dependencyManagement>
    
    // 省略...
```

接着，编辑 `xiaohashu-auth` 认证服务，添加依赖：

```php-template
	// 省略...

	<dependencies>
		// 省略...

        <!-- Druid 数据库连接池 -->
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>druid-spring-boot-3-starter</artifactId>
        </dependency>
    </dependencies>
    
    // 省略...
```

依赖添加完毕后，别忘了点击 IDEA 右侧栏的 Reload 按钮，刷新一下 Maven 依赖，将包下载到本地仓库中。

#### 3.2 连接池配置

然后就是配置连接池相关参数了，编辑 `application-dev.yml` 文件，先为本地开发环境配置一下，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171523660061331.jpeg)

配置代码如下：

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver # 指定数据库驱动类
    # 数据库连接信息
    url: jdbc:mysql://127.0.0.1:3306/xiaohashu?useUnicode=true&characterEncoding=utf-8&autoReconnect=true&useSSL=false&serverTimezone=Asia/Shanghai
    username: root # 数据库用户名
    password: 123456 # 数据库密码
    type: com.alibaba.druid.pool.DruidDataSource
    druid: # Druid 连接池
      initial-size: 5 # 初始化连接池大小
      min-idle: 5 # 最小连接池数量
      max-active: 20 # 最大连接池数量
      max-wait: 60000 # 连接时最大等待时间（单位：毫秒）
      test-while-idle: true
      time-between-eviction-runs-millis: 60000 # 配置多久进行一次检测，检测需要关闭的连接（单位：毫秒）
      min-evictable-idle-time-millis: 300000 # 配置一个连接在连接池中最小生存的时间（单位：毫秒）
      max-evictable-idle-time-millis: 900000 # 配置一个连接在连接池中最大生存的时间（单位：毫秒）
      validation-query: SELECT 1 FROM DUAL # 配置测试连接是否可用的查询 sql
      test-on-borrow: false
      test-on-return: false
      pool-prepared-statements: false
      web-stat-filter:
        enabled: true
      stat-view-servlet:
        enabled: true
        url-pattern: /druid/* # 配置监控后台访问路径
        login-username: admin # 配置监控后台登录的用户名、密码
        login-password: admin
      filter:
        stat:
          enabled: true
          log-slow-sql: true # 开启慢 sql 记录
          slow-sql-millis: 2000 # 若执行耗时大于 2s，则视为慢 sql
          merge-sql: true
        wall: # 防火墙
          config:
            multi-statement-allow: true
```

> 解释一下上面各项配置，都是干啥的：
>
> 1. `type: com.alibaba.druid.pool.DruidDataSource`：指定使用 Druid 连接池。
>
> 2. `initial-size`：初始化连接池大小，即连接池启动时创建的初始化连接数。
>
> 3. `min-idle`：最小连接池数量，连接池中保持的最小空闲连接数。
>
> 4. `max-active`：最大连接池数量，连接池中允许的最大活动连接数。
>
> 5. `max-wait`：连接时最大等待时间，当连接池中的连接已经用完时，等待从连接池获取连接的最长时间，单位是毫秒。
>
> 6. `test-while-idle`：连接空闲时是否执行检查。
>
> 7. `time-between-eviction-runs-millis`：配置多久进行一次检测，检测需要关闭的连接，单位是毫秒。
>
> 8. `min-evictable-idle-time-millis`：一个连接在连接池中最小生存的时间，单位是毫秒。
>
> 9. `max-evictable-idle-time-millis`：一个连接在连接池中最大生存的时间，单位是毫秒。
>
> 10. `validation-query`：测试连接是否可用的查询 SQL。
>
> 11. `test-on-borrow`：连接从连接池获取时是否测试连接的可用性。
>
> 12. `test-on-return`：连接返回连接池时是否测试连接的可用性。
>
> 13. `pool-prepared-statements`：是否缓存 PreparedStatement，默认为 false。
>
> 14. `web-stat-filter`：用于配置 Druid 的 Web 监控功能。在这里，`enabled` 表示是否开启 Web 监控功能。如果设置为 true，就可以通过浏览器访问 Druid 的监控页面。
>
> 15. ```
>     stat-view-servlet
>     ```
>
>     ：配置 Druid 的监控后台访问路径、登录用户名和密码。
>
>     - `enabled` 表示是否开启监控后台功能。
>     - `url-pattern` 指定了监控后台的访问路径，即通过浏览器访问监控页面时的 URL。
>     - `login-username` 和 `login-password` 分别指定了监控后台的登录用户名和密码，用于访问监控后台时的身份验证。
>
> 16. ```
>     filter
>     ```
>
>     ：用于配置 Druid 的过滤器，包括统计过滤器和防火墙过滤器。
>
>     - `stat`：配置 Druid 的统计过滤器。`enabled` 表示是否开启统计功能，`log-slow-sql` 表示是否开启慢 SQL 记录，`slow-sql-millis` 指定了执行时间超过多少毫秒的 SQL 语句会被认为是慢 SQL，`merge-sql` 表示是否开启 SQL 合并功能。
>     - `wall`：配置 Druid 的防火墙过滤器。防火墙用于防止 SQL 注入攻击。在这里，`config` 配置了防火墙的规则，`multi-statement-allow` 表示是否允许执行多条 SQL 语句。

#### 3.3 测试一波

上述配置完成后，我们来执行一下上小节的单元测试，看看加入连接池后，查询功能是否还是正常的：

![img](http://public.file.lvshuhuai.cn/图床\171523685879450.jpeg)

> **TIP** : 如果控制台日志中，有输出 `Init DruidDataSource` 信息，说明当前我们使用的数据库连接池，已经是 Druid 德鲁伊了。

#### 3.4 监控后台

重启认证服务，访问地址：http://localhost:8080/druid ，即可登录 Druid 监控后台, 如下图所示，用户名和密码填写刚刚 `yml` 文件中手动配置的：

![img](http://public.file.lvshuhuai.cn/图床\171523694932858.jpeg)

登录成功后，就能看到各项监控信息了，有兴趣的小伙伴可以自己点点各个页面，探索探索：

![img](http://public.file.lvshuhuai.cn/图床\171523721423466.jpeg)

### 4. 数据库密码加密

#### 4.1 为什么配置文件中的密码需要加密？

数据库连接密码加密是为了增强系统的安全性。在配置文件中，明文存储数据库连接密码存在以下几个潜在风险：

- **泄露风险：** 如果配置文件被不当地公开或者泄露，其中包含的数据库连接密码也会暴露给不可信的第三方，从而造成数据库的安全威胁。
- **权限滥用：** 如果系统中的某个用户拥有访问配置文件的权限，那么他就可以直接获取到数据库连接密码。如果这个用户是不可信的，就有可能滥用这个权限，对数据库进行非法操作。
- **审计追踪：** 明文存储密码会降低系统的审计追踪能力。一旦出现安全问题，无法准确追踪是谁在何时何地使用了数据库连接密码。

为了避免以上风险，我们可以采取数据库连接密码加密的方式。**加密后的密码可以在配置文件中存储，即使被泄露也不会直接暴露真实的密码，增加了攻击者破解密码的难度。**

#### 4.2 Druid 内置工具加密密码

接下来，我们将通过 Druid 内置的密码加密工具 `ConfigTools`，来对明文密码进行加密处理。在 `xiaohashu-auth` 认证服务中，新建一个 `DruidTests` 单元测试，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\171523770074333.jpeg)

代码如下：

```typescript
package com.quanxiaoha.xiaohashu.auth;

import com.alibaba.druid.filter.config.ConfigTools;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;


@SpringBootTest
@Slf4j
class DruidTests {


    /**
     * Druid 密码加密
     */
    @Test
    @SneakyThrows
    void testEncodePassword() {
        // 你的密码
        String password = "123456";
        String[] arr = ConfigTools.genKeyPair(512);

        // 私钥
        log.info("privateKey: {}", arr[0]);
        // 公钥
        log.info("publicKey: {}", arr[1]);

        // 通过私钥加密密码
        String encodePassword = ConfigTools.encrypt(arr[0], password);
        log.info("password: {}", encodePassword);
    }

}
```

> 解释一下上述代码：
>
> 1. `String password = "123456";`：定义了要加密的密码。
> 2. `String[] arr = ConfigTools.genKeyPair(512);`：调用 `ConfigTools` 类的 `genKeyPair` 方法生成 RSA 密钥对。RSA 是一种非对称加密算法，`512` 表示密钥长度为 512 位。
> 3. `log.info("privateKey: {}", arr[0]);` 和 `log.info("publicKey: {}", arr[1]);`：分别打印生成的私钥和公钥。私钥用于加密，公钥用于解密。
> 4. `String encodePassword = ConfigTools.encrypt(arr[0], password);`：调用 `ConfigTools` 类的 `encrypt` 方法，使用生成的私钥对密码进行加密。这里将生成的私钥和密码作为参数传入，返回加密后的密码。
> 5. `log.info("password: {}", encodePassword);`：打印加密后的密码。

运行该单元测试，控制台输入如下：

![img](http://public.file.lvshuhuai.cn/图床\171523797036344.jpeg)

#### 4.3 配置加密后的密码

接下来，编辑 `applicaiton-dev.yml` 文件，配置密码加密相关配置，如下图标注所示：

![img](http://public.file.lvshuhuai.cn/图床\171523831307111.jpeg)

核心配置如下：

```yaml
spring:
  datasource:
    // 省略...
    password: A2qT03X7KlL4v/F2foD6kV/Ch9gpNBWOh1qoCywanjv1AsI7f9x3iAyR9NkUKeV+FMo+halCTzy5Llbk2VOrVQ== # 数据库密码
    type: com.alibaba.druid.pool.DruidDataSource
    druid: # Druid 连接池
      // 省略...
      connectionProperties: config.decrypt=true;config.decrypt.key=MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAIaJmhsfN14oM+bghiOfARP6YgIiArekviyAOEa9Dt8spf4W38kSJShGs0NkzT3btqJB0O2o0X/yfVE8kqme1jMCAwEAAQ==
      // 省略...
      filter:
        config:
          enabled: true
        // 省略...
```

> 解释一下上述配置项：
>
> 1. `password: A2qT03X7KlL4v/F2foD6kV/Ch9gpNBWOh1qoCywanjv1AsI7f9x3iAyR9NkUKeV+FMo+halCTzy5Llbk2VOrVQ==`：这里的密码改为加密后的密码。
> 2. `connectionProperties: config.decrypt=true;config.decrypt.key=MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAIaJmhsfN14oM+bghiOfARP6YgIiArekviyAOEa9Dt8spf4W38kSJShGs0NkzT3btqJB0O2o0X/yfVE8kqme1jMCAwEAAQ==`：这里配置了连接属性，其中 `config.decrypt=true` 表示开启密码解密功能，`config.decrypt.key` 是用于解密的密钥，即上面单元测试生成**公钥**。在 Druid 连接池中，如果我们的密码已经经过了加密处理，就需要在连接属性中配置解密相关的参数，以便 Druid 能够正确解密密码，然后连接到数据库。
> 3. `filter.config.enabled: true`：这里配置了 Druid 连接池的 `filter`，其中 `config` 是一个配置项，`enabled: true` 表示开启该配置项。这个配置项通常用于配置 Druid 连接池的一些额外功能，比如密码解密等。

Druid 加解密配置项搞定后，再次运行上小节中的单元测试方法，测试整体功能是否好使：

![img](http://public.file.lvshuhuai.cn/图床\171523846102695.jpeg)

可以看到，密码加密后，查询数据也是没有问题的，说明 Druid 加解密配置正确。至此，本小节我们就将 Druid 数据库连接池整合完毕啦~

### 本小节源码下载

https://t.zsxq.com/5K2h0