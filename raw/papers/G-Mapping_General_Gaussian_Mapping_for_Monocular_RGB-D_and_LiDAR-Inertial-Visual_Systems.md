---
title: "G²-Mapping: General Gaussian Mapping for Monocular, RGB-D, and LiDAR-Inertial-Visual Systems"
source: "https://ieeexplore.ieee.org/document/10884537"
author:
published:
created: 2026-05-15
description: "In this paper, we introduce G2-Mapping, a novel method to comprehensively support online monocular, RGB-D, and LiDAR-Inertial-Visual systems, employing 3D gauss"
tags:
  - "clippings"
---
## Abstract:

In this paper, we introduce G2-Mapping, a novel method to comprehensively support online monocular, RGB-D, and LiDAR-Inertial-Visual systems, employing 3D gaussian points...

---

Real-time localization and synchronous high-fidelity map reconstruction have long been the goals of SLAM systems. In recent years, attention has shifted to Neural Radiance Field (NeRF), which embeds point coordinates into high-dimensional space through frequency embedding, enabling them to capture high-frequency details at the cost of a large number of multi-layer perceptrons (MLPs). To reduce the computational cost of MLPs, recent work embeds them into artificially designed spatial structures, such as octrees \[1\], \[2\], tri-planes \[3\], hash grids \[4\] and so on. NICE-SLAM \[4\] adopts a multi-resolution feature grid SLAM to address the limitations of large scene local updates. ESLAM \[3\] and Co-SLAM \[5\] combine multi-scale axis-aligned encoding of scene, but this does not fundamentally solve the problem of low computational efficiency.

3D gaussian splatting is an appealing scene alternative representation that has an astonishing rendering efficiency, and can even reach 800 fps \[6\] (1080P) by reducing the dimension of spherical harmonics (SH), regularization, etc. It expresses the scene through tiled splats with gaussian points containing mean, covariance, opacity, and color. Similar to point cloud, it is easy to add, delete, and update locally, making it an ideal SLAM scene representation.

Although gaussian splatting employs differentiable rendering for color using CUDA, the lack of differentiable gradients for depth and pose constrains its direct application to SLAM. Furthermore, for monocular, the lack of depth information presents a significant challenge to scene initialization. At the same time, the non-convex nature in photometric loss introduces additional complexity to pose optimization, particularly over large baselines. Additionally, efficient scene update strategies are still needed to process online input frames without causing memory overflow, while also ensuring the quick convergence of the scene.

To address those issues, we propose G <sup>2</sup> -Mapping, a general mapping method based on gaussian scene representation, distinguished as the first to facilitate online tracking and mapping of data from monocular, RGB-D, or LiDAR-Inertial-Visual (LIV) sensors. We first derive formulas for differentiable color and depth rendering, including the Jacobian with respect to the camera pose. Second, to address the challenge of monocular scene initialization, we propose a scale consistency and uncertainty weighted depth optimization module, which counters inherent prediction inaccuracies. Finally, in terms of mapping, we delve into the rendering pipeline and propose a refined strategy for adding and deleting gaussian points to prevent rapid memory growth. Additionally, we propose depth-based gaussian initialization to accelerate scene convergence. Through alternating optimization of the camera pose and the scene, we achieve precise localization. Our method sets a new benchmark, outperforming current state-of-the-art methods in both localization accuracy and view synthesis quality. In summary, our contributions can be summarized as follows:

- We develop a comprehensive differentiable renderer that handles both color and depth. It includes the Jacobian with respect to the camera pose, enhancing the rendering process. By incorporating extra constraints during backpropagation, our renderer facilitates more accurate depth estimation and improves online pose estimation.
- We introduce a simplified odometry approach that provides metric depth estimation for monocular, addressing the challenge of scene initialization. Furthermore, We eliminate the impact of inaccurate depth by leveraging consistent observation.
- We propose a gaussian scene updating strategy that meticulously integrates depth-based gaussian initialization, the addition of gaussian points tailored to the rendering pipeline, and the removal of transparency. This strategy enables rapid convergence from novel views while preventing substantial memory growth.
- Experiments on monocular, RGB-D, and LiDAR datasets demonstrate that our method surpasses traditional SLAM methods in localization and exceeds the view synthesis quality of the latest neural-based SLAM methods.

### A. Traditional Visual SLAM

Existing visual SLAM systems commonly rely on either discrete handcrafted feature extraction or deep learning embeddings, following the framework outlined in \[7\] regarding mapping and tracking. Generally, dense visual SLAM focuses more on establishing detailed and accurate 3D maps, with pose estimation not being as accurate as in sparse SLAM \[8\], \[9\]. There are two main approaches to 3D scene representation for visual SLAM, namely using voxel grids \[10\], \[11\] and point clouds \[12\], \[13\], \[14\]. Voxel-based geometric representations are often highly efficient but are computationally expensive and challenging to directly determine the resolution of voxel representation when the scene is unknown. In contrast, point-based representations can adaptively adjust resolution and scene size by dynamically allocating points, making them well-suited for use in online SLAM \[13\]. Many recent works have focused on integrating deep learning techniques into dense visual SLAM systems to achieve more accurate and robust mapping and tracking. For example, SceneCode \[15\] and DROID-SLAM \[16\] have made significant contributions in this field, achieving more accurate and robust mapping and tracking. However, optimizing representations to capture high-fidelity correlations between primitives remains challenging.

### B. Neural Radiance Field Based SLAM

Traditional 3D reconstruction methods often involve the back-projection of 2D images into three-dimensional space and the weighted fusion of those projected results \[17\], \[18\]. This reconstruction approach often lacks the ability to express scene details. Neural Radiance Fields (NeRF) \[19\] has become a popular differentiable rendering method \[20\], dedicating to the generation of high-fidelity images from novel view. NeRF encodes color and opacity in the scene using MLPs. NeRF technology excels in expressing scene details and consistency. However, its training is time consuming, and it struggles to represent large scenes. Various approaches have addressed the issues of training speed \[21\], \[22\], \[23\] and large scene representation capacity \[24\], \[25\].

NeRF based SLAM has also achieved significant progress. iMAP \[26\] is the first method that incorporates NeRF technology into tracking and mapping. To improve scalability, NICE-SLAM \[4\] encodes maps with neural networks, avoiding the need for sparse feature matching and keypoint extraction required in traditional SLAM, thus achieving more robust and efficient mapping and localization. Recently, Point-SLAM \[27\] provids better 3D reconstruction by using neural point clouds and performing volume rendering with feature interpolation. However, the use of neural networks for implicit representation and rendering severely limits the improvement in runtime speed, making it difficult to meet real-time requirements.

### C. 3D Gaussian Splatting

Recently, 3D gaussian splatting \[28\] has shown tremendous potential in high-quality real-time 3D scene synthesis. Based on differentiable rendering techniques, 3DGS achieving state-of-the-art visual quality and fast high-resolution rendering performance. Owning to the explicit scene representation and speed advantages of 3DGS, it has great potential for application in SLAM. In recent months, SplaTAM \[29\] has achieved real-time localization and mapping with RGB-D data by introducing silhouette masks and optimizing camera poses. However, it does not implement a backward pass for depth. Gaussian splatting SLAM \[6\] claims to support both monocular and RGB-D data, but when depth information is lacking, it is difficult to track under large motion with photometric error. Moreover, the method inserts points at the average depth, and these noise points will cause the optimization to struggle. LIV-GaussMap \[30\] is the first LIV system based on 3DGS, but it does not make full use of depth, relying solely on color to optimize the scene, which affects the accuracy of localization and scene rendering.

In contrast, we propose a comprehensive differentiable renderer with Taichi \[31\], and fully utilize the backpropagation information from output depth, color, and intermediate variables such as pose. Moreover, it is the first general 3DGS mapping framework that supports multi-source data input.

As shown in Fig. 1, we uses gaussian points (Section III-A) as the scene representation, and derive a comprehensive differentiable depth and color (Section III-B). After different types of data input, the odometry provides an initial pose and sparse depth. For monocular, we propose a scale-consistent and uncertainty-weighted depth optimization method (Section III-C), which reduces the error estimation of depth prediction. Map-based re-optimization (Section III-D) improves the localization accuracy from the odometry, and then the frame is added to the scene. Our proposed scene updating (Section III-D) strategy effectively prevents rapid memory growth and enables rapid convergence. Scene and pose optimization (Section III-E) are performed alternately, achieving precise localization and synchronous high-fidelity map reconstruction.

**Fig. 1.**

**System overview.** Our method takes RGB/RGB-D/LIV data as input and outputs camera pose and scene representation. These input data first pass through a specific pre-tracking module to obtain the initial pose. If pre-tracking fails, the pose is initialized using the constant velocity assumption. For monocular systems, we also integrate a metric depth estimation module to provide initial depth information. We further improve the system performance by assigning pixel weights based on multi-view consistency. To achieve joint mapping and tracking, we render the predicted color and depth and alternately optimize the pose of the new frame and scene parameters.

### A. Gaussian Scene Representation

The advantags of gaussian scene representation include rapid rendering and convergence, as well as ease of modification. The entire scene is represented by $\mathcal {G}$, where each $G_{i}$ denotes the *i* -th gaussian point within the scene. Each gaussian point comprises four components: the position $\mathbf {P}_{i} \in \mathbb {R}^{3}$, the covariance matrix $\boldsymbol {\Sigma }_{i} \in \mathbb {R}^{3 \times 3}$, the opacity $\alpha _{i}$, and the color $\mathbf {c}_{i}$.

The set of cameras present in the scene is denoted by $\mathcal {K}$. Each camera frame ${\mathcal {K}}_{j}$ is defined by an intrinsic matrix $\mathbf {K}_{j} \in \mathbb {R}^{3 \times 3}$, which remains constant and known when the scene is captured by the same camera, and a transformation matrix $\mathbf {T}_{j} \in SE(3)$ that specifies the camera’s pose relative to the world coordinate system.

\\begin{align\*} \\mathcal {G} & = \\{{\\mathcal {G}}\_{i}:(\\mathbf {P}\_{i}, \\boldsymbol {\\Sigma }\_{i}, \\alpha \_{i},\\mathbf {c}\_{i})|i=1,\\ldots,n\\}, \\\\ \\mathcal {K} & = \\{{\\mathcal {K}}\_{j}:(\\mathbf {K}, \\mathbf {T\_{j}})| j=1,\\ldots,m\\}, \\tag {1}\\end{align\*}

View Sourceduring rendering, the 2D mean $\mathbf {\mu ^{\prime } }$ is derived from the pose $\mathbf {T}_{cw}$ and the projection

$\\pi $

. The 2D covariance $\mathbf {\Sigma ^{\prime } }$ follows a linear approximation \[32\] using Jacobian **J**. Opacity at $u_{i}$ is *a*. The overall projection process is shown in [Eq. (2)](#deqn2).

\\begin{align\*} \\mathbf {\\mu ^{\\prime }} = \\pi (\\mathbf {T}\_{cw}\\mathbf {P}), \\; \\mathbf {\\Sigma ^{\\prime }}=\\mathbf {JR}\_{cw}\\boldsymbol {\\Sigma } \\mathbf {R}\_{cw}^{T}\\mathbf {J}^{T}, \\; a\_{i} = f\_{exp}(\\mathbf {u\_{i}} | \\mathbf {\\mu \_{i}^{\\prime }}, \\mathbf {\\Sigma \_{i}^{\\prime }})\\alpha \_{i}. \\tag {2}\\end{align\*}

View Source

Given the mean $\mathbf {\mu ^{\prime } }$ and covariance $\mathbf {\Sigma ^{\prime } }$ on the 2D plane, the rendering process sequentially accumulates the color $c_{i}$, depth $d_{i}$, and opacity $a_{i}$ for each gaussian point indexed by *i* along the ray, based on their respective depth values. This results in the rendered color $\hat {C}$, depth $\hat {D}$, and opcacity $\hat {T}$. The rendering equations are shown in [Eq. (3)](#deqn3).

\\begin{align\*} w\_{i} & = \\prod \_{j=1}^{i-1} (1 - a\_{j}), \\quad \\hat {T} = \\sum \_{i=1}^{n} a\_{i} w\_{i}, \\\\ \\hat {C} & = \\sum \_{i=1}^{n} c\_{i} a\_{i} w\_{i}, \\quad \\hat {D} = \\sum \_{i=1}^{n} d\_{i} a\_{i} w\_{i}, \\tag {3}\\end{align\*}

View Sourcewhere $w_{i}$ represents the accumulated opacity. Leveraging these rendering equations, we extend the differentiable color rendering found in orignal 3DGS \[28\] to include differentiable rendering for depth and opacity. By incorporating depth constraints, we achieve stable pose estimation while ensuring the fidelity of the synthesized novel views.

### B. Differentiable Depth and Pose Optimization Analysis

PyTorch lacks an automatic differentiation mechanism for gaussian scene. The original 3DGS \[28\] derived and implemented the derivatives of color with respect to gaussian point attributes $\left ({{\textbf {P}, \Sigma , \alpha , c}}\right)$ using CUDA. We not only introduce differentiable depth to optimize gaussian point attributes but also derive an optimization method for camera pose parameters, achieving accurate depth rendering and online pose estimation.

Figure 2 illustrates the overall chain rule process, where $\mathbf {P_{c}}$ represents the mean of gaussian points in the camera coordinate system. The camera transformation matrix $\mathbf {T_{cw}}$ is expressed using a quaternion $\mathbf {q_{cw}}\in \mathbb {R}^{4}$ and a translation matrix $\mathbf {t_{cw}}\in \mathbb {R}^{3}$.

**Fig. 2.**

**Diagram of the chain rule for color and depth.** The paper \[28\] implements the orange part, and we add the blue part. The optimization of depth and pose allows us to incrementally add new frames while ensuring rapid convergence of the scene.

#### 1) Differentiable Depth:

We introduce dense depth information to constrain the scene for RGB-D and monocular. Depth information ensures the geometric consistency of the scene and provides improved guidance for camera pose estimation.

Initially, we examine the derivative of depth *D* in relation to the attributes of the gaussian points. This process involves the transformation of the gaussian point coordinates into the camera’s coordinate frame, followed by their subsequent projection onto the two-dimensional plane as delineated by [Eqs. (2)](#deqn2) and [(3)](#deqn3). Through this, the derivative of depth *D* concerning the gaussian point attributes is explicated in [Eq. (4)](#deqn4).

\\begin{align\*} \\frac {\\partial D}{\\partial \\mathbf {P}}& = \\frac {\\partial D}{\\partial a}\\frac {\\partial a}{\\partial \\mathbf {P}}+\\frac {\\partial D}{\\partial d}\\frac {\\partial d}{\\partial \\mathbf {P}}, \\\\ \\frac {\\partial D}{\\partial \\boldsymbol {\\Sigma }}& = \\frac {\\partial D}{\\partial a} \\frac {\\partial a}{\\partial \\boldsymbol {\\Sigma }}, \\\\ \\frac {\\partial D}{\\partial \\alpha }& = \\frac {\\partial D}{\\partial a} \\frac {\\partial a}{\\partial \\alpha }. \\tag {4}\\end{align\*}

View Source

Following the chain rule as illustrated in Fig. 2, we calculate the derivative of depth *D* with respect to the gaussian point attributes using [Eqs. (2)](#deqn2) and [(3)](#deqn3).

\\begin{align\*} \\frac {\\partial D}{\\partial a\_{i}} & = d\_{i}w\_{i}-\\frac {\\sum \_{j=i+1}^{n}d\_{j}a\_{j}w\_{i}}{1-a\_{i}}, \\\\ \\frac {\\partial D}{\\partial d\_{i}} & = a\_{i}w\_{i}, \\\\ \\frac {\\partial d\_{i}}{\\partial \\mathbf {P}\_{i}} & = \\mathbf {R}\_{cw}\[:,3\]. \\tag {5}\\end{align\*}

View Source

By iteratively applying these adjustments through gradient descent, the scene’s parameters can be fine-tuned to minimize the difference between the rendered and expected depth, improving the accuracy and realism of the rendered scene.

#### 2) Camera Pose Gradient:

For convenience, we differentiate rotation quaternion $\mathbf {q_{cw}}$ and translation $\mathbf {t_{cw}}$ separately rather than the transformation matrix $\mathbf {T_{cw}}$.

Let $\mathbf {q_{cw}} = [w,\mathbf {v}]$, and $\mathbf {q_{cw}}^{*}$ is the conjugate of the quaternion. $[\cdot]_{ \times }$ denotes the antisymmetric matrix. Then we have:

\\begin{align\*} \\frac {\\partial \\mathbf {P\_{c}}}{\\partial \\mathbf {q\_{cw}}} & = \\frac {\\partial \\mathbf {q\_{cw}}\\otimes \\mathbf {P}\\otimes \\mathbf {q\_{cw}}^{\*}}{\\partial \\mathbf {q}} \\\\ & = 2\[\\mathbf {J}\_{imag}| \\mathbf {J}\_{real}\] \\in \\mathbb {R}^{3 \\times 4}, \\tag {6}\\\\ \\frac {\\partial \\mathbf {P\_{c}}}{\\partial \\mathbf {t\_{cw}}} & = \\mathbf {I}\_{3} \\in \\mathbb {R}^{3 \\times 3}, \\tag {7}\\end{align\*}

View Sourcewhere $\mathbf {J}_{imag}=\mathbf {v}^{\top }\mathbf {P}\mathbf {I}_{3}+\mathbf {v}\mathbf {P}^{\top }-\mathbf {P}\mathbf {v}^{\top }-w[\mathbf {P}]_{ \times }, \mathbf {J}_{real} = w\mathbf {P}+\mathbf {v} \times \mathbf {P}$.

We fully derive the gradients in the rendering process, enabling us to optimize the scene’s parameters through gradient descent. In practice, we found that depth continuously reduces the opacity

$\\alpha $

of observed gaussian points, leading to incorrect deletions in the deletion step. Therefore, in our implementation, we empirically multiply the value of $\frac {\partial D}{\partial \alpha _{i}}$ by a coefficient of 1e-4 to mitigate the impact of depth on opacity.

### C. Monocular / RGB-D / LIV Preprocess

#### 1) Pre-Tracking:

The paper \[33\] proves that large pose mismatch will lead to failure pose registration for complex image signals. Existing end-to-end SLAM \[6\], \[29\], \[34\] often assumes constant velocity for initial pose, which is difficult to handle large baseline data. In our system, we implement a custom, simplified odometry to estimate the frame to frame relative pose. For monocular, a simply feature based pre-tracking process is designed to maintain a local map to ensure scale consistency in tracking. For LiDAR and RGB-D, we employ the Iterative Closest Point (ICP) algorithm to estimate the relative pose between scans.

This process primarily serves three functions. (a) It addre- sses the scale consistency problem in depth estimation, ensuring the dense addition of gaussians in monocular mode; (b) for LiDAR-Inertial-Visual data, it allows for quick preprocessing by employing IMU-based undistortion methods; (c) it provides a more accurate subsequent pose estimate compared to the constant velocity assumption, avoiding multi-layer downsampling. Even if it fails, the algorithm can still degrade to assuming constant velocity to continue optimizing the pose through photometric and geometric constraints.

#### 2) Monocular Initialization:

On mono case, the absence of depth information hinders the initialization of Gaussian points by 3DGS. However, our pre-tracking odometry process allows us to overcome this issue by integrating a monocular depth estimation algorithm. The sparse points maintained by the odometry ensure scale consistency across adjacent frames, allowing us to align the results of depth estimation to a consistent scale. If pre-tracking fails, the scale consistency is calculated using the median of the scene depth. To ensure scale drift is minimized during long-term tracking, we continuously update the pre-tracking poses with the pose optimization results from the 3DGS frame-to-map tracking.

#### 3) Uncertainty Assignment:

Even with sparse point alignment, there are still many erroneous points. To address this, depth uncertainty is proposed to be assigned to each pixel. During optimization, pixels with greater uncertainty are assigned less weight, and vice versa, thereby reducing the impact of erroneous points on optimization. For LiDAR data, the uncertainty is set to a fixed value, as the depth values of LiDAR data are usually accurate.

When a posed frame from odometry is received, we project the depth maps of nearby frames onto the current frame and calculate the depth discrepancies between the current frame and the reference frames.

\\begin{equation\*} \\sigma (\\mathbf {p}) = \\left \[{{ \\mathbf {T}\_{rc} \\cdot \\pi ^{-1}(\\mathbf {p}\_{c}, d\_{c}) }}\\right \]\_{z} - d\_{r}. \\tag {8}\\end{equation\*}

View Source

The pose of the current frame relative to the reference frame is denoted by $\mathbf {T_{rc}}$. The function $\pi ^{-1}$ reverses the projection process, while $d_{r}$ and $d_{c}$ represent the depths in the reference and current frames, respectively. Through this, we determine the depth uncertainty $\sigma (\mathbf {p})$ at a pixel **p**.

### D. Gaussian Scene Updating With Depth Prior

#### 1) Map-Based Tracking:

Fine-tune the pose obtained from the pre-tracking process will improve the accuracy. Once the pre-tracked pose is acquired, it is continuously refined by minimizing the discrepancy between color and depth. Typically, low opacity areas indicate incomplete initialization. We propose an opacity mask, refining only the regions with opacity greater than $a_{thres}$, to avoid the impact of uninitialized areas on the pose adjustment process. After the adjustment is complete, this updated pose is then used to enhance the pre-tracking process.

#### 2) Gaussian Addition:

SplaTAM and GS-SLAM \[29\], \[34\] directly add pixels with large differences between rendered and actual depth. This easily leads to non-convergence and memory overload when the depth values are inaccurate. We delve into the rendering pipeline and propose an efficient search for the gaussian scene $\mathcal {G}$, directly determining whether there is a gaussian point near the depth $D(\mathbf {p})$ during alpha-blending. If there is not, the pixel **p** will be unprojected and added to the scene. Otherwise, it will not be added to the scene. Additionally, we render an opacity map $\hat {T}$ based on the pose. Pixels **p** with opacity less than $a_{thres}$ and uncertainty less than $\sigma _{thres}$ are also added. Experiments on TUM-RGBD \[35\] and Replica \[36\] datasets show that this can reduce the number of gaussian points by $70 \; \sim \; 95$ % compared to SplaTAM \[29\], while ensuring the fidelity of the rendering.

\\begin{equation\*} D(\\mathbf {p}) \\notin \\left \\{{{\\mathcal {G}}}\\right \\} \\quad or \\quad \\hat {T}(\\mathbf {p}) \\lt a\_{thres} \\quad or \\quad \\sigma (\\mathbf {p}) \\lt \\sigma \_{thres}. \\tag {9}\\end{equation\*}

View Source

#### 3) Depth-Based Gaussian Initialization:

To accelerate the convergence of novel view, we initialize the gaussian point by leveraging dense depth data, constructing a kd-tree from the newly added 3D points, and applying SVD on neighbors to get eigenvalues

$\\lambda $

and eigenvectors

$\\xi $

. These are then used to initialize scale *s* and orientation **R**. The point’s color initializes the SH coefficients, and we set

$\\alpha $

to 0.5.

#### 4) Gaussian Deletion:

GS-SLAM \[34\] manually reduces the opacity of points based on the distance from the depth. In contrast, we directly use [Eq. (5)](#deqn5). Erroneous points that fail depth or color criteria will continuously diminish in opacity as observations proceed, which is more elegant. We delete points with opacity less than 0.1 every 200 frames. Through experiments, we find that depth constraints are highly effective in removing erroneous points.

### E. Optimization

Our proposed depth uncertainty $\sigma (\mathbf {p})$ enables us to control the weight of the loss function on a per-pixel basis. The Gaussian Negative Log Likelihood Loss (GNLL) possesses favorable properties, assigning greater weight where uncertainty is low, and vice versa. Hence, in conjunction with the depth uncertainty we propose, the depth and color loss at pixel **p** is shown in [Eqs. (10) and (11)](#deqn10-deqn11).

\\begin{align\*} {\\mathcal {L}}\_{\\mathrm {depth}}(\\mathbf {p}) & = \\log \\left ({{\\sigma (\\mathbf {p})^{2}}}\\right )+\\frac {\\left ({{\\hat {D}(\\mathbf {p})-D(\\mathbf {p})}}\\right )^{2}}{\\sigma (\\mathbf {p})^{2}}, \\tag {10}\\\\ {\\mathcal {L}}\_{\\mathrm {color}}(\\mathbf {p}) & = \\left \\|{{\\hat {C}(\\mathbf {p})-C(\\mathbf {p})}}\\right \\|\_{1}, \\tag {11}\\end{align\*}

View Source $\hat {C}$ and *C* represent the rendered color and the ground truth color, respectively, while $\hat {D}$ and *D* represent the rendered depth and the ground truth depth, respectively. ${\mathcal {L}}_{depth},{\mathcal {L}}_{color}$ are the loss corresponding to depth and color. Thus, the total loss for a pixel can be expressed as [Eq. (12)](#deqn12).

\\begin{equation\*} \\mathcal {L}(\\mathbf {p}) = (1 - \\lambda \_{s}){\\mathcal {L}}\_{color}(\\mathbf {p}) + \\lambda \_{s}{\\mathcal {L}}\_{ssim}(\\mathbf {p}) + \\lambda \_{d}{\\mathcal {L}}\_{depth}(\\mathbf {p}). \\tag {12}\\end{equation\*}

View Source

The total loss $\mathcal {L}(\mathbf {p})$ for a pixel **p** combines color loss ${\mathcal {L}}_{color}(\mathbf {p})$, structural similarity loss ${\mathcal {L}}_{ssim}(\mathbf {p})$, and depth loss ${\mathcal {L}}_{depth}(\mathbf {p})$. The weights $\lambda _{s}$ and $\lambda _{d}$ adjust the importance of structural similarity and depth accuracy, respectively.

We only taken valid pixels for account, as shown in [Eq. (13)](#deqn13). The symbol $\mathbb {I}$ represents an indicator function, which equals 1 when the condition in the parentheses is true, and 0 when it is false.

\\begin{equation\*} \\underset {\\mathcal {G}, \\mathcal {K}}{\\min } \\, \\mathcal {L} = \\sum \_{\\mathbf {p}}\\mathbb {I}(a\\gt a\_{thres})\\mathcal {L}(\\mathbf {p}). \\tag {13}\\end{equation\*}

View Source

Alternating optimization of the gaussian scene $\mathcal {G}$ and camera extrinsic $\mathcal {K}$ is employed to accounts for their mutual influence. Scene optimization is performed on randomly selected frames that are in proximity to each newly added frame.

### A. Experimental Setup

#### 1) Datasets and Evaluation Metrics:

We evaluate our method on three datasets: Replica \[36\], TUM-RGBD \[35\], and R3Live-Dataset \[41\]. We evaluate the rendering quality and localization accuracy.

The average absolute trajectory error (ATE, RMSE in \[cm\]) is utilized to evaluate the pose accuracy. The stability of localization is evaluated by reducing the frame overlap through selective frame decimation. The PSNR, SSIM and LPIPS \[42\] are employed to assess rendering performance. The number of gaussian points and runtime are used to evaluate the efficiency of reconstruction.

#### 2) Implementation Details:

Our differentiable renderer is implemented in the Taichi language \[31\], and the optimization is performed using the Adam optimizer with a learning rate of 1e-5. Our method runs on a desktop computer with an NVIDIA RTX 4090. We set $\alpha _{thres}$ to 0.1 and $\sigma _{thres}$ is set according to the depth range of the scene. For the TUM-RGBD \[35\] and Replica \[36\] datasets, we set it to 0.3.

### B. Evaluation of Localization

The TUM-RGBD dataset \[35\] is a challenging dataset due to the motion blur, low-textured RGB images, inferior depth sensor quality and extensive blank areas. Results in Table I demonstrate superior results when benchmarked against state-of-the-art SLAM techniques. In RGB-D case, our approach outperformed the Point-SLAM \[27\] and SplaTAM \[29\] methods, achieving a remarkable 64.6% reduction in trajectory error, decreasing from 3.42 cm to just 1.21 cm. Furthermore, when compared to the feature-based ORB-SLAM2 \[43\] method, our method achieved a substantial 38.9% decrease in trajectory error, from 1.98 cm to 1.21 cm.

**TABLE I** Camera Tracking Result on TUM-RGBD \[35\]. Our Method Achieves State-of-the-Art Results in Both Monocular and RGB-D Cases. Particularly, Our Method Also Outperforms Systems That Use Depth Priors in the Monocular Case. Best Results Are Highlighted as First

In the monocular case, we tested the DOIRD-SLAM (w/o loop-closure) \[16\], DSO \[40\], and GS-SLAM \[34\]. Our method also achieved the best results in the monocular case. Compared to the latest monocular gaussian-based SLAM, our method achieved a 30.27% reduction in trajectory error, decreasing from 3.7 cm to 2.58cm. Due to the proposed opacity mask and differentiable depth, our method is able to further optimize the pose based on the reconstructed scene under the initial pose provided by the odometry, achieving superior results compared to other methods.

To evaluate the robustness of our algorithm against images with low overlap, we incrementally increased the stride between images during our experiments. Figure 3 demonstrates that SplaTAM \[29\] struggles with tracking at low overlap, leading to a significant increase in ATE error, while our algorithm ensures stable convergence.

**Fig. 3.**

**Stride and Accuracy.** As the stride increases, the accuracy of SplaTAM decreases, while our method remains stable.

### C. Runtime Analysis

We compared the runtime performance of our method with that of SplaTAM \[29\] as shown in Table II. Our method outperformed SplaTAM on all three datasets, achieving an average improvement of 66.17%. The efficient performance comes from the stability of our method when adding new points and the initial value provided by the odometry, which requires less time to optimize the pose. Additionally, we provide a version that reduces the dimensions of SH to speed up the algorithm’s speed. While this entails a certain level of compromise in rendering accuracy, it has enabled rapid map construction.

**TABLE II** Time Consuming Per Frame. It Is Observable That Our Method Outperforms SplaTAM \[29\] in Terms of Speed. Additionally, We Provides an Accelerated Version With a Reduced SH Dimension, Which Reduces the Training Time by Half, Albeit With a Minor Sacrifice in Rendering Quality (~1.2 Decrease in PSNR on TUM)

### D. Rendering Evaluation

As shown in Table III, for the RGB-D scenario, we compare our method with SplaTAM \[29\], ESLAM \[44\], Point-SLAM \[27\], and NICE-SLAM \[4\]. It is important to note that Point-SLAM utilizes depth ground truth for sampling, which leads to an unfair comparison. Despite this, our method still surpasses the second-best method by 5.19dB ($\uparrow 15.2$ %) and 0.08 ($\uparrow 80$ %) in PSNR and LPIPS, but slightly decrease in SSIM ($\downarrow 2$ %).

**TABLE III** Rendering Performance on Replica \[36\] and TUM-RGBD \[35\]. We Evaluate NICE-SLAM \[4\], ESLAM \[44\], Point-SLAM \[27\], and SplaTAM \[29\] on the RGB-D Data. To Ensure Consistency With NICER-SLAM \[45\], We Use Novel View to Evaluate the Monocular Case. Best Results Are Highlighted as First, Second and Third

In the monocular case, to maintain consistency with prior work \[45\], we present the novel view synthesis performance. Our approach comprehensively outperforms NICER-SLAM \[45\] by 3.65 ($\uparrow 15.3$ %) in PSNR, 0.01 ($\uparrow 1.1$ %) in SSIM, and 0.02 ($\uparrow 75$ %) in LPIPS in novel view synthesis. This demonstrates that our method can achieve the best results in the monocular case, with the help of depth prediction priors.

As shown in Fig. 4, the latest gaussian-based SLAM method, SplaTAM \[29\], still has abnormal color points, blurry edges, and holes at the edges in the rendered results. Our method produces more realistic rendering results.

**Fig. 4.**

**RGB-D rendering results.** Although SplaTAM \[29\] is the most advanced gaussian-based SLAM method, there are still some flaws in its rendering results. These include abnormal color points, blurry edges, and holes at the edges. Our method produces more realistic rendering results.

This is because our scene update method only adds necessary points, thereby reducing the training load. On the other hand, SplaTAM \[29\] employs a more extensive point-adding strategy, which leads to an excessive training burden and results in renderings that are not as good as those produced by our method.

We test the performance of our method against the original 3DGS \[28\] method and two latest lidar-based gaussian splatting methods LVI-GS \[46\] and Gaussian-LIC \[47\] on three R3Live-Dataset \[41\] sequences: *deg 00*, *deg 01* and *campus 00*. Considering the sparsity of LiDAR data, we adjust our strategy for densifying points more aggressively. In the tests with the original 3DGS method, we use the fused LiDAR point clouds as the initial point cloud and the odometry as the initial poses. Figure 5 shows our rendering results, which clearly demonstrate that our method effectively fills the scene, producing more realistic rendering outcomes. Table V presents the quantitative results on the R3Live Dataset. Our approach maintains competitive performance even when compared to the latest LiDAR-specific methods such as LVI-GS \[46\] and Gaussian-LIC \[47\]. The subpar performance observed with 3DGS can be attributed to the accumulation of errors in the odometry poses, resulting in inconsistent observations. Conversely, our approach more accurately reconstructs the actual scene through the optimization of both poses and the scene.

**TABLE IV** Memory Comparison on Replica \[36\] and TUM-RGBD \[35\]. We Represent Memory Consumption by the Number of Points in the Scene \[In Millions\]. Our Method Achieves Better Results With Fewer Points

**TABLE V** Rendering Performance on R3Live-Dataset \[41\]. Our Method Has Achieved Competitive Results in PSNR, SSIM, and LPIPS Compared to the Latest LiDAR-Specific Gaussian Splatting methods \[46\], \[47\]

**Fig. 5.**

**Rendering results on R3Live-Dataset \[41\].** Our method surpasses the original 3DGS \[28\], which relies on fused LiDAR point clouds for initial data. It demonstrates a significant improvement in accurately depicting the real scene depth.

### E. Memory Comparison

SplaTAM \[29\], Gaussian Splatting SLAM \[6\] and GS-SLAM \[34\] add gaussian points according to the rendered depth and ground truth depth. Table IV indicates that this approach can lead to a rapid increase in memory usage, particularly with data exhibiting poor depth quality. The inconsistency in depth values tends to result in the continuous addition of points, making the parameters difficult to converge. Our rendering pipeline-oriented method only adds necessary points, avoiding the problem of memory overflow.

### F. Ablation Study

#### 1) View Synthesis:

As shown in Table VI, we evaluate the impact of different strategies on a TUM-RGBD sequence *fr1/desk*. The results show that no matter in novel view or train view, isotropic regularization leads to a decrease in fidelity, as scale regularization conflicts with color loss, reducing the efficiency of color constraints. In contrast, isotropic regularization has a positive impact on depth optimization, as it constrains the number of affected tiles, thereby benefiting depth optimization.

**TABLE VI** Ablation Study on View Synthesis. The Evaluation of Novel View Synthesis Is Conducted Using Ground Truth Poses. The Results Indicate That Isotropic Regularization Has a Negative Impact on Novel View Synthesis, While Depth Constraint Has a Positive Impact

Meanwhile, it can be observed that depth constraint has little impact on the fidelity of the training view, but significantly affects the fidelity of the novel view, as it eliminates depth ambiguity.

#### 2) Uncertainty & Depth Prediction & Pre-Tracking:

Table VIII examines the effects of depth prediction and the assignment of uncertainty on monocular scene optimization. We observe that scene optimization is substantially hindered by the absence of depth prediction, due to the difficulty of fulfilling the scene with only sparse points. Furthermore, by accounting for uncertainty, the problems caused by incorrect points in depth prediction are reduced.

**TABLE VII** Ablation Study on Scene Initialization

**TABLE VIII** Ablation Study on Monocular Uncertainty & Depth Prediction

Our photometric constraint frame-to-map optimization yields better accuracy than frame-to-frame pose optimization. If depth constraint is available, it is incorporated for potentially higher accuracy.

#### 3) Depth-Based Scene Initialization:

Scene initialization includes the initialization of the scale and rotation of the gaussian points. In the random initialization test, the random scale *S* is distributed according to $\mathcal {N}(0.05, 0.01)$. The random rotation is sampled uniformly in space according to the method in \[48\].

**TABLE IX** Ablation Study on RGB-D Localization Accuracy (ATE, RMSE in cm)

To evaluate the importance of scene initialization, the scene continues to be optimized even after all frames have been added, until the performance metrics stabilize. The efficiency gain from initialization is assessed by comparing the required number of iterations. Table VII displays the efficiency.

Generally, our initialization can converge faster and achieve better results. In particular, within the LiDAR dataset, an asterisk (\*) signifies ongoing optimization, indicating that the metrics are in the process of improvement and have not yet attained the performance benchmark set by our approach.

We propose G <sup>2</sup> -Mapping, a general gaussian-based mapping method that supports multi-source data input, offering a comprehensive differentiable renderer and a dynamically expandable gaussian scene representation. Our comparative analysis indicates that the proposed method not only achieves state-of-the-art results for monocular and RGB-D data in positioning accuracy and rendering quality but also shows promising applicability to LVI data. We believe that G <sup>2</sup> -Mapping sets a new benchmark for future research in scene representation and rendering, and open up a new avenue for general gaussian splatting based SLAM.

*Limitations:* When monocular tracking fails, the system relies on the median of scene depth to maintain scale consistency. On the other hand, the depth estimation module uses linear mapping to calculate depth values, which can result in errors and subsequently lead to inaccurate Gaussian point initialization. Sparse-guided depth completion presents a promising solution to this problem, as it leverages the sparse points to provide clues for the depth completion network, potentially improving accuracy.