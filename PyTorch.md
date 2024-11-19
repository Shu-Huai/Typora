#  PyTorch

## `torch.nn`相关

### 定义

`torch.nn`是`PyTorch`中的一个模块，它提供了一系列用于构建和训练神经网络的类和函数。

### 激活函数

#### Sigmoid 激活函数`torch.nn.Sigmoid()`

- 将输入的实数值映射到`(0, 1)`范围内
- 数学表达式：$\text{Sigmoid}(x)=\frac{1}{1+e^{-z}}$
- 容易出现梯度消失问题，特别是在深层网络中
- 使用场景：二分类任务的输出层，输出一个值，表示属于某一类别的概率

#### 双曲正切激活函数`torch.nn.Tanh()`

- 将输入值映射到`(-1, 1)`范围内
- 数学表达式：$\text{Tanh}(x)=\frac{e^x-e^{-x}}{e^x+e^{-x}}=2\cdot\text{Sigmoid}(2x)−1$
- 使用场景：常用于隐藏层的激活函数，能够使数据更中心化（均值为0），这通常有助于加速训练收敛
- Tanh函数是对称的，可以解决某些特定场景下的对称性问题
- 仍然可能出现梯度消失问题


### 损失函数

#### 交叉熵损失函数`torch.nn.CrossEntropyLoss`

用于分类任务

#### 均方误差损失函数`torch.nn.MSELoss`

用于回归任务

#### 二元交叉熵损失函数`torch.nn.BCELoss`

用于二分类任务

## 数据预处理和数据增强

### 处理对象

实际上数据增强是数据预处理的一部分

数据集分为训练集和测试集，对训练集需要做数据预处理和数据增强，即通过变换增大数据集的规模，对测试集只做一些图像的缩放、标准化等操作。

### 数据预处理使用方式

`torchvision`中`transforms`模块自带功能，将这些功能做成列表的形式，传入`transforms.Compose`中，形成流水线的形式对输入数据进行处理

#### 随机旋转

参数是角度

```python
transforms.RandomRotation(45)
```

#### 缩放

参数是目标的宽高像素点

```python
transforms.Resize(256)
```

#### 裁剪

有中心裁剪和随机裁剪

参数是目标的宽高像素点

```python
transforms.CenterCrop(224)
transforms.RandomCrop(224)
```

#### 随机翻转

分为随机水平翻转和随机垂直翻转

参数为翻转的概率

```python
transforms.RandomHorizontalFlip(p=0.5)
transforms.RandomVerticalFlip(p=0.5)
```

#### 对图像的基本变换

亮度、对比度、饱和度、色相

```python
ransforms.ColorJitter(brightness=0.2, contrast=0.1, saturation=0.1, hue=0.1)
```

#### 转换为灰度图

以概率将图片转换为灰度图

三通道的原图转换后的灰度图依旧为三通道表示，其R=G=B

```python
transforms.RandomGrayscale(p=0.025)
```

#### 将图片转化为Tensor格式

```python
transforms.ToTensor()
```

#### 数据标准化操作

计算均值、标准差，作为参数传递

在进行迁移学习的时候，使用的均值、标准差需要根据别人的模型的数据指定

```python
transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
```

### 数据准备

使用`torchvision.datasets.ImageFolder`工具，传入训练集和测试集的路径，传入`transforms.Compose`对象

例如

```python
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x]) for x in ['train', 'valid']}
```

使用`torch.utils.data.DataLoader`工具，将数据集按照`batch_size`划分

```
torch.utils.data.DataLoader(image_datasets[x], batch_size=batch_size, shuffle=True)
```
