---
title: "Mobile-GS: Real-time Gaussian Splatting for Mobile Devices"
source: "https://arxiv.org/abs/2603.11531"
author:
  - "[[Xiaobiao Du]]"
  - "[[Yida Wang]]"
  - "[[Kun Zhan]]"
  - "[[Xin Yu]]"
published:
created: 2026-05-07
description: "Abstract page for arXiv paper 2603.11531: Mobile-GS: Real-time Gaussian Splatting for Mobile Devices"
tags:
  - "clippings"
---
## Title:Mobile-GS: Real-time Gaussian Splatting for Mobile Devices

Authors:[Xiaobiao Du](https://arxiv.org/search/cs?searchtype=author&query=Du,+X), [Yida Wang](https://arxiv.org/search/cs?searchtype=author&query=Wang,+Y), [Kun Zhan](https://arxiv.org/search/cs?searchtype=author&query=Zhan,+K), [Xin Yu](https://arxiv.org/search/cs?searchtype=author&query=Yu,+X)

[View PDF](https://arxiv.org/pdf/2603.11531) [HTML (experimental)](https://arxiv.org/html/2603.11531v1)

> Abstract:3D Gaussian Splatting (3DGS) has emerged as a powerful representation for high-quality rendering across a wide range of [this http URL](http://applications.however/), its high computational demands and large storage costs pose significant challenges for deployment on mobile devices. In this work, we propose a mobile-tailored real-time Gaussian Splatting method, dubbed Mobile-GS, enabling efficient inference of Gaussian Splatting on edge devices. Specifically, we first identify alpha blending as the primary computational bottleneck, since it relies on the time-consuming Gaussian depth sorting process. To solve this issue, we propose a depth-aware order-independent rendering scheme that eliminates the need for sorting, thereby substantially accelerating rendering. Although this order-independent rendering improves rendering speed, it may introduce transparency artifacts in regions with overlapping geometry due to the scarcity of rendering order. To address this problem, we propose a neural view-dependent enhancement strategy, enabling more accurate modeling of view-dependent effects conditioned on viewing direction, 3D Gaussian geometry, and appearance attributes. In this way, Mobile-GS can achieve both high-quality and real-time rendering. Furthermore, to facilitate deployment on memory-constrained mobile platforms, we also introduce first-order spherical harmonics distillation, a neural vector quantization technique, and a contribution-based pruning strategy to reduce the number of Gaussian primitives and compress the 3D Gaussian representation with the assistance of neural networks. Extensive experiments demonstrate that our proposed Mobile-GS achieves real-time rendering and compact model size while preserving high visual quality, making it well-suited for mobile applications.

| Comments: |
| --- |
| Subjects: | Computer Vision and Pattern Recognition (cs.CV) |
| Cite as: | [arXiv:2603.11531](https://arxiv.org/abs/2603.11531) \[cs.CV\] |
|  | (or [arXiv:2603.11531v1](https://arxiv.org/abs/2603.11531v1) \[cs.CV\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2603.11531](https://doi.org/10.48550/arXiv.2603.11531) |

## Submission history

From: Xiaobiao Du \[[view email](https://arxiv.org/show-email/d91971ae/2603.11531)\]  
**\[v1\]** Thu, 12 Mar 2026 04:33:04 UTC (8,877 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2603.11531) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))