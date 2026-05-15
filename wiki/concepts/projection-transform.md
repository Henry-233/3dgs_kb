---
title: "投影变换"
tags: [concept, math, rendering]
---

## 定义
投影变换是将3D高斯从世界坐标系映射到2D图像平面的数学操作。3DGS中使用局部仿射近似：将3D协方差矩阵通过视图变换和投影变换的雅可比矩阵映射为2D协方差矩阵，从而在屏幕空间执行高效的2D高斯评估和Alpha合成。

## 直觉理解
用聚光灯照射一个3D椭球体到墙上——墙上呈现的是一个2D椭圆光斑。椭球的朝向、形状和聚光灯的角度共同决定了墙上椭圆的大小和方向。投影变换就是精确计算这个"墙上投影"的数学工具。

## 数学形式
将3D协方差 $\Sigma$ 投影为2D协方差 $\Sigma'$：

$$\Sigma' = J W \Sigma W^T J^T$$

- $W$：世界到相机的视图变换矩阵
- $J$：透视投影的雅可比矩阵（局部仿射近似）

该近似对于小尺寸高斯足够精确。

## 关联
- 相关概念: [[concepts/covariance-matrix]]、[[concepts/3d-gaussian]]、[[concepts/point-map]]（投影的逆操作）
- 用到该概念的论文: [[papers/3d-gaussian-splatting]]、[[papers/gs-livo]]、[[papers/vggt]]、[[papers/g2-mapping]]

## 扩展：位姿可微性

G²-Mapping在投影变换链路上进一步推导了相机位姿的Jacobian，使SLAM中的位姿优化可以通过高斯渲染的可微性实现。将3D点从世界坐标变换到相机坐标 P_c = q_cw ⊗ P ⊗ q_cw* + t_cw 后，分别对四元数 q_cw 和平移 t_cw 求导：

$$\frac{\partial P_c}{\partial q_{cw}} = 2[J_{imag} | J_{real}] \in \mathbb{R}^{3\times4}, \quad \frac{\partial P_c}{\partial t_{cw}} = I_3$$

这使得在线SLAM中可以通过可微渲染直接优化相机位姿，而无需额外的位姿估计算法。
