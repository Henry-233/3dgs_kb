# 3DGS Knowledge Base — Directory Manifest

用于跨设备同步时保持文件路径一致。新文件请同步更新此文档。

## 目录结构

```
3dgs-kb/
├── index.md                          # 知识库主索引（概念+论文列表）
├── log.md                            # 操作日志
├── progress.md                       # 学习进度追踪
├── prompts.md                        # AI提示词模板
├── CLAUDE.md                         # Claude Code 项目配置
├── doc.md                            # 本文件：目录清单
│
├── raw/                              # 原始资料（未经整理的输入）
│   ├── papers/                       #   论文原文（Markdown知识库）
│   │   ├── 3D Gaussian Splatting for Real-Time Radiance Field Rendering.md
│   │   ├── Dr. Splat Directly Referring 3D Gaussian Splatting via Direct Language Embedding Registration.md
│   │   ├── G-Mapping_General_Gaussian_Mapping_for_Monocular_RGB-D_and_LiDAR-Inertial-Visual_Systems.md
│   │   ├── G-Mapping_General_Gaussian_Mapping_for_Monocular_RGB-D_and_LiDAR-Inertial-Visual_Systems.pdf
│   │   ├── G-Mapping_General_Gaussian_Mapping_for_Monocular_RGB-D_and_LiDAR-Inertial-Visual_Systems_annotated.pdf
│   │   ├── G-Mapping_General_Gaussian_Mapping_for_Monocular_RGB-D_and_LiDAR-Inertial-Visual_Systems_annotations.json
│   │   ├── GS-LIVO Real-Time LiDAR, Inertial, and Visual Multisensor Fused Odometry With Gaussian Mapping.pdf
│   │   ├── Gaussian Opacity Fields Efficient Adaptive Surface Reconstruction in Unbounded Scenes.md
│   │   ├── LangSplat 3D Language Gaussian Splatting.md
│   │   ├── LangSplat 3D Language Gaussian Splatting.pdf
│   │   ├── LangSplat 3D Language Gaussian Splatting_annotated.pdf
│   │   ├── LangSplat 3D Language Gaussian Splatting_annotations.json
│   │   ├── Mip-Splatting Alias-free 3D Gaussian Splatting.md
│   │   ├── Mobile-GS Real-time Gaussian Splatting for Mobile Devices.md
│   │   ├── Mobile-GS Real-time Gaussian Splatting for Mobile Devices.pdf
│   │   ├── Mobile-GS Real-time Gaussian Splatting for Mobile Devices_annotated.pdf
│   │   ├── Mobile-GS Real-time Gaussian Splatting for Mobile Devices_annotations.json
│   │   ├── Street Gaussians Modeling Dynamic Urban Scenes with Gaussian Splatting.md
│   │   ├── VGGT Visual Geometry Grounded Transformer.md
│   │   └── VGGT Visual Geometry Grounded Transformer.pdf
│   ├── blogs/                        #   博客文章（待填充）
│   └── videos/                       #   视频资料（待填充）
│
├── wiki/                             # 知识库（整理后的笔记）
│   ├── index.md                      #   Wiki索引
│   ├── log.md                        #   Wiki变更日志
│   │
│   ├── concepts/                     #   核心概念（每个概念一页）
│   │   ├── 3d-gaussian.md            #   3D高斯：场景基本表示单元
│   │   ├── 3d-language-field.md      #   3D语言场：CLIP特征嵌入到3D空间
│   │   ├── adaptive-density-control.md # 自适应密度控制：克隆/分裂/剪枝
│   │   ├── alpha-compositing.md      #   Alpha合成：透明度加权累加
│   │   ├── alternating-attention.md  #   交替注意力：帧间特征匹配机制
│   │   ├── covariance-matrix.md      #   协方差矩阵：高斯形状描述
│   │   ├── feed-forward-3d-reconstruction.md # 前馈3D重建：直接从图像预测3D
│   │   ├── gaussian-compression.md   #   高斯压缩：向量量化+SH蒸馏+剪枝
│   │   ├── ieskf.md                  #   IESKF：迭代误差状态卡尔曼滤波
│   │   ├── instant-ngp.md            #   Instant-NGP：多分辨率哈希编码
│   │   ├── mip-nerf.md               #   Mip-NeRF：锥形截锥体反混叠
│   │   ├── nerf.md                   #   NeRF：神经辐射场基础
│   │   ├── neural-view-dependent-enhancement.md # 神经视角依赖增强
│   │   ├── order-independent-rendering.md # 顺序无关渲染
│   │   ├── point-map.md              #   点图：逐像素3D坐标预测
│   │   ├── product-quantization.md   #   乘积量化：向量压缩技术
│   │   ├── projection-transform.md   #   投影变换：3D→2D映射
│   │   ├── slam.md                   #   SLAM：同步定位与建图
│   │   ├── spherical-harmonics.md    #   球谐函数：视角依赖颜色编码
│   │   ├── ssim-loss.md              #   SSIM损失：结构相似性度量
│   │   ├── structure-from-motion.md  #   SfM：运动推断结构
│   │   ├── tensorf.md                #   TensoRF：张量分解辐射场
│   │   └── tile-based-rasterization.md # Tile-based光栅化：分块并行渲染
│   │
│   ├── papers/                       #   论文笔记（每篇论文一页）
│   │   ├── 3d-gaussian-splatting.md  #   3DGS (SIGGRAPH 2023)：开创性工作
│   │   ├── dr-splat.md               #   Dr. Splat：语言引导的3D指代定位
│   │   ├── g2-mapping.md             #   G-Mapping：通用高斯建图框架
│   │   ├── gaussian-opacity-fields.md # GOF：高斯不透明度场提取表面
│   │   ├── gs-livo.md                #   GS-LIVO：LiDAR-惯性-视觉融合SLAM
│   │   ├── langsplat.md              #   LangSplat：3D语言高斯泼溅
│   │   ├── mip-splatting.md          #   Mip-Splatting (CVPR 2024)：无混叠
│   │   ├── mobile-gs.md              #   Mobile-GS (ICLR 2026)：移动端实时
│   │   ├── street-gaussians.md       #   Street Gaussians (ECCV 2024)：城市场景
│   │   └── vggt.md                   #   VGGT：视觉几何Transformer
│   │
│   └── synthesis/                    #   综述/对比（待填充）
│
├── Clippings/                        # Obsidian Clipper 抓取的文章
│   └── GS-LIVO Real-Time LiDAR, Inertial, and Visual Multisensor Fused Odometry With Gaussian Mapping.md
│
├── scripts/                          # 工具脚本
│   └── annotate_pdf.py              #   PDF标注工具
│
├── output/                           # 输出文件（渲染结果、图表等，待填充）
│
└── .claude/                          # Claude Code 配置（不同步）
    ├── settings.json
    └── settings.local.json
```

## 路径约定

| 路径 | 说明 |
|------|------|
| `raw/papers/` | 原始论文（PDF + Markdown知识库导出 + 标注文件） |
| `wiki/concepts/` | 核心概念笔记，每个概念一个 `.md` 文件 |
| `wiki/papers/` | 论文笔记，每篇论文一个 `.md` 文件 |
| `wiki/synthesis/` | 方法对比、发展时间线、综述 |
| `Clippings/` | Obsidian Clipper 浏览器插件抓取 |
| `scripts/` | 辅助工具脚本 |
| `output/` | 生成的图表、渲染结果等 |

## 文件命名规范

- **概念文件**：小写短横线命名，如 `tile-based-rasterization.md`
- **论文文件**：小写短横线命名，以缩写/简称命名，如 `mobile-gs.md`
- **PDF文件**：保留论文完整标题，空格用下划线，如 `Mobile-GS_Real-time_Gaussian_Splatting_for_Mobile_Devices.pdf`
- **标注文件**：`{PDF文件名}_annotated.pdf` 和 `{PDF文件名}_annotations.json`