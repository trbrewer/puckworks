# Mass-only 5-CQA interval delivery: fixed comparison

SCI-MD-5CQA-DELIVERY-001; G1; NO_GOVERNING_PHYSICS_CHANGE; RESEARCH_ONLY.
The owner task authorizes implementation, bounded FIT development, one independent
exact-freeze review and one frozen score without a second owner authorization.
No production adoption, registry/default change, EWP change, merge, acquisition,
additional family or successor is authorized. Protocol committed before fitting.

## Question and source roles

Can measured mass coordinates alone predict absolute later-fraction 5-CQA?
Compare exactly E0, a shared global exponential, and D0, the inherited
mass-conditioned spline retrained on 5CQA only. D0 advantage concerns curvature
and mass conditioning together; this comparison cannot identify either cause.
No claim of first-ever 5-CQA modeling, a newly discovered declining trajectory,
identified kinetics/transport, or new independent validation is permitted.

SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE. The later campaign is exposed
evaluation data, not a fresh blind holdout. Pannusch and Schmieder share lineage
and are counted once. Physical validation and assay uncertainty remain
NOT_ESTABLISHED. These engineering budgets are not assay, health or sensory limits.

Resolve PANNUSCH2024_MENDELEY_FULL_REPOSITORY through the existing external-data
configuration. SOURCE_IDENTITIES.json binds eight original DoE, preparation,
HPLC and MAT files and ten accepted registers. No replacement source or download.
5CQA is MATLAB cAlcaloids(:,3), HPLC column Y (area I), not CQA_sum or another
isomer. FIT calibration is (I-78.923)/(24.513*1000)*dilution*sample_mass_g;
PRED is (I+88.067)/(26.383*1000)*dilution*sample_mass_g, giving mg/fraction.
Divide by original fraction mass in g for mg/g. Reconcile original arrays and
HPLC formulas against normalized tables within their eight-decimal rounding.
Use original, unrounded, source-authorized concentrations in fitting/scoring;
rounding is not new measurement uncertainty. Preserve validity, spills,
missingness and censor semantics. No substituted values or filled mass prefixes.

Internal beverage/analyte mass is kg; concentration kg/kg. q=mg/g /1000;
beverage_kg=g/1000; analyte_mg=1e6*analyte_kg;
average_mg_g=1000*analyte_kg/interval_beverage_kg.

## Inputs and cohorts

Only original first-vial mass m1, second-vial mass m2, and requested cumulative
mass endpoints enter inference. No chemical assay, TDS, other analyte, time,
temperature, pressure, flow, recipe, grinder dial, inventory, dose-normalized
closure or query-target amplitude/decay adjustment is permitted.
The qualified original-vial cumulative-mass adapter includes every intervening
unassayed vial. Never sum assayed vials alone or replace mass with nominal flow.

FIT_2021_12: 15 original designs, 45 physical shots, fractions 3/5/7/10,
180 original slots, 177 qualified windows. Retain three unavailable measured
prefixes with their reasons. Each design requires at least two physical shots
with at least three supported supervised windows. PREDICTION_2022_03 primary:
C01/C02/C05/C06, 12 shots, 48/48 windows required. Secondary temperature C03/C04:
6 shots/24 windows; flow C07/C08: 6 shots/24 original, 23 supported windows.
Unexpected primary loss or changed source semantics stops the source contract.
No random fraction splits; whole original designs and physical replicates remain
intact. The domain is derived from retained FIT endpoints; unchanged source
geometry gives upper support 0.06971540000000001 kg.

PRED integrity checks may silently verify source identities, formulas,
finite/valid status and normalized-table agreement, emitting only aggregates.
PRED values/patterns cannot affect fitting, initialization, bounds, support,
preprocessing, selection or predictions. Separate FIT chemistry, coordinate-only
queries/predictions and the sole approved outcome join into private artifacts.

## Exactly two model arms

E0: q(m)=A exp(-m/L); one pair shared across every shot. A in [0,1] kg/kg;
L in [0.001,1.0] kg. m1/m2 establish the permissible anchor only. Integral
A*L*exp(-a/L)*[-expm1(-(b-a)/L)] is exact; use no midpoint approximation.
Fit A and log(L), using exactly initial L=0.01,0.03,0.10 kg in that order.
For each initial L let h_i=integral of exp(-m/L) over [a_i,b_i] divided by
b_i-a_i. Initialize A=clip(sum(w_i*h_i*q_i)/sum(w_i*h_i^2),0,1).
There is no E0 hyperparameter, penalty or shot/condition/campaign fit.

D0: five uniformly spaced knots on [0,B], B=max retained training endpoint.
At knot j, logit_j=theta[j] @ [1,(m1-mean1)/0.01,(m2-mean2)/0.01].
Interpolate logits linearly, then apply logistic. Exactly 15 coefficients,
each in [-20,20]. No predecessor coefficients or TDS parent. Means are
training-only equal-design/equal-shot weighted masses; minima/maxima are
training-only. Feature extrapolation stays visible and never excludes a window.
Inherited penalty: append theta[:,1:] times sqrt(lambda/10), and flattened
second knot differences divided by 0.25^2 times sqrt(lambda/9).
Lambda grid: [0.0001,0.01,1,100]. Three deterministic starts have zero feature
slopes; intercept=logit(clip(weighted training q,1e-8,1-1e-8)) plus ramp
(-1,0,+1)*linspace(-1,1,5). Clipping is initialization-only.

Both arms fit integrated interval averages. Weights give equal total weight
to each original design, equal physical-shot weight within design, and measured
interval-mass weights normalized within shot. Data residuals are
(1000/0.25)*(predicted_q-observed_q)*sqrt(weight). Fixed scipy least_squares:
method=trf, tr_solver=exact, loss=linear, jac=2-point, diff_step=1e-6,
x_scale=1, ftol=xtol=gtol=1e-10, max_nfev=8000; enforce an additional ceiling of
8000 actual residual calls including numerical Jacobians. Retain every start,
failure, boundary solution, objective, call count and wall time. Lowest finite
converged objective wins; exact ties use start order. No bound expansion/rescue.

## Development and numerical qualification

Run 15 whole-design leave-one-out folds. Preprocessing, means/ranges, domain,
knots and support come only from retained training rows. Freeze identical
coordinate-only held-window masks across arms; retain every original slot/reason.
Report mean physical-shot mass-weighted RMSE, balanced over held designs.
Choose the largest D0 lambda within 1e-6 mg/g of the minimum balanced development
RMSE among candidates with every required fold selectable. E0 has the same
fold record with no selection. Development CV is selection, not unbiased nested
validation. Fit final E0 and selected D0 on all qualified FIT windows.
Maximum starts: D0 15*4*3+3=183; E0 15*3+3=48; total 231.

E0 analytic integrals are checked against independent adaptive quadrature.
D0 uses inherited knot-split 64/128-point Gauss-Legendre and independent
knot-split adaptive quadrature (epsabs=1e-14 kg, epsrel=2e-13, limit=200).
Allowance=max(|I64-I128|,|I64-Iadaptive|+error,|I128-Iadaptive|+error)
+128*machine_epsilon*(width+|I64|). For E0 the two analytic evaluations
coincide; adaptive discrepancy/error and floating-point term still apply.
Only source fraction 3 can reconcile a start to m1+m2 within four ULPs,
adding twice the absolute displacement to the allowance. No broader tolerance.
Total per-interval allowance including reconciliation must be <=1e-9 kg.
Runtime rejects nonfinite/reversed/out-of-support/before-anchor queries,
wrong species/schema/units and extra inputs. Zero width returns zero mass and
undefined concentration. Modeled gaps are not measured whole-cup delivery or
extractable-inventory closure.

## Freeze, single score, decision

Create all 192 arm/slot PRED predictions without joined outcomes. Freeze sources,
protocol, exact code/runtime, models, preprocessing, support and predictions.
Obtain genuine independent G1 approval bound to exact freeze/head/tree. The
implementer cannot approve. If unavailable: READY_FOR_INDEPENDENT_REVIEW.
Approval permits the exclusive single score without new owner authorization.
One durable score-start receipt precedes the sole outcome join. Existing score
or failed receipt prevents retries. No post-score tuning, changed predictions,
thresholds or exclusions. Scientific defects after scoring invalidate affected
results and require STOP; publication-only corrections preserve frozen science.

For each original shot e=predicted-observed mg/g and w=measured interval mass:
R=sqrt(sum(w*e^2)/sum(w)); B=sum(w*e)/sum(w). Each condition averages R and
abs(B) over its three original shots; balanced summaries average equally over
the four primary conditions. Never cancel signed shot biases before abs.
Each arm must have every primary R<=0.25 and A<=0.125 mg/g.
D0 earns complexity only if adequate and all increments pass: balanced R
reduction >=0.05 mg/g and >=15%, definite R improvement in >=3/4 conditions,
balanced mean absolute shot bias worsening <=0.025 mg/g.

Convert interval allowances to mg/g with measured mass; propagate weighted L2
for shot R and weighted L1 for B/abs(B), then the same equal-shot/condition
averages. Difference allowances add; relative gain uses D0_R<=0.85*E0_R with
allowances on both. A favorable upper/lower bound must satisfy the inequality
for PASS; definite violation is FAIL; overlap UNRESOLVED. A conjunction fails
if any requirement definitely fails. No rounding into PASS.
Secondary panels cannot rescue primary failure. Incomplete flow cannot pass
full-flow adequacy; supported-subset diagnostics preserve original denominators.

Disposition: FIVE_CQA_CONDITIONED_MODEL_EARNED if D0 adequate with every increment;
SIMPLE_FIVE_CQA_EXPONENTIAL_ADEQUATE if E0 adequate and D0 does not earn complexity;
FIVE_CQA_D0_ADEQUATE_INCREMENT_NOT_ESTABLISHED if E0 fails and D0 passes but the
increment fails; TESTED_FIVE_CQA_FAMILIES_INADEQUATE if both definitely fail
with qualified complete primary evidence. Required unresolved scientific decisions
give NOT_ADJUDICATED with exact cause. A completed negative is a valid result.

## Execution and publication

The active continuation deadline is 2026-09-29 04:48:20 UTC, as authorized
below; the original stopped window is retained separately.
60-minute fitting-stage span (conservative cumulative clock); one worker and
one BLAS thread; 12 GiB process memory; 5 GiB private task evidence. Reuse durable
exclusive counters and cancellation; incomplete attempts consume budget, and no
restart in a fresh directory. One substantive implementation/review cycle, at
most one bounded pre-score correction for a material defect.

CLI: prepare; develop (folds plus final fits); freeze (coordinate-only prediction
then freeze); score --review; verify; report. Verify replays saved inference and
identities without fitting/scoring. Report reads retained scores only. Originals,
row observations/predictions and detailed logs stay outside Git. Publish compact
aggregate/model artifacts with CC-BY-NC-3.0 attribution, separately from software
licensing. One draft Puckworks PR; actual CI state only; EWP remains read-only.

## Authorized continuation accounting

The original attempt stopped before any real fit or score: 0 starts, 0 actual
residual calls, 0 fitting seconds, 0 scores; elapsed time 1418.985946 seconds.
Retain that evidence unchanged. The owner's bounded amendment authorizes a
continuation from 2026-09-28 22:48:20 UTC through 2026-09-29 04:48:20 UTC, with
at most 90 minutes for the specific WP6 fixed-history repair and its baseline.
A separate G0 repair commit precedes this protocol and the scientific implementation.
The original 231-start, 8000-call/start, 60-minute fitting, one-worker, one-thread,
12-GiB memory, total 5-GiB evidence and one-score ceilings remain cumulative.
The same task identity and initially unused run-001 directory are retained.
No deadline extension or restart may be inferred after this window.
