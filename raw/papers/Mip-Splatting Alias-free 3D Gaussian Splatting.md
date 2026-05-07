---
title: "Mip-Splatting: Alias-free 3D Gaussian Splatting"
source: "https://arxiv.org/abs/2311.16493"
author:
  - "[[Zehao Yu]]"
  - "[[Anpei Chen]]"
  - "[[Binbin Huang]]"
  - "[[Torsten Sattler]]"
  - "[[Andreas Geiger]]"
published:
created: 2026-05-07
description: "Abstract page for arXiv paper 2311.16493: Mip-Splatting: Alias-free 3D Gaussian Splatting"
tags:
  - "clippings"
---
## Title:Mip-Splatting: Alias-free 3D Gaussian Splatting Notebook

Authors:[Zehao Yu](https://arxiv.org/search/cs?searchtype=author&query=Yu,+Z), [Anpei Chen](https://arxiv.org/search/cs?searchtype=author&query=Chen,+A), [Binbin Huang](https://arxiv.org/search/cs?searchtype=author&query=Huang,+B), [Torsten Sattler](https://arxiv.org/search/cs?searchtype=author&query=Sattler,+T), [Andreas Geiger](https://arxiv.org/search/cs?searchtype=author&query=Geiger,+A)

[View PDF](https://arxiv.org/pdf/2311.16493)

> Abstract:Recently, 3D Gaussian Splatting has demonstrated impressive novel view synthesis results, reaching high fidelity and efficiency. However, strong artifacts can be observed when changing the sampling rate, \\eg, by changing focal length or camera distance. We find that the source for this phenomenon can be attributed to the lack of 3D frequency constraints and the usage of a 2D dilation filter. To address this problem, we introduce a 3D smoothing filter which constrains the size of the 3D Gaussian primitives based on the maximal sampling frequency induced by the input views, eliminating high-frequency artifacts when zooming in. Moreover, replacing 2D dilation with a 2D Mip filter, which simulates a 2D box filter, effectively mitigates aliasing and dilation issues. Our evaluation, including scenarios such a training on single-scale images and testing on multiple scales, validates the effectiveness of our approach.

| Comments: |
| --- |
| Subjects: | Computer Vision and Pattern Recognition (cs.CV) |
| Cite as: | [arXiv:2311.16493](https://arxiv.org/abs/2311.16493) \[cs.CV\] |
|  | (or [arXiv:2311.16493v1](https://arxiv.org/abs/2311.16493v1) \[cs.CV\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2311.16493](https://doi.org/10.48550/arXiv.2311.16493) |

## Submission history

From: Zehao Yu \[[view email](https://arxiv.org/show-email/925b5f83/2311.16493)\]  
**\[v1\]** Mon, 27 Nov 2023 13:03:09 UTC (35,030 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2311.16493) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))