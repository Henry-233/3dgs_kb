---
title: "ViMGS-SLAM: A real-time monocular 3DGS-based SLAM via multiscale vision transformers"
authors: Huixin Zhu, Junyang Zhao, Yutie Wang, Chen Xie, Fan Zhang, Jiayi Wang
year: 2026
venue: Array (Elsevier)
doi: 10.1016/j.array.2026.100973
tags: [paper, application, slam, monocular, real-time, vision-transformer]
status: done
---

## 一句话总结
ViMGS-SLAM 是首个将多尺度视觉Transformer（MViT）与3DGS紧耦合的单目SLAM框架。MViT通过层级金字塔架构（三尺度输入→五级特征金字塔）生成**度量尺度的逆深度图**，消除单目SLAM固有的尺度模糊；深度先验初始化并约束3DGS显式场景表示，同步跟踪-建图管线联合优化位姿和高斯参数。TUM fr3上ATE降低46.0%（vs MonoGS），Replica上PSNR 39.6 dB，单目模式2.7 FPS端到端、渲染1130 FPS。

## 通俗理解（Plain Language）

### 这个问题为什么难？
单目SLAM就一个摄像头——不知道绝对距离（"尺子没了"）。现有方案要么用自监督深度估计（只知道相对远近，不知道具体几米），要么依赖RGB-D传感器（贵、耗电）。3DGS需要可靠的深度来初始化高斯椭球的位置，深度不准→地图扭曲→定位漂移。

### ViMGS-SLAM 怎么做？

**类比**：想象你闭着一只眼走路。普通人只能判断"树比房子近"（相对深度）。ViMGS-SLAM的MViT模块相当于给了你一只"电子眼"——它看过海量数据，学会了从单张图片推断绝对距离（"树3米，房子15米"）。这个电子眼同时看大图（全局布局）、中图（物体关系）、小图（纹理细节），三合一判断距离。3DGS拿到这个准确距离后，用高斯椭球构建3D地图，并用各向同性正则化防止高斯被拉得太长变畸形。

**具体分三步**：

1. **MViT深度预测**：输入640×640图像→构建三级金字塔（640/320/160）→每级分成16×16的patch→共享权重的ViT编码器处理每个patch→五级特征金字塔（320到20分辨率）→DPT解码器上采样→输出度量尺度逆深度图。关键：训练时混入多数据集的度量深度真值，学会直接预测"多少米"而非"相对远近"。

2. **深度先验驱动3DGS初始化与约束**：MViT预测的逆深度→反投影为3D点→初始化为各向异性高斯椭球。建图时，深度损失 $\mathcal{L}_{\text{depth}}$ 用MViT深度作为伪真值约束高斯优化，消除尺度漂移。

3. **同步跟踪-建图管线**：跟踪模块通过光度损失+深度残差优化位姿（≥50次Adam迭代/帧）；自适应关键帧选择根据IoU/位移阈值和跟踪损失动态调整插入频率；建图模块优化高斯参数+各向同性正则化抑制过度拉伸。

## 核心方法

### 系统总览
```
单目RGB输入 → MViT深度预测（度量尺度逆深度）
              ↓
        3DGS初始化（深度反投影→各向异性高斯）
              ↓
    ┌→ 跟踪（Tracking）: 光度L1+SSIM + 深度L1 → 位姿优化（Adam, ≥50 iter）
    │        ↓
    ├→ 关键帧选择（Keyframing）: IoU/位移阈值 + 自适应间隔调整
    │        ↓
    └→ 建图（Mapping）: 光度损失 + 深度损失 + 各向同性正则化 → 高斯精化
        三模块同步顺序执行，每帧更新一次
```

### 1. MViT：多尺度视觉Transformer深度预测

**三级输入金字塔**：输入图像pad到640×640→下采样到320×320和160×160。

**共享权重Patch编码**：每级用kernel=16, stride=16的卷积切分为非重叠patch→共享权重的ViT编码器处理每个patch→每个patch输出24×24特征→滑动窗口合并（25%重叠）重建全分辨率特征图。

**五级特征金字塔**：通过1×1卷积（通道对齐）、3×3卷积（空间精化）、2×2转置卷积（上采样）构建：
| Level | 分辨率 | 通道数 |
|-------|--------|--------|
| 1 | 320×320 | 256 |
| 2 | 160×160 | 512 |
| 3 | 80×80 | 1024 |
| 4 | 40×40 | 1024 |
| 5 | 20×20 | 1024 |

**双分支Transformer编码器**（受BeiT启发）：
- 局部分支：捕获细粒度细节
- 全局分支：建模长程语义依赖
- 融合函数 $\Phi$：跨尺度拼接 + 空间-语义对齐

统一多尺度特征表示（Eq. 1）：
$$\mathcal{F} = \Phi\left(\left(\mathcal{H}^{(L)}(\mathbf{E} \cdot \mathbf{x}^{(s)} + \mathbf{P}^{(s)})\right)_{s \in \mathcal{S}}\right)$$

**DPT解码器与深度重建**（Eq. 2）：五级特征先与全局上下文特征融合→逐步2×转置卷积上采样→各尺度特征经Align纠正空间错位→聚合→1×1卷积压缩为单通道逆深度图 $\hat{\mathbf{d}}^{-1}$。

$$\hat{\mathbf{d}}^{-1} = \mathbf{W}_{d} \circ \text{Upsample}_{1:1}\left(\bigoplus_{s \in \mathcal{S}} \text{Align}\left(\text{Upsample}_{t \leftarrow s}\left(\mathbf{F}^{(s)} \oplus \mathbf{F}_{g}\right)\right)\right)$$

**Zero-shot度量深度训练**：在真实+合成数据混合集上训练，监督损失包括MAE（度量真值）和尺度-位移不变损失（非度量数据）。训练后可直接从单张RGB预测绝对尺度逆深度图，无需相机内参或元数据。

### 2. 3DGS表示（Eq. 3-4）

标准3DGS参数化：$\mathcal{G} = \{(G_i(\boldsymbol{\mu}_i, \boldsymbol{\Sigma}_i, O_i))\}_{i=1}^{N}$，协方差分解 $\boldsymbol{\Sigma}_i = \mathbf{R}_i \text{diag}(\mathbf{S}_i) \mathbf{R}_i^{\top}$。

Alpha-blending渲染（Eq. 4）：
$$\mathbf{C}(p) = \sum_{i \in \mathcal{N}} \mathbf{c}_i \alpha_i \prod_{j=1}^{i-1} (1-\alpha_j), \quad \alpha_i = O_i \exp\left(-\frac{1}{2} \boldsymbol{\Delta}_i^{\top} \tilde{\boldsymbol{\Sigma}}_i^{-1} \boldsymbol{\Delta}_i\right)$$

### 3. 跟踪模块（Tracking）

损失函数（Eq. 5）：
$$\mathcal{L}_{\text{track}} = \lambda_c \left(\mathcal{L}_1(\hat{I}, I) + \mathcal{L}_{\text{SSIM}}(\hat{I}, I)\right) \odot M_{\text{rgb}} + \lambda_d \mathcal{L}_1(\hat{D}, D) \odot M_{\text{depth}}$$

- 单目模式：$\lambda_d = 0$，仅用光度损失估计位姿
- 但建图时将MViT预测深度作为伪真值 $D$ 约束几何
- 每帧≥50次Adam迭代，高斯参数冻结

### 4. 关键帧选择（Keyframing）

**几何选择标准**（Eq. 6）：
$$\text{Insert if}: \text{IoU}(\mathcal{G}_m, \mathcal{G}_n) < \theta \text{ or } \frac{L_{mn}}{\hat{D}_m} > \xi$$
$$\text{Remove if}: \text{OC}(\mathcal{G}_m, \mathcal{G}_n) < \theta - \xi$$

数据集特定阈值：TUM $\theta=0.85, \xi=0.05$；Replica $\theta=0.95, \xi=0.04$。

**自适应间隔调整**（Eq. 7）——根据跟踪损失动态调节插入频率：
$$\Delta_{\text{kf}} = \begin{cases} \max(2, \Delta_{\text{default}} - 2), & \text{if } \mathcal{L}_{\text{track}} > \omega \\ \min(3, \Delta_{\text{default}} + 1), & \text{otherwise} \end{cases}$$

跟踪损失高（场景复杂/运动剧烈）→缩小间隔→更密集的关键帧→更强几何约束。损失低→增大间隔→减少计算冗余。

### 5. 建图模块（Mapping）

建图损失（Eq. 8）：
$$\mathcal{L}_{\text{map}} = \lambda_c \mathcal{L}_{\text{color}} + \lambda_d \mathcal{L}_{\text{depth}} + \lambda_{\text{reg}} \| \mathbf{S}_h - \bar{S}_h \mathbf{1} \|_2$$

- $\mathcal{L}_{\text{color}}$ 和 $\mathcal{L}_{\text{depth}}$ 与跟踪损失同构
- **各向同性正则化项** $\| \mathbf{S}_h - \bar{S}_h \mathbf{1} \|_2$：惩罚缩放向量偏离其均值的程度，抑制高斯过度拉伸、减少伪影
- 权重：$\lambda_c=0.8, \lambda_d=0.2, \lambda_{\text{reg}}=0.05$
- 单目模式下，$D$ 来自MViT对当前关键帧的前向推理

## 实验结论

### 实验设置
- **数据集**：TUM RGB-D（含动态/运动模糊）+ Replica（合成、毫米级真值）
- **硬件**：NVIDIA RTX 4090, PyTorch
- **训练**：MViT编码器lr=1.28×10⁻⁵，解码器lr=1.28×10⁻⁴，cosine annealing + 1% warm-up，batch=128，Adam optimizer + gradient clipping norm=0.2
- **对比方法**：单目RGB — MonoGS, GO-SLAM, MGSO；RGB-D — Vox-Fusion, NICE-SLAM, Point-SLAM, GS-SLAM, SplaTAM

### 跟踪精度

**TUM-RGBD fr3**（单目模式）：
| Method | ATE RMSE [m] |
|--------|-------------|
| MonoGS | 0.0437 |
| **ViMGS-SLAM** | **0.0236**（↓46.0%）|

关键帧分析：第600帧ATE 0.68cm vs MonoGS 2.29cm；第1150帧MonoGS出现平面结构断裂而ViMGS保持准确；第2400帧ViMGS通过帧间特征传播维持时序一致性。

**急转弯鲁棒性**：两方法在急转弯时均出现显著误差波动（快速视角变化对动态物体跟踪的固有挑战），但ViMGS-SLAM的均值跟踪误差比MonoGS低**50%**——归因于时序特征聚合和遮挡感知注意力机制缓解误差传播。

在TUM fr2/desk序列（2965帧）上，轨迹误差随序列长度逐渐累积——当前里程计式设计缺乏回环检测和全局优化的共性局限。

**TUM-RGB 单目渲染**：
| Method | PSNR | SSIM | LPIPS |
|--------|------|------|-------|
| GO-SLAM | 21.26 | 0.74 | 0.33 |
| MonoGS | 20.18 | 0.72 | 0.35 |
| **ViMGS-SLAM** | **23.27** | **0.78** | **0.27** |

单目深度估计精度接近RGB-D水平——MViT架构达到接近传感器级的深度推断精度。

### 新视角渲染（Replica）

| Method | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|--------|--------|--------|---------|
| Point-SLAM | 37.91 | 0.975 | 0.126 |
| GS-SLAM | 36.67 | 0.971 | 0.072 |
| MonoGS | 36.28 | 0.969 | 0.098 |
| **ViMGS-SLAM** | **39.60** | **0.976** | **0.042** |

PSNR接近无损重建阈值（≥40 dB），LPIPS相较第二名降低66.7%。

**三个维度归因分析**：
1. **辐射精度（PSNR 39.60 dB）**：MViT层级特征保留细粒度强度变化，全局注意力抑制噪声——在视角变化和复杂几何配置下保持几何一致性
2. **结构完整性（SSIM 0.976）**：显式3DGS提供物理上有根据的几何模型，可微性质允许精确优化场景几何
3. **感知保真度（LPIPS 0.042）**：MViT层级特征聚合提供丰富上下文信息引导高斯优化，3DGS保障高效精确渲染

**定性区域分析（Replica Room1）**：
| 区域 | ViMGS-SLAM | Point-SLAM / MonoGS |
|------|-----------|---------------------|
| 布料褶皱（Region 1） | 亚厘米级层状结构保持 | 模糊、不完整 |
| 镜面边界（Region 2） | 减少材质边界伪影 | 边界伪影 |
| 部分观测区（Region 3） | 语义一致补全 | 空洞、虚假纹理 |
| 木质桌面（Region 4） | 精细纹理准确恢复 | 模糊纹理 |

### 3D高斯重建

ViMGS-SLAM生成95,156个高斯基元，MonoGS仅35,159个（+170.64%）。定性分析：ViMGS的高斯更接近各向同性圆形（各向同性正则化起效）、颜色重建更准确（MViT多尺度特征融合）、未出现MonoGS的错误浅色高斯。

### 消融实验（TUM-RGB, ATE [cm]）

| 变体 | fr1 | fr2 | fr3 | Avg |
|------|-----|-----|-----|-----|
| w/o Color Loss | 5.22 | 1.00 | 4.45 | 3.56 |
| w/o Depth Loss | 3.61 | 1.15 | 3.27 | 2.68 |
| w/o Isotropic Loss | 3.05 | 0.75 | 3.78 | 2.53 |
| **ViMGS-SLAM** | **1.73** | **0.36** | **2.36** | **1.48** |

**逐项分析**：

(1) **去除光度损失**：ATE从1.48→3.56 cm（↑2.41 cm），退化最严重。光度损失提供像素级视觉反馈用于当前帧与参考帧对齐——在光照变化和无纹理区域（深度不可靠时）尤为关键。

(2) **去除深度损失**：ATE增加**1.8倍**。深度损失提供度量尺度约束，直接消除单目SLAM固有的尺度模糊。但即使无深度损失，系统仍保留功能性的跟踪和建图能力——光度和正则化项在静态环境中可部分补偿深度缺失。

(3) **去除各向同性正则化**：ATE从1.48→2.53 cm（↑70%），与去除深度损失的退化相当。正则化项 $\| \mathbf{S}_h - \bar{S}_h \mathbf{1} \|_2$ 抑制高斯过度伸长，鼓励更紧凑、几何一致的高斯基元。定性证据：ViMGS-SLAM生成的高斯比MonoGS更接近圆形。

### 运行时

| 模式 | 总时间 | FPS | 平均建图迭代/帧 |
|------|--------|-----|---------------|
| Mono/tum/fr2 | 1325.9s | 2.7 | 19.6 |
| RGBD/tum/fr2 | 1471.9s | 2.3 | 17.7 |

渲染子系统单独：平均1130.2 FPS，峰值1440.8 FPS。总体帧率受限于跟踪的多次渲染pass和建图的迭代高斯参数更新（~95k基元）。

## 与前作的区别

| 前作 | 关键区别 |
|------|---------|
| **MonoGS** (CVPR 2024) | MonoGS无深度先验→尺度模糊+漂移；ViMGS-SLAM用MViT提供度量深度先验消除尺度漂移 |
| **WildGS-SLAM** (arxiv 2025) | 单目+不确定性感知动态过滤；ViMGS-SLAM聚焦深度先验质量提升（不专门处理动态） |
| **UP-SLAM** (ICRA 2026) | RGB-D+并行框架+概率八叉树+训练无关不确定性；ViMGS-SLAM单目+同步管线+MViT深度先验 |
| **Pseudo Depth Meets Gaussian** (arxiv 2025) | UniDepthV2预测相对深度→需尺度对齐；ViMGS-SLAM的MViT直接预测度量深度→无需尺度对齐 |
| **GO-SLAM** | 基于NeRF的隐式表示；ViMGS-SLAM用3DGS显式表示→渲染更快 |
| **MGSO** | 多传感器融合；ViMGS-SLAM仅需单目RGB |

## 局限性

1. **无回环检测**：当前为里程计式系统，长序列ATE逐渐累积。大多数3DGS-SLAM方法的共性问题
2. **无重定位**：跟踪失败后依赖重新初始化而非主动重定位
3. **同步管线瓶颈**：跟踪→关键帧→建图顺序执行，总帧率受限于建图迭代次数。未来可探索异步执行
4. **MViT推理延迟**：虽然渲染达1130 FPS，MViT深度预测的前向传播仍是每帧的必要开销
5. **静态场景假设**：未专门处理动态物体

## 关联
- 基于: [[papers/2026-05/3d-gaussian-splatting]]
- 单目SLAM同行: MonoGS (CVPR 2024), [[papers/2026-05/wildgs-slam]]（单目动态SLAM）, [[papers/2026-05/pseudo-depth-meets-gaussian]]（前馈式伪深度SLAM）
- RGB-D SLAM对比: [[papers/2026-06/up-slam]]（并行框架+概率八叉树）, [[papers/2026-05/g2-mapping]]（通用GS-SLAM）
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/slam]], [[concepts/monocular-depth-estimation]], [[concepts/vision-transformer]], [[concepts/isotropic-regularization]], [[concepts/alpha-compositing]], [[concepts/projection-transform]], [[concepts/adaptive-density-control]]
