# mo2023 — data provenance

Source card: `docs/cards/mo2023.md` (ROADMAP item 0.4). Calibration-provider
(P6 Forchheimer priors); **no runtime component**.

**Origin:** Mo, Johnston, Navarini, Suggi Liverani & Ellero, *"Exploring the link
between coffee matrix microstructure and flow properties..."* **arXiv:2305.03911v2
(2023)** — no journal DOI on the preprint. microCT (16.8 µm voxels) of four illy
capsule beds (types E/H/M/F) + SPH percolation. Figures/tables digitized by Tim.

## Files
| file | source | content |
|---|---|---|
| `table1_laser_diffraction.csv` | Table 1 | PSD per type (uniformity, specific surface, d32, d43, %<100 µm). |
| `table{2,3,4,5}_type{H,E,M,F}_samples.csv` | Tables 2–5 | 6 microCT samples each: location, porosity, tortuosity, kD (Darcy), kF (Forchheimer), k1F (inertial). **24 real-geometry (k, k₁) pairs.** |
| `fig8a_permeability_vs_pressure_gradient.csv` | Fig 8a | apparent Darcy kD vs ∇P (Darcy→Forchheimer decline). |

## ⚠ k₁ UNITS CAVEAT (§5.3) — mandatory
Forchheimer Eq. 2 (∇P = −(µ/k)q − (ρ/k₁)|q|q) requires **[k₁] = m** (length), but
the Table 2–5 headers give k₁F in **1e-9 m²**, and the Fig 8b annotation reads
2.17e-13 for the sample the table lists as 4.21e-9 — **internally inconsistent by
~1e4**. **Do NOT use k₁ quantitatively** until resolved (against a standard
β = ρ/k₁ form; author correspondence pending, §5.8). kD, porosity, tortuosity,
and Fig 8a are safe to use.

## Validation strength
- Re band **0.84–3.86** reproduced from Fig 8a at Mo's SPH water properties
  (µ=1e-3, ρ=1000, char. length d43=341.6 µm) — see `gate_mo_reynolds_overlay`.
  Per §5.2 this Re is **NOT interchangeable** with wadsworth's Fo_F.
- Segmentation is **circular for absolute porosity** (threshold set to reproduce
  ε=0.17 from literature incl. Cameron). SPH k is compared to literature only —
  no flow measurement on the same capsules → no direct quantitative k validation.
