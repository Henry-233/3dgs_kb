# 3D Gaussian Splatting — Knowledge Base

## Papers

### Base
- [[papers/2026-05/3d-gaussian-splatting|3D Gaussian Splatting for Real-Time Radiance Field Rendering]] (Kerbl et al., SIGGRAPH 2023)

### Extensions
- [[papers/2026-05/mip-splatting|Mip-Splatting: Alias-free 3D Gaussian Splatting]] (Yu et al., CVPR 2024)
- [[papers/2026-05/gaussian-opacity-fields|Gaussian Opacity Fields]] (Yu et al., arxiv 2024)
- [[papers/2026-05/mobile-gs|Mobile-GS: Real-time Gaussian Splatting for Mobile Devices]] (2024)
- [[papers/2026-05/langsplat|LangSplat: 3D Language Gaussian Splatting]] (Qin et al., CVPR 2024)
- [[papers/2026-05/dr-splat|Dr. Splat: Direct Language Embedding Registration]] (Kim et al., CVPR 2025 Highlight)
- [[papers/2026-05/proxy-gs|Proxy-GS: Unified Occlusion Priors for Structured 3DGS]] (Gao et al., arxiv 2025)

### Applications
- [[papers/2026-05/street-gaussians|Street Gaussians: Modeling Dynamic Urban Scenes]] (Yan et al., ECCV 2024)
- [[papers/2026-05/gs-livo|GS-LIVO: Real-Time LiDAR-Inertial-Visual Odometry With Gaussian Mapping]] (Hong et al., IEEE TRO 2025)
- [[papers/2026-05/g2-mapping|G²-Mapping: General Gaussian Mapping for Monocular, RGB-D, and LiDAR-Inertial-Visual Systems]] (Chen et al., IEEE TASE 2025)
- [[papers/2026-05/wildgs-slam|WildGS-SLAM: Monocular Gaussian Splatting SLAM in Dynamic Environments]] (Zheng et al., arxiv 2025)
- [[papers/2026-05/pseudo-depth-meets-gaussian|Pseudo Depth Meets Gaussian: A Feed-forward RGB SLAM Baseline]] (Zhao et al., arxiv 2025)
- [[papers/2026-05/langgs-slam|LangGS-SLAM: Real-Time Language-Feature Gaussian Splatting SLAM]] (Ha et al., arxiv 2026)
- [[papers/2026-06/up-slam|UP-SLAM: Adaptively Structured Gaussian SLAM with Uncertainty Prediction]] (Zheng et al., ICRA 2026)
- [[papers/2026-06/vimgs-slam|ViMGS-SLAM: A real-time monocular 3DGS-based SLAM via multiscale vision transformers]] (Zhu et al., Array 2026)
- [[papers/2026-05/gaussnav|GaussNav: Gaussian Splatting for Visual Navigation]] (Lei et al., TPAMI 2025)

### Related Methods
- [[papers/2026-05/vggt|VGGT: Visual Geometry Grounded Transformer]] (Wang et al., CVPR 2025 Best Paper)

---

## Concepts

### Core Representation
- [[concepts/3d-gaussian|3D高斯]]
- [[concepts/covariance-matrix|协方差矩阵]]
- [[concepts/spherical-harmonics|球谐函数]]
- [[concepts/mlp-based-3dgs|MLP驱动的3DGS]]

### Rendering
- [[concepts/projection-transform|投影变换]]
- [[concepts/tile-based-rasterization|Tile-based光栅化]]
- [[concepts/alpha-compositing|Alpha合成]]
- [[concepts/top-k-rendering|Top-K渲染]]
- [[concepts/order-independent-rendering|顺序无关渲染]]
- [[concepts/occlusion-aware-culling|遮挡感知剔除]]
- [[concepts/proxy-rendering|代理渲染]]

### Training & Optimization
- [[concepts/adaptive-density-control|自适应密度控制]]
- [[concepts/ssim-loss|SSIM损失]]
- [[concepts/hybrid-field-optimization|混合场优化]]
- [[concepts/isotropic-regularization|各向同性正则化]]

### Compression
- [[concepts/gaussian-compression|高斯压缩]]
- [[concepts/neural-view-dependent-enhancement|神经视角依赖增强]]
- [[concepts/product-quantization|乘积量化]]

### Semantics
- [[concepts/3d-language-field|3D语言场]]

### 3D Vision Foundations
- [[concepts/structure-from-motion|运动恢复结构（SfM）]]
- [[concepts/point-map|点图（Point Map）]]

### Neural 3D Reconstruction
- [[concepts/feed-forward-3d-reconstruction|前馈式3D重建]]
- [[concepts/alternating-attention|交替注意力（Alternating-Attention）]]

### SLAM & State Estimation
- [[concepts/slam|SLAM（同步定位与建图）]]
- [[concepts/ieskf|IESKF（迭代误差状态卡尔曼滤波）]]
- [[concepts/uncertainty-aware-mapping|不确定性感知建图]]
- [[concepts/parallel-tracking-mapping|并行跟踪与建图]]
- [[concepts/bundle-adjustment|Bundle Adjustment / DBA]]
- [[concepts/feed-forward-pose-prediction|前馈式位姿预测]]
- [[concepts/local-graph-rendering|局部图渲染 (LGR)]]
- [[concepts/monocular-depth-estimation|单目深度估计]]

### Geometry & Scaling
- [[concepts/differentiable-rendering|可微渲染]]
- [[concepts/surface-reconstruction-from-3dgs|3DGS表面重建]]
- [[concepts/spatial-data-structures|空间数据结构]]
- [[concepts/probabilistic-octree|概率八叉树]]

### External Models
- [[concepts/clip|CLIP]]
- [[concepts/sam|SAM]]
- [[concepts/dinov2|DINOv2]]
- [[concepts/vision-transformer|视觉Transformer（ViT）]]

### Embodied AI & Navigation
- [[concepts/visual-navigation|视觉导航（Visual Navigation）]]

### Comparison Methods
- [[concepts/nerf|NeRF]]
- [[concepts/instant-ngp|Instant-NGP]]
- [[concepts/mip-nerf|Mip-NeRF]]
- [[concepts/tensorf|TensoRF]]

---

## Meta
- [[log|Ingest Log]] — 记录所有变更历史
- [[synthesis/timeline|3DGS发展时间线]] — 论文年代脉络与研究主线
