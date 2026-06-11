---
title: "可微渲染"
tags: [concept, rendering, optimization]
---

## 定义
可微渲染（Differentiable Rendering）是使渲染过程的每一个计算步骤都可求导的技术，使得渲染输出（像素颜色、深度）对场景参数（3D高斯属性、相机位姿）的梯度可以被反向传播。这是3DGS能用梯度下降优化的根本原因——没有可微渲染就没有3DGS。

## 直觉理解
可微渲染相当于给渲染管线装上了"反向齿轮"——正向时输入场景参数得到图像，反向时告诉系统"这个像素应该更亮，那个高斯应该往左移一点"，所有调整都通过链式法则自动传播。传统图形学渲染管线的光栅化和深度测试都是不可微的"硬判决"，3DGS通过重新设计渲染器绕过了这些不可微操作。

## 数学形式

### 原始3DGS的颜色可微渲染
3DGS的tile-based光栅化实现颜色 $\hat{C}$ 对每个高斯属性（均值 $\mu$、协方差 $\Sigma$、不透明度 $\alpha$、SH系数 $c$）的梯度：
$$\frac{\partial \hat{C}}{\partial \mu}, \frac{\partial \hat{C}}{\partial \Sigma}, \frac{\partial \hat{C}}{\partial \alpha}, \frac{\partial \hat{C}}{\partial c}$$

原始CUDA实现**仅包含颜色梯度**——缺少深度和位姿的Jacobian。

### G²-Mapping扩展的深度可微渲染
G²-Mapping在Taichi中重新实现完整渲染器，补全了深度梯度链：

**深度对不透明度的导数**（关键——一个高斯的α变化会影响它后面所有高斯）：
$$\frac{\partial D}{\partial a_i} = d_i w_i - \frac{\sum_{j=i+1}^n d_j a_j w_i}{1-a_i}$$

**深度对自身深度的导数**：
$$\frac{\partial D}{\partial d_i} = a_i w_i$$

**位姿Jacobian**（用于SLAM的相机位姿优化）：
$$\frac{\partial \mathbf{P}_c}{\partial \mathbf{q}_{cw}} = 2[J_{\text{imag}} | J_{\text{real}}] \in \mathbb{R}^{3\times4}, \quad \frac{\partial \mathbf{P}_c}{\partial \mathbf{t}_{cw}} = \mathbf{I}_3$$

### GS-LIVO的视觉Jacobian
将高斯渲染的光度误差Jacobian通过可微渲染传播到相机位姿，嵌入IESKF实现紧耦合融合。

## 工程实践
- **∂D/∂α 抑制**：深度损失会持续降低被观测高斯的α。G²-Mapping对 ∂D/∂α 乘以 1e-4 防止误删
- **位姿参数化**：用四元数 + 平移向量（而非SE(3)矩阵）使位姿各分量可独立求导

## 关联
- 相关概念: [[concepts/projection-transform]], [[concepts/alpha-compositing]], [[concepts/tile-based-rasterization]], [[concepts/3d-gaussian]]
- 用到可微渲染的论文: [[papers/2026-05/3d-gaussian-splatting]], [[papers/2026-05/g2-mapping]], [[papers/2026-05/gs-livo]]
