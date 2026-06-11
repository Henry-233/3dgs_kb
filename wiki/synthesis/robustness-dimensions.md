---
title: "3DGS-SLAM鲁棒性维度分解"
tags:
  - synthesis
  - robust-slam
  - 3dgs
---

## 概述

3DGS-SLAM系统面临多种退化条件，每种条件破坏SLAM的不同环节。VarSplat、Taming the Light、TVG-SLAM三篇论文恰好覆盖了三个正交的鲁棒性维度——测量不确定性、光照不变性、几何约束——构成了一个"鲁棒性三角"。

## 鲁棒性三角

```
           测量鲁棒性 (VarSplat)
           ┌─ 方差学习 + 不确定性加权跟踪
           │  "传感器给我的信号有多可靠？"
          ╱ ╲
         ╱   ╲
        ╱     ╲
  光照鲁棒性 ───── 几何鲁棒性
(Taming the Light)   (TVG-SLAM)
 IAN + DRB-Loss      三视图约束 + DART
"场景看起来该什么样？"  "我在哪里？"
```

## 核心差异一览

| 维度 | VarSplat | Taming the Light | TVG-SLAM |
|------|----------|------------------|----------|
| **退化类型** | 传感器噪声/深度不确定性 | 极端曝光变化(过曝/欠曝) | 视角剧变+光照变化 |
| **退化影响环节** | 跟踪+建图（深度信号不可靠） | 外观渲染（颜色不一致） | 跟踪（光度假设失效） |
| **核心机制** | 逐高斯外观方差σ² | IAN颜色量化(64色) + DRB-Loss | 三焦张量几何约束 |
| **机制类型** | 概率建模(学习不确定性) | 表示学习(解耦反照率/光照) | 几何优化(多视图约束) |
| **是否需要学习** | 是(Gaussian NLL优化方差) | 否(量化是结构约束) | 否(三焦张量是几何公式) |
| **传感器** | RGB-D | RGB-D + 语义 | RGB-only |
| **室内/室外** | 室内为主 | 室内 | 室外为主 |
| **运行时代价** | 方差渲染额外开销 | 量化可忽略 | 稠密匹配400ms |
| **正常条件影响** | 零(方差自动适应) | 零(DRB仅在SSIM<0.5激活) | 零(DART在地图新时高权重) |

## 三者的互补关系

### 1. 为什么不能互替

- **VarSplat不能替代Taming the Light**：方差学习告诉系统"渲染不可靠"，但不能修复颜色本身——曝光错误时方差高但恢复不了正确颜色
- **Taming the Light不能替代TVG-SLAM**：IAN让颜色对光照不变，但跟踪仍依赖光度——视角偏移导致的内容变化IAN无法处理
- **TVG-SLAM不能替代VarSplat**：三视图约束给定位姿锚点，但深度噪声仍影响建图质量——需要方差加权

### 2. 组合可能性

理想鲁棒SLAM系统应同时具备三维度：

| 场景 | VarSplat贡献 | Taming the Light贡献 | TVG-SLAM贡献 |
|------|-------------|---------------------|-------------|
| **正常室内** | 轻微提升(噪声自适应) | 零(DRB不激活) | 零(几何约束冗余) |
| **低纹理室内** | 不确定性标记困难区 | 无效(光照正常) | **关键**(三焦约束替代光度) |
| **过曝室内** | 中(标记过曝区不可靠) | **关键**(反照率不变+DRB补偿) | 中(几何约束不依赖颜色) |
| **室外长直道** | 低(RGB-D不可用) | 低(光照变化但无极端曝光) | **关键**(抑制低视差漂移) |
| **室外急速转向** | 低 | 低 | **关键**(几何锚定处理视角跳变) |
| **噪声+低光** | **关键**(深度方差自适应) | 无效(63色丢失暗区细节) | 中(三视图匹配在低光退化) |

### 3. 冲突点

- **TVG-SLAM vs VarSplat**：TVG-SLAM是RGB-only，VarSplat依赖深度输入——传感器模态不同，无法直接组合
- **Taming the Light vs VarSplat**：IAN量化可能放大暗区的深度不确定性（颜色信息丢失→深度估计更难），VarSplat的方差会在暗区增大
- **Taming the Light vs TVG-SLAM**：无直接冲突，光照不变反照率可以辅助三视图的特征匹配

## 统一视角：不确定性的三种来源

三个论文实际处理了SLAM中不确定性的三种不同来源：

| 不确定性类型 | 来源 | 表现形式 | 解决方案 |
|-------------|------|---------|---------|
| **偶然不确定性(Aleatoric)** | 传感器噪声 | 深度/颜色测量的逐像素方差 | VarSplat: 高斯NLL学习σ² |
| **环境不确定性(Environmental)** | 光照变化 | 同一场景点在不同光照下颜色不同 | Taming the Light: IAN解耦反照率 |
| **几何不确定性(Geometric)** | 视角变化/运动 | 光度一致性消失，跟踪漂移 | TVG-SLAM: 三视图几何约束 |

这三种不确定性是加性的——即使光照稳定（无环境不确定性），传感器噪声（偶然不确定性）仍存在；即使传感器完美（无偶然不确定性），大视角变化下的几何退化（几何不确定性）仍需处理。

## 关键数字速查

| 论文 | 关键指标 | 最佳 | 基线 | 提升 |
|------|---------|------|------|------|
| VarSplat | Replica ATE | 0.23 cm | 0.36 cm (SplaTAM) | 36% |
| Taming the Light | Replica ATE | 0.34 cm | 0.63 cm (ESLAM) | 46% |
| TVG-SLAM | Cambridge ATE | 2.009 m | 6.490 m (OpenGS) | 69% |
| VarSplat | TUM ATE | 3.20 cm | 5.48 cm | 42% |
| TVG-SLAM | Waymo PSNR | 25.38 | 23.99 (OpenGS) | +1.39 dB |
| Taming the Light | Replica mIoU | 92.69% | — | SOTA语义 |

## 关联论文

- [[papers/varsplat]] — 测量不确定性（外观方差学习）
- [[papers/taming-the-light]] — 光照不变性（IAN + DRB-Loss）
- [[papers/tvg-slam]] — 几何约束（三视图匹配 + DART + TUGI）
- [[synthesis/dynamic-slam-comparison]] — 动态SLAM对比（互补视角：动态物体 vs 传感器/光照/几何退化）

## 关联概念

- [[concepts/uncertainty-aware-tracking]] — 三种不确定性感知实现方案对比
- [[concepts/intrinsic-appearance-normalization]] — IAN机制详解
- [[concepts/tri-view-geometric-constraints]] — 三视图几何约束机制详解
