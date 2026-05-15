---
title: "3D高斯"
tags: [concept, math, rendering]
---

## 定义
3D高斯是三维空间中的高斯分布函数，在3DGS中作为场景的基本表示单元。每个3D高斯由一个均值向量（中心位置）和协方差矩阵定义其空间范围与方向，并携带不透明度和颜色信息（通过球谐函数编码）。场景由数百万个这样的3D高斯组成的显式点云构建而成。

## 直觉理解
可以将每个3D高斯想象成三维空间中的一个"模糊椭球体"——它在中心最亮（高密度），向边缘逐渐变淡（高斯衰减）。成千上万个这样的椭球体堆叠在一起，从某个视角看去，它们叠加形成了完整的图像。相比于NeRF用神经网络隐式编码场景，3D高斯是显式的、可以自由移动和调整的几何体。

## 数学形式
3D高斯函数定义如下：

$$G(x) = e^{-\frac{1}{2}(x - \mu)^T \Sigma^{-1} (x - \mu)}$$

其中：
- $\mu \in \mathbb{R}^3$：高斯中心（均值）
- $\Sigma \in \mathbb{R}^{3 \times 3}$：协方差矩阵，描述椭球形状与方向

协方差矩阵分解为：$\Sigma = RSS^T R^T$
- $R$：旋转矩阵（四元数参数化）
- $S$：缩放矩阵（对角矩阵，3个尺度参数）

## 关联
- 相关概念: [[concepts/covariance-matrix]], [[concepts/spherical-harmonics]], [[concepts/projection-transform]]
- 用到该概念的论文: [[papers/3d-gaussian-splatting]], [[papers/mip-splatting]], [[papers/gaussian-opacity-fields]], [[papers/street-gaussians]], [[papers/langsplat]], [[papers/gs-livo]], [[papers/g2-mapping]]

3DGS中每个高斯携带颜色和几何信息（SH系数、不透明度、协方差）。LangSplat扩展了这一表示，为每个3D高斯添加语言特征向量（从CLIP蒸馏），使高斯同时具备视觉和语义表达能力。
