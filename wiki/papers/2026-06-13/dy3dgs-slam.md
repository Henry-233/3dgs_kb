---
title: "Dy3DGS-SLAM: Monocular 3D Gaussian Splatting SLAM for Dynamic Environments"
authors: "Mingrui Li, Yiming Zhou, Hongxing Zhou, Xinggang Hu, Florian Roemer, Hongyu Wang, Ahmad Osman"
year: 2025
venue: arXiv (2506.05965v1)
status: done
tags:
  - slam
  - dynamic-slam
  - 3dgs
  - monocular-slam
---

## 一句话总结

首个纯单目RGB输入的动态场景3DGS-SLAM，通过**概率融合光流mask与深度mask**检测动态区域，并结合**运动损失**约束位姿估计，单次网络迭代即可实现SOTA动态环境跟踪与渲染。

## 解决的问题

现有NeRF/3DGS SLAM在含运动物体的动态场景中跟踪和重建性能严重退化，且已有的动态NeRF-SLAM依赖RGB-D输入。Dy3DGS-SLAM首次以**纯单目RGB**实现动态场景的3DGS-SLAM，解决了三个核心子问题：(1) 如何仅从RGB估计准确的动态mask；(2) 如何用动态mask约束单目尺度模糊的位姿估计；(3) 如何消除动态像素对高斯建图的污染。

## 核心贡献 (from abstract)

- **概率融合动态mask**：将光流mask与深度mask通过贝叶斯概率模型融合，单次网络迭代即可约束跟踪尺度并优化渲染几何
- **运动损失 (motion loss)**：基于融合动态mask设计的新型损失函数，含尺度约束的平移损失+旋转损失，约束位姿估计网络的跟踪精度
- **动态像素渲染损失**：在建图阶段对动态像素施加独立惩罚项的颜色和深度渲染损失，消除动态物体造成的瞬态干扰和遮挡
- SOTA跟踪与渲染性能：BONN ATE 4.5 cm、TUM ATE 4.7 cm，在动态环境中超越或匹配现有RGB-D方法

## 核心方法

### 1. 动态Mask概率融合 (Sec III-A)

系统接收连续两帧无畸变图像 I_t, I_{t+1}，首先用**轻量U-Net运动分割网络**估计光流F和光流异常mask F_m。同时用**Depth Anything v2**估计单目深度图D和深度不一致mask D_m。

关键创新在于融合策略：对每个像素p，用**贝叶斯公式**计算其后验动态概率：

P(M(p)=1 | D_m, F_m) ∝ P(D_m | M(p)=1) · P(F_m | M(p)=1) · P(M(p)=1)

最终以阈值 T=0.95 二值化得到融合mask M̂。该mask通过并集运算处理多运动物体：M̂ = M(N_1) ∪ M(N_2) ∪ ... ∪ M(N_i)。整个过程无需额外网络迭代，无需场景特定参数调整。

### 2. 单目动态场景跟踪 (Sec III-B)

从融合mask中提取**静态深度mask** M_ds = {p ∈ M̂ | M(p)=0}，将其应用到光流图以过滤动态区域，并融合尺度因子S_n：

F̃ = F · M_ds · S_n

这使得网络能在静态区域获得可靠的深度约束，同时避免动态区域干扰。

**运动损失 L_M** 结合尺度约束的平移误差和旋转误差（Eq. 6），统一优化光流损失L_O、运动分割损失L_U和相机运动损失L_M（Eq. 7）。位姿估计基于**ResNet50**骨干，遵循TartanVO训练设计。

与DytanVO的三次迭代不同，该方法仅需**单次网络迭代**即可获得准确的位姿和mask。每10帧生成关键帧，≥4个关键帧组成关键帧组进行局部BA优化。

### 3. 动态场景高斯渲染 (Sec III-C)

标准3DGS渲染管线（Eq. 8-11），但引入动态感知的渲染损失：

- **光度损失 L_c**（Eq. 12）：对动态像素施加权重λ_d，对静态像素施加权重λ_s。动态像素的渲染误差被独立惩罚，防止其污染静态高斯优化。
- **深度损失 L_d**（Eq. 13）：类似结构，λ_t惩罚动态深度mask，λ_m惩罚静态深度mask。

被标记为动态的高斯直接设置深度为无穷大进行剪枝。

## 数学形式

**高斯定义**（Eq. 8）：
```
g(x) = o · exp(-½ x^T Σ^{-1} x),  Σ = RSS^T R^T
```
其中 o∈[0,1]为不透明度，S为尺度矩阵，R为旋转矩阵。

**相机空间协方差**（Eq. 9）：
```
Σ' = J W Σ W^T J^T
```

**颜色渲染**（Eq. 10）：
```
C = Σ_{i∈N} c_i · g_i · Π_{j=1}^{i-1} (1-g_j)
```

**深度渲染**（Eq. 11）：
```
D = Σ_{i=1}^n d_i · g_i · Π_{j=1}^{i-1} (1-g_j)
```
其中d_i为第i个3D高斯中心在z轴上的深度。

**动态mask后验**（Eq. 2-3）：
```
P(M(p)=1|D_m, F_m) = [P(D_m|M=1)·P(F_m|M=1)·P(M=1)] / P(D_m, F_m)
```

**运动损失**（Eq. 6）：
```
L_M = ||T̂ / max(|T̂·S_n|, ε) - T / max(|T·S_n|, ε)|| + ||R̂ - R|| · M_ds
```

**联合跟踪损失**（Eq. 7）：
```
L_P = λ₁L_O + λ₂L_U + L_M
```

## 与前作的区别

| 方法 | 输入 | 动态检测 | 核心机制 |
|------|------|----------|----------|
| **Dy3DGS-SLAM** | 单目RGB | 概率融合(光流+深度mask) | 单次迭代运动损失+动态像素惩罚 |
| ADD-SLAM | 单目RGB | 场景一致性分析(渲染vs观测) | 时序高斯模型 |
| WildGS-SLAM | 单目RGB | 不确定性图(DINOv2) | 不确定性感知动态建图 |
| GGD-SLAM | 单目RGB | 时序注意力(FIFO) | 可泛化运动模型 |
| DROID-SLAM in the Wild | 单目RGB | 多视图特征不一致性 | 不确定性感知BA |
| DynaSLAM | RGB-D | 语义先验+几何约束 | Mask R-CNN + 多视图几何 |
| DytanVO | 单目RGB | 光流异常 | 三次迭代运动分割 |
| NID-SLAM | RGB-D | 光流估计 | NeRF建图 |

与DytanVO的关键区别：DytanVO需要3次迭代细化mask和位姿，Dy3DGS-SLAM通过概率融合depth mask弥补光流mask的粗糙性，仅需1次迭代。与ADD-SLAM/GGD-SLAM的区别：后者在"建图"阶段处理动态（渲染vs观测比较/时序注意力），而Dy3DGS-SLAM在"跟踪"阶段直接估计动态mask。

## 实验结论

### 跟踪精度
- **BONN RGB-D**（Table I）：ATE 4.5 cm（6场景平均），在balloon2场景最优（1.9 cm），仅略逊于DynaSLAM（4.8 cm，但DynaSLAM依赖RGB-D+语义先验）
- **TUM RGB-D**（Table II）：ATE 4.7 cm（6场景平均），在f3/static/xyz场景最优（2.0 cm），在低动态场景中接近DynaSLAM

### 消融实验 (AirDOS-Shibuya)
- **光流+深度融合**：ATE 3.0 cm（vs 仅光流7.6 cm → 60.52%提升；仅深度94.8 cm → 深度单独不足以处理动态）
- **Mask融合质量**（Fig. 3）：仅光流mask或仅DytanVO式运动损失均产生显著mask估计误差，完整方法最接近ground truth

### 运行效率 (Table IV)
- 跟踪：17.0 FPS（DytanVO 10.5 FPS）
- 建图：430.5 ms/帧
- 网络更新：10.3 ms（DytanVO 32.9 ms → 3.2×更快，归功于单次迭代）
- GPU显存：12.8 MB

### 定性结果
在BONN和TUM数据集上，重建mesh比基线方法更完整、更准确，无动态物体残影（floaters）。

## 局限性

- **依赖深度估计质量**：概率融合中深度mask的可靠性受限于Depth Anything v2的域泛化能力，在室外或特殊光照下可能退化
- **仅验证室内场景**：BONN、TUM、AirDOS-Shibuya均为室内数据集，室外动态场景（如自动驾驶）尚未评估
- **阈值T=0.95固化了准确率-召回率权衡**：高阈值可能漏检慢速运动物体或部分遮挡的动态区域
- **单次迭代的极限**：极快运动或运动模糊场景下，单次网络前向可能不足以精确分割动态区域
- **无语义理解**：无法区分"需要移除的动态物体"与"需要保留的交互物体"

## 关联

- [[concepts/3d-gaussian]] — 基础3DGS表示
- [[concepts/slam]] — SLAM问题定义
- [[concepts/probabilistic-dynamic-segmentation]] — 本文核心贡献：概率光流+深度mask融合
- [[concepts/monocular-depth-estimation]] — 深度估计（Depth Anything v2）提供深度mask
- [[concepts/alpha-compositing]] — 动态像素渲染损失的基础渲染操作
- [[concepts/bundle-adjustment]] — 关键帧局部BA优化
- [[papers/2026-06-11/add-slam]] — 同为纯RGB动态SLAM，场景一致性分析方法
- [[papers/2026-05-21/wildgs-slam]] — 不确定性感知动态SLAM
- [[papers/2026-06-13/ggd-slam]] — 可泛化运动模型方法
- [[papers/2026-06-13/droid-slam-in-the-wild]] — 不确定性感知BA方法
- [[synthesis/dynamic-slam-comparison]] — 动态SLAM方法综合对比
