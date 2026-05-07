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
