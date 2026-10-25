# mo2023 — data provenance

Source card: `docs/cards/mo2023.md` (ROADMAP item 0.4). Calibration-provider
(P6 Forchheimer priors); **no runtime component**.

**Origin:** Mo, Johnston, Navarini, Suggi Liverani & Ellero, *"Exploring the link
between coffee matrix microstructure and flow properties..."* **arXiv:2305.03911v2
(2023)** — original intake lineage retained. The final article is *Scientific
Reports* **13, 16374 (29 September 2023)**, DOI
[10.1038/s41598-023-42380-y](https://doi.org/10.1038/s41598-023-42380-y).
arXiv v1 was submitted 6 May 2023; v2 was posted 8 October 2023, after publication.
Final text controls the new profile analysis; matching geometry does not imply
identical method wording across versions. microCT (16.8 µm voxels) of four illy
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
and Fig 8a retain their existing source-conditioned uses and historical evidence labels; this does not authorize interpreting wet segmented profiles as intrinsic geometric porosity.

## Validation strength
- Re band **0.84–3.86** reproduced from Fig 8a at Mo's SPH water properties
  (µ=1e-3, ρ=1000, char. length d43=341.6 µm) — see `gate_mo_reynolds_overlay`.
  Per §5.2 this Re is **NOT interchangeable** with wadsworth's Fo_F.
- Segmentation is **circular for absolute porosity** (threshold set to reproduce
  ε=0.17 from literature incl. Cameron). SPH k is compared to literature only —
  no flow measurement on the same capsules → no direct quantitative k validation.

## Figure 14/16 segmented-profile intake (2026-10-24)

Stable dataset ID: `mo2023/fig14_fig16_segmented_profiles`.
`fig14_fig16_segmented_profiles.csv` retains 12,494 native straight segments,
original subpaths/orientation and visible/legend-occluded/axis-clipped portions.
`fig14_fig16_profile_metadata.json` owns per-panel calibration, stroke widths,
PDF clip/legend rectangles, versions, URLs and SHA-256 identities. Hidden path
coordinates are AUDIT_ONLY, excluded from displayed-evidence means and bounds.
No raw voxels or CT slices are reconstructed. Existing tables and Figure 8a are unchanged.

Final PDF pp.12/13: 14a medium/pre; 14b medium/three-days-post;
16a dark/pre; 16b dark/immediate-post. Each shows six annular-region radial
labels, 0.92, 2.77, 4.61, 6.45, 8.30, 10.14 mm. Twenty-four profiles represent
two capsule histories, not independent extractions or point/radially weighted
whole-bed observations. ArXiv v2 pp.14/15 geometry matches within production
rounding and is counted once. Figure 6 is context only.

The canonical ordinate is `published_segmented_signal`; native epsilon and
“porosity” are metadata. y increases bottom/outlet toward top/inlet. Dry threshold
selection matches reference porosity 0.17; wet threshold selection uses the
midpoint between grayscale histogram peaks. Wet liquid/solid distinction is
inadequate. Graphical reading allowances do not quantify segmentation sensitivity,
measurement error, repeatability or physical variability. Roast/capsule/delay are
confounded; printed-coordinate pre/post contrasts do not establish material
registration or a common operator.

Rights: Mo, Johnston, Navarini, Suggi Liverani & Ellero (2023), final article
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Figures 14/16 and their
captions carry no third-party credit-line exception. Retained source crops are
rendered/cropped derivatives; canonical transcriptions, masks and the comparison
figure are modified/redrawn derivatives with attribution. Source PDFs remain
external. This grant is distinct from repository software MIT terms.

The final supplement was retrieved and inspected (seven pages of SPH methods
and enlarged sections); 1-hour and 24-hour scan mentions remain narrative-only.
See [source identities and extraction](../../../docs/analysis/sci_md_mo_wet_ct_profiles_001/SOURCE_NOTES.md),
[frozen plan](../../../docs/analysis/sci_md_mo_wet_ct_profiles_001/PLAN.md) and
[all 48 results](../../../docs/analysis/sci_md_mo_wet_ct_profiles_001/RESULT.md).
Eligible: retrospective descriptive displayed-signal spatial contrasts and
printed-coordinate contrast differences under the retained contract. Blocked:
intrinsic porosity ordering/change, permeability conversion, independent
replication, mechanism validation and unqualified evolving-bed calibration.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. SCI-MD-MO-TRANSFER-001 remains separate.
