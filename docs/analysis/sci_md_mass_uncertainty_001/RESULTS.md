# Retained MASS predictions: uncertainty and physical-shot influence

The unchanged predictions retain useful performance and all original verdicts. MASS-006 earns its original two-assay mapping decision; MASS-007 improves substantially over both frozen controls while failing its original adequacy contract; MASS-008 is adequate but does not earn its three incremental-value claims. All original arm metrics and decision components reproduce from verified retained evidence.

The comparisons remain positive under every tested physical-shot deletion. Their size is less stable: MASS-006’s gain over C1 and all three MASS-008 gains cross the original 0.10 pp gain component. MASS-007’s mean absolute shot bias crosses 0.50 pp, although its gains over C0/C1 remain above both original continuous gain thresholds. These are finite-cohort influence results, not replacement verdicts or confidence intervals.

Quantified here: original numerical allowances, observed between-shot variability on MASS-006 scored fractions, distributions of retained performance and paired gains, and physical-shot deletion ranges. Within-shot analytical repeatability, calibration/systematic uncertainty, propagated early-input uncertainty, training uncertainty, cross-source uncertainty and population confidence coverage remain unestablished. Unknown components are not zero. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

[Frozen specification](PROTOCOL.md) · [Full precision aggregates, headroom and provenance](RESULTS.json) · [Execution and handoff](HANDOFF.md)

## Historical reproduction and all original arms

Errors are TDS percentage points. R is mass-weighted RMSE within a shot/pair; B is signed mass-weighted bias; A is absolute bias within that same unit. Higher means average these metrics, never all fraction errors together. Mean A is not abs(mean B). Numerical allowances are carried separately and do not resolve sampling or assay uncertainty.

### MASS-006

Original disposition: **LEARNED_TWO_ASSAY_MAPPING_EARNED**, A/B/C/D PASS. All 45 FIT shots across 15 conditions remain training. PRED uses 12 primary shots/48 suffix slots and two separate 6-shot/24-slot stress panels. Fractions 1/2 condition; fractions 3/5/7/10 are scored. Each condition receives equal weight after equal weighting of its three shots.

| Panel | Arm | Mean R | Mean B | Mean A | Original adequacy | Support |
|---|---|---:|---:|---:|---|---|
| primary | C0 | 0.652055 | -0.410419 | 0.410419 | PASS | 48/48 |
| primary | C1 | 0.597587 | -0.400205 | 0.400205 | FAIL | 48/48 |
| primary | C2 | 0.480034 | -0.395567 | 0.395567 | PASS | 48/48 |
| primary | FIRST_ASSAY_EMPIRICAL | 0.779601 | -0.665654 | 0.665654 | FAIL | 48/48 |
| temperature_stress | C0 | 0.444403 | -0.279829 | 0.279829 | PASS | 24/24 |
| temperature_stress | C1 | 0.450277 | -0.324285 | 0.324285 | PASS | 24/24 |
| temperature_stress | C2 | 0.332810 | -0.256547 | 0.256547 | PASS | 24/24 |
| temperature_stress | FIRST_ASSAY_EMPIRICAL | 0.627070 | -0.487457 | 0.487457 | FAIL | 24/24 |
| flow_stress | C0 | 0.586396 | 0.003967 | 0.412570 | SOURCE_SUPPORT_INCOMPLETE | 23/24 diagnostic only |
| flow_stress | C1 | 0.502247 | -0.093189 | 0.374577 | SOURCE_SUPPORT_INCOMPLETE | 23/24 diagnostic only |
| flow_stress | C2 | 0.770336 | 0.021371 | 0.491562 | SOURCE_SUPPORT_INCOMPLETE | 23/24 diagnostic only |
| flow_stress | FIRST_ASSAY_EMPIRICAL | 0.467793 | -0.349704 | 0.349704 | SOURCE_SUPPORT_INCOMPLETE | 23/24 diagnostic only |

Flow values are supported-subset diagnostics, not complete-panel estimates. The original one unsupported learned flow slot remains absent; legacy support is separately restricted. C08’s three learned shots retain m2 extrapolation flags. Primary and temperature have no learned extrapolation flags. The C2/legacy primary comparison uses the exact complete common support. C1’s primary aggregate A is below 0.50 pp, but it fails the original requirement that **every condition** pass.

| Original C2 comparison | R gain | Relative gain | Definite condition wins | Gain headroom over 0.10 pp |
|---|---:|---:|---:|---:|
| C0 (secondary) | 0.172021 | 26.38% | 3/4 (3 required) | +0.072021 |
| C1 (B) | 0.117553 | 19.67% | 3/4 (3 required) | +0.017553 |
| Legacy (D) | 0.299567 | 38.43% | 4/4 (3 required) | +0.199567 |

The machine-readable report supplies signed headroom for each original condition’s 1.00/0.50 pp gates, B/D gain and win gates, and C competitiveness/deterioration gates, including numerical bounds. Primary C0 is also adequate; its success is retained.

### MASS-007

Original disposition: **FROZEN_CONDITIONAL_TRANSFER_INADEQUATE_ON_DECLARED_COHORT**. C2 adequacy FAIL; I0/I1 PASS/PASS. The qualified source has 13 shots; 11 are eligible, with 55 scored positive suffix windows. Two shots remain excluded for unavailable pooled chemistry. The 22 pooled inputs consume **98 original assays**, not two physical assays per shot. No heterogeneous shots are treated as repeat assays of an identical condition.

| Arm | Mean R | Mean B | Mean A | R headroom ≤1 | A headroom ≤0.5 | Adequate shots / required | Original A |
|---|---:|---:|---:|---:|---:|---:|---|
| C0 | 0.965470 | 0.830451 | 0.831110 | +0.034530 | -0.331110 | 3/9 | FAIL |
| C1 | 1.001235 | 0.969673 | 0.969673 | -0.001235 | -0.469673 | 2/9 | FAIL |
| C2 | 0.599149 | 0.509950 | 0.532635 | +0.400851 | -0.032635 | 7/9 | FAIL |

C2 is two adequate shots short of the original 9/11 requirement, and its mean A exceeds 0.50 pp by 0.032635 pp. Coverage and numerics pass. Both increments have 11/11 definite paired wins (two above the requirement). All original exclusions and feature-extrapolation counts are retained in RESULTS.json.

| Comparison | R gain | Relative gain | A deterioration | Original increment |
|---|---:|---:|---:|---|
| I0 | 0.366321 | 37.94% | -0.298476 | PASS |
| I1 | 0.402086 | 40.16% | -0.437039 | PASS |

The separately reproduced source-trained GRUDEVA-CLOCK MASS diagnostic has R=0.420832, A=0.314583 on the same suffix support. It has different information privileges and is not a fair primary arm or ablation.

### MASS-008

Original disposition: **ADAPTATION_ADEQUATE_INCREMENT_NOT_ESTABLISHED**. Exactly F2/A2/A0/M; 11 physical identities, 110 ordered off-diagonal pairs, 55 unique suffix observations and 550 slots per arm. This reuses MASS-007’s eligible cohort. Every pair metric, calibration-row mean, target-column mean and overall mean reproduces. Source, coverage, calibration and numerics pass.

| Arm | Mean R | Mean B | Mean A | R headroom ≤1 | A headroom ≤0.5 | Adequate calibration choices / required | Original A |
|---|---:|---:|---:|---:|---:|---:|---|
| F2 | 0.599149 | 0.509950 | 0.532635 | +0.400851 | -0.032635 | 0/9 | FAIL |
| A2 | 0.483158 | 0.012838 | 0.346410 | +0.516842 | +0.153590 | 9/9 | PASS |
| A0 | 0.600496 | 0.037845 | 0.499013 | +0.399504 | +0.000987 | 3/9 | FAIL |
| M | 0.582649 | -0.072253 | 0.455719 | +0.417351 | +0.044281 | 4/9 | FAIL |

A2 has zero surplus above the required nine adequate calibration choices. Each choice needs at least eight adequate targets out of ten. The generic overall `required_adequate_pairs=83` metadata is unused: A2’s 81/110 adequate pairs are not an overall failure gate. A0 and M meet overall continuous budgets but fail calibration-choice counts.

| Increment | R gain | Headroom over 0.10 | Relative gain | Target wins / required | Calibration wins / required | Original |
|---|---:|---:|---:|---:|---:|---|
| I_CAL | 0.115991 | +0.015991 | 19.36% | 8/9 | 9/9 | FAIL |
| I_CHEM | 0.117338 | +0.017338 | 19.54% | 7/9 | 9/9 | FAIL |
| I_LOCAL | 0.099492 | -0.000508 | 17.08% | 8/9 | 7/9 | FAIL |

I_CAL and I_CHEM miss target-win requirements; I_LOCAL also misses the absolute gain by 0.000508447 pp and calibration-choice wins. These are multiple components, not one isolated near-threshold failure. Numerical bounds do not straddle the historical decisions.

## Measured variability and deletion sensitivity

No bootstrap was used. No confidence intervals or prospective population coverage are claimed. Deletion removes whole physical shots with every fraction and arm together. MASS-006 retains fixed condition weights; MASS-008 removes an identity from **both** roles, leaving 10 identities and exactly 90 pairs in every deletion, without refitting.

### MASS-006 observed scored fractions

Each condition/fraction has three source-observed replicate shots; actual scored support is tracked separately for every arm. Sample SD uses n−1; it is between-shot spread at measured windows, not analytical repeatability. Fractions 1/2 and FIT scatter are not used to characterize PRED suffix uncertainty.

| Panel | Scored condition/fraction groups | Across-group range of source-observed TDS SD (pp) | Largest b0 range (g) | Largest b1 range (g) |
|---|---:|---:|---:|---:|
| primary | 16 | 0.007966–1.410758 | 6.233700 | 6.477100 |
| temperature_stress | 8 | 0.002776–0.324923 | 1.905600 | 1.833400 |
| flow_stress | 8 | 0.004646–0.409600 | 11.832400 | 13.553300 |

| Restricted scored cell | Arm | Source-observed n | Scored n | Scored TDS SD (pp) |
|---|---|---:|---:|---:|
| PRED-C07 / fraction 10 | C0 | 3 | 2 | 0.502263 |
| PRED-C07 / fraction 10 | C1 | 3 | 2 | 0.502263 |
| PRED-C07 / fraction 10 | C2 | 3 | 2 | 0.502263 |
| PRED-C07 / fraction 10 | FIRST_ASSAY_EMPIRICAL | 3 | 2 | 0.502263 |

The same fraction label therefore does not guarantee an identical mass window. RESULTS.json retains every condition/fraction n, SD and coordinate range. These empirical spreads do not identify a noise floor or a perfect-model failure probability.

### Continuous metric ranges after deleting one physical shot

| Task/panel | Arm | Mean R range | Mean B range | Mean A range |
|---|---|---:|---:|---:|
| 006/flow_stress | C0 | unavailable (original incomplete support) | unavailable (original incomplete support) | unavailable (original incomplete support) |
| 006/flow_stress | C1 | unavailable (original incomplete support) | unavailable (original incomplete support) | unavailable (original incomplete support) |
| 006/flow_stress | C2 | unavailable (original incomplete support) | unavailable (original incomplete support) | unavailable (original incomplete support) |
| 006/flow_stress | FIRST_ASSAY_EMPIRICAL | unavailable (original incomplete support) | unavailable (original incomplete support) | unavailable (original incomplete support) |
| 006/primary | C0 | 0.618733–0.701991 | -0.450214–-0.388451 | 0.388451–0.450214 |
| 006/primary | C1 | 0.583812–0.614712 | -0.416547–-0.385698 | 0.385698–0.416547 |
| 006/primary | C2 | 0.455720–0.511259 | -0.427618–-0.376894 | 0.376894–0.427618 |
| 006/primary | FIRST_ASSAY_EMPIRICAL | 0.758891–0.803793 | -0.686799–-0.646352 | 0.646352–0.686799 |
| 006/temperature_stress | C0 | 0.395642–0.480570 | -0.292759–-0.272358 | 0.272358–0.292759 |
| 006/temperature_stress | C1 | 0.431605–0.476919 | -0.335727–-0.301583 | 0.301583–0.335727 |
| 006/temperature_stress | C2 | 0.325587–0.337816 | -0.280754–-0.244054 | 0.244054–0.280754 |
| 006/temperature_stress | FIRST_ASSAY_EMPIRICAL | 0.589292–0.660834 | -0.558410–-0.430325 | 0.430325–0.558410 |
| 007/cohort | C0 | 0.898850–1.023815 | 0.752393–0.913858 | 0.753119–0.913858 |
| 007/cohort | C1 | 0.949646–1.066073 | 0.915022–1.034728 | 0.915022–1.034728 |
| 007/cohort | C2 | 0.554430–0.634328 | 0.456753–0.573421 | 0.481706–0.573421 |
| 008/cohort | A0 | 0.523633–0.630664 | 0.025671–0.043414 | 0.418209–0.527212 |
| 008/cohort | A2 | 0.428337–0.505679 | 0.008832–0.014707 | 0.272346–0.375796 |
| 008/cohort | F2 | 0.554430–0.634328 | 0.456753–0.573421 | 0.481706–0.573421 |
| 008/cohort | M | 0.511557–0.615499 | -0.084447–-0.018903 | 0.378762–0.485368 |

MASS-006 flow full-scope ranges remain unavailable; dropping its incomplete shot cannot silently repair the original scope. Complete-shot subset distributions explicitly report their smaller n. All supported-subset original metrics remain separate.

| Task/panel | Candidate versus control | R-gain range (pp) | Relative-gain range |
|---|---|---:|---:|
| 006/flow_stress | C2 vs C0 | unavailable | unavailable |
| 006/flow_stress | C2 vs C1 | unavailable | unavailable |
| 006/flow_stress | C2 vs FIRST_ASSAY_EMPIRICAL | unavailable | unavailable |
| 006/primary | C2 vs C0 | 0.138859–0.214102 | 0.220856–0.309548 |
| 006/primary | C2 vs C1 | 0.093939–0.135358 | 0.160907–0.228173 |
| 006/primary | C2 vs FIRST_ASSAY_EMPIRICAL | 0.269018–0.331073 | 0.345618–0.420788 |
| 006/temperature_stress | C2 vs C0 | 0.070056–0.145890 | 0.177068–0.306337 |
| 006/temperature_stress | C2 vs C1 | 0.104451–0.139102 | 0.237677–0.291669 |
| 006/temperature_stress | C2 vs FIRST_ASSAY_EMPIRICAL | 0.258942–0.327771 | 0.439412–0.495996 |
| 007/cohort | C2 vs C0 | 0.312063–0.402896 | 0.347180–0.404012 |
| 007/cohort | C2 vs C1 | 0.352958–0.431745 | 0.369672–0.428484 |
| 008/cohort | A2 vs A0 | 0.072819–0.159468 | 0.125876–0.264134 |
| 008/cohort | A2 vs F2 | 0.081108–0.205991 | 0.138224–0.324739 |
| 008/cohort | A2 vs M | 0.005877–0.149255 | 0.011489–0.251472 |

MASS-007 C2’s A range is 0.481706–0.573421 pp; one deletion lowers that continuous metric below 0.50. Its original 7/11 adequate-shot count remains authoritative. MASS-008’s A2 continuous adequacy metrics remain comfortably below their budgets under deletion, while practical-gain margins remain sensitive. A positive gain range does not establish an increment, equivalence or independent validation.

### Adverse calibration choices in MASS-008

These are ranges of the worst retained calibration-row mean after each joint-role deletion. Individual calibrators are not selected or published.

| Arm | Worst row R range | Worst row A range |
|---|---:|---:|
| A0 | 0.937791–1.086900 | 0.840300–1.006828 |
| A2 | 0.647599–0.788600 | 0.516053–0.752400 |
| F2 | 0.588549–0.667275 | 0.521366–0.616562 |
| M | 0.722648–1.362327 | 0.597727–1.156190 |

A2 retains an adverse calibration choice with mean A above 0.50 pp in every deletion. Overall adequacy does not make every choice reliable. Target-column adverse ranges, all paired distributions and all numerical headroom are retained in RESULTS.json.

## Interpretation and next decision

The next decision can distinguish useful conditional performance from evidence that an incremental margin is robust to the observed cohort. This audit does not authorize changed thresholds, revised historical decisions or adoption. Any later acceptance-rule change needs an independently justified intended use and practical margin; prospective coverage and total predictive uncertainty need evidence not supplied by these retained fits. No successor, source acquisition or laboratory operation is started.

Pannusch/Schmieder source-derived aggregates retain CC-BY-NC-3.0, attribution and Mendeley DOI 10.17632/y2tz67f6ry.1. Grudeva material retains Dr. Yoana Grudeva’s documented permission scope and thesis attribution; no new redistribution rights are inferred. First-party software licensing is separate. Raw observations, individual results, predictions and local locators remain outside Git.

Implementation, complete real-data reduction, independent nonhuman review and hosted CI are separate dispositions recorded in HANDOFF.md. EWP, historical science, source evidence, production settings and dependency locks remain unchanged. This result does not establish reliability of the host implicated in previous integrity failures.
