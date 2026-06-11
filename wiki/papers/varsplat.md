---
title: "VarSplat: Uncertainty-aware 3D Gaussian Splatting for Robust RGB-D SLAM"
authors:
  - "Anh Thuan Tran"
  - "Jana Kosecka"
year: 2026
venue: arXiv
status: skimmed
tags:
  - slam
  - rgb-d-slam
  - uncertainty
  - 3dgs
---

## 一句话总结

VarSplat通过学习每个高斯的显式外观方差，利用全方差定律+Alpha合成在单次光栅化中渲染可微的逐像素不确定性图，引导跟踪、子图配准和回环检测聚焦可靠区域，在低纹理/透明表面/复杂反射区域显著提升RGB-D SLAM鲁棒性。

## 解决的问题

现有3DGS-SLAM隐式处理测量可靠性，在低纹理区域、透明表面或复杂反射属性区域，位姿估计和全局对齐容易漂移。核心洞察：**显式建模每个高斯的方差可以提供逐像素的不确定性信号**，指导优化聚焦可信区域。

## 核心贡献

**1. 逐高斯外观方差学习。** 为每个3D高斯显式学习外观方差参数，编码该高斯在不同视角下外观的一致性程度。

**2. 可微不确定性渲染。** 利用全方差定律（law of total variance）+ Alpha合成，在单次光栅化中高效渲染逐像素不确定性图——不需要额外渲染pass。

**3. 不确定性引导的多层级优化。** 渲染的不确定性图同时引导：(a) 帧到模型跟踪——低不确定性像素权重更高；(b) 子图配准——不确定性加权ICP；(c) 回环检测——在可靠区域提取特征。

## 关联

- [[concepts/slam]] — SLAM基础框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示
- [[concepts/alpha-compositing]] — Alpha合成用于渲染不确定性
- [[concepts/differentiable-rendering]] — 可微渲染管线
- [[concepts/covariance-matrix]] — 协方差矩阵与方差建模的关系
- [[concepts/uncertainty-aware-tracking]] — 不确定性引导跟踪是本文核心创新
- [[papers/wildgs-slam]] — 互补方向：WildGS-SLAM用不确定性做动态检测，VarSplat用不确定性做跟踪鲁棒
