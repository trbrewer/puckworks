# PRESSURE-PEAK C3d: Pd transfer in the low-pressure folds

**PLAN ONLY. No implementation, candidate fits or results are authorized by this delivery.** G1 retrospective screen, ungraded. **capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.**

Base main and #405 squash commit: **de8ee1ca34919bbbdfac3b76ac9a7a216d0a3279**, confirmed by fetching origin. Branch: **pressure-peak-c3d-plan**, created from that main. This plan includes the owner's clarification about training-onset inputs to arm A and the added start-dependence sentence in rule 4. Python only; no EWP, restart work, new data collection or automatic successor.

## Question and evidence

Do W3/W4 fail the held-out 1- and 2-bar conditions because of the flow law, or because those folds inherit an onset Pd of 7.37 and 4.86 bar? C3c alone cannot separate those explanations.

Read [C3c's plan](../PRESSURE_PEAK_STAGE_C3C/PLAN.md), [summary](../PRESSURE_PEAK_STAGE_C3C/SUMMARY.md), [table](../PRESSURE_PEAK_STAGE_C3C/RESULT_TABLE.csv), the C2 reference table and the C1/C2/C3a/C3c helpers before implementation. The inherited bounds, starts, masks and fixed quantities were checked against those files during planning. The espresso data guide, Waszkiewicz card and manifest identify the same source-internal, single-rig, single-coffee evidence. Local raw traces and the onset cache were inspected during the preceding C3c work, not just catalog metadata; this plan adds no raw-data reduction or candidate calculation.

Reuse the 56 distinct brews and 11 nominal conditions, with the existing alias exclusion. Sources are waszkiewicz2025/traces_per_brew and waszkiewicz2025/equilibrium_windows; waszkiewicz2025/brewer_quadratic remains pressure-interpretation context only. Native files are under /home/tim/wasz-terminal-mass-evidence/upstream/measurements_time_dependent; the read-only cache is /home/tim/pressure-peak-stage-a/.b0-b0c-onsets.csv. Use C3a's read-only context loader. Data: Waszkiewicz et al., [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0. Do not import upstream source code.

## Arms and exact fit coverage

Retain C3c's family, with pressure in bar, mass in g, flow in g/s and time in s:

\[
P=\max(P_{\rm raw},0),\quad x=\frac{\max(P-P_0,0)}{P_d},\quad
C=aP_d[1-\exp(-x^n)]\exp(-P/P_\star),
\qquad q=C\exp[-\exp(-M/M_c)],\quad \dot M=q,\quad M(0)=0.
\]

| Arm | Free flow parameters | Fixed quantities | Fits | Initial starts per fit |
|---|---|---|---:|---:|
| A: W3, EXPLORATORY | a, Pstar, n, Pd (4) | P0=0; matching C3c Mc | 5 | 6 |
| B: W3, DIAGNOSTIC ONLY | a, Pstar, n (3) | P0=0; full-cohort onset Pd; matching C3c Mc | 4 | 3 |
| B: W4, EXPLORATORY, DIAGNOSTIC ONLY | a, Pstar, n, P0 (4) | full-cohort onset Pd; matching C3c Mc | 4 | 4 |

Each arm/form has HYD-LOCO-1.0, HYD-LOCO-2.0, HYD-LOCO-1.0-OMIT-3.5 and HYD-LOCO-2.0-OMIT-3.5. Only A also has DESCRIPTIVE_ALL. Total: **13 point fits and 58 prescribed initial starts**. No other held-out folds, A-W4 fit, B full-cohort refit or bootstrap is in scope. Saved C3c DESCRIPTIVE_ALL fits may be reported as existing in-sample references, not new B fits.

Arm A uses no onset-derived fixed Pd and no onset loss. Training-brew onsets enter only through the inherited B0c masks and the saved-Pd start; **no held-out onset time enters arm A**. The training-derived seed is an input to optimization, so its influence must be reported under rule 4. Held-out flow is used for scoring after fitting, not for selecting a start, parameters or settings. A is the clean held-out test of freeing the flow scale within this retrospective, already target-exposed research sequence; it is not independent physical validation.

Arm B fixes Pd to the saved DESCRIPTIVE_ALL onset value: **3.9844972419062152 bar**, the full-precision value denoted 3.98449724 in the task. **TARGET_EXPOSED in the strong sense:** that onset fit used the held-out brews' onset times, although not their flow targets. B is diagnostic only and cannot establish held-out capability. Do not refit onset in either arm or use A's fitted flow Pd to create a new onset prediction.

Keep Mc fixed to the matching saved C3c fold:

| Source fold | Saved onset Pd for A's seed, bar | Fixed Mc, g |
|---|---:|---:|
| DESCRIPTIVE_ALL | 3.9844972419062152 | 28.709461834955388 |
| HYD-LOCO-1.0 | 7.3714863815314375 | 27.768458181900897 |
| HYD-LOCO-2.0 | 4.862853280568316 | 27.13799939129517 |

Each 3.5-omitted twin retains its matching standard fold's Mc and starts. Remove 3.5 bar only from flow training and renormalize the same equal-condition/equal-brew weights over the remaining conditions. Do not recalibrate nuisance quantities. The twins therefore isolate removal of 3.5-bar flow loss, not all historical uses of that condition. The 1-bar-held-out onset seed comes from the saved onset fit with its P0 bound-pinned at -5 bar.

## Objective, bounds and starts

Preserve raw line-pressure forcing, stable-zero hydraulic mass, the B0c observed-x1-onset+2-s mask, clean support and duration normalization. Use the same 0.5-s fitting grid, 0.1-s reporting grid and stored 100-s endpoint observer. Observed mass never drives the modeled hydraulic state; observed onset never resets it. With represented training conditions G and N_g brews per condition:

\[
w_i=\frac{1}{|G|N_g},\qquad
L_i=\frac{\sum_j m_{ij}(q_{ij}-q^{obs}_{ij})^2}{\sum_jm_{ij}},\qquad
J=\sum_iw_iL_i.
\]

There is no onset residual in J. Keep the historical joint scales 0.437 g/s and 4.534 s unchanged, but do not apply them to this unscaled flow-only objective. Report each training condition's objective component and share alongside its matching saved T2-F evaluation. Absolute-flow loss gives low-flow conditions little weight; shares describe loss contributions, not unique identification of Pd or n. No reweighting is authorized.

Before any candidate fit or objective comparison, replay DESCRIPTIVE_ALL T2-F's saved J **0.0719361259858887**, then its saved standard 1- and 2-bar fold objectives, with assert_allclose(rtol=1e-12, atol=0). Failure stops the stage for owner review. On reduced training support, evaluate the matching saved T2-F parameters as a **plug-in**, not a refit. Reuse C3c's committed residuals and parameters as comparators; do not rerun its fits.

Bounds remain a=[0.001,20], Pstar=[0.5,100], n=[1,infinity), and W4 P0=[-5,5]. A adds C1's **Pd=[0.1,100] bar**. Optimize A in (log(a),log(Pstar),n,log(Pd)); B uses C3c's (log(a),log(Pstar),n[,P0]). No finite upper bound on n is added.

The three W3 starts (a,Pstar,n) are **(1,15,1), (1.5,30,2), (2,8,4)**.

- A crosses each of those three starts with Pd at the matching fold's saved onset value and at **4.0 bar**, in that order. Run all six, including the nearly coincident two Pd seeds in DESCRIPTIVE_ALL; do not deduplicate them. Identify the saved-onset-Pd and 4.0-bar groups in every output.
- B-W3 uses exactly the three W3 starts.
- B-W4 uses those three starts with P0=0, plus the matching standard fold's saved C2 T2-F (a,Pstar,n=1,P0) start. Its model Pd is always the full-cohort value above. Do not substitute full-cohort flow parameters into this fourth start.
- Twins reuse the exact standard-fold starts, not a newly fitted optimum. Preserve original and optimizer-clipped coordinates; keep C3c's 1e-10 interior clipping at finite bounds.

Use the C3c/C2 least_squares settings: analytic Jacobian, x_scale="jac", ftol/xtol/gtol=1e-8 and 500 evaluations per prescribed start. Select the lowest converged finite J. If none converges, retain only the inherited 1500-evaluation dogbox fallback from the lowest-cost finite attempt. This is the existing fallback, not permission for additional initial seeds; record it separately if used. An unresolved fit or nonfinite evaluation stops execution for owner review. No bounds, starts, settings, masks or rules may be tuned after results.

## Numerics and interpretation of diagnostics

Reuse C3c's stable power/opening and mass-memory helpers without editing earlier modules. With u=x**n and H=1-exp(-u), the added derivative is

\[
\frac{\partial C}{\partial\log P_d}
=aP_d\exp(-P/P_\star)\,[H-nu\exp(-u)].
\]

Differentiate through the unchanged capacity integral and memory inversion. For the n derivative, x**n*log(x) has limit zero at x=0. Retain stable large-u evaluation and explicit zero limits. Before fitting, test A at n=1 against C1's P0=0 flow and shared-parameter Jacobian columns, and A at fixed Pd against C3c W3; use the existing rtol=1e-12, atol=0 replay tolerance. Check positive/zero pressure and large-power limits using synthetic fixtures. No additional acceptance tolerance may be invented after results.

For every start, retain initial/final parameters, J, convergence, failures, bound distances and zero-capacity training-brew counts by condition. Censoring here means C=0 throughout the masked trace, not failed onset detection. Separate structural zeros from numerical underflow. Keep B-W4's P0=0,n=2 start and check that it avoids structural censoring in positive-pressure histories. Selected zero-capacity training brews warn of flat gradients; convergence alone does not establish an identified fit.

At each selected fit, compare the complete weighted-residual analytic Jacobian with finite differences at h=1e-4*max(1,abs(z)) and h/2. Use central differences where feasible and one-sided differences at bounds. Retain B-W4's initial n=1 checks, masked pressure-range/threshold-bracketing counts and branch-switch counts as in C3c. Smooth synthetic errors should improve on halving until roundoff dominates; investigate contrary behavior. Report analytic-versus-FD and full-versus-half-step relative norms, with absolute errors for zero norms. Separate threshold nonsmoothness from derivative errors; do not assign a new pass band.

Keep C3c's start-objective disagreement rule: spread > 1e-6*max(1,Jbest). Report physical parameter ranges across all starts even when objectives agree. Near a finite bound means C3c's 1e-6 fraction of the transformed-coordinate range; for n, report its lower-bound distance and optimizer active flag. Bound proximity or disagreement limits scale identification; no new numerical meaning of "sharply" is introduced. Show free Pd minus and divided by the matching onset Pd and by 3.9844972419062152, together with its start ranges.

For A, report each seed group's converged objectives and Pd/n ranges, its best objective and which group supplies the selected fit. Use the existing objective-disagreement tolerance when saying that only the saved-onset-Pd group reaches the selected objective; an insignificant cost tie must not be labeled dependence merely because the numerical argmin came from that group. Parameter disagreement at similar J remains visible. Apply the added sentence in rule 4 without hiding failed 4.0-bar attempts.

At frozen fitted parameters, evaluate candidate and matching reference J on both grids. As in C3c, a positive coarse-grid gain is unresolved at the fitting resolution if it changes sign or its between-grid change is at least that gain. Report this warning without refitting. These diagnostics qualify interpretation; they do not authorize new starts or an altered "helps" rule.

## Helps, reports and predeclared interpretation

Let r be the signed condition-mean 100-s endpoint residual, prediction minus observation. For each ordinary held-out condition h=1 or 2 and each arm/form f:

\[
\mathrm{helps}_{f,h}
\iff |r_{f,h}|<|r_{\mathrm{T2F},h}|
\quad\hbox{and}\quad
|r_{f,h}|<|r_{\mathrm{C3c},f,h}|.
\]

A compares with C3c W3; B-W3 compares with C3c W3; B-W4 compares with C3c W4. **"Fixes held-out low-pressure flow" means helps at both 1 and 2 bar for the same arm/form.** Use strict inequalities, without a new margin or tie band. Print the signed residuals and unrounded reductions against both comparators so a negligible arithmetic gain is visible. Keep numerical warnings beside the literal flags.

Report B-W3 and B-W4 separately. Do not combine one form's 1-bar success with the other's 2-bar success. When applying the two-arm reading, identify which B form, if any, fixes both conditions; show the matched W3 comparison first. A result that relies on B-W4 also involves its extra P0 freedom.

Print each 3.5-omitted twin beside its standard fit, with the signed omission change and the matching saved C3c twin residual. T2-F's held-out reference remains its saved standard-fold prediction. The primary helps/fixes flags use the ordinary folds; twins are sensitivity tests, never pooled into those flags or into a fabricated 11-fold aggregate. Report sensitivity directly. Do not turn the weak/near-zero-baseline C3c dependence flag into evidence of insensitivity.

Retain the owner's interpretation rules verbatim:

1. "If arm B fixes held-out 1/2-bar flow and arm A does too, the C3c failure was mainly the Pd transfer. If only B helps, the low-pressure fit needs information from the held-out brews' onsets, which is a weaker result. If neither helps, the flow law is the limit."

2. "Arm B is target-exposed and cannot count as held-out capability."

3. "A free Pd that differs sharply from the onset Pd weakens the shared-scale reading of T2-F; report it, don't hide it."

4. "A free Pd at or near a bound, or disagreeing across starts, is not an identified scale." "If arm A's selected fit comes only from the saved-onset-Pd starts and the 4.0-bar starts disagree, the result depends on onset information through the start and we will say so."

These are conditional screen readings within this family, fixed Mc, objective and start schedule, not proof of a unique physical cause. Partial improvement is a tradeoff, not a two-condition fix. If A fixes both conditions but neither B form does, freeing the flow scale helps whereas the specified fixed full-cohort value does not; that does not establish 3.98 as the correct flow scale. Bound/start/numerical qualifications remain part of every interpretation.

Later reports must include all fitted parameters and starts, per-brew and per-condition held-out residuals, fixed Mc, fitted/fixed Pd provenance, zero held-out endpoints, condition loss shares, and the numerical diagnostics above. DESCRIPTIVE_ALL A is **in-sample**: compare its free Pd with the saved onset value and its residuals with saved C3c, without calling that held-out evidence. Preserve inherited onset predictions as historical references only; no new onset fit or scale-consistency claim is authorized.

If reporting the downstream peak/slope, use each fit's continuous capacity peak and C3c's constant-pressure 100-s grid, labeled by fit. A >=9-bar slope from these fits regresses condition-mean predicted endpoints from measured pressure histories against the actual mean endpoint line pressures of the 9/11/13-bar conditions. It is descriptive/in-sample: C3d has no held-out high-pressure fits and no pooled high-pressure LOCO slope. Any ranges across these selected fits are not confidence intervals.

## Delivery and stop

This delivery changes only this PLAN.md, the active pressure-peak-flow-turnover item's next_gate, and generated STATE_OF_TRUTH.md. Keep state=active and verified_commit=null. Set next_gate to say the C3d plan awaits owner review. Regenerate with python -m puckworks.statusdoc --write; never edit the generated file by hand. Run relevant documentation/status checks, push without force and open a **draft PR**. Stop for owner review: no C3d module, candidate evaluation, result table or summary now.

After separate implementation approval, use a new puckworks/analysis/pressure_peak_stage_c3d.py and focused tests, importing earlier helpers without editing them. Deliver one concise SUMMARY.md and RESULT_TABLE.csv under this stage directory, following the existing table conventions. Retain source hashes and CI-runnable CSV twins of raw-data-dependent checks. Python 3.10/3.12 checks must cover the new Pd derivative, nested identities, training isolation, exact arm/start coverage, group provenance, residual/helps arithmetic, and exposure labels. No new schema or receipts.

Preserve C0's two-hour cumulative execution cap, including retries, interruptions and checks. Default serial execution; any parallel workers each use one BLAS thread before NumPy/SciPy imports. No bootstrap in this screen; a later full stage still requires separate approval and the standing 200 paired whole-brew refits, seed 20261105. Existing grading bands are unchanged and are not applied to this screen. Keep earlier stages, source data and R0's known extraction time-step issue unchanged.

Report main SHA, plan branch, commit SHA, draft PR number, PLAN.md SHA-256 and statusdoc result. If a rule blocks the task, stop and ask Tim. Do not start implementation or a successor.
