# 0320-BSPC-D-24-10623_reviewer

## 总结

生成器没有处理成像特征

生成器没有提取局部和全局信息的能力

判别器无法区分生成图像的细节

损失函数的设计

## 审稿

This article describes a GAN method for data generation of medical images and demonstrates its effectiveness in synthesizing missing modal data using experiments with BraTS2018, OCT2017, and private CT datasets. Overall, it is sufficiently innovative and experimental, but there are the following areas for improvement

1. Missing Reference in Page 1. "Considering the security and     privacy of medical data, Daset al.[? ] proposed..."
2. The data descriptions in the abstract are redundant. The     research objectives, methods, and main contributions should be more     clearly summarized.
3. Formula 2 display Issues on Page 5.
4. The reason for the need to divide the feature map into N groups     in the Trigeminy Shuffle Feature Module should be discussed in Page 6.     Also, the method of the grouping operation (random or with some basis)     should be described.
5. The contribution of "DC Loss" and "Info     Loss" should be described in more detail in Page 7. The reason that these     loss functions are more effective should be included in the paper.
6. The MAE of CT dataset in abstract is 0.08, and in Table 2, it     is 0.09. They're not consistent.
7. The reason for the roughly twofold difference in variance     between the real and fake images should be explained in Figure 10.
8. It is recommended to add comparisons to recent generation     models, such as diffusion models.
9. In terms of indicators, only image evaluation indicators are     selected, and more domain-specific clinically relevant indicators can be     introduced.

