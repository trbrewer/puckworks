# PW-COR15-SHAPE-001 — frozen D0 shape comparison

G1 / SOURCE_INTERNAL / TARGET_EXPOSED / DESCRIPTIVE / PHYSICAL_VALIDATION=NOT_ESTABLISHED

**FA loses to L0 in all 12 series: pooled D=0.06868 [0.06732, 0.07004].** Positive favors L0. Both have **one amplitude per series** (12 fits each). D uses fixed central S². Intervals: central 95% of 4096 paired reading realizations with shared panel calibration, **not population confidence intervals**.

RMSE and lowest-pressure residual (predicted−observed): **mL/s = 10⁻⁶ m³/s**. Every contrast uses matched observations.

| Series (grind–kg/m³) | RMSE L0 / FA | Lowest residual L0 / FA | Data m / FA-grid m_FA | Paired contrast [reading interval] |
|---|---:|---:|---:|---:|
| A-360 | 0.393 / 1.415 | -0.302 / -1.084 | 0.790 / 1.715 | 0.0712 [0.0683, 0.0742] |
| B-360 | 0.466 / 2.066 | -0.408 / -1.552 | 0.815 / 1.863 | 0.0794 [0.0765, 0.0824] |
| C-360 | 0.185 / 2.593 | 0.150 / -1.287 | 1.013 / 2.164 | 0.0685 [0.0640, 0.0729] |
| D-360 | 0.264 / 2.794 | 0.380 / -1.515 | 1.069 / 2.270 | 0.0651 [0.0597, 0.0707] |
| A-400 | 0.344 / 0.945 | -0.110 / -0.594 | 0.736 / 1.614 | 0.0698 [0.0660, 0.0735] |
| B-400 | 0.398 / 1.760 | -0.180 / -1.186 | 0.831 / 1.800 | 0.0724 [0.0696, 0.0753] |
| C-400 | 0.411 / 2.369 | -0.393 / -1.732 | 0.855 / 1.959 | 0.0796 [0.0762, 0.0830] |
| D-400 | 0.832 / 1.942 | 0.864 / -1.351 | 1.279 / 2.180 | 0.0288 [0.0242, 0.0333] |
| A-480 | 0.149 / 0.428 | -0.189 / -0.685 | 0.741 / 1.529 | 0.0440 [0.0387, 0.0493] |
| B-480 | 0.376 / 0.862 | 0.116 / -0.284 | 0.698 / 1.593 | 0.0751 [0.0710, 0.0795] |
| C-480 | 0.486 / 1.180 | -0.472 / -1.004 | 0.660 / 1.629 | 0.0806 [0.0772, 0.0841] |
| D-480 | 0.658 / 1.596 | -0.635 / -1.323 | 0.645 / 1.688 | 0.0899 [0.0869, 0.0929] |

Outcome: resolved curvature in the declared graphical-reading analysis, predominantly sub-linear. The L2 exponent interval lies below 1 in nine series, above 1 in D-360 and D-400, and includes 1 in C-360. Frozen D0 has higher RMSE than L0 in all twelve series, and every paired m−m_FA reading interval is negative. This establishes failure of the specified shape transfer under the declared mapping, not absence of all low-pressure suppression or identification of a fresh-bed mechanism. Experimental spread, instrument/correction uncertainty and descending-sweep history remain separate qualifications.

**Diagnostics (two parameters each):** L1 P0=−0.906 to +0.254 bar (nine negative offsets). L1/L2 contain L0: lower residual alone establishes no new law. No boundary fits; one central minimum per scalar profile.

FA-S's Pstar = 1.0–3.0 bar is compensation within the restricted function (n, Pd frozen), not an identified compaction scale. FA-S fits worse than L0 in 11/12 and worse than L2 in 12/12 series (central RMSEs).

**Qualifications:** 108 means; three beds/series. A-480 has seven markers (lowest 1.412 bar); C/D-360 have ten despite nine described steps. No bed trajectories reconstructed. SD, reading and instrument/correction uncertainty remain separate. Recovery absorbed into amplitude, pressure-coordinate substitution, descending-sweep history and unverified thesis-calibration reuse limit transfer.

The 64–96% lowest-point underprediction is not a common-pressure comparison: A-480's lowest retained point is about 1.41 bar; the others 0.23–0.42 bar.

**Table 2:** The inverse-normalization check gives plausible implied-viscosity magnitudes, but absolute permeability reconstruction remains unresolved. Support for the digitization comes from the marker overlay, axis checks and recorded coordinates, rather than this inverse calculation.

[Figure](comparison.svg) · [readings/SD](DIGITIZED.csv) · [fits/units](MODELS.csv) · [signed residuals](RESIDUALS.csv) · [dimensional contrasts](PAIRED_DIMENSIONAL.csv) · [D/exponents](CONTRASTS.csv) · [Table 2](TABLE2_CHECK.csv) · [source qualifications](SOURCE_RECONCILIATION.md) · [verification](VERIFICATION.md).
