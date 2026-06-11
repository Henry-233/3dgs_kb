---
title: "场景一致性分析"
stub: true
tags:
  - dynamic-detection
  - slam
---

## 定义

场景一致性分析是一种无需预定义语义类别的动态物体检测方法：通过比较实时观测图像与历史高斯地图的渲染结果，检测颜色不一致 $I_{err}$ 和几何不一致 $D_{err}$ 来识别运动区域，完全类别无关。

## 关联

- [[concepts/slam]]
- [[concepts/differentiable-rendering]]
- [[papers/add-slam]]
