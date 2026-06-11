---
title: "时序高斯模型"
stub: true
tags:
  - dynamic-scene
  - 3dgs
---

## 定义

时序高斯模型 $\bm{G}_{d}^{id}(t)$ 将动态物体表示为随时间变化的高斯椭球体集合，每个时刻 $t$ 的高斯参数 $(\mu_i^t, \Sigma_i^t, o_i^t, h_i^t)$ 随物体运动独立优化，实现在线增量动态建模。

## 关联

- [[concepts/3d-gaussian]]
- [[concepts/slam]]
- [[papers/add-slam]]
