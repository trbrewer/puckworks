# SCI-MD-GRUDEVA-CLOCK-001 frozen experiment

G1 / NO_PRODUCTION_GOVERNING_PHYSICS_CHANGE; repository declaration
NO_GOVERNING_PHYSICS_CHANGE. Owner task authorizes this analysis and the final
unmerged PRs. Puckworks issue #275; EWP issue #181. No production model registration,
solver/default/lock change, native EWP, laboratory activity, rescue or successor.

This is retrospective, source-conditioned, whole-shot-grouped predictive
evaluation. The source and historical aggregate targets were already exposed.
These are not previously unseen or sealed targets, independent prospective
validation, or identification of a physical mechanism. Delivery additivity is
not a complete solid/liquid puck-inventory balance.

## Source contract

Grudeva, *Espresso brewing: mathematical modelling & experiment*, thesis §2.1–2.2,
printed pp. 27–30, supplies the physical interpretation: repeat coffee extractions,
a single-spout collection wheel, 16 consecutive 2-second samples, nominal 32-second
collection from simultaneous pump/wheel activation. First-drip alignment is
explicitly not used. Source clock is nominal collection/pump time, not a measured
high-frequency flow trace. Different barista-selected settings across repeats
are retained as source variability, not assigned covariates or fitted offsets.

Upstream `YoanaGrudeva/espresso-model` commit
`567ad8f3808eb74fbe3e470eaa333161bf2eac1c`; exact bytes and thesis in SOURCE.json.
`exp13.csv` contains 14 blocks, each with Vial No., Vial Weight, Vial+Coffee,
Weight, TDS rows. Preserve 18 original column slots per block (252 rectangular
rows; 240 present vials). `PlotData.ipynb` was inspected as JSON and never
executed. Its cells 3/4/6/18 iterate the first 13 blocks as experiments. Together
with the thesis's 13-shot methods, this establishes the first 13 physical-shot
groups by source block ordinal. There are no globally unique timestamps/shot IDs;
ordinal IDs are valid only within the pinned file. No pairing across files is
inferred. The extra block is preserved but has no qualified explanation or
physical-shot membership in that processing cohort. The alternate 14-block
comparison is SOURCE_CONTRACT_BLOCKED_FOR_NAMED_COMPARISON. No residual-based
inclusion or inferred fourteenth replicate, and no replacement alternate cohort.

Primary: original blocks 1–13, vials 1–16, 13 folds and 208 predictions/model.
26 zero-mass vials have structural zero delivery; 180 positive-mass vials have
available chemistry; block 6/vial 3 and block 13/vial 2 have positive beverage
mass with recorded zero TDS. Primary marks their chemistry unavailable. Their
known mass still increments b; predictions remain present. Eleven shots have
full regular-window support and two have observed support. No complete-cup claim
includes terminal liquid or unresolved chemistry. Zero sensitivity uses the two
recorded zeros literally (182 scored positive-mass vials).

The recorded Weight field is the notebook's beverage-mass authority, in grams.
Every checkable net agrees with gross minus tare at 0.01 g displayed precision
(discrepancy reporting threshold 0.005 g; not a measurement-error estimate).
Do not replace recorded net, independently compact missing columns, or derive
net from a missing tare. Terminal block 6/vial 17 has missing tare and recorded
Weight equal to gross; its liquid mass is unqualified. Terminal TDS is missing
in blocks 5, 8 and 13 at vial 17. Across all raw blocks there are 16 terminal
vials (17/18), without qualified intervals; inventory them, exclude from this
regular-window experiment. Their problems do not block regular support.

TDS is mass percent: notebook cell 6 labels %, cell 8 computes weight*TDS/100;
source methods describe refractometry and dilution correction. Values are
recorded/dilution-corrected as supplied, not independently reconstructed.
Observed solute g = beverage g * TDS percent / 100. No dose, inlet volume,
held-shot total normalization, missing-chemistry zero fill or inventory mapping.
Positive-mass recorded zero semantics remain ambiguous despite the method's
small-sample discussion. Both bounded interpretations were selected before fits.

Historical reconciliation only: all 14 blocks, literal zeros, first 16 vials,
recorded net, arithmetic mean and sample SD (ddof=1) reproduce every historical
mean/SD at 4 decimals. That summary is not the new dataset. Notebook uses
nanstd population SD, omits zeros, and independently removes NaNs; these are
historical processing differences, not operations copied into this adapter.
Historical data, registered solver, fitted coefficients and gates remain intact.

## Models, operator and computation

c(t,b)=c0 exp(-(a_t t+a_m b)^p), mass fraction g/g; t in s, b in g beverage.
TIME fixes a_m=0; MASS fixes a_t=0; MIXED fits both. Bounds c0=[0,1], each active
rate=[0,10] in s^-1 or g^-1, p=[0.25,4] are computational bounds, not measured
physical priors. Zero rates yield c0 exactly. No per-shot coefficient or shift.

For each vial integrate c(t(b),b) db from measured cumulative b_start to b_end.
Primary t=t_start+duration*u, u=(b-b_start)/m. Timing sensitivities use u² and
sqrt(u). Both are assumptions about unobserved within-vial timing and are refit
on training shots. MASS is timing invariant. Structural zero mass predicts zero.
Finite nonnegative delivery must be <= beverage mass +1e-12 g; never clip.
For every frozen fit calculate integral c(t_end,b) db and integral c(t_start,b) db.
They bound the observation for fixed parameters, not all recalibrated models.

Integration: 128-point Gauss–Legendre on v in [0,1], u=v^8, weight 8v^7.
The transformation regularizes origin behavior. Independent per-vial QUADPACK
integration directly on u: epsabs=epsrel=1e-11, limit=200; refinement 256-point.
Allowance is maximum of primary/refinement disagreement and primary/independent
absolute disagreement plus QUADPACK error, including both endpoint bounds.
Target strictly <1e-6 g/vial. This is numerical, not measurement uncertainty.
No tolerance increase, output clipping, failed-fold exclusion or rescue after score.

Training objective: equal mean over training shots of mean squared solute-mass
errors on eligible positive-mass vials. Residual multiplier is
1/sqrt(number_training_shots * eligible_vials_in_that_shot). Structural zeros
are predicted/operator-tested, excluded from fit and scoring denominators.
Held coordinates are projected to shot, vial, mass, b_start, t_start, t_end before
fitting. Held chemistry and eligibility never reach training or template.

Deterministic scipy.optimize.least_squares, TRF, 2-point Jacobian, exact trust
solver, linear loss, ftol=xtol=gtol=1e-10, diff_step=1e-6. x_scale is [.2,.05,1]
for single-coordinate candidates, [.2,.05,.05,1] for MIXED. No estimated scales.
Every residual call, including initial evaluation and numerical Jacobian calls,
counts against 2,000 calls/start (wrapper hard cap; max_nfev also 2,000).
Retain every attempt's actual calls, scipy nfev/njev/status/message, final training
loss and parameter vector. On exceptions retain last evaluated theta/loss and wrapper count; scipy counters
are explicitly unavailable after exception. No random source, optimizer rescue
or changed bounds.

Eight starts for TIME/MASS (c0,active_rate,p):
(.2,.03,1), (.3,.08,1), (.1,.02,.5), (.5,.1,2), (.25,.05,4),
(.4,.15,.25), (.15,0,1), (.75,.3,3).
MIXED six fixed starts (c0,a_t,a_m,p):
(.2,.02,.02,1), (.3,.05,.05,1), (.1,.01,.01,.5), (.5,.05,.05,2),
(.25,.025,.025,4), (.4,.075,.075,.25), then training-only TIME and MASS solutions
at exact nested limits. Select lowest training loss among converged endpoints
and those exact nested starts whose optimization succeeded. Ties use lower
start index, then insertion order. All failures retained; all-start failure
makes the affected comparison unresolved, never reduces its denominator.
Boundary hits: within 1e-7 of fitted bounds (fixed absent rates not counted).

TEMPLATE: arithmetic mean eligible positive-mass training concentration at each
vial position, multiplied by held measured beverage mass. Exclude structural-zero
placeholders. Missing-position fallback: nearest eligible training position, tie
to smaller position. Record each fallback, number of supported positions and
training counts. No all-data source coefficients are scored as competitors.

## Frozen matrix and decisions

- primary: notebook13, unavailable ambiguous-zero chemistry, linear; 4 candidates.
- literal_zero: same cohort/linear, literal zero chemistry; 4 candidates.
- time_u2 and time_sqrt: primary cohort/chemistry; TIME and MIXED refit; MASS and
  TEMPLATE reuse exact primary fold records because inputs are unchanged.
- alternate14: not executed, source cohort/physical identity unresolved.

Expected new compact fits: 13*(3+3+2+2)=130; eight starts each=1,040 attempts.
MASS/TEMPLATE reuse does not add fitting attempts. 52 fold files; 208
model/fold prediction sets (including reused predictions). No factorial combinations;
the sensitivities do not establish robustness to every combination of assumptions.

Freeze all authorized predictions and their manifest before any comparative score.
Score once, with exclusive output creation and hash verification. Reporting reads
the saved scores and does not retune/re-score. Tests use synthetic data only.

Per shot: positive-mass vial solute RMSE g; signed/absolute support-total error g;
maximum absolute running cumulative residual on the same eligible support;
TDS RMSE/signed error in percentage points with positive-mass denominators;
support identities/gaps, structural zeros, boundary hits, numerical allowances.
Missing chemistry is skipped in observed-support sums, never imputed as zero.
Equal-shot aggregate is arithmetic mean of shot RMSEs, not pooled RMSE.
Paired differences preserve original shot order. No inferential resampling.

OWNER-TASK WORKING BUDGETS (not source uncertainties or espresso standards):
Adequacy: RMSE<=.05 g AND max absolute cumulative residual<=.20 g in at least
ceil(.75*N)=10/13 shots. Report A separately for every form including TEMPLATE.
Material gain: mean RMSE at least 20% lower AND absolute reduction >=.005 g AND
strictly lower RMSE in >=10/13 pairs AND mean absolute support-total error
worsens by <=.05 g. Report every condition and paired differences separately.
B compares MASS against TIME (mass multiplication alone is not a mass-clock gain).
C requires MIXED adequate and material versus BOTH TIME and MASS.
Competitive compact: adequate, mean RMSE <=TEMPLATE+.005 g, and mean absolute
support-total error <=TEMPLATE+.05 g. Distinguish competitiveness from material
improvement over TEMPLATE; absence of earned gain is not statistical equivalence.

Propagate per-vial numerical allowances to RMSE by RMS allowance and cumulative/
total errors by sum allowance. Reevaluate decision conditions at conservative
per-model metric-box corners; any change, numerical target failure, or failed
fold gives NUMERICALLY_UNRESOLVED on affected treatment/decision. Failed-fold
treatments retain all 13 expected shots and do not calculate reduced-denominator
comparisons. Reports mark failed folds and remain executable; nominal numerical
booleans are diagnostics beneath the explicit scientific disposition. Report nominal
scores without treating them as a resolved result in that case. Each sensitivity
has a separate disposition; no unconditional architecture claim if gains depend
on sampling/zero assumptions. No alternate-cohort robustness claim is available.

## Freeze, privacy and execution

FREEZE.json binds this protocol, source audit/manifest, implementation, tests,
synthetic QA and exact software identity. Independent reviewer must issue
APPROVED_FOR_SCORING against its SHA-256 before fit-predict/scoring; implementation
author cannot grant approval. One substantive pre-scoring audit covers source,
fairness, leakage, mathematics and decision surface. Ordinary final review/CI
remain separate. Bounded corrections follow the controlling governance standard;
preserve all original evidence and distinguish defects from scientific retuning.

Raw source files, rectangular observations, row-level predictions, fit logs,
per-shot metrics and plots remain private. Public artifacts: first-party code,
synthetic tests, protocol, source/count/hash audit, permitted aggregate outcomes,
sanitized hash manifests and exact research handoff. Upstream permission is
PERMISSION_DOCUMENTED, not SPDX/MIT/CC-BY. No new raw payload is redistributed.

PHYSICAL_VALIDATION = NOT_ESTABLISHED
NATIVE_EWP_BUILDS = 0
NATIVE_EWP_INTEGRATIONS = 0
PRODUCTION_DEFAULTS_CHANGED = false
PRODUCTION_DEPENDENCY_LOCK_CHANGED = false
