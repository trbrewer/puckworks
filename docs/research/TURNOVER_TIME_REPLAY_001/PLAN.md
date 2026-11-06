# PW-TURNOVER-TIME-REPLAY-001 — frozen no-fit plan

2026-11-06, before new outcomes. Fetched main/base:
`4c5ebab5df79929813949df7113c21290dde40cc`.
Read #423 at `c4b4a07e110a3ede5013fd876a02a58ee6456eab` and #422 at
`d4386441fbc387c0a83219817dac6f4bce3b94a3`. Neither merge is required.
The #423 observation module is brought forward **byte-identically** for reuse;
historical bundles, saved fits, originals and EWP remain read-only.
[INPUT_MANIFEST.json](INPUT_MANIFEST.json) freezes the authenticated inputs.
Underlying native traces, retained fits/prediction arrays and Visualizer cache
files were inspected/authenticated, not merely catalogued. No new harvest.

## A1 — separate historical prerequisites

Use the inherited runtime: Python 3.12.3, NumPy 2.2.6, SciPy 1.18.1,
Numba 0.68.1, Matplotlib 3.11.2. Authenticate JOINT_CLOCK and WETTING_SCREEN
manifests, 12 A-J1 λ=1 fits, the D0 parameter/Mc bank, FORM_A source inputs and
configurations, original files, forcing/observation grids, evaluator identities,
and retained metadata/arrays. Keep the eleven nominal conditions and 56 brews,
excluding only the inherited alias. No parameter, Mc or chemistry changes.

Before new model comparisons, reproduce:

1. A-J1 λ=1: all 56 saved held-condition cases and 23 saved DESCRIPTIVE_ALL
   constant-pressure cases, at their original 0.02-s and 0.005-s conventions.
   Compare retained state arrays, instantaneous liquid endpoints/traces and
   detector outputs using original forcing and observation timestamps.
2. D0 Form A original replay: use its saved fixture, original forcing grids,
   original evaluators, M(0)=0, saved LOCO parameter/Mc bank and flow-only
   observation contract. Reproduce saved arrays/statistics separately.
3. D0 diagnostic fresh-bed R0 beverage wrapper (screen arm Z): all 56 saved
   held-condition and 23 DESCRIPTIVE_ALL constant-pressure cases, at both
   retained numerical steps, against original state arrays, instantaneous
   liquid endpoints/traces and detector outputs.

Numerical reproduction uses the inherited joint/screen equivalence tolerance
`rtol=atol=1e-12`; D0's original replay uses its inherited `rtol=1e-12, atol=0`.
Discrete identities, detection status, masks and brew/fold membership match
exactly. Failure is preserved in the new receipt and stops the **affected
model's** new comparison; other authenticated models and part B can proceed.
Do not equate historical instantaneous liquid endpoints, historical constant
pressure curves and the new measured-history beverage-window means.

## A2 — four frozen measured-history replays

Two models × two scopes × 56 brews: **224** intended new predictions.
Models are A-J1 λ=1 and D0 Form A with its already-defined diagnostic fresh-bed
R0 beverage wrapper. LOCO uses the fit excluding the brew's entire nominal
condition and that fold's matching fixed Mc; verify the full training membership.
DESCRIPTIVE_ALL uses one all-condition parameter/Mc vector separately on each
brew's measured forcing. It remains in-sample. A pooled LOCO slope combines
different held-condition fits and is not one constitutive curve.

Use the unchanged inherited pressure/initial-state/chemistry conventions and
**0.005-s, 256-cell** evaluation. Retained FORM_A pressure through 100 s is
extended only with genuine inherited clean-course pressure samples beyond 100 s,
as in JOINT_CLOCK. Integrate through the actual clean end; no terminal holding,
padding or extrapolation. J1 retains its fitted wetting delay and event insertion.
D0 starts fully wet with M=0, fresh R0 inventory and zero dissolved solute; the
general-horizon `Prepared`/arm-Z path reuses exactly the screen's hydraulic update
and conservative column (historical original replay remains separate).
Pressure is clipped at zero by the inherited helper. Recovery uses predicted
liquid M; no observed mass, TDS or chemistry drives any simulated state.

Record C(P), liquid M, R(M)=exp(−exp(−M/Mc)), liquid flow, beverage mass and front
fraction along the **same** replay. Diagnostics are time averages over the same
native window nodes, then equal-brew condition means; they are not extra runs,
products of averaged factors, fitted explanations or ablations.

## A3 — identical observation support

Stable-pressure centers: **10, 20, 30, 40, 60, 100 s**. Observed-onset centers:
**10, 20, 30, 40 s**. Both signals use each brew's **observed** onset for onset
windows. The predicted detector onset/status is reported separately on the
inherited fixed native 0–100-s detector timestamps, including non-detections
and their censor bounds; it never shifts windows or alters eligibility.

Freeze #423's observed per-brew windows, native clean-course timestamps,
terminal handling, availability and achieved window pressures. Recompute the
observed operator as a prerequisite against its retained rows. Sample predicted
cumulative beverage mass onto those native timestamps, then apply exactly
`savgol_filter(gradient(B,t),31,1)`. Apply #423's unchanged paired-window integral
to each centered **2-s** window. Use recorded #423 achieved window pressure for
both observed and predicted slopes. The 100-s window is **99–101 s**, with full
native differentiation/filter support, not a truncated endpoint. No fit mask.

Retain every attempted brew/window and explicit availability reasons privately;
publish aggregate availability and detector status. Missing model outputs are
not zero or non-detections. If any observed-eligible brew lacks a prediction,
that condition/comparison is marked unavailable rather than silently averaging
a smaller cohort. Reproduction failures are unavailable comparisons, not fits.

## A4 — paired descriptive outputs

Reuse #423's exact **1,000 whole-brew-within-condition draws, seed 20261106**;
verify its full brew order and draw-bank SHA-256
`d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6`.
One bank spans observations, models, scopes, clocks and times. Never redraw for
missingness. Intervals are inherited nearest-rank pointwise 95% intervals,
conditional on frozen parameters and Mc; no refit bootstrap or new grades.

At every time/clock/model/scope, retain condition means, unweighted slope across
nominal 9/11/13-bar condition means against achieved pressure, observed-minus-
predicted slope differences, and paired stable-100-minus-current slope changes
for both observations and predictions (plus their difference). For onset rows
the reference is explicitly **stable-pressure 100 s**, not onset 100 s.
Retain adjacent-time changes within each clock. Maxima are among condition means
with #423's exact-tie, available-edge and missing-support handling; recompute the
maximum and 13-bar/maximum ratio in every draw, with nonpositive denominators
undefined. Do not locate or fit a continuous peak or peak time.

Retain observed/predicted trajectories at nominal 9/11/13 bar and increments
for stable **10→40, 40→60, 60→100 s**, plus adjacent declared times on both clocks.
For every increment report 9-minus-13 growth and observed-minus-predicted
differences with the same paired draws. A matching slope cannot excuse an
incorrectly directed trajectory, particularly the observed late decreases.

## B — Visualizer scored-window coverage and release

Use only authenticated #422 retained objects: **10,231 unflagged shots / 315
users**. Read only; no fitting, new prediction scores, filtering or fold changes.
Use NumPy 2.0.2 / SciPy 1.13.1 for the snapshot census. Select `role == "score"`
and count its actual denominator. The 159,466 retained windows include other
roles and are not substituted. Compute stored mean machine pressure by its
unchanged dot-product property and midpoint `(start_s+end_s)/2`, relative to
Visualizer's inherited first-reported-weight>1-g delivery onset.

One fixed disjoint window partition: **P<9; 9≤P≤10; 10<P≤11; 11<P≤12;
12<P≤13; P>13 bar**. For releasable cells report scored-window counts and percent
of all scored windows, distinct shots/users, and window-weighted time median,
25th and 75th percentiles (NumPy's default linear quantiles). Shot/user sets can
overlap bins and their counts must not be summed as distinct totals.

Apply the inherited minimum **20 shots / 10 users**, complements and whole-
partition rule. Also protect changes in contributor shot sets and actual user
sets across neighboring published bins, including the full-cohort-to-first-bin
transition, as in the inherited linkage check. Any nonempty member/complement
or linked nonempty change failing its threshold withholds the **entire pressure
partition**, including all bin counts, percentages and time summaries. Empty
cells carry no private summaries. No post-result bin merging or alternative
above-10 aggregate. A safe independent all-score denominator may be published
without any bin statistics; with every bin withheld it cannot reveal one hidden
cell by subtraction. Suppressed means withheld, not zero. Preserve the detailed
census and release audit outside Git; never publish which private cell failed,
identifiers, paths, linkage or per-record data.

## Outputs, checks and interpretation

Publish the requested bundle and two-panel slope figure with a task-local VizSpec,
clearly distinguishing LOCO and DESCRIPTIVE_ALL. Additional compact provenance,
historical-reproduction, onset and availability receipts support the requested
checks. All new private predictions, caches and audits use a fresh task directory.
No historical evaluator CLI that writes old artifacts is invoked. Reuse only
authenticated read/predict functions; no optimizer calls or parameter changes.

Focused checks cover historical reproduction, condition isolation/Mc, observed
onset alignment and non-detections, full native support and frozen pressure/flow,
draw identity and paired calculations, and score-role/bin/denominator/disclosure
rules. Run required CI and obtain a fresh read-only reviewer check, explicitly
including late 60→100-s directions. Measure replay/census CPU core-hours and
separate verification/CI cost. Keep PR draft/unmerged, auto-merge disabled.

A mismatch or suppressed coverage is a complete finding. Explain model behavior
using the full retained predictor and internal states without uniquely assigning
recovery's contribution or a physical mechanism. Coverage is exposure, not
detection power. No aggregate AR gain does not mean no fitted downturn. Pressure
node, coffee, machine, brew style and observation contracts differ across sources;
no physical-validation or cross-corpus agreement claim. No successor.

Attribution: Waszkiewicz et al. (2025), Zenodo 18046315, CC-BY-4.0 data. Visualizer
research use is permissioned; credit Visualizer and the users who made their
shots public. No raw Visualizer redistribution or endorsement is implied.
