# VAL-CASE-5CQA-DECISION-RESOLUTION-001

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL. This is one retained-evidence addendum to
SCI-MD-5CQA-ASSAY-002, one October 9 T04 case and bounded 5-CQA T02 sensitivity
interpretation. Neither broader queue is completed. No automatic successor.
The owner authorizes the reducer, targeted intake, synthetic checks, finite
reductions, independent review and one draft unmerged Puckworks PR; auto-merge
disabled. EWP stays read-only. Existing public results and schemas were read
before this specification; this is not blind validation. The named private
files were hashed and structurally inspected, without new empirical reductions.

## Admission and immutable contract

Use only the configured PANNUSCH2024_MENDELEY_FULL_REPOSITORY or
PUCKWORKS_EXTERNAL_DATA_ROOT and its documented
`5cqa-assay-002-evidence-20260929T163451Z/run-001`. No archive search, new
acquisition, workbook reconstruction or historical fitting-attempt intake.
INPUT_MANIFEST.json binds public authorities and every admitted private file.
Verify public freeze, approval, receipt and nested completion `files` links,
producer/tree, arms and panels. STARTED receipt is intentional; completion must
be COMPLETE with scientific_score_passes=1. Public-copy fallbacks are explicitly
scores.json -> RESULTS.json, score_completion.json -> SCORE_COMPLETION.json,
score_receipt.json -> SCORE_RECEIPT.json, freeze.json -> FREEZE.json, only when
the private file is absent. A present mismatch never falls back. Core defects
block empirical core; optional-only defects are scoped unless they contradict
shared identity. Missing required shots are never reconstructed from means.
If core admission fails, report empirical NOT_RUN and exact artifact, preserving
source-independent verification and the targeted intake report.

Core: shot_results, scores and public evidence chain. Optional: predictions and
observed_suffix for fraction arithmetic; predictions or raw JSON states for
detailed extrapolation. No model loading/inference. Hash inputs before and after.
Actual locators, logs and all detailed outputs stay outside Git and outside the
original evidence directory, with an exclusive new output directory per reduction.

Exactly L1M=(m1,m2,q1), L2M=(m1,m2,q2), L12=(m1,m2,q1,q2), all forecasting
from m1+m2. q1/q2 are measured 5CQA interval averages; L2M requires m1.
Reuse qualification of 42 common FIT shots from 45, retaining all three q2
INVALID_SPILL exclusions. Historical E0/D0/A1/L1 are contextual, and historical
L1 is not L1M. Species exactly 5CQA; fractions 3,5,7,10; every intervening vial
mass remains in cumulative coordinates. PRED-C01/C02/C05/C06 primary, C03/C04
temperature_stress, C07/C08 flow_stress, three shots per condition. All original
24 shots/96 slots retained as original-population metadata. Primary support
48/48, temperature 24/24, flow 23/24 per arm; original unsupported C07 fraction
10 remains. Repeated arm predictions are not new observations.

## Reproduction and diagnostic aggregation

Validate actual nested panel/arm rows with shot, condition, full, bounds,
supported_subset_diagnostic and coverage. Validate canonical membership,
duplicates, finite values, support and nonnegative numerical allowances.
Aggregate exactly R_mg_g, B_mg_g, absB_mg_g, R_allowance_mg_g,
B_allowance_mg_g, absB_allowance_mg_g. R is measured-vial-mass-weighted RMSE;
B is prediction minus observation mean error; A averages abs(B) per shot.
Use equal shots within conditions and equal conditions within panels.

Binary64 point arithmetic follows historical NumPy reduction order where
applicable. Reconciliation tolerance is 512 ulps at max(1,abs(expected)),
covering short sums, square roots and subtraction across arithmetic orderings.
Report maximum differences, all decision discrepancies and private per-field
differences. This tolerance never changes thresholds, strictness or identity.
Point V checks use a tighter 16 ulps at max(R²,B²), with negligible negative
subtraction roundoff set to zero and counted; material negativity blocks reliance.
Prediction allowances cannot excuse negative point V.

Reproduce complete condition/panel metrics, bounds, allowances, support,
adequacy, comparisons and disposition from unrounded retained shots. Both
R<=0.25 and A<=0.125 must hold in every primary condition. Material comparisons
L12/L1M, L12/L2M, L2M/L1M separately require candidate adequacy, gain>=0.05,
relative gain>=15%, >=3/4 definite condition wins, A deterioration<=0.025 mg/g.
Both L12 comparisons must pass to earn two assays. Historical upper(v,u,t)
is PASS if v+u<=t, FAIL if v-u>t, otherwise UNRESOLVED; missing gives
INCOMPLETE_SUPPORT. Conjunction: FAIL, all PASS, incomplete, unresolved.
Wins are strict. Relative component is upper(C-.85*R,uC+.85*uR,0), without
caffeine's small-denominator forced failure. Report point ratios only for R>0
and conservative lower ratios only for R-uR>0. Keep gain_status, candidate
adequacy and final status distinct. Missing flow point metrics stay unavailable;
failure witnesses use complete nonnegative errors divided by original three
shots, not by number of complete shots. Preserve L1M C07 incomplete and L2M/L12
C07 FAIL with A lower bounds near 0.166164611/0.154031495 mg/g.

Exactly twelve primary and six temperature scenarios omit one physical shot's
entire trajectory from all arms simultaneously. Logical masks do not change
source records. Mean the affected condition's remaining two shots, then all four
or two conditions equally. Never pool eleven/five shots globally. Retain actual
membership privately: 11 shots/44 windows or 5/20 per arm. Intentional omission
is distinct from missing input. Local aggregation does not modify the original
three-shot panel_metrics. Flow receives baseline support diagnostics only; no
full-flow decomposition or flow perturbations. No bootstrap, fraction/condition
deletion, subset selection or additional perturbation family.

For each baseline and deletion retain gain, its own allowance/enclosure,
qualified relative gain, signed B change, A deterioration, condition contrasts,
definite/possible wins, original numerical margin components and contributions.
Primary diagnostic decisions cannot replace historical acceptance; three
untouched inadequate conditions remain in each deletion. Temperature gets scalar
margin diagnostics and two-condition win counts, never the three-of-four rule
or a primary material-value verdict. Preserve adverse temperature L12/L1M
baseline (~-0.001114821440 mg/g), improving C03 and worsening C04.
Independently verify G_without_s = G + (mean_g_condition-g_s)/(2*C) for net
gain and both contributions (C=4/2). Baseline and deletion-only ranges are
separate. Report point signs separately from numerical endpoint signs.

## RMSE-scale algebra and enclosures

For complete shots R²=B²+V, with V=sum(w*(e-B)²), normalized measured mass w.
Core computes V=R²-B² from unrounded retained R/B, preserving signed B.
For each paired shot D=R_ref+R_cand, C_B=(B_ref²-B_cand²)/D and
C_V=(V_ref-V_cand)/D. Compute before nested averaging. Verify C_B+C_V=R_ref-R_cand
per shot, condition, baseline and deletion. Report both mg/g contributions:
“Contribution from squared mean shot error” and “Contribution from within-shot
centered residual variation”. Preserve opposing signs and contributions greater
than the net; no percentages of net gain. Any squared aggregates average per-shot
R²/B²/V, never square panel averages. V is residual variation over measured
fraction supports, not assay variance, irreducible noise, unbiased sample variance
or continuous-curve shape error; no n-1 correction, causal diagnosis or predictor
correction follows.

Case-local interval arithmetic propagates retained R/B allowances: nonnegative
R interval; signed B; zero-crossing squares have lower zero. Each elementary
add/subtract/multiply/divide endpoint is rounded outward using math.nextafter;
endpoint extrema cover either numerator sign and positive denominator. Squared
V enclosure derives from R²-B², then intersects V>=0 explicitly; a negative
unintersected lower bound is dependence relaxation, not negative point V.
Average interval endpoints with actual nested scenario weights and outward
rounding. Keep the tighter direct net-gain enclosure separately; independent
contribution endpoints need not sum to it. Exactly zero point R values with
consistent zero components give zero point contributions. Denominator enclosure
including zero gives unresolved contribution bounds unless both complete R
intervals are exactly zero, which resolves the contributions to [0,0].

## Optional checks and interpretation

Authenticated prediction/observation pairs join exact physical-shot/fraction/arm,
campaign, condition, analyte, support and original coordinate fields, preserving
unsupported slots/reasons. Use stored five_cqa_mg_g, never five_cqa_kg/measured
mass: original b0 may differ from the documented integration anchor adjustment.
e=prediction_mg_g-1000*q; w=mass/sum(mass); u=1000*allowance_kg/mass.
Recompute R=sqrt(sum(w*e²)), B=sum(w*e), V=sum(w*(e-B)²), uR=sqrt(sum(w*u²)),
uB=uAbsB=sum(w*u); total allowance already includes coordinate allowance once.
Compare R/B/V, allowances and paired contributions with core, without prediction
generation or source requalification. Raw saved states are JSON only. Verify
shot flags and deletion flag summaries privately when admitted; otherwise keep
published totals and mark detailed verification unavailable. Published counts
L1M/L2M/L12: primary 9/3/9 of 12, temperature 5/3/5 of 6, flow 6/3/6 of 6.

Use unchanged accepted decision_resolution helper (PR #335). It compares
supplied evidence, authenticates nothing and propagates no error. Historical
allowance conclusions and finite deletion sensitivity use separate scopes and
evidence kinds. Deletion extrema are finite sensitivity evidence, never a
population/certified bound, confidence interval or future prediction interval.
Unknown training/model-selection, assay/calibration, early/input-measurement and
transfer uncertainty remain unquantified. Frozen fitted parameters and measured
inputs condition every conclusion. No causal calibration/batch/instrument/
inventory conclusion or recentered predictor is allowed. Practical value lacks
independently justified intended-use evidence beyond the retained engineering
contract; failure to earn complexity establishes neither absence nor equivalence.

## Outputs and verification

Commit this protocol, input manifest and SYNTHETIC_SPEC before new reductions.
One proportionate independent nonhuman reviewer examines method and actual
favorable/adverse retained results, public projection and numerical interpretation.
Preserve failures/corrections, rerunning only affected deterministic work. No
historical prepare/develop/freeze/score/verify/report invocation, fit, optimizer,
model conditioning, prediction regeneration, native simulation or EWP run.

Publish baseline condition/panel aggregates and only ranges/counts over each
entire twelve/six scenario family. Keep individual shot metrics/contrasts,
complete deletion vectors (keyed or unkeyed), keyed deletion means,
condition-by-deletion tables, per-condition deletion extrema/ranges, residuals,
locators and logs outside Git. Removing labels is insufficient to protect a
three-shot condition from algebraic reconstruction. Hash-bind private artifacts.
Public component statuses: historical metric/decision reproduction, primary
sensitivity, temperature sensitivity, RMSE decomposition, direct fraction check,
detailed extrapolation. Preserve TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE, no earned
two-assay route, PHYSICAL_VALIDATION=NOT_ESTABLISHED and
ANALYTICAL_UNCERTAINTY=NOT_ESTABLISHED. Software verification and hosted CI are
separate. Source-derived aggregates retain Pannusch/Schmieder CC-BY-NC-3.0,
Mendeley 10.17632/y2tz67f6ry.1, separately from first-party software licensing.
