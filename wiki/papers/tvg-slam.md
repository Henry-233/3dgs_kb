---
title: "TVG-SLAM: Robust Gaussian Splatting SLAM with Tri-view Geometric Constraints"
authors:
  - "Zhen Tan"
  - "Xieyuanli Chen"
  - "Lei Feng"
  - "Yangbing Ge"
  - "Shuaifeng Zhi"
  - "Jiaxiong Liu"
  - "Dewen Hu"
year: 2025
venue: arXiv
status: done
tags:
  - slam
  - rgb-only-slam
  - outdoor-slam
  - 3dgs
---

## 一句话总结

TVG-SLAM通过三视图几何范式——DUST3R稠密匹配→三视图一致性筛选→混合几何跟踪（光度+三焦张量2D重投影+3D对齐+DART动态权重衰减）+ TUGI不确定性引导高斯初始化——将纯RGB 3DGS-SLAM从"光度依赖"升级为"几何-光度协同"，在Cambridge Landmarks上ATE相对OpenGS-SLAM降低69.0%（2.009 vs 6.490 m），Waymo ATE 0.602 m。

## 解决的问题

现有纯RGB 3DGS-SLAM系统（MonoGS、GS-SLAM等）的相机跟踪严重依赖光度渲染一致性——在无界室外环境中，光照剧变（阴影、云层、太阳角度）和大幅视角偏移导致光度假设频繁失效。同时，现有建图方法的高斯初始化依赖启发式规则（如基于光度梯度或深度残差），未能利用多视图几何信息，导致几何不准确或冗余高斯。

核心矛盾：**光度一致性在室外场景中不可靠，需要显式几何约束作为稳定锚点**。

## 核心方法

### 1. 系统总览 (Sec 3.1)

TVG-SLAM管线由三个紧密耦合的组件构成：稠密三视图匹配 → 混合几何跟踪（含DART） → 不确定性引导建图（含TUGI）。使用DUST3R作为稠密匹配器，通过前一关键帧初始化每帧位姿。

### 2. 稠密三视图匹配 (Sec 3.3)

将DUST3R生成的可靠成对对应关系聚合为**一致的三视图匹配**。对于三帧(I_k1, I_k2, I_cur)，一个三视图匹配(p_k1, p_k2, p_cur)必须同时满足三个两两之间的极线约束。相比成对匹配，三视图验证天然滤除不一致的误匹配，极大提高几何约束的可靠性。

### 3. 混合几何跟踪 (Sec 3.4)

跟踪损失由三项组成：

$$\mathcal{L} = \lambda_{\text{photo}}\mathcal{L}_{\text{photo}} + \lambda_{\text{tri}}\mathcal{L}_{\text{tri}} + \lambda_{\text{3D}}\mathcal{L}_{\text{3D}}$$

**光度损失 L_photo**：标准L1+SSIM组合损失，比较渲染图与观测图。

**三焦张量约束 L_tri**：对每个三视图匹配(p_k1, p_k2, p_cur)，由两关键帧位姿计算三焦张量T（3个3×3矩阵），通过极线传输公式计算第三视图中对应的极线l，最小化p_cur到l的几何距离：

$$\mathcal{L}_{\text{tri}} = \sum \rho(\text{dist}(p_{\text{cur}}, l)^2)$$

其中ρ为Huber损失。三焦约束提供比成对极线几何更强的几何可观测性——三个视角的交点唯一确定3D点位置。

**3D对齐损失 L_3D**：利用从三视图匹配三角化得到的3D点云，直接最小化估计3D坐标与通过估计位姿投影的3D坐标之间的对齐误差。这是显式的点-点3D约束。

### 4. DART: 动态渲染信任衰减 (Sec 3.4)

在异步跟踪-建图架构中，建图延迟导致渲染视图基于过期地图，光度监督不再可靠。DART以距上一关键帧的帧数n作为地图陈旧度代理，用sigmoid函数平滑调节光度权重：

$$\lambda_{\text{photo}}(n) = \lambda_{\min} + \frac{\lambda_{\max} - \lambda_{\min}}{1 + \exp(-k(n - n_0))}$$

- n小（地图新）：λ_photo高，充分利用光度信息
- n大（地图旧）：λ_photo平滑衰减，系统自动转向不依赖地图的几何约束L_tri和L_3D

参数设置：λ_max, λ_min为光度权重边界，n_0为中点，k控制过渡锐度。

### 5. TUGI: 不确定性引导高斯初始化 (Sec 3.5)

**不确定性估计**：对每个三视图匹配(p_k1, p_k2, p_cur)，从对应的pointmap中获取3D位置估计（来自(k1,k2)、(k1,cur)、(k2,cur)三对），变换到统一参考系后计算各向同性方差：

$$\sigma^2 = \frac{1}{N_{\text{valid}} - 1} \sum \|X_i - \bar{X}\|^2$$

σ²捕获多视图一致性：小σ²表示三个点map估计高度一致（高置信度），大σ²表示不一致（低置信度）。

**初始化策略**：
- **位置**：候选点3D坐标直接作为高斯中心μ
- **颜色**：三视图像素强度的均值，确保跨视角外观鲁棒性
- **协方差**：缩放矩阵正比于σ（不确定点获得更大初始支撑域，给优化器更大灵活性）
- **不透明度**：α = α_base / (1 + β·σ²)，随不确定性递减——不可靠高斯以低不透明度开始，抑制早期渲染伪影

## 数学形式

**跟踪损失 (Eq. 2):**
$$\mathcal{L}_{\text{track}} = \lambda_{\text{photo}}\mathcal{L}_{\text{photo}} + \lambda_{\text{tri}}\mathcal{L}_{\text{tri}} + \lambda_{\text{3D}}\mathcal{L}_{\text{3D}}$$

**光度损失 (Eq. 3):**
$$\mathcal{L}_{\text{photo}} = (1 - \lambda)\mathcal{L}_1 + \lambda\mathcal{L}_{\text{SSIM}}$$

**三焦极线传输 (Eq. 4):**
$$l = T \cdot [p_{k1}, p_{k2}]^T$$

**三焦约束损失 (Eq. 5):**
$$\mathcal{L}_{\text{tri}} = \sum \rho(\|p_{\text{cur}} - l\|^2)$$

**DART权重衰减 (Eq. 7):**
$$\lambda_{\text{photo}}(n) = \lambda_{\min} + \frac{\lambda_{\max} - \lambda_{\min}}{1 + \exp(-k(n - n_0))}$$

**不确定性估计 (Eq. 8):**
$$\sigma^2 = \frac{1}{N_{\text{valid}} - 1} \sum_{i=1}^{N_{\text{valid}}} \|X_i - \bar{X}\|^2$$

**TUGI不透明度衰减 (Eq. 9):**
$$\alpha = \frac{\alpha_{\text{base}}}{1 + \beta \cdot \sigma^2}$$

## 与前作的区别

| 维度 | MonoGS | OpenGS-SLAM | Photo-SLAM | **TVG-SLAM** |
|------|--------|-------------|------------|-------------|
| **跟踪约束** | 纯光度 | 纯光度 | 纯光度 | **光度+三焦几何+3D对齐** |
| **几何源** | 无 | 无 | ORB特征 | **DUST3R稠密三视图匹配** |
| **高斯初始化** | 启发式 | 启发式 | 启发式 | **TUGI不确定性引导** |
| **光度权重** | 固定 | 固定 | 固定 | **DART动态衰减** |
| **室外鲁棒性** | 弱（光度失效） | 弱 | 中等 | **强（几何锚定）** |

与VarSplat对比：TVG-SLAM处理几何层面鲁棒性（三视图约束），VarSplat处理测量层面鲁棒性（方差加权）。与Taming the Light对比：TVG-SLAM通过几何约束绕过光照问题，Taming the Light通过IAN直接解耦光照。

## 实验结论

**数据集**：Waymo（长距驾驶，低视差）、Small City（动态物体+光照变化）、Cambridge Landmarks（手持拍摄，剧烈运动+频繁光照变化）。

**Waymo (Table I):**
| 方法 | ATE↓ | PSNR↑ | SSIM↑ | LPIPS↓ |
|------|------|-------|-------|--------|
| MonoGS | 8.530 | 21.80 | 0.781 | 0.578 |
| OpenGS-SLAM | 0.839 | 23.99 | 0.800 | 0.434 |
| **Ours** | **0.602** | **25.38** | **0.817** | **0.361** |

Waymo ATE相对OpenGS-SLAM降低28.2%，PSNR提升1.39 dB。在低视差长直道场景，纯光度方法严重漂移，三焦+3D约束提供稳定几何参考。

**Small City (Table II):**
| 方法 | ATE↓ | PSNR↑ |
|------|------|-------|
| MonoGS | 3.142 | 17.32 |
| OpenGS-SLAM | 3.481 | 17.63 |
| **Ours** | **1.195** | **18.78** |

**Cambridge Landmarks (Table III):**
| 方法 | ATE↓ | PSNR↑ |
|------|------|-------|
| MonoGS | 14.834 | 14.42 |
| OpenGS-SLAM | 6.490 | 15.75 |
| **Ours** | **2.009** | **16.47** |

**ATE相对OpenGS-SLAM降低69.0%**，验证了三视图几何约束在极端手持运动下的关键作用。

**消融实验 (Waymo scene 153495, Table IV):**

| 配置 | ATE↓ | PSNR↑ |
|------|------|-------|
| Full model | 0.870 | 25.62 |
| w/o L_3D (3D对齐) | 1.038 | 25.23 |
| w/o L_tri (三焦约束) | 1.193 | 25.44 |
| w/o TGC (两种几何全去) | 1.269 | 25.45 |
| w/o DART | 1.053 | 25.31 |
| **w/o TUGI** | **1.203** | **24.90** |

- TUGI去除：ATE增加38.3%，PSNR下降0.72 dB——单组件中影响最大
- DART去除：ATE增加21.0%，DART同时降低ATE和RPE的方差（55.3% RPE降低）
- 三焦+3D两种几何约束互补，联合去除后ATE从0.870升至1.269（+45.9%）

**效率分析 (Table V)**：稠密匹配400ms占主导（可按需替换为轻量替代），跟踪位姿/尺度优化49ms，渲染3.5ms/iter（跟踪）、4.5ms/iter（建图）。

## 局限性

1. **稠密匹配开销**：DUST3R匹配耗时400ms，占总运行时间的大部分，限制了实时性——虽可替换为轻量替代，但会损失几何可靠性
2. **无回环检测**：长轨迹累积漂移无法通过回环闭合消除
3. **RGB-only限制**：未利用深度传感器信息，纯视觉在纹理缺失区仍有退化风险
4. **仅验证室外**：未在室内数据集（Replica、TUM RGB-D）上评估
5. **静态场景假设**：Small City数据集虽有动态物体，但系统未显式建模动态目标
6. **依赖DUST3R预训练模型**：稠密匹配质量依赖于第三方模型的泛化能力

## 关联

- [[concepts/slam]] — SLAM基础框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示
- [[concepts/tri-view-geometric-constraints]] — 三视图几何约束是本文核心创新
- [[concepts/uncertainty-aware-tracking]] — TUGI的方差引导初始化与VarSplat/WildGS-SLAM的方差机制互补
- [[concepts/ssim-loss]] — 颜色损失中的SSIM分量
- [[concepts/projection-transform]] — 三焦张量、极线传输的数学基础
- [[papers/mono-gs]] — 纯RGB 3DGS-SLAM基线方法
- [[papers/varsplat]] — 互补：VarSplat处理测量不确定性，TVG-SLAM处理几何约束
- [[papers/taming-the-light]] — 互补：Taming the Light处理光照不变性，TVG-SLAM通过几何绕过光照问题
