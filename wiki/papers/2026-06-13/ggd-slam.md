---
title: "GGD-SLAM: Monocular 3DGS SLAM Powered by Generalizable Motion Model for Dynamic Environments"
authors: "Yi Liu, Haoxuan Xu, Hongbo Duan, Keyu Fan, Zhengyang Zhang, Peiyu Zhuang, Pengting Luo, Houde Liu"
year: 2026
venue: arXiv
status: done
tags:
  - slam
  - dynamic-slam
  - 3dgs
  - monocular-slam
  - motion-model
---

## 一句话总结

基于**可泛化运动模型（GMM）**的单目动态场景3DGS-SLAM，无需预定义语义标注或深度输入，通过FIFO队列+时序注意力机制分离动静态特征，并引入**干扰自适应SSIM损失**和**静态KD-tree遮挡恢复**，在TUM（ATE 1.3 cm）和Bonn（ATE 2.7 cm）数据集上实现SOTA纯单目跟踪与重建。

## 解决的问题

3DGS-SLAM依赖静态环境假设，动态场景中性能严重退化。现有方法要么依赖语义先验（YOLO+SAM），要么依赖深度传感器，要么仅用单帧信息无法跨帧追踪运动。GGD-SLAM提出**无需任何预定义标注或深度输入**的可泛化运动模型，从RGB帧序列的时序变化中学习"什么是运动"。

## 核心贡献 (from abstract)

- **可泛化运动模型（GMM）**：FIFO队列管理渐进式SLAM输入帧，通过时序注意力机制提取动态语义特征，与动态特征增强器集成实现动静态分离
- **干扰自适应SSIM损失**：通过自适应核仅在静态区域计算SSIM，避免动态像素污染结构相似性度量
- **静态信息采样填充遮挡**：构建静态高斯KD-tree，在移除动态物体后通过最近邻采样填充被遮挡区域
- SOTA动态场景位姿估计与稠密重建，在TUM fr3/w/half（ATE 1.4 cm）和bonn/crowd2（ATE 1.8 cm）超过RGB-D方法

## 核心方法

### 1. 可泛化运动模型 GMM (Sec III-A)

**数据预处理**：用预训练DINOv2提取当前帧特征 x_t ∈ R^{H'×W'×C}（H'=384, W'=512）。x_t仅含结构和语义信息，缺乏时序动态。引入**FIFO队列** Q_t ∈ R^{L×H'×W'×C} 渐进聚合历史帧（L=12默认）：

```
Q_t = [x_{t-L}, ..., x_{t-1}]  (满队列)
Q_t = [0,...,0, x_1,...,x_{t-1}]  (未满队列，零填充)
```

**时序注意力机制**：以当前帧x_t为Query，历史队列Q_t为Key/Value，多头注意力捕捉帧间运动语义：

```
Q_t = x_t W_Q,  K_t = Q_t W_K,  V_t = Q_t W_V
F_attn,t = MultiHeadAttention(Q_t, K_t, V_t)
```

**动态特征增强器**：两个独立头（Dynamic Head D, Static Head S）从注意力特征中分离动静态成分，增强公式：
```
F_enh,t = F_attn,t ⊙ (1 + αD) ⊙ (1 - αS)
```
其中α为增强系数——动态信号被放大，静态信号被抑制。

**训练**（Davis Dataset，含GT运动mask）：
- L_base: 逐像素 |M_gt - M̂|（几何精度）
- L_reg: 二元熵惩罚 −(M̂ log M̂ + (1−M̂) log(1−M̂))（驱赶中间值到{0,1}）
- L_dice: Dice Loss = 1 − 2|M_gt ∩ M̂|/(|M_gt| + |M̂|)（保持形状完整性）

**推理**：Otsu自适应阈值二值化 → 形态学膨胀（disk核）消除边缘模糊 → 最终先验mask M_t

### 2. 跟踪 (Sec III-B)

采用DROID-SLAM的**稠密BA（DBA）**框架，维护帧图 G=(V,E)。将GMM输出的动态先验M_t注入：静态成分 S = 1−M_t 用于构建因子图，完全消除动态区域的残差。深度估计用**Metric3D-v2**提供尺度感知单目深度。

跟踪损失：L_t = λ₁ L_DBA + λ₂ L_depth + λ₃ L_smoothness

### 3. 建图 (Sec III-C)

**不确定性模型**（Eq. 8）：结合几何渲染不确定性和运动先验U_t，为动态区域设定目标不确定性阈值T_max=0.1，防止不确定性感知机制将静态干扰（噪声、光照变化）误判为动态。

**增量高斯图**：新关键帧到来时，为新观测像素创建高斯（颜色c*、位置μ*通过反投影、不透明度0.5、半径0.1）。

**遮挡恢复**（Eq. 9）：对动态点μ_i ∈ M_t，构建静态高斯KD-tree，查询k=10近邻，从中随机采样替换被遮挡像素的深度和颜色：
```
μ_i ← (μ_{i,x}, μ_{i,y}, μ_{j,z}),  c_i ← c_j  (j ∼ Sample(1, k))
```

**干扰自适应SSIM**（Eq. 13）：核心创新——传统方法在计算SSIM map后移除动态区域，但卷积核覆盖范围内的静态像素O仍被动态像素污染（Fig. 3）。GGD-SLAM通过Hadamard积 w_ad(O) = w_unit ⊙ S_t(O) 生成自适应核，仅用静态像素计算SSIM：
```
SSIM Map_μ(O) = (w_ad(O) ⊙ w_ori,μ) * I / N_ad(O)
```

**建图损失**（Eq. 11）：L_mapping = λ₁ L_3DGS + λ₂ L_iso + λ₃ L_ssim_dy
其中 L_3DGS = (1−λ_d) ||(I_r−I)/U_t²||₁ + λ_d ||(D_r−D_est)/U_t²||₁（λ_d=0.5）

## 数学形式

**时序注意力**（Eq. 2）：
```
Q_t = x_t W_Q,  K_t = Q_t W_K,  V_t = Q_t W_V
F_attn,t = softmax(Q_t K_t^T / √d_k) V_t
```

**动态特征增强**：
```
F_enh,t = F_attn,t ⊙ (1 + αD) ⊙ (1 − αS)
```

**训练损失**（Eq. 3-5）：
```
L_GD = λ₁ L_base + λ₂ L_reg + λ₃ L_dice
L_base = |M_gt − M̂|
L_reg = −(M̂ log M̂ + (1−M̂) log(1−M̂))
L_dice = 1 − 2 Σ M_gt M̂ / Σ(M_gt + M̂)
```

**不确定性建模**（Eq. 8）：
```
U_t = clamp(U_geo + λ_m · M_t, 0, T_max)
```
其中 U_geo 为几何渲染不确定性，M_t 为GMM运动先验。

**自适应SSIM核**（Eq. 13b）：
```
w_ad(O) = w_unit ⊙ S_t(O),  N_ad(O) = w_unit ∗ S_t(O)
```

## 与前作的区别

| 方法 | 动态检测机制 | 需要训练 | 需要深度 | 是否需要语义标注 |
|------|-------------|---------|---------|----------------|
| **GGD-SLAM** | GMM (FIFO+时序注意力) | 是（Davis数据集预训练） | 否（纯单目RGB） | 否 |
| Dy3DGS-SLAM | 光流+深度mask概率融合 | 否（前向推理） | 单目估计 | 否 |
| ADD-SLAM | 场景一致性分析 | 否 | 否 | 否 |
| WildGS-SLAM | DINOv2不确定性 | 是（DINOv2预训练） | 否 | 否 |
| DG-SLAM | YOLO+SAM语义分割 | 是（预训练模型） | RGB-D | 是 |
| DyPho-SLAM | 语义标签 | 是（预训练模型） | RGB-D | 是 |

GGD-SLAM以WildGS-SLAM为基线，核心差异：(1) 用GMM替代WildGS的纯不确定性方法——GMM跨多帧学习运动语义，而非仅依赖单帧渲染误差；(2) 干扰自适应SSIM替代标准SSIM——解决了动态像素通过卷积核污染相邻静态像素SSIM值的问题；(3) KD-tree遮挡恢复替代简单的高斯丢弃。

## 实验结论

### 跟踪精度 (Table I)
- **TUM**（3场景平均）：ATE 1.3 cm——在fr3/w/xyz（1.1 cm）、fr3/w/half（1.4 cm）超过所有RGB-D方法
- **Bonn**（4场景平均）：ATE 2.7 cm——在crowd2（1.8 cm）表现最优
- **关键发现**：高动态序列中纯单目方法首次超越RGB-D方法——归功于GMM精确的动态识别避免了错误数据关联

### 建图质量 (Table III)
- 平均PSNR 23.03 dB（WildGS-SLAM 22.23 dB, MonoGS 17.04 dB）
- 平均SSIM 0.859，LPIPS 0.158——均为单目方法最优

### 消融实验
- **GMM模块**（Table II）：GMM先验+Otsu二值化+平滑项组合ATE最优（ps_track 3.41, crowd2 1.79）
- **自适应SSIM + KD-tree**（Table IV）：两者联合PSNR最高（fr3/w/xyz 22.68, bonn/cr2 24.27）——单独使用自适应SSIM（21.96）优于单独KD-tree（21.59）

### 定性结果 (Fig. 4)
GMM在复杂场景中准确提取动态语义：快速运动模糊物体、小目标、大尺度相机运动、跨帧静态但长期运动的物体（如椅子）均能正确分类。仅用L_base训练特征噪声大（结构保持不足）。

### 泛化性 (Fig. 6)
在Wild-SLAM Dataset上成功分割多种运动物体（球、球拍、雨伞），GMM引导的不确定性生成实现高质量渲染。

## 局限性

- **非实时动态重建**：仅移除动态物体，不能重建动态物体自身的运动轨迹或几何
- **完全遮挡区域无法修复**：KD-tree采样仅处理部分遮挡，完全被遮挡的背景区域缺乏静态信息源
- **GMM泛化上限**：仅在Davis Dataset（视频物体分割）上训练，极端域外场景（如特殊光照、非常见物体运动模式）可能失效
- **依赖DROID-SLAM DBA框架**：跟踪精度受限于DROID-SLAM的设计选择，非端到端联合优化
- **FIFO队列长度L=12**：长队列提供更广时序上下文但也增加计算开销，短队列可能遗漏慢速运动

## 关联

- [[concepts/3d-gaussian]] — 基础3DGS表示
- [[concepts/slam]] — SLAM问题定义
- [[concepts/generalizable-motion-model]] — 本文核心贡献：可泛化运动模型
- [[concepts/uncertainty-aware-mapping]] — 结合GMM先验的不确定性建模
- [[concepts/ssim-loss]] — SSIM损失基础，本文提出干扰自适应变体
- [[concepts/dinov2]] — DINOv2特征提取用于GMM输入
- [[concepts/bundle-adjustment]] — DROID-SLAM DBA跟踪框架
- [[concepts/isotropic-regularization]] — 稀疏区域各向同性正则化
- [[papers/2026-06-11/add-slam]] — 同为纯RGB动态SLAM，场景一致性分析方法
- [[papers/2026-06-13/dy3dgs-slam]] — 同期单目动态SLAM，概率融合方法
- [[papers/2026-05-21/wildgs-slam]] — 基线方法，不确定性感知动态SLAM
- [[papers/2026-06-13/droid-slam-in-the-wild]] — DROID-SLAM动态扩展，不同技术路线
- [[synthesis/dynamic-slam-comparison]] — 动态SLAM方法综合对比
