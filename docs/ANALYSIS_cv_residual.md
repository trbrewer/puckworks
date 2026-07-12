# Cross-validation + residual-autocorrelation diagnostics

*DIAGNOSTIC strength — NOT gates, NOT in `run_all_gates()`. Small-n
cross-validation and residual analysis that QUANTIFY known model weaknesses
honestly; they do not discover new defects nor claim power-backed validation.
Reproduce: `python -m puckworks.analysis.lopo_cv` and
`python -m puckworks.analysis.residual_autocorr` (or the `summary()` /
`lopo_*` callables). Addresses the PAPER_B review's "leave-one-out validation" and
"residual autocorrelation" asks.*

**A crossing the review conflated, kept separate here.** The RSM is schmieder's
cup-mass response surface (factors flow/grind/temp — **pressure is NOT a factor**),
so leave-one-PRESSURE-out is inapplicable to it; its held-out unit is a distinct
(F,G,T) design point. Leave-one-PRESSURE-out applies to the **waszkiewicz**
cross-pressure flow calibration (a different dataset), and residual
autocorrelation is only meaningful on the waszkiewicz time series (the RSM
residuals are independent design points, no time axis).

## 1. RSM leave-one-design-point-out (schmieder cup mass, TDS 1/2)
`lopo_cv.lopo_rsm_design_point('tds','1/2')`. Refits the retained-term model
`[1, F, G, T, G², T², F·G]` (identical to `harness.schmieder_rsm_refit`) leaving
out all replicates of one (F,G,T) condition, predicts the held-out condition mean.

- **Q² (predictive R²) = 0.48** over **15 held-out design points**; RMSE_cv 0.13 g,
  worst held-out residual −0.22 g.
- **Reading:** weak but **consistent with schmieder's own adjusted R² 0.41–0.75**.
  The RSM is *honestly weak* (use for SHAPE, not absolute level) — this CV
  quantifies that known weakness, it does not reveal a new problem. It also
  independently corroborates that the RSM absolute level is usable-with-caution
  (the earlier "overpredicts 1.7×" was a printed-coefficient rounding artifact; a
  refit reproduces the data — see ANALYSIS_P2 §2.3).

## 2. Waszkiewicz leave-one-pressure-out (Eq. 16 static (P_c,Q_c) calibration)
`lopo_cv.lopo_waszkiewicz_pressure()`. Drops each of the 11 equilibrium pressures,
refits (P_c,Q_c) via `poroelastic.fit_static` on the other 10, predicts the
held-out pressure.

- **Q² = 0.81** over **11 pressures**; RMSE_cv 0.28 g/s; worst held-out fold at
  **4.5 bar** (an *interior* basket pressure, not an edge extrapolation).
- **Reading:** the Eq. 16 static characteristic **generalizes across the pressure
  axis** — it does not merely interpolate its own fit points. A genuinely good
  result. (This is the within-rig cross-pressure claim, now with a leave-one-out
  score rather than a single home-pressure fit.)

## 3. RC-3a dynamic residual autocorrelation (waszkiewicz flow traces)
`residual_autocorr.summary()`. Residual = measured flow − RC-3a model Q(t) (zero
free parameters: published (P_c,Q_c) + solids sigmoid, as
`gate_waszkiewicz_dynamic_9bar`), over t ≥ 15 s (skip infiltration).

**Sampling caveat (load-bearing).** The raw trace is ~10 Hz, where the *measured
signal itself* has lag-1 autocorrelation ~1.0, so raw Durbin-Watson ≈ 0 for **any**
model — a sampling artifact (reported as `durbin_watson_raw`). The analysis
therefore **decimates to 1 s** before DW/ACF, so the statistic tests model
structure, not sample spacing. **Do not remove the decimation.**

| P [bar] | DW (1 s) | DW raw | ACF lag-1 | resid std | signal std | resid/signal |
|---:|---:|---:|---:|---:|---:|---:|
| 1.0 | 0.001 | 0.000 | 0.956 | 0.140 | 0.023 | **6.1** |
| 2.0 | 0.002 | 0.000 | 0.956 | 0.281 | 0.028 | **10.2** |
| 3.5 | 0.006 | 0.000 | 0.981 | 0.413 | 0.175 | 2.4 |
| 4.0 | 0.006 | 0.000 | 0.991 | 0.289 | 0.242 | 1.2 |
| 5.0 | 0.004 | 0.000 | 0.989 | 0.182 | 0.370 | 0.49 |
| 6.0 | 0.003 | 0.000 | 0.981 | 0.182 | 0.408 | 0.45 |
| 7.0 | 0.008 | 0.000 | 0.961 | 0.076 | 0.528 | **0.14** |
| 8.0 | 0.034 | 0.001 | 0.962 | 0.107 | 0.494 | 0.22 |
| 9.0 | 0.047 | 0.002 | 0.967 | 0.111 | 0.559 | 0.20 |
| 11.0 | 0.027 | 0.001 | 0.972 | 0.148 | 0.547 | 0.27 |
| 13.0 | 0.010 | 0.000 | 0.968 | 0.209 | 0.517 | 0.40 |

- Mean DW (decimated) **0.013**; lag-1 ACF **0.96–0.99** at every pressure →
  **genuine slow lack-of-fit** persists at 1 s spacing (the residual has real
  temporal structure the model misses), *not* the raw-10 Hz sampling artifact.
- **Where the model is weak:** worst at **1–2 bar** (residual std *exceeds* signal
  std — the model is poor in that low-pressure regime); **best at the
  espresso-relevant 7–9 bar** (residual std 0.08–0.11 vs signal 0.53–0.56).
- **Reading:** expected for a **zero-free-parameter** model; reported as an honest
  lack-of-fit that *localizes* where the RC-3a reconstruction is weak — NOT a
  defect to eliminate. The pooled DW ≪ 1.6 correctly reads "systematic positive
  autocorrelation remains".

## Still owed (unchanged; not fabricated)
- Full-precision RSM coefficients (author request; the refit is the interim).
- A *physical* lateral operator + its Jacobian for a real stability analysis
  (card-blocked, rule 1; the current lateral term stays a labelled proxy).
- A second-rig FLOW transfer set (angeloni is second-rig *chemistry*, a different
  observable; no second-rig flow/pressure series on file).
- Conventional Methods + related-work + LaTeX (needs journal/voice direction).
