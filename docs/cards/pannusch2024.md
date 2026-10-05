# Model card: Pannusch 2024 kinetic espresso extraction

**Paper/thesis:** Pannusch et al., "Model-based kinetic espresso brewing control chart for
representative taste components," J. Food Eng. 367, 111887 (2024). DOI 10.1016/j.jfoodeng.2023.111887.
Reprinted as Article 3 in Pannusch (V.B.), PhD dissertation, TU Munich, 2024 (accepted 21.06.2024).
**Stage(s):** extraction (primary); grind, packing (PSD→representative particles, porosity) · **Kind:** runtime
**Status:** implemented; source-faithful reconstructed data authority

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

## Additive prescribed-temperature capability (MODEL-PANNUSCH2024-TEMP-HISTORY-001)

`puckworks.models.pannusch2024.temperature_history.simulate_temperature_history`
accepts explicit piecewise-linear Kelvin knots or piecewise-constant Kelvin
intervals (explicit Celsius constructors), a fixed SI volumetric flow, model
start/end, observations and fraction boundaries. Temperature is prescribed
spatially uniformly; this is not a solved thermal field or an experimental ramp
reconstruction. The input flow envelope 1e-6..3e-6 m³/s is numerical and does not
resolve the source's disputed experimental flow convention. Reynolds uses
superficial Q/A; density does not convert the prescribed throughput.

The source saturated equations and fitted parameters are retained. Geometry:
alpha_l=0.17, bed diameter 0.058 m, L=0.015 m, d1=24e-6 m, phi_v2=0.4;
psi/d2 are the declared source grind entries and d32 is recomputed from them.
Physical liquid/fine/coarse concentrations (kg/m³) and accumulated outlet solute
(kg) carry continuously through coefficient jumps; only the initial model time
uses source pre-equilibration. Hydraulic volume (m³) is Q*(t-t0). Source c_s0
mg/mL is numerically kg/m³ and remains fitted, not measured recoverable inventory.
The coarse inventory capacity includes phi_v2; the fine capacity does not.
The redundant drifting legacy inlet-liquid coordinate is omitted, with physical
inlet concentration reconstructed as exactly zero. Source grain and nodal
interior/outlet equations remain; the new analytic Jacobian includes all boundary
stencil dependencies. The inherited nodal accounting defect is reported, not
corrected by a fictitious flux.

Both legacy APIs retain their old behavior: `simulate_fractions` has fixed T/Q;
`simulate_fractions_qt` varies Q with fixed T. The new API varies T at fixed Q.
The legacy arithmetic remains `flow_mL_s/1000.0/980.0`; Q=2e-6 corresponds to
legacy argument 1.96, not 2.0. No new registry component, evidence-strength
promotion, default redirection or coupling is introduced. Failed/partial solves
have explicit actual support and absent unsupported observers.

G2 / NUMERICAL_METHOD_CHANGE. Full numerical qualification is **INCOMPLETE**: three step-state agreement
checks, sampled liquid positivity, and the fixed discrete-budget quadrature
fail; constant compatibility, ramp temporal comparisons, continuum inventory
and finest-grid fractions pass. See the
[result](../analysis/model_pannusch2024_temp_history_001/RESULTS.md) and frozen
[contract](../analysis/model_pannusch2024_temp_history_001/CONTRACT.md);
[offline example](../../examples/pannusch_temperature_history.py) uses a small
illustrative mesh. PHYSICAL_VALIDATION=NOT_ESTABLISHED. Source-internal exposed
prediction targets and historical results retain their limits. Source-derived
reports retain CC-BY-NC-3.0 separately from first-party software licensing.

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

Mass-transfer constitutive (Eqs. 7–10): Sh_x,i(u_s,T) = A_x,i Re^{B_x,i} Sc_i^{1/3}, with
Sh_x,i = h_slx,i d32 / D_i(T), Re = d32 u_s ρ(T)/η(T), Sc_i = η(T)/(ρ(T) D_i(T)),
where u_s = Q/A_cs is the SUPERFICIAL (Darcy) velocity and v_l = u_s/α_l the interstitial one
(Eq. 4). The advection term of Eq. 1 transports at v_l; the Reynolds number is formed on u_s.
Equivalently Re = d32 α_l v_l ρ(T)/η(T).

  UNIT-CONTRACT NOTE (round-7 P0-1). Earlier revisions of this card and of the manuscript wrote
  Re = d32 v_l ρ/(α_l η), which with v_l = Q/(A_cs α_l) is Re = d32 Q ρ/(A_cs α_l² η) — larger
  than the implemented value by α_l^{-2} ≈ 34.6 at α_l = 0.17. The SOURCE MATLAB
  (SherwoodFunction.m: `Re = paramPh.d32 .* q ./ kin_vis`, q superficial) and our port
  (`closures.sherwood_h`) both use the superficial form; the documentation was the discrepant
  item, and the fitted A_x,i/B_x,i were estimated under the superficial convention, so the
  implementation is the authority here. See docs/paper1_resource/PAPER_A_SOLVER_CONTRACT_AUDIT.json
  and the contract test in tests/test_paper_a_model_contract.py.
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
  Cameron: two-population saturated, grain-volume concentration and phase-weighted inventory (EY ceiling 24.47 %), TDS only,
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

## Reconstructed estimand and campaign contract (2026-08-30)

`c_s0` is a `FITTED_MODEL_PARAMETER`. Experiment-46 totals are direct or directly
derived recovered mass and an `N1_OPERATIONAL_REFERENCE_ESTIMATE`; total roasted
composition, production M0, `I_ref→M0`, and a common-basis `c_s0→recovered mass`
mapping are not established. Its tail is `EMPIRICALLY_RESOLVED_MEASURED_TAIL`, not
proof of exhaustion. Lot and roast batch remain unresolved. The March campaign is
source-designated prediction, campaign-separated, target-exposed, source-internal,
and not independent validation. See `PANNUSCH_RAW_REPRO_001_REPORT.md`.


## Separate research finite-volume backend (002)

MODEL-PANNUSCH2024-POSITIVE-FV-002 is an explicitly authorized G2 /
NUMERICAL_METHOD_CHANGE, merged via PR #315 at
`1d780b7fb57df4693e22e564010c891602df119d`. Parent 001 merged via PR #314 at
`1e9f85a5e42d206baf05a0a95aa81847d506c9d5`; its numerical result stays INCOMPLETE. It retains the continuum
model and source parameters but uses cell-centered first-order upwind finite
volumes and exponential midpoint propagation of phase masses. Prescribed
spatially uniform T(t) is not a solved/measured thermal field. Numerical qualification
is VERIFIED only for the 28 declared cases/settings: sampled positivity, inventory,
temporal and spatial accuracy gates pass. Software QA, CI and review are separate;
physical validation remains NOT_ESTABLISHED. Conservation/positivity alone are
not accuracy evidence.
The 001 INCOMPLETE disposition and all its evidence remain unchanged. No registry
promotion, production-default change, coupling or successor follows.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. See
[002 results](../analysis/model_pannusch2024_positive_fv_002/RESULTS.md).


## Joint prescribed flow and temperature FV research API (003)

`puckworks.models.pannusch2024.flow_temperature_history_fv.simulate_flow_temperature_history_fv`
adds independent immutable `FlowHistory` and unchanged `TemperatureHistory` inputs.
Q is strictly prescribed SI m^3/s in [1e-6,3e-6], T is spatially uniform Kelvin
in [353.15,371.15]; both histories cover the explicit model interval. Constant
intervals and linear knots are supported without extrapolation. This API uses
the source superficial Q/A for Sherwood transfer and interstitial Q/(A*alpha_l)
for upwind transport. Source equations, coefficients, grinds and fixed geometry
are preserved. Cell phase masses and evolved outlet solute carry through the
union of Q/T knots. Collected volume is analytically integrated separately;
fractions use solute mass divided by prescribed volume.

Interior observations use the same primary-step midpoint-frozen T/Q generator
from the saved step start. Numerical frozen-step flux and prescribed-flow
diagnostic flux are separately retained and checked. No inventory complement,
clipping or state reset is used. Per-call temporal/spatial accuracy remains
NOT_ASSESSED. G2 / NUMERICAL_METHOD_CHANGE; RESEARCH_ONLY. The new joint-linear
engineering target is 5e-4 on fixed source scales, covering interior observations;
this neither inherits nor amends 002's tighter 1e-6 temperature-only result.
**VERIFIED_ON_DECLARED_CASES** for the fixed 32-execution matrix; worst
default/Radau fixed-scale error 8.20e-5. This result is bounded to the declared
histories, grids and settings; software QA, CI and independent review are separate.
See the [003 results](../analysis/model_pannusch2024_flow_temp_fv_003/RESULTS.md)
and [003 contract](../analysis/model_pannusch2024_flow_temp_fv_003/CONTRACT.md)
and [offline example](../../examples/pannusch_flow_temperature_history_fv.py).

These synthetic prescribed histories are not authorized experimental inlet
histories. The EWP flow-authority and input-mapping restrictions remain. No
registry promotion, production-default redirection, empirical accuracy, coupling,
taste or native-MATLAB equivalence follows. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Source-derived reports retain Pannusch attribution and CC-BY-NC-3.0 separately
from first-party software licensing.

## Explicit chemical states and continuation (004)

The additive model-local `stateful_fv` API exposes `FVChemicalState`, `FVPlan`,
`simulate_stateful_fv`, checked `FVCheckpoint` export, and `branch_stateful_fv`.
It reuses the prescribed-Q/T FV engine. G2 / NUMERICAL_METHOD_CHANGE includes
an explicit initial-condition extension; governing balances, source parameters,
geometry and constitutive laws are unchanged. RESEARCH_ONLY;
PHYSICAL_VALIDATION=NOT_ESTABLISHED; runtime accuracy NOT_ASSESSED.

The source-equilibrium constructor preserves the existing initialization.
Caller-supplied states require separate liquid/fine/coarse cell-average arrays
in kg/m^3 on their source phase bases, exact mesh edges, species, grind and
absolute model time. Fine capacity excludes phi_v2; coarse capacity includes it.
Inventory is computed from these physical fields, not fitted c_s0. Positive
first-cell liquid is allowed because the clean inlet is a face condition.
No missing-phase inference, equilibration, c_s0 cap, clipping or remeshing occurs.
Accepted inputs are structurally/numerically admissible, not established
post-wetting measurements. Arrays cannot reveal a caller mislabelling a basis.

A planned stop selects an existing endpoint of the original full-horizon plan.
Checked export retains exact raw masses, physical-field views, root inventory,
absolute clocks, prior mass/volume terms and remaining primary endpoints/frozen
forcing. Same-schedule resume preserves that plan; changed forcing requires an
explicit branch from the immutable checkpoint. Passive observations do not
alter propagation. A branch changes coefficients without resetting chemistry.
Only wholly checked primary endpoints export; diagnostic/interpolated times
and endpoints beyond an admissible supported prefix do not.

Segment and root-origin accounting are separately named. Each numerical step
uses a local outlet accumulator, avoiding cancellation against a large prior
total. Fractions use direct local deliveries and analytic prescribed volume;
adjacent portions recombine by mass and volume. Positive-volume exact-zero
states return valid numerical zero; zero-duration/zero-volume concentration is
undefined, and unresolved positive-state delivery is not promoted to zero.
No solid-phase monotonicity is assumed. Numerical frozen-flow and actual-Q
diagnostic flux remain distinct. Optional versioned strict-JSON checkpoints
detect corruption through content hashes, not measurement authenticity.

**IMPLEMENTED_QUALIFICATION_INCOMPLETE** under the fixed 28-integration
[contract](../analysis/model_pannusch2024_stateful_fv_004/CONTRACT.md) and
[matrix](../analysis/model_pannusch2024_stateful_fv_004/CASES.json).
All 28 integrations completed. Equilibrium, supplied-state/reference, continuation,
branching, inventory/flux/volume, positivity, mesh and repeat gates pass. The
mandatory temporal aggregate-decrease gate fails: the short
[2.737002188183808,2.74] s fraction has .04/.02/.01 errors
7.99e-5 / 2.03e-4 / 8.36e-5 on C*, despite each meeting 5e-4. No monotone
temporal-refinement claim is earned. [Results](../analysis/model_pannusch2024_stateful_fv_004/RESULTS.md).
The [offline N4 example](../../examples/pannusch_stateful_fv.py) demonstrates
equilibrium compatibility, nonequilibrium initial fields, genuine stop/resume,
and independent checkpoint reuse under a new future forcing plan.
This capability does not identify wetting chemistry, demonstrate empirical
predictive improvement, qualify arbitrary initial states, or authorize coupling,
production adoption, laboratory operation or a successor. No global shot-chain
contract or registry evidence level changes. The 001/002/003 ceilings remain.

## Conditional initial-state delivery envelopes (005)

`state_envelope` adds `FVChemicalStateSet`, reusable `FVDeliveryResponse`,
`bound_delivery`, direct shared-state `contrast_deliveries`, and explicit
`replay_extrema` operations over the unchanged discrete FV model. G0 /
NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. All existing runtime source and
parameter files remain byte-identical; application defaults and registry
evidence strength are unchanged. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The caller supplies all liquid/fine/coarse cell bounds in their source kg/m^3
bases, total and optional phase inventory intervals in kg, and an assumption
label. No initial state is inferred or supplied by default. The set intersects
these constraints on a fixed species, grind, source configuration, mesh and
absolute start. Fine capacity excludes phi_v2. Sparse transpose responses use
the original plan's frozen steps and direct partial-window rewards; volume
uses the prescribed flow integral. Concentration is kg/m^3, never percent TDS.
Scaled HiGHS extrema include checked original-coordinate primal/dual evidence,
both numerical gaps and reconstructed states. Primary witnesses receive fresh
unchanged forward replays, both plans from the identical contrast state.

The one declared synthetic matched-volume comparison is numerically qualified
as `NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET` at delta=1e-6 kg, while feasible
replayed witnesses support an opposite-sign reversal below that margin. Its
shared-state contrast enclosure is [-9.53471519e-8, 8.57447042e-7] kg.
The 28 planned plus four reserved correction response passes completed in
104.017 s (32/32 hard total). A scaling-underflow guard was corrected; declared
responses, extrema and primary witness identities repeat exactly. Whole-set temporal and inventory-preserving N400/N800 sensitivity
remain separate from fixed-operator arithmetic enclosures and physical accuracy.
Software QA, hosted CI and ordinary review are separate acceptance evidence;
see the [005 handoff](../analysis/model_pannusch2024_state_envelope_005/HANDOFF.md)
and [public API contract](../analysis/model_pannusch2024_state_envelope_005/README.md).
The historical 004 temporal-decrease failure and incomplete qualification stand.
No universally better profile, measured state recovery, physical validation,
taste claim, production adoption or successor follows.
Pannusch attribution and source-derived CC-BY-NC-3.0 remain separate from
first-party code licensing.

## Early-fraction-conditioned finite delivery (006)

`prefix_conditioned` adds a model-local set-valued inverse query: explicit
starting-state set U, one immutable prescribed Q/T plan, already specified early
fraction mass bands in kg, and one finite later fraction. `FVFractionObservation`,
`FVPrefixConditionedSet`, `condition_on_fractions`, `bound_future_delivery` and
`replay_conditioned_extrema` retain joint constraints, check outer LP bounds and
contradictions, and separately reconstruct/replay sufficient compatible witnesses.
The original forward dynamics, parameters, defaults and `state_envelope.py`
remain unchanged. No registry component, observation adapter or fitting is added.

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. Engineering response allowances
are not rigorous interval arithmetic, statistical confidence, continuum accuracy
or physical bounds. PHYSICAL_VALIDATION=NOT_ESTABLISHED. Compatibility, complete
extremum-gap qualification, informativeness and discretization sensitivity are
separate. No implicit equilibrium or coffee prior; no unique-state recovery.
Earlier empirical two-assay predictors already exist; no MASS-DELIVERY conclusion
is reversed. 004's IMPLEMENTED_QUALIFICATION_INCOMPLETE and temporal failure stand.
See the [006 public contract](../analysis/model_pannusch2024_prefix_conditioned_006/README.md)
and [pre-execution specification](../analysis/model_pannusch2024_prefix_conditioned_006/CONTRACT.md).
The synthetic representative and all four fixed operators qualify at epsilon
1e-9 kg: ENGINEERING_CAPABILITY_VERIFIED. The default finite-target interval is
[1.5496913443458448e-5, 2.4013808699025333e-5] kg, with complete minimum/maximum
gaps 1.0982634987804617e-12 and 1.5832919861519332e-12 kg. The N800 minimum
endpoint shifts about -7.13e-9 kg: discretization sensitivity remains separate,
with no continuum certificate. [Results](../analysis/model_pannusch2024_prefix_conditioned_006/RESULTS.md)
and [handoff](../analysis/model_pannusch2024_prefix_conditioned_006/HANDOFF.md)
separate final software QA, author review and hosted checks.
