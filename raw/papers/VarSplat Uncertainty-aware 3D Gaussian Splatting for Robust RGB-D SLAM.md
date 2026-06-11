---
title: "VarSplat: Uncertainty-aware 3D Gaussian Splatting for Robust RGB-D SLAM"
source: "https://arxiv.org/abs/2603.09673"
author:
  - "[[Anh Thuan Tran]]"
  - "[[Jana Kosecka]]"
published:
created: 2026-06-11
description: "Abstract page for arXiv paper 2603.09673: VarSplat: Uncertainty-aware 3D Gaussian Splatting for Robust RGB-D SLAM"
tags:
  - "clippings"
---
## Title:VarSplat: Uncertainty-aware 3D Gaussian Splatting for Robust RGB-D SLAM

Authors:[Anh Thuan Tran](https://arxiv.org/search/cs?searchtype=author&query=Tran,+A+T), [Jana Kosecka](https://arxiv.org/search/cs?searchtype=author&query=Kosecka,+J)

[View PDF](https://arxiv.org/pdf/2603.09673) [HTML (experimental)](https://arxiv.org/html/2603.09673v1)

> Abstract:Simultaneous Localization and Mapping (SLAM) with 3D Gaussian Splatting (3DGS) enables fast, differentiable rendering and high-fidelity reconstruction across diverse real-world scenes. However, existing 3DGS-SLAM approaches handle measurement reliability implicitly, making pose estimation and global alignment susceptible to drift in low-texture regions, transparent surfaces, or areas with complex reflectance properties. To this end, we introduce VarSplat, an uncertainty-aware 3DGS-SLAM system that explicitly learns per-splat appearance variance. By using the law of total variance with alpha compositing, we then render differentiable per-pixel uncertainty map via efficient, single-pass rasterization. This map guides tracking, submap registration, and loop detection toward focusing on reliable regions and contributes to more stable optimization. Experimental results on Replica (synthetic) and TUM-RGBD, ScanNet, and ScanNet++ (real-world) show that VarSplat improves robustness and achieves competitive or superior tracking, mapping, and novel view synthesis rendering compared to existing studies for dense RGB-D SLAM.

| Comments: |
| --- |
| Subjects: | Computer Vision and Pattern Recognition (cs.CV) |
| Cite as: | [arXiv:2603.09673](https://arxiv.org/abs/2603.09673) \[cs.CV\] |
|  | (or [arXiv:2603.09673v1](https://arxiv.org/abs/2603.09673v1) \[cs.CV\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2603.09673](https://doi.org/10.48550/arXiv.2603.09673) |

## Submission history

From: Anh Thuan Tran \[[view email](https://arxiv.org/show-email/f1516290/2603.09673)\]  
**\[v1\]** Tue, 10 Mar 2026 13:42:58 UTC (4,609 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2603.09673) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))