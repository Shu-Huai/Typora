# scikit-learn

## 什么是scikit-learn

### 简介

`scikit-learn`是一个用于数据挖掘和数据分析的开源机器学习库。它建立在NumPy、SciPy和matplotlib之上，并提供了多种工具来进行数据预处理、特征选择、模型训练、模型评估和预测等任务。

### 特点和功能

1. 丰富的算法

- 分类：SVM、最近邻、随机森林、逻辑回归等。
- 回归：线性回归、岭回归、LASSO、弹性网等。
- 聚类：KMeans、层次聚类、DBSCAN等。
- 降维：PCA、LDA、因子分析等。
- 模型选择：网格搜索、随机搜索、交叉验证等。
- 预处理：标准化、归一化、特征缩放、特征选取等。

2. 易于使用

- scikit-learn的API设计简单且一致，适合初学者和专家使用。所有的算法都遵循fit-predict 模式。

3. 文档丰富

- 提供了详细的文档、教程和示例，有助于用户快速上手。

4. 集成其他库

- 可以与Pandas、NumPy、SciPy等库无缝集成，方便进行数据处理和分析。

## 安装

使用 pip 安装 scikit-learn

```shell
pip install scikit-learn
```

## 主要模块

### 数据集（Datasets）

提供一些内置的数据集，并支持加载外部数据集。

- sklearn.datasets
  - `load_iris()`：加载鸢尾花数据集
  - `load_digits()`：加载手写数字数据集
  - `make_classification()`：创建分类数据集
  - `make_regression()`：创建回归数据集

### 数据预处理（Preprocessing）

包含用于数据预处理和特征工程的工具。

- sklearn.preprocessing
  - `StandardScaler`：标准化特征
  - `MinMaxScaler`：将特征缩放到指定范围
  - `OneHotEncoder`：对分类特征进行独热编码
  - `LabelEncoder`：对目标标签进行编码

### 线性模型（Linear Models）

提供了各种线性模型的实现。

- sklearn.linear_model
  - `LinearRegression`：线性回归
  - `LogisticRegression`：逻辑回归
  - `Ridge`：岭回归
  - `Lasso`：套索回归

### 监督学习（Supervised Learning）

包含分类和回归的算法。

- `sklearn.svm`
  - `SVC`：支持向量分类
  - `SVR`：支持向量回归
- `sklearn.tree`
  - `DecisionTreeClassifier`：决策树分类
  - `DecisionTreeRegressor`：决策树回归
- `sklearn.ensemble`
  - `RandomForestClassifier`：随机森林分类
  - `RandomForestRegressor`：随机森林回归
  - `GradientBoostingClassifier`：梯度提升分类
  - `GradientBoostingRegressor`：梯度提升回归

### 5. 无监督学习（Unsupervised Learning）

包含聚类、降维和密度估计的算法。

- `sklearn.cluster`
  - `KMeans`：K 均值聚类
  - `DBSCAN`：基于密度的聚类
- `sklearn.decomposition`
  - `PCA`：主成分分析
  - `NMF`：非负矩阵分解
- `sklearn.mixture`
  - `GaussianMixture`：高斯混合模型

### 6. 模型选择（Model Selection）

包含用于模型选择和评估的工具。

- ```
  sklearn.model_selection
  ```

  - `train_test_split`：训练/测试集拆分
  - `GridSearchCV`：网格搜索
  - `RandomizedSearchCV`：随机搜索

### 7. 度量（Metrics）

提供了评估模型性能的工具。

- ```
  sklearn.metrics
  ```

  - `accuracy_score`：准确率
  - `confusion_matrix`：混淆矩阵
  - `roc_auc_score`：ROC AUC 分数
  - `mean_squared_error`：均方误差

### 8. 特征选择（Feature Selection）

包含用于特征选择的工具。

- ```
  sklearn.feature_selection
  ```

  - `SelectKBest`：选择 K 个最佳特征
  - `RFE`：递归特征消除

### 9. 管道（Pipeline）

用于简化工作流的创建。

- ```
  sklearn.pipeline
  ```

  - `Pipeline`：管道化

### 10. 检验（Validation）

提供用于模型验证的工具。

- ```
  sklearn.model_selection
  ```

  - `cross_val_score`：交叉验证分数
  - `KFold`：K 折交叉验证
  - `StratifiedKFold`：分层 K 折交叉验证