---
title: "ADD-SLAM: Adaptive Dynamic Dense SLAM with Gaussian Splatting"
source: "https://arxiv.org/html/2505.19420v1"
author:
published:
created: 2026-05-22
description:
tags:
  - "clippings"
---
Wenhua Wu  Chenpeng Su  Siting Zhu  Tianchen Deng  Zhe Liu  Hesheng Wang  
Shanghai Jiao Tong University Corresponding authors.

###### Abstract

Recent advancements in Neural Radiance Fields (NeRF) and 3D Gaussian-based Simultaneous Localization and Mapping (SLAM) methods have demonstrated exceptional localization precision and remarkable dense mapping performance. However, dynamic objects introduce critical challenges by disrupting scene consistency, leading to tracking drift and mapping artifacts. Existing methods that employ semantic segmentation or object detection for dynamic identification and filtering typically rely on predefined categorical priors, while discarding dynamic scene information crucial for robotic applications such as dynamic obstacle avoidance and environmental interaction. To overcome these challenges, we propose ADD-SLAM: an Adaptive Dynamic Dense SLAM framework based on Gaussian splitting. We design an adaptive dynamic identification mechanism grounded in scene consistency analysis, comparing geometric and textural discrepancies between real-time observations and historical maps. Ours requires no predefined semantic category priors and adaptively discovers scene dynamics. Precise dynamic object recognition effectively mitigates interference from moving targets during localization. Furthermore, we propose a dynamic-static separation mapping strategy that constructs a temporal Gaussian model to achieve online incremental dynamic modeling. Experiments conducted on multiple dynamic datasets demonstrate our method’s flexible and accurate dynamic segmentation capabilities, along with state-of-the-art performance in both localization and mapping.

###### Abstract

In the document, we provide additional details about the following:

1. More information about the datasets.
2. Further implementation details.
3. Additional results and analysis.

## 1 Introduction

Dense visual Simultaneous Localization and Mapping (SLAM) is the foundation of perception, navigation, and planning that finds wide applications in areas such as autonomous driving, mobile robotics, and virtual reality [^1] [^2].

Although existing dense visual SLAM methods based on Neural Radiance Field (NeRF) and 3D Gaussians have shown promising results in static scenes, their performance often deteriorates in complex dynamic environments due to the disruption caused by dynamic objects to the scene’s consistency. Dynamic SLAM faces two key challenges. The first is how to identify dynamic objects. Some methods predominantly rely on pre-trained detection, semantic segmentation, or optical flow networks for dynamic object identification [^3] [^4] [^5] [^6]. They suffer from false detections, generalization issues, and the need for predefined dynamic classes. Even if the objects are static, they will be separated mistakenly due to their class. DG-slam [^7] designs a multi-view depth warp mask to compensate for missing objects. However, the occlusion caused by the view change is also contained in the mask and cannot be distinguished. Gassidy [^8] performs instance segmentation of the scene and relies on object-by-object iterative analysis to distinguish dynamics. The latest WildGS-SLAM [^9] introduces an uncertainty-aware approach that eliminates dependency on prior. However, uncertainties in dynamic object boundaries remain prone to ambiguity. Additionally, when the frame sequence is short, the uncertainty network cannot be trained sufficiently, resulting in significantly weaker capabilities to handle dynamic objects.

The second challenge is how to track and model dynamic objects. Dynamic information is crucial for the perception and interaction of intelligent robots. However, existing dynamic SLAM methods typically filter out dynamic objects, focusing solely on constructing static maps. Although some offline dynamic modeling methods [^10] [^11] [^12] exist, they are time-consuming and require camera poses input, making them unsuitable for SLAM systems.

To address the aforementioned challenges, we propose ADD-SLAM, an adaptive dynamic dense visual SLAM with Gaussian splatting. Unlike existing approaches that rely on priors or uncertainty perception, we design an adaptive dynamic identification mechanism grounded in scene consistency analysis, comparing geometric and textural discrepancies between real-time observations and historical maps. In static scenes, observations from different viewpoints exhibit consistency. When objects move, this consistency is disrupted. We identify dynamic regions by detecting inconsistencies between the rendered images and actual observations and then obtain fine-grained dynamic segmentation using MobileSAM [^13]. Our method does not require predefined dynamic object categories and can adaptively detect dynamics directly from the scene, offering greater flexibility.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x1.png)

Figure 1: ADD-SLAM. Given RGB-D stream, our method achieves precise camera pose tracking while constructing dynamic-static composition maps. Our method can adaptively segment dynamic objects of any category without any semantic priors. The illustration presents effective dynamic tracking and mapping results, and high-quality rendering results of the dynamic-static separation.

Building on accurate dynamic object identification, we continuously perform 2D tracking of dynamic objects. During camera tracking, dynamic objects are excluded to prevent interference, resulting in more accurate localization. In the mapping process, we design a dynamic-static composition mapping method. When an object is first identified as dynamic, it is removed from the static map. The occluded background is gradually filled during the object’s motion. For dynamic objects, we construct a temporal Gaussian model to achieve online incremental dynamic modeling.

Overall, the main contributions of this paper are as follows:

- We propose a novel adaptive dynamic dense visual SLAM, ADD-SLAM, which accurately performs tracking and mapping in complex dynamic environments while modeling dynamic objects. ADD-SLAM achieves promising performance across multiple dynamic datasets.
- We propose a scene consistency analysis-based dynamic identification method that enables category-agnostic adaptive recognition of dynamic objects without requiring semantic priors, which is more accurate and flexible.
- We design a hybrid mapping approach that combines static and dynamic components, utilizing a temporal Gaussian model to achieve online incremental dynamic modeling.

## 2 Related Work

Traditional Visual SLAM. The foundation of dense visual SLAM lies in DTAM [^14], which pioneers real-time tracking and mapping via dense scene representation. In the same period, the KinectFusion method [^15] makes notable strides by using ICP algorithms [^16] and volumetric TSDF to achieve accurate and real-time reconstruction of dense surfaces for indoor scenes. Lots of innovative data structures including Surfels [^17] [^18] and Octrees [^19] [^20], are proposed to improve scalability and reduce memory. In contrast to these methods which rely on per-frame pose optimization, BAD-SLAM [^21] is the first to propose a full Bundle Adjustment (BA) to jointly optimize the keyframes. Recently, numerous deep learning-based SLAM methods [^22] [^23] [^24] [^25] [^26] are introduced to improve the precision and robustness of traditional SLAM methods with various learnable parameters.

NeRF and 3DGS based SLAM. Recent advances in Neural Radiance Fields (NeRF) [^27] and 3D Gaussian splatting (3DGS) [^28] have demonstrated remarkable success in SLAM, particularly due to their flexible scene parameterization and photorealistic rendering capabilities. iMAP [^29] pioneered the integration of NeRF into SLAM, achieving real-time joint optimization, though a single MLP setup often limits reconstruction detail and leads to catastrophic forgetting. This challenge inspired NICE-SLAM [^30] to incorporate a hierarchical scene representation, improving scalability and efficiency. Subsequent studies [^31] [^32] [^33] [^34] [^35] [^36] [^37] [^38] [^39] [^40] have made a series of improvements in scene representation and camera tracking. Considering the higher rendering quality and faster rendering speed of 3DGS, recent research has turned to using 3D Gaussians as map representations [^41] [^42] [^43] [^44] [^45]. However, they assume that the scene is static. The disruption of scene consistency by dynamic objects can lead to significant performance degradation or even complete failure.

SLAM in Dynamic Environments. To handle dynamics, several methods [^5] [^46] [^4] employ semantic segmentation or object detection. However, they rely on predefined dynamic category priors, leading to two inherent limitations: (1) inability to process unknown object categories, and (2) misclassification of stationary objects from predefined dynamic categories as moving objects. DynaMoN [^3] and RoDyn-SLAM [^47] incorporate optical flow estimation, but the inherent ambiguity between object motion and camera motion measurements remains challenging to disambiguate. DG-SLAM [^7] designs a multi-view depth warp mask to compensate for missing objects. However, the occlusion caused by the view change is contained in the mask. Gassidy [^8] performs instance segmentation of the scene and relies on object-by-object iterative analysis to distinguish dynamics. The latest WildGS-SLAM [^9] introduces an uncertainty-aware approach that eliminates dependency on prior. However, uncertainties in dynamic object boundaries remain prone to ambiguity, and the incrementally trained MLP performs poorly at the beginning stage and short sequence case. In contrast, our method adaptively segments arbitrary dynamic objects through scene consistency analysis, requiring no prior knowledge while achieving precise boundary delineation. Furthermore, whereas existing methods simply filter out dynamic elements to construct static maps only, ours simultaneously builds both dynamic and static maps.

## 3 Method

Our proposed adaptive dynamic dense SLAM framework is illustrated in Fig. 2. The input consists of an RGB-D image sequence $\{(I_{t},D_{t})|t=0,1,...,n\}$ and camera intrinsic parameter $K$, while the output of ADD-SLAM includes the camera poses and the dynamic-static composition map. The process begins with static map initialization using the first frame (3.1). Next, dynamic objects in the environment are adaptively segmented based on dynamic consistency analysis, and a dynamic tracking sequence is constructed (3.2). Building upon this, dynamic-static separation is performed on the original static map. Camera pose optimization is then conducted using tracking loss (3.3), followed by dynamic-static composition mapping (3.4).

![Refer to caption](https://arxiv.org/html/2505.19420v1/x2.png)

Figure 2: Overview of ADD-SLAM. The input RGB-D stream is first used to initialize the static map with the first frame. Dynamic objects in the environment are then adaptively segmented based on consistency analysis, and a dynamic tracking sequence is constructed. Building upon this, dynamic-static separation is performed on the original static map. Camera pose optimization is carried out using tracking loss, followed by dynamic-static map optimization.

### 3.1 3D Gaussian Splatting

Our dynamic SLAM employs 3D Gaussian as the static map representation. Following previous 3D Gaussian-based SLAM methods, we initialize the static map using the first frame. The first RGB-D images are reconstructed into a point cloud based on the intrinsic parameters and the initial pose. The point cloud is then initialized as 3D Gaussian ellipsoid $\bm{G}_{s}=\{(\mu_{i},\bm{\Sigma}_{i},o_{i},h_{i})\}.$ Each Gaussian ellipsoid contains the center position $\mu_{i}\in\mathbb{R}^{3}$, covariance matrix $\bm{\Sigma}_{i}\in\mathbb{R}^{3\times 3}$, opacity $o\in\mathbb{R}$, and spherical harmonic coefficients $h\in\mathbb{R}^{3(L+1)^{2}}$, where $L$ is the order of the spherical harmonics. The Gaussian function $g_{i}(x)$ is:

$$
g_{i}(x)=e^{-\frac{1}{2}(x-\mu_{i})^{T}\bm{\Sigma}_{i}^{-1}(x-\mu_{i})}.
$$

Rendering. Given the camera pose $T$, project the 3D Gaussian to 2D image plane. The Gaussian ellipsoid distribution is sorted in depth order to render color, depth, and accumulated opacity.

$$
\hat{I}=\sum_{i\in N}c_{i}\alpha_{i}\prod_{j=1}^{i-1}(1-\alpha_{j}),\quad\hat{%
D}=\sum_{i\in N}d_{i}\alpha_{i}\prod_{j=1}^{i-1}(1-\alpha_{j}),\quad\hat{O}=%
\sum_{i\in N}\alpha_{i}\prod_{j=1}^{i-1}(1-\alpha_{j}),
$$

where $c_{i}$ represents the color of the $i$ -th Gaussian obtained from spherical harmonic coefficients. $d_{i}$ is the depth of the depth of the $i$ -th Gaussian. $\alpha_{i}$ represents the density computed from opacity and covariance.

### 3.2 Adaptive Dynamic Object Segmentation and Tracking

We propose an adaptive dynamic object recognition and segmentation method that does not depend on detection or semantic segmentation models. The following provides a detailed description.

Scene Consistency Analysis. The Gaussian map is built from historical observations. When the scene remains static, the physical world is consistent with the historical map. At this point, the rendered image from the Gaussian map aligns with the observed image. However, when objects in the scene move, the historical map is not updated in time, leading to inconsistency between the physical world and the historical map in the areas where objects are in motion. By comparing the rendered image with the observed image, inconsistencies in the scene can be detected. We simultaneously consider both color and geometric inconsistencies:

$$
I_{err}=\lVert I-\hat{I}\rVert_{2},\quad D_{err}=\lVert D-\hat{D}\rVert_{1}.
$$
 
$$
M_{ic}=(I_{err}>\tau_{I})\cup(D_{err}>\tau_{D}),
$$

where $\tau_{I}$ and $\tau_{D}$ represent the thresholds for color and geometric inconsistencies, respectively. $M_{ic}$ represents the mask of the inconsistent region.

Dynamic Regions Detection. Dynamic objects in the field of view can be classified into two types: one is a dynamic object moving from outside the field of view into it, and the other is an object moving within the field of view. For the first type, the inconsistent region in the observed image corresponds to the dynamic object that has entered the field of view. For the second type, the inconsistent region in the observed image manifests as the area where the dynamic object has newly moved or the previously occluded background has been exposed. The new occlusion caused by the dynamic object in the background will make the observed depth smaller than the rendered depth. In contrast, the newly exposed background region will have an observed depth larger than the rendered depth. This allows for the distinction between dynamic objects and the background.

$$
M_{ic}^{d}=M_{ic}\cap((D-\hat{D})<0).
$$

Dynamic Fine Segmentation. We utilize MobileSAM [^13] to perform detailed segmentation on dynamic objects, which is a vision foundation model for segmentation guided by prompts. Due to the minimal object movement between consecutive frames (with a time interval of 1/30s), the resulting dynamic inconsistency region represents only a small portion of the object. Therefore, we use the center of the inconsistent region as a prompt input for MobileSAM $f_{\theta}$ to obtain the complete dynamic object segmentation.

$$
M_{d}=f_{\theta}(I,\textit{o}(M_{ic}^{d})),
$$

where $\textit{o}(\cdot)$ represents the center of the inscribed circle.

Dynamic Object Tracking. Building upon the identification of dynamic objects in the scene, we construct a 2D dynamic tracking sequence. Each dynamic object is assigned a unique $id$ along with its mask in each frame and the object center, defined as the center of the inscribed circle within the mask. When the next frame is processed, previously recognized objects do not require inconsistency re-detection. Instead, the object center serves as a prompt for MobileSAM to generate an updated mask and refine the object center, enabling continuous object tracking.

$$
M_{d}^{t+1}=f_{\theta}(I_{t+1},\textit{o}(M_{d}^{t})).
$$

For dynamic objects initially present within the field of view rather than those entering from outside, We backtrack the frames before the detection of the dynamics, ensuring temporal-coherent segmentation across all frames.

Unlike traditional object detection methods that operate on single frames and ignore temporal consistency, our approach incorporates dynamic tracking to naturally associate objects across frames, effectively capturing their motion over time. In contrast to existing dynamic segmentation methods, which often depend on category-specific pre-trained detection networks, our method identifies dynamic objects by detecting scene inconsistencies caused by motion. It is entirely category-agnostic and does not rely on any pre-trained detectors. By leveraging the MobileSAM visual foundation model, we achieve fine-grained segmentation of dynamic objects, regardless of their category.

### 3.3 Camera Tracking

For each incoming frame, we employ frame-to-model tracking. The camera pose is initialized based on the constant velocity assumption. Then, it is refined using rendering loss with well-reconstructed static regions.

$$
M_{track}=(\neg M_{d})\cap(\hat{O}>\tau_{track}),
$$
 
$$
T_{t}=\operatorname*{arg\,min}\lambda_{track}\sum{M_{track}\cdot\lVert\hat{I}-%
I\rVert_{1}}+(1-\lambda_{track})\sum{(M_{track}\cap M_{v})\cdot\lVert\hat{D}-D%
\rVert_{1}},
$$

where $\tau_{track}$ represents the opacity threshold for the tracking region. $M_{v}$ is the valid region of the ground truth depth, taking into account the presence of holes in the depth ground truth.

To mitigate pose drift in extended sequences, we incorporate loop detection and global bundle adjustment (BA). Following Droid-SLAM [^26], we integrate a pre-trained optical flow model with Dense Bundle Adjustment Layer (DBA) to optimize keyframe camera poses and depth. In contrast to WildGS-SLAM [^9] that introduces uncertainty maps during BA optimization, we leverage acquired dynamic masks to eliminate interference from moving entities while preserving static scene integrity. Following DG-SLAM [^7], the cost function over the keyframe graph is defined as:

$$
\mathbf{E}(\mathbf{T},\mathbf{d})=\sum_{(i,j)\in\mathcal{E}}\|\mathbf{p}_{ij}^%
{*}-\Pi_{c}(\mathbf{T}_{ij}\circ\Pi_{c}^{-1}(\mathbf{p}_{i},\mathbf{d}_{i}))\|%
^{2}_{\Sigma_{ij}\cdot\neg M_{d}},\quad\Sigma_{ij}=\operatorname{diag}\omega_{%
ij},
$$

where $\mathbf{p}_{ij}^{*}$ where $\Pi_{c}$ denotes the projection transformation from 3D coordinates to the image plane. $\mathbf{p}_{i}$ represents pixel coordinates, $\mathbf{d}_{i}$ indicates inverse depth values. $\mathbf{T}_{ij}$ corresponds to the relative camera pose between frames $i$ and $j$. $\mathbf{p}_{ij}^{*}$ represents the propagated coordinates of pixel $\mathbf{p}_{i}$ in frame $j$ through optical flow estimation. $\|\cdot\|^{2}_{\Sigma_{ij}\cdot\neg M_{d}}$ denotes the Mahalanobis distance weighted by confidence metric $\Sigma_{ij}$, while filtering the dynamic.

### 3.4 Dynamic-static Composite Mapping

Unlike existing dynamic SLAM [^7] [^9] [^8] that perform elimination of dynamic objects, we propose a dynamic-static composite mapping strategy that leverages temporal Gaussian models to achieve online incremental dynamic modeling.

Dynamic-Static Separation. At the start of ADD-SLAM, we initialize a completely static map. Once the detection module identifies dynamic objects, we immediately separate them from the static map. Specifically, we use MobileSAM to segment dynamic objects from the rendered images, thereby determining their 2D positions within the map. Then, using the depth map and camera intrinsic and extrinsic parameters, we obtain the point cloud of the dynamic objects. In the original static Gaussian map, we filter out the Gaussian spheres representing the dynamic object regions, thus achieving adaptive dynamic-static separation.

Static Mapping. For each newly added keyframe, we insert Gaussian ellipsoids into the static Gaussian map to fill regions with holes or poor quality in the rendered output.

$$
M_{instert}=(\neg M_{d})\cap M_{v}\cap(\hat{O}<\tau_{map}),
$$

where $\tau_{map}$ represents the opacity threshold for the static mapping region. The RGB-D pixels in $M_{in}$ will be initialized as Gaussian ellipsoids and incorporated into the static Gaussian map. Subsequently, keyframes are selected from the keyframe set to optimize the static map. We compute the rendering loss for the valid static regions:

$$
\begin{split}L_{I}=(1-\lambda_{ssim})\frac{1}{M_{map}}\sum M_{map}\cdot\lVert%
\hat{I}-I\rVert_{1}+\lambda_{ssim}SSIM(\hat{I},I,M_{map}),\end{split}
$$
 
$$
L_{D}=\frac{1}{M_{map}}\sum M_{map}\cdot\lVert\hat{D}-D\rVert_{1},\quad M_{map%
}=(\neg M_{d})\cap M_{v},
$$

where $\lambda_{ssim}$ is the weight of ssim loss. The final static mapping loss is:

$$
L_{map}^{static}=\lambda_{color}L_{I}+\lambda_{depth}L_{D}+\lambda_{reg}L_{reg},
$$

where $L_{reg}$ is the Gaussian ellipsoid scale regularization loss from [^48].

Dynamic Mapping. For each tracked dynamic object $id$, we construct a temporal Gaussian model:

$$
\bm{G}_{d}^{id}(t)=\{(\mu_{i}^{t},\bm{\Sigma}_{i}^{t},o_{i}^{t},h_{i}^{t})\}.
$$

Each Gaussian ellipsoid at a given time is initialized using the corresponding 2D tracking results. At time $t$, the corresponding dynamic Gaussians $\{\bm{G}_{d}^{id}(t),id\in ID$ } are used to render the dynamic image:

$$
\hat{I}_{d}=\sum_{i\in N_{d}}c_{i}^{t}\alpha_{i}^{t}\prod_{j=1}^{i-1}(1-\alpha%
_{j}^{t}),\quad\hat{D}_{d}=\sum_{i\in N_{d}}d_{i}^{t}\alpha_{i}^{t}\prod_{j=1}%
^{i-1}(1-\alpha_{j}^{t}).
$$

Then, the dynamic Gaussians are optimized using the rendering loss:

$$
\begin{split}L_{I}^{d}=(1-\lambda_{ssim})\frac{1}{M_{map}^{d}}\sum M_{map}^{d}%
\cdot\lVert\hat{I}_{d}-I\rVert_{1}+\lambda_{ssim}SSIM(\hat{I}_{d},I,M_{map}^{d%
}),\end{split}
$$
 
$$
L_{D}^{d}=\frac{1}{M_{map}^{d}}\sum M_{map}^{d}\cdot\lVert\hat{D}_{d}-D\rVert_%
{1},\quad M_{map}^{d}=M_{d}\cap M_{v}.
$$

The final dynamic mapping loss is:

$$
L_{map}^{d}=\lambda_{color}L_{I}^{d}+\lambda_{depth}L_{D}^{d}+\lambda_{reg}L_{%
reg}.
$$
![Refer to caption](https://arxiv.org/html/2505.19420v1/x3.png)

Figure 3: Rendering Visualization. Compared to other methods, ADD-SLAM not only accurately reconstructs the static background but also captures fine details of the dynamic foreground. Our dynamic mask is more complete and precise than the uncertainty of WildGS-SLAM 9.

Table 1: Camera tracking results on Bonn dataset. "\*" denotes the version reproduced by NICE-SLAM. "-" denotes the absence of mention. "X" denotes a failure in execution, with no valid result. " ${\dagger}$ " indicates the replacement of depth estimation with ground-truth depth. The metric unit is \[cm\]. Best results are highlighted as first, second, and third.

<table><tbody><tr><td>Methods</td><td>Input</td><td colspan="2">balloon</td><td colspan="2">balloon2</td><td colspan="2">ps_track</td><td colspan="2">ps_track2</td><td colspan="2">ball_track</td><td colspan="2">mv_box2</td><td colspan="2">Avg.</td></tr><tr><td>Traditional</td><td></td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td></tr><tr><td>ORB-SLAM3 <sup><a href="#fn:49">49</a></sup></td><td>RGBD</td><td>5.8</td><td>2.8</td><td>17.7</td><td>8.6</td><td>70.7</td><td>32.6</td><td>77.9</td><td>43.8</td><td>3.1</td><td>1.6</td><td>3.5</td><td>1.5</td><td>29.8</td><td>15.2</td></tr><tr><td>Droid-VO <sup><a href="#fn:26">26</a></sup></td><td>RGBD</td><td>5.4</td><td>-</td><td>4.6</td><td>-</td><td>21.34</td><td>-</td><td>46.0</td><td>-</td><td>8.9</td><td>-</td><td>5.9</td><td>-</td><td>15.4</td><td>-</td></tr><tr><td>DynaSLAM <sup><a href="#fn:50">50</a></sup></td><td>RGBD</td><td>3.0</td><td>-</td><td>2.9</td><td>-</td><td>6.1</td><td>-</td><td>7.8</td><td>-</td><td>4.9</td><td>-</td><td>3.9</td><td>-</td><td>4.77</td><td>-</td></tr><tr><td>ReFusion <sup><a href="#fn:51">51</a></sup></td><td>RGBD</td><td>17.5</td><td>-</td><td>25.4</td><td>-</td><td>28.9</td><td>-</td><td>46.3</td><td>-</td><td>30.2</td><td>-</td><td>17.9</td><td>-</td><td>27.7</td><td>-</td></tr><tr><td>NeRF based</td><td></td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td></tr><tr><td>iMAP <sup>∗</sup> <sup><a href="#fn:29">29</a></sup></td><td>RGBD</td><td>14.9</td><td>5.4</td><td>67.0</td><td>19.2</td><td>28.3</td><td>12.9</td><td>52.8</td><td>20.9</td><td>24.8</td><td>11.2</td><td>28.3</td><td>35.3</td><td>36.1</td><td>17.5</td></tr><tr><td>NICE-SLAM <sup><a href="#fn:30">30</a></sup></td><td>RGBD</td><td>X</td><td>X</td><td>66.8</td><td>20.0</td><td>54.9</td><td>27.5</td><td>45.3</td><td>17.5</td><td>21.2</td><td>13.1</td><td>31.9</td><td>13.6</td><td>-</td><td>-</td></tr><tr><td>Vox-Fusion <sup><a href="#fn:33">33</a></sup></td><td>RGBD</td><td>65.7</td><td>30.9</td><td>82.1</td><td>52.0</td><td>128.6</td><td>52.5</td><td>162.2</td><td>46.2</td><td>43.9</td><td>16.5</td><td>47.5</td><td>19.5</td><td>88.4</td><td>36.3</td></tr><tr><td>Co-SLAM <sup><a href="#fn:31">31</a></sup></td><td>RGBD</td><td>28.8</td><td>9.6</td><td>20.6</td><td>8.1</td><td>61.0</td><td>22.2</td><td>59.1</td><td>24.0</td><td>38.3</td><td>17.4</td><td>70.0</td><td>25.5</td><td>46.3</td><td>17.8</td></tr><tr><td>ESLAM <sup><a href="#fn:32">32</a></sup></td><td>RGBD</td><td>22.6</td><td>12.2</td><td>36.2</td><td>19.9</td><td>48.0</td><td>18.7</td><td>51.4</td><td>23.2</td><td>12.4</td><td>6.6</td><td>17.7</td><td>7.5</td><td>31.4</td><td>14.7</td></tr><tr><td>RoDyn-SLAM <sup><a href="#fn:47">47</a></sup></td><td>RGBD</td><td>7.9</td><td>2.7</td><td>11.5</td><td>6.1</td><td>14.5</td><td>4.6</td><td>13.8</td><td>3.5</td><td>13.3</td><td>4.7</td><td>12.6</td><td>4.7</td><td>12.3</td><td>4.38</td></tr><tr><td>DynaMoN(MS&SS) <sup><a href="#fn:3">3</a></sup></td><td>RGB</td><td>2.8</td><td>-</td><td>2.7</td><td>-</td><td>14.8</td><td>-</td><td>2.2</td><td>-</td><td>3.4</td><td>-</td><td>2.7</td><td>-</td><td>4.77</td><td>-</td></tr><tr><td>3DGS based</td><td></td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td></tr><tr><td>SplaTAM <sup><a href="#fn:44">44</a></sup></td><td>RGBD</td><td>40.0</td><td>14.6</td><td>39.5</td><td>15.8</td><td>217.9</td><td>81.2</td><td>131.0</td><td>33.1</td><td>20.2</td><td>16.3</td><td>17.1</td><td>9.3</td><td>77.6</td><td>28.4</td></tr><tr><td>MonoGS <sup><a href="#fn:45">45</a></sup></td><td>RGBD</td><td>31.2</td><td>15.3</td><td>26.7</td><td>13.5</td><td>43.8</td><td>16.8</td><td>48.4</td><td>16.6</td><td>4.7</td><td>2.4</td><td>7.1</td><td>3.5</td><td>27.0</td><td>11.4</td></tr><tr><td>GS-ICP SLAM <sup><a href="#fn:52">52</a></sup></td><td>RGBD</td><td>42.2</td><td>14.4</td><td>57.5</td><td>22.4</td><td>87.8</td><td>40.6</td><td>49.8</td><td>21.2</td><td>32.1</td><td>11.7</td><td>26.0</td><td>12.4</td><td>49.2</td><td>20.5</td></tr><tr><td>DG-SLAM <sup><a href="#fn:7">7</a></sup></td><td>RGBD</td><td>3.7</td><td>-</td><td>4.1</td><td>-</td><td>4.5</td><td>-</td><td>6.9</td><td>-</td><td>10.0</td><td>-</td><td>3.5</td><td>-</td><td>5.45</td><td>-</td></tr><tr><td>WildGS-SLAM <sup><a href="#fn:9">9</a></sup></td><td>RGB</td><td>2.9</td><td>1.2</td><td>2.5</td><td>1.2</td><td>3.6</td><td>1.9</td><td>3.1</td><td>1.4</td><td>3.1</td><td>1.6</td><td>2.4</td><td>1.3</td><td>2.93</td><td>1.43</td></tr><tr><td>WildGS-SLAM <math><semantics><mo>†</mo> <ci>†</ci> <annotation>{\dagger}</annotation> <annotation>†</annotation></semantics></math> <sup><a href="#fn:9">9</a></sup></td><td>RGBD</td><td>2.4</td><td>1.0</td><td>2.4</td><td>1.2</td><td>3.4</td><td>1.9</td><td>3.1</td><td>1.4</td><td>3.4</td><td>1.9</td><td>2.6</td><td>1.3</td><td>2.88</td><td>1.45</td></tr><tr><td>Ours</td><td>RGBD</td><td>2.7</td><td>1.1</td><td>2.3</td><td>0.8</td><td>2.4</td><td>1.1</td><td>3.7</td><td>1.4</td><td>3.4</td><td>1.2</td><td>2.1</td><td>0.8</td><td>2.77</td><td>1.05</td></tr></tbody></table>

Table 2: Camera tracking results on TUM RGB-D dataset."\*" denotes the version reproduced by NICE-SLAM. "-" denotes the absence of mention. "X" denotes a failure in execution, with no valid result. The metric unit is \[cm\]. Best results are highlighted as first, second, and third.

<table><tbody><tr><td rowspan="2">Methods</td><td rowspan="2">Input</td><td colspan="8">Dynamic</td><td colspan="4">Static</td><td colspan="2" rowspan="2">Avg.</td></tr><tr><td colspan="2">fr3/wk_xyz</td><td colspan="2">fr3/wk_hf</td><td colspan="2">fr3/wk_st</td><td colspan="2">fr3/st_hf</td><td colspan="2">fr1/xyz</td><td colspan="2">fr1/rpy</td></tr><tr><td>Traditional</td><td></td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td></tr><tr><td>ORB-SLAM3 <sup><a href="#fn:49">49</a></sup></td><td>RGBD</td><td>28.1</td><td>12.2</td><td>30.5</td><td>9.0</td><td>2.0</td><td>1.1</td><td>2.6</td><td>1.6</td><td>1.1</td><td>0.6</td><td>2.2</td><td>1.3</td><td>11.1</td><td>4.3</td></tr><tr><td>DVO-SLAM <sup><a href="#fn:53">53</a></sup></td><td>RGBD</td><td>59.7</td><td>-</td><td>52.9</td><td>-</td><td>21.2</td><td>-</td><td>6.2</td><td>-</td><td>1.1</td><td>-</td><td>2.0</td><td>-</td><td>22.9</td><td>-</td></tr><tr><td>DynaSLAM <sup><a href="#fn:50">50</a></sup></td><td>RGBD</td><td>1.7</td><td>-</td><td>2.6</td><td>-</td><td>0.7</td><td>-</td><td>2.8</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>ReFusion <sup><a href="#fn:51">51</a></sup></td><td>RGBD</td><td>9.9</td><td>-</td><td>10.4</td><td>-</td><td>1.7</td><td>-</td><td>11.0</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>NeRF based</td><td></td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td></tr><tr><td>iMAP <sup>∗</sup> <sup><a href="#fn:29">29</a></sup></td><td>RGBD</td><td>111.5</td><td>43.9</td><td>X</td><td>X</td><td>137.3</td><td>21.7</td><td>93.0</td><td>35.3</td><td>7.9</td><td>7.3</td><td>16.0</td><td>13.8</td><td>-</td><td>-</td></tr><tr><td>NICE-SLAM <sup><a href="#fn:30">30</a></sup></td><td>RGBD</td><td>113.8</td><td>42.9</td><td>X</td><td>X</td><td>88.2</td><td>27.8</td><td>45.0</td><td>14.4</td><td>4.6</td><td>3.8</td><td>3.4</td><td>2.5</td><td>-</td><td>-</td></tr><tr><td>Vox-Fusion <sup><a href="#fn:33">33</a></sup></td><td>RGBD</td><td>146.6</td><td>32.1</td><td>X</td><td>X</td><td>109.9</td><td>25.5</td><td>89.1</td><td>28.5</td><td>1.8</td><td>0.9</td><td>4.3</td><td>3.0</td><td>-</td><td>-</td></tr><tr><td>Co-SLAM <sup><a href="#fn:31">31</a></sup></td><td>RGBD</td><td>51.8</td><td>25.3</td><td>105.1</td><td>42.0</td><td>49.5</td><td>10.8</td><td>4.7</td><td>2.2</td><td>2.3</td><td>1.2</td><td>3.9</td><td>2.8</td><td>36.3</td><td>14.1</td></tr><tr><td>ESLAM <sup><a href="#fn:32">32</a></sup></td><td>RGBD</td><td>45.7</td><td>28.5</td><td>60.8</td><td>27.9</td><td>93.6</td><td>20.7</td><td>3.6</td><td>1.6</td><td>1.1</td><td>0.6</td><td>2.2</td><td>1.2</td><td>34.5</td><td>13.5</td></tr><tr><td>RoDyn-SLAM <sup><a href="#fn:47">47</a></sup></td><td>RGBD</td><td>8.3</td><td>5.5</td><td>5.6</td><td>2.8</td><td>1.7</td><td>0.9</td><td>4.4</td><td>2.2</td><td>1.5</td><td>0.8</td><td>2.8</td><td>1.5</td><td>4.05</td><td>2.28</td></tr><tr><td>DynaMoN(MS&SS) <sup><a href="#fn:3">3</a></sup></td><td>RGB</td><td>1.4</td><td>-</td><td>1.9</td><td>-</td><td>0.7</td><td>-</td><td>2.3</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>3DGS based</td><td></td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td><td>RMSE</td><td>S.D.</td></tr><tr><td>SplaTAM <sup><a href="#fn:44">44</a></sup></td><td>RGBD</td><td>160.5</td><td>42.4</td><td>X</td><td>X</td><td>42.6</td><td>13.0</td><td>14.5</td><td>6.2</td><td>1.1</td><td>0.6</td><td>3.2</td><td>1.5</td><td>44.4</td><td>12.8</td></tr><tr><td>MonoGS <sup><a href="#fn:45">45</a></sup></td><td>RGBD</td><td>28.4</td><td>12.3</td><td>47.8</td><td>16.5</td><td>15.3</td><td>8.4</td><td>13.9</td><td>3.2</td><td>1.0</td><td>0.4</td><td>2.6</td><td>1.3</td><td>18.2</td><td>7.0</td></tr><tr><td>GS-ICP <sup><a href="#fn:52">52</a></sup></td><td>RGBD</td><td>68.9</td><td>50.8</td><td>84.6</td><td>34.3</td><td>87.5</td><td>16.9</td><td>11.2</td><td>2.7</td><td>1.4</td><td>0.7</td><td>4.2</td><td>3.9</td><td>43.0</td><td>18.2</td></tr><tr><td>DG-SLAM <sup><a href="#fn:7">7</a></sup></td><td>RGBD</td><td>1.6</td><td>-</td><td>0.6</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>WildGS-SLAM <sup><a href="#fn:9">9</a></sup></td><td>RGB</td><td>1.2</td><td>0.6</td><td>1.5</td><td>0.8</td><td>0.5</td><td>0.2</td><td>1.8</td><td>1.1</td><td>0.9</td><td>0.5</td><td>2.3</td><td>1.3</td><td>1.37</td><td>0.75</td></tr><tr><td>WildGS-SLAM <math><semantics><mo>†</mo> <ci>†</ci> <annotation>{\dagger}</annotation> <annotation>†</annotation></semantics></math> <sup><a href="#fn:9">9</a></sup></td><td>RGBD</td><td>1.2</td><td>0.6</td><td>1.4</td><td>0.7</td><td>0.5</td><td>0.2</td><td>1.7</td><td>1.0</td><td>0.9</td><td>0.5</td><td>2.2</td><td>1.0</td><td>1.32</td><td>0.67</td></tr><tr><td>Ours</td><td>RGBD</td><td>1.4</td><td>0.9</td><td>1.6</td><td>0.8</td><td>0.5</td><td>0.2</td><td>1.3</td><td>0.6</td><td>1.0</td><td>0.5</td><td>1.7</td><td>0.9</td><td>1.25</td><td>0.65</td></tr></tbody></table>

## 4 Experiment

### 4.1 Experimental Setting

Dataset. We evaluate ADD-SLAM on three real-world dynamic datasets: the TUM RGB-D [^54] dataset, the Bonn dataset [^55], and the DAVIS dataset [^56].

Evaluation Metrics. For camera tracking performance, we use the Root Mean Square Error (RMSE) and Standard Deviation (S.D.) of the Absolute Trajectory Error (ATE). For the quality of Gaussian-based mapping, we employ image rendering quality metrics, including Peak Signal-to-Noise Ratio (PSNR), Structure Similarity Index Measure (SSIM), and Learned Perceptual Image Patch Similarity (LPIPS). Since the original images contain both static backgrounds and dynamic foregrounds, the rendering metrics can effectively reflect the performance of dynamic-static composition mapping.

Baselines. We conduct extensive and comprehensive comparisons between ADD-SLAM and traditional SLAM methods, NeRF-based SLAM methods, and 3D Gaussian-based SLAM methods to highlight the superiority of our method.

Implementation Details. The order of spherical harmonics $L$ is 0. The thresholds for color and geometric inconsistencies $\tau_{I}=20\cdot\operatorname{median}(I_{err})$ and $\tau_{D}=20\cdot\operatorname{median}(D_{err})$. The opacity thresholds for tracking $\tau_{track}$ and mapping $\tau_{map}$ are set to 0.7 and 0.8, respectively. The weights of loss $\lambda_{track}=0.6,\lambda_{ssim}=0.2,\lambda_{color}=1.0,\lambda_{depth}=1.0%
,\lambda_{reg}=1.0$. The iterative optimization steps for tracking and mapping are set to 100. Adaptive dynamic detection is performed every 5 frames for Bonn and DAVIS dataset, and every 10 frames for TUM RGB-D dataset. All experiments are conducted on a server equipped with a Intel Platinum 8362 CPU and an NVIDIA A100 GPU.

### 4.2 Experimental Results

Evaluation of Camera Tracking Performance. The camera tracking results on the Bonn and TUM RGB-D datasets are shown in Tab. 1 and Tab. 2. Note that the original WildGS-SLAM [^9] uses RGB input with depth estimation. For fair comparison, we replace the estimated depth with ground truth depth, denoted as " ${\dagger}$ ". Compared with various traditional methods, NeRF-based and 3DGS-based methods, our method achieves state-of-the-art performance in both static and dynamic scenarios.

Table 3: Rendering performance on Bonn dataset.

<table><tbody><tr><td>Methods</td><td colspan="3">balloon</td><td colspan="3">balloon2</td><td colspan="3">ps_track</td><td colspan="3">ps_track2</td><td colspan="3">ball_track</td><td colspan="3">mv_box2</td><td colspan="3">Avg</td></tr><tr><td></td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td><td>PSNR</td><td>SSIM</td><td>LPIPS</td></tr><tr><td>SplaTAM <sup><a href="#fn:44">44</a></sup></td><td>16.92</td><td>0.78</td><td>0.22</td><td>17.35</td><td>0.69</td><td>0.30</td><td>17.11</td><td>0.62</td><td>0.33</td><td>15.54</td><td>0.58</td><td>0.37</td><td>19.83</td><td>0.80</td><td>0.22</td><td>20.93</td><td>0.85</td><td>0.18</td><td>17.95</td><td>0.72</td><td>0.27</td></tr><tr><td>MonoGS <sup><a href="#fn:45">45</a></sup></td><td>20.25</td><td>0.77</td><td>0.34</td><td>18.54</td><td>0.72</td><td>0.38</td><td>19.64</td><td>0.76</td><td>0.37</td><td>18.47</td><td>0.71</td><td>0.40</td><td>23.40</td><td>0.81</td><td>0.33</td><td>23.51</td><td>0.84</td><td>0.26</td><td>20.64</td><td>0.77</td><td>0.35</td></tr><tr><td>Ours</td><td>22.91</td><td>0.91</td><td>0.22</td><td>19.10</td><td>0.80</td><td>0.31</td><td>23.53</td><td>0.91</td><td>0.25</td><td>22.95</td><td>0.91</td><td>0.24</td><td>23.23</td><td>0.88</td><td>0.28</td><td>22.74</td><td>0.89</td><td>0.27</td><td>22.41</td><td>0.89</td><td>0.26</td></tr></tbody></table>

Table 4: Comparison of different methods in terms of running time (ms).

| Methods | Dynamic Seg. | Tracking | Mapping |
| --- | --- | --- | --- |
| Rodyn-SLAM [^47] | 278.66 | 875.70 | 1083.60 |
| SplaTAM [^44] | \- | 2630.36 | 548.06 |
| WildGS-SLAM [^9] | 25.77 | 2467.28 | 2948.27 |
| Ours | 68.79 | 1025.39 | 1108.78 |

Evaluation of Mapping Performance. Unlike existing approaches that either neglect dynamic elements or directly filter them out for static mapping, our method achieves dynamic-static decoupled mapping. To evaluate comprehensive mapping performance, we perform dynamic-static combined rendering to assess the complete scene reconstruction $\bm{G}_{all}(t)=\bm{G}_{s}\cup\{\bm{G}_{d}^{id}(t),id\in ID\}$. Tab. 3 presents quantitative evaluations of our mapping results, demonstrating significant superiority over state-of-the-art dense mapping methods. Fig. 3 provides visual comparisons of rendering quality: SplaTAM [^44] and MonoGS [^45] fail to handle dynamic elements, producing extensive blur and artifacts. Although WildGS-SLAM [^9] employs uncertainty-aware dynamic removal, its ambiguous boundary delineation of uncertain dynamic objects leads to residual interference, exemplified by the incomplete foot segmentation in row 2, where ground plane residuals persist. In contrast, our method achieves precise dynamic object segmentation with clean background reconstruction. Furthermore, ours uniquely enables dynamic object modeling, a capability absent in comparative methods.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x4.png)

Figure 4: Comparison between our dynamic mask and the uncertainty of WildGS-SLAM 9 on the DAVIS dataset.

Evaluation of dynamic mask. Considering that the scenes and dynamic categories in the Bonn and TUM-RGBD datasets are limited, we conducted experiments on the dedicated dynamic segmentation dataset DAVIS, which contains richer scenes and dynamic objects. Fig. 4 shows a comparison between our dynamic mask and the uncertainty of WildGS-SLAM [^9]. Our dynamic mask is more complete and precise than WildGS-SLAM’s uncertainty, and it is not disturbed by the background. The dynamic segmentation of various objects in multiple environments demonstrates the adaptability and robustness of our method.

Table 5: Comparison of tracking metrics of different ways to manange dynamic segmentation.

<table><tbody><tr><td>Methods</td><td colspan="2">balloon</td><td colspan="2">ball_track</td><td colspan="2">mv_box2</td></tr><tr><td></td><td>RMSE</td><td>SD</td><td>RMSE</td><td>SD</td><td>RMSE</td><td>SD</td></tr><tr><td>a. Ours w/o dynamic detection</td><td>52.5</td><td>21.6</td><td>15.2</td><td>5.2</td><td>18.3</td><td>5.4</td></tr><tr><td>b. Ours w/ MaskDINO <sup><a href="#fn:57">57</a></sup></td><td>5.5</td><td>2.1</td><td>11.4</td><td>4.6</td><td>12.5</td><td>3.9</td></tr><tr><td>c. Ours w/o keyframe DBA</td><td>3.3</td><td>1.0</td><td>6.9</td><td>3.9</td><td>7.4</td><td>3.0</td></tr><tr><td>d. ADD-SLAM (Ours)</td><td>2.7</td><td>1.0</td><td>3.4</td><td>1.2</td><td>2.1</td><td>0.8</td></tr></tbody></table>

Runtime Analysis. Tab. 4 presents the runtime analysis, including the time for dynamic segmentation, camera tracking, and mapping. Our tracking and mapping times are comparable to other methods, while additionally performing dynamic mapping. For dynamic segmentation, our method is more efficient than Rodyn-SLAM [^47], which relies on pre-trained semantic segmentation and optical flow networks.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x5.png)

Figure 5: Comparison of the dynamic segmentation results of our method with those obtained using a semantic segmentation network.

Ablation Study We conduct an ablation study on our adaptive dynamic segmentation. Fig. 5 presents a comparison between our method’s dynamic segmentation results and those obtained by a semantic segmentation network. We utilize MaskDINO [^57], with the predefined dynamic category set to “human". Unlike prior-based semantic segmentation, our method can adaptively detect atypical moving objects, such as boxes and balloons, enabling more precise and flexible dynamic segmentation. Tab. 5 shows the camera tracking results under different settings: a. without dynamic segmentation, b. using the prior-based semantic segmentation, and d. employing our adaptive dynamic segmentation. With more accurate and flexible dynamic segmentation, camera tracking accuracy is significantly improved. Additionally, we validated the effect of keyframe DBA. As shown in row c. of Tab. 5, keyframe DBA can significantly improve tracking accuracy.

## 5 Conclusion

We propose ADD-SLAM, a novel dynamic dense visual SLAM system. We introduce an adaptive dynamic object identification method based on scene consistency analysis, which eliminates the need for pre-trained detection or optical flow networks, offering greater accuracy and flexibility. Unlike existing methods that directly filter out dynamic objects, we design a hybrid mapping approach that models dynamic objects by constructing dynamic Gaussian sequences, preserving scene dynamics. Extensive experiments demonstrate the outstanding performance of our method, achieving not only accurate tracking but also realistic dynamic-static scene modeling. Our method provides a technical foundation for robotic localization and perception in complex dynamic environments. Limitation: Although our method has achieved remarkable performance, it relies on mobileSAM to segment inconsistent regions. Partial segmentation or over-segmentation in complex environments can negatively impact the performance.

## References

## ADD-SLAM: Adaptive Dynamic Dense SLAM with Gaussian Splatting Supplementary Material

## Appendix A Datasets

TUM RGB-D dataset [^54]. The TUM RGB-D Dataset offers a comprehensive collection of indoor RGB-D sequences recorded using a Microsoft Kinect sensor at 30 Hz with a resolution of 640×480. Ground-truth trajectories were captured using a high-precision motion capture system operating at 100 Hz.

Bonn dataset [^55]. The Bonn RGB-D Dynamic Dataset is a dataset for RGB-D SLAM, containing highly dynamic sequences capturing human activities such as object manipulation and interaction with balloons. Each sequence includes ground-truth camera poses obtained via an OptiTrack Prime 13 motion capture system.

DAVIS Dataset [^56]. The Densely Annotated Video Segmentation (DAVIS) dataset comprises high-resolution video sequences capturing a wide array of dynamic scenes and moving objects. It includes scenarios ranging from human activities and animal movements to complex object interactions and natural phenomena, providing a rich variety of motion patterns and object appearances. DAVIS doesn’t contain depth information. Following WildGS-SLAM [^9], we leverage Depth Anything V2 [^58] to estimate depth, ensuring compatibility with our pipeline.

## Appendix B Further implementation details

Tracking settings. We employ a weighted combination of color and depth losses for tracking, with weights set to $w_{\text{color}}=0.6$ and $w_{\text{depth}}=0.4$, respectively. Each frame is optimized for 100 iterations. The learning rates for camera pose optimization are set to 0.002 for rotation and 0.01 for translation. To mitigate the influence of outliers, alpha and depth filtering are applied to generate masks during the computation of the tracking loss. The tracking loss is defined as:

$$
\mathcal{L}_{\text{track}}=w_{\text{color}}\cdot\mathcal{L}_{\text{color}}+w_{%
\text{depth}}\cdot\mathcal{L}_{\text{depth}}.
$$

Mapping settings. For mapping, the position learning rate decays from an initial value of 0.001 to a final value of $1.6\times 10^{-6}$. The learning rates for color, opacity, scaling, and rotation are set to 0.0025, 0.05, 0.005, and 0.001, respectively. Similar to tracking, each frame undergoes 100 iterations. The opacity threshold is set to 0.8 during densification and 0.3 during pruning. The weights for the composite losses are configured as $\lambda_{\text{ssim}}=0.2$, $\lambda_{\text{color}}=1.0$, $\lambda_{\text{depth}}=1.0$, and $\lambda_{\text{reg}}=1.0$. The color loss is defined as:

$$
\mathcal{L}_{\text{color}}=(1-w_{\text{ssim}})\cdot\mathcal{L}_{\text{rgb}}+w_%
{\text{ssim}}\cdot\mathcal{L}_{\text{ssim}}.
$$

The overall tracking loss function, incorporating regularization, is:

$$
\mathcal{L}_{\text{map}}=w_{\text{color}}\cdot\mathcal{L}_{\text{color}}+w_{%
\text{depth}}\cdot\mathcal{L}_{\text{depth}}+w_{\text{reg}}\cdot\mathcal{L}_{%
\text{reg}}.
$$

Adaptive dynamic detection and tracking settings. Adaptive dynamic object detection is performed every 5 frames for the Bonn and DAVIS datasets, and every 10 frames for the TUM RGB-D dataset. For 2D dynamic tracking, tracking is terminated if the center of a dynamic object approaches within 4% of the image boundary. Additionally, tracking is considered erroneous and is terminated if the dynamic object’s mask area increases by more than 1.5× or its center moves over 20% of the field of view within a single frame.

## Appendix C Additional results and analysis

Adaptive dynamic segmentation and dynamic-static separation mapping. We provide additional visualizations of the adaptive dynamic segmentation and dynamic-static separation mapping process during ADD-SLAM execution, as shown in Fig. 6 and Fig. 7. We initialize the first frame as a static Gaussian map. Then, adaptive dynamic segmentation is performed based on inconsistency detection. When a dynamic object is detected, it is separated from the static map, and a sequential dynamic Gaussian is constructed for dynamic mapping. The holes in the static map are gradually filled as the object moves.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x6.png)

Figure 6: Visualizations of the adaptive dynamic segmentation and dynamic-static separation mapping process during ADD-SLAM execution on Scene ps\_track of the Bonn dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x7.png)

Figure 7: Visualizations of the adaptive dynamic segmentation and dynamic-static separation mapping process during ADD-SLAM execution on Scene balloon of the Bonn dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x8.png)

Figure 8: Visualizations of the adaptive dynamic segmentation and dynamic-static composition mapping process during ADD-SLAM execution on Scene ps\_track (start at the 90th frame of the original sequence) of the Bonn dataset.

It should be noted that our method does not enforce the first frame scene to be completely static. We initialize the first frame as a static map, and the single-frame map initialization can be completed regardless of whether there are moving objects. When object movements in subsequent frames disrupt scene consistency, our method can identify moving regions and separate dynamic objects from the original map. We supplement experiments with person tracking sequences starting from the 90th frame. As shown in Fig. 8, our method remains effective when a person is in motion from the first frame. Actually, in most scenarios of our experiments, the objects have already started moving at the beginning of the sequence.

Multiple dynamic objects overlap and large movement of dynamic objects. For multiple dynamic objects that overlap, we supplement experiments on the Scenario crowd of the Bonn Dataset, containing multiple moving people, as shown in Fig. 9. For large movements of dynamic objects, we provide visualizations from the Scenario balloon, where balloon motion blur indicates high-speed movement, as shown in Fig. 10. In addition, Fig. 16 to Fig. 23 show the extensive experiments of our method on the DAVIS dataset, validating the effectiveness under challenging conditions.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x9.png)

Figure 9: Visualization of dynamic mask and rendering results in Scenario crowd of the Bonn Dataset, featuring overlapping moving pedestrians.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x10.png)

Figure 10: Visualization of dynamic mask and rendering results in the Scenario balloon of the Bonn Dataset, featuring a high-speed balloon exhibiting motion blur.

Sensitivity analysis of geometric and color inconsistency thresholds. For geometric and color inconsistency thresholds, we statistically analyze the rendered geometric and color error distributions, as shown in Fig. 11 and Fig. 12. The red dashed lines indicate error medians, while the yellow shaded areas represent the range from 10× to 30× the error median. The observed long-tailed error distribution reveals two distinct characteristics: minimal errors in static regions (distribution head) and significantly larger errors in dynamic regions (distribution tail). Selecting 20× the median as the operational threshold effectively distinguishes genuine motion areas. Notably, the error threshold maintains a wide acceptable range (10×-30×, even wider), ensuring robust applicability in practice. Fig. 13 presents a sensitivity analysis of the threshold selection, demonstrating that while the inconsistent mask area slightly decreases from 10× to 30× median thresholds. The dynamic mask segmentation results remain unaffected, with true motion regions consistently identifiable. This analysis demonstrates the effectiveness and robustness of our threshold Settings.

![Refer to caption](https://arxiv.org/html/2505.19420v1/extracted/6477724/sec/sup_figure/rgb.png)

Figure 11: RGB error distribution analysis. The yellow part is between 10 and 30 times the median.

![Refer to caption](https://arxiv.org/html/2505.19420v1/extracted/6477724/sec/sup_figure/depth.png)

Figure 12: Depth error distribution analysis. The yellow part is between 10 and 30 times the error median.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x11.png)

Figure 13: Inconsistent regions M i ⁢ c d subscript superscript 𝑀 𝑑 𝑖 𝑐 M^{d}\_{ic} italic\_M start\_POSTSUPERSCRIPT italic\_d end\_POSTSUPERSCRIPT start\_POSTSUBSCRIPT italic\_i italic\_c end\_POSTSUBSCRIPT and dynamic masks M\_{d} italic\_M start\_POSTSUBSCRIPT italic\_d end\_POSTSUBSCRIPT under different multiples of the error median. From left to right: 10×, 15×, 20×, 25×, and 30× the error median.

Comparison with the dynamic mask of DG-SLAM [^7]. DG-SLAM [^7] uses semantic segmentation prior and multi-view depth warp mask to compensate for missing objects. Even if the prior objects are static, they will be divided. Although the multi-view depth warp mask compensates for missing objects, the occlusion caused by the view change is also contained in the mask and cannot be distinguished, as shown in Fig. 14.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x12.png)

Figure 14: Comparison of dynamic segmentation masks between our method and DG-SLAM. The red-circled area represents the noise artifacts in the warp mask.

Supplementary results on the Davis dataset. We supplement experiments on multiple scenarios from the DAVIS dataset. Fig. 16 to Fig. 23 demonstrate our method’s performance across diverse complex scenarios, validating its robustness. The uncertainty learning in WildGS-SLAM [^9] fails to effectively distinguish scene dynamics in low-motion scenarios, such as the camel shown in Fig. 16. Moreover, its uncertainty estimation is susceptible to background interference, preventing accurate localization of dynamic object regions. In contrast, our scene-consistency-based adaptive dynamic segmentation method achieves precise dynamic object masks. Furthermore, while WildGS-SLAM [^9] only models static backgrounds while ignoring dynamic foregrounds, our method simultaneously models scene dynamics and preserves richer scene information.

Limitation. While our method enables adaptive discovery of dynamic regions within scenes, the integrity of dynamic object segmentation is contingent upon mobileSAM [^13]. In complex environments, partial segmentation or over-segmentation may degrade system performance, as exemplified in Fig. 15(a) and (b). Furthermore, scene inconsistencies arising from imprecise depth estimation can induce erroneous dynamic object detection, such as the wrong detection of the sky in the upper-left corner of Fig. 15 (c).

![Refer to caption](https://arxiv.org/html/2505.19420v1/x13.png)

Figure 15: Failure cases. The green points in the RGB image serve as prompts from inconsistency detection. From left to right, three failure cases on the DAVIS dataset are demonstrated: (a) partial segmentation, (b) over-segmentation, and (c) wrong detection caused by inaccurate depth estimation.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x14.png)

Figure 16: Visualization of dynamic mask and rendering results in the Scenario camel of the DAVIS Dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x15.png)

Figure 17: Visualization of dynamic mask and rendering results in the Scenario tennis of the DAVIS Dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x16.png)

Figure 18: Visualization of dynamic mask and rendering results in the Scenario rollerblade of the DAVIS Dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x17.png)

Figure 19: Visualization of dynamic mask and rendering results in the Scenario parkour of the DAVIS Dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x18.png)

Figure 20: Visualization of dynamic mask and rendering results in the Scenario motocross-bumps of the DAVIS Dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x19.png)

Figure 21: Visualization of dynamic mask and rendering results in the Scenario soccerball of the DAVIS Dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x20.png)

Figure 22: Visualization of dynamic mask and rendering results in the Scenario car-turn of the DAVIS Dataset.

![Refer to caption](https://arxiv.org/html/2505.19420v1/x21.png)

Figure 23: Visualization of dynamic mask and rendering results in the Scenario crossing of the DAVIS Dataset.

[^1]: Yanan Wang, Yaobin Tian, Jiawei Chen, Kun Xu, and Xilun Ding. A survey of visual slam in dynamic environment: the evolution from geometric to semantic approaches. IEEE Transactions on Instrumentation and Measurement, 2024.

[^2]: Basheer Al-Tawil, Thorsten Hempel, Ahmed Abdelrahman, and Ayoub Al-Hamadi. A review of visual slam for robotics: evolution, properties, and future applications. Frontiers in Robotics and AI, 11:1347985, 2024.

[^3]: Nicolas Schischka, Hannah Schieber, Mert Asim Karaoglu, Melih Gorgulu, Florian Grötzner, Alexander Ladikos, Nassir Navab, Daniel Roth, and Benjamin Busam. Dynamon: Motion-aware fast and robust camera localization for dynamic neural radiance fields. IEEE Robotics and Automation Letters, 2024.

[^4]: Ziheng Xu, Jianwei Niu, Qingfeng Li, Tao Ren, and Chen Chen. Nid-slam: Neural implicit representation-based rgb-d slam in dynamic environments. arXiv preprint arXiv:2401.01189, 2024.

[^5]: Chenyu Ruan, Qiuyu Zang, Kehua Zhang, and Kai Huang. Dn-slam: A visual slam with orb features and nerf mapping in dynamic environments. IEEE Sensors Journal, 2023.

[^6]: Haoang Li, Xiangqi Meng, Xingxing Zuo, Zhe Liu, Hesheng Wang, and Daniel Cremers. Pg-slam: Photo-realistic and geometry-aware rgb-d slam in dynamic environments. arXiv preprint arXiv:2411.15800, 2024.

[^7]: Yueming Xu, Haochen Jiang, Zhongyang Xiao, Jianfeng Feng, and Li Zhang. Dg-slam: Robust dynamic gaussian splatting slam with hybrid pose optimization. arXiv preprint arXiv:2411.08373, 2024.

[^8]: Long Wen, Shixin Li, Yu Zhang, Yuhong Huang, Jianjie Lin, Fengjunjie Pan, Zhenshan Bing, and Alois Knoll. Gassidy: Gaussian splatting slam in dynamic environments. arXiv preprint arXiv:2411.15476, 2024.

[^9]: Jianhao Zheng, Zihan Zhu, Valentin Bieri, Marc Pollefeys, Songyou Peng, and Iro Armeni. Wildgs-slam: Monocular gaussian splatting slam in dynamic environments. arXiv preprint arXiv:2504.03886, 2025.

[^10]: Jonathon Luiten, Georgios Kopanas, Bastian Leibe, and Deva Ramanan. Dynamic 3d gaussians: Tracking by persistent dynamic view synthesis. In 2024 International Conference on 3D Vision (3DV), pages 800–809. IEEE, 2024.

[^11]: Guanjun Wu, Taoran Yi, Jiemin Fang, Lingxi Xie, Xiaopeng Zhang, Wei Wei, Wenyu Liu, Qi Tian, and Xinggang Wang. 4d gaussian splatting for real-time dynamic scene rendering. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 20310–20320, 2024.

[^12]: Zeyu Yang, Hongye Yang, Zijie Pan, and Li Zhang. Real-time photorealistic dynamic scene representation and rendering with 4d gaussian splatting. In The Twelfth International Conference on Learning Representations.

[^13]: Chaoning Zhang, Dongshen Han, Yu Qiao, Jung Uk Kim, Sung-Ho Bae, Seungkyu Lee, and Choong Seon Hong. Faster segment anything: Towards lightweight sam for mobile applications. arXiv preprint arXiv:2306.14289, 2023.

[^14]: Richard A Newcombe, Steven J Lovegrove, and Andrew J Davison. Dtam: Dense tracking and mapping in real-time. In 2011 international conference on computer vision, pages 2320–2327. IEEE, 2011.

[^15]: Richard A Newcombe, Shahram Izadi, Otmar Hilliges, David Molyneaux, David Kim, Andrew J Davison, Pushmeet Kohi, Jamie Shotton, Steve Hodges, and Andrew Fitzgibbon. Kinectfusion: Real-time dense surface mapping and tracking. In 2011 10th IEEE international symposium on mixed and augmented reality, pages 127–136. Ieee, 2011.

[^16]: Paul J Besl and Neil D McKay. Method for registration of 3-d shapes. In Sensor fusion IV: control paradigms and data structures, volume 1611, pages 586–606. Spie, 1992.

[^17]: Thomas Whelan, Stefan Leutenegger, Renato Salas-Moreno, Ben Glocker, and Andrew Davison. Elasticfusion: Dense slam without a pose graph. Robotics: Science and Systems, 2015.

[^18]: Thomas Schöps, Torsten Sattler, and Marc Pollefeys. Surfelmeshing: Online surfel-based mesh reconstruction. IEEE transactions on pattern analysis and machine intelligence, 42(10):2494–2507, 2019.

[^19]: Emanuele Vespa, Nikolay Nikolov, Marius Grimm, Luigi Nardi, Paul HJ Kelly, and Stefan Leutenegger. Efficient octree-based volumetric slam supporting signed-distance and occupancy mapping. IEEE Robotics and Automation Letters, 3(2):1144–1151, 2018.

[^20]: Binbin Xu, Wenbin Li, Dimos Tzoumanikas, Michael Bloesch, Andrew Davison, and Stefan Leutenegger. Mid-fusion: Octree-based object-level multi-instance dynamic slam. In 2019 International Conference on Robotics and Automation (ICRA), pages 5231–5237. IEEE, 2019.

[^21]: Thomas Schops, Torsten Sattler, and Marc Pollefeys. Bad slam: Bundle adjusted direct rgb-d slam. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 134–144, 2019.

[^22]: Michael Bloesch, Jan Czarnowski, Ronald Clark, Stefan Leutenegger, and Andrew J Davison. Codeslam—learning a compact, optimisable representation for dense visual slam. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 2560–2568, 2018.

[^23]: Ruihao Li, Sen Wang, and Dongbing Gu. Deepslam: A robust monocular slam system with unsupervised deep learning. IEEE Transactions on Industrial Electronics, 68(4):3577–3587, 2020.

[^24]: Lukas Koestler, Nan Yang, Niclas Zeller, and Daniel Cremers. Tandem: Tracking and dense mapping in real-time using deep multi-view stereo. In Conference on Robot Learning, pages 34–45. PMLR, 2022.

[^25]: Songyou Peng, Michael Niemeyer, Lars Mescheder, Marc Pollefeys, and Andreas Geiger. Convolutional occupancy networks. In Computer Vision–ECCV 2020: 16th European Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part III 16, pages 523–540. Springer, 2020.

[^26]: Zachary Teed and Jia Deng. Droid-slam: Deep visual slam for monocular, stereo, and rgb-d cameras. Advances in neural information processing systems, 34:16558–16569, 2021.

[^27]: Ben Mildenhall, Pratul P Srinivasan, Matthew Tancik, Jonathan T Barron, Ravi Ramamoorthi, and Ren Ng. Nerf: Representing scenes as neural radiance fields for view synthesis. Communications of the ACM, 65(1):99–106, 2021.

[^28]: Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, and George Drettakis. 3d gaussian splatting for real-time radiance field rendering. ACM Trans. Graph., 42(4):139–1, 2023.

[^29]: Edgar Sucar, Shikun Liu, Joseph Ortiz, and Andrew J Davison. imap: Implicit mapping and positioning in real-time. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 6229–6238, 2021.

[^30]: Zihan Zhu, Songyou Peng, Viktor Larsson, Weiwei Xu, Hujun Bao, Zhaopeng Cui, Martin R Oswald, and Marc Pollefeys. Nice-slam: Neural implicit scalable encoding for slam. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 12786–12796, 2022.

[^31]: Hengyi Wang, Jingwen Wang, and Lourdes Agapito. Co-slam: Joint coordinate and sparse parametric encodings for neural real-time slam. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 13293–13302, 2023.

[^32]: Mohammad Mahdi Johari, Camilla Carta, and François Fleuret. Eslam: Efficient dense slam system based on hybrid representation of signed distance fields. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 17408–17419, 2023.

[^33]: Xingrui Yang, Hai Li, Hongjia Zhai, Yuhang Ming, Yuqian Liu, and Guofeng Zhang. Vox-fusion: Dense tracking and mapping with voxel-based neural implicit representation. In 2022 IEEE International Symposium on Mixed and Augmented Reality (ISMAR), pages 499–507. IEEE, 2022.

[^34]: Youmin Zhang, Fabio Tosi, Stefano Mattoccia, and Matteo Poggi. Go-slam: Global optimization for consistent 3d instant reconstruction. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), pages 3727–3737, October 2023.

[^35]: Xinyang Liu, Yijin Li, Yanbin Teng, Hujun Bao, Guofeng Zhang, Yinda Zhang, and Zhaopeng Cui. Multi-modal neural radiance field for monocular dense slam with a light-weight tof sensor. In Proceedings of the ieee/cvf international conference on computer vision, pages 1–11, 2023.

[^36]: Mingrui Li, Jiaming He, Yangyang Wang, and Hongyu Wang. End-to-end rgb-d slam with multi-mlps dense neural implicit representations. IEEE Robotics and Automation Letters, 2023.

[^37]: Yuhang Ming, Weicai Ye, and Andrew Calway. idf-slam: End-to-end rgb-d slam with neural implicit mapping and deep feature tracking. arXiv preprint arXiv:2209.07919, 2022.

[^38]: Haocheng Wang, Yanlong Cao, Xiaoyao Wei, Yejun Shou, Lingfeng Shen, Zhijie Xu, and Kai Ren. Structerf-slam: Neural implicit representation slam for structural environments. Computers & Graphics, 119:103893, 2024.

[^39]: Wenhua Wu, Guangming Wang, Ting Deng, Sebastian Aegidius, Stuart Shanks, Valerio Modugno, Dimitrios Kanoulas, and Hesheng Wang. Dvn-slam: dynamic visual neural slam based on local-global encoding. arXiv preprint arXiv:2403.11776, 2024.

[^40]: Tianchen Deng, Guole Shen, Tong Qin, Jianyu Wang, Wentao Zhao, Jingchuan Wang, Danwei Wang, and Weidong Chen. Plgslam: Progressive neural scene represenation with local to global bundle adjustment. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 19657–19666, 2024.

[^41]: Chi Yan, Delin Qu, Dan Xu, Bin Zhao, Zhigang Wang, Dong Wang, and Xuelong Li. Gs-slam: Dense visual slam with 3d gaussian splatting. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 19595–19604, 2024.

[^42]: Huajian Huang, Longwei Li, Hui Cheng, and Sai-Kit Yeung. Photo-slam: Real-time simultaneous localization and photorealistic mapping for monocular stereo and rgb-d cameras. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 21584–21593, 2024.

[^43]: Vladimir Yugay, Yue Li, Theo Gevers, and Martin R Oswald. Gaussian-slam: Photo-realistic dense slam with gaussian splatting. arXiv preprint arXiv:2312.10070, 2023.

[^44]: Nikhil Keetha, Jay Karhade, Krishna Murthy Jatavallabhula, Gengshan Yang, Sebastian Scherer, Deva Ramanan, and Jonathon Luiten. Splatam: Splat track & map 3d gaussians for dense rgb-d slam. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 21357–21366, 2024.

[^45]: Hidenobu Matsuki, Riku Murai, Paul H. J. Kelly, and Andrew J. Davison. Gaussian Splatting SLAM. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024.

[^46]: Mingrui Li, Jiaming He, Guangan Jiang, and Hongyu Wang. Ddn-slam: Real-time dense dynamic neural implicit slam with joint semantic encoding. arXiv preprint arXiv:2401.01545, 2024.

[^47]: Haochen Jiang, Yueming Xu, Kejie Li, Jianfeng Feng, and Li Zhang. Rodyn-slam: Robust dynamic dense rgb-d slam with neural radiance fields. IEEE Robotics and Automation Letters, 2024.

[^48]: Liyuan Zhu, Yue Li, Erik Sandström, Shengyu Huang, Konrad Schindler, and Iro Armeni. Loopsplat: Loop closure by registering 3d gaussian splats. arXiv preprint arXiv:2408.10154, 2024.

[^49]: Carlos Campos, Richard Elvira, Juan J Gómez Rodríguez, José MM Montiel, and Juan D Tardós. Orb-slam3: An accurate open-source library for visual, visual–inertial, and multimap slam. IEEE Transactions on Robotics, 37(6):1874–1890, 2021.

[^50]: Berta Bescos, José M Fácil, Javier Civera, and José Neira. Dynaslam: Tracking, mapping, and inpainting in dynamic scenes. IEEE Robotics and Automation Letters, 3(4):4076–4083, 2018.

[^51]: Emanuele Palazzolo, Jens Behley, Philipp Lottes, Philippe Giguere, and Cyrill Stachniss. Refusion: 3d reconstruction in dynamic environments for rgb-d cameras exploiting residuals. In 2019 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pages 7855–7862. IEEE, 2019.

[^52]: Seongbo Ha, Jiung Yeon, and Hyeonwoo Yu. Rgbd gs-icp slam. In European Conference on Computer Vision, pages 180–197. Springer, 2025.

[^53]: Christian Kerl, Jürgen Sturm, and Daniel Cremers. Dense visual slam for rgb-d cameras. In 2013 IEEE/RSJ International Conference on Intelligent Robots and Systems, pages 2100–2106. IEEE, 2013.

[^54]: Jürgen Sturm, Nikolas Engelhard, Felix Endres, Wolfram Burgard, and Daniel Cremers. A benchmark for the evaluation of rgb-d slam systems. In 2012 IEEE/RSJ international conference on intelligent robots and systems, pages 573–580. IEEE, 2012.

[^55]: E. Palazzolo, J. Behley, P. Lottes, P. Giguère, and C. Stachniss. ReFusion: 3D Reconstruction in Dynamic Environments for RGB-D Cameras Exploiting Residuals. 2019.

[^56]: Federico Perazzi, Jordi Pont-Tuset, Brian McWilliams, Luc Van Gool, Markus Gross, and Alexander Sorkine-Hornung. A benchmark dataset and evaluation methodology for video object segmentation. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 724–732, 2016.

[^57]: Feng Li, Hao Zhang, Huaizhe xu, Shilong Liu, Lei Zhang, Lionel M. Ni, and Heung-Yeung Shum. Mask dino: Towards a unified transformer-based framework for object detection and segmentation, 2022.

[^58]: Lihe Yang, Bingyi Kang, Zilong Huang, Zhen Zhao, Xiaogang Xu, Jiashi Feng, and Hengshuang Zhao. Depth anything v2. arXiv:2406.09414, 2024.