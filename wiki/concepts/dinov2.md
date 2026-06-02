---
title: "DINOv2"
tags: [concept, external-model, feature-extraction]
---

## 定义
DINOv2是Meta提出的自监督Vision Transformer（ViT），无需标注数据即可学习稠密视觉特征表示。其自监督训练使特征具有天然的跨视图对应能力。在3DGS中，DINOv2作为特征骨干被用于两个不同方向：[[papers/vggt|VGGT]]用它做图像patchify和全局几何推理，[[papers/wildgs-slam|WildGS-SLAM]]用其3D-aware微调版作为不确定性预测的特征提取器。

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
- 在3D高斯上附加低维特征向量，通过浅层MLP映射为DINO特征空间
- DINO特征场为不确定性估计提供语义上下文——帮助区分"真正的动态物体"和"视点变化导致的正常外观变化"
- 与WildGS-SLAM的区别：UP-SLAM用DINO特征丰富高斯场（特征场），WildGS-SLAM用DINOv2作为不确定性预测器的输入特征提取器
- 低维→高维的设计节省存储开销，避免在高斯上直接存储完整DINO特征

## 与CLIP的区别
| | CLIP | DINOv2 |
|---|---|---|
| 训练方式 | 图文对比学习 | 纯图像自监督学习 |
| 输出 | 图文对齐嵌入 | 视觉结构特征 |
| 在3DGS中的用途 | 语义理解与查询 | 几何感知特征提取 |
| 跨视图一致性 | 中等 | 强（尤其3D-aware版） |

## 关联
- 用到DINOv2的论文: [[papers/vggt]], [[papers/wildgs-slam]], [[papers/up-slam]]
- 相关概念: [[concepts/clip]], [[concepts/feed-forward-3d-reconstruction]], [[concepts/uncertainty-aware-mapping]]
