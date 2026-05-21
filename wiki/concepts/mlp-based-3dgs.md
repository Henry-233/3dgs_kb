---
title: "MLP驱动的3DGS"
tags: [concept, representation]
---

## 定义
MLP-based 3DGS（或称结构化3DGS / Structured 3DGS）是3D Gaussian Splatting的一个变体家族，其核心思想是用多层感知机（MLP）神经网络动态生成高斯属性，而非像原始3DGS那样直接优化每个高斯的参数。通过引入结构化锚点（anchor points）和神经解码器，这类方法显著提升了表示能力和渲染质量，但代价是推理时需要额外的MLP解码计算。

## 直觉理解
原始3DGS像一个每个演员（高斯）独立即兴表演的剧团——每个演员自己决定位置、颜色、形状，灵活但缺乏协调。MLP-based 3DGS则像一个有导演（MLP解码器）的剧团——导演根据场景结构（锚点+视角）统一指导演员的表演，效果更精致，但每次演出前导演需要额外时间调度。

## 数学形式
给定锚点特征 $f_i$ 和视角方向 $v_i$：

$$\{\mu_j, \Sigma_j, c_j, \alpha_j\}_{j=1}^{M} = \text{MLP}_\theta(f_i, v_i)_{i=1}^{N}$$

其中 $\theta$ 为MLP参数，每个锚点 $i$ 解码出 $M$ 个高斯。解码后的高斯与原始3DGS以相同方式光栅化。

**与原始3DGS的关键区别**：
- 原版3DGS：每个高斯的属性（$\mu, \Sigma, c, \alpha$）是直接优化的参数
- MLP-based：高斯属性由MLP根据锚点特征和视角动态生成，参数存在于MLP权重中

## 主要变体

### Scaffold-GS
- 从SfM稀疏点云构建粗体素网格，在体素中心放置锚点
- 每个锚点携带隐式特征向量，MLP解码出关联的高斯属性
- 优势：继承SfM结构先验，减少冗余，提升新视角鲁棒性

### Octree-GS
- 将Scaffold-GS的体素网格替换为显式八叉树表示
- 八叉树层级结构天然支持LOD：根据相机距离自适应选择层级
- 优势：大规模场景可扩展性更好，远距离用粗层级节省解码

### Proxy-GS
- 在Octree-GS锚点框架上增加遮挡感知
- 代理网格+硬件光栅化快速获取遮挡深度图
- 训练时用遮挡引导锚点增密，推理时剔除被遮挡锚点

## 优势与代价
| 维度 | 原始3DGS | MLP-based 3DGS |
|------|---------|----------------|
| 表示能力 | 受限于显式参数 | MLP解码增强视角依赖细节 |
| 结构先验 | 无 | 锚点网格/八叉树提供几何结构 |
| 推理速度 | 快（无解码） | 需MLP前向传播，较慢 |
| 高斯效率 | 需大量高斯拟合细节 | 锚点+解码器更紧凑 |
| 可扩展性 | 大场景冗余严重 | LOD天然支持大场景 |

## 关联
- 相关概念: [[concepts/3d-gaussian]], [[concepts/adaptive-density-control]], [[concepts/occlusion-aware-culling]]
- 用到该概念的论文: [[papers/proxy-gs]]
- 该领域论文: Scaffold-GS, Octree-GS, Cache-GS
