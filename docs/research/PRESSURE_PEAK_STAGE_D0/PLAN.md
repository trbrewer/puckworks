# PRESSURE-PEAK D0: graded A and exploratory LC capability plan

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.**

**PLAN ONLY. This delivery authorizes no fits, evaluators, scientific checks,
results or result artifacts.** Execution requires separate owner approval. D0
is a Python-only, retrospective G1 full stage for C3e form A (primary, four free
flow parameters) and LC (EXPLORATORY, five). There is no overall PASS.

Base main is `f9d17a4bb50b3de34bf059d61f19de8cdf3866ab` (#408, X1), confirmed
after `git fetch origin`; its parent is
`45387cf00ff001d656c2e6dc60369c37d5aa948d` (#407, C3e). The plan branch is
`pressure-peak-d0-plan`, created from that exact main. The stage is **D0**, not
C4: `"C4"` is the existing B0 course model called by `B.fit_course` to supply Mc.
This PR remains draft with auto-merge off; never force-push.

## Evidence read and inherited decisions

The following committed sources were read before fixing this plan. All links
refer to the base above; none of their scientific contents changes here.

| Source | Decision carried into D0 |
|---|---|
| C3e [PLAN](../PRESSURE_PEAK_STAGE_C3E/PLAN.md), [SUMMARY](../PRESSURE_PEAK_STAGE_C3E/SUMMARY.md), [RESULT_TABLE](../PRESSURE_PEAK_STAGE_C3E/RESULT_TABLE.csv) | Exact A/LC capacities, state, point fits, starts, numerical diagnostics, global maximum definition, and the low-pressure tradeoff. Point fold ranges are not uncertainty intervals. |
| C3d [PLAN](../PRESSURE_PEAK_STAGE_C3D/PLAN.md), [SUMMARY](../PRESSURE_PEAK_STAGE_C3D/SUMMARY.md) | Free flow Pd, both seed groups, inherited optimizer settings and the distinction between onset information in a seed and a fixed flow scale. |
| C3c [PLAN](../PRESSURE_PEAK_STAGE_C3C/PLAN.md), [SUMMARY](../PRESSURE_PEAK_STAGE_C3C/SUMMARY.md) | Unchanged objective, observers, replay tolerance, numerical qualifications and rule 7 below. |
| C2 [SUMMARY](../PRESSURE_PEAK_STAGE_C2/SUMMARY.md), [RESULT_TABLE](../PRESSURE_PEAK_STAGE_C2/RESULT_TABLE.csv), [pressure_peak_stage_c2.py](../../../puckworks/analysis/pressure_peak_stage_c2.py) | `fit_folds`: point-bank/refit-Mc distinction and sampled weights; `paired_samples`: exact C1 pairing; `margin_audit`: training-only cap and ungraded held-out floor audit; `flow_identity`: saved-field replay precedent at rtol=1e-12, atol=0. D0 does not call the whole C2 fit pipeline, which would refit historical comparators. |
| C1 [SUMMARY](../PRESSURE_PEAK_STAGE_C1/SUMMARY.md), [metrics and reporting helpers](../../../puckworks/analysis/pressure_peak_stage_c1.py) | Held-out grades, DESCRIPTIVE_ALL parameter intervals, independent onset/flow scale comparison and 200 paired whole-brew refits. |
| C0 [SUMMARY](../PRESSURE_PEAK_STAGE_C0/SUMMARY.md), [helpers](../../../puckworks/analysis/pressure_peak_stage_c0.py) | Existing bands, signed low-pressure bias with magnitude grading, no overall PASS, no wall-clock cap in D0 (owner decision; C0's cap is not inherited). |
| X1 [SUMMARY](../PRESSURE_PEAK_X1/SUMMARY.md) | Context only. **No X1 quantity enters D0**: no viscosity, pore-volume, clock, pressure-sign or other X1 result becomes an input, prior, target, bound, start, grade or correction. |

C3c's rule 7 is retained explicitly: “Unchanged onset predictions are inherited
results. Fixing Pd from onset cannot establish scale consistency, and n differing
from one changes the interpretation of that pressure scale.” D0 therefore keeps
the onset law separate and compares independently fitted scales rather than
assigning onset capability to A or LC.

Source scope follows the [espresso data guide](../../data/ESPRESSO_DATA_GUIDE.md),
[Waszkiewicz card](../../cards/waszkiewicz2025.md),
[MANIFEST](../../../puckworks/data/MANIFEST.csv) and
[available-data register](../../../puckworks/data/AVAILABLE_DATA_REGISTER.json).
Use `waszkiewicz2025/traces_per_brew` and
`waszkiewicz2025/equilibrium_windows`: 56 distinct brews at nominal
1/2/3.5/4/5/6/7/8/9/11/13 bar, preserving the alias exclusion, brew ordering and
accepted source identities. These are source-internal, single-rig, single-coffee
data; flow is derived from cup mass and shares its information. Existing negative
adoption results remain unchanged. Waszkiewicz et al., Zenodo 18046315,
CC-BY-4.0; no upstream GPL source-code import.

This planning task inspects repository documents, committed result fields and
helper source, not the underlying raw files afresh. Raw records and the onset
cache were used by the accepted stages; fresh authentication is step (i) after
approval. No new raw reduction, scientific replay or candidate calculation runs
in this PR. Earlier stages and source data remain unchanged. Leave R0's known
extraction time-step issue alone.

## Exact forms, objective and numerical settings

Import [C3e](../../../puckworks/analysis/pressure_peak_stage_c3e.py),
[C3d](../../../puckworks/analysis/pressure_peak_stage_c3d.py) and
[C3c](../../../puckworks/analysis/pressure_peak_stage_c3c.py) helpers unchanged.
Use their capacity, analytic derivatives, mass-memory integration, stable limits
and observers; the new module supplies D0's draw/fold orchestration. Pressure is
in bar, mass in g, time in s and flow in g/s. With raw line pressure
`P=max(Praw,0)` and fixed `P0=0`, define

\[
H_n(P)=1-\exp[-(P/P_d)^n],\qquad
C_A(P)=aP_d H_n(P)\exp(-P/P_\star),
\]
\[
C_{LC}(P)=aP_d\{(1-f)H_n(P)+f[1-\exp(-P/P_d)]\}\exp(-P/P_\star),
\]
\[
R(M)=\exp[-\exp(-M/M_c)],\qquad q=C(P)R(M),\qquad
\frac{dM}{dt}=q,\qquad M(0)=0.
\]

Zero is the inherited stable-pressure origin. Integrate through masked intervals
without pausing or resetting the state; observed cup mass never drives M. A has
`(a,Pstar,n,Pd)`; LC adds f. LC at f=0 is A; at f=1, n drops out; at n=1, f drops
out. No M1, M2, combined form, onset law or alternative pressure basis is added.

Bounds are `a=[0.001,20]`, `Pstar=[0.5,100]`, `n=[1,inf)`, `Pd=[0.1,100]`,
and LC `f=[0,1]`. Coordinates are `(log a, log Pstar, n, log Pd[, f])`.
Keep `least_squares`, analytic Jacobian, `x_scale="jac"`,
`ftol=xtol=gtol=1e-8`, 500 evaluations per scheduled start and `1e-10` interior
clipping at finite bounds. Choose the lowest converged finite training objective.
Only if no scheduled start converges, use the inherited 1500-evaluation dogbox
fallback from the lowest-cost finite attempt, recorded separately. An unresolved
fit or nonfinite evaluation stops for owner review; no draw is discarded.
**No post-result changes to bounds, starts, masks or settings.**

The objective is B0c's post-onset trace loss, from observed onset + 2 s through
clean support, on the inherited 0.5-s fit grid. Reporting uses the 0.1-s grid and
the stored 100-s endpoint observer, not a new endpoint window or condition-mean
forcing. Training onsets determine the fixed masks; held-out onset targets never
enter a flow fit. Preserve equal-condition/equal-brew weighting and duration
normalization:

\[
L_i=\frac{\sum_j m_{ij}(q_{ij}-q^{obs}_{ij})^2}{\sum_jm_{ij}},\qquad
J=\sum_{i\in train}w_iL_i.
\]

For point fits `w_i=1/(|G|N_g)`. In a draw use C2's multiplicities s: training is
`sample>0` excluding the held-out condition; weights are `s_i/N_g`, normalized
over training, exactly as `C2.fit_folds`. Whole-condition sample sizes remain
fixed, so this retains equal-condition weights. Reuse the same multiplicities
for held-out condition summaries. Absolute-flow loss gives low-flow conditions
little weight; report condition contributions/shares without reweighting.
The historical joint scales 0.437 g/s and 4.534 s remain unchanged but are not
applied to A/LC's flow-only loss.

## Paired draws, Mc and the separate onset law

Use **200 paired whole-brew refits, seed 20261105**, with
`C2.paired_samples`. Retain brew order, raw draw indices and count vectors, and
assert multiplicities against `C1.B.brew_samples(brews,200,C1.SEED)` exactly
(`rtol=0, atol=0`), as C2 does. Do not resample time points. Each draw contains
DESCRIPTIVE_ALL and all 11 ordinary HYD-LOCO folds for both forms: 2,400 refit
problems per form, 4,800 flow problems total. There are **no omission-twin
refits**. The two C3e point twins per form are replayed context only, with their
original caveat that 3.5-bar information remains in inherited Mc; they never
enter ordinary held-out grades or draw intervals.

**Point Mc:** follow C2's accepted convention. Ordinary point folds use the
saved matching per-fold Mc bank; DESCRIPTIVE_ALL uses
`B.fit_course("C4", coarse, train, sample, budget)[2]` as in C2. Assert the
full-cohort value against the committed bank before point replay. The 28 C3e
A/LC point fits are replays at committed parameters, not optimizer reruns;
twins retain their committed ordinary-fold Mc.

**Refit Mc:** in every draw and every one of the 12 folds, re-derive training Mc
using `B.fit_course("C4", coarse, train, sample, budget)[2]`. Fix that result
during both A and LC flow fits for the matching draw/fold. Assert every value
against C2 T2-F's saved `refit_parameters_by_fold[draw][fold]["Mc_fixed_g"]`
with `assert_allclose(rtol=1e-12, atol=0)`. This propagates the training-Mc
uncertainty under C2's convention; retaining one point-bank scalar throughout
the refits would change the procedure. Saved per-draw values are assertion
references, not substitutes. Any failure stops; switching to saved Mc needs
owner approval.

**Onset:** A and LC contain no onset law; both onset columns are **NOT_SCORED**.
Re-run `C2.fit_t2` with kind `"onset"` for each draw/fold, using the same sampled
training rows, weights, bounds, starts and settings as C2. The cap is
`P0 <= min(5, min(training Pe)-0.01)` bar, lower bound -5 bar. Only sampled
training Pe enters the cap. Assert the four fitted parameters
`Pd_bar,P0_bar,b_s_bar,t0_s` against the saved
`"T2 onset-only (capped)"` row's `refit_parameters_by_fold`, at
`rtol=1e-12, atol=0`; preserve its objective and bound diagnostics for replay too.
On failure stop, with no switch to saved onset parameters without owner approval.

Keep `C2.margin_audit` unchanged: enforce the training margin/inactive training
floor and report every held-out denominator-floor use and prediction ungraded.
Do not cap using held-out data or alter the fixed denominator floor. The onset
fit remains independent of the flow fit: its Pd is only the draw/fold start seed
and the DESCRIPTIVE_ALL comparison scale. It is never fixed inside A or LC and
does not become an onset prediction from either flow form.

Report a separate row labelled exactly:

**INHERITED: C2 capped onset-only law (onset RMSE 3.522 s, NEAR, fixed by C2)**

That row carries C2's full-precision held-out onset value and its 95% interval,
reproduced on the same draws, with its grade fixed by C2. Do not copy the grade
into A's or LC's onset column or imply that D0 earns it.

For every replay/assertion failure, stop dependent work for owner review. Report
every mismatch in the compared batch, not merely the first exception: draw
index (C2's zero-based order), fold, candidate/source, field or array element,
both values, absolute difference and relative difference. Relative difference
is `abs(actual-saved)/abs(saved)`; for a zero saved value report zero if equal,
otherwise infinity, retaining the absolute difference. Identify point checks
as `draw=POINT`. State the number of mismatches and entries compared; mark any
unattempted entries. The complete Mc/onset sweeps cover all 200 x 12 entries;
no failed assertion is hidden by changing inputs, tolerance or draw order.

## Starts and retained numerical qualifications

For every A refit problem use C3d arm A's six starts in this order: iterate
`(a,Pstar,n)=(1,15,1),(1.5,30,2),(2,8,4)`, crossing each with Pd equal first
to that draw/fold's re-run onset-only Pd and then to **4.0 bar**. Keep both seed
groups even if they nearly coincide. LC crosses each of those six, in the same
order, with `f in {0,0.1}`: twelve starts. Do not seed from the fitted A optimum,
reduce starts, or select using held-out outcomes. Start reduction is forbidden.

For every start, including failed attempts and separately recorded fallbacks,
store original/clipped initial coordinates, initial/final parameters and
objective, success, nfev, bound flags/distances, and initial/final censored
training-brew counts and identities by condition, split into structural and
numerical zeros. Censoring means zero capacity throughout the masked training
trace, not onset non-detection. Aggregate these counts across draws, folds,
forms and seed groups while retaining the individual records. Report seed-group
best objectives and parameter ranges so dependence on the onset-Pd group remains
visible. A numerically smaller argmin alone is not seed dependence when group
objectives agree under the inherited spread rule.

Start disagreement remains `spread > 1e-6*max(1,Jbest)`. Finite-coordinate bound
proximity remains `1e-6` of its transformed range; for unbounded n report its
lower-bound distance and optimizer active flag. Keep and count draws with
disagreement, boundary estimates, fallbacks or censored training brews. Identify
any such draws contributing to interval endpoints; wide or multimodal intervals
are reported without trimming. Retain physical parameter ranges even when J
agrees. These diagnostics qualify interpretation; they introduce no rejection
threshold or permission to tune.

Per-start Jacobian checks occur **only for point fits**, by replaying C3e's
committed checks. There are none in refits. Retain its selected/initial check
coverage, analytic norms, branch counts, halving direction, and saved
relative-error = absolute-error / analytic-norm arithmetic. Do not demand
12-digit reproduction of roundoff-dominated finite-difference cancellation
remainders; zero norms use the saved absolute-error convention. Committed
numerical-field comparisons use `rtol=1e-12, atol=0`. Replay the committed
point-grid/nesting diagnostics without adding optimizer starts or changing
their meaning. Analytic Jacobians still drive every refit optimizer.

## Scale consistency and uncertainty

Use the inherited nearest-rank 95% interval helper
[`A.interval`](../../../puckworks/analysis/pressure_peak_stage_a.py), not a newly
interpolated interval convention. Parameter intervals use DESCRIPTIVE_ALL
refits; prediction grades use ordinary held-out predictions. Point values,
draw medians and intervals remain separately labelled.

For **A, graded**, pair its DESCRIPTIVE_ALL flow-fitted Pd with the independent
capped onset-only DESCRIPTIVE_ALL Pd on the identical 200 draws. This follows
C2's precedent of pairing onset-only with a separate flow-only fit. Compare
their marginal 95% intervals: overlap **MEETS**, otherwise gap <=1 bar **NEAR**,
otherwise **MISSES**. Report each interval and its width, the interval gap,
the paired per-draw difference `flow Pd - onset Pd` and its 95% interval, and
descriptive percentiles 2.5/25/50/75/97.5 of each Pd distribution (label these
percentiles separately from the inherited interval rule).

For **LC**, report the same two intervals, widths, gap, descriptive percentiles
and paired-difference interval, labelled **EXPLORATORY, NOT_GRADED**. LC's Pd is
inside a mixture opening and is a different quantity again. Its scale comparison
cannot change A's grade. P0 consistency is **NOT_APPLICABLE** because the flow
forms fix P0=0. Pstar is reported with its DESCRIPTIVE_ALL interval, not graded.
Independent fits here mean separately optimized objectives on identical draws,
not statistically independent estimates or independent validation data.

## Grading and report definitions fixed before results

Apply the existing [C1/C2 bands and scorecard helpers](../../../puckworks/analysis/pressure_peak_scorecard.py)
without alteration. A is primary; LC's flow capability grades carry its
EXPLORATORY label, while its scale comparison is NOT_GRADED. Every awarded
grade carries its continuous value and interval; for trends include the five
continuous trend estimates and intervals beside the discrete match count.
NOT_SCORED/NOT_APPLICABLE rows have no invented value or interval.

| Criterion | Definition and unchanged band |
|---|---|
| Accuracy vs B1 | B0c's 1,000 paired condition-then-whole-brew resamples of frozen held-out predictions, seed 20261105 as C2, +/-0.25 g/s band. Preserve `B.paired_course_loss`, `A.comparison` and the scorecard ordering. MEETS = TIE or BETTER; NEAR = UNRESOLVED with lower error; otherwise MISSES. Show candidate and B1 endpoint RMSE and the paired candidate-minus-B1 interval. These 1,000 no-refit comparisons are distinct from the 200 whole-brew refits. |
| Peak | C1/C2 nominal-condition peak: nominal pressure of the largest sampled held-out condition-mean endpoint, using `B.refit_response`, with its 95% interval over refits. Interval overlap with 5-7 bar MEETS; overlap with 4 or 8 bar NEAR; otherwise MISSES. This is the lenient nominal criterion, not a dense pressure-grid extremum. |
| Slope | Out-of-fold project regression at >=9 bar: the 9/11/13-bar held-out condition-mean endpoints versus their actual mean endpoint line pressures, both using draw multiplicities. Its refit interval MEETS if overlapping [-0.0880,-0.0403] g/s/bar; NEAR if wholly within [-0.176,-0.020]; otherwise MISSES. Preserve the existing nonnegative/zero-crossing MISSES guard. This combines three fitted models, not one capacity-curve derivative. |
| Trends | Inherited late-window observer on resolved 2/3.5/4/5/6-bar conditions; MEETS >=4/5, NEAR 3/5, otherwise MISSES. Retain each signed held-out trend with its refit interval and observed rising direction, plus the draw match-count distribution and 95% interval. No new slope window or resolution test. |
| Onset | A and LC: NOT_SCORED. The separate INHERITED row above retains C2's onset RMSE 3.522 s, NEAR, fixed by C2, with continuous value/interval. |
| Low-pressure bias | Signed mean of held-out condition residuals at 1/2/3.5 bar, prediction minus observation. Grade its magnitude: MEETS <=0.10, NEAR <=0.20 g/s, otherwise MISSES, as C0/C1/C2. Report the signed mean and refit interval, all three residuals and intervals, and their mean absolute value. Signed cancellation does not imply small individual errors. `bias12=(e1+e2)/2` and `mae12=(abs(e1)+abs(e2))/2` remain separate screen metrics. |
| Scale consistency | A only, using the independent-fit Pd interval rule above; LC EXPLORATORY, NOT_GRADED. P0 NOT_APPLICABLE; Pstar reported, not graded. |

Endpoint and trace RMSE preserve C0/C1/C2's mean of condition-specific brew
RMSEs, not pooled RMSE or RMS of condition-mean residuals. Trace errors retain
the duration-normalized B0c mask. Report all 11 condition residuals, not only
the graded subset. All ordinary prediction summaries exclude DESCRIPTIVE_ALL
and twins.

Beside the nominal peak, report the **continuous global capacity maximum** over
P>=0 using C3e's definition/helper: all stationary candidates and endpoint
limits, including competing LC maxima, with their capacities. Never substitute
one local optimum or a pressure-grid maximum. Report DESCRIPTIVE_ALL peak
location/capacity and their 95% refit intervals as parameter-derived quantities;
also retain ordinary-fold peaks and their median/range for continuity with C3e.
Give the refit interval of the ordinary-fold median separately, labelled as such;
fold ranges themselves remain ranges, not confidence intervals. Twins are
replayed context only. Neither continuous-peak summary replaces the nominal
held-out peak grade; it is the better guide to location.

## Saved comparators and low-pressure paired contrasts

B1 is the accuracy reference. Use saved rows only for **C2 T2-F, C2 T2 joint
(capped), C2 C0 joint (capped), C1 T2-F, C0 T1 flow-only, C0 joint
(saved name `T1/T1-W joint`), E1, F1 and B1**. Replay compatible parameters,
predictions, objectives and saved metrics at `rtol=1e-12, atol=0`, preserving
their original stage labels and definitions. No historical refits. C2's saved
reference rows and C1's saved-reference helpers supply the provenance; no
restart evaluation or new model comparison is added.

T2-F's per-draw predictions come from evaluating C2's saved per-draw, per-fold
T2-F parameters, labelled **"replay of saved C2 refits"**. Before using those
predictions, replay `objective_sum_squares` on the original sampled training
support for **all 200 x 12 = 2,400 entries**, including DESCRIPTIVE_ALL, with
`rtol=1e-12, atol=0`. A failure stops for owner review with the complete
mismatch report described above. Saved Mc/onset values embedded in a frozen
T2-F comparator replay do not authorize replacing the required D0 Mc/onset
re-runs.

Using identical draw indices and scoring weights, report paired **A - T2-F**
and **LC - A** differences, their medians and 95% intervals, for endpoint RMSE,
trace RMSE, signed low-pressure bias, each 1/2/3.5-bar condition residual,
brew 1-2 residual, within-2-bar ratio, and out-of-fold >=9-bar slope. Retain all
per-draw values. Differences of signed residuals or slopes are not automatically
improvements; show absolute-error changes where needed to interpret direction.

For A, LC and T2-F, report per-draw held-out distributions (median and 95%) of
the individual brew **1-2 residual** from HYD-LOCO-1.0 and the **3.5-bar
condition-mean residual** from HYD-LOCO-3.5, plus the paired LC - A differences.
As in C2, predict every original held-out brew even when its scoring
multiplicity is zero: the individual brew 1-2 diagnostic and the four specified
2-bar predictions remain defined for each fitted draw. Condition means use the
draw multiplicities. The 3.5-bar condition has three brews; sampling three with
replacement has only **10 distinct multisets**, so its within-condition
resampling interval is coarse, even though variation in training can also move
the fitted predictions.

The within-2-bar ratio in each draw, from HYD-LOCO-2.0, is
`mean(qhat[2-2],qhat[2-4])/mean(qhat[2-3],qhat[2-5])`, a ratio of the two fixed
pair means, not a mean of ratios or a multiplicity-weighted change in the named
pairs. Recompute the observed counterpart from authenticated data; C3e reports
**1.249606122** (rounded context, never a hard-coded target). If a denominator
is zero the ratio is undefined, never floored. Retain/count those draws and
mark the all-draw ratio/difference interval unavailable if any required value
is undefined; any additional defined-subset summary must name its count and
cannot masquerade as the 200-draw interval. Report ratio discrepancy and its
change beside brew 1-2 and 3.5-bar absolute residual changes, as R5 requires.

## Runtime and execution order after approval

D0 has **no wall-clock cap** (owner decision, 1 Nov 2026); C0's two-hour cap is
not inherited. Earlier helpers stay unchanged: pass an infinite deadline
(`math.inf`) wherever they take one, including `C0.Deadline` as used by
`C2.fit_folds`-style budgets, `B.fit_course` and C3e's `fit_fold`, so no
`TimeoutError` can fire. Before execution, confirm by reading the call path that
no other wall-clock stop applies; if one exists that cannot be disabled through
its arguments, stop and ask rather than editing an earlier helper. Optimizer
evaluation limits (500 per start, inherited 1500-evaluation dogbox fallback) are
fit settings, not time limits, and stay unchanged.

Use `ProcessPoolExecutor` with **32 workers**, one BLAS thread per worker set
before imports (`OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=OMP_NUM_THREADS=1`),
retaining C2's spawn discipline. Record cumulative wall time and worker CPU time
for every check, pilot, rerun and interruption, and report them; they inform,
they do not stop the run.

Checkpoint each completed draw (both forms, all 12 folds, Mc/onset assertions
and diagnostics) to a local directory outside Git, e.g.
`/home/tim/pressure-peak-d0-work/`, keyed by draw index and the PLAN.md SHA-256.
On restart, reload completed draws, verify their keys and recompute nothing
already asserted; run only the remaining draws in the original draw order.
Record which draws were resumed. Checkpoints are working files, not deliverables.

Run the first **two draws (indices 0 and 1)** as the pilot, with all 12 folds,
the full six/twelve-start schedules and the required Mc/onset re-runs. Keep
those results among the 200. Record wall/CPU time, start timings and a projection
of the full run at 32 workers, stating the parallelism assumption. The projection
is reported for information only; it never stops or trims the run.

The planning estimate from C3e start timings is approximately
**14,400 A + 28,800 LC scheduled starts**, about **6-7 CPU h plus Mc/onset
re-runs**. Fallbacks are additional and counted separately. Do not reduce starts,
omit checks or trim draws for runtime.

After separate execution approval, use this order:

1. **Authenticate** `/home/tim/wasz-terminal-mass-evidence/upstream` and
   `/home/tim/pressure-peak-stage-a/.b0-b0c-onsets.csv` against the accepted source
   identities, including cohort/alias order, masks, pressure basis and observers.
   Use the read-only context path; do not invoke cache-writing historical mains.
2. **Replay C2 T2-F** DESCRIPTIVE_ALL objective `0.0719361259858887` on its saved
   support at `rtol=1e-12, atol=0` before objective comparisons.
3. **Replay all 28 committed C3e A and LC point fits**: 12 standard problems
   (DESCRIPTIVE_ALL + 11 ordinary folds) plus 2 twins per form. Check parameters,
   objectives and predictions at `rtol=1e-12, atol=0`; replay the committed
   Jacobian/numerical checks as specified above. No point optimizer reruns.
4. **Reproduce C2 draws**, exact sampler assertion and saved draw/fold mapping.
5. **Two-draw pilot and projection**, with prerequisites asserted before any
   dependent A/LC fit within those draws. Stop on a failed assertion; the
   projection never stops the run.
6. **Mc and capped onset-only re-run assertions** for the remaining draws and
   all folds, completing both 200 x 12 assertion sets before the remaining flow
   refits. Reuse already asserted pilot quantities; never substitute saved
   per-draw values after a mismatch.
7. **Refit A and LC** on the remaining paired draws, preserving the full starts,
   masks/settings, retained diagnostics, checkpoints and draw order.
8. **Comparator replays**, including all 2,400 saved T2-F per-fold objectives
   before any T2-F paired comparison, then its saved-refit predictions and all
   named saved point rows. No historical optimization.
9. **Report** the fixed grades, continuous values/intervals, paired differences,
   source hashes, qualifications, and cumulative wall/CPU time, including resumed draws; run the approved checks.

Any replay or assertion failure stops for owner review with the locations,
values and differences specified above. An interruption leaves an explicitly
incomplete stage that resumes from checkpoints, never a partial-draw grade. No post-result repair to the
scientific contract is authorized by this plan.

## Interpretation rules, verbatim

R1. "Grades measure capability on this retrospective cohort under the stated bands, not validation. A is primary; LC has five parameters and is EXPLORATORY. There is no overall PASS. Each MEETS, NEAR or MISSES is read with its continuous value and interval."

R2. "A and LC contain no onset law, so their onset grade is NOT_SCORED. The separate INHERITED row reports C2's capped onset-only law re-run on the same draws; its grade was fixed by C2 and is not evidence about either flow law. (In C2, T2-F took its Pd from that onset fit, so onset was part of T2-F; A and LC have no such link.)"

R3. "Scale consistency compares A's flow-fitted Pd with C2's capped onset-only Pd from independent fits on the same draws. Interval overlap gives the grade under the existing band. If the grade is MEETS while the paired per-draw difference interval excludes zero, the consistency is weak and comes from interval width; it is reported that way, not as a shared scale. A paired interval that contains zero means the two fits are compatible on these data; it does not show they measure the same physical quantity. With n near 2.5, A's Pd scales a convex opening, which is not the same functional scale as the onset law's Pd. Overlap shows the two fitted numbers are compatible on these data, not that they measure one physical scale. LC's comparison is reported, not graded: its Pd sits inside a mixture opening and is a different quantity again."

R4. "Paired differences use identical whole-brew draws. An interval that excludes zero is a paired difference on this cohort; one that includes zero is unresolved. T2-F per-draw values are replays of saved C2 refits, not new refits."

R5. "The within-2-bar ratio tests the held-out response shape. Report its improvement or deterioration alongside changes in the held-out residual of brew 1-2 and the held-out 3.5-bar residual. An improved ratio accompanied by deterioration elsewhere is a tradeoff, not evidence by itself that the low-pressure law has been fixed. Report the magnitudes; do not make an arbitrarily small worsening or the single 1.42-bar brew an automatic scientific veto. The 3.5-bar condition has three brews, so its interval is coarse. Neither brew 1-2 nor 3.5 bar is a veto for any form. Introduce no new post-result threshold."

R6. "Start disagreement uses the inherited spread > 1e-6*max(1,Jbest). Draws with start disagreement, bound-located parameters, fallbacks or censored training brews are kept and counted, never dropped. If such draws set an interval endpoint, say so. In a draw, f=0 supports A for that draw; at f=1, n drops out; at n=1, f drops out. Materially different parameters at near-equivalent objectives indicate weak practical identification; materially different objectives indicate optimization instability."

R7. "The graded peak uses the C1/C2 nominal-condition definition, which is lenient. The continuous global capacity maximum and its interval are the better guide to location; a nominal-band MEETS is not a precise peak claim."

R8. "Run order and dates are unavailable. Steps in conductance between conditions with near-proportional flow within a condition are also what a per-condition batch effect would produce. No result here can exclude that."

R9. "A five-parameter form must improve held-out predictions, not merely the in-sample objective, to earn its extra parameter. LC's results do not change A's grades."

## Later deliverables and this PR's stop

After approval only: add `puckworks/analysis/pressure_peak_stage_d0.py`, importing
earlier helpers unchanged, and `tests/test_pressure_peak_stage_d0.py`. Every
raw-data-dependent check needs a CI-runnable committed-field twin, using
`assert_allclose(rtol=1e-12, atol=0)` for numerical replays, with exact sampler
and membership checks where required. Cover source identities, point replays,
Mc/onset assertions, all saved T2-F objectives, start coverage, sampled training
isolation, metric arithmetic, interval provenance and labels. Run on Python
3.10 and 3.12; mark slow raw replays `pytest.mark.slow`. Do not replace a twin
with a saved success flag. Deliver one concise `SUMMARY.md` and
`RESULT_TABLE.csv` here, with source hashes and retained fields needed for those
checks, using existing table conventions. No new governance layers, receipts
or schema. Earlier stages and source data stay unchanged; no solver/EWP,
restart, new-data, R0 correction or automatic successor work.

**This PR contains only PLAN.md and status bookkeeping.** Keep
`pressure-peak-flow-turnover` active with `verified_commit=null`; set `next_gate`
exactly to **D0 plan awaits owner review**. Regenerate
`docs/planning/STATE_OF_TRUTH.md` with `python -m puckworks.statusdoc --write`,
never by hand. Run only documentation/status checks: status tests, Ruff if
applicable files are touched, and statusdoc verification. Do not run any
scientific test suite, evaluator, fit, pilot or replay now.

Push without force and open a draft PR with auto-merge off. Report the base main
SHA, branch, commit SHA, PR link, PLAN.md SHA-256 and statusdoc result, plus the
onset/Mc/start/scale decisions. Then stop for owner review.
