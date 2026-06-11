# 3D Gaussian Splatting 知识库索引

## 概念 (wiki/concepts/)

### 高斯表示
- [[concepts/3d-gaussian]] — 3D高斯：场景的基本表示单元，带有位置、协方差、不透明度和球谐函数系数的显式椭球体
- [[concepts/covariance-matrix]] — 协方差矩阵：描述高斯椭球形状和方向的3×3正定矩阵
- [[concepts/spherical-harmonics]] — 球谐函数：球面上的正交基函数，编码视角依赖颜色
- [[concepts/relightable-3dgs]] — 可重光照3DGS：将SH替换为物理材质属性（反照率、法向量）+显式光照，支持基于物理的光照编辑

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

### 动态场景与鲁棒性
- [[concepts/temporal-gaussian-model]] — 时序高斯模型：将动态物体表示为随时间变化的高斯椭球体，实现在线增量动态建模
- [[concepts/scene-consistency-analysis]] — 场景一致性分析：通过比较渲染与观测检测运动区域，无需语义先验的动态识别方法
- [[concepts/uncertainty-aware-mapping]] — 不确定性感知建图：利用预测的不确定性指导动态物体移除和建图优化

### 语言场与语义
- [[concepts/language-feature-registration]] — 语言特征注册：直接将CLIP嵌入分配到3D高斯，无需渲染过程的语言-几何关联方法
- [[concepts/3d-language-field]] — 3D语言场：将CLIP语言特征嵌入3D高斯，支持开放词汇3D查询

### 动态场景与鲁棒性
- [[concepts/tri-view-geometric-constraints]] — 三视图几何约束：利用三帧稠密匹配构建跨帧几何约束，抗误匹配能力优于成对几何
- [[concepts/intrinsic-appearance-normalization]] — 内在外观归一化：将场景反照率与瞬态光照解耦，学习光照不变的标准化颜色表示
- [[concepts/uncertainty-aware-tracking]] — 不确定性感知跟踪：利用逐像素不确定性图加权跟踪损失，使优化聚焦信息丰富区域

### 传感器融合
- [[concepts/multi-sensor-fusion]] — 多传感器融合SLAM：统一支持单目、RGB-D、LiDAR-惯性-视觉数据的通用高斯建图框架

## 论文 (wiki/papers/)

### 基础方法
- [[papers/2026-05-07/3d-gaussian-splatting]] — 3DGS (Kerbl et al., SIGGRAPH 2023)：开创性工作，首次实现实时高质量新视角合成

### 扩展方法
- [[papers/2026-05-07/mip-splatting]] — Mip-Splatting (Yu et al., CVPR 2024)：解决3DGS的多尺度混叠问题
- [[papers/2026-05-07/gaussian-opacity-fields]] — GOF (Yu et al., 2024)：从3D高斯原生提取表面几何
- [[papers/2026-05-21/proxy-gs]] — Proxy-GS (Gao et al., arXiv 2025)：快速代理系统生成遮挡深度图，统一训练推理中的遮挡感知，速度比Octree-GS快2.5倍

### 移动端/压缩
- [[papers/2026-05-07/mobile-gs]] — Mobile-GS (Du et al., ICLR 2026)：首个移动端实时3DGS方法，顺序无关渲染+神经增强+压缩，骁龙8 Gen 3上127 FPS @ 4.6 MB

### 应用
- [[papers/2026-05-07/street-gaussians]] — Street Gaussians (Yan et al., ECCV 2024)：动态自动驾驶城市场景建模

### 3DGS-SLAM
- [[papers/2026-05-15/g2-mapping]] — G²-Mapping (IEEE 2025)：首个通用多传感器融合3DGS-SLAM，支持单目/RGB-D/LiDAR输入
- [[papers/2026-05-21/wildgs-slam]] — WildGS-SLAM (Zheng et al., arXiv 2025)：不确定性感知动态SLAM，DINOv2+MLP预测不确定性图引导动态物体移除
- [[papers/2026-06-11/add-slam]] — ADD-SLAM (Wu et al., arXiv 2025)：场景一致性分析自适应识别动态物体，时序高斯模型实现动态-静态分离建图
- [[papers/2026-06-02/up-slam]] — UP-SLAM (Zheng et al., ICRA 2026)：并行跟踪建图+概率八叉树+无训练不确定性估计器，开放集动态物体处理
- [[papers/2026-06-11/roger-slam]] — RoGER-SLAM (Yin et al., arXiv 2025)：噪声/低光鲁棒SLAM，SP-RoFusion多模态融合+CLIP增强
- [[papers/2026-06-08/vimgs-slam]] — ViMGS-SLAM (Array 2026)：多尺度ViT+3DGS单目SLAM，ATE提升46%，PSNR 39.6 dB
- [[papers/2026-05-21/pseudo-depth-meets-gaussian]] — Pseudo Depth (Zhao et al., arXiv 2025)：Feed-forward位姿预测替代测试时优化，跟踪时间减少90%

### 语言场
- [[papers/2026-05-07/langsplat]] — LangSplat (Qin et al., CVPR 2024)：首个3D高斯语言场，CLIP+SAM分层语义，比LERF快199倍
- [[papers/2026-05-08/dr-splat]] — Dr. Splat (Kim et al., arXiv 2025)：直接语言特征注册，无需渲染过程，产品量化压缩嵌入
- [[papers/2026-05-21/langgs-slam]] — LangGS-SLAM (Ha et al., arXiv 2026)：实时语言特征SLAM，Top-K渲染+混合场优化，15 FPS

### 导航
- [[papers/2026-05-28/gaussnav]] — GaussNav (Lei et al., TPAMI 2025)：首次将3DGS引入具身视觉导航，Semantic Gaussian地图+DISK-LightGlue特征匹配实现实例图像目标导航
- [[papers/2026-06-10/zero-shot-uav-navigation]] — Zero-Shot UAV Navigation (Lv et al., 2026)：Relightable 3DGS+端到端RL，零样本sim-to-real森林UAV导航，10 m/s无碰撞飞行

### 鲁棒性与光照
- [[papers/2026-06-11/tvg-slam]] — TVG-SLAM (Tan et al., arXiv 2025)：三视图几何约束纯RGB SLAM，室外场景ATE降低69%
- [[papers/2026-06-11/taming-the-light]] — Taming the Light (Zhang et al., arXiv 2025)：光照不变语义SLAM，IAN主动去耦+DRB-Loss被动纠正
- [[papers/2026-06-11/varsplat]] — VarSplat (Tran & Kosecka, arXiv 2026)：不确定性感知RGB-D SLAM，逐高斯方差+单pass不确定性渲染

### 神经3D重建
- [[papers/2026-05-09/vggt]] — VGGT (CVPR 2025 Best Paper)：交替注意力机制的前馈3D重建，从稀疏视图直接预测点图

## 综合专题 (wiki/synthesis/)

- [[synthesis/dynamic-slam-comparison]] — 动态/鲁棒3DGS-SLAM方法对比（WildGS-SLAM, ADD-SLAM, UP-SLAM, RoGER-SLAM）
- [[synthesis/robustness-dimensions]] — 3DGS-SLAM鲁棒性维度分解（测量/光照/几何三维度 + 组合矩阵 + 统一不确定性视角）
