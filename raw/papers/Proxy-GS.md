---
title: "Proxy-GS: Unified Occlusion Priors for Training and Inference in Structured 3D Gaussian Splatting"
source: "https://arxiv.org/abs/2509.24421"
author:
  - "[[Yuanyuan Gao]]"
  - "[[Yuning Gong]]"
  - "[[Yifei Liu]]"
  - "[[Li Jingfeng]]"
  - "[[Dingwen Zhang]]"
  - "[[Yanci Zhang]]"
  - "[[Dan Xu]]"
  - "[[Xiao Sun]]"
  - "[[Zhihang Zhong]]"
published:
created: 2026-05-20
description: "Abstract page for arXiv paper 2509.24421: Proxy-GS: Unified Occlusion Priors for Training and Inference in Structured 3D Gaussian Splatting"
tags:
  - "clippings"
---
## 标题：Proxy-GS：用于结构化 3D 高斯散射训练和推理的统一遮挡先验

作者： [高媛媛](https://arxiv.org/search/cs?searchtype=author&query=Gao,+Y) 、 [宫宇宁](https://arxiv.org/search/cs?searchtype=author&query=Gong,+Y) 、 [刘逸飞](https://arxiv.org/search/cs?searchtype=author&query=Liu,+Y) 、 [李景峰](https://arxiv.org/search/cs?searchtype=author&query=Jingfeng,+L) 、 [张鼎文](https://arxiv.org/search/cs?searchtype=author&query=Zhang,+D) 、 [张彦慈](https://arxiv.org/search/cs?searchtype=author&query=Zhang,+Y) 、 [徐丹](https://arxiv.org/search/cs?searchtype=author&query=Xu,+D) 、 [孙晓](https://arxiv.org/search/cs?searchtype=author&query=Sun,+X) 、 [钟志航](https://arxiv.org/search/cs?searchtype=author&query=Zhong,+Z)

[查看PDF](https://arxiv.org/pdf/2509.24421) [HTML（实验性）](https://arxiv.org/html/2509.24421v4)

> 抽象的： 三维高斯散射（3DGS）已成为实现逼真渲染的有效方法。近年来，基于多层感知器（MLP）的变体进一步提升了视觉保真度，但也引入了显著的渲染解码开销。为了降低计算成本，人们提出了多种剪枝策略和细节层次（LOD）技术，旨在有效减少大规模场景中的高斯图元数量。然而，我们的分析表明，由于缺乏遮挡感知，仍然存在显著的冗余。本文提出了一种名为Proxy-GS的新型渲染流程，该流程利用代理从任意视角引入高斯遮挡感知。我们方法的核心是一个快速代理系统，能够在1毫秒内生成1000x1000分辨率的精确遮挡深度图。该代理发挥着双重作用：首先，它指导锚点和高斯图元的剔除，从而加快渲染速度。其次，它在训练过程中引导密度向表面移动，避免遮挡区域出现不一致的情况，从而提升渲染质量。在诸如 MatrixCity Streets 数据集等严重遮挡的场景中，Proxy-GS 不仅赋予基于 MLP 的高斯分布算法更强大的渲染能力，而且实现了更快的渲染速度。具体而言，它的速度比 Octree-GS 快 2.5 倍以上，并且始终提供显著更高的渲染质量。代码将在审核通过后公开。

| 评论： |
| --- |
| 主题： | 计算机视觉与模式识别（cs.CV） |
| 引用格式： | [arXiv:2509.24421](https://arxiv.org/abs/2509.24421) \[cs.CV\] |
|  | （或 此版本的 [arXiv:2509.24421v4](https://arxiv.org/abs/2509.24421v4) \[cs.CV\] ） |
|  | [https://doi.org/10.48550/arXiv.2509.24421](https://doi.org/10.48550/arXiv.2509.24421) |

## 提交历史

发件人：Yuanyuan Gao \[[查看电子邮件](https://arxiv.org/show-email/315f22b3/2509.24421)\]  
**[\[v1\]](https://arxiv.org/abs/2509.24421v1)** 2025 年 9 月 29 日星期一 08:10:07 UTC (6,099 KB)  
**[\[v2\]](https://arxiv.org/abs/2509.24421v2)** 2025 年 10 月 1 日星期三 04:55:39 UTC (6,101 KB)  
**[\[v3\]](https://arxiv.org/abs/2509.24421v3)** 2026 年 2 月 26 日星期四 15:33:44 UTC (7,264 KB)  
**\[v4\]** 世界标准时间 2026 年 3 月 3 日星期二 05:50:42 (7,264 KB)

[本文的哪些作者是支持者？](https://arxiv.org/auth/show-endorsers/2509.24421) | 禁用 MathJax （ [什么是 MathJax？](https://info.arxiv.org/help/mathjax.html) ）