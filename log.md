# Ingest Log

## 2026-05-07 — Initial ingest
- Ingested 4 papers from raw/papers/
- Created 12 concept pages in wiki/concepts/
- Created 4 paper pages in wiki/papers/
- Updated index.md

### Papers ingested
- [[papers/2026-05-07/3d-gaussian-splatting]] (3D Gaussian Splatting for Real-Time Radiance Field Rendering, SIGGRAPH 2023)
- [[papers/2026-05-07/mip-splatting]] (Mip-Splatting: Alias-free 3D Gaussian Splatting, CVPR 2024)
- [[papers/2026-05-07/gaussian-opacity-fields]] (Gaussian Opacity Fields, 2024)
- [[papers/2026-05-07/street-gaussians]] (Street Gaussians: Modeling Dynamic Urban Scenes with Gaussian Splatting, ECCV 2024)

### Concepts created
- [[concepts/3d-gaussian]], [[concepts/covariance-matrix]], [[concepts/spherical-harmonics]]
- [[concepts/projection-transform]], [[concepts/alpha-compositing]], [[concepts/tile-based-rasterization]]
- [[concepts/adaptive-density-control]], [[concepts/ssim-loss]]
- [[concepts/nerf]], [[concepts/instant-ngp]], [[concepts/mip-nerf]], [[concepts/tensorf]]

## 2026-05-12 — Ingest VGGT (deep read from PDF)
- Read [[papers/2026-05-09/vggt]] PDF in full detail (CVPR 2025 Best Paper, 20 pages)
- Rewrote paper page with complete methodology: problem definition, AA architecture, token design, all prediction heads, loss functions, training details, and all experimental results (Tables 1-10)
- Created 3 new concept pages:
  - [[concepts/point-map]] — per-pixel 3D world coordinate representation, key difference from depth map
  - [[concepts/alternating-attention]] — frame-wise + global self-attention alternating pattern
  - [[concepts/feed-forward-3d-reconstruction]] — paradigm shift from optimization-based to neural 3D reconstruction
- Updated [[concepts/structure-from-motion]] with links to new concepts
- Updated [[concepts/projection-transform]] with link to point-map
- Updated index.md (3 new concepts, new "Neural 3D Reconstruction" section)

## 2026-05-07 — Ingest Mobile-GS (deep read from PDF)
- Read [[papers/2026-05-07/mobile-gs]] PDF in full detail (ICLR 2026, 19 pages)
- Rewrote paper page with complete methodology, all mathematical formulations (Eq. 2-10), experimental results (Tables 1-8), and limitations
- Created new concept page: [[concepts/neural-view-dependent-enhancement]] (MLP-predicted view-dependent opacity)
- Updated concept pages with paper-specific details:
  - [[concepts/order-independent-rendering]] — added complete rendering formula (Eq. 2, 3), comparison with SortFreeGS, alpha blending vs OIR table
  - [[concepts/gaussian-compression]] — added NVQ sub-vector decomposition, SH feature decomposition (fd/fv), contribution-based pruning formulas (Eq. 7, 8), compression summary table
  - [[concepts/adaptive-density-control]] — added voting-based pruning mechanism with full formulas and parameters
  - [[concepts/alpha-compositing]] — added cross-link to neural view-dependent enhancement
- Updated [[papers/2026-05-07/3d-gaussian-splatting]] with new reference to Mobile-GS
- Updated index.md (fixed venue to ICLR 2026, added neural-view-dependent-enhancement)

## 2026-06-11 — Batch shallow ingest (13 papers)
- Processed 13 unlogged paper clips from raw/papers/
- Created 2 new paper pages: [[papers/2026-06-11/add-slam]], [[papers/2026-06-11/roger-slam]]
- Created 4 new concept stubs:
  - [[concepts/temporal-gaussian-model]] — time-varying Gaussians for dynamic objects
  - [[concepts/scene-consistency-analysis]] — prior-free dynamic detection via render-vs-observe comparison
  - [[concepts/language-feature-registration]] — direct CLIP-to-Gaussian embedding assignment
  - [[concepts/multi-sensor-fusion]] — unified monocular/RGB-D/LiDAR SLAM framework
- 11 papers already had wiki pages from prior runs (skipped overwrite): Proxy-GS, WildGS-SLAM, Pseudo Depth, LangGS-SLAM, LangSplat, Dr. Splat, G²-Mapping, GaussNav, UP-SLAM, ViMGS-SLAM, Zero-Shot UAV
- Generated [[output/待精读列表]] with priority rankings

### Papers ingested (shallow)
- [[papers/2026-06-11/add-slam]] (ADD-SLAM, arXiv 2025) — adaptive dynamic dense SLAM, scene consistency analysis + temporal Gaussian model
- [[papers/2026-06-11/roger-slam]] (RoGER-SLAM, arXiv 2025) — robust SLAM for noise/low-light, SP-RoFusion + CLIP enhancement
- [[papers/2026-05-21/proxy-gs]] (Proxy-GS, arXiv 2025) — occlusion-aware rendering via fast proxy system
- [[papers/2026-05-21/wildgs-slam]] (WildGS-SLAM, arXiv 2025) — uncertainty-aware dynamic SLAM with DINOv2
- [[papers/2026-05-21/pseudo-depth-meets-gaussian]] (Pseudo Depth, arXiv 2025) — feed-forward pose prediction, 90% faster tracking
- [[papers/2026-05-21/langgs-slam]] (LangGS-SLAM, arXiv 2026) — real-time language-feature SLAM, Top-K rendering
- [[papers/2026-05-07/langsplat]] (LangSplat, CVPR 2024) — 3D language Gaussian splatting, 199x faster than LERF
- [[papers/2026-05-08/dr-splat]] (Dr. Splat, arXiv 2025) — direct language embedding registration without rendering
- [[papers/2026-05-15/g2-mapping]] (G²-Mapping, IEEE 2025) — general multi-sensor 3DGS mapping framework
- [[papers/2026-05-28/gaussnav]] (GaussNav, TPAMI 2025) — visual navigation with 3DGS for IIN task
- [[papers/2026-06-02/up-slam]] (UP-SLAM, ICRA 2026) — parallel tracking-mapping, probabilistic octree, open-set dynamics
- [[papers/2026-06-08/vimgs-slam]] (ViMGS-SLAM, Array 2026) — multi-scale ViT monocular 3DGS SLAM
- [[papers/2026-06-10/zero-shot-uav-navigation]] (Zero-Shot UAV Nav, arXiv 2026) — relightable 3DGS + RL forest navigation

## 2026-06-11 — Deep read: ADD-SLAM
- Read ADD-SLAM in full detail from arXiv HTML (PDF encrypted, used raw .md clip with full paper content)
- Rewrote [[papers/2026-06-11/add-slam]] with complete methodology, math formulations (scene consistency analysis, MobileSAM segmentation, temporal Gaussian model, tracking/mapping losses), experimental results (Bonn ATE 2.77 cm, TUM ATE 1.25 cm, PSNR 22.41 dB), and limitations
- Upgraded 2 concept stubs → full pages:
  - [[concepts/temporal-gaussian-model]] — time-varying Gaussian representation for dynamic objects
  - [[concepts/scene-consistency-analysis]] — prior-free motion detection via render-vs-observe comparison
- ⚠️ Annotation skipped: PDF password-protected

## 2026-06-11 — Deep read: RoGER-SLAM (retry)
- Fetched full paper from arXiv HTML (2510.22600v1) via curl — PDF was encrypted
- Rewrote [[papers/2026-06-11/roger-slam]] with complete methodology (SP-RoFusion fusion, adaptive tracking with residual balancing, CLIP enhancement module), math formulations (Eq. 1-17), experimental results (Replica ATE 0.24 cm clean / 0.60 cm noise+low-light, 91% improvement over SplaTAM), and limitations
- Updated [[synthesis/dynamic-slam-comparison]] with RoGER-SLAM quantitative data table
- ⚠️ Annotation skipped: PDF still password-protected

## 2026-06-11 — Batch shallow ingest (3 papers, round 2)
- Processed 3 new unlogged paper clips from raw/papers/
- Created 3 new paper pages: [[papers/2026-06-11/tvg-slam]], [[papers/2026-06-11/taming-the-light]], [[papers/2026-06-11/varsplat]]
- Created 3 new concept stubs:
  - [[concepts/tri-view-geometric-constraints]] — three-view matching for robust cross-frame geometric constraints
  - [[concepts/intrinsic-appearance-normalization]] — disentangling albedo from transient lighting for illumination-invariant Gaussians
  - [[concepts/uncertainty-aware-tracking]] — per-pixel uncertainty map guiding tracking/submap registration/loop detection
- Updated index.md (new section: 鲁棒性与光照, 3 new concepts under 动态场景与鲁棒性)
- Updated [[output/待精读列表]] with 3 new papers + revised reading roadmap

### Papers ingested (shallow)
- [[papers/2026-06-11/tvg-slam]] (TVG-SLAM, arXiv 2025) — tri-view geometric constraints, RGB-only SLAM, 69% ATE reduction outdoor
- [[papers/2026-06-11/taming-the-light]] (Taming the Light, arXiv 2025) — IAN+DRB-Loss, illumination-invariant semantic SLAM
- [[papers/2026-06-11/varsplat]] (VarSplat, arXiv 2026) — per-splat variance, uncertainty-aware RGB-D SLAM

## 2026-06-11 — Deep read: Taming the Light
- Read Taming the Light from arXiv HTML (2511.22968v1) — full methodology and experiments
- Rewrote [[papers/2026-06-11/taming-the-light]] with complete methodology (IAN color quantization → 64-color palette, DRB-Loss SSIM-gated affine exposure compensation, illumination-invariant tracking with albedo matching), math formulations (Eq. 1-10), experimental results (Replica ATE 0.34 cm best, mIoU 92.69%), ablation (Full: Depth L1 0.25 vs Baseline 0.46), and limitations
- Upgraded [[concepts/intrinsic-appearance-normalization]] stub → full page with IAN vs SH comparison
- ⚠️ Annotation skipped: no annotate_pdf.py script found

## 2026-06-11 — Deep read: VarSplat
- Read VarSplat from arXiv HTML (2603.09673v1) — 8 pages, full methodology and experiments
- Rewrote [[papers/2026-06-11/varsplat]] with complete methodology (law of total variance derivation, variance learning via Gaussian NLL, median-centered log scaling, 3-level uncertainty-guided pose estimation), math formulations (Eq. 1-19), experimental results (Replica ATE 0.23 cm, ScanNet++ 1.69 cm, TUM 3.20 cm), and limitations
- Upgraded [[concepts/uncertainty-aware-tracking]] stub → full page with 3 implementation schemes comparison
- ⚠️ Annotation skipped: no annotate_pdf.py script found

## 2026-06-11 — Deep read: TVG-SLAM
- Read TVG-SLAM from arXiv HTML (2510.21135v1) — 507KB dense MathML, used Python extraction to get plain text
- Rewrote [[papers/2026-06-11/tvg-slam]] with complete methodology (DUST3R dense tri-view matching → Hybrid Geometric Tracking with photometric+trifocal 2D+3D alignment, DART sigmoid photometric weight decay, TUGI variance-guided Gaussian initialization with opacity attenuation), math formulations (Eq. 1-9), experimental results across 3 outdoor datasets (Waymo ATE 0.602, Small City ATE 1.195, Cambridge ATE 2.009 — 69% reduction vs OpenGS-SLAM), ablation (TUGI removal +38.3% ATE, DART +21.0%), and limitations
- Upgraded [[concepts/tri-view-geometric-constraints]] stub → full page with trifocal tensor details, vs pairwise geometry comparison table, TUGI uncertainty estimation formula
- ⚠️ Annotation skipped: no annotate_pdf.py script found

## 2026-06-11 — Cross-paper synthesis
- Created [[synthesis/dynamic-slam-comparison]] comparing 3 papers addressing dynamic/robust 3DGS-SLAM
- Created [[synthesis/robustness-dimensions]] — orthogonal robustness taxonomy (measurement/illumination/geometry) across VarSplat, Taming the Light, TVG-SLAM with combination matrix and unified uncertainty perspective
