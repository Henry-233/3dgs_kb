---
title: "Mip-NeRF"
tags: [concept, rendering, comparison]
---

## 定义
Mip-NeRF是NeRF的改进版本，通过使用锥形截锥体（conical frustum）代替单点采样来解决多尺度渲染中的混叠（aliasing）问题。它使用集成位置编码（Integrated Positional Encoding, IPE）对锥形区域内的坐标分布进行编码，使得在不同分辨率下渲染时保持抗混叠效果。

## 直觉理解
传统NeRF沿光线采样"点"，Mip-NeRF改为采样"锥形光束"——就像从一束激光换成了有一定发散角的手电筒。这样在远距离（光束覆盖更多空间）时自然产生模糊，避免了远处物体出现锯齿。这和Mip-Splatting解决的是同一类混叠问题，只是方法不同。

## 数学形式
IPE的数学形式：
- 将锥形截锥体近似为多元高斯分布
- 计算位置编码在该高斯分布下的期望
- $\gamma(\mu, \Sigma) = \mathbb{E}_{x \sim \mathcal{N}(\mu, \Sigma)}[\gamma(x)]$

Mip-NeRF 360进一步扩展到无界场景。

## 关联
- 相关概念: [[concepts/nerf]]
- 相关方法: [[papers/mip-splatting]]（3DGS中的对应抗混叠方案）
