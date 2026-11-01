# PRESSURE-PEAK C3c: low-pressure flow screen

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** Ungraded; W4 is exploratory. 56 brews, 11 ordinary LOCO folds, plus two omission fits per form. All 28 point fits and 98 starts ran; no bootstrap or onset refit.

**T2-F objective replay first:** saved 0.0719361259858887; recomputed 0.071936125985888694. All 12 saved standard-fold objectives agree at rtol=1e-12, atol=0. The objectives below are unscaled flow losses; joint scales remain 0.437 g/s and 4.534 s.

| Form | Full-cohort J | Held-out residual: 1 / 2 / 3.5 bar, g/s | Endpoint / trace RMSE, g/s | Continuous peak, bar | >=9-bar slope, g/s/bar |
|---|---:|---|---|---:|---:|
| T2-F | 0.071936126 | -0.0928 / -0.1639 / +0.4979 | 0.1798 / 0.2743 | 6.8913 | -0.11931 |
| W3 | 0.067103959 | +0.0994 / +0.1840 / +0.3550 | 0.1758 / 0.2639 | 6.5801 | -0.11418 |
| W4 | 0.063507768 | -0.0928 / -0.1275 / +0.4078 | 0.1472 / 0.2513 | 5.9215 | -0.07095 |

Continuous peaks are medians of the 11 standard-fold capacity roots; constant-pressure mass memory preserves their locations. The 0.05-bar-grid peak medians [fold ranges], not confidence intervals, are T2-F 6.90 [6.70, 7.00]; W3 6.60 [6.20, 7.25]; W4 5.90 [5.75, 6.95] bar.

The W4 continuous-peak median is **5.9215 [5.7252, 6.9730] bar**, a range across the 11 standard LOCO fits, not uncertainty. The median happens to be the fit holding out 6 bar: n=2.8391, P0=-0.5085 bar. The range endpoints come from holding out 2 bar (n=3.8501, P0=-1.2748) and 1 bar (n=1.0000, P0=1.2147). DESCRIPTIVE_ALL instead has peak 5.9318 bar, n=2.8215 and P0=-0.4405 bar. W3's continuous-peak median and fold range are 6.5801 [6.2038, 7.2344] bar.

The **W4 slope -0.07095 g/s/bar is one regression through the held-out 9/11/13-bar condition means against their actual mean endpoint line pressures**. It is neither a DESCRIPTIVE_ALL slope nor a median of fold slopes, so it has no fold range. Its three contributing fits have (n, P0/bar) of (2.8839, -0.5149), (2.8162, -0.4277) and (2.7066, -0.2853), respectively. W3's -0.11418 and T2-F's -0.11931 use the same pooled LOCO definition.

P0 is below all early 1-bar line pressures (Pe=0.88-1.31 bar) in the W4 median-peak fit, DESCRIPTIVE_ALL and the three slope-contributing fits. It is above four of the five early pressures when 1 bar is held out, including the additional 3.5-bar omission fit; it remains below the highest early pressure, 1.3074 bar. Those two fits give four zero held-out endpoints each. These different fits must not be read as one parameter set achieving both the high-pressure result and adequate held-out 1-bar flow.

W3 does not reduce absolute held-out residuals at both 1 and 2 bar. Its low-pressure signed bias is +0.2128 g/s; mean absolute condition residual is 0.2128 g/s. Rising trends match 4/5 resolved conditions.
W4 reduces the 2-bar absolute residual by 0.0364 g/s. Its strict arithmetic comparison also gives a 1-bar reduction, but only 2.31e-7 g/s: n reaches its lower bound of 1, and four of the five held-out 1-bar endpoints remain zero. The condition mean is 0.0183 versus observed 0.1111 g/s. This does not demonstrate the intended joint low-pressure improvement. Its low-pressure signed bias is +0.0625 g/s; mean absolute condition residual is 0.2094 g/s. Rising trends match 4/5 resolved conditions. The improved peak and slope remain useful point results.

The 3.5-bar condition has only three brews. The additional held-out tests remove it from flow training while retaining the standard fold's onset bank and Mc. Dependence uses each form's own difference from T2-F:

| Form / held-out bar | Standard residual | 3.5 omitted residual | Baseline B | Signed omission change | Dependence flag |
|---|---:|---:|---:|---:|---|
| W3 / 1 | +0.0994 | +0.1226 | 0.192220533 | +0.0231817828 | no |
| W3 / 2 | +0.1840 | +0.3003 | 0.347952352 | +0.116274286 | no |
| W4 / 1 | -0.0928 | -0.0840 | 2.30929753e-07 | +0.00881124839 | yes |
| W4 / 2 | -0.1275 | -0.1245 | 0.0364352656 | +0.00298479559 | no |

All values in that table are g/s. The unchanged rule flags W4's 1-bar result as dependent on 3.5 bar, but this flag is uninformative about useful improvement because B=2.3093e-7 g/s and the improvement it tests is negligible. The mechanical flag remains yes; no threshold or rule changed. Both W4 residuals move toward zero on omission, retaining their arithmetic improvements over T2-F; both W3 residuals move farther above zero, and neither improves on T2-F. The unflagged W3 2-bar result still worsens by 0.1163 g/s. Extra omission predictions are excluded from the ordinary LOCO metrics. The CSV also keeps the separate in-sample 3.5-omitted curves.

| Fold | W3 n | W4 n | W4 P0, bar | W4 continuous peak, bar | W4 zero 1-bar endpoints / 5 (role) |
|---|---:|---:|---:|---:|---|
| DESCRIPTIVE_ALL | 2.1184 | 2.8215 | -0.4405 | 5.9318 | 0/5 (training) |
| HYD-LOCO-1.0 | 1.5373 | 1.0000 | 1.2147 | 6.9730 | 4/5 (held out) |
| HYD-LOCO-2.0 | 1.6121 | 3.8501 | -1.2748 | 5.7252 | 0/5 (training) |
| HYD-LOCO-3.5 | 1.9713 | 2.8240 | -0.5927 | 5.8801 | 0/5 (training) |
| HYD-LOCO-4.0 | 2.1256 | 2.8364 | -0.4538 | 5.9104 | 0/5 (training) |
| HYD-LOCO-5.0 | 2.0151 | 2.7122 | -0.4315 | 6.0270 | 0/5 (training) |
| HYD-LOCO-6.0 | 2.0206 | 2.8391 | -0.5085 | 5.9215 | 0/5 (training) |
| HYD-LOCO-7.0 | 2.1149 | 2.8323 | -0.4881 | 5.9669 | 0/5 (training) |
| HYD-LOCO-8.0 | 2.1198 | 2.6938 | -0.3854 | 6.0552 | 0/5 (training) |
| HYD-LOCO-9.0 | 2.0409 | 2.8839 | -0.5149 | 5.9203 | 0/5 (training) |
| HYD-LOCO-11.0 | 2.1599 | 2.8162 | -0.4277 | 5.9109 | 0/5 (training) |
| HYD-LOCO-13.0 | 2.3156 | 2.7066 | -0.2853 | 5.9400 | 0/5 (training) |
| HYD-LOCO-1.0-OMIT-3.5 | 1.4941 | 1.0000 | 1.1423 | 6.8456 | 4/5 (held out) |
| HYD-LOCO-2.0-OMIT-3.5 | 1.4840 | 3.8517 | -1.2834 | 5.7169 | 0/5 (training) |

Condition objective shares use the unchanged absolute-flow loss. Full-cohort largest contributions are W3: 3.5 bar 14.9%, 8 bar 14.0%; W4: 3.5 bar 16.1%, 9 bar 12.5%. The 1/2-bar shares are only 0.36%/1.09% for W3 and 0.46%/1.63% for W4. These are loss contributions, not unique identification of n. All condition shares and frozen-parameter fine-grid gains are in the CSV.

W3: start-objective disagreement 0/14; bound/proximity flags 0/14; selected zero-capacity training folds 0/14; grid-unresolved improvements 0/14. Selected half-step relative Jacobian changes range 2.26e-09 to 7.05e-09. Bound folds: none. Disagreeing-start folds: none.
W4: start-objective disagreement 4/14; bound/proximity flags 2/14; selected zero-capacity training folds 0/14; grid-unresolved improvements 1/14. Selected half-step relative Jacobian changes range 1.86e-09 to 1.13e-05. Bound folds: HYD-LOCO-1.0, HYD-LOCO-1.0-OMIT-3.5. Disagreeing-start folds: HYD-LOCO-2.0, HYD-LOCO-3.5, HYD-LOCO-6.0, HYD-LOCO-2.0-OMIT-3.5.

The unresolved objective improvement is W4 holding out 1 bar: its coarse-grid gain over T2-F is 2.14e-13, versus 3.55e-11 on the fine grid. The change exceeds the coarse gain. This is the declared resolution warning, not an optimizer failure: all 98 starts converged and no fallback ran. The saved-T2-F start retains 5/4/1 zero-capacity training brews in the 2/3.5/6-bar-held-out fits; the selected alternatives retain none. The fourth start also reaches a worse optimum in the additional 2-bar omission fit, despite ending without censored training brews.

Selected W4 finite-difference branch switches occur in 0/14 fits, and no selected P0 lies inside a training brew's masked pressure range. Initial n=1 checks, threshold brackets, every start's initial/final censor counts and parameter spreads are retained. W4's negative P0 values are offset diagnostics, not physical entry pressures. Its positive P0 values when holding out 1 bar are 1.2147/1.1423 bar, much larger than the machine's 0.28316-bar constant correction. As planned, a positive P0 comparable to that correction would be consistent with a basket-pressure offset, not evidence of a physical entry threshold.

Onset RMSE remains 3.5224 s and its fold-median minimum 4.55 bar, inherited unchanged. Training floors are inactive; the 1-bar-omitted onset threshold remains bound-pinned at -5 bar. Fixed Pd cannot establish scale consistency. Both forms retain the exponential high-pressure decline; the slope tradeoff does not negate a low-pressure capability result.

Saved C2 joint, C1/C0/E1/F1/B1 comparisons are included without refits. In-sample screens can mislead and point LOCO does not replace paired refits. No physical mechanism or independent validation is established.

Local checks: 53 C3c tests passed on each of Python 3.10 and 3.12. The Python 3.12 offline suite finished with 7,740 passed, 69 skipped and 70 deselected; registry gates had 66 passes and one acknowledged exception. Ruff and statusdoc regeneration passed. The 28-fit screen execution took 56.09 s.

Cumulative analysis/check wall time through output: 1651.81 s; serial, one BLAS thread, two-hour cumulative cap. [Full results and CI fixtures](RESULT_TABLE.csv). Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. C3c awaits owner review; no successor is authorized.

## Fixed Pd in the low-pressure folds

The table gives fixed Pd=7.371 bar when holding out 1 bar, including its 3.5-omitted twin; 4.863 bar when holding out 2 bar, including its twin; and 3.81-4.07 bar in all other fits. Both forms use these same saved values.

The 1-bar-held-out Pd comes from the onset fit whose P0 is bound-pinned at -5 bar. The held-out 1- and 2-bar tests therefore test the flow law together with that Pd transfer and cannot separate them. W4's collapse to n=1, flow P0=1.21 bar in the 1-bar-held-out fold (all four starts agree), and W3's lower held-out n values of 1.54 and 1.61, are consistent with that Pd. This screen doesn't show which explains the held-out errors.

These DESCRIPTIVE_ALL signed residuals are **in-sample**, in g/s, calculated from the committed brew residuals:

| Form | 1 bar | 2 bar | 3.5 bar |
|---|---:|---:|---:|
| T2-F | -0.098270 | -0.031509 | +0.433846 |
| W3 | -0.023203 | -0.031651 | +0.314469 |
| W4 | -0.035660 | -0.078962 | +0.347434 |

They show that the shapes can describe 1 bar in-sample, not that they predict it when held out. The dependence rule is uninformative when B is near zero, as for W4/1, and weak when the form is far from T2-F: W3/2 moved +0.116 g/s without being flagged. The rule and its flags are unchanged.
