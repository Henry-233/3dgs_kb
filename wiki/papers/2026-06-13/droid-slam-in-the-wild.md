---
title: "DROID-SLAM in the Wild: Robust RGB SLAM with Uncertainty-aware Bundle Adjustment"
authors: "Moyang Li, Zihan Zhu, Marc Pollefeys, Daniel Barath"
year: 2026
venue: CVPR 2026
status: skimmed
---

## 一句话总结

基于**可微不确定性感知Bundle Adjustment**的鲁棒实时RGB SLAM，通过多视图视觉特征不一致性估计逐像素不确定性，无需预定义动态先验即可在杂乱动态场景中实现SOTA跟踪与重建。

## 解决的问题

传统SLAM假设静态场景，在有运动物体的环境中跟踪失败。现有动态SLAM依赖预定义动态先验或不确定性感知建图，面对未知动态物体或高度杂乱场景仍受限。DROID-SLAM in the Wild通过多视图特征不一致性估计不确定性，无需任何动态先验。

## 核心贡献 (from abstract)

- **可微不确定性感知Bundle Adjustment**：利用多视图视觉特征不一致性估计逐像素不确定性，实现动态环境鲁棒跟踪
- **无需预定义动态先验**：不依赖语义标注或已知动态物体类别，对未知动态物体泛化
- **统一不确定性框架**：同时改进跟踪精度和场景几何重建
- 杂乱动态场景中SOTA位姿估计与几何重建，实时运行约10 FPS
- CVPR 2026接收

## 关联

- [[concepts/slam]] — SLAM问题定义
- [[concepts/bundle-adjustment]] — Bundle Adjustment基础
- [[concepts/uncertainty-aware-bundle-adjustment]] — 本文核心贡献：多视图特征不一致性驱动的可微BA
- [[concepts/uncertainty-aware-tracking]] — 对比：VarSplat的方差学习不确定性跟踪
- [[concepts/uncertainty-aware-mapping]] — 对比：WildGS-SLAM的不确定性建图
- [[concepts/scene-consistency-analysis]] — 对比：ADD-SLAM的渲染vs观测一致性分析
- [[papers/2026-06-11/add-slam]] — 同为prior-free动态SLAM，不同技术路线
- [[papers/2026-06-13/dy3dgs-slam]] — 同为单目动态SLAM
- [[papers/2026-06-13/ggd-slam]] — 同为单目动态SLAM，可泛化运动模型方法
- [[synthesis/dynamic-slam-comparison]] — 动态SLAM方法综合对比
- [[synthesis/robustness-dimensions]] — 鲁棒性维度分解框架

## 待精读标记: ⬜ 未精读
