# Second-assay value and minimum tested early-assay contract for 5-CQA delivery

SCI-MD-5CQA-ASSAY-002 / G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
The owner authorizes this bounded implementation, source verification, synthetic
checks, FIT development, independent exact-freeze audit, one frozen evaluation,
reporting and one Puckworks draft PR. EWP is read-only. No registration, defaults,
dependency locks, production adoption, merge, auto-merge, release, native runs,
acquisition, laboratory operation, external contact, paid service or successor.
This protocol and model/input/source contracts are committed before real fitting.

## Decision and scope

Within the fixed five-knot conditional 5CQA family, does original fraction 2,
alone or alongside original fraction 1, adequately predict fractions 3/5/7/10?
Separately determine every arm's adequacy, single-assay placement value, and the
increment earned by retaining both assays instead of either alone.
NEW_INFORMATION: original fraction-2 5CQA becomes a permitted conditional input.
DECISION: retain only the tested adequate research contracts; require both
increment comparisons before earning the two-assay route. Negative rejects only
these families; null or blocked retains exact limitations and stops.
GRINDER_TO_CUP_LINK: named chemical delivery conditional on measured early inputs
and supplied beverage-mass intervals. LOWER_COST_ALTERNATIVE: matched single-assay
controls; Python only. The three-test selection gate passes for this explicitly
selected task. Direct q2 changes information relative to previous failed tests;
there is no inventory/closure rescue or repeated-blocker mechanism search.

#299 tested q1 normalization and learned q1, never q2. #298 used early TDS,
not fraction-2 5CQA; MASS-DELIVERY-006 tested two TDS assays. EWP #105 addresses
shared/species-specific production parameters and is excluded. #296 scalar
permeability rescaling is closed. The selection-stage rank-5 check on five FIT
shots is evidence of non-affine duplication only, not coefficient identifiability,
independent errors or predictive usefulness. L1M is a matched-cohort control,
not a refit or replacement of #299's frozen conclusion. No task search is repeated.

## Source, cohort and information contract

Use the registered PANNUSCH2024_MENDELEY_FULL_REPOSITORY resolver, eight original
file identities and ten normalized register bindings. SOURCE_IDENTITIES.json
preserves the inherited authority. No downloads, alternate source or broad census.
Species exactly 5CQA: MAT cAlcaloids(:,3), HPLC Y using area I. Never CQA_sum,
generic CGA, TDS or other analytes. Campaign-specific HPLC analyte mass (mg):
FIT=(I-78.923)/(24.513*1000)*C*B; PRED=(I+88.067)/(26.383*1000)*C*B.
Require positive sample mass/dilution, finite nonnegative chemistry, formula/cache
and cache/mE-to-MAT agreement <=1e-12 mg/g, exported concentration agreement
<=5.001e-9 mg/g and vial-mass agreement <=5.001e-9 g. These are reconciliation
tolerances, not analytical uncertainty. Real computation uses unrounded originals.
Units: vial g/1000=kg; assay mg/g/1000=kg/kg; species kg*1e6=mg;
interval average mg/g=1000*species_kg/interval_beverage_kg.

FIT_2021_12 original denominator: 45 physical shots, 15 whole original designs,
180 suffix slots. Exclude FIT-E03-R1, FIT-E11-R3, FIT-E14-R3 from ALL arms because
original fraction 2 is registered INVALID_SPILL. Source zero assignments are not
nondetects or valid zero assays. Preserve exclusion identities and original slots.
Derive the common cohort by joining exact shot/fraction/species validity records:
42 eligible shots, 15 designs, 168 intended suffix slots, 165 with qualified mass
prefixes. The three unavailable prefixes remain FIT-E01-R3 fractions 7/10 and
FIT-E06-R3 fraction 10. Unexpected counts/identity/status changes block execution.

PREDICTION_2022_03: all 24 original physical shots and 96 suffix slots. Primary
C01/C02/C05/C06=12 shots/48 slots; temperature C03/C04=6/24; flow C07/C08=6/24.
Preserve original C07 unsupported fraction-10 slot and C08 feature extrapolation.
The final domain is derived only from supported eligible FIT endpoints, never
PRED, with hard ceiling 0.06971540000000001 kg. Fold domains are training-only.
Cumulative coordinates include ALL intervening original vial masses, even
unassayed ones. No nominal-flow mass, inferred prefixes, clipping or imputation.

Separate role projections: FIT early assays and later targets; PRED early assays;
PRED coordinate-only suffix queries; later PRED outcomes only at the approved
single join. Recipe, flow, temperature, batch, TDS and other chemical fields are
forbidden. IDs are join/split keys, never predictors. Poisoned disallowed values
must not affect projections, initialization, fitting or frozen predictions.
Pannusch/Schmieder is one shared lineage. Whole original designs stay together;
repeated fractions are not independent shots. Lot/roast joins remain unknown.

## Exactly three learned arms

L1M: m1,m2,q1; five knots by four coefficients=20.
L2M: m1,m2,q2; five knots by four coefficients=20.
L12: m1,m2,q1,q2; five knots by five coefficients=25.
All forecast from m1+m2. L2M requires first-vial MASS, not its chemical assay.
Both chemical inputs are measured interval averages used as covariates, not
point concentrations or fitted kinetic states; no forced assay interpolation.

q_hat(m)=expit(sum_j H_j(m/B)*theta_j dot [1,z]). Five equally spaced knots on
[0,B]; piecewise-linear logit interpolation. Fixed feature scales are .01 in
corresponding SI units. Center shared columns identically using training-only
equal-design/equal-shot weighted means; minima/maxima use the same training
partition. Compute each mean column independently so shared transforms are
identical across arm widths. Coefficients [-20,20]. No additional knots,
interactions, transforms, hyperparameters, mechanistic rates or per-shot fitting.

Data residual=(1000/.25)*(interval-average predicted q-observed q)*sqrt(w).
Each design has equal total weight, shots within design equal weight, supported
suffix windows within a shot weighted by original measured interval mass.
Preserve original penalties: theta[:,1:3]*sqrt(lambda/10), and second differences
of theta[:,:3]/.25^2*sqrt(lambda/9). For EACH chemical column separately append
its five coefficients*sqrt(lambda/5) and three second differences/.25^2*
sqrt(lambda/3). Never renormalize old penalties by new column count. At fixed
lambda, zeroing L12 q2 exactly nests L1M; zeroing q1 nests L2M, modulo floating
arithmetic covered by the numerical qualification. Test objective and predictor.

Historical E0/D0/A1/L1 models, retained predictions/results and verdicts remain
immutable reference controls. Verify #299 publication c2bea543f21d9d43ad71dc23a44ea5f8216e8c9b,
producer 35fe284b386f0bec468956c4be9508dcb06ddf43 and freeze SHA-256
401b3a58fe6ca275b1482c1eb4a8146bdad8952bcbabf8bf4a1c7e96f3ed5b68.
Reuse retained records/results without refitting, regenerating or rescoring them.
They do not supply matched-cohort information-ablation comparisons.

## FIT-only development and numerical qualification

Fifteen whole-design held-out FIT folds; all three arms use identical cohort,
coordinate-derived comparison masks and folds. Compute transforms/domain/starts
using each fold's training partition only. For each arm independently test fixed
lambdas [.0001,.01,1,100]. Three deterministic starts in order -1,0,+1: zero
feature slopes; intercept logit(clip(weighted training q,1e-8,1-1e-8)) plus
ramp*linspace(-1,1,5). Only initialization clips. SciPy least_squares: trf/exact,
linear loss, jac=2-point, diff_step=1e-6, x_scale=1, ftol=xtol=gtol=1e-10,
max_nfev=8000 plus an independent cap of 8000 ACTUAL residual calls including
numerical Jacobians. Retain every attempt, initial/final/last parameters,
objective, convergence, boundary indices (distance <=1e-7), actual/Jacobian calls,
time and memory. All three starts must converge; choose lowest finite converged
objective, exact ties by start order. Selected boundary solutions are unresolved.

Select largest lambda within 1e-6 mg/g of minimum balanced held-design shot R
among fully qualified candidates. Numerical lower/upper bounds must prove choice
invariant, using #299's conservative rule. No architecture, threshold or source
selection from PRED outcomes. Development is FIT selection, not unbiased nested
validation. Final fit uses the same complete eligible FIT cohort, three starts.
Maximum 549 starts=3*(15*4*3+3), at most 183 per arm. No retries/rescue search.

Use inherited knot-split 64/128-point Gauss-Legendre plus independent adaptive
integration (epsabs=1e-14 kg, epsrel=2e-13, limit=200).
Allowance=max(|I64-I128|,|I64-Iadaptive|+err,|I128-Iadaptive|+err)
+128*epsilon*(width+|I64|). Only original fraction-3 shared-anchor discrepancies
within four ULPs may reconcile to m1+m2; retain original coordinates and add
twice the displacement. Every interval allowance <=1e-9 kg. Never clip to qualify.
Reject wrong units/species, nonfinite/reversed/before-anchor/out-of-domain queries.
Zero-width gives zero delivery and undefined average. Nonnegative concentration
bounded by one follows from expit; extrapolated features remain flagged.

## Exact freeze, review and one score

Commit and freeze code/contracts/source bindings, all three models, permitted
PRED early inputs, all 288 prediction/status slots and original coordinates before
later PRED chemistry. The existing independent G1 reviewer must be separate from
the implementer/fitter and approve the actual head/tree/freeze. Label nonhuman
review explicitly; no fabricated or template approval. A missing/blocked review
prevents score. One exclusive durable score-start receipt precedes exactly one
new-task outcome join/score; failed or completed attempts prohibit retry.
Pre-score software corrections stay within existing bounded review rules and
preserve superseded evidence. No post-score refit, feature/threshold change,
favorable subset, prediction regeneration or second score. Verify only replays
saved inference/identities; report only reads retained scores. A material defect
after score is reported honestly and stops affected execution.

## Decision matrix

Shot R=measured-interval-mass-weighted concentration RMSE (mg/g);
B=mass-weighted signed concentration bias. Condition R is equal-shot mean R;
A is equal-shot mean abs(B), never abs(mean B). Primary balanced metrics average
four conditions equally. Every primary condition must have R<=.25 mg/g AND
A<=.125 mg/g with complete qualified primary support. These are engineering
budgets, not assay uncertainty, confidence intervals, sensory or health limits.
Propagate interval mass allowances to mg/g, shot R by weighted L2, bias/absolute
bias by weighted L1, then equal-shot/condition averages. PASS requires conservative
bounds; definite violation is FAIL; overlap UNRESOLVED. Comparisons add allowances.

Report L2M/L1M (single-assay placement), L12/L1M (add second assay), and L12/L2M
(retain first assay) separately. A comparison earns material value only if the
candidate is adequate AND balanced R reduction >=.05 mg/g AND >=15% AND definite
condition R improvement in >=3/4 primary conditions AND balanced absolute-bias
deterioration <=.025 mg/g. Relative criterion is candidate_R<=.85*control_R with
both numerical allowances. The two-assay route requires BOTH L12 comparisons.
No preference from lower nominal RMSE alone or a gain by an inadequate model.

Summary order: actual source/review blocker => BLOCKED_SOURCE_CONTRACT /
BLOCKED_REVIEW. Definite inadequacy of all arms, including rigorous complete-shot
nonnegative error lower bounds with original denominators, remains
TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE even if another slot lacks support. Otherwise
incomplete primary support => SOURCE_SUPPORT_INCOMPLETE; required numerical or
decision ambiguity => NUMERICAL_OR_DECISION_UNRESOLVED. Qualified L12 adequate and
both comparisons PASS => TWO_ASSAY_MAPPING_EARNED. Any adequate single-assay arm
and no earned two-assay route => SINGLE_ASSAY_ADEQUATE_NO_EARNED_TWO_ASSAY_COMPLEXITY.
Only L12 adequate without earned increments => ADEQUATE_INCREMENT_NOT_ESTABLISHED.
Always retain complete adequacy/comparison matrix and coverage; summaries do not
replace it. Secondary panels cannot rescue primary failure. Missing support alone
is not scientific failure. A tested single-assay success is not universal sufficiency.

## Execution, API and handoff

Actual task start 2026-09-29T16:34:51Z; hard deadline 2026-09-29T22:34:51Z.
The persistent clock never resets across restarts. One fitting worker and one
BLAS/OpenMP thread; <=60 minutes elapsed real-fitting phase, <=12 GiB address
space and <=5 GiB task-private evidence. Failed/incomplete attempts consume budget.
No predecessor deadline is edited. Baseline failure blocks implementation without
an unrelated repair. Run #299 normal/historical/registry/static/type/generated/
claim/evidence/data-guide/README/source/privacy/packaging checks and affected
predecessor regressions; no protected historical execution through QA.

Strict immutable L1M/L2M/L12 inputs reject forbidden fields. Saved models and
conditioned states use exact schema/content identities and deterministic replay.
Model.load needs no source, private evidence, network or optimizer. Each state
predicts independent supplied mass intervals and remaining_5cqa(stop_mass_kg),
returning species kg/mg, average mg/g, support, numerical allowance and feature
extrapolation. Remaining means modeled delivery to that stop, not puck inventory;
query mass is supplied, not hydraulically predicted. Include source-free example.
Six-stage CLI: prepare, develop, freeze, score --review, verify, report; each --out.
Only verify/report repeat after completion. Actual private paths and commands,
failures, attempt counters and receipts remain outside Git. Public aggregate/model
artifacts retain Pannusch/Schmieder CC-BY-NC-3.0, DOI 10.17632/y2tz67f6ry.1,
separately from first-party software licensing. No individual observations or
predictions, detailed shot results, originals or private logs are published.

SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
PHYSICAL_VALIDATION=NOT_ESTABLISHED; ANALYTICAL_UNCERTAINTY=NOT_ESTABLISHED;
PRODUCTION_ADOPTION_AUTHORIZED=false; MERGE_AUTHORIZED=false; NATIVE_EWP_RUNS=0;
NO_SUCCESSOR_AUTHORIZED. No transport/equilibrium/inventory/batch causation,
hydraulic prediction, measured whole-cup closure, joint TDS closure, real-time
HPLC-control or universal minimum-assay claim. Either qualified result ends here.
