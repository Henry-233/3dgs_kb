# Ingest Log

## 2026-05-07 — Initial ingest
- Ingested 4 papers from raw/papers/
- Created 12 concept pages in wiki/concepts/
- Created 4 paper pages in wiki/papers/
- Updated index.md

### Papers ingested
- [[papers/3d-gaussian-splatting]] (3D Gaussian Splatting for Real-Time Radiance Field Rendering, SIGGRAPH 2023)
- [[papers/mip-splatting]] (Mip-Splatting: Alias-free 3D Gaussian Splatting, CVPR 2024)
- [[papers/gaussian-opacity-fields]] (Gaussian Opacity Fields, 2024)
- [[papers/street-gaussians]] (Street Gaussians: Modeling Dynamic Urban Scenes with Gaussian Splatting, ECCV 2024)

### Concepts created
- [[concepts/3d-gaussian]], [[concepts/covariance-matrix]], [[concepts/spherical-harmonics]]
- [[concepts/projection-transform]], [[concepts/alpha-compositing]], [[concepts/tile-based-rasterization]]
- [[concepts/adaptive-density-control]], [[concepts/ssim-loss]]
- [[concepts/nerf]], [[concepts/instant-ngp]], [[concepts/mip-nerf]], [[concepts/tensorf]]

## 2026-05-12 — Ingest VGGT (deep read from PDF)
- Read [[papers/vggt]] PDF in full detail (CVPR 2025 Best Paper, 20 pages)
- Rewrote paper page with complete methodology: problem definition, AA architecture, token design, all prediction heads, loss functions, training details, and all experimental results (Tables 1-10)
- Created 3 new concept pages:
  - [[concepts/point-map]] — per-pixel 3D world coordinate representation, key difference from depth map
  - [[concepts/alternating-attention]] — frame-wise + global self-attention alternating pattern
  - [[concepts/feed-forward-3d-reconstruction]] — paradigm shift from optimization-based to neural 3D reconstruction
- Updated [[concepts/structure-from-motion]] with links to new concepts
- Updated [[concepts/projection-transform]] with link to point-map
- Updated index.md (3 new concepts, new "Neural 3D Reconstruction" section)

## 2026-05-07 — Ingest Mobile-GS (deep read from PDF)
- Read [[papers/mobile-gs]] PDF in full detail (ICLR 2026, 19 pages)
- Rewrote paper page with complete methodology, all mathematical formulations (Eq. 2-10), experimental results (Tables 1-8), and limitations
- Created new concept page: [[concepts/neural-view-dependent-enhancement]] (MLP-predicted view-dependent opacity)
- Updated concept pages with paper-specific details:
  - [[concepts/order-independent-rendering]] — added complete rendering formula (Eq. 2, 3), comparison with SortFreeGS, alpha blending vs OIR table
  - [[concepts/gaussian-compression]] — added NVQ sub-vector decomposition, SH feature decomposition (fd/fv), contribution-based pruning formulas (Eq. 7, 8), compression summary table
  - [[concepts/adaptive-density-control]] — added voting-based pruning mechanism with full formulas and parameters
  - [[concepts/alpha-compositing]] — added cross-link to neural view-dependent enhancement
- Updated [[papers/3d-gaussian-splatting]] with new reference to Mobile-GS
- Updated index.md (fixed venue to ICLR 2026, added neural-view-dependent-enhancement)

## 2026-06-11 — Batch shallow ingest (13 papers)
- Processed 13 unlogged paper clips from raw/papers/
- Created 2 new paper pages: [[papers/add-slam]], [[papers/roger-slam]]
- Created 4 new concept stubs:
  - [[concepts/temporal-gaussian-model]] — time-varying Gaussians for dynamic objects
  - [[concepts/scene-consistency-analysis]] — prior-free dynamic detection via render-vs-observe comparison
  - [[concepts/language-feature-registration]] — direct CLIP-to-Gaussian embedding assignment
  - [[concepts/multi-sensor-fusion]] — unified monocular/RGB-D/LiDAR SLAM framework
- 11 papers already had wiki pages from prior runs (skipped overwrite): Proxy-GS, WildGS-SLAM, Pseudo Depth, LangGS-SLAM, LangSplat, Dr. Splat, G²-Mapping, GaussNav, UP-SLAM, ViMGS-SLAM, Zero-Shot UAV
- Generated [[output/待精读列表]] with priority rankings

### Papers ingested (shallow)
- [[papers/add-slam]] (ADD-SLAM, arXiv 2025) — adaptive dynamic dense SLAM, scene consistency analysis + temporal Gaussian model
- [[papers/roger-slam]] (RoGER-SLAM, arXiv 2025) — robust SLAM for noise/low-light, SP-RoFusion + CLIP enhancement
- [[papers/proxy-gs]] (Proxy-GS, arXiv 2025) — occlusion-aware rendering via fast proxy system
- [[papers/wildgs-slam]] (WildGS-SLAM, arXiv 2025) — uncertainty-aware dynamic SLAM with DINOv2
- [[papers/pseudo-depth-meets-gaussian]] (Pseudo Depth, arXiv 2025) — feed-forward pose prediction, 90% faster tracking
- [[papers/langgs-slam]] (LangGS-SLAM, arXiv 2026) — real-time language-feature SLAM, Top-K rendering
- [[papers/langsplat]] (LangSplat, CVPR 2024) — 3D language Gaussian splatting, 199x faster than LERF
- [[papers/dr-splat]] (Dr. Splat, arXiv 2025) — direct language embedding registration without rendering
- [[papers/g2-mapping]] (G²-Mapping, IEEE 2025) — general multi-sensor 3DGS mapping framework
- [[papers/gaussnav]] (GaussNav, TPAMI 2025) — visual navigation with 3DGS for IIN task
- [[papers/up-slam]] (UP-SLAM, ICRA 2026) — parallel tracking-mapping, probabilistic octree, open-set dynamics
- [[papers/vimgs-slam]] (ViMGS-SLAM, Array 2026) — multi-scale ViT monocular 3DGS SLAM
- [[papers/zero-shot-uav-navigation]] (Zero-Shot UAV Nav, arXiv 2026) — relightable 3DGS + RL forest navigation

## 2026-06-11 — Deep read: ADD-SLAM
- Read ADD-SLAM in full detail from arXiv HTML (PDF encrypted, used raw .md clip with full paper content)
- Rewrote [[papers/add-slam]] with complete methodology, math formulations (scene consistency analysis, MobileSAM segmentation, temporal Gaussian model, tracking/mapping losses), experimental results (Bonn ATE 2.77 cm, TUM ATE 1.25 cm, PSNR 22.41 dB), and limitations
- Upgraded 2 concept stubs → full pages:
  - [[concepts/temporal-gaussian-model]] — time-varying Gaussian representation for dynamic objects
  - [[concepts/scene-consistency-analysis]] — prior-free motion detection via render-vs-observe comparison
- ⚠️ Annotation skipped: PDF password-protected

## 2026-06-11 — Deep read: RoGER-SLAM
- ⚠️ PDF加密无法读取 — PDF is password-protected, raw .md clip is abstract-only (35 lines)
- Paper page remains at status: skimmed, pending unprotected PDF acquisition

## 2026-06-11 — Cross-paper synthesis
- Created [[synthesis/dynamic-slam-comparison]] comparing 3 papers addressing dynamic/robust 3DGS-SLAM
