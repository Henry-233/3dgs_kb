---
title: "LangSplat: 3D Language Gaussian Splatting"
source: "https://arxiv.org/abs/2312.16084"
author:
  - "[[Minghan Qin]]"
  - "[[Wanhua Li]]"
  - "[[Jiawei Zhou]]"
  - "[[Haoqian Wang]]"
  - "[[Hanspeter Pfister]]"
published:
created: 2026-05-07
description: "Abstract page for arXiv paper 2312.16084: LangSplat: 3D Language Gaussian Splatting"
tags:
  - "clippings"
---
## Title:LangSplat: 3D Language Gaussian Splatting

Authors:[Minghan Qin](https://arxiv.org/search/cs?searchtype=author&query=Qin,+M), [Wanhua Li](https://arxiv.org/search/cs?searchtype=author&query=Li,+W), [Jiawei Zhou](https://arxiv.org/search/cs?searchtype=author&query=Zhou,+J), [Haoqian Wang](https://arxiv.org/search/cs?searchtype=author&query=Wang,+H), [Hanspeter Pfister](https://arxiv.org/search/cs?searchtype=author&query=Pfister,+H)

[View PDF](https://arxiv.org/pdf/2312.16084) [HTML (experimental)](https://arxiv.org/html/2312.16084v2)

> Abstract:Humans live in a 3D world and commonly use natural language to interact with a 3D scene. Modeling a 3D language field to support open-ended language queries in 3D has gained increasing attention recently. This paper introduces LangSplat, which constructs a 3D language field that enables precise and efficient open-vocabulary querying within 3D spaces. Unlike existing methods that ground CLIP language embeddings in a NeRF model, LangSplat advances the field by utilizing a collection of 3D Gaussians, each encoding language features distilled from CLIP, to represent the language field. By employing a tile-based splatting technique for rendering language features, we circumvent the costly rendering process inherent in NeRF. Instead of directly learning CLIP embeddings, LangSplat first trains a scene-wise language autoencoder and then learns language features on the scene-specific latent space, thereby alleviating substantial memory demands imposed by explicit modeling. Existing methods struggle with imprecise and vague 3D language fields, which fail to discern clear boundaries between objects. We delve into this issue and propose to learn hierarchical semantics using SAM, thereby eliminating the need for extensively querying the language field across various scales and the regularization of DINO features. Extensive experimental results show that LangSplat significantly outperforms the previous state-of-the-art method LERF by a large margin. Notably, LangSplat is extremely efficient, achieving a 199 $\times$ 与分辨率为 1440 × 1080 的 LERF 相比，速度提升了 数倍。 $\times$ 我们强烈建议读者查看我们的视频测试结果。 [this https URL](https://langsplat.github.io/)

| Comments: |
| --- |
| Subjects: | Computer Vision and Pattern Recognition (cs.CV) |
| Cite as: | [arXiv:2312.16084](https://arxiv.org/abs/2312.16084) \[cs.CV\] |
|  | (or [arXiv:2312.16084v2](https://arxiv.org/abs/2312.16084v2) \[cs.CV\] for this version) |
|  | [https://doi.org/10.48550/arXiv.2312.16084](https://doi.org/10.48550/arXiv.2312.16084) |

## Submission history

From: Wanhua Li \[[view email](https://arxiv.org/show-email/7b620b08/2312.16084)\]  
**[\[v1\]](https://arxiv.org/abs/2312.16084v1)** Tue, 26 Dec 2023 15:14:37 UTC (6,834 KB)  
**\[v2\]** Sun, 31 Mar 2024 04:45:58 UTC (7,986 KB)

[Which authors of this paper are endorsers?](https://arxiv.org/auth/show-endorsers/2312.16084) | Disable MathJax ([What is MathJax?](https://info.arxiv.org/help/mathjax.html))