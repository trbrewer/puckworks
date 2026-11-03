# Frozen form A: wetting and observation screen

**Retrospective capability screen; TARGET_EXPOSED; PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

**W2 reduces the held-out onset RMSE bound from 16.29 to 10.16 s; W2T reaches 8.71 s. Neither completes the repair.**

| Arm | Onset RMSE bound, s | Flow RMSE endpoint/primary/companion, g/s | Paired onset-bound change vs W0 [95%], s |
|---|---:|---|---|
| W0: A1 reference | ≥16.29 | 0.156/0.283/0.326 | — |
| Z: zero-delay diagnostic | ≥17.97 | 0.153/0.268/0.345 | +1.68 [−8.55, +6.86] |
| W1: constant-delay null | ≥9.35 | 0.149/0.308/0.305 | −6.95 [−14.50, −2.61] |
| W2: primary, two parameters | ≥10.16 | 0.153/0.304/0.304 | −6.13 [−12.00, −2.72] |
| W2T: three-parameter observation diagnostic | ≥8.71 | 0.146/0.307/0.301 | −7.58 [−15.23, −3.25] |

All arms retain **56/56 brews, 52 detections**. W0/W1/W2/W2T are **MISSES on onset; NEAR / UNRESOLVED on accuracy vs B1**. Z is ungraded. B1's matched endpoint/primary/companion RMSE is **0.286/0.456/0.621 g/s**. Scored flow is liquid ρQ; observations are scale-derived beverage flow. [Grades and marginal intervals](GRADES.csv).

**Pressure errors** at 2/3.5/6/13 bar: W0 **+38.54/−1.68/−5.88/−9.27 s**; W2 **+12.62/+1.03/−1.49/+7.55**; W2T **+6.45/+2.24/+0.47/+3.21**. W2 overshoots at 13 bar; W2T improves high-pressure timing, leaves 2 bar late and worsens 3.5-bar absolute error. W1's delay is not an identified volume. [Eleven conditions/fronts](ONSET_BY_PRESSURE.csv).

| Supplementary descriptive view (ungraded) | W0 | Z | W1 | W2 | W2T |
|---|---:|---:|---:|---:|---:|
| RMS of condition-median signed errors, 3.5–13 bar (s) | 6.873 | 13.503 | 2.232 | 3.044 | 1.449 |

This equally weighted nine-condition median view suppresses within-condition variation; read it beside the full 56-brew score above and [per-brew results](ONSET_BY_BREW.csv), not as their replacement.

**Fold ranges (11 ordinary folds):** W1 τ0 **13.06–13.95 s**; W2 Pw **4.39–5.48 bar**; W2T Pw **3.13–3.84 bar**, t_s **9.20–10.83 s**. Heavily overlapping training sets do not identify a mechanism. W2's agreement with B0d's **5.07 bar** is consistency between related fits on the same cohort, not an independent repeat. [Fits](FITS.csv).

**Zero delay still leaves 1-1, 1-3, 1-4 and 1-5b undetected.** All four 2-bar brews detect, but 2-5 remains **5.33 s late** under Z. The four censor contributions alone give **5.88 s**, above 4.53 s. Bounds use actual confirmable timestamps (97.858–97.946 s). [Z cases](Z_LOW_PRESSURE.csv).

**W2T primary-trace decomposition:** **0.2662 g/s** unshifted bed, **0.3072** shifted scale, versus W0 **0.2827**. t_s is a **fitted scale lag; physical mechanism unidentified**. It may compensate for recovery, observer, initial-state or clock assumptions. [Bed/scale diagnostics](W2T_BED_DIAGNOSTIC.csv).

Form A was calibrated with its state accumulating from stable-pressure zero. Introducing bed breakthrough and an observation lag changes the calibrated trajectories. Joint fitting will test whether the coupled model can improve detector onset while retaining useful flow accuracy.

**Paired W2T−W2:** onset-bound difference **−1.45 [−3.26, −0.22] s**; endpoint difference **−0.0072 [−0.0193, +0.0006] g/s**. W2T−W0 primary-trace difference is **+0.0244 [+0.0003, +0.0456] g/s**. All intervals use identical draws and are **conditional on fitted wetting parameters and transferred tuples**. Bound differences are not bounds on unknown true-RMSE differences. [Every paired metric](PAIRED_COMPARISONS.csv).

**Extrema:** W2T's fastest held-out detector condition is **4 bar**; its descriptive minimum ties at **4 and 5 bar** (12.8 s). Pw locates the fitted wetting law's constant-pressure front minimum, distinct from the observed **3.5-bar detector minimum**. W2/W2T 100-s flow peaks: **6.006/6.007 bar**, W0 **6.009** (three-point interpolation; no statistical interval). D0's capacity peak **6.00 [5.77, 6.27] bar** has a parameter-refit interval. [All extrema/ties](EXTREMA.csv).

**Verification/execution:** 102 native cases; matching native stepping reproduces beverage traces within **3.8×10⁻⁸ g**. Final W0 detector differences ≤**0.094 s** on retained support; [one native coverage limitation and three qualification flags](VERIFICATION.csv). **36 fits, 395 frozen case pairs, 13.22 core-hours; no CFD.** R0 chemistry retains engineering assumptions. [Methods](METHODS.md) · [manifest](RUN_MANIFEST.json) · [onset figure](ONSET.svg) · [flow figure](FLOW.svg).

**Recommendation:** W2 offers a partial wetting repair; W1 remains competitive and W2T diagnostic. No sufficient minimal mechanism is established. Joint-clock planning is separate; no new fits here.
