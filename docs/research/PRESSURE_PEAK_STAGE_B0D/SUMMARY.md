**FAIL: timing and flow do not support a common compaction/air mechanism.**

Timing alone locates a minimum near the observed flow-peak region, but its
parameters do not predict the flow endpoints adequately. The table separates
the compaction parameter from the actual timing minimum, which includes air
when present. Pressures are in bar; brackets are 95% whole-brew refit intervals.
Delay RMSE uses held-out pressures. W0 is the empirical quadratic reference.

| Timing law | Delay RMSE, s | Compaction P* [interval] | Minimum-delay pressure [interval] |
|---|---:|---|---|
| W0, quadratic | 4.534 | — | 6.70 [6.24, 7.04] |
| W1, exponential | 3.512 | 5.07 [4.81, 5.29] | 5.07 [4.81, 5.29] |
| W2, exponential + air | 3.457 | 3.07 [2.83, 4.14] | 4.61 [4.40, 5.04] |
| WD1, D1 form | 3.877 | 5.72 [5.48, 5.93] | 5.72 [5.48, 5.93] |
| WD2, D1 form + air | 4.519 | 4.29 [4.11, 5.15] | 5.60 [5.45, 5.82] |

W2 and WD2 are **exploratory four-parameter fits**. The minimum-delay region
cannot separately determine the transport offset t0, so it remains fitted.
D1's compaction parameter expresses its modulus as the air-free conductance
peak; its original permeability law is retained.

With timing parameters fixed inside each training fold, W1 gives a full-model
flow peak of 4 [3.5, 5] bar and endpoint RMSE 0.526 g/s; W2 gives 4 [4, 5] bar
and 0.638 g/s. Both are WORSE than endpoint-refitted B1 (0.294 g/s). Their peak
intervals only touch the 5–7-bar band at 5 bar. D1-form transfers give
7 [6, 7] bar / 0.423 g/s without air and 6 [5, 7] bar / 0.470 g/s with air;
their comparisons are UNRESOLVED and their high-pressure slopes fail.
Thus a peak in the desired band alone does not establish successful prediction.

Flow-fitted air reduces, but does not remove, low-pressure overprediction:
C4's +0.315 becomes F1's +0.149 g/s; D1's +0.266 becomes F2's +0.185 g/s.
At 4–6 bar, F1/F2 still underpredict by 0.214/0.272 g/s. Primary raw-pressure
results follow; residuals are predicted minus observed. Full-model peak
intervals use the original nominal-pressure statistic; slopes use g/s/bar.

| Model | Endpoint RMSE, g/s | Comparison | Residual 1–3.5 bar, g/s | Full-model peak interval, bar | Slope interval | Trend signs | P* overlap | PASS |
|---|---:|---|---:|---|---|---:|:---:|:---:|
| F1, C4 + air | 0.211 | BETTER | +0.149 | [7, 8] | [−0.230, −0.188] | 8/11 | N | N |
| F2, D1 + air | 0.251 | BETTER | +0.185 | [7, 8] | [−0.288, −0.236] | 8/11 | N | N |

F1/F2 compaction scales are 5.99 [5.72, 6.20] and 7.03 [6.91, 7.14] bar.
For the required like-with-like check, their **air-inclusive conductance peak**
intervals are [7.23, 7.51] and [7.45, 7.69] bar. Neither overlaps its matching
timing interval: W2 [4.40, 5.04] or WD2 [5.45, 5.82]. F2 also disagrees with
the exponential W2 timing fit. These comparisons exclude delivered mass;
the full-model flow peaks are reported separately above. Both candidates also
fail the required slope interval. m=2/4 and basket sensitivities supply no PASS.

No coffee trapped-air bound was found in the checked sources.
[Yasuda et al.'s glass-bead analogy](https://arxiv.org/html/2501.13361v1#S10)
supports m=3 qualitatively; its residual saturation is liquid water, not air.
Foster's headspace gas does not bound gas trapped inside the bed. The additional
prior-constrained rows therefore repeat m=3 exactly, without inventing an s0
constraint. Provenance and limits are in [AIR_PRIOR.md](AIR_PRIOR.md).

The same 56 brews, folds, observer and 0.25 g/s tolerance are retained.
Each pressure view has 200 whole-brew refits, seed 20261101. Mc is estimated
inside each training fold before being fixed for F1/F2. Measured wetting delay
is a timing target, never a hydraulic input. Endpoint grid differences are
below 0.00014 g/s; all trend refits use 0.1-s sampling. Fitting used 1.7 minutes,
including the refinement. Committed data are attributed
[CC-BY-4.0 Waszkiewicz aggregates](https://zenodo.org/records/18046315);
prior summaries reproduce no restricted source data.

**Recommendation: stop.** Trapped air partly corrects the low-pressure error,
but timing and flow require incompatible conductance peaks and the fitted
high-pressure decline is too steep. No mechanism earns entry to solver B1;
no successor task is started.
