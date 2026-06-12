---
title: "RoGER-SLAM: A Robust Gaussian Splatting SLAM System for Noisy and Low-light Environment Resilience"
authors:
  - "Huilin Yin"
  - "Zhaolin Yang"
  - "Linchuan Zhang"
  - "Gerhard Rigoll"
  - "Johannes Betz"
year: 2025
venue: arXiv
status: done
tags:
  - slam
  - robust-slam
  - low-light
  - 3dgs
---

## 一句话总结

RoGER-SLAM利用3DGS渲染管线Alpha合成的隐式低通滤波特性，通过SP-RoFusion结构保持融合（渲染外观+深度+边缘）、自适应残差平衡跟踪和条件触发CLIP增强三大创新，在噪声和低光条件下实现鲁棒SLAM——干净Replica上ATE 0.24 cm（优于SplaTAM 50%），噪声+低光下ATE 0.60 cm（SplaTAM为6.82 cm，提升91%）。

## 解决的问题

现有3DGS-SLAM（SplaTAM、MonoGS、GS-SLAM）在干净条件下表现良好，但在视觉输入受噪声和低光照影响时性能急剧下降。核心洞察：**3DGS渲染管线中的Alpha合成（沿视线加权累加多个高斯）本质上充当隐式低通滤波器**，可衰减高频噪声但存在过平滑风险，且该属性是非结构化的隐式效应，在复合退化条件下不足以保证鲁棒性。

此外，现有基准缺乏同时包含传感器噪声和低光照且提供真值轨迹的数据集（ExDark等仅用于识别任务），导致噪声+低光对3DGS-SLAM的耦合影响从未被系统研究。

## 核心方法

RoGER-SLAM框架由四个核心模块组成：

**1. 3D高斯表示与初始化。** 标准3DGS流程：每帧RGB-D反投影初始化高斯椭球体 $\mu_i = K^{-1}[x_i, y_i, 1]^T \cdot d_i$，多尺度门控densification策略避免冗余插入——在3个分辨率尺度 $\{1.0, 0.5, 0.25\}$ 上渲染不透明度，加权融合得到重要性分数 $\text{IMP}_{\text{fuse}} = \sum_s w^{(s)} \cdot \frac{1}{|P|} \sum_p O_p^{(s)}$，仅当分数>0.01时触发densification。

**2. SP-RoFusion（结构保持鲁棒融合）。** 核心创新——构建结构感知伪监督信号替代原始噪声图像：

$$I_{\text{fuse}} = \lambda_r \cdot I_{\text{render}} + \lambda_d \cdot \text{Norm}(\text{Rep}_3(D_{\text{gt}})) + \lambda_g \cdot \text{Norm}(\text{Rep}_3(G))$$

其中边缘图 $G = \sqrt{(K_x \cdot I_{\text{gray}})^2 + (K_y \cdot I_{\text{gray}})^2}$ 通过Sobel算子提取。融合图像保留了渲染外观、几何深度和结构边缘三重信息，总建图损失为：

$$\mathcal{L}_{\text{map}} = 0.5\mathcal{L}_{\text{color}} + \mathcal{L}_{\text{depth}} + \omega_{\text{illum}}\mathcal{L}_{\text{illum}}$$

其中 $\mathcal{L}_{\text{illum}} = \|I_{\text{render}} - I_{\text{fuse}}\|_1$，$\mathcal{L}_{\text{color}} = 0.8\|I_{\text{render}} - I_{\text{gt}}\|_1 + 0.2(1-\text{SSIM})$，动态光照权重 $\omega_{\text{illum}} = \min(\mathcal{L}_{\text{illum}}/(\mathcal{L}_{\text{color}}+\epsilon), \tau)$ 防止融合损失主导优化。

**3. 自适应跟踪目标。** 针对不同场景纹理/深度范围/噪声变化的静态权重无法泛化的问题，设计动态残差平衡机制：

$$w_{\text{im}} = \frac{\gamma_{\text{im}}}{\mathcal{L}_{\text{color}} + \gamma_{\text{im}}}, \quad w_{\text{depth}} = \frac{\gamma_{\text{depth}}}{\mathcal{L}_{\text{depth}} + \gamma_{\text{depth}}}$$

跟踪损失包含正则化项防止权重发散：

$$\mathcal{L}_{\text{Tracking}} = \mathbf{1}_{\{O_p > 0.99\}}\left(w_{\text{im}}L_1(C_p) + w_{\text{depth}}L_1(D_p) + \lambda_R(\log\frac{w_{\text{depth}}}{w_{\text{im}}} - \log\rho)^2\right)$$

仅使用高不透明度像素（>0.99），位姿初始化采用匀速模型 $E_{t+2} = E_{t+1} + (E_{t+1} - E_t)$。

**4. CLIP增强模块（选择性触发）。** 在复合噪声+低光条件下，SP-RoFusion单独不足以保证鲁棒性，因此引入双分支CLIP增强：
- **去噪分支**：冻结CLIP图像编码器提取抗失真多尺度特征 + 可学习多层解码器重建，损失 $\mathcal{L}_{\text{denoising}} = L_1(I_d, I_c)$
- **低光增强分支**：神经表示归一化(NRN)将不同退化水平统一预处理 + 编码器-解码器增强 + CLIP文本引导监督（训练图像向量与"高光图像"prompt相似、与"低光图像"prompt不相似），损失 $\mathcal{L}_{\text{LE}} = L_1(I_{\text{NR}}, I_L) + L_1(I_H, I_L) + \mathcal{L}_{\text{CLIP}}$
- **双重条件判断**：基于全局亮度和残差噪声方差 $\sigma_R^2$ 判断，仅当 $\sigma_R^2 > 30$（严重退化）时激活，额外开销46 ms/帧

## 数学形式

**SP-RoFusion融合：**
$$I_{\text{fuse}} = \lambda_r I_{\text{render}} + \lambda_d \text{Norm}(\text{Rep}_3(D_{\text{gt}})) + \lambda_g \text{Norm}(\text{Rep}_3(G))$$
$$G = \sqrt{(K_x \cdot I_{\text{gray}})^2 + (K_y \cdot I_{\text{gray}})^2}$$

**建图损失：**
$$\mathcal{L}_{\text{map}} = 0.5\mathcal{L}_{\text{color}} + \mathcal{L}_{\text{depth}} + \omega_{\text{illum}}\mathcal{L}_{\text{illum}}$$
$$\omega_{\text{illum}} = \min\left(\frac{\mathcal{L}_{\text{illum}}}{\mathcal{L}_{\text{color}} + \epsilon}, \tau\right)$$

**自适应跟踪：**
$$w_{\text{im}} = \frac{\gamma_{\text{im}}}{\mathcal{L}_{\text{color}} + \gamma_{\text{im}}}, \quad w_{\text{depth}} = \frac{\gamma_{\text{depth}}}{\mathcal{L}_{\text{depth}} + \gamma_{\text{depth}}}$$
$$\mathcal{L}_{\text{Tracking}} = \mathbf{1}_{\{O_p > 0.99\}}\left(w_{\text{im}}L_1(C_p) + w_{\text{depth}}L_1(D_p) + \lambda_R(\log\frac{w_{\text{depth}}}{w_{\text{im}}} - \log\rho)^2\right)$$

**多尺度densification门控：**
$$\text{IMP}_{\text{fuse}} = \sum_{s \in \{1.0,0.5,0.25\}} w^{(s)} \cdot \frac{1}{|P|}\sum_{p \in P} O_p^{(s)}$$

## 与前作的区别

| 维度          | SplaTAM | MonoGS | WildGS-SLAM | ADD-SLAM  | **RoGER-SLAM**      |
| ----------- | ------- | ------ | ----------- | --------- | ------------------- |
| **鲁棒性目标**   | 无       | 无      | 动态物体        | 动态物体+动态建模 | **噪声+低光照**          |
| **监督信号**    | 原始RGB   | 原始RGB  | 原始RGB+不确定性  | 原始RGB-D   | **SP-RoFusion融合信号** |
| **跟踪权重**    | 固定      | 固定     | 固定          | 固定(动态掩码)  | **自适应残差平衡**         |
| **增强策略**    | 无       | 无      | 无           | 无         | **CLIP条件增强**        |
| **退化系统性研究** | 无       | 无      | 无           | 无         | **首次系统量化**          |

RoGER-SLAM是首个针对**光度退化**（噪声、低光）而非**场景动态**（运动物体）设计鲁棒性的3DGS-SLAM系统，与WildGS-SLAM/ADD-SLAM/UP-SLAM形成互补。它也是首个系统量化噪声+低光对3DGS-SLAM耦合影响的论文。

## 实验结论

**干净条件跟踪（ATE cm）：**
- Replica：**0.24 cm**（SplaTAM 0.36 → 提升50%；MonoGS 0.58；GS-SLAM 0.50）
- TUM RGB-D：**4.79 cm**（SplaTAM 5.48 → 提升12%；MonoGS 1.47仅3序列；Co-SLAM 8.38）

**自然传感器噪声（Poisson-Gaussian模型）：**
- office3场景：PSNR下降仅 **0.55 dB** vs SplaTAM 1.48 dB
- 无需CLIP模块即可抵抗轻度噪声

**复合噪声+低光（最严苛条件）：**
- Replica ATE：**0.60 cm** vs SplaTAM 6.82 cm（**提升91%**）
- TUM ATE：**2.63 cm** vs SplaTAM 12.23 cm
- PSNR提升：3-5 dB
- SSIM恢复：最高0.90（SplaTAM降至0.73）
- SplaTAM从干净0.36 cm退化到6.82 cm（**恶化19倍**），RoGER-SLAM仅从0.24到0.60 cm

**效率：**
- CLIP增强模块触发时增加46 ms/帧
- 条件触发避免正常场景冗余计算
- 多尺度门控+重要性驱动剪枝维持建图效率

**消融实验：**
- SP-RoFusion单独：干净条件提升明显，轻度噪声有效
- 自适应跟踪单独：跨场景权重稳定
- CLIP增强：仅在复合退化条件激活，显著恢复语义和结构

**真实世界验证：** UGV平台搭载Intel RealSense D435i + RTK，RoGER-SLAM产生更干净RGB/深度渲染和更完整几何一致地图。

## 局限性

1. **RGB-D依赖**：需要深度传感器输入，不适用于纯单目场景
2. **CLIP模块训练**：增强模块需预训练，泛化到极端域外退化可能受限
3. **SP-RoFusion额外开销**：融合机制略微增加建图计算成本
4. **未处理动态物体**：聚焦光度退化而非场景动态，需与WildGS-SLAM/ADD-SLAM等方法结合
5. **室外动态光照**：极端室外光照变化（如昼夜交替）尚未验证
6. **仅仿真退化**：噪声+低光数据集通过后处理构造，非真实传感器采集

## 关联

- [[concepts/slam]] — 基础SLAM框架
- [[concepts/3d-gaussian]] — 3D高斯场景表示
- [[concepts/clip]] — CLIP用于语义增强和去噪
- [[concepts/alpha-compositing]] — Alpha合成的隐式低通滤波特性是本文核心洞察
- [[concepts/differentiable-rendering]] — 可微渲染管线
- [[concepts/ssim-loss]] — 颜色损失中的SSIM分量
- [[papers/2026-05-07/3d-gaussian-splatting]] — 3DGS基础方法
- [[papers/2026-06-11/add-slam]] — 互补方向：动态物体鲁棒性
- [[papers/2026-05-21/wildgs-slam]] — 互补方向：不确定性感知动态SLAM
- [[papers/2026-06-02/up-slam]] — 互补方向：并行架构动态SLAM

## 标注状态
---
annotated: true
annotation_date: 2026-06-12
annotated_pdf: raw/papers/RoGER-SLAM A Robust Gaussian Splatting SLAM System for Noisy and Low-light Environment Resilience_annotated.pdf
---
