---
title: "SSIM Loss"
tags: [concept, optimization]
---

## 定义
SSIM（Structural Similarity Index Measure）损失是衡量两幅图像结构相似性的感知损失函数。在3DGS中，训练损失由L1损失和SSIM损失的加权组合构成：$L = (1-\lambda)L_1 + \lambda L_{SSIM}$，其中 $\lambda = 0.2$。SSIM项帮助模型捕捉图像的结构信息，提升视觉质量。

## 直觉理解
L1损失只关心每个像素值是否匹配（像逐字校对），SSIM损失则关心图像的"结构感"是否对——亮度是否一致、对比度是否匹配、纹理结构是否保留（像整体风格校对）。两者结合让渲染结果既像素精确又视觉自然。

## 数学形式
SSIM在三个维度上比较两幅图像：

$$\text{SSIM}(x, y) = \frac{(2\mu_x\mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}$$

- 亮度比较：$\mu_x, \mu_y$
- 对比度比较：$\sigma_x, \sigma_y$
- 结构比较：$\sigma_{xy}$

训练总损失：
$$L = (1 - \lambda) L_1 + \lambda (1 - \text{SSIM})$$

## 关联
- 用到该概念的论文: [[papers/3d-gaussian-splatting]], [[papers/mip-splatting]], [[papers/gaussian-opacity-fields]]
