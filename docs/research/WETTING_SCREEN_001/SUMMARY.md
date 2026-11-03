# Frozen form A: wetting and observation screen

**Retrospective capability screen; TARGET_EXPOSED; PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

**W2 reduces the held-out onset RMSE bound from 16.29 to 10.16 s; W2T reaches 8.71 s. Neither completes the repair.** Useful endpoint performance remains, with a primary-trace tradeoff.

| Arm | Onset RMSE bound, s | Flow RMSE endpoint/primary/companion, g/s | Paired onset-bound change vs W0 [95%], s |
|---|---:|---|---|
| W0: A1 reference | ≥16.29 | 0.156/0.283/0.326 | — |
| Z: zero-delay diagnostic | ≥17.97 | 0.153/0.268/0.345 | +1.68 [−8.55, +6.86] |
| W1: constant-delay null | ≥9.35 | 0.149/0.308/0.305 | −6.95 [−14.50, −2.61] |
| W2: primary, two parameters | ≥10.16 | 0.153/0.304/0.304 | −6.13 [−12.00, −2.72] |
| W2T: three-parameter observation diagnostic | ≥8.71 | 0.146/0.307/0.301 | −7.58 [−15.23, −3.25] |

All arms retain **56/56 brews, 52 detections**. W0/W1/W2/W2T are **MISSES on onset; NEAR / UNRESOLVED on accuracy vs B1**. Z is ungraded. B1's matched endpoint/primary/companion RMSE is **0.286/0.456/0.621 g/s**. Scored flow is liquid ρQ; observations are scale-derived beverage flow. [Grades and marginal intervals](GRADES.csv).

**Pressure errors:** at 2/3.5/6/13 bar, W0's signed detector-median errors are **+38.54/−1.68/−5.88/−9.27 s**. W2 gives **+12.62/+1.03/−1.49/+7.55**: removing the flow-opening term from wetting repairs much of the early timing but overshoots at 13 bar. W2T gives **+6.45/+2.24/+0.47/+3.21**; its lag improves high-pressure timing while leaving 2 bar late and worsening 3.5-bar absolute error. W1's one-parameter phenomenological null has a lower bound than W2; its delay is not an identified volume. [All eleven conditions and separate front times](ONSET_BY_PRESSURE.csv).

**Zero delay still leaves 1-1, 1-3, 1-4 and 1-5b undetected.** All four 2-bar brews detect, but 2-5 remains **5.33 s late** under Z. These observations expose limitations of frozen flow plus the R0 beverage observer, beyond front timing. The four retained censor contributions alone give **5.88 s**, already above 4.53 s. Bounds use actual confirmable timestamps (97.858–97.946 s), never an exact 100-s substitution. [Z cases](Z_LOW_PRESSURE.csv).

**Paired W2T−W2:** onset-bound difference **−1.45 [−3.26, −0.22] s**; endpoint difference **−0.0072 [−0.0193, +0.0006] g/s**. W2T−W0 primary-trace difference is **+0.0244 [+0.0003, +0.0456] g/s**. All intervals use identical draws and are **conditional on fitted wetting parameters and transferred tuples**. Bound differences are not bounds on unknown true-RMSE differences. [Every paired metric](PAIRED_COMPARISONS.csv).

**Extrema:** fastest held-out nominal detector conditions, W0/Z/W1/W2/W2T: **7/7/11/5/4 bar**, versus observed **3.5 bar**. Descriptive W2/W2T detector minima are **11.0 s at 5 and 5.25 bar / 12.8 s at 4 and 5 bar** (grid ties). Their 100-s flow peaks are **6.006/6.007 bar**, versus W0 **6.009**: numerical three-point interpolation, without a statistical interval. D0's capacity peak **6.00 [5.77, 6.27] bar** instead has a parameter-refit interval. [All extrema, ties and qualifications](EXTREMA.csv).

**Verification/execution:** 102 retained native cases; matching native stepping reproduces beverage traces within **3.8×10⁻⁸ g**. Final W0 detector differences are ≤**0.094 s** on retained support; [one native coverage limitation and three qualification flags](VERIFICATION.csv) remain disclosed. **36 fits, 395 frozen case pairs, 13.22 recorded core-hours; no CFD.** The fixed R0 chemistry retains engineering assumptions. [Methods](METHODS.md) · [fits](FITS.csv) · [manifest](RUN_MANIFEST.json) · [onset figure](ONSET.svg) · [flow figure](FLOW.svg).

**Recommendation:** W2 is a partial, independently motivated wetting change; the smaller W1 null remains competitive, and W2T's fitted observation lag is diagnostic. This screen does not establish a sufficient minimal mechanism. No successor work was started.
