---
title: "前馈式位姿预测"
tags: [concept, slam, tracking, feed-forward]
---

## 定义
前馈式位姿预测（Feed-forward Pose Prediction）是一种SLAM跟踪范式：用神经网络直接从传感器数据（光流、图像特征）一次性预测相机位姿，替代传统的迭代非线性优化（如DBA、光度误差最小化、Levenberg-Marquardt）。核心优势是将跟踪从数十到数百毫秒的迭代过程压缩为单次网络前向pass（<10ms）。

## 直觉理解
传统SLAM跟踪像一个"猜-验证-调整"的循环：猜一个位姿→渲染/投影看差多少→调整→再猜→再调……重复几十次。前馈式位姿预测像是一个训练有素的"投篮手"：看准篮筐（当前帧的光流/特征），直接出手，一次命中。速度极快，但需要大量训练数据来培养"手感"。

## 与传统优化的对比

| | 优化式跟踪 | 前馈式跟踪 |
|---|---|---|
| 机制 | 迭代非线性最小二乘 | 神经网络单次前向pass |
| 速度 | 慢（50-200ms/帧） | 快（<10ms/帧） |
| 泛化 | 无训练域限制 | 受训练数据分布限制 |
| 初始化 | 需要较好初值 | 无需初值 |
| 典型方法 | DBA (DROID-SLAM), SplaTAM, G²-Mapping | Pseudo Depth Meets Gaussian |

## 技术架构（以Pseudo Depth Meets Gaussian为例）

### GRU + DBA 前馈管线

1. **稠密对应场**：将源帧像素 $p_i$ 通过估计位姿和深度投影到目标帧，得到初始对应场 $p_{ij}$
2. **GRU精化**：RAFT预训练权重，输入关联特征+光流特征，输出修正光流 $r_{ij}$ + 置信度 $w_{ij}$
3. **DBA求解**：固定深度，Gauss-Newton最小化重投影误差，CUDA实现端到端推理

整个过程无渲染/反传循环——全是网络前向pass。

### 纯2帧 vs 局部图约束

纯2帧前馈（$I_{t-1}, I_t$）极快（0.19s/帧）但对光照变化和弱纹理敏感。[[concepts/local-graph-rendering|局部图渲染（LGR）]]从3DGS渲染N个已知位姿的参考图像加入约束图，鲁棒性提升但速度略降（0.53s/帧）。

### 性能对比

| | SplaTAM（优化式） | 纯2帧前馈 | LGR前馈 |
|---|---|---|---|
| 跟踪/帧 | 65ms/iter × N iter | 0.19s | 0.53s |
| Replica ATE | 31.19 | 16.12 | 15.49 |
| 泛化 | 无限制 | 受训练域限制 | 受训练域限制 |

## 与相关概念的分辨

- [[concepts/feed-forward-3d-reconstruction|前馈式3D重建]]：关注场景几何的直接预测（如VGGT一次性输出点图/深度），而前馈式位姿预测关注的是**SLAM中的跟踪环节**
- [[concepts/bundle-adjustment|BA/DBA]]：优化式跟踪的代表，是前馈式方法试图替代的目标
- [[concepts/slam|SLAM]]：前馈式位姿预测是SLAM中跟踪模块的一种实现方式

## 关联
- 用到该概念的论文: [[papers/2026-05/pseudo-depth-meets-gaussian]]
- 相关概念: [[concepts/slam]], [[concepts/bundle-adjustment]], [[concepts/feed-forward-3d-reconstruction]], [[concepts/monocular-depth-estimation]], [[concepts/local-graph-rendering]]
