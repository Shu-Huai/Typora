# 04 multipart 请求

查询参数走 URL，JSON 请求体走 application/json。表单和文件上传走的是第三种编码：multipart/form-data 与 application/x-www-form-urlencoded。本章覆盖 Form 表单字段、File 与 UploadFile 文件上传、两者组合的完整场景。

本章环境约定：Python 3.10 以上，FastAPI 0.100 以上。命令以 Windows PowerShell 为例，macOS、Linux 的 curl 用法相同。

## 表单参数

表单编码常出现在两个场景：浏览器原生 form 标签提交，以及 OAuth2 密码登录。FastAPI 用 **Form** 声明表单字段，用法与 Query、Path 几乎相同，区别只是数据来源。

先装依赖：

```powershell
pip install python-multipart
```

这个包不随 FastAPI 自动安装。漏装时接口一被访问，服务端立刻报错，原文如下：

```
RuntimeError: Form data requires "python-multipart" to be installed. 
You can install "python-multipart" with: 

pip install python-multipart
```

最小示例：

```python
from fastapi import FastAPI, Form

app = FastAPI()


@app.post("/submit/")
def submit(name: str = Form(...), age: int = Form(ge=18, le=120), memo: str | None = Form(default=None)):
    return {"name": name, "age": age, "memo": memo}
```

PowerShell 发送表单请求：

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/submit/ `
    -Method Post -Body @{ name = "张三"; age = 25 } `
    -ContentType "application/x-www-form-urlencoded"
    # 输出：name=张三  age=25
```

curl 写法：

```bash
curl -X POST http://127.0.0.1:8000/submit/ \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "name=张三&age=25"
```

中文、空格这类字符在表单编码里必须做百分号编码，Invoke-RestMethod 的哈希表写法会自动处理，curl -d 手写字符串时用 --data-urlencode 更省心：

```bash
curl -X POST http://127.0.0.1:8000/submit/ \
     -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "name=张三" \
     --data-urlencode "age=25"
```

服务端拿到的仍是解码后的原始值，编码只发生在传输层。

Form(...) 里的三个点表示必填。表单字段和 JSON 请求体不能出现在同一个路径操作里：声明了 Form 的接口按表单编码解析，声明了 Pydantic 模型的接口按 JSON 解析，两者混用 FastAPI 会拒绝。文件上传是例外，File 与 Form 可以共存，原因在组合场景一节展开。

第 09 章的 OAuth2 登录预览：FastAPI 内置的 OAuth2PasswordRequestForm 内部就是把 username、password 声明成 Form 字段，再包装一层 Pydantic 校验。登录表单的写法与本节完全同源，届时看到它不会陌生。

### 校验规则

表单字段的校验手段与查询参数相同，min_length、pattern、gt 全部适用：

```python
from fastapi import FastAPI, Form

app = FastAPI()


@app.post("/register/")
def register(
    username: str = Form(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$"),
    password: str = Form(min_length=8),
):
    return {"username": username, "password_length": len(password)}
```

密码不足 8 位时返回 422，结构与 JSON 请求体校验失败完全一致，loc 同样指向 body：

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "abc123"
    }
  ]
}
```

表单校验失败的排查方式与请求体相同：先看 loc 定位字段，再看 msg 确认规则。

## 文件上传

文件上传依赖 multipart 编码。请求体被 boundary 分隔成多个 part，表单字段是纯文本 part，文件 part 额外携带 filename 属性。

![](Z:\Public\images\fastapi-form-file.png)

上图展示了一个 multipart 请求的分包结构：每个 part 以 --boundary 开头，Content-Disposition 声明字段名与文件名。FastAPI 解析时靠每个 part 的 name 与路径操作函数的参数名匹配。

文件参数有两种声明方式。**File** 声明 bytes 类型，框架把整份文件内容读进内存再交给函数；**UploadFile** 是 Starlette 提供的异步文件句柄，函数内按需读取：

```python
from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/upload/bytes/")
def upload_bytes(file: bytes = File(...)):
    return {"size": len(file)}


@app.post("/upload/async/")
async def upload_async(file: UploadFile = File(...)):
    data = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(data),
    }
```

UploadFile 自带两个属性：**filename** 是客户端上传的原始文件名，**content_type** 是 MIME 类型，例如 image/png。read 方法是异步的，函数必须声明成 async def。

两种方式对比：

| 维度 | File | UploadFile |
|---|---|---|
| 参数类型 | bytes | UploadFile |
| 读取时机 | 框架预先全部读入内存 | 函数内按需读取 |
| 内存占用 | 至少等于文件体积 | 只占已读部分 |
| 适用场景 | 小文件，如头像、小图标 | 大文件，如视频、压缩包 |
| 自带属性 | 无 | filename、content_type |
| 底层封装 | 一次性 bytes | SpooledTemporaryFile |

### 测试命令

两个接口都可用 curl -F 验证，-F 会让 curl 自动切换成 multipart/form-data 编码：

```bash
curl -X POST http://127.0.0.1:8000/upload/bytes/ \
     -F "file=@./logo.png"

curl -X POST http://127.0.0.1:8000/upload/async/ \
     -F "file=@./logo.png;type=image/png"
```

-F 里的 type= 用于显式指定 MIME 类型，省略时 curl 按文件扩展名推断。Windows PowerShell 的 curl 是 curl.exe 的别名，参数用法与 Linux 一致。PowerShell 5.1 的 Invoke-RestMethod 没有 -Form 参数，多文件表单直接用 curl.exe 更简单。

### 分块读取

大文件一次读完会把内存顶爆。UploadFile 支持按块读取，配合 pathlib 保存到磁盘：

```python
from pathlib import Path

from fastapi import FastAPI, File, UploadFile

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    safe_name = Path(file.filename or "unnamed").name
    dest = UPLOAD_DIR / safe_name
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)
    return {"filename": safe_name, "size": dest.stat().st_size}
```

`Path(file.filename).name` 只保留文件名最后一段，客户端传 ../../etc/passwd 这类路径穿越字符串会被剥掉目录部分，这是文件保存前必须做的一步。

UploadFile 底层是 SpooledTemporaryFile，小文件驻留内存，超过阈值自动落到临时文件。read 到末尾后再调 file.seek(0) 可以回到开头重新读取，处理完成后框架负责关闭底层句柄，显式 await file.close() 属于可选动作。

文件大小限制在读取过程中检查，超限立刻中止并返回 413：

```python
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI()

MAX_SIZE = 10 * 1024 * 1024  # 10 MB


@app.post("/upload/limited/")
async def upload_limited(file: UploadFile = File(...)):
    total = 0
    chunks = []
    while chunk := await file.read(1024 * 1024):
        total += len(chunk)
        if total > MAX_SIZE:
            raise HTTPException(status_code=413, detail="文件超过 10 MB 上限")
        chunks.append(chunk)
    return {"size": total}
```

服务端校验永远只是兜底，真正挡住超大文件的应该是反向代理的请求体大小限制。

## 组合场景

文件上传几乎总是伴随元数据：标题、分类、描述。File 与 Form 在同一个路径操作里混用是官方支持的：

```python
from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI()


@app.post("/photo/")
async def upload_photo(
    title: str = Form(...),
    tag: str = Form(default="默认"),
    file: UploadFile = File(...),
):
    return {"title": title, "tag": tag, "filename": file.filename}
```

> 官方文档原文：“You can define files and form fields at the same time, using File and Form.” 大意是：同一个路径操作里可以同时声明文件和表单字段，分别使用 File 与 Form。

多个文件用 list 泛型声明：

```python
@app.post("/gallery/")
async def upload_many(files: list[UploadFile] = File(...)):
    names = []
    for f in files:
        names.append(f.filename)
    return {"count": len(files), "names": names}
```

多文件请求里 file 字段重复出现，FastAPI 会把它们收集进列表。文件数量很大时循环里逐个按块读取，避免一次性全读进内存。

带元数据的请求用多个 -F 拼装，字段顺序无关紧要：

```bash
curl -X POST http://127.0.0.1:8000/photo/ \
     -F "title=周末爬山" \
     -F "tag=风景" \
     -F "file=@./photo.jpg"
```

表单字段和文件字段混在同一个 multipart 请求里，FastAPI 按参数名分发：字符串字段进 Form 参数，文件进 UploadFile 参数。

### 静态文件挂载

文件保存到磁盘后还需要一个可访问的 URL。**StaticFiles** 把目录挂载到路径前缀：

```python
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.staticfiles import StaticFiles

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/profile/")
async def profile(
    nickname: str = Form(min_length=2, max_length=20),
    avatar: UploadFile = File(...),
):
    ext = Path(avatar.filename or "").suffix or ".bin"
    saved = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    with saved.open("wb") as out:
        while chunk := await avatar.read(1024 * 1024):
            out.write(chunk)
    return {"nickname": nickname, "avatar_url": f"/static/{saved.name}"}


app.mount("/static", StaticFiles(directory="uploads"), name="static")
```

文件名用 uuid 重建，同时避开重名覆盖与路径穿越两个问题。返回的 avatar_url 可以直接拼上域名给前端使用。挂载语句写在所有路由之后，路由优先级高于挂载，同名路径会先命中路由。

StaticFiles 的 directory 必须在启动时存在，示例里 UPLOAD_DIR.mkdir(exist_ok=True) 就是为此准备。name 参数是挂载的标识符，反向生成 URL 时配合 url_for 使用，字符串写错不影响访问，只影响 url_for 的结果。

## 练手题

1. 不安装 python-multipart，启动一个 Form 接口并访问，把服务端抛出的 RuntimeError 原文记录下来。
2. 写一个接收头像的 UploadFile 接口，保存前打印 file.filename 与 file.content_type，用 curl -F 上传两种不同格式的文件对比。
3. 实现带 5 MB 上限的分块上传，分别上传小于与大于上限的文件，验证 413 响应。
4. 把头像的保存目录挂载到 /static，浏览器打开返回的 URL 确认图片能显示。
5. 实现一个多文件接口，一次上传三个文件，检查返回列表长度与顺序。

multipart 常见坑：

- 忘记装 python-multipart，接口访问时直接 500。
- 表单接口却按 JSON 发送请求体，返回 422。
- 大文件用 File 声明，内存占用等于文件完整副本。
- 直接用 file.filename 拼保存路径，被路径穿越。
- 客户端多个字段重名，后端想全收却只声明了单个参数。
