---
title: "Tile-based光栅化"
tags: [concept, rendering]
---

## 定义
Tile-based光栅化是3DGS中实现实时渲染的关键算法。不同于逐像素遍历所有高斯，该算法将屏幕划分为16×16像素的tile（瓦片），每个tile只处理与其重叠的高斯，从而大幅减少无效计算。配合GPU上的并行前缀和和共享内存排序，实现高吞吐量的可微光栅化。

## 直觉理解
类似拼图游戏——与其在整个桌面上搜索每块拼图的位置，不如先把桌面划分成小方格，每块拼图只去看它落在哪几个方格内。3DGS把屏幕分成16×16的tile网格，每个高斯椭球投影后只覆盖少量tile，渲染时每个tile独立处理自己的那部分高斯，GPU并行处理所有tile。

## 数学形式
算法分为三个步骤：
1. **预处理**：将每个投影后的2D高斯分配到其覆盖的tile
2. **排序**：在每个tile内按深度对高斯排序
3. **合成**：每个像素独立执行Alpha合成

该算法的复杂度为 $O(N \cdot K)$，其中 $N$ 是高斯数量，$K$ 是每个tile平均覆盖的高斯数（远小于 $N$）。

## 关联
- 相关概念: [[concepts/alpha-compositing]], [[concepts/projection-transform]], [[concepts/occlusion-aware-culling]], [[concepts/proxy-rendering]]
- 用到该概念的论文: [[papers/2026-05/3d-gaussian-splatting]], [[papers/2026-05/langsplat]], [[papers/2026-05/gs-livo]], [[papers/2026-05/proxy-gs]], [[papers/2026-05/gaussnav]]

LangSplat将tile-based splatting从颜色渲染扩展到语言特征渲染，通过同一光栅化管线高效生成语言特征图。

GS-LIVO的滑动窗口策略通过限制渲染范围到当前FoV内的高斯，避免了全场景tile-based深度排序中前景污染背景的混叠伪影。

## 扩展：遮挡感知预剔除

Proxy-GS在tile-based光栅化之前增加了遮挡感知剔除阶段：利用快速代理系统生成的遮挡深度图，在预处理步骤中直接剔除被遮挡的锚点和高斯，使其不进入后续的tile分配、排序和合成流程。对MLP-based结构化3DGS而言，锚点级剔除发生在MLP解码之前，额外节省了解码计算量。这使得tile-based管线仅处理可见图元，在严重遮挡场景中实现2.5倍以上的加速。
