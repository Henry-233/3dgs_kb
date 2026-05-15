---
title: "交替注意力（Alternating-Attention）"
tags: [concept, architecture, attention, transformer]
---

## 定义
交替注意力（Alternating-Attention, AA）是VGGT提出的一种Transformer注意力机制设计，在**帧内自注意力（Frame-wise Self-Attention）**和**全局自注意力（Global Self-Attention）**之间交替切换。帧内注意力让每张图像的token内部交互（学习单帧几何结构），全局注意力让所有图像的所有token跨帧交互（学习跨视图几何对应）。

## 直觉理解
想象你在拼一个3D拼图：
- **帧内注意力**就像你先仔细看每一张照片——理解每张照片里的物体轮廓、纹理、边界
- **全局注意力**就像你来回比较不同照片——"这个桌角在照片A的右下角，在照片B的左下角，所以相机是从不同角度拍的"

交替进行这两个步骤，模型逐步构建起对整个3D场景的全局理解。纯全局注意力的缺点是每张图内部的表征会被其他图"污染"；纯帧内注意力的缺点是无法建立跨视图关联。AA在两者之间取得平衡。

## 数学形式

设输入为N帧图像的token序列 $t^I = \bigcup_{i=1}^N \{t_i^I\}$，其中 $t_i^I \in \mathbb{R}^{K \times C}$ 为第i帧的K个token。

**帧内自注意力**（每帧独立）：
$$\forall i \in [1, N]: \quad t_i^I \leftarrow \text{SelfAttn}(Q=t_i^I, K=t_i^I, V=t_i^I)$$

**全局自注意力**（所有帧联合）：
$$t^I \leftarrow \text{SelfAttn}(Q=t^I, K=t^I, V=t^I)$$

两种注意力交替堆叠L次（VGGT中L=24），形成完整的AA Transformer。

## 与其他注意力设计的对比

| 设计 | 计算复杂度 | 跨帧信息 | 帧内归一化 | 效果 |
|------|-----------|---------|-----------|------|
| **AA（VGGT）** | $O(NK^2 + (NK)^2)$ | ✅ | ✅ | **最优** |
| 纯全局自注意力 | $O((NK)^2)$ | ✅ | ❌ | 次优 |
| 交叉注意力 | $O(N \cdot (NK)^2)$ | ✅ | ✅ | 最差+最高计算 |

## 关键设计要点

1. **不使用交叉注意力**：VGGT完全只用自注意力，交叉注意力在初步实验中始终劣于自注意力
2. **QK归一化（QKNorm）**：每个注意力层使用QK归一化稳定训练
3. **LayerScale**：每层使用LayerScale（初始值0.01），缓解深层Transformer的梯度问题
4. **寄存器Token**：每帧附加4个可学习寄存器token，提供额外的信息存储空间

## 关联
- 提出论文: [[papers/vggt]]
- 受启发于: ViT的全局自注意力设计、视频Transformer中的时空分离注意力（如TimeSformer）
- 相关概念: [[concepts/feed-forward-3d-reconstruction]]
