---
title: "球谐函数"
tags: [concept, math, rendering]
---

## 定义
球谐函数（Spherical Harmonics, SH）是一组定义在球面上的正交基函数，在3DGS中用于编码每个高斯的视角依赖颜色（view-dependent color）。每个3D高斯携带一组SH系数，在渲染时根据观察方向计算对应颜色，从而捕捉镜面反射、高光等视角相关效果。

## 直觉理解
球谐函数可以理解为"球面上的傅里叶变换"。就像傅里叶级数可以用不同频率的正弦波叠加表示任意信号，球谐函数用不同频率的球面基函数叠加表示任意球面上的函数（如从不同方向看一个点呈现的颜色）。3DGS中使用低阶（通常4阶）SH就足以表达自然的视角相关效果。

## 数学形式
球谐函数基 $Y_l^m(\theta, \phi)$，其中 $l$ 是阶数（degree），$m$ 是次数（order）。

颜色计算公式：

$$c(\mathbf{d}) = \sum_{l=0}^{L} \sum_{m=-l}^{l} \mathbf{c}_{lm} Y_l^m(\mathbf{d})$$

其中 $\mathbf{d}$ 是观察方向，$\mathbf{c}_{lm}$ 是每个SH基的RGB系数，$L$ 是最大阶数（通常 $L=3$，即4阶，共16个基函数）。

## 压缩：SH蒸馏
Mobile-GS提出一阶球谐函数蒸馏（First-order SH Distillation），将高阶SH（3阶16系数/通道）蒸馏到一阶SH（仅4系数/通道），参数量从48个RGB系数降至12个（4倍压缩）。

**蒸馏损失**：$L_{distill} = \frac{1}{|P|} \sum \|C_p^{tea} - C_p\|^2$，直接用教师模型（Mini-Splatting）的渲染颜色监督学生。

**尺度不变深度蒸馏**：额外使用深度监督 $L_{depth}$（尺度不变形式），因为教师和学生的深度可能存在尺度偏差且教师深度并非始终可靠。

Mobile-GS还将蒸馏后的SH特征进一步分解为漫反射分量 $h_d$ 和视角依赖分量 $h_v$，用轻量MLP重建后参与渲染，避免直接存储完整的SH系数。实验表明一阶SH在质量（27.12 vs 27.15 for 三阶）和存储（4.6 MB vs 9.6 MB）间取得最佳平衡。

## 关联
- 相关概念: [[concepts/3d-gaussian]], [[concepts/gaussian-compression]]
- 用到该概念的论文: [[papers/3d-gaussian-splatting]], [[papers/street-gaussians]], [[papers/mobile-gs]], [[papers/gs-livo]]
