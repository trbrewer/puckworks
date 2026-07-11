# Model card: Wadsworth 2026 inertial permeability / Forchheimer closure

**Paper:** Wadsworth et al., R. Soc. Open Sci. 13, 252031 (2026). DOI 10.1098/rsos.252031 (§2.1, §2.4, §5.3, fig. 8)
**Stage(s):** flow · **Kind:** runtime (Forchheimer correction to Darcy in the shot chain; γ constants are an offline calibration import)
**Status:** card-only

## Scope and mechanism
Extends Darcy flow through the puck with the Forchheimer inertial term, closed by an
empirical constitutive law k_I(k) relating inertial permeability to Darcian permeability.
The closure is claimed microstructure-agnostic: the k–k_I covariance collapses across
sintered materials, porous ceramics, and other media, so a ceramics-calibrated fit is
argued transferable to coffee. A dimensionless friction factor f and Forchheimer number
Fo diagnose when inertia matters; the authors estimate espresso sits in the laminar
regime but close to the inertial onset. This is a distinct, separable sub-model of the
paper — the core percolation permeability k(⟨R⟩, φ_p) is already registered and gated
as wadsworth2026.permeability.

## Governing equations
1. Forchheimer momentum law (their eq. 2.1):
   ∇p = −(μ/k) q − (ρ/k_I) |q| q
   ∇p pressure gradient [Pa m⁻¹]; μ fluid viscosity [Pa s]; ρ fluid density [kg m⁻³];
   q Darcy velocity [m s⁻¹]; k permeability [m²]; k_I inertial permeability [m].
   Darcy's law is the special case with the second RHS term dropped.
2. Adopted k_I closure (their eq. 2.8, ceramics fit; preferred by the authors for the
   shape of the k–k_I covariance):
   k_I = exp(γ₂ k^τ), with k in m² and k_I in m (parameters carry hidden units — the
   expression is not dimensionally clean; implement with strict SI inputs).
3. Alternative closure (their eq. 2.7, Zhou et al. power law; captures the range but
   not the curvature): k_I = γ₁ k^(τ′/2), dataset bounded by 10⁷ ≤ γ₁ ≤ 10¹³ m^(1−τ′).
4. Ergun-derived form (their §2.4, NOT adopted): k_I = 2⟨R⟩φ³ / (γ₃(1−φ)), γ₃ = 1.75;
   they reformulate it as k_I ∝ k^(1/2) φ^(3/2) but reject it as hard to validate due
   to the residual φ dependence.
5. Dimensionless diagnostics (their eqs. 5.2a,b): f ≡ ∇p·k_I/(ρq²), Fo ≡ ρkq/(μk_I),
   with the model curve f = 1/Fo + 1 (Darcy-only: f = 1/Fo). Inertia matters where the
   two curves separate, i.e. Fo approaching O(0.1–1).
Implementation = given k and ∇p, compute k_I from (2), then solve the scalar quadratic
(ρ/k_I)q² + (μ/k)q − |∇p| = 0 for q; report Fo as a regime flag.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| γ₂ | −1.71588 | — (k in m²) | fitted (ceramics compilation, their ref. [32]) |
| τ | −0.08093 | — | fitted (same dataset) |
| γ₁ | 10¹⁰ (best fit) | m^(1−τ′) | fitted (Zhou et al. cross-media compilation) |
| τ′ | 3 | — | fitted (same) |
| γ₃ (Ergun) | 1.75 | — | nominal (Ergun 1952) |
| μ (water, 92 °C) | 3 × 10⁻⁴ | Pa s | nominal |
| ρ (water, 92 °C) | 960 | kg m⁻³ | nominal |

## Calibration and validation offered by the source
- No new k_I measurement in this paper: their own LB simulations are deliberately run
  at Re 1.4×10⁻⁷–2.5×10⁻⁶ and cannot probe inertia; LBflow is stated as untested in
  the inertial regime.
- Validation is a graphical compilation (fig. 8a) of published k–k_I pairs (sintered
  materials, ceramics, other media) plus coffee points from Mo et al. 2023 (their ref.
  [14]) that fall within the same trend. Eq. 2.8 traces the covariance shape; eq. 2.7's
  band covers the scatter. No fit statistics are reported.
- Worked espresso estimate: G 1–4 (⟨R⟩ 145–276 µm), 38–42 g out in 27–32 s, R_g = 29 mm
  basket, φ_p 0.3–0.5, k from their eq. 5.3 → q = 5.36–5.74 × 10⁻⁴ m s⁻¹ and
  0.0161 ≤ Fo ≤ 0.0639: laminar, but "very close to the inertial regime". This is a
  model-chained estimate, not a measurement.

## Assumptions and validity range
- Assumes k_I(k) is independent of pore microstructure; asserted from cross-media
  collapse, never calibrated on coffee by these authors.
- Eq. 2.8 was fitted on ceramics whose k range is far wider than tamped-coffee k
  (~10⁻¹³–10⁻¹² m²); coffee sits inside the compiled band (fig. 8a) but at one edge of
  the fit's support — extrapolation risk is modest but nonzero.
- Dimensional inconsistency of exp(γ₂k^τ): valid only with k in m²; unit slips are a
  silent failure mode.
- Steady incompressible single-phase flow; silent on unsteady preinfusion transients,
  two-phase/degassing flow, and channel-localized jets where local Re can exceed the
  bed-average estimate.
- Regime conclusion depends on φ_p and grind assumptions; finer grinds/tighter packs
  at fixed target flow push Fo up (their own caveat).

## Interface mapping
Inputs consumed: BedState.k (or kappa via adapter), MachineState.P_of_t (→ ∇p with bed
depth), fluid μ, ρ (temperature nominal). Outputs produced: q(t) (hence flow trace in
ShotResultState.traces), Fo(t) diagnostic. Coupling: runtime replacement/wrapper for the
Darcy step in the flow stage; γ constants imported as calibration data. Adapter needed
from the DE1/Cameron kappa convention to SI k [m²] before computing k_I.

## Extractable data
- Fig. 8a k–k_I compilation is digitizable and the underlying sources are cited
  individually (their refs. [11,14,32,65–78]) — worth transcribing the Mo et al. coffee
  points at minimum into data/.
- The espresso Fo band (0.0161–0.0639) with its full input list is a ready-made gate
  target. Paper's processed data zip (permeability + PSD) is published open-access.

## Overlaps and conflicts
- Directly fills the open backlog item "flow: Forchheimer/inertial correction (gusher
  regime)". Conflict to resolve: the backlog estimates Fo ~ 0.3–0.9 at Cameron bed
  density, an order of magnitude above this paper's 0.016–0.064 band — different k and
  φ_p assumptions (their eq. 5.3 chain vs Cameron flux-table k). Discriminate by
  computing Fo along the DE1 fixture A traces with the fitted kappa = 1.196.
- Complements wadsworth2026.permeability (supplies k) and brewer2026.lb_reference /
  lb_taichi (both Stokes-regime; this component covers what they explicitly cannot).
- Complements cameron2020.extraction_bdf: modifies the flow law upstream of extraction;
  no contract change needed beyond the flow stage.

## Implementation estimate
Small: one closed-form closure + one scalar quadratic + Fo diagnostic; no new state.
Gate design: (i) reproduce their Fo band from their stated inputs; (ii) verify Darcy
limit recovery as k_I → ∞; (iii) recompute Fo on DE1 fixture A and adjudicate the
backlog's gusher-regime estimate. Dependencies: wadsworth2026.permeability or fitted
kappa; kappa→k unit adapter.

VERDICT: implement-now — closed-form, cheap, fills a named backlog slot, and settles the registry's own Fo-regime disagreement against real DE1 traces — effort S
