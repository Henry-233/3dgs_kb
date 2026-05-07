---
title: "TensoRF"
tags: [concept, rendering, comparison]
---

## 定义
TensoRF是一种将辐射场表示为张量分解（tensor decomposition）的方法。通过将3D空间分解为多个低秩张量因子的乘积（向量-矩阵分解，VM decomposition），TensoRF在保持高渲染质量的同时大幅降低了NeRF类方法的存储和计算开销。它是介于纯隐式方法（NeRF）和纯显式方法（3DGS）之间的混合方案。

## 直觉理解
把3D空间想象成一个巨大的3D数组，存储每个点的密度和颜色。直接存储这个数组太大，TensoRF将这个大数组分解为几个小数组（向量和矩阵）的乘积——类似于将一个大矩阵用SVD分解后只用前几个奇异值近似，大幅压缩存储。

## 数学形式
VM分解（Vector-Matrix decomposition）：

$$T = \sum_{r=1}^{R_1} \mathbf{v}_r^1 \circ \mathbf{M}_r^{23} + \sum_{r=1}^{R_2} \mathbf{v}_r^2 \circ \mathbf{M}_r^{13} + \sum_{r=1}^{R_3} \mathbf{v}_r^3 \circ \mathbf{M}_r^{12}$$

其中 $\circ$ 表示外积，$R_1, R_2, R_3$ 是秩参数。

对比：
| 方法 | 表示 | 存储 | 速度 |
|------|------|------|------|
| NeRF | MLP权重 | 小 | 慢 |
| TensoRF | 张量因子 | 中 | 中 |
| 3DGS | 显式高斯 | 大 | 快 |

## 关联
- 相关概念: [[concepts/nerf]], [[concepts/instant-ngp]]
- 上下文: TensoRF代表了从"全隐式"到"结构化显式"的过渡思路，3DGS继续推动了这一方向。
