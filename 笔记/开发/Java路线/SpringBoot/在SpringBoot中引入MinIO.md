# 在 SpringBoot 中入 MinIO

## 版本

- SpringBoot 3.2.4
- MinIO 8.5.17
- JDK 23

## Maven 中

```xml
<properties>
    <minio.version>8.5.17</minio.version>
</properties>
<properties>
<dependency>
    <groupId>io.minio</groupId>
    <artifactId>minio</artifactId>
    <version>${minio.version}</version>
</dependency>
```

## Java 中

### Controller

```java
package shuhuai.mediacenter.oss.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import shuhuai.mediacenter.framework.common.controller.BaseController;
import shuhuai.mediacenter.framework.common.response.Response;
import shuhuai.mediacenter.framework.log.aspect.ApiOperationLog;
import shuhuai.mediacenter.oss.service.IFileService;

@RestController
@RequestMapping("/file")
public class FileController extends BaseController {

    private final IFileService fileService;

    @Autowired
    public FileController(IFileService fileService) {
        this.fileService = fileService;
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Response<String> uploadFile(@RequestPart(value = "file") MultipartFile file) {
        return new Response<>(fileService.uploadFile(file));
    }

    @PostMapping(value = "/test")
    @ApiOperationLog(description = "Feign 测试接口")
    public Response<String> test() {
        return new Response<>("1111111111111111111111111111");
    }
}
```

### Service

Service 层使用面向接口编程

#### Service 接口

```java
package shuhuai.mediacenter.oss.service;

import org.springframework.web.multipart.MultipartFile;

public interface IFileService {

    /**
     * 上传文件
     */
    String uploadFile(MultipartFile file);
}
```

#### Service 实现

```java
package shuhuai.mediacenter.oss.service.impl;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import shuhuai.mediacenter.oss.service.IFileService;
import shuhuai.mediacenter.oss.strategy.IFileStrategy;

@Service
@Slf4j
public class FileServiceImpl implements IFileService {
    private final IFileStrategy fileStrategy;

    @Autowired
    public FileServiceImpl(@Qualifier("getFileStrategy") IFileStrategy fileStrategy) {
        this.fileStrategy = fileStrategy;
    }

    @Override
    public String uploadFile(MultipartFile file) {
        // 上传文件到
        return fileStrategy.uploadFile(file);
    }
}

```

同时，使用策略模式和工厂模式，便于后续扩展

#### 策略接口

```java
package shuhuai.mediacenter.oss.strategy;

import org.springframework.web.multipart.MultipartFile;

public interface IFileStrategy {

    /**
     * 文件上传
     */
    String uploadFile(MultipartFile file);
}
```

#### MinIO 策略类

```java
package shuhuai.mediacenter.oss.strategy.impl;

import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;
import shuhuai.mediacenter.oss.config.MinioProperties;
import shuhuai.mediacenter.oss.strategy.IFileStrategy;

import java.util.UUID;

@Slf4j
@Component
public class MinioFileStrategy implements IFileStrategy {
    private final MinioProperties minioProperties;
    private final MinioClient minioClient;

    @Autowired
    public MinioFileStrategy(MinioProperties minioProperties, MinioClient minioClient) {
        this.minioProperties = minioProperties;
        this.minioClient = minioClient;
    }

    @Override
    @SneakyThrows
    public String uploadFile(MultipartFile file) {
        log.info("## 上传文件至 Minio ...");

        // 判断文件是否为空
        if (file == null || file.getSize() == 0) {
            log.error("==> 上传文件异常：文件大小为空 ...");
            throw new RuntimeException("文件大小不能为空");
        }

        // 文件的原始名称
        String originalFileName = file.getOriginalFilename();
        // 文件的 Content-Type
        String contentType = file.getContentType();

        // 生成存储对象的名称（将 UUID 字符串中的 - 替换成空字符串）
        String key = UUID.randomUUID().toString().replace("-", "");
        // 获取文件的后缀，如 .jpg
        String suffix = null;
        if (originalFileName != null) {
            suffix = originalFileName.substring(originalFileName.lastIndexOf("."));
        }

        // 拼接上文件后缀，即为要存储的文件名
        String objectName = String.format("%s%s", key, suffix);

        log.info("==> 开始上传文件至 Minio, ObjectName: {}", objectName);

        // 上传文件至 Minio
        minioClient.putObject(PutObjectArgs.builder()
                .bucket(minioProperties.getBucketName())
                .object(objectName)
                .stream(file.getInputStream(), file.getSize(), -1)
                .contentType(contentType)
                .build());

        // 返回文件的访问链接
        String url = String.format("%s/%s/%s", minioProperties.getEndpoint(), minioProperties.getBucketName(),
                objectName);
        log.info("==> 上传文件至 Minio 成功，访问路径: {}", url);
        return url;
    }
}
```

#### 工厂类

```java
package shuhuai.mediacenter.oss.fatory;

import com.alibaba.druid.util.StringUtils;
import io.minio.MinioClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import shuhuai.mediacenter.oss.config.MinioProperties;
import shuhuai.mediacenter.oss.strategy.IFileStrategy;
import shuhuai.mediacenter.oss.strategy.impl.MinioFileStrategy;

@Configuration
@RefreshScope
public class FileStrategyFactory {
    private final MinioProperties minioProperties;
    private final MinioClient minioClient;
    @Value("${storage.type}")
    private String strategyType;

    @Autowired
    public FileStrategyFactory(MinioProperties minioProperties, MinioClient minioClient) {
        this.minioProperties = minioProperties;
        this.minioClient = minioClient;
    }

    @Bean
    @RefreshScope
    public IFileStrategy getFileStrategy() {
        if (StringUtils.equals(strategyType, "minio")) {
            return new MinioFileStrategy(minioProperties, minioClient);
        }
        throw new IllegalArgumentException("不可用的存储类型");
    }
}
```

### config

#### MinioConfig

```java
package shuhuai.mediacenter.oss.config;

import io.minio.MinioClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MinioConfig {
    private final MinioProperties minioProperties;

    public MinioConfig(MinioProperties minioProperties) {
        this.minioProperties = minioProperties;
    }

    @Bean
    public MinioClient minioClient() {
        return MinioClient.builder()
                .endpoint(minioProperties.getEndpoint())
                .credentials(minioProperties.getAccessKey(), minioProperties.getSecretKey())
                .build();
    }
}
```

#### MinioProperties

```
package shuhuai.mediacenter.oss.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@ConfigurationProperties(prefix = "minio")
@Component
@Data
public class MinioProperties {
    private String endpoint;
    private String accessKey;
    private String secretKey;
    private String bucketName;
}
```

## application-dev.yml

```yaml
storage:
    type: minio # 对象存储类型
minio:
    endpoint: http://minio.example.cn:9000
    accessKey: accessKey
    secretKey: secretKey
    bucketName: media-center
```