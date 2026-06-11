---
title: "CLIP (Contrastive Language-Image Pre-training)"
tags: [concept, external-model, vision-language]
---

## 定义
CLIP是OpenAI训练的视觉-语言基础模型，在4亿图文对上通过对比学习将图像和文本映射到共享的512维嵌入空间。在3DGS中，CLIP是构建[[concepts/3d-language-field|3D语言场]]的语义骨干——其图像编码器提取像素/区域特征，文本编码器将查询文本映射到同一空间，通过余弦相似度实现开放词汇3D查询。

## 直觉理解
CLIP像一个"双语词典"——读过4亿张带文字说明的图片后，它能同时"看懂"图片和"读懂"文字，并把它们翻译成同一种"中间语言"（512维向量）。如果一张猫的照片和文字"cat"的向量很接近，CLIP就知道它们说的是同一件事。

## 在3DGS中的作用

### LangSplat
用OpenCLIP ViT-B/16提取SAM分割区域的CLIP特征作为训练目标，训练3D高斯携带语言特征。查询时CLIP文本编码器将用户文本转为特征，与渲染的语言特征图匹配。

### Dr. Splat
直接将CLIP特征通过光线-高斯交叉注册到主导高斯（无需渲染训练），用预训练PQ压缩CLIP特征。

## 局限性
CLIP对细粒度属性（如"生了锈的银色水龙头"）不够鲁棒，因其训练数据以粗粒度图文对为主。

## 关联
- 用到CLIP的论文: [[papers/2026-05-07/langsplat]], [[papers/2026-05-08/dr-splat]]
- 相关概念: [[concepts/3d-language-field]], [[concepts/product-quantization]]
