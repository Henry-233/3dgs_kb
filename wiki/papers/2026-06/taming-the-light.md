---
title: "Taming the Light: Illumination-Invariant Semantic 3DGS-SLAM"
authors:
  - "Shouhe Zhang"
  - "Dayong Ren"
  - "Sensen Song"
  - "Yurong Qian"
  - "Zhenhong Jia"
year: 2025
venue: arXiv
status: done
tags:
  - slam
  - semantic-slam
  - illumination-invariant
  - 3dgs
---

## 一句话总结

Taming the Light通过IAN（颜色量化强正则化，将反照率强制离散化为4级palette → 光照变化被隔离到独立的光照因子l_i）与DRB-Loss（SSIM门控触发 → 可学习曝光参数(g,o)对渲染图做仿射变换 → L1对齐）的主动-被动协同，首次实现极端曝光变化下仍保持光照不变的语义3DGS-SLAM——Replica ATE 0.34 cm（超过所有对比方法），语义mIoU 92.69%，完整模型Room0深度误差从0.46降至0.25。

## 解决的问题

极端曝光（过曝/欠曝）同时破坏3D地图重建和语义分割——对紧耦合的系统尤为致命。标准3DGS直接优化连续RGB值，会将瞬态光照效应"烘焙"进场景颜色表示，导致不同光照条件下的渲染不一致。现有方法缺乏专门光照不变性设计。

## 核心方法

### 1. 光照不变的高斯表示（Sec 2.1）

在标准3DGS基础上，将每个高斯的颜色参数**分解**为两个独立分量：
- **内在反照率 a_i**：光照不变的标准化颜色——反映场景材质本身
- **光照因子 l_i**：可学习参数捕捉残余光照变化

渲染时颜色 = SH系数评估 + a_i + l_i 的组合。这一分解是IAN的基础——反照率与光照显式分离。

### 2. Intrinsic Appearance Normalization (IAN, Sec 2.2)

IAN的核心是将连续反照率空间**强制量化为离散palette**，阻止网络将光照变化编码进反照率：

$$a_{v}^{\prime} = \lfloor 4 \cdot a_{v} \rfloor \cdot 0.25 + 0.125$$

每个RGB通道被约束到{0.125, 0.375, 0.625, 0.875}四个值之一（共4³=64种颜色），形成标准化"内在外观模型"。由于反照率空间被严重压缩，网络被迫将光照变化归因到光照因子l_i而非a_i，实现了从表示层面的光照免疫。

### 3. Dynamic Radiance Balancing Loss (DRB-Loss, Sec 2.3)

IAN提供前摄不变性，但无法处理剧烈的逐帧辐射度变化（相机自动曝光、光照环境剧变）。DRB-Loss作为被动纠正机制：

**门控检测：**
$$S = \text{SSIM}(I_{\text{render}}, I_{\text{gt}})$$

当S < T_DRB（设为0.50）时判定为"曝光帧"，激活DRB-Loss。

**仿射曝光补偿：**
引入可学习曝光参数θ={g, o}：
$$I_{\text{render}}^{\theta} = g \cdot I_{\text{render}} + o$$

$$\mathcal{L}_{\text{DRB}} = \|I_{\text{render}}^{\theta} - I_{\text{gt}}\|_1$$

(g, o)与场景参数联合优化。正常帧(SSIM≥0.50)的DRB-Loss为零，不影响正常性能。

### 4. 光照不变跟踪（Sec 2.4）

跟踪损失使用IAN产生的内在反照率C_a(p)（而非原始渲染颜色）+ 深度 + 语义 + 条件DRB-Loss：

$$\mathcal{L}_{\text{tracking}} = \lambda_D\|D-D_{\text{gt}}\|_1 + \lambda_C\|C_a-C_{\text{gt}}\|_1 + \lambda_S\|S-S_{\text{gt}}\|_1 + \lambda_{\text{DRB}}\mathbb{I}(S<T_{\text{DRB}})\mathcal{L}_{\text{DRB}}$$

关键：跟踪匹配使用的是**光照不变的内在反照率**C_a，而非受光照影响的原始颜色。

### 5. 建图优化（Sec 2.5）

建图损失包括几何、外观、语义：L_mapping = Σ(λ_D·L1_depth + λ_C·L1_albedo + λ_S·L_CE + λ_DRB·I·L_DRB)，语义损失使用交叉熵（比SSIM更适合分类任务）。

## 数学形式

**IAN量化 (Eq. 5):**
$$a_{v}^{\prime} = \lfloor 4 \cdot a_{v} \rfloor \cdot 0.25 + 0.125$$

**DRB门控 (Eq. 6):**
$$S = \text{SSIM}(I_{\text{render}}, I_{\text{gt}}), \quad \text{activate if } S < 0.50$$

**DRB损失 (Eq. 7):**
$$I_{\text{render}}^{\theta} = g \cdot I_{\text{render}} + o, \quad \mathcal{L}_{\text{DRB}} = \|I_{\text{render}}^{\theta} - I_{\text{gt}}\|_1$$

**跟踪损失 (Eq. 8):**
$$\mathcal{L}_{\text{tracking}} = \lambda_D\|D-D_{\text{gt}}\|_1 + \lambda_C\|C_a-C_{\text{gt}}\|_1 + \lambda_S\|S-S_{\text{gt}}\|_1 + \lambda_{\text{DRB}}\mathbb{I}(S<T_{\text{DRB}})\mathcal{L}_{\text{DRB}}$$

**关键帧选择 (Eq. 9):**
$$\eta = \frac{\sum_{G_i \in G_{\text{map}}}\mathbb{I}(\text{is\_in\_view}(G_i, E_{\text{cand}}))}{|G_{\text{map}}|}$$

两级过滤：几何过滤器（重投影比例η）+ 语义过滤器（丢弃与上一关键帧语义相同的候选帧）。

**建图损失 (Eq. 10):**
$$\mathcal{L}_{\text{mapping}} = \sum_{p \in \mathcal{P}}(\lambda_D\|D-D_{\text{gt}}\|_1 + \lambda_C\|C-C_{\text{gt}}\|_1 + \lambda_S\mathcal{L}_{\text{CE}}(S,S_{\text{gt}}) + \lambda_{\text{DRB}}\mathbb{I}(S<T_{\text{DRB}})\mathcal{L}_{\text{DRB}})$$

## 与前作的区别

| 维度 | SGS-SLAM | MonoGS | SplaTAM | **Taming the Light** |
|------|----------|--------|---------|---------------------|
| **颜色表示** | 连续RGB | SH+RGB | SH+RGB | **反照率a_i + 光照l_i分解** |
| **光照不变性** | 无 | 无 | 无 | **IAN量化+DRB矫正** |
| **语义集成** | 语义渲染 | 无 | 无 | **紧耦合语义建图+跟踪** |
| **极端曝光** | 崩溃 | 崩溃 | 崩溃 | **门控自适应补偿** |
| **正常光照** | 正常 | 正常 | 正常 | **零性能损失**（DRB仅在S<0.50激活） |

与RoGER-SLAM对比：Taming the Light处理场景光照变化（反照率-光照解耦），RoGER-SLAM处理传感器退化（噪声+低光+CLIP增强），两者正交。

## 实验结论

**跟踪 (ATE RMSE cm ↓):**
- **Replica**: Ours **0.34 cm**（Avg.最佳），ESLAM 0.63，Point-SLAM 0.52，NICE-SLAM 1.07
- **ScanNet**: Ours **11.30 cm**（Avg.），各场景7.9-17.1 cm

**语义分割 (mIoU %):**
- Replica: Ours **92.69%**（与SGS-SLAM的92.72%可比），各场景92.02-93.10%
- 在光照鲁棒性前提下保持语义精度

**消融实验 (Replica Room0, Table 4):**
| 配置 | ATE↓ | Depth L1↓ | PSNR↑ | mIoU↑ |
|------|------|-----------|-------|-------|
| Baseline (SGS-SLAM) | 0.50 | 0.46 | 32.41 | 92.69 |
| + IAN | 0.50 | 0.36 | 32.22 | 92.40 |
| + DRB-Loss | 0.53 | 0.30 | 32.85 | 92.56 |
| **Full (IAN+DRB)** | **0.49** | **0.25** | **33.03** | **92.94** |

- IAN单独：深度误差从0.46降至0.36（提升22%），PSNR轻微下降（量化损失），语义略降
- DRB单独：深度降至0.30（提升35%），PSNR升至32.85，但ATE略差（0.53）
- **协同效应**：完整模型在所有指标上优化——ATE持平最佳、深度提升46%、PSNR+0.62 dB、mIoU+0.25%

**定性分析：** IAN使渲染反照率在不同光照下保持颜色一致；DRB-Loss在曝光帧自适应调整亮度/对比度，防止误差累积。

## 局限性

1. **粗粒度量化**：仅4级per-channel量化（64种颜色），丢失精细材质信息，可能不适合高保真外观要求
2. **DRB简单仿射**：g·I+o的仿射模型过于简单，无法处理空间变化的曝光（如角落过暗、窗边过亮）
3. **SSIM门控粗糙**：固定阈值0.50在所有场景通用性不足
4. **仅验证室内**：Replica+ScanNet均为室内数据集，室外极端光照（昼夜、阳光直射）未验证
5. **无回环检测**：未讨论回环闭合，长轨迹可能累积漂移
6. **反照率-光照分离非物理**：非基于物理渲染的材质分解，l_i是纯学习参数

## 关联

- [[concepts/slam]] — SLAM基础框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示，IAN对颜色参数的重构
- [[concepts/spherical-harmonics]] — SH编码视角依赖外观，IAN与其互补（SH视角 + IAN光照不变）
- [[concepts/intrinsic-appearance-normalization]] — IAN是本文核心创新
- [[concepts/ssim-loss]] — SSIM同时用作DRB门控信号和颜色损失分量
- [[concepts/semantic-slam]] — 紧耦合语义SLAM
- [[papers/2026-06/roger-slam]] — 互补：RoGER-SLAM处理传感器退化（噪声/低光），本论文处理场景光照变化
- [[papers/2026-06/varsplat]] — 互补：VarSplat用方差处理测量可靠性，本论文用量化处理光照不变性
