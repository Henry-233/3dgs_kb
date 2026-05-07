---
title: "Instant-NGP"
tags: [concept, rendering, comparison]
---

## 定义
Instant-NGP（Instant Neural Graphics Primitives）是NVIDIA提出的加速NeRF训练方法。通过多分辨率哈希编码（multi-resolution hash encoding）将输入坐标映射为高维特征，配合小型MLP，将NeRF的训练时间从数小时缩短至数秒到数分钟。3DGS在此基础上进一步实现了实时渲染。

## 直觉理解
传统NeRF用"大网兜住所有细节"——一个深层MLP同时处理粗粒度和细粒度信息。Instant-NGP改用"查字典"的方式——把空间划分成多个分辨率的哈希表，查表得到特征再喂给小网络。这就像把详细的地图信息存在不同缩放级别的表格里，查找比推理快得多。

## 数学形式
多分辨率哈希编码：
1. 将空间划分为 $L$ 层不同分辨率的网格
2. 每层对输入坐标哈希查表获取特征向量
3. 拼接各层特征送入小型MLP

使得MLP从拟合完整场景简化为解码已编码特征。

## 关联
- 相关概念: [[concepts/nerf]], [[concepts/tensorf]]
- 上下文: Instant-NGP是3DGS之前最快的隐式方法，3DGS借鉴了其"用显式数据结构加速"的思路。
