# Model card: huang2016 — third-order-consistent MRT pseudopotential LB scheme

**Paper/thesis:** Huang, R., Wu, H. (2016). Third-order analysis of pseudopotential lattice Boltzmann model for multiphase flow. arXiv:1605.00365v1 [physics.comp-ph]. (Preprint submitted to Elsevier; copy held is the v1 preprint. A journal version is believed to exist in *J. Comput. Phys.* — confirm DOI before citing formally.)
**Stage(s):** flow, infiltration · **Kind:** calibration (method reserve; no runtime candidate)
**Status:** proposed (contingency card — see verdict condition)

## Scope and mechanism

Theory/methods paper: first third-order Chapman–Enskog analysis of the D2Q9 MRT pseudopotential (Shan–Chen-class) LB model for multiphase flow. Identifies the leading time- and velocity-independent third-order terms on the interaction force — an isotropic term R_iso and an anisotropic term R_aniso — in the recovered macroscopic momentum equation, and derives from them (i) the condition eliminating lattice-induced droplet distortion, (ii) an accurate *continuum-form* pressure tensor (previously believed unobtainable), and (iii) a "consistent scheme" of third-order additional terms Q_m that adjusts coexistence densities and surface tension independently. This is exactly the closure set (relaxation-rate constraints, k₁/k₂ source terms, magic parameter) that wang2027 uses but does not publish. Registry relevance is solely as the primary methods reference for a contingent pore-scale multiphase wetting solver targeting the incomplete-wetting backlog hypothesis (fine-grind EY dip: tubes at k→0).

## Governing equations

What would actually be implemented if this scheme were adopted (source equation numbers):

1. **MRT collision with additional term** (Eq. 47, superseding Eq. 2): m̄(x,t) = m − S[m − m^eq] + δ_t(I − S/2)F_m + SQ_m; streaming f_i(x + e_iδ_t, t + δ_t) = f̄_i (Eq. 3). D2Q9 velocities e_i (Eq. 1); Lallemand–Luo orthogonal M (Eq. 4); S = diag(s₀, s_e, s_ε, s_j, s_q, s_j, s_q, s_p, s_p).
2. **Equilibrium moment with free parameter α** (Eq. 5): m^eq = (ρ, −2ρ + 3ρ|u|²/c², αρ − 3ρ|u|²/c², ρu_x/c, −ρu_x/c, ρu_y/c, −ρu_y/c, ρ(u_x² − u_y²)/c², ρu_xu_y/c²)ᵀ; α = 1 recovers the classical moment.
3. **Guo-type discrete force moments F_m** (Eq. 6); macroscopics ρ = Σf_i, ρu = Σe_if_i + (δ_t/2)F (Eq. 7).
4. **Nearest-neighbor interaction force** (Eq. 8): F(x) = −Gψ(x) Σ_{i=1..8} ω(|e_iδ_t|²) ψ(x + e_iδ_t) e_iδ_t, with ω(δ_x²) = 1/3, ω(2δ_x²) = 1/12 (fourth-order isotropic). Resulting EOS (Eq. 9): p_EOS = ρc²/3 + (Gδ_x²/2)ψ²; for a prescribed EOS, ψ = √(2(p_EOS − ρc²/3)/(Gδ_x²)), G arbitrary in sign-consistent range.
5. **Carnahan–Starling EOS example** (Eq. 10): p_EOS = K[ρRT(1 + bρ/4 + (bρ/4)² − (bρ/4)³)/(1 − bρ/4)³ − aρ²], a = 0.4963R²T_c²/p_c, b = 0.18727RT_c/p_c; K scales interface thickness.
6. **Third-order macroscopic result** (Eqs. 30–31), with diag(σ₀,…) = S⁻¹ − I/2:
   - R_iso = −δ_t²c² · [2(α−1)(σ_eσ_q − σ_pσ_q) − 1]/12 · ∇·∇F (Eq. 31a)
   - R_aniso = −δ_t²c² · (α−1)(12σ_pσ_q − 1)/12 · (∂²_y F_x, ∂²_x F_y)ᵀ (Eq. 31b)
7. **Anisotropy elimination** (Eq. 33): R_aniso = 0 iff α = 1 or the magic parameter Λ = σ_pσ_q = (1/s_p − 1/2)(1/s_q − 1/2) ≡ 1/12.
8. **Continuum-form pressure tensor** (Eq. 38/43, redefined with R_Q in Eq. 54/56): ∇·P = ∇(ρc²/3) − F − R_iso − R_Q; with k_d = [2(α−1)(σ_eσ_q − σ_pσ_q) − 1]/12 and free parameters a₁₋₄ (Eq. 40), b₁₋₂ (Eq. 42) that provably do not affect coexistence densities.
9. **Mechanical stability condition** (Eq. 45, generalized Eq. 61): ∫_{ρ_g}^{ρ_l} (p₀ − ρc²/3 − (Gδ_x²/2)ψ²) ψ′/ψ^{1+ϵ} dρ = 0 with ϵ = (1 + 12k_d − 12k₁ − 12k₂)/(1 − 6k_d); ψ′ = dψ/dρ, p₀ = p_EOS(ρ_g) = p_EOS(ρ_l). Discrete-form tensor (Eq. 34/37) corresponds to ϵ = 0 and is accurate only when k_d = −1/12 (α = 1 or σ_e = σ_p).
10. **Consistent additional term** (Eqs. 48, 57, 59): Q_m = (0, Q_m1, Q_m2, 0, 0, 0, 0, Q_m7, Q_m8)ᵀ, discrete form Q_m1 = 3(k₁ + 2k₂)|F|²/(Gψ²c²), Q_m7 = k₁(F_x² − F_y²)/(Gψ²c²), Q_m8 = k₁F_xF_y/(Gψ²c²); Q_m2 arbitrary at third order, set Q_m2 = −Q_m1. Continuum equivalent R_Q = −∇·[k₁Gδ_x⁴∇ψ∇ψ + k₂Gδ_x⁴(∇ψ·∇ψ)I] (Eq. 55), with ∇ψ evaluated via the isotropic central scheme ∇ψ ≈ −F/(Gδ_x²ψ) (Eq. 58).
11. **Surface tension** (Eq. 62): σ = −(Gδ_x⁴/6)(1 − 6k₁) ∫_{ρ_g}^{ρ_l} ψ′² √ϱ dρ, ϱ = (dρ/dx)². Net tuning rule: coexistence densities set by k₁ + k₂ (via ϵ), surface tension independently by k₁.
12. **Appendix A**: the EDM forcing scheme is exactly Eq. 47 with a specific Q_m^EDM (Eq. A.6b) — i.e., EDM is a special case, not a distinct family. **Appendix B**: fifth-order heuristic — the differential operator before Q_m^(2) at order ε^{n+2} equals that before m^(0) at order ε^n, so Λ ≡ 1/12 also kills the k₁-amplified fifth-order anisotropy from Q_m (recommended even when α = 1).

Nothing simplified away; all "≈" steps in the source (cubic-velocity neglect, Eq. 18–19; O(∇⁴) anisotropic truncations, Eqs. 35, 39, 41) are the authors' and are noted in the validity section.

## Parameters

| symbol | value | units | source |
|---|---|---|---|
| ω(δ_x²), ω(2δ_x²) | 1/3, 1/12 | – | nominal (4th-order isotropy) |
| Λ = σ_pσ_q | 1/12 | – | nominal (derived elimination condition) |
| α | 1 (recommended); tests −0.5–2.5 | – | nominal |
| G | −1 (with ψ from Eq. 9, value immaterial) | lattice | nominal |
| C–S EOS a, b, R, K | 1, 4, 1, 1 | lattice | nominal (test config) |
| k₁, k₂ | free; tests 1−6k₁ ∈ [0.1, 2.0], ϵ ∈ {1, 2} | – | assumed (tuning knobs; coffee values would be calibration targets) |
| a₁₋₄, b₁₋₂ | free subject to Eqs. 40, 42 | – | nominal (no observable effect) |
| relaxation rates s_i | per-test (e.g. s₀ = s_j = 1, s_p = s_ε = 1/τ, s_e = 1/(5τ−2), s_q from Λ) | – | nominal |
| ρ_g^thermo, ρ_l^thermo (T = 0.9T_c) | 4.5435×10⁻², 2.4806×10⁻¹ | lattice | derived (Maxwell construction) |

No physical-fluid parameter exists in the paper; everything is lattice units.

## Calibration and validation offered by the source

All validation is **verification-grade self-consistency** (analytics vs. the authors' own simulations); there is no experiment and no physical fluid anywhere.

- Droplet isotropy (Figs. 1–2, 128², T = 0.9T_c): α ≠ 1 with generic S gives visibly out-of-round, τ-dependent droplets; α = 1 or Λ ≡ 1/12 restores circularity for all tested α ∈ [−0.5, 2.5], τ ∈ {0.6, 1, 1.5}. Qualitative (contour plots), no roundness metric quantified.
- Coexistence curves (Fig. 3, 1024×8 flat interface): for α = 1 (k_d = −1/12), discrete and continuum tensors coincide and match simulation; for α = 2.5 (k_d = 0), the discrete-form prediction visibly deviates in the gas branch while the continuum form (ϵ = 1) tracks the numerics. Agreement is graphical; no error norms reported. τ-independence confirmed.
- Adjustable ϵ (Fig. 4): simulated coexistence curves for ϵ = 1, 2 match Eq. 61 across k₁ ∈ {0, k₂, with k₂ = 0}, confirming densities depend on k₁ + k₂ only.
- Laplace law (Fig. 5, Table 1, 256×265, T = 0.9T_c, r₀ = 32–96δ_x): δp vs 1/r linear; σ spans 1.5814×10⁻⁴–2.6174×10⁻³ (ϵ = 1) and 1.4828×10⁻⁴–2.4574×10⁻³ (ϵ = 2) as 1−6k₁ goes 0.1→2.0. Authors note σ departs from linearity in 1−6k₁ when σ is very small (truncated higher-order terms), and ρ_g/ρ_l drift slightly with k₁ at fixed ϵ (EOS compressibility).
- Density ratio exercised in all tests is only ~5.5 (0.248/0.0454). Nothing here demonstrates the ~10³ ratio a hot-water/air coffee simulation needs (wang2027 builds that on top of this scheme, in a different fluid regime).

Nothing to upgrade: the paper claims theory + numerical confirmation, and delivers exactly that.

## Assumptions and validity range

- **2D D2Q9 only.** All third-order coefficients (Eqs. 29, 31, 33, 45) are lattice-specific. A puckworks pore-scale build needs 3D (D3Q19, matching brewer2026.lb_reference's lattice); the analysis would have to be redone or sourced for 3D — a real, unbudgeted derivation cost.
- Nearest-neighbor interaction force (Eq. 8) with the specific ω weights; multirange forces not covered.
- Steady/stationary derivation: third-order terms identified at u = 0; authors assert they persist generally but only the static case is proven.
- Low Mach: cubic velocity terms discarded (Eq. 18–19); isothermal; single component.
- O(∇⁴) anisotropic truncations in F, R_iso, P (Eqs. 35, 39, 41) — the tensors are leading-order isotropic approximations.
- D2Q9 LBE is at most fourth-order isotropic ⇒ fifth-order anisotropic terms and hence spurious currents are **intrinsic** and cannot be removed by force isotropy alone (§5.1 end) — a stated hard floor on solver quality.
- Adjusting coexistence via α couples to bulk viscosity and destabilizes for α far from 1 (§5.2 end) — that route is deprecated by the authors in favor of Q_m.
- Silent on: wetting/solid boundaries (no contact-angle model at all — wang2027's addition), thermal effects, 3D, high density ratio stability, solute transport, deformable solids. Every coffee-specific ingredient is out of scope.

## Interface mapping

Inputs consumed: none of GrindState/BedState/MachineState map; a contingent solver would take voxel geometry from brewer2026.pack_generator and coffee-regime fluid properties (σ, θ, μ(T) from telisromero cards) — none plumbed for multiphase.
Outputs produced: none to contracts. Contingent product = offline wetting/regime maps and an effective saturated-fraction or k(S) closure feeding the incomplete-wetting atom in brewer2026.streamtube, or a test of foster2025.infiltration's sharp-front assumption.
Couplings: strictly offline calibration chain; runtime coupling would be the mega-model failure mode. Adoption = a second LB code path (MRT multiphase) beside the single-phase TRT verification twins — a new solver, not an adapter.

## Extractable data

None worth transcribing: all tables/figures are lattice-unit self-consistency tests (Table 1 σ values are scheme-verification numbers, reproducible from Eqs. 61–62). No code or data repository published. The card's value is the equations themselves — specifically Eqs. 33, 45, 57, 59, 61, 62, which are the closures wang2027 leaves unpublished.

## Overlaps and conflicts

- **wang2027 (skip card)**: this paper is the dangling pointer in that card's verdict ("go to the primary methods literature"). huang2016 supplies the missing s_i-constraint (Λ ≡ 1/12), k₁/k₂ scheme, and pressure-tensor machinery. Resolves that reference; the two cards should cross-link.
- **brewer2026.lb_reference / lb_taichi (flow, calibration)**: same numerical family, disjoint physics tier (single-phase TRT saturated Darcy verification vs. multiphase MRT interface capture). Note the TRT twins already fix their own magic parameter — conceptually adjacent but not the same Λ; no code reuse beyond streaming scaffolding.
- **foster2025.infiltration (runtime)**: the continuum model this method class could someday stress-test (sharp-front assumption, p_c magnitude).
- **egidi2018 (framework pointer)**: the *other* candidate framework for the unsaturated backlog (Richards/van Genuchten continuum). Both are blocked on the same missing constitutive data (coffee wettability/retention); Richards is blocked on θ(ψ) curves, this route on σ/θ for hot water on coffee solids. Neither unblocks the other.
- **Backlog "unsaturated flow at fine grinds"**: this is the designated pore-scale method reserve for that item; competes with nothing registered, supersedes nothing.

## Implementation estimate

Effort L, and only under the named condition: promotion of the incomplete-wetting hypothesis (P3 cluster) to requiring pore-scale multiphase simulation. Cost stack: 3D generalization of the third-order coefficients (or sourcing a 3D equivalent), high-density-ratio stabilization (this paper tests ratio ~5.5), wetting boundary conditions (not in this paper), coffee-regime σ/θ calibration data (absent from registry), then a verification ladder (Laplace law, Maxwell coexistence, spurious-current audit — this paper defines those gates in 2D). Gate design is actually a strength: Figs. 3–5/Table 1 are directly reusable acceptance tests for any implementation.

VERDICT: implement-later — canonical, complete, and internally verified closure set (Λ ≡ 1/12, k₁/k₂ scheme, continuum pressure tensor) for the pore-scale multiphase LB route, held strictly as the method reserve for the incomplete-wetting hypothesis; 2D-only, verification-gated, zero coffee data, so it activates only if that hypothesis graduates — effort L
