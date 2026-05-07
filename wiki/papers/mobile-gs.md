---
title: "Mobile-GS: Real-time Gaussian Splatting for Mobile Devices"
authors: Xiaobiao Du, Yida Wang, Kun Zhan, Xin Yu
year: 2026
venue: ICLR
tags: [paper, extension, application, compression]
status: done
---

## 一句话总结
提出Mobile-GS——首个面向移动设备的实时3DGS方法，通过深度感知顺序无关渲染消除排序瓶颈、神经视角依赖增强修复伪影、一阶SH蒸馏+神经向量量化+贡献度剪枝将模型压缩至4.6 MB，在骁龙8 Gen 3移动GPU上实现127 FPS实时渲染。

## 解决的问题
3DGS虽然渲染质量高，但三个瓶颈使其无法部署到移动设备：

1. **Alpha合成依赖深度排序**：排序操作占渲染时间的40-70%（Fig. 2），是最大计算瓶颈。移除排序后3DGS速度可提升数倍，但会破坏标准alpha合成的正确性。
2. **模型体积过大**：原版3DGS模型通常800-1300 MB，远超移动端内存预算。
3. **高斯数量过多**：数百万高斯带来的计算量超出移动GPU能力。

## 核心方法

### 1. 深度感知顺序无关渲染（Depth-aware Order-Independent Rendering）

传统Alpha合成需要对高斯按深度排序（near-to-far），排序本身消耗高达一半的渲染时间。Mobile-GS提出用深度加权混合方案替代排序依赖：

**渲染公式**：

$$C = (1 - T) \frac{\sum_{i=1}^{N} c_i \alpha_i w_i}{\sum_{i=1}^{N} \alpha_i w_i} + T c_{bg}$$

其中 $T = \prod_{j=1}^{N}(1 - \alpha_j)$ 是全局透射率，用于区分前景和背景。

**深度感知权重**：

$$w_i = \frac{\beta_i^2}{\sigma_i + \beta_i \cdot d_i^2 + \exp(\frac{s_{max}}{d_i})}$$

- $d_i$：高斯在相机坐标系中的深度
- $s_{max}$：高斯的最大尺度
- $\beta_i$：视角依赖的逐高斯参数（由后续MLP预测）
- $\sigma_i$：可学习参数

权重函数的设计意图：距离近的高斯权重高，尺度大的高斯权重高（覆盖面积大），两者共同决定对像素的贡献。公式中所有项都是可交换求和，因此无需排序，GPU可完全并行执行。

### 2. 神经视角依赖增强（Neural View-dependent Enhancement）

顺序无关渲染虽然快，但由于失去了精确的遮挡顺序，在重叠几何区域会产生透明度伪影。Mobile-GS用一个轻量MLP预测视角依赖的不透明度和权重因子来补偿。

**MLP输入**：相机-高斯方向向量 $P_i = \frac{\mu_i - t_v}{\|\mu_i - t_v\|}$、3D高斯尺度 $s_i \in \mathbb{R}^3$、旋转 $r_i \in SO(3)$、球谐系数 $Y_i$

**MLP输出**：

$$F = \text{MLP}_f(P_i, s_i, r_i, Y_i)$$
$$\beta_i = \text{ReLU}(\text{MLP}_\beta(F))$$
$$o_i = \sigma(\text{MLP}_o(F))$$

MLP结构：三层，神经元数 256 → 128 → 64，共训练30k迭代。$\beta_i$（视角依赖权重）作为深度衰减因子调节远处高斯的贡献，$o_i$（视角依赖不透明度）动态抑制遮挡区域的透明度。

### 3. 一阶球谐函数蒸馏（First-order SH Distillation）

原版3DGS使用三阶SH（3×16=48个RGB系数），存储开销大。Mobile-GS蒸馏到一阶SH（3×4=12系数），参数量减少4倍。

**蒸馏损失**：$L_{distill} = \frac{1}{|P|} \sum_{p \in P} \|C_p^{tea} - C_p\|^2$

**尺度不变深度蒸馏损失**：

$$L_{depth}(D, D^{tea}) = \frac{1}{|P|} \sum \log(\hat{D}_p) - \log(\hat{D}_p^{tea}) - \frac{1}{|P|^2} \left(\sum \log(\hat{D}_p) - \log(\hat{D}_p^{tea})\right)^2$$

使用尺度不变损失而非L1/L2，因为教师和学生的深度可能存在尺度差异。教师模型使用Mini-Splatting。

### 4. 神经向量量化（Neural Vector Quantization）

将高斯属性向量 $z \in \mathbb{R}^{KL}$ 通过K-Means划分为K个簇，每个簇用独立码本 $C_k \in \mathbb{R}^{B \times L}$ 量化（B=码字数量）。多码本设计减少码字碰撞、简化推理查找。

量化后用Huffman编码进一步压缩码流。

**SH特征分解**：将量化后的SH特征 $Y$ 分解为漫反射分量 $h_d \in \mathbb{R}^3$ 和视角依赖分量 $h_v \in \mathbb{R}^3$，用两个轻量MLP重建：

$$f_d = \text{MLP}_d(h_d, h_v), \quad f_v = \text{MLP}_v(h_d, h_v)$$

两者量化为16-bit精度以进一步减少存储。最优码本大小：$2^{10}$（Table 7分析）。

### 5. 贡献度剪枝（Contribution-based Pruning）

联合考虑不透明度和尺度的投票式剪枝：

**候选识别**（每迭代t）：
$$C_{opacity}^{(t)} = \{g \in G \mid o_g < Q_\tau(o)\}, \quad C_{scale}^{(t)} = \{g \in G \mid s_{max}(g) < Q_\tau(s_{max})\}$$

$$C_{prune}^{(t)} = C_{opacity}^{(t)} \cap C_{scale}^{(t)}$$

**投票累积**：
$$V_g^{(t+1)} = V_g^{(t)} + \mathbf{1}[g \in C_{prune}^{(t)}]$$

当累积票数超过阈值时永久剪除：
$$G_{new} = G \setminus \{g \in G \mid \mathbf{1}[V_g^{(t)} > I_{prune} \cdot v]\}$$

参数设置：$\tau = 0.2$（分位数阈值），$I_{prune} = 1000$（剪枝间隔），$v = 0.6$（投票阈值）。仅在前25k迭代执行剪枝，后期保留细节。仅用不透明度或仅用尺度剪枝都会导致质量退化（Table 4）。

### 总损失函数

$$L = L_{rgb} + \lambda_{distill} L_{distill} + \lambda_{depth} L_{depth}$$

其中 $L_{rgb} = \lambda L_1 + (1-\lambda) L_{D-SSIM}$（$\lambda = 0.8$），$\lambda_{distill} = 1$，$\lambda_{depth} = 0.1$。

## 与前作的区别

| 前作 | 区别 |
|------|------|
| 3DGS | Mobile-GS消除排序瓶颈+模型压缩至4.6MB，可移动端实时渲染 |
| LightGaussian | LightGaussian仅做后处理压缩（二阶SH），Mobile-GS增加顺序无关渲染+神经增强+一阶SH |
| SortFreeGS | SortFreeGS消除排序但未压缩（851MB），Mobile-GS同时实现加速和压缩 |
| Speedy-Splat | Speedy-Splat聚焦稀疏像素，Mobile-GS聚焦移动端全栈优化 |
| Mini-Splatting | 使用Mini-Splatting作为教师模型，但Mobile-GS替换了渲染管线核心 |

### 与其他排序无关方法对比（Table 8）

| 方法 | 渲染公式类型 | 移动端FPS | 存储 |
|------|------------|----------|------|
| SortFreeGS* (quantized) | 加权和 $w(d_i) = \exp(-\kappa_i d_i)$ | 18 | 64.3 MB |
| GES | Surfel混合 | 24 | 29.4 MB |
| **Mobile-GS** | 深度感知OIR + MLP增强 | **127** | **4.6 MB** |

## 实验结论

### 桌面GPU（RTX 3090 Ti）定量结果（Table 1）

| 数据集 | PSNR | SSIM | LPIPS | 存储 | FPS |
|--------|------|------|-------|------|-----|
| Mip-NeRF 360 | 27.12 | 0.807 | 0.235 | 4.6 MB | 1125 |
| Tanks&Temples | 23.09 | 0.831 | 0.208 | 2.5 MB | 1179 |
| Deep Blending | 29.93 | 0.906 | 0.243 | 4.6 MB | 1132 |

对比3DGS原版（Mip-NeRF360: 27.21/0.815/0.214/840MB/174FPS），PSNR仅降0.09，存储减少183倍，FPS提升6.5倍。

### 移动端结果（骁龙8 Gen 3, Table 2）

| 方法 | PSNR | 移动端FPS | 存储 | 训练时间 |
|------|------|----------|------|---------|
| 3DGS* | 27.01 | 8 | 61.8 MB | 0.5 h |
| Mini-Splatting* | 27.02 | 12 | 36.9 MB | 0.4 h |
| SortFreeGS* | 26.74 | 24 | 64.3 MB | 1.3 h |
| Speedy-Splat | 26.92 | 19 | 79.5 MB | 0.4 h |
| HAC | 26.98 | 12 | 11.8 MB | 0.7 h |
| LocoGS-S | 27.02 | 17 | 8.5 MB | 0.8 h |
| C3DGS | 27.03 | 14 | 30.6 MB | 0.6 h |
| GES | 26.98 | 18 | 29.4 MB | 0.7 h |
| **Mobile-GS** | **27.12** | **127** | **4.6 MB** | 1.5 h |

**移动端127 FPS**是唯一真正实现移动设备实时渲染的方法（Bicycle场景116 FPS @ 1600×1063分辨率）。

### 消融实验（Table 3, Mip-NeRF 360）

去除各组件的影响：

| 配置 | PSNR | FPS | 存储 |
|------|------|-----|------|
| **完整Mobile-GS** | **27.12** | **1125** | **4.6 MB** |
| w/o 顺序无关渲染（回退标准alpha合成） | 27.26 (+0.14) | 684 (-441) | 4.5 MB |
| w/o 视角依赖增强 | 26.68 (-0.44) | 1227 | 4.4 MB |
| w/o 神经向量量化 | 27.33 | 841 | 121 MB (+26×) |
| w/ 0阶SH蒸馏 | 27.04 | 1219 | 3.6 MB |
| w/ 2阶SH蒸馏 | 27.13 | 917 | 7.3 MB |
| w/ 3阶SH（无蒸馏） | 27.15 | 841 | 9.6 MB |
| w/o 深度项（Eq.3中去掉 $d_i$） | 27.03 | 1167 | 4.5 MB |
| w/o 尺度项（Eq.3中去掉 $s_{max}$） | 27.08 | 1171 | 4.5 MB |

关键观察：顺序无关渲染贡献了最大加速（684→1125 FPS），视角依赖增强贡献了最大质量提升（26.68→27.12 PSNR）。

### 贡献度剪枝分析（Table 4, 5, 6）

- 仅用不透明度剪枝：PSNR 26.84，0.43M高斯
- 仅用尺度剪枝：PSNR 26.87，0.45M高斯
- 联合剪枝：PSNR 27.12，0.47M高斯（最佳平衡）
- 阈值 $\tau=0.2$ 为最佳（Table 5）：0.47M高斯，PSNR 27.12
- 剪枝策略可无缝集成到MaskGaussian和Mini-Splatting中（Table 6）

## 局限性

1. **训练时间更长**：1.5小时 vs 0.4-0.8小时（baseline方法），因为需要训练MLP和蒸馏过程
2. **轻微质量退化**：PSNR相比原版3DGS降0.09（Mip-NeRF360），在需要最高质量的场景中可能不足
3. **视角依赖增强的MLP开销**：虽然轻量（256→128→64），仍增加推理延迟（Fig. 6中MLP占~25%渲染时间）
4. **顺序无关渲染的固有伪影**：在深度模糊的重叠几何区域，即使有神经增强仍有轻微透明度伪影（Fig. 7对比显示）
5. **码本大小敏感**：码本过小（$2^6$）时PSNR骤降至25.52；码本过大（$2^{12}$）时存储增至7.9 MB（Table 7）
6. **教师模型依赖**：蒸馏质量受限于Mini-Splatting教师模型的能力
7. **量化精度损失**：SH分解为 $h_d/h_v$ 并量化为16-bit会损失部分视角依赖细节

## 实现细节

- **训练**：PyTorch + 自定义CUDA Kernel用于顺序无关渲染，RTX 3090 GPU，60k迭代
- **量化启动**：第35k迭代启动神经向量量化
- **MLP初始化**：$\beta$ 初始化为1以稳定训练
- **多视角训练**：采用MVGS的多视角约束增强整体渲染性能
- **移动端部署**：Vulkan 2.0实现，跨平台图形API，低开销GPU访问
- **教师模型**：Mini-Splatting（传统alpha合成，无量化过程）

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 涉及概念: [[concepts/alpha-compositing]], [[concepts/spherical-harmonics]], [[concepts/adaptive-density-control]], [[concepts/order-independent-rendering]], [[concepts/gaussian-compression]], [[concepts/neural-view-dependent-enhancement]]
- 对比方法: SortFreeGS, LightGaussian, Speedy-Splat, C3DGS, GES, LocoGS-S, HAC, AdR-Gaussian
