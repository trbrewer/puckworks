# PW-MASS-FADE-DIAGNOSTICS-001 — pre-execution plan

Fetched main base: `4c5ebab5df79929813949df7113c21290dde40cc`.
G0 bounded retrospective diagnostic of frozen evidence; TARGET_EXPOSED,
RESEARCH_ONLY, PHYSICAL_VALIDATION=NOT_ESTABLISHED. No change to scientific
parameters, objective, observer, frozen predictions or production behavior.
Owner-authorized through a draft, unmerged PR with auto-merge disabled.
Commit this plan before diagnostic evaluations. No successor.

## Frozen sources and execution

Read #427 at `ec0dc887ca0f66338fe166cd4ed8e7cbf2994441` and #423 at
`c4b4a07e110a3ede5013fd876a02a58ee6456eab`. Use #427's inherited code directly
from a pinned, read-only checkout, with separate diagnostic outputs; do not
modify or transplant historical artifacts. Bind its FITS.csv, STARTS.csv,
RUN_RECEIPT.json and EVALUATION_FREEZE/EVALUATION files by SHA256, then verify
all 24 selected fit JSON hashes, fold membership and fixed Mc. Reuse its source
loader to authenticate original files, saved inputs, masks, clocks and Mc bank.
The same 56 Waszkiewicz brews/eleven conditions are available as underlying raw
files, not catalog-only evidence: waszkiewicz2025/traces_per_brew, Zenodo
18046315, CC-BY-4.0. EWP and raw inputs remain read-only.

## A — fixed-coordinate slices, never fitting

For each of 12 selected A-J1-F vectors and 12 refreshed A-J1 vectors, hold
(a,Pstar,n,Pd,tau0) and that fold's Mc fixed. Evaluate gamma = x/Mc at exactly
x = 0, .0025, .005, .01, .015, .02, .025, .03, .035, .04, .05, .06,
.08, .10, .13, .17, .25, .40. Use the inherited lambda=1 objective, equal-condition/
equal-brew weights, masks, normalizers, exact-prefix evaluator, .02-s step and
256 cells unchanged. No optimizer, search refinement, new starts or fit updates.

There are 432 grid evaluations plus 24 selected-vector reference evaluations.
At a selected vector, use its exact saved gamma (avoid a multiply/divide round
trip), requiring exact objective/component/detection reproduction. At gamma=0,
require exact agreement with #427's frozen-zero diagnostic for fade vectors and
selected objective for controls. Report objective, normalized flow/onset
components, counts, every grid minimum/tie and its boundary/interior status,
selected-minus-grid-minimum objective, selected/grid distance and neighboring
grid values. START_VS_FINAL.csv binds each selected fade winner to its matching
row in STARTS.csv and reports initial and final gamma*Mc.

Describe exact grid shape using finite differences: strictly constant values
are flat; nonnegative/nonpositive differences are monotone; a decrease then
increase has an interior minimum; other shapes are reported as nonmonotone with
all local minima and continuous values. No flatness tolerance, new threshold,
or statistical preference criterion. These are one-dimensional slices with
other parameters fixed, **not profile likelihoods** or joint-optimum proofs.
The selected point need not equal a grid node. Compare its neighboring values
and objective gap before attributing the result to the seed.

## B — observations only, same support

Reuse #423's stable-pressure native clock and frozen clean terminal support.
Late change is the exact paired +100-minus-+60-s 2-s-window beverage flow.
Replay all 112 required brew windows against #423's retained per-brew records,
including pressure, window boundaries and support endpoints. No exclusions,
new smoothing, extrapolation, model predictions or new observation clock.

Mass is the recorded scale, relative to the median raw mass at stable −2 to 0 s
(first raw mass only if that interval is empty), exactly #423's onset baseline.
Interpolate this mass at +60 and +100 s inside the same retained native support;
do not integrate filtered flow or use predicted liquid mass. Retain per-brew
baseline, support endpoints, mass values, matched window pressure and flow.
LATE_CHANGE_ORDERING.csv contains both the 56 brew rows and 11 condition means,
with paired intervals for the latter and explicit sample counts.

For the pressure comparison, predeclare achieved pressure as the mean of the
two matched +60/+100-s window pressures, per brew before condition averaging.
Report both individual window pressures too. Plot late change against mass at
+60 s and against this achieved pressure, with eleven condition means and faint
per-brew points behind. No regression line, model, cutoff or mechanism claim.

Use #423's exact shared 1,000 whole-brew-within-condition resamples, hash
`d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6`.
Resample mass, pressure and late change together and recompute all eleven
condition means in each draw; calculate Spearman rho using average ranks for
ties. Report point estimates and #423 nearest-rank 2.5/97.5-percentile intervals,
finite counts and the paired difference in absolute correlations (mass minus
pressure), without a decision threshold. Do not resample conditions or treat
the 56 brews as 56 independent condition comparisons. Stable elapsed times are
identical (60,100; duration40 s), so their across-condition rank correlation is
undefined; this design cannot order conditions by elapsed time. Explicitly
retain 3.5 bar's observed interval touching/crossing zero.

## Deliverables and checks

GAMMA_SLICES.csv, START_VS_FINAL.csv, LATE_CHANGE_ORDERING.csv; compact slice and
correlation summaries as needed; two SVG figures (12-panel objective slices,
two-panel observed ordering); numbers-first short SUMMARY with one sentence
answering each question; REPRODUCE with exact commands, hashes and core-hours.
Large or intermediate arrays stay outside Git. Record process-tree user+system
CPU for every scientific command, including failures/retries. Forecast under
1 core-hour for these fixed evaluations; QA/review/CI accounted separately.

Focused tests cover exact selected/zero reproduction, fixed-vector adaptation,
grid/shape bookkeeping, native mass baseline and support/no extrapolation,
whole-brew paired ranks, shared resample identity and unchanged #423 intervals.
Run required CI and a fresh read-only review of claims. Reuse unchanged baseline
evidence from the same main SHA; run relevant local checks for new code. No
changes to #427 artifacts, EWP, production defaults or historical results.
