---
title: "RoGER-SLAM: A Robust Gaussian Splatting SLAM System for Noisy and Low-light Environment Resilience"
authors:
  - "Huilin Yin"
  - "Zhaolin Yang"
  - "Linchuan Zhang"
  - "Gerhard Rigoll"
  - "Johannes Betz"
year: 2025
venue: arXiv
status: skimmed
tags:
  - slam
  - robust-slam
  - low-light
  - 3dgs
---

## 一句话总结

RoGER-SLAM利用3DGS渲染管线固有的隐式低通滤波特性，结合结构保持鲁棒融合、自适应跟踪和CLIP增强，实现噪声与低光环境下的鲁棒SLAM。

## 解决的问题

现有3DGS-SLAM在干净条件下表现良好，但在视觉输入受噪声和低光照影响时性能严重下降。3DGS渲染管线本质上充当隐式低通滤波器，可衰减高频噪声但有过平滑风险。

## 核心贡献

- **SP-RoFusion（结构保持鲁棒融合）**：耦合渲染外观、深度和边缘线索的多模态融合机制
- **自适应跟踪目标**：带有残差平衡正则化的跟踪损失，在退化条件下保持稳定
- **CLIP增强模块**：在复合退化条件下选择性激活，恢复语义和结构保真度
- **全面的噪声/低光实验验证**：在Replica、TUM和真实世界序列上一致优于其他3DGS-SLAM

## 关联

- [[concepts/slam]] — 基础SLAM框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示
- [[concepts/clip]] — CLIP用于语义增强
- [[concepts/alpha-compositing]] — 可微渲染核心
- [[concepts/differentiable-rendering]] — 可微渲染管线
- [[papers/3d-gaussian-splatting]] — 3DGS基础方法
- [[papers/add-slam]] — 同期动态SLAM工作

## 待精读标记: ⬜ 未精读
