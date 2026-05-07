---
title: "Mip-Splatting: Alias-free 3D Gaussian Splatting"
authors: Zehao Yu, Anpei Chen, Binbin Huang, Torsten Sattler, Andreas Geiger
year: 2023
venue: CVPR
tags: [paper, extension]
status: done
---

## 一句话总结
指出3DGS在改变采样率（如缩放焦距或改变相机距离）时出现严重混叠伪影，原因是缺乏3D频率约束和2D dilation滤波器的使用，提出3D平滑滤波器和2D Mip滤波器来解决该问题。

## 解决的问题
3DGS在训练图像为单尺度时，改变测试采样率会产生强烈的混叠和高频伪影。这与NeRF社区已有Mip-NeRF等解决多尺度渲染问题形成对比——3DGS此前缺乏对应的抗混叠机制。

## 核心方法
两个关键技术：

1. **3D平滑滤波器**：基于输入视图的最大采样频率约束每个3D高斯的尺寸，消除放大时的高频伪影

2. **2D Mip滤波器**：用模拟2D盒式滤波器的2D Mip滤波器替代原3DGS中的2D dilation滤波器，有效缓解混叠和dilation问题

核心思想：引入频率感知，使高斯的频率内容与输入视图的采样率匹配。

## 与前作的区别
- 继承3DGS的显式高斯表示和快速渲染
- 新增3D频率约束，类比Mip-NeRF在NeRF系列中的作用
- 在不显著增加计算开销的前提下解决混叠问题

## 实验结论
- 在单尺度训练、多尺度测试场景下，显著优于原始3DGS
- 消除放大时的伪影，同时保持渲染速度优势
- 多个数据集上验证有效性

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/alpha-compositing]], [[concepts/ssim-loss]]
- 相关方法: [[concepts/mip-nerf]]
