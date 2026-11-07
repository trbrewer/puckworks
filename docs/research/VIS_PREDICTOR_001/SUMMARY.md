# PW-VIS-PREDICTOR-001

**36.17 g/s: T0 (time-only) has the lowest primary held-out RMSE**, versus C0
64.63, AR 78.06, M0R 78.26, R0 104.00 and L0R 327.14. The frozen funnel is
**23,169 canonical → 14,471 pressure/weight → 10,686 usable shots / 318 users**
(177,394 windows). Five user-isolated folds use equal-user means of per-shot
RMSE. Amplitude uses the first six seconds after reported delivery onset; a
two-second guard precedes disjoint later scoring. The target is **reported
weight-derived flow**.

On the pressure-varying subset (2,954 shots / 227 users), T0 also wins:
148.01 g/s versus AR 323.83 and M0R 324.65. Overall paired differences, with
95% complete-user bootstrap intervals, are AR−M0R **−0.204 [−4.519, 2.464]**,
AR−T0 **+41.888 [1.198, 122.913]**, and T0−C0 **−28.461 [−85.113, −0.122]**
g/s. AR's small point improvement over its monotone limit is uncertain; the extra
shape is not the most useful information. M0R−R0 is −25.734 [−77.114, −0.0013],
but pressure models do not beat T0 on the primary metric. Normalization changes
the ranking: L0R has the lowest NRMSE (1.830), versus T0 1.920 and AR 3.722.

**Absolute performance is poor and heterogeneous.** T0's no-reset-flag group
scores 1.144 g/s; its reset-like group scores 324.787. Large retained negative
increments can produce negative fitted amplitudes. No observations were trimmed
after scoring. Direction dependence and pressure-band failures are reported,
without identifying lag or a time artefact. Whole-shot amplitude-adjusted
reconstruction favors AR (47.73 g/s); this uses later targets and is secondary.

The reusable extractor, fitter and saved-model predictor deliver the best
reference **T0**, recommended from cross-validation. Seven all-user refits plus
analytical C0 are deployment artifacts, excluded from scores and contrasts.
New relative to EWP's private programme (12,093 same-shot fits; 6,655 out-of-fold
evaluations / 213 cohorts) is this shared pressure-shape benchmark with held-out
user transfer and fixed early-shot calibration; that programme already explored
early scalar adaptation and competitive time baselines.

Unknown machine/sensor authority is retained, including unresolved estimated-weight
status. Results concern a self-selected public corpus and conditional predictions
using recorded pressure/current mass. The amplitude approximation fails materially;
these results establish no mechanism, puck pressure, causal law, universal peak or
physical validation. See [results](RESULTS.md), [reproduction](REPRODUCE.md) and
[preserved numerical failures](DEVIATIONS.md). Visualizer and its contributing users
are the data source.
