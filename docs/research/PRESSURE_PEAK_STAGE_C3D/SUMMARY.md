# PRESSURE-PEAK C3d: Pd transfer

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** Ungraded Python screen.

Only B-W3 fixes both ordinary held-out conditions under the declared rule. A and B-W4 help at 1 bar but worsen 2 bar. This is rule 1's weaker, target-exposed reading: the specified full-cohort onset Pd helps W3, while freeing flow Pd does not fix both. It does not establish the Pd transfer as the main cause. These conclusions are conditional on this family, fixed Mc, objective and starts.

B-W3's 2-bar result leans on the 3.5-bar condition: omitting it changes the residual from -0.081 to -0.325 g/s, with disagreeing starts. Arm B used the held-out brews' onset times through its fixed Pd and cannot count as held-out capability. Arm A used no fixed onset Pd or onset loss; training onsets entered its masks and saved-Pd starts, with no held-out onset time.

## Held-out flow

Residuals are prediction minus observation, g/s. Helps requires smaller absolute error than both references; fixes requires helps at both ordinary conditions.

| Arm | Held bar | T2-F | C3c same form | C3d | Helps |
|---|---:|---:|---:|---:|---|
| A | 1 | -0.092796059 | +0.099424473 | -0.056664676 | True |
| A | 2 | -0.163916163 | +0.184036189 | -0.193412203 | False |
| B-W3 | 1 | -0.092796059 | +0.099424473 | -0.027467440 | True |
| B-W3 | 2 | -0.163916163 | +0.184036189 | -0.081006756 | True |
| B-W4 | 1 | -0.092796059 | -0.092795828 | -0.040794656 | True |
| B-W4 | 2 | -0.163916163 | -0.127480897 | -0.166451023 | False |

**Fixes: A=False; B-W3=True; B-W4=False.**

Unrounded absolute-error reductions (T2-F, C3c):

- A, 1.0 bar: (0.036131383330586825, 0.04275979714943852).
- A, 2.0 bar: (-0.02949603986466165, -0.009376013392905502).
- B-W3, 1.0 bar: (0.06532861915676054, 0.07195703297561223).
- B-W3, 2.0 bar: (0.08290940714883635, 0.1030294336205925).
- B-W4, 1.0 bar: (0.052001403141482765, 0.052001172211729556).
- B-W4, 2.0 bar: (-0.0025348605857449247, -0.03897012622496179).

Twins remain separate sensitivity tests; they are not pooled into helps/fixes.

| Arm | Held bar | Standard | 3.5 omitted | Signed change | C3c omitted |
|---|---:|---:|---:|---:|---:|
| A | 1 | -0.056664676 | -0.040325697 | +0.016338979 | +0.122606256 |
| A | 2 | -0.193412203 | -0.237720223 | -0.044308021 | +0.300310476 |
| B-W3 | 1 | -0.027467440 | -0.014246498 | +0.013220943 | +0.122606256 |
| B-W3 | 2 | -0.081006756 | -0.324686408 | -0.243679653 | +0.300310476 |
| B-W4 | 1 | -0.040794656 | -0.021699920 | +0.019094736 | -0.083984580 |
| B-W4 | 2 | -0.166451023 | -0.171444685 | -0.004993662 | -0.124496102 |

## Arm A's flow Pd

Pd values are bar; seed ranges cover the three converged starts in each group, not confidence intervals. All selected fits came from 4.0-bar starts, but both groups reach the same objective under the declared comparison. **Rule-4 start dependence is false in all five fits.** No A start failed or reached a bound.

| Fit | Selected Pd | n | Saved-onset seed Pd range | 4.0-bar seed Pd range |
|---|---:|---:|---|---|
| DESCRIPTIVE_ALL | 3.563370405 | 2.470936069 | 3.563339 to 3.563371 | 3.563339 to 3.563370 |
| HYD-LOCO-1.0 | 3.566120037 | 2.530105278 | 3.566126 to 3.566128 | 3.566104 to 3.566131 |
| HYD-LOCO-2.0 | 3.590247866 | 2.930937201 | 3.590231 to 3.590268 | 3.590242 to 3.590248 |
| HYD-LOCO-1.0-OMIT-3.5 | 3.456647295 | 2.393238264 | 3.456610 to 3.456632 | 3.456619 to 3.456647 |
| HYD-LOCO-2.0-OMIT-3.5 | 3.637447627 | 3.197452919 | 3.637414 to 3.637445 | 3.637404 to 3.637448 |

The 1-bar and 2-bar flow Pd values are about 48% and 74% of their inherited onset scales, 7.371 and 4.863 bar. That weakens the shared-scale reading in these folds, without rescuing held-out 2-bar flow. DESCRIPTIVE_ALL gives 3.563 bar versus the full-cohort onset value 3.984 bar. Exact differences and ratios to both onset references, each group's objectives, Pd/n ranges and all fitted parameters are in RESULT_TABLE.csv.

## Numerical qualifications

All 58 starts converged; no fallback or nonfinite evaluation occurred. No selected fit is at or near a bound, has a zero-capacity training brew, or has an unresolved coarse-grid gain. The selected Jacobians' relative errors decrease on halving h: full-step errors span about 2.6e-9 to 1.7e-8, and half-step errors about 6.6e-10 to 4.2e-9. All selected and B-W4 initial checks have zero branch switches. Initial n=1 checks improve on halving too.

The CI replay checks the analytic Jacobian norm, branch counts and halving direction exactly; it does not replay finite-difference cancellation remainders, which are roundoff-dominated.

Start disagreement remains in B-W3's 2-bar omitted twin and B-W4's ordinary 2-bar fold and both omitted twins. In the B-W3 twin, n is about 1.87 in two starts and 4.01 in the selected start. B-W4's fourth start retains five censored training brews in the ordinary 2-bar fold; the selected fit has none. Its P0=0,n=2 safeguard starts have no structural censoring. All initial/final counts, structural versus numerical zeros, bound distances, Jacobian norms and threshold counts are retained in the table.

The unchanged absolute-flow objective gives low-flow conditions little weight. For DESCRIPTIVE_ALL A, the 1- and 2-bar shares are 0.68% and 2.00%. Condition contributions and shares are reported beside matching T2-F evaluations. A better trace objective does not guarantee a better low-pressure endpoint.

## In-sample description

These in-sample DESCRIPTIVE_ALL residuals describe the fitted cohort and are not held-out evidence. C3c and T2-F are saved references, with no refit.

| Fit | 1 bar | 2 bar | 3.5 bar |
|---|---:|---:|---:|
| T2-F | -0.098269590 | -0.031508999 | +0.433845535 |
| C3c W3 | -0.023203094 | -0.031650647 | +0.314468783 |
| C3c W4 | -0.035660142 | -0.078961698 | +0.347434411 |
| C3d A | -0.051990923 | -0.096555569 | +0.350089472 |

No new onset prediction, scale-consistency claim or high-pressure held-out result is made.

## Execution and checks

T2-F's saved DESCRIPTIVE_ALL and ordinary 1/2-bar objectives replayed first with assert_allclose(rtol=1e-12, atol=0), including 0.0719361259858887. Reduced-support T2-F evaluations are plug-ins.

13 fits / 58 prescribed starts, serial with one BLAS thread. The fit/report run took 27.570 s. Cumulative execution and checks at final accounting: 4874.469 s of the 7200-s cap. This includes the interrupted 1,353.77-s suite through its 1,355.408-s wrapper, the approved focused/quick/gate rerun wrapper (1,604.136 s), the offline slow wrapper (1848.793 s), and all earlier attempts and final checks. The interrupted run is counted once.

The 29 focused C3d checks passed on Python 3.10 and 3.12, including CSV twins and saved-field FD-ratio arithmetic. Full offline coverage used two disjoint selectors: `not slow and not live and not gpu and not external_data` gave 7,769 passed and 69 skipped; `slow and not live and not gpu and not external_data` gave 68 passed and 7 skipped. Collection-level skips can appear in both runs. Registry gates gave 66 passes and one acknowledged exception; Ruff and statusdoc verification passed.

The first focused run exposed a test's handling of an omitted null CSV cell. The interrupted suite's failure was the summary's missing lowercase `in-sample` wording. Both were corrected without changing fits or parameters; the exposure test stayed unchanged. The full rerun partitions passed. Only execution metadata changed in RESULT_TABLE.csv; every scientific cell matches the frozen pre-rerun snapshot.

PLAN.md, earlier stage modules and source data are unchanged. RESULT_TABLE.csv contains source hashes and replay inputs. The status item stays active with verified_commit=null; the C3d screen awaits owner review.
