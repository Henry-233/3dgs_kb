---
title: "Dr. Splat: Directly Referring 3D Gaussian Splatting via Direct Language Embedding Registration"
authors: Kim Jun-Seong, GeonU Kim, Kim Yu-Ji, Yu-Chiang Frank Wang, Jaesung Choe, Tae-Hyun Oh
year: 2025
venue: CVPR 2025 (Highlight)
tags: [paper, extension, semantics]
status: done
---

## 一句话总结
提出直接语言特征注册（Direct Language Embedding Registration）替代LangSplat的渲染训练范式——将CLIP特征通过光线-高斯交叉直接分配给主导高斯，并用通用大规模数据训练的Product Quantization（PQ）替代逐场景自编码器压缩，无需渲染训练即可构建精确的3D语义高斯场。

## 解决的问题

LangSplat引入基于渲染训练的3D语言场，但存在两个关键痛点：

1. **渲染训练开销**：LangSplat需通过可微渲染来训练每个高斯的语言特征（固定几何参数，优化语言嵌入），仍然需要多轮迭代渲染和损失回传
2. **逐场景压缩**：LangSplat的场景级自编码器需为每个场景单独训练MLP，无跨场景泛化能力，且编码器质量依赖该场景的SAM分割质量

Dr. Splat追问：能否**完全绕过渲染训练**，直接将2D语义特征"注册"到3D高斯中？

## 核心方法

### 整体思路
Dr. Splat不学习语言特征——而是直接**分配**已知的CLIP特征到3D高斯。流程分为两步：
1. 从每张训练图像的每个像素出发，发射光线穿过场景，找到该像素"看到"的**主导高斯**（dominant Gaussians —— 沿光线alpha累积贡献最大的前K个高斯）
2. 将该像素对应的SAM+CLIP特征**直接注册**（赋给）这些高斯，聚合为每个高斯的最终语言特征

无需渲染训练，无需损失函数反向传播。

### 1. 直接语言特征注册

**动机**：LangSplat的渲染训练本质是"通过2D监督间接学习3D特征"——渲染2D语言特征图，与SAM+CLIP提取的2D目标特征计算损失，梯度反传更新每个高斯的 $f_i^l$。这个过程可被绕过。

**方案**：直接建立像素↔高斯的对应关系。
- 对每张训练图像的每个像素 $v$，使用3DGS的alpha合成权重确定该像素"看到"哪些高斯
- 取alpha贡献（$\alpha_i \prod_{j=1}^{i-1}(1-\alpha_j)$）最大的前 $K$ 个高斯（top-K dominant Gaussians）
- 将该像素的CLIP语言特征（来自SAM分割区域）直接赋给这些高斯
- 多个像素映射到同一高斯时，特征取加权平均

**数学形式**：
给定像素 $v$ 的语言特征 $L(v) \in \mathbb{R}^{D}$（经SAM分割提取的CLIP特征），找到该像素的主导向高斯集合 $\mathcal{G}_v$，则每个3D高斯的语言特征为：

$$f_i = \frac{\sum_{v: i \in \mathcal{G}_v} w_i(v) \cdot L(v)}{\sum_{v: i \in \mathcal{G}_v} w_i(v)}$$

其中 $w_i(v) = \alpha_i \prod_{j=1}^{i-1} (1 - \alpha_j)$ 是高斯 $i$ 在像素 $v$ 处的alpha贡献权重。

**关键优势**：训练是一次性的前向pass——计算alpha权重 → 匹配高斯 → 加权聚合 → 完成。无需损失函数、无需梯度反传、无需多轮迭代。

### 2. Product Quantization（PQ）压缩

**动机**：直接存储每个高斯的512维CLIP特征仍然导致显存膨胀。LangSplat用逐场景训练的自编码器（512D→3D）。Dr. Splat追求**无逐场景优化**的压缩方案。

**方案**：
- **Product Quantization（乘积量化）**：将 $D$ 维向量划分为 $m$ 个子空间（每个 $D/m$ 维），每个子空间用一个codebook（含 $k$ 个聚类中心）量化
  - 原始向量被编码为 $m$ 个codebook索引（每个 $\log_2 k$ bits），总码长 $m \log_2 k$ bits
  - 解码时查表拼接：$\hat{v} = [c_1^{(idx_1)}; c_2^{(idx_2)}; ...; c_m^{(idx_m)}]$
- **关键是codebook的来历**：在**大规模通用图像数据**（非当前场景）上预先训练PQ codebook，构建到 `.faiss` 索引文件中
- 推理时使用同一个预训练PQ索引（`pq_index.faiss`），无需任何场景特定训练

**与LangSplat自编码器的对比**：
| | LangSplat Autoencoder | Dr. Splat PQ |
|---|---|---|
| 训练数据 | 当前场景SAM分割区域（数百个） | 大规模通用图像数据（百万级） |
| 逐场景优化 | 需要（每个场景训练一次AE） | 不需要（预训练，零样本） |
| 压缩比 | 512 → 3（~170×） | 512 → m × log₂k bits（可调） |
| 泛化性 | 场景内专用，跨场景不共享 | 通用，跨场景共享 |
| 实现 | 轻量MLP（编码器+解码器） | FAISS PQ索引（查表） |

### 3. 查询与推理

**推理流程**：
1. 3D高斯已携带PQ压缩的语言特征码（无需渲染训练！）
2. 给定文本查询 → CLIP文本编码器 → 文本特征 $qry$
3. 对每个高斯 $i$：
   - 查PQ表解码语言特征 → $\hat{f}_i \in \mathbb{R}^{D}$
   - 计算与 $qry$ 的余弦相似度 → 该高斯的激活值
4. 渲染激活图（沿相机视角做alpha合成，类似渲染RGB但因无需反传所以极快）
5. 应用阈值 → 得到分割mask；取激活最高点 → 定位结果

**关键**：查询阶段仍需渲染（将高斯激活值splat到2D图像），但**训练阶段完全不需要渲染**。

## 与前作的区别

| 前作 | 区别 |
|------|------|
| LangSplat (CVPR 2024) | Dr. Splat**不需要渲染训练**：直接注册CLIP特征到主导高斯，而非通过可微渲染学习；**不需要逐场景自编码器**：用通用预训练PQ替代 |
| LERF (ICCV 2023) | 3D表示：高斯替代NeRF；训练：直接注册替代体渲染训练；速度提升显著 |
| 3D-OVS | 3D-OVS需完整类别列表，Dr. Splat支持开放词汇任意文本查询 |

## 实验结论

### 基准任务
- **开放词汇3D语义分割**：在LERF和3D-OVS数据集上超越LangSplat及其他SOTA
- **3D物体定位**：更精确的定位精度
- **3D物体选择**：新增的交互式任务——用户用自然语言描述，系统直接选中对应3D物体

### 关键消融发现
- 直接注册替代渲染训练：精度相当或更高，训练时间大幅缩短（单次前向pass，无需迭代）
- PQ替代AE：跨场景通用，压缩效率高，且不损失精度
- top-K参数（默认K=45）：控制每个像素分配的高斯数量，K太小则稀疏，K太大则模糊

### 效率
- 训练更快：无需渲染训练的迭代过程
- 推理可比：查询时仍需splatting渲染激活图，但无需解码（PQ查表比MLP解码更快）
- 跨场景泛化：PQ预训练一次，所有场景复用

## 局限性与未来方向

1. **依赖高质量3DGS预训练**：直接注册的质量依赖3DGS几何质量——如果初始3DGS重建不好（高斯位置不准），注册的语义特征也会错位
2. **PQ在非常见类别上的泛化**：PQ在大规模通用数据上训练，对于高度场景特定的概念（如特定品牌名称）可能压缩损失更大
3. **静态场景假设**：与LangSplat相同，当前仅处理静态场景
4. **直接注册的稀疏性**：部分像素可能没有足够的主导高斯，导致语义覆盖不完整

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 对比/继承: [[papers/langsplat]]
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/3d-language-field]], [[concepts/product-quantization]], [[concepts/alpha-compositing]]
