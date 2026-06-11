---
title: "Bundle Adjustment (BA) / Dense Bundle Adjustment (DBA)"
tags: [concept, optimization, slam, tracking]
---

## 定义
Bundle Adjustment（光束平差法）是同时优化3D结构与相机位姿的联合非线性优化技术，通过最小化重投影误差实现。Dense Bundle Adjustment（DBA）由DROID-SLAM引入，将BA从稀疏特征点扩展到稠密光流——对所有像素的对应关系做联合优化，而非仅若干特征角点。

## 直觉理解
BA像在做"拼图对齐"——你有从不同角度拍的多张照片和每张照片上的一些参考点。BA同时调整每张照片的拍摄位置和3D参考点的空间位置，使得当你把3D点投影回每张照片时，投影位置与观测位置尽可能一致。传统BA只对齐几百个角点（稀疏），DBA对齐上百万像素（稠密），精度大幅提升但计算量也更大。

## 数学形式

### 经典BA
$$\arg\min_{\mathbf{P}_i, \mathbf{X}_j} \sum_{i,j} \rho\left(\|\mathbf{x}_{ij} - \pi(\mathbf{P}_i, \mathbf{X}_j)\|^2\right)$$
$\mathbf{P}_i$ 为相机位姿，$\mathbf{X}_j$ 为3D点，$\pi$ 为投影函数，$\rho$ 为鲁棒核函数。

### DROID-SLAM的DBA
在关键帧图上定义光流重投影误差，通过DBA层联合优化所有关键帧位姿和逆深度：
$$\arg\min_{\omega, d} \sum_{(i,j)\in E} \|\tilde{p}_{ij} - \Pi_c(\omega_j^{-1}\omega_i \Pi_c^{-1}(p_i, d_i))\|_{\Sigma_{ij}}^2$$

## 在3DGS中的应用

### VGGT
可选的BA后处理（<2s），在前馈预测的位姿基础上进一步精化：纯前馈AUC@30=85.3 → +BA=93.5。

### WildGS-SLAM
**不确定性加权DBA**：将每像素不确定性 $\beta_i$ 融入DBA协方差：
$$\arg\min_{\omega, d} \sum_{(i,j)} \|\tilde{p}_{ij} - \Pi_c(...)\|_{\Sigma_{ij}/\beta_i^2}^2 + \lambda\|\mathbf{M}_i(d_i - 1/\tilde{D}_i)\|^2$$
动态区域 $\beta_i$ 大 → 权重小 → 不影响位姿优化。后续还有全局BA精化所有关键帧。

## 关联
- 用到BA/DBA的论文: [[papers/2026-05/vggt]], [[papers/2026-05/wildgs-slam]]
- 相关概念: [[concepts/slam]], [[concepts/ieskf]], [[concepts/structure-from-motion]]
