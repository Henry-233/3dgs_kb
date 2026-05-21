---
title: "SLAM（同步定位与建图）"
tags: [concept, slam, robotics]
---

## 定义
SLAM（Simultaneous Localization and Mapping，同步定位与建图）是机器人学和计算机视觉中的核心问题：机器人/设备在未知环境中移动时，同时估计自身位姿（定位）并构建环境地图（建图）。这是"鸡和蛋"问题——精确建图需要精确位姿，精确位姿需要精确地图——二者必须联合求解。

## 直觉理解
想象你蒙着眼睛被人推进一个陌生房间，你需要一边摸墙判断自己在哪里（定位），一边在脑中画房间的布局图（建图）。每一步你摸到的墙既帮你更新位置估计，也帮你完善地图。随着你在房间里走动，你对位置的估计和地图的精度应该逐步提高——这就是SLAM的闭环过程。

## 数学形式

### 概率形式
SLAM通常建模为贝叶斯滤波问题：
$$p(x_{1:t}, m \mid z_{1:t}, u_{1:t-1})$$

其中 $x_t$ 是 $t$ 时刻的位姿，$m$ 是地图，$z_t$ 是观测，$u_t$ 是控制输入。

### 两种主流框架
- **滤波方法**：扩展卡尔曼滤波（EKF）、粒子滤波（FastSLAM）——增量式处理
- **图优化方法**：构建因子图（factor graph），使用非线性最小二乘求解——离线或滑动窗口优化

## SLAM与3DGS

### NeRF-SLAM (2021-2023)
iMAP、NICE-SLAM、ESLAM等将NeRF用作隐式地图表示，但因体渲染计算量大，地图更新通常滞后于里程计。

### Gaussian-SLAM (2024-)
3DGS因其显式表示和快速可微光栅化成为SLAM的理想地图表示：

| 系统 | 传感器 | 核心策略 |
|------|--------|---------|
| SplaTAM | RGB-D | 轮廓引导高斯增删 |
| GS-SLAM | RGB-D | 自适应扩展 |
| MonoGS | Mono/RGB-D | 深度损失+手动位姿Jacobian |
| PhotoSLAM | Mono/Stereo/RGB-D | 结合ORB特征与高斯金字塔 |
| **GS-LIVO** | **LiDAR+IMU+Camera** | **多传感器融合+哈希八叉树+滑动窗口** |
| **G²-Mapping** | **Mono/RGB-D/LIV** | **通用可微渲染器（颜色+深度+位姿）+ 渲染管线感知高斯增删 + 深度不确定性加权** |
| **WildGS-SLAM** | **Mono** | **不确定性感知（DINOv2+MLP预测不确定性图）+ 动态场景鲁棒跟踪建图** |

Gaussian-SLAM的优势：渲染快、表示显式可调、可微渲染天然适合位姿优化。挑战：地图更新频率、GPU显存、大场景可扩展性——GS-LIVO通过滑动窗口和多传感器融合针对性解决了这些问题。

## 动态SLAM（Dynamic SLAM）

传统SLAM假设场景刚性（static world assumption），动态物体会破坏特征匹配和光度一致性，导致严重跟踪漂移。动态SLAM的核心挑战是在跟踪和建图中识别并排除动态干扰物。

### 主要策略
| 策略 | 方法 | 局限 |
|------|------|------|
| 语义分割 | DynaSLAM（Mask R-CNN）、DG-SLAM（YOLO）、DDN-SLAM（目标检测+高斯混合模型） | 依赖预定义物体类别，对未知动态物体失效 |
| 几何残差 | ReFusion（TSDF+深度残差）、StaticFusion | 需要RGB-D深度传感器 |
| 光流/运动检测 | RoDyn-SLAM（光流+刚性运动）、DynaMoN（运动分割+语义） | 纹理弱区域不可靠 |
| **不确定性感知** | **WildGS-SLAM（DINOv2+MLP预测不确定性加权DBA和渲染损失）** | 仅需单目RGB，无类别先验，在线适应 |

### WildGS-SLAM的不确定性感知方案
- 预训练DINOv2（3D-aware微调）提取特征 → 浅层MLP在线预测逐像素不确定性 $\beta$
- **跟踪**：不确定性加权DBA $\sum \|\tilde{p}_{ij} - \Pi(\cdots)\|^2_{\Sigma_{ij}/\beta_i^2}$
- **建图**：不确定性加权渲染损失 $\mathcal{L}_{\text{render}} = (\mathcal{L}_{\text{color}} + \lambda \mathcal{L}_{\text{depth}})/\beta^2$
- 不确定性预测器与高斯地图独立优化，梯度互不传播

## 关联
- 相关概念: [[concepts/ieskf]], [[concepts/uncertainty-aware-mapping]]
- 用到该概念的论文: [[papers/gs-livo]], [[papers/g2-mapping]], [[papers/wildgs-slam]]
- 基于该范式的Gaussian-SLAM: [[papers/3d-gaussian-splatting]]
