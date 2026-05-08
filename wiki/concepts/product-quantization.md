---
title: "乘积量化"
tags: [concept, compression]
---

## 定义
乘积量化（Product Quantization, PQ）是一种高维向量压缩技术，将 $D$ 维向量空间分解为 $m$ 个低维子空间的笛卡尔积，每个子空间独立用 $k$ 个聚类中心（codebook）进行向量量化。原始向量被编码为 $m$ 个codebook索引，总比特数为 $m \log_2 k$，实现从 $D \times 32$ bits 到 $m \log_2 k$ bits 的显著压缩。在3DGS中，Dr. Splat使用PQ在大规模通用图像数据上预训练codebook，用于压缩CLIP语言特征，无需逐场景优化。

## 直觉理解
想象你有512本不同颜色的彩色铅笔（512维CLIP特征），想把颜色信息压缩存储。乘积量化相当于把512支铅笔分成8组（每组64支），每组内选出最常见的256种颜色做成色卡（codebook）。以后存储颜色时不需要记录精确的RGB值，只需记录"第1组用第35号色"、"第2组用第128号色"...共8个编号。解压时按编号查色卡拼回近似颜色。因为是在大规模图像上预训练的色卡，适用于任何场景。

## 数学形式

### 向量分解
将向量 $v \in \mathbb{R}^{D}$ 分解为 $m$ 个子向量：
$$v = [v_1; v_2; ...; v_m], \quad v_j \in \mathbb{R}^{D/m}$$

### 子空间量化
每个子空间 $j$ 维护一个codebook $\mathcal{C}_j = \{c_{j,1}, c_{j,2}, ..., c_{j,k}\} \subset \mathbb{R}^{D/m}$

量化过程（最近邻搜索）：
$$idx_j = \arg\min_{n \in \{1,...,k\}} \|v_j - c_{j,n}\|_2$$

编码结果：$[idx_1, idx_2, ..., idx_m]$，存储开销 $m \lceil \log_2 k \rceil$ bits

### 解码
$$\hat{v} = [c_{1, idx_1}; c_{2, idx_2}; ...; c_{m, idx_m}]$$

### 压缩比
$$\frac{D \times 32}{m \lceil \log_2 k \rceil}$$

典型配置（Dr. Splat）：$D=512, m=8, k=256$ → 压缩比 $512 \times 32 / (8 \times 8) = 256\times$

## PQ vs 场景级自编码器

| | Product Quantization | Scene-Specific Autoencoder |
|---|---|---|
| 训练 | 大规模通用数据，离线预训练 | 每个场景单独训练MLP |
| 跨场景泛化 | 天然支持 | 不共享 |
| 重建质量 | 取决于codebook对目标域的覆盖 | 场景内压缩效率更高 |
| 解码速度 | O(m)查表，极快 | 一次MLP前向 |
| 适用场景 | 需跨场景部署 | 单场景精度优先 |

## 关联
- 相关概念: [[concepts/3d-language-field]], [[concepts/gaussian-compression]]
- 用到该概念的论文: [[papers/dr-splat]]
