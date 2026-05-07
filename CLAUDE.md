# Knowledge Base Schema — 3D Gaussian Splatting

## Domain
3D Gaussian Splatting and related 3D representation methods —
core papers, concepts, mathematical foundations, implementations,
comparisons with NeRF and other methods.

## Directory conventions
- wiki/concepts/ → 核心概念（每个概念一页）
- wiki/papers/   → 论文页（每篇论文一页）
- wiki/synthesis/→ 方法对比、发展时间线、综述

## Concept page format
---
title: "概念名"
tags: [concept, math | rendering | optimization]
---

## 定义
(2-3句核心定义)

## 直觉理解
(类比解释，不依赖公式)

## 数学形式
(关键公式)

## 关联
- 相关概念: [[concepts/...]]
- 用到该概念的论文: [[papers/...]]

## Paper page format
---
title: "论文名"
authors:
year:
venue: CVPR | ICCV | ECCV | NeurIPS | arxiv
tags: [paper, base | extension | application]
status: unread | reading | done
---

## 一句话总结
## 解决的问题
## 核心方法
## 与前作的区别
## 实验结论
## 关联
- 基于: [[papers/...]]
- 被引用: [[papers/...]]
- 涉及概念: [[concepts/...]]

## Ingest workflow
When asked to ingest new content from raw/:
1. Identify type: paper / concept / blog
2. Create corresponding wiki page
3. Add wikilinks to related pages
4. Update index.md
5. Log operation in log.md

## Key concepts to track
高斯表示: 3D Gaussian、协方差矩阵、球谐函数、不透明度
渲染管线: 投影变换、alpha合成、tile-based光栅化
训练优化: 自适应密度控制、梯度反传、SSIM loss
对比方法: NeRF、Instant-NGP、Mip-NeRF、TensoRF