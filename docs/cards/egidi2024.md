# Model card: Egidi 2024 ADR extraction (RBF collocation)

**Paper:** Egidi, Giacomini, Larsson, Perticarini, "An improved numerical scheme for coffee Extraction Yield evaluation," Chaos, Solitons and Fractals 188, 115625 (2024). DOI 10.1016/j.chaos.2024.115625
**Stage(s):** extraction · **Kind:** runtime
**Status:** card-only

## Scope and mechanism
1D saturated two-population (fines/boulders) espresso extraction: liquid-phase
advection–diffusion along the bed axis, coupled at every depth level to
spherical intra-grain diffusion in each grain class, with a nonlinear surface
dissolution term transferring solubles to the liquid. Imbibition is explicitly
discarded (bed starts fully wet); Darcy flux q is a prescribed constant, not
computed from pressure/permeability. One lumped chemical species. The paper's
actual novelty is numerical, not physical: a polynomial-augmented polyharmonic
(r³, p = 3) RBF collocation replacing the finite differences of Egidi 2022
[their ref 10], with Crank–Nicolson time stepping and a nested fixed-point
iteration for the nonlinear coupling. The physical model is the same lineage as
Cameron 2020 [their ref 9] and Egidi/Giacomini 2022 [refs 10, 11].

## Governing equations
Liquid phase, their Eq. (1), z ∈ (0, L), t ∈ (0, τ):
1. (1 − φ) ∂c_l/∂t − D ∂²c_l/∂z² + q ∂c_l/∂z = b_f G_f + b_b G_b
   BCs: −D ∂c_l/∂z(0,t) + q c_l(0,t) = 0 (no soluble flux at inlet);
   −D ∂c_l/∂z(L,t) = 0 (no diffusive flux at outlet); IC c_l(z,0) = 0.
   φ = φ_f + φ_b, with φ_s = b_s a_s³ (b_s the BET parameters, s = f, b).

Solid phase per grain class s = f, b at each z, their Eq. (2), r ∈ (0, a_s):
2. ∂c_s/∂t = (D_g/r²) ∂/∂r (r² ∂c_s/∂r)
   BCs: symmetry at r = 0 (De L'Hôpital limit 3 D_g ∂²c_s/∂r² used at r = 0);
   −D_g ∂c_s/∂r(a_s, z, t) = G_s(z,t); IC c_s(r,z,0) = c_0.

Coupling (dissolution), their Eq. (3):
3. G_s = k_r · c_s(a_s,z,t) · max(c_s(a_s,z,t) − c_l(z,t), 0) · max(c_sat − c_l(z,t), 0)
   In the scheme, max(x,0) is replaced by the smooth f_α(x) of their Eq. (22),
   α = 0.1. Note G_s is quadratic in surface concentration (hence k_r in
   m⁷/kg²) — a different kinetic form than Cameron's first-order-in-deficit law.

Observable, their Eq. (4):
4. EY = q/(φ_s ρ L) · ∫₀^τ c_l(L,t) dt
   (trapezoidal quadrature). Symbol φ_s in Eq. (4) is not defined at that
   point in the paper; from ref [10]'s derivation it should be the total solid
   fraction φ. Flagged, not resolved here.

Symbols: c_l liquid concentration [kg/m³]; c_s solid concentration in class s;
φ solid volume fraction; q Darcy flux [m/s]; D effective liquid diffusivity;
D_g intra-grain diffusivity (size-independent by assumption); a_f, a_b fine
and boulder radii; k_r reaction rate; c_sat saturation concentration; ρ grain
density; L bed depth; τ shot time.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| φ | 0.8272 | – | nominal (from refs [9,10,12]; fixed across grinds) |
| c_0 | 200 | kg/m³ | nominal (from refs [9,10]) |
| c_sat | 212.4 | kg/m³ | nominal (from refs [9,10]) |
| D | 1.0e−8 | m²/s | nominal (from refs [9,10]) |
| D_g | 6.25e−10 | m²/s | nominal (from refs [9,10]) |
| k_r | 6.0e−9 | m⁷/kg² | nominal (from refs [9,10]) |
| ρ | not provided | kg/m³ | — (needed by Eq. 4; not stated in paper) |
| a_f | 15.5 / 16.6 / 15.6 | μm | measured (laser diffraction, Table 3; fine/optimal/coarse) |
| a_b | 200.0 / 227.0 / 227.0 | μm | measured (Table 3) |
| φ_f | 0.24 / 0.22 / 0.20 | – | measured (fraction of φ, Table 3) |
| q | 3 / 4.5 / 5.3 ×10⁻⁴ | m/s | derived from lab flow (fixed 1:2 brew ratio; Table 3) |
| τ | 40 / 26 / 20 | s | measured (mean shot times, Tables 1–2) |
| L | 13.27 / 13.00 / 14.20 | mm | measured (tamped bed height, Table 1) |
| α | 0.1 | kg/m³ | assumed (smoothing of max) |
| basket | r = 29.25 mm, h = 26 mm, dose 20 g | – | measured (VST Competition) |

## Calibration and validation offered by the source
Lab campaign (from ref [10], summarized here): Modœtia Arabica, 36 shots =
3 grinds × 2 pressures (6, 9 bar) × 2 temperatures (90.4, 93.4 °C) × 3
replicates, dose 20 g, beverage 40 g, EY via refractometer TDS / brew ratio.
Validation claim: the simulated mean EY per grind falls inside the lab EY
range per grind (Table 4): fine 22.53 vs 22.07–22.58; optimal 20.44 vs
20.43–20.87; coarse 19.30 vs 19.09–20.11. That is three scalar comparisons
against ranges of width 0.4–1.0 pt, with all physico-chemical parameters
inherited from prior work and q, τ, L, a_s, φ_f set per grind from
measurement. Pressure and temperature never enter the model explicitly — they
are absorbed into q and τ — so the 12-condition structure of the data is not
actually predicted, only the grind-averaged EY. Authors themselves call the
validation "preliminary". Convergence evidence: Table 5 varies only N
(50/80/100 → EY 19.56/19.34/19.30, coarse); M^f, M^b, h_t not varied. No
positivity/mass-conservation proof for this scheme (the FD scheme of ref [10]
had one); positivity here is maintained by ad-hoc relaxation (ω_l, ω_s
schedules) at early time steps. Note Table 5's "experimental range" column
appears mislabeled (repeats all three grind ranges).

## Assumptions and validity range
- Fully wet bed at t = 0; imbibition discarded (no first-drip transient).
- q constant in z and t, prescribed — no pressure or permeability coupling;
  cannot represent flow decline/rise, channeling, or profile shots.
- Single lumped species; c_sat cap on dissolution.
- Two monodisperse spherical grain classes; D_g size-independent.
- φ fixed at 0.8272 for all grinds even though φ_f varies — internal tension.
- No temperature dependence anywhere in the equations.
- Validated only at: 20 g dose, VST basket, 1:2 ratio, τ = 18–42 s, EY 19–23%.
  Silent on: gushers, chokes, very fine grinds (unsaturated flow), long-ratio
  lungos, temperature/pressure extrapolation.
- Numerics: dense PA-RBF differentiation matrices; ill-conditioning grows with
  node count (authors note preconditioning needed at scale); nested fixed-point
  with maxit 500 — more expensive than the FD version by their own account.

## Interface mapping
Inputs consumed: GrindState (a_f ↔ fines radius, a_b ↔ boulder radius,
fines_fraction ↔ φ_f), BedState (depth_m ↔ L, porosity ↔ 1−φ, area — for q
from flow), MachineState only degenerately (q must be supplied; no P(t) use).
Outputs produced: ShotResultState.EY_pct (+ c_l(L,t) trace → tds trace).
Coupling: runtime extraction component, same slot as cameron2020.extraction_bdf.
Adapter needed to convert our BedState/MachineState → constant q (or to feed a
flow-stage q(t), which the model as published does not support). The RBF
discretisation is an implementation choice, not a contract concern.

## Extractable data
- Table 2 → data/egidi2024_ey_tds.csv: 12 conditions (T × p × grind) with TDS
  mean, σ, and EY. Genuinely useful gate data for the extraction stage —
  independent of Cameron's dataset, different machine/coffee/basket. **Highest
  value in the paper.**
- Table 1 + Table 3 → same csv or companion: L, τ, a_f, a_b, φ_f, q per grind.
- Fig. 2 (PSD, bimodal, minimum ~100 μm) — digitizable if needed for the grind
  backlog; low priority.
- Code: not published. "Data are contained in the article" (no repository).

## Overlaps and conflicts
- **cameron2020.extraction_bdf (competes):** same stage, same model family.
  Differences: per-grain-volume inventory c_0 = 200 kg/m³ with c_sat cap
  (vs Cameron's per-bed-volume 118/φ_s, EY ceiling 29.6%); quadratic-in-surface
  dissolution kinetics (3) vs Cameron's law; prescribed constant q vs Cameron's
  flux table. Lower coupling fidelity than our registered component; no reason
  to swap runtimes. The kinetic form is worth remembering as a competing
  dissolution closure if extraction-gate residuals point at kinetics.
- **foster2025.infiltration (complements/conflicts):** this model assumes away
  exactly what Foster models; the infiltration↔extraction coupling backlog item
  would supersede this paper's t = 0 wet-bed assumption.
- **Backlog "multi-class solute chemistry":** not here, but their ref [11]
  (Giacomini 2022, J Math Chem) generalises this model to multiple species —
  better intake candidate for that backlog slot.
- **wadsworth2026.permeability / flow backlog:** no conflict; this model simply
  ignores permeability (q prescribed), which is its main fidelity gap.

## Implementation estimate
As a runtime component: M (RBF machinery or a re-discretisation, nonlinear
relaxation tuning, adapter for q) — and it would duplicate cameron2020 at
lower coupling fidelity. As data intake: S (transcribe Tables 1–3, add an
extraction-gate case: given Table 3 inputs, does our chain land in Table 2's
EY ranges?). Gate design: per-grind EY range bracketing, mirroring Table 4.

VERDICT: data-only — the physics duplicates cameron2020 at lower coupling fidelity (prescribed q, preliminary 3-point validation), but Table 2's 12-condition EY/TDS campaign is an independent, transcribable gate dataset for the extraction stage — effort S
