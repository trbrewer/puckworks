# Trigonelline recipe campaign transfer: frozen methods

Task: SCI-MD-TRIGONELLINE-RECIPE-CAMPAIGN-TRANSFER-001. G1;
RESEARCH_ONLY; NO_GOVERNING_PHYSICS_CHANGE. This is a task-local empirical
observer, not a registered production component or a kinetic model. These
methods and the code/tests are bound in a private FREEZE before real fitting.
The requested task defines this campaign's controls; expired predecessor CLI
deadlines, approval receipts and fitting budgets do not govern new execution.
One implementation/review cycle and at most one material pre-score correction
are permitted. Numerical verification is not independent human review.

The question is whether nominal recipe adds conditional March-campaign value
beyond the accepted measured-mass observer, controlling added fitting capacity.
R18/Q18 is primary. R18/D0 and R18/K0 are the only other new contrasts.
The completed TR-D0/TR-K0 decision and all Wadsworth decisions remain unchanged.
No Wadsworth private bundle, new source acquisition, experiment, figure reading,
native EWP run, additional analyte, ramp representation or adoption enters.

## Authorities, inspection and support

Base PR382: `9f311e70bd08ae16387c9ac40aa9c71595f95a65`, branch
`sci-md-wadsworth-measured-surface-permeability-001`; its Git parent PR381:
`7c04a644c7b74be53ffb1cf611ebfb7ab06c5fd2`. Main:
`21669a427145194e1f4003e3cf1b97dedefe2679`. Read-only EWP reference:
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Scientific baseline producer:
`de31200f272711ca6b2e9fc5dc7c4881c406ab56`; old FREEZE SHA256:
`6f1b1afc73615eafb9b463b49089a1069d60179ea96b2a02a2951a9ec22f0b12`.
Accepted complete projection identity:
`58766702caa144e7641e87dca4d2d13e541459f276bb59c7cf4891261a91015e`.

Read AGENTS/CLAUDE/onboarding, available-data guide, register, manifest and
relevant card. Use the configured Pannusch resolver and retained receipt locator;
no broad owner-directory search or configuration/path publication. Absence is a
named local blocker, never evidence that the owner's collection is exhausted.
Authenticate all eight originals against the pinned SOURCE_IDENTITIES.json,
all bound preparation artifacts including training.json/development_support.json,
and SCORE_COMPLETION.json's scored artifacts. Authenticate accepted models before
new reproduction. Do not invoke old prepare/develop/final-fit/score campaigns.
Reuse the accepted source observer and pure linear-hat numerical geometry only.

Retain 45 canonical December FIT physical shots, three per original design,
not the 48-shot Schmieder export. Fractions are exactly 3,5,7,10: 180 slots,
177 qualified and three UNAVAILABLE_MEASURED_MASS_PREFIX. No imputation; every
shot has at least one qualified window and every design at least two shots
with three. Reconcile original measured vial masses including all intervening
unassayed vials. Only fraction 3 may reconcile the source start with m1+m2
within exactly four ULPs; allowance is twice absolute displacement. No general
clipping, prefix repair or domain extension.

Authenticate all 15 source recipe assignments using original doe_conditions,
ExpSheet/DoE, experiment identities and register program labels. Do not call
the predecessor qualify_settings, whose FIT population has only five designs.
The exact (grind, nominal Celsius temperature, dimensionless flow-program code)
assignments are:

| FIT | grind | temperature | code |
| --- | --- | --- | --- |
| C01/C02 | 1.4 | 80/98 | 1 |
| C03/C04 | 2.0 | 80/98 | 1 |
| C05/C06 | 1.4 | 80/98 | 3 |
| C07/C08 | 2.0 | 80/98 | 3 |
| C09 | 1.7 | 89 | 2 |
| C10/C11 | 1.7 | 89 | 1/3 |
| C12/C13 | 1.4/2.0 | 89 | 2 |
| C14/C15 | 1.7 | 80/98 | 2 |

All nominal doses are 20 g. March C01/C02/C05/C06 use grind 1.7 and respectively
(86,2), (92,2), (90,1.7), (90,2.3). Verify constant original start/end settings,
headers, collection-design convention and all physical-shot joins. Flow is a
dimensionless source-program code; neither measured flow, puck temperature,
density conversion nor cross-grinder physical mapping is inferred. Ramps
C03/C04/C07/C08 are not analyzed or represented by start/end averages.

Freeze one coordinate-only LOCO mask per held design, identical across all
nonlinear arms, preserving all intended slots/reasons. Every held shot must
have a supported window. Global 177 does not imply 177 held predictions.
For each shot s, b_s is its largest qualified endpoint. Require all 48 target
endpoints <= B_floor = max_d min_(s in d) b_s, and valid lower prefix boundaries.
Also require every source-design-deletion domain to cover all 48 windows.
Save floors, target maximum, margins, memberships, masks and augmented-projection
hashes before fitting. Any failed guard stops the campaign without replacement.

## Exposure, observation and uncertainty

Both campaigns are SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE /
CONDITIONAL_ON_MEASURED_EARLY_AND_QUERY_BEVERAGE_MASS. Earlier outcomes,
summaries and selections are exposure; a new arm cannot make this blind.
Trigonelline authority is MATLAB cAlcaloids(:,2), HPLC column T: mg/fraction
divided by that vial's measured grams gives mg/g beverage. Internal concentration
is kg/kg; beverage and analyte mass are kg. TDS/EY basis: NOT_APPLICABLE.
Trigonelline is a constituent of TDS, not additional TDS. No density conversion.

Private inspection receipts enumerate originals, recipes, supports and old
receipts actually inspected. Known collection dates are retained; session
independence remains unresolved. Recipe/date/lot/roast effects are confounded.
All evaluation grinder settings are 1.7; isolated grinder-transfer benefit
cannot be established. Assay calibration/recovery, LOD/LOQ, shared systematic
errors, mass/assay covariance and campaign/population uncertainty remain
unquantified. Intervals also omit tuning-selection and prior family-selection
uncertainty. They establish no adequacy, causality, kinetics, inventory/whole-cup
closure, blindness, physical validation or production readiness.

## Four arms and fitting

B is the largest endpoint among positive-weight training windows. Five equally
spaced knots on [0,B] use the inherited linear hat basis. For early vial masses,
x_i=(m_i-training design/shot-weighted mean_i)/0.01 kg. Common D0 logit is the
interpolated five knot values theta[j,0]+theta[j,1]x1+theta[j,2]x2 (15 coefficients).
R18 adds three global gamma offsets for standardized (grind, temperature, code).
Q18 adds three global gamma offsets for standardized (x1²,x1*x2,x2²).
Neither adds knot-specific interactions. D0 is independently refitted; K0 is
one independently fitted nonnegative weighted constant. R18/Q18 have exactly
18 coefficients; D0/K0 have 15/1 and are references, not capacity matches.

For every fit, use its training sample's design/shot-weighted means and
population SDs for added features. Require finite, nonzero scales; record
feature rank/conditioning and all target feature extrapolation. No target
information normalizes features. Regularization selects penalized coefficient
representations; a nonlinear Jacobian is not a physical-identifiability proof.
No jaxgsa campaign, extra feature family or residual-driven subgroup is allowed.

All arms use equal source-design weight, shot multiplicity normalized within
design, and measured window mass normalized within shot. Zero-weight source
rows stay in provenance but cannot set B, transforms or geometry. K0 is the
analytic mean under these weights. Nonlinear data residual is
(1000/0.25)*(predicted_q-observed_q)*sqrt(weight). The inherited 0.25 scale is
not a new adequacy margin. Retain D0's slope penalty and second-knot-difference
penalty exactly: lambda*mean(theta[:,1:]²) and
lambda*mean((diff(theta,n=2,axis=0)/0.25²)²). R18/Q18 additionally use
lambda*mean(gamma²). All coefficients have [-20,20] bounds.

Attempt all three inherited starts in order (-1,0,+1), gamma initially zero.
Only initial weighted concentration is bounded to [1e-8,1-1e-8] for its logit.
Use scipy least_squares trf/exact/linear, 2-point Jacobian, diff_step=1e-6,
x_scale=1 and ftol=xtol=gtol=1e-10. Choose lowest finite feasible converged
objective, exact ties by start order. Disclose finite unsuccessful terminations.
No converged start, structural/nonfinite error or exhausted budget stops the
required fit and campaign. No rescue, retry, reseed or target-informed change.

Each nonlinear arm independently evaluates lambda {0.0001,0.01,1,100} on all
15 whole-design LOCO folds. Fit transforms, B, knots and coefficients using only
retained training. Score common frozen held masks using mean mass-weighted shot
RMSE, then equal mean over held designs. Select largest lambda within 1e-6 mg/g
of minimum. Require all folds/all lambdas; never prune failures. These are
tuning diagnostics, not nested validation. Fit each selected arm on full FIT
with three starts. No K0 LOCO campaign. Before the new March outcome join,
freeze selected lambdas and point models in SELECTED_MODELS.json.

Reproduce saved historical D0/K0 primary predictions and losses inline from
these new necessary point fits with frozen 1e-8 mg/g tolerance. Check selected
D0 lambda agreement and maximum differences. A mismatch stops interpretation;
never force the old lambda or fit to March outcomes.

## Numerics, scoring and resampling

Float64; accepted 64-point Gauss–Legendre integration split at knots, 128-point
refinement and independent split adaptive quad (epsabs=1e-14 kg,
epsrel=2e-13, limit=200). Allowance is
max(|I64-I128|, |I64-Iadapt|+quad_error, |I128-Iadapt|+quad_error)
+128*machine_epsilon*(width+|I64|), plus the exact coordinate allowance.
Every held, point, draw and deletion scored interval must have allowance <=1e-9
kg. Convert allowances to mg/g using measured interval mass; propagate L2 to
shot RMSE and L1 to bias/MAE, then the same hierarchy. Propagate bounds to
contrasts and percentile endpoints. Interval-based selections must be invariant
under these bounds; otherwise NUMERICALLY_UNRESOLVED. Numeric bounds are not CIs.

Per-shot R=sqrt(sum(window_mass*error_mg_g²)/sum(window_mass)). Primary L is
mean R within each condition, then equal mean of four conditions; never pooled
window RMSE. Report mass-weighted MAE, signed bias, mean absolute shot bias,
condition metrics, coverage, worst errors and feature/domain support.
Delta=L_A-L_B (negative favors A); gain=1-L_A/L_B (positive favors A).

Exactly 2,000 paired draws: SeedSequence(20261027).spawn(19), independent
default_rng streams ordered FIT-C01..C15 then PRED-C01,C02,C05,C06.
Each condition draws three indices from its three original shots and retains
integer multiplicities; whole shots carry all windows. Source/target draws are
independent, identical vectors across arms. All 19 conditions remain represented.
Refit all coefficients at each independently selected, subsequently frozen
lambda, recomputing transforms and positive-weight domain/knots. Do not retune.
Save predictions for all 48 windows, including zero target multiplicity.

Use percentile 95% intervals with linear 2.5/97.5% quantiles, aggregate and
condition-specific. These are marginal conditional resampling intervals with
uncalibrated coverage, not simultaneous, measurement, tuning-aware, nested or
new-campaign confidence. If any reference loss is zero, count undefined gain
and leave its entire CI undefined; no epsilon or omitted draws. Absolute
contrasts remain valid. Stop first required failed fit/draw, retain its vectors
and diagnostics, and report requested/completed/failed/unattempted/undefined.

## Frozen decisions and influence

For aggregate R18/Q18 delta CI: upper<0 gives
RECIPE_LOWER_THAN_MATCHED_MASS_CONTROL; lower>0 gives
MATCHED_MASS_CONTROL_LOWER_THAN_RECIPE; otherwise (including zero endpoints)
RECIPE_MASS_COMPARISON_UNRESOLVED.

RECIPE_CONDITIONAL_TRANSFER_PREFERENCE requires aggregate delta CI upper<0
against EACH Q18/D0/K0 AND R18 point loss no higher than EACH comparator in ALL
four conditions. The latter is a frozen safeguard, not a confidence level.
If any comparator has resolved lower aggregate loss, RECIPE_NOT_SELECTED names
it. Otherwise a failed conjunction gives RECIPE_INCREMENT_UNRESOLVED and failed
requirements. Incomplete inference gives INCOMPLETE, with no preference claim.

Gain grades: worse <0; small [0,.10); moderate [.10,.25); large >=.25. Report
point grade and every grade intersected by each closed CI. Reclassify unchanged
estimates at all nine lower {.075,.10,.125} × upper {.1875,.25,.3125} pairs.
These ±25% descriptive-boundary checks are not acceptance or measurement-error
limits and cannot reinterpret a zero-crossing interval.

Exactly 15 source-design deletions refit all arms at frozen lambdas, recomputing
transforms/domain, and evaluate unchanged 12-shot/48-window March targets.
Exactly four target-condition deletions rescore saved point predictions.
Report ranges, ties, ranking reversals and adverse conditions for all three
contrasts. These are influence diagnostics, not CIs or retuned validation.
No additional sensitivity or scientific successor runs here.

## Execution and deliverables

One worker/BLAS thread; <=8,000 actual residual calls per start including finite
differences. Durable compact start/finish journal and one persistent byte per
actual residual call; exclusive execution refuses restart, counters never reset.
Expected 540 tuning +9 point +18,000 bootstrap +135 deletion =18,684 iterative
starts, and 1+2,000+15=2,016 analytic K0 fits. Qualification <=30 minutes;
scientific computation <=150 minutes from first real fit, including prediction,
resampling and influence. One session <=4 hours excluding installation/hosted
CI waiting. Cap exhaustion is INCOMPLETE; do not shorten the campaign.

Synthetic checks cover identities/all designs, prefix/floor/masks, leakage,
recipe isolation, 18-coefficient construction, penalties, training-only
transforms, literal replication, zero-weight geometry, four target conditions,
independent tuning, quadrature, complete draws/failure accounting and refusal
of preference on R18/Q18 alone. Run required repository QA once at end, with
focused follow-up for concrete failures; disclose local and hosted separately.
Preserve PR381's failed-suite history and PR382's narrow repair.

Public files contain code, synthetic tests, methods and safe status/hashes.
Private output includes <=750-word/two-page RESULT.md, <=120-word SUMMARY.md,
complete RESULT.json, SCORES.csv, CONTRASTS.csv, PREDICTIONS.csv, inspection and
source/recipe/support receipts, memberships/folds, tuning, all multiplicities,
draw predictions/scores, diagnostics/allowances, deletions, failures, FREEZE,
selected-model receipt and SHA256 ARTIFACTS.json. Preserve Pannusch/Schmieder
attribution and CC-BY-NC-3.0 restrictions; no source originals in Git.
Draft PR stacked on PR382, unmerged, auto-merge disabled, verified directly.

Exactly one provisional next candidate is NOT_RUN:
SCI-MD-TRIGONELLINE-RECIPE-INCREMENT-HELD-DESIGN-001. It is justified only if
this comparison supports recipe preference; a genuinely nested, fully retuned
held-design test needs a fresh credible budget. Otherwise NOT_JUSTIFIED.
Reassess priorities if genuinely unexposed existing data become executable.
P1 blind-TDS remains OPEN.
