---
title: "ADD-SLAM: Adaptive Dynamic Dense SLAM with Gaussian Splatting"
authors:
  - "Wenhua Wu"
  - "Chenpeng Su"
  - "Siting Zhu"
  - "Tianchen Deng"
  - "Zhe Liu"
  - "Hesheng Wang"
year: 2025
venue: arXiv
status: skimmed
tags:
  - slam
  - dynamic-slam
  - 3dgs
---

## 一句话总结

ADD-SLAM是一种无需预定义语义类别的自适应动态SLAM系统，通过场景一致性分析检测运动物体，并同时构建静态与动态组合高斯地图。

## 解决的问题

动态物体会破坏3DGS-SLAM中的场景一致性，导致跟踪漂移和建图伪影。现有方法依赖预定义类别先验（语义分割/目标检测），无法处理未知动态类别，且丢弃了对机器人应用至关重要的动态信息。

## 核心贡献

- **场景一致性分析的动态识别**：通过比较实时观测与历史地图的几何和纹理差异检测动态区域，无需语义先验，完全类别无关
- **MobileSAM精细化分割**：利用视觉基础模型从不一致区域的中心点提示获得完整动态物体掩码
- **动态-静态分离建图**：构建时序高斯模型 $\bm{G}_{d}^{id}(t)$ 实现在线增量动态建模，同时保持静态背景地图
- **动态感知的位姿优化**：跟踪时排除动态区域，仅使用静态区域进行BA优化，提升定位精度

## 关联

- [[concepts/slam]] — 基础SLAM框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示
- [[concepts/adaptive-density-control]] — 高斯椭球体的增删管理
- [[concepts/sam]] — SAM用于动态物体分割
- [[concepts/alpha-compositing]] — 可微渲染核心
- [[concepts/bundle-adjustment]] — 全局BA用于回环检测
- [[concepts/temporal-gaussian-model]] — 时序高斯建模动态物体
- [[concepts/scene-consistency-analysis]] — 无先验的动态检测方法
- [[papers/wildgs-slam]] — 对比方法：基于不确定性感知的动态SLAM
- [[papers/up-slam]] — 同期工作：并行跟踪建图的动态SLAM

## 待精读标记: ⬜ 未精读
