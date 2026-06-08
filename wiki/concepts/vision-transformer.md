---
title: "视觉Transformer（Vision Transformer）"
tags: [concept, transformer, depth, slam, deep-learning]
---

## 定义
视觉Transformer（ViT）将NLP中的自注意力机制应用于图像——将图像切分为固定大小的patch，通过Transformer编码器建模全局上下文依赖。在3DGS-SLAM中，ViT被用于单目深度估计：其全局感受野比CNN更能处理无纹理区域和遮挡，多尺度变体（MViT）进一步捕获分层几何特征。

## 直觉理解
CNN看图像像透过一个小窗口——一层层看，远处的信息要好几次卷积才能关联起来。ViT看图像像从空中俯瞰——所有patch一次性看全，任意两个patch直接对话（自注意力），全局关系一目了然。这对于判断距离特别重要：知道"桌子上的杯子"需要同时理解桌子、杯子、它们之间的距离关系——这正是ViT擅长的全局上下文。

## 核心组件

### Patch Embedding
图像 $I \in \mathbb{R}^{H \times W \times 3}$ → 切分为 $N$ 个 $P \times P$ 的patch → 线性投影为 $\mathbf{E} \cdot \mathbf{x}_i$ → 加位置编码 $\mathbf{P}$。

ViMGS-SLAM中使用卷积实现（kernel=16, stride=16），共享权重编码器处理所有patch。

### Multi-head Self-Attention (MHSA)
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

每个patch查询所有其他patch，$\sqrt{d_k}$ 缩放防止梯度消失。

### 层级结构 vs 柱状结构
- **柱状ViT**（标准）：所有层同分辨率——计算量大，不产生多尺度特征
- **层级ViT**（Swin, MViT）：逐步下采样——产生CNN式的多尺度特征金字塔，更适合密集预测任务（深度估计、分割）

## 在3DGS-SLAM中的应用

### ViMGS-SLAM 的 MViT 架构
ViMGS-SLAM首次将MViT紧耦合进3DGS-SLAM管线：

1. **三级输入金字塔**：640×640 → 320×320 → 160×160
2. **共享权重Patch编码**：每级用kernel=16切patch→共享ViT编码器→24×24特征/patch
3. **五级特征金字塔**：滑动窗口合并→320×320到20×20共五级
4. **双分支编码器**：局部分支（细粒度细节）+ 全局分支（长程语义依赖）
5. **DPT解码器**：渐进上采样 + 跨尺度对齐 → 度量尺度逆深度图

**关键差异**：MViT直接预测**度量尺度**深度（训练混合度量+非度量数据集）——相比UniDepthV2等仅预测相对深度的方法，省去了与SLAM稀疏特征点的尺度对齐步骤。

### 为什么ViT适合深度估计

| 挑战 | CNN的局限 | ViT的优势 |
|------|---------|---------|
| 无纹理区域 | 局部感受野无梯度信号 | 全局上下文推断——从远处纹理区借用信息 |
| 遮挡 | 局部滤波器无法推断被遮挡区域 | 自注意力跨物体关联——"看到部分就知道整体" |
| 物体边界 | 卷积混合边界两侧特征→模糊 | 自注意力可学习边界两侧特征分离→锐利边界 |
| 尺度模糊 | 单一尺度特征 | 多尺度金字塔——大尺度看全局布局，小尺度看纹理细节 |

## 多尺度变体对比

| 架构 | 多尺度策略 | 代表应用 |
|------|---------|---------|
| **MViT** (ViMGS-SLAM) | 三尺度输入金字塔 + 五级特征金字塔 + 共享权重编码器 | 单目度量深度估计 |
| Swin Transformer | 移位窗口自注意力 + patch合并逐步下采样 | 通用骨干网络 |
| DPT (Dense Prediction Transformer) | ViT编码器 + 多尺度融合解码器 | 密集预测（深度/分割） |
| DINOv2 | 大规模自监督预训练ViT | 视觉特征提取（[[papers/wildgs-slam]], [[papers/up-slam]]） |

## 关联
- 用到ViT的论文: [[papers/vimgs-slam]]（MViT深度先验）, [[papers/wildgs-slam]]（DINOv2特征提取）, [[papers/up-slam]]（DINOv2特征+不确定性）
- 相关概念: [[concepts/monocular-depth-estimation]], [[concepts/slam]], [[concepts/dinov2]]
- 替代方案: [[concepts/monocular-depth-estimation|单目深度估计]]（CNN方案: UniDepthV2, Metric3D v2）
