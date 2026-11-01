# PRESSURE-PEAK C3c: low-pressure flow screen plan

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** G1 retrospective, ungraded. **PLAN ONLY: implementation, candidate fits and results are not authorized.** This draft incorporates owner amendments 0–6 and the subsequent pressure-basis clarification. No EWP/solver work, restart work, new data collection, production change or automatic successor.

Base main: `7fec5e16712c1eb3fd2340ea13d68b9f41e60024`. PR #404 squash commit: `7fec5e16712c1eb3fd2340ea13d68b9f41e60024`. Findings branch head: `479635b74d15af76b93abe53c0a0f194ea342567`. Branch: `pressure-peak-c3c-plan`, created from that main. The owner accepts content equivalence after the squash, not ancestry. After `git fetch origin`, this check returned an empty diff, exit 0:

```bash
git diff --exit-code 479635b74d15af76b93abe53c0a0f194ea342567 origin/main -- \
  docs/research/PRESSURE_PEAK_FINDINGS.md docs/status/current.json \
  docs/planning/STATE_OF_TRUTH.md
```

If this prerequisite check differs before starting a replacement plan branch, stop and show Tim the diff; do not reconcile it. Never force-push. Update an existing branch by merging main.

## Evidence and scope

Read [findings](../PRESSURE_PEAK_FINDINGS.md), C3b/C3a PLAN/SUMMARY/RESULT_TABLE, C2 reference artifacts, C1/C0 summaries, and the C0/C1/C2/C3a/C3b helpers. B0's `sustained_onset`, `measure_onsets`, pressure calibration and clean-support conventions govern reuse. Repository instructions, the espresso data guide, MANIFEST, available-data register and Waszkiewicz card were inspected. Underlying local raw traces and the onset cache were inspected in the advisor's preceding read-only review, not just catalog metadata. No new candidate calculation is part of this plan delivery.

Use `waszkiewicz2025/traces_per_brew`, `waszkiewicz2025/equilibrium_windows` and `waszkiewicz2025/brewer_quadratic`. Native records are under `/home/tim/wasz-terminal-mass-evidence/upstream/measurements_time_dependent`; reuse `/home/tim/pressure-peak-stage-a/.b0-b0c-onsets.csv` read-only. Join C2's 56 distinct brew IDs and 11 conditions; preserve the alias exclusion. Use C3a's read-only context loader, not cache-writing parent entry points. Existing evidence is source-internal, single-rig and target-exposed; derived flow and cup mass share information. Accepted earlier negative results remain unchanged. Waszkiewicz et al. (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0; no upstream source-code import.

## Family, fit scope and objective

Pressure is in bar, time in s, mass in g, flow in g/s. With `P=max(Praw,0)`:

\[
x=\frac{\max(P-P_0,0)}{P_d},\qquad
C=aP_d[1-\exp(-x^n)]\exp(-P/P_\star),\qquad
q=C\exp[-\exp(-M/M_c)],\quad \dot M=q,\quad M(0)=0.
\]

**W3:** fit `(a,Pstar,n)`, with `P0=0`. **W4, EXPLORATORY:** fit `(a,Pstar,n,P0)`. These are three/four flow parameters; the saved preceding onset calibration has four parameters of its own. W4 at `n=1` reproduces T2-F, and W4 at `P0=0` reproduces W3. These identities do not make W3 a superset of T2-F.

Fix Pd and Mc to the matching saved C2 fold, including DESCRIPTIVE_ALL. Keep the separate saved capped onset law, its parameters and predictions unchanged. Initialize hydraulic mass at stable zero; never reset it at observed onset. Observed onset defines targets/masks only, and observed mass never drives the fitted hydraulic state. Preserve raw line forcing, B0c observed-x1-onset+2-s mask, clean support, duration normalization, equal-condition/equal-brew weights, 0.5-s fit/0.1-s reporting grids, and the stored 100-s endpoint observer. The inherited detector requires strict mass >0.5 g AND smoothed flow >0.1 g/s for 2 s, reporting interval start; do not redefine it or fit C3b's model-side detector.

For represented training conditions G, brew weights are `w_i=1/(|G|*N_g)`. With the fixed mask `m_ij`:

\[
L_i=\frac{\sum_jm_{ij}(q_{ij}-q^{obs}_{ij})^2}{\sum_jm_{ij}},\qquad
J=\sum_iw_iL_i,\qquad J_g=\sum_{i\in g}w_iL_i,\quad s_g=J_g/J.
\]

For each selected W3/W4 fit, report every training condition's `J_g` and share `s_g`, which sum to J and 1. If J is exactly zero, shares are undefined; retain the zero components. Replay matching saved T2-F parameters on the same training support and report its components/shares alongside. Reduced-training evaluations of saved T2-F are plug-in evaluations, not new reference refits. Removed/held-out conditions have no training share; label them excluded rather than silently treating their loss as zero.

> Residuals are absolute g/s, so low-flow conditions carry little weight. Condition shares show which conditions determine n. This screen does not reweight the objective; any reweighting needs separate approval.

Shares identify loss contributions, not unique causal identification of n; report n across starts and folds alongside them. Before any candidate comparison, replay DESCRIPTIVE_ALL T2-F's saved J `0.0719361259858887` using `assert_allclose(rtol=1e-12, atol=0)`, then replay each saved standard fold. Distinguish this unscaled flow loss from joint loss. Joint scales remain 0.437 g/s and 4.534 s; no joint fit is authorized in this screen.

Run **14 point fits per form, 28 total** after separate approval: DESCRIPTIVE_ALL, all 11 ordinary LOCO folds, and two additional held-out fits. The additional fits hold out 1 bar with 3.5 bar also removed from flow training, and hold out 2 bar with 3.5 bar also removed. Renormalize the unchanged equal-condition/equal-brew weighting over the remaining training conditions. Use exactly the matching standard fold's bounds, starts, settings, saved onset bank and fixed Mc. Do not refit onset. Thus the omission isolates 3.5-bar flow-loss dependence; it does not remove that condition from the historical calibration of fixed nuisance quantities. Report the extra held-out 1/2-bar signed residuals beside their standard-fold residuals. Never pool these extra predictions into the standard 11-fold aggregate.

> If held-out 1-bar or 2-bar residuals change materially when 3.5 bar is removed from training, the low-pressure result leans on the 3.5-bar condition and we will say so. These are additional held-out tests, unlike the in-sample 3.5-omitted curves in rule 3.

Define materiality before results: for each form f and held-out condition h, let `B_{f,h}=abs(r_f,standard,h-r_T2F,standard,h)`. Flag material dependence for form f when `abs(r_f,omitted,h-r_f,standard,h)>B_{f,h}`. If `B_{f,h}=0`, any nonzero change meets this comparative rule. Report both quantities, the direction of the change, and whether an improvement relative to T2-F is retained, lost or reversed. This is a dependence diagnostic, not a new accuracy band; even an improvement after omission establishes dependence. No retuning follows it.

## Bounds, starts and numerics fixed before execution

Use C2 bounds for shared parameters: a `[0.001,20]` g/s/bar, Pstar `[0.5,100]` bar, P0 `[-5,5]` bar. Set n in `[1,infinity)` with no invented finite upper bound. Optimize `(log(a),log(Pstar),n[,P0])`; Pd/Mc are fixed. Evaluate large powers through stable log-domain/asymptotic expressions using floating-point representability, not a fitted cutoff. Any unresolved nonfinite evaluation is reported, not concealed by changing bounds.

W3's three physical starts `(a,Pstar,n)` are `(1,15,1)`, `(1.5,30,2)`, `(2,8,4)`. W4 has those same three starts with `P0=0`, plus its matching saved C2 T2-F `(a,Pstar,n=1,P0)` start. This includes `P0=0,n=2`, which permits positive capacity in every positive-pressure 1-bar history. Check its zero-capacity counts explicitly; a contradictory result requires investigation, not a claim that the safeguard ran. Additional omission fits reuse these exact matching-standard-fold starts, not the newly fitted standard optimum. Total: **98 starts**, plus only the inherited fallback if needed. Preserve original and optimizer-clipped start coordinates; apply C2's `1e-10` interior clipping at finite bounds, while evaluating the exact n=1 identity separately.

Use C2 `least_squares`, analytic Jacobian, `x_scale="jac"`, ftol/xtol/gtol `1e-8`, 500 evaluations/start; if none converges, its lowest-cost finite attempt supplies the 1500-evaluation dogbox fallback. Retain all attempts, parameters, objectives, convergence and failures; select the lowest converged J. An unresolved fit stops the run for owner review; no fit is dropped. Reuse the C3a/C3b start-objective disagreement flag `spread > 1e-6*max(1,Jbest)` and finite-coordinate bound proximity `1e-6` of coordinate range. For unbounded n report its exact lower-bound distance and optimizer active flag, without inventing a range. Report parameter spreads even at equal J; n at its lower bound does not support additional convex opening, and a large or start-sensitive n is not an identified physical exponent.

With `u=x**n`, `du/dn=x**n*log(x)`; guard x=0 with the zero limit. Use stable `-expm1(-u)` and analytic derivatives through the unchanged memory inversion. For x>0, with `A=a*exp(-P/Pstar)`, capacity derivatives are `C_log(a)=C`, `C_log(Pstar)=C*P/Pstar`, `C_n=A*Pd*exp(-u)*u*log(x)`, and `C_P0=-A*n*x**(n-1)*exp(-u)`. At x=0 use the inactive side; n=1 inherits T2-F's kink. Do not evaluate `log(0)` or rely on `0*infinity` cancellation. Test positive/zero pressure, large-u limits, and the n=1/P0=0 identities using synthetic and committed numerical fixtures.

For every W4 start, count censored **training** brews at initial and final points, including failed attempts: here censored means `C=0` throughout the masked trace, not an onset non-detection. Report counts by condition, structural zeros (`P<=P0`) and any numerical underflow separately. If the selected fit retains such brews, report possible flat-gradient dependence and the other starts; do not infer a well-identified optimum from convergence alone.

For W4 specifically, report how many training brews have P0 inside the minimum-to-maximum pressure range on the masked fit grid, how many adjacent masked pressure segments bracket/touch P0, and exact threshold coincidences. The fit grid is in time, so there is no uniform pressure increment to use as an invented near-threshold band. These counts describe exposure to the kink; they are not rejection criteria.

Check the complete weighted-residual analytic Jacobian against finite differences at every selected W3/W4 fit and at W4's initial n=1 starts. Use the C3b transformed-coordinate step `h=1e-4*max(1,abs(z))`, then h/2; center where feasible and use one-sided differences at bounds. Recompute all threshold branches, count branch changes, and report analytic-versus-FD and full-versus-half-step relative norms and absolute errors when a norm is zero. Smooth synthetic checks should improve with halving until roundoff dominates; investigate contrary behavior. At threshold switches, report nonsmoothness separately from a derivative coding error. Do not claim an identified optimum from unstable derivatives or give it a new arbitrary pass band.

At frozen fitted parameters evaluate candidate and matched reference J on both the 0.5-s and 0.1-s grids, without refitting. Report the gain on each grid and their difference. If a positive coarse-grid gain changes sign, or its between-grid change is at least that gain, call the objective improvement unresolved at the fitting resolution. Report the result without post-holdout retuning. Identities/replays use `assert_allclose`, rtol `1e-12`, atol 0; never exact float equality as a replay assertion. Any additional numerical tolerance must have its purpose fixed in an owner-reviewed amendment before results.

## Reports and interpretation fixed before results

Report all starts and fold parameters; endpoint and trace RMSE; standard held-out signed residuals at all 11 conditions; 1/2/3.5-bar signed mean bias and mean absolute condition residual; extra omission residuals; condition objective shares; and late trends on the resolved 2/3.5/4/5/6-bar conditions. The primary comparator is saved C2 T2-F; show saved C2 joint, C1/C0/E1/F1/B1 metrics where relevant, with their stage and objective conventions. Do not silently refit comparators. Full-cohort and extra-omission results remain separate from ordinary LOCO metrics.

Report each fit's constant-pressure 100-s response on C2's 1:0.05:13-bar grid, its nominal-condition peak and continuous capacity peak. For x>0 the latter satisfies

\[
\frac{n x^{n-1}}{P_d[\exp(x^n)-1]}=\frac1{P_\star}.
\]

Check domain endpoints and label boundary maxima. At common fixed Mc, stable-zero initial mass and constant pressure, the endpoint is increasing in capacity, so these peak locations agree apart from grid resolution. Preserve the ordinary-LOCO median/range convention; ranges are not confidence intervals. For the project >=9-bar slope, regress condition-mean predicted endpoints against actual mean endpoint line pressures at nominal 9/11/13 bar, as C2; do not substitute a dense pressure-grid regression. Report inherited onset RMSE/minimum, training-only cap/floor diagnostics and the known P0=-5-bar onset fit holding out 1 bar; no onset refit or held-out cap.

Retain these original interpretation rules verbatim:

1. “Failure to replay the reference objective blocks objective comparison until the discrepancy is explained.”

2. “A lower in-sample objective is descriptive. The central test is whether absolute held-out endpoint residuals decrease at both 1 and 2 bar relative to C2 T2-F. Improvement at only one is a tradeoff, which we will report rather than hide in their signed mean.”

3. “The 3.5-bar condition has three brews. Report its residual separately. Compare the full-cohort and 3.5-bar-omitted fitted curves at 1 and 2 bar to expose dependence on that condition. Those 1/2-bar predictions are in-sample diagnostics, not additional held-out tests.”

4. “Pressure-history variation is already an input to C2. Report the nine low-pressure brews’ early pressure, 100-s pressure, and range through 100 s. The basket estimate is derived using observed flow; it is not an independent pressure measurement or an authorized alternative fitting arm in this screen.”

5. “Report predicted capacity, hydraulic mass and memory multiplier at 100 s. A no-memory calculation with frozen parameters is plug-in only. Any observed-mass-based capacity reconstruction is a conditional diagnostic, not an independently measured capacity or a replacement fitting target.”

6. “Positive 1-bar flow alone does not establish an adequate shape. Report all condition residuals, low-pressure signed bias and mean absolute condition residual, continuous peak, high-pressure slope, and late trends. A better low-pressure fit may worsen the peak or slope, and that tradeoff remains a useful result.”

7. “Unchanged onset predictions are inherited results. Fixing Pd from onset cannot establish scale consistency, and n differing from one changes the interpretation of that pressure scale.”

8. “Bound hits, disagreeing starts, weakly identified parameters and numerical sensitivity limit parameter interpretation even when the objective improves. Retain every start and failure. Negative P0 is an offset diagnostic, not a physical entry pressure.”

9. “In-sample screens can mislead and do not replace LOCO + paired whole-brew refits. Point LOCO remains retrospective and target-exposed.”

Rule 3 uses the ordinary 3.5-bar-held-out flow fit, not either of the two additional omission fits. A changed low-pressure curve there is evidence of dependence within the descriptive fit; the additional tests assess held-out dependence as specified above. For any observed-mass proxy in rule 5, define the increment from stable time zero, preserve its baseline and clock, and label it a cup-mass proxy for the model state. It never enters the fit.

> The A.MACHINE correction at 1 and 2 bar is about 0.28 bar, mostly the constant c. A positive W4 P0 of similar size is consistent with a basket-pressure offset and is not evidence of a physical entry threshold.

Use the existing `Pbasket=Pline-(a_machine*q_obs**2+b_machine*q_obs+c_machine)` audit, with `A.MACHINE=(0.017184292098914252,0.03670858658698296,0.2831597837775055)`. This is a declared pressure interpretation only; raw line pressure remains the fitting input.

> W3 and W4 keep the exp(-P/Pstar) high-pressure decline. We do not expect them to fix the >=9-bar slope; a slope result that stays MISSES or NEAR is expected, not a failure of the low-pressure aim.

Those labels describe the unchanged full-stage criteria, not grades awarded by this ungraded screen. Report slope changes and any improvement without making a slope grade a new advancement gate.

## Existing plug-in illustration, not C3c results

Two plug-in runs of W3 at n=2 with C2 Pd/Pstar/Mc (3.9844972419062152 bar, 12.213432655100736 bar, 28.709461834955388 g), a matched at the 4-bar condition, constant condition-mean pressures, M(0)=0. Codex's run (a=0.9134045044685302, mean pressures 1.0454/1.791125/3.44575/4.076975 bar) gave 0.108/0.407/1.412 g/s at 1/2/3.5 bar; the advisor's run (a=0.9131) gave 0.108/0.407/1.411. The third-decimal difference comes from inputs, and neither is a test tolerance or a trace refit.

Use the clarified continuous peak **6.095 bar** (6.10 on the 0.05-bar grid) and project >=9-bar slope **-0.12933 g/s/bar**, using actual mean pressures of the 9/11/13-bar conditions. The advisor's -0.126 came from a line fitted to a dense 0.05-bar grid over 9-14 bar, which is not the project slope definition; the difference is method, not error.

Also retain the supplied n sensitivity with a rematched at 4 bar: 1-bar flow **0.259/0.108/0.049/0.023 g/s** at n=**1.5/2/2.5/3**. These are supplied planning numbers, not newly computed or independently replayed C3c results. One-point amplitude normalization and constant condition-mean pressures are target-exposed and omit the measured pressure histories. They motivate the screen; they neither establish low-pressure held-out capability nor replace the trace objective. No new calculations were run for this illustration during plan preparation.

## Unchanged bands, later delivery and stop

Screens have no MEETS/NEAR/MISSES/PASS grades. Preserve the owner's full-stage bands: accuracy vs B1 with +/-0.25 g/s tie band, MEETS=TIE or BETTER and NEAR=UNRESOLVED with lower error; each fit's own nominal-condition peak interval MEETS if it overlaps 5–7 bar, NEAR if it overlaps 4 or 8 bar; slope MEETS if it overlaps observed [-0.0880,-0.0403] g/s/bar, NEAR if within [-0.176,-0.020]; resolved trends MEETS >=4/5, NEAR 3/5; onset RMSE MEETS <=3.51 s, NEAR <=4.53 s; magnitude of signed mean low-pressure bias MEETS <=0.10 g/s, NEAR <=0.20 g/s, always alongside per-condition residuals and their mean absolute value; scale consistency MEETS for interval overlap, NEAR for gap <=1 bar. Lean on the continuous peak when interpreting the lenient nominal criterion. No overall PASS and no band changes after results. Fixed Pd is not an independent consistency test.

Any later full stage needs separate approval and **200 paired whole-brew refits, seed 20261105**, preserving the 11 LOCO folds, fold-fixed Mc and training-only onset caps with inactive training floor. Retain failures, wide/bimodal intervals and boundary dependence. A useful four-parameter result is not rejected solely for complexity.

Later implementation belongs in new `puckworks/analysis/pressure_peak_stage_c3c.py` and focused tests, importing earlier helpers without editing them. Deliver one concise `SUMMARY.md` and `RESULT_TABLE.csv` in this directory, using the existing table conventions, no new schema or receipts. Retain all starts, fold/condition/brew arithmetic, omission membership, source hashes and numerical fixtures. CI on Python 3.10/3.12 must verify nesting/replays, derivative limits, training isolation, exact fit/start coverage, objective-share sums, residual/slope arithmetic and labels from committed fields. Every raw-data-dependent check needs a CI-runnable CSV twin, not a saved success flag.

Default serial execution later; parallel workers each get one BLAS thread (`OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=OMP_NUM_THREADS=1` before imports). Retain C0's **two-hour cumulative wall cap**, including retries and interrupted attempts. Runtime is unmeasured for this family; the cap is not extended to finish an incomplete run. Keep earlier stages/source data unchanged and leave R0's known extraction time-step issue alone.

This delivery changes only this plan, the existing active status item's next_gate, and generated STATE_OF_TRUTH.md. Keep verified_commit=null. Regenerate only with `python -m puckworks.statusdoc --write`, then verify; do not hand-edit the generated document. Run relevant documentation/status checks and open a **draft** PR for owner review. Report base main SHA, #404 squash SHA, content-diff result, branch, pushed commit SHA, draft PR number, PLAN.md SHA-256 and statusdoc result. After approved implementation, report RESULT_TABLE.csv and SUMMARY.md SHA-256 as well. If a rule blocks the task, stop and ask Tim. No implementation, candidate fits, result artifacts or successor work until the owner approves the plan.
