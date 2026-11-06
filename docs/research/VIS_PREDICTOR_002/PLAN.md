# PW-VIS-PREDICTOR-002 — post-hoc observation correction

**This is a post-hoc rerun motivated by #421's reset-like breakdowns.** Exclude
every stored shot with `reset_like == True`, and make no other scientific change.
Call survivors **unflagged shots**, never clean or certified. The flag does not
identify the cause of the discontinuity. #421 remains the original result.

Pinned base: `65f51c63856677eccc4ba5a45ce555ea0c4eab99`, the unmerged head of
[#421](https://github.com/trbrewer/puckworks/pull/421). Stack the new draft PR
against `pw-vis-predictor-001`; leave it draft, unmerged, auto-merge disabled.
G1 empirical research; no governing-physics change or validation upgrade. EWP,
the source snapshot, the entire 001 bundle/models and production defaults are
read-only. The owner authorized this correction and execution through a draft PR.

## Exact correction and source continuity

The pinned extractor defines the flag as `bool(np.any(np.diff(weight_kg * 1000)
< -5))`, over adjacent native samples in the **entire original history**, before
window/support selection. Use that stored boolean exactly; do not infer it from
window means, alter its threshold, or identify its cause. Delete whole flagged
shots before training, early calibration, scoring, numerical audits and all-user
deployment refits. Every other flag, including negative native increments,
clipping-like behavior, quantization, gaps, supplied-flow agreement and unknown
weight authority, remains a diagnostic only. Add no exclusions.

Read the authenticated 001 private `windows.pkl` and corpus/fold manifest; retain
the original shot objects in their original order. Do not re-extract, reconstruct
or realign observations. Preserve every surviving shot's **existing fold ID**;
never invoke the fold generator. Users without surviving shots drop out. Recompute
training/reporting weights by the unchanged equal-user rule over survivors.
Private membership and full-object continuity hashes bind the filtered cache.
FROZEN_MANIFEST.json, FUNNEL.csv and FOLD_MANIFEST.csv record the resulting census.

Dataset: `visualizer/hydraulic_timeseries`, the same permissioned July-15 snapshot
used by 001. Source aggregate SHA-256:
`6769656c8555d940bf79a2243a784c38b63066d3fe231227628667d251ba4d5b`;
inventory identity `f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766`.
The 465-file source authentication and 23,169 canonical-shot identity are inherited
from the pinned bundle. Actual stored pressure/weight window arrays are inspected,
not merely catalog metadata. No harvest and no use of TDS/EY, sensory or free text.

## Unchanged observation, windows and models

The complete scientific contract is the [pinned 001 plan](../VIS_PREDICTOR_001/PLAN.md),
including its final pre-score numerical amendment, not an intermediate version.
The evaluator, X1 observation/support helpers and COR15 amplitude helper stay
byte-identical to the pinned head. The only scientific change is whole-shot reset
exclusion.

Target: **reported weight-derived flow**, `(W(end)-W(start))/duration`, g/s.
Machine pressure is the coordinate, never reconstructed puck pressure. Alignment
is native common time with zero shift. Onset is the first finite native weight
strictly above 1 g. Complete non-overlapping 2-s windows start there; the first
three (6 s) calibrate amplitude, [6,8) is the guard, and all supported windows
starting at 8 s are scored (minimum three). Existing support/gap rules are unchanged.
Whole-shot reconstruction calibrates and scores all retained complete windows,
including the guard. No fitted lag, flow-flatness selection or robust loss.

One direct unconstrained least-squares amplitude per shot, using early windows
only in both training and primary held-out prediction. An exactly zero calibration
basis has minimum-norm amplitude zero. Ordinary negative increments are retained.
M is observed mass at the start of a window; t is its start time from delivery onset.
`R(M)=exp(-exp(-M/Mc))`, `Rt(t)=exp(-exp(-t/Tc))`.
`hA(P)=Pd*(1-exp(-(P/Pd)^n))*exp(-kappa*P)`; `hM0=hA` at kappa=0 exactly.
C0=1, T0=Rt, R0=R, L0R=mean(P)*R, M0R=mean(hM0)*R, AR=mean(hA)*R;
M0 and A omit R and remain no-recovery sensitivities. Pressure response is
time-mean h(P(t)), never h(mean P). Query pressure/current observed mass remain
conditional inputs; this is not autonomous forecasting from a prefix alone.

Bounds/coordinates: n>=1 with no upper bound, linear n and kappa;
Pd in [0.1,100] bar, kappa in [0,2]/bar, Mc in [0.1,10000] g,
Tc in [0.1,1000] s. Pd/Mc/Tc use log coordinates. Keep exact-hash node
deduplication, log-domain evaluation, compensated extended-precision calibration,
GL16 on native linear pressure intervals subdivided to <=0.1-bar spans, and all
pinned integrity guards. No previous failed implementation or fitted pressure
shape is a new start. The runtime is Python 3.12 / NumPy 2.0.2 / SciPy 1.13.1,
one BLAS/OMP thread per process, eight independent starts per fit.

L-BFGS-B, analytic gradients, ftol=1e-9, gtol=1e-6, maxiter=400, maxfun=1000,
maxls=40. Starts remain byte-identical STARTS.json plus the same generator:
16 log-spaced starts for T0/R0/L0R; D0 and all twelve JOINT_CLOCK DESCRIPTIVE_ALL
seeds plus 16 LHS for M0R/M0; those pressure starts plus the fitted corresponding
monotone solution at exact kappa=0 for AR/A. Seed 20261105; initial LHS n range
[1,8] is not an optimization upper bound. Recovery historical start Mc=28.709461834955388 g.
Keep all start diagnostics; choose the lowest finite training objective, including
the unchanged exact nested candidate. Parameter/bound contacts do not disqualify
a result. Report contacts within 1e-7 in optimization coordinates as diagnostics.

## Checks and execution order

Commit this plan and the filtered corpus/fold manifest **before C0 reproduction,
any shared fit or held-out scoring**. First verify identical surviving complete
shot objects and fold IDs. Then recompute C0 through the saved-model prediction API
and compare with 001's cached C0 on the same survivors. Required equal-user results:
RMSE **1.2084042519 g/s**, NRMSE **1.6547408860**. Use absolute tolerance **1e-9**
(the supplied references have ten decimal places), also requiring per-window cached
C0 agreement within 1e-9. **A discrepancy stops execution and interpretation.**
No repair/tuning of observations to pass this check is permitted.

Use fresh public/private 002 roots for every model, cache, prediction and audit.
Parameterize the common runner's output root; no 001 output is a fallback.
Read 001 files only as authenticated source/comparison artifacts. Resume a 002
model only when its task, cohort/window hashes, plan hash, original fold ID,
starts, engineering/integration settings and evaluator hash match. Otherwise
preserve the stale artifact privately and refit that same declared model.
Check provenance again before audit/scoring/reporting; test that a 001 artifact
cannot satisfy the 002 skip check. No prior 001 fitted parameter is a warm start.
Prediction caches bind the task, cohort/windows, plan, evaluator and all CV model
hashes; reporting rejects missing or mismatched identities. Numerical audit receipts
must contain the complete current model inventory, not merely a passing boolean.

Exactly **35 CV shared fits (5x7)** and **seven all-user deployment refits**, plus
analytical C0. Deployment artifacts never enter scores, contrasts or default
selection. Audit each selected pressure shape against original-interval GL64 plus
adaptive integration, including start-mass recovery and the same calibration-based
floor; unchanged per-window relative tolerance 1e-5. Batches contain complete shots,
preserving their calibration scale. Numerical failure stops scoring; preserve and
report it rather than altering the declared evaluator/settings.

## Reporting and interpretation

Optimize/report equal-user means of per-shot later-window RMSE in g/s. NRMSE
uses the same calibration-only RMS flow scale for every model, floored at 0.1 g/s.
Report overall and the unchanged pressure-varying subset (scored-window mean-P
range >2 bar), including all five fold scores. Recommendation is the lowest
overall primary cross-validated RMSE among all eight declared models, with the
same fixed tie order; deployment refits are excluded.

Paired contrasts: AR-M0R, AR-T0, AR-R0, M0R-R0, **L0R-T0, L0R-R0**, R0-C0,
T0-C0. For each metric/subset, bootstrap complete users 1,000 times, seed
20261105, percentile 2.5/97.5 intervals, cached predictions only, no refits.
Report 001 full-cohort-fit cached predictions versus 002 filtered-fit predictions
on **identical surviving shots/windows**, overall/subset and per fold. Never
compare 002 to 001's full-cohort headline as a fit-improvement estimate.

Reuse all 001 diagnostic breakdown definitions and release rules. Rising/falling
window differences are direction dependence, not proof of a time artefact.
Report all per-fold parameters and contacts; explain selected curves only after
the continuity/C0 checks and held-out errors/contrasts/fold variation. Compute AR/A
global maxima using the same stationary-point proof/root check, and compare with
native training pressure ranges. Kappa=0 has no finite maximum (supremum at infinity).
Large Mc, large Pd/n near one, or boundary contacts describe the selected empirical
curve; they are neither admissions nor criteria for whether results count.

Public cells require >=20 shots and >=10 users, including complementary groups;
suppress whole unsafe partitions. Aggregate example support changes protect shot
changes and actual contributor-user entries/departures; suppressed bins are gaps,
with markers for isolated released points. No per-shot/user records or predictions
in Git. Three task-local VizSpec figures: paired differences, aggregate example,
and capacity curves. Unknown provenance, residual negative increments, hidden state,
lag, post-drip/shutdown and self-selection remain limitations. No mechanism, puck
pressure, causal law, universal peak or physical-validation claim.

A fresh independent read-only reviewer checks exclusion, continuity, paths,
resume provenance, C0 and final claims. Run focused tests and required CI.
No successor is authorized by this task.

Data source: Visualizer; thanks to the contributing users who made their shots public.
Research-use permission does not grant raw redistribution or endorsement.

## Frozen filtered census

23,169 canonical shots / 555 users → 14,471 common pressure/weight histories /
344 users → 10,686 structurally usable 001 shots / 318 users → **10,231 unflagged
shots / 315 users**, **159,466 windows**. Exactly 455 shots are excluded.
Preserved folds 0–4 contain 1,810 / 1,521 / 2,068 / 2,846 / 1,986 shots and
64 / 64 / 63 / 62 / 62 users. FROZEN_MANIFEST.json binds private membership,
unchanged surviving objects and the filtered window cache. This census was
computed before C0 reproduction, fitting or scoring.
