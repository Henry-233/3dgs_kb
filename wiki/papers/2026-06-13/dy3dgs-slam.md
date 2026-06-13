---
title: "Dy3DGS-SLAM: Monocular 3D Gaussian Splatting SLAM for Dynamic Environments"
authors: "Mingrui Li, Yiming Zhou, Hongxing Zhou, Xinggang Hu, Florian Roemer, Hongyu Wang, Ahmad Osman"
year: 2025
venue: arXiv
status: skimmed
---

## 一句话总结

首个纯单目RGB输入的动态场景3DGS-SLAM，通过**概率融合光流mask与深度mask**检测动态区域，并结合**运动损失**约束位姿估计，实现SOTA动态环境跟踪与渲染。

## 解决的问题

现有NeRF/3DGS SLAM在含运动物体的动态场景中跟踪和重建性能严重退化，且已有的动态NeRF-SLAM依赖RGB-D输入。Dy3DGS-SLAM首次以**纯单目RGB**实现动态场景的3DGS-SLAM。

## 核心贡献 (from abstract)

- **概率融合动态mask**：将光流mask与深度mask通过概率模型融合，单次网络迭代即可约束跟踪尺度并优化渲染几何
- **运动损失 (motion loss)**：基于融合动态mask设计的新型损失函数，约束位姿估计网络的跟踪精度
- **动态像素渲染损失**：在建图阶段利用动态像素的颜色和深度渲染损失，消除动态物体造成的瞬态干扰和遮挡
- SOTA跟踪与渲染性能：在动态环境中超越或匹配现有RGB-D方法

## 关联

- [[concepts/3d-gaussian]] — 基础3DGS表示
- [[concepts/slam]] — SLAM问题定义
- [[concepts/temporal-gaussian-model]] — 时序高斯建模动态物体
- [[concepts/scene-consistency-analysis]] — 另一种prior-free动态检测方法（渲染vs观测对比）
- [[concepts/alpha-compositing]] — 动态像素渲染损失的基础渲染操作
- [[concepts/probabilistic-dynamic-segmentation]] — 本文核心贡献：概率光流+深度mask融合
- [[papers/2026-06-11/add-slam]] — 同为纯RGB动态SLAM，场景一致性分析方法
- [[papers/2026-05-21/wildgs-slam]] — 不确定性感知动态SLAM
- [[synthesis/dynamic-slam-comparison]] — 动态SLAM方法综合对比

## 待精读标记: ⬜ 未精读
