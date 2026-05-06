# Streamlit

[Streamlit](https://streamlit.io/) 的优势在于，它把“页面组件”和“Python 变量”直接连接起来。开发者不需要自己写 HTML、CSS、JavaScript，也不需要手写前后端接口。页面上的输入框、按钮、下拉框、上传组件，本质上都是 Python 函数调用；函数既负责在浏览器里渲染控件，也负责把用户输入返回给 Python 变量。这个模式极大降低了数据工具和 AI Demo 的开发成本，但它也带来了一套特殊的运行模型：脚本会反复 rerun，普通变量不能保存状态，耗时函数会反复执行，按钮只是瞬时事件。理解这些机制，是写好 Streamlit 的前提。

![Streamlit 标识](http://public.file.lvshuhuai.cn/images\streamlit-logo.svg)

## Streamlit 的基本定位与运行模型

Streamlit 可以理解为一种“Python 脚本驱动的 Web App 框架”。它适合做数据看板、模型 Demo、实验结果展示、LLM 评估页、文件上传处理工具、内部分析系统等。它不太适合直接替代完整的业务系统前端，也不适合承担复杂后端服务的职责。

![Streamlit 应用概览](http://public.file.lvshuhuai.cn/images\streamlit-docs-overview.jpg)

一个最小 Streamlit 应用通常长这样：

```python
import streamlit as st

st.title("我的第一个 Streamlit 页面")

name = st.text_input("请输入你的名字")

if name:
    st.write("你好，", name)

if st.button("提交"):
    st.success("按钮被点击了")
```

运行方式：

```powershell
uv run streamlit run app.py
```

或者：

```powershell
streamlit run app.py
```

运行后，Streamlit 会启动一个本地 Web 服务，并在浏览器中打开页面。此时 `app.py` 不再是普通终端脚本，而是浏览器页面的渲染逻辑。

### 组件返回 Python 变量

Streamlit 组件的共同模式是：

```python
value = st.xxx("显示给用户看的标签", 参数...)
```

例如：

```python
prompt = st.text_area("请输入 Prompt")
```

这行代码同时做了两件事：

- 在页面上显示一个多行输入框；
- 把用户输入的内容返回给 Python 变量 `prompt`。

所以 Streamlit 的开发方式不是传统前后端的“前端事件 → 请求后端接口 → 后端返回数据”，而是更直接的：

```text
页面组件 → 用户操作 → Python 变量 → Python 逻辑处理 → Streamlit 渲染结果
```

这也是它特别适合 AI/数据实验页面的原因。模型选择、参数滑块、文件上传、Prompt 输入，都可以直接变成 Python 变量。

### rerun：Streamlit 最核心的运行机制

Streamlit 最重要的机制是 rerun。用户打开页面、修改输入框、拖动滑块、点击按钮、上传文件时，Streamlit 通常会让 `app.py` 从上到下重新执行一次，然后根据当前组件状态重新渲染页面。

可以用一个实验观察：

```python
import streamlit as st
from datetime import datetime

st.title("观察 rerun")

st.write("脚本执行时间：", datetime.now().strftime("%H:%M:%S.%f"))

name = st.text_input("请输入名字")
st.write("name =", name)
```

每次输入内容后，页面上的“脚本执行时间”会变化。这说明不是某个局部组件单独刷新，而是整个脚本重新运行。

这个机制带来的结果是：

```text
用户操作组件
→ 触发 rerun
→ app.py 从第一行重新执行到最后一行
→ 普通变量重新初始化
→ widget 根据当前状态返回最新值
→ 页面重新渲染
```

因此，Streamlit 中的普通变量并不适合保存跨操作的状态。

### 普通变量为什么会丢失

看这个计数器：

```python
import streamlit as st

st.title("普通变量计数器")

count = 0

if st.button("加一"):
    count += 1

st.write("count =", count)
```

点击很多次，`count` 也不会稳定变成 2、3、4。因为每次点击按钮都会重新执行：

```python
count = 0
```

执行流程是：

```text
第一次打开页面：count = 0
点击按钮：rerun → count = 0 → button 返回 True → count += 1 → count = 1
再次点击按钮：rerun → count = 0 → button 返回 True → count += 1 → count = 1
```

所以普通变量只属于当前这一次脚本执行。下一次 rerun，它会重新初始化。

### button 是瞬时事件，不是持久开关

`st.button()` 返回的是“这一次脚本运行中，按钮是否刚刚被点击”。

```python
clicked = st.button("开始推理")
st.write("clicked =", clicked)
```

页面刚打开时，`clicked = False`。点击按钮触发的那一次 rerun 中，`clicked = True`。如果随后你又修改了一个输入框，页面再次 rerun，而这次按钮并没有被点击，所以 `clicked` 又会变回 `False`。

因此，按钮后的结果如果要保留，不能只存在普通变量里，而应该写入 `st.session_state`。

扩展阅读：[Streamlit architecture and execution model](https://docs.streamlit.io/develop/concepts/architecture/architecture)。

## 组件、数据展示与页面交互

Streamlit 的页面主要由输入组件和展示组件组成。输入组件负责把用户操作变成 Python 值，展示组件负责把 Python 数据渲染到页面上。

### 常用输入组件

常用组件及返回值可以概括如下：

| 组件               | 作用         | 返回值类型                |
| ------------------ | ------------ | ------------------------- |
| `st.text_input`    | 单行文本输入 | `str`                     |
| `st.text_area`     | 多行文本输入 | `str`                     |
| `st.number_input`  | 数值输入     | `int` 或 `float`          |
| `st.slider`        | 滑块         | `int` / `float` / 日期等  |
| `st.selectbox`     | 单选下拉框   | 一个选项值                |
| `st.radio`         | 单选按钮     | 一个选项值                |
| `st.multiselect`   | 多选         | `list`                    |
| `st.checkbox`      | 勾选框       | `bool`                    |
| `st.toggle`        | 开关         | `bool`                    |
| `st.file_uploader` | 文件上传     | `None` 或 `UploadedFile`  |
| `st.button`        | 按钮事件     | `bool`，仅点击那次为 True |

一个 LLM 参数面板可以这样写：

```python
import streamlit as st

st.title("LLM 参数面板")

model = st.selectbox(
    "选择模型",
    ["Qwen2.5-7B", "Qwen2.5-14B", "DeepSeek", "GPT"]
)

prompt = st.text_area("Prompt")
temperature = st.slider("temperature", 0.0, 2.0, 0.7, 0.1)
max_tokens = st.number_input("max_tokens", 1, 8192, 1024, 1)
stream = st.checkbox("启用流式输出")

if st.button("开始推理"):
    if not prompt:
        st.error("Prompt 不能为空")
    else:
        st.json({
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        })
```

这里没有真正调用模型，但已经形成了模型推理页面的基本结构：选择模型、输入 Prompt、设置参数、点击按钮、展示结果。

### 文件上传的基本模式

文件上传前，`uploaded_file` 是 `None`。上传后，它才是可读取的对象。所以必须判断：

```python
import pandas as pd
import streamlit as st

uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df, use_container_width=True)
else:
    st.info("请上传 CSV 文件")
```

错误写法是：

```python
uploaded_file = st.file_uploader("上传 CSV")
df = pd.read_csv(uploaded_file)  # 上传前 uploaded_file 是 None，会报错
```

### 数据展示组件

Streamlit 里不要所有内容都用 `st.write()`。不同类型的数据应该用更明确的组件：

| 场景            | 推荐组件         |
| --------------- | ---------------- |
| 普通文字、变量  | `st.write`       |
| 交互式表格      | `st.dataframe`   |
| 小型静态表格    | `st.table`       |
| 可编辑表格      | `st.data_editor` |
| 字典、JSON 配置 | `st.json`        |
| 指标卡片        | `st.metric`      |
| 趋势图          | `st.line_chart`  |
| 类别对比        | `st.bar_chart`   |
| Matplotlib 图   | `st.pyplot`      |

例如训练结果展示：

```python
import pandas as pd
import streamlit as st

st.title("训练结果展示")

df = pd.DataFrame({
    "epoch": [1, 2, 3, 4, 5],
    "loss": [0.92, 0.76, 0.58, 0.43, 0.31],
    "accuracy": [0.52, 0.63, 0.72, 0.81, 0.87],
    "f1": [0.48, 0.60, 0.70, 0.78, 0.85],
})

st.dataframe(df, use_container_width=True)

final_row = df.iloc[-1]
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Final Loss", final_row["loss"])
with col2:
    st.metric("Final Accuracy", f"{final_row['accuracy']:.2%}")
with col3:
    st.metric("Final F1", f"{final_row['f1']:.2%}")

st.line_chart(df, x="epoch", y="loss")
st.line_chart(df, x="epoch", y=["accuracy", "f1"])
```

对于模型评估工具，常见的数据展示组合是：

- 顶部用 `st.metric` 展示样本数、字段数、推理次数、准确率等；
- 主区域用 `st.dataframe` 展示上传数据、批量结果、历史记录；
- 用 `st.json` 展示请求参数、模型输出、调试信息；
- 用 `st.line_chart` 或 `st.bar_chart` 展示指标变化和模型对比。

![Streamlit 数据应用示例](http://public.file.lvshuhuai.cn/images\streamlit-demo-movies-screenshot.png)

## 状态管理：`st.session_state`

由于 Streamlit 会频繁 rerun，普通变量不能跨操作保存状态。[st.session_state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state) 用来保存当前用户会话中的状态。

它适合保存：

```text
当前用户的聊天记录
当前选择的样本
按钮点击后的推理结果
历史推理记录
上传文件的 bytes
批量评估结果摘要
当前页面临时配置
```

不适合保存：

```text
大模型本体
tokenizer
数据库连接
embedding model
过大的 DataFrame
大型图片、视频、WSI 特征
```

这些资源更适合缓存机制，尤其是 `st.cache_resource`。

### 标准初始化写法

使用 `session_state` 前，必须先初始化：

```python
import streamlit as st

if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("加一"):
    st.session_state.count += 1

st.write("count =", st.session_state.count)
```

也可以用字典写法：

```python
if "count" not in st.session_state:
    st.session_state["count"] = 0
```

这两种写法都可以。属性写法简洁，字典写法适合 key 名来自变量或包含特殊字符的情况。

### 保存按钮结果

错误写法：

```python
prompt = st.text_area("Prompt")

if st.button("开始推理"):
    result = "模型输出：" + prompt
    st.success(result)
```

这个结果只在点击按钮触发的那一次 rerun 中显示。如果之后修改输入框，结果会消失。

正确写法：

```python
if "result" not in st.session_state:
    st.session_state.result = ""

prompt = st.text_area("Prompt")

if st.button("开始推理"):
    st.session_state.result = "模型输出：" + prompt

if st.session_state.result:
    st.subheader("推理结果")
    st.success(st.session_state.result)
else:
    st.info("还没有推理结果")
```

### 保存历史记录

推理历史可以用列表保存：

```python
from datetime import datetime
import streamlit as st

if "history" not in st.session_state:
    st.session_state.history = []

prompt = st.text_area("Prompt")

if st.button("开始推理"):
    if prompt:
        record = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "prompt": prompt,
            "output": "模拟输出：" + prompt,
        }
        st.session_state.history.append(record)

for item in st.session_state.history:
    with st.expander(f"{item['time']} - 推理记录"):
        st.json(item)
```

聊天记录也类似。核心结构是：

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("请输入内容")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": "模拟回复：" + prompt})
    st.rerun()
```

### widget key 与 session_state

给 widget 指定 `key` 后，可以通过 `st.session_state` 访问它：

```python
st.text_input("请输入名字", key="name")
st.write(st.session_state.name)
```

注意 Python 变量名和 widget key 不是一回事：

```python
slider_value = st.slider("数值", 0, 100, 50, key="my_slider")
```

此时：

```python
st.session_state.my_slider
```

才是 widget key 对应的值，`slider_value` 只是当前脚本运行中的普通 Python 变量。

复杂页面和多页面应用中，重要组件建议显式指定 key，例如：

```python
model_name = st.selectbox("模型", models, key="inference_model_name")
temperature = st.slider("temperature", 0.0, 2.0, 0.7, key="inference_temperature")
```

![Session State 未初始化异常示例](http://public.file.lvshuhuai.cn/images\streamlit-session-state-exception.png)

## 缓存：`st.cache_data` 与 `st.cache_resource`

Streamlit rerun 带来的另一个问题是：耗时函数会反复执行。如果每次输入框变化都重新读取 CSV、重新连接数据库、重新加载模型，页面会非常慢。缓存机制就是为了解决这个问题。

简单区分：

| 机制                | 解决什么问题     | 典型内容                                |
| ------------------- | ---------------- | --------------------------------------- |
| `st.session_state`  | 当前用户会话状态 | 聊天记录、当前结果、历史记录            |
| `st.cache_data`     | 缓存数据计算结果 | DataFrame、dict、list、查询结果         |
| `st.cache_resource` | 缓存资源对象     | 模型、tokenizer、数据库连接、API client |

![Streamlit 缓存机制概览](http://public.file.lvshuhuai.cn/images\streamlit-caching-high-level-diagram.png)

### `st.cache_data`：缓存数据结果

`st.cache_data` 适合缓存返回数据的函数。例如读取 CSV：

```python
import io
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="正在读取 CSV...")
def load_csv_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes))

uploaded_file = st.file_uploader("上传 CSV", type=["csv"])

if uploaded_file is not None:
    df = load_csv_from_bytes(uploaded_file.getvalue())
    st.dataframe(df, use_container_width=True)
```

这里推荐传入 `file_bytes`，而不是直接把 `UploadedFile` 对象传进缓存函数。bytes 更稳定，也更容易被缓存机制识别。

`st.cache_data` 缓存的是“函数在某组参数下的返回值”。如果参数不变，后续 rerun 会直接返回缓存结果；如果参数变化，则重新执行函数。

例如：

```python
@st.cache_data
def compute_square(x: int) -> dict:
    return {"x": x, "square": x * x}
```

`compute_square(2)` 和 `compute_square(3)` 会分别缓存。

常用参数：

```python
@st.cache_data(ttl=3600, max_entries=100)
def query_data(...):
    ...
```

- `ttl`：缓存有效时间；
- `max_entries`：最多保存多少条缓存记录；
- `func.clear()`：清空某个函数的缓存；
- `st.cache_data.clear()`：清空全部 data cache。

![Streamlit 清理缓存入口](http://public.file.lvshuhuai.cn/images\streamlit-clear-cache.png)

### `st.cache_resource`：缓存资源对象

模型、数据库连接、OpenAI-compatible client 这类对象不应该每次 rerun 都重新创建。它们属于资源对象，应该用 `st.cache_resource`。

```python
import time
from datetime import datetime
import streamlit as st

class FakeModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.loaded_at = datetime.now().strftime("%H:%M:%S")

    def predict(self, text: str):
        return f"{self.model_name} 输出：{text}"

@st.cache_resource(show_spinner="正在加载模型...")
def load_model(model_name: str) -> FakeModel:
    time.sleep(2)
    return FakeModel(model_name)

model = load_model("Qwen2.5-7B")
```

同一个 `model_name` 会复用同一个模型对象。切换 `model_name` 时，参数变化，缓存会创建新的资源。

要注意：`st.cache_resource` 返回的是共享对象本体，不是副本。如果你对返回对象做原地修改，修改会影响缓存中的对象。因此，普通 DataFrame 更适合 `st.cache_data`，不要随意用 `st.cache_resource` 缓存后再 `inplace=True` 修改。

### 数据库和 API 的典型缓存模式

数据库连接和查询结果应该分开：

```python
@st.cache_resource
def get_db_engine():
    return create_engine(...)

@st.cache_data(ttl=3600)
def query_users(_engine, limit: int):
    return pd.read_sql(f"select * from users limit {limit}", _engine)
```

`_engine` 前面的下划线表示这个参数不参与缓存 hash。对于不可 hash 或不应该参与缓存 key 的对象，可以用这种写法。

LLM 项目也类似：

```python
@st.cache_resource
def get_llm_client(api_key: str, base_url: str):
    return OpenAI(api_key=api_key, base_url=base_url)
```

是否缓存 LLM 输出要谨慎。因为 temperature、模型版本、隐私数据、随机采样都会影响是否应该复用结果。默认更稳的做法是缓存 client，不缓存推理输出。

## 页面组织：布局与多页面结构

当页面变复杂时，不应把所有内容从上到下堆在一个 `app.py` 里。Streamlit 提供了侧边栏、列布局、标签页、折叠面板、容器和多页面机制。

### 单页面布局

常用布局组件：

| 组件           | 用途                                   |
| -------------- | -------------------------------------- |
| `st.sidebar`   | 侧边栏，放参数和控制项                 |
| `st.columns`   | 横向布局，适合指标卡片或左右对比       |
| `st.tabs`      | 内容分区，适合数据、推理、指标、历史   |
| `st.expander`  | 折叠细节，适合 JSON、日志、原始 Prompt |
| `st.container` | 组织一组元素                           |
| `st.empty`     | 动态占位、状态更新                     |

一个模型评估页面可以组织为：

```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="模型评估工具", layout="wide")
st.title("模型评估工具")

with st.sidebar:
    model = st.selectbox("模型", ["A", "B", "C"])
    temperature = st.slider("temperature", 0.0, 2.0, 0.7)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("样本数", 100)
with col2:
    st.metric("当前模型", model)
with col3:
    st.metric("历史推理次数", 5)

tab_data, tab_infer, tab_history = st.tabs(["数据预览", "样本推理", "推理历史"])

with tab_data:
    st.write("这里展示数据表")

with tab_infer:
    prompt = st.text_area("Prompt")
    if st.button("开始推理"):
        st.success(f"{model} 输出：{prompt}")

with tab_history:
    st.write("这里展示历史记录")
```

一个重要细节是：`st.tabs` 并不是“点哪个 tab 才执行哪个 tab 的代码”。tab 内的内容通常都会执行和发送到前端。因此，耗时逻辑仍然要用按钮、表单和缓存控制，而不能只靠 tab 隔离。

### 多页面结构

对于稍微正式的工具，推荐使用 [st.Page + st.navigation](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation)。

![Streamlit 多页面 set_page_config 示例](http://public.file.lvshuhuai.cn/images\streamlit-multipage-set-page-config.jpg)

项目结构：

```text
streamlit-eval-tool/
  app.py
  services/
    data_service.py
    model_service.py
    metric_service.py
  views/
    home.py
    upload.py
    inference.py
    batch_eval.py
    metrics.py
    history.py
```

入口文件 `app.py`：

```python
import streamlit as st

st.set_page_config(
    page_title="Streamlit 模型评估工具",
    page_icon="🧪",
    layout="wide",
)

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

if "uploaded_file_bytes" not in st.session_state:
    st.session_state.uploaded_file_bytes = None

if "current_result" not in st.session_state:
    st.session_state.current_result = None

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.title("🧪 模型评估工具")
    if st.session_state.uploaded_file_name:
        st.success(f"已上传：{st.session_state.uploaded_file_name}")
    else:
        st.warning("尚未上传数据")

pages = [
    st.Page("views/home.py", title="首页", icon="🏠"),
    st.Page("views/upload.py", title="数据上传", icon="📄"),
    st.Page("views/inference.py", title="样本推理", icon="🧪"),
    st.Page("views/batch_eval.py", title="批量评估", icon="📦"),
    st.Page("views/metrics.py", title="指标统计", icon="📊"),
    st.Page("views/history.py", title="推理历史", icon="🕘"),
]

page = st.navigation(pages)
page.run()
```

关键点：

- `app.py` 是入口，也是公共 frame；
- 公共 `session_state` 初始化放在入口；
- 页面文件放在 `views/`；
- 业务逻辑放在 `services/`；
- `st.navigation()` 返回当前页面对象，必须调用 `page.run()`。

![Streamlit 多页面分区示例](http://public.file.lvshuhuai.cn/images\streamlit-multipage-page-sections.jpg)

多页面之间共享数据，主要依赖 `st.session_state`。例如上传页写入：

```python
st.session_state.uploaded_file_bytes = uploaded_file.getvalue()
```

推理页读取：

```python
df = get_uploaded_dataframe()
```

## 模型评估工具的核心工程实现

一个可用的模型评估工具，至少应该包括：数据上传、样本推理、真实 LLM API 调用、批量评估、指标计算、结果导出和错误日志。下面把这些模块按工程逻辑整理出来。

### 数据服务

`services/data_service.py` 负责读取上传文件和提取列信息：

```python
import io
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="正在读取 CSV 数据...")
def load_csv_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes))


def get_uploaded_dataframe() -> pd.DataFrame | None:
    file_bytes = st.session_state.get("uploaded_file_bytes")
    if file_bytes is None:
        return None
    return load_csv_from_bytes(file_bytes)


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["int64", "float64"]).columns.tolist()


def get_text_like_columns(df: pd.DataFrame) -> list[str]:
    text_columns = df.select_dtypes(include=["object", "string"]).columns.tolist()
    return text_columns if text_columns else df.columns.tolist()
```

这里把上传文件 bytes 存在 `session_state`，而 DataFrame 读取结果用 `cache_data`。这样多页面都能访问数据，又避免重复读取。

### OpenAI-compatible LLM Client

第 9 课将 `FakeModel` 替换为真实 OpenAI-compatible API。服务层可以写成：

```python
import os
import time
from datetime import datetime
from typing import Any

import streamlit as st
from openai import OpenAI


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name
        self.loaded_at = datetime.now().strftime("%H:%M:%S")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def predict(
        self,
        text: str,
        temperature: float,
        max_tokens: int,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        if not system_prompt:
            system_prompt = "你是一个严谨的模型评估助手。"

        started_at = time.time()

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        elapsed_ms = int((time.time() - started_at) * 1000)
        output = response.choices[0].message.content or ""

        usage = None
        if getattr(response, "usage", None) is not None:
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", None),
                "completion_tokens": getattr(response.usage, "completion_tokens", None),
                "total_tokens": getattr(response.usage, "total_tokens", None),
            }

        return {
            "provider": "openai-compatible",
            "base_url": self.base_url,
            "model": self.model_name,
            "client_loaded_at": self.loaded_at,
            "input": text,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "output": output,
            "elapsed_ms": elapsed_ms,
            "usage": usage,
        }


@st.cache_resource(show_spinner="正在初始化 LLM Client...")
def load_model(model_name: str, base_url: str, api_key: str) -> LLMClient:
    return LLMClient(api_key=api_key, base_url=base_url, model_name=model_name)


def get_llm_config_from_env() -> dict[str, str]:
    api_key = (
        os.getenv("LLM_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("DASHSCOPE_API_KEY")
    )

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("LLM_MODEL", "gpt-5.5")

    if not api_key:
        raise RuntimeError("未找到 API Key。请设置 LLM_API_KEY。")

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model_name": model_name,
    }
```

PowerShell 临时配置示例：

```powershell
$env:LLM_API_KEY="你的 API Key"
$env:LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qwen-plus"
```

API Key 不应该放在页面输入框中，也不应该写死在代码里。推荐放在环境变量或 `.env` 中。页面可以显示和修改 `base_url`、`model_name`，但不显示 API Key。

### 批量推理与分类指标

批量评估的结构是：

```text
选择输入文本列
选择真实标签列
读取候选标签
构造分类 prompt
逐行调用 LLM
解析预测标签
保存结果表
计算 Accuracy / Macro-F1 / Weighted-F1 / classification_report
```

分类任务中，Prompt 应该强约束模型输出：

```text
你是一个严格的文本分类器。

你的任务：
根据用户输入文本，从候选标签中选择一个最合适的标签。

候选标签：
['positive', 'negative', 'neutral']

输出要求：
1. 只能输出一个标签。
2. 输出必须来自候选标签。
3. 不要解释。
4. 不要输出 JSON。
5. 不要输出多余文字。
```

`temperature` 建议设为 0，`max_tokens` 建议设小，例如 16 或 32。分类任务不需要长文本生成，目标是稳定输出标签。

标签解析函数可以这样设计：

```python
import re
from typing import Any


def normalize_label(value: Any) -> str:
    text = str(value).strip()
    text = text.strip("\"'`“”‘’")
    text = re.sub(r"[。.!！,，;；:：]+$", "", text)
    return text.lower().strip()


def parse_prediction_label(raw_output: str, allowed_labels: list[str]) -> str:
    normalized_output = normalize_label(raw_output)
    normalized_label_map = {
        normalize_label(label): str(label)
        for label in allowed_labels
    }

    if normalized_output in normalized_label_map:
        return normalized_label_map[normalized_output]

    for normalized_label, original_label in normalized_label_map.items():
        if normalized_label and normalized_label in normalized_output:
            return original_label

    return normalized_output
```

指标计算：

```python
from sklearn.metrics import accuracy_score, classification_report, f1_score


def compute_classification_metrics(y_true: list[str], y_pred: list[str]) -> dict:
    y_true_norm = [normalize_label(x) for x in y_true]
    y_pred_norm = [normalize_label(x) for x in y_pred]

    accuracy = accuracy_score(y_true_norm, y_pred_norm)
    macro_f1 = f1_score(y_true_norm, y_pred_norm, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true_norm, y_pred_norm, average="weighted", zero_division=0)

    report_dict = classification_report(
        y_true_norm,
        y_pred_norm,
        zero_division=0,
        output_dict=True,
    )

    report_text = classification_report(
        y_true_norm,
        y_pred_norm,
        zero_division=0,
    )

    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "classification_report_dict": report_dict,
        "classification_report_text": report_text,
    }
```

Accuracy 表示预测正确比例。Macro-F1 对每个类别的 F1 做简单平均，能反映模型对少数类的表现。Weighted-F1 按各类别样本数量加权，类别不平衡时更接近整体表现。

### 结果导出与保存

批量结果不能只留在页面上。常见导出格式：

| 格式  | 适合内容                       |
| ----- | ------------------------------ |
| CSV   | 表格结果，方便 Excel 打开      |
| JSONL | 一行一个样本，适合程序继续处理 |
| JSON  | 指标摘要、配置、历史元信息     |

导出服务：

```python
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def dataframe_to_jsonl_bytes(df: pd.DataFrame) -> bytes:
    text = df.to_json(orient="records", lines=True, force_ascii=False)
    return text.encode("utf-8")


def dict_to_json_bytes(data: dict[str, Any]) -> bytes:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str).encode("utf-8")


def make_timestamp_filename(prefix: str, suffix: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{suffix}"


def save_bytes_to_outputs(file_name: str, data: bytes) -> Path:
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / file_name
    file_path.write_bytes(data)
    return file_path
```

页面下载按钮：

```python
st.download_button(
    label="下载结果 CSV",
    data=csv_bytes,
    file_name="batch_results.csv",
    mime="text/csv",
)
```

要区分下载和保存：

```text
st.download_button：浏览器下载，文件在用户电脑上
Path.write_bytes：服务器本地保存，文件在运行 Streamlit 的机器上
```

如果 Streamlit 在远程服务器上运行，`outputs/` 目录也在远程服务器，不在本地电脑。

## 错误处理、日志与进度条

批量任务不能只写一个简单 `for` 循环。真实批量评估里，API 可能失败、网络可能超时、模型可能输出非法标签、某条样本可能为空、服务商可能限流。一个稳一点的批量任务至少要有：

```text
progress：让用户知道任务执行到哪里
status：显示当前处理状态
try-except：单条失败不影响整体
errors：记录失败样本
logger：把详细信息写入日志文件
```

### 日志服务

`services/log_service.py`：

```python
from __future__ import annotations

import logging
from pathlib import Path


def get_app_logger() -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("streamlit_eval_tool")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_file = log_dir / "app.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def read_recent_logs(max_lines: int = 100) -> str:
    log_file = Path("logs/app.log")
    if not log_file.exists():
        return ""

    lines = log_file.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[-max_lines:])
```

日志等级建议：

| 日志等级           | 使用场景                               |
| ------------------ | -------------------------------------- |
| `logger.info`      | 正常事件：任务开始、样本完成、任务结束 |
| `logger.warning`   | 可疑但不致命：输出为空、标签解析失败   |
| `logger.error`     | 明确错误                               |
| `logger.exception` | 捕获异常时使用，会记录 traceback       |

### 批量循环中的错误处理

批量循环应当像这样组织：

```python
progress_bar = st.progress(0, text="批量推理准备中...")
status_area = st.empty()
logger = get_app_logger()

total = len(rows)
results = []
errors = []

logger.info("Batch eval started | samples=%s", total)

with st.status("批量推理运行中...", expanded=True) as status:
    for i, row in rows.iterrows():
        original_index = int(row["index"])
        input_text = str(row[text_column])
        true_label = str(row[label_column])

        current_no = i + 1
        progress_bar.progress(
            current_no / total,
            text=f"正在处理第 {current_no}/{total} 条样本..."
        )

        status.write(f"正在处理原始行号：{original_index}")
        status_area.info(f"当前样本原始行号：{original_index}")

        try:
            result = model.predict(
                text=input_text,
                temperature=float(temperature),
                max_tokens=int(max_tokens),
                system_prompt=system_prompt,
            )

            raw_output = result["output"]
            pred_label = parse_prediction_label(raw_output, allowed_labels)

            is_correct = (
                str(true_label).strip().lower()
                == str(pred_label).strip().lower()
            )

            results.append({
                "original_index": original_index,
                "input": input_text,
                "true_label": true_label,
                "raw_output": raw_output,
                "pred_label": pred_label,
                "is_correct": is_correct,
                "model": result["model"],
                "elapsed_ms": result.get("elapsed_ms"),
                "usage": result.get("usage"),
            })

            logger.info(
                "Sample done | original_index=%s | pred_label=%s | correct=%s",
                original_index,
                pred_label,
                is_correct,
            )

        except Exception as e:
            logger.exception(
                "Sample failed | original_index=%s | true_label=%s",
                original_index,
                true_label,
            )

            errors.append({
                "original_index": original_index,
                "input": input_text,
                "true_label": true_label,
                "error": repr(e),
            })

            results.append({
                "original_index": original_index,
                "input": input_text,
                "true_label": true_label,
                "raw_output": "",
                "pred_label": "__ERROR__",
                "is_correct": False,
                "model": model_name,
                "elapsed_ms": None,
                "usage": None,
            })

    status.update(label="批量推理完成", state="complete", expanded=False)

progress_bar.progress(1.0, text="批量推理完成")
status_area.success("批量推理完成")
logger.info("Batch eval completed | samples=%s | errors=%s", total, len(errors))
```

这个结构保证一条样本失败不会导致整个批量任务中断。

页面底部可以显示最近日志：

```python
with st.expander("查看最近日志"):
    recent_logs = read_recent_logs(max_lines=80)
    if recent_logs:
        st.code(recent_logs, language="text")
    else:
        st.info("暂无日志。")
```

如果是调试阶段，需要直接展示异常，可以用：

```python
st.exception(e)
```

但正式批量任务里，不建议每条失败都在页面上展开完整 traceback。更好的方式是错误表展示摘要，日志文件保存详细信息。

## 常见问题与工程判断

### 什么时候用 `session_state`，什么时候用 cache

一个简单判断：

```text
这个东西是当前用户正在操作的临时状态吗？
→ 用 session_state

这个东西是重复计算很慢、可以复用的结果吗？
→ 用 cache_data

这个东西是模型、连接、client 这类资源对象吗？
→ 用 cache_resource
```

例如：

| 内容                 | 推荐机制                                             |
| -------------------- | ---------------------------------------------------- |
| 当前上传文件名       | `session_state`                                      |
| 当前上传文件 bytes   | `session_state`                                      |
| 读取出的 DataFrame   | `cache_data`                                         |
| 当前推理结果         | `session_state`                                      |
| 推理历史摘要         | `session_state`                                      |
| OpenAI SDK client    | `cache_resource`                                     |
| tokenizer / 本地模型 | `cache_resource`                                     |
| 批量评估结果表       | 小规模可放 `session_state`，大规模应保存文件或数据库 |

### 为什么不要把所有东西都塞进 `app.py`

页面文件应该负责 UI，业务逻辑应该拆出去。推荐分层：

```text
app.py：入口、导航、公共初始化
views/：页面展示与用户输入
services/：数据读取、模型调用、指标计算、导出、日志
outputs/：导出结果
logs/：运行日志
```

页面函数中只做三件事：

```text
1. 读取用户输入
2. 调用 service
3. 展示结果
```

这样后续改模型服务、改指标算法、加导出格式，都不需要大改页面。

### OpenAI-compatible API 的常见错误

| 错误                          | 常见原因                                           |
| ----------------------------- | -------------------------------------------------- |
| `ModuleNotFoundError: openai` | 没安装 `openai` SDK                                |
| 未找到 API Key                | 没设置 `LLM_API_KEY`                               |
| 401 Unauthorized              | Key 错、服务商不匹配、Key 过期                     |
| 404 model not found           | 模型名错误或模型不属于当前 base_url                |
| 429                           | 服务商限流                                         |
| 输出不是标签                  | Prompt 约束不足，temperature 太高，max_tokens 太大 |

分类评估时，建议：

```text
temperature = 0.0
max_tokens = 16 或 32
Prompt 强制“只能输出候选标签之一”
解析失败时标记为 __INVALID__ 或 __ERROR__
```

### 下载与服务器保存的区别

`st.download_button` 是让浏览器下载文件。文件在用户电脑上。

`Path.write_bytes()` 是写入运行 Streamlit 的机器。文件在服务器上。

本地开发时，二者看起来都在你电脑上；一旦部署到远程服务器，它们就完全不同。

### 批量任务的边界

当前 Streamlit 批量评估页面是同步任务。也就是说，点击按钮后，页面会一直执行循环，直到所有样本处理完。进度条可以显示状态，但它不是后台任务。

如果样本很多、API 调用很慢、要支持多人使用，就应该考虑后端任务队列，例如：

```text
FastAPI + Celery / RQ
数据库保存任务状态
Streamlit 只负责提交任务和查看进度
```

但对于小规模实验、模型评估 Demo、内部工具，同步批量循环已经足够。
