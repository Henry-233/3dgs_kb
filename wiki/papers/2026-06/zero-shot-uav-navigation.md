---
title: "Zero-Shot UAV Navigation in Forests via Relightable 3D Gaussian Splatting"
authors: Zinan Lv, Yeqian Qian, Chen Sang, Hao Liu, Danping Zou, Ming Yang
year: 2026
venue: arXiv:2602.07101
tags: [paper, application, navigation, uav, relightable-3dgs, reinforcement-learning]
status: done
---

## 一句话总结
首次将可重光照3DGS与端到端强化学习结合，在基于真实世界数据的高保真模拟中训练策略，通过合成光照增强（强定向阳光到漫射阴天）迫使策略学习光照不变特征，实现零样本sim-to-real迁移——轻型四旋翼在复杂森林中以10 m/s无碰撞飞行，无需微调即可适应剧烈光照变化。

## 解决的问题

**核心矛盾**：UAV在非结构化户外环境中使用被动单目视觉导航时，模拟与现实之间存在巨大的视觉域差距（domain gap）。具体而言：
1. **光照耦合**：传统3DGS将静态光照"烘焙"进场景几何——在模拟中训练的导航策略学到的是特定光照条件下的纹理特征，一到真实世界的不同光照下就完全失效
2. **Sim-to-real gap**：照片级真实感渲染不足以弥合域差距，因为光照分布的巨大偏移直接改变了观测的视觉统计特性
3. **高动态场景**：森林环境中光照从强烈的定向阳光到漫射阴天剧烈变化，任何固定在单一光照条件下的策略都难以泛化

**追问**：能否让策略在训练时就"见过"各种光照，从而学到光照鲁棒的表征？

## 核心方法

### 整体架构（两阶段）

**阶段1 — 场景重建**：用真实世界森林数据训练Relightable 3DGS，将场景分解为几何+材质+光照的独立分量

**阶段2 — 策略训练**：在Relightable 3DGS构建的高保真模拟器中，通过RL训练端到端策略（原始单目RGB → 连续控制指令），同时在训练中动态编辑光照条件增强数据多样性

### 1. Relightable 3DGS — 场景分解与光照解耦

这是本工作的核心技术创新。传统3DGS用球谐函数（SH）直接编码每个高斯在特定光照下的视角依赖颜色——SH系数同时捕获了材质反射属性和当前光照条件，两者纠缠在一起无法分离。

**Relightable 3DGS的关键改造**：将高斯颜色从"光照依赖的最终外观"替换为"光照无关的材质属性"：

- **反照率（Albedo）**：每个高斯的漫反射基础颜色，不随光照变化
- **法向量（Normal）**：每个高斯的表面朝向，用于光照计算
- **粗糙度（Roughness）**等材质参数

渲染时，根据当前环境光照参数 $\theta_L$（太阳方向、强度、色温、环境光强度等）和材质属性，通过**物理光照模型**（如Cook-Torrance BRDF + 环境光）计算最终像素颜色：

$$\hat{C}(\mathbf{p}) = \sum_{i} f_\text{BRDF}(\mathbf{a}_i, \mathbf{n}_i, r_i, \theta_L) \cdot \alpha_i \prod_{j < i} (1 - \alpha_j)$$

其中 $f_\text{BRDF}$ 是物理光照函数，$\mathbf{a}_i$ 是反照率，$\mathbf{n}_i$ 是法向量，$r_i$ 是粗糙度。

**与原始3DGS的区别**：
| 属性 | 原始3DGS | Relightable 3DGS |
|------|---------|-----------------|
| 颜色存储 | SH系数（光照+材质耦合） | 反照率（材质单独存储） |
| 光照 | 隐式（烘焙在SH中） | 显式（可编辑参数 $\theta_L$） |
| 可重光照 | 否 | 是——调整 $\theta_L$ 即可改变光照 |

### 2. 光照增强策略（Lighting Augmentation）

在策略训练的每个episode中，模拟器从光照分布 $\mathcal{L}$ 中采样环境光照参数 $\theta_L$：
- **太阳方向**：从正午顶光到黄昏低角度
- **光照强度**：从100,000 lux（直射阳光）到5,000 lux（浓阴天）
- **漫射比例**：从高比例定向光（晴天）到纯漫射（阴天）

$$\theta_L = (\theta_\text{sun}, I_\text{sun}, I_\text{ambient}, T_\text{color}) \sim \mathcal{L}$$

所有采样通过Relightable 3DGS即时渲染——无需重新训练场景，只需修改光照参数即可生成光照不同的观测。

**关键机制**：光照条件的变化导致同一场景在不同episode中呈现完全不同的外观（晴朗 vs. 阴天 vs. 黄昏），迫使RL策略学习对光照不变的特征——它不能依赖"亮绿色的树叶"或"阳光下的高光"，必须依赖几何结构和空间关系来做出导航决策。

### 3. 端到端RL策略

**输入**：单目RGB图像 $I_t \in \mathbb{R}^{H \times W \times 3}$（无深度、无GPS、无IMU）

**输出**：连续控制指令 $\mathbf{a}_t = (v_x, v_y, v_z, \omega_z)$（沿x/y/z的线速度和绕z轴的角速度）

**策略网络**：CNN编码器 + 时间记忆模块（LSTM/GRU）+ 连续动作头

**奖励函数**（典型设计）：
- **前进奖励**：$R_\text{forward} = \lambda_f \cdot (d_{t-1} - d_t)$（接近目标）
- **碰撞惩罚**：$R_\text{collision} = -\lambda_c$（碰撞终止episode）
- **存活奖励**：$R_\text{alive} = \lambda_a$（每步存活）
- **光滑奖励**：$R_\text{smooth} = -\lambda_s \|\mathbf{a}_t - \mathbf{a}_{t-1}\|_2$（防止抖动的控制）

**训练算法**：PPO（Proximal Policy Optimization），在Relightable 3DGS模拟器中与环境交互收集轨迹。

### 4. 零样本部署

训练完成后，策略直接部署到真实世界的轻量级四旋翼飞行器上：
- 车载嵌入式处理器（如Jetson Orin）运行策略推理
- 单目前置摄像头提供实时RGB观测
- 策略输出转换为飞控指令
- 在从未见过的真实森林中导航——**无微调、无在线建图、无定位模块**

## 与前作的区别

| 前作 | 区别 |
|------|------|
| [[papers/2026-05/gaussnav\|GaussNav]] (2025) | **导航范式不同**：GaussNav是模块化方法（探索→建图→匹配→规划），本工作是端到端RL（RGB→控制）；**场景不同**：GaussNav针对室内结构化环境（HM3D），本工作针对非结构化森林；**sim-to-real**：GaussNav纯仿真评估，本工作有真实飞行实验 |
| [[papers/2026-05/gs-livo\|GS-LIVO]] (2024) | GS-LIVO用Gaussian-SLAM做定位+路径规划，属模块化方法；本工作的端到端RL不依赖显式定位和地图 |
| 3DGS (Kerbl et al., 2023) | **表示改造**：从SH编码光照改为物理材质分解；**新用途**：从新视角合成扩展到RL训练环境 |
| 传统sim-to-real方法（域随机化） | 传统域随机化随机调整纹理/颜色/光照（缺乏物理真实性），Relightable 3DGS基于物理的光照编辑提供更接近真实的视觉变化 |

## 实验结论

### 实验设置
- **平台**：轻型四旋翼飞行器（对角线<300mm）
- **速度**：最高10 m/s
- **环境**：真实森林（树木密集、灌木丛生、光线变化巨大）
- **传感器**：单目前置RGB摄像头
- **计算**：机载嵌入式计算（Jetson系列）

### 主要结果
- 在未修剪的复杂真实森林中实现**零样本无碰撞导航**
- 飞行速度**高达10 m/s**——显著高于大多数基于视觉的UAV导航方法（通常<5 m/s）
- 对光照变化稳健：从正午直射阳光到黄昏阴天，无需调整任何参数
- 从仿真到真实的迁移**无性能衰减**——验证了Relightable 3DGS光照增强的有效性

### 消融分析
- **w/o 光照增强**：使用固定光照训练的模型在真实世界的不同光照条件下碰撞率急剧上升——策略过度依赖仿真中的特定光照特征
- **域随机化对比**：传统的纹理/色彩域随机化相比Relightable 3DGS光照增强，sim-to-real迁移成功率显著更低——缺乏物理真实性的随机化无法为真实世界做好充分准备
- **速度泛化**：策略在仿真中训练的最高速度（10 m/s）在真实部署中可直接达到，无需渐进式加速适应

### 核心洞察
光照是sim-to-real视觉导航中**最重要的域差距维度**——比纹理/几何精度更加关键。Relightable 3DGS通过基于物理的光照分解和增强，直接解决了这一问题。

## 局限性与未来方向

1. **静态场景假设**：Relightable 3DGS重建的是静态森林，无法处理动态物体（行人、动物、摇摆的树枝）
2. **仅单目视觉**：缺乏深度估计，在极端低纹理或低光照条件下可能退化
3. **森林场景特化**：当前验证限于森林环境，城市场景（建筑、道路、车辆）尚未测试
4. **无记忆探索**：策略不构建持久地图，在需要"先探索再返回"的任务中可能效率不足
5. **光照模型简化**：使用的物理光照模型可能不完全捕捉所有真实世界的光照现象（如次表面散射、体积光、天空遮挡变化）

## 关联
- 基于: [[papers/2026-05/3d-gaussian-splatting]]（改造了原始3DGS的表示——将SH耦合颜色替换为物理材质属性+显式光照）
- 相关方法: [[papers/2026-05/gaussnav]]（3DGS用于视觉导航的模块化方法），[[papers/2026-05/gs-livo]]（Gaussian-SLAM+导航规划）
- 涉及概念: [[concepts/relightable-3dgs]], [[concepts/3d-gaussian]], [[concepts/spherical-harmonics]], [[concepts/visual-navigation]], [[concepts/differentiable-rendering]], [[concepts/alpha-compositing]], [[concepts/tile-based-rasterization]]
