# 1218-NEUNET-D-25-03023_R1_reviewer

This paper proposes a multi-task learning framework for mediastinal lymph node metastasis prediction based on chest CT images. The authors design a Dual-control Branch Routing Gate to guide feature routing across tasks and a Dual-Dimensional Gradient Balancing method to mitigate gradient conflicts in multi-task learning. The authors have thoroughly revised the manuscript in response to the reviewers’ comments. Yet there are still some points to be noticed.

1. In 2.3, the sentence "However, the methods described fail to consider the data distribution characteristics among tasks." appears twice.

2. The description of the gating mechanism of MOEs in the Introduction—specifically the claim that "models overlook the allocation and weighting of similar features across related tasks in their gating mechanisms"—is insufficiently detailed, leading to a lack of coherence in the contextual logic.

3. The description of the dataset in the current Section 4.1 is relatively general. Since the paper repeatedly emphasizes the "inter-task data distribution characteristics" and discusses issues such as task dominance and uneven cross-category performance, adding a table illustrating the sample distribution in Section 4.1 would significantly enhance the persuasiveness of the paper.

4. Although Section 4.2.2 states that MT-IDS “overcomes the negative impact of class imbalance”, the main task still shows a relatively modest F1-score (73.03%) compared to its high AUC (94.96%), and the confusion matrices reveal noticeable misclassification for some classes. I would suggest softening this claim.

5. 

    # 1572. 矩阵对角线元素的和

    给你一个正方形矩阵 `mat`，请你返回矩阵对角线元素的和。

    请你返回在矩阵主对角线上的元素和副对角线上且不在主对角线上元素的和。

    **示例 1：**

    ![](https://assets.leetcode.com/uploads/2020/08/14/sample_1911.png)

    > **输入：** mat = \[\[**1** ,2,**3** ],
    >
    > \[4,**5** ,6],
    >
    > \[**7** ,8,**9** ]]
    >
    > **输出：** 25
    >
    > **解释：** 对角线的和为：1 \+ 5 \+ 9 \+ 3 \+ 7 = 25
    >
    > 请注意，元素 mat\[1]\[1] = 5 只会被计算一次。

    **示例 2：**

    > **输入：** mat = \[\[**1** ,1,1,**1** ],
    >
    > \[1,**1** ,**1** ,1],
    >
    > \[1,**1** ,**1** ,1],
    >
    > \[**1** ,1,1,**1** ]]
    >
    > **输出：** 8

    **示例 3：**

    > **输入：** mat = \[\[**5** ]]
    >
    > **输出：** 5

    **提示：**

    * `n == mat.length == mat[i].length`
    * `1 <= n <= 100`
    * `1 <= mat[i][j] <= 100`

