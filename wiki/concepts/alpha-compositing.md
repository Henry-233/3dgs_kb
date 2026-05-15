---
title: "Alpha合成"
tags: [concept, rendering]
---

## 定义
Alpha合成（Alpha Compositing / Alpha Blending）是从后到前（或从前到后）按透明度加权累加颜色的渲染技术。在3DGS中，将投影到图像平面的2D高斯按深度排序后，通过Alpha合成逐点计算每个像素的最终颜色，是可微渲染管线的核心。

## 直觉理解
想象你在玻璃上画了多层不同透明度的色块。从后往前看，每层颜色都会"穿透"前面的层贡献到最终画面——越不透明的层遮挡越强，越透明的层让后面的颜色透过来越多。Alpha合成的数学公式就是精确描述了这个"透明叠加"过程。

## 数学形式
3DGS中使用从前到后的Alpha合成公式：

$$C = \sum_{i=1}^{N} c_i \alpha_i \prod_{j=1}^{i-1} (1 - \alpha_j)$$

其中：
- $c_i$：第 $i$ 个高斯的颜色
- $\alpha_i$：第 $i$ 个高斯在当前像素处的不透明度（由高斯值和全局opacity乘积计算）
- $\prod_{j=1}^{i-1} (1 - \alpha_j)$：透射率（transmittance），即前面所有高斯的累积遮挡

## 扩展：可微深度渲染

G²-Mapping将Alpha合成从仅颜色可微扩展到深度也可微。在前到后合成中，渲染深度 D̂ = Σ d_i α_i w_i，其对高斯属性的导数通过链式法则传播：

$$\frac{\partial D}{\partial P} = \frac{\partial D}{\partial a}\frac{\partial a}{\partial P} + \frac{\partial D}{\partial d}\frac{\partial d}{\partial P}, \quad \frac{\partial D}{\partial a_i} = d_i w_i - \frac{\sum_{j=i+1}^n d_j a_j w_i}{1-a_i}$$

这使得深度信息不仅可以监督场景几何，还可以通过可微渲染优化相机位姿（对四元数和平移的Jacobian）。

## 变体：顺序无关渲染
标准Alpha合成需要按深度排序高斯，这是移动端的主要计算瓶颈。Mobile-GS提出了深度感知的顺序无关渲染（Order-Independent Rendering），用深度加权混合替代排序，大幅加速渲染但可能引入重叠区域伪影（需神经增强修正）。

## 关联
- 相关概念: [[concepts/3d-gaussian]], [[concepts/tile-based-rasterization]], [[concepts/order-independent-rendering]], [[concepts/neural-view-dependent-enhancement]]
- 用到该概念的论文: [[papers/3d-gaussian-splatting]], [[papers/mip-splatting]], [[papers/gaussian-opacity-fields]], [[papers/street-gaussians]], [[papers/mobile-gs]], [[papers/gs-livo]], [[papers/g2-mapping]]
