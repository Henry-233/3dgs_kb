---
title: "SAM (Segment Anything Model)"
tags: [concept, external-model, segmentation]
---

## 定义
SAM是Meta发布的图像分割基础模型，输入点/网格提示即可输出高质量物体掩码。在3DGS语言场（[[papers/langsplat|LangSplat]]、[[papers/dr-splat|Dr. Splat]]）中，SAM提供三个层级（subpart/part/whole）的精确物体分割，使CLIP特征可以在干净的物体区域（而非含背景噪声的粗糙crop）上提取。

## 直觉理解
SAM像一个"万物分割器"——给它一张图，它能自动把图中所有物体、部件、子部件都精确地"抠"出来。传统CLIP只能对整个矩形区域提取特征（常混入背景），SAM先把物体边界精确找出，再让CLIP在这些干净区域内提取特征，语义质量大幅提升。

## 在3DGS中的作用

### LangSplat
- 对每张训练图像输入32×32均匀点网格到SAM (ViT-H)
- 获取三层masks：**subpart**（子部件）、**part**（部件）、**whole**（整体）
- 逐层去冗余（IoU/稳定度/重叠率过滤）后提取CLIP特征
- 三层预定义语义尺度解决了"点歧义"问题，不再需要LERF的密集多尺度搜索

### Dr. Splat
同样依赖SAM分割区域提取CLIP特征，用于直接注册到3D高斯。

## 关联
- 用到SAM的论文: [[papers/langsplat]], [[papers/dr-splat]]
- 相关概念: [[concepts/clip]], [[concepts/3d-language-field]]
