---
title: "GS-LIVO: Real-Time LiDAR, Inertial, and Visual Multisensor Fused Odometry With Gaussian Mapping"
authors: Sheng Hong, Chunran Zheng, Yishu Shen, Changze Li, Fu Zhang, Tong Qin, Shaojie Shen
year: 2025
venue: IEEE TRO (IEEE Transactions on Robotics)
tags: [paper, extension, slam, multisensor-fusion]
status: done
---

## 一句话总结
提出GS-LIVO——首个可部署在嵌入式设备上的实时Gaussian-SLAM系统，通过LiDAR-惯性-视觉多传感器融合实现高精度定位，并结合哈希索引八叉树全局地图和滑动窗口局部高斯优化实现实时高保真建图。

## 解决的问题

现有3DGS-SLAM系统存在三个核心瓶颈：

1. **地图更新滞后于里程计**：大多数Gaussian-SLAM方法（SplaTAM、GS-SLAM等）虽能实时估计位姿，但地图优化运行在独立慢速线程上，更新频率低，无法适应动态或大规模场景
2. **GPU显存限制**：将整个场景的高斯全部放在GPU显存中不可扩展，限制了Gaussian-SLAM在大场景中的部署
3. **初始化依赖**：纯视觉3DGS方法依赖手工启发式点云增密，难以处理遮挡和复杂几何

GS-LIVO追问：能否用LiDAR-惯性-视觉多传感器融合，构建一个在嵌入式设备上也能实时运行、且地图更新频率匹配里程计的Gaussian-SLAM系统？

## 核心方法

### 整体架构
系统由四个关键模块组成，硬件上集成同步的LiDAR、IMU和相机：

**1. 全局高斯地图：哈希索引八叉树**
- 全局地图采用空间哈希索引的递归八叉树结构
- 哈希键 = floor(高斯中心坐标 / 根体素边长)，覆盖稀疏空间体积
- 支持多层次细节（LoD），适应不同尺度和复杂度的环境
- 全局高斯存储在RAM（CPU内存），仅将当前视场角（FoV）内的高斯拷贝到VRAM（GPU显存）

**2. LiDAR-视觉联合初始化**
- 结构参数（缩放矩阵S、旋转矩阵R）由LiDAR点云初始化
- 缩放参数基于八叉树叶节点体素大小设定：沿表面切向 = 体素边长，沿法向 = 很小的薄片厚度（使高斯表现为贴附在物体表面的2D平面）
- 旋转矩阵由LiDAR点云法向量推导
- 颜色（零阶球谐系数）由相机图像双线性插值初始化，高阶SH系数置零

**3. 滑动窗口高斯维护**
- 仅在当前FoV内的高斯参与优化，限制GPU显存使用
- 利用连续帧之间的大幅重叠，增量式更新滑动窗口：更新全局地图 → 删除离开FoV的体素并压缩 → 识别重叠和新增区域 → 追加新体素到缓冲区尾部
- 避免了原始3DGS中tile-based深度排序的混叠伪影（前景污染背景）

**4. IESKF紧耦合多传感器融合里程计**
- 基于迭代误差状态卡尔曼滤波（IESKF）顺序融合LiDAR、IMU和视觉测量
- LiDAR测量：尺寸自适应体素提取平面特征，与FAST-LIO2类似
- 视觉测量：不再使用稀疏patch的光度误差，而是利用高斯地图渲染当前帧，与真实图像计算光度误差，通过高斯渲染的可微性推导Jacobian更新相机位姿
- 视觉更新的Jacobian从相机位姿传播到IMU位姿，形成紧耦合的IESKF系统

### 地图优化
滑动窗口内的高斯通过最小化光度损失进行优化：
$$\theta^* = \arg\min_\theta \|I_{obs} - I_{render}(T_{WC}; \theta)\|$$
使用Adam优化器迭代更新高斯参数。

## 与前作的区别

| 前作 | 区别 |
|------|------|
| SplaTAM / GS-SLAM | GS-LIVO多传感器融合（LiDAR+IMU+视觉），非纯视觉RGB-D；地图更新频率显著更高（10Hz vs. 低频） |
| MonoGS | GS-LIVO不依赖恒速运动模型，使用LiDAR-惯性里程计位姿先验，精度和鲁棒性大幅提升 |
| FAST-LIVO2 | GS-LIVO将稀疏surfel地图替换为稠密高斯地图，具有光度真实感渲染能力，但计算成本略高 |
| LIV-GaussMap | GS-LIVO使用哈希八叉树和滑动窗口实现更高效的地图管理和实时优化 |
| LetsGo | GS-LIVO固定层级八叉树，通过滑动窗口策略实现在线实时运行（vs. LetsGo的离线处理） |

## 实验结论

- **定位精度**：室内媲美传统LIV-SLAM方法（FAST-LIVO2），室外显著超越R3 LIVE和LVI-SAM（RMSE 0.042m vs. 1.465m/4.665m）
- **建图质量**：PSNR稳定在25-30dB，渲染质量与全GPU方法相当
- **实时性能**：室内~10Hz地图更新（单CPU线程），室外~3Hz——均为Gaussian-SLAM中最高频率
- **嵌入式部署**：NVIDIA Jetson Orin NX上总处理时间48.3ms（优化15.3ms + 地图维护18.9ms），PSNR 23.52dB
- **自主导航验证**：首次将Gaussian-SLAM集成到完整的自主导航系统（A*全局规划 + LQR轨迹跟踪），使用2D占据栅格地图进行路径规划
- **显存效率**：滑动窗口策略使GPU显存使用不随场景增长

## 局限性

1. **室内-室外过渡**：固定层级八叉树难以同时适应室内精细结构和室外大尺度场景
2. **计算开销**：维护稠密高斯地图比稀疏表示（如FAST-LIVO2的surfel）消耗更多计算资源
3. **动态物体**：未专门处理动态场景物体

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 相关方法: [[concepts/slam]], [[concepts/ieskf]]
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/covariance-matrix]], [[concepts/projection-transform]], [[concepts/alpha-compositing]], [[concepts/tile-based-rasterization]], [[concepts/spherical-harmonics]], [[concepts/adaptive-density-control]]
