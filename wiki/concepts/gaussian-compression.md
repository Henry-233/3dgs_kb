---
title: "高斯压缩"
tags: [concept, optimization, deployment]
---

## 定义
高斯压缩（Gaussian Compression）是针对3DGS模型体积大、计算量高的问题，通过一系列技术减少高斯数量、降低参数精度或蒸馏关键特征的策略集合。主要技术包括：神经向量量化（NVQ）、球谐函数蒸馏（SH Distillation）、贡献度剪枝（Contribution-based Pruning）和知识蒸馏。目标是使3DGS能在移动端、嵌入式设备等资源受限平台上实时运行。

## 直觉理解
3DGS模型就像一个用几百万块彩色积木搭成的精细雕塑——每块积木（高斯）都记录着位置、形状、颜色等信息。要把这个雕塑塞进口袋（手机内存），就需要"压缩"：减少积木数量（剪枝）、用更简化的颜色编码（SH蒸馏）、把相似积木归类共用一份数据（向量量化）。压缩过程需要在"雕塑还好看"和"够小够快"之间做权衡。

## 主要技术

### 神经向量量化（Neural Vector Quantization）

**子向量分解**：给定高斯属性向量 $z \in \mathbb{R}^{KL}$，通过K-Means划分为K个簇 $\{z_1, z_2, ..., z_K\}$（每个长度L），每个簇用独立码本 $C_k \in \mathbb{R}^{B \times L}$ 量化（B为码字数量）。

多码本设计的好处：减少单码本内存占用、缓解码字碰撞、简化推理时查找操作。

**后处理压缩**：训练结束后用Huffman编码对量化后的码字序列进行熵编码，进一步减少码流大小而不影响运行时性能。

**SH特征分解**：将SH特征Y分解为漫反射分量 $h_d \in \mathbb{R}^3$ 和视角依赖分量 $h_v \in \mathbb{R}^3$，用两个轻量MLP（单隐藏层64神经元，量化为16-bit）在推理时重建：
$$f_d = \text{MLP}_d(h_d, h_v), \quad f_v = \text{MLP}_v(h_d, h_v)$$

这避免直接存储高维SH系数，进一步降低存储。码本大小选择$2^{10}$在质量和存储间取得最佳平衡（4.6 MB, PSNR 27.12）。

### 球谐函数蒸馏（SH Distillation）

**一阶蒸馏**：将教师模型的三阶SH（3×16=48个RGB系数）蒸馏到学生模型的一阶SH（3×4=12系数），参数量减少4倍。

**蒸馏损失**：
$$L_{distill} = \frac{1}{|P|} \sum_{p \in P} \|C_p^{tea} - C_p\|^2$$

**尺度不变深度蒸馏损失**：
$$L_{depth} = \frac{1}{|P|} \sum \log(\hat{D}_p) - \log(\hat{D}_p^{tea}) - \frac{1}{|P|^2} \left(\sum \log(\hat{D}_p) - \log(\hat{D}_p^{tea})\right)^2$$

使用尺度不变损失而非L1/L2：教师和学生的深度可能存在尺度偏差，且教师深度并非始终可靠。

**蒸馏配置**：$\lambda_{distill}=1$，$\lambda_{depth}=0.1$，教师模型使用Mini-Splatting。

### 贡献度剪枝（Contribution-based Pruning）

联合不透明度和尺度的投票式剪枝策略。

**候选高斯识别**：
$$C_{opacity}^{(t)} = \{g \in G \mid o_g < Q_\tau(o)\}, \quad C_{scale}^{(t)} = \{g \in G \mid s_{max}(g) < Q_\tau(s_{max})\}$$

两个集合的交集为剪枝候选：$C_{prune}^{(t)} = C_{opacity}^{(t)} \cap C_{scale}^{(t)}$。

**投票累积与执行**：
$$V_g^{(t+1)} = V_g^{(t)} + \mathbf{1}[g \in C_{prune}^{(t)}]$$
$$G_{new} = G \setminus \{g \in G \mid \mathbf{1}[V_g^{(t)} > I_{prune} \cdot v]\}$$

**参数**：$\tau = 0.2$（分位数阈值），$I_{prune} = 1000$（剪枝间隔），$v = 0.6$（投票阈值）。仅在前25k迭代执行。

**消融验证**：仅用不透明度剪枝（PSNR 26.84）或仅用尺度剪枝（PSNR 26.87）均不如联合剪枝（PSNR 27.12）。剪枝策略可无缝集成到MaskGaussian和Mini-Splatting中。

## 压缩效果汇总（Mobile-GS, Mip-NeRF 360）

| 指标 | 3DGS原版 | Mobile-GS | 压缩比 |
|------|---------|-----------|--------|
| 存储 | 839.9 MB | 4.6 MB | **183×** |
| 高斯数量 | 约5.6M | 约0.47M | **12×** |
| SH系数/高斯 | 48 (3阶) | 12 (1阶) | **4×** |
| FPS (3090 Ti) | 174 | 1125 | **6.5×** |
| PSNR | 27.21 | 27.12 | -0.09 |

## 关联
- 相关概念: [[concepts/3d-gaussian]], [[concepts/spherical-harmonics]], [[concepts/adaptive-density-control]], [[concepts/order-independent-rendering]]
- 用到该概念的论文: [[papers/mobile-gs]]
