---
title: "GaussNav: Gaussian Splatting for Visual Navigation"
authors: Xiaohan Lei, Min Wang, Wengang Zhou, Houqiang Li
year: 2025
venue: IEEE TPAMI, Vol. 47, No. 5, May 2025
tags: [paper, application, navigation, embodied-ai]
status: done
---

## 一句话总结
首次将3DGS引入具身视觉导航——提出Semantic Gaussian地图表示（简化各向同性高斯+语义标签），通过ResNet50分类器+DISK-LightGlue特征匹配+DISK-NVS多视角渲染，将IIN任务转化为PointGoal导航，在HM3D数据集上将SPL从0.347提升至0.578（+66%），运行效率>20 FPS。

## 解决的问题

**核心矛盾**：实例图像目标导航（IIN）要求智能体在未探索环境中，仅凭一张目标物体照片，定位并导航到该特定实例。关键挑战：(1) 跨视角识别同一物体 (2) 区分同类不同实例的干扰物。

现有BEV地图方法的根本局限：
1. **BEV是2D俯视图**：将3D场景投影为2D占据网格 → 丢失所有纹理细节和3D几何
2. **无法跨楼层**：BEV天然是单层表示，无法处理多层建筑
3. **语义层面有效，实例层面失效**：BEV能编码"这里有椅子"但无法区分"这把红椅子和那把蓝椅子"
4. **需要额外验证步骤**：IEVE等方法必须走到候选物体附近做近距离验证 → 路径冗余，SPL低

GaussNav追问：能否用3DGS构建一种同时保留几何、语义、纹理的地图，使智能体无需额外探索和验证，直接从地图中"认出"目标物体并导航过去？

## 核心方法

### 整体架构（三阶段）

GaussNav是模块化的场景级框架。在新环境的**第一个episode**中，智能体执行Frontier Exploration收集观测并构建Semantic Gaussian地图；在**后续episode**中，智能体直接使用已构建的地图，通过Gaussian Navigation定位目标并规划路径。

### 1. Semantic Gaussian — 简化但高效的3DGS变体

与原始3DGS（Kerbl et al.）的关键区别：GaussNav将3DGS简化以适配导航场景的计算和存储约束。

**每个高斯仅9个参数**（原始3DGS需59+参数）：
- 颜色向量 $\mathbf{c} \in \mathbb{R}^3$（**视角无关**RGB，无球谐函数）
- 质心 $\boldsymbol{\mu} \in \mathbb{R}^3$
- 半径 $r$（**各向同性**，无协方差矩阵/旋转/缩放）
- 不透明度 $o \in [0, 1]$
- 类别标签 $l$（语义分割赋值）

**设计动机**：导航任务不需要照片级新视角合成——只需要足够好的外观来区分不同物体实例。简化带来的收益：计算效率提升、存储需求降低、建图速度快。

**可微渲染**：Semantic Gaussian支持四种渲染输出（在已知相机位姿下），均通过alpha合成：

RGB渲染（Eq.1）：
$$\hat{I}(\mathbf{p}) = \sum_{i=1}^{n} \mathbf{c}_i \cdot f_i(\mathbf{p}) \cdot \prod_{j=1}^{i-1} (1 - f_j(\mathbf{p}))$$

深度渲染（Eq.4）：
$$\hat{D}(\mathbf{p}) = \sum_{i=1}^{n} d_i \cdot f_i(\mathbf{p}) \cdot \prod_{j=1}^{i-1} (1 - f_j(\mathbf{p}))$$

轮廓渲染（Eq.5）：
$$\hat{S}(\mathbf{p}) = \sum_{i=1}^{n} f_i(\mathbf{p}) \cdot \prod_{j=1}^{i-1} (1 - f_j(\mathbf{p}))$$

语义渲染（Eq.6）：
$$\hat{C}(\mathbf{p}) = \sum_{i=1}^{n} l_i \cdot f_i(\mathbf{p}) \cdot \prod_{j=1}^{i-1} (1 - f_j(\mathbf{p}))$$

其中高斯在像素空间的贡献函数为（Eq.2）：
$$f(\mathbf{x}) = o \cdot \exp\left(-\frac{\|\mathbf{x} - \boldsymbol{\mu}\|^2}{2r^2}\right)$$

投影变换（Eq.3）：$\boldsymbol{\mu}_{2D} = K \frac{E_t \boldsymbol{\mu}}{d},\quad r_{2D} = \frac{f \cdot r}{d},\quad d = (E_t \boldsymbol{\mu})_z$

### 2. Frontier Exploration — 首个episode的探索策略

智能体同时维护两种2D地图（Fig. 3）：
- **探索地图**：记录已探索区域
- **障碍物地图**：标记场景中的障碍物

策略：检测探索地图轮廓 → 排除障碍物区域 → 选择最近的frontier点作为waypoint → 导航到该点继续探索。这是机器人学中经典的frontier-based exploration，迭代执行直到环境被充分覆盖。

### 3. Semantic Gaussian Construction — 增量式建图

建图是一个迭代交替过程，包含两个步骤：

**Step 1: Gaussian Densification（高斯增密）**

对每个新帧，比较t-1时刻高斯的渲染结果与当前真值观测，在缺失区域添加新高斯。增密遮罩（Eq.7）：
$$M(\mathbf{p}) = \underbrace{(\hat{S}(\mathbf{p}) < 0.5)}_{\text{高斯不够密}} \;\lor\; \underbrace{\left(D(\mathbf{p}) < \hat{D}(\mathbf{p}) \land \frac{|\hat{D}(\mathbf{p}) - D(\mathbf{p})|}{D(\mathbf{p})} > 50 \cdot \text{MDE}\right)}_{\text{真值深度在前方且误差超过50倍中位深度误差}}$$

**语义分割**：对每帧RGB观测使用MaskRCNN分割，分割结果用于初始化新高斯的语义标签 $l$ 和监督训练。

**Step 2: Semantic Gaussian Updating（高斯参数更新）**

通过可微渲染 + 梯度优化，最小化RGB、深度和语义分割误差，更新所有高斯参数。等价于经典的"给定位姿和图像拟合辐射场"问题。

### 4. Gaussian Navigation — 从图像目标到导航路径

给定已构建的Semantic Gaussian，Gaussian Navigation分四步将IIN转化为PointGoal导航：

#### Step 1: Classifier（目标分类）

用ResNet50（ImageNet预训练 + HM3D训练集目标图像微调）将目标图像 $I_g$ 分类为6个类别之一：chair, couch, plant, bed, toilet, television。分类器将候选搜索空间缩小**2.5倍**（Table III），且仅损失0.039匹配成功率。

#### Step 2: Match & Grounding（匹配与定位）

这是GaussNav最核心的创新——如何从Semantic Gaussian中"认出"目标物体。

**候选实例筛选**：从Semantic Gaussian中查询所有标签=$\hat{l}_g$的高斯 → DBSCAN空间聚类 → 得到 $n$ 个候选物体实例。

**多视角渲染（NVS）**：对每个候选实例，从原始训练视角出发，在水平和垂直方向旋转生成 $n_v$ 个新视角的渲染图像：
$$c2w_h(\theta) = o2w \cdot R_y(\theta) \cdot w2o \cdot c2w$$
$$c2w_v(\theta) = o2w \cdot R_x(\theta) \cdot w2o \cdot c2w$$

其中 $o2w$ 是物体到世界的刚体变换（Eq.8-10），$R_y(\theta)$/$R_x(\theta)$ 是绕y/x轴的旋转。实验中 $n_v = 3$（θ=±15°水平+垂直）或 $n_v = 5$（θ=±15°, ±30°）。

**特征匹配**（Eq.12-14）：
1. 用**DISK**（轻量级局部特征提取器）提取渲染图像 $s$ 和目标图像 $I_g$ 的关键点+描述符
2. 用**LightGlue**（基于Transformer的特征匹配器）计算匹配对
3. 匹配点数 $\kappa(s)$ 作为相似度得分

$$\kappa(s) = |\text{LightGlue}(\text{DISK}(s), \text{DISK}(I_g))|$$

目标实例选择（Eq.12）：
$$i_{max} = \arg\max_i \left\{\max_{s \in S_1} \kappa(s), \max_{s \in S_2} \kappa(s), \ldots, \max_{s \in S_n} \kappa(s)\right\}$$

选出匹配点数最多的实例后，用DBSCAN对其高斯聚类去噪，定位到该实例的3D位置 $\hat{P}_g$。

#### Step 3: Path Planning（路径规划）

Semantic Gaussian → 提取点云 → 体素化为3D体素 $M_{3D}$ → 投影为2D BEV网格 $M_{2D}$ → Fast Marching Method (FMM)计算最短距离场 → 在智能体操作范围内选择无碰撞的局部最优点作为waypoint → 重复直到到达目标。

#### 关键设计决策：场景级地图 vs 回合级地图

不同于之前方法（每episode重新建图），GaussNav在场景的第一个episode建图后，**所有后续episode复用同一地图**。这使得导航阶段极其高效（>20 FPS），因为不需要在线语义分割、特征匹配或探索决策。

## 与前作的区别

| 前作 | 区别 |
|------|------|
| Mod-IIN / IEVE (BEV地图方法) | **地图表示革命**：3DGS替代2D BEV → 保留纹理细节；**无需验证**：GaussNav一步定位目标，不再需要走到候选物体旁反复验证 → SPL +0.231 |
| 3DGS (Kerbl et al., SIGGRAPH 2023) | **简化表示**：各向同性高斯+视角无关颜色替代完整SH+协方差；**新任务**：将3DGS从新视角合成扩展到具身导航 |
| SplaTAM / Gaussian-SLAM | **目标不同**：SLAM以ATE/PSNR为核心指标，GaussNav以SPL/Success为核心指标；**地图用法不同**：SLAM用地图优化位姿，GaussNav用地图渲染做目标匹配 |
| OVRL-v2 (端到端ImageNav) | OVRL-v2直接迁移到IIN仅Success=0.006（域差距+任务差异），微调后0.248但仍远低于GaussNav |

## 实验结论

### 实验设置
- **数据集**：HM3D（145/36/35 训练/验证/测试场景），IIN episode 7056K/1K/1K
- **目标类别**：chair, couch, plant, bed, toilet, television（6类，验证集795个独特实例）
- **智能体**：Hello Robot Stretch平台参数（高1.41m，半径0.17m，相机高1.31m，640×480 RGB-D）
- **动作空间**：离散4动作 {STOP, FORWARD(25cm), TURN_RIGHT(25°), TURN_LEFT(25°)}
- **成功条件**：STOP时距目标<1.0m
- **指标**：Success Rate, SPL (Eq.15)

### 主要结果（Table I）

| 方法 | Success | SPL |
|------|---------|-----|
| RL Baseline (PPO, scratch) | ~0.015 | ~0.012 |
| OVRL-v2 (zero-shot) | 0.006 | ~0.005 |
| OVRL-v2 (fine-tuned) | 0.248 | ~0.209 |
| Mod-IIN (episodic map) | ~0.475 | ~0.344 |
| IEVE (episodic map) | ~0.559 | ~0.347 |
| Mod-IIN (scene map) | ~0.480 | ~0.335 |
| IEVE (scene map) | ~0.562 | ~0.340 |
| **GaussNav** | **~0.597** | **0.578** |

**核心洞察**：GaussNav的SPL（0.578）比IEVE（0.347）高出**0.231（+66%）**。这不是因为GaussNav更容易成功（成功率~0.597 vs ~0.559，差距不大），而是因为GaussNav**不需要绕路验证**——直接从地图定位目标，走最短路径到达（Fig. 6轨迹分析）。

### 消融实验（Table II）

| 配置 | Success | SPL |
|------|---------|-----|
| **完整GaussNav** | **~0.597** | **0.578** |
| w/o Classifier（随机类别标签） | 0.375 | 0.291 |
| w/o Match（随机选候选） | 0.444 | 0.353 |
| SIFT + FLANN 替代 DISK+LightGlue | ~0.568 | ~0.533 |
| GlueStick 替代 | ~0.585 | ~0.561 |
| w/ GT Match（oracle匹配） | 0.723 | — |
| w/ GT Match + GT Goal Localization | **0.946** | — |

**消融结论**：
- **Match模块**贡献最大：随机选候选 → Success从0.597降至0.444（-0.153）
- **Classifier**也很关键：随机标签 → Success降至0.375（-0.222），且搜索时间变2.5倍
- **误差上限分析**：Match错误导致约0.127 Success损失，定位不精确导致额外0.096损失，两者合计解释了0.223的Success差距。剩余0.054归因于路径规划等其他因素

### NVS分析（Table V）

| NVS配置 | 匹配成功率 |
|---------|-----------|
| $n_v=1$（无NVS） | 基线 |
| 水平 $n_v=3$（θ=±15°） | ↑ 提升 |
| 水平 $n_v=5$（θ=±15°, ±30°） | ≈ $n_v=3$ |
| 垂直 $n_v=3$ | ↑ 提升 |
| 垂直 $n_v=5$ | ↓ **低于** $n_v=3$ |
| GT NVS | ↑↑ **显著提升** |

**关键发现**：更多NVS视角不一定更好——垂直 $n_v=5$ 反而降低性能。原因是Semantic Gaussian对每个物体仅有少量观测视角（不同于传统3DGS的数十个），大角度NVS会产生空洞和伪影（Fig. 8），减少可匹配特征点。GT渲染的提升说明**建图质量是当前NVS的瓶颈**。

### 无预探索场景（Table VI）

将GaussNav的Semantic Gaussian集成到IEVE框架中（无预探索，每episode在线建图），仅靠增强现有观测做NVS，也带来了正向提升——说明Semantic Gaussian即使不依赖预建图也有价值。

### 效率分析

- **搜索空间压缩**（以场景CrMo8WxCyVb为例）：54m²可导航区域×12个朝向=648个候选观测 → 按语义分组后仅需3×11=33次渲染比较（**~20倍压缩**）
- **运行时帧率**：>20 FPS，在模块化方法中最高（Fig. 7），因为导航阶段无需语义分割、特征匹配或切换模块
- **预处理开销**：仅在场景首个episode发生，后续episode直接复用地图

### 建图质量（Fig. 10-12）

- 部分场景PSNR高达40+，深度误差接近零
- 但渲染质量呈**两极分化**：HM3D仿真器在某些高纹理场景中渲染质量低（Fig. 12），导致这些场景的3DGS重建质量差
- 对重建差的场景，GaussNav保留原始训练视图（不强行做NVS）

### 错误模式分析

两个主要错误来源：
1. **Match失败**（无法从渲染中识别目标）— 代价~0.127 Success。改进方向：更鲁棒的重识别算法
2. **Goal定位不准**（识别了目标但位置估计偏差）— 代价~0.096 Success。改进方向：更精确的Grounding策略

## 局限性与未来方向

1. **建图质量瓶颈**：NVS质量受限于HM3D仿真器渲染质量和3DGS重建精度——低质量场景的渲染特征不足，匹配不可靠。GT渲染可大幅提升性能（Table V）说明这是改进的关键方向
2. **首个episode探索开销**：需完整探索环境建图后才能高效导航，对单episode场景不划算
3. **仅6个目标类别**：当前实验限于HM3D的6类语义标注，开放类别需扩展语义分割能力
4. **静态场景假设**：与大多数3DGS方法相同，无法处理动态物体
5. **DISK+LightGlue的固有限制**：局部特征匹配对极端视角变化和严重遮挡不够鲁棒
6. **DBSCAN聚类的敏感性**：语义分割错误导致outlier时，聚类参数需手动调节

## 关联
- 基于: [[papers/2026-05/3d-gaussian-splatting]]（简化了原始3DGS：各向同性高斯+视角无关颜色，去除SH和协方差矩阵）
- IIN前置工作: Mod-IIN, IEVE（第一作者Lei也是IEVE的一作——从BEV验证范式演进到3DGS直接定位范式）
- 相关方法: [[papers/2026-05/gs-livo]]（已验证Gaussian地图可用于A*路径规划）, [[papers/2026-05/langsplat]]（语义3DGS可为GaussNav提供语言驱动的目标描述替代图像输入）, [[papers/2026-06/zero-shot-uav-navigation]]（端到端RL范式——不需要显式地图和模块化流水线，直接从RGB预测控制指令）
- 涉及概念: [[concepts/3d-gaussian]], [[concepts/visual-navigation]], [[concepts/slam]], [[concepts/alpha-compositing]], [[concepts/tile-based-rasterization]], [[concepts/differentiable-rendering]]
