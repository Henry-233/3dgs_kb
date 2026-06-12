---
title: "VarSplat: Uncertainty-aware 3D Gaussian Splatting for Robust RGB-D SLAM"
authors:
  - "Anh Thuan Tran"
  - "Jana Kosecka"
year: 2026
venue: arXiv
status: done
tags:
  - slam
  - rgb-d-slam
  - uncertainty
  - 3dgs
---

## 一句话总结

VarSplat是首个在3DGS-SLAM中将外观不确定性作为一等量（first-class quantity）显式建模的系统——为每个3D高斯学习外观方差σ²，利用全方差定律+Alpha合成在单次光栅化中渲染可微的逐像素不确定性图V，该图同时引导跟踪（权重化L1光度损失）、子图配准和回环检测（不透明度加权相似度），在ScanNet++上ATE 1.69 cm（比次优方法提升18%），TUM-RGBD上ATE 3.20 cm（纯3DGS方法最佳）。

## 解决的问题

现有3DGS-SLAM对所有像素等权对待，但在低纹理区域（白墙）、深度不连续处和目标边界、透明/反射表面，光度观测可靠性差异巨大。此前方法要么建模几何不确定性（深度方差，CG-SLAM/UncLe-SLAM），要么依赖预训练预测器（WildGS-SLAM的DINOv2特征）。核心洞察：**外观方差可以直接从3DGS光栅化过程中推导出逐像素不确定性，在在线SLAM中以单pass效率可微渲染**——无需额外网络或采样。

## 核心方法

### 1. 逐高斯外观方差参数化

在标准3DGS参数（位置μ、协方差Σ、不透明度α、尺度s、颜色c）基础上，VarSplat为每个高斯增加外观方差参数σ²∈ℝ³：

$$P^{s}=\{G_{i}^{s}(\mu_{i},\Sigma_{i},\alpha_{i},s_{i},c_{i},\sigma_{i}^{2})|i=1,\ldots,N^{s}\}$$

σ²与几何协方差Σ不同：Σ定义高斯在3D空间中的空间范围，σ²编码该高斯在不同视角下外观颜色的一阶不确定性——即使SH正确建模了平均颜色，实际观测仍因遮挡变化、反射方向变化而产生方差。深度不连续处和遮挡边界由于透射率权重w_i突变，方差自然较大。

### 2. 全方差定律 → 单pass不确定性渲染

利用全方差定律将逐像素方差分解：

$$\mathrm{Var}[X] = \mathbb{E}[\mathrm{Var}[X|Z]] + \mathrm{Var}(\mathbb{E}[X|Z])$$

- 第一项：每个高斯对像素贡献的条件方差的加权平均 = Σw_i·σ²_i
- 第二项：不同高斯之间颜色均值的方差 = Σw_i·c²_i − (Σw_i·c_i)²

合并后得到**单pass可微不确定性渲染公式**：

$$V = \sum_{i}w_{i}(\sigma_{i}^{2}+c_{i}^{2}) - \Big(\sum_{i}w_{i}c_{i}\Big)^{2}$$

其中w_i = T_i·α_i，T_i = ∏ⱼ^{i-1}(1−αⱼ)。V与颜色C和深度D共享同一次光栅化pass——**零额外渲染开销**。

### 3. 方差学习：高斯负对数似然

不同于用L1（拉普拉斯尺度）监督方差会导致不一致估计，VarSplat使用MSE（高斯负对数似然形式）：

$$\mathcal{L}_{\text{var}} = \frac{1}{2V}\Big(\|\hat{I}-I\|_{2}^{2}+\|\hat{D}-D\|_{2}^{2}\Big) + \log(V)$$

∂L_var/∂V = −(||Î−I||²+||D̂−D||²)/(2V²) + 1/V，通过链式法则 ∂V/∂σ²_i = w_i 梯度回传到每个高斯：
- 残差大 → V增大 → σ²增大（不确定性上升）
- 残差小 → V减小 → σ²减小（置信度提升）
- log(V)正则化项防止V发散到0

建图总损失：L_map = λ_color·L_color + λ_depth·L_depth + λ_reg·L_reg + λ_var·L_var

### 4. 中值中心对数缩放 → 置信度权重

将渲染的V和学习的σ²转换为[0,1]置信度权重：

$$\widetilde{V} = \underset{\Omega}{\mathrm{median}}(\log(V)), \quad \widetilde{w}_{p} = \exp[-(\log V-\widetilde{V})/\tau]$$

$$\widetilde{\sigma^{2}} = \mathrm{median}(\log\sigma^{2}), \quad \widetilde{w}_{s} = \exp[-(\log\sigma^{2}-\widetilde{\sigma^{2}})/\tau]$$

τ控制权重锐度。方差大于中位数的像素/高斯权重<1，方差小的权重趋近1。

### 5. 不确定性引导的三级位姿估计

**跟踪 (Eq. 17):** 仅在高不透明度（>0.99）像素上，用ṽₚ加权光度L1损失：
$$\mathcal{L}_{\text{track}} = \sum\lambda_{c}(\widetilde{w_{p}}\odot\|\hat{I}-I\|_{1}) + (1-\lambda_{c})\|\hat{D}-D\|_{1}$$
跟踪时冻结方差参数，停止ṽₚ的梯度。

**回环检测 (Eq. 18):** 用不透明度比率调制子图相似度：r = Σṽₛαⱼ / Σαⱼ。r高表示子图中可靠外观信息多，r低表示高不确定性。最终相似度 = cross_sim ⊙ (r_q * r_db)，使高不确定性子图更难匹配。

**子图配准 (Eq. 19):** 检测到回环后，用ṽₚ加权配准损失定位查询关键帧在数据库子图中的位姿。

## 数学形式

**核心不确定性渲染 (Eq. 9):**
$$V = \sum_{i}w_{i}(\sigma_{i}^{2}+c_{i}^{2}) - \Big(\sum_{i}w_{i}c_{i}\Big)^{2}$$

**方差学习 (Eq. 13):**
$$\mathcal{L}_{\text{var}} = \frac{1}{2V}\Big(\|\hat{I}-I\|_{2}^{2}+\|\hat{D}-D\|_{2}^{2}\Big) + \log(V)$$

**梯度 (Eq. 15):**
$$\frac{\partial\mathcal{L}_{\text{var}}}{\partial\sigma_{i}^{2}} = \frac{\partial\mathcal{L}_{\text{var}}}{\partial V} w_{i}$$

**置信度权重 (Eq. 16):**
$$\widetilde{w}_{p} = \exp[-(\log V-\widetilde{V})/\tau], \quad \widetilde{w}_{s} = \exp[-(\log\sigma^{2}-\widetilde{\sigma^{2}})/\tau]$$

**跟踪损失 (Eq. 17):**
$$\mathcal{L}_{\text{track}} = \sum\lambda_{c}(\widetilde{w_{p}}\odot\|\hat{I}-I\|_{1}) + (1-\lambda_{c})\|\hat{D}-D\|_{1}$$

**回环调制 (Eq. 18):**
$$r = \frac{\sum_{j}\widetilde{w_{s}}\alpha_{j}}{\sum_{j}\alpha_{j}}, \quad \text{sim} = \text{cross\_sim}\odot(r_{q} \cdot r_{db})$$

## 与前作的区别

| 维度 | SplaTAM | Gaussian-SLAM | CG-SLAM | WildGS-SLAM | **VarSplat** |
|------|---------|---------------|---------|-------------|-------------|
| **不确定性来源** | 无 | 无 | 深度方差 | 预训练DINOv2 | **可学习外观方差** |
| **不确定性渲染** | — | — | 几何侧 | MLP预测 | **全方差定律Alpha合成** |
| **额外pass** | — | — | — | 需要 | **零（单pass共享）** |
| **跟踪用途** | — | — | 深度加权 | 动态过滤 | **光度加权** |
| **回环用途** | 标准 | 标准 | — | — | **方差调制相似度** |
| **方差训练** | — | — | 几何监督 | 预训练 | **端到端高斯NLL** |

VarSplat区别于CG-SLAM（建模深度方差而非外观方差）和WildGS-SLAM（预训练预测器而非在线学习）。VarSplat在外观侧建模不确定性，从光栅化过程内部导出，与现有几何不确定性方法正交。

## 实验结论

**跟踪 (ATE RMSE cm ↓):**
- **Replica**: VarSplat **0.23 cm**（平均最佳，比现有方法提升约10%），SplaTAM 0.36
- **ScanNet++**: VarSplat **1.69 cm**（比次优提升18%），SplaTAM在长序列失败（443.10 cm）
- **TUM-RGBD**: VarSplat **3.20 cm**（纯3DGS方法最佳），SplaTAM 5.48，Gaussian-SLAM 6.08，CG-SLAM 4.00
- **ScanNet**: VarSplat总体最佳，对噪声室内场景鲁棒

**重建 (Replica):** VarSplat第三（仅次于Loopy-SLAM和LoopSplat），方差正则化未损害网格质量

**渲染:** 在Replica/TUM/ScanNet三数据集上竞争性表现，但非最优（方差学习引入了额外自由度）

**消融实验 (Table 8-9):**
- 不确定性跟踪比固定权重一致提升ATE
- 高斯NLL (MSE+logV) 优于L1方差监督
- 中值对数缩放比线性缩放更鲁棒

**定性分析:** 不确定性图在深度不连续、遮挡边界、反射表面自然呈现高值，在纹理丰富平坦区域呈现低值，验证了方差学习的物理合理性。

## 局限性

1. **深度依赖初始化**：高斯添加策略依赖深度输入，深度稀疏或缺失时性能受限
2. **方差计算开销**：学习和渲染方差增加计算和显存，每个高斯额外3个可学习参数
3. **仅外观不确定性**：未联合建模几何不确定性（深度方差），TUM部分序列结果体现此限制
4. **静态场景聚焦**：实验集中在静态场景，未处理运动物体——方差引导的运动分割和动态建图是有前景方向
5. **无方差共享/剪枝**：方差参数可跨高斯共享或剪枝以降低开销，未探索

## 关联

- [[concepts/slam]] — SLAM基础框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示，σ²是对每个高斯的扩展参数
- [[concepts/alpha-compositing]] — Alpha合成既是颜色/深度渲染基础，也是方差渲染基础
- [[concepts/differentiable-rendering]] — 可微渲染使方差可端到端学习
- [[concepts/covariance-matrix]] — Σ是几何协方差，σ²是外观方差，两者互补
- [[concepts/uncertainty-aware-tracking]] — 本文是该概念的核心实例
- [[concepts/ssim-loss]] — 颜色损失中的SSIM分量
- [[papers/2026-05-07/3d-gaussian-splatting]] — 3DGS基础方法
- [[papers/2026-05-21/wildgs-slam]] — 不确定性用于动态检测（预训练DINOv2），VarSplat用于跟踪加权（在线学习方差）
- [[papers/2026-06-11/roger-slam]] — 互补：RoGER-SLAM用CLIP处理传感器退化，VarSplat用方差处理测量可靠性

## 标注状态
---
annotated: true
annotation_date: 2026-06-12
annotated_pdf: raw/papers/VarSplat Uncertainty-aware 3D Gaussian Splatting for Robust RGB-D SLAM_annotated.pdf
---
