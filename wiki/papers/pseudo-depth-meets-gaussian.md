---
title: "Pseudo Depth Meets Gaussian: A Feed-forward RGB SLAM Baseline"
authors: Linqing Zhao, Xiuwei Xu, Yirui Wang, Hao Wang, Wenzhao Zheng, Yansong Tang, Haibin Yan, Jiwen Lu
year: 2025
venue: arxiv
tags: [paper, extension, slam, feed-forward]
status: done
---

## 一句话总结
提出首个前馈式Gaussian SLAM基线——用GRU循环网络+DBA层直接从光流预测相机位姿替代迭代优化跟踪，结合伪深度驱动的3D高斯建图，精度持平或超越SplaTAM且跟踪速度提升5-13倍。核心发现：3D高斯天然能"模糊化"伪深度误差（网格和点云则不能），使无深度传感器的RGB SLAM成为可能。

## 解决的问题

### 在线RGB重建的四个瓶颈

| 瓶颈            | 现有方法的问题                                             |
| ------------- | --------------------------------------------------- |
| **深度传感器依赖**   | SplaTAM、Point-SLAM等RGB-D SLAM需要深度传感器，不适用于手机/无人机等设备  |
| **伪深度不可靠**    | 直接用单目深度估计器（UniDepthV2）生成伪深度替代真值→网格和点表示直接暴露深度误差，重建崩溃 |
| **跟踪速度极慢**    | SplaTAM每帧需10次迭代×65ms = 数秒/帧的测试时优化（渲染→反传→更新位姿）       |
| **端到端方法记忆遗忘** | Spann3R等前馈方法用隐式特征记忆，长序列中灾难性遗忘破坏重建质量                 |

**核心问题**：什么样的3D表示能容忍伪深度噪声？跟踪能否从"迭代优化"变为"网络推理"？

## 核心方法

### 场景表示的适应性实验（Fig. 2）

先对比三种3D表示在真值深度→伪深度的退化情况：

| 表示                      | 解码        | 可微渲染            | 自适应形状         | 可优化属性                  | GT深度 | 伪深度                  |
| ----------------------- | --------- | --------------- | ------------- | ---------------------- | ---- | -------------------- |
| **Grids** (NICE-SLAM)   | MLP       | 稀疏体渲染           | 无（固定网格）       | 无                      | 良好   | **崩溃**（深度误差致网格错位）    |
| **Points** (Point-SLAM) | MLP       | 稀疏体渲染           | 无（固定点）        | 无                      | 良好   | **有空洞和断裂**（深度误差直接暴露） |
| **Gaussians** (SplaTAM) | Splatting | **稠密splatting** | **有**（各向异性椭球） | **有**（μ, Σ, α, SH全可优化） | 最佳   | **能用**（不确定性自然扩散）     |

**核心直觉**：3D高斯 $f(x) = o \cdot \exp(-\frac{|x-\mu|^2}{2r^2})$ 天然编码了空间不确定性——一个高斯椭球的延展范围本身就说"在这个区域内我不确定"。当伪深度有误差时，高斯会将不确定性"扩散"到一个区域，产生连续稳定的重建；而网格和点云没有这种扩展性，深度误差直接表现为空洞和错位。

### 基线建图管线（Fig. 3a）

系统在线增量生长高斯场景表示，交替优化高斯和位姿：

**高斯优化**（固定位姿，Eq. 1）——最小化渲染RGB和深度与输入的差异：
$$\mathcal{G}_t = \min_{\mathcal{G}} \sum_{i \in \mathcal{N}(t)} \left(|R_{\text{img}}(\mathcal{G}_{t-1} \oplus \mathcal{P}(D_t), G_i) - I_i| + |R_{\text{dep}}(\mathcal{G}_{t-1} \oplus \mathcal{P}(D_t), G_i) - D_i|\right)$$

**位姿优化**（固定高斯，Eq. 2）——迭代优化消除渲染-观测差异：
$$G_t = \min_G \left(|R_{\text{img}}(\mathcal{G}_{t-1}, G) - I_t| + |R_{\text{dep}}(\mathcal{G}_{t-1}, G) - D_t|\right)$$

其中 $\mathcal{P}$ 是将伪深度反投影为3D高斯初始化的模块，$\mathcal{N}(t)$ 为近期时间戳窗口（含 $t$），$\oplus$ 为增量添加新高斯操作。

> 这就是"伪深度+RGB-D SLAM"的基线版本——位姿仍用迭代优化，跟踪速度极慢。接下来解决这个问题。

### 前馈式位姿预测（Fig. 3b）

受DROID-SLAM启发，用GRU循环网络+DBA层替代迭代优化。

**稠密对应场计算**（Eq. 3）——给定估计位姿 $G$ 和伪深度 $d$：
$$p_{ij} = \Pi_c\left(G_{ij} \cdot \Pi_c^{-1}(p_i, d_i)\right), \quad G_{ij} = G_j \circ G_i^{-1}$$

**GRU精化**：RAFT预训练权重初始化，输入关联特征和光流特征，输出修正的光流场 $r_{ij}$ 和置信度图 $w_{ij}$。修正后对应场 $\tilde{p}_{ij} = r_{ij} + p_{ij}$。

**DBA层求解位姿**（Eq. 4）——固定深度，用Gauss-Newton最小化重投影误差：
$$\Delta G_{ij} = \arg\min_{\delta G} \|\tilde{p}_{ij} - \Pi_c(\delta G \cdot \Pi_c^{-1}(p_i, d_i))\|^2$$

DBA层用CUDA实现端到端高效推理（DROID-SLAM [Teed & Deng, NeurIPS 2021]）。

**直觉**：传统SplaTAM跟踪每帧要做"渲染→算损失→反传→更新位姿"的迭代循环（每迭代65ms，一张图10次=650ms）。前馈模块把这个过程替换为"光流估计+一次Gauss-Newton"——全是网络前向pass，无需渲染/反传。

### 局部图渲染（LGR）——解决2帧预测不可靠

仅用 $(I_{t-1}, I_t)$ 两帧做前馈预测对光照变化、运动模糊、无纹理区域极敏感。LGR构造一个包含已知位姿的渲染帧的局部图提供额外约束。

**球面姿态采样**（Eq. 5-7）：

**惯性近似位姿**（Eq. 6）——假设相机惯性（位置二阶差分恒定）：
$$\hat{G}_t = [R_{t-1}] \cdot [2T_{t-1} - T_{t-2}]$$

**球面采样**（Eq. 7）——在 $\hat{G}_t$ 周围采样 $N$ 个相机位姿：
$$G_t^{(k)} = [R_{t-1}] \cdot [T_{t-1} + \eta \cdot \|T_{t-1}-T_{t-2}\| \cdot \hat{v}^i(\theta)]$$

其中 $\hat{v}^i(\theta)$ 是与惯性方向成角 $\theta$ 的单位球面向量，$\eta$ 为惯性系数（默认5.0），$\theta \in [0, 30^\circ]（默认30°）$。

**渲染局部图**（Eq. 5）——从3D高斯 splat 出已知位姿的渲染帧和深度：
$$I_t^{(k)} = R_{\text{img}}(\mathcal{G}_t, G_t^{(k)}), \quad D_t^{(k)} = R_{\text{dep}}(\mathcal{G}_t, G_t^{(k)})$$

**构建局部图** $\mathcal{E}$：节点为 $I_t$ + $I_{t-1}$ + $\{I_t^{(k)}\}_{k=1}^{N-1}$，边连接图像对。在全部边上运行DBA求解最优相对位姿。

**直觉类比**：你到了一个陌生路口不知方向。LGR的做法是——"我先大致猜一下自己的位置（惯性估计），然后在周围几个角度各拍一张照片（球面采样），用已知的3D地图在这几个位置生成参考照片（渲染），把我的照片和这些参考照片一一比对（光流+DBA），综合判断最终位置。"

## 与前作的区别

| 前作 | 关键区别 |
|------|---------|
| **SplaTAM** (CVPR 2024) | 跟踪：前馈网络推理替代RGB-D迭代优化→总跟踪时间从5232s降到389s（w/o LGR）/ 1056s（w/ LGR）；伪深度替代真值深度 |
| **G²-Mapping** (IEEE TASE 2025) | G²-Mapping优化式预跟踪+地图位姿优化→仍耗时；本方法直接用前馈网络预测，无需渲染/反传 |
| **WildGS-SLAM** (arxiv 2025) | WildGS-SLAM依赖优化式DBA跟踪；本方法将DBA嵌入前馈网络做单次推理 |
| **DROID-SLAM** (NeurIPS 2021) | DROID-SLAM无3DGS建图（纯视觉里程计）；本方法的前馈模块继承其RAFT+DBA架构，但加入LGR（从3DGS渲染的额外约束） |
| **VGGT** (CVPR 2025) | VGGT离线批量→需所有帧同时输入；本方法在线逐帧增量处理 |
| **Spann3R** (arxiv 2024) | Spann3R用隐式空间记忆（catastrophic forgetting）；本方法用显式3D高斯地图（持久化几何） |

### SplaTAM伪深度基线

论文额外报告了SplaTAM直接使用伪深度的结果（原论文仅用GT深度）：TUM-RGBD上ATE从4.95cm退化到8.89cm。本方法在伪深度条件下ATE=8.62cm（持平）且速度快5-13倍。

## 实验结论

### 跟踪精度（ATE RMSE [cm]）

**Replica**（Table I）：
| 方法 | 输入 | Avg ATE |
|------|------|---------|
| SplaTAM | GT深度 | 31.19 |
| Ours (w/o LGR) | 伪深度 | 16.12 |
| **Ours (full)** | **伪深度** | **15.49** |

用伪深度反而超越用真值深度的SplaTAM——高斯建图展现了超预期的伪深度适应能力。

**TUM-RGBD**（Table II）：
| 方法 | 输入 | Avg ATE | 时间/帧 |
|------|------|---------|---------|
| SplaTAM | GT深度 | 4.95 | 3.67s |
| SplaTAM | 伪深度 | 8.89 | 2.61s |
| **Ours (full)** | **伪深度** | **8.62** | **0.53s** |

### 渲染质量

**Replica**（Table III）：
| 方法 | 输入 | PSNR | SSIM | LPIPS |
|------|------|------|------|-------|
| SplaTAM | GT深度 | 35.23 | 0.98 | 0.09 |
| SplaTAM | 伪深度 | 23.06 | 0.80 | 0.36 |
| **Ours (full)** | **伪深度** | **22.92** | **0.79** | **0.37** |

**TUM-RGBD**（Table IV）：
| 方法 | 输入 | PSNR | MS-SSIM | LPIPS |
|------|------|------|---------|-------|
| SplaTAM | GT深度 | 16.97 | 0.660 | 0.460 |
| **Ours (w/o LGR)** | **伪深度** | **16.66** | **0.728** | **0.449** |

伪深度输入下渲染质量与SplaTAM（用伪深度）相当，且MS-SSIM/LPIPS在某些指标上反超。

### 运行时（Table V — Replica R0, RTX A6000）

| 方法 | 跟踪总时间 | 建图总时间 | 跟踪/帧 | ATE RMSE |
|------|----------|----------|---------|----------|
| SplaTAM | **5232s** | 9384s | 65ms/iter | 12.48 |
| Ours (w/o LGR) | **389s** | 8978s | 0.19s | 16.74 |
| Ours (full) | **1056s** | 8896s | 0.53s | **10.96** |

**跟踪加速**：w/o LGR = 13.4×, w/ LGR = 4.95×。SplaTAM每帧平均78ms×N迭代，而本方法0.19-0.53s/帧的单次前向pass。

### 消融实验（Table VI + Fig. 5）

**局部图节点数N**：N=2→8，ATE从7.39→7.27 cm改善（边际递减，N=6最优性价比）
**采样角度θ**：15°~60°，PSNR和SSIM随θ增大改善（视觉质量提升），ATE基本稳定
**惯性系数η**（Fig. 5）：η=1-2时ATE最优（7.27cm），η>5性能下降（过度依赖惯性引入漂移）

### 真实世界部署

在会议室和教室两个真实场景的RGB视频流上在线运行（UniDepthV2伪深度），推理速度>1 FPS。

## 关键发现总结

1. **3D高斯是唯一能处理伪深度的表示**：网格（Grid）和点云（Point）在伪深度下重建崩溃，3D高斯因其空间扩散性和可优化属性天然适配
2. **前馈跟踪可替代迭代优化**：跟踪从"渲染→反传→更新"的迭代变成"光流+DBA"的单次推理
3. **LGR用已知3D信息锚定未知位姿**：从3DGS渲染已知位姿的参考图像构造局部图，显著提升2帧预测的鲁棒性
4. **可插拔设计**：LGR关闭即为纯2帧前馈（389s/seq），打开则为图约束前馈（1056s/seq），精度显著提升

## 局限性

1. **伪深度质量依赖**：深度估计器（UniDepthV2）的系统性偏差在极端场景中仍会传播到重建
2. **前馈泛化边界**：GRU+DBA模块在训练域外场景可能退化（相比优化式方法无训练域限制）。文中仅用预训练DROID-SLAM权重初始化，无额外微调
3. **无回环检测**：当前基线未集成回环/全局BA——这是ATR与ORB-SLAM2等方法仍有差距的主要原因
4. **静态场景假设**：未处理动态物体
5. **LGR的渲染开销**：渲染N个视角的局部图引入额外开销（0.19→0.53s/帧），N=6为精度-速度最优

## 关联
- 基于: [[papers/3d-gaussian-splatting]]
- 跟踪架构继承: DROID-SLAM (Teed & Deng, NeurIPS 2021), RAFT (Teed & Deng, ECCV 2020)
- 对比方法: SplaTAM (Keetha et al., CVPR 2024)
- 相关SLAM: [[papers/g2-mapping]], [[papers/wildgs-slam]], [[papers/gs-livo]]
- 相关前馈方法: [[papers/vggt]]
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/slam]], [[concepts/monocular-depth-estimation]], [[concepts/feed-forward-pose-prediction]], [[concepts/local-graph-rendering]], [[concepts/feed-forward-3d-reconstruction]]
