# Model card: Foster 2025 infiltration

**Paper:** J. Foster, W. Lee, K. Moroney, D. Prjamkov, M. Salamon, A. Smith,
J. Petrassem-de-Sousa, M. Vynnycky, "Dynamics of liquid infiltration into an
espresso bed using time-resolved micro-computed tomography: Insights from
experiment and modeling," Phys. Fluids 37, 013383 (2025).
DOI 10.1063/5.0245167.
**Stage(s):** infiltration, machine · **Kind:** runtime
**Status:** gated — recorded-pressure closed form implemented and gated
parameter-free (predicted first-drip 6.4–7.8 s brackets observed 7.0 s on
DE1 fixture A; bed capacity 7.5–14.0 g brackets fitted W_dead 8.8 g). Full
pump/headspace model (their Eqs. 2–7) and infiltration↔extraction coupling
remain backlog. This card supersedes the earlier abbreviated foster2025.md.

## Scope and mechanism
One-dimensional sharp-front infiltration of hot water into an initially dry
espresso bed, coupled to a quadratic pump characteristic, laminar pipe
resistance, and an ideal-gas trapped-air headspace above the bed. Saturation
is binary (fully wet behind the front at z = s(t), dry ahead); water may pond
to height H(t) above the bed, compressing the trapped air and raising
headspace pressure. Three stages: pre-ponding (pump-limited, front moves
linearly), post-ponding (coupled ODEs for s and H), post-saturation (s = L
fixed, H relaxes to equilibrium). Validated against time-resolved micro-CT
(ROXS, 1 s reconstructions) tracking the wetting front in a 59 mm portafilter.
Notably reproduces a mid-shot flow-rate minimum with no extraction, degassing,
swelling, or particle-rearrangement mechanism — pump + headspace dynamics
alone suffice.

## Governing equations
Pump characteristic (their Eq. 2):
  p_p = p_m − (p_m − p_a)(Q/Q_m)²,  0 ≤ Q ≤ Q_m
with p_p pump-outlet pressure, Q volumetric flow rate, p_m shut-off pressure,
p_a atmospheric pressure, Q_m maximum flow rate.

Pipe resistance (Eq. 3): p_p − p_h = R_f Q, with p_h headspace pressure and
R_f a resistance coefficient (Darcy–Weisbach laminar form).

Trapped-gas headspace, ideal gas with instantaneous heating β = T1/T0
(Eqs. 4–5): p_h|t=0 = p_a β;  p_h = p_a H0 β / (H0 − H),
with H0 initial headspace height and H(t) ponded-water height.

Pump flow for given H (Eq. 7, positive root of the quadratic Eq. 6):
  Q = −Q_m²/(2(p_m−p_a)) · [ R_f − sqrt( R_f² + 4((p_m−p_a)/Q_m²)(p_m − p_a H0 β/(H0−H)) ) ]

Headspace liquid conservation (Eqs. 8–9):
  dH/dt = 0 for t < t_p;  dH/dt = q_f − q|_{z=0} for t ≥ t_p,  q_f = Q/A,
with A portafilter cross-sectional area and t_p the ponding time.

Darcy flow in the wet region with incompressibility (Eqs. 11–16): q constant
in z, pressure linear in z with boundary conditions p|_{z=s} = p_a − p_c
(capillary suction p_c at the front) and p|_{z=0} = p_h + ρgH, giving
  q|_{z=0} = f(H,s) = −(k/(μ s)) [ p_a − p_c − p_a H0 β/(H0 − H) − ρg(H + s) ]
with k bed permeability, μ, ρ fluid viscosity and density, g gravity.

Flow into bed (Eq. 18): q|_{z=0} = min(Q_p/A, f(H,s)), where Q_p is Eq. 7
evaluated at H = 0 (Eq. 10).

Front motion (Eqs. 19–21): φ_T ds/dt = Q_p/A (pre-ponding, so s linear in t,
Eq. 23); = f(H,s) (post-ponding, Eq. 27 with Eq. 26 for H); = 0 for t ≥ t_s,
where φ_T is water-accessible total porosity and s(t_s) = L defines
saturation. Ponding position/time closed-form (Eqs. 24–25):
  s_p = kA (p_a(1−β) − p_c) / (kAρg − μQ_p),  t_p = A φ_T s_p / Q_p.
Requires β − 1 ≥ −p_c/p_a for s_p > 0.

Non-dimensionalization (Eqs. 30–31) yields groups P_m, R, ℋ = H0/L,
K = kAp_a/(μQ_mL), G = ρgL/p_a, P_c, φ_T, β; dimensionless staged system
Eqs. 32–38. Appendix A reduced model: for R ≪ P_m and G ≪ 1 the R and gravity
terms drop (Eqs. A3–A4), and for ℋ ≫ H an implicit analytical solution
I(s) − I(s_p) = t_p − t exists (Eqs. A8–A19).

Implemented in PUCK LAB: the recorded-pressure closed form
s(t) = sqrt(2k ∫P dt / (μ φ_T)) with p_c option — a simplification of the
above that replaces the pump/headspace subsystem (Eqs. 2–7) with a measured
P(t) trace. The full pump/headspace ODE system is NOT yet implemented
(= "machine mode" backlog); this card transcribes it faithfully for that
purpose.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| L | 9.975 | mm | measured (estimate from CT data) |
| H0 | 7.8 | mm | measured (estimate from CT data) |
| A | 0.002734 | m² | measured (59 mm cylinder) |
| μ | 0.315e-3 | Pa s | nominal (water 90 °C) |
| ρ | 965 | kg m⁻³ | nominal (water 90 °C) |
| p_a | 1.01325 | bar | nominal |
| Q_m | 317 | ml min⁻¹ | measured (no-portafilter steady flow) |
| R_f | 3.83e6 | Pa m³ kg⁻¹ | nominal (R = 2e-4; output insensitive, App. A) |
| g | 9.81 | m s⁻² | nominal |
| p_c | 0.1 | bar | nominal (no literature data for coffee; authors flag) |
| p_m | 15 | bar | nominal (manufacturer spec, Delonghi EC685) |
| T0 | 296.15 | K | measured (room 23 °C) |
| T1 | 363.15 | K | nominal (brew 90 °C) |
| β | 1.226 | – | derived T1/T0 |
| K | 0.0495 | – | fitted → k = 2.97e-15 m² |
| φ_T | 0.322 | – | fitted |
| t_shift | 0.796 | s | fitted (experiment start-time alignment) |

Dimensionless (Table II): P_c 0.0987, P_m 14.8038, ℋ 0.782, G 9.32e-4,
R 2e-4 (nominal).

## Calibration and validation offered by the source
Fine-grind experiment only: 10 g Arabica, <300 μm grind, 12 kg tamp,
Delonghi EC685, ROXS micro-CT at 1 reconstruction/s. Front positions s(t) and
headspace level H(t) extracted by fitting triple-sigmoid profiles (their
Eq. 1) to depth-resolved absorption; radial-shell analysis (Figs. 7–9)
supports the uniform-sharp-front assumption for the fine grind. Three
parameters (K i.e. k, φ_T, t_shift) fitted by fmincon least squares on s and
H simultaneously; Multistart used to check against local minima. Agreement is
qualitative-good: s(t) shape captured well; model H(t) rises slightly faster
than experiment (authors' own wording). Ponding at t = 0.823 s, saturation
t_s = 6.669 s. Plausibility checks on fitted values: k = 2.97e-15 m²
consistent with literature; φ_T = 0.322 below the literature 0.4–0.6 range
(authors call it "a little low" and offer delayed intragranular wetting or
closed pores as explanations). Note the circularity: k and φ_T are fitted to
the same s/H curves being reproduced, so the source validates model FORM, not
parameter-free prediction. No error metrics (RMSE etc.) are reported.
Sensitivity study (Appendix B): φ_T, K, P_m, β matter substantially; P_c and
R negligible over the ranges scanned (P_c ×0.25–2). Coarse grind: front
visibly non-uniform (faster near walls); authors explicitly decline to apply
the 1D model to it. Our own gate (registry): parameter-free first-drip window
6.4–7.8 s brackets the observed 7.0 s on DE1 fixture A; bed water capacity
7.5–14.0 g brackets fitted W_dead 8.8 g.

## Assumptions and validity range
- Sharp binary saturation front, flat and 1D. Holds for fine grind
  (<300 μm); demonstrably fails for coarse grind (300–1000 μm), where the
  front is non-uniform — model is silent there.
- Rigid bed: z = 0 fixed, no compaction/swelling/expansion during wetting.
- Headspace air trapped by a water film from t = 0; fixed moles; heating to
  T1 instantaneous. β and p_c enter only through the combination
  β − (1 − P_c); requires β > 1 − P_c.
- Constant μ, ρ (pure water at 90 °C); no dependence on dissolved coffee.
- No extraction, no CO2 exsolution, no fines migration, no channeling — all
  explicitly out of scope.
- Pump characteristic is a nominal quadratic, not a measured curve; p_m from
  manufacturer spec. Sub-atmospheric pump-outlet pressures excluded.
- p_c is a nominal guess (0.1 bar); its unimportance is only demonstrated
  within ×0.25–2 of that guess. If real capillary pressures are much larger,
  the authors say a continuous-saturation unsaturated-flow model would be
  needed.
- Silent on: temperature effects on wetting/absorption, intragranular pore
  filling dynamics, partial saturation, and everything after saturation
  except headspace equilibration.

## Interface mapping
Inputs consumed: BedState (k, depth_m → L, area_m2 → A, porosity → φ_T);
MachineState — either recorded P(t) (implemented path) or pump/headspace
parameters (p_m, Q_m, R_f, H0, β, p_c), which are NOT yet fields on
MachineState; an adapter/contract extension is needed for machine mode.
Outputs produced: front trajectory s(t), ponding time t_p, saturation time
t_s, early-shot flow transient Q(t) — feeds ShotResultState.traces and gates
extraction start.
Couplings: runtime, upstream of extraction. The clean coupling is the backlog
item: delay cameron2020.extraction_bdf per depth cell until front passage
(changes the early TDS transient). Forcing full pump/headspace + infiltration
+ extraction into one monolith is unnecessary; machine mode can be a separate
machine-stage component emitting P(t)/Q(t) that infiltration consumes.

## Extractable data
- Table I and Table II parameter sets — transcribed above; worth a
  data/foster2025_params.csv for regression tests.
- Fig. 6/8 (fine grind): s(t) and −H(t) at 1 s resolution with error bars,
  t = 0–8 s — the key validation series; transcribable from plots.
- Figs. 12–14: fitted s, w = H + φ_T s, H curves vs data (mean of 5 vertical
  lines + center line).
- Fig. 15: normalized headspace pressure and pump flow rate vs time — the
  flow-minimum signature; useful qualitative gate for machine mode.
- Raw CT data: available from corresponding author on reasonable request; no
  code or data repository published.

## Overlaps and conflicts
- foster2025.infiltration (registered): this card IS that component's full
  documentation; supersedes the abbreviated card.
- Machine backlog: Eqs. 2–7 here are the named source for "machine mode"
  (pump characteristic + headspace). Their flow-minimum result competes with
  the bed_dynamics backlog item kappa(t) = kappa0·f(P,eps,E) as an
  explanation for early-shot flow transients — a pump/headspace-only model
  reproduces the dip, so any compaction/swelling closure must be gated
  against this null.
- brewer2026.streamtube: competing hypothesis for the fine-grind EY dip.
  Foster's unsaturated-flow account (incomplete wetting = tubes at k → 0, an
  atom the lognormal lacks) must be cited alongside the channeling closure;
  per-grind first-drip timing and time-resolved CT discriminate.
- cameron2020.extraction_bdf: complement — supplies the infiltration delay
  that Cameron's fully-saturated model assumes away (infiltration ≈ 1/3 of
  shot time).
- wadsworth2026.permeability: complement — its k(⟨R⟩, φ_p) prior could
  replace Foster's fitted k, making the infiltration prediction fully
  parameter-free per grind setting (their fitted 2.97e-15 m² is a
  cross-check point).

## Implementation estimate
Recorded-pressure closed form: done and gated. Remaining: (1) machine-mode
component — three-stage ODE system Eqs. 32–38 plus Appendix A reduced/
analytic path, ode-solver on 2 states, contract extension for pump/headspace
fields; effort S–M, no new dependencies. (2) Infiltration↔extraction
coupling (delay per depth cell): touches the extraction solver's time loop;
effort M. Gate design: reproduce their t_p = 0.823 s, t_s = 6.669 s and the
Fig. 15 flow-minimum shape from Table I/II inputs; re-run the parameter-free
first-drip triangle on DE1 fixture A.

VERDICT: implement-now — the pump/headspace subsystem (Eqs. 2–7) is the
named, transcribable source for the machine-mode backlog and the coupling
that makes early-shot flow/TDS transients predictable — effort M
