---
title: "UP-SLAM: Adaptively Structured Gaussian SLAM with Uncertainty Prediction in Dynamic Environments"
source: "https://arxiv.org/abs/2505.22335"
author:
  - "[[Wancai Zheng]]"
  - "[[Linlin Ou]]"
  - "[[Jiajie He]]"
  - "[[Libo Zhou]]"
  - "[[Xinyi Yu]]"
  - "[[Yan Wei]]"
published:
created: 2026-06-02
description: "Abstract page for arXiv paper 2505.22335: UP-SLAM: Adaptively Structured Gaussian SLAM with Uncertainty Prediction in Dynamic Environments"
tags:
  - "clippings"
---
## 标题：UP-SLAM：动态环境下具有不确定性预测的自适应结构化高斯SLAM

作者： [郑万才](https://arxiv.org/search/cs?searchtype=author&query=Zheng,+W) 、 [欧琳琳](https://arxiv.org/search/cs?searchtype=author&query=Ou,+L) 、 [何家杰、](https://arxiv.org/search/cs?searchtype=author&query=He,+J) [周立波](https://arxiv.org/search/cs?searchtype=author&query=Zhou,+L) 、 [余欣怡](https://arxiv.org/search/cs?searchtype=author&query=Yu,+X) 、 [魏](https://arxiv.org/search/cs?searchtype=author&query=Wei,+Y) 岩

[查看PDF](https://arxiv.org/pdf/2505.22335) [HTML（实验性）](https://arxiv.org/html/2505.22335v1)

> 抽象的： 近年来，用于视觉同步定位与建图（SLAM）的3D高斯散射（3DGS）技术在目标跟踪和高保真建图方面取得了显著进展。然而，其顺序优化框架以及对动态物体的敏感性限制了其在实际场景中的实时性能和鲁棒性。我们提出了UP-SLAM，一个面向动态环境的实时RGB-D SLAM系统，它通过并行框架将目标跟踪和建图过程解耦。我们采用概率八叉树自适应地管理高斯基元，无需手动设置阈值即可实现高效的初始化和剪枝。为了在跟踪过程中鲁棒地过滤动态区域，我们提出了一种无需训练的不确定性估计器，该估计器融合多模态残差来估计每个像素的运动不确定性，从而在不依赖语义标签的情况下实现对开放集动态物体的处理。此外，我们还设计了一个时间编码器来提升渲染质量。同时，低维特征通过浅层多层感知器高效转换，构建DINO特征，然后利用DINO特征丰富高斯场，提高不确定性预测的鲁棒性。在多个具有挑战性的数据集上进行的大量实验表明，UP-SLAM在定位精度（提高59.8%）和渲染质量（PSNR提高4.57 dB）方面均优于现有最佳方法，同时保持实时性能，并在动态项目中生成可重用、无伪影的 [静态](http://environments.the/) 地图 [。](https://aczheng-cai.github.io/up_slam.github.io/)

| 主题： | 机器人学（cs.RO） ；计算机视觉与模式识别（cs.CV） |
| --- | --- |
| 引用格式： | [arXiv:2505.22335](https://arxiv.org/abs/2505.22335) \[cs.RO\] |
|  | （或 此版本的 [arXiv:2505.22335v1](https://arxiv.org/abs/2505.22335v1) \[cs.RO\] ） |
|  | [https://doi.org/10.48550/arXiv.2505.22335](https://doi.org/10.48550/arXiv.2505.22335) |
| 期刊参考文献： | ICRA 2026 |

## 提交历史

发件人：Wancai Cheng \[[查看电子邮件](https://arxiv.org/show-email/bde4afff/2505.22335)\]  
**\[v1\]** 2025 年 5 月 28 日星期三 13:23:16 UTC (14,584 KB)

[本文的哪些作者是支持者？](https://arxiv.org/auth/show-endorsers/2505.22335) | 禁用 MathJax （ [什么是 MathJax？](https://info.arxiv.org/help/mathjax.html) ）