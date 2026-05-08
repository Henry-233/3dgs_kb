---
title: "3D语言场"
tags: [concept, semantics]
---

## 定义
3D语言场（3D Language Field）是三维场景的一种语义表示形式，将场景中的每个空间位置映射到语言特征向量（通常来自CLIP等多模态模型）。用户通过自然语言查询即可定位场景中的物体或区域，实现开放词汇的3D场景理解。

两种构建范式：
- **渲染训练**（LangSplat）：通过可微渲染训练每个高斯的语言特征，最小化渲染特征与SAM+CLIP目标特征的差异
- **直接注册**（Dr. Splat）：将CLIP特征直接分配给每个像素光线穿过的"主导高斯"（top-K alpha贡献），无需渲染训练和梯度反传

## 直觉理解
3D语言场可以理解为给3D场景"涂上了一层语义颜料"——每个点不仅有颜色和形状，还带有"这是什么"的语言描述能力。当你用"红色的椅子"查询场景时，语言场在所有高斯中搜索与"红色椅子"语义最匹配的区域并高亮显示。

核心挑战是**点歧义**（point ambiguity）：同一个3D点（如熊鼻子上的一个点）同时属于"熊鼻子"、"熊头"、"整只熊"三个不同语义层级。解决方法是从SAM获取三层语义分割图（subpart/part/whole），让每个3D点学习三个层级分别的语言特征，查询时在三层中选择最佳匹配。

相比于NeRF体渲染需逐光线采样查询（30+秒/次），3D高斯语言场通过一次性splatting渲染整张语言特征图（~3通道经自编码器压缩），再与文本特征做相似度匹配，速度快两个数量级（0.26秒/次）。

## 数学形式

### 3D语言高斯
每个3D高斯 $G_i$ 在原有 $\{\mu_i, \Sigma_i, o_i, SH_i\}$ 基础上增加三层语言嵌入：
$$\{f_i^s, f_i^p, f_i^w\}, \quad f_i^l \in \mathbb{R}^d$$
其中 $d$ 为潜空间维度（通常 $d=3$），s/p/w 对应 subpart/part/whole

### 语言特征渲染
与RGB渲染共享同一光栅化管线：
$$F^l(v) = \sum_{i \in \mathcal{N}} f_i^l \cdot \alpha_i \cdot \prod_{j=1}^{i-1} (1 - \alpha_j), \quad l \in \{s, p, w\}$$

### 场景级自编码器
编码器 $E: \mathbb{R}^{512} \to \mathbb{R}^{3}$，解码器 $\Psi: \mathbb{R}^{3} \to \mathbb{R}^{512}$

训练目标：$\mathcal{L}_{ae} = \sum_{l} \sum_{t} d_{ae}(\Psi(E(L_t^l)), L_t^l)$（L1 + 余弦距离）

### 相关度计算
$$\text{Relevancy}(v, qry) = \max_{l \in \{s,p,w\}} \left(\min_i \frac{\exp(\Psi(F^l(v))_i \cdot qry)}{\exp(\Psi(F^l(v))_i \cdot qry) + \exp(\Psi(F^l(v))_i \cdot canon)}\right)$$

## 层次语义（SAM引导）
SAM（Segment Anything Model, ViT-H）对每张训练图像输入32×32均匀点提示，输出三层mask——subpart、part、whole——经去冗余（IoU评分+稳定度+重叠率过滤）后得到全图分割。每层独立提取CLIP特征并分配给区域内所有像素，作为语言高斯的学习目标。

优势：
- 物体边界精确 → 训练目标干净无噪声
- 三层语义预定义尺度 → 无需多尺度密集搜索
- 消除对DINO特征的依赖

## 关联
- 相关概念: [[concepts/3d-gaussian]], [[concepts/nerf]], [[concepts/tile-based-rasterization]], [[concepts/product-quantization]]
- 用到该概念的论文: [[papers/langsplat]], [[papers/dr-splat]]
