# Results and interpretation

All results below use the one private prediction cache identified in
RECOMMENDATION.json. No deployment model enters these tables. Lower is better;
values are equal-user means of per-shot RMSE. NRMSE divides by each shot's
calibration-only RMS flow, floored at 0.1 g/s. It is dimensionless, not a percentage.

| Model | Later RMSE, g/s | Later NRMSE | Pressure-varying RMSE, g/s | Pressure-varying NRMSE | Whole-shot reconstruction RMSE, g/s |
|---|---:|---:|---:|---:|---:|
| C0 | 64.630 | 2.004 | 267.158 | 6.391 | 55.341 |
| T0 | **36.168** | 1.920 | **148.011** | 6.319 | 57.626 |
| R0 | 103.995 | 1.934 | 432.581 | 6.330 | 51.660 |
| L0R | 327.138 | **1.830** | 1370.694 | **6.164** | 56.921 |
| M0R | 78.261 | 2.008 | 324.650 | 6.415 | 47.746 |
| AR | 78.057 | 3.722 | 323.833 | 13.696 | **47.728** |
| M0 (no recovery sensitivity) | 99.817 | 2.009 | 415.246 | 6.416 | 56.225 |
| A (no recovery sensitivity) | 100.898 | 3.972 | 420.140 | 15.068 | 56.568 |

Overall: 10,686 shots / 318 users. Pressure-varying: 2,954 / 227, defined only
by a >2-bar range of scored-window mean pressures. The dimensional primary loss
selects T0; selecting by NRMSE would answer a different question. The very large
raw and normalized errors both argue against treating the frozen-amplitude
approximation as uniformly reliable. Reconstruction calibrates amplitude on all
complete windows and scores those same windows, including the guard. Its lower
AR error cannot substitute for the primary early-to-late test.

## Paired contrasts

First minus second, in g/s; brackets are 95% percentile intervals from 1,000
resamples of complete users, seed 20261105, with no refitting. These are continuous
paired comparisons on identical shots, not multiplicity-adjusted hypothesis tests.

| Contrast | Overall difference [interval] | Pressure-varying difference [interval] |
|---|---:|---:|
| AR−M0R | −0.204 [−4.519, 2.464] | −0.817 [−19.833, 12.013] |
| AR−T0 | 41.888 [1.198, 122.913] | 175.823 [3.565, 518.086] |
| AR−R0 | −25.938 [−81.615, 2.369] | −108.748 [−343.513, 11.954] |
| M0R−R0 | −25.734 [−77.114, −0.0013] | −107.931 [−323.713, −0.0019] |
| R0−C0 | 39.365 [−0.039, 118.147] | 165.423 [−0.046, 496.340] |
| T0−C0 | −28.461 [−85.113, −0.122] | −119.147 [−357.132, −0.112] |

AR's small point improvement over M0R is uncertain, while AR is worse than T0.
M0R improves on R0 in the primary mean, with its interval barely below zero;
the wide interval and metric dependence discourage a strong general claim.
AR−M0R NRMSE is **+1.714 [0.984, 2.928]** overall and
**+7.281 [3.535, 12.097]** on the pressure-varying subset. All dimensional and
normalized contrasts are in [CONTRASTS.csv](CONTRASTS.csv).

## Failures and diagnostic groups

The frozen structural admission rules deliberately retain ordinary noisy increments
and flagged signal problems. No outcome-based exclusion, winsorization, additional
fit, lag adjustment or weighting was applied. The diagnostics below reuse the same
held-out predictions; groups can overlap and have different user composition.
They are not separately trained models or evidence that a flag caused the error.

| Diagnostic group | Shots / users | T0 RMSE, g/s | AR RMSE, g/s |
|---|---:|---:|---:|
| No reset-like native drop | 10,231 / 315 | 1.144 | 3.086 |
| Reset-like native drop >5 g | 455 / 106 | 324.787 | 686.780 |
| No negative native increment | 4,073 / 273 | 1.005 | 3.008 |
| Supplied scale-flow agrees | 8,814 / 298 | 1.049 | 2.944 |
| Supplied scale-flow disagrees | 1,797 / 190 | 180.943 | 383.566 |
| Rising pressure windows | 3,575 / 241 | 139.474 | 313.527 |
| Falling pressure windows | 3,959 / 281 | 1.484 | 8.453 |
| Pressure 0–3 bar | 3,022 / 215 | 156.385 | 369.954 |
| Pressure 3–6 bar | 5,720 / 275 | 1.428 | 4.478 |

T0's five held-out fold scores are 1.691, 173.590, 1.482, 1.468 and 1.528 g/s;
AR's are 2.750, 373.072, 6.255, 2.639 and 3.221. Thus the overall dimensional
mean is highly sensitive to retained extreme signals concentrated in one fold.
The reset-like group shows severe error, and unconstrained LS can turn large
negative early increments into negative later predictions. This is a substantive
limitation of the prescribed amplitude approximation on reported signals, not a
reason to alter the frozen benchmark. No individual extreme shot or user is released.

Rising/falling results describe **direction dependence**, with differing support;
they do not prove a time artefact, physical hysteresis or sensor lag. No fitted
alignment was applied. Pressure/flow stability, quantization, clipping-like flags,
all pressure bands and supplied-flow comparisons are in [BREAKDOWNS.csv](BREAKDOWNS.csv).
Agreement with supplied scale-flow is not independent sensor validation.
All retained weight-channel authority is unknown: there is no documented
known-estimated-weight cohort to score separately. Generic supplied flow has
estimated/unknown quantity authority and is never the target. Small-cell or
linkage-unsafe partitions are explicitly suppressed, including their complements.

## Shared shapes and numerical qualification

All 35 selected CV and seven deployment optimizers report success; this does not
prove global optimization. All start diagnostics remain in the model JSON files.
T0's Tc is 0.1 s (the lower bound) in four folds and 0.732 s in fold 1. R0's Mc
is 10,000 g in four folds and 5.221 g in fold 1; AR's Mc is 10,000 g in all folds.
These boundary solutions and fold changes weaken a physical reading of parameters.

| Fold | AR n | AR Pd, bar | AR kappa, /bar | AR capacity maximum, bar | A maximum, bar |
|---|---:|---:|---:|---:|---:|
| 0 | 2.1299 | 0.5434 | 0.85565 | 0.7593 | 0.7269 |
| 1 | 1.0000 | 100.0000 | 0.22645 | 4.3212 | 4.3404 |
| 2 | 2.1659 | 0.5296 | 0.91790 | 0.7318 | 0.7046 |
| 3 | 2.1350 | 0.5433 | 0.85838 | 0.7587 | 0.7262 |
| 4 | 2.1226 | 0.5460 | 0.86639 | 0.7595 | 0.7258 |

For n>=1 and kappa>0 the stationary equation has exactly one positive root;
the derivative term decreases from infinity to zero, and both capacity endpoints
are zero. Each tabulated root is therefore the global maximum, inside that fold's
0–15-bar native training range. M0/M0R have kappa=0 exactly, no finite maximum,
and supremum Pd at infinity. All per-fold parameters, including A kappa and
the monotone models, are in [FITTED_PARAMETERS.csv](FITTED_PARAMETERS.csv).
Being inside the range does not establish dense support near a peak, or a
universal/physical capacity maximum.

Preserved numerical failures led to log-domain evaluation, compensated direct LS,
exact-node ownership checks and pressure-interval refinement **before scoring**.
All 24 pressure artifacts then passed the unchanged 1e-5 independent full-basis
integration gate (maximum error 5.0124e-7); analytical families need no nonlinear
pressure quadrature. All 42 selected training objectives replayed within
2.274e-13 g/s. Execution indexing failures remain of unresolved origin; see
[DEVIATIONS.md](DEVIATIONS.md). No held-out result informed those repairs.

## Artifacts and scope

[PAIRED_DIFFERENCES.svg](PAIRED_DIFFERENCES.svg) shows the six requested contrasts.
[AGGREGATED_EXAMPLE.svg](AGGREGATED_EXAMPLE.svg) shows release-compliant, equal-user
mean trajectories, not an individual shot; changing cohorts and large negative
calibration increments can dominate the display. Suppressed time bins carry no
released estimate. [CAPACITY_CURVES.svg](CAPACITY_CURVES.svg) shows all four shared
pressure families by fold, normalized at 6 bar, with a linear reference.

The recommended reusable artifact is [deployment/T0.json](models/deployment/T0.json).
The recommendation comes solely from the cross-validated primary score, never
from the all-user refits. Model hashes and roles are in [MODEL_INDEX.csv](MODEL_INDEX.csv).
The API returns conditional later-window flow from early observations and query
covariates; pressure families need the recorded later pressure history, and mass
families need observed mass at the start of each query window. This is not an
autonomous prefix-only future-shot forecast.

EWP's prior programme already included early scalar adaptation and competitive
time baselines. This work adds reusable shared nonlinear pressure shapes, their
exact monotone limit and a fixed early-calibration benchmark transferring across
held-out users. It does not revise the private programme, source snapshot,
production defaults or historical physical-qualification results. Unknown machine
and sensor provenance, unresolved lag, post-drip/shutdown, hidden shot state,
unresolved physical reuploads and public-corpus self-selection limit generality.
Neither the best score nor a fitted peak establishes a mechanism, puck pressure,
causal law, universal peak or physical validation.

Data source: Visualizer; thanks to the contributing users who made their shots public.
