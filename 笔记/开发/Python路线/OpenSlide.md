# OpenSlide

## OpenSlide 是什么

OpenSlide 是一个用于读取多种全图显微镜图像格式（WSI, Whole Slide Image）的 C 语言库，常与 Python 配合使用进行数字病理图像处理。

## 安装

使用 pip 包管理器安装

```bash
pip install openslide-python
pip install openslide-bin
```

## 官方文档

https://openslide.org/api/python/

## 图像格式支持

OpenSlide 支持以下格式（如果依赖库支持）

- `.svs` (Aperio)
- `.ndpi` (Hamamatsu)
- `.scn` (Leica)
- `.mrxs` (3DHISTECH)
- `.vms`, `.vmu` (Mirax)
- `.tiff` (Philips 等使用的 WSI TIFF)

## 使用

### 加载切片图像

```python
import openslide

# 加载 svs/tiff 文件
slide = openslide.OpenSlide('path/to/image.svs')

# 获取切片的基本信息
print(slide.level_dimensions)   # 每层的尺寸
print(slide.level_downsamples) # 每层的缩放因子
print(slide.properties)        # 元数据（如扫描仪型号、放大倍数等）
```

### 读取区域图像

```python
# 读取某个位置的一块区域，单位是像素（左上角坐标），原始层级 level=0
region = slide.read_region((x, y), level=0, size=(512, 512))

# 转换为 numpy 数组
import numpy as np
np_img = np.array(region)
```

### 查看缩略图

```python
thumbnail = slide.get_thumbnail((1024, 1024))
thumbnail.show()
```

### 常用属性与方法

| 方法 / 属性                          | 说明                                       |
| ------------------------------------ | ------------------------------------------ |
| `read_region(location, level, size)` | 从指定层级读取图像区域，返回 PIL 图像      |
| `get_thumbnail(size)`                | 获取缩略图                                 |
| `level_dimensions`                   | 每层图像的尺寸（从高分辨率到底）           |
| `level_count`                        | 层级数量                                   |
| `level_downsamples`                  | 每层相对于 level 0 的缩放比例              |
| `properties`                         | 图像的元数据信息（字典）                   |
| `dimensions`                         | 原始层级的尺寸（即 `level_dimensions[0]`） |

### 使用示例

将 WSI 切割成 256x256 的小图块（patch）

```python
import openslide
from PIL import Image
import os

# 文件路径
slide_path = "sample.svs"  # 你的WSI路径
output_dir = "patches"
os.makedirs(output_dir, exist_ok=True)

# 打开WSI文件
slide = openslide.OpenSlide(slide_path)

# 获取最高分辨率尺寸
width, height = slide.dimensions

# 设置 patch 尺寸
patch_size = 256

# 遍历整个图像区域，步长为 patch 大小
for y in range(0, height, patch_size):
    for x in range(0, width, patch_size):
        # 读取 patch，level=0 表示最高分辨率
        patch = slide.read_region((x, y), level=0, size=(patch_size, patch_size)).convert("RGB")
        
        # 保存 patch 到磁盘
        filename = f"{output_dir}/patch_{x}_{y}.png"
        patch.save(filename)
```

