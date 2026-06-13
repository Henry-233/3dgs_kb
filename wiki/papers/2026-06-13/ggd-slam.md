---
title: "GGD-SLAM: Monocular 3DGS SLAM Powered by Generalizable Motion Model for Dynamic Environments"
authors: "Yi Liu, Haoxuan Xu, Hongbo Duan, Keyu Fan, Zhengyang Zhang, Peiyu Zhuang, Pengting Luo, Houde Liu"
year: 2026
venue: arXiv
status: skimmed
---

## 一句话总结

基于**可泛化运动模型**的单目动态场景3DGS-SLAM，无需预定义语义标注或深度输入，通过FIFO队列+时序注意力机制分离动静态特征，并引入**静态信息采样填充遮挡区域**和**干扰自适应SSIM损失**。

## 解决的问题

3DGS-SLAM依赖静态环境假设，动态场景中性能严重退化。GGD-SLAM提出无需语义先验和深度输入的**可泛化运动模型**，从RGB帧序列中学习动静态分离。

## 核心贡献 (from abstract)

- **FIFO帧管理 + 时序注意力机制**：用FIFO队列管理输入帧，通过时序注意力提取动态语义特征
- **动态特征增强器**：分离静态和动态成分，无需预定义语义标注或深度输入
- **静态信息采样填充遮挡**：移除动态物体后，通过采样静态信息填充被遮挡区域
- **干扰自适应SSIM损失**：针对动态环境定制的SSIM损失变体，显著增强系统鲁棒性
- SOTA动态场景位姿估计与稠密重建

## 关联

- [[concepts/3d-gaussian]] — 基础3DGS表示
- [[concepts/slam]] — SLAM问题定义
- [[concepts/generalizable-motion-model]] — 本文核心贡献：可泛化运动模型
- [[concepts/uncertainty-aware-mapping]] — 不确定性感知的建图优化
- [[concepts/ssim-loss]] — SSIM损失基础，本文提出干扰自适应变体
- [[concepts/dinov2]] — 与DINOv2特征提取方法形成对比
- [[concepts/temporal-gaussian-model]] — 另一种动态物体建模方式
- [[papers/2026-06-11/add-slam]] — 同为纯RGB动态SLAM
- [[papers/2026-06-13/dy3dgs-slam]] — 同期单目动态SLAM
- [[papers/2026-05-21/wildgs-slam]] — 不确定性感知动态SLAM
- [[synthesis/dynamic-slam-comparison]] — 动态SLAM方法综合对比

## 待精读标记: ⬜ 未精读
