---
title: "VGGT: Visual Geometry Grounded Transformer"
authors: Jianyuan Wang, Minghao Chen, Nikita Karaev, Andrea Vedaldi, Christian Rupprecht, David Novotny
year: 2025
venue: CVPR 2025 (Best Paper Award)
affiliations: Visual Geometry Group (University of Oxford), Meta AI
tags: [paper, 3d-vision, foundation-model, feed-forward]
status: done
---

## 一句话总结
VGGT是一个前馈式Transformer，从1到数百张图像直接推理场景的全部关键3D属性（相机参数、点图、深度图、3D点轨迹），推理时间<1秒，无需任何逐场景优化或后处理，获CVPR 2025最佳论文奖。代码开源：https://github.com/facebookresearch/vggt

## 解决的问题

传统3D视觉管线依赖**逐场景优化**：

1. **SfM（Structure from Motion）**：用COLMAP等工具从多视图图像中估计相机姿态和稀疏点云，耗时数分钟到数十分钟，且可能失败（纹理缺失、运动模糊等场景）
2. **MVS（Multi-View Stereo）**：从已知姿态的图像中稠密重建，需要SfM输出作为前置条件
3. **单任务模型割裂**：相机标定、深度估计、点云重建、点追踪各有专门模型，彼此独立

VGGT追问：能否用一个**通用前馈模型**，一次性完成所有3D几何估计任务？

**核心洞察**：随着网络容量的增长，3D任务可以直接由神经网络解决，几乎完全省去几何后处理。这与DUSt3R/MASt3R形成对比——后者只能处理两张图像，且依赖昂贵的全局对齐后处理来融合成对重建结果。

## 核心方法

### 问题定义
输入为N张RGB图像 $(I_i)_{i=1}^N \in \mathbb{R}^{3 \times H \times W}$，观测同一3D场景。VGGT的Transformer映射该序列到逐帧3D标注：

$$f\left((I_i)_{i=1}^N\right) = \left(g_i, D_i, P_i, T_i\right)_{i=1}^N$$

- **相机参数** $g_i \in \mathbb{R}^9$：旋转四元数 $q \in \mathbb{R}^4$ + 平移向量 $t \in \mathbb{R}^3$ + 视场角 $f \in \mathbb{R}^2$（假设主点在图像中心）
- **深度图** $D_i \in \mathbb{R}^{H \times W}$：每像素的深度值
- **点图（Point Map）** $P_i \in \mathbb{R}^{3 \times H \times W}$：每像素映射到3D世界坐标（以第一帧坐标系为世界参考系）
- **追踪特征** $T_i \in \mathbb{R}^{C \times H \times W}$：用于3D点追踪的密集特征

### 整体架构

```
Input Images → DINOv2 Patchify → Token序列
    → [Alternating-Attention × 24 layers]
        ├── Frame-wise Self-Attention（帧内token交互）
        └── Global Self-Attention（跨帧token交互）
    → Camera Head → 相机参数
    → DPT Head → 深度图、点图、追踪特征
    → CoTracker2 Head → 3D点轨迹
```

**核心设计原则**：
- **全局注意力（Global Attention）**：所有视图的所有patch之间做全对全注意力，模型自动学习跨视图几何对应——不需要显式的对极几何或特征匹配
- **交替注意力（Alternating-Attention, AA）**：交替使用帧内自注意力和全局自注意力，在跨帧信息融合和帧内表征归一化之间取得平衡
- **多任务联合输出**：单次前向pass同时预测相机、深度、点图、轨迹
- **无需后处理**：纯前馈推理，不使用BA（Bundle Adjustment）或任何迭代优化
- **最小3D归纳偏置**：基于标准大型Transformer，除AA外无特殊3D设计

### Alternating-Attention（AA）详解

AA是VGGT的核心架构创新。标准Transformer改造如下：

1. **Frame-wise Self-Attention**：每个帧的token $t_k^I$ 仅在帧内互相关注——让模型学习单帧内部的几何结构
2. **Global Self-Attention**：所有帧的所有token $t^I = \bigcup_{i=1}^N\{t_i^I\}$ 之间全对全关注——让模型学习跨帧的几何对应关系
3. 两种注意力交替堆叠，默认各24层（共L=24个block，每个block含1个frame-wise层+1个global层）

消融实验表明AA显著优于：
- **纯全局自注意力**：缺乏帧内归一化，性能下降
- **交叉注意力（Cross-Attention）**：每帧独立关注其他所有帧，计算量随帧数急剧增长，且性能不如AA

**注意**：VGGT完全不使用交叉注意力层，仅使用自注意力。

### Token设计

每帧的图像token $t_i^I$ 外加：
- **相机token** $t_i^g \in \mathbb{R}^{1 \times C}$：汇总该帧的相机参数信息
- **寄存器token（Register Tokens）** $t_i^R \in \mathbb{R}^{4 \times C}$：提供额外的存储空间（来自Darcet et al. 2023）

**首帧特殊处理**：第一帧的相机token和寄存器token使用不同的可学习初始化值（$t^g, t^R$），其他帧共享另一组初始化值（$\bar{t}^g, \bar{t}^R$）。这使模型能识别第一帧作为世界参考坐标系。

经过AA Transformer后，寄存器token被丢弃（遵循ViT惯例），图像token $t_i^I$ 和相机token $t_i^g$ 用于预测。

### 预测头（Prediction Heads）

**相机头（Camera Head）**：
- 4个额外自注意力层处理所有帧的输出相机token $(\hat{t}_i^g)_{i=1}^N$
- 接线性层预测 $g_i = [q_i, t_i, f_i]$
- 第一帧的相机外参固定为单位变换（$q_1 = [0,0,0,1], t_1 = [0,0,0]$）

**稠密预测头（DPT Head）**：
- 输出图像token $\hat{t}_i^I$ 通过DPT解码器转换为稠密特征图 $F_i \in \mathbb{R}^{C \times H \times W}$
- 3×3卷积层分别映射到深度图 $D_i$、点图 $P_i$、追踪特征 $T_i$
- 同时预测任意不确定性（Aleatoric Uncertainty）：$\sigma_i^D \in \mathbb{R}_+^{H \times W}$ 和 $\sigma_i^P \in \mathbb{R}_+^{H \times W}$
- DPT使用第4、11、17、23个block的token进行多尺度上采样

**追踪头（Tracking Head）**：
- 采用CoTracker2架构，以追踪特征 $T_i$ 为输入
- 给定查询图像 $I_q$ 中的查询点 $y_j$（训练时q=1），在 $T_q$ 上双线性采样获得查询特征
- 查询特征与所有其他帧的 $T_i$ 做相关运算，生成相关图
- 相关图经自注意力层处理，预测所有帧中对应的2D点位置
- 同时预测可见性（二分类：该点在某帧是否可见）
- 不假设输入帧的时间顺序——适用于任意图像集合，不限于视频

### 过完备预测（Over-complete Predictions）

VGGT预测的所有量并非完全独立——例如相机参数 + 深度图可以反投影得到点图。但实验发现：
- **训练时**：显式监督所有输出（包括冗余量）带来显著性能提升
- **推理时**：独立估计的深度图+相机参数反投影得到的点云，比直接使用点图分支输出更准确（ETH3D Overall: 0.677 vs 0.709）

这表明将复杂任务分解为更简单的子问题是有益的。

## 数学形式

### 损失函数
多任务联合训练的总体损失：

$$\mathcal{L} = \mathcal{L}_{\text{camera}} + \mathcal{L}_{\text{depth}} + \mathcal{L}_{\text{pmap}} + \lambda \mathcal{L}_{\text{track}}, \quad \lambda = 0.05$$

**相机损失**（Huber Loss）：
$$\mathcal{L}_{\text{camera}} = \sum_{i=1}^N |\hat{g}_i - g_i|$$

**深度损失**（Aleatoric Uncertainty Loss）：
$$\mathcal{L}_{\text{depth}} = \sum_{i=1}^N \sigma_i^D \odot (\hat{D}_i - D_i) + \alpha \nabla(\hat{D}_i - D_i) - \beta \log \sigma_i^D$$

其中 $\odot$ 为逐元素乘积，$\nabla$ 为梯度项（广泛用于单目深度估计）。

**点图损失**（同深度损失形式）：
$$\mathcal{L}_{\text{pmap}} = \sum_{i=1}^N \sigma_i^P \odot (\hat{P}_i - P_i) + \alpha \nabla(\hat{P}_i - P_i) - \beta \log \sigma_i^P$$

**追踪损失**（L1 + 可见性BCE）：
$$\mathcal{L}_{\text{track}} = \sum_{j=1}^M \sum_{i=1}^N |y_{j,i} - \hat{y}_{j,i}| + \mathcal{L}_{\text{visibility}}$$

### 坐标归一化

以第一帧相机坐标系为世界参考系。计算点图 $P$ 中所有3D点到原点的平均欧氏距离，用该尺度归一化相机平移 $t$、点图 $P$ 和深度图 $D$。

与DUSt3R的关键区别：VGGT不对网络预测做归一化——而是强制模型学习训练数据中选择的特定规范化。实验发现这既不损害收敛也不影响性能，且避免了训练不稳定。

## 训练细节

| 配置项 | 参数 |
|--------|------|
| 总参数量 | ~1.2B（12亿） |
| 注意力层数 | L=24层全局+24层帧内 |
| 特征维度 | 1024 |
| 注意力头数 | 16 |
| 优化器 | AdamW |
| 峰值学习率 | 0.0002（cosine调度） |
| Warmup | 8K iterations |
| 总训练步数 | 160K iterations |
| Batch构成 | 每batch随机采样2-24帧/场景，总共48帧/batch |
| 图像分辨率 | 最长边518像素，短边168-518（14倍数裁剪） |
| 数据增强 | 色彩抖动、高斯模糊、灰度化（逐帧独立应用） |
| 训练硬件 | 64×A100 GPU，训练9天 |
| 精度 | bfloat16 + 梯度检查点 |
| 梯度裁剪 | 阈值1.0 |

### 训练数据
大规模多样化数据集集合：Co3Dv2、BlendMVS、DL3DV、MegaDepth、Kubric、WildRGB、ScanNet、HyperSim、Mapillary、Habitat、Replica、MVS-Synth、PointOdyssey、Virtual KITTI、Aria Synthetic Environments、Aria Digital Twin、以及类似Objaverse的合成数据集。

覆盖室内/室外、合成/真实等多种场景。3D标注来源包括传感器直接采集、合成引擎、SfM技术等。数据规模和多样性与MASt3R相当。

### Patchify方案
比较了两种图像切分方式：
- 14×14卷积层（标准ViT方案）
- 预训练DINOv2模型

DINOv2性能更好且训练更稳定（尤其初期），对学习率和动量等超参数不敏感。最终选择DINOv2作为默认方案。

## 与前作的区别

| 前作 | 核心区别 |
|------|----------|
| **COLMAP/SfM** | VGGT纯前馈推理（<1秒）vs 迭代优化（数分钟到数十分钟），不依赖特征匹配和三角化 |
| **DUSt3R** | VGGT扩展到数百视图（DUSt3R仅2视图）、增加3D点追踪、一次预测绝对相机位姿（非成对相对位姿后全局对齐）、无需昂贵的后处理 |
| **MASt3R** | VGGT是通用3D基础模型（多任务联合），MASt3R聚焦点匹配与局部几何 |
| **VGGSfM** | VGGT无BA（可选的BA仅作为后处理增强），VGGSfM深度集成可微BA于训练和推理 |
| **RelPose系列** | VGGT处理多视图（非仅双视图），输出稠密几何（非仅相机姿态） |
| **DUSt3R并发改进** (MV-DUSt3R, CUT3R, FLARE, Fast3R) | VGGT显著优于这些同期工作，速度与最快的Fast3R相当 |

### 与3DGS的关系

| 3DGS流程环节 | 传统方案 | VGGT替代 |
|-------------|---------|---------|
| 相机姿态估计 | COLMAP (SfM)，数分钟 | VGGT前馈推理，<1秒 |
| 初始点云 | COLMAP稀疏点云（数千点） | VGGT稠密点图（每像素3D坐标） |
| 高斯初始化 | 从稀疏SfM点初始化高斯 | 可从VGGT稠密点图采样，初始几何更完整 |

VGGT可作为3DGS的**初始化前端**，尤其对前馈式新视角合成（pixelSplat、MVSplat等）意义重大。

## 实验结论

### 1. 相机姿态估计

**Co3Dv2 & RealEstate10K**（10帧/场景，AUC@30）：

| 方法 | Re10K AUC@30↑ | CO3Dv2 AUC@30↑ | 时间 |
|------|---------------|-----------------|------|
| COLMAP+SPSG | 45.2 | 25.3 | ~15s |
| DUSt3R | 67.7 | 76.7 | ~7s |
| MASt3R | 76.4 | 81.8 | ~9s |
| VGGSfM v2 | 78.9 | 83.4 | ~10s |
| **VGGT (Feed-Forward)** | **85.3** | **88.2** | **0.2s** |
| **VGGT + BA** | **93.5** | **91.8** | 1.8s |

关键发现：VGGT纯前馈模式已超越所有需要后处理的竞争方法；在未训练过的RealEstate10K上优势更明显，验证了其泛化能力。

**IMC（Image Matching Challenge）**（摄影旅游数据，AUC@10）：

| 方法 | AUC@10↑ | 时间 |
|------|----------|------|
| VGGSfM v2 | 76.82 | ~10s |
| **VGGT** | **71.26** | **0.2s** |
| **VGGT + BA** | **84.91** | 1.8s |

VGGT纯前馈与VGGSfMv2接近但快50倍；加上BA后显著超越全部方法。

### 2. 多视图深度估计（DTU数据集）

| 方法 | 已知GT相机 | Overall↓ |
|------|-----------|----------|
| GeoMVSNet | 需要 | 0.295 |
| MASt3R | 需要 | 0.374 |
| DUSt3R | 不需要 | 1.741 |
| **VGGT** | **不需要** | **0.382** |

VGGT是仅有的两个不需要GT相机的方法之一，且性能与需要GT相机的方法相当。从DUSt3R的1.741降到0.382，归功于多图像训练机制——模型原生学会了多视图三角化推理。

### 3. 点图估计（ETH3D数据集，10帧/场景）

| 方法 | Overall↓ | 时间 |
|------|----------|------|
| DUSt3R（含全局对齐） | 1.005 | ~7s |
| MASt3R（含全局对齐） | 0.826 | ~9s |
| **VGGT Point Head直接** | **0.709** | **0.2s** |
| **VGGT Depth+Cam反投影** | **0.677** | **0.2s** |

VGGT的Depth+Cam反投影方案达到最佳性能，验证了复杂任务分解为子问题的有效性。

### 4. 图像匹配（ScanNet-1500，AUC）

| 方法 | AUC@5↑ | AUC@10↑ | AUC@20↑ |
|------|---------|----------|----------|
| SuperGlue | 16.2 | 33.8 | 51.8 |
| LoFTR | 22.1 | 40.8 | 57.6 |
| Roma（SOTA） | 31.8 | 53.4 | 70.9 |
| **VGGT** | **33.9** | **55.2** | **73.4** |

尽管VGGT并未专门为双视图匹配训练，其追踪头在该任务上仍超越了SOTA方法Roma。

### 5. 消融实验

**AA架构对比**（ETH3D点图）：

| 架构 | Overall↓ |
|------|----------|
| Cross-Attention | 1.061 |
| Global Self-Attn Only | 0.827 |
| **Alternating-Attention** | **0.709** |

**多任务学习对比**（ETH3D点图Overall）：

| 训练配置 | Overall↓ |
|----------|----------|
| 单独训练（无相机/深度/追踪） | 0.834 |
| + 相机损失 | 0.727 |
| + 深度损失 | 0.790 |
| + 追踪损失 | 0.834 |
| **全部联合** | **0.709** |

相机参数估计对点图精度帮助最大，深度估计贡献边际改进。

### 6. 下游任务微调

**前馈新视角合成**（GSO数据集）：
- 修改VGGT直接输出目标视角RGB（无需输入帧的相机参数）
- 仅用Objaverse 20%大小的训练数据
- 达到与LVSM（需要已知相机参数）相当的性能（PSNR 30.41 vs 31.71）

**动态点追踪**（TAP-Vid基准）：
- 将VGGT预训练backbone融入CoTracker2
- TAP-Vid RGB-S上 $\delta_{\text{avg}}^{\text{vis}}$ 从78.9提升到84.0
- Kinetics上AJ从49.6提升到57.2
- 所有三个TAP-Vid子集上全面超越此前所有方法

## 局限性与未来方向

1. **显存限制**：全局注意力复杂度 $O(N^2)$（N为总token数）。200帧需40GB+显存。可通过Fast3R的Tensor Parallelism等多GPU方案缓解，或采用稀疏注意力
2. **不支持鱼眼/全景图像**：当前仅处理透视投影
3. **极端旋转下性能下降**：输入帧间旋转角过大时重建质量降低
4. **主要针对静态场景**：严重非刚性形变场景会失败（但轻微动态可容忍）
5. **分辨率限制**：当前处理最长边518像素，高分辨率细节可能不足
6. **特定领域泛化未充分验证**：医学影像、水下等特殊领域

**应对策略**：VGGT的灵活性是其优势——通过针对性数据集微调即可适应新场景，无需像传统方法那样重新设计测试时优化流程。

### 推理效率（H100 GPU, 336×518分辨率）

| 帧数 | 1 | 2 | 4 | 8 | 10 | 20 | 50 | 100 | 200 |
|------|---|---|---|---|----|----|----|----|-----|-----|
| 时间(s) | 0.04 | 0.05 | 0.07 | 0.11 | 0.14 | 0.31 | 1.04 | 3.12 | 8.75 |
| 显存(GB) | 1.88 | 2.07 | 2.45 | 3.23 | 3.63 | 5.58 | 11.41 | 21.15 | 40.63 |

相机头约占5%时间和2%显存；DPT头每帧约0.03s和0.2GB显存。

### 其他技术要点

- **单视图重建**：与DUSt3R不同（需复制图像成对），VGGT架构天然支持单视图输入。虽未专门训练单视图，但展示出令人惊讶的单视图重建能力
- **可微BA探索**：在小规模实验中可微BA表现有希望，但使每步训练慢约4倍，不适合大规模训练。被识别为未来大规模无监督训练的有前景方向
- **预测归一化**：与DUSt3R不同，VGGT不对预测值做归一化——实验发现这对收敛既不必要也不有益，反而引入训练不稳定性

## 关联
- 基于: [[concepts/structure-from-motion]]
- 引入概念: [[concepts/point-map]]、[[concepts/alternating-attention]]、[[concepts/feed-forward-3d-reconstruction]]
- 对比方法: DUSt3R, MASt3R, VGGSfM, COLMAP
- 可初始化: [[papers/3d-gaussian-splatting]]
- 涉及概念: [[concepts/projection-transform]]、[[concepts/alpha-compositing]]
- 追踪组件: CoTracker2架构
- 特征提取: DINOv2（ViT-L）
- 稠密预测头: DPT（Dense Prediction Transformer）
