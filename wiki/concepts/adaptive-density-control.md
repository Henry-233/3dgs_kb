---
title: "自适应密度控制"
tags: [concept, optimization]
---

## 定义
自适应密度控制（Adaptive Density Control, ADC）是3DGS训练过程中动态调整高斯数量与分布的优化策略。通过检测梯度过大或覆盖不足的区域来增加高斯（克隆或分裂），并移除冗余或过于透明的高斯，使场景表示在训练过程中自动适应几何复杂度。

## 直觉理解
类似于做雕塑——一开始用较少的大块黏土定出大致形状后，在细节丰富的地方（如面部五官）增加更多小块黏土来精细刻画，而在平坦区域（如后脑勺）则可以合并或减少不必要的黏土块。3DGS在训练中自动判断哪里需要"加细"、哪里可以"减粗"。

## 数学形式
两种主要操作：

**克隆（Clone）**：当梯度 $\nabla L > \tau_{grad}$ 且高斯尺寸较小时，在高梯度位置复制一个同样的高斯。

**分裂（Split）**：当梯度 $\nabla L > \tau_{grad}$ 且高斯尺寸较大时，将一个高斯替换为两个，位置沿采样方向偏移。

**剪枝（Prune）**：定期移除不透明度 $\alpha < \epsilon_\alpha$ 或尺寸过大的高斯。

周期性执行：每 $N$ 次迭代执行一次密度控制。

## 扩展：贡献度剪枝
Mobile-GS在标准ADC基础上提出贡献度剪枝（Contribution-based Pruning），采用投票式联合评估：

**候选识别**：$C_{prune}^{(t)} = \{g \mid o_g < Q_\tau(o)\} \cap \{g \mid s_{max}(g) < Q_\tau(s_{max})\}$

**投票累积**：高斯被持续标记为低贡献候选时累积票数，票数超过阈值（$I_{prune} \cdot v$）时永久剪除。参数：$\tau=0.2$，$I_{prune}=1000$，$v=0.6$，仅在前25k迭代执行。

仅用不透明度或仅用尺度的单一标准剪枝都会导致质量退化，联合二者达到最佳平衡（0.47M高斯，PSNR 27.12）。该策略可无缝集成到MaskGaussian和Mini-Splatting中。

## 关联
- 相关概念: [[concepts/3d-gaussian]], [[concepts/gaussian-compression]]
- 用到该概念的论文: [[papers/3d-gaussian-splatting]], [[papers/street-gaussians]], [[papers/mobile-gs]]
