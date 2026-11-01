# PRESSURE-PEAK C3e: free-Pd W3 base and low-pressure forms

**PLAN ONLY. This PR authorizes no evaluators, fits, scientific diagnostics or results.** G1 retrospective screen, ungraded. **capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** Execution requires separate owner approval.

Base main: **a42b2d93936c35bf9e97c4201569b46953a90e7f**. GitHub confirms #406 is merged with that squash SHA; after fetching origin, `git merge-base --is-ancestor a42b2d93936c35bf9e97c4201569b46953a90e7f origin/main` returned exit 0. Branch **pressure-peak-c3e-plan** was created from that main. No merge of #406 is part of this task. The C3e PR stays draft, unmerged and with auto-merge disabled.

## Question and evidence

Using C3d arm A as the free-Pd base, can a recovery-law control, a clock contribution to conditioning, or a linear-convex opening mixture improve held-out 1- and 2-bar flow together? The primary base is A's ordinary 11-condition LOCO predictions. All comparisons remain conditional on this cohort, fixed Mc bank and trace objective.

Use the accepted 56 distinct brews at nominal 1, 2, 3.5, 4, 5, 6, 7, 8, 9, 11 and 13 bar, preserving the alias exclusion and source identities. Relevant datasets are `waszkiewicz2025/traces_per_brew` and `waszkiewicz2025/equilibrium_windows`, Waszkiewicz et al. (2025), Zenodo 18046315, CC-BY-4.0. The espresso data guide, source card and accepted C2/C3c/C3d artifacts supply the source-internal, single-rig, single-coffee limits. Raw traces and the onset cache were used in those accepted stages; this planning task reads repository evidence and settings, without fresh raw-data reduction or scientific calculation. Authenticate the existing files before execution: `/home/tim/wasz-terminal-mass-evidence/upstream/measurements_time_dependent` and `/home/tim/pressure-peak-stage-a/.b0-b0c-onsets.csv`. No source code from the deposit is imported.

Inherit [C3c's plan](../PRESSURE_PEAK_STAGE_C3C/PLAN.md), [C3d's plan](../PRESSURE_PEAK_STAGE_C3D/PLAN.md), its [summary](../PRESSURE_PEAK_STAGE_C3D/SUMMARY.md) and [table](../PRESSURE_PEAK_STAGE_C3D/RESULT_TABLE.csv), and the accepted [C2 table](../PRESSURE_PEAK_STAGE_C2/RESULT_TABLE.csv). The C3a context loader and C3c/C3d helpers identify masks, observers, banks and numerical settings. Earlier stages and source data stay unchanged.

## Four forms

Use raw line pressure, with the inherited nonnegative-pressure convention `P=max(Praw,0)`. Pressure is in bar, mass in g, time in s and flow in g/s. P0=0 throughout. Define

\[
H_n(P)=1-\exp[-(P/P_d)^n],\qquad
C_A(P)=aP_d H_n(P)\exp(-P/P_\star),\qquad
R(Y)=\exp[-\exp(-Y/M_c)].
\]

| Form | Flow and state law | Free parameters | Role |
|---|---|---|---|
| A | q=C_A R(M), dM/dt=q | a, Pstar, n, Pd (4) | C3d arm A, primary base |
| M1 | q=C_A R1(M), dM/dt=q | a, Pstar, n, Pd (4) | Recovery-law control |
| M2 | q=C_A R(X), dM/dt=q, dX/dt=q+v | a, Pstar, n, Pd, v (5) | EXPLORATORY |
| LC | q=C_LC R(M), dM/dt=q | a, Pstar, n, Pd, f (5) | EXPLORATORY |

For M1,

\[
R_1(M)=1-(1-\exp(-1))\exp(-M/M_c).
\]

M1 is a parameter-neutral recovery-law swap, not a pure shape comparison. At the same Mc, R(Mc) is about 0.6922 and R1(Mc) about 0.7675, so recovery speed changes too. These are supplied planning illustrations, not new screen results.

For M2, X(0)=M(0)=0 at A's stable-pressure origin, and X(t)=M(t)+v*t. Masks and censoring never pause or reset integration. There is no onset detector or fitted wetting event. v=0 reproduces A. Restart records are outside this screen; claim nothing about restarts.

For LC,

\[
C_{LC}(P)=aP_d\{(1-f)H_n(P)+f[1-\exp(-P/P_d)]\}\exp(-P/P_\star).
\]

LC means linear-convex mixture and avoids confusion with stage C2. f=0 reproduces A. At f=1, n drops out; at n=1, f drops out. A, M1 and LC also start at M(0)=0 at the same stable-pressure origin. No other forms or M2+LC combination are in scope.

## Fit problems, fixed bank and starts

Each form has DESCRIPTIVE_ALL, the 11 ordinary HYD-LOCO folds, and HYD-LOCO-1.0-OMIT-3.5 / HYD-LOCO-2.0-OMIT-3.5. Ordinary folds exclude the named condition from flow training. Twins also exclude 3.5 bar from flow training and are reported separately.

| Form | Ordinary plus descriptive problems | Omission twins | Starts per problem | Scheduled starts |
|---|---:|---:|---:|---:|
| A | 12 | 2 | 6 | 84 |
| M1 | 12 | 2 | 6 | 84 |
| M2 | 12 | 2 | 12 | 168 |
| LC | 12 | 2 | 12 | 168 |
| Total | 48 | 8 | | 504 |

There are **56 fit problems and 504 scheduled optimizer starts**, not 504 fits. Select starts by training objective only, never by held-out performance or report-only diagnostics.

Mc stays fixed across A, M1, M2 and LC for a given training mask, using the accepted C3c/C3d rule: `Mc_fixed_g` from the matching saved per-fold bank in C2 T2-F's `parameters_by_fold`, read through C3a's `ctx.saved`. Record the source artifact and fold key, actual Mc, flow-training brew IDs/conditions, held-out IDs and the bank's ordinary training mask. DESCRIPTIVE_ALL uses its full-cohort entry; ordinary folds use their own entries. Do not recalculate Mc or substitute a candidate's estimate.

Twins reuse their ordinary fold's Mc, as in C3c/C3d. **3.5-bar information remains in Mc.** These twins assess omitting 3.5 bar from flow fitting, conditional on that inherited scalar. They do not establish robustness to removing 3.5 bar from the whole calibration pipeline. Its effect has not been measured, so do not call it a minor leak. Keep this distinction in the eventual report. The twins are sensitivity tests comparable with C3c/C3d twins; remove 3.5 bar from flow loss and renormalize inherited weights without changing the bank or ordinary-fold seeds.

The six A starts are C3d arm A's exact schedule: each `(a,Pstar,n)` in `(1,15,1)`, `(1.5,30,2)`, `(2,8,4)` crossed, in that order, with Pd equal to the matching fold's saved onset Pd and 4.0 bar. Keep both groups even when their seeds nearly coincide. M1 uses those six. M2 crosses those six with v in `{0,0.3}` g/s; LC crosses them with f in `{0,0.1}`. Twins reuse ordinary-fold starts, not the fitted ordinary optimum. Record both seed groups, original and optimizer-clipped coordinates, and every attempt.

No form uses an onset-derived fixed Pd or an onset loss. Training-brew onsets enter through B0c masks and the saved-Pd start; no held-out onset time enters that fold's optimization. Record group objectives and parameter ranges, including whether only saved-onset-Pd seeds reach the selected objective under the inherited disagreement rule. A numerical argmin in that group alone is not start dependence when group objectives agree.

## Objective, bounds and first execution steps

Keep **B0c's post-onset trace objective**, scored from observed onset + 2 s through clean support. Post-onset trace shape already enters the fit; the pre-onset stretch is unscored. Integrate from stable-pressure zero through masked intervals without resets. Observed cup mass never drives the model state. Use full measured pressure histories, the inherited 0.5-s fitting grid, 0.1-s reporting grid and the stored 100-s endpoint observer. Do not replace that observer with a new endpoint window or constant condition-mean forcing.

For represented training conditions G and N_g brews in condition g,

\[
w_i=\frac{1}{|G|N_g},\qquad
L_i=\frac{\sum_j m_{ij}(q_{ij}-q^{obs}_{ij})^2}{\sum_jm_{ij}},\qquad
J=\sum_i w_iL_i.
\]

This preserves equal-condition/equal-brew weighting and duration normalization. Report condition components and shares of J. Absolute g/s residuals give low-flow conditions little weight. No reweighting is authorized. The historical joint scales 0.437 g/s and 4.534 s stay unchanged but are not applied to this flow-only objective.

Any additional early-trace or pre-onset diagnostic is report-only: it must not select starts or trigger post-result bound changes. If the fitted observations do not distinguish large v values, report that limitation explicitly. Diagnostic agreement is not parameter identification.

Bounds are a=[0.001,20] g/s/bar, Pstar=[0.5,100] bar, n=[1,infinity), Pd=[0.1,100] bar, plus v=[0,10] g/s for M2 and f=[0,1] for LC. Optimize `(log(a),log(Pstar),n,log(Pd))`, appending linear v or f. The f bounds follow the mixture interpretation. The v bounds provide broad computational coverage, not a physical range. Do not expand a bound after results.

For Mc ~ 28.7 g, v = 10 g/s contributes v*t/Mc ~ 34.8 by 100 s from the clock alone. Since X = M + v*t, the total X/Mc also includes M/Mc. The clock alone reaches R ~ 0.99 after about 13.2 s. Large v values are near-indistinguishable at the endpoint; the scored early trace must constrain rapid conditioning if it can. This supplied illustration does not justify a physical bound. Report Mc/v with each fold's actual inherited Mc, infinity at v=0.

Execution starts only after approval, in this order:

1. Authenticate source identities and replay T2-F's saved reference objective **0.0719361259858887**. Replay the applicable saved ordinary-fold objectives before comparing them. A replay failure stops execution for owner review.
2. Replay C3d arm A's committed predictions and objectives for all five accepted fits at their saved parameters, including its twins. These are replays, not historical refits.
3. Confirm M2 at exactly v=0 and LC at exactly f=0 reproduce A with inherited `assert_allclose(rtol=1e-12, atol=0)` tolerances. Keep the exact identities separate from optimizer interior clipping. Verify analytic derivative limits and synthetic boundary cases before candidate fitting, with no new tolerance.
4. Run the declared schedule. For each training mask, A's optimum is a feasible benchmark for M2 at v=0 and LC at f=0. Evaluate those embeddings without adding optimizer starts. A materially worse returned training objective, under the inherited objective-disagreement diagnostic, flags an implementation or optimization problem, not evidence against the larger model. Preserve the selected start and benchmark separately; neither silently adds a start nor replaces the optimizer result. M1 has no such nesting claim.

Use inherited `least_squares`, analytic Jacobian, `x_scale="jac"`, ftol/xtol/gtol=1e-8 and 500 evaluations per scheduled start. Preserve 1e-10 interior clipping at finite bounds. Select the lowest converged finite J. Only if none converges, retain the inherited 1500-evaluation dogbox fallback from the lowest-cost finite attempt, recorded separately from the 504 scheduled starts. An unresolved fit or nonfinite evaluation stops for owner review. No post-result change to bounds, starts, masks, settings or rules is authorized.

## Numerical diagnostics after approval

Retain every start's initial/final parameters, objective, convergence, failures, bound distances and censored training-brew counts by condition. Censoring means C=0 throughout the masked trace, not onset non-detection; distinguish structural zeros from underflow. Convergence with such zeros does not establish an identified fit. Keep stable large-power evaluation and the zero limit of `x**n*log(x)` at x=0. Do not change earlier helpers to implement these forms.

Check the complete weighted-residual analytic Jacobian at selected fits with inherited transformed-coordinate `h=1e-4*max(1,abs(z))` and h/2, retaining applicable initial boundary checks and branch counts. Use central differences where feasible and one-sided differences at bounds; never evaluate outside the declared domain. Report analytic-versus-FD and full-versus-half-step norms, absolute errors and analytic norms. Smooth errors should decrease on halving until roundoff dominates; investigate contrary behavior without a new numeric band. LC's vanishing derivative columns at f=1 or n=1 are structural, not necessarily a coding error.

Retain C3d's accepted replay distinction: committed objectives, endpoints, residuals, parameters and saved-field arithmetic use `assert_allclose(rtol=1e-12, atol=0)`. Do not demand 12-digit replay of roundoff-dominated FD cancellation remainders. Replay analytic norms, branch counts and the declared halving direction; if relative FD errors are stored, verify from committed fields that relative=absolute/analytic norm with the same tolerance, handling zero norms through the saved absolute errors. No FD tolerance band is added.

Start-objective disagreement remains `spread > 1e-6*max(1,Jbest)`. Near a finite bound means the inherited 1e-6 fraction of its transformed-coordinate range; for unbounded n, report the lower-bound distance and optimizer active flag. Show physical parameter ranges even when objectives agree. Use these inherited diagnostics to distinguish numerical noise from material differences; do not invent parameter-identification thresholds. Upper-v-bound estimates leave bound sensitivity unresolved, without permission to expand the bound.

At frozen parameters, evaluate each candidate and matching A/reference on the 0.5-s and 0.1-s grids without refitting. A positive coarse-grid objective gain is unresolved at the fitting resolution if it changes sign or its between-grid change is at least that gain. Report the warning beside held-out improvements; it does not authorize tuning. The same inherited diagnostic applies to material nesting discrepancies, alongside start agreement and Jacobian evidence.

## Reports and metric compatibility

Report ordinary LOCO predictions fold-for-fold, with DESCRIPTIVE_ALL explicitly in-sample and twins separate. No pooling of twins or descriptive predictions into the primary 11-fold summary.

- All 11 held-out condition-mean signed residuals per form and the nine individual low-pressure out-of-fold brew predictions, observations and residuals. Errors are prediction minus observation. Highlight brew 1-2 from ordinary LOCO-1 and 3.5 bar from ordinary LOCO-3.5.
- The existing 1/2/3.5-bar signed mean bias and mean absolute condition residual, plus the separate screen metrics `bias12=(e1+e2)/2` and `mae12=(abs(e1)+abs(e2))/2`. Keep all per-condition errors visible because signed errors cancel.
- The within-2-bar ratio from ordinary LOCO-2, using full measured pressure histories and the same observer: `mean(qhat[2-2],qhat[2-4])/mean(qhat[2-3],qhat[2-5])`. This is a ratio of pair means. Recompute the observed counterpart from authenticated data; the supplied rounded 1.249 is context, not a target to hard-code or a tolerance. Report absolute discrepancy from the observed ratio and its change from A beside the changes in absolute brew 1-2 and 3.5-bar residuals. If a denominator is zero, report it as undefined rather than flooring it.
- Endpoint and trace RMSE with inherited condition/brew weighting, late trends on resolved 2/3.5/4/5/6-bar conditions, condition objective shares, parameters and Mc provenance by fold, and all start/numerical qualifications. Use the inherited late-window observer, not a new slope window.
- Continuous **global capacity maximum** over nonnegative pressure for every fit. Check all stationary candidates and endpoint limits, including possible competing LC maxima; do not equate one local maximum with the global peak or substitute a pressure-grid peak. Report the ordinary-fold median and range, explicitly not confidence intervals; give DESCRIPTIVE_ALL and twins separately. Report peak location and capacity with the fit label.
- Project >=9-bar slope, regressing condition-mean predicted endpoints against actual mean endpoint line pressures at nominal 9/11/13 bar. Report (i) DESCRIPTIVE_ALL condition means and (ii) ordinary out-of-fold 9/11/13-bar means. The latter is a predictive summary across three fitted models, not one curve's derivative. Do not substitute a dense pressure-grid regression. Label any twin slope separately.

Comparators are A and C2 T2-F from its accepted artifacts, with no historical refits. Before comparison, confirm cohort/alias membership, pressure basis, observer, masks, normalization, weighting, fold mapping and slope definition. Reuse compatible saved predictions/fields; label frozen-parameter evaluations as plug-in where needed. Do not call unmatched results paired or imply paired uncertainty without refits. Ordinary A comparisons are matched fold-for-fold; no new onset fit, onset prediction or scale-consistency claim follows from free flow Pd.

## Interpretation rules, verbatim

1. "A's ordinary 11-condition LOCO predictions are the primary base. M1, M2 and LC are judged first on whether absolute held-out condition-mean residuals fall at both 1 and 2 bar relative to the matching A folds. Improvement at one is a tradeoff. Passing this low-pressure screen does not establish overall preference: peak, slope, all other held-out conditions, trace behaviour and the existing full-stage grading rules remain applicable. DESCRIPTIVE_ALL is descriptive only."

2. "The within-2-bar ratio tests the held-out response shape. Report its improvement or deterioration alongside changes in the held-out residual of brew 1-2 and the held-out 3.5-bar residual, relative to matching A predictions. An improved ratio accompanied by deterioration elsewhere is a tradeoff, not evidence by itself that the low-pressure law has been fixed. Report the magnitudes; do not make an arbitrarily small worsening or the single 1.42-bar brew an automatic scientific veto. Introduce no new post-result threshold."

3. "Run order and dates are unavailable. Steps in conductance between conditions with near-proportional flow within a condition are also what a per-condition batch effect would produce. No result here can exclude that."

4. "Boundary estimates, near-zero contributions and disagreements across starts are reported explicitly. A stable optimum at v=0 or f=0 can support retaining the nested base and is not, by itself, evidence of non-identifiability. Materially different parameters at near-equivalent objectives indicate weak practical identification; materially different objectives indicate optimization instability. At f=1, n drops out; at n=1, f drops out. An upper-v-bound solution flags unresolved bound sensitivity. A five-parameter form must improve held-out predictions, not merely the in-sample objective, to earn its extra parameter."

## Closeout and limits

This screen is ungraded. Existing full-stage bands remain unchanged as recorded in C3c's plan: accuracy vs B1 with +/-0.25 g/s tie band; nominal peak interval overlap at 5-7 bar for MEETS or 4/8 for NEAR; slope overlap with the observed interval for MEETS or within [-0.176,-0.020] for NEAR; resolved trends >=4/5 or 3/5; onset RMSE <=3.51 or <=4.53 s; magnitude of signed low-pressure bias <=0.10 or <=0.20 g/s; scale intervals overlapping or separated by <=1 bar. Keep their original definitions and qualifications, with no overall PASS. Fold ranges here cannot replace full-stage uncertainty intervals or earn grades. A later full stage still needs separate approval for 200 paired whole-brew refits, seed 20261105.

Python only, no bootstrap, profiling, onset refit, solver work, restart analysis, new data collection or automatic successor. Retain C0's two-hour cumulative execution cap, including retries, interrupted attempts and checks. Parallel workers are allowed with one BLAS thread per worker set before imports. Stop and ask if a rule blocks completion; do not silently skip required work. Leave R0's known extraction time-step issue alone.

After implementation approval, use a new C3e analysis module and focused tests importing earlier helpers unchanged. Deliver one concise SUMMARY.md and RESULT_TABLE.csv with source hashes and committed-field CI twins for raw-data-dependent checks, following existing conventions without new schemas or receipts. The report must retain the Mc/omission distinction and all four interpretation rules. Tests must cover the nested identities, zero/boundary cases, source and training isolation, 56 problems/504 scheduled starts, metric arithmetic and labels on Python 3.10 and 3.12.

**This PR changes only this PLAN.md and status bookkeeping.** Keep `pressure-peak-flow-turnover` active with `verified_commit=null`; set `next_gate` exactly to **C3e plan awaits owner review**. Regenerate STATE_OF_TRUTH.md with `python -m puckworks.statusdoc --write`, never by hand. Only documentation/status checks run now. Push without force, open a draft PR with auto-merge off, report base main SHA, branch, commit SHA, PR link, PLAN.md SHA-256 and statusdoc result, then stop for owner review. No scientific execution or result artifacts in this delivery.
