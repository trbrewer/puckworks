**FAIL: no candidate meets all four requirements for entry to solver B1.**

Wetting delay falls to a minimum near 3.5 bar, then rises again.
Mean delay (95% brew-bootstrap interval) is 25.5 [24.3, 27.1] s at 1 bar,
13.6 [11.8, 15.0] s at 2 bar,
11.0 [9.8, 12.0] s at 3.5 bar, 12.4–12.9 s across 4–6 bar, and
18.0 [16.6, 19.6] s at 13 bar. The fitted law is
`t_on = 15.97 × (P/bar)^−0.0469 s`, with n = 0.047 [0.004, 0.086].
This does not support 1/P scaling. Onset is detected in all 56 brews:
baseline-relative cup mass >0.5 g and smoothed flow >0.1 g/s for two seconds.
Delay runs from B0b's stable-pressure clock to the start of this interval;
it includes transport and detection lag. Halving both
thresholds gives n = 0.027 [−0.032, 0.077]; raising both by 50% leaves all
five 1-bar brews undetected, preventing a full-cohort exponent.
[ONSET.csv](ONSET.csv) contains every condition and interval.

Starting trace scoring at measured onset +2 s reduces errors but does not
remove the low-pressure mismatch. With existing B0b fits, B1/C4/D1 still
overpredict flow at 1–3.5 bar and underpredict it at 4–6 bar. After refitting,
their mean trace residuals in those two bands are respectively
+0.132/−0.272, +0.309/−0.255 and +0.247/−0.247 g/s.

Hargarten's swelling anchors imply descriptive exponential times of
17–34 s, with practical completion by 240 s. They supply the weak 10–240 s
bound on τ, not a measured pore-closure rate. Mo calibrates to Hargarten;
Foster supplies infiltration timing, not an independent grain-swelling rate.
Provenance and retained CC BY-NC attribution are in
[SWELLING_PRIOR.md](SWELLING_PRIOR.md).

Raw-pressure results follow. RMSE and endpoint residuals are in g/s; positive
means overprediction. Peaks use nominal bar; slopes use g/s/bar at ≥9 bar.
Brackets are 95% refit intervals; comparisons use refitted B1.
PASS requires TIE/BETTER, a slope interval within [−0.176, −0.020], a peak
interval overlapping 5–7 bar, and ≥8/11 matching trend signs.

| Model | Endpoint / trace RMSE | Comparison | Residual 1–3.5 / 4–6 bar | Peak [interval] | Slope interval | Trend signs | PASS |
|---|---:|---|---:|---|---|---:|:---:|
| B1 | 0.286 / 0.437 | TIE | +0.150 / −0.407 | 8 [8, 8] | [−0.370, −0.316] | 7/11 | N |
| C4 | 0.257 / 0.340 | TIE | +0.470 / −0.178 | 8 [8, 8] | [−0.070, −0.041] | 8/11 | N |
| D1 | 0.238 / 0.325 | TIE | +0.405 / −0.178 | 8 [7, 8] | [−0.151, −0.110] | 7/11 | N |
| E1, predictive | 0.242 / 0.329 | TIE | +0.446 / −0.168 | 8 [8, 8] | [−0.104, −0.067] | 8/11 | N |
| E2, conditional | 0.242 / 0.324 | TIE | +0.429 / −0.141 | 8 [6, 11] | [−0.085, −0.007] | 7/11 | N |
| E3, predictive | 0.249 / 0.329 | TIE | +0.375 / −0.175 | 8 [7, 8] | [−0.209, −0.149] | 7/11 | N |

Swell-before-percolate leaves every point peak at 8 bar. E1 passes comparison,
slope and trend requirements but fails the peak requirement. E3's peak interval
overlaps 7 bar, but slope and trend agreement fail. E2 uses observed onset and
is ineligible; slope and trend also fail. Predictive τ estimates commonly hit
their bounds and do not identify a material swelling rate.

The same folds, observer, terminal exclusions, 100-s endpoint and 0.25 g/s
tolerance are retained. Each pressure view has 200 whole-brew refits; loss/onset
intervals use 1,000 bootstraps, seed 20261031. E1–E3 fit three hydraulic
parameters; Mc and predictive onset coefficients are fixed training-fold inputs.
Basket sensitivity supplies no PASS. Fitting took 10.3 minutes; grid differences
are below 0.001 g/s. Only attributed
[CC-BY-4.0 Waszkiewicz aggregates](https://zenodo.org/records/18046315) and
licence-cleared prior summaries are committed; originals were inspected.

**Recommendation: stop.** This measured-delay swelling mechanism leaves the
low-pressure shape error and earns no entry to solver B1. This result does not
exclude other swelling mechanisms; no successor task is started.
