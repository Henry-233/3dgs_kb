---
title: "TVG-SLAM: Robust Gaussian Splatting SLAM with Tri-view Geometric Constraints"
source: "https://arxiv.org/abs/2506.23207"
author:
  - "[[Zhen Tan]]"
  - "[[Xieyuanli Chen]]"
  - "[[Lei Feng]]"
  - "[[Yangbing Ge]]"
  - "[[Shuaifeng Zhi]]"
  - "[[Jiaxiong Liu]]"
  - "[[Dewen Hu]]"
published:
created: 2026-06-11
description: "Abstract page for arXiv paper 2506.23207: TVG-SLAM: Robust Gaussian Splatting SLAM with Tri-view Geometric Constraints"
tags:
  - "clippings"
---
## Title:TVG-SLAM: Robust Gaussian Splatting SLAM with Tri-view Geometric Constraints

Authors:[Zhen Tan](https://arxiv.org/search/cs?searchtype=author&query=Tan,+Z), [Xieyuanli Chen](https://arxiv.org/search/cs?searchtype=author&query=Chen,+X), [Lei Feng](https://arxiv.org/search/cs?searchtype=author&query=Feng,+L), [Yangbing Ge](https://arxiv.org/search/cs?searchtype=author&query=Ge,+Y), [Shuaifeng Zhi](https://arxiv.org/search/cs?searchtype=author&query=Zhi,+S), [Jiaxiong Liu](https://arxiv.org/search/cs?searchtype=author&query=Liu,+J), [Dewen Hu](https://arxiv.org/search/cs?searchtype=author&query=Hu,+D)

[View PDF](https://arxiv.org/pdf/2506.23207) [HTML (experimental)](https://arxiv.org/html/2506.23207v1)

> Abstract:Recent advances in 3D Gaussian Splatting (3DGS) have enabled RGB-only SLAM systems to achieve high-fidelity scene representation. However, the heavy reliance of existing systems on photometric rendering loss for camera tracking undermines their robustness, especially in unbounded outdoor environments with severe viewpoint and illumination changes. To address these challenges, we propose TVG-SLAM, a robust RGB-only 3DGS SLAM system that leverages a novel tri-view geometry paradigm to ensure consistent tracking and high-quality mapping. We introduce a dense tri-view matching module that aggregates reliable pairwise correspondences into consistent tri-view matches, forming robust geometric constraints across frames. For tracking, we propose Hybrid Geometric Constraints, which leverage tri-view matches to construct complementary geometric cues alongside photometric loss, ensuring accurate and stable pose estimation even under drastic viewpoint shifts and lighting variations. For mapping, we propose a new probabilistic initialization strategy that encodes geometric uncertainty from tri-view correspondences into newly initialized Gaussians. Additionally, we design a Dynamic Attenuation of Rendering Trust mechanism to mitigate tracking drift caused by mapping latency. Experiments on multiple public outdoor datasets show that our TVG-SLAM outperforms prior RGB-only 3DGS-based SLAM systems. Notably, in the most challenging dataset, our method improves tracking robustness, reducing the average Absolute Trajectory Error (ATE) by 69.0\\% while achieving state-of-the-art rendering quality. The implementation of our method will be released as open-source.

| Subjects: | Computer Vision and Pattern Recognition (cs.CV) |
| --- | --- |
| Cite as: | [arXiv:2506.23207](https://arxiv.org/abs/2506.23207) \[cs.CV\] |
|  | (or [arXiv:2506.23207v1](https://arxiv.org/abs/2506.23207v1) \[cs.CV\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2506.23207](https://doi.org/10.48550/arXiv.2506.23207) |

## Submission history

From: Zhen Tan \[[view email](https://arxiv.org/show-email/7abf3fd8/2506.23207)\]  
**\[v1\]** Sun, 29 Jun 2025 12:31:05 UTC (5,366 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2506.23207) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))