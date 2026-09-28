# SCI-VAL-TAMPED-K-001 result

**CONSOLIDATED_INPUT_PRIOR_FAILS_DECLARED_SCREEN**

Tested object: unchanged Wadsworth law plus the frozen Sauter-radius / bulk-porosity adapter.
TARGET_EXPOSED_RETROSPECTIVE_COMPARISON; G1; NO_GOVERNING_PHYSICS_CHANGE.

Coverage: 12 intended, 12 qualified, 12 scored triplicate summaries from one campaign.
The new permissive mean-level screen requires all twelve ratio intervals within [0.5, 2.0].
Reading/rounding intervals and reported SDs are not confidence intervals.

Case counts: {'FAIL': 7, 'PASS': 4, 'UNRESOLVED_AT_DECLARED_INPUT_PRECISION': 1}.

| Case | K mean ± SD (m²) | Primary K [reading bounds] (m²) | Ratio [bounds] | ln ratio | Decision |
|---|---|---|---|---|---|
| A-360 | 7.65e-14 ± 8.2e-15 | 1.1134e-13 [1.0066e-13, 1.2291e-13] | 1.4555 [1.3150, 1.6077] | 0.37534 | PASS |
| A-400 | 4.94e-14 ± 3.2e-15 | 6.381e-14 [5.6971e-14, 7.1283e-14] | 1.2917 [1.1521, 1.4444] | 0.25596 | PASS |
| A-480 | 2.59e-14 ± 2.5e-15 | 2.1376e-14 [1.8522e-14, 2.4565e-14] | 0.8253 [0.7138, 0.9503] | -0.19197 | PASS |
| B-360 | 1.37e-13 ± 8e-15 | 4.89e-13 [4.5117e-13, 5.2935e-13] | 3.5694 [3.2812, 3.8780] | 1.27239 | FAIL |
| B-400 | 1.18e-13 ± 9e-15 | 2.1574e-13 [1.9617e-13, 2.3684e-13] | 1.8283 [1.6554, 2.0157] | 0.60340 | UNRESOLVED_AT_DECLARED_INPUT_PRECISION |
| B-480 | 4.87e-14 ± 9e-16 | 5.2024e-14 [4.5758e-14, 5.8949e-14] | 1.0683 [0.9386, 1.2117] | 0.06603 | PASS |
| C-360 | 2.39e-13 ± 4.9e-14 | 2.0292e-12 [1.9054e-12, 2.1596e-12] | 8.4905 [7.9557, 9.0548] | 2.13895 | FAIL |
| C-400 | 1.93e-13 ± 1e-14 | 1.1264e-12 [1.0498e-12, 1.2075e-12] | 5.8365 [5.4254, 6.2728] | 1.76412 | FAIL |
| C-480 | 6.44e-14 ± 3.5e-15 | 2.654e-13 [2.4156e-13, 2.9107e-13] | 4.1211 [3.7480, 4.5233] | 1.41612 | FAIL |
| D-360 | 3.36e-13 ± 5.8e-14 | 5.1328e-12 [4.8567e-12, 5.4217e-12] | 15.2761 [14.4329, 16.1600] | 2.72629 | FAIL |
| D-400 | 4.38e-13 ± 4e-14 | 4.7357e-12 [4.4774e-12, 5.0061e-12] | 10.8120 [10.2106, 11.4425] | 2.38066 | FAIL |
| D-480 | 8.95e-14 ± 7.5e-15 | 1.1649e-12 [1.0829e-12, 1.2518e-12] | 13.0155 [12.0929, 13.9942] | 2.56614 | FAIL |

Every case is QUALIFIED_DECLARED_ADAPTER_INPUT, with SAUTER_RADIUS_PROXY, BULK_POROSITY_PROXY,
READING_BOUNDS_ONLY and SHARED_INPUT_DEPENDENCE flags. Machine-readable result.json retains both arms,
all per-case bounds and descriptive target SDs.

| Arm | Geometric mean ratio | Geometric RMS error factor | Maximum multiplicative error |
|---|---:|---:|---:|
| consolidated | 3.60067 | 5.06814 | 15.27609 |
| initial | 39.95109 | 43.42980 | 130.05175 |

| Grind | Primary GM ratio | Primary RMS factor | Primary maximum factor | Initial GM ratio |
|---|---:|---:|---:|---:|
| A | 1.15771 | 1.32943 | 1.45549 | 62.66929 |
| B | 1.91033 | 2.25675 | 3.56937 | 45.72121 |
| C | 5.88887 | 6.03433 | 8.49053 | 34.32907 |
| D | 12.90603 | 12.95641 | 15.27609 | 25.89883 |

Consolidated/initial prediction geometric mean: 0.090127.
Per-case porosity-substitution effects are retained in result.json; the initial arm is diagnostic only.

Reject all-case adequacy of this fixed composite predictor for the tested offline source domain.
Do not fit a correction in this task; failure does not isolate the native law from its adapter.

EWP consumer consequence: no compatible production permeability transfer is established; EWP is unchanged.
No fresh-shot hydraulics, H1, equilibrium, extraction kinetics or EWP validation is established.
No structural mechanism is identified, clean-screen question reopened, or successor authorized.

BASELINE.json records clean source/software baselines. GATES.json records novelty/source decisions.
FREEZE.json and PRE_SCORE_REVIEW.json bind the approved scientific artifacts; CLOSEOUT.json separates
affected tests, independent review and local-only publication status. No push, PR, merge or auto-merge.
