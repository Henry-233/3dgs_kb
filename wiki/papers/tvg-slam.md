---
title: "TVG-SLAM: Robust Gaussian Splatting SLAM with Tri-view Geometric Constraints"
authors:
  - "Zhen Tan"
  - "Xieyuanli Chen"
  - "Lei Feng"
  - "Yangbing Ge"
  - "Shuaifeng Zhi"
  - "Jiaxiong Liu"
  - "Dewen Hu"
year: 2025
venue: arXiv
status: skimmed
tags:
  - slam
  - rgb-only-slam
  - outdoor-slam
  - 3dgs
---

## 一句话总结

TVG-SLAM针对纯RGB 3DGS-SLAM在室外无界环境中因视角和光照剧变导致跟踪失败的难题，提出三视图几何约束范式——通过稠密三视图匹配构建鲁棒跨帧几何约束，替代单纯依赖光度误差的跟踪策略，在最具挑战性数据集上ATE降低69%。

## 解决的问题

现有纯RGB 3DGS-SLAM系统（MonoGS、GS-SLAM等）严重依赖光度渲染损失进行相机跟踪，在无界室外环境中面临严重视角变化和光照变化时鲁棒性不足。核心矛盾：**光度一致性假设在室外场景中频繁失效**，需要几何约束作为补充。

## 核心贡献

**1. 稠密三视图匹配模块。** 将可靠的成对对应关系聚合为一致的三视图匹配，构建跨帧鲁棒几何约束——三视图几何比成对几何更严格，能有效滤除误匹配。

**2. 混合几何约束跟踪（Hybrid Geometric Constraints）。** 利用三视图匹配构建几何约束与光度损失互补，在剧烈视角偏移和光照变化下保持位姿估计的准确性和稳定性。

**3. 概率初始化策略。** 将三视图对应关系的几何不确定性编码到新初始化高斯的协方差中，使高斯初始化质量直接反映观测可靠性。

**4. 动态渲染信任衰减（DART）。** 在建图延迟导致渲染不可靠时自动降低渲染损失的权重，缓解建图延迟引入的跟踪漂移。

## 关联

- [[concepts/slam]] — SLAM基础框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示
- [[concepts/differentiable-rendering]] — 可微渲染管线
- [[concepts/ssim-loss]] — 颜色损失中的SSIM分量
- [[concepts/adaptive-density-control]] — 高斯密度管理
- [[concepts/tri-view-geometric-constraints]] — 三视图几何约束是本文核心创新
- [[concepts/projection-transform]] — 多视图几何投影基础
- [[papers/mono-gs]] — 纯RGB 3DGS-SLAM基线方法
