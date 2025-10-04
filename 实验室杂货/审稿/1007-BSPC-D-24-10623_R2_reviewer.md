# 1007-BSPC-D-24-10623_R2_reviewer

This paper introduces DualMedGAN for medical image modality completion, combining a CNN+Transformer generator with SLC skip connections and a TSFM discriminator, and training with mutual-information and GLCM-based texture losses. Experiments show that the proposed method achieves superior PSNR/SSIM/FID/MAE over baselines across multiple datasets. 

The authors have thoroughly revised the manuscript in response to the reviewers’ comments.

Here are two additional suggestion

1. All chosen metrics (FID, PSNR, SSIM, MAE) are image-level measures. Please consider adding medical friendly metrics, e.g., MS-SSIM. Alternatively, report the minimum clinically perceptible difference (thresholds for PSNR/SSIM) to contextualize whether the observed gains are likely to be meaningful in practice.
2. Given batch size =2, the implementation of stable mutual information estimation, for example, InfoNCE, MINE or soft-histogram may be detailed, since the manuscript currently provides only theoretical formulas.