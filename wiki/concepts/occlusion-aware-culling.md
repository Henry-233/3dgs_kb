---
title: "遮挡感知剔除"
tags: [concept, rendering, optimization]
---

## 定义
遮挡感知剔除（Occlusion-Aware Culling）是指在3DGS渲染管线中，利用场景遮挡信息判断哪些高斯图元对当前视角的最终渲染不可见（被前方物体完全遮挡），从而在渲染前将其剔除的技术。与传统的基于贡献度或细节层次的剔除不同，遮挡感知剔除直接建模几何遮挡关系，更精确地识别真正冗余的高斯。

## 直觉理解
传统剔除像一个近视的管理者——只根据每个员工（高斯）自身的大小和贡献度决定去留。遮挡感知剔除则像一个能看清全局的指挥者——他知道哪些员工被前面的人完全挡住了，观众根本看不见，所以直接让他们休息。这样既节省资源，又不会影响最终呈现效果。

## Proxy-GS中的遮挡剔除管道

### 完整管线
在单个CUDA kernel中融合视锥剔除和遮挡剔除：

**步骤1：NDC→像素映射**
$$x_{pix} = \frac{x_{ndc}+1}{2} \cdot W,\quad y_{pix} = \frac{y_{ndc}+1}{2} \cdot H$$

无效像素（落在画面外）直接丢弃：
$$x_{pix} < 0 \lor x_{pix} \geq W \lor y_{pix} < 0 \lor y_{pix} \geq H$$

**步骤2：硬件深度→线性深度**
从硬件深度缓冲读取 $z_{hw} \in [0,1]$，转换为相机空间线性深度：
$$d_{mesh}(x_{pix}, y_{pix}) = \frac{nf}{f - z_{hw}(x_{pix}, y_{pix})(f-n)}$$

其中 $n, f$ 为近/远裁剪面。

**步骤3：安全容限**
$$\hat{d}(x_{pix}, y_{pix}) = d_{mesh}(x_{pix}, y_{pix}) + \varepsilon$$

**步骤4：遮挡判定**
$$\text{Cull}(p) = \begin{cases} \text{True} & \text{if } z_h > \hat{d}(x_{pix}, y_{pix}) \\ \text{False} & \text{otherwise} \end{cases}$$

若深度值无效（如点在相机后方 $z_h < \delta$，$\delta = 10^{-4}$），不剔除。

### 安全容限的选择
$\varepsilon$ 是最关键的参数，在Small City数据集上：
| $\varepsilon$ | PSNR | FPS | 效果 |
|------------|------|-----|------|
| 0.1 | 22.94 | 142 | 近处出现渲染伪影 |
| **0.3** | **23.09** | **139** | **最优平衡** |
| 0.6 | 23.02 | 135 | 开始引入冗余锚点 |
| 1.0 | 23.05 | 128 | 过多锚点，FPS下降 |

太小→误剔除可见高斯产生伪影；太大→漏剔除过多被遮挡高斯，FPS下降。

### 锚点级剔除的加速级联
对[[concepts/mlp-based-3dgs|MLP-based 3DGS]]，剔除在锚点（anchor）级别执行——被遮挡的锚点及其关联的所有高斯在MLP解码之前即被跳过。这带来双重加速：
1. **解码节省**：不需要对被遮挡锚点执行MLP前向传播
2. **渲染节省**：不需要对被遮挡高斯执行光栅化

在MatrixCity上，Proxy-GS将平均解码锚点数从Octree-GS的719k降至106k（减少85%）。

## 与其他剔除策略的对比
| 策略 | 依据 | 视角依赖 | 代表性工作 |
|------|------|---------|-----------|
| 贡献度剪枝 | 不透明度+尺度 | 否（全局剔除） | Mobile-GS, LightGaussian |
| LOD剔除 | 相机距离 | 是（距离） | Octree-GS, Hierarchical-GS |
| **遮挡感知剔除** | **实际遮挡关系** | **是（遮挡）** | **Proxy-GS** |

## 关联
- 相关概念: [[concepts/proxy-rendering]], [[concepts/adaptive-density-control]], [[concepts/tile-based-rasterization]], [[concepts/alpha-compositing]], [[concepts/mlp-based-3dgs]]
- 用到该概念的论文: [[papers/proxy-gs]]
