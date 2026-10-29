**No mechanism passes the primary rules for entry to solver B1.**

The shared endpoint shape error is an overestimated low-pressure rise at 1–3.5 bar and an underestimated peak at 4–6 bar, with B1 also falling too far at 13 bar. The saved B0 raw-pressure D2/D3 fits have positive high-pressure slopes and peaks at 13/11 bar. The observed peak is 6 [5, 6] bar; its high-pressure slope is −0.066 [−0.087, −0.040] g/s/bar.

Observed late flow rises at **2, 3.5, 4, 5 and 6 bar**; at **1, 7, 8, 9, 11 and 13 bar**, its interval includes zero. No condition has a resolved late decline. Trends become less positive with pressure: correlation −0.345 [−0.467, −0.175], consistent with an eventual plateau.

Primary results use raw pressure: RMSE in g/s, slope in g/s/bar, nominal peak in bar. Brackets are 95% refit intervals; comparisons use trace-refitted B1. Trend agreement counts mean-slope signs; LATE_TRENDS.csv separately reports interval categories. PASS requires TIE/BETTER, the slope interval within −0.176 to −0.020, a peak interval overlapping 5–7 bar, and at least 8/11 matching trend signs.

| Model | Trace / endpoint RMSE | COMPARISON | Slope [interval] | Peak [interval] | Trend agreement | PASS |
|---|---:|---|---|---|---:|:---:|
| B1 | 0.579 / 0.349 | TIE | −0.338 [−0.371, −0.306] | 8 [8, 8] | 7/11 | N |
| C4 | 0.395 / 0.242 | UNRESOLVED | −0.057 [−0.070, −0.042] | 8 [8, 8] | 8/11 | N |
| D1 | 0.384 / 0.232 | UNRESOLVED | −0.132 [−0.150, −0.113] | 8 [7, 8] | 7/11 | N |
| D2 | 0.561 / 0.312 | UNRESOLVED | +0.012 [+0.008, +0.018] | 13 [13, 13] | 8/11 | N |
| D3, exploratory | 0.382 / 0.220 | UNRESOLVED | −0.116 [−0.139, −0.096] | 8 [8, 9] | 8/11 | N |

The time course favours increasing conductance (C4/D1) over pure jamming. Five-parameter D3 adds little improvement and is ineligible. C4/D1/D2/D3's paired endpoint intervals cross zero and extend outside the TIE band. All five are NOT CAPABLE on full-trace RMSE; endpoint capability is UNRESOLVED except D2 (NOT CAPABLE). The empirical per-pressure smooth curve achieves 0.105 trace / 0.083 endpoint RMSE using evaluated brews: an optimistic, ineligible ceiling.

Basket pressure is SENSITIVITY because it uses observed flow. Excluding ≤3 bar makes C4/D1/D3 BETTER at endpoints. Raw-pressure C4 keeps its peak at 8 [7, 8], with slope −0.091 [−0.106, −0.077]; D1 moves to 7 [7, 8], with slope −0.165 [−0.184, −0.143]. RESULT_TABLE.csv contains all four pressure/cohort scenarios; sensitivities cannot replace the primary result.

The 56 brews retain SCI-MD-010 folds and the 100-second endpoint observer. Trace scoring starts at stable pressure +5 s, with B0 terminal exclusions before smoothing. T1/T3 reuse stored fits; T4/T5 have 200 refits per row. Loss intervals use 1,000 paired resamples, seed 20261030; tolerance is 0.25 g/s. Fitting used 27.2 minutes, including the discarded attempt; final grid differences are ≤0.0135 g/s. Original measurements and Puckworks/EWP tables were inspected. Committed aggregates credit Waszkiewicz et al.'s [CC-BY-4.0 Zenodo data](https://zenodo.org/records/18046315).

**Recommendation: one further analysis of measured outflow onset before solver work.** Mean flow during stable pressure +5–10 s is only 0.022 g/s. Identify first sustained cup outflow in the existing traces and test whether separating wetting/transport delay from saturated flow resolves the mismatch. No successor analysis has been started.
