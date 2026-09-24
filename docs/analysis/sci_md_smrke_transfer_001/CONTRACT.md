# SCI-MD-SMRKE-TRANSFER-001 exact pre-scoring contract

G1 / NO_GOVERNING_PHYSICS_CHANGE. Owner authorization is the bounded task prompt;
its present authorization does not rewrite predecessor NO_SUCCESSOR dispositions.
Exactly four analysis-only endpoint response forms, no production registration.
Public previously inspected data; no protected or previously unseen holdout claim.
Implementation author has inspected the publication, figure and all marker values
before this freeze. No real-data fitting or model scoring precedes independent audit.

## Source, identity and eligibility

Smrke, Eiermann & Yeretzian (2024), [The role of fines in espresso extraction
dynamics](https://doi.org/10.1038/s41598-024-55831-x), Scientific Reports 14, 5612,
CC BY 4.0. Existing Puckworks digitization attributed to its source and repository
history; no source image or historical CSV changed. SOURCE.json hashes inputs,
loader, existing envelope and gates. observations.json binds CSV line identities,
not shot IDs; support.json enumerates every fold and exclusion before fitting.

The machine displayed extraction time (seconds) is the source's clock; exact
pump/first-drop origin is not supplied. Final extraction percentage uses beverage
mass and filtered-brew refractometric TDS relative to source coffee dose. Retain
that reported mass basis: no moisture/dry-coffee correction is supplied or applied.
The nominal total dose is 20 g, beverage target 40 g. f = added_fines_g / 20 g is
nominal replacement fraction (0, .05, .10, .20), not measured total fines or Q100.
The 120 µm sieve material is distinct from Q100; burr spacing is not particle
size. No PSD/EY joins, inferred grind groups, replicate-order identities, S1
shot histories, Figure 5 predicted values, or whole-source maximum-yield ceiling.

Historical notes call the 46 points extractions. This analysis calls them marker
estimates: 20/10/9/7 at 0/1/2/4 g, while the method's six unspiked and nine spiked
conditions times three imply 18/9/9/9 nominal shots (45 total). The figure does
not establish a one-to-one reconciliation. In particular the no-fines and 1 g
counts exceed nominal counts, and 4 g is short. Preserve all visible estimates;
do not manufacture hidden observations or force nominal replicate counts.

Primary rule: markers_in_blob == 1 AND an empty note. This excludes every split
marker and the partially occluded no-fines center. Counts: 12/7/7/7 (33 total),
with exclusions 8/3/2/0. All-marker sensitivity retains 46 labeled estimates;
split markers are not independently verified replication. Source image inspection
supports the explicit spatial blob map in code (blue12, mixed17 including the
partially occluded black center, black9, black23, black46). Equal blob area is
never used to assign identity. No transcription correction was made.

Training support must include at least three distinct zero-fines times; every
primary scored arm/fold must contain >=3 time-supported eligible markers. This
conservative coverage rule applies in B as well as A. No insufficient arm passes.

## Four equations and constrained objective

- M0: E_inf - A exp(-t/tau).
- M1: E_inf - A exp(-t/tau) + beta f.
- B0: b0 + b1 log(t/1 s) + b2 log(t/1 s)^2.
- B1: B0 + gamma f.

E is source-basis yield percentage points. beta/gamma units: pp per unit
replacement fraction. 0 <= A <= E_inf <= 100; .1 <= tau <= 10000 s.
Broad mathematical bounds are not measured coffee priors. Offset is not initial
inventory and tau is not diffusion time. No derivative is interpreted as an
in-shot extraction rate and no equation enters EWP governing physics.

Frozen comparison domain: 7.9 <= t <= 80 s, 0 <= f <= .2, enclosing all eligible
coordinates and perturbations. All fits enforce 0 <= predicted E <= 100 on
this rectangle. M is inherently nondecreasing. B constrains its derivative with
respect to log(t) at both domain endpoints; it is linear between them. Yield
endpoints at f=0/.2 suffice under monotonicity and linear f. The quadratic vertex
is also checked analytically if interior. Constraint tolerance 1e-7 pp is only
floating-point feasibility slack; predictions are never clipped. Requests outside
the declared domain are rejected; inside-domain predictions carry support flags.

Objective: weighted sum squared errors in pp²; intervention groups equally
weighted then observations equally within each group. Same weights, rows,
objective, constraints and masks for each parent/correction pair. No uncertainties
are treated as statistical precision weights. Internally scale f by .2, then
convert returned coefficients to the equations above. B internally centers log(t)
at 3.2 to condition its linear solve; returned b0/b1/b2 use uncentered log(t).

Deterministic fitting: SLSQP solves the convex linear-coefficient subproblem with
analytic gradient, fixed feasible initial intercept 50 and other coefficients 0,
ftol 1e-11, maxiter 2000. M profiles log(tau) over 65 equally spaced grid values
including both bounds, then bounded scalar minimization in each grid-local-minimum
bracket (xatol 1e-8, maxiter 300); smallest objective wins, fixed traversal breaks
ties. Record convergence, constraint activity, tau-bound hits, weighted Jacobian
condition, profile candidates within 1e-6 pp² of optimum and their prediction
spread across 101 domain times at f=.1. These diagnostics are not statistical
intervals. No optimizer failure is silently discarded or rescued.

Tighter calculation uses 129 profile points, SLSQP ftol 1e-13 and scalar xatol
1e-11 for every treatment and fold. Every reported error metric must change by
<=.01 pp and dispositions must agree, otherwise UNRESOLVED. Parameter stability
and prediction stability are separate; neither establishes physical parameters.

## Frozen protocols and support

A: fit M0/B0 to zero-fines only, reuse identical frozen fits for 1/2/4 g. No M1/B1.
Score only test times inside inclusive training min/max. Primary zero-fines range
9.18–68.07 s: 7/7/6 supported markers in 1/2/4 g; 4 g CSV line 27 at 79.52 s
is extrapolation. All-marker range 8.24–68.07 s: 10/9/6 supported markers.

B: four outer folds with all rows of one fines level withheld; fit all four
models on the other three levels. Principal gain comparisons use identical
supported-time points. Intervention support is a separate min/max flag; 0 g
and 4 g folds extrapolate f for M1/B1. Both 1 g and 2 g folds must be non-worse.
Endpoint extrapolation alone cannot earn gain. B is grouped internal comparison,
not a second independent experiment. No random row splits or inferred groups.

Support is recomputed from each perturbed training-time range, never target
yield. Every excluded point is retained with its extrapolation label and scored
only in separate diagnostic metrics. Three supported markers per arm are required.

## Metrics and disposition (unrounded arithmetic)

Each protocol/model/arm: n, RMSE, MAE, signed mean prediction-minus-observation
error, max absolute error, each residual and CSV line. Equal-arm RMSE is square
root of mean arm MSE (not pooled-row RMSE). Report all arms and both families.

A adequacy budgets: each supported arm RMSE <= .50 pp AND |mean error| <= .25 pp.
These are owner development thresholds, not source SDs, confidence limits or S-B.
ADEQUATE_FOR_TESTED_SOURCE_SUPPORT requires one named common model passing all
arms in every treatment. TESTED_COMMON_MODELS_INADEQUATE requires both models
failing in every treatment. Otherwise UNRESOLVED.

B material gain over each own parent requires equal-arm RMSE reduction >=20%
and >=.10 pp, interior folds both non-worse, and no arm worsens >.10 pp RMSE.
MATERIAL_OUT_OF_FIT_GAIN_FOR_TESTED_CORRECTION requires a named correction to
pass every treatment. NO_MATERIAL_GAIN_FOR_TESTED_CORRECTIONS requires neither
correction to pass any treatment. Mixed source dispositions give UNRESOLVED.
M/B outcomes are always retained separately; no scored-target model selection is
represented as prospective. All zero/insufficient support is UNRESOLVED.

## Tested digitization sensitivities

Source image axes: x ticks at approximately 153/399/645/891/1137 pixels for
0/20/40/60/80 s; y at 969/763/558/353/148 pixels for 16/18/20/22/24 pp.
A pixel is about .0814 s/.00975 pp; linear calibration is subpixel in the
historical notes. Isolated-marker allowance is one pixel plus CSV rounding,
rounded outward to .09 s/.011 pp. For ambiguous positions use the notes' .30 s/
.05 pp center allowances; applying these to all split/occluded centers is an
explicit conservative tested treatment, not measured error for each marker.

Each inclusion treatment has central coordinates plus eight perturbations:
four sign corners (+/-t, +/-E) shifting all centers together, and four sign
corners with deterministic position signs from SHA256(position identity)'s first
byte parity. Genuine connected/occluding positions share signs across colors;
other centers use CSV line identity. Keep inclusion and labels fixed; shift every
included training/test coordinate, refit under the same folds and score only after
prediction freeze. This is 18 treatments, each computed standard and tight.
No row bootstrap, independent-replicate claim, SE, p-value, or confidence interval.
Ranges are labeled tested digitization sensitivities, not exhaustive bounds.

## Execution, outputs and claims

`prepare` only loads/hashes metadata and establishes eligibility/support.
`fit-predict` requires actual independent AUDIT.json bound to the precise reviewed
head/tree, base applicability, FREEZE.json and its file hashes. Fit sees training
Observation objects; predict accepts only Covariate objects (no yield field).
All predictions are exclusively written before scoring, followed by a hash receipt.
`score` verifies immutable input/prediction identities and exclusively writes metrics
and residuals. Existing artifacts cannot be overwritten by these commands.

Schemas: observations.json = ordered serialized Observation records;
support.json = treatment/protocol/held-level counts, ranges, kept/excluded IDs;
predictions.json = treatment/precision/protocol/held-level/model -> fit record and
covariate/prediction/support records. metrics.json = standard/tight reports,
per-family gain, numerical differences and two verdicts; residuals.json includes
individual predictions, observations and signed errors. Synthetic verification
and exact environment are recorded before FREEZE. Figures consume these artifacts
only, show ambiguity and endpoint-curve/support labels, and never full-data refits.

Development: robust adequate common response/no gain retains the simpler tested
source response; material gain retains a fines-associated endpoint constraint for
separately authorized mechanistic discrimination; failure without useful gain
rejects these forms without a missing-mechanism inference; instability names the
unresolved quantity. No automatic adoption, physical-mechanism identification,
permeability estimate, EWP/Cameron/radial-E2 validation or universal coffee claim.

PHYSICAL_VALIDATION_OF_EWP=NOT_ESTABLISHED
SMRKE_CROSS_SETUP_S_B=UNCHANGED
PRODUCTION_DEFAULTS_AND_LOCK=UNCHANGED
NO_SUCCESSOR_EXECUTION_AUTHORIZED
