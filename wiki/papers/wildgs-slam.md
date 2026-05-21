---
title: "WildGS-SLAM: Monocular Gaussian Splatting SLAM in Dynamic Environments"
authors: Jianhao Zheng, Zihan Zhu, Valentin Bieri, Marc Pollefeys, Songyou Peng, Iro Armeni
year: 2025
venue: arxiv
tags: [paper, extension, slam, dynamic]
status: done
---

## 一句话总结
提出WildGS-SLAM——首个仅用单目RGB即可在动态环境中鲁棒运行的Gaussian SLAM系统。核心创新：用DINOv2（3D-aware微调）提取图像特征 → 浅层MLP在线预测逐像素"不确定性图" → 同时指导跟踪（不确定性加权DBA，让动态物体不影响位姿估计）和建图（不确定性加权渲染损失，让动态区域不影响场景重建）。无需深度传感器、无需语义分割、无需预定义物体类别。

## 通俗理解（Plain Language）

### 这个问题为什么难？
传统SLAM假设"世界是静止的"——如果有人在镜头前走过，系统会误以为"是相机自己在动"，导致跟踪崩掉。已有的解决方案各有软肋：
- 用深度相机看"深度残差"→ 单目相机没深度
- 用YOLO/Mask R-CNN识别"人"→ 不认识的东西（机器人狗、篮球、雨伞）就漏了
- 用光流检测运动 → 白墙上没纹理就失效了

### WildGS-SLAM 怎么做？
它给每个像素分配一个"可信度分数"（不确定性 $\beta$）。核心直觉是：

> 如果一个像素区域今天看是这样、明天看是那样（因为有个动态物体来回移动），那它就是"不可信的"——跟踪和建图时自动忽略它。

**具体三步走**：

1. **"谁不可信？"——不确定性预测器**：一个预训练的DINOv2（看过几亿张图片的视觉基础模型）提取每帧的语义特征，一个在线训练的浅层MLP把特征翻译成"不确定性热力图"。MLP随视频流边看边学，不需要任何人工标注。

2. **"忽略干扰物做跟踪"——不确定性加权DBA**：传统跟踪把所有像素一视同仁。WildGS-SLAM把不确定性作为权重——动态物体上的像素对跟踪优化的贡献被大幅削弱（除以$\beta^2$）。同时用Metric3D v2的单目深度估计作为辅助锚点，在MLP还没训练好时稳住跟踪。

3. **"只重建静态世界"——不确定性加权建图**：渲染损失同样被不确定性加权。动态区域高不确定性 → 低权重 → 高斯优化不理会它们 → 3D高斯地图自动只包含静态场景。

**类比**：一个画家在繁华广场上写生。他不是把所有看到的东西都画进去（那样画里全是鬼影），而是先快速判断"哪些东西一直在变？"，然后画的时候自动忽略那些区域，只画稳定的建筑背景。

## 解决的问题
现有SLAM在动态环境中失效的原因及已有方法局限：

| 方法类型 | 代表工作 | 为什么不够 |
|---------|---------|-----------|
| 静态假设SLAM | MonoGS, Splat-SLAM, DROID-SLAM | 动态物体破坏光度一致性→严重漂移 |
| 语义分割法 | DG-SLAM, DDN-SLAM, DynaSLAM | 依赖预定义类别，不认识ANYmal机器人/雨伞等 |
| 几何残差法 | ReFusion, StaticFusion | 需要RGB-D深度，单目不可用 |
| 光流/运动法 | RoDyn-SLAM, DynaMoN | 纹理弱区域失效；DynaMoN需离线精化 |
| 稀疏视图去干扰 | NeRF On-the-go, WildGaussians | 假设已知位姿，不支持SLAM序列跟踪 |

**核心挑战**：仅用单目RGB，不依赖任何类别先验，如何在线识别并排除任意动态物体？

## 核心方法

### 系统总览
```
RGB序列输入 → ┬→ 不确定性预测 (DINOv2 + MLP, 在线训练)
              ├→ 跟踪 (不确定性加权DBA + Metric3D深度先验 + 回环/全局BA)
              └→ 建图 (不确定性加权3DGS优化, 独立于MLP)
```

**两阶段初始化**（Supplementary Sec. 7.1）：前12个关键帧不使用不确定性权重跑DBA得到粗位姿→用粗位姿初始化高斯地图并训练MLP→再用不确定性权重激活的DBA精化位姿。

### 1. 不确定性预测（$\S$3.2）— 系统核心

**特征提取**：预训练DINOv2（3D-aware微调版 [Yue et al. ECCV 2024]）提取图像特征 $F_i = \mathcal{F}(I_i)$，特征图分辨率 = 输入1/14。选择3D-aware微调版（而非原版DINOv2）的原因是它注入了3D几何意识，特征对多视图一致性更敏感。

**在线训练MLP**：浅层MLP $\mathcal{P}$ 将特征解码为不确定性图 $\beta_i = \mathcal{P}(F_i)$，双线性上采样回原分辨率。MLP随输入帧增量训练——每来一个新关键帧就更新一次，动态适应场景。

**不确定性损失**（借鉴NeRF On-the-go [Ren et al. CVPR 2024] + 自定义深度项）：

$$\mathcal{L}_{\text{uncer}} = \underbrace{\frac{\mathcal{L}_{\text{SSIM}}' + \lambda_1 \mathcal{L}_{\text{depth}}}{\beta_i^2}}_{\text{数据项}} + \underbrace{\lambda_2 \mathcal{L}_{\text{reg\_V}} + \lambda_3 \mathcal{L}_{\text{reg\_U}}}_{\text{正则化}}$$

其中：
- $\mathcal{L}_{\text{depth}} = |\hat{D}_i - \tilde{D}_i|_1$：渲染深度 vs Metric3D v2预测深度的L1——**作者发现这是关键**，深度信号显著帮助MLP区分"静态几何"和"运动干扰物"
- $\mathcal{L}_{\text{SSIM}}'$：修改的SSIM损失（来自NeRF On-the-go），衡量渲染颜色一致性
- $\mathcal{L}_{\text{reg\_V}}$：最小化高相似度特征的不确定性方差（相似区域应该有相似的不确定性）
- $\mathcal{L}_{\text{reg\_U}} = \log \beta_i$：防止 $\beta_i$ 无限增大

**关键设计决策**：不确定性MLP $\mathcal{P}$ 与3D高斯地图 $\mathcal{G}$ **独立优化**——$\mathcal{L}_{\text{uncer}}$ 到 $\mathcal{G}$ 的梯度被detach，$\mathcal{L}_{\text{render}}$ 到 $\mathcal{P}$ 的梯度也被detach。NeRF On-the-go已证明混在一起优化会导致两者互相干扰。

**在线预测可视化**（Supplementary Fig. 11）：当雨伞进入场景时（frame 215），仅用前80帧训练的MLP不认识雨伞→将其标记为高不确定性。到frame 451时MLP已稳定，不确定性图准确识别所有动态区域。

### 2. 不确定性感知跟踪（$\S$3.3）

基于DROID-SLAM [Teed & Deng, NeurIPS 2021]的DBA框架，加入深度和不确定性引导。DROID-SLAM使用预训练的循环光流模型 + DBA层联合优化关键帧位姿和视差。

**不确定性加权DBA**：

$$\arg\min_{\omega, d} \sum_{(i,j)\in E} \underbrace{\left\|\tilde{p}_{ij} - \Pi_c\left(\omega_j^{-1}\omega_i \Pi_c^{-1}(p_i, d_i)\right)\right\|_{\Sigma_{ij}/\beta_i^2}^2}_{\text{不确定性加权光流重投影误差}} + \lambda_4 \sum_{i\in V}\underbrace{\left\|M_i\left(d_i - 1/\tilde{D}_i\right)\right\|^2}_{\text{视差正则化}}$$

- **第一项**：标准DBA的光流重投影误差，但协方差矩阵被不确定性缩放 $\Sigma_{ij}/\beta_i^2$。动态物体上的像素 $\beta_i$ 很大 → 权重极小 → 不影响位姿优化
- **第二项**：鼓励估计视差接近Metric3D v2单目深度。在MLP未收敛时（跟踪早期）提供关键稳定性

**视差正则化掩码 $M_i$**（Supplementary Eq. 8）：通过多视图深度一致性计算——将相邻帧的深度投影到当前帧，比较深度值的一致性 + DINOv2特征余弦相似度。仅当某像素在多个视图中深度一致时才激活正则化，避免在不可靠区域强制约束。

**帧图管理**：每8帧强制插入新关键帧（独立于DROID-SLAM原版基于平均光流的准则）。回环检测和全局BA继承自Splat-SLAM [Sandström et al. 2024]。

**最终全局BA**：处理完所有帧后进行，保留DBA第一项（不确定性加权光流误差），但去掉视差正则化项——此时多视图信息已足够，不确定性图也已收敛。

### 3. 不确定性感知建图（$\S$3.4）

**地图扩展**：新关键帧插入后，用Metric3D v2深度作为代理深度（proxy depth），遵循MonoGS的RGB-D扩展策略。若回环/全局BA更新了历史位姿，主动变形高斯地图以保持几何一致性（同Splat-SLAM）。

**不确定性加权渲染损失**：

$$\mathcal{L}_{\text{render}} = \frac{\lambda_5 \mathcal{L}_{\text{color}} + \lambda_6 \mathcal{L}_{\text{depth}}}{\beta^2} + \lambda_7 \mathcal{L}_{\text{iso}}$$

$$\mathcal{L}_{\text{color}} = (1-\lambda_{\text{ssim}})\|\hat{I} - I\|_1 + \lambda_{\text{ssim}} \mathcal{L}_{\text{ssim}}$$

- 不确定性 $\beta$ 出现在**分母**——动态区域高不确定性 → 损失项趋近于0 → 高斯优化不受干扰
- $\mathcal{L}_{\text{iso}}$：各向同性正则化（来自MonoGS），约束稀疏观测区的高斯不产生过度拉长的"针状"伪影
- 仅对不透明度 > 阈值的有效像素计算损失

**局部窗口采样**：维护关键帧共视窗口。每帧 ≥ 50% 概率均匀采样（保证覆盖），其余帧共享剩余概率。

**最终地图精化**（Supplementary）：全局BA后，固定所有关键帧位姿，用全部关键帧联合优化 $\mathcal{G}$ 和 $\mathcal{P}$。

**非关键帧位姿恢复**：运行motion-only BA + L1 RGB重渲染损失（均被不确定性加权）。

### 4. 快速版本（Supplementary）

跳过4项低影响操作：(i) 不算视差正则化掩码 (ii) 每5帧才优化一次地图和MLP (iii) 跳过非关键帧重渲染精化 (iv) 最终地图精化减至3000迭代。速度大幅提升，精度仅微降（Wild-SLAM ATE 0.46→0.48 cm）。

## 与前作的区别
| 前作 | 关键区别 |
|------|---------|
| **MonoGS** (CVPR 2024) | 假设静态场景→动态中崩溃；WildGS-SLAM用不确定性处理动态 |
| **Splat-SLAM** (2024) | 有回环/全局BA但假设静态；WildGS-SLAM保留回环能力+增加动态鲁棒性 |
| **DG-SLAM** (NeurIPS 2024) | 用YOLO语义分割识别动态物体→不认识非人物体；WildGS-SLAM纯几何无类别依赖 |
| **DynaMoN** (2023) | 先粗跟踪再离线精化→不能实时；WildGS-SLAM在线流式处理 |
| **NeRF On-the-go** (CVPR 2024) | 不确定性感知思想来源，但仅处理稀疏视图+已知位姿；WildGS-SLAM扩展到序列SLAM |
| **ReFusion / DynaSLAM** | 需要RGB-D深度传感器；WildGS-SLAM仅需单目RGB |
| **MonST3R** (2024) | 前馈式短序列几何估计+点云输出；WildGS-SLAM支持长序列+视角合成 |

## 实验结论

### 数据集
| 数据集 | 内容 | 用途 |
|--------|------|------|
| **Wild-SLAM MoCap** (自采) | 10序列，OptiTrack真值，含ANYmal机器人/篮球/人群/球拍/石头/雨伞等 | 定量跟踪+渲染 |
| **Wild-SLAM iPhone** (自采) | 7序列非摆拍RGB（购物/街头/停车场/钢琴/美术馆） | 定性评估 |
| **Bonn RGB-D Dynamic** | 8序列（气球/人群/行人/移动物体） | 定量跟踪+渲染 |
| **TUM RGB-D** | 高动态序列（f3/ws, wx, wr, whs）+ 静态序列 | 定量跟踪 |

**Wild-SLAM MoCap数据采集**（Supplementary Sec. 6）：Intel RealSense D455 @ 720×1280 30fps，OptiTrack 32×PrimeX-13相机 @ 120fps。同步方案：用iPhone手电筒闪烁产生时间戳对应（平均标准差5.25ms，远小于帧间隔33.33ms）。标定方案：标定板+4个反光标记球+chordal L2旋转平均，旋转偏差0.44°、平移偏差0.24cm。

### 跟踪精度（ATE RMSE [cm]）
| 数据集 | WildGS-SLAM | Splat-SLAM | MonoGS | DynaMoN | DROID-SLAM | DDN-SLAM |
|--------|-------------|------------|--------|---------|------------|----------|
| Wild-SLAM MoCap | **2.40** | 47.99 | F | — | 16.17 | — |
| Bonn Dynamic | **2.31** | — | 22.8 | 4.02 | 4.91 | 2.91 |
| TUM Dynamic | **1.63** | 2.43 | 21.05 | 2.18 | 2.25 | 2.15 |
| TUM Static | **1.07** | 1.13 | 4.0 | — | 1.7 | — |

在Wild-SLAM MoCap上**大幅领先所有方法（包括使用RGB-D的方法）**。唯一的例外是Person序列（单人简单运动→DynaSLAM语义分割足够）。在TUM静态序列上与SOTA持平——证明不确定性模块**不会在静态场景中产生副作用**。

### 渲染质量
| 评估 | WildGS-SLAM | Splat-SLAM | 提升 |
|------|------------|------------|------|
| PSNR (Wild-SLAM NVS) | **20.59** | 17.23 | +3.36 dB |
| SSIM | **0.783** | 0.699 | +0.084 |
| LPIPS | **0.209** | 0.346 | -0.137 |

定性：成功去除ANYmal机器人、篮球、人群、雨伞等各类动态物体，渲染无伪影。不确定性图甚至能为动态物体的**阴影**分配更高不确定性。在TUM上，MonoGS和Splat-SLAM产生模糊和漂浮伪影，ReFusion有ghosting，DynaSLAM有"黑洞"。

### 消融实验
| 变体 | Wild-SLAM | Bonn | TUM | 分析 |
|------|-----------|------|-----|------|
| **完整WildGS-SLAM** | **0.46** | **2.31** | **1.63** | |
| 无不确定性掩码 | 3.89 | 5.11 | 1.91 | 不确定性是核心，移除后退化显著 |
| 无L1深度损失(Eq.4) | 0.50 | 2.37 | 1.83 | 深度信号帮助MLP学习，但影响小于不确定性本身 |
| YOLOv8+SAM替代 | 3.06 | 2.37 | 1.65 | 类别先验在Wild-SLAM上不如不确定性（含非人物体） |
| 无视差正则化(Eq.5) | **10.97** | F | 2.9 | **最关键的稳定器**——移除后Wild-SLAM错误暴增24倍 |
| MonST3R动态掩码替代 | 2.60 | 2.58 | 1.80 | 不如不确定性感知，但优于YOLO方案 |

**视差正则化消融**（Supplementary Table 11）：在最终全局BA中移除视差正则化→Before BA差异巨大（证明单目深度预测的多视图不一致性），但After BA结果改善（多视图信息已足够）。在实践中，只在在线跟踪阶段使用视差正则化。

**深度估计器和DINOv2变体消融**（Supplementary Table 13）：
- Metric3D v2优于DPTv2作为深度估计器
- 3D-aware微调DINOv2优于原版DINOv2（尤其在Wild-SLAM上新视角PSNR +0.02，ATE -0.01）
- 最佳组合：Metric3D v2 + 3D-aware finetuned DINOv2

### 运行时分析（Supplementary Table 9）
| 方法 | Wild-SLAM FPS | Bonn FPS |
|------|-------------|----------|
| MonoGS | 2.41 | 2.98 |
| Splat-SLAM | 2.44 | 1.99 |
| WildGS-SLAM (full) | 0.49 | 0.50 |
| **WildGS-SLAM (fast)** | **1.96** | **2.13** |

Fast版本速度接近MonoGS/Splat-SLAM，精度仅微降（ATE 0.46→0.48），仍远超所有基线。

### 限制
1. **观测不足时难以识别干扰物**：不确定性预测器依赖多视图一致性——如果某个区域只有少数几帧看到，无法判断它是不是动态的。引入运动先验（如光流）可以改进
2. **在线训练冷启动**：初始阶段MLP未训练，依赖视差正则化维持跟踪（但消融证明这已足够鲁棒）
3. **处理速度**：完整版<1 FPS，比静态SLAM慢（因额外的不确定性预测+加权计算）。Fast版本恢复到~2 FPS

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 不确定性感知思想来源: NeRF On-the-go (Ren et al. CVPR 2024), WildGaussians (Kulhanek et al. NeurIPS 2024)
- 跟踪框架: DROID-SLAM (Teed & Deng, NeurIPS 2021)
- 地图框架: MonoGS (Matsuki et al. CVPR 2024), Splat-SLAM (Sandström et al. 2024)
- 相关SLAM: [[papers/gs-livo]], [[papers/g2-mapping]]
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/slam]], [[concepts/uncertainty-aware-mapping]], [[concepts/alpha-compositing]], [[concepts/projection-transform]]
