---
title: "Pseudo Depth Meets Gaussian: A Feed-forward RGB SLAM Baseline"
source: "https://arxiv.org/abs/2508.04597"
author:
  - "[[Linqing Zhao]]"
  - "[[Xiuwei Xu]]"
  - "[[Yirui Wang]]"
  - "[[Hao Wang]]"
  - "[[Wenzhao Zheng]]"
  - "[[Yansong Tang]]"
  - "[[Haibin Yan]]"
  - "[[Jiwen Lu]]"
published:
created: 2026-05-21
description: "Abstract page for arXiv paper 2508.04597: Pseudo Depth Meets Gaussian: A Feed-forward RGB SLAM Baseline"
tags:
  - "clippings"
---
## Title:Pseudo Depth Meets Gaussian: A Feed-forward RGB SLAM Baseline

Authors:[Linqing Zhao](https://arxiv.org/search/cs?searchtype=author&query=Zhao,+L), [Xiuwei Xu](https://arxiv.org/search/cs?searchtype=author&query=Xu,+X), [Yirui Wang](https://arxiv.org/search/cs?searchtype=author&query=Wang,+Y), [Hao Wang](https://arxiv.org/search/cs?searchtype=author&query=Wang,+H), [Wenzhao Zheng](https://arxiv.org/search/cs?searchtype=author&query=Zheng,+W), [Yansong Tang](https://arxiv.org/search/cs?searchtype=author&query=Tang,+Y), [Haibin Yan](https://arxiv.org/search/cs?searchtype=author&query=Yan,+H), [Jiwen Lu](https://arxiv.org/search/cs?searchtype=author&query=Lu,+J)

[View PDF](https://arxiv.org/pdf/2508.04597) [HTML (experimental)](https://arxiv.org/html/2508.04597v1)

> Abstract:Incrementally recovering real-sized 3D geometry from a pose-free RGB stream is a challenging task in 3D reconstruction, requiring minimal assumptions on input data. Existing methods can be broadly categorized into end-to-end and visual SLAM-based approaches, both of which either struggle with long sequences or depend on slow test-time optimization and depth sensors. To address this, we first integrate a depth estimator into an RGB-D SLAM system, but this approach is hindered by inaccurate geometric details in predicted depth. Through further investigation, we find that 3D Gaussian mapping can effectively solve this problem. Building on this, we propose an online 3D reconstruction method using 3D Gaussian-based SLAM, combined with a feed-forward recurrent prediction module to directly infer camera pose from optical flow. This approach replaces slow test-time optimization with fast network inference, significantly improving tracking speed. Additionally, we introduce a local graph rendering technique to enhance robustness in feed-forward pose prediction. Experimental results on the Replica and TUM-RGBD datasets, along with a real-world deployment demonstration, show that our method achieves performance on par with the state-of-the-art SplaTAM, while reducing tracking time by more than 90\\%.

| Comments: |
| --- |
| Subjects: | Computer Vision and Pattern Recognition (cs.CV) |
| Cite as: | [arXiv:2508.04597](https://arxiv.org/abs/2508.04597) \[cs.CV\] |
|  | (or [arXiv:2508.04597v1](https://arxiv.org/abs/2508.04597v1) \[cs.CV\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2508.04597](https://doi.org/10.48550/arXiv.2508.04597) |

## Submission history

From: Linqing Zhao \[[view email](https://arxiv.org/show-email/5ed3e457/2508.04597)\]  
**\[v1\]** Wed, 6 Aug 2025 16:16:58 UTC (27,240 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2508.04597) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))