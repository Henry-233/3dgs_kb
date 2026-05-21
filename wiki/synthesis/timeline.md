---
title: "3DGS发展时间线"
tags: [synthesis, timeline]
---

# 3D Gaussian Splatting 发展时间线

## 2023 — 奠基之年

| 论文 | 会议/期刊 | 贡献 |
|------|-----------|------|
| **[[papers/3d-gaussian-splatting\|3DGS]]** (Kerbl et al.) | SIGGRAPH 2023 | 开创性工作：显式3D高斯椭球体 + 自适应密度控制 + tile-based可微光栅化，首次实现1080p ≥30FPS实时高质量新视角合成 |

核心突破：用可微高斯光栅化替代NeRF的MLP体渲染，训练时间和渲染速度均获数量级提升，奠定了整个3DGS研究范式的基石。

## 2024 — 扩展与应用元年

| 论文 | 会议/期刊 | 贡献 |
|------|-----------|------|
| **[[papers/mip-splatting\|Mip-Splatting]]** (Yu et al.) | CVPR 2024 | 解决3DGS的混叠伪影：引入3D频率滤波器，在不同分辨率下保持渲染质量 |
| **[[papers/langsplat\|LangSplat]]** (Qin et al.) | CVPR 2024 | 3DGS语义化：SAM+CLIP蒸馏到3D高斯，开放词汇3D查询，比NeRF-based方法快200倍 |
| **[[papers/gaussian-opacity-fields\|Gaussian Opacity Fields]]** (Yu et al.) | arxiv 2024 | 3DGS几何化：从不透明度场直接提取表面，无需Poisson重建或TSDF融合 |
| **[[papers/street-gaussians\|Street Gaussians]]** (Yan et al.) | ECCV 2024 | 动态场景：4D球谐函数+位姿优化，适用于复杂城市场景建模 |
| **[[papers/mobile-gs\|Mobile-GS]]** | arxiv 2024 | 移动端部署：高斯压缩+顺序无关渲染，将3DGS推向移动设备 |

2024年是3DGS从"能工作"到"能用好"的关键一年——解决了混叠（Mip-Splatting）、赋予语义（LangSplat）、提取几何（GOF）、处理动态（Street Gaussians）、压缩部署（Mobile-GS），覆盖了从质量到效率到应用的完整谱系。

## 2025 — 系统化与SLAM时代

### 前馈式3D基础模型
| 论文 | 会议/期刊 | 贡献 |
|------|-----------|------|
| **[[papers/vggt\|VGGT]]** (Wang et al.) | CVPR 2025 **Best Paper** | 前馈Transformer一次性预测相机/深度/点图/轨迹，<1秒推理，替代COLMAP作为3DGS初始化前端 |

### 语言场精细化
| 论文 | 会议/期刊 | 贡献 |
|------|-----------|------|
| **[[papers/dr-splat\|Dr. Splat]]** (Kim et al.) | CVPR 2025 **Highlight** | 直接语言特征注册替代渲染训练，通用PQ替代逐场景自编码器，零样本跨场景泛化 |

### Gaussian SLAM 三连发
| 论文 | 会议/期刊 | 贡献 |
|------|-----------|------|
| **[[papers/gs-livo\|GS-LIVO]]** (Hong et al.) | IEEE TRO 2025 | 首个嵌入式Gaussian-SLAM：LiDAR-惯性-视觉融合 + 哈希八叉树全局地图，Jetson Orin NX上实时运行 |
| **[[papers/g2-mapping\|G²-Mapping]]** (Chen et al.) | IEEE TASE 2025 | 首个通用三模态框架（单目/RGB-D/LIV）：完整可微渲染器（颜色+深度+位姿），RGB-D ATE仅1.21cm |
| **[[papers/wildgs-slam\|WildGS-SLAM]]** (Zheng et al.) | arxiv 2025 | 首个动态环境Gaussian SLAM：DINOv2在线预测不确定性，纯单目RGB，无需语义分割或深度传感器 |
| **[[papers/pseudo-depth-meets-gaussian\|Pseudo Depth Meets Gaussian]]** (Zhao et al.) | arxiv 2025 | 首个前馈式Gaussian SLAM基线：RNN直接从光流预测位姿替代迭代优化，跟踪速度>10×提升 |

### 结构化与遮挡感知
| 论文 | 会议/期刊 | 贡献 |
|------|-----------|------|
| **[[papers/proxy-gs\|Proxy-GS]]** (Gao et al.) | arxiv 2025 | 代理网格+硬件光栅化实现<1ms遮挡深度获取，MLP-based 3DGS的3×推理加速和遮挡感知训练 |

2025年的主题是"系统化"——3DGS不再只是新视角合成工具，而是演进为完整的感知-建图-定位系统。Gaussian-SLAM覆盖了嵌入式部署（GS-LIVO）、多模态通用（G²-Mapping）、动态场景（WildGS-SLAM）、前馈式跟踪（Pseudo Depth Meets Gaussian）四个维度。同时VGGT将3DGS初始化从COLMAP（分钟级）推到前馈推理（秒级），标志着3DGS从"逐场景优化"向"前馈式通用化"的范式迁移。

## 2026 — 语义SLAM时代开启

| 论文 | 会议/期刊 | 贡献 |
|------|-----------|------|
| **[[papers/langgs-slam\|LangGS-SLAM]]** (Ha et al.) | arxiv 2026 | 首个在线实时语言特征Gaussian SLAM：Top-K渲染替代alpha-blending做高维特征渲染（消除语义歧义），无压缩存储原始VLM特征，15 FPS同时超越纯几何SOTA的几何精度和离线方法的语义保真度 |

2026年的LangGS-SLAM标志着3DGS从"纯几何SLAM"向"几何+语义双场SLAM"的融合——将LangSplat等离线语言场的高斯语义嵌入范式首次以在线实时方式实现，同时通过Top-K渲染解决了alpha-blending在高维特征上的语义歧义本质缺陷。

## 研究主线分化

```
                    ┌── 语义语言场 ─── LangSplat (2024) → Dr. Splat (2025)
                    │                                      └→ LangGS-SLAM (2026)
                    │
3DGS (SIGGRAPH 2023) ──┼── 表面重建 ───── GOF (2024)
                    │
                    ├── 渲染质量 ───── Mip-Splatting (2024) → Mobile-GS (2024)
                    │
                    ├── 动态场景 ───── Street Gaussians (2024) → WildGS-SLAM (2025)
                    │
                    ├── Gaussian SLAM ─ GS-LIVO (2025) → G²-Mapping (2025)
                    │                      │                   └→ WildGS-SLAM (2025)
                    │                      ├→ Pseudo Depth Meets Gaussian (2025)
                    │                      └→ LangGS-SLAM (2026)
                    │
                    ├── 结构化/加速 ── Proxy-GS (2025)
                    │
                    └── 前馈范式 ─── VGGT (2025) → Pseudo Depth Meets Gaussian (2025)
```

## 关联
- [[papers/3d-gaussian-splatting]]
- [[../index|返回知识库首页]]
