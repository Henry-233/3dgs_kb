---
title: "LangGS-SLAM: Real-Time Language-Feature Gaussian Splatting SLAM"
authors: Seongbo Ha, Sibaek Lee, Kyungsu Kang, Joonyeol Choi, Seungjun Tak, Hyeonwoo Yu
year: 2026
venue: arxiv
tags: [paper, extension, slam, semantics]
status: done
---

## 一句话总结
提出首个在线实时（15 FPS）语言特征Gaussian SLAM系统——用Top-K渲染替代alpha-blending做高维特征渲染（避免语义歧义），多标准地图管理控制内存（高斯数削减76-90%），混合场优化解耦几何与语义更新频率，在几何精度超越纯几何SOTA的同时达到与离线方法相当的语义保真度。

## 解决的问题

将语言特征嵌入3DGS是让SLAM支持开放词汇查询的关键，但现有方案有三个根本瓶颈：

| 瓶颈 | 现有方法的问题 |
|------|-------------|
| **渲染瓶颈** | alpha-blending对高维特征（512D CLIP/LSeg）渲染极慢——每个像素需累加所有光线高斯的高维向量；且alpha-blending混合来自多个表面的语义，产生无意义的"语义熵" |
| **内存爆炸** | 每高斯存储512维特征，百万高斯直接爆显存。LangSplat用逐场景自编码器压缩→损失精度且额外训练开销 |
| **优化低效** | 几何场（高频结构）和语义场（平滑、依赖稳定几何）以相同频率更新→冗余计算且收敛慢 |

**核心问题**：能否构建一个在线SLAM系统，同时保持几何精度、语义保真度和实时性能？

## 核心方法

### 系统概览 (Fig. 2)

基于GS-ICP SLAM（同组作者，ECCV 2024）的几何骨干：
- **跟踪线程**：G-ICP对齐源高斯与地图高斯估计位姿；低重叠时触发关键帧
- **建图线程**：Top-K渲染高维特征 → 多标准地图管理 → 混合场优化

**场景表示**：每个3D高斯含几何属性（$\mu$, $\Sigma$, $\alpha$, $c$）+ VLM特征向量 $f$（无SH系数以加速收敛）

### 1. Top-K Rendering — 解决高维特征渲染瓶颈 (Sec 3.2)

**Alpha-blending的两大致命问题**（Fig. 3）：
1. **计算量**：像素 $\mathbf{p}$ 的512维特征渲染需沿光线累加所有高斯 → $\mathcal{O}(N \cdot D)$
2. **语义歧义**：混合多个表面（前景+背景）的语义向量→不可解释的"平均语义"

**Top-K方案**（Eq. 2-4）：

**选择**（Eq. 2）：取alpha合成中贡献权重最高的K个高斯：
$$\mathcal{K} = \{\pi(1), ..., \pi(K)\} \quad \text{s.t.} \quad w_{\pi(1)} \ge w_{\pi(2)} \ge \dots \ge w_{\pi(N)}$$

**重归一化**（Eq. 3）——因为语义特征是单位方向向量（LSeg），权重需归一化：
$$w'_k = \frac{w_k}{\sum_{j \in \mathcal{K}} w_j}$$

**渲染**（Eq. 4）：
$$\mathbf{F}(\mathbf{p}) = \sum_{k \in \mathcal{K}} w'_k \mathbf{f}_k$$

**CUDA实现**：颜色/深度渲染kernel记录Top-K高斯的索引和权重→特征渲染kernel复用（固定K→确定性线程分配+通道并行累加）。K=3为最优（Tab. 4：渲染FPS 122，mIoU 0.673；K=1对噪声敏感，K=10近似alpha-blending重引入歧义）。

> 注意：几何渲染仍用alpha-blending（保证稳定收敛），仅语义渲染用Top-K——双渲染策略。

### 2. 多标准地图管理 — 解决内存爆炸 (Sec 3.3)

#### 语义-几何一致性剪枝

仅基于Top-K参与度剪枝会误删"语义参与少但对几何关键"的高斯。两阶段概率剪枝：

**候选集**：Top-K参与度低的高斯 $\mathcal{G}_{\text{prune}}$

**几何重要性评分**（Eq. 5）——高斯的alpha-blending最大贡献值：
$$S_i = \max_{k \in \mathcal{K}, \mathbf{r} \in \mathcal{R}_k} w_i(\mathbf{r})$$

**概率存活**（Eq. 6）——归一化评分作为存活概率，加权采样保留预设比例：
$$P_{\text{survive}}(\mathcal{G}_i) = \frac{S_i}{\sum_{j \in \mathcal{G}_{\text{prune}}} S_j}$$

每500迭代执行一次，从候选集保留50%。

#### 冗余感知高斯插入

在添加新高斯前，复用G-ICP跟踪已计算的对应点距离——若源高斯与最近地图高斯距离小于阈值，该区域已被充分表示，跳过插入。零额外计算开销。

**效果**（Tab. 6）：
- Replica：高斯数从912k→215k（-76.3%），PSNR仅微降
- TUM-RGBD：高斯数从971k→91k（-90.6%），PSNR反升（剪枝去除了噪声深度产生的floating伪影）
- 无管理 → OOM（>24GB）；有管理 → 4.4-8.5GB

**新视图效果**（Tab. 7）：剪枝后新视图PSNR和mIoU同时提升——说明被剪的高斯既是语义伪影也是几何floater。

### 3. 混合场优化 — 解决优化低效 (Sec 3.4)

**总损失**（Eq. 7）：
$$\mathcal{L}_{\text{map}} = \lambda_{\text{geo}} \mathcal{L}_{\text{geo}} + \lambda_{\text{feat}} \mathcal{L}_{\text{feat}}$$

**几何损失**（Eq. 8）：
$$\mathcal{L}_{\text{geo}} = (1 - \lambda_1)\mathcal{L}_1(\mathbf{C}, \mathbf{C}_{gt}) + \lambda_1\mathcal{L}_1(\mathbf{C}, \mathbf{C}_{gt}) + \lambda_2\mathcal{L}_1(D, D_{gt})$$

**语义损失**（Eq. 9）——Top-K渲染特征与GT LSeg特征图的L1：
$$\mathcal{L}_{\text{feat}} = \mathcal{L}_1(\mathbf{F}, \mathbf{F}_{gt})$$

**关键策略**：几何场（高频结构）更新更频繁 → 先稳定几何基础；语义场（光滑、依赖几何）在稳定几何上低频更新。这消除了几何未收敛时语义的无效学习。

**消融验证**（Tab. 5）：在TUM-RGBD（噪声大、几何难收敛）上混合优化显著提升语义mIoU；在Replica（高质量数据、几何收敛快）上混合优化与同步优化无显著语义差异→证明了"先稳定几何、再优化语义"的因果关系。

## 与前作的区别

| 前作 | 关键区别 |
|------|---------|
| **LangSplat** (CVPR 2024) | LangSplat离线重建+逐场景自编码器压缩→<1 FPS；LangGS-SLAM在线RGB-D SLAM+无压缩原始特征+15 FPS |
| **Feature3DGS** (CVPR 2024) | Feature3DGS离线+COLMAP位姿+alpha-blending渲染512维特征→0.3 FPS；LangGS-SLAM在线+Top-K渲染+概率剪枝→50×快 |
| **Online Language Splatting** (arxiv 2025) | 同类在线语言场工作，但<1 FPS且仅优化几何参数不更新特征；LangGS-SLAM直接优化特征场 |
| **SplaTAM** (CVPR 2024) | 纯几何SLAM；LangGS-SLAM在几何精度超越SplaTAM的同时额外重建语义场 |
| **GS-ICP SLAM** (ECCV 2024) | LangGS-SLAM的几何骨干（同组作者）；扩展为语义+几何双场系统 |
| **SGS-SLAM / SemGauss-SLAM** | 封闭集语义标签；LangGS-SLAM用VLM特征→开放词汇查询 |

## 实验结论

### 跟踪与几何精度（Tab. 1）

| 方法 | Replica ATE | Replica PSNR | TUM PSNR | 系统FPS |
|------|------------|-------------|---------|---------|
| Point-SLAM | 0.471 | 35.56 | 21.33 | 0.42 |
| SplaTAM | 0.367 | 34.19 | 23.53 | 1.18 |
| MonoGS | 0.318 | 35.34 | 18.07 | 0.68 |
| **LangGS-SLAM** | **0.213** | **35.92** | **23.78** | **15** |

同时优化几何+语义双场的LangGS-SLAM在几何精度上超越所有纯几何SOTA。

### 语义保真度（Tab. 2 — Replica）

| 方法 | 类型 | mIoU | Acc | FPS |
|------|------|------|-----|-----|
| LeRF | 离线 | 0.277 | 0.618 | 5.4 |
| LangSplat | 离线 | 0.263 | 0.614 | 0.86 |
| Feature3DGS-512D | 离线 | **0.671** | **0.893** | 0.30 |
| Feature3DGS-128D | 离线 | 0.660 | 0.890 | 1.43 |
| **LangGS-SLAM** | **在线** | **0.673** | **0.883** | **15** |

mIoU超越Feature3DGS-512D（0.673 vs 0.671），FPS快50倍。

**TUM-RGBD**（Tab. 3）：mIoU 0.642 vs Feature3DGS-512D的0.633。真实噪声数据上鲁棒性显著优于离线方法。

### 消融实验

**Top-K的K值**（Tab. 4）：K=1几何最佳（PSNR 34.94）但语义受噪声影响（mIoU 0.667）；K=10近似alpha-blending重引入歧义；K=3为最优平衡（几何34.52 + 语义0.673）

**混合优化**（Tab. 5）：TUM-RGBD噪声数据上混合优化显著提升语义mIoU（0.578→0.642）→实验证明"先稳定几何→再优化语义"的因果链

**地图管理**（Tab. 6）：无管理OOM；管理后高斯数-90.6%（TUM）且PSNR反升→剪枝去除深度噪声引入的floating伪影

**新视图一致性剪枝**（Tab. 7）：剪枝后几何PSNR和语义mIoU同时提升→被剪高斯同时是几何floater和语义伪影

## 局限性

1. **表面假设**：方法假设高斯良好贴合表面，Top-K选择依赖表面精度。未来可集成2DGS等几何保真方法
2. **深度传感器依赖**：当前为RGB-D系统，未扩展到单目（需深度做G-ICP跟踪和初始化）
3. **LSeg特征固有限制**：语义质量受限于LSeg的视觉-语言对齐能力（类似于CLIP的细粒度限制）
4. **无回环检测**：当前基线无回环/全局BA

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 几何骨干: GS-ICP SLAM (Ha et al., ECCV 2024)
- 语义范式: [[papers/langsplat]]（语言特征嵌入高斯的范式来源）, Feature3DGS (Zhou et al., CVPR 2024)
- 相关SLAM: [[papers/gs-livo]], [[papers/g2-mapping]], [[papers/wildgs-slam]], [[papers/pseudo-depth-meets-gaussian]]
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/3d-language-field]], [[concepts/slam]], [[concepts/alpha-compositing]], [[concepts/top-k-rendering]], [[concepts/hybrid-field-optimization]], [[concepts/clip]]
