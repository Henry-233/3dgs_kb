---
title: "局部图渲染 (Local Graph Rendering, LGR)"
tags: [concept, slam, tracking, rendering]
---

## 定义
局部图渲染（LGR）是一种增强前馈式位姿预测的跟踪技术：利用已有3D高斯地图渲染已知位姿的参考图像，与真实观测帧一起构建局部约束图，通过图上多帧光流+DBA联合求解目标帧的精确位姿。LGR解决了"仅用两帧预测位姿不可靠"的问题，用已知3D信息为未知位姿提供几何锚定。

## 直觉理解
你在一个陌生的十字路口要确定自己的位置。纯两帧方法相当于"只看上一秒自己在哪里，猜现在的位置"——光线变了或面对白墙就猜不准。LGR的做法是——先用粗略的"运动惯性"猜一下大致位置，然后在周围的几个角度，用已知的3D地图各渲染一张"如果我在这个位置应该看到什么"的参考照片。把你的真实照片和这些参考照片一一对比（光流匹配），综合所有对比结果用数学优化精确求解你现在的位姿。

## 数学形式

### 球面姿态采样

**惯性近似位姿**（假设相机二阶差分恒定）：
$$\hat{G}_t = [R_{t-1}] \cdot [2T_{t-1} - T_{t-2}]$$

**球面采样**（在惯性近似周围采样 $N$ 个候选位姿）：
$$G_t^{(k)} = [R_{t-1}] \cdot [T_{t-1} + \eta \cdot \|T_{t-1}-T_{t-2}\| \cdot \hat{v}^i(\theta)]$$

其中 $\hat{v}^i(\theta)$ 是与惯性方向偏移角 $\theta$ 的单位球面向量，$\eta$ 控制采样半径（默认5.0），$\theta \leq 30^\circ$。

### 渲染局部图

从3D高斯 splat 出已知位姿的参考图像：
$$I_t^{(k)} = R_{\text{img}}(\mathcal{G}_t, G_t^{(k)}), \quad D_t^{(k)} = R_{\text{dep}}(\mathcal{G}_t, G_t^{(k)})$$

### 图约束位姿优化

构建局部图 $\mathcal{E}$，节点含 ${I_t, I_{t-1}, I_t^{(1)}, ..., I_t^{(N-1)}}$，边连接图内全部图像对。在全部边上运行DBA最小化重投影误差：
$$\Delta G_{ij} = \arg\min_{\delta G} \|\tilde{p}_{ij} - \Pi_c(\delta G \cdot \Pi_c^{-1}(p_i, d_i))\|^2$$

## 关键参数与消融

| 参数 | 默认值 | 消融结论 |
|------|--------|---------|
| 图节点数 $N$ | 6 | N=2→8，ATE持续改善但边际递减；N=6最优性价比 |
| 采样角 $\theta$ | 30° | 增大改善PSNR/SSIM（更多视角覆盖），ATE基本稳定 |
| 惯性系数 $\eta$ | 5.0 | η=1-2时ATE最优（7.27cm），η≥5过度依赖惯性引入漂移 |

## 与相关技术的区分

- [[concepts/feed-forward-pose-prediction|前馈式位姿预测]]：LGR是增强前馈预测鲁棒性的具体技术——纯2帧前馈不可靠时，LGR用渲染的已知位姿图像提供额外约束
- [[concepts/bundle-adjustment|BA/DBA]]：LGR用DBA作为优化求解器，但DBA作用在渲染帧+真实帧构成的局部图上（传统DBA作用在真实关键帧对上）
- 关键区别：LGR引入了"从3D表示渲染出的图像"作为图的节点——这些节点位姿精确已知（是采样出来的），为位姿估计提供绝对几何锚定

## 关联
- 用到LGR的论文: [[papers/2026-05-21/pseudo-depth-meets-gaussian]]
- 相关概念: [[concepts/feed-forward-pose-prediction]], [[concepts/slam]], [[concepts/bundle-adjustment]], [[concepts/3d-gaussian]]
