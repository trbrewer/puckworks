# PW-VIS-PREDICTOR-001 — frozen engineering plan

G1 empirical research; no governing-physics change or validation upgrade.
Owner authorizes execution through a draft, unmerged PR with auto-merge disabled.
Base: `4c5ebab5df79929813949df7113c21290dde40cc` (current main fetched 2026-11-05).
EWP, source snapshot, historical results and production defaults remain read-only.

## Source and observation

Use only `visualizer/hydraulic_timeseries`, July-15 snapshot, authenticated with
X1's `authenticate`, projected whitelist reader and latest-index identity rule.
X1 funnel: 23,169 logical shots; 14,471 pressure/weight common-time histories;
3,419 span 9–5 bar (the latter is NOT an admission rule). Inspect underlying
arrays, not merely catalog metadata. No harvest, outcomes, sensory or free text.
Unknown machine/sensor/parser provenance stays in the broad corpus. Known estimated
weight channels require explicit retained channel authority; absent such authority
label UNKNOWN, never inferred measured. Generic supplied flow is documented as
estimated/unknown-quantity and is not substituted for the observation. Only the
reported scale-flow channel can supply the consistency diagnostic.

Target: **reported weight-derived flow**, Qw=(W(end)-W(start))/duration in g/s.
Machine pressure is the model coordinate, never reconstructed puck pressure.
Reuse X1 support-block and boundary/weight-increment code. The reusable API takes
seconds, Pa and kg at extraction; window/model research coordinates explicitly use
seconds from onset, bar, grams and g/s.

## Fixed windows and diagnostics

Time alignment: the stored common native elapsed-time coordinate, zero shift.
Cadence-only inspection (14,471 histories) gave median 0.224 s, IQR 0.211–0.246 s;
95th-percentile median cadence 0.2675 s; 99th-percentile largest gap 0.7753 s.
Choose **2 s** non-overlapping windows. Onset is the first native finite weight
sample strictly above **1 g**; no pump-start calibration and no fitted lag.
First **3 windows / 6 s** calibrate. Guard is **2 s**, [6,8) after onset.
Score every fully supported later window beginning at 8 s; require at least
**3 scored windows** and all 3 calibration windows. Do not score partial windows.
Whole-shot reconstruction uses every retained complete window, including guard.

Require equal channel lengths, finite strictly increasing timestamps, and finite
pressure/weight support. X1 finite support blocks are additionally split at
nonfinite weights, negative pressure (undefined model domain) or gaps > **2 s**.
Do not interpolate across unsupported gaps. Reject missing user linkage because
user-isolated folds cannot be defined; disclose it separately from provenance.
Logical versions deduplicated by inherited rules; physical reuploads unresolved.

Keep finite negative/noisy weight increments, apparent resets and clipped/flat
weights. Diagnostics do not exclude shots/windows: negative increment; reset-like
native drop >5 g; clipping-like repeated maximum for >=2 s (not proof of clipping);
quantization-like >=95% of weights within 1e-6 g of the 0.1-g grid; onset already
above threshold at first sample; gap present; pressure stability range <=0.5 bar;
flow stability SD<=0.2 g/s; supplied scale-flow agreement RMSE <=0.5 g/s versus
window increments (else disagreement/missing). No shift is applied. Report plausible
lag only as unresolved, with the 2-s guard reducing direct adjacency, not identifying
latency. All thresholds fixed here, before scoring.

Pressure-varying subset: range of **scored-window time-mean pressure >2 bar**.
Window direction: endpoint change >0.25 bar rising, <-0.25 falling, else level.
Pressure bands of window-mean pressure: [0,3), [3,6), [6,9), [9,infinity) bar.

## Models, numerical integration and training

One unconstrained direct least-squares amplitude per shot, reusing COR15's helper
(the helper's docstring says positive but its actual solve is unconstrained).
An identically zero calibration basis has minimum-norm amplitude zero. No use of
later observations to adjust primary amplitude. Ordinary negative observations stay.
C0=1, T0=exp(-exp(-t/Tc)), R0=exp(-exp(-M/Mc)); L0R=P*R;
M0R=Pd*(1-exp(-(P/Pd)^n))*R; AR=M0R*exp(-kappa*P).
Sensitivities M0 and A omit R. Here M is the **observed mass at window start**,
and t is window-start time from delivery onset. These are conditional predictions
using recorded pressure during the window and (for R models) current observed mass,
not autonomous forecasts of an entire future shot from its prefix alone.

Pressure factors use time-weighted **mean[h(P(t))]**, with piecewise-linear native
pressure and fixed 16-point Gauss–Legendre quadrature in every native subinterval,
including interpolated window boundaries. Do not use h(mean P).
Before scoring, audit each selected fold model on all training and held-out pressure
covariates against 64-point integration plus adaptive integration on sharp intervals
(n*log(Pmax/Pmin)>1 or kappa*pressure-span>1). Require per-window relative basis
error <=1e-5 (scaled by max(reference basis, 1e-12*that shot's calibration maximum));
otherwise stop, retain the failed version, and disclose a forced numerical repair.
No flow targets enter this check. Audit deployment models separately. The provisional
4-point operator was rejected by synthetic pre-score review, before the freeze. Recovery/time factors
are evaluated once at the window start as specified. All families share windows.
Bounds: n>=1 with no upper bound; Pd [0.1,100] bar; kappa [0,2]/bar, exactly zero
allowed; Mc [0.1,10000] g and Tc [0.1,1000] s. Log coordinates for Pd/Mc/Tc,
linear n/kappa. Stable exponent evaluation and analytic derivatives.

Optimize the mean over users of mean per-shot later-window RMSE (g/s), fitting
amplitude from only calibration windows at every objective evaluation. Primary
reporting uses this same averaging. Normalized RMSE divides each shot's RMSE by
max(RMS calibration Q, **0.1 g/s**), identical across models and calibration-only.
L-BFGS-B with analytic gradient, ftol=1e-9, gtol=1e-6, maxiter=400,
maxfun=1000, maxls=40; retain every start's status/objective, no post-score tuning.
Lowest finite objective wins, including the unchanged exact nested candidate;
nonconvergence is disclosed. No optimizer family or fallback added. Exact repeated quadrature pressure values
may be deduplicated with a sparse weighted window operator; no rounding, bins or
quadrature changes are introduced by this computational optimization.

T0/R0/L0R: 16 one-dimensional log-spaced scale starts across their full bounds.
M0R/M0: D0 and all twelve JOINT_CLOCK DESCRIPTIVE_ALL n/Pd seeds plus 16 LHS.
AR/A: those full shapes, the fitted matching monotone model at kappa=0, plus
16 LHS. Historical shapes are external Waszkiewicz starts, not Visualizer fits.
D0 values from COR15: n=2.4709360685491837, Pd=3.5633704054718103 bar,
kappa=1/24.396659674282887 /bar. Historical recovery start Mc=28.709461834955388 g.
LHS seed **20261105**; initial n [1,8], all other transformed coordinates cover
full declared bounds. n may exceed 8 during optimization. Freeze extracted
external start values in STARTS.json. Same schedule in every fold and deployment fit.

Capacity maxima: for kappa>0, solve n*x/(P*expm1(x))=kappa, x=(P/Pd)^n.
For n>=1 the positive term is strictly decreasing from infinity to zero:
there is exactly one stationary point and it is the global maximum; check both
zero and infinity endpoints. At kappa=0 the supremum is Pd at infinity, with
no finite global maximum. Report whether each finite maximum is inside observed
training pressure range. Do not treat a fitted peak as universal or physical.

## Frozen folds, reporting, release

Sort distinct stored salted users, permute with numpy default_rng(20261105),
assign round-robin to five folds. All shots of a user share its fold. Private
manifest includes canonical identity/content hash, user, fold and window roles;
commit its SHA-256 and aggregate fold/corpus manifest, never individual tokens.
Training excludes held-out users completely. Freeze PLAN and manifest in Git before
any held-out scoring; independent read-only pre-scoring audit checks implementation.

Exactly **35 shared cross-validation fits** (5x7), C0 analytical. Cached held-out
predictions supply every benchmark result. Secondary reconstruction fits amplitude
on all retained windows of the held-out shot and scores the same windows, using the
fold's shared parameters; no extra shared fit. Paired differences (first minus
second): AR-M0R, AR-T0, AR-R0, M0R-R0, R0-C0, T0-C0. Bootstrap complete users,
1,000 resamples, seed 20261105; percentile 2.5/97.5 intervals, no refits. Overall
and pressure-varying reports, dimensional and normalized. Breakdowns from the same
predictions only: direction, bands, quality flags and known-estimated authority.
For window subsets, recompute per-shot RMSE on those windows then equal-user means.

Owner clarification: also perform **7 all-user deployment fits**, plus analytical
C0, with the same settings/starts. Keep their cost separate. They never enter
scores or contrasts. Recommend the lowest primary held-out RMSE among all eight declared models
(C0/T0/R0/L0R/M0R/AR/M0/A; fixed listed order for exact ties), not an all-user
training winner. M0/A remain explicitly labelled no-recovery sensitivity families.

Public cells need >=20 shots and >=10 distinct linked users. Suppress entire
partition if any nonempty member or its complement fails either threshold;
zero groups can be shown only without private values. User-balanced averaging
prevents heavy-user dominance. Release no individual errors, IDs, user hashes,
private paths, selected traces or free-text labels. Aggregated example uses fixed
elapsed-window bins, equal-user means, and only bins and increments/decrements in
contributing shot/user sets satisfying the same thresholds; no exact-shot example.
Curves/figures are research diagnostic VizSpecs, no production visualization entry.

Final independent fresh read-only review checks observation, windows, calibration,
folds, nesting, fairness and claims. Fix concrete defects with preserved failure
records; do not revise settings/corpus/folds based on outcomes. Run focused tests,
quick CI and repository required checks. No successor.

New relative to the completed EWP private programme (12,093 same-shot fits, 6,655
out-of-fold evaluations / 213 cohorts): shared pressure shape, transfer to held-out
users, early-shot calibration with frozen amplitude and competitive progression
baselines. Prior failures/limits remain historical. PRs #419/#420 concern physical
qualification and metadata recovery; they do not prohibit this authorized empirical
benchmark. Unknown sensors, lag, machine identity, post-drip/shutdown, self-selection
and hidden shot state limit conclusions. No TDS/EY, causal law, puck pressure,
mechanism, universal peak or physical validation claim.

Data source: Visualizer; thanks to the contributing users who made their shots public.
Owner-attested permission permits this research, not raw redistribution or endorsement.

## Frozen extraction result (before fitting/scoring)

23,169 canonical shots / 555 linked users → 14,471 common pressure/weight
histories / 344 users → **10,686 retained shots / 318 users**, **177,394 windows**.
Five folds contain respectively 1,927/1,565/2,141/2,999/2,054 shots and
64/64/64/63/63 users. All retained shots have user linkage. Detailed structural
rejection reasons and individual membership remain private. The public funnel
and fold table are in FUNNEL.csv and FOLD_MANIFEST.csv.

Private corpus/fold manifest SHA-256:
`ee751332d3f3f955f6cd3530a1e8e6c53f0b034dfc7a1ad5e667cf8adf406975`.
Private validated-window cache SHA-256:
`8cd8369cca2b12fd4a9e776ee58215f8634aee097d03dd5c46b2fa53cea6c935`.
The corpus is identical under provisional GL4 and final GL16 integration; only
quadrature nodes and the corrected presence diagnostic changed before freezing.
