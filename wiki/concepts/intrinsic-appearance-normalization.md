---
title: "内在外观归一化"
tags:
  - illumination-invariant
  - appearance-modeling
  - slam
---

## 定义

内在外观归一化（Intrinsic Appearance Normalization, IAN）是一种将场景内在属性（如反照率、材质颜色）与瞬态光照条件解耦的表示学习方法：通过为每个高斯基元学习标准化、光照不变的颜色表示，使场景表示对光照变化天然免疫。

## 动机

3DGS使用球谐函数（SH）编码视角依赖外观，但SH同时捕获了场景材质和光照的混合信息——当光照条件改变时，原本正确的SH系数反而产生错误的渲染颜色。IAN将光照从外观表示中显式剥离，保留仅反映场景材质的内在颜色。

## 与SH的区别

- **SH (球谐函数)**：编码视角依赖辐射度，包含材质+光照的混合效应
- **IAN**：学习光照归一化后的内在反照率，光照变化不影响渲染颜色
- **协同**：IAN处理光照鲁棒性，SH仍可用于编码视角依赖的镜面反射等效应

## 关联

- [[concepts/spherical-harmonics]] — SH是传统视角依赖编码方式，IAN是其光照不变性改进
- [[concepts/3d-gaussian]] — 3D高斯的颜色表示
- [[papers/taming-the-light]] — 首次提出IAN的论文
