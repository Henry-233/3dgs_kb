---
title: "Taming the Light: Illumination-Invariant Semantic 3DGS-SLAM"
authors:
  - "Shouhe Zhang"
  - "Dayong Ren"
  - "Sensen Song"
  - "Yurong Qian"
  - "Zhenhong Jia"
year: 2025
venue: arXiv
status: skimmed
tags:
  - slam
  - semantic-slam
  - illumination-invariant
  - 3dgs
---

## 一句话总结

Taming the Light通过主动去耦（Intrinsic Appearance Normalization将反照率与瞬态光照分离）与被动纠正（Dynamic Radiance Balancing Loss仅在极端曝光帧激活）的协同机制，首次实现极端光照变化下仍能稳定工作的语义3DGS-SLAM系统。

## 解决的问题

极端曝光（过曝/欠曝）同时破坏3D地图重建质量和语义分割精度，对紧耦合系统尤为致命。现有方法缺乏专门针对光照不变性的设计，在光照剧变场景中建图和语义理解同时崩溃。

## 核心贡献

**1. Intrinsic Appearance Normalization (IAN)。** 主动将场景内在属性（如反照率albedo）与瞬态光照解耦——学习标准化、光照不变的 appearance 模型，为每个高斯基元分配稳定一致的颜色表示。IAN从表示层面使高斯对光照变化免疫。

**2. Dynamic Radiance Balancing Loss (DRB-Loss)。** 仅在图像曝光质量差时激活，直接操作辐射场进行定向优化——防止极端光照下的误差累积，同时不影响正常光照条件下的性能。

**3. IAN+DRB协同。** IAN提供前摄不变性（让系统天然抗光照变化），DRB-Loss提供被动纠正（在IAN不够时兜底），两者协同实现前所未有的光照鲁棒性。

## 关联

- [[concepts/slam]] — SLAM基础框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示
- [[concepts/spherical-harmonics]] — SH编码视角依赖外观，与IAN的去耦目标形成对比
- [[concepts/intrinsic-appearance-normalization]] — 本文核心创新：光照-反照率解耦
- [[concepts/semantic-slam]] — 语义SLAM基础
- [[papers/roger-slam]] — 互补方向：噪声+低光鲁棒（RoGER-SLAM处理传感器退化，本论文处理场景光照变化）
