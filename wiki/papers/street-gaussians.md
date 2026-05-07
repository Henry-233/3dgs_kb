---
title: "Street Gaussians: Modeling Dynamic Urban Scenes with Gaussian Splatting"
authors: Yunzhi Yan, Haotong Lin, Chenxu Zhou, Weijie Wang, Haiyang Sun, Kun Zhan, Xianpeng Lang, Xiaowei Zhou, Sida Peng
year: 2024
venue: ECCV
tags: [paper, application]
status: done
---

## 一句话总结
将3DGS扩展到动态城市场景建模，将场景表示为带语义logits的前景车辆高斯和静态背景高斯，结合可优化跟踪姿态和4D球谐函数实现动态外观建模，实现自动驾驶场景的实时渲染和场景编辑。

## 解决的问题
自动驾驶场景中动态街道建模面临训练慢、渲染慢的瓶颈。此前方法（如NSG、SUDS）通过扩展NeRF跟踪车辆姿态来实现动态场景合成，但训练和渲染速度极慢。需要在保持高质量的同时实现快速训练和实时渲染。

## 核心方法
1. **场景分解**：点云分为前景（车辆）和背景，每个点配备语义logits和3D高斯
2. **动态前景建模**：每辆车的点云配备可优化的跟踪姿态（旋转+平移），结合4D球谐函数（输入方向+时间）建模动态外观
3. **高效合成**：显式高斯表示使车辆和背景的合成变得简单，支持场景编辑
4. **渲染**：使用3DGS的tile-based光栅化管线

## 与前作的区别
| 前作 | 区别 |
|------|------|
| NSG (NeRF-based) | 渲染速度快 ~1000x（135 FPS vs <1 FPS），训练快 ~10x |
| 3DGS (static) | 扩展到4D动态场景，加入语义和跟踪姿态 |
| SUDS | 显式表示支持场景编辑操作 |

## 实验结论
- KITTI和Waymo Open数据集上始终优于SOTA方法
- 渲染速度：135 FPS @ 1066×1600
- 训练时间：约30分钟
- 支持场景编辑（移除/添加/变换车辆）

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/spherical-harmonics]], [[concepts/adaptive-density-control]], [[concepts/alpha-compositing]]
- 对比方法: [[concepts/nerf]]
