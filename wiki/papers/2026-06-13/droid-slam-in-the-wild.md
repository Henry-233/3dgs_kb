---
title: "DROID-SLAM in the Wild: Robust RGB SLAM with Uncertainty-aware Bundle Adjustment"
authors: "Moyang Li, Zihan Zhu, Marc Pollefeys, Daniel Barath"
year: 2026
venue: CVPR 2026 (arXiv:2603.19076v1)
status: done
tags:
  - slam
  - dynamic-slam
  - bundle-adjustment
  - uncertainty
  - monocular-slam
---

## 一句话总结

基于**可微不确定性感知Bundle Adjustment**的鲁棒实时单目RGB SLAM，通过多视图DINOv2视觉特征不一致性迭代优化逐像素动态不确定性，无需预定义动态先验即可在杂乱动态场景中实现SOTA跟踪与重建——Bonn ATE 2.30 cm / TUM ATE 1.36 cm / 自建室外数据集ATE 0.230 m，~10 FPS。

## 解决的问题

传统SLAM假设静态场景，在有运动物体的环境中跟踪失败。现有动态SLAM方法两类：(1) 依赖预定义语义先验（YOLO/SAM）检测动态物体——面对未知动态物体泛化差；(2) 依赖不确定性感知建图（WildGS-SLAM等用MLP+DINOv2估计不确定性）——但需要先构建完美的静态地图来优化不确定性，在杂乱真实场景中地图本身就不稳定。DROID-W通过**多视图特征一致性**直接优化不确定性，不依赖高质量建图或语义先验。

## 核心贡献 (from abstract)

- **可微不确定性感知Bundle Adjustment（UBA）**：将逐像素动态不确定性作为BA残差的权重（Σ_uncer = diag(w·1/u)），不确定性高→残差被降权→动态物体不影响位姿优化
- **多视图特征不一致性驱动不确定性优化**：用DINOv2特征的跨视图余弦相似度测量"该像素是否违反刚性运动假设"，相似度低→运动物体→不确定性高
- **交替优化策略**：位姿-深度精化 与 不确定性优化 交替进行，避免联合优化的计算爆炸
- **无需预定义动态先验**：不依赖语义标注或已知动态物体类别
- 自建**DROID-W室外数据集**（7条序列，LiDAR+RGB，RTK真值）+ YouTube野外视频评估

## 核心方法

### 1. 预备知识：DROID-SLAM (Sec 3.1)

DROID-SLAM维护两个状态变量：相机位姿 G_t ∈ SE(3) 和逆深度 d_t ∈ R^{H/8 × W/8}（8×下采样）。帧图 (V,E) 表示共视关系。可微BA层通过最小化稠密对应残差迭代更新位姿和深度：

```
p_ij = Π_c(G'_ij ∘ Π_c^{-1}(p_i, d'_i))  (Eq.1)
E(G',d') = Σ_{(i,j)∈E} ||p*_ij − p_ij||²_Σ_ij  (Eq.2)
```

DROID-SLAM用ConvGRU预测2D稠密对应 p*_ij 和置信度 w_ij。

### 2. 不确定性感知BA (Sec 3.2)

动态物体违反刚性运动假设，产生不可靠的对应残差。DROID-W引入**逐像素动态不确定性** u_t ∈ R^{H/8 × W/8}：

```
Σ_uncer_ij = diag(w_ij · 1/u'_i)  (Eq.4)
Ê(G',d') = Σ_{(i,j)∈E} ||p*_ij − p_ij||²_Σ_uncer_ij  (Eq.5)
```

直觉：u_i高（像素在运动物体上）→ 1/u_i低 → Σ_uncer中对应项小 → 该残差被降权。这是通过修改马氏距离的协方差矩阵实现的，完全可微。

由于联合优化位姿、深度和不确定性在Gauss-Newton框架下计算代价过高，采用**交替优化**：位姿-深度精化（Schur补，Eq.3）与不确定性优化交替进行。

### 3. 不确定性优化 (Sec 3.3)

核心洞察：**多视图特征不一致性** = 动态物体的信号。

对于帧对 (i,j)，利用当前位姿和深度估计建立刚性运动对应关系 p_ij，从I_i和I_j的DINOv2特征图中采样特征F_i和F_ij，计算余弦相似度：

```
E_sim(u') = Σ_{(i,j)∈E} (1 − cos(F_i, F_ij)) · u'_i²  (Eq.6)
```

- cos(F_i, F_ij)低（特征不一致）→ (1−cos)高 → 最小化该损失迫使u'_i降低 → 即提高不确定性
- 但u'_i不能任意增长 → 添加正则化项 u'² 防止不确定性发散

完整不确定性损失（Eq.7）：
```
E_uncertain(u') = E_sim(u') + λ_reg Σ u'_i² − α Σ log(u'_i)
```
其中 log(u'_i) 项防止不确定性退化为零。

**关键实现细节**：
- **仿射映射参数化**：不确定性通过小MLP的仿射映射参数化（而非直接优化u值），确保时空一致性
- **权重衰减**：正则化仿射映射参数，防止过拟合导致的不稳定

### 4. 系统集成 (Sec 3.4)

- **Metric3D**提供单目深度先验，作为BA的正则化项——在高度动态环境下尤为重要
- 基于DROID-SLAM的特征提取器（冻结）+ ConvGRU更新模块
- 关键帧选取策略，非关键帧位姿通过SE(3)插值+位姿图优化恢复

## 数学形式

**刚性运动对应**（Eq.1）：
```
p_ij = Π_c(G'_ij ∘ Π_c^{-1}(p_i, d'_i))
```

**不确定性感知马氏距离**（Eq.4）：
```
Σ_uncer_ij = diag(w_ij · 1/u'_i)
```

**不确定性感知能量函数**（Eq.5）：
```
Ê(G',d') = Σ_{(i,j)∈E} ||p*_ij − p_ij||²_Σ_uncer_ij
```

**特征不一致性损失**（Eq.6）：
```
E_sim(u') = Σ_{(i,j)∈E} (1 − F_i·F_ij/(||F_i||₂||F_ij||₂)) · u'_i²
```

**Gauss-Newton更新**（Eq.3）：
```
[B E; E^T C] [∆ξ; ∆d] = [v; w]  →  ∆ξ = [B − EC^{-1}E^T]^{-1}(v − EC^{-1}w)
```

## 与前作的区别

| 方法 | 动态处理机制 | 是否需要高质量建图 | 是否需要语义先验 | 表示 |
|------|-------------|-------------------|-----------------|------|
| **DROID-W** | 多视图特征不一致性→UBA | 否 | 否 | 点云（非3DGS） |
| DROID-SLAM | 无（静态假设） | — | — | 点云 |
| WildGS-SLAM | DINOv2→MLP不确定性→建图 | 是（需3DGS map在线优化不确定性） | 否 | 3DGS |
| ADD-SLAM | 渲染vs观测场景一致性 | 是（需3DGS map渲染比较） | 否 | 3DGS |
| DynaSLAM | Mask R-CNN语义分割+几何约束 | 否 | 是（已知类别） | 稀疏特征 |
| GGD-SLAM | GMM(FIFO+时序注意力) | 是（Davis预训练GMM） | 否 | 3DGS |
| Dy3DGS-SLAM | 光流+深度mask概率融合 | 否 | 否 | 3DGS |

**核心差异**：DROID-W是**非3DGS路线**——不构建高斯基元，而是直接输出点云。这使其不确定性优化不依赖建图质量，在野外环境中比3DGS-SLAM更鲁棒。

与**WildGS-SLAM**的关键区别：WildGS需要先构建高斯地图，再通过渲染误差优化DINOv2→MLP不确定性预测器。这在杂乱场景中形成恶性循环：地图差→不确定性差→地图更差。DROID-W用特征相似度直接优化不确定性，完全绕过了建图环节。

## 实验结论

### 跟踪精度
- **Bonn**（Table 1, 8场景）：ATE 2.30 cm——超过所有RGB-only和RGB-D方法（WildGS-SLAM 2.52, DynaSLAM 6.45, DROID-SLAM 4.91）
- **TUM**（Table 2, 9场景）：ATE 1.36 cm——超过DynaSLAM(1.69)、DynaMoN(1.63)、WildGS-SLAM(1.51)
- **DyCheck**（Table 3, 12场景）：ATE 0.034——超过DROID-SLAM(0.044)、WildGS-SLAM(0.056)
- **DROID-W室外**（Table 4, 7场景）：ATE 0.230 m——远超DROID-SLAM(1.460 m)，WildGS-SLAM(0.637 m)（Downtown 2从7.84降至0.25 m）

### 运行效率 (Table 5)
- Bonn: 10.57 FPS (RTX 3090)
- TUM: 14.92 FPS
- DyCheck: 11.06 FPS

### 消融实验 (Table 6, Bonn ATE)
- 无UBA: 5.13 cm（退化显著，证明UBA是关键）
- 无单目深度正则化: 3.30 cm
- 无不确定性解耦(Eq.10): 2.57 cm
- 无仿射映射: 2.47 cm
- 无权重衰减: 2.34 cm
- 完整模型: 2.30 cm

### YouTube野外定性 (Fig.4)
WildGS-SLAM在大多数YouTube序列上完全失败（3DGS建图无法在高动态场景稳定）；DROID-SLAM出现明显尺度漂移和不准确几何；DROID-W产生几何准确、时序一致的点云。

## 局限性

- **依赖帧间对齐**：不确定性优化需要帧间有足够的共视区域——大旋转、快速运动、遮挡严重时特征对应质量下降
- **非3DGS表示**：输出为点云而非可微高斯表示，无法进行新视角合成和照片级渲染——牺牲了3DGS的渲染能力换取鲁棒性
- **ConvGRU更新模块冻结**：使用预训练DROID-SLAM的特征提取器和ConvGRU，未针对动态场景微调——动态物体的特征可能仍干扰对应预测
- **仿射映射的简单性**：不确定性通过小MLP的仿射映射参数化，可能无法捕捉高度非线性的不确定性分布
- **~10 FPS**：虽称为实时但未达到DROID-SLAM的~20 FPS——不确定性优化的额外开销

## 关联

- [[concepts/slam]] — SLAM问题定义
- [[concepts/bundle-adjustment]] — Bundle Adjustment基础（Schur补、Gauss-Newton）
- [[concepts/uncertainty-aware-bundle-adjustment]] — 本文核心贡献：多视图特征不一致性驱动的可微UBA
- [[concepts/dinov2]] — DINOv2特征用于跨视图不一致性测量
- [[concepts/monocular-depth-estimation]] — Metric3D提供单目深度先验
- [[concepts/uncertainty-aware-tracking]] — 对比：VarSplat的方差学习不确定性跟踪
- [[concepts/uncertainty-aware-mapping]] — 对比：WildGS-SLAM的建图侧不确定性
- [[papers/2026-05-21/wildgs-slam]] — 同为不确定性方法，建图vs特征对比
- [[papers/2026-06-11/add-slam]] — 同为prior-free动态SLAM，不同技术路线
- [[papers/2026-06-13/dy3dgs-slam]] — 同为单目动态SLAM
- [[papers/2026-06-13/ggd-slam]] — 同为单目动态SLAM
- [[synthesis/dynamic-slam-comparison]] — 动态SLAM方法综合对比
- [[synthesis/robustness-dimensions]] — 鲁棒性维度分解框架
