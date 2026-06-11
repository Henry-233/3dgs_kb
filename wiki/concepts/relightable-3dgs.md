---
title: "可重光照3D高斯散射"
tags: [concept, rendering, relighting, 3dgs-variant]
---

## 定义
可重光照3D高斯散射（Relightable 3DGS）是将传统3DGS扩展为支持基于物理的光照编辑的变体。其核心思想是将场景表示分解为光照无关的**材质属性**（反照率、法向量、粗糙度）与显式的**环境光照参数**，渲染时通过物理光照模型（如BRDF）重新组合——从而可以在不改变几何和材质的前提下，自由编辑光照条件并即时生成不同光照下的新视图。

## 直觉理解
传统3DGS就像一张"已经拍好的照片"——光照已经被固定在场景里了。你想看阴天下的场景？没办法，阳光已经"印"进每个高斯的颜色中了。可重光照3DGS则把场景拆成了两本"账"：一本记录"这个东西本身是什么颜色、有多粗糙、面朝哪个方向"（材质），另一本记录"此刻太阳在哪、有多亮、环境光是暖是冷"（光照）。渲染时把两本账按物理公式算在一起——于是换一本光照账就能得到完全不同天气下的同一场景。

## 数学形式

传统3DGS的颜色存储：
$$c(\mathbf{d}) = \sum_{l,m} \mathbf{c}_{lm} Y_l^m(\mathbf{d}) \quad\text{(SH编码，光照与材质耦合)}$$

Relightable 3DGS的颜色计算：
$$\hat{C}(\mathbf{p}) = \sum_{i} f_\text{BRDF}(\mathbf{a}_i, \mathbf{n}_i, r_i, \theta_L) \cdot \alpha_i \prod_{j < i} (1 - \alpha_j)$$

其中：
- $\mathbf{a}_i$：第i个高斯的反照率（Albedo），光照无关的漫反射颜色
- $\mathbf{n}_i$：第i个高斯的表面法向量（Normal）
- $r_i$：粗糙度（Roughness），控制高光扩散程度
- $\theta_L = (\theta_\text{sun}, I_\text{sun}, I_\text{ambient}, T_\text{color})$：环境光照参数
- $f_\text{BRDF}$：物理光照模型（如Cook-Torrance BRDF + 环境光），计算材质在给定光照下的最终颜色

### 物理光照模型（示意）
$$f_\text{BRDF}(\mathbf{a}, \mathbf{n}, r, \theta_L) = \underbrace{\mathbf{a} \cdot (\mathbf{n} \cdot \mathbf{l}) \cdot I_\text{sun}}_{\text{漫反射}} + \underbrace{f_\text{specular}(\mathbf{n}, \mathbf{v}, \mathbf{l}, r) \cdot I_\text{sun}}_{\text{镜面高光}} + \underbrace{\mathbf{a} \cdot I_\text{ambient}}_{\text{环境光}}$$

其中 $\mathbf{l}$ 是光源方向（由 $\theta_\text{sun}$ 决定），$\mathbf{v}$ 是观察方向。

## 光照增强训练

Relightable 3DGS的关键应用场景是为RL策略提供光照增强训练：

**训练循环**：
1. 从光照分布 $\mathcal{L}$ 采样 $\theta_L$（太阳方向、强度、色温、漫射比例）
2. 用Relightable 3DGS渲染当前场景在 $\theta_L$ 下的观测图像
3. RL策略基于RGB观测输出控制指令
4. 环境状态更新，重复步骤1-3

**有效性的原因**：光照条件从"强定向阳光"到"漫射阴天"的巨大变化迫使策略学习光照**不变**特征——它不能依赖"亮绿色的树叶"（阴天树叶呈暗绿色）或"阳光下的高光"（阴天没有高光），必须依赖几何结构和空间关系。

## 与球谐函数的关系

| | 球谐函数 (SH) | 可重光照分解 |
|------|---------|------------|
| 存储内容 | SH系数——间接编码了材质+光照的联合效果 | 材质属性（反照率、法向量、粗糙度） |
| 光照表示 | 隐式（无法直接编辑） | 显式（参数 $\theta_L$ 可直接修改） |
| 光照编辑 | 不支持——改变光照需重新训练 | 支持——修改参数即时渲染，无需重训 |
| 物理直觉 | 弱——SH是数学基函数，不是物理量 | 强——BRDF遵循能量守恒和物理定律 |
| 参数效率 | 高（4阶SH仅需16基/通道） | 较低（需要额外存储法向量和粗糙度） |

## 关联
- 基于: [[concepts/3d-gaussian]], [[concepts/spherical-harmonics]], [[concepts/differentiable-rendering]]
- 用到该概念的论文: [[papers/2026-06/zero-shot-uav-navigation]]
- 传统对比: 传统3DGS的SH方案（光照与材质耦合，无法编辑光照条件）
