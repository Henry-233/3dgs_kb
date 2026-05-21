---
title: "Proxy-GS: Unified Occlusion Priors for Training and Inference in Structured 3D Gaussian Splatting"
authors: Yuanyuan Gao, Yuning Gong, Yifei Liu, Li Jingfeng, Dingwen Zhang, Yanci Zhang, Dan Xu, Xiao Sun, Zhihang Zhong
year: 2025
venue: arxiv
tags: [paper, extension]
status: done
---

## 一句话总结
提出Proxy-GS——利用轻量级代理网格+硬件光栅化在<1ms内生成1000×1000遮挡深度图，为[[concepts/mlp-based-3dgs|MLP-based结构化3DGS]]引入统一的遮挡先验：推理时剔除被遮挡锚点/高斯实现3×加速，训练时引导密度向代理网格表面迁移以提升质量。在MatrixCity Streets等重度遮挡场景中比Octree-GS快2.5×以上且质量更高，消费级RTX 4090上可达151 FPS。

## 解决的问题
MLP-based 3DGS变体（Scaffold-GS、Octree-GS）通过神经网络解码器提升渲染质量，但引入显著解码开销。现有剪枝策略（LightGaussian、MaskGaussian）和LOD技术（Hierarchical-GS、Octree-GS）缺乏**遮挡感知**——在严重遮挡的大规模城市场景中，大量锚点和高斯位于被遮挡区域，解码后对最终渲染无任何贡献，造成计算浪费。

核心观察（Fig.1）：可视化Octree-GS的激活锚点时，大量锚点对应严重遮挡区域，且3DGS为拟合所有训练视角而产生冗余高斯，忽略底层场景几何结构。

关键约束：(1) 遮挡关系获取必须极快，不能成为新瓶颈；(2) 需要适配消费级GPU（RTX 4090等）的硬件特性，利用其专用硬件光栅化单元。

## 核心方法

### 1. 代理网格构建
- **室外场景**：已有稠密点云时直接用表面重建（如Neural Kernel Surface Reconstruction）；仅有稀疏COLMAP时用CityGS-X多GPU并行生成
- **室内场景**（纹理稀疏导致SfM失败）：使用MapAnything（RGB+COLMAP位姿输入）生成稠密点云
- **网格简化**：QEM（Quadric Error Metric）拓扑保留简化，仅保留粗粒度几何结构（108MB→824KB仍可用）
- **聚类划分**：简化网格划分为细粒度三角形簇 $\{L_k\}$，预计算AABB和屏幕空间包围矩形

### 2. 快速代理深度获取（<1ms）
利用GPU硬件光栅化固定功能管线实现极低延迟深度渲染：

**预处理**：网格→QEM简化→三角形簇划分→每簇预计算AABB

**逐帧管线**：
- **Frustum culling**：对6个视锥面，AABB全部在负侧则剔除
- **Hi-Z剔除**：构建层级Z缓冲金字塔 $Z^{(\ell+1)}(u,v) = \max_{x,y\in\{0,1\}} Z^{(\ell)}(2u+x, 2v+y)$，对每簇在适当层级做保守深度测试：$\text{occluded}(L_k) \iff \hat{z}_k \leq \max_{(u,v)\in R_k^{(\ell)}} Z^{(\ell)}(u,v)$
- **Early-Z深度通道**：仅渲染存活簇，fragment shader最小化（仅写深度），硬件Early-Z自动丢弃被遮挡片段
- **零拷贝互操作**：Vulkan渲染→导出深度图为外部FD→CUDA导入为外部内存→映射为PyTorch CUDA张量，全程GPU驻留无CPU往返

结果：1000×1000深度图 < 1ms，比nvdiffrast（32 FPS等效）和3DGS自渲染（54 FPS等效）快一个数量级。

### 3. 遮挡感知剔除（推理）
在单个CUDA kernel中融合视锥剔除和遮挡剔除：

NDC映射到像素：$x_{pix} = \frac{x_{ndc}+1}{2} \cdot W,\quad y_{pix} = \frac{y_{ndc}+1}{2} \cdot H$

硬件深度转线性深度：$d_{mesh}(x_{pix}, y_{pix}) = \frac{nf}{f - z_{hw}(x_{pix}, y_{pix})(f-n)}$

加安全容限：$\hat{d}(x_{pix}, y_{pix}) = d_{mesh}(x_{pix}, y_{pix}) + \varepsilon$

剔除判定：$\text{Cull}(p) = \begin{cases} \text{True} & \text{if } z_h > \hat{d}(x_{pix}, y_{pix}) \\ \text{False} & \text{otherwise} \end{cases}$

锚点级剔除发生在MLP解码之前，节省解码计算量。安全容限 $\varepsilon = 0.3$ 为最优平衡点（太小产生近处伪影，太大引入过多冗余锚点降低FPS）。

### 4. 代理引导密度控制（训练）
标准锚点增密策略在高梯度位置生成新锚点，但忽略了遮挡——被遮挡区域的高斯即使梯度大也对渲染无贡献。

Proxy-GS的改进：
- 将渲染图像划分为patches，计算每patch的平均L1损失 $\bar{P} = \frac{1}{|P|}\sum_{(u,v)\in P} \mathcal{L}(u,v)$
- 筛选高误差patches：$P > \mu + 3\sigma$（$\mu$为帧内平均patch误差）
- 对每个高误差patch取中心像素 $(u_P, v_P)$，读取硬件深度 $z_h(u_P, v_P)$，反投影到3D——将新锚点直接放置在**代理网格表面**上
- 网格去重：维护体素网格（尺寸h），每格最多K个锚点

效果：密度从遮挡区域向可见表面迁移，避免"幽灵几何"——被遮挡但因梯度大而持续存在的高斯。

## 关键数学形式
| 组件 | 公式 |
|------|------|
| MLP解码 | $\{\mu_j, \Sigma_j, c_j, \alpha_j\}_{j=1}^{M} = \text{MLP}_\theta(f_i, v_i)_{i=1}^{N}$ |
| NDC→像素 | $x_{pix} = \frac{x_{ndc}+1}{2}W,\quad y_{pix} = \frac{y_{ndc}+1}{2}H$ |
| 硬件深度→线性深度 | $d_{mesh} = \frac{nf}{f - z_{hw}(f-n)}$ |
| 遮挡剔除 | $\text{Cull}(p) = \mathbf{1}[z_h > d_{mesh} + \varepsilon]$ |
| Hi-Z金字塔 | $Z^{(\ell+1)}(u,v) = \max_{x,y\in\{0,1\}} Z^{(\ell)}(2u+x, 2v+y)$ |
| QEM边折叠 | $x^* = -A^{-1}b,\quad \Delta = E([x^*, 1])$ |

## 与前作的区别
| 前作 | 区别 |
|------|------|
| 3DGS | Proxy-GS针对MLP-based结构化变体，用遮挡先验同时加速训练和推理 |
| Octree-GS | 在LOD基础上增加遮挡感知剔除，解码锚点数减少75%+，速度2.5×以上 |
| Scaffold-GS | 保留锚点框架，增加遮挡感知的锚点选择和表面引导增密 |
| OccluGaussian | 逐像素代理引导过滤（保留细节）vs 场景分簇推理遮挡 |
| Ye et al. [37] | 硬件光栅化代理（<1ms）vs surfel渲染深度图，速度快一个数量级 |
| Cache-GS | Proxy-GS不缓存解码高斯，而是从源头减少需解码的锚点；无质量损失 |
| 标准剪枝（LightGaussian等） | 从贡献度驱动升级为实际几何遮挡驱动，更精确 |

## 实验结论

### 主要结果
**MatrixCity**（5个Block，8477张街景）：
| 方法 | PSNR | SSIM | LPIPS | FPS |
|------|------|------|-------|-----|
| 3DGS | 21.01 | 0.722 | 0.388 | 117 |
| Scaffold-GS | 20.85 | 0.714 | 0.392 | 73 |
| Octree-GS | 21.43 | 0.737 | 0.359 | 37 |
| **Proxy-GS** | **21.62** | **0.749** | **0.347** | **137** |

Proxy-GS在全部5个Block上同时实现最高质量和最高速度（Block 5上PSNR 21.68 vs Octree-GS 21.41，FPS 151 vs 48）。

**真实场景泛化**（Small City强遮挡 / Berlin弱遮挡 / CUHK-LOWER航拍 / ZipNeRF室内）：在所有场景上达到最优或次优。Small City上比Octree-GS FPS提升2.73×（139 vs 51）。

### 消融实验
| ID | 遮挡训练 | 代理引导增密 | 代理引导推理 | PSNR | FPS | 平均锚点数 |
|----|---------|------------|------------|------|-----|----------|
| 1 | | | | 21.41 | 48 | 719k |
| 2 | | | ✓ | 19.06 | 165 | 82k |
| 3 | ✓ | | ✓ | 21.50 | 147 | 93k |
| 4 | ✓ | ✓ | ✓ | 21.68 | 143 | 106k |

- ID 2：仅在测试时剔除→训练-推理不一致导致质量崩溃（-2.35 PSNR）
- ID 3：训练+推理均用遮挡剔除→质量恢复超越基线
- ID 4：加上代理引导增密→最佳质量，FPS略降但仍3×于基线

### 代理质量鲁棒性
- **网格分辨率**：从108MB降到824KB（1%分辨率），PSNR仅降~0.4dB（城市建筑以大平面为主，粗代理仍保持正确遮挡结构）
- **顶点噪声**：≤5%噪声影响有限（锚点-高斯间存在固有偏移提供容差）；≥10%噪声显著破坏遮挡边界，PSNR大幅下降
- **安全容限ε**：ε=0.3最优；ε=0.1产生近处伪影；ε=1.0引入过多冗余锚点降低FPS

### 与硬件3DGS渲染器结合
将Proxy-GS的剔除结果配合硬件3DGS光栅化器：MatrixCity Block 5可达196 FPS（+30%），轻微质量损失（PSNR -0.1）。

### 限制
- 需要代理网格作为输入（依赖稠密点云或额外的重建步骤）
- 室内纹理稀疏场景需MapAnything等前馈模型辅助
- 顶点噪声>5%时性能退化，代理网格质量影响最终效果
- ε需按场景调节

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 对比方法: Octree-GS, Scaffold-GS, Hierarchical-GS, Cache-GS, OccluGaussian
- 涉及概念: [[concepts/mlp-based-3dgs]], [[concepts/3d-gaussian]], [[concepts/occlusion-aware-culling]], [[concepts/proxy-rendering]], [[concepts/adaptive-density-control]], [[concepts/tile-based-rasterization]], [[concepts/alpha-compositing]]
