---
title: "LangSplat: 3D Language Gaussian Splatting"
authors: Minghan Qin, Wanhua Li, Jiawei Zhou, Haoqian Wang, Hanspeter Pfister
year: 2023
venue: CVPR 2024
tags: [paper, extension, semantics]
status: done
---

## 一句话总结
将CLIP语言特征蒸馏到3D高斯中，构建支持开放词汇查询的3D语言场——通过场景级语言自编码器将512维CLIP特征压缩至3维潜空间、SAM提供三层语义分割训练信号，实现精确物体边界的零样本语义查询，渲染速度比LERF快199倍。

## 解决的问题

**核心矛盾**：如何让3D场景理解自然语言查询？

现有方法（以LERF为代表）存在三个瓶颈：

1. **渲染慢**：基于NeRF做体渲染，每帧需沿光线采样上百个点查询MLP，一次查询耗时30秒以上
2. **语义模糊**：用不同尺度的裁剪patch提取CLIP特征作为训练目标，但这些patch常常包含背景杂讯或漏掉部分物体，导致学到的3D语言场边界不清、噪声大
3. **点歧义**（point ambiguity）：同一个3D点（如"熊鼻子上的点"）同时属于"鼻子"、"头"、"熊"三个语义层级。LERF靠多尺度查询+绝对尺度输入+DINO正则化来缓解，但增加了数十倍推理时间且效果不理想

## 核心方法

### 整体思路
用3D高斯替换NeRF作为3D表示，每个高斯除了原有的颜色/几何信息外，额外携带**语言特征向量**。渲染时，tile-based splatting同时输出RGB图和语言特征图，后者与CLIP文本编码做相似度匹配完成开放词汇查询。

### 1. 层次语义学习（SAM）

这是解决"点歧义"和"语义模糊"的关键。

**具体流程**：
- 对每张训练图像，输入32×32的均匀点提示网格到SAM（ViT-H），获取三个层级的masks：**subpart**（子部件）、**part**（部件）、**whole**（整体）
- 对每个层级分别执行去冗余（基于IoU、稳定度、重叠率过滤），得到三张全图分割图 $M^s, M^p, M^w$
- 对每张分割图中的每个区域，用CLIP图像编码器（OpenCLIP ViT-B/16）提取该区域的特征 $L_t^l(v) \in \mathbb{R}^D$（$D=512$），赋给区域内所有像素

**为什么有效**：
- SAM精确分割物体边界 → CLIP特征是在"干净"的物体区域上提取的，不含背景噪声
- 三层语义预定义了查询尺度 → 推理时只需在三个尺度上各查询一次（而非LERF的密集多尺度搜索），同时直接解决点歧义问题
- 不需要DINO特征作为额外正则化

### 2. 场景级语言自编码器

**动机**：直接在每个3D高斯上存512维CLIP特征 → 存储需求膨胀35倍以上（相对无SH系数的RGB高斯），百万级高斯场景下直接爆L1缓存

**方案**：
- 收集该场景所有SAM分割区域的CLIP特征 $\{L_t^l\}$，训练一个轻量MLP自编码器：
  - 编码器 $E: \mathbb{R}^{512} \to \mathbb{R}^{3}$（压缩至3维）
  - 解码器 $\Psi: \mathbb{R}^{3} \to \mathbb{R}^{512}$（恢复CLIP特征）

- 训练目标（L1 + 余弦距离）：
  $$\mathcal{L}_{ae} = \sum_{l \in \{s,p,w\}} \sum_{t=1}^{T} d_{ae}(\Psi(E(L_t^l(v))), L_t^l(v))$$

**为什么只需3维就能压缩512维CLIP特征**：
CLIP在4亿图文对上训练，其潜空间需对齐"任意图文对"；但单个场景中SAM分割出的区域数量仅数百个，这些区域特征在CLIP空间中**稀疏分布**，利用场景先验可大幅压缩

### 3. 3D语言高斯 Splatting

**表示**：每个3D高斯 $G_i$ 在原有参数（均值 $\mu_i$、协方差 $\Sigma_i$、不透明度 $o_i$、SH颜色系数）基础上，增加三个语言嵌入 $\{f_i^s, f_i^p, f_i^w\}$，分别对应subpart/part/whole三个语义层级，每个 $f_i^l \in \mathbb{R}^3$

**渲染**（与RGB渲染完全相同的tile-based rasterizer）：
$$F^l(v) = \sum_{i \in \mathcal{N}} f_i^l \cdot \alpha_i \cdot \prod_{j=1}^{i-1} (1 - \alpha_j), \quad l \in \{s, p, w\}$$

**训练**：固定3DGS的几何参数（均值、协方差、不透明度），仅优化语言特征 $f_i^l$：
$$\mathcal{L}_{lang} = \sum_{l \in \{s,p,w\}} \sum_{t=1}^{T} d_{lang}(F_t^l(v), H_t^l(v))$$

其中 $H_t^l(v) = E(L_t^l(v))$ 是自编码器压缩后的目标特征（在3维潜空间中）

### 4. 开放词汇查询

**推理流程**：
1. Splatting渲染 → 三张语言特征图 $F^s, F^p, F^w$（每张3通道）
2. 解码器 $\Psi$ 恢复 → 三张CLIP特征图（每张512通道）
3. 与文本查询 $qry$ 计算相关度（遵循LERF的softmax归一化）：
   $$\text{score} = \min_i \frac{\exp(img_i \cdot qry)}{\exp(img_i \cdot qry) + \exp(img_i \cdot canon)}$$
   其中 $canon$ 是预定义的"中性"短语（"object"/"things"/"stuff"/"texture"）的CLIP文本嵌入
4. 在三层相关度图中选择得分最高的层级作为最终输出
5. **定位任务**：取最高分像素点；**分割任务**：阈值过滤低分区域

## 与前作的区别

| 前作 | 区别 |
|------|------|
| LERF (NeRF-based, ICCV 2023) | 3D表示：高斯替代NeRF → 渲染快199×；训练目标：SAM分割区域替代多尺度crop → 语义边界更精确；不需要绝对尺度输入和DINO正则化 |
| 3D-OVS (NeurIPS 2023) | 3D-OVS需完整类别列表生成mask，LangSplat仅靠文本查询即可生成mask |
| 3DGS (SIGGRAPH 2023) | 为每个高斯增加语义维度（语言特征），将纯视觉管线推广到视觉-语言 |
| FFD (NeurIPS 2022) | FFD在NeRF中蒸馏DINO特征做编辑，LangSplat用SAM+CLIP做精确查询 |

## 实验结论

### 数据集
- **LERF数据集**（Polycam拍摄的in-the-wild场景）：3D物体定位 + 扩展标注了语义分割GT mask
- **3D-OVS数据集**（长尾物体、多姿态多背景）：开放词汇语义分割

### 定位精度（LERF数据集）
| 方法 | 准确率(%) |
|------|-----------|
| LSeg | 21.1 |
| LERF | 73.6 |
| **LangSplat** | **84.3** |

### 语义分割（LERF数据集，IoU%）
| 方法 | IoU(%) |
|------|--------|
| LSeg | 16.6 |
| LERF | 37.4 |
| **LangSplat** | **51.4** |

### 语义分割（3D-OVS数据集，mIoU%）
| 方法 | mIoU(%) |
|------|---------|
| LSeg | 20.6 |
| ODISE | 43.5 |
| LERF | 54.8 |
| OV-Seg | 77.5 |
| 3D-OVS | 86.8 |
| **LangSplat** | **93.4** |

### 推理速度
- 988×731分辨率：LangSplat **0.26秒/查询** vs LERF 30.93秒 → **119×加速**
- 1440×1080分辨率：LangSplat **0.28秒/查询** vs LERF 55.7秒 → **199×加速**
- 训练时间：~25分钟（RTX 3090，~4GB显存）

### 消融实验（ramen场景）
| 配置 | IoU(%) | 速度(s/q) |
|------|--------|-----------|
| Baseline (=LERF) | 28.20 | 30.93 |
| + SAM替代多尺度crop | 46.74 | 7.77 |
| 直接用3DGS存CLIP特征（无autoencoder） | OOM | OOM |
| **完整LangSplat** | **51.15** | **0.26** |

**消融结论**：
- SAM替代多尺度方案直接带来+18.54 IoU提升
- 无自编码器时直接爆显存（存512维特征 × 250万高斯）
- 自编码器不仅解决显存问题，还带来额外的精度和速度提升

## 局限性与未来方向

1. **场景特定训练**：每个场景需独立训练RGB场景（30K步）和语言特征（30K步），总时间约55分钟。未来可探索前馈式或few-shot泛化
2. **CLIP的固有限制**：语言理解受限于CLIP的视觉-语言对齐能力，对细粒度属性（如"生了锈的银色水龙头"）可能不够鲁棒
3. **解码器瓶颈**：高分辨率下解码器（MLP逐像素恢复512维特征）成为推理速度的主要瓶颈，论文提到用1×1卷积替代MLP可进一步加速
4. **动态场景未覆盖**：当前仅处理静态场景，城市场景应用场景（参考Street Gaussians）是可能的扩展方向

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 对比方法: [[concepts/nerf]]（LERF为NeRF-based）
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/3d-language-field]], [[concepts/tile-based-rasterization]], [[concepts/alpha-compositing]]
