# PRESSURE-PEAK C3b: T3-O screen plan

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** G1 retrospective, ungraded, **EXPLORATORY**. Base: `main@e93f261ed8a858322c98956769e7fb763dd519f5` (PR #402). Branch: `pressure-peak-c3b-plan`. Owner approved implementation and C3b runs with amendment B1, after committing this amended plan. No grades, grading-band changes, EWP or solver work. C3 is not authorized.

**Inputs.** Reuse C2's 56 distinct brews/11 LOCO conditions, `waszkiewicz2025/traces_per_brew`, `equilibrium_windows`, raw `measurements_time_dependent/*.txt` under `/home/tim/wasz-terminal-mass-evidence/upstream`, and saved x1 targets in `/home/tim/pressure-peak-stage-a/.b0-b0c-onsets.csv`. Guide, MANIFEST/register, card, [findings](../PRESSURE_PEAK_FINDINGS.md), [C2](../PRESSURE_PEAK_STAGE_C2/SUMMARY.md)/[C3a](../PRESSURE_PEAK_STAGE_C3A/SUMMARY.md) artifacts and helpers reviewed; external paths available, raw files not reread for planning. Preserve alias exclusion, stable clock, source identities and rights: Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0; no source-code import. Source-internal evidence; mass and derived flow share information, not independent validation.

## Model and fit

Seven fitted parameters `(a, Pstar, P0f, Pd, P0o, b, t0)`: shared Pd, separate flow/onset thresholds. With pressure in bar, time in s, mass in g, flow in g/s:

\[
P=\max(P_{raw},0),\quad
C=aP_d e^{-P/P_\star}\{1-e^{-\max(P-P_{0f},0)/P_d}\},\quad
\dot M=q=C e^{-e^{-M/M_c}},\quad M(0)=0,
\]
\[
P_e=\operatorname{median}P_{raw}(0\!:\!2\,s),\quad
t_w=t_0+\frac{b e^{P_e/P_d}}{\max(P_e-P_{0o},0.01)},\quad
cap=\min(5,\min_{training}P_e-0.01).
\]

Keep C2's hydraulic state initialized at stable zero, without resetting at wetting; the observer's cup mass is separately accumulated as `m_cup(t)=integral(t_w,t) q(s) ds`. Set `t_mass=first t>=t_w with m_cup>=0.5 g`, `t_flow=first t>=t_w with q>0.1 g/s`, and predicted onset `max(t_mass,t_flow)`. Use the model's own q, never observed flow. Report mass/flow/tie as the later crossing; flag q below 0.1 at onset or within the next 2 s, without adding persistence or shifting onset. Mark incomplete 2-s follow-up. Search through each brew's **last raw recorded time**, independently of the cleaned trace end/100-s endpoint. If either crossing is absent before that end, including `t_w>=end`, censor at that end and count it; no other time limit or extrapolation.

Fix Mc to C2's saved value for each fold, including DESCRIPTIVE_ALL. Retain raw line pressure, C2/B0c clean support and observed-x1-onset+2-s loss mask, duration normalization, 0.5-s fit/0.1-s reporting grids and stored 100-s endpoint observer. Equal-condition/equal-brew weights `w_i` and fixed mask `m_ij` give

\[
J=\sum_i w_i\left[\frac{\sum_jm_{ij}(q_{ij}-q^{obs}_{ij})^2}{(0.437)^2\sum_jm_{ij}}
+\frac{(\widehat t_i-t_i^{obs})^2}{(4.534)^2}\right].
\]

Use end-censored predictions in J; also report uncensored-only RMSE and censor counts. Bounds in parameter order: `[0.001,20]`, `[0.5,100]`, `[-5,5]`, `[0.1,100]`, `[-5,cap]`, `[0.0001,10000]`, `[0,120]`; a has units g/s/bar, b s·bar. Log coordinates for a/Pstar/Pd/b. Four starts: `(1,15,1,3,1,15,0)`, `(1.5,30,0.5,2,0.5,3,8)`, `(2,8,1,6,1,1,10)`, and `(1.2,12.2,0.5,4.0,0.54,4.8,9.1)`, clipped inside training bounds as C2. Training floor must remain inactive; record margins, cap binding and held-out floor uses without imposing a held-out cap.

Run **12 point fits, 48 starts**, no bootstrap. Reuse C2 least-squares tolerances `1e-8`, 500 evaluations/start and its 1500-evaluation dogbox fallback; retain every start's parameters/J/convergence and select lowest converged J. No post-holdout retuning. For onset use 0.1-s model q through raw end; interpolate fixed-grid q at wetting/end times and integrate each linear segment exactly for continuous crossing times. Compute centered finite-difference Jacobians in transformed coordinates with `h=1e-4 max(1,abs(z))`, one-sided at bounds; recompute crossings, max and censor branches on every perturbation. Ties use the symmetric difference, without smoothing; record branch switches, plateaued censor derivatives and half-step sensitivity. Keep C2's flow helper unchanged.

**B1:** Censored predictions have zero finite-difference derivatives away from a censor switch; a start censoring 1-bar training brews cannot escape that plateau through their onset gradient. The fourth start supplies a low flow threshold near C2 T2-F DESCRIPTIVE_ALL. For every start report initial and converged-point censored **training** counts by condition (retain final diagnostics on failure too). If any selected fold fit censors training brews, label it **"possible plateau artefact"** in SUMMARY and CSV and still report it; do not retune, drop or restart. Held-out censoring still decides the pre-declared reading.

## Reports and pre-declared reading

Report all parameters, starts, bound hits/proximity, caps/floors; per-condition descriptive and held-out censor/criterion/drop-back counts; every held-out 1-bar onset and record end; J components, onset/trace/endpoint RMSE, all 11 signed endpoint residuals (prediction minus observation), 1/2/3.5-bar mean bias/MAE and >=9-bar slope, using C2 weighting. Compare matched saved **T2-F and T2 joint (capped)** without refits. Replay T2-F's saved flow J `0.0719361259858887` first, plus saved joint J, before comparing objectives; do not compare unscaled flow J directly with joint J.

Report DESCRIPTIVE_ALL and each fold's constant-pressure 100-s flow peak and observer-onset minimum on C2's 1:0.05:13-bar grid; label boundary extrema and never-firing pressures. Constant-pressure onset roots have no arbitrary time cutoff. Also report analytic capacity peak `P0f+Pd*ln(1+Pstar/Pd)` and wetting minimum `P0o+Pd` separately from observer onset. Compare the **LOCO median** continuous flow peak with C2's 6.90 bar, preserving its fold-median convention.

> If no held-out 1-bar onset is censored and the continuous flow peak is below C2 T2-F's 6.90 bar, T3-O goes to a full C3 run with 200 paired refits. If any held-out 1-bar onset is censored, the kink flow law cannot support T3-O and the programme reports that finding instead.

If uncensored but peak >=6.90 bar, the advancement criterion is unmet; return to owner. This reading is a recommendation, not authorization to start C3.

## Delivery, checks and budget

Later files: `puckworks/analysis/pressure_peak_stage_c3b.py` importing earlier helpers unchanged; `tests/test_pressure_peak_stage_c3b.py`; this directory's `RESULT_TABLE.csv` and one concise, plain-prose `SUMMARY.md`. CSV stores fold/brew predictions, raw ends, crossing witnesses, masks/weights, numerical fixtures, all-start diagnostics and source hashes. CI on **Python 3.10/3.12**, without external data: cohort/LOCO isolation; training caps/Mc/floors; mass/flow/tie, strict-flow equality, drop-back and record-end censoring; crossing/Jacobian checks including switches; C2 flow/objective replays (`assert_allclose`, `rtol=1e-12`); residual/RMSE/objective/peak arithmetic; complete starts, labels and reading. Raw-data checks require CSV-based twins, not saved success flags.

Estimated serial wall time: **5–20 minutes**, unmeasured. One BLAS thread per worker; C0's **two-hour cumulative wall cap** includes retries/interruption. Flag failures, bounds within `1e-6` of coordinate range, and start J spread `>1e-6 max(1,Jbest)`; report parameter spreads even at equal J. Preserve earlier stages/source data. SUMMARY states that in-sample fits can mislead and point LOCO does not replace paired refits. Keep status active with verified_commit=null; set next_gate to "C3b screen ready for owner review; C3 not authorized" and regenerate STATE_OF_TRUTH.md only via `python -m puckworks.statusdoc --write`. Push, wait for Python 3.10/3.12 CI, mark ready if green, then stop for owner review.
