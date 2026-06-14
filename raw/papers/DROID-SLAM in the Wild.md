---
title: "DROID-SLAM in the Wild"
source: "https://arxiv.org/html/2603.19076v1"
author:
published:
created: 2026-06-14
description:
tags:
  - "clippings"
---
Moyang Li <sup>1</sup> <sup>1</sup>   Zihan Zhu <sup>1</sup> <sup>1</sup>   Marc Pollefeys <sup>1,2</sup>   Daniel Barath <sup>1</sup>  
<sup>1</sup> ETH Zurich   <sup>2</sup> Microsoft

###### Abstract

We present a robust, real-time RGB SLAM system that handles dynamic environments by leveraging differentiable Uncertainty-aware Bundle Adjustment. Traditional SLAM methods typically assume static scenes, leading to tracking failures in the presence of motion. Recent dynamic SLAM approaches attempt to address this challenge using predefined dynamic priors or uncertainty-aware mapping, but they remain limited when confronted with unknown dynamic objects or highly cluttered scenes where geometric mapping becomes unreliable. In contrast, our method estimates per-pixel uncertainty by exploiting multi-view visual feature inconsistency, enabling robust tracking and reconstruction even in real-world environments. The proposed system achieves state-of-the-art camera poses and scene geometry in cluttered dynamic scenarios while running in real time at around 10 FPS. Code and datasets are available at [https://github.com/MoyangLi00/DROID-W.git](https://github.com/MoyangLi00/DROID-W.git).

![[Uncaptioned image]](https://arxiv.org/html/2603.19076v1/x1.png)

Figure 1: DROID-W. Given a casually captured in-the-wild video, our method estimates accurate dynamic uncertainty, camera trajectory, and scene structure, where existing SLAM baselines fail. Left: frames of the input video. Middle: reconstructed dynamic point clouds with estimated camera poses. Right: overlay of optimized uncertainty on the corresponding input frames.

## 1 Introduction

Simultaneous Localization and Mapping (SLAM) is a fundamental task in computer vision, with broad applications in autonomous driving [^3] [^12], robotics [^31] [^1] [^69], and embodied intelligence [^15] [^5] [^24]. Despite remarkable progress, achieving reliable SLAM in real-world environments is challenging. Dynamic and non-rigid objects often compromise pose estimation and 3D reconstruction, limiting the robustness and applicability of SLAM systems in practice.

Although this task has been extensively studied, many existing methods [^36] [^34] [^9] [^35] [^48] [^49] still assume a static environment and ignore non-rigid motion, which results in errors in both camera tracking and scene reconstruction. Some recent works [^4] [^44] [^57] [^18] [^55] attempt to handle dynamic scenes by detecting or segmenting moving objects and masking out those regions. However, they rely heavily on prior knowledge of dynamic objects, which limits their robustness in complex and diverse real-world environments.

Recently, uncertainty-aware methods [^39] [^25] [^66] [^67] have attracted increasing attention for handling scene dynamics without relying on predefined motion priors. These approaches typically employ a shallow multi-layer perceptron (MLP) to estimate pixel-wise uncertainty from DINO [^37] features and optimize the predictor through an online update. However, these approaches rely on constructing a perfectly static neural implicit [^33] or Gaussian Splatting [^21] map to optimize uncertainty. Consequently, their performance remains limited in complex real-world environments, where dynamic and cluttered scenes pose significant challenges for stable scene representation.

To address these limitations, we propose DROID-W, a novel dynamics-aware SLAM system that adapts prior deep visual SLAM system DROID-SLAM [^48] to dynamic environments. We incorporate uncertainty optimization into the differentiable bundle adjustment (BA) layer to iteratively update dynamic uncertainty, camera poses, and scene geometry. The pixel-wise uncertainty of the frame is updated by leveraging multi-view visual feature similarity. In contrast with prior approaches, our uncertainty estimation is not constrained by high-quality geometric mapping or predefined motion priors. In addition, we introduce the DROID-W dataset, capturing diverse and unconstrained outdoor dynamic scenes, and further include YouTube clips for truly in-the-wild evaluation. In contrast to the saturated indoor benchmarks prevalent in prior works, our sequences feature challenging real-world settings with various object dynamics. Experimental results demonstrate that our approach achieves robust uncertainty estimation in real-world environments, leading to state-of-the-art camera tracking accuracy and scene geometry reconstruction while running in real time at approximately 10 FPS.

## 2 Related Works

#### Traditional Visual SLAM

Many existing traditional visual SLAM methods [^10] [^34] [^9] [^35] [^48] [^49] assume a static environment, which often leads to feature mismatching and degrades both tracking accuracy and mapping quality. To mitigate the disruption caused by object motion, some prior works [^22] [^23] implicitly handle dynamic elements through penalizing large frame-to-frame residuals during optimization. Other methods [^45] [^38] identify dynamic areas based on frame-to-model alignment residuals. StaticFusion [^45] employs keypoint clustering and frame-to-model alignment to detect regions with large residuals, introducing a penalization term to constrain the map to static regions. ReFusion [^38] adopts a TSDF [^8] representation and removes uncertain regions with large depth residuals to maintain a consistent background map.

A complementary line of approaches [^40] [^4] [^60] [^68] [^41] exploits object detection and segmentation to explicitly filter out dynamic regions. DynaSLAM [^4] and DS-SLAM [^60], both built upon ORB-SLAM2 [^35], employ segmentation networks [^14] [^2] to detect moving objects and reconstruct a static background. Detect-SLAM [^68] integrates the SSD detector [^30] and propagates the moving probability of keypoints to reduce latency caused by object detection. Co-Fusion [^40] and MaskFusion [^41] extend to the object level, jointly segmenting, tracking, and reconstructing multiple independently moving objects. FlowFusion [^63] instead leverages optical flow residuals to highlight dynamic regions.

#### NeRF- and GS-based SLAM

Recent advances in Neural Radiance Fields (NeRF) [^33] have garnered substantial attention for their integration into SLAM systems, owing to their dense representation and photorealistic rendering capabilities. The pioneering work iMAP [^47] introduces the first neural implicit SLAM framework, achieving high-quality dense mapping. However, iMAP [^47] suffers from the loss of fine details and catastrophic forgetting, as it represents the entire scene in a single MLP. To overcome these limitations, NICE-SLAM [^71] incorporates hierarchical feature grids to enhance scalability and reconstruction fidelity. Subsequent methods [^59] [^19] [^51] [^42] [^64] [^70] further improve the efficiency and robustness of such SLAM systems. More recently, the emergence of 3D Gaussian Splatting (3DGS) [^21] inspired numerous SLAM approaches [^20] [^43] [^32] [^58] [^16] [^13] that adopt Gaussian primitives. However, these methods typically assume predominantly static environments, which limits their applicability in real-world scenarios with dynamic objects.

![Refer to caption](https://arxiv.org/html/2603.19076v1/x2.png)

Figure 2: System Overview. The proposed DROID-W takes a sequence of RGB images as inputs and simultaneously estimates camera poses while recovering scene geometry. It alternatingly performs pose-depth refinement and uncertainty optimization in an iterative manner. The proposed uncertainty-aware dense bundle adjustment weights reprojection residuals with per-pixel uncertainty 𝐮 \\mathbf{u} to mitigate the influence of dynamic distractors. In addition, we use predicted monocular depth 𝐃 {\\mathbf{D}} as regularization of bundle adjustment, to improve its robustness under highly dynamic environments. For the uncertainty optimization module, we first extract DINOv2 37 features from the input images and then iteratively update the dynamic uncertainty map by leveraging multi-view feature consistency. Specifically, feature consistency is measured by the cosine similarity between features of image 𝐈 i \\mathbf{I}\_{i} and its corresponding features in image j \\mathbf{I}\_{j}, where the rigid-motion correspondences 𝐩 \\mathbf{p}\_{ij} are derived using the current pose and depth estimates.

To overcome this limitation, several dynamic NeRF-based [^44] [^26] [^18] [^56] and GS-based SLAM systems [^57] [^67] [^55] [^66] [^29] [^27] have been proposed. Most of them [^26] [^29] [^27] [^55] rely on object detection or semantic segmentation to mask out dynamic regions, but struggle to handle undefined or unseen object classes. To address this, DynaMoN [^44] introduces an additional CNN to predict motion masks from forward optical flow, while RoDyn-SLAM [^18] and DG-SLAM [^57] combine semantic segmentation with warping masks to improve motion mask estimation. WildGS-SLAM [^66] and UP-SLAM [^67] employ uncertainty modeling to handle scene dynamics. They utilize a shallow MLP to estimate per-pixel motion uncertainty from DINOv2 [^37] features, as these features are robust to appearance variations and can represent abundant semantic information. The uncertainty MLP is optimized under the supervision of photometric and depth losses between input and rendered images. Furthermore, UP-SLAM [^67] extends high-dimensional visual features into the 3DGS feature space and introduces a similarity loss as additional uncertainty constraints.

However, the optimization of uncertainty in these methods remains tightly coupled with scene representation, leading to performance degradation in complex environments where mapping struggles. In contrast, our approach adopts visual feature similarity between frames to estimate dynamic uncertainty, demonstrating robustness and effectiveness in challenging real-world environments.

#### Feed-forward Approaches

Recent feed-forward reconstruction and pose estimation methods have achieved remarkable progress. DUSt3R [^54] and VGGT [^52] demonstrate strong performance in scene geometry estimation. MonST3R [^62] extends DUSt3R [^54] to dynamic environments by estimating the dynamic mask from optical flow and pointmaps. Easi3R [^6] introduces a training-free 4D reconstruction framework that isolates motion information from the attention maps of DUSt3R [^54]. However, these methods are restricted to short sequences. CUT3R [^53] and TTT3R [^7] further advance feed-forward reconstruction by handling long sequences in an online continuous manner. Despite these approaches achieving visually convincing geometry estimation, purely feed-forward pipelines often struggle to recover accurate camera trajectories and metrically consistent structure compared to SLAM-style systems. In contrast, our method, grounded in a visual SLAM framework, yields more accurate camera trajectories and reconstructions.

## 3 Proposed Method

Our approach adapts prior deep visual SLAM DROID-SLAM [^48] by introducing a differentiable Uncertainty-aware Bundle Adjustment (UBA) that explicitly models per-pixel uncertainty to handle dynamic objects. Given RGB sequences from cluttered real-world scenes, our system optimizes camera poses, depth, and uncertainty to achieve robust tracking and accurate geometry estimation.

Next, we will first summarize the key components of DROID-SLAM designed for static environments (Sec. 3.1). We then present our proposed differentiable Uncertainty-aware Bundle Adjustment (Sec. 3.2) and dynamic uncertainty update (Sec. 3.3) modules. Finally, we introduce the proposed overall dynamic SLAM system (Sec. 3.4). The overview of DROID-W is shown in Fig. 2.

### 3.1 Preliminaries

DROID-SLAM leverages a differentiable bundle adjustment (BA) layer to update camera poses and depths in an iterative manner. For each RGB image in the input sequence $\{\mathbf{I}_{t}\}_{t=0}^{N}$, it maintains two state variables: camera pose $\mathbf{G}_{t}\in SE(3)$, inverse depth $\mathbf{d}_{t}\in\mathcal{R}^{\frac{H}{8}\times\frac{W}{8}}$. In addition, it constructs the frame-graph $(\mathcal{V},\mathcal{E})$ to represent co-visibility across frames, where an edge $(i,j)\in\mathcal{E}$ means that the images $\mathbf{I}_{i}$ and $\mathbf{I}_{j}$ overlap. The set of camera poses $\{\mathbf{G}_{t}\}_{t=0}^{N}$ and inverse depths $\{\mathbf{d}_{t}\}_{t=0}^{N}$ are iteratively updated through the differentiable BA layer, operating on a set of image pairs $(\mathbf{I}_{i},\mathbf{I}_{j})$.

#### Differential Bundle Adjustment

For each pair of images $(\mathbf{I}_{i},\mathbf{I}_{j})$, we can derive the rigid-motion correspondence as:

$$
\footnotesize\mathbf{p}_{ij}=\Pi_{c}\Big(\mathbf{G}_{ij}^{\prime}\circ\Pi_{c}^{-1}(\mathbf{p}_{i},\mathbf{d}_{i}^{\prime})\Big),
$$

where $\Pi_{c}$ denotes the camera projection function, and $\mathbf{G}^{\prime}_{ij}$ is the relative pose between frames $i$ and $j$. Variable $\mathbf{p}_{i}\in\mathcal{R}^{\frac{H}{8}\times\frac{W}{8}\times 2}$ represents a grid of pixel coordinates in frame $i$. DROID-SLAM predicts the 2D dense correspondence $\mathbf{p}_{ij}^{*}\in\mathcal{R}^{\frac{H}{8}\times\frac{W}{8}\times 2}$ and confidence map $\mathbf{w}_{ij}\in\mathcal{R}^{\frac{H}{8}\times\frac{W}{8}\times 2}$ in an iterative manner. The differentiable BA jointly refines camera poses and inverse depths by minimizing dense correspondence residuals as follows:

$$
\displaystyle\mathbf{E}(\mathbf{G}^{\prime},\mathbf{d}^{\prime})
$$
 
$$
\displaystyle=\sum_{(i,j)\in\mathcal{E}}\left\|\mathbf{p}_{ij}^{*}-\mathbf{p}_{ij}\right\|_{\boldsymbol{\Sigma}_{ij}}^{2},
$$
$$
\displaystyle\boldsymbol{\Sigma}_{ij}
$$
 
$$
\displaystyle=\mathrm{diag}\,(\mathbf{w}_{ij}).
$$

where $\|\cdot\|_{\Sigma}$ denotes Mahalanobis distance that weights the residuals according to the confidence map predicted by DROID-SLAM. The pose and disparity are optimized using the Gauss-Newton algorithm as follows:

$$
\footnotesize\begin{bmatrix}\mathbf{B}&\mathbf{E}\\
\mathbf{E}^{\mathsf{T}}&\mathbf{C}\end{bmatrix}\begin{bmatrix}\Delta\boldsymbol{\xi}\\
\Delta\mathbf{d}\end{bmatrix}=\begin{bmatrix}\mathbf{v}\\
\mathbf{w}\end{bmatrix},
$$
 
$$
\displaystyle\Delta\boldsymbol{\xi}
$$
 
$$
\displaystyle=[\mathbf{B}-\mathbf{E}\mathbf{C}^{-1}\mathbf{E}^{\mathsf{T}}]^{-1}(\mathbf{v}-\mathbf{E}\mathbf{C}^{-1}\mathbf{w}),
$$
$$
\displaystyle\Delta\mathbf{d}
$$
 
$$
\displaystyle=\mathbf{C}^{-1}(\mathbf{w}-\mathbf{E}^{\mathsf{T}}\Delta\boldsymbol{\xi}).
$$

where $(\boldsymbol{\Delta\xi},\mathbf{\Delta d})$ represents pose and disparity update. Matrix $\mathbf{C}$ is diagonal as each term in Eq. (3.1) depends only on a single depth value, thus it can be inverted by $\mathbf{C}^{-1}=1/\mathbf{C}$.

### 3.2 Uncertainty-aware Bundle Adjustment

Dynamic objects violate the rigid-motion assumption, yielding unreliable residuals that destabilize the BA layer of DROID-SLAM. To address this, we introduce a per-pixel dynamic uncertainty $\mathbf{u}_{t}\in\mathcal{R}^{\frac{H}{8}\times\frac{W}{8}}$ that downweights inconsistent correspondences during optimization. Intuitively, $\mathbf{u}_{t}$ acts as a confidence term penalizing high residuals caused by dynamic objects. Thus, we define uncertainty-aware Mahalanobis distance term $\|\cdot\|_{\Sigma_{ij}^{\text{uncer}}}$ as follows:

$$
\footnotesize\boldsymbol{\Sigma}_{ij}^{\text{uncer}}=\mathrm{diag}\,(\mathbf{w}_{ij}\cdot\frac{1}{\mathbf{{u}}^{\prime}_{i}}).
$$

However, jointly optimizing pose, depth, and uncertainty via Gauss-Newton algorithms is computationally prohibitive. We thus adopt an interleaved optimization strategy that alternates between pose-depth refinement and uncertainty optimization. The pose-depth refinement is performed by minimizing the following uncertainty-aware energy function:

$$
\footnotesize\hat{\mathbf{E}}(\mathbf{G}^{\prime},\mathbf{d}^{\prime})=\sum_{(i,j)\in\mathcal{E}}\left\|\mathbf{p}_{ij}^{*}-\mathbf{p}_{ij}\right\|_{\boldsymbol{\Sigma}^{\text{uncer}}_{ij}}^{2}.
$$

### 3.3 Uncertainty Optimization

For the optimization of dynamic uncertainty, we measure multi-view inconsistency via the similarity of DINOv2 [^37] features across image pairs rather than the reprojection residuals in Eq. (5). Reprojection error can become unreliable under large dynamic motion, while 2D visual feature similarity yields a more stable and semantically meaningful measure for multi-view inconsistency.

#### Uncertainty Cost Function

For each pair of images $(\mathbf{I}_{i},\mathbf{I}_{j})$, 2D visual features $(\mathbf{F}_{i},\mathbf{F}_{j})$ are first extracted using FiT3D [^61], a refined DINOv2 model. For each pixel $\mathbf{p}_{i}$ in frame $i$, we compute its rigid-motion correspondence $\mathbf{p}_{ij}$ in frame $j$ via Eq. (1). We then obtain corresponding feature $\mathbf{F}_{ij}$ and uncertainty $\mathbf{u}_{ij}$ through bilinear interpolation. Multi-view consistency of the image pair is measured by cosine similarity between the DINOv2 features $(\mathbf{F}_{i},\mathbf{F}_{ij})$. The dynamic objects in the environment with multi-view inconsistency are expected to have high uncertainty. Thus, we formulate the following similarity loss:

$$
\footnotesize\mathbf{E}_{\text{sim}}(\mathbf{u}{{}^{\prime}})=\sum_{(i,j)\in\mathcal{E}}\frac{1-\frac{\mathbf{F}_{i}\cdot{\mathbf{F}}_{ij}}{{\|\mathbf{F}_{i}\|}_{2}{\|{\mathbf{F}}_{ij}\|}_{2}}}{\mathbf{u}^{\prime}_{i}\cdot{\mathbf{u}}^{\prime}_{ij}}.
$$

Here, we optimize bidirectional uncertainties for each image pair to decouple inter-frame dynamics.

To avoid the trivial solution of $\mathbf{u^{\prime}}\rightarrow+\infty$, we regularize the uncertainty with a logarithmic prior:

$$
\footnotesize\mathbf{E}_{\text{prior}}(\mathbf{u^{\prime}})=\sum_{i}\mathrm{log}(\mathbf{u}^{\prime}_{i}+1.0).
$$

Here, we add a bias term 1.0 to the uncertainty to prevent the prior loss from being negative.

Thus, the total uncertainty cost function is defined as:

$$
\footnotesize\mathbf{E}_{\text{uncer}}(\mathbf{u}^{\prime})=\mathbf{E}_{\text{sim}}(\mathbf{u}^{\prime})+\gamma_{\text{prior}}\mathbf{E}_{\text{prior}}(\mathbf{u}^{\prime}).
$$

#### Uncertainty Regularization

Direct optimization of pixel-wise uncertainty may suffer from spatial inconsistency and overfitting to noise due to various dynamic motion. To address this, we learn a local affine mapping followed by the Softplus activation function from DINOv2 features to uncertainties. Thus, the uncertainty is obtained via $\mathbf{u}=\text{Softplus}(\boldsymbol{\theta}\cdot\mathbf{F})$. This affine mapping plays the role of a regularization term within the small local window, which is different from the decoder in prior works [^66] [^39].

#### Optimization

To avoid the inverse computation of the large Hessian matrix, we optimize uncertainty using Gradient Descent with weight decay instead of the Newton algorithm. All backpropagation operations are implemented in CUDA to ensure efficiency. The learnable parameters $\boldsymbol{\theta}$ of the affine mapping layer are updated as the following Jacobians:

$$
\displaystyle\boldsymbol{g}_{t}
$$
 
$$
\displaystyle=\sum_{i=0}^{N}\frac{\partial\mathbf{E}_{\text{uncer}}}{\partial\mathbf{u}^{\prime}_{i}}\cdot\frac{\partial\mathbf{u}^{\prime}_{i}}{\partial\boldsymbol{\theta}_{t-1}}
$$
 
$$
\displaystyle=\sum_{i=0}^{N}\frac{\partial\mathbf{E}_{\text{uncer}}}{\partial\mathbf{u}^{\prime}_{i}}\cdot\frac{1}{1+\text{exp}(-{\boldsymbol{\theta}_{t-1}\cdot\mathbf{F}_{i}})}\cdot\mathbf{F}_{i},
$$
$$
\displaystyle\boldsymbol{\theta}_{t}
$$
 
$$
\displaystyle=\boldsymbol{\theta}_{t-1}-\lambda\cdot\boldsymbol{g}_{t}-\eta\cdot\boldsymbol{\theta}_{t-1}.
$$

For more details about the gradient derivations, please refer to the supplementary material.

### 3.4 SLAM System

Following DROID-SLAM, we accumulate 12 keyframes with sufficient motion to initialize the SLAM system. DROID-SLAM initializes the disparities as the constant value of 1, which can cause inaccurate tracking in high-dynamic scenes. Thus, we adopt the metric monodepth $\mathbf{D}_{t}\in\mathcal{R}^{\frac{H}{8}\times\frac{W}{8}}$ predicted by Metric3D [^17] to penalize the disparity and improve accuracy. Thus, the cost function of BA with depth regularization is defined as follows:

$$
\footnotesize\mathbf{E}^{+}(\mathbf{G}^{\prime},\mathbf{d}^{\prime})=\sum_{(i,j)\in\mathcal{E}}\left\|\mathbf{p}_{ij}^{*}-\mathbf{p}_{ij}\right\|_{\boldsymbol{\Sigma}^{\text{uncer}}_{ij}}^{2}+\gamma_{d}\sum_{i}\left\|\mathbf{d}_{i}^{\prime}-\mathbf{D}_{i}\right\|^{2}.
$$

After the initialization, we process incoming keyframes in an incremental manner. For newly added keyframes, we follow DROID-SLAM to perform local bundle adjustment in a sliding window and adopt depth regularization. For both initialization and frontend tracking stages, we optimize poses, disparities, and uncertainties. After frontend tracking, we perform global BA over all keyframes to refine camera poses and disparities. We freeze the dynamic-uncertainty parameters during global BA, since the affine transformation is intended to regularize uncertainty locally within the sliding window rather than at global scale.

## 4 Experiments

![Refer to caption](https://arxiv.org/html/2603.19076v1/fig_tex/figures_vis_uncer/dycheck_haru/input_kf_003_ts_00014.png)

Figure 3: Uncertainty Estimation. WildGS-SLAM 66 and our approach estimate dynamic uncertainty, whereas MonST3R 62 predicts a binary motion mask. Our approach produces more accurate and spatially consistent uncertainty estimations across all challenging sequences.

#### Datasets

We evaluate our approach on the Bonn RGB-D Dynamic dataset [^38], TUM RGB-D dataset [^46], and DyCheck [^11] dataset. To further assess performance in unconstrained, outdoor settings, we introduce the DROID-W dataset, captured using a Livox Mid-360 LiDAR rigidly mounted with an RGB camera. The dataset comprises 7 sequences (Downtown 1–7) with RGB frames at a resolution of $1200{\times}1600$, ground-truth camera poses, and synchronized IMU and LiDAR measurements. Since satellite-based localization is unavailable for Downtown 1–2, we use FAST-LIVO2 [^65] trajectories as ground truth, whereas the remaining sequences rely on RTK ground truth.

Additionally, we test on 6 dynamic videos downloaded from YouTube. The sequences span 8 seconds to 30 minutes, featuring diverse object motion and cluttered scenes. Sequences exceeding 5 minutes are partitioned into non-overlapping 5-minute segments due to resource bottlenecks of SLAM on a single GPU. For each video, the camera intrinsics are estimated with MonST3R [^62] using 20 frames.

<table><tbody><tr><td>Method</td><td>Balloon</td><td>Balloon2</td><td>Crowd</td><td>Crowd2</td><td>Person</td><td>Person2</td><td>Moving</td><td>Moving2 </td><td>Avg.</td></tr><tr><td colspan="10">RGB-D</td></tr><tr><td>NICE-SLAM <sup><a href="#fn:71">71</a></sup></td><td>24.4</td><td>20.2</td><td>19.3</td><td>35.8</td><td>24.5</td><td>53.6</td><td>17.7</td><td>8.3 </td><td>22.74</td></tr><tr><td>ReFusion <sup><a href="#fn:38">38</a></sup></td><td>17.5</td><td>25.4</td><td>20.4</td><td>15.5</td><td>28.9</td><td>46.3</td><td>7.1</td><td>17.9 </td><td>22.38</td></tr><tr><td>RoDyn-SLAM <sup><a href="#fn:18">18</a></sup></td><td>7.9</td><td>11.5</td><td>-</td><td>-</td><td>14.5</td><td>13.8</td><td>-</td><td>12.3 </td><td>N/A</td></tr><tr><td>DynaSLAM (N+G) <sup><a href="#fn:4">4</a></sup></td><td>3.0</td><td>2.9</td><td>1.6</td><td>3.1</td><td>6.1</td><td>7.8</td><td>23.2</td><td>3.9 </td><td>6.45</td></tr><tr><td>ORB-SLAM2 <sup><a href="#fn:35">35</a></sup></td><td>6.5</td><td>23.0</td><td>4.9</td><td>9.8</td><td>6.9</td><td>7.9</td><td>3.2</td><td>3.9 </td><td>6.36</td></tr><tr><td>DG-SLAM <sup><a href="#fn:57">57</a></sup></td><td>3.7</td><td>4.1</td><td>-</td><td>-</td><td>4.5</td><td>6.9</td><td>-</td><td>3.5 </td><td>N/A</td></tr><tr><td>DDN-SLAM (RGB-D) <sup><a href="#fn:26">26</a></sup></td><td>1.8</td><td>4.1</td><td>1.8</td><td>2.3</td><td>4.3</td><td>3.8</td><td>2.0</td><td>3.2 </td><td>2.91</td></tr><tr><td>UP-SLAM <sup><a href="#fn:67">67</a></sup></td><td>2.8</td><td>2.7</td><td>-</td><td>-</td><td>4.0</td><td>3.6</td><td>-</td><td>3.2 </td><td>N/A</td></tr><tr><td>ADD-SLAM <sup><a href="#fn:55">55</a></sup></td><td>2.7</td><td>2.3</td><td>-</td><td>-</td><td>2.4</td><td>3.7</td><td>-</td><td>2.1 </td><td>N/A</td></tr><tr><td colspan="10">RGB-only</td></tr><tr><td>Splat-SLAM <sup><a href="#fn:43">43</a></sup></td><td>8.8</td><td>3.0</td><td>6.8</td><td>F</td><td>4.9</td><td>25.8</td><td>1.7</td><td>3.0 </td><td>N/A</td></tr><tr><td>TTT3R <sup><a href="#fn:7">7</a></sup></td><td>21.5</td><td>15.4</td><td>9.8</td><td>7.7</td><td>30.0</td><td>21.4</td><td>33.4</td><td>41.2 </td><td>22.55</td></tr><tr><td>DSO <sup><a href="#fn:9">9</a></sup></td><td>7.3</td><td>21.8</td><td>10.1</td><td>7.6</td><td>30.6</td><td>26.5</td><td>4.7</td><td>11.2 </td><td>14.98</td></tr><tr><td>MonST3R <sup><a href="#fn:62">62</a></sup></td><td>7.2</td><td>6.0</td><td>6.6</td><td>6.9</td><td>9.8</td><td>16.1</td><td>3.5</td><td>6.7 </td><td>7.85</td></tr><tr><td>DROID-SLAM <sup><a href="#fn:48">48</a></sup></td><td>7.5</td><td>4.1</td><td>5.2</td><td>6.5</td><td>4.3</td><td>5.4</td><td>2.3</td><td>4.0 </td><td>4.91</td></tr><tr><td>DynaMoN (MS&SS) <sup><a href="#fn:44">44</a></sup></td><td>2.8</td><td>2.7</td><td>3.5</td><td>2.8</td><td>14.8</td><td>2.2</td><td>1.3</td><td>2.7 </td><td>4.10</td></tr><tr><td>DynaMoN (MS) <sup><a href="#fn:44">44</a></sup></td><td>6.8</td><td>3.8</td><td>6.1</td><td>5.6</td><td>2.4</td><td>3.5</td><td>1.4</td><td>2.6 </td><td>4.02</td></tr><tr><td>WildGS-SLAM <sup><a href="#fn:66">66</a></sup></td><td>2.8</td><td>2.4</td><td>1.6</td><td>2.2</td><td>3.9</td><td>3.1</td><td>1.7</td><td>2.5 </td><td>2.52</td></tr><tr><td>DROID-W (Ours)</td><td>2.6</td><td>2.5</td><td>1.3</td><td>1.8</td><td>3.3</td><td>2.9</td><td>1.6</td><td>2.3 </td><td>2.30</td></tr></tbody></table>

Table 1: Tracking Performance on the Bonn RGB-D Dynamic Dataset [^38] (ATE RMSE $\downarrow$ \[cm\]). Best results are highlighted as first, second, and third. “-” indicates sequences without reported results in the original papers or unavailable code. “F” denotes tracking failure. For MonST3R [^62], we use the same keyframes as our method and perform evaluation in a window-wise manner with a window size of 20 and an overlap ratio of 0.5 to reduce memory consumption.

<table><tbody><tr><td>Method</td><td>f2/dp</td><td>f3/ss</td><td>f3/sx</td><td>f3/sr</td><td>f3/shs</td><td>f3/ws</td><td>f3/wx</td><td>f3/wr</td><td>f3/whs </td><td>Avg.</td></tr><tr><td colspan="11">RGB-D</td></tr><tr><td>NICE-SLAM <sup><a href="#fn:71">71</a></sup></td><td>88.8</td><td>1.6</td><td>32.0</td><td>59.1</td><td>8.6</td><td>79.8</td><td>86.5</td><td>244.0</td><td>152.0 </td><td>83.60</td></tr><tr><td>ORB-SLAM2 <sup><a href="#fn:35">35</a></sup></td><td>0.6</td><td>0.8</td><td>1.0</td><td>2.5</td><td>2.5</td><td>40.8</td><td>72.2</td><td>80.5</td><td>72.3 </td><td>30.36</td></tr><tr><td>ReFusion <sup><a href="#fn:38">38</a></sup></td><td>4.9</td><td>0.9</td><td>4.0</td><td>13.2</td><td>11.0</td><td>1.7</td><td>9.9</td><td>40.6</td><td>10.4 </td><td>10.73</td></tr><tr><td>DynaSLAM (N+G) <sup><a href="#fn:4">4</a></sup></td><td>0.7</td><td>0.5</td><td>1.5</td><td>2.7</td><td>1.7</td><td>0.6</td><td>1.5</td><td>3.5</td><td>2.5 </td><td>1.69</td></tr><tr><td>DG-SLAM <sup><a href="#fn:57">57</a></sup></td><td>3.2</td><td>-</td><td>1.0</td><td>-</td><td>-</td><td>0.6</td><td>1.6</td><td>4.3</td><td>- </td><td>N/A</td></tr><tr><td>RoDyn-SLAM <sup><a href="#fn:18">18</a></sup></td><td>-</td><td>-</td><td>-</td><td>-</td><td>4.4</td><td>1.7</td><td>8.3</td><td>-</td><td>5.6 </td><td>N/A</td></tr><tr><td>DDN-SLAM (RGB-D) <sup><a href="#fn:26">26</a></sup></td><td>-</td><td>-</td><td>1.0</td><td>-</td><td>1.7</td><td>1.0</td><td>1.4</td><td>3.9</td><td>2.3 </td><td>N/A</td></tr><tr><td>UP-SLAM <sup><a href="#fn:67">67</a></sup></td><td>1.3</td><td>-</td><td>0.9</td><td>-</td><td>-</td><td>0.7</td><td>1.6</td><td>-</td><td>2.6 </td><td>N/A</td></tr><tr><td>ADD-SLAM <sup><a href="#fn:55">55</a></sup></td><td>-</td><td>-</td><td>-</td><td>-</td><td>1.3</td><td>0.5</td><td>1.4</td><td>-</td><td>1.6 </td><td>N/A</td></tr><tr><td colspan="11">RGB-only</td></tr><tr><td>TTT3R <sup><a href="#fn:7">7</a></sup></td><td>113.1</td><td>3.1</td><td>5.8</td><td>6.4</td><td>24.9</td><td>2.0</td><td>24.7</td><td>15.9</td><td>23.1 </td><td>24.33</td></tr><tr><td>MonST3R <sup><a href="#fn:62">62</a></sup></td><td>33.9</td><td>0.8</td><td>28.3</td><td>5.1</td><td>36.8</td><td>1.6</td><td>19.1</td><td>16.6</td><td>32.8 </td><td>19.45</td></tr><tr><td>DSO <sup><a href="#fn:9">9</a></sup></td><td>2.2</td><td>1.7</td><td>11.5</td><td>3.7</td><td>12.4</td><td>1.5</td><td>12.9</td><td>13.8</td><td>40.7 </td><td>11.15</td></tr><tr><td>DDN-SLAM (RGB) <sup><a href="#fn:26">26</a></sup></td><td>-</td><td>-</td><td>1.3</td><td>-</td><td>3.1</td><td>2.5</td><td>2.8</td><td>8.9</td><td>4.1 </td><td>N/A</td></tr><tr><td>Splat-SLAM <sup><a href="#fn:43">43</a></sup></td><td>0.7</td><td>0.5</td><td>0.9</td><td>2.3</td><td>1.5</td><td>2.3</td><td>1.3</td><td>3.9</td><td>2.2 </td><td>1.71</td></tr><tr><td>DynaMoN (MS) <sup><a href="#fn:44">44</a></sup></td><td>0.6</td><td>0.5</td><td>0.9</td><td>2.1</td><td>1.9</td><td>1.4</td><td>1.4</td><td>3.9</td><td>2.0 </td><td>1.63</td></tr><tr><td>DynaMoN (MS&SS) <sup><a href="#fn:44">44</a></sup></td><td>0.7</td><td>0.5</td><td>0.9</td><td>2.4</td><td>2.3</td><td>0.7</td><td>1.4</td><td>3.9</td><td>1.9 </td><td>1.63</td></tr><tr><td>DROID-SLAM <sup><a href="#fn:48">48</a></sup></td><td>0.6</td><td>0.5</td><td>0.9</td><td>2.2</td><td>1.4</td><td>1.2</td><td>1.6</td><td>4.0</td><td>2.2 </td><td>1.62</td></tr><tr><td>WildGS-SLAM <sup><a href="#fn:66">66</a></sup></td><td>1.4</td><td>0.5</td><td>0.8</td><td>2.4</td><td>2.0</td><td>0.4</td><td>1.3</td><td>3.3</td><td>1.6 </td><td>1.51</td></tr><tr><td>DROID-W (Ours)</td><td>1.1</td><td>0.5</td><td>0.8</td><td>2.1</td><td>1.4</td><td>0.5</td><td>1.2</td><td>3.1</td><td>1.6 </td><td>1.36</td></tr></tbody></table>

Table 2: Tracking Performance on TUM RGB-D Dataset [^46] (ATE RMSE $\downarrow$ \[cm\]). Best results are highlighted as first,second, andthird. “-” indicates sequences without reported results in the original papers or unavailable code. Our approach consistently leads to the best or second-best results on the sequences, on average, outperforming all baselines.

<table><tbody><tr><td>Method</td><td>apple</td><td>backpack</td><td>block</td><td>creeper</td><td>handwavy</td><td>haru</td><td>mochi</td><td>paper</td><td>pillow</td><td>spin</td><td>sriracha</td><td>teddy </td><td>Avg.</td></tr><tr><td colspan="14">RGB-D</td></tr><tr><td>NICE-SLAM <sup><a href="#fn:71">71</a></sup></td><td>0.186</td><td>0.149</td><td>0.099</td><td>0.166</td><td>0.059</td><td>F</td><td>0.042</td><td>0.062</td><td>0.171</td><td>0.211</td><td>0.073</td><td>0.060 </td><td>N/A</td></tr><tr><td>DynaSLAM (N+G) <sup><a href="#fn:4">4</a></sup></td><td>0.981</td><td>0.045</td><td>0.731</td><td>1.709</td><td>0.796</td><td>0.322</td><td>1.263</td><td>F</td><td>0.713</td><td>0.322</td><td>1.098</td><td>0.296 </td><td>N/A</td></tr><tr><td colspan="14">RGB-only</td></tr><tr><td>MonST3R <sup><a href="#fn:62">62</a></sup></td><td>1.236</td><td>0.013</td><td>1.141</td><td>0.324</td><td>0.125</td><td>0.263</td><td>0.089</td><td>0.037</td><td>1.118</td><td>0.118</td><td>0.060</td><td>0.279 </td><td>0.400</td></tr><tr><td>TTT3R <sup><a href="#fn:66">66</a></sup></td><td>0.915</td><td>0.026</td><td>0.507</td><td>0.699</td><td>0.298</td><td>0.042</td><td>0.233</td><td>0.070</td><td>0.712</td><td>0.353</td><td>0.215</td><td>0.125 </td><td>0.350</td></tr><tr><td>Splat-SLAM <sup><a href="#fn:43">43</a></sup></td><td>0.038</td><td>0.005</td><td>0.078</td><td>0.052</td><td>0.024</td><td>0.078</td><td>0.211</td><td>0.011</td><td>0.262</td><td>0.007</td><td>0.005</td><td>0.048 </td><td>0.068</td></tr><tr><td>WildGS-SLAM <sup><a href="#fn:7">7</a></sup></td><td>0.043</td><td>0.006</td><td>0.047</td><td>0.029</td><td>0.016</td><td>0.085</td><td>0.017</td><td>0.013</td><td>0.378</td><td>0.005</td><td>0.005</td><td>0.027 </td><td>0.056</td></tr><tr><td>DROID-SLAM <sup><a href="#fn:48">48</a></sup></td><td>0.036</td><td>0.008</td><td>0.156</td><td>0.015</td><td>0.016</td><td>0.005</td><td>0.018</td><td>0.011</td><td>0.179</td><td>0.009</td><td>0.010</td><td>0.061 </td><td>0.044</td></tr><tr><td>DROID-W (Ours)</td><td>0.043</td><td>0.005</td><td>0.037</td><td>0.017</td><td>0.015</td><td>0.093</td><td>0.010</td><td>0.012</td><td>0.145</td><td>0.005</td><td>0.004</td><td>0.019 </td><td>0.034</td></tr></tbody></table>

Table 3: Tracking Performance on DyCheck Dataset [^11] (ATE RMSE $\downarrow$). Best results are highlighted as first,second, andthird. “-” indicates sequences without reported results in the original papers or unavailable code. “F” means tracking failure. Our approach demonstrates the effectiveness and robustness in highly-textured, diverse environments, where prior methods relying on object segmentation or Gaussian mapping for uncertainty optimization often fail.

| Method | Downtown 1 | Downtown 2 | Downtown 3 | Downtown 4 | Downtown 5 | Downtown 6 | Downtown 7 | Avg. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TTT3R [^7] | 4.64 | 11.25 | 4.30 | 7.35 | 11.28 | 5.09 | 7.26 | 7.309 |
| Splat-SLAM [^43] | 0.10 | 6.44 | 0.89 | 0.66 | 0.91 | 2.11 | 0.07 | 1.597 |
| DROID-SLAM [^48] | 0.26 | 7.84 | 1.05 | 0.33 | 0.64 | 0.06 | 0.05 | 1.460 |
| WildGS-SLAM [^7] | 0.10 | 0.95 | 0.43 | 0.36 | 0.87 | 1.22 | 0.53 | 0.637 |
| DROID-W (Ours) | 0.15 | 0.25 | 0.15 | 0.32 | 0.24 | 0.43 | 0.07 | 0.230 |

Table 4: Tracking Performance on DROID-W Dataset (ATE RMSE $\downarrow$ \[m\]). Best results are highlighted as first, second.

| Method | Dynamic | Bonn [^38] | TUM [^46] | DyCheck [^11] |
| --- | --- | --- | --- | --- |
| DROID-SLAM [^48] | ✗ | 19.89 | 26.97 | 17.50 |
| WildGS-SLAM [^66] | ✓ | 0.22 | 0.32 | 0.18 |
| DROID-W (Ours) | ✓ | 10.57 | 14.92 | 11.06 |

Table 5: Runtime Comparisons (average FPS $\uparrow$). All evaluations are conducted on an RTX 3090 GPU with a 16-core CPU.

![Refer to caption](https://arxiv.org/html/2603.19076v1/fig_tex/figures_vis_recon/StMoritz01/stmoritz_seg00_frames.jpg)

Figure 4: 3D Reconstruction Comparisons on YouTube Sequences. We compare 3D reconstruction quality of DROID-SLAM 48, WildGS-SLAM 66, and our method. Point clouds from DROID-SLAM and ours are visualized directly, while Gaussian renderings from WildGS-SLAM are displayed using the 3DGS viewer. WildGS-SLAM fails on most sequences. DROID-SLAM shows obvious scale drift ( St. Moritz 1 ), inaccurate geometry ( St. Moritz 3 ), and noisy distractors ( Tokyo Walking 2 & 3 ) under challenging dynamic environments. Our approach produces accurate and consistent reconstructions across highly dynamic and visually challenging real-world sequences.

| Method | ATE RMSE \[cm\] |
| --- | --- |
| a. w/o Uncertainty-aware BA | 5.13 |
| b. w/o monocular depth | 3.30 |
| c. w/o uncertainty decouple | 2.57 |
| d. w/o affine mapping | 2.47 |
| e. w/o weight decay | 2.34 |
| Full | 2.30 |

Table 6: Ablation Studies on Bonn RGB-D Dataset [^38]. Details about each configuration are described in Sec. 4.2.

#### Baselines

We conduct comparisons with both SLAM-style and recent feed-forward methods. For SLAM-style methods, existing methods can be categorized into four groups: (a) Classic SLAM: DSO [^9], ORB-SLAM2 [^35], and DROID-SLAM [^48]; (b) Classic dynamic SLAM: ReFusion [^38] and DynaSLAM [^4]; (c) NeRF-/GS-based SLAM in static environments: NICE-SLAM [^71], and Splat-SLAM [^43]; (d) NeRF-/GS-based SLAM in dynamic environments: DG-SLAM [^57], RoDyn-SLAM [^18], DDN-SLAM [^26], DynaMoN [^44], UP-SLAM [^67], and ADD-SLAM [^55]. For feed-forward approaches, we compare with MonST3R [^62] and the very recent TTT3R [^7].

#### Metrics

We use the Absolute Trajectory Error (ATE) to evaluate camera tracking accuracy. For the DyCheck dataset [^11], we follow MegaSaM [^28] and normalize the ground-truth camera trajectories to unit length, as the sequence lengths in this dataset vary significantly. Following DROID-SLAM, our approach performs optimization only for keyframes. To evaluate full trajectories, we recover non-keyframe poses through SE(3) interpolation followed by a pose graph update. For all methods, we align the estimated camera trajectory with the ground-truth camera trajectory through Sim(3) Umeyama alignment [^50]. In addition to tracking accuracy, for each method, we report the average run-time by dividing the number of input frames by the total time.

### 4.1 Experimental Results

Quantitative Results. Camera tracking results on four benchmarks are reported in Tables 1, 2, 3, and 4. Table 1 indicates that our approach achieves the best camera tracking accuracy across all baselines on the Bonn RGB-D Dynamic dataset [^38] due to effective uncertainty optimization. As shown in Table 2, WildGS-SLAM [^66] exhibits a noticeable performance drop compared to DROID-SLAM [^48] on low-dynamic sequences (f3/sr, f3/shs). This gap mainly stems from the unreliable uncertainty estimation, caused by challenging mapping in visually complex environments. In contrast, our method achieves comparable tracking accuracy to DROID-SLAM on low-dynamic scenes and significantly outperforms it on high-dynamic sequences by effectively handling motion-induced inconsistencies.

The DyCheck dataset is characterized by motion and scene diversity across indoor and outdoor scenarios. Table 3 demonstrates that WildGS-SLAM often fails to achieve accurate camera tracking due to the difficulty of scene reconstruction in these complex settings and erroneous uncertainty estimation, whereas our method remains stable and accurate. On scene haru, where a moving dog dominates the view, our accurate uncertainty estimation suppresses dynamic regions. Consequently, fewer reliable background features remain to support tracking, which degrades our performance. On average, our proposed method outperforms all baselines. Table 4 presents the experimental results on the proposed large-scale outdoor dataset DROID-W. Our method shows superior performance over prior works under this extremely challenging condition. Feed-forward approaches such as MonST3R [^62] and TTT3R [^7] suffer from substantially higher tracking errors across all benchmarks compared to optimization-based SLAM systems.

Runtime analysis is in Table 5. We compare with DROID-SLAM and WildGS-SLAM, the most recent state-of-the-art baseline for monocular dynamic SLAM. Our system achieves a $\mathbf{40\times}$ speedup over WildGS-SLAM and maintains real-time performance at approximately 10 FPS. Our approach is slightly slower than DROID-SLAM due to monocular depth estimation and DINOv2 [^37] feature extraction. Overall, these results highlight the effectiveness, robustness, and efficiency of our uncertainty-aware formulation compared with existing SLAM-style and feed-forward baselines.

Qualitative Comparisons. Fig. 3 presents comparisons of the estimated uncertainty maps. We observe that our approach delivers the most accurate dynamic uncertainty estimates, whereas WildGS-SLAM produces erroneous results near moving objects and severely incorrect predictions on challenging sequences. As shown in Fig. 3, TUM RGB-D dataset features motion blur, partial overexposure, and cluttered indoor scenes that easily degrade mapping quality. Our introduced sequences offer diverse object motion and scene configuration, which poses challenges to high-quality geometric reconstruction. WildGS-SLAM exhibits degraded performance in these challenging sequences with low-quality imagery and highly textured backgrounds, where erroneous Gaussian reconstruction leads to unstable uncertainty estimates. MonST3R [^62] heavily depends on the alignment of dynamic point clouds predicted by the pretrained model, which often results in incomplete or missed detections of moving objects due to limited generalizability.

In contrast, our method yields spatially coherent, semantically consistent uncertainty maps. It sharply delineates dynamic regions and maintains stable confidence in static areas across challenging scenarios, demonstrating the robustness of our uncertainty optimization.

Finally, we compare the reconstruction quality in challenging YouTube sequences. Fig. 4 illustrates that DROID-SLAM produces inaccurate point clouds in dynamic scenes, as moving distractors lead to unreliable reprojection residuals and disrupt pose estimation. The reconstructions of DROID-SLAM exhibit scale drift (St. Moritz 1), erroneous geometry (St. Moritz 3), and noisy distractors (Tokyo Walking 1 & 2). WildGS-SLAM struggles to reconstruct Gaussian maps under these conditions, resulting in near-complete failures on all sequences. In contrast, our method yields geometrically accurate and temporally consistent point clouds, maintaining stable reconstruction quality even in challenging outdoor scenarios.

### 4.2 Ablation Study

We conduct ablations of the main modules in Table 6. In the a. w/o Uncertainty-aware BA setting, we disable the uncertainty update and weight the reprojection term solely by the confidence map. For the experiments c. w/o uncertainty decouple, we modify the similarity loss in Eq. (6) as follows:

$$
\footnotesize\mathbf{E}_{\text{sim}}^{*}(\mathbf{u}^{\prime})=\sum_{(i,j)\in\mathcal{E}}\frac{1-\frac{\mathbf{F}_{i}\cdot{\mathbf{F}}_{ij}}{{\|\mathbf{F}_{i}\|}_{2}{\|{\mathbf{F}}_{ij}\|}_{2}}}{{{\mathbf{u}}^{\prime}_{i}}^{2}}.
$$

In experiments d. w/o affine mapping, uncertainties are updated directly rather than by optimizing parameters of the affine mapping. Removing the affine mapping introduces temporal and spatial inconsistencies in uncertainty estimation, leading to degraded performance. In case of e. w/o weight decay, the lack of regularization term for affine mapping will cause instability, thereby leading to performance drop on some scenes. As shown in Table 6, the full system consistently outperforms all variants, validating the effectiveness of each component.

## 5 Conclusion

In this paper, we presented a novel monocular dynamic SLAM system. Our system optimizes dynamic uncertainty within a differentiable bundle adjustment framework by leveraging multi-view feature similarity. Extensive experiments demonstrate that our effective uncertainty optimization enables robust camera tracking and accurate geometric reconstruction across challenging real-world scenarios, where prior methods often struggle. Code will be public.

#### Limitations

Our uncertainty optimization relies on frame-to-frame alignment, which can lead to inaccurate uncertainty estimation during SLAM initialization when pose estimates are still unreliable. Incorporating reconstruction priors could improve the robustness of the initialization stage.

## 6 Acknowledgements

We thank Wei Zhang for valuable help with collecting the DROID-W dataset.

## References

Supplementary Material

In the supplementary material, we provide additional details about the following:

- More information about the DROID-W dataset and downloaded YouTube videos (Sec. 7).
- Details about the Jacobian derivation of our uncertainty optimization (Sec. 8).
- Additional qualitative comparisons for uncertainty, point clouds, and ablation study (Sec. 9).

## 7 Dataset

| Sequence | Number of Frames | Length of Trajectory \[m\] |
| --- | --- | --- |
| Downtown 1 | 1427 | 90.83 |
| Downtown 2 | 2200 | 122.25 |
| Downtown 3 | 1438 | 62.33 |
| Downtown 4 | 1794 | 85.19 |
| Downtown 5 | 2157 | 129.93 |
| Downtown 6 | 1900 | 104.99 |
| Downtown 7 | 1900 | 109.35 |

Table 7: Overview of Our DROID-W Dataset.

| Method | Inputs | Downtown 3 | Downtown 4 | Downtown 5 | Downtown 6 | Downtown 7 | Avg. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FAST-LIVO2 [^65] | RGB + IMU + LiDAR | 0.06 | 0.06 | 0.09 | 0.09 | 0.06 | 0.071 |
| DROID-W (Ours) | RGB | 0.15 | 0.32 | 0.24 | 0.43 | 0.07 | 0.242 |

Table 8: Tracking performance of FAST-LIVO2 [^65] on the DROID-W dataset (ATE RMSE $\downarrow$ \[m\]). FAST-LIVO2 is an efficient and accurate LiDAR-inertial-visual fusion system capable of delivering centimeter-level localization accuracy. Its performance on Downtown 3-7 demonstrates sufficient accuracy to serve as ground truth for Downtown 1-2.

| Sequence | Time | FPS | Resolution |
| --- | --- | --- | --- |
| Elephant Herd | 00:08 | 24 | 1280 $\times$ 720 |
| Giraffe | 00:09 | 24 | 1280 $\times$ 720 |
| Taylor | 01:13 | 30 | 1280 $\times$ 720 |
| Tomyum 1 | 01:40 | 30 | 1280 $\times$ 720 |
| Tomyum 2 | 01:40 | 30 | 1280 $\times$ 720 |
| St. Moritz | 30:00 | 50 | 1280 $\times$ 720 |
| Tokyo Walking 1 | 00:50 | 60 | 1920 $\times$ 1080 |
| Tokyo Walking 2 | 00:22 | 60 | 1920 $\times$ 1080 |
| Tokyo Walking 3 | 00:40 | 60 | 1920 $\times$ 1080 |

Table 9: Overview of Downloaded YouTube Videos.

Prior benchmarks on dynamic SLAM are limited to indoor environments, exhibiting simple object motions and lacking truly challenging real-world conditions. To enable evaluation in more complex and unconstrained settings, we introduce an outdoor dataset, DROID-W, and additionally download 6 challenging videos from YouTube.

#### DROID-W Dataset

The DROID-W dataset is captured using a Livox Mid-360 LiDAR rigidly mounted with an RGB camera. It comprises 7 outdoor sequences (Downtown 1-7) with RGB frames at a resolution of 1200 ${\times}$ 1600, ground-truth camera poses, and synchronized IMU and LiDAR measurements. The RGB stream is recorded at 20 FPS, while RTK provides ground-truth poses at 10 Hz. We use the estimated trajectories from FAST-LIVO2 [^65] as ground truth for Downtown 1-2 due to the absence of RTK measurements. As shown in Table 8, FAST-LIVO2 provides sufficiently accurate estimates to serve as reliable ground truth for these sequences. Detailed information, including trajectory lengths and frame numbers, is reported in Table 7. The DROID-W dataset features long camera trajectories, high scene dynamics, and partial over-exposure – characteristics commonly encountered in real-world scenarios. We believe this dataset will provide significant value to the community and support future research on robust in-the-wild SLAM.

#### YouTube Videos

The framerates of the YouTube videos vary substantially. Therefore, we report the FPS and sequence duration for each sequence in Table 9, which provides a more meaningful characterization of camera motion and scene dynamics. Camera intrinsics are estimated using MonST3R [^62] from the first 20 frames of each video. The sequences contain a large number of dynamic objects of diverse categories, with many of them moving simultaneously, leading to highly dynamic scenes. They also exhibit challenging and cluttered conditions, including motion blur, strong view-dependent effects, and low dynamic range.

## 8 Uncertainty Optimization and Jacobians

Given the definition in Sec. 3.3 of the main paper, we obtain the following uncertainty energy function:

$$
\displaystyle\mathbf{u}^{\prime}_{i}
$$
 
$$
\displaystyle=\mathrm{log}(\mathrm{exp}(\boldsymbol{\theta}\cdot\mathbf{F}_{i})+1),
$$
$$
\displaystyle\mathbf{E}_{\text{uncer}}(\mathbf{u}^{\prime})
$$
 
$$
\displaystyle=\sum_{(i,j)\in\mathcal{E}}\mathbf{e}_{ij}+\gamma_{\text{prior}}\sum_{i}\mathrm{log}(\mathbf{u}^{\prime}_{i}+0),
$$
$$
\displaystyle=\sum_{(i,j)\in\mathcal{E}}\frac{1-\frac{\mathbf{F}_{i}\cdot{\mathbf{F}}_{ij}}{{\|\mathbf{F}_{i}\|}_{2}{\|{\mathbf{F}}_{ij}\|}_{2}}}{\mathbf{u}^{\prime}_{i}\cdot{\mathbf{u}}^{\prime}_{ij}}+\gamma_{\text{prior}}\sum_{i}\mathrm{log}(\mathbf{u}^{\prime}_{i}+0).
$$

Thus, we can derive the following Jacobians:

$$
\displaystyle\frac{\partial\mathbf{e}_{ij}}{\partial\mathbf{u}^{\prime}_{i}}
$$
 
$$
\displaystyle=-\frac{1-\frac{\mathbf{F}_{i}\cdot{\mathbf{F}}_{ij}}{{\|\mathbf{F}_{i}\|}_{2}{\|{\mathbf{F}}_{ij}\|}_{2}}}{{(\mathbf{u}^{\prime}_{i})}^{2}\cdot\mathbf{u}^{\prime}_{ij}}=-\frac{\mathbf{e}_{ij}}{\mathbf{u}^{\prime}_{i}},
$$
$$
\displaystyle\frac{\partial\mathbf{e}_{ij}}{\partial\mathbf{u}^{\prime}_{j}}
$$
 
$$
\displaystyle=-\frac{1-\frac{\mathbf{F}_{i}\cdot{\mathbf{F}}_{ij}}{{\|\mathbf{F}_{i}\|}_{2}{\|{\mathbf{F}}_{ij}\|}_{2}}}{\mathbf{u}^{\prime}_{i}\cdot{(\mathbf{u}^{\prime}_{ij})}^{2}}\cdot\frac{\partial\mathbf{u}^{\prime}_{ij}}{\mathbf{u}^{\prime}_{j}}=-\frac{\mathbf{e}_{ij}}{\mathbf{u}^{\prime}_{j}}\cdot\boldsymbol{\alpha}_{ij}.
$$

where $\boldsymbol{\alpha}_{ij}\in\mathcal{R}^{(\frac{H}{8}\times\frac{W}{8})\times(\frac{H}{8}\times\frac{W}{8})}$ is the bilinear interpolation weight matrix whose non-zero elements are of size $\frac{H}{8}\times\frac{W}{8}\times 4$. The final Jacobians are defined as follows:

$$
\displaystyle\frac{\partial{\mathbf{E}_{uncer}}}{\mathbf{u}^{\prime}_{l}}
$$
 
$$
\displaystyle=-\sum_{(l,m)\in\mathcal{E}}\frac{\mathbf{e}_{lm}}{\mathbf{u}^{\prime}_{l}}-\sum_{(k,l)\in\mathcal{E}}\frac{\mathbf{e}_{kl}}{\mathbf{u}^{\prime}_{k}}\cdot\boldsymbol{\alpha}_{kl}+\gamma_{\text{prior}}\cdot\frac{1}{\mathbf{u}^{\prime}_{l}+1.0},
$$
$$
\displaystyle\frac{\partial{\mathbf{u}^{\prime}_{l}}}{\partial{\boldsymbol{\theta}}}
$$
 
$$
\displaystyle=\frac{1}{1+\mathrm{exp}(-\boldsymbol{\theta\cdot\mathbf{F}_{l}})}\cdot\mathbf{F}_{l},
$$
$$
\displaystyle\frac{\partial{\mathbf{E}_{\text{uncer}}}}{\partial\boldsymbol{\theta}}
$$
 
$$
\displaystyle=\sum_{l=0}^{N}\frac{\partial{\mathbf{E}_{\text{uncer}}}}{\partial\mathbf{u}^{\prime}_{l}}\cdot\frac{\partial{\mathbf{u}^{\prime}_{l}}}{\partial{\boldsymbol{\theta}}}.
$$

Here, frame $l$ serves as the reference frame in all edges $(l,m)$ and as the target frame in all edges $(k,l)$.

## 9 Additional Experiments

### 9.1 Uncertainty Estimation

![Refer to caption](https://arxiv.org/html/2603.19076v1/fig_tex/sup/uncer/stmoritz01/input_kf_297_ts_02900.png)

Figure 5: Uncertainty Estimation.

![Refer to caption](https://arxiv.org/html/2603.19076v1/x3.png)

Figure 6: Uncertainty Visualization for Consecutive Frames of YouTube Tomyum 1. We observe that our method robustly handles scenarios in which an object transitions from a static state to dynamic motion, such as a door being pushed open by a person. Prior to the onset of motion, our approach leverages stable visual correspondences on the door to help tracking, since our uncertainty optimization is based on frame-to-frame feature alignment.

![Refer to caption](https://arxiv.org/html/2603.19076v1/x4.png)

Figure 7: Uncertainty Visualization for Consecutive Frames of YouTube Tomyum 2. Our approach assigns high uncertainty to regions exhibiting strong view-dependent effects (e.g., the mirror).

#### Uncertainty Comparisons on YouTube Videos

We provide additional qualitative results on uncertainty estimation in Fig. 5. As shown in Fig. 5, WildGS-SLAM [^66] always fails to construct the reliable Gaussian map, leading to inaccurate and noisy uncertainty predictions. In contrast, our method leverages frame-to-frame feature alignment, demonstrating significantly greater robustness in visually complex and truly in-the-wild environments.

Moreover, our approach effectively handles strong view-dependent effects such as reflections and shadows (e.g. reflections in Taylor 22 and Tokyo Walking 2). It is also highly sensitive to small dynamic objects, enabling precise uncertainty estimation even under challenging real-world conditions. Our method further exhibits strong robustness to severe motion blur and low dynamic range (e.g. Tomyum 1 and Tomyum 2), which are extremely difficult for conventional segmentation or detection approaches.

Overall, Fig. 5 highlights the accuracy and robustness of our uncertainty optimization in unconstrained in-the-wild settings, effectively delineating uncertain regions while maintaining high confidence in static areas.

#### Uncertainty Visualization for Consecutive Keyframes

We visualize the optimized uncertainties across consecutive keyframes in Fig. 6 and Fig. 7. Our method optimizes frame-wise uncertainty by exploiting multi-view feature similarity, allowing it to fully leverage static-scene information whenever available. As shown in Fig. 6, the system effectively utilizes the door region for camera tracking prior to keyframe 280. In addition, our uncertainty estimation integrates multi-view cues from frames connected through the frame graph, i.e. it captures multi-view inconsistency within a local window. Thus, our approach assigns the reasonable higher uncertainty to the door region of keyframes 280/281 before the door begins to move.

We observe strong mirror-reflection effects in Fig. 7, with keyframe 283 exhibiting the largest appearance change. Accordingly, our method assigns the highest uncertainty to keyframe 283, while maintaining relatively low uncertainty for the remaining keyframes that show only minor appearance differences. This behavior demonstrates the effectiveness of our approach and the precision of the resulting uncertainty estimates.

### 9.2 Point Cloud Reconstruction

#### Static Reconstruction Comparisons

We present 3D reconstruction comparisons between DROID-SLAM [^48] and our method in Fig. 8. In the top row, DROID-SLAM fails to recover consistent geometry – erroneously reconstructing a single corridor as two separate structures – and exhibits noticeable tracking drift in sequences with the presence of strong dynamic distractors. In contrast, our approach produces coherent geometric reconstructions and accurate pose estimates. The second row further highlights the robustness of our method: it reconstructs cleanly visible and highly accurate white lane markings on the asphalt road, even under challenging real-world conditions.

![Refer to caption](https://arxiv.org/html/2603.19076v1/fig_tex/figures_vis_recon/Taylor_22/Taylor_22_frames.jpg)

Figure 8: 3D Reconstruction Comparisons on YouTube Sequences. We compare reconstructed static point clouds between DROID-SLAM 48 and our method. Our approach produces more accurate and consistent reconstructions across highly dynamic and visually challenging real-world sequences. For the Taylor 22 scene, DROID-SLAM reconstructs two separate corridor structures due to inaccurate pose tracking, as highlighted in the boxed region, whereas our method produces a consistent geometric reconstruction. Moreover, the white lane marking on the asphalt road of Tokyo Walking 1 is faint and fragmented in the point cloud reconstructed by DROID-SLAM, while in our reconstruction it remains cleanly visible, continuous, and highly accurate.

#### Static / Dynamic Reconstruction

We visualize the static and dynamic point clouds in Fig. 9 and Fig. 10, providing complementary perspectives from both top-down and interior viewpoints. The high geometric consistency between our static reconstruction and the static regions within the dynamic point clouds illustrates the precision of our uncertainty estimation. These results demonstrate that our method effectively suppresses dynamic or uncertain regions while preserving the underlying static scene structure.

![Refer to caption](https://arxiv.org/html/2603.19076v1/x5.png)

Figure 9: Point Clouds Visualization from 4 Views. Top view: reconstructed static scene from 4 input views shown in the figure. Bottom view: reconstructed dynamic point clouds. The comparisons between the dynamic and static point clouds further demonstrate the effectiveness of our uncertainty estimation. In both visualizations, the static point clouds remain highly consistent, indicating that our method reliably preserves static geometry while filtering dynamic regions.

![Refer to caption](https://arxiv.org/html/2603.19076v1/fig_tex/dynamic_reconstruction/stmoritz02_static.jpg)

Figure 10: Qualitative Results of Our Static and Dynamic Reconstruction. We visualize globally aligned static reconstructions alongside dynamic point clouds across all keyframes. Notably, we apply the estimated per-frame dynamic uncertainty to filter out dynamic points. The left and right columns show the static and dynamic reconstructions, respectively. These comparisons highlight the accuracy of our uncertainty estimation, as our method effectively suppresses dynamic regions while preserving geometric fidelity in static areas.

### 9.3 Additional Ablation Study

| Method | ATE RMSE \[cm\] |
| --- | --- |
| w/o prior term | 5.18 |
| Full | 2.30 |

Table 10: Ablation Studies on Bonn RGB-D Dataset [^38].

Table 10 shows that the prior regularization term effectively avoid the trivial solution $\mathbf{u}\rightarrow\infty$. Without this prior, the system assigns uniformly large uncertainties to all pixels, resulting in results similar to the w/o Uncertainty-aware BA configuration reported in Table 6 of the main paper.

[^1]: P. Arm, G. Waibel, J. Preisig, T. Tuna, R. Zhou, V. Bickel, G. Ligeza, T. Miki, F. Kehl, H. Kolvenbach, et al. (2023) Scientific exploration of challenging planetary analog environments with a team of legged robots. Science robotics 8 (80), pp. eade9548. Cited by: §1.

[^2]: V. Badrinarayanan, A. Kendall, and R. Cipolla (2017) Segnet: a deep convolutional encoder-decoder architecture for image segmentation. IEEE transactions on pattern analysis and machine intelligence 39 (12), pp. 2481–2495. Cited by: §2.

[^3]: C. Badue, R. Guidolini, R. V. Carneiro, P. Azevedo, V. B. Cardoso, A. Forechi, L. Jesus, R. Berriel, T. M. Paixao, F. Mutz, et al. (2021) Self-driving cars: a survey. Expert systems with applications 165, pp. 113816. Cited by: §1.

[^4]: B. Bescos, J. M. Fácil, J. Civera, and J. Neira (2018) DynaSLAM: Tracking, Mapping and Inpainting in Dynamic Scenes. IEEE Robotics and Automation Letters (RA-L). Cited by: §1, §2, §4, Table 1, Table 2, Table 3.

[^5]: J. Chen, G. Li, S. Kumar, B. Ghanem, and F. Yu (2023) How to not train your dragon: training-free embodied object goal navigation with semantic frontiers. arXiv preprint arXiv:2305.16925. Cited by: §1.

[^6]: X. Chen, Y. Chen, Y. Xiu, A. Geiger, and A. Chen (2025) Easi3r: estimating disentangled motion from dust3r without training. arXiv preprint arXiv:2503.24391. Cited by: §2.

[^7]: X. Chen, Y. Chen, Y. Xiu, A. Geiger, and A. Chen (2025) Ttt3r: 3d reconstruction as test-time training. arXiv preprint arXiv:2509.26645. Cited by: §2, §4, §4.1, Table 1, Table 2, Table 3, Table 4, Table 4.

[^8]: B. Curless and M. Levoy (1996) A volumetric method for building complex models from range images. In ACM Trans. on Graphics, Cited by: §2.

[^9]: J. Engel, V. Koltun, and D. Cremers (2017) Direct sparse odometry. IEEE Trans. on Pattern Analysis and Machine Intelligence (PAMI). Cited by: §1, §2, §4, Table 1, Table 2.

[^10]: J. Engel, T. Schöps, and D. Cremers (2014) LSD-slam: large-scale direct monocular slam. In European conference on computer vision, pp. 834–849. Cited by: §2.

[^11]: H. Gao, R. Li, S. Tulsiani, B. Russell, and A. Kanazawa (2022) Monocular dynamic view synthesis: a reality check. Advances in Neural Information Processing Systems 35, pp. 33768–33780. Cited by: §4, §4, Table 3, Table 3, Table 5.

[^12]: A. Geiger, P. Lenz, C. Stiller, and R. Urtasun (2013) Vision meets robotics: the kitti dataset. The international journal of robotics research 32 (11), pp. 1231–1237. Cited by: §1.

[^13]: S. Ha, J. Yeon, and H. Yu (2024) Rgbd gs-icp slam. In European Conference on Computer Vision, pp. 180–197. Cited by: §2.

[^14]: K. He, G. Gkioxari, P. Dollár, and R. Girshick (2017) Mask r-cnn. In Proc. of the IEEE International Conf. on Computer Vision (ICCV), Cited by: §2.

[^15]: R. Hoque, P. Huang, D. J. Yoon, M. Sivapurapu, and J. Zhang (2025) EgoDex: learning dexterous manipulation from large-scale egocentric video. arXiv preprint arXiv:2505.11709. Cited by: §1.

[^16]: J. Hu, X. Chen, B. Feng, G. Li, L. Yang, H. Bao, G. Zhang, and Z. Cui (2024) Cg-slam: efficient dense rgb-d slam in a consistent uncertainty-aware 3d gaussian field. In European Conference on Computer Vision, pp. 93–112. Cited by: §2.

[^17]: M. Hu, W. Yin, C. Zhang, Z. Cai, X. Long, H. Chen, K. Wang, G. Yu, C. Shen, and S. Shen (2024) Metric3D v2: a versatile monocular geometric foundation model for zero-shot metric depth and surface normal estimation. arXiv preprint arXiv:2404.15506. Cited by: §3.4.

[^18]: H. Jiang, Y. Xu, K. Li, J. Feng, and L. Zhang (2024) RoDyn-slam: robust dynamic dense rgb-d slam with neural radiance fields. IEEE Robotics and Automation Letters (RA-L). Cited by: §1, §2, §4, Table 1, Table 2.

[^19]: M. M. Johari, C. Carta, and F. Fleuret (2022) ESLAM: efficient dense slam system based on hybrid representation of signed distance fields. arXiv preprint arXiv:2211.11704. Cited by: §2.

[^20]: N. Keetha, J. Karhade, K. M. Jatavallabhula, G. Yang, S. Scherer, D. Ramanan, and J. Luiten (2024) SplaTAM: splat track & map 3d gaussians for dense rgb-d slam. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), Cited by: §2.

[^21]: B. Kerbl, G. Kopanas, T. Leimkühler, and G. Drettakis (2023) 3D gaussian splatting for real-time radiance field rendering. ACM Trans. on Graphics. Cited by: §1, §2.

[^22]: C. Kerl, J. Sturm, and D. Cremers (2013) Dense visual slam for rgb-d cameras. In 2013 IEEE/RSJ international conference on intelligent robots and systems, pp. 2100–2106. Cited by: §2.

[^23]: C. Kerl, J. Sturm, and D. Cremers (2013) Robust odometry estimation for rgb-d cameras. In 2013 IEEE international conference on robotics and automation, pp. 3748–3754. Cited by: §2.

[^24]: A. Krishnan, S. Liu, P. Sarlin, O. Gentilhomme, D. Caruso, M. Monge, R. Newcombe, J. Engel, and M. Pollefeys (2025) Benchmarking egocentric visual-inertial slam at city scale. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 25207–25217. Cited by: §1.

[^25]: J. Kulhanek, S. Peng, Z. Kukelova, M. Pollefeys, and T. Sattler (2024) Wildgaussians: 3d gaussian splatting in the wild. In Advances in Neural Information Processing Systems (NIPS), Cited by: §1.

[^26]: M. Li, J. He, G. Jiang, and H. Wang (2024) Ddn-slam: real-time dense dynamic neural implicit slam with joint semantic encoding. arXiv preprint arXiv:2401.01545. Cited by: §2, §4, Table 1, Table 2, Table 2.

[^27]: Y. Li, Y. Fang, Z. Zhu, K. Li, Y. Ding, and F. Tombari (2025) 4d gaussian splatting slam. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 25019–25028. Cited by: §2.

[^28]: Z. Li, R. Tucker, F. Cole, Q. Wang, L. Jin, V. Ye, A. Kanazawa, A. Holynski, and N. Snavely (2024) Megasam: accurate, fast, and robust structure and motion from casual dynamic videos. arXiv preprint arXiv:2412.04463. Cited by: §4.

[^29]: H. Liu, L. Wang, H. Luo, F. Zhao, R. Chen, Y. Chen, M. Xiao, J. Yan, and D. Luo (2025) SDD-slam: semantic-driven dynamic slam with gaussian splatting. IEEE Robotics and Automation Letters. Cited by: §2.

[^30]: W. Liu, D. Anguelov, D. Erhan, C. Szegedy, S. Reed, C. Fu, and A. C. Berg (2016) Ssd: single shot multibox detector. In European conference on computer vision, pp. 21–37. Cited by: §2.

[^31]: X. Liu, J. Lei, A. Prabhu, Y. Tao, I. Spasojevic, P. Chaudhari, N. Atanasov, and V. Kumar (2024) Slideslam: sparse, lightweight, decentralized metric-semantic slam for multi-robot navigation. arXiv preprint arXiv:2406.17249. Cited by: §1.

[^32]: H. Matsuki, R. Murai, P. H. Kelly, and A. J. Davison (2024) Gaussian splatting slam. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), Cited by: §2.

[^33]: B. Mildenhall, P. P. Srinivasan, M. Tancik, J. T. Barron, R. Ramamoorthi, and R. Ng (2020) Nerf: representing scenes as neural radiance fields for view synthesis. In Proc. of the European Conf. on Computer Vision (ECCV), Cited by: §1, §2.

[^34]: R. Mur-Artal, J. M. M. Montiel, and J. D. Tardos (2015) ORB-slam: a versatile and accurate monocular slam system. IEEE transactions on robotics. Cited by: §1, §2.

[^35]: R. Mur-Artal and J. D. Tardós (2017) Orb-slam2: an open-source slam system for monocular, stereo, and rgb-d cameras. IEEE transactions on robotics. Cited by: §1, §2, §2, §4, Table 1, Table 2.

[^36]: R. A. Newcombe, S. Izadi, O. Hilliges, D. Molyneaux, D. Kim, A. J. Davison, P. Kohi, J. Shotton, S. Hodges, and A. Fitzgibbon (2011) Kinectfusion: real-time dense surface mapping and tracking. In 2011 10th IEEE international symposium on mixed and augmented reality, pp. 127–136. Cited by: §1.

[^37]: M. Oquab, T. Darcet, T. Moutakanni, H. Vo, M. Szafraniec, V. Khalidov, P. Fernandez, D. Haziza, F. Massa, A. El-Nouby, et al. (2023) Dinov2: learning robust visual features without supervision. arXiv preprint arXiv:2304.07193. Cited by: §1, Figure 2, Figure 2, §2, §3.3, §4.1.

[^38]: E. Palazzolo, J. Behley, P. Lottes, P. Giguère, and C. Stachniss (2019) ReFusion: 3D Reconstruction in Dynamic Environments for RGB-D Cameras Exploiting Residuals. In Proc. IEEE International Conf. on Intelligent Robots and Systems (IROS), Cited by: §2, §4, §4, §4.1, Table 1, Table 1, Table 1, Table 2, Table 5, Table 6, Table 6, Table 10, Table 10.

[^39]: W. Ren, Z. Zhu, B. Sun, J. Chen, M. Pollefeys, and S. Peng (2024) NeRF on-the-go: exploiting uncertainty for distractor-free nerfs in the wild. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), Cited by: §1, §3.3.

[^40]: M. Rünz and L. Agapito (2017) Co-fusion: real-time segmentation, tracking and fusion of multiple objects. In 2017 IEEE International Conference on Robotics and Automation (ICRA), pp. 4471–4478. Cited by: §2.

[^41]: M. Runz, M. Buffier, and L. Agapito (2018) Maskfusion: real-time recognition, tracking and reconstruction of multiple moving objects. In 2018 IEEE international symposium on mixed and augmented reality (ISMAR), pp. 10–20. Cited by: §2.

[^42]: E. Sandström, Y. Li, L. Van Gool, and M. R. Oswald (2023) Point-slam: dense neural point cloud-based slam. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 18433–18444. Cited by: §2.

[^43]: E. Sandström, K. Tateno, M. Oechsle, M. Niemeyer, L. Van Gool, M. R. Oswald, and F. Tombari (2024) Splat-slam: globally optimized rgb-only slam with 3d gaussians. arXiv preprint arXiv:2405.16544. Cited by: §2, §4, Table 1, Table 2, Table 3, Table 4.

[^44]: N. Schischka, H. Schieber, M. Asim Karaoglu, M. Görgülü, F. Grötzner, A. Ladikos, D. Roth, N. Navab, and B. Busam (2023) DynaMoN: motion-aware fast and robust camera localization for dynamic neural radiance fields. arXiv e-prints, pp. arXiv–2309. Cited by: §1, §2, §4, Table 1, Table 1, Table 2, Table 2.

[^45]: R. Scona, M. Jaimez, Y. R. Petillot, M. Fallon, and D. Cremers (2018) Staticfusion: background reconstruction for dense rgb-d slam in dynamic environments. In Proc. IEEE International Conf. on Robotics and Automation (ICRA), Cited by: §2.

[^46]: J. Sturm, N. Engelhard, F. Endres, W. Burgard, and D. Cremers (2012) A benchmark for the evaluation of rgb-d slam systems. In Proc. IEEE International Conf. on Intelligent Robots and Systems (IROS), Cited by: §4, Table 2, Table 2, Table 5.

[^47]: E. Sucar, S. Liu, J. Ortiz, and A. J. Davison (2021) IMAP: implicit mapping and positioning in real-time. In Proc. of the IEEE International Conf. on Computer Vision (ICCV), Cited by: §2.

[^48]: Z. Teed and J. Deng (2021) Droid-slam: deep visual slam for monocular, stereo, and rgb-d cameras. In Advances in Neural Information Processing Systems (NeurIPS), Cited by: §1, §1, §2, §3, Figure 4, Figure 4, Figure 4, §4, §4.1, Table 1, Table 2, Table 3, Table 4, Table 5, Figure 8, Figure 8, Figure 8, §9.2.

[^49]: Z. Teed, L. Lipson, and J. Deng (2023) Deep patch visual odometry. Advances in Neural Information Processing Systems 36, pp. 39033–39051. Cited by: §1, §2.

[^50]: S. Umeyama (1991) Least-squares estimation of transformation parameters between two point patterns. IEEE Trans. on Pattern Analysis and Machine Intelligence (PAMI). Cited by: §4.

[^51]: H. Wang, J. Wang, and L. Agapito (2023) Co-slam: joint coordinate and sparse parametric encodings for neural real-time slam. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 13293–13302. Cited by: §2.

[^52]: J. Wang, M. Chen, N. Karaev, A. Vedaldi, C. Rupprecht, and D. Novotny (2025) Vggt: visual geometry grounded transformer. In Proceedings of the Computer Vision and Pattern Recognition Conference, pp. 5294–5306. Cited by: §2.

[^53]: Q. Wang, Y. Zhang, A. Holynski, A. A. Efros, and A. Kanazawa (2025) Continuous 3d perception model with persistent state. In Proceedings of the Computer Vision and Pattern Recognition Conference, pp. 10510–10522. Cited by: §2.

[^54]: S. Wang, V. Leroy, Y. Cabon, B. Chidlovskii, and J. Revaud (2024) Dust3r: geometric 3d vision made easy. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), Cited by: §2.

[^55]: W. Wu, C. Su, S. Zhu, T. Deng, Z. Liu, and H. Wang (2025) ADD-slam: adaptive dynamic dense slam with gaussian splatting. arXiv preprint arXiv:2505.19420. Cited by: §1, §2, §4, Table 1, Table 2.

[^56]: W. Wu, G. Wang, T. Deng, S. Ægidiu, S. Shanks, V. Modugno, D. Kanoulas, and H. Wang (2025) Dvn-slam: dynamic visual neural slam based on local-global encoding. In 2025 IEEE International Conference on Robotics and Automation (ICRA), pp. 14564–14571. Cited by: §2.

[^57]: Y. Xu, H. Jiang, Z. Xiao, J. Feng, and L. Zhang (2024) Dg-slam: robust dynamic gaussian splatting slam with hybrid pose optimization. Advances in Neural Information Processing Systems 37, pp. 51577–51596. Cited by: §1, §2, §4, Table 1, Table 2.

[^58]: C. Yan, D. Qu, D. Xu, B. Zhao, Z. Wang, D. Wang, and X. Li (2024) Gs-slam: dense visual slam with 3d gaussian splatting. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 19595–19604. Cited by: §2.

[^59]: X. Yang, H. Li, H. Zhai, Y. Ming, Y. Liu, and G. Zhang (2022) Vox-fusion: dense tracking and mapping with voxel-based neural implicit representation. In 2022 IEEE International Symposium on Mixed and Augmented Reality (ISMAR), pp. 499–507. Cited by: §2.

[^60]: C. Yu, Z. Liu, X. Liu, F. Xie, Y. Yang, Q. Wei, and Q. Fei (2018) DS-slam: a semantic visual slam towards dynamic environments. In 2018 IEEE/RSJ international conference on intelligent robots and systems (IROS), pp. 1168–1174. Cited by: §2.

[^61]: Y. Yue, A. Das, F. Engelmann, S. Tang, and J. E. Lenssen (2024) Improving 2d feature representations by 3d-aware fine-tuning. In Proc. of the European Conf. on Computer Vision (ECCV), Cited by: §3.3.

[^62]: J. Zhang, C. Herrmann, J. Hur, V. Jampani, T. Darrell, F. Cole, D. Sun, and M. Yang (2024) MonST3R: a simple approach for estimating geometry in the presence of motion. arXiv preprint arxiv:2410.03825. Cited by: §2, Figure 3, Figure 3, Figure 3, §4, §4, §4.1, §4.1, Table 1, Table 1, Table 1, Table 2, Table 3, §7.

[^63]: T. Zhang, H. Zhang, Y. Li, Y. Nakamura, and L. Zhang (2020) Flowfusion: dynamic dense rgb-d slam based on optical flow. In Proc. IEEE International Conf. on Robotics and Automation (ICRA), Cited by: §2.

[^64]: Y. Zhang, F. Tosi, S. Mattoccia, and M. Poggi (2023) Go-slam: global optimization for consistent 3d instant reconstruction. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 3727–3737. Cited by: §2.

[^65]: C. Zheng, W. Xu, Z. Zou, T. Hua, C. Yuan, D. He, B. Zhou, Z. Liu, J. Lin, F. Zhu, et al. (2024) Fast-livo2: fast, direct lidar-inertial-visual odometry. IEEE Transactions on Robotics. Cited by: §4, §7, Table 8, Table 8, Table 8.

[^66]: J. Zheng, Z. Zhu, V. Bieri, M. Pollefeys, S. Peng, and I. Armeni (2025) Wildgs-slam: monocular gaussian splatting slam in dynamic environments. In Proceedings of the Computer Vision and Pattern Recognition Conference, pp. 11461–11471. Cited by: §1, §2, §3.3, Figure 3, Figure 3, Figure 3, Figure 4, Figure 4, Figure 4, §4.1, Table 1, Table 2, Table 3, Table 5, §9.1.

[^67]: W. Zheng, L. Ou, J. He, L. Zhou, X. Yu, and Y. Wei (2025) UP-slam: adaptively structured gaussian slam with uncertainty prediction in dynamic environments. arXiv preprint arXiv:2505.22335. Cited by: §1, §2, §4, Table 1, Table 2.

[^68]: F. Zhong, S. Wang, Z. Zhang, and Y. Wang (2018) Detect-slam: making object detection and slam mutually beneficial. In 2018 IEEE winter conference on applications of computer vision (WACV), pp. 1001–1010. Cited by: §2.

[^69]: X. Zhou, X. Wen, Z. Wang, Y. Gao, H. Li, Q. Wang, T. Yang, H. Lu, Y. Cao, C. Xu, et al. (2022) Swarm of micro flying robots in the wild. Science Robotics 7 (66), pp. eabm5954. Cited by: §1.

[^70]: Z. Zhu, S. Peng, V. Larsson, Z. Cui, M. R. Oswald, A. Geiger, and M. Pollefeys (2024) Nicer-slam: neural implicit scene encoding for rgb slam. In Proc. of the International Conf. on 3D Vision (3DV), Cited by: §2.

[^71]: Z. Zhu, S. Peng, V. Larsson, W. Xu, H. Bao, Z. Cui, M. R. Oswald, and M. Pollefeys (2022) NICE-slam: neural implicit scalable encoding for slam. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), Cited by: §2, §4, Table 1, Table 2, Table 3.