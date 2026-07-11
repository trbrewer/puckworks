# Model card: Pannusch 2024 kinetic espresso extraction

**Paper/thesis:** Pannusch et al., "Model-based kinetic espresso brewing control chart for
representative taste components," J. Food Eng. 367, 111887 (2024). DOI 10.1016/j.jfoodeng.2023.111887.
Reprinted as Article 3 in Pannusch (V.B.), PhD dissertation, TU Munich, 2024 (accepted 21.06.2024).
**Stage(s):** extraction (primary); grind, packing (PSD→representative particles, porosity) · **Kind:** runtime
**Status:** card-only

## Scope and mechanism
One-dimensional, convection-dominated **two-grain** (bidisperse fine/coarse) saturated
extraction of individual solutes from a coffee puck, extending the Moroney et al. (2019)
model — itself from Melrose/Corrochano (2012, 2015, 2018) — with constitutive relations
that make mass transfer and equilibrium depend on **water temperature and flow rate**.
The bed is a mix of two representative particle sizes; solute leaves fine and coarse
particles by first-order (volume-averaged) interphase transfer into a percolating liquid
phase. Grind enters through the two representative sizes and the fines volume fraction.
The model is parameterized per solute against the Schmieder et al. (2023) kinetics data
(TDS, caffeine, trigonelline, chlorogenic acid) and outputs cup concentrations and a
yield-vs-(temperature, flow) control chart per component. Wetting/swelling is assumed
complete at t=0 and porosity constant.

## Governing equations
Liquid-phase balance for solute i (Eq. 1); fine- and coarse-particle solid balances
(Eqs. 2–3). Subscript 1 = fine, 2 = coarse; k indexes grind level.

Eq. 1: ∂c_l,i/∂t + v_l ∂c_l,i/∂z = (6 h_sl1,i α_s1,k)/(α_l d_s1)·(K_i c_s1,i − c_l,i)
       + (6 h_sl2,i α_s2,k)/(α_l d_s2,k)·(K_i c_s2,i − c_l,i)

Eq. 2: ∂c_s1,i/∂t = −(6 h_sl1,i / d_s1)·(K_i c_s1,i − c_l,i)   [fines: no intragranular porosity]

Eq. 3: ∂c_s2,i/∂t = −(6 h_sl2,i / (φ_v2 d_s2,k))·(K_i c_s2,i − c_l,i)

Eq. 4: v_l = Q / (A_cs α_l)   (interstitial velocity from imposed flow rate Q)

Grind reduction (Eqs. 5–6): fines volume fraction from Sauter diameter d32,k and the two
peak sizes, ψ_k = (d32,k^{-6} − d_s2,k^{-6}) / (d_s1^{-6} − d_s2,k^{-6}); then
α_s1,k = (1−α_l)ψ_k, α_s2,k = (1−α_l)(1−ψ_k).

Mass-transfer constitutive (Eqs. 7–10): Sh_x,i(v_l,T) = A_x,i Re^{B_x,i} Sc_i^{1/3}, with
Sh_x,i = h_slx,i d32 / D_i(T), Re = d32 v_l ρ(T)/(α_l η(T)), Sc_i = η(T)/(ρ(T) D_i(T)).
Diffusion coefficient (Eq. 11, Wilke–Chang): D_i(T) = 7.4·10^{-15}·(2.6 M_i)^{1/2} T /
(η(T) V_i^{0.6}); ρ(T), η(T) from pure-water correlations (Stephan et al. 2019).

Equilibrium constitutive (Eq. 12, van 't Hoff): K_i(T) = K_ref,i · exp[γ_i (1/T_ref − 1/T)].

Initial/boundary conditions (Eqs. 13–14): c_l,i(0,z)=K_i c_s0,i, c_s1,i(0,z)=c_s2,i(0,z)=c_s0,i;
c_l,i(t,0)=0 (equilibrium at t=0 from preinfusion; clean inlet).

Observables (Eqs. 15, 18): fraction/cup concentration C_fij = (1/V_fj)∫ c_l,ij(L,t) Q_j(t) dt;
yield Y_i = C_cup,i(Q,T) V_cup / M_0 (mg solute per g coffee, default M_0 = 20 g).

Symbols: c liquid/solid solute concentration (M L⁻³), v_l interstitial velocity, z axial
coordinate, h_slx,i lumped mass-transfer coefficient (L T⁻¹) for class x, K_i solid–liquid
distribution constant (1), α_l bulk porosity, α_sx,k solid volume fraction, φ_v2 coarse
intragranular pore fraction, d_s1/d_s2,k representative sizes, d32 Sauter diameter, D_i
diffusivity, ρ/η water density/viscosity, M_i molar mass, V_i Le Bas molar volume,
c_s0,i initial solid concentration, A_x,i/B_x,i Sherwood coefficients, γ_i van 't Hoff slope.

## Parameters
Fitted per component (Table 2). h_sl and K carry no direct measured values — they are
generated at runtime from the coefficients below.

| symbol | value | units | source |
| --- | --- | --- | --- |
| A1, B1 (caffeine) | 7.92e-3, 0.36 | 1 | fitted |
| A2, B2 (caffeine) | 3.11e-2, 1.13 | 1 | fitted |
| K_ref, γ, c_s0 (caffeine) | 0.81, −371, 10.80 | 1, K, mg mL⁻¹ | fitted |
| A1, B1 (trigonelline) | 3.33e-3, 0.06 | 1 | fitted |
| A2, B2 (trigonelline) | 2.06e-2, 0.77 | 1 | fitted |
| K_ref, γ, c_s0 (trigonelline) | 1.36, −431, 4.19 | 1, K, mg mL⁻¹ | fitted |
| A1, B1 (chlorogenic acid) | 4.17e-3, 0.06 | 1 | fitted |
| A2, B2 (chlorogenic acid) | 2.07e-2, 0.82 | 1 | fitted |
| K_ref, γ, c_s0 (CGA) | 0.94, −379, 6.23 | 1, K, mg mL⁻¹ | fitted |
| A1, B1 (TDS) | 3.04e-3, 1.08e-7 | 1 | fitted |
| A2, B2 (TDS) | 2.16e-2, 0.86 | 1 | fitted |
| K_ref, γ, c_s0 (TDS) | 1.18, 68.3, 182 | 1, K, mg mL⁻¹ | fitted |
| ψ, d_s2 (grind 1.4 / 1.7 / 2.0) | 0.19/0.23/0.22, 332/330/301 | 1, μm | fitted per grind |
| d_s1 (fine peak) | ~24 (PSD peak) | μm | measured (PSD peak; fixed across grinds) |
| d32 (Sauter) | 84 | μm | measured |
| α_l (bulk porosity) | not provided (per-grind, Δ≤0.02) | 1 | measured (solid density) |
| φ_v2 (coarse intragranular) | not provided | 1 | measured/derived |
| T_ref | within 80–98 °C range | K | nominal |
| D_i, ρ(T), η(T) | Wilke–Chang / water correlations | L² T⁻¹, kg m⁻³, Pa s | computed (nominal) |

TDS is modeled as a caffeine-like pseudo-molecule (same D_i). Authors note the fitted
parameters "lack physical meaning and generality."

## Calibration and validation offered by the source
**Fit** (nonlinear least squares, lsqnonlin trust-region-reflective, sequential estimation
to break parameter correlations; weight w = 1/y(t); ode15s, five-point biased-upwind FDM).
Mean absolute percentage error over all fit experiments: TDS 6.07 %, caffeine 4.59 %,
trigonelline 7.85 %, CGA 4.98 % — roughly half the MAPE of Schmieder et al. (2023)
exponential fits (16.12 / 11.03 / 16.51 / 13.01 %).

**Prediction on independent experiments** (constant + gradient temperature 86–93 °C, flow
1.7–2.3 mL s⁻¹). Temperature set: caffeine matched well, average MAPE 4.71 %; CGA poor
(avg 16.86 %), attributed by the authors to a **roasting-batch difference** in the
validation coffee, not model error. Flow-rate set: average MAPE 18.23 % (weaker).

**Honest caveats.** Across their data the cup-concentration differences from temperature,
flow rate, and grind were **not statistically significant** (ANOVA / Tukey HSD; one
exception, CGA between constant 1.7 and 1.7→2.3 mL s⁻¹, p=0.025, which they ascribe to
beverage-volume/measurement variance). So the kinetic fit is good, but the very
process-variable sensitivities the model is built to characterize sit largely within
experimental noise in the validation set. Validation is against the authors' own
Schmieder-2023 apparatus and one coffee; no external replication.

## Assumptions and validity range
- Constant flow-rate control (Q imposed). The model consumes flow, **not pressure**, and
  does **not** predict permeability or flow.
- Constant porosity; swelling, particle erosion, compaction, and fines migration ignored —
  explicitly acknowledged, and contradicted by the same author's Article 1 (Hargarten 2020),
  which measured ~15 % coarse-particle diameter growth and erosion during wetting.
- Wetting complete at t=0 (fully saturated pores) — **silent on the infiltration/first-drip
  transient**; a preinfusion step is assumed to have finished.
- Homogeneous, unidirectional 1D flow; no channeling. The fine-grind concentration dip is
  attributed to flow inhomogeneity + higher pressure, i.e. outside the model.
- Isothermal bed (heat transfer ≫ mass transfer); TDS = single caffeine-like molecule.
- Solutes assumed below saturation, so no solubility ceiling — authors note this breaks in
  cold brew (<10 °C) but holds above 80 °C.
- Fitted range: T 80–98 °C, Q 1–3 mL s⁻¹, EK43-type grind 1.4–2.0, brew volumes to ~60 mL
  at 20 g. No extrapolation beyond this design space (authors' instruction).
- Diagnostic from the thesis framing (Fourier analysis): fines Fo>1, coarse Fo<1 over a
  20–60 s shot — the fine fraction dominates yield; coarse-particle diffusion barely completes.

## Interface mapping
Inputs consumed: GrindState (→ d_s1, and the fitted ψ/d_s2 per grind); BedState.porosity
(α_l, φ_v2); a **flow-rate trace Q(t) and temperature T(t)** — NOT MachineState.P_of_t.
Outputs produced: ShotResultState.tds_pct, EY_pct (as TDS yield), t_shot, beverage_g, and
per-component traces (caffeine, trigonelline, CGA concentration/yield).

Couplings/adapters: **runtime** in the shot chain, but only if driven by flow rate. The
puckworks MachineState is pressure-based, so an adapter is needed to supply Q(t) — either
the measured DE1-fixture-A flow W(t)/flow trace, or a flow model converting P(t)→Q(t) via
permeability (unlike cameron2020, which consumes MachineState.P directly). Grind coupling
is really an **offline calibration**: ψ and d_s2 are fitted per grind, not mapped from a
measured PSD, so a clean GrindState→parameter adapter would require the fitted table or a
refit. Per-component outputs exceed the current ShotResultState schema (see backlog below).

## Extractable data
- **Table 2** → data/pannusch2024_table2.csv: A1,B1,A2,B2,K_ref,γ,c_s0 for TDS/caffeine/
  trigonelline/CGA plus ψ,d_s2 per grind (1.4/1.7/2.0). Directly transcribable.
- **Table 1** (validation DoE: 8 experiments, flow/temperature start–end points).
- **Schmieder et al. (2023) extraction-kinetics dataset** (TDS, caffeine, trigonelline, CGA
  vs beverage volume; flow 1–3 mL s⁻¹, T 80–98 °C, three grinds) — the parameterization/
  validation data, published in a **public Mendeley repository, DOI 10.17632/y2tz67f6ry.1**.
  High registry value: transcribable multi-component kinetics with named solutes.
- Fit/prediction MAPE tables and the yield control-chart array (also in the repo); a public
  "Espresso Brewing Control App" visualizes interpolated yields.

## Overlaps and conflicts
- **cameron2020.extraction_bdf (extraction, runtime)** — direct competitor and complement.
  Cameron: two-population saturated, per-bed-volume inventory (EY ceiling 29.6 %), TDS only,
  40 g, pressure/flux-driven. Pannusch: bidisperse two-grain, four analytes incl. named
  taste solutes, full kinetics, explicit temperature+flow constitutive relations, but
  flow-driven and constant-porosity. The dissertation explicitly faults Cameron for
  measuring only TDS in 40 g. Pannusch adds component chemistry and a T/flow parameter map
  Cameron lacks; Cameron keeps the pressure→flux coupling Pannusch lacks.
- **Backlog: extraction multi-class solute chemistry (acids/sugars/bitter)** — Pannusch
  directly fills this. Caffeine (bitter), CGA (sour proxy), trigonelline, with distribution
  constants ordered by polarity (K_ref: trigonelline 1.36 > CGA 0.94 > caffeine 0.81), makes
  polarity-linked sensory claims testable. Strongest reason to bring it in.
- **Backlog: observables temperature effects** — supplies a temperature model (van 't Hoff K,
  Wilke–Chang D, water props) but concludes the effect above 80 °C is small.
- **brewer2026.streamtube (bed_dynamics)** — complementary "no-channeling" mechanistic
  baseline; its constant-porosity/homogeneous-flow assumption is the null against the
  lognormal channeling closure. Adds a *third* fine-grind-dip explanation (flow inhomogeneity
  + pressure), distinct from streamtube channeling and Foster's unsaturated wetting.
- **foster2025.infiltration** — non-overlapping/complementary: Foster models the wetting
  front and first drip that Pannusch assumes already complete at t=0. Pannusch is silent
  exactly where Foster is scoped.
- **wadsworth2026.permeability / grind stage** — Pannusch's ψ,d_s2 fitting is a weaker,
  data-fitted route from PSD to an effective bed than Wadsworth's percolation k(R,φ_p); it
  does not model permeability at all.

## Implementation estimate
Effort **M**. All three PDEs, constitutive relations, ICs/BCs, numerical scheme (FDM
five-point biased-upwind + ode15s), and a full fitted parameter table are given, and the
validation data are public (Mendeley 10.17632/y2tz67f6ry.1). A runtime extraction solver
already exists (cameron2020.extraction_bdf), so the two-grain/per-component variant can
reuse machinery; new pieces are the Sherwood/Re/Sc + Wilke–Chang + water-property closures,
the van 't Hoff K(T), and a flow-rate input adapter (pressure→Q or measured flow). Gate:
reproduce the reported fit MAPEs (TDS 6.07 %, caffeine 4.59 %, trigonelline 7.85 %,
CGA 4.98 %) against the Schmieder kinetics, and the yield control-chart array; quarantine
the flow-rate-prediction regime (their own MAPE 18.23 %) and the CGA validation (roasting
confound). Dependency: a flow-rate provider, since the model does not consume pressure.

VERDICT: implement-now — fills the top extraction backlog gap (named multi-solute chemistry with polarity-linked kinetics) and ships full equations, fitted parameters, and public validation data, complementing rather than duplicating cameron2020 — effort M.
