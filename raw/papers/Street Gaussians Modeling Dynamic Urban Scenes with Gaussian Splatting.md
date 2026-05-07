---
title: "Street Gaussians: Modeling Dynamic Urban Scenes with Gaussian Splatting"
source: "https://arxiv.org/abs/2401.01339"
author:
  - "[[Yunzhi Yan]]"
  - "[[Haotong Lin]]"
  - "[[Chenxu Zhou]]"
  - "[[Weijie Wang]]"
  - "[[Haiyang Sun]]"
  - "[[Kun Zhan]]"
  - "[[Xianpeng Lang]]"
  - "[[Xiaowei Zhou]]"
  - "[[Sida Peng]]"
published:
created: 2026-05-07
description: "Abstract page for arXiv paper 2401.01339: Street Gaussians: Modeling Dynamic Urban Scenes with Gaussian Splatting"
tags:
  - "clippings"
---
## 标题：街道高斯：利用高斯散射对动态城市场景进行建模

作者： 严 [云志](https://arxiv.org/search/cs?searchtype=author&query=Yan,+Y),[林浩桐](https://arxiv.org/search/cs?searchtype=author&query=Lin,+H),周晨旭,[王伟杰,](https://arxiv.org/search/cs?searchtype=author&query=Zhou,+C)[孙海洋](https://arxiv.org/search/cs?searchtype=author&query=Wang,+W),[詹坤](https://arxiv.org/search/cs?searchtype=author&query=Sun,+H),[郎](https://arxiv.org/search/cs?searchtype=author&query=Zhan,+K) [贤鹏](https://arxiv.org/search/cs?searchtype=author&query=Lang,+X),[周晓伟](https://arxiv.org/search/cs?searchtype=author&query=Zhou,+X),[彭思达](https://arxiv.org/search/cs?searchtype=author&query=Peng,+S)

[查看PDF](https://arxiv.org/pdf/2401.01339) [HTML（实验性）](https://arxiv.org/html/2401.01339v3)

> 抽象的： 本文旨在解决自动驾驶场景中动态城市街道建模的问题。近期方法通过引入跟踪车辆姿态来扩展NeRF，从而实现车辆动画，并合成动态城市街道场景的逼真视图。然而，这些方法存在训练和渲染速度缓慢的显著局限性。我们提出了一种新的显式场景表示方法——街道高斯（Street Gaussians），以克服这些局限性。具体而言，动态城市场景被表示为一组点云，每个点云都配备了语义logits和3D高斯分布，分别对应前景车辆或背景。为了对前景车辆的动态特性进行建模，每个目标点云都使用可优化的跟踪姿态进行优化，并结合4D球谐函数模型来模拟其动态外观。这种显式表示方法使得车辆和背景的合成变得简单，从而能够在半小时的训练时间内完成场景编辑操作，并以135帧/秒（1066 1600分辨率）的速度进行渲染。我们在多个具有挑战性的基准数据集上对所提出的方法进行了评估，包括KITTI和Waymo Open数据集。实验表明，所提出的方法在所有数据集上均始终优于现有最佳方法。我们将公开代码以确保实验结果的可复现性。 $\times$

| 评论： |
| --- |
| 主题： | 计算机视觉与模式识别（cs.CV） ；图形学（cs.GR） |
| 引用格式： | [arXiv:2401.01339](https://arxiv.org/abs/2401.01339) \[cs.CV\] |
|  | （或 此版本的 [arXiv:2401.01339v3](https://arxiv.org/abs/2401.01339v3) \[cs.CV\] ） |
|  | [https://doi.org/10.48550/arXiv.2401.01339](https://doi.org/10.48550/arXiv.2401.01339) |

## 提交历史

发件人：Yunzhi Yan \[[查看电子邮件](https://arxiv.org/show-email/64b44b7b/2401.01339)\]  
**[\[v1\]](https://arxiv.org/abs/2401.01339v1)** 2024 年 1 月 2 日星期二 18:59:55 UTC (33,668 KB)  
**[\[v2\]](https://arxiv.org/abs/2401.01339v2)** 2024 年 7 月 16 日星期二 14:12:54 UTC (45,063 KB)  
**\[v3\]** 2024 年 8 月 18 日星期日 14:26:31 UTC (45,063知识库）

[本文的哪些作者是支持者？](https://arxiv.org/auth/show-endorsers/2401.01339) | 禁用 MathJax （ [什么是 MathJax？](https://info.arxiv.org/help/mathjax.html) ）