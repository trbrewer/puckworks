# PW-JOINT-PRESSURE-FADE-001 — pre-fit specification

Owner-authorized execution through a draft, unmerged PR; auto-merge disabled.
G1 retrospective capability comparison; TARGET_EXPOSED;
PHYSICAL_VALIDATION=NOT_ESTABLISHED. EWP remains read-only. No successor.
Fetched main/base: `fa0b14003cb0d7c77a902e3adf1e6fd1a38bf120`.
#427 and #428 are merged, so this branch targets main.

**Question.** Does one shared pressure-time fade improve held-out trajectories
over #427's refreshed A-J1 control? Negative or mixed results complete the task.
This is phenomenological, with no mechanism claim. The observed pressure ordering
motivates the hypothesis; it does not establish the fade. #428's fixed-coordinate
slices support the mass-fade neighborhood but do not prove joint convergence or
exclude start dependence.

**Research model card.** Inherit J1's capacity, front, fixed fold Mc, R0 chemistry,
geometry, units, observation and objective from [JOINT_CLOCK](../JOINT_CLOCK_001/PLAN.md)
and [JOINT_MASS_FADE](../JOINT_MASS_FADE_001/PLAN.md). After breakthrough only,

    M' = C_A(P) exp(-exp(-M/Mc)) exp(-gamma_P Phi),
    Phi' = P,  M(tb) = Phi(tb) = 0,
    C_A(P) = a Pd [1-exp(-(P/Pd)^n)] exp(-P/Pstar).

P=max(interpolated recorded raw line pressure,0) in bar, Phi in bar s,
M in predicted delivered liquid g, gamma_P in 1/(bar s), q in g/s. Before
breakthrough M=Phi=q=0. No observed mass drives the predictor. gamma_P=0
exactly embeds A-J1; there is no combined mass/pressure fade in this task.

Both `joint_clock_001.liquid_only` and `wetting_screen_001._column` independently
carry Phi on the inherited event-inserted time grid. On each saturated step,
DeltaPhi=dt*(P_old+P_new)/2, Phi_mid=Phi_old+DeltaPhi/2. Apply fade at Phi_old
in the old-state mass predictor, Phi_mid in the midpoint water increment, and
Phi_new in instantaneous output. The actual water increment drives unchanged
solute release/storage/transport. Preserve all zero-fade arithmetic and the
inherited breakthrough-node convention. The research adapter uses the joint-clock
midpoint scheme; pressure fade is not enabled in the historical native-time scheme.
No integrated trace is post-multiplied.

Adapter vector (a,Pstar,n,Pd,gamma_P,tau0), tau0 last. Log a/Pstar/Pd;
n and gamma_P linear; tau0/100. Bounds a [.001,20], Pstar [.5,100],
n [1,infinity), Pd [.1,100], gamma_P [0,.005], tau0 [0,100]. Construct
inherited theta=(a,Pstar,n,Pd,Mc_fixed) explicitly; gamma_P travels separately.

At constant pressure, d log(q)/dt=q exp(-M/Mc)/Mc-gamma_P P.
Report beverage-flow maxima per brew and condition on native clean support,
including exact ties, left/right boundaries, local maxima and horizon. A global
boundary maximum is labelled "no interior peak within horizon"; a fully flat
curve has no unique peak. This does not extrapolate beyond support. Record
exp(-gamma_P P*40) at every nominal condition for each fit, with P labelled
constant nominal pressure; also report the actual recorded-pressure exposure
increment/factor for each brew's stable +60→100 s interval. These factors alone
do not determine beverage-flow changes.

**Authentication and control reuse.** Pin #427 to
`ec0dc887ca0f66338fe166cd4ed8e7cbf2994441` and #428 to
`093b8b5e5a4c86ebf31bc48f46521441069072ec`. Authenticate compact artifacts,
large selected fits and original code against Git objects and receipts. Reuse
the twelve refreshed A-J1 vectors without fitting. Before any optimization,
reproduce their objective, flow/onset components and training detections exactly
at .02 s under the modified zero-fade code. Preserve all historical artifacts.
Reuse inherited source loaders for original trace hashes, configurations, masks,
onsets, training memberships and Mc. Dataset `waszkiewicz2025/traces_per_brew`,
Zenodo 18046315, CC-BY-4.0: 56 distinct brews in eleven conditions; duplicate
excluded. Mounted underlying originals and configurations are inspected and
authenticated, not replaced by catalog metadata. EWP code is only read.

**Exactly twelve fits, 228 starts, lambda=1.** Eleven ordinary LOCO folds plus
DESCRIPTIVE_ALL, same equal-condition/equal-brew objective, fixed flow/onset
support, masks, normalizers .437 g/s and 4.534 s, censor loss and fixed Mc bank.
Fit at .02 s / 256 cells with inherited exact-prefix chemistry. Report frozen
fits at .005 s and .02-s sensitivity; no post-score refitting.

Nineteen total starts per fold: matching refreshed control at gamma_P*1300
=0,.05,.15,.30, then the first fifteen common-parameter LHS vectors from #427's
control bank, retaining their original common coordinates exactly. The new
one-dimensional gamma_P LHS uses seed 20261107 and gamma_P*1300 in [0,.6]
(same deterministic fifteen products in every fold). Thus the inherited common
bank retains seed 20261106; 20261107 supplies the new fade coordinate.
[START_BANK.csv](START_BANK.csv) freezes all realized vectors before fitting.

Bounded Powell xtol=1e-4, ftol=1e-7, maxiter=maxfev=infinity, one BLAS thread per
worker, no wall-clock cap. Retain the lowest finite evaluated point including
starts and all intermediate trials, regardless of returned Powell endpoint.
Preserve failures and their CPU; no extra starts. Each winner must be no worse
than its exact embedded refreshed control; violation is bookkeeping failure.
Evaluate each selected fit at gamma_P=0, other parameters fixed, without refitting.

**Frozen evaluation.** Four arms: saved A-J1 (continuity), refreshed A-J1 (primary
control), A-J1-F (#427 context), A-J1-PF. Primary paired contrast PF minus refreshed;
mass-fade comparisons are descriptive. Reuse #427 evaluation and #424 trajectory
operators: both clocks, observed-onset anchoring for observation and prediction,
2-s windows, frozen native timestamps/terminal masks, matched window pressures.
Verify the exact shared 1,000 whole-brew-within-condition bank SHA256
`d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6`.
Inherited J1 aggregate RMSE intervals use its separate condition-then-brew bank,
seed 20261103. All intervals condition on frozen fits/Mc, without refit uncertainty.

For LOCO and DESCRIPTIVE_ALL separately: endpoint/primary/companion liquid-flow
RMSE; full-cohort onset RMSE or computed lower bound with intended/available/
detected counts; separate 1/2/3.5 bar; high-pressure slope/peak/trend criteria
with continuous values; onset+10 absolute beverage flow; 9/11/13-bar slopes at
all declared times; +10→40, +40→60, +60→100 changes and 9-minus-13 increments;
100-s levels; every condition's +60→100 change and paired discrepancy against
#423. Explicitly report invented declines where observed points rise and missed
declines where they fall, preserving intervals (3.5 bar crosses zero). Reuse
#425's linear-observer liquid/solute split, with no observed split claim.
No B0b comparison. Reuse unaffected saved-arm evaluations only by authenticated
identity; verify zero nesting and continuity after the integration change.

For each selected PF vector, evaluate the fixed-other-parameter objective slice
at gamma_P*1300={0,.0125,.025,.05,.075,.1,.15,.2,.3,.45,.6}, plus its selected
value for exact reproduction. Report flow/onset components, training detections,
grid minima, neighboring values and selected-minus-minimum gaps using #428's
slice classification. These are one-dimensional slices, not profile likelihoods;
there is no optimizer, adaptive grid or new threshold in this step.

**Compute/checks.** Forecast 25–40 scientific core-hours, no cap. Record actual
external process-tree user+system CPU including failures, reference checks,
replay and slices; keep QA/review/CI separate. Large traces/trials outside Git.
Baseline CI at integration head `392e788f1b1e6629d1b7c18268382f230ab93b23`
is reusable because its tree equals the fetched merge base; run final required CI.
Focused tests: zero nesting (rtol=1e-12,atol=0), analytic constant-P Phi and both
paths at positive gamma_P, variable-P quadrature and pre-breakthrough reset,
declining/nondetecting exact-prefix equivalence, adapter/Mc/tau0, fold/control
reproduction, trajectory/resample identity. Independent read-only pre-fit audit
and fresh final review of Phi wiring, control reuse, cross-condition evaluation
and claims. No parameter/objective retuning after viewing results.

**Outputs/decision.** Half-page numbers-first SUMMARY answers (1) late changes,
especially rising 4/5 versus declining 6+ bar, (2) catch-up, (3) early/100-s/
low-pressure/onset tradeoffs, (4) gamma_P stability and slice minima. FITS,
STARTS, METRICS_PAIRED, TRAJECTORY_COMPARISON, CROSS_CONDITION_LATE,
CONTRIBUTIONS, NUMERICAL_SENSITIVITY, GAMMA_P_SLICES, peak/fade-factor details,
one observed/all-arm 4/6/9/11/13-bar LOCO/descriptive flow figure, REPRODUCE with
hashes/commands/core-hours, compact verification and review. Lower training loss
or descriptive-only gains are insufficient. Retain A-J1 if gamma_P selects zero
or held-out trajectories do not improve; report mixed tradeoffs without overall
PASS. Stop at the draft PR: no pressure threshold, combined fade, additional
extension/weight/clock/chemistry change, Visualizer work or successor.
