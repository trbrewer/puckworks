# Model card: kusumaatmaja2010 — free-energy binary-fluid LB with wetting boundary conditions (MRT + Bouzidi bounce-back)

**Paper/thesis:** Kusumaatmaja, H., Yeomans, J.M. "Lattice Boltzmann simulations of wetting and drop dynamics." Book chapter (Springer; appears in the cellular-automata simulation volume ed. Kroc/Sloot/Hoekstra, ~2010). No DOI in the provided copy; latest cited references are 2008, so the year tag "2010" is nominal — verify on registration.
**Stage(s):** infiltration, flow · **Kind:** calibration (method reference; no runtime candidate)
**Status:** proposed

## Scope and mechanism

Tutorial/review chapter presenting one coherent numerical model: a **binary-fluid (liquid–liquid) free-energy lattice Boltzmann method** for wetting and drop dynamics. A Landau φ⁴ free energy gives phase coexistence, a diffuse interface of tunable width, surface tension, and — via a Cahn surface-energy term — an equilibrium contact angle set by a single boundary parameter h. Hydrodynamics (continuity + Navier–Stokes + convection–diffusion for the order parameter) is solved with a D3Q19 LB scheme, upgraded to multiple-relaxation-time (MRT) collisions for viscosity-contrast stability, with Bouzidi interpolated bounce-back for no-slip on off-lattice walls and two explicit discrete implementations of the wetting boundary condition. Applications shown (capillary filling vs Lucas–Washburn, Saffman–Taylor fingering, drops on chemically striped surfaces, Cassie–Baxter/Wenzel states, contact-angle hysteresis, collapse transitions) are demonstrations of the one method, not separable models — hence a single card. Zero coffee content; registry value is that this chapter publishes, closure-complete, the **wetting/solid-boundary machinery that the kupershtokh2009 card explicitly flags as missing** from the pseudopotential route.

## Governing equations

What would actually be implemented (source equation numbers in parentheses):

1. **Free energy** (2): Ψ = ∫_V [ψ_b + (κ/2)(∂_α φ)²] dV + ∫_S ψ_s dS, with bulk density (3) ψ_b = (c²/3) n ln n + A(−φ²/2 + φ⁴/4). n = fluid density (set to 1 everywhere), φ = order parameter (bulk phases φ = ±1), c = Δx/Δt, κ = gradient-energy coefficient, A = bulk energy scale.
2. **Chemical potential** (4): μ = −Aφ + Aφ³ − κ d²φ/dx²; equilibrium 1D interface (5) φ = tanh(x/√2ξ), interface width ξ = √(κ/A); fluid–fluid surface tension (8) γ = √(8κA/9).
3. **Wetting boundary condition** (Cahn): surface energy ψ_s = −hφ_s; minimisation gives (9) κ dφ/dx|_surface = −h. Fluid–solid tensions (10, 11) γ_{sα,sβ} = γ/2 − (γ/2)(1 ± Ω)^{3/2}, Ω = h√(2/(κA)). Contact angle (12): cos θ_e = [(1+Ω)^{3/2} − (1−Ω)^{3/2}]/2, inverted (13): h = √(2κA) · sign(π/2 − θ_e) · √(cos(α/3)[1 − cos(α/3)]), α = cos⁻¹(sin²θ_e). This h(θ_e) map is the reusable closure; spatially varying h implements chemical patterning (validity requires patterning length scale > interface width).
4. **Hydrodynamics** (14–16): ∂_t n + ∂_α(nv_α) = 0; ∂_t(nv_α) + ∂_β(nv_α v_β) = −∂_β P_αβ + ∂_β[nν(∂_β v_α + ∂_α v_β) + nλ δ_αβ ∂_γ v_γ] + na_α; ∂_t φ + ∂_α(φv_α) = M∇²μ. ν = shear kinematic viscosity, λ per (32), a = body-force acceleration, M = mobility (controls contact-line slip via interfacial diffusion — the singularity relief mechanism in this model class).
5. **Pressure tensor** (18, 19): P_αβ = (p_b − (κ/2)(∂_γφ)² − κφ∂_γγφ)δ_αβ + κ(∂_αφ)(∂_βφ), p_b = (c²/3)n + A(−φ²/2 + 3φ⁴/4); c_s² = c²/3.
6. **LB scheme** (20–22): D3Q19 velocity set; two distributions f_i (mass/momentum) and g_i (order parameter); moments (21) n = Σf_i, nu_α = Σf_i e_iα, φ = Σg_i, with u = v − aΔt/2. BGK collide-and-stream (22) with relaxation times τ, τ_φ; equilibrium constraints (23–29); explicit f_i^eq, g_i^eq, F_i expansions (30) with the Pooley–Furtado spurious-velocity-minimising weights w_i, w_i^{xx…zx} (tabulated in full in the chapter). Transport coefficients (31–33): ν = c²Δt(τ − ½)/3; λ = ν(1 − 3c_s²/c²); M = ΔtΓ(τ_φ − ½), Γ tunable.
7. **MRT collision** (34–36): replace (1/τ)[f − f^eq] with M⁻¹SM[f − f^eq]; 19×19 orthogonal moment matrix M given in full; S = diag(0,1,1,0,1,0,1,0,1,ω,1,ω,1,ω,ω,ω,1,1,1) with ω = 1/τ on the five viscous-stress modes, ghost modes relaxed at 1, conserved modes 0. Required because BGK accuracy degrades away from τ = 1 (spurious contact-point velocities), which precludes viscosity contrast.
8. **No-slip wall** (37, Bouzidi): d_wall < 0.5: f₁*[k] = 2d_wall f₂[k] + (1 − 2d_wall) f₂[k+1]; d_wall > 0.5: f₁*[k] = f₂[k]/(2d_wall) + (1 − 1/(2d_wall)) f₁[k]; moving-wall Δf, Δg correction terms given (unnumbered). Second-order accurate (Ginzburg–d'Humières).
9. **Discrete wetting BC** (38 or 39): either set ∂φ/∂z|₀ from (9) and ∂²φ/∂z²|₀ = 2(φ₅ − φ₀ − ∂φ/∂z|₀) without solid nodes (38), or assign ghost solid-node values φ₆ = φ₅ − 2∂φ/∂z|₀ (39, allows uniform bulk stencils). Five-step per-timestep algorithm for viscosity-contrast contact lines summarised at end of §4.2.
10. **Analytics used as validation targets** (not implemented, but gate material): Lucas–Washburn (42) l = (σ_LG h cos θ^a/3η)^{1/2}(t + t₀)^{1/2} and its two-viscosity correction (43) η_A l²/2 + η_B(Ll − l²/2) = σ_LG h cos θ^a (t + t₀)/6; Cox-type dynamic angle (44) cos θ^a = cos θ_eq − Ca·log(KL/l_s); Cassie–Baxter (45) cos θ_CB = Φ cos θ_e − (1 − Φ); Wenzel (46) cos θ_W = r cos θ_e; Gibbs pinning criteria θ^a = θ_e + α, θ^r = θ_e − α.

Nothing simplified away. Note: n ≡ 1 — this is a **density-matched** binary model; buoyancy and liquid–gas density contrast are outside the formulation (viscosity contrast is handled, density contrast is not).

## Parameters

| symbol | value | units | source |
|---|---|---|---|
| A, κ | not provided as numbers (set γ, ξ via γ = √(8κA/9), ξ = √(κ/A)) | lattice | nominal (user-chosen) |
| h | from θ_e via Eq. (13) | lattice | derived closure |
| w_i, w_i^{xx…zx} | full tables given (§4, after Eq. 30) | – | nominal (Pooley–Furtado, spurious-current minimising) |
| MRT M, S | given in full (Eqs. 34–36) | – | nominal (d'Humières basis) |
| τ, τ_φ | > 1/2 (stability); τ = 1 for BGK demos | lattice | assumed |
| Capillary-filling demo: L, h_channel | 640, 50 | lattice | assumed |
| θ_e (demo) | 60 | ° | assumed |
| γ (demo) | 0.0188 | lattice | assumed |
| η_A, η_B (demo) | 0.83, 0.03 | lattice | assumed |
| M (mobility, demo) | 0.05 / 0.1 / 0.25 / 0.5 | lattice | assumed (sweep) |
| θ^a extrapolated at Ca→0 | 58 / 60 / 60 (M = 0.05/0.1/0.5) | ° | measured (from their own simulation) |
| Striped-surface demo | θ = 5° and 64°, widths 26 and 47 μm | mixed | measured (matched to Léopoldès expt) |
| Hysteresis demo | post width 7, spacing 13, θ_e = 120° | lattice | assumed |
| Superhydrophobic demo | θ_e = 110°; results 156° (suspended), 130° (collapsed) | ° | measured (simulation) |

Unit mapping: three scales (L_o, T_o, M_o) fixed by matching L, η, γ to experiment; body force then follows — the chapter is explicit that simulation parameters cannot be matched arbitrarily.

## Calibration and validation offered by the source

Mostly **verification-grade**, with two qualitative experimental comparisons:

- **Equilibrium contact angle vs theory** (Fig. 2, at τ = 1): simulated θ_e vs boundary gradient sits on the Eq. (13) curve; deviation only at small angles (interface width ≈ drop height). No error norm given. Authors state agreement degrades for τ ≠ 1 under BGK — the motivation for MRT.
- **Capillary filling vs Lucas–Washburn** (Fig. 5a): "excellent" fit to Eq. (43) using the *measured advancing angle* (not θ_e) and the displaced-fluid viscosity correction; deviations only at early time (inertia, non-Poiseuille entry). Note the circularity flag: the fit uses the simulation's own measured θ^a, so this validates internal consistency with Washburn scaling, not prediction.
- **Dynamic contact angle** (Fig. 5b): cos θ^a linear in Ca per Eq. (44); θ^a → θ_e as Ca → 0 (58–60° vs 60° set). Slope (slip length) depends on mobility M — an honest statement that contact-line dynamics is regularised by a numerical/model parameter.
- **Chemically striped surface vs experiment** (Fig. 8, Léopoldès 2003): simulation with matched physical parameters reproduces the experimentally observed diamond and butterfly final morphologies and their selection by impact position. Morphological/qualitative; no quantitative shape metric.
- **Inkjet mottle control vs experiment** (Fig. 9, Dupuis 2005): hydrophobic-grid confinement effect reproduced; qualitative.
- **Hysteresis vs Gibbs-criterion analytics** (Fig. 14): receding depin at θ^r ≈ 120° = θ_e (suspended) and 32° vs predicted 30° (collapsed); advancing line stays pinned to ≥ 162° without depinning (analytic θ^a = 180°). Verification against their own analytic pinning argument.
- **Cassie–Baxter/Wenzel** (Fig. 12): 156°/130° simulated vs formulae — "compatible but not exactly the same," attributed to few-post coverage and metastability; honest.

No validation in any porous-medium, imbibition-into-random-geometry, or liquid–gas configuration.

## Assumptions and validity range

- **Density-matched binary fluid (n = 1)**: no liquid–gas density ratio, no buoyancy, no inertial density asymmetry. Hot water invading an air-filled coffee bed is a liquid–gas problem; only viscosity contrast (up to ~10³ via MRT) is representable. Their own footnote 6 warns that the one-component liquid–gas variant used for some demos exhibits unphysical contact-line dynamics from evaporation–condensation across the artificially wide interface.
- Diffuse interface of a few lattice spacings: chemical-patterning length scales must exceed the interface width; small-drop / small-angle results degrade when ξ ≈ feature size.
- Contact-line slip is diffusion-controlled via mobility M — slip length is a tunable numerical parameter, not a measured physical closure; dynamic-angle predictions inherit this.
- Isothermal; no solute transport, dissolution, or Marangoni effects (surfactant-active coffee species out of scope); no thermal fluctuations (chapter lists this as an open problem).
- No contact-angle hysteresis model beyond geometric pinning on resolved topography; smooth-surface hysteresis (chemical disorder) not treated.
- Silent on: random/polydisperse porous geometry (chapter asserts LB suits porous media but demonstrates none), swelling/deformable solids, trapped-gas compression during imbibition, gravity-driven drainage.
- Spurious velocities are acknowledged, minimised (weight choice, MRT ghost relaxation, τ = 1 damping) but not eliminated; strongest near interfaces/contact points.
- All demo parameters are lattice units; nothing transfers numerically to coffee conditions without the L_o/T_o/M_o matching procedure.

## Interface mapping

Inputs consumed: none of the v0.1 contracts. A pore-scale wetting study would take voxel geometry from brewer2026.pack_generator and fluid properties (η(T), σ, θ_e for hot water on coffee solids — the last not held anywhere in the registry).
Outputs produced: nothing writing BedState/ShotResultState. Plausible offline products: (i) pore-scale test of foster2025.infiltration's sharp-front assumption (the chapter's capillary-filling physics is exactly the channel-level Lucas–Washburn ingredient underlying Foster's continuum front); (ii) wetting/invasion regime maps feeding the tubes-at-k→0 atom in brewer2026.streamtube (unsaturated-flow backlog).
Couplings: offline calibration chain only. Implementation would extend brewer2026.lb_reference/lb_taichi: the D3Q19 lattice is shared, but this route replaces the collision content (MRT with the given M, S), adds a second distribution g_i, the φ machinery in f^eq (Eq. 30 with the special weights), Bouzidi walls, and the Eq. (9/38/39) wetting BC. Solver extension, not an adapter. **Route note:** this is the *binary free-energy* alternative to the kupershtokh2009 *pseudopotential/EOS* route; the two are competing method choices for the same contingency, and this chapter's Cahn-type wetting BC is the missing piece of the kupershtokh package (transferable in spirit, though Eqs. (9), (13) are specific to the φ⁴ functional).

## Extractable data

- Closure content worth keeping: h(θ_e) relation (13); Pooley–Furtado weight tables; MRT M and S matrices; Bouzidi rules (37); wetting-BC discretisations (38, 39); five-step algorithm. All transcribed/summarised above — this card is the artifact; no puckworks/data/ file warranted.
- Fig. 5 (filling length vs time; cos θ^a vs Ca) and Fig. 14 (hysteresis) are verification targets for a future gate, but they are lattice-unit results readable from the derived laws (42–44); digitisation unnecessary.
- No raw data or code published. Primary sources for gate-grade numbers: Pooley–Kusumaatmaja–Yeomans PRE 78:056709 (2008) (MRT wetting accuracy) and Kusumaatmaja–Pooley–Girardo–Pisignano–Yeomans PRE 77:067301 (2008) (capillary filling) — acquire those if this route graduates.

## Overlaps and conflicts

- **kupershtokh2009 (implement-later, flow/infiltration)**: competing method route (free-energy binary vs pseudopotential single-component liquid–gas) for the same unsaturated-wetting contingency. Complementary in content: this chapter supplies the wetting boundary closure and MRT/bounce-back machinery kupershtokh omits; kupershtokh supplies the realistic liquid–gas EOS and density ratio this chapter cannot represent (n ≡ 1). If the contingency graduates, the route decision is: density-matched binary + rigorous wetting BC (this) vs high-density-ratio EOS + externally sourced wetting BC (kupershtokh). Neither supersedes the other; register both as method references.
- **wang2027 (skip)**: this chapter is closure-complete where wang2027 was not (full MRT matrices, weights, wetting BC published here), and it carries the same "wrong regime, method-only" caveat. The wang2027 skip stands; this chapter partially fills the "go to the primary methods literature" pointer in that verdict.
- **brewer2026.lb_reference / lb_taichi (flow, calibration)**: same D3Q19 family; natural host code. The MRT machinery here is a superset of TRT — adopting it is a collision-operator change, documented fully in this chapter. Complement.
- **foster2025.infiltration (infiltration, runtime)**: same physical stage at continuum scale; this chapter's Lucas–Washburn analysis (Eqs. 40–43, with advancing-angle and displaced-fluid corrections) is the channel-scale physics under Foster's front model. A future pore-scale study on this method could test the sharp-front assumption and the incomplete-wetting hypothesis. Complement, far downstream.
- **Backlog "unsaturated flow at fine grinds"**: designated on-ramp, jointly with kupershtokh2009. Does not itself address the hypothesis.
- Competes with nothing registered.

## Implementation estimate

Not implementable now as a registry component (no coffee-relevant observable; writes no contract). If the unsaturated-wetting hypothesis graduates: extending lb_reference with the binary free-energy scheme (g_i distribution, Eq. 30 equilibria with special weights, MRT, Bouzidi, wetting BC 38/39) is effort M, with clean verification gates directly from the chapter: (i) θ_e vs h against Eq. (13) across 15–165° (Fig. 2); (ii) capillary filling vs corrected Lucas–Washburn (43); (iii) cos θ^a linearity in Ca with θ^a → θ_e as Ca → 0; (iv) receding depin angles vs Gibbs criterion (120°, θ_e − 90°). The full track to a coffee-relevant result (liquid–gas density contrast — which forces either the kupershtokh route or a density-contrast extension of this one — plus σ/θ_e data for hot water on coffee solids and 3D random-packing geometry) is effort L. Key open acquisition if pursued: Pooley 2008 PRE 78:056709.

VERDICT: implement-later — closure-complete wetting-boundary + MRT method reference (the exact piece missing from the kupershtokh2009 route) for the unsaturated-wetting contingency, but density-matched binary formulation and zero coffee observables mean no registry deliverable until that hypothesis graduates — effort M (scheme atop lb_reference) / L (coffee-relevant application)
