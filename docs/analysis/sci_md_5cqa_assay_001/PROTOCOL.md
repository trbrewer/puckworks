# First-assay-conditioned 5-CQA interval delivery

SCI-MD-5CQA-ASSAY-001 / G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
The owner authorizes bounded implementation, FIT-only development, independent
exact-freeze review, one evaluation and one draft Puckworks PR. EWP is read-only.
No production registration/adoption, defaults/locks, merge, release, purchase,
external contact, acquisition, laboratory operation or successor is authorized.
This protocol, model card, source roles, thresholds and budgets are committed
before real fitting. Existing G1 receipts and numerical machinery are reused.

## Task selection and novelty

NEW_INFORMATION: each query shot's original fraction-1 5CQA assay is now an
explicit input, alongside original m1/m2. The observations already exist; their
role changes locally. #297 mass-only E0/D0 and #298 early-TDS S0/S1/S2 never used
this chemical input. Their complete negative primary results remain unchanged.
DECISION_IF_POSITIVE: identify the least-complex adequate research arm and
separately test whether L1 earns replacement over both D0 and A1.
DECISION_IF_NEGATIVE: reject only the tested first-assay families on qualified
evidence and stop. DECISION_IF_NULL_OR_BLOCKED: retain any adequate simpler arm
and the exact support/source/numerical/review limitation; no rescue experiment.
GRINDER_TO_CUP_LINK: conditional delivery of a named species in later measured
beverage intervals. REPEATED_BLOCKER: direct query-shot chemistry changes the
information entering the prior negative tests; inventory identifiability and
hydraulic prediction are outside this task. LOWER_COST_ALTERNATIVE: analytical
normalization A1 and frozen E0/D0, no CFD or new measurement. All three task
selection tests pass for this owner-selected bounded question.

Generic early-assay conditioning and amplitude normalization are established
methods. Novelty is their tested usefulness for this exact species, information
contract, target and separated campaign, not first-ever 5-CQA modeling. This
comparison identifies no transport, equilibrium, inventory, roast-batch or
physical shape mechanism. #296 consolidated-bed scalar rescaling remains closed:
A-480 requires multiplier >=0.5261544; D-360 requires <=0.1385720.

SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
No target-blind, independent external validation, sensor-free capability, causal
recipe response, real-time HPLC control or joint TDS/composition closure claim.
Physical validation and analytical uncertainty remain NOT_ESTABLISHED.

## Source and information roles

Only registered PANNUSCH2024_MENDELEY_FULL_REPOSITORY through the existing local
resolver/configuration is used. Preserve #297's eight source and ten register
bindings, original source data/exclusions and all predecessor artifacts. No
acquisition, alternate lineage, digitization, imputation or missing-prefix repair.
Species is exactly source analyte 5CQA, MAT cAlcaloids(:,3), HPLC Y using area I.
Not CQA_sum, generic CGA, an isomer, caffeine or TDS. Named concentration mg/g
measured liquid converts to q kg/kg by /1000; original mE g converts to kg by
/1000; analyte kg converts to mg by *1e6; average mg/g=1000*M_kg/(b-a).

Extend the source projection locally for fraction 1; never loosen old readers.
Check all 45 FIT and 24 PRED first assays against unrounded MAT cAlcaloids(1,3),
original mE(1), cached HPLC mass and exact calibration/dilution formula:
FIT mass_mg=(I-78.923)/(24.513*1000)*C*B;
PRED mass_mg=(I+88.067)/(26.383*1000)*C*B.
Require positive calibration sample mass/dilution, nonnegative finite mass,
mg/g mass/mE agreement within 1e-12, public concentration rounding agreement
within 5.001e-9 mg/g and public vial mass agreement within 5.001e-9 g.
These tolerances reconcile exports, not analytical uncertainty. Use original
unrounded q1 and FIT outcome values. Require exact campaign/shot/fraction/source
identities, units and valid status. The three registered fraction-2 HPLC spills
FIT-E03-R1, FIT-E11-R3 and FIT-E14-R3 do not supply zeros or first assays.
Unexpected missing first assays or changed support gives SOURCE_CONTRACT_BLOCKED
with exact identities; never shrink the cohort or add another assay.

Prediction input: measured m1_kg, m2_kg and q1_kg_kg ONLY. Future chemistry,
fraction-2 5CQA, TDS, other analytes, conditions/shot IDs, recipes and temperature/
flow programs are not features. IDs join records only. Inference accepts strict
species/units and rejects extra fields. Keep first-assay, FIT outcome and later
PRED outcome projections distinct. Pre-score PRED suffix queries use measured
geometry and bound source identities; later chemical values never enter them.
All original source cells required for the later outcome role reconcile at the
single approved outcome join; immutable source hashes bind them before fitting.

FIT_2021_12: 15 original designs, 45 shots, 180 intended fractions 3/5/7/10,
177 supported intervals. Preserve every original slot/reason. PRED: 8 conditions,
24 shots, 96 intended slots. Primary C01/C02/C05/C06: 12 shots, 48/48; temperature
C03/C04: 6 shots, 24/24; flow C07/C08: 6 shots, 23/24. Missing flow slot is C07;
C08 mass feature extrapolation remains retained. Original cumulative coordinates
include every intervening unassayed vial; never infer missing mass from flow,
time or the sum of assayed vials. Forecast anchor=m1+m2. Final hard upper domain
0.06971540000000001 kg. Fold domains use training-only supported endpoints.

Physical-shot rows stay together and all replicates of each original design
stay in the same fold, using established identical-design grouping. Pannusch and
Schmieder are shared lineage, not independent datasets. Lot/roast joins remain
unknown. No inventory inference or whole-cup closure follows from modeled gaps.

## Exactly four arms

E0/D0: load the exact #297 model files through its unchanged runtime. No fitting,
calibration, replacement parameters or predecessor scientific scoring commands.
#297 producer cadb7aeaa00630ad311970610ec5763ad4ffc9a3 and freeze
 da6023c0e0077f5f89d2a7ed877b1a3ff26c8c4bc6935b9263ecdf798184b7a1 remain fixed.
#298 producer 5fb08749315ff145f7f68d57b055dd5a79c95f5d and freeze
 f7495e5c75f56698507126be89be1dd4c9a464227c8d7461f0d8655dec1859da remain fixed.

A1: fixed tau=0.02319173692244203 kg from E0 semantic SHA-256
f1c27d0c942234761a274ee52e38a9912fe0e5a47ae72269d43103c646a9106d.
For first interval-average assay q1 and mass m1:
A=q1*m1/[tau*(-expm1(-m1/tau))];
M[a,b]=q1*m1*exp(-a/tau)*(-expm1(-(b-a)/tau))/(-expm1(-m1/tau)).
Use the algebraically identical stable amplitude-times-kernel computation. No
optimizer, new fitted global coefficient or decay adjustment. This extends the
fixed exponential mathematically to [0,m1]; old E0 never established validity
in that early interval. q1 is an interval average, not a point value. Finite
positive masses and 0<=q1<=1 are required; zero q1 gives zero delivery. Reject
nonfinite amplitude or A outside [0,1]; never clip. Training feature summaries
flag extrapolation without fitting A1. No unbiased A1 leave-design-out claim:
its decay was learned using all FIT observations.

L1: same five uniform knots on [0,B_train] and piecewise-linear-logit numerical
geometry as D0. x=[1,z_m1,z_m2,z_q1]; eta_j=theta_j dot x; q(b)=sigmoid(linear
interpolation of eta); M[a,b]=integral q(u)du. Exactly 20 coefficients in [-20,20].
Fixed scales [.01 kg,.01 kg,.01 kg/kg]. Equal-design/equal-shot feature means and
feature minima/maxima come from training shots only. No extra knots, interactions,
random effects, recipe features, mechanisms, ensembles or family search.
A1/L1 tests fixed-shape normalization versus a learned conditional curve; it does
not isolate a physical shape mechanism or guarantee interpolation of q1 by L1.

## FIT development and numerical qualification

Only FIT later outcomes train L1. Each design has equal total weight, each shot
within design equal weight; measured interval mass normalizes weights within
shot. Data residual=(1000/.25)*(predicted interval-average q-observed q)*sqrt(w).
Preserve D0 penalties EXACTLY on theta[:,:3]: slopes theta[:,1:3]*sqrt(lambda/10)
and second knot differences(theta[:,:3])/.25^2*sqrt(lambda/9). Append separate
assay-column penalties theta[:,3]*sqrt(lambda/5) and second differences(theta[:,3])
/.25^2*sqrt(lambda/3). Setting assay coefficients to zero reproduces D0's
fixed-lambda objective, without weakening old-column regularization.

Fifteen leave-whole-design-out folds. Fixed lambdas .0001,.01,1,100. Three starts
per fit: intercept logit(clip(training weighted q,1e-8,1-1e-8)) plus ramp -1,0,+1
in order across linspace(-1,1,5); all feature slopes zero. Clipping is only for
initialization. SciPy least_squares trf, tr_solver=exact, loss=linear, jac=2-point,
diff_step=1e-6, x_scale=1, ftol=xtol=gtol=1e-10, max_nfev=8000, with a separate
hard maximum of 8000 actual residual calls including finite differences.
Retain initial/final/last coefficients, failures, convergence, boundary indices
(distance <=1e-7), objectives, actual/Jacobian calls, wall and peak RSS per start.
Choose lowest finite converged objective; exact ties use start order. No extra
starts or bounds. All three attempts must complete and converge for a qualified
fit; selected boundary limitations are retained and prevent an unqualified claim
of a defensible interior choice. No rescue search follows a failed choice.

Freeze support from training/held geometry before fitting, identical for every
lambda. Keep unsupported slots/reasons and original denominators. Held shot R
uses supported measured-mass weights, averaged equally over shots then designs.
Select largest lambda within 1e-6 mg/g of minimum among fully qualified comparable
candidates. Conservative numerical bounds must prove the choice invariant;
otherwise report unresolved selection. Development is selection, not external
or unbiased nested validation. Refit the selected lambda once on all eligible FIT
shots, three starts. Maximum 15*4*3+3=183 real starts. E0/D0/A1 global fits=0.

Reuse knot-split 64/128-point Gauss-Legendre and independent adaptive integration,
epsabs=1e-14 kg, epsrel=2e-13, limit=200. A1 is analytical; adaptive comparison
still applies. Allowance=max(|I64-I128|,|I64-Iadaptive|+err,|I128-Iadaptive|+err)
+128*epsilon*(width+|I64|). Preserve fraction-3 shared-anchor reconciliation only
within four ULPs, adding twice the displacement. Total allowance <=1e-9 kg;
retain failures, never increase tolerances. Reject nonfinite/reversed/before-anchor
or outside-hard-domain intervals; zero width gives zero mass and undefined mean.
Feature extrapolation is flagged and retained without clipping or favorable
exclusion; numerical support is not an in-domain validation claim.

## Independent freeze and one evaluation

Freeze all 384 records (four arms x 96 original suffix slots), including unsupported
records, models, strict input projections, exact code/protocol/runtime and source
identities before outcome join. A genuinely independent reviewer, not implementer,
approves the exact producer/tree/freeze; identify automated review as nonhuman.
Use existing G1 review receipt schema. If unavailable: READY_FOR_INDEPENDENT_REVIEW,
no score and no manufactured receipt. One exclusive score-start receipt precedes
the sole new-task PRED outcome join. Failed/completed receipts prohibit retry.
No predecessor scoring entry points. Check E0/D0 against their retained aggregate
results within combined numerical bounds (arithmetic floor 1e-12 mg/g), preserving
their conclusions. No post-score retuning or repeated scientific evaluation.
Scientific defects invalidate affected results; later report corrections read
retained evidence only. Verify replays inference only; report reads retained scores.

For each shot R=sqrt(sum(w*error^2)), B=sum(w*error), w=measured interval mass /
total scored mass. Conditions average R and abs(B) equally over original three
shots; absolute bias is taken BEFORE shot averaging. Panels average conditions
equally. Every primary condition must have R<=.25 mg/g and mean abs(B)<=.125 mg/g.
A positive all-primary claim needs complete qualified 48/48 support.

Material comparisons: A1/E0, A1/D0, L1/D0, L1/A1. Each requires candidate all-primary
adequacy AND balanced R reduction >=.05 mg/g AND relative reduction >=15% AND
definite R improvement in >=3/4 conditions AND balanced mean-absolute-bias
worsening <=.025 mg/g. L1 earns the complex route only if BOTH L1/D0 and L1/A1
pass. Report adequacy separately. These budgets are engineering criteria, not
assay uncertainty, sensory/health limits or confidence intervals.

Convert mass allowances to mg/g using measured interval mass; propagate shot R
by weighted L2, B/abs(B) by weighted L1, then equal-shot/condition averages.
Paired allowances add; relative gain uses candidate_R<=.85*comparator_R with
both allowances. Conservative bound proves PASS; definite violation FAIL;
overlap UNRESOLVED. A conjunction fails if any criterion definitely fails.
Secondary temperature/flow cannot rescue primary failures. 23/24 flow never
becomes complete flow. Missingness alone is not scientific failure; a valid
complete-shot nonnegative error lower bound can establish full-condition failure.

Disposition order: source-contract failure => SOURCE_CONTRACT_BLOCKED; exceeded
execution budget => EXECUTION_BUDGET_EXHAUSTED; missing review =>
READY_FOR_INDEPENDENT_REVIEW; unqualified/support/ambiguous required decisions =>
SUPPORT_OR_NUMERICAL_RESULT_NOT_ADJUDICATED. With qualified primary evidence,
L1 adequate and both gains PASS => L1_ADEQUATE_AND_EARNED; A1 adequate and learned
increment not established => A1_ADEQUATE_LEARNED_INCREMENT_NOT_ESTABLISHED;
otherwise any adequate new arm => ADEQUATE_INCREMENT_NOT_ESTABLISHED; definite
failure of both new families => TESTED_FIRST_ASSAY_FIVE_CQA_FAMILIES_INADEQUATE.
Always retain adequacy and gains separately, including numerical ambiguity.
A failed optimizer, missing source or reviewer is never a negative scientific result.

## Execution and delivery

Fresh task start 2026-09-29T12:22:32Z; six-hour ceiling 2026-09-29T18:22:32Z,
excluding externally pending hosted CI/reviewer availability. One worker and one
BLAS/OpenMP thread; <=183 real starts; <=8000 calls/start; <=60 minutes real
fitting wall span; <=12 GiB address space; <=5 GiB cumulative private evidence.
Durable exclusive receipts and task clock persist across all corrections; no
counter reset, fresh-directory evasion or inherited expired deadline. Bounded
pre-score correction within this same family/budget requires exact review.

Stage interface: prepare, develop, freeze, score --review, verify, report, all
with --out. First four are one authorized execution, not casual replay commands.
Saved inference requires no optimizer, source workbook, private directory or
network. Synthetic example uses no corpus. Required normal selector, registry,
lint/mypy, generated-state/data-guide/README, historical-integrity, claim/evidence,
source/static/JSON/shell/scope/secret checks and predecessor regressions run.
Existing skips, acknowledged exceptions and hosted CI are separately reported.
No historical WP6 repair or unrelated baseline-failure repair is authorized.

Public deliverables are compact protocols, saved models, aggregate development,
freeze/review, condition results/bounds, qualification, handoff and commands.
Originals, observations, individual predictions and detailed logs remain external.
Source-derived models/results: Pannusch/Schmieder, Mendeley DOI
10.17632/y2tz67f6ry.1, CC-BY-NC-3.0, separate from first-party software licensing.
