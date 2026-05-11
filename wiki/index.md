# 3D Gaussian Splatting — Knowledge Base

## Papers

### Base
- [[papers/3d-gaussian-splatting|3D Gaussian Splatting for Real-Time Radiance Field Rendering]] (Kerbl et al., SIGGRAPH 2023)

### Extensions
- [[papers/mip-splatting|Mip-Splatting: Alias-free 3D Gaussian Splatting]] (Yu et al., CVPR 2024)
- [[papers/gaussian-opacity-fields|Gaussian Opacity Fields]] (Yu et al., arxiv 2024)
- [[papers/mobile-gs|Mobile-GS: Real-time Gaussian Splatting for Mobile Devices]] (2024)
- [[papers/langsplat|LangSplat: 3D Language Gaussian Splatting]] (Qin et al., CVPR 2024)
- [[papers/dr-splat|Dr. Splat: Direct Language Embedding Registration]] (Kim et al., CVPR 2025 Highlight)

### Applications
- [[papers/street-gaussians|Street Gaussians: Modeling Dynamic Urban Scenes]] (Yan et al., ECCV 2024)
- [[papers/gs-livo|GS-LIVO: Real-Time LiDAR-Inertial-Visual Odometry With Gaussian Mapping]] (Hong et al., IEEE TRO 2025)

### Related Methods
- [[papers/vggt|VGGT: Visual Geometry Grounded Transformer]] (Wang et al., CVPR 2025 Best Paper)

---

## Concepts

### Core Representation
- [[concepts/3d-gaussian|3D高斯]]
- [[concepts/covariance-matrix|协方差矩阵]]
- [[concepts/spherical-harmonics|球谐函数]]

### Rendering
- [[concepts/projection-transform|投影变换]]
- [[concepts/tile-based-rasterization|Tile-based光栅化]]
- [[concepts/alpha-compositing|Alpha合成]]
- [[concepts/order-independent-rendering|顺序无关渲染]]

### Training & Optimization
- [[concepts/adaptive-density-control|自适应密度控制]]
- [[concepts/ssim-loss|SSIM损失]]

### Compression
- [[concepts/gaussian-compression|高斯压缩]]
- [[concepts/neural-view-dependent-enhancement|神经视角依赖增强]]
- [[concepts/product-quantization|乘积量化]]

### Semantics
- [[concepts/3d-language-field|3D语言场]]

### 3D Vision Foundations
- [[concepts/structure-from-motion|运动恢复结构（SfM）]]

### SLAM & State Estimation
- [[concepts/slam|SLAM（同步定位与建图）]]
- [[concepts/ieskf|IESKF（迭代误差状态卡尔曼滤波）]]

### Comparison Methods
- [[concepts/nerf|NeRF]]
- [[concepts/instant-ngp|Instant-NGP]]
- [[concepts/mip-nerf|Mip-NeRF]]
- [[concepts/tensorf|TensoRF]]
