# PRESSURE-PEAK C3e: free-Pd base and low-pressure forms

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** Ungraded Python screen.

M1 and M2 improve absolute held-out condition-mean errors at both 1 and 2 bar under the literal screen rule. M1's 1-bar gain is only **1.336272278525813e-05 g/s**, negligible in size; its 2-bar gain is 0.016571160731226914 g/s, while its within-2-bar ratio worsens.

M2's gains are 0.004274402851917172 g/s at 1 bar and 0.003664732096147344 g/s at 2 bar. **Both M2 omission twins put v at its lower bound, v=0** (stored optimizer estimates 3.6868397178689595e-14 and 2.303154116308822e-33 g/s), so M2's low-pressure gain depends on the 3.5-bar condition. Under rule 4, a stable v=0 supports the nested base A; it does not by itself show non-identifiability. This omission reading is conditional on the inherited Mc, which retains 3.5-bar information.

LC gives the largest overall endpoint/trace error reductions and the largest ratio improvement, but trades away held-out 1-bar accuracy. Its absolute 1-bar error worsens by **0.008946955239267099 g/s**, and brew 1-2 worsens by **0.1391777843850074 g/s**, beside gains of 0.107754921622197 g/s at 2 bar, 0.18852816381021706 g/s at 3.5 bar, and 0.7373028460799447 in ratio absolute error. This is rule 2's tradeoff, not a fixed low-pressure law or an automatic veto.

A and M1 have four free parameters; M2 and LC have five and are exploratory. Passing the low-pressure comparison does not establish overall preference. Peak, slope, other conditions and trace behavior still matter, and the existing full-stage rules remain unchanged. DESCRIPTIVE_ALL is in-sample only.

## Ordinary held-out predictions

Residuals are prediction minus observation, g/s. T2-F is the accepted historical reference, with matched observers and no refit.

| Form | 1 bar | 2 bar | bias12 | mae12 | Within-2-bar ratio | Brew 1-2 residual | 3.5-bar residual |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | -0.056665 | -0.193412 | -0.125038 | 0.125038 | 2.424662 | +0.001946 | +0.428495 |
| M1 | -0.056651 | -0.176841 | -0.116746 | 0.116746 | 2.470136 | +0.006648 | +0.373702 |
| M2 | -0.052390 | -0.189747 | -0.121069 | 0.121069 | 2.405426 | +0.010706 | +0.409006 |
| LC | +0.065612 | -0.085657 | -0.010023 | 0.075634 | 1.687359 | +0.141123 | +0.239967 |
| T2-F | -0.092796 | -0.163916 | -0.128356 | 0.128356 | 7.462966 | -0.025820 | +0.497898 |

Recomputed observed within-2-bar ratio: **1.249606122**, a ratio of pair means from authenticated 100-s endpoint observations.

| Form | Ratio absolute-error reduction vs A | Brew 1-2 absolute-error reduction | 3.5-bar absolute-error reduction |
|---|---:|---:|---:|
| M1 | -0.045474 | -0.004702 | +0.054794 |
| M2 | +0.019236 | -0.008760 | +0.019490 |
| LC | +0.737303 | -0.139178 | +0.188528 |

Positive reductions improve the named metric; negative reductions are tradeoffs. A ratio gain alone does not fix the law, and a small worsening or brew 1-2 alone is not an automatic veto.

## All conditions and downstream behavior

| Form | 1 | 2 | 3.5 | 4 | 5 | 6 | 7 | 8 | 9 | 11 | 13 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | -0.0567 | -0.1934 | +0.4285 | +0.0820 | -0.0516 | +0.0281 | +0.1273 | +0.2065 | +0.0483 | -0.0361 | +0.0061 |
| M1 | -0.0567 | -0.1768 | +0.3737 | +0.0212 | -0.1169 | -0.0455 | +0.0510 | +0.1290 | -0.0282 | -0.1106 | -0.0661 |
| M2 | -0.0524 | -0.1897 | +0.4090 | +0.0633 | -0.0656 | +0.0090 | +0.0985 | +0.1741 | +0.0157 | -0.0680 | -0.0200 |
| LC | +0.0656 | -0.0857 | +0.2400 | +0.0879 | +0.0192 | +0.0166 | +0.1110 | +0.1920 | +0.0531 | -0.0305 | -0.0072 |
| T2-F | -0.0928 | -0.1639 | +0.4979 | +0.0450 | -0.1575 | -0.0398 | +0.1293 | +0.2409 | +0.1176 | -0.0003 | -0.0799 |

| Form | Endpoint / trace RMSE, g/s | 1-3.5 bias / MAE, g/s | Rising resolved trends | Capacity peak median [range], bar | >=9 slope: in-sample / out-of-fold, g/s/bar |
|---|---|---|---:|---|---|
| A | 0.15300 / 0.25418 | +0.05947 / 0.22619 | 3/5 | 5.99513 [5.74217, 6.14063] | -0.075343 / -0.076273 |
| M1 | 0.14703 / 0.26354 | +0.04674 / 0.20240 | 3/5 | 5.96360 [5.73542, 6.10917] | -0.074399 / -0.075063 |
| M2 | 0.14750 / 0.25405 | +0.05562 / 0.21705 | 3/5 | 5.95025 [5.74194, 6.08721] | -0.074944 / -0.074425 |
| LC | 0.12465 / 0.24141 | +0.07331 / 0.13041 | 4/5 | 5.65009 [5.51846, 5.74382] | -0.078023 / -0.081324 |
| T2-F | 0.17980 / 0.27429 | +0.08040 / 0.25154 | 3/5 | historical C2 | -0.104174 / -0.119312 |

Peaks are global capacity maxima; ordinary-fold ranges are not confidence intervals. The out-of-fold slope combines the 9/11/13-bar held-out predictions from three models and is not a curve derivative. Both slopes use actual mean endpoint pressures.

## Reading against T2-F and the targets

A's ordinary-fold peak median of 5.995 bar is inside 5-7 bar. Its out-of-fold >=9-bar slope of -0.0763 g/s/bar lies inside the observed interval [-0.0880, -0.0403]; T2-F's -0.1193 lies outside it. The unweighted RMS of the 11 held-out condition-mean residuals is 0.164 (A), 0.144 (M1), 0.154 (M2), 0.109 (LC) and 0.192 (T2-F) g/s. This RMS is a descriptive summary, not a graded metric. The screen remains ungraded; these comparisons are not grades.

LC's f is 0.30-0.47 in every ordinary fold and both omission twins. Unlike M2's v, its gain does not vanish when 3.5 bar is removed from flow training, conditional on inherited Mc, which retains 3.5-bar information.

LC's held-out brew 1-2 prediction is 0.258 g/s versus the observed 0.117 g/s. Brew 1-2's observed q/P is among the lowest at 1 bar. This is context only: rule 2's tradeoff reading still applies, and rule 3's batch-effect caveat stands.

## Fixed-bank omission tests and fitted additions

Twins omit 3.5 bar from flow fitting only. **3.5-bar information remains in Mc**; its effect has not been measured. These are conditional sensitivity tests, not robustness to removing 3.5 bar from the whole calibration pipeline.

| Form | Held bar | Ordinary residual | Omission-twin residual | Signed change |
|---|---:|---:|---:|---:|
| A | 1.0 | -0.056665 | -0.040326 | +0.016339 |
| A | 2.0 | -0.193412 | -0.237720 | -0.044308 |
| M1 | 1.0 | -0.056651 | -0.043038 | +0.013613 |
| M1 | 2.0 | -0.176841 | -0.219164 | -0.042323 |
| M2 | 1.0 | -0.052390 | -0.040327 | +0.012063 |
| M2 | 2.0 | -0.189747 | -0.237720 | -0.047973 |
| LC | 1.0 | +0.065612 | +0.076092 | +0.010480 |
| LC | 2.0 | -0.085657 | -0.134594 | -0.048937 |

| Fit | M2 v, g/s | Mc/v, s | LC f |
|---|---:|---:|---:|
| DESCRIPTIVE_ALL | 0.0892347868 | 321.729483 | 0.399303454 |
| HYD-LOCO-1.0 | 0.0548850367 | 505.938592 | 0.438997632 |
| HYD-LOCO-2.0 | 0.0107767534 | 2518.19806 | 0.301668523 |
| HYD-LOCO-3.5 | 0.0589992141 | 514.630357 | 0.422391828 |
| HYD-LOCO-4.0 | 0.0823993443 | 358.512507 | 0.397522353 |
| HYD-LOCO-5.0 | 0.091713949 | 315.087373 | 0.397875955 |
| HYD-LOCO-6.0 | 0.0911953704 | 319.566403 | 0.435168154 |
| HYD-LOCO-7.0 | 0.111561459 | 258.125188 | 0.395022673 |
| HYD-LOCO-8.0 | 0.114535076 | 253.94006 | 0.396772198 |
| HYD-LOCO-9.0 | 0.117132522 | 243.562388 | 0.399184199 |
| HYD-LOCO-11.0 | 0.115144866 | 243.762349 | 0.391171345 |
| HYD-LOCO-13.0 | 0.106211773 | 264.45933 | 0.39668333 |
| HYD-LOCO-1.0-OMIT-3.5 | 3.68683972e-14 | 7.53177797e+14 | 0.469851312 |
| HYD-LOCO-2.0-OMIT-3.5 | 2.30315412e-33 | 1.17829715e+34 | 0.306178686 |

All fitted parameters, nine individual low-pressure predictions, condition objective shares, descriptive and twin peaks, and all start diagnostics are in RESULT_TABLE.csv.

## Numerical and interpretive limits

All 504 starts converged. There were no start-objective disagreements, saved-onset-Pd seed dependence, selected zero-capacity training brews or Jacobian branch switches. All selected and recorded initial Jacobian checks improved on halving the step.

The only selected bound flags are v=0 in the two M2 omission twins. The 1-bar twin's coarse-grid gain over A is 6.95596358291084e-13 and reverses to -1.2373035929158505e-10 on the fine grid, so that tiny gain is unresolved at the fitting resolution. No other grid-gain warning occurred. The stored parameters and objectives are unchanged.

Materially different parameters at near-equivalent objectives would indicate weak practical identification; materially different objectives would indicate optimization instability. LC loses n at f=1 and f at n=1. No fit reaches the upper v bound. A five-parameter form must earn its extra parameter through held-out improvement, not its in-sample objective alone. No form is physically validated here.

M1 changes recovery speed as well as shape. M2 uses symmetric clock/exposure integration on the inherited grid, with the exact v=0 identity preserved. Masks never pause or reset its state. The B0c objective scores observed onset + 2 s through clean support; the pre-onset stretch is unscored. Large v values can be indistinguishable at the endpoint; diagnostic agreement alone cannot identify v. No restart claim is made.

The Jacobian checks retain halving direction and branch counts. CI replays analytic norms and saved error-ratio arithmetic, not roundoff-dominated finite-difference cancellation remainders. A synthetic extreme-pressure LC check reaches an unused overflow branch in the unchanged parent n=1 Taylor expression; returned capacity and derivatives are finite.

Run order and dates are unavailable. Per-condition batch effects can also produce conductance steps with near-proportional within-condition flow; this screen cannot exclude them. No bootstrap, profiling, onset refit or grading was performed.

## Execution

Source authentication, T2-F objective replays (including 0.0719361259858887), all five C3d A prediction/objective replays, and exact v=0 / f=0 identities completed before fitting with rtol=1e-12, atol=0.

56 fit problems / 504 scheduled starts; 0 inherited fallbacks. The fit/report run took 952.046 s. Cumulative execution and checks at final accounting: 2106.158 s of 7200 s. 83 focused tests passed on each of Python 3.10 and 3.12: 69 quick plus all 14 slow M2 trajectory replays. 16 status tests, Ruff and statusdoc verification passed. All interruptions and reruns are counted.

The full M2 trajectory replays carry `pytest.mark.slow`. They remain selected by `pytest -m slow` in the hosted `slow-science` workflow's `slow` job on Python 3.12, run weekly or by manual dispatch. Ordinary PR CI runs the quick committed-field twin. Its numerical comparisons use `assert_allclose(rtol=1e-12, atol=0)`; the full local focused runs include every slow replay as well.

The serial test run was deliberately interrupted after 42 passes to partition the same checks; its 354.79-s pytest run is counted through the 355.120-s wrapper. The first partitioned attempt then found a QA metadata mismatch: the CSV writer adds `claim`, while `readings()` returns calculated fields without that wrapper field. The test now checks `claim` explicitly before comparing the calculated fields. No numerical assertion, tolerance, fit or scientific result changed. All interrupted and repeated checks count toward cumulative wall time.

The status item remains active with verified_commit=null. The C3e screen awaits owner review; no successor is authorized.
