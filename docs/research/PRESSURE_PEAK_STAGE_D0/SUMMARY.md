# PRESSURE-PEAK D0: A and exploratory LC

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.**

A is primary (four parameters); LC is EXPLORATORY (five). Grades use ordinary held-out predictions on this retrospective cohort. No overall PASS. DESCRIPTIVE_ALL parameter intervals are in-sample.

| Form | Accuracy | Peak | Slope | Trends | Onset | Low bias | Scale |
|---|---|---|---|---|---|---|---|
| A | NEAR | MEETS | MEETS | NEAR | NOT_SCORED | MEETS | MEETS |
| LC (EXPLORATORY) | MEETS | MEETS | MEETS | MEETS | NOT_SCORED | MEETS | EXPLORATORY, NOT_GRADED |

| Separate onset law | Held-out onset RMSE [95%], s | Grade |
|---|---|---|
| INHERITED: C2 capped onset-only law (onset RMSE 3.522 s, NEAR, fixed by C2) | 3.52242665 [2.81089, 4.13837] | NEAR, fixed by C2 |

This onset grade belongs only to the inherited law.

| Form | Endpoint RMSE [95%], g/s | Trace RMSE [95%], g/s | Slope >=9 bar [95%], g/s/bar | Nominal peak [95%], bar |
|---|---|---|---|---|
| A | 0.153001 [0.124412, 0.176737] | 0.254185 [0.23639, 0.268321] | -0.0762726 [-0.096948, -0.0564472] | 6 [6, 7] |
| LC | 0.124648 [0.100755, 0.155715] | 0.241407 [0.228327, 0.277713] | -0.0813241 [-0.104813, -0.0613562] | 6 [5, 7] |

B1 endpoint/trace RMSE: 0.286452649/0.436697665 g/s. RMSE is mean condition RMSE. Accuracy uses the separate B0c 1,000 paired condition-then-brew resamples, +/-0.25 g/s.

| Form | Accuracy delta [95%], g/s | Continuous global capacity peak [95%], bar | Capacity at peak [95%], g/s | Ordinary-fold peak median [95%], bar |
|---|---|---|---|---|
| A | UNRESOLVED [-0.32335, 0.0188018] | 5.99856 [5.76991, 6.27247] | 2.1039 [2.04876, 2.15085] | 5.99513 [5.75488, 6.25872] |
| LC | BETTER [-0.342431, -0.0270325] | 5.65049 [5.25622, 5.9378] | 2.11448 [2.0572, 2.16127] | 5.65009 [5.26025, 5.92829] |

A ordinary point-fold continuous peak range: [5.74217, 6.14063] bar (range, not a confidence interval).

LC ordinary point-fold continuous peak range: [5.51846, 5.74382] bar (range, not a confidence interval).

Continuous peaks are DESCRIPTIVE_ALL parameter-derived global maxima, checking all stationary candidates and endpoint limits, including competing LC maxima. The nominal peak grade is lenient; fold ranges are not confidence intervals.

| Form | Flow Pd [95%]; width, bar | Onset Pd [95%]; width, bar | Paired flow-minus-onset Pd median [95%], bar | Grade |
|---|---|---|---|---|
| A | [3.36766, 3.70875]; 0.341086 | [3.23283, 4.75571]; 1.52287 | -0.363373 [-1.33581, 0.335285] | MEETS |
| LC | [3.62958, 3.98257]; 0.35299 | [3.23283, 4.75571]; 1.52287 | -0.101756 [-1.11169, 0.605269] | EXPLORATORY, NOT_GRADED |

A scale interval gap 0 bar; flow/onset descriptive percentiles (2.5/25/50/75/97.5): 3.40898/3.51558/3.56387/3.61544/3.70884 / 3.24184/3.64737/3.91866/4.21845/4.75753 bar. P0 consistency NOT_APPLICABLE. Pstar 24.3967 [21.2201, 28.0651] bar, NOT_GRADED.

LC scale interval gap 0 bar; flow/onset descriptive percentiles (2.5/25/50/75/97.5): 3.63134/3.77071/3.81819/3.87327/3.98264 / 3.24184/3.64737/3.91866/4.21845/4.75753 bar. P0 consistency NOT_APPLICABLE. Pstar 20.5028 [18.1478, 23.4288] bar, NOT_GRADED.

| Form | 1 / 2 / 3.5-bar signed residuals, g/s | Signed low bias [95%], g/s | Low-condition MAE [95%], g/s | bias12 / mae12, g/s |
|---|---|---|---|---|
| A | -0.0566647 / -0.193412 / +0.428495 | 0.0594728 [0.0314547, 0.0852473] | 0.226191 [0.135241, 0.30279] | -0.125038 / 0.125038 |
| LC | +0.0656116 / -0.0856573 / +0.239967 | 0.0733072 [-0.162926, 0.13379] | 0.130412 [0.0361177, 0.22151] | -0.0100228 / 0.0756345 |

| Form / nominal bar | Held-out residual [95%], g/s | Late trend [95%], g/s/s (resolved conditions only) |
|---|---|---|
| A / 1 | -0.0566647 [-0.0898451, -0.0125029] | not scored |
| A / 2 | -0.193412 [-0.270045, -0.0906939] | -7.71864e-05 [-0.00100113, 0.000776714] |
| A / 3.5 | +0.428495 [0.264579, 0.57009] | -0.000751925 [-0.00306875, 0.000717177] |
| A / 4 | +0.0820394 [-0.0543908, 0.205] | 0.00077269 [0.000592305, 0.00103086] |
| A / 5 | -0.0515828 [-0.169482, 0.0451161] | 0.000535908 [0.000267857, 0.000780101] |
| A / 6 | +0.0281413 [-0.0863668, 0.132922] | 0.000348842 [0.00026202, 0.000458698] |
| A / 7 | +0.127344 [0.0353023, 0.211408] | not scored |
| A / 8 | +0.206479 [0.114768, 0.276263] | not scored |
| A / 9 | +0.0483259 [-0.0455747, 0.13568] | not scored |
| A / 11 | -0.0361109 [-0.0852309, 0.0105522] | not scored |
| A / 13 | +0.00605022 [-0.0734285, 0.0724877] | not scored |
| LC / 1 | +0.0656116 [0.0123546, 0.127432] | not scored |
| LC / 2 | -0.0856573 [-0.153157, -0.00933146] | 0.000585499 [-0.000190618, 0.00129248] |
| LC / 3.5 | +0.239967 [-0.470871, 0.425314] | -0.0005488 [-0.00292543, 0.00267682] |
| LC / 4 | +0.0879452 [-0.07303, 0.230279] | 0.000770816 [0.000558927, 0.00104736] |
| LC / 5 | +0.0192257 [-0.0973215, 0.135168] | 0.000465074 [0.000197502, 0.000681242] |
| LC / 6 | +0.0166394 [-0.0975186, 0.13249] | 0.000353356 [0.000252961, 0.000468001] |
| LC / 7 | +0.11097 [0.0214619, 0.203368] | not scored |
| LC / 8 | +0.191967 [0.0998989, 0.261828] | not scored |
| LC / 9 | +0.0530551 [-0.0406161, 0.140379] | not scored |
| LC / 11 | -0.0305273 [-0.0795054, 0.0168289] | not scored |
| LC / 13 | -0.00722391 [-0.0961704, 0.0628211] | not scored |

A resolved rising-trend matches: 3/5, refit count interval [3, 5].


LC resolved rising-trend matches: 4/5, refit count interval [3, 5].


A - T2-F paired differences; identical whole-brew draws. T2-F is a replay of saved C2 refits.

| Metric | Median difference | 95% interval |
|---|---:|---|
| endpoint_rmse_g_s | -0.0250841 | [-0.0403907, -0.00596572] |
| trace_rmse_g_s | -0.0192977 | [-0.0283708, -0.00896177] |
| low_pressure_bias_g_s | -0.0221306 | [-0.109105, 0.0142089] |
| residual_1_g_s | 0.035783 | [0.00271074, 0.0636459] |
| residual_2_g_s | -0.0395513 | [-0.30947, 0.099577] |
| residual_3_5_g_s | -0.069941 | [-0.111631, -0.0172359] |
| brew_1_2_residual_g_s | 0.0279776 | [-0.0486333, 0.0912455] |
| within_2bar_ratio | undefined | unavailable |
| slope_g_s_bar | 0.0423769 | [0.0151202, 0.06808] |

LC - A paired differences; identical whole-brew draws. T2-F is a replay of saved C2 refits.

| Metric | Median difference | 95% interval |
|---|---:|---|
| endpoint_rmse_g_s | -0.0263347 | [-0.0523512, -0.0019501] |
| trace_rmse_g_s | -0.0098649 | [-0.0216129, 0.0205183] |
| low_pressure_bias_g_s | 0.00979893 | [-0.223068, 0.0532286] |
| residual_1_g_s | 0.123157 | [0.0773492, 0.163714] |
| residual_2_g_s | 0.106068 | [0.0577795, 0.1659] |
| residual_3_5_g_s | -0.194636 | [-0.894972, -0.0799547] |
| brew_1_2_residual_g_s | 0.139987 | [0.0831297, 0.196096] |
| within_2bar_ratio | -0.744359 | [-1.1792, -0.404922] |
| slope_g_s_bar | -0.00511257 | [-0.010218, 0.00254483] |

| Form | Brew 1-2 residual median [95%], g/s | 3.5-bar residual median [95%], g/s | Within-2-bar ratio median [95%] |
|---|---|---|---|
| A | 0.000438797 [-0.0356847, 0.0667409] | 0.437614 [0.264579, 0.57009] | 2.44793 [2.14462, 2.69274] |
| LC | 0.145924 [0.0910455, 0.187706] | 0.22379 [-0.470871, 0.425314] | 1.67869 [1.49439, 1.83826] |
| T2-F | -0.0252786 [-0.107591, 0.0819293] | 0.504213 [0.335468, 0.628119] | unavailable (46 undefined) |

Observed within-2-bar ratio, recomputed from authenticated endpoints: 1.24960612199. Zero denominators are undefined, never floored. The 3.5-bar condition has three brews and only 10 distinct within-condition resampling multisets, so its interval is coarse.

| Form | Start disagreement draws / fits | Bound draws / fits | Fallback draws / fits | Censored selected-training draws / fits |
|---|---|---|---|---|
| A | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| LC | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

LC minus A point changes in absolute error: within-2-bar ratio -0.737302846; brew 1-2 +0.139177784 g/s; 3.5-bar condition -0.188528164 g/s. Negative reduces absolute error. Read these magnitudes as a tradeoff, not a veto.

A start totals: {"scheduled": 14400, "unsuccessful": 0, "initial_structural": 0, "initial_numerical": 0, "final_structural": 0, "final_numerical": 0}. Onset-seed dependence: 0 draws. Bound fields: {"log_a": 0, "log_Pstar": 0, "log_Pd": 0, "n": 0, "f": 0}. Flagged interval endpoint contributors: {}.

A seed-group start totals: {"saved_onset_Pd": {"starts": 7200, "initial_structural": 0, "initial_numerical": 0, "final_structural": 0, "final_numerical": 0}, "4.0_bar": {"starts": 7200, "initial_structural": 0, "initial_numerical": 0, "final_structural": 0, "final_numerical": 0}}. Largest within-fit parameter spans across starts: {"a_g_s_bar": 3.815147203245495e-05, "Pstar_bar": 0.009063604239130996, "n": 0.0005669920101842862, "Pd_bar": 0.00019859525685239632}. Selected boundary draw counts: {"n=1": 0}.


LC start totals: {"scheduled": 28800, "unsuccessful": 0, "initial_structural": 0, "initial_numerical": 0, "final_structural": 0, "final_numerical": 0}. Onset-seed dependence: 0 draws. Bound fields: {"log_a": 0, "log_Pstar": 0, "log_Pd": 0, "n": 0, "f": 0}. Flagged interval endpoint contributors: {}.

LC seed-group start totals: {"saved_onset_Pd": {"starts": 14400, "initial_structural": 0, "initial_numerical": 0, "final_structural": 0, "final_numerical": 0}, "4.0_bar": {"starts": 14400, "initial_structural": 0, "initial_numerical": 0, "final_structural": 0, "final_numerical": 0}}. Largest within-fit parameter spans across starts: {"a_g_s_bar": 4.8247133182299784e-05, "Pstar_bar": 0.0037273549269052353, "n": 0.009818648389145146, "Pd_bar": 0.0004848068482163903, "f": 0.0003469845797786919}. Selected boundary draw counts: {"f=0": 0, "f=1": 0, "n=1": 0}.

All starts, failures and boundary/censoring qualifications are retained. No Jacobian checks ran in refits. Point checks replayed C3e. Omission twins are replayed context only; 3.5-bar information remains in Mc.

Runtime and source details

Pilot draws 0 and 1: 56.814 s wall, 98.655 s worker CPU. Projection: 308.297 s at 32 workers, 9865.502 s worker CPU. Two draw workers in pilot; projection assumes 32 occupied workers and similar draw costs. Startup, checks, comparator replays and reporting are additional. Informational only; no time cap. Pilot draws are included in the 200.

Pilot per-start wall seconds (count/min/median/max/sum): {"A": {"count": 144, "minimum": 0.12906851898878813, "median": 0.1708588949404657, "maximum": 0.33916832227259874, "sum": 24.71322383917868}, "LC": {"count": 288, "minimum": 0.13910131994634867, "median": 0.22732681408524513, "maximum": 0.42919364711269736, "sum": 67.00528296036646}}.

Cumulative measured wall 892.858 s; worker/check CPU 11240.362 s; driver CPU 139.685 s. Resumed draws: none. Union of measured driver/check wall intervals; nested worker events counted once. Every completed/failed/interrupted logged attempt retained. Per-attempt records are retained in RESULT_TABLE.csv and the work-directory runtime log.

Call-path inspection: C0.Deadline.check contains a monotonic >= end TimeoutError; end=math.inf disables it. B.fit_course and C2.fit_t2 only call their supplied budget; no independent wall-time stop. C3a.Budget/timed_attempt and earlier CLI mains hardcode 7200; none is called by D0. A.FitBudget has a default 7200-second limit; D0 never constructs it. Scorecard time_limit/evaluate_rows use SIGALRM and deadline comparisons; D0 calls neither. C3e.fit_fold and training_evaluator are not used for refits. D0 time.monotonic calls measure durations only. No subprocess/future timeout is set.

Source hashes, selected fits, compact per-start records, assertion twins and paired draw values are in RESULT_TABLE.csv. Full start records remain outside Git at the recorded paths and SHA-256 values. Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. Earlier stages and source data are unchanged.

Interpretation rules, verbatim

R1. "Grades measure capability on this retrospective cohort under the stated bands, not validation. A is primary; LC has five parameters and is EXPLORATORY. There is no overall PASS. Each MEETS, NEAR or MISSES is read with its continuous value and interval."

R2. "A and LC contain no onset law, so their onset grade is NOT_SCORED. The separate INHERITED row reports C2's capped onset-only law re-run on the same draws; its grade was fixed by C2 and is not evidence about either flow law. (In C2, T2-F took its Pd from that onset fit, so onset was part of T2-F; A and LC have no such link.)"

R3. "Scale consistency compares A's flow-fitted Pd with C2's capped onset-only Pd from independent fits on the same draws. Interval overlap gives the grade under the existing band. If the grade is MEETS while the paired per-draw difference interval excludes zero, the consistency is weak and comes from interval width; it is reported that way, not as a shared scale. A paired interval that contains zero means the two fits are compatible on these data; it does not show they measure the same physical quantity. With n near 2.5, A's Pd scales a convex opening, which is not the same functional scale as the onset law's Pd. Overlap shows the two fitted numbers are compatible on these data, not that they measure one physical scale. LC's comparison is reported, not graded: its Pd sits inside a mixture opening and is a different quantity again."

R4. "Paired differences use identical whole-brew draws. An interval that excludes zero is a paired difference on this cohort; one that includes zero is unresolved. T2-F per-draw values are replays of saved C2 refits, not new refits."

R5. "The within-2-bar ratio tests the held-out response shape. Report its improvement or deterioration alongside changes in the held-out residual of brew 1-2 and the held-out 3.5-bar residual. An improved ratio accompanied by deterioration elsewhere is a tradeoff, not evidence by itself that the low-pressure law has been fixed. Report the magnitudes; do not make an arbitrarily small worsening or the single 1.42-bar brew an automatic scientific veto. The 3.5-bar condition has three brews, so its interval is coarse. Neither brew 1-2 nor 3.5 bar is a veto for any form. Introduce no new post-result threshold."

R6. "Start disagreement uses the inherited spread > 1e-6*max(1,Jbest). Draws with start disagreement, bound-located parameters, fallbacks or censored training brews are kept and counted, never dropped. If such draws set an interval endpoint, say so. In a draw, f=0 supports A for that draw; at f=1, n drops out; at n=1, f drops out. Materially different parameters at near-equivalent objectives indicate weak practical identification; materially different objectives indicate optimization instability."

R7. "The graded peak uses the C1/C2 nominal-condition definition, which is lenient. The continuous global capacity maximum and its interval are the better guide to location; a nominal-band MEETS is not a precise peak claim."

R8. "Run order and dates are unavailable. Steps in conductance between conditions with near-proportional flow within a condition are also what a per-condition batch effect would produce. No result here can exclude that."

R9. "A five-parameter form must improve held-out predictions, not merely the in-sample objective, to earn its extra parameter. LC's results do not change A's grades."


D0 results await owner review. No merge or successor is authorized.
