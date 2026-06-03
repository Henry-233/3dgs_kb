---
title: "UP-SLAM: Adaptively Structured Gaussian SLAM with Uncertainty Prediction in Dynamic Environments"
authors: Wancai Zheng, Linlin Ou, Jiajie He, Libo Zhou, Xinyi Yu, Yan Wei
year: 2025
venue: ICRA 2026
tags: [paper, application, slam, dynamic, real-time]
status: done
---

## 一句话总结
UP-SLAM 是面向动态环境的实时 RGB-D SLAM 系统。核心贡献：(1) 并行框架将跟踪与建图解耦，12 FPS实时定位；(2) 概率八叉树（Probabilistic Octree）自适应管理锚点（anchor），贝叶斯更新自动决定初始化/剪枝，无需手动阈值；(3) 训练无关的多模态不确定性估计器，融合颜色残差+深度残差+DINO特征余弦距离，实现开放集动态物体过滤；(4) DINO特征场通过低维→高维MLP蒸馏到3DGS中，增强不确定性预测鲁棒性；(5) 时间编码器用正弦位置编码嵌入帧间时序信息到MLP，提升渲染质量。在定位精度（提升59.8%）和渲染质量（PSNR +5.47 dB）上均超越SOTA，模型大小仅7.01 MB。

## 通俗理解（Plain Language）

### 这个问题为什么难？
现有Gaussian SLAM系统的两大痛点：
- **顺序优化瓶颈**：跟踪和建图串行执行——跟踪完一帧才能建图、建完图才能跟踪下一帧。动态调整或重置地图时，跟踪被迫等待，无法实现真正实时
- **动态物体敏感**：现有动态SLAM方法要么依赖语义分割（不认识非人物体），要么需要离线训练不确定性模型（冷启动困难），要么仅适用单目（RGB-D的深度信息未被充分利用）

### UP-SLAM 怎么做？

**类比**：想象两个人合作完成一项任务——一个人专门负责定位（我在哪？），另一个人专门负责画地图。两人并行工作，互不阻塞。定位的人有一个快速判断机制：如果某个区域渲染结果和传感器观测不一致（颜色差很多、深度差很多、DINO特征不像），自动忽略它。画地图的人用一棵带概率的智能树来组织空间——树根据观测历史自动生长和修剪。

**具体五步走**：

1. **并行框架（Parallel Tracking & Mapping）**：跟踪线程独立运行ORB-SLAM3的特征法定位，建图线程维护3D高斯地图。关键帧通过共享队列传递，两线程异步通信、互不阻塞。

2. **概率八叉树（Probabilistic Octree）**：用贝叶斯更新管理锚点（anchor）的空间分布——新观测到区域→概率上升→触发高斯初始化；长期未观测→概率衰减→触发剪枝。完全替代3DGS原版的手动梯度阈值式ADC。

3. **训练无关的不确定性估计器**：在跟踪线程中，利用建图线程传来的3DGS渲染结果，计算多模态残差（颜色L1 + 深度L1 + DINO特征余弦距离），通过优化目标函数直接求解逐像素不确定性图，无需任何预训练网络。

4. **DINO特征场**：在3D高斯锚点上附加低维特征向量（$N_l=16$），通过浅层MLP（卷积→ReLU→卷积）映射到高维DINO特征空间（$N_h$维），在3DGS框架中渲染后与DINOv2提取的特征做余弦相似度监督。

5. **时间编码器**：用正弦位置编码 $\mathbf{t} = \{\sin(t), \cos(t)\}$ 将帧索引嵌入所有MLP（颜色、不透明度、旋转、缩放、特征），提升动态环境下的渲染质量。

## 核心方法

### 系统总览
```
RGB-D输入 → ┬→ 跟踪线程 (Tracking): ORB-SLAM3特征法 + 不确定性估计 + 位姿优化
            ├→ 建图线程 (Mapping): 概率八叉树锚点管理 + 3DGS优化 + DINO特征蒸馏
            └→ 共享: 多模态残差 + 关键帧队列 + 不确定性掩码
        两线程并行运行，通过共享地图状态和残差反馈异步通信
```

### 0. 预备知识：3DGS渲染

场景表示为一组各向异性高斯椭球：
$$G = \{G_i : (\mu_i, o_i, c_i, \Sigma_i) \mid i = 1, ..., N\}$$

协方差分解：$\Sigma_i = RSS^T R^T$，使用EWA投影 $\Sigma' = J T_{wc}^{-1} \Sigma T_{wc}^{-T} J^T$。

Alpha-blending渲染颜色和深度：
$$\{\tilde{C}, \tilde{D}\} = \sum_{i=1}^N \{c_i, z_i\} \alpha_i \prod_{j=1}^{i-1} (1-\alpha_j)$$

几何监督损失：
$$\mathcal{L}_g = \lambda_1 \left(\frac{\|\tilde{C} - C\|_2}{2} + (1-\gamma)(1-\text{SSIM}(\tilde{C}, C))\right) + \lambda_2 \frac{\|\tilde{D} - D\|_2}{2}$$

### 1. 并行跟踪与建图框架

传统Gaussian SLAM（MonoGS、Splat-SLAM、WildGS-SLAM）采用**顺序流水线**：跟踪→建图→跟踪→建图。UP-SLAM将两者放入独立线程：

- **跟踪线程**：基于ORB-SLAM3的鲁棒特征法定位，接收传感器帧→提取关键帧→利用建图线程传来的多模态残差计算不确定性→滤除动态特征点→估计位姿→将关键帧推入共享队列
- **建图线程**：从共享队列取关键帧→更新概率八叉树锚点→优化3D高斯属性和DINO特征→渲染当前帧用于残差计算→同时优化不确定性MLP精化运动掩码
- 两线程通过共享关键帧队列和渲染残差异步通信

### 2. 概率八叉树（Probabilistic Octree）— 自适应结构化3DGS

**动机**：3DGS SLAM需要快速识别欠重建区域并初始化新高斯，但手动阈值策略在动态环境中不可靠——阈值不当导致显存爆炸或重建不完整。

**核心思想**：从每个锚点特征 $\hat{f}_v$ 以及相机与锚点的相对方向 $\delta_{vc}$ 和距离 $d_{vc}$，通过MLP解码出 $k$ 个高斯属性。锚点配备概率属性——概率值反映该锚点处的运动程度。

**贝叶斯更新公式**（来自OctoMap [Hornung et al. 2013]）：
$$P(n \mid z_{1:t}) = \left[1 + \frac{1 - P(n \mid z_t)}{P(n \mid z_t)} \cdot \frac{1 - P(n \mid z_{1:t-1})}{P(n \mid z_{1:t-1})} \cdot \frac{P(n)}{1 - P(n)}\right]^{-1}$$

- $P(n)$：先验概率
- $P(n \mid z_t)$：给定当前观测 $z_t$ 时锚点 $n$ 被占用的概率
- $P(n \mid z_{1:t-1})$：基于历史观测的递归估计

**工作机制**：
- 新观测到该区域 → 概率上升 → 触发高斯初始化
- 长期未观测 → 概率衰减 → 触发高斯剪枝（删除动态物体产生的冗余锚点）
- 概率模型天然处理噪声和遮挡

**优势**：无需手动设置梯度阈值；模型大小从22.92 MB降至7.01 MB；逆残差反馈增强跟踪精度。

### 3. 训练无关的不确定性估计

**与WildGS-SLAM的关键区别**：WildGS-SLAM用预训练DINOv2 + 在线训练MLP预测不确定性；UP-SLAM完全无需训练，利用3DGS快速渲染能力直接优化不确定性图。

**多模态残差构建**（Eq. 6）：
$$R = \mathbb{1}(\tilde{T} < 0.1) \left(t_1 \|\tilde{C} - C\|_1 + t_2 \|\tilde{D} - (D \circledast B)\|_1 + t_3 \left\|1 - \frac{F \cdot \hat{F}}{\|F\|_2 \|\hat{F}\|_2}\right\|_2\right)$$

其中：
- $\tilde{T}$：累积透射率，用作可见性掩码（过滤低不透明度区域）
- $B$：3×3 box filter，对深度做卷积平滑
- $F$：DINOv2提取的视觉特征（双线性上采样到图像尺寸）
- $\hat{F}$：渲染的高维视觉特征
- $\{t_1, t_2, t_3\} = \{0.25, 0.7, 0.1\}$：残差权重

**跟踪中的不确定性优化**（Eq. 5, 15）：

不确定性模型基于贝叶斯学习框架——预测高斯分布而非单点值。对每个像素，损失为负对数似然：
$$\mathcal{L}_u = \frac{R}{2\sigma^2} + \lambda_3 \log \sigma$$

第二项 $\log \sigma$ 为对数配分函数，防止平凡解 $\sigma = \infty$。

在跟踪线程中，通过优化以下目标函数实时求解不确定性图 $\sigma$：
$$\Phi(\sigma) = \min_{\sigma} \frac{1}{HW} \sum_{i=1}^{H} \sum_{j=1}^{W} \left[\frac{R_{ij}}{2\sigma^2} + \log \sigma\right]$$

不确定性图阈值化生成运动掩码 $M = (2\sigma^2 > 1)$，用于过滤动态关键点。

**初始化增强**：在初始化阶段，为增强掩码完整性，将残差引导的运动掩码与YOLOv8-seg分割结果取交并集——YOLOv8-seg提供闭集物体的准确分割，残差引导确保对无训练的开放集动态物体也有效（Fig. 3）。

**与WildGS-SLAM不确定性方案对比**：
| | WildGS-SLAM | UP-SLAM |
|---|---|---|
| 特征提取 | 3D-aware DINOv2（需预训练） | DINOv2（无需微调） |
| 预测器 | 在线训练MLP | **无需训练**——直接优化不确定性图 |
| 输入信号 | DINOv2特征 + 渲染RGB | 渲染RGB + 传感器深度 + DINO余弦距离 |
| 传感器 | 单目RGB | RGB-D |
| 冷启动 | 需MLP预热（前12帧） | 第一帧即可用 |
| 动态物体范围 | 语义辅助 | 几何+语义联合驱动 |
| 不确定性优化位置 | 建图线程中 | 跟踪线程中（并行） |

### 4. DINO特征场

**动机**：高维视觉特征直接存储在高斯上会显著扩展优化空间，导致显存消耗大、计算效率低。

**低维→高维蒸馏**：

锚点特征通过MLP $F_d$ 解码低维高斯视觉属性 $\{f\} \in \mathbb{R}^{k \times N_l}$：
$$\{f_0, ..., f_{k-1}\} = F_d(\hat{f}_v, \delta_{vc}, d_{vc}, \mathbf{t})$$

低维特征经3DGS框架渲染得到特征图 $\tilde{F}$：
$$\tilde{F} = \sum_{i=1}^N f_i \alpha_i \prod_{j=1}^{i-1} (1-\alpha_j)$$

浅层MLP $F_m$ 将低维特征映射到高维DINO特征空间：
$$\hat{F} = F_m(\tilde{F}) \in \mathbb{R}^{N_h}$$

**DINO特征监督**（Eq. 12）：
$$\mathcal{L}_d = \frac{1}{N_d} \sum_{i=0}^{N_d} \left(1 - \frac{F_i \cdot \hat{F}_i}{\|F_i\|_2 \|\hat{F}_i\|_2}\right)$$

其中 $N_l = 16 \ll N_h$，确保优化效率同时减少显存和计算开销。

**建图中不确定性预测**（Eq. 13-14）：
DINO特征输入MLP $F_u$ 预测逐像素不确定性 $\sigma = F_u(F)$，与高斯地图同时优化但梯度隔离。映射总损失：
$$\mathcal{L} = M(\mathcal{L}_g + \lambda_4 \mathcal{L}_d) + \lambda_5 \bar{s}$$

其中 $\bar{s}$ 为平均尺度，防止尺度爆炸。$\{\lambda_4, \lambda_5\} = \{0.01, 0.01\}$。

**与LangSplat/LangGS-SLAM的区别**：LangSplat构建CLIP语言场用于开放词汇查询；UP-SLAM构建DINO特征场用于提升不确定性预测鲁棒性——用途不同但技术路线相似（高斯附加特征 → 渲染 → MLP解码）。

### 5. 时间编码器

**动机**：Scaffold-GS等方法将外观嵌入引入颜色预测以提升in-the-wild重建质量。SLAM中也有工作将位姿作为MLP额外输入。但旋转矩阵位于SO(3)非欧流形，传统MLP难以有效建模旋转变化。由于SLAM运行在时序相关的图像序列上，位姿演化是时间依赖的——因此直接对帧索引做时间编码。

**方案**：每帧 $t$ 映射为时间嵌入 $\mathbf{t} = \{\sin(t), \cos(t)\} \in \mathbb{R}^2$，注入所有MLP：
$$\{c_0, ..., c_{k-1}\} = F_c(\hat{f}_v, \delta_{vc}, d_{vc}, \mathbf{t})$$

同样，不透明度 $\{o\}$、旋转 $\{q\}$、尺度 $\{s\}$ 和特征 $\{f\}$ 均由各自的独立MLP预测，均以时间编码为条件。

## 实验结论

### 实验设置

**数据集**：
| 数据集 | 分辨率 | 动态内容 | 用途 |
|--------|--------|---------|------|
| TUM RGB-D | 640×480 | 人 | 定量跟踪 |
| Bonn RGB-D Dynamic | 640×480 | 人+气球+箱子 | 定量跟踪+渲染 |
| MoCap RGB-D | 1280×720 | ANYmal机器人/篮球/人群/球拍/石头/雨伞 | 开放集动态测试 |
| ScanNet | 640×480 | 静态室内 | 静态鲁棒性验证 |

**对比方法（16种）**：
- 经典SLAM: ORB-SLAM3
- 经典动态SLAM: ReFusion, DynaSLAM, EM-Fusion
- NeRF SLAM: iMAP, NICE-SLAM, Vox-Fusion, Co-SLAM, ESLAM
- NeRF动态SLAM: RoDyn-SLAM
- 3DGS SLAM: Photo-SLAM, GS-SLAM, SplaTAM
- 3DGS动态SLAM: DG-SLAM, Gassidy, WildGS-SLAM

**评价指标**：ATE RMSE [cm]（轨迹误差）、PSNR/SSIM/LPIPS（渲染质量，使用Ground-DINO预生成掩码排除动态区域）

**硬件**：Intel i7-12700KF + NVIDIA RTX 4060ti 16G。完全用C++和CUDA实现。

### 跟踪精度

**Bonn RGB-D (Table 1)**：
| Method | Balloon | Balloon2 | Ball_track | Ps_track | Ps_track2 | Mv_box2 | Avg. |
|--------|---------|----------|------------|----------|-----------|---------|------|
| ORB-SLAM3 | 5.8 | 17.7 | 3.1 | 70.7 | 77.9 | 3.5 | 29.78 |
| DynaSLAM | 3.0 | 2.9 | 4.9 | 6.1 | 7.8 | 3.9 | 4.76 |
| DG-SLAM | 3.7 | 4.1 | 10 | 4.5 | 6.9 | 3.5 | 5.45 |
| **UP-SLAM** | **2.8** | **2.7** | **2.9** | **4.0** | **3.6** | **3.2** | **3.2** |

**MoCap RGB-D (Table 2)** — 开放集动态物体测试：
| Method | ANY1 | ANY2 | Ball | Crowd | Person | Racket | Stones | Table1 | Table2 | Umb. | Avg. |
|--------|------|------|------|-------|--------|--------|--------|--------|--------|------|------|
| DynaSLAM | 1.6 | 0.5 | 0.5 | 1.7 | 0.5 | 0.8 | 2.1 | 1.2 | 34.8 | 34.7 | 7.84 |
| Photo-SLAM | 79.5 | 11.8 | 50.3 | 105.9 | 27.5 | 38.23 | 113.5 | 39.1 | 64.8 | 84 | 61.46 |
| DG-SLAM | 1.2 | 2.1 | 0.8 | 1.3 | 1.5 | 1.6 | 1.5 | 2 | 57.9 | 1.35 | 7.06 |
| **UP-SLAM** | **0.4** | **0.6** | **0.6** | **1.1** | **1.1** | **0.9** | **1.0** | **0.7** | **3.6** | **0.8** | **1.08** |

相比DG-SLAM，定位精度平均提升**84.7%**。DynaSLAM在Table2和Umbrella序列显著漂移（34.8, 34.7 cm）——因为这些数据集包含大量难以预定义的动态物体。

**TUM RGB-D (Table 3)**：
| Method | Fr3/w/xyz | Fr3/w/half | Fr3/w/static | Fr3/s/xyz | Fr2/desk_person | Avg. |
|--------|-----------|------------|--------------|-----------|-----------------|------|
| ORB-SLAM3 | 28.1 | 30.5 | 2.0 | 1.0 | 1.5 | 12.62 |
| DynaSLAM | 1.5 | 2.9 | 0.7 | 1.6 | 0.9 | 1.52 |
| DG-SLAM | 1.7 | 1.8 | 0.7 | 1.0 | 3.2 | 1.68 |
| **UP-SLAM** | **1.6** | **2.6** | **0.7** | **0.9** | **1.3** | **1.42** |

**静态场景 ScanNet (Table 5)**：
| Method | 00 | 59 | 106 | 169 | 207 | Avg. |
|--------|----|----|-----|-----|-----|------|
| Co-SLAM | 7.1 | 11.1 | 9.4 | 5.9 | 7.1 | 8.8 |
| SplaTAM | 12.8 | 10.1 | 17.7 | 12.1 | 7.5 | 11.9 |
| DG-SLAM | 7.9 | 11.5 | 8.0 | 8.3 | 8.2 | 8.6 |
| **UP-SLAM** | **8.2** | **7.3** | **8.2** | **8.8** | **7.0** | **7.9** |

静态场景平均提升**10.2%**（相比静态专用SLAM）和**8.1%**（相比DG-SLAM）——证明不确定性模块不会在静态场景产生副作用。

### 渲染质量

**Bonn RGB-D (Table 6)**：
| Method | PSNR | SSIM | LPIPS |
|--------|------|------|-------|
| SplaTAM | 19.30 | 0.724 | 0.240 |
| Photo-SLAM | 23.48 | 0.825 | 0.208 |
| DG-SLAM | 17.46 | 0.745 | 0.464 |
| WildGS-SLAM (RGB) | 23.43 | **0.941** | 0.185 |
| **UP-SLAM** | **28.0** | 0.904 | **0.117** |

PSNR平均提升**5.47 dB**（vs 第二名）。SSIM略低于WildGS-SLAM（后者专攻单目渲染），但LPIPS显著更优（0.117 vs 0.185，↓36.8%）。定性结果：SplaTAM和Photo-SLAM无法生成静态地图，DG-SLAM重建不完整（缺孔），WildGS-SLAM有不同程度的失败。UP-SLAM成功去除动态物体并构建高保真、无伪影静态地图。

### 消融实验 (Table 4)

| 变体 | ATE↓ | PSNR↑ | Model Size↓ | DINO Sim.↑ |
|------|------|-------|-------------|------------|
| w/o 时间编码器 | 3.37 | 26.6 | 7.04 | 78.6 |
| w/o 分割 (YOLOv8) | 3.46 | 27.1 | 7.03 | 78.5 |
| w/o 概率锚点更新 | 3.57 | 27.74 | 22.92 | 79.2 |
| **UP-SLAM (完整)** | **3.2** | **28.0** | **7.01** | **79.5** |

分析：
- **时间编码器**：主要提升渲染质量（PSNR +1.4 dB），对定位也有正向帮助
- **分割模块（YOLOv8-seg）**：对定位和渲染都关键——初始化阶段非刚体阻碍完整分割，可能导致动态关键点被错误添加为静态路标
- **概率锚点更新**：模型大小从22.92 MB降至7.01 MB（↓69.4%），无锚点更新时无法有效剪枝→地图更新变慢→残差反馈减弱→定位精度下降
- **DINO相似度**近80%，证明下游应用（目标级导航、语义理解）潜力

### 运行时分析 (Table 7)

| | SplaTAM | WildGS-SLAM | DG-SLAM | UP-SLAM |
|---|---|---|---|---|
| 每帧平均 [ms] | 4046 | 1838 | 1011 | **78** |
| 总时间(+精化) [s] | 1776.54(+0) | 1526.58(+719.61) | 444.17(+0) | 694.81(+660.31) |
| 模型大小 [MB] | 29.9 | 8.8 | 4.9 | **7.01** |

UP-SLAM处理速率**12 FPS**（78 ms/帧），满足机器人实时定位需求。相比WildGS-SLAM，在相同精化迭代次数下速度提升约**24倍**（1838→78 ms）。DG-SLAM总时间最短（444s），但不含分割时间且渲染质量显著更低（PSNR 17.46 vs 28.0）——UP-SLAM在重建质量和定位速度之间取得更好平衡。

## 与前作的区别

| 前作 | 关键区别 |
|------|---------|
| **MonoGS** (CVPR 2024) | 静态假设+串行框架→动态中崩溃；UP-SLAM并行+动态鲁棒 |
| **Splat-SLAM** (2024) | 有回环但假设静态+串行；UP-SLAM并行+开放集动态处理 |
| **WildGS-SLAM** (arxiv 2025) | 单目+在线训练MLP预测不确定性+串行；UP-SLAM RGB-D+**训练无关**不确定性+**并行** |
| **DG-SLAM** (NeurIPS 2024) | 语义分割+几何一致性运动掩码，固定掩码无精化；UP-SLAM**连续精化**运动掩码+不确定性与高斯优化同时进行 |
| **GS-LIVO** (IEEE TRO 2025) | 多传感器融合+哈希八叉树，非针对动态场景；UP-SLAM专注动态+概率八叉树 |
| **G²-Mapping** (IEEE TASE 2025) | 通用可微渲染器+深度不确定性，但串行框架；UP-SLAM**并行框架** |
| **LangGS-SLAM** (arxiv 2026) | RGB-D在线语义SLAM但非动态鲁棒；UP-SLAM专注**动态过滤** |
| **Photo-SLAM** (CVPR 2024) | ORB-SLAM3跟踪+图像金字塔优化，但动态中定位失败（TUM上ATE 22.28）；UP-SLAM不确定性过滤动态特征 |

## 实现细节

**损失权重**：$\{\gamma, \lambda_1, \lambda_2, \lambda_3, \lambda_4, \lambda_5\} = \{0.8, 0.6, 1.0, 0.4, 0.01, 0.01\}$

**残差权重**：$\{t_1, t_2, t_3\} = \{0.25, 0.7, 0.1\}$（深度残差权重最大——RGB-D下深度是关键信号）

**MLP架构**（使用SoftPlus激活）：
| MLP | 用途 | 架构 | 隐藏层维度 |
|-----|------|------|-----------|
| $F_c, F_o, F_s, F_q$ | 颜色/不透明度/尺度/旋转 | LINEAR→SoftPlus→LINEAR | 32 |
| $F_d$ | 低维特征解码 | LINEAR→SoftPlus→LINEAR | 32 |
| $F_m$ | 低维→高维特征映射 | Conv→ReLU→Conv | 128 |
| $F_u$ | 不确定性预测 | Conv→ReLU→Conv→SoftPlus | 128 |

**低维特征维度**：$N_l = 16$

**精化迭代次数**：20000

## 限制

1. **MLP解码开销**：概率锚点通过MLP解码高斯属性，增加优化时间，在有限训练迭代下可能引入残差计算噪声
2. **初始化阶段依赖YOLOv8-seg**：虽然日常跟踪中训练无关的残差引导方法即可检测动态物体，但在初始化阶段仍借助YOLOv8-seg的闭集分割来确保动态区域完整排除——对未训练的物体类别，初始化掩码可能不完整
3. **RGB-D依赖**：需要深度传感器，无法直接应用于纯单目场景（但深度信号使不确定性估计更简单可靠）
4. **概率模型参数**：概率八叉树的先验和更新率仍需根据场景类型调参（尽管比手动阈值更鲁棒）

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 动态SLAM同行: [[papers/wildgs-slam]]（单目不确定性感知，串行框架+训练依赖）, DG-SLAM（语义几何一致性，固定掩码）
- 相关SLAM: [[papers/gs-livo]]（八叉树+多传感器）, [[papers/g2-mapping]]（通用GS-SLAM+深度不确定性）, [[papers/pseudo-depth-meets-gaussian]]（前馈式SLAM）
- 在线语义GS-SLAM: [[papers/langgs-slam]]
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/slam]], [[concepts/uncertainty-aware-mapping]], [[concepts/spatial-data-structures]], [[concepts/dinov2]], [[concepts/3d-language-field]], [[concepts/alpha-compositing]], [[concepts/projection-transform]], [[concepts/probabilistic-octree]], [[concepts/parallel-tracking-mapping]], [[concepts/adaptive-density-control]]
