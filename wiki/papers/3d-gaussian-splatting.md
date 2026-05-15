---
title: "3D Gaussian Splatting for Real-Time Radiance Field Rendering"
authors: Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis
year: 2023
venue: SIGGRAPH (ACM TOG)
tags: [paper, base]
status: done
---

## 一句话总结
提出3D Gaussian Splatting（3DGS）——用显式3D高斯椭球体表示场景，配合自适应密度控制和tile-based可微光栅化，首次实现1080p分辨率下≥30 FPS的实时高质量新视角合成。

## 解决的问题
已有NeRF类方法存在训练和渲染速度慢的瓶颈。更快的方法（如Instant-NGP）以牺牲质量为代价。对于无界完整场景和1080p渲染，没有任何方法可以实现实时显示速率。

## 核心方法
三个关键创新：
1. **3D高斯表示**：从 [[concepts/structure-from-motion|SfM]] 稀疏点云初始化3D高斯，每个高斯携带位置、协方差矩阵、不透明度和球谐函数颜色系数。VGGT等前馈模型可替代SfM提供更稠密的初始几何
2. **自适应密度优化**：训练中周期性执行高斯的克隆、分裂和剪枝操作，自动适应场景几何复杂度
3. **Tile-based快速渲染**：将屏幕划分为16×16 tile，每个tile独立排序和Alpha合成，GPU友好

训练损失：$L = 0.8 L_1 + 0.2 (1 - SSIM)$

## 与前作的区别
| 前作 | 区别 |
|------|------|
| NeRF | 3DGS用显式高斯替代MLP隐式表示，渲染快100-1000倍 |
| Instant-NGP | 3DGS渲染速度更快，视觉质量更好 |
| Plenoxels | 3DGS用各向异性高斯替代各向同性体素，表示更高效 |

## 实验结论
- 在Mip-NeRF360、Tanks&Temples、Deep Blending等数据集上达到SOTA视觉质量
- 1080p分辨率下渲染速度 ≥ 30 FPS
- 训练时间约30-60分钟（单GPU）

## 关联
- 被引用: [[papers/mip-splatting]], [[papers/gaussian-opacity-fields]], [[papers/street-gaussians]], [[papers/mobile-gs]], [[papers/langsplat]], [[papers/dr-splat]], [[papers/gs-livo]], [[papers/g2-mapping]]
- 相关方法: [[papers/vggt]]（替代SfM初始化）
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/covariance-matrix]], [[concepts/spherical-harmonics]], [[concepts/alpha-compositing]], [[concepts/tile-based-rasterization]], [[concepts/adaptive-density-control]], [[concepts/projection-transform]], [[concepts/ssim-loss]], [[concepts/structure-from-motion]]
