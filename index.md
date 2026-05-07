# 3D Gaussian Splatting 知识库索引

## 概念 (wiki/concepts/)

### 高斯表示
- [[concepts/3d-gaussian]] — 3D高斯：场景的基本表示单元，带有位置、协方差、不透明度和球谐函数系数的显式椭球体
- [[concepts/covariance-matrix]] — 协方差矩阵：描述高斯椭球形状和方向的3×3正定矩阵
- [[concepts/spherical-harmonics]] — 球谐函数：球面上的正交基函数，编码视角依赖颜色

### 渲染管线
- [[concepts/projection-transform]] — 投影变换：将3D高斯映射到2D图像平面的数学操作
- [[concepts/alpha-compositing]] — Alpha合成：按透明度加权累加颜色的可微渲染核心
- [[concepts/tile-based-rasterization]] — Tile-based光栅化：将屏幕分tile并行处理，实现实时渲染的关键算法
- [[concepts/order-independent-rendering]] — 顺序无关渲染：无需深度排序的透明度合成方案，消除移动端渲染瓶颈
- [[concepts/neural-view-dependent-enhancement]] — 神经视角依赖增强：用MLP预测视角依赖不透明度和权重，补偿顺序无关渲染的伪影

### 训练优化
- [[concepts/adaptive-density-control]] — 自适应密度控制：训练中动态克隆、分裂和剪枝高斯的优化策略
- [[concepts/gaussian-compression]] — 高斯压缩：通过向量量化、SH蒸馏和剪枝减少模型体积，实现移动端部署
- [[concepts/ssim-loss]] — SSIM Loss：结构相似性损失函数，与L1组合用于训练

### 对比方法
- [[concepts/nerf]] — NeRF：神经辐射场，用MLP隐式表示场景的开创性方法
- [[concepts/instant-ngp]] — Instant-NGP：多分辨率哈希编码加速NeRF训练
- [[concepts/mip-nerf]] — Mip-NeRF：用锥形截锥体解决多尺度混叠的NeRF改进
- [[concepts/tensorf]] — TensoRF：用张量分解压缩辐射场表示的混合方案

## 论文 (wiki/papers/)

### 基础方法
- [[papers/3d-gaussian-splatting]] — 3DGS (Kerbl et al., SIGGRAPH 2023)：开创性工作，首次实现实时高质量新视角合成

### 扩展方法
- [[papers/mip-splatting]] — Mip-Splatting (Yu et al., CVPR 2024)：解决3DGS的多尺度混叠问题
- [[papers/gaussian-opacity-fields]] — GOF (Yu et al., 2024)：从3D高斯原生提取表面几何

### 移动端/压缩
- [[papers/mobile-gs]] — Mobile-GS (Du et al., ICLR 2026)：首个移动端实时3DGS方法，顺序无关渲染+神经增强+压缩，骁龙8 Gen 3上127 FPS @ 4.6 MB

### 应用
- [[papers/street-gaussians]] — Street Gaussians (Yan et al., ECCV 2024)：动态自动驾驶城市场景建模
