---
title: "不确定性感知建图"
tags: [concept, rendering, slam, optimization]
---

## 定义
不确定性感知建图（Uncertainty-Aware Mapping）是一种在3D重建/SLAM中处理噪声、动态物体和观测歧义的技术。核心思想是：为每个像素或区域预测一个"可信度分数"（不确定性），在优化过程中用该分数加权渲染损失——不可信的区域（如动态物体、镜面反射、欠观测区域）自动降低其对建图的贡献，使优化集中在可信的静态场景部分。

## 直觉理解
想象你在一个繁忙的广场上画画——不断有人从你面前走过。一个 naive 的画家会把所有看到的东西都画进去，结果画里全是"鬼影"。而不确定性感知的画家会先快速判断"这个区域是不是一直在变？"——如果某个区域今天有人、明天没人，它就标记为"不可信"，画的时候自动忽略这些区域，只画稳定的背景建筑。

## 数学形式

### 不确定性加权渲染损失
给定逐像素不确定性图 $\beta$，渲染损失被不确定性加权：

$$\mathcal{L}_{\text{render}} = \frac{\mathcal{L}_{\text{color}} + \lambda \mathcal{L}_{\text{depth}}}{\beta^2}$$

- 高不确定性 $\beta \uparrow$ → 损失权重 $\downarrow$ → 该像素对建图影响减小
- 低不确定性 $\beta \downarrow$ → 损失权重 $\uparrow$ → 该像素主导建图优化

### 不确定性预测（WildGS-SLAM风格）
使用预训练视觉基础模型（DINOv2）提取特征 + 在线训练的浅层MLP预测不确定性：

$$\beta = \mathcal{P}(\mathcal{F}_{\text{DINOv2}}(I))$$

MLP的损失函数包含：
- **渲染一致性项**：渲染结果与观测的差异（SSIM变体）
- **深度监督项**：$\mathcal{L}_{\text{depth}} = |\hat{D} - \tilde{D}|_1$，帮助MLP区分静态几何与动态干扰物
- **正则化项**：防止不确定性无限增长 $\mathcal{L}_{\text{reg\_U}} = \log \beta$；鼓励相似特征具有一致的不确定性 $\mathcal{L}_{\text{reg\_V}}$

### 关键设计原则
1. **独立优化**：不确定性预测器和场景表示的优化应**解耦**——梯度互不传播，避免两者互相干扰
2. **在线适应**：预测器随数据流式增量训练，动态适应场景特性
3. **无需显式标签**：通过渲染一致性自监督训练，不需要动态物体的标注

## 在SLAM中的应用
不确定性感知不仅用于建图，还用于**跟踪**——在Dense Bundle Adjustment (DBA) 中以 $\Sigma_{ij}/\beta_i^2$ 加权残差，使动态物体上的特征匹配误差不影响位姿估计。

## 与其他方法的对比
| 方法 | 动态处理策略 | 需要先验？ |
|------|------------|----------|
| 语义分割法（DG-SLAM, DynaSLAM） | Mask R-CNN / YOLO 分割动态物体 | 需要预定义物体类别 |
| 几何残差法（ReFusion） | 深度残差阈值滤除动态区域 | 需要RGB-D深度传感器 |
| 光流法（RoDyn-SLAM） | 光流+刚性运动检测 | 纹理需求 |
| **不确定性感知（WildGS-SLAM）** | **DINOv2+MLP预测不确定性加权** | **仅需单目RGB，无类别先验** |

## 关联
- 相关概念: [[concepts/slam]], [[concepts/3d-gaussian]], [[concepts/alpha-compositing]]
- 用到该概念的论文: [[papers/wildgs-slam]]
- 相关工作: NeRF On-the-go, WildGaussians
