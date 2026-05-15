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
- 用到该概念的论文: [[papers/3d-gaussian-splatting]]、[[papers/gs-livo]]、[[papers/vggt]]
