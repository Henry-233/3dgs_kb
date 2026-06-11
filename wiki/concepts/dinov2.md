---
title: "DINOv2"
tags: [concept, external-model, feature-extraction]
---

## 定义
DINOv2是Meta提出的自监督Vision Transformer（ViT），无需标注数据即可学习稠密视觉特征表示。其自监督训练使特征具有天然的跨视图对应能力。在3DGS中，DINOv2作为特征骨干被用于两个不同方向：[[papers/2026-05/vggt|VGGT]]用它做图像patchify和全局几何推理，[[papers/2026-05/wildgs-slam|WildGS-SLAM]]用其3D-aware微调版作为不确定性预测的特征提取器。

## 直觉理解
DINOv2就像一个"看图高手"——不需要任何文字标签，仅靠看过几亿张图片，就能学会识别物体、理解场景结构。更妙的是，它看到的特征在不同角度拍同一物体时是相似且可对应的，这对3D任务极其有用。

## 在3DGS中的作用

### VGGT (CVPR 2025 Best Paper)
- 用预训练DINOv2将图像切分为token序列（替代标准ViT的14×14卷积patchify）
- DINOv2特征比从头训练的patchify更稳定，对超参数不敏感
- 经过Alternating-Attention Transformer处理后输出相机、深度、点图、轨迹

### WildGS-SLAM
- 使用3D-aware微调版DINOv2（Yue et al. ECCV 2024）提取图像特征
- 3D-aware微调注入了多视图几何意识，特征对跨视图一致性更敏感
- 浅层MLP将DINOv2特征解码为逐像素不确定性图
- 消融证明3D-aware版优于原版DINOv2（Wild-SLAM上新视角PSNR +0.02）

### UP-SLAM (ICRA 2026)

UP-SLAM在3DGS中构建**DINO特征场**，用于增强不确定性预测的语义鲁棒性：

**低维→高维特征蒸馏**：
1. 锚点特征 $\hat{f}_v$ 通过MLP $F_d$ 解码出低维高斯视觉属性 $\{f\} \in \mathbb{R}^{k \times N_l}$（$N_l = 16$，远小于DINO特征维度 $N_h$）
2. 低维特征经3DGS alpha-blending渲染：$\tilde{F} = \sum_{i=1}^N f_i \alpha_i \prod_{j=1}^{i-1} (1-\alpha_j)$
3. 浅层MLP $F_m$（Conv→ReLU→Conv，隐藏层128维）将低维渲染特征映射到高维DINO特征空间：$\hat{F} = F_m(\tilde{F}) \in \mathbb{R}^{N_h}$
4. 与DINOv2提取的GT特征做余弦相似度监督：$\mathcal{L}_d = \frac{1}{N_d} \sum (1 - \frac{F_i \cdot \hat{F}_i}{\|F_i\|_2 \|\hat{F}_i\|_2})$

**为什么用低维→高维设计**：
- 直接在高斯上存储完整DINO特征（$N_h$维）会显著扩展优化空间，导致显存爆炸和计算效率降低
- $N_l=16 \ll N_h$，节省存储同时保留优化效率
- 渲染低维特征后通过MLP映射到高维，在特征质量和计算开销之间取得平衡

**DINO特征场的作用**：
- 为不确定性估计提供语义上下文——帮助区分"真正的动态物体"和"视点变化导致的正常外观变化"
- DINO特征天然对跨帧外观变化鲁棒，非常适合动态场景
- 消融证明DINO相似度近80%，证明下游应用（目标级导航、语义理解）潜力

与WildGS-SLAM的区别：UP-SLAM用DINO特征**丰富高斯场**（特征场→输入不确定性MLP），WildGS-SLAM用DINOv2作为不确定性预测器的**图像特征提取器**。与LangSplat的区别：LangSplat构建CLIP语言场用于开放词汇查询，UP-SLAM构建DINO特征场用于提升不确定性预测鲁棒性——用途不同但技术路线相似。

## 与CLIP的区别
| | CLIP | DINOv2 |
|---|---|---|
| 训练方式 | 图文对比学习 | 纯图像自监督学习 |
| 输出 | 图文对齐嵌入 | 视觉结构特征 |
| 在3DGS中的用途 | 语义理解与查询 | 几何感知特征提取 |
| 跨视图一致性 | 中等 | 强（尤其3D-aware版） |

## 关联
- 用到DINOv2的论文: [[papers/2026-05/vggt]], [[papers/2026-05/wildgs-slam]], [[papers/2026-06/up-slam]]
- 相关概念: [[concepts/clip]], [[concepts/feed-forward-3d-reconstruction]], [[concepts/uncertainty-aware-mapping]]
