# PW-CUP-TIME-INCREMENT-001 — fixed-mass prefix TDS

**11 shots; M*=19.8 g. A0 RMSE 0.701 pp (95% bootstrap [0.458, 1.004]); A1 0.796 pp ([0.487, 1.456]). Δ=+0.095 pp ([-0.039, 0.566]): prediction difference unresolved.** The point direction is an error increase. This Δ statement answers the prediction question.

| Shot | t(M*) s | C(M*) TDS pp | A0 error pp | A1 error pp |
|---|---:|---:|---:|---:|
| 1 | 31.957 | 12.820 | -0.288 | -0.329 |
| 2 | 28.134 | 13.807 | +0.798 | +0.836 |
| 3 | 22.565 | 14.317 | +1.359 | +1.632 |
| 4 | 28.194 | 13.651 | +0.626 | +0.661 |
| 5 | 27.106 | 12.333 | -0.824 | -0.821 |
| 7 | 25.596 | 12.412 | -0.737 | -0.752 |
| 8 | 24.813 | 13.195 | +0.124 | +0.112 |
| 9 | 21.136 | 12.613 | -0.516 | -0.919 |
| 10 | 27.054 | 13.353 | +0.298 | +0.304 |
| 11 | 26.014 | 12.246 | -0.919 | -0.926 |
| 12 | 30.653 | 13.152 | +0.078 | +0.135 |

Errors are observed minus held-out prediction. Original physical-block IDs; mass is 19.8 g for every row. [All endpoints](observations.csv) · [fold coefficients, predictions and influence](folds.csv).

**Duration association: unresolved.** β=-0.221 pp per unit ln(t/20 s), 95% bootstrap [-3.839, 3.876]. Implied change over 21.136–31.957 s: -0.091 pp [-1.587, 1.602]. **DESCRIPTIVE_ALL (in-sample):** Student-t 95% β interval [-4.366, 3.925], 9 df; it does not determine the reporting vocabulary.

| Sensitivity | A0 / A1 RMSE pp | Δ pp [95% bootstrap] | β [95% bootstrap] |
|---|---:|---:|---:|
| Timing u² | 0.701 / 0.796 | +0.095 [-0.033, 0.551] | -0.224 [-3.796, 3.771] |
| Timing √u | 0.701 / 0.793 | +0.092 [-0.046, 0.533] | -0.063 [-3.893, 4.086] |
| Conserving interpolation | 0.704 / 0.799 | +0.095 [-0.038, 0.568] | -0.268 [-3.913, 3.862] |
| 9.90 g | 1.079 / 1.191 | +0.112 [-0.203, 0.789] | +1.414 [-4.160, 6.426] |
| 14.85 g | 0.875 / 0.996 | +0.121 [-0.079, 0.674] | +0.294 [-4.520, 4.913] |

Each sensitivity refits training shots separately; no families are combined. Secondary endpoints reuse all 11 shots; agreement is not independent confirmation.

**Uncertainty/influence:** 2,000 bootstrap and 2,000 permutation draws per variant; 0 variant-draws have an unfit slope fold. Primary Δ/β intervals use 2000/2000 defined draws. Observed primary Δ is at the 78.65th percentile of duration-shuffled Δ (descriptive). A1 improves 2/11 shots; maximum A1 leverage 0.436; fold β range [-1.625, 1.549]; paired squared-error difference range [-0.004, 0.815] pp². All finite-only interval denominators, failure counts and ranges are in [summaries.csv](summaries.csv); all requested draws are retained.

The primary increase in held-out squared error is concentrated in the two fastest shots: shot 9 (21.136 s, 12.613% TDS) and shot 3 (22.565 s, 14.317% TDS) contribute +0.578 and +0.815 pp², together 88.9% of the total +1.568 pp² increase over A0. Omitting shot 9 makes the all-shot slope more negative, from beta -0.221 to -1.625; omitting shot 3 changes it to +1.549. Every other shot's paired squared-error difference has absolute magnitude below 0.062 pp².

Retrospective conditional prediction, not a fixed-grind experiment: EK43 2.85–3.1 varies and is not recorded per shot; the thesis excludes channelled/clogged shots. A resolved β alone does not establish improved held-out prediction; neither result identifies a causal mechanism. An interval including zero establishes neither negligible sensitivity nor equivalence. EY at fixed mass/nominal dose rescales TDS, adding no separate evidence. Intervals omit shared calibration and other unmodelled errors; no gates, pass/fail grades, or independent-campaign claim.

[Plan](PLAN.md) · [plots](primary.png) · [sensitivity intervals](sensitivities.png) · [draw distributions](uncertainty.png) · [CPU/execution](EXECUTION.json) · [QA](QA.json). EWP untouched; PR remains draft/unmerged.

Attribution: **Dr. Yoana Grudeva**, [espresso-model@567ad8f3808eb74fbe3e470eaa333161bf2eac1c](https://github.com/YoanaGrudeva/espresso-model/tree/567ad8f3808eb74fbe3e470eaa333161bf2eac1c); [permission](../../permissions/grudeva2025.md): **PERMISSION_DOCUMENTED; no SPDX licence; not relicensed under MIT**. No Pocket Science-derived data.
