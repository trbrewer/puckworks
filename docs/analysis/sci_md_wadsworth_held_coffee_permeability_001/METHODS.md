# SCI-MD-WADSWORTH-HELD-COFFEE-PERMEABILITY-001

Owner-authorized G1 exposed retrospective comparison. One implementation/review
cycle, at most one material correction before scoring; no post-score retuning.
Qualification cap 15 minutes; scientific computation cap 30 minutes, excluding
installation and required repository QA. No physical experiments, new raw data,
figure reading, LB/OpenFOAM, extra families, or predecessor campaign replay.

## Authority and inspection

PW main `21669a427145194e1f4003e3cf1b97dedefe2679`; branch base and scientific
parent PR380 `097e5c7f0bdc1bef38d56938374f936003d55a39`; its Git parent
`d41af1d08cda65864fdbdf5c6e1814cc027c5ef1`; scientific predecessor PR379
`cc6e3d66eb5192e08e0949373548bb3a04ee69fd`; read-only EWP
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.

Source: Wadsworth et al., *Royal Society Open Science* 13, 252031 (2026),
[DOI 10.1098/rsos.252031](https://doi.org/10.1098/rsos.252031),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The owner's existing Table 1 transcription is used unchanged; derived results
are newly calculated, private, and do not extend the bounded permissions record.
Methods §§3.1, 3.3–3.4 were inspected in the
[original methods PDF](https://strathprints.strath.ac.uk/95930/1/Wadsworth-etal-RSOS-2026-A-model-for-the-permeability-of-coffee-pucks-validated.pdf).
No figures or new raw data were acquired. The source CSV, provenance, both cards,
native permeability module, historical collapse gate, permissions and PR380
STATUS lineage were actually inspected. No PR380 private packet was accessed.

Authenticate full-table bytes before parsing: SHA256
`3b0139fe02108d3dfcd1441d9e4062e86d9b7e1a8505141a7beefd9366ebf20f`,
Git blob `37b4136bfa1a84df159f41c01245000288db4ebf`, 2315 bytes,
23 CRLF lines. Preserve original coffee/G order, Guayacan then Tumba, G1–11.
There are 22 preparations, 21 endpoints (10/11), two coffees and zero espresso
shots. Guayacan G2 lacks porosity/permeability and is explicitly excluded.
Validate unique ordered membership, finite positive mean radius (metres, not
diameter), connected dimensionless porosity strictly between zero and one,
positive finite permeability (m²), and finite nonnegative reported error.
Do not use total porosity, impute missing outcomes or convert density/TDS/EY;
TDS/EY basis is NOT_APPLICABLE.

Each coffee/setting is one untamped XCT preparation. Permeability is the mean
of x/y/z simulations, not three preparations. The reported error is described
as “standard deviation on the average.” It is not assigned replicate-variance,
Gaussian-SD or SEM meaning; never divide by sqrt(3), weight by it, or simulate
observations from it. Directional components and replicated preparations are
unavailable. Two coffees are not 21 independent coffees.

Both folds are SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE /
CONDITIONAL_ON_MEASURED_RADIUS_AND_CONNECTED_POROSITY. Prior target/mean use and
source fits preclude blindness. Historical measured-surface-area collapse
numbers (GM about 0.91, scatter ×1.31) are not scores of the radius formula.
All new W3/E3/N losses and CIs are NOT_RUN until the private frozen execution.

## Frozen arms and numerics

Fit Guayacan's ten endpoints, evaluate Tumba's eleven; then reverse. Exactly one
out-of-coffee prediction per eligible record and arm. R0=1e-3 m, k0=1e-10 m²,
r=R/R0, z=ln(k/k0), o=ln[2 R0²/(9 k0)]+2 ln(r)-ln(1-phi).

* W3: z_hat=o+c-2 a r+b ln(phi), unrestricted c,a,b; a=alpha R0.
* E3: z_hat=e0+eR ln(r)+ePhi ln(phi), unrestricted e0,eR,ePhi.
* N: training mean z, hence training geometric mean permeability.

W3/E3 have equal three-coefficient freedom and log squared-error objective;
independent fits in every fold/draw/deletion. No imported all-source constants,
target means/offsets/scales, ridge or hyperparameter search. G/coffee identify
folds and diagnostics only. Surface area and k_err are not inference inputs.
Production alpha=4808 m^-1 and b=4.4 remain unchanged. W3 is a calibrated
surrogate. Preserve and score a<0 or b<=0; report both flags and frequencies.
No constrained rescue, physical identification or native-law validation follows.

Use float64 exact linear least squares, unit point weights and nonnegative
bootstrap multiplicities. Center/scale features with weighted training means
and population standard deviations only. Retain exact inverse coefficient map.
Use the weighted active-row design; rank is the count of singular values greater
than eps*max(matrix_shape)*largest singular value. Require full column rank,
nonzero finite scales, positive total weight, finite objectives and predictions.
Save singular values, threshold, condition number, scales, centers, coefficients,
weights and SSE. Local rank is not physical identifiability.

Cross-check SVD with independently implemented QR plus triangular solution on
source and held predictors: absolute difference <=1e-9*max(1,abs(z_hat)). Check
inverse-map predictions at that same tolerance. Synthetic tests compare weighted
fits with literal replicated rows, including zero individual weights. E3 SSE
must be <=N SSE+1e-12*max(1,N SSE); no such nesting test applies to W3.
Predict directly in log units and exponentiate ln(k0)+z with finite/positive
checks. Retain every eligible extrapolation; never clip or omit predictions,
losses or coefficients. Training design diagnostics suffice; no GSA campaign.
Any necessary future GSA is training-only; ST<0.01 supports fixing a parameter,
not calling it refuted. A need to redesign these arms blocks this task.

## Metrics, uncertainty and decisions

Primary L=sqrt(0.5 MSE_Guayacan(z_hat-z)+0.5 MSE_Tumba(z_hat-z)).
This is neither pooled record RMSE nor mean directional RMSE. Report each coffee,
log MAE/bias, and absolute permeability RMSE/MAE/bias with the same equal-coffee
aggregation, using the same fitted predictions. Store per-record predictions,
errors, coverage, worst cases, source/target R/phi ranges and marginal flags.
Within both marginal ranges does not establish joint support.

Exactly 2000 ordinary paired draws: NumPy SeedSequence(20261027), two spawned
default_rng streams, stable Guayacan/Tumba order; rng.integers(0,n,size=n), then
bincount(minlength=n), independently per coffee. Reuse each coffee's ONE vector
for its training and opposite-fold evaluation role, across all three arms.
Refit every arm per draw. Score with evaluation multiplicities and equal coffee
weight. Never resample source/target roles independently or coffee labels.
Save every vector and draw result, diagnostics, scores and contrasts.

Percentile 95% conditional CIs use numpy percentile method='linear', 2.5/97.5,
for every metric, direction, and paired contrast. W3/E3 primary; W3/N and E3/N
secondary. Delta=L_A-L_B; gain=1-L_A/L_B. Zero reference loss makes gain undefined,
without epsilon; preserve delta, report undefined counts and no gain CI if any
required value is undefined. Record requested/completed/failed/unattempted counts.
First failed required draw: save weights/reason, stop, INCOMPLETE; no retry,
reseed, pseudoinverse rescue, successful-only CI or omission.

Conditional intervals assume within-coffee record sampling despite deliberately
selected grinder settings, not repeated independent shots. Coverage is
uncalibrated. Measurement and coffee-population CIs are NOT_ESTIMABLE. These
intervals exclude new-coffee generalization, physical replicate variance,
directional measurement uncertainty, correlated segmentation/geometry error,
shared systematic effects and prior selection.

W3/E3 delta CI upper<0: W3_LOWER_CONDITIONAL_LOG_LOSS; lower>0:
E3_LOWER_CONDITIONAL_LOG_LOSS; otherwise, including zero endpoints:
HELD_COFFEE_COMPARISON_UNRESOLVED. Incomplete inference: INCOMPLETE, no selection.
Preference additionally requires aggregate paired intervals favoring one arm
against BOTH alternatives and point loss no higher in BOTH coffee directions.
Otherwise report unresolved, baseline or direction dependence explicitly. W3
preference is only for its calibrated surrogate, with nonphysical signs flagged.
No adequacy, equivalence, causation, production or physical-law claim follows.

Gain grades: worse<0; small [0,.10); moderate [.10,.25); large>=.25. Report point
grade and all grades intersected by the closed CI. Reclassify unchanged estimates
at all nine lower {.075,.10,.125}/upper {.1875,.25,.3125} combinations. These are
descriptive boundaries, not error allowances or practical acceptance thresholds;
zero is a directional boundary, not an adequacy margin.

Bounded sensitivity: (A) absolute-unit losses on identical fits/draws; (B) each of
21 physical records deleted from BOTH roles; (C) each nominal G1–11 deleted from
BOTH coffees with actual G2 missingness retained. Refit both folds for B/C once.
Report delta/gain ranges, exact zero ties and point-sign reversals for every
contrast/direction/unit. These are influence ranges, not CIs. No new bootstraps.

## Freeze, QA and outputs

Private FREEZE.json is written before any real-table fit/score, binding this
method, implementation, launcher, tests, authority files, ordered memberships,
folds, equations, seed and numerical policy. A fresh output directory outside
the checkout is mandatory. No silent replay. Stop on source/identity/unit drift,
missing inputs, leakage, rank/arithmetic failure, unrepresentable predictions,
invalid inference, exhausted budget or unfixed material defect. Preserve partial
artifacts and precise BLOCKED/INCOMPLETE/NOT_RUN status.

Meaningful synthetic tests precede scoring; required repository QA runs once,
with focused follow-up only for concrete failures. Report local versus hosted
verification separately; numerical checks are not independent human review.
The parent QA evidence may be reused by exact hashes; no predecessor scientific
campaign is replayed. Existing test discovery automatically includes this file.

Private outputs: RESULT.md <=750 words/approximately two pages; SUMMARY.md <=120
words; complete RESULT.json, SCORES.csv, CONTRASTS.csv, PREDICTIONS.csv,
FOLDS.json, MULTIPLICITIES.csv, DRAWS.jsonl, DIAGNOSTICS.json, FREEZE.json and
ARTIFACTS.json SHA256 manifest. Numerical results remain outside Git. The source
CSVs, old gates, production defaults, predecessor artifacts and EWP are untouched.

Draft PR stacks on `sci-md-pocketscience-grudeva-window-tds-001`, unmerged, with
auto-merge disabled. P1 blind-TDS remains OPEN. Exactly one provisional next
candidate, unexecuted: SCI-MD-TRIGONELLINE-RECIPE-INCREMENT-001, testing nominal
recipe information beyond independently refitted accepted TR-D0 with naive
TR-K0 on canonical 45-shot/15-design source. Its feature/fitting/inference
contract needs fresh bounded selection review. Do not repeat the completed
mass-shape comparison. Reassess priority if genuinely unexposed existing data
become executable.
