---
title: "NeRF"
tags: [concept, rendering, comparison]
---

## 定义
NeRF（Neural Radiance Fields）是一种用神经网络隐式表示3D场景的方法。通过MLP网络将空间坐标 $(x, y, z)$ 和观察方向 $(\theta, \phi)$ 映射为颜色和体密度，再通过体渲染（volume rendering）沿光线积分合成像素颜色。NeRF开创了可微渲染与隐式神经表示的新范式。

## 直觉理解
NeRF就像是把场景"压缩"进了神经网络的权重里——给网络输入一个位置和观察角度，网络就告诉你"这里是什么颜色、有多'实'"。要渲染一张图，就从相机出发发射光线，沿光线采样很多点，逐一查询网络，然后按透明度叠加。这和3DGS用显式高斯椭球的思路完全相反。

## 数学形式
NeRF的体渲染公式：

$$C(\mathbf{r}) = \sum_{i=1}^{N} T_i (1 - \exp(-\sigma_i \delta_i)) \mathbf{c}_i$$

其中 $T_i = \exp(-\sum_{j=1}^{i-1} \sigma_j \delta_j)$ 是累积透射率。

与3DGS的关键区别：
| 特性 | NeRF | 3DGS |
|------|------|------|
| 场景表示 | MLP隐式 | 3D高斯显式 |
| 渲染方式 | 沿光线采样 | 投影+光栅化 |
| 渲染速度 | 慢（秒级/帧） | 快（≥30 FPS） |
| 训练速度 | 慢（小时级） | 快（~30分钟） |

## 关联
- 相关概念: [[concepts/instant-ngp]], [[concepts/mip-nerf]], [[concepts/tensorf]]
- 与该方法对比的论文: [[papers/3d-gaussian-splatting]], [[papers/street-gaussians]]
