# PW-JOINT-MASS-FADE-001 — pre-fit specification

Owner-authorized execution through a draft, unmerged PR with auto-merge disabled.
G1 retrospective capability comparison; TARGET_EXPOSED;
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No successor. Base fetched main:
`4c5ebab5df79929813949df7113c21290dde40cc`. EWP remains read-only.

**Question.** Does one shared delivered-liquid-mass fade improve held-out
Waszkiewicz trajectories over a freshly fitted A-J1 control? A mixed or negative
answer completes the task. Lower training loss or descriptive-only gains do not
establish held-out improvement. Keep A-J1 if gamma selects zero or held-out
trajectories do not improve. This is a phenomenological hypothesis; mass as its
driver is under test. No fines, compaction, clogging or measured liquid/solute claim.

**Model card for this research extension.** The inherited J1 front, capacity,
Mc bank, R0 chemistry, geometry, units and detector remain as in
[JOINT_CLOCK](../JOINT_CLOCK_001/PLAN.md). After breakthrough only,
M'=q_liquid=C_A(P) exp(-exp(-M/Mc)) exp(-gamma M), M(tb)=0,
C_A(P)=a Pd [1-exp(-(max(P,0)/Pd)^n)] exp(-max(P,0)/Pstar).
Mass is predicted delivered liquid in g, pressure recorded line pressure in bar,
flow g/s, gamma 1/g; no observed mass enters dynamics. Before breakthrough M=q=0.
Both `joint_clock_001.liquid_only` and `wetting_screen_001._column` use their own
liquid state, with fade in old-state prediction, midpoint, output flow and water
increment driving transport. No trace post-multiplication; chemistry equations
and parameters unchanged, solute responds to changed water flux. Zero gamma
must nest the original implementation at rtol=1e-12, atol=0.

Fitting vector (a,Pstar,n,Pd,gamma,tau0), tau0 last. Log a/Pstar/Pd,
n and gamma linear, tau0/100. Adapter explicitly constructs inherited
(a,Pstar,n,Pd,Mc_fixed) and passes gamma separately. Bounds inherited:
a [.001,20], Pstar [.5,100], n [1,infinity), Pd [.1,100], tau0 [0,100];
gamma [0,.2]. No Mc fitting.

**Regimes.** gamma=0: rises to limit, no interior maximum. For
0<gamma Mc<1: rises then falls, M*=Mc ln(1/(gamma Mc)). For gamma Mc>=1:
maximum at breakthrough and decline afterwards (zero derivative at breakthrough
when product=1). M* describes constant-pressure liquid flow only. Report gamma,
product, regime and M* for every fit. Parameter contacts are exact lower/upper
bounds plus continuous transformed distances. Beverage maxima use the inherited
native-node observer on each brew's fixed clean support; record global maximum,
all tied times, whether at left/right boundary, and interior local maximum times.
A boundary-only maximum is labelled "no interior peak within horizon"; do not
extrapolate. Also report condition means on the shared supported time interval.
Recorded pressure, solute and observer can move these peaks. Accumulated mass,
not pressure ordering, controls analytic crossing; C_A is nonmonotone.

**Evidence authentication.** Same 56 distinct brews/eleven conditions,
`waszkiewicz2025/traces_per_brew`, Zenodo 18046315, CC-BY-4.0; duplicate excluded.
Underlying original files, native FORM_A source/configuration files, saved fit
JSON and Mc tables are mounted and inspected, not catalog-only. Inherited
source loader verifies raw hashes, configurations, onset, masks and fold bank.
SOURCE_FITS.json binds the saved J1 and LC fits, including matching training
membership and Mc. Source heads: JOINT_CLOCK ef32f90 (on main), LC
0e1944d; #423 c4b4a07e110a3ede5013fd876a02a58ee6456eab;
#424 ec82d1f019da3a5fcd9ff8748c29926c763d7bcc;
#425 717d7494efa09de2bcd2249c7186dedb17fa3136. Imported observation/replay
modules are byte-identical to their pinned sources. The #424 exact-prefix/native
observation contract is reused, not redefined. Authenticate compact source tables
against git objects and each large fit/prediction against its retained manifest.
Historical code identities refer to the pinned source; changed implementation
identity is recorded separately and zero nesting is explicitly verified.

**Exactly 24 fit problems, lambda=1 only.** Eleven ordinary whole-condition LOCO
folds and DESCRIPTIVE_ALL, separately for refreshed A-J1 and A-J1-F.
Inherit J1's equal-condition/equal-brew composite, fixed support/masks,
normalizers .437 g/s and 4.534 s, valid censor loss and complete detection counts.
These scales are not noise estimates. Fit at .02 s/256 cells with the exact-prefix
observer; report frozen fits at .005 s, with .02-s sensitivity and no refitting.

Step 1: 19 starts per fold, saved A-J1, any compatible better LC frozen-zero
point for the same fold/weight (9 and 11 bar), then 18 or 17 five-dimensional
Latin-hypercube starts respectively, seed 20261106. Initial n in [1,8].
Step 2: 19 starts per fold: refreshed control at gamma Mc=0,.03,.13,.25,
then the first 15 LHS common-parameter vectors from that fold's Step 1 bank.
For those 15, a one-dimensional LHS with seed 20261106 supplies gamma Mc in
[0,.4]. This implements 19 total starts, not 19+4; the LHS common parameters
are reused exactly. The first four common parameters and tau0 are determined
only by the matching Step 1 winner. [START_BANK.csv](START_BANK.csv) freezes
all 456 start prescriptions, including every gamma Mc, before fitting.

Bounded Powell xtol=1e-4, ftol=1e-7, maxiter=maxfev=infinity, no wall-clock cap;
one BLAS thread per worker. Keep the lowest finite evaluated point including
all starts and intermediate trials, regardless of optimizer return. Preserve
failed attempts/trials and account their CPU. Fade selection must be no worse
than its exact embedded control under the same contract; any violation is a
bookkeeping defect, not a scientific result. Evaluate each selected fade again
with gamma=0 and all other parameters unchanged, no refit. Report search spread
and numerical change without new thresholds or an overall PASS.

**Frozen evaluation.** Three labelled arms: saved A-J1 (continuity), refreshed
A-J1 (primary control), A-J1-F. Primary contrasts are paired fade minus refreshed.
Report J1 endpoint/primary/companion liquid-flow RMSE and full-cohort onset score
or computed lower bound with intended/available/detected counts; separate
1,2,3.5 bar; inherited high-pressure slope and peak/trend continuous criteria.
Use inherited J1 shared condition-then-brew resamples for these metrics.
For trajectories use #423/#424 exact 2-s windows, both clocks, observed-onset
anchoring for observation AND prediction, native timestamps, terminal masks,
matched window pressure, shared 1,000 whole-brew bank (SHA256
`d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6`).
Verify byte identity/order, not merely seed equality.

For LOCO and DESCRIPTIVE_ALL separately: onset+10 absolute flow; high-pressure
slope at every declared time; stable +10→40, +40→60, +60→100 changes at 9/11/13
bar and 9-minus-13 increments; 100-s levels. Cross-condition +60→100 changes
at every condition, with paired observed-minus-predicted discrepancies and
intervals. Explicitly report invented declines where observations rise and missed
declines where observations fall, retaining uncertainty. In particular preserve
2/3.5/4/5/6 bar observed +.0786/-.1393/+.1892/+.1023/-.0838 g/s and source
intervals. No B0b comparison. Reuse #425 linear-observer split for predicted
liquid and solute contributions. Intervals are conditional on frozen fits,
not refit uncertainty. LOCO pools distinct held-condition vectors; descriptive
uses one in-sample vector. Neither increases independent campaign counts.

**Compute and verification.** Forecast 80–120 CPU core-hours, no wall-clock cap.
Record actual process-tree CPU including failed scientific commands; distinguish
QA/review/CI. Large traces/trials outside Git. Before fitting run focused zero
nesting, positive-gamma integration and prefix (decline/nondetection), analytic
regime, adapter/tau0, fold/Mc and shared-trajectory/resample tests. Baseline quick
suite and registry; final required CI. Fresh read-only independent reviewer
checks both integrations, adapter, refreshed comparison, cross-condition results
and claims. No post-score fitting or scope extension.

**Deliverables/decision.** SUMMARY.md (~half page, numbers first) answers separately
(1) late changes across conditions per scope, (2) high-pressure catch-up,
(3) early/100-s/low-pressure/onset tradeoffs, (4) gamma/regime fold stability.
FITS.csv, STARTS.csv, METRICS_PAIRED.csv, TRAJECTORY_COMPARISON.csv,
CROSS_CONDITION_LATE.csv, CONTRIBUTIONS.csv, NUMERICAL_SENSITIVITY.csv,
one 6/9/11/13-bar observed/three-arm time figure with LOCO/descriptive panels,
REPRODUCE.md with commands/hashes/core-hours, compact verification and review.
Stop after fitting, replay/evaluation and draft PR; no other extension, weight,
clock, chemistry change, Visualizer work or EWP writes.
