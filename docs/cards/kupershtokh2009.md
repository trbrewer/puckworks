# Model card: kupershtokh2009 — arbitrary-EOS multiphase LBE (EDM forcing + combined potential-gradient approximation)

**Paper/thesis:** Kupershtokh, A.L., Medvedev, D.A., Karpov, D.I. (2009). On equations of state in a lattice Boltzmann method. *Computers and Mathematics with Applications* 58(5), 965–974. https://doi.org/10.1016/j.camwa.2009.02.024
**Stage(s):** flow, infiltration · **Kind:** calibration (method reference; no runtime candidate)
**Status:** proposed

## Scope and mechanism

Numerical-methods paper for single-component vapor–liquid multiphase lattice Boltzmann: how to embed an arbitrary equation of state (van der Waals, Carnahan–Starling, modified Kaplun–Meshalkin) into an isothermal LBE via a special-potential body force, how to discretize that force so the simulated coexistence curve matches the Maxwell rule, and how to apply body forces without relaxation-time artifacts (the exact difference method, EDM). Delivers stationary density ratios up to 10⁷–10⁹ with coexistence deviations < 0.4% and greatly reduced spurious interface currents. Zero coffee content; the registry-relevant value is that this is the self-contained forcing/EOS scheme a future pore-scale multiphase solver (for the unsaturated-wetting backlog hypothesis) would be built on — it is among the primary methods literature the wang2027 card deferred to.

## Governing equations

What would actually be implemented:

1. **LBE evolution** (Eq. 7): fₖ(x + eₖ, t + Δt) = fₖ(x, t) + Ωₖ + Δfₖ, BGK collision Ωₖ = (fₖᵉᑫ − fₖ)/τ (authors note EDM works for arbitrary collision operators, incl. MRT/TRT). Moments (Eq. 8): ρ = Σₖ fₖ, ρu = Σₖ cₖfₖ.
2. **EDM body-force term** (Eq. 10): Δfₖ = fₖᵉᑫ(ρ, u + Δu) − fₖᵉᑫ(ρ, u), with Δu = FΔt/ρ. Real fluid velocity at half-step: ρu = Σₖ cₖfₖ + FΔt/2 (unnumbered, after Eq. 10).
3. **Special-potential force** (Eq. 13, Zhang–Chen): F = −∇U, U = P(ρ, T) − ρθ, with kinetic temperature θ = (h/Δt)²/3 for D1Q3/D2Q9/D3Q19.
4. **Reduced-variable potential** (Eq. 14): Ũ = kP̃(ρ̃, T̃) − ρ̃θ̃, θ̃ = 1/3, unit-matching coefficient k = (P_c/ρ_c)(Δt²/h²). For h/Δt = 10³ m/s, k = 0.00915 for argon; O(0.01) for inert gases (the values used throughout the paper).
5. **Φ-function** (Eq. 15): Φ(ρ̃, T̃) = √(−Ũ(ρ̃, T̃)), so F = 2Φ∇Φ (Eq. 16).
6. **Combined (general) gradient approximation** (Eq. 21) — the paper's central deliverable:
   F = (1/αh)[ A Σₖ (Gₖ/G₁) Φ²(x + eₖ)eₖ + (1 − 2A) Φ(x) Σₖ (Gₖ/G₁) Φ(x + eₖ)eₖ ],
   which interpolates the mean-value approximation (Eq. 17, A = 0.5) and the local approximation (Eq. 19, A = 0). Lattice constants: α = 1 (D1Q3), 3/2 (D2Q9), 3 (D3Q19); diagonal weights Gₖ = G₁/4 (D2Q9), G₁/2 (D3Q19).
7. **EOS options** (reduced variables): vdW (Eq. 2) P̃ = 8ρ̃T̃/(3 − ρ̃) − 3ρ̃²; Carnahan–Starling (Eq. 3) P̃ = cρ̃T̃(1 + bρ̃ + (bρ̃)² − (bρ̃)³)/(1 − bρ̃)³ − aρ̃² with a = 3.852462257, b = 0.1304438842, c = 2.785855166 fixed by the critical-point conditions (Eq. 4); modified Kaplun–Meshalkin (Eq. 6) P̃ = cρ̃T̃(1 + d/(1/ρ̃ − b)) − aρ̃², with a = 1/(3 − c), b = 3 − c, d = (12c − 6c² + c³ − 8)/(c(3 − c)); c free, c = 8/3 recovers vdW, c = 2.78 best fits experimental coexistence data.

Nothing simplified away. Note the paper provides **no wetting/solid-boundary closure**: the drop-on-wall examples (Fig. 6) reference wetting angles but the fluid–solid interaction model is never written down — for the incomplete-wetting application it must be sourced elsewhere.

## Parameters

| symbol | value | units | source |
|---|---|---|---|
| A (combined approx., vdW EOS) | −0.152 | – | fitted (to Maxwell-rule coexistence) |
| A for C–S, mKM EOS | not provided ("depends only on the EOS used") | – | – |
| c (mKM EOS) | 2.78 | – | fitted (coexistence data, ref [18]) |
| a, b, c (C–S EOS) | 3.852462257 / 0.1304438842 / 2.785855166 | – | derived (critical-point conditions) |
| α; Gₖ/G₁ | 1, 3/2, 3; 1/4 (D2Q9), 1/2 (D3Q19) | lattice | nominal (lattice geometry) |
| k (unit matching) | 0.00915 (argon); 0.01 typical | – | nominal (P_c, ρ_c, h/Δt = 10³ m/s) |
| θ̃ | 1/3 | lattice | nominal |
| τ (demonstrations) | 0.55–0.9 | lattice | assumed |

## Calibration and validation offered by the source

All **verification-grade** (theory-vs-numerics), no experiment beyond EOS-vs-literature coexistence data:

- EOS realism (Fig. 1, vs Skripov–Faizullin data on Ar, O₂, CO, Cr, Ne, Xe, N₂, CH₄): liquid branch equally good for all three EOS; vapor branch mKM (c = 2.78) best, vdW worst. Qualitative figure comparison; no error norms given.
- EDM vs alternatives (Fig. 2, vdW at T̃ = 0.85): explicit-derivative and collision-operator-modification methods give τ-dependent vapor density (unphysical); Guo forcing is τ-independent but biased; EDM matches the Maxwell-rule value and is τ-independent.
- Coexistence with combined approximation (Fig. 3): A = −0.152 makes vdW simulation "virtually coincide" with theory; deviations < 0.4% for T̃ ≥ 0.4. Mean-value approx. unstable below T̃ ≈ 0.72; local approx. unstable below T̃ ≈ 0.45 with incorrect vapor branch.
- Stationary flat-interface density ratio: > 10⁷ (vdW, mKM), > 10⁹ (C–S).
- Surface tension (Table 1, vdW, T̃ = 0.4–0.8): Laplace-law and stress-integral methods agree within ~4% (e.g. 0.01494 vs 0.01555 at T̃ = 0.8); temperature scaling γ ∼ (1 − T̃)^1.48 vs theoretical 1.5.
- Spurious currents (Fig. 4): combined approximation lowest across EOS; ~10⁻⁴–10⁻³ lattice units at moderate T̃.
- Demonstrations (Figs. 5–7): cavitation, drop impact, Marangoni — qualitative only.

Honest self-limitation stated: vapor-phase sound speed c̃ₛ = √(k ∂P̃/∂ρ̃) becomes small, so only flows with u < c̃ₛh/Δt are reliable.

## Assumptions and validity range

- Isothermal, single-component fluid; no solute transport, no dissolution — a coffee application would need scalar-transport coupling from elsewhere.
- Athermal demonstrations at 2D (D2Q9); D3Q19 constants given but 3D untested here.
- A is EOS-specific and only tabulated for vdW; must be re-fitted per EOS.
- Static solid wetting not specified (see equations note); no contact-angle hysteresis, no dynamic wetting closure.
- Reduced-variable framework assumes a critical point mapping; hot water + dissolved coffee solids is a mixture whose effective EOS/σ is not addressed (surfactant-active species alter σ — outside scope).
- Low-Mach constraint from the vapor sound speed; stationary density-ratio claims (10⁷–10⁹) are flat-interface equilibrium results, not dynamic-flow guarantees.
- Silent on porous/random geometry, polydisperse grains, swelling solids — all central to coffee beds.

## Interface mapping

Inputs consumed: none of the v0.1 contracts. A pore-scale wetting study would take geometry from brewer2026.pack_generator voxel fields and fluid properties external to the registry.
Outputs produced: nothing writing to BedState/ShotResultState directly. Plausible offline product: wetting/invasion regime maps informing the tubes-at-k→0 atom in brewer2026.streamtube, or a test of foster2025.infiltration's sharp-front assumption.
Couplings: offline calibration chain only. Implementation path would extend brewer2026.lb_reference/lb_taichi (single-phase TRT) — EDM is collision-operator-agnostic, so the TRT core is reusable; additions are the Φ field, the Eq. 21 force stencil, an EOS module, and a wetting boundary sourced from other literature. That is a solver extension, not an adapter.

## Extractable data

- Table 1 (γ_L, γ_s vs T̃ for vdW): worth inline transcription in this card only (done above, 5 points × 2 methods) — these are verification targets for a future gate, not physical data.
- Closure constants (A = −0.152; C–S a,b,c; mKM relations, c = 2.78): captured above; these are the reusable content.
- No raw data or code published; nothing warrants a puckworks/data/ file.

## Overlaps and conflicts

- **wang2027 (skipped)**: this paper is precisely the "primary methods literature" that card deferred to — it publishes the closures wang2027 omits (force stencil weights, A, EOS constants) with a simpler (BGK/any) collision operator. Supersedes wang2027 as the method reference of record for the multiphase-LB contingency; the wang2027 skip verdict stands unchanged.
- **brewer2026.lb_reference / lb_taichi (flow, calibration)**: complementary — same numerical family, and EDM's collision-operator independence means the registered TRT kernels are the natural host. No conflict.
- **foster2025.infiltration (infiltration, runtime)**: a future solver built on this scheme could test its sharp-front assumption at pore scale. Complement, far downstream.
- **Backlog "unsaturated flow at fine grinds"**: this is the designated on-ramp if that hypothesis graduates to pore-scale simulation. It does not itself address the hypothesis.
- Competes with nothing registered.

## Implementation estimate

Not implementable now as a registry component (no coffee-relevant observable, no contract it writes). If the unsaturated-wetting hypothesis graduates: extending lb_reference with EDM + Eq. 21 + one EOS is effort M, with clean verification gates directly from this paper (Maxwell-rule coexistence at T̃ = 0.85 vs Fig. 2/3; Table 1 surface tensions; spurious-current levels vs Fig. 4; A re-fit per EOS). The full track to a coffee-relevant result (wetting boundary from external literature, σ/θ calibration for hot water on coffee solids — no contact-angle data in the registry — plus 3D porous geometry) is effort L. Gate design is unusually easy because the paper's verification numbers are explicit.

VERDICT: implement-later — self-contained, closure-complete multiphase-LB forcing/EOS scheme that is the designated method-of-record for the unsaturated-wetting contingency, but has no registry deliverable until that hypothesis graduates — effort M (scheme atop lb_reference) / L (coffee-relevant application)
