# PW-WETTING-SCREEN-001 — frozen-form-A wetting screen

**Phase 0: plan only; stop for owner approval.** G1, retrospective and target-exposed; no production change or validation upgrade. Seek the smallest independently motivated correction to early onset without losing flow accuracy; [B0d W1](../PRESSURE_PEAK_STAGE_B0D/SUMMARY.md) is timing-only precedent.

**Inputs and equations.** Freeze [D0's saved form-A tuples](../PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv) (PW `dce84b2`) and [EWP #220](https://github.com/trbrewer/espresso-whole-pull/pull/220) (`67bead2`) R0 geometry/fluid/inventory; use authenticated `waszkiewicz2025/traces_per_brew`: 56 distinct brews, eleven conditions, [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0. Raw/native files inspected. Use stable-pressure time, 100-s horizon, inlet gauge pressure $P=\max(P_{\rm raw},0)$ in bar, and $\Delta p_w=10^5P$ in Pa. For a uniform dry bed:

$$
x_f^2(t)=\frac{2}{\phi\mu}\int_0^t k_w(s)\Delta p_w(s)\,ds,
\qquad \int_0^{t_b}k_w\Delta p_w\,ds=\phi\mu L^2/2.
$$
$$
q_{\rm eq}=\frac{1000\rho A k_w\Delta p_w}{\mu L},\quad
\int_0^{t_b}q_{\rm eq}\,dt=M_{\rm pore}/2\approx4.595\ {
m g},\quad M_{\rm pore}=1000\rho A\phi L\approx9.19\ {
m g}.
$$

After breakthrough, $\dot M=C_A(P)\exp[-\exp(-M/M_c)]$, $M(t_b)=0$, with $C_A=aP_d[1-e^{-(P/P_d)^n}]e^{-P/P_\star}$. Pressure retains its original absolute times. W0 uses $k_A(P,0)=\mu L C_A(P)e^{-1}/(1000\rho A10^5P)$, zero flux at zero pressure. Breakthrough changes finite-time flow.

| Arm | Rule and fitted parameter domains |
|---|---|
| W0 reference | A1: $k_w=k_A(P,0)$; no fit. |
| Z diagnostic only | $t_b=0$; no fit. |
| W1 | Phenomenological constant-delay null: $t_b=\tau_0$, $\tau_0\in[0,100]$ s; not an identified volume. |
| W2 primary | $k_w=k_{w0}e^{-P/P_w}$; $k_{w0}\in[10^{-16},10^{-12}]$ m², $P_w\in[0.5,30]$ bar. |
| W2T predeclared | W2 plus $t_s\in[0,100]$ s: detector sees $B(t-t_s)$, zero before time zero; bed/recovery clock unchanged. |

W2 has constant-pressure $t_b=\beta e^{P/P_w}/P$, $\beta=\phi\mu L^2/(2\cdot10^5k_{w0})$, minimum at $P_w$: a **fitted wetting pressure scale**, with Corrochano qualitative motivation only. Bounds are search domains, not priors. W3 and other combinations remain deferred.

**Beverage observer.** Build one wetting-independent outlet-TDS relation $w(P,t-t_b)$ from all 23 native A0/A1 constant pressures; integrate $dB=dM/(1-w)$, so $B=M+M_{\rm solute,out}$. Cross-check A0↔A1 beverage traces/onsets before averaging arms with linear pressure/age interpolation; disclose unsupported regions. If discrepancies/unsupported coverage obscure onset errors, use 1D R0 release/transport (0.15/s, 180 kg/m³, unchanged inventory), without tuning chemistry. No observed held-out mass/TDS enters predictions. Report the route and W0 per-brew front/liquid/beverage/detection differences from EWP, including non-detections and native qualification flags; no gate. Resample beverage mass onto original timestamps on common support, never extend terminal mass, then apply B0c baseline, differentiation, 31-sample filter, strict 0.5-g/0.1-g/s thresholds for ≥2 s, reporting interval start.

**Fitting.** In fold h, **use its ordinary-LOCO (a, Pstar, n, Pd, Mc) for every brew**, never training brews' own tuples; fit timing outside h. DESCRIPTIVE_ALL is descriptive only. Minimize condition-balanced mean squared loss: detected $(\hat t-y)^2$; valid non-detection $\max(0,c_i-y)^2$, where $c_i=\max\{t_j:T_{last}-t_j\ge2\}$. Report unavailable evidence separately. Use nine log-grid points per k/Pw axis and 21 linear delay points, then bounded Powell refinement from five best distinct starts; retain tied minima, boundary solutions and unidentified directions, without post-score domain changes.

**Outputs and compute.** One-page, numbers-first SUMMARY; per-brew/per-pressure CSVs: signed median errors/bounds, detection counts, separate fronts (never detected-only medians); fits, verification/transfer and hashed run records; onset/flow figures. Keep all 56 brews; show 1/2 bar separately, including Z's remaining non-detections/errors. Reuse C0/D0 bands and FORM_A liquid-flow endpoint/primary/companion masks and aggregation. Censored onset bounds >4.53 s are MISSES; otherwise unresolved. Pair against W0 on 1,000 identical condition/brew draws (seed 20261103); label differences of computed bounds and intervals conditional on fitted timing/transferred tuples. Report lowest held-out nominal detector median and each DESCRIPTIVE_ALL constant onset/flow extremum on the same 23-pressure, 100-s sweep with a common 0.1-s observation grid; qualify interpolation against W0's 6.009-bar reference. Future changes: analysis helper, tests, this directory. Estimate 36 fits, 1–10 core-hours using caching; 1D fallback may cost more. Record core-hours; no wall-clock limits, CFD, form-A refitting, new gates or successor work. This PR contains only this plan.
