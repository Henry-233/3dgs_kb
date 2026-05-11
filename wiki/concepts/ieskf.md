---
title: "IESKF（迭代误差状态卡尔曼滤波）"
tags: [concept, state-estimation, filter]
---

## 定义
IESKF（Iterated Error State Kalman Filter，迭代误差状态卡尔曼滤波）是一种用于非线性系统的状态估计方法。它维护"误差状态"（error state）而非全状态，在每次观测更新时对误差状态进行迭代线性化，从而处理高度的非线性。广泛应用于LiDAR-惯性里程计（FAST-LIO系列）和多传感器融合SLAM（FAST-LIVO系列、GS-LIVO）。

## 直觉理解
与标准卡尔曼滤波"一步到位"地更新状态不同，IESKF像是在"反复修正"：拿到新的观测后，不是立刻接受第一个估计，而是用更新后的状态重新计算"如果我现在在这个位置，观测应该长什么样"，与真实观测对比后再次修正——反复迭代直到收敛。这样做的好处是，即使初始线性化不太准确，迭代过程也能逐步逼近真实的非线性最优解。

## 数学形式

### 误差状态
将全状态 $x$ 分解为名义状态 $\hat{x}$ 和误差状态 $\delta x$：
$$x = \hat{x} \boxplus \delta x$$

在SE(3)流形上，误差状态是李代数元素 $\delta \theta \in \mathfrak{se}(3)$。

### IESKF迭代更新
对每次观测 $z_k$：
1. **预测步骤**：通过IMU运动模型传播名义状态和协方差
2. **迭代更新**（重复直到收敛）：
   - 在当前估计点线性化观测模型 $h(\cdot)$ 得到Jacobian $H$
   - 计算卡尔曼增益：$K = P H^T (H P H^T + R)^{-1}$
   - 更新误差状态：$\delta x = K (z - h(\hat{x}))$
   - 更新名义状态：$\hat{x} \leftarrow \hat{x} \boxplus \delta x$
   - 重置误差状态：$\delta x \leftarrow 0$

### 协方差恢复
每次迭代后，状态协方差以重置后的名义状态为参考重新参数化，确保下次迭代的数学一致性。

## 在GS-LIVO中的应用

GS-LIVO使用IESKF顺序融合三种传感测量：
1. **IMU预测**：高频IMU数据驱动状态预测（前向传播）
2. **LiDAR更新**：平面特征点到平面的距离残差
3. **视觉更新**：高斯渲染图像与真实图像的像素级光度残差——Jacobian通过高斯渲染的可微性链式法则传播

视觉更新的Jacobian从相机位姿传播到IMU位姿（用SE(3)伴随变换），实现了真正的紧耦合融合。与大多数Gaussian-SLAM直接用Adam优化位姿不同，IESKF能输出位姿的协方差，可进一步传播到后续传感器更新。

## 关联
- 相关概念: [[concepts/slam]]
- 用到该概念的论文: [[papers/gs-livo]]
