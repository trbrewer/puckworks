# PRESSURE-PEAK C3a: owner-approved diagnostic plan

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** G1 retrospective diagnostics, ungraded; owner approved with amendments A1–A4. Base: `main@6e25f0a71b70deda5e3ec1398d0b71ae5f326051`. Python implementation and C3a runs are authorized after this amended plan is committed. No grading-band changes or EWP/solver work; C3 is not authorized.

**Inputs and reuse.** Read [findings](../PRESSURE_PEAK_FINDINGS.md), C0/C1/C2 summaries, C2 `RESULT_TABLE.csv`, their Python modules, and B0 `sustained_onset()`/`measure_onsets()`. Use Waszkiewicz `traces_per_brew` and `equilibrium_windows`: 56 distinct brews, 11 conditions, existing alias exclusion and 100-s endpoint. Guide, MANIFEST, register and card inspected; original restart/one brew record sampled, existing onset-cache rows inspected; no new measurements computed. Single-rig source-internal evidence, derived flow shares mass information; CC-BY-4.0, Zenodo 18046315; source programs not imported. New `puckworks/analysis/pressure_peak_stage_c3a.py` imports A/B0/C0/C1/C2 helpers unchanged. Join packaged data using C2's saved brew IDs/folds; avoid EWP-dependent `load_brews()` and cache-writing `context()`/`measure_onsets()`.

## 1. Detector audit and onset point fits

Reuse `/home/tim/pressure-peak-stage-a/.b0-b0c-onsets.csv` read-only, keyed by brew (hash and check cohort/clock). Its x0.5/x1/x1.5 detections already use strict mass/flow thresholds `(0.5k g, 0.1k g/s)` sustained for 2 s, reporting interval start, with threshold scale `k`. Do not redefine or regenerate these detections. B0 raw alignment, clean support, pre-stable mass baseline and 31-point/order-1 flow smoothing stay fixed.

For every brew report smoothed flow at x1 onset, saved 100-s endpoint flow, their ratio (onset/endpoint), first native-sample strict crossings of flow 0.05/0.10/0.15 g/s and mass 0.25/0.5/0.75 g on stable time, all three cached onsets and paired shifts. Crossings have no persistence requirement. Preserve missing values/reasons; count undetected values per field. Report condition means, medians, ranges and counts; compare condition mean paired x1-minus-x0.5 shifts. For each brew identify which strict criterion became true last at the start of the x1 qualifying interval: flow >0.1 g/s or baseline-relative mass >0.5 g. Trace each criterion back to the start of its uninterrupted true run containing that onset, and report both crossing times and their gap; flag simultaneous crossings explicitly. Report last-criterion counts by condition. Ties still do not satisfy “larger.”

> If the flow criterion is the last to become true for a majority of the 1-bar brews, and the 1-bar mean paired x1-minus-x0.5 onset shift is larger than at every other condition, the 1-bar onset is treated as detector-limited and T3-O is carried into C3; otherwise T3-O is dropped. The x1.5 non-detection of all five 1-bar brews is reported alongside.

Fit x0.5 and x1.5 separately: `DESCRIPTIVE_ALL` + 11 LOCO folds, **24 point fits**, no bootstrap. Reuse C2 `fit_t2(kind="onset")`:

\[
t_{on}=t_0+\frac{b\exp(P_e/P_d)}{\max(P_e-P_0,0.01)},\quad
P_e=\operatorname{median}P_{raw}(0\!:\!2\,s),\quad
P_{0,max}=\min(5,\min_{training}P_e-0.01).
\]

Four parameters `(Pd,P0,b,t0)`; bounds `[0.1,100] bar`, `[-5,P0_max] bar`, `[0.0001,10000] s·bar`, `[0,120] s`; starts `(3,1,15,0)`, `(2,0.5,3,8)`, `(6,1,1,10)`. Log coordinates for Pd/b; C2 clipping, optimizer/tolerances/retry unchanged. Minimize equal-condition/equal-brew weighted squared onset residuals. Missing detections are never imputed: fit detected training targets, normalize within represented conditions, compute C2's cap from those same training brews only. All five 1-bar x1.5 entries are undetected in the cache; disclose lost low-pressure target/cap support. Keep every fold, including one with no detected evaluation targets (RMSE unavailable). Report parameters, `P0+Pd`, training and held-out RMSE/coverage, objective, bound hits, cap binding, minimum margins and floor uses; training floor must be inactive, held-out floor uses remain visible and never constrain fitting. Reuse saved x1 as reference. For each matching C2 T2-F fold report `P0f + Pd*ln(1+Pstar/Pd)` using its saved P0f/Pstar and new onset Pd: **plug-in only; Pstar would refit**.

## 2. Restart record: one qualitative, ungraded observation

Read `/home/tim/wasz-terminal-mass-evidence/upstream/measurements_brew_restarting/brew_restarting.txt`; `t/1000` seconds, `m` grams, `p2/100` line bar. As C1, flowing episodes have line pressure >6 bar; pauses are intervening complementary episodes. List all episodes, including initial/final off intervals, native start/end times, durations, source lines and pause median/minimum line pressure, observed baseline-relative mass change and mean mass slope (end-minus-start mass divided by duration). For each flow episode use C1's OLS mass slope over its last 5 s; flag shorter episodes unavailable. Preserve time order and ratios to the first episode. For each post-restart episode also report OLS slope of smoothed flow against time (g/s per s); differentiate/smooth within the episode only, same 31/1 observer, excluding half-window edge samples; short support is unavailable.

**Pre-declared reading:** decay toward the pre-pause level within segments is consistent with a reversible lagging state; holding or ratcheting up across restarts points to an irreversible change. Off-state line pressure is not measured puck pressure; this record cannot establish a mechanism.

## 3. In-sample flow screens

`DESCRIPTIVE_ALL` only. Fix C2's saved `Mc=28.709461834955388 g`; fixed-Pd screens use `Pd=3.9844972419062152 bar`. Preserve B0c raw-line forcing (`P=max(Praw,0)`), clean support, x1-onset+2-s mask, 0.5-s fit/0.1-s reporting grids and stored 100-s observer. With equal-condition/equal-brew weights `w_i`, mask `m_ij`, retain

\[
J=\sum_i w_i\frac{\sum_jm_{ij}(q_{ij}-q^{obs}_{ij})^2}{\sum_jm_{ij}},\qquad
\dot M=q=C\exp[-\exp(-M/M_c)],\quad M(0)=0
\]

at stable pressure; observed onset never initializes hydraulic state. Reuse C0/C1 exposure inversion/trapezoids. Replay saved C2 T2-F on identical data (saved fit objective `0.0719361259858887`); compare both objectives on each identical grid. Put the saved-versus-recomputed T2-F objective replay FIRST in SUMMARY’s screens section, before comparing screen objectives (A4). SUMMARY must say: **“In-sample screens can mislead and do not replace LOCO + refits.”**

**T3-D:** exponential threshold distribution, mean `lam`:

\[
C=aP_d e^{-P/P_\star}H(P),\quad H=1-e^{-P/\lambda}-\frac{P_d}{\lambda-P_d}(e^{-P/\lambda}-e^{-P/P_d}).
\]

For near equality use `x=P/Pd`, `z=P(1/Pd−1/lam)`, `H=1−exp(−x)[1+x·exprel(z)]`, `exprel(z)=Σ z^k/(k+1)!`; at equality `H=1−(1+x)exp(−x)`. Test `lam→0` against T2 with P0=0. Fit `(a,Pstar,lam)` (**3**) and `(a,Pstar,lam,Pd)` (**4, EXPLORATORY**). Bounds: a `[0.001,20] g/s/bar`, Pstar `[0.5,100] bar`, lam `[0.0001,100] bar`, free Pd `[0.1,100] bar`; all log coordinates. Three starts `(1,15,0.5)`, `(1.5,30,1)`, `(2,8,2)`; free-Pd starts append `3,2,6` respectively. Add a third T3-D screen with Pd fixed at the x0.5 onset DESCRIPTIVE_ALL fit (3 parameters, same bounds/starts/reports): **plug-in only; Pd comes from a sensitivity detection, not the primary onset target** (A2).

Report `P0_eff=−Pd ln(1−lam/Pd)` only for lam<Pd, otherwise undefined. Analytic capacity peak solves `Pstar H′=H`, where `H′=(exp(−P/lam)−exp(−P/Pd))/(lam−Pd)` and equality limit `H′=P exp(−P/Pd)/Pd²`; bracket roots and check endpoints. Separately report constant-pressure 100-s flow peak on C1's 1–13-bar/0.05-bar grid, ≥9-bar endpoint slope, signed endpoint residual at **all 11 conditions**, low-pressure (1/2/3.5-bar) mean signed bias/mean absolute residual, and J versus T2-F.

**T3-R:**

\[
C=aP_d e^{-S/P_\star}\{1-e^{-\max(P-P_0,0)/P_d}\},\qquad
\tau\dot S=P-S,\quad S(t_{first\ raw})=0.
\]

Four fitted parameters `(a,Pstar,P0,tau)`, **EXPLORATORY**, Pd fixed as T2-F. Bounds: a/Pstar as above, P0 `[-5,5] bar`, tau `[0.1,1000] s` searched in log-tau; starts `(1,15,1,1)`, `(1.5,30,0.5,10)`, `(2,8,1,100)`. Integrate S over the entire measured pre-stable ramp and onward, never reset S at stable pressure/onset; keep M's stable-zero convention. For linear pressure between samples, `v=(Pnext−P)/dt`, use `Snext=Pnext−tau*v+(S−P+tau*v)exp(−dt/tau)`. Explicit tau=0 limit sets S=P and replays C2 T2-F via `assert_allclose(rtol=1e-12, atol=0)`.

Report tau, bounds/starts and per-condition predicted flow at observed onset versus saved T2-F. Replay fitted parameters through the restart history twice: pause forcing of S = zero puck pressure or measured line pressure; q=0 during pauses, M retained, S evolves; start M=S=0 at first raw record. SUMMARY must state that the replay uses q=0 in pauses and, for the line-pressure scenario, S tracks off-state line pressure while q=0, which is a bound, not a model of the pause (A3). Compute predicted last-5-s **mass slopes**, ratios and min/max exactly as observed. With other fitted parameters frozen, invert each min/max ratio versus log-tau over `[0.1,1000]` using the saved full-precision ratios (approximately `1.747450`/`2.349328`; display 1.747/2.349). Report all solutions or unattainability, numerical brackets and the needed-tau range between endpoint solutions; it is conditional on frozen parameters, not a confidence interval.

**Pre-declared reading:** if needed tau overlaps the fitted tau, one time constant serves traces and restart; if not, it does not; if tau is bound-pinned or starts disagree, traces do not identify tau and only the needed tau is reported. Preserve fitted-start diagnostics in CSV even when withholding an identified tau interpretation; report each off-state scenario separately.

## 4. Artefacts, tests, delivery and stop

Before trusting a better J, inspect floors, bound-pinned parameters, every start's convergence/objective/parameters, and lam≈Pd cancellation (use series for `|z|<1e-4`). Flow fits use C2's three-start least-squares tolerances `1e-8`, 500 evaluations/start and existing 1500-evaluation dogbox fallback. Flag bound proximity within `1e-6` of coordinate range; start disagreement if J differs by `>1e-6 max(1,Jbest)` or fitted tau differs by >10%, including near-equal J. No adaptive bounds/starts or dropped failures.

**Later files:** new module above; `tests/test_pressure_peak_stage_c3a.py`; this directory's one-page plain-prose `SUMMARY.md` (no em dashes), `RESULT_TABLE.csv`, optional `FIGURE.png`. CSV holds typed audit/fit/condition/restart/check rows, hashes, missingness, all starts, numerical replay fixtures and OLS sufficient statistics; no raw-source copies. CI tests on **Python 3.10 and 3.12** consume these fields without external data: 56/11 coverage and cached-threshold ordering/missingness; training-only caps/floors and fold membership; onset/plug-in arithmetic; T3-D equality/zero-lam limits, nonnegativity and peak stationarity; T3-R tau=0 identity, ramp/constant-pressure relaxation and no reset; restart segmentation/windows/slope ratios; same-data objectives/residual aggregates; starts/bounds/labels. Each optional raw-data check has a CI-runnable CSV twin, not merely a saved pass flag.

Estimate **10–20 min** for later point fits/screens/replays and focused tests, no bootstrap; retain C0's **two-hour cumulative wall cap**, counting interrupted/resumed work. Default serial; any parallel workers get one BLAS thread (`OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=OMP_NUM_THREADS=1` before imports). Earlier stages and source data stay unchanged. Update only the status item’s next_gate to say C3a diagnostics are ready for owner review and C3 is not authorized; keep it active with `verified_commit = null`. Regenerate `STATE_OF_TRUTH.md` only via `python -m puckworks.statusdoc --write`. Mark PR #402 ready when CI is green, report results and artefact flags, then stop for owner review. No MEETS/NEAR/MISSES/PASS grades in C3a outputs.
