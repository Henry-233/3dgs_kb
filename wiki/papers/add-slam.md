---
title: "ADD-SLAM: Adaptive Dynamic Dense SLAM with Gaussian Splatting"
authors:
  - "Wenhua Wu"
  - "Chenpeng Su"
  - "Siting Zhu"
  - "Tianchen Deng"
  - "Zhe Liu"
  - "Hesheng Wang"
year: 2025
venue: arXiv
status: done
tags:
  - slam
  - dynamic-slam
  - 3dgs
---

## 一句话总结

ADD-SLAM是一种无需预定义语义类别的自适应动态SLAM系统，通过场景一致性分析检测运动物体，并同时构建静态与动态组合高斯地图（dynamic-static composite map），在Bonn和TUM RGB-D数据集上达到SOTA跟踪精度。

## 解决的问题

动态物体会破坏3DGS-SLAM中的场景一致性，导致跟踪漂移和建图伪影。现有方法有两类缺陷：(1) 基于语义分割/目标检测的方法依赖预定义类别先验，无法处理未知动态类别，且可能误判静止的人/车；(2) 基于不确定性感知的方法（如WildGS-SLAM）在边界处模糊、短序列时训练不充分。两类方法都直接丢弃动态物体信息，但动态信息对机器人避障和交互至关重要。

## 核心方法

ADD-SLAM的核心思路是：**场景是静态的假设意味着历史高斯地图的渲染结果应与当前观测一致；当有物体运动时，渲染与观测之间会出现颜色和几何不一致。通过检测这些不一致，就能自适应地发现任意类别的动态物体。**

流程分为四步：

**1. 静态地图初始化。** 第一帧RGB-D图像根据内参和初始位姿重建为点云，初始化为3D高斯椭球体 $\bm{G}_s$。

**2. 自适应动态物体检测与跟踪。** 这是核心创新，分四阶段：
- **场景一致性分析**：计算颜色不一致 $I_{err} = \|I - \hat{I}\|_2$ 和几何不一致 $D_{err} = \|D - \hat{D}\|_1$，联合阈值得到不一致区域 $M_{ic} = (I_{err} > \tau_I) \cup (D_{err} > \tau_D)$，其中 $\tau_I = 20 \cdot \text{median}(I_{err})$，$\tau_D = 20 \cdot \text{median}(D_{err})$。
- **动态区域定位**：利用深度方向区分动态物体和新暴露背景——动态物体遮挡背景使观测深度小于渲染深度，因此 $M_{ic}^d = M_{ic} \cap ((D - \hat{D}) < 0)$。
- **MobileSAM精细分割**：以不一致区域的内切圆中心作为点提示输入MobileSAM $f_\theta$，获得完整动态物体掩码 $M_d = f_\theta(I, o(M_{ic}^d))$。
- **2D动态跟踪**：为每个动态物体分配唯一id，在后续帧中以物体中心为提示持续跟踪，无需重复检测。跟踪终止条件：中心靠近图像边界4%以内，或mask面积增长>1.5倍，或中心移动>20%视野。

**3. 相机跟踪。** 在排除动态区域 $M_d$ 的静态区域上优化位姿：$T_t = \arg\min \lambda_{track} \sum M_{track} \cdot \|\hat{I} - I\|_1 + (1-\lambda_{track}) \sum (M_{track} \cap M_v) \cdot \|\hat{D} - D\|_1$，其中 $M_{track} = (\neg M_d) \cap (\hat{O} > \tau_{track})$，$\tau_{track} = 0.7$。引入Droid-SLAM的DBA层进行关键帧全局BA，并用动态掩码过滤动态区域。

**4. 动态-静态组合建图。** 这是与所有现有动态SLAM的关键区别——不丢弃动态物体，而是建模它们：
- **动态-静态分离**：检测到动态物体后，从渲染图中用MobileSAM分割，利用深度图反投影获得动态点云，从原静态高斯图中滤除。
- **静态建图**：对空洞和低质量区域插入新高斯，$M_{insert} = (\neg M_d) \cap M_v \cap (\hat{O} < \tau_{map})$，$\tau_{map} = 0.8$。用L1+SSIM渲染损失优化。
- **动态建图**：为每个动态物体id构建时序高斯模型 $\bm{G}_d^{id}(t) = \{(\mu_i^t, \Sigma_i^t, o_i^t, h_i^t)\}$，独立渲染和优化。组合渲染 $\bm{G}_{all}(t) = \bm{G}_s \cup \{\bm{G}_d^{id}(t), id \in ID\}$。

## 数学形式

**场景一致性分析：**
$$I_{err} = \|I - \hat{I}\|_2, \quad D_{err} = \|D - \hat{D}\|_1$$
$$M_{ic} = (I_{err} > \tau_I) \cup (D_{err} > \tau_D)$$
$$M_{ic}^d = M_{ic} \cap ((D - \hat{D}) < 0)$$

**MobileSAM精细分割：**
$$M_d = f_\theta(I, o(M_{ic}^d))$$

**跟踪损失（排除动态区域）：**
$$M_{track} = (\neg M_d) \cap (\hat{O} > \tau_{track})$$
$$T_t = \arg\min \lambda_{track} \sum M_{track} \cdot \|\hat{I} - I\|_1 + (1-\lambda_{track}) \sum (M_{track} \cap M_v) \cdot \|\hat{D} - D\|_1$$

**关键帧BA（过滤动态）：**
$$\mathbf{E}(\mathbf{T}, \mathbf{d}) = \sum_{(i,j)\in\mathcal{E}} \|\mathbf{p}_{ij}^* - \Pi_c(\mathbf{T}_{ij} \circ \Pi_c^{-1}(\mathbf{p}_i, \mathbf{d}_i))\|^2_{\Sigma_{ij} \cdot \neg M_d}$$

**静态建图损失：**
$$L_{map}^{static} = \lambda_{color} L_I + \lambda_{depth} L_D + \lambda_{reg} L_{reg}$$

**时序高斯动态模型：**
$$\bm{G}_d^{id}(t) = \{(\mu_i^t, \Sigma_i^t, o_i^t, h_i^t)\}$$

## 与前作的区别

| 方法 | 动态检测方式 | 是否需要先验 | 动态物体处理 |
|------|------------|------------|------------|
| DG-SLAM | 语义分割 + 多视图深度warp | 需要类别先验 | 直接过滤 |
| WildGS-SLAM | MLP+DINOv2预测不确定性 | 无需先验 | 直接过滤 |
| DynaSLAM | Mask R-CNN语义分割 | 需要类别先验 | 直接过滤 |
| **ADD-SLAM** | **场景一致性分析 + MobileSAM** | **无需先验，类别无关** | **时序高斯建模** |

**vs WildGS-SLAM**：WildGS-SLAM用不确定性图，但边界模糊、短序列MLP训练不充分。ADD-SLAM用几何/颜色不一致性直接检测，边界更精确（Fig. 4, DAVIS数据集对比），且能建模动态物体而不仅过滤。

**vs DG-SLAM**：DG-SLAM的多视图深度warp掩码包含视点变化导致的遮挡噪声（Fig. 14），而ADD-SLAM通过深度方向区分真正的动态区域。

**核心独特优势**：ADD-SLAM是首个同时支持类别无关动态检测和动态物体在线建模的3DGS-SLAM系统。

## 实验结论

**跟踪精度（ATE RMSE cm）：**
- Bonn数据集：平均 **2.77 cm**，优于WildGS-SLAM (2.93 cm RGB / 2.88 cm RGBD)，远超SplaTAM (77.6 cm)
- TUM RGB-D数据集：平均 **1.25 cm**，略优于WildGS-SLAM† (1.32 cm)，大幅优于MonoGS (18.2 cm)
- 消融实验：去掉动态检测→52.5 cm（balloon场景），用MaskDINO语义分割替代→5.5 cm，去掉关键帧DBA→3.3 cm

**渲染质量（Bonn数据集平均）：**
- PSNR **22.41 dB** vs SplaTAM 17.95 / MonoGS 20.64
- SSIM **0.89** vs SplaTAM 0.72 / MonoGS 0.77
- LPIPS **0.26** vs SplaTAM 0.27 / MonoGS 0.35

**运行时（ms）：**
- 动态分割 68.79 / 跟踪 1025.39 / 建图 1108.78
- 动态分割比Rodyn-SLAM (278.66 ms)快4倍

**阈值鲁棒性**：10×-30×中位数误差阈值范围内动态掩码结果稳定（Fig. 13）。

## 局限性

1. **依赖MobileSAM**：复杂环境下MobileSAM的局部分割或过度分割会影响性能
2. **单帧初始化假设**：第一帧初始化为全静态地图，虽然后续能检测运动物体，但首帧大面积运动时初始化质量受影响
3. **无回环检测**：依赖Droid-SLAM的DBA做关键帧优化，但未集成独立的回环检测模块
4. **动态建模精度**：时序高斯模型每帧独立优化，长序列可能累积误差

## 关联

- [[concepts/slam]] — 基础SLAM框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示
- [[concepts/adaptive-density-control]] — 高斯椭球体的增删管理
- [[concepts/sam]] — SAM用于动态物体分割
- [[concepts/alpha-compositing]] — 可微渲染核心
- [[concepts/bundle-adjustment]] — 全局BA用于回环检测
- [[concepts/temporal-gaussian-model]] — 时序高斯建模动态物体
- [[concepts/scene-consistency-analysis]] — 无先验的动态检测方法
- [[concepts/differentiable-rendering]] — 可微渲染管线
- [[papers/wildgs-slam]] — 主要对比方法：不确定性感知动态SLAM
- [[papers/up-slam]] — 同期工作：并行跟踪建图的动态SLAM
