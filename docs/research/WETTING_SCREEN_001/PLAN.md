# PW-WETTING-SCREEN-001 — frozen-form-A wetting screen

**Owner-approved execution, with amendments.** G1, retrospective and target-exposed; no production change or validation upgrade. Repair early onset while preserving flow; [B0d W1](../PRESSURE_PEAK_STAGE_B0D/SUMMARY.md) is timing-only precedent.

**Inputs/equations.** Freeze [D0 tuples](../PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv) (PW `dce84b2`) and [EWP #220](https://github.com/trbrewer/espresso-whole-pull/pull/220) (`67bead2`) R0 constants/inventory; authenticated `waszkiewicz2025/traces_per_brew`: 56 brews/eleven conditions, [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0. Stable-pressure clock, 100-s horizon, inlet $P=\max(P_{\rm raw},0)$ bar, $\Delta p_w=10^5P$ Pa. Uniform dry bed:

$$
x_f^2(t)=\frac{2}{\phi\mu}\int_0^t k_w(s)\Delta p_w(s)\,ds,
\qquad \int_0^{t_b}k_w\Delta p_w\,ds=\phi\mu L^2/2.
$$
$$
q_{\rm eq}=\frac{1000\rho A k_w\Delta p_w}{\mu L},\quad
\int_0^{t_b}q_{\rm eq}\,dt=M_{\rm pore}/2\approx4.595\,\mathrm{g},\quad M_{\rm pore}=1000\rho A\phi L\approx9.19\,\mathrm{g}.
$$

After breakthrough, $\dot M=C_A(P)\exp[-\exp(-M/M_c)]$, $M(t_b)=0$, with $C_A=aP_d[1-e^{-(P/P_d)^n}]e^{-P/P_\star}$. Pressure keeps absolute times. W0 uses $k_A(P,0)=\mu L C_A(P)e^{-1}/(1000\rho A10^5P)$, zero flux at zero pressure. Breakthrough changes finite-time flow.

| Arm | Rule and fitted parameter domains |
|---|---|
| W0 reference | A1: $k_w=k_A(P,0)$; no fit. |
| Z diagnostic only | $t_b=0$; no fit. |
| W1 | Phenomenological constant-delay null: $t_b=\tau_0$, $\tau_0\in[0,100]$ s; not an identified volume. |
| W2 primary | $k_w=k_{w0}e^{-P/P_w}$; $k_{w0}\in[10^{-16},10^{-12}]$ m², $P_w\in[0.5,30]$ bar. |
| W2T diagnostic | W2 plus $t_s\in[0,100]$ s: detector sees $B(t-t_s)$, zero before time zero; bed/recovery clock unchanged; three-parameter observation diagnostic, explicit exception to the two-parameter limit. |

W1 uses $x_f/L=\sqrt{t/\tau_0}$ and $t_w(z)=\tau_0(z/L)^2$: **chosen phenomenological trajectory for W1**, no added parameter. Z/$\tau_0=0$ is immediately wet, fresh inventory, zero dissolved solute. W2 is primary/two-parameter: $t_b=\beta e^{P/P_w}/P$, $\beta=\phi\mu L^2/(2\cdot10^5k_{w0})$, minimum at $P_w$: the **fitted wetting pressure scale**; [Corrochano reconciliation](../../analysis/sci_md_corrochano_dry_compaction_001/SOURCE_RECONCILIATION.md) qualitative only. Bounds are search domains. W3/other combinations remain deferred.

**Beverage predictor/observer.** Fixed R0 release/storage/transport in 1D Python (0.15/s, 180 kg/m³, diffusivity $10^{-9}$ m²/s, unchanged inventory), no chemistry fitting. Use each wetting history/outer-fold tuple; carry dissolved mass and remaining inventory through breakthrough. R0 chemistry remains engineering assumptions. $B_{bed}=M+M_{solute,out}$. Verify against 23-pressure native A0/A1 constants and A1 histories: per-brew front/liquid/beverage/detection differences, non-detections/qualification flags; no new gate. Accelerations approximate this fold-isolated column; DESCRIPTIVE_ALL lookups stay descriptive; no outflow is not zero TDS. No observed held-out mass/TDS predictor inputs.

W2T leaves the bed unchanged: $B_{scale}(t)=B_{bed}(t-t_s)$ and $q_{scale,liq}(t)=q_{bed}(t-t_s)$, zero before the delayed trace. Detector/flow scores/extrema use shifted quantities; unshifted flow is diagnostic. Resample beverage mass onto original timestamps, then B0c baseline, differentiation, 31-sample filter, strict 0.5-g/0.1-g/s thresholds sustained ≥2 s, reported at interval start.

**Fitting.** In fold h, **use its ordinary-LOCO (a, Pstar, n, Pd, Mc) for every brew**, fit timing outside h, never using training brews’ own tuples. DESCRIPTIVE_ALL is descriptive only. Condition-balanced squared loss: detected $(\hat t-y)^2$; valid non-detection $\max(0,c_i-y)^2$, where $c_i=\max\{t_j:T_{last}-t_j\ge2\}$. Censor support is fixed: missing coverage never shortens the horizon; resolve or report unavailable. Nine log-grid points per k/Pw axis, 21 linear delay points; bounded Powell from five best distinct starts in log(k_w0), log(Pw) and scaled-delay coordinates; report tied minima, boundaries/unidentified directions; no post-score domain changes.

**Outputs and compute.** One-page numbers-first SUMMARY; CSVs by brew/pressure: signed median errors/bounds, detection counts, separate fronts (never detected-only medians); fits, verification, hashes/core-hours; onset/flow figures. Keep all 56; separate 1/2 bar, including Z's remaining non-detections/errors. Reuse C0/D0 bands and FORM_A liquid-flow endpoint/primary/companion masks and aggregation. Censored onset bounds >4.53 s are MISSES; otherwise unresolved. Pair every arm−W0 and W2T−W2 on 1,000 paired condition/brew draws (seed 20261103); label bound differences; intervals conditional on fitted timing/transferred tuples. Lowest held-out nominal detector median; DESCRIPTIVE_ALL onset/flow extrema on the same 23-pressure, 100-s sweep with common 0.1-s observations; qualify interpolation against W0's 6.009-bar reference. Mark edge minima as boundary, censor-obscured minima unidentified; no extra sweep. 3 families × (11 folds + 1 descriptive) = 36 fits; W0/Z evaluations only. Estimate 20–100 core-hours including columns inside search; record actuals; no wall-clock limits, CFD, form-A refitting, new gates or successor work. Report the onset/flow tradeoff even if none succeeds.
