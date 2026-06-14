---
title: "不确定性感知Bundle Adjustment"
tags:
  - slam
  - bundle-adjustment
  - uncertainty
  - dynamic-slam
  - differentiable-optimization
---

## 定义

不确定性感知Bundle Adjustment（Uncertainty-aware BA, UBA）是一种**可微优化框架**，将逐像素动态不确定性作为BA残差的权重嵌入马氏距离的协方差矩阵中，使动态物体的对应残差被自动降权，从而在动态场景中实现鲁棒的联合位姿-深度优化。

## 核心思想

标准BA假设所有像素对应残差同等可信——动态物体违反这一假设。UBA通过修改残差的协方差矩阵来解决：

```
Σ_uncer_ij = diag(w_ij · 1/u_i)  (Eq.4, DROID-W)
Ê(G',d') = Σ_{(i,j)∈E} ||p*_ij − p_ij||²_Σ_uncer_ij  (Eq.5)
```

其中u_i为像素i的动态不确定性（u_i高=该像素可能在运动物体上），w_ij为对应置信度。效果：
- u_i高 → 1/u_i低 → 协方差大 → 马氏距离小 → 残差被降权
- u_i低（静态） → 1/u_i高 → 协方差小 → 残差正常参与优化

## 关键设计

### 不确定性来源：多视图特征不一致性

不依赖语义标注或预定义动态类别。用**DINOv2特征**的跨视图余弦相似度测量不一致性：

```
E_sim(u') = Σ_{(i,j)∈E} (1 − cos(F_i, F_ij)) · u'_i²  (Eq.6)
```

- 当前姿态和深度估计建立像素在视图间的刚性对应
- 如果该像素遵守刚性运动假设，跨视图特征应高度相似
- 如果特征不相似→该像素可能属于独立运动物体→提高不确定性

### 交替优化而非联合优化

联合优化位姿、深度和不确定性在Gauss-Newton框架下计算代价过高。采用**交替策略**：
1. 固定不确定性 → Gauss-Newton更新位姿和深度
2. 固定位姿和深度 → 优化不确定性

### 仿射映射参数化

不确定性不直接优化像素值，而是通过小MLP的仿射映射参数化——确保时空一致性和平滑性。添加权重衰减正则化防止过拟合。

### Monocular Depth Regularization

纯单目BA在高度动态场景中可能退化（可用的静态对应不足）。将Metric3D预测的单目深度作为BA的正则化项，提供额外的几何约束。

## 与建图侧不确定性的对比

| 维度 | UBA (DROID-W) | 建图侧不确定性 (WildGS-SLAM) |
|------|--------------|---------------------------|
| 优化位置 | BA残差权重（跟踪侧） | 高斯渲染损失（建图侧） |
| 不确定性来源 | 多视图特征不一致性 | DINOv2→MLP预测+渲染误差 |
| 依赖高质量地图 | 否 | 是（需稳定地图优化不确定性） |
| 对地图退化的鲁棒性 | 高 | 低（恶性循环） |
| 表示 | 点云 | 3DGS |

## 在SLAM系统中的应用

- **DROID-SLAM in the Wild**：UBA + DROID-SLAM DBA框架，CVPR 2026
- **VarSplat**：逐高斯方差学习+单pass不确定性渲染（不同范式：用方差的逆作为跟踪损失的权重，但方差来自渲染侧而非特征侧）

## 关联

- [[concepts/slam]]
- [[concepts/bundle-adjustment]]
- [[concepts/dinov2]]
- [[concepts/uncertainty-aware-tracking]]
- [[concepts/uncertainty-aware-mapping]]
- [[papers/2026-06-13/droid-slam-in-the-wild]]
