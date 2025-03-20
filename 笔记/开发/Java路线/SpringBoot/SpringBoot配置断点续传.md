# SpringBoot 配置断点续传和按需加载文件

## 需求说明

故事的起源是我需要在前端做一个 PDF 预览显示的功能，但我的 PDF 太大了，动辄 3-500 MB，这时候需要引入按需加载。

在后端定义一个传文件的接口，在前端接受数据。

## 步骤

### 后端

#### Controller

```java
@ApiOperationLog
@GetMapping("/pdf")
public ResponseEntity<Resource> loadPDFByPage(@RequestParam("bookId") Integer bookId,
                                              @RequestHeader(value = "Range", required = false) String rangeHeader) {
    List<HttpRange> httpRanges = rangeHeader != null ? HttpRange.parseRanges(rangeHeader) : null;
    return fileService.loadPDF(bookId, httpRanges);
}
```

#### Service

```java
/**
 * 加载PDF文件
 *
 * @param bookId     书籍ID
 * @param httpRanges HTTP范围
 * @return ResponseEntity
 */
public ResponseEntity<Resource> loadPDF(Integer bookId, List<HttpRange> httpRanges) {
    File pdf = getPDFFile(bookId);
    if (!pdf.exists()) {
        throw new BaseException(ResponseCode.ERROR);
    }
    try {
        long fileLength = pdf.length();
        InputStreamResource resource;
        HttpHeaders headers = new HttpHeaders();
        if (httpRanges == null || httpRanges.isEmpty()) {
            // 全量下载
            resource = new InputStreamResource(new FileInputStream(pdf));
            headers.setContentLength(fileLength);
            headers.set("Accept-Ranges", "bytes");
            // 关键：设置Access-Control-Expose-Headers
            headers.add("Access-Control-Expose-Headers", "Accept-Ranges,Content-Range");
            return ResponseEntity.ok()
                    .headers(headers)
                    .contentType(MediaType.APPLICATION_PDF)
                    .body(resource);
        } else {
            // 断点续传
            HttpRange range = httpRanges.getFirst();
            // 获取请求的范围
            long start = range.getRangeStart(fileLength);
            long end = range.getRangeEnd(fileLength);
            long rangeLength = end - start + 1;
            // RandomAccessFile 支持随机访问文件
            RandomAccessFile raf = new RandomAccessFile(pdf, "r");
            raf.seek(start);
            byte[] buffer = new byte[(int) rangeLength];
            raf.readFully(buffer);
            raf.close();
            // ByteArrayInputStream 从字节数组中读取数据
            ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(buffer);
            // 将字节数组转换为 InputStreamResource
            resource = new InputStreamResource(byteArrayInputStream);
            headers.set("Content-Range", "bytes " + start + "-" + end + "/" + fileLength);
            headers.setContentLength(rangeLength);
            headers.set("Accept-Ranges", "bytes");
            // 关键：设置Access-Control-Expose-Headers
            headers.add("Access-Control-Expose-Headers", "Accept-Ranges,Content-Range");
            return ResponseEntity.status(HttpStatus.PARTIAL_CONTENT)
                    .headers(headers)
                    .contentType(MediaType.APPLICATION_PDF)
                    .body(resource);
        }
    } catch (IOException e) {
        throw new BaseException(ResponseCode.ERROR);
    }
}
```

其中关键代码是要设置 `Access-Control-Expose-Headers`，没设置这个的话我搞了好久都不能正常按需加载。

### 前端

```vue
<template>
    <div class="rounded-xl">
        <div id="pdf-container" class="w-full h-80vh rounded-xl"></div>
    </div>
</template>

<script lang="ts" setup>
import {initPdfView} from "@sunsetglow/vue-pdf-viewer";
import "@sunsetglow/vue-pdf-viewer/dist/style.css";
import {onMounted, ref, watchEffect} from "vue";
import {useRoute} from "vue-router"; // ① 引入 useRoute

const route = useRoute(); // ② 获取当前路由信息
const bookId = ref(route.params.id); // ③ 读取 bookId 参数

const loading = ref(false);
const isMobile = ref(window.innerWidth <= 768); // 监听窗口宽度

const pdfPath = new URL(
    "@sunsetglow/vue-pdf-viewer/dist/libs/pdf.worker.min.js",
    import.meta.url
).href;

// 监听窗口变化
const updateIsMobile = () => {
    isMobile.value = window.innerWidth <= 768;
};

// 监听页面变化
watchEffect(() => {
    window.addEventListener("resize", updateIsMobile);
});

// ④ 监听路由变化，动态更新 bookId
// watchEffect(() => {
//     bookId.value = route.params.bookId;
// });

onMounted(() => {
    const baseURL = import.meta.env.VITE_APP_INTERFACE_URL;
    loading.value = true;
    initPdfView(document.querySelector("#pdf-container") as HTMLElement, {
        // ⑤ 使用动态 bookId 加载 PDF
        loadFileUrl: `${baseURL}book/file/pdf?range=true&bookId=${bookId.value}`,
        pdfPath: pdfPath,
        loading: (load: boolean) => {
            loading.value = load;
        },
        pdfOption: {
            search: true,
            scale: true,
            pdfImageView: true,
            page: true,
            navShow: true,
            navigationShow: !isMobile.value, // 💡 在手机上隐藏左侧导航
            pdfViewResize: true,
            toolShow: true,
            download: true,
            clearScale: 1.5,
            fileName: "preview.pdf",
            lang: "en",
            print: true,
            customPdfOption: {
                cMapPacked: true,
                cMapUrl: "https://cdn.jsdelivr.net/npm/pdfjs-dist@2.2.228/cmaps/",
                rangeChunkSize: 1024 * 1024,
                disableRange: false,
                disableStream: true,
                disableAutoFetch: true,
            },
            textLayer: true,
        },
    });
});
</script>

<style scoped>
#pdf-container {
    overflow: hidden; /* 💡 让 PDF 内容不会超出容器 */
    border-radius: 12px; /* 💡 确保 PDF 容器本身有圆角 */
}
</style>
```

其中关键的代码是

```javascript
disableRange: false,
disableStream: true,
disableAutoFetch: true,
```

进行配置

