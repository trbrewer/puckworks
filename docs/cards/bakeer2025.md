# Model card: Bakeer 2025 — Bayesian inversion + Fisher-information sensor informativeness for distributed parameter fields

**Paper/thesis:** T. Bakeer, M. Herbers, S. Marx, "Sensor Informativeness, Identifiability, and Uncertainty in Bayesian Inverse Problems for Structural Health Monitoring," arXiv:2511.16628v2 [cs.CE], Nov 2025 (no DOI; preprint, not yet peer-reviewed).
**Stage(s):** none (cross-cutting methods — inverse-problems / identifiability family, alongside liu2025 and boulle2026); serves parameterization of bed_dynamics, flow, extraction, observables · **Kind:** calibration (offline methodology; never runtime)
**Status:** proposed

## Scope and mechanism
An SHM paper: recover a spatially distributed flexural-rigidity field EI(x) along a bridge beam from sparse rotation (tilt) influence-line measurements under a traversing point load, posed as a linear-Gaussian Bayesian inverse problem. Zero espresso content; the beam forward model is discarded entirely for our purposes. What transfers is the assembled generic layer: (i) linear/linearized Gaussian inversion with a smoothness (GMRF) prior, whose MAP is exactly Tikhonov regularization with λ = σ²τ and whose posterior covariance gives credible intervals for free; (ii) the Fisher information matrix (FIM) as a cheap, prior-agnostic **informativeness map** — per-observation, per-spatial-element — that tells you *before fitting* which parts of a distributed field the data can and cannot constrain; (iii) an explicit bias–variance criterion for choosing the discretization N of the unknown field given a fixed sensing plan. The headline transferable lessons: informativeness is spatially heterogeneous and strictly bounded by experiment design; zero-leverage regions (where the forward kernel vanishes) are non-identifiable at any noise level; refining the field mesh past what the data inform buys variance, not resolution. Honesty note: the generic layer is textbook (Kaipio–Somersalo, Tarantola — the authors cite both); the paper's novelty is the SHM application. Its registry value is as a clean, self-contained recipe with all formulas in one place, applied end-to-end on synthetic + field data.

## Governing equations
Transcribed as the machinery that would actually be implemented (generic layer). Beam-specific kernels (Eqs. 4–8, 12: Maxwell–Betti influence-line kernel K(r,z;s) = m_r(s)M(s;z) for a simply supported Euler–Bernoulli beam) are context only and would be replaced by a puckworks forward map.

1. **Discretized linear forward map (Eqs. 9–12):** y = A v + ε, with y ∈ R^(RK) stacked measurements (R sensors × K load positions), v ∈ R^N element-averaged unknown field (element average v_j = (1/Δs_j)∫ v(s)ds, Eq. 9), A_(r,k),j = ∫_{s_{j−1}}^{s_j} K(r,z_k;s) ds (Eq. 12), ε noise.
2. **Likelihood (Eq. 14):** y | m, σ² ~ N(F(m), σ²Γ). F = forward map (F(m)=Am linear case); Γ ≻ 0 known relative noise-correlation structure; σ² unknown overall noise scale; m ∈ R^N unknown parameter vector.
3. **GMRF smoothness prior (Eq. 15):** m | τ ~ N(m₀, (τ D⊤D)⁻¹). D = discrete difference operator (first or second differences); τ = prior precision (larger τ → smoother field near m₀).
4. **Positivity via log-transform (Eq. 16):** m = exp(η) elementwise, η ~ N(m_η, (τ_η D⊤D)⁻¹); inference in η-space needs no Jacobian for MAP.
5. **Gaussian posterior (Eq. 17):** Q_post = (1/σ²)A⊤Γ⁻¹A + τD⊤D; m_post = Q_post⁻¹[(1/σ²)A⊤Γ⁻¹y + τD⊤D m₀]; m | y,σ²,τ ~ N(m_post, Q_post⁻¹).
6. **MAP–Tikhonov identity (§3.3, unnumbered):** the MAP normal equation is deterministic Tikhonov with λ = σ²τ; the posterior covariance is the uncertainty quantification the deterministic solution lacks.
7. **Nonlinear case (§3.4):** Gauss–Newton/Levenberg–Marquardt linearization F(m) ≈ F(m_k) + J_k(m−m_k), J_k = ∂F/∂m; Laplace covariance Σ_post ≈ [(1/σ²)J⊤Γ⁻¹J + τD⊤D]⁻¹ at the MAP.
8. **Fisher information (Eq. 18):** I(m) = (1/σ²) J(m)⊤Γ⁻¹J(m); prior-agnostic data precision.
9. **Prior/data decomposition (Eq. 19):** Q_post = τD⊤D (prior precision) + I (data precision) — makes explicit what the prior, vs. the data, is doing.
10. **Per-sensor additivity (Eq. 20):** with Γ block-diagonal by sensor, I = Σᵢ (1/σ²) Jᵢ⊤Γᵢ⁻¹Jᵢ =: Σᵢ I⁽ⁱ⁾ — informativeness attributable observation-by-observation.
11. **Reparameterization chain rule (Eq. 21):** for an inverse-quantity reparameterization EI = 1/v: J^EI_{·,j} = −EI_j⁻² J^v_{·,j}, so I_EI = W⁻¹[(1/σ²)(J^v)⊤Γ⁻¹J^v]W⁻¹, W = diag(EI₁², …, EI_N²). (Directly reusable for permeability ↔ resistance parameterizations.)
12. **Per-element informativeness curve (Eq. 22, iid noise Γ=I):** I⁽ⁱ⁾_jj = (1/(σ²EI_j⁴)) Σ_k [A_(i,k),j]². Interpreted via Cramér–Rao *ignoring cross-parameter couplings* (authors' own caveat — diagonal reading is optimistic).
13. **Bias–variance decomposition (Eq. 23):** RMSE²(ÊI_{1/2}) = Var[ÊI_{1/2}] + (E[ÊI_{1/2}] − EI*(L/2))², used to select field discretization N: refine until discretization bias no longer dominates; beyond that, variance grows (U-shaped RMSE vs N, minimum at N ≈ 40–60 in their beam example with fixed sensing).

Hyperparameters (σ², τ): empirical Bayes by evidence maximization, or conjugate hyperpriors (inverse-Gamma for σ², Gamma for τ) (§3.5). Nothing simplified away; the beam kernel equations are the only content deliberately not carried.

## Parameters
No espresso-relevant parameters exist. Domain values below are context only.

| symbol | value | units | source |
|---|---|---|---|
| synthetic beam L | 4 | m | nominal (synthetic study) |
| tilt-noise σ sweep | 0.02 / 0.01 / 0.005 / 0.001 | mm/m | assumed (synthetic) |
| example CI case (N, R, λ) | 24, 24, 7.44×10⁻⁴ | —, —, — | nominal (Fig. 4) |
| bias–variance sweet spot N | ≈ 40–60 | elements | fitted (synthetic sweep, Fig. 7; λ per R by Quasi-Optimality) |
| openLAB spans 1–2 | 15 + 15 | m | measured (as-built) |
| load vehicle | 4.9 t, 2 axles, 2 m spacing | — | measured |
| tilt sampling | 5 | Hz | measured |
| field EI result | span 1 < span 2, order 1×10⁹ | N·m² | fitted (posterior mean, Figs. 12–13) |
| generic (σ², τ, D, Γ, N) | not provided | — | problem-specific by construction |

## Calibration and validation offered by the source
- **Synthetic (§5, Figs. 4–7):** ground truth known by construction. Damage-zone recovery sharpens as σ decreases 0.02→0.001 mm/m with two stations; near-support uncertainty remains large at all noise levels, matching the FIM prediction. Bias–variance U-shape in N demonstrated across R = 4–20 sensors. This is **verification/demonstration**, not experimental validation.
- **Field (§6, openLAB bridge):** two composite tilt channels (three tiltmeters per span averaged), constant-speed load segments 5–30 m. Data–model influence-line fits are visually close (Fig. 11) — post-fit reconstruction in registry vocabulary. The recovered contrast (span 1 less stiff than span 2) is **consistent with construction records** (span 1 cast C25/30 concrete, span 2 C50/60) — a qualitative, binary sanity check. There is **no independent measurement of EI(x)** anywhere; no controlled-damage recovery on the real bridge (listed as future work). Boundary rotational springs are estimated jointly with EI via empirical Bayes, which the authors acknowledge enlarges the parameter set and its uncertainty.
- Net: methodology is internally coherent and verification-gated; field claims are plausibility-level. Authors do not overclaim, and neither should we.

## Assumptions and validity range
- Linear-Gaussian core; nonlinear handled only by local GN/LM + Laplace (quadratic approximation — silent on multimodal posteriors).
- Noise correlation structure Γ assumed **known**; only the scale σ² is inferred. Empirical-Bayes tuning explicitly relies on this.
- FIM is a **local** metric evaluated at a nominal parameter; diagonal Cramér–Rao reading ignores cross-parameter coupling (authors' caveat).
- GMRF smoothness prior suits smoothly varying fields; steps/cracks need edge-preserving priors (mentioned, not developed).
- Domain-specific and discarded: small-deflection Euler–Bernoulli kinematics, quasi-static traversing point load, simply-supported/frame boundary conditions.
- Acknowledged omissions: dynamic effects, temperature drift, torsional coupling, model-discrepancy terms; only two field channels assimilated.
- Structural failure mode that transfers verbatim: where the forward kernel has no leverage (their zero-moment sections; our analogue — field components a boundary observable integrates away), the field is non-identifiable regardless of noise, and only the prior fills the gap. Credible bands there report the prior, not the data.

## Interface mapping
Inputs consumed / outputs produced: **no contract fields** — not a process-model component. Offline diagnostic layer wrapped around an existing component + dataset. Concrete puckworks couplings, all offline:
- **FIM informativeness audit for depth-resolved BedState fields:** linearize a forward model (streamtube or LB surrogate) around nominal BedState; J maps depth-cell kappa(x)/k(x) perturbations to ShotResultState traces (P(t), flow, W(t)); eigen-analysis of I answers "how many depth modes do top-pressure + bottom-flow observables actually constrain?" **before** the bed_dynamics kappa(t)=kappa₀·f(P,eps,E) backlog fit is attempted. Expected (and useful) answer: few — which caps how that backlog model should be parameterized.
- **Credible intervals on existing fits:** DE1 fixture A fitted kappa = 1.196 is currently a point estimate; Eq. 17 / Laplace turns it into a posterior at negligible cost.
- **Discretization criterion:** Eq. 23's U-curve replaces "as fine as feasible" when choosing the number of depth cells for any distributed fit.
- **Reparameterization bookkeeping:** Eq. 21 for FIM/posteriors in kappa vs. resistance (1/kappa) parameterizations.
Adapters: replace the beam kernel with puckworks forward-map Jacobians (finite differences or autodiff); the GN/Laplace layer for our nonlinear stack. No runtime coupling ever.

## Extractable data
Nothing for puckworks/data/ — all quantitative content is bridge-specific. The underlying openLAB monitoring data are published (Jansen et al., Data in Brief 60 (2025) 111624 + supplementary release) but espresso-irrelevant. No code repository is stated in the paper.

## Overlaps and conflicts
- **liu2025 (registered methods card, implement-later): complements, does not compete.** liu2025 covers practical identifiability via frequentist profile likelihood (accurate but expensive; demonstrated on scalar ODE parameters) and OED-by-control-design via PMP. This paper covers exactly what liu2025's card lists as silent: distributed **spatial** fields, **priors**, and cheap linear-algebra informativeness diagnostics (FIM) that scale where profile likelihood does not. Division of labor if both are adopted: FIM (this paper) as the fast first-pass audit and sensing/parameterization design; profile likelihood (liu2025) for careful CIs on the handful of parameters that survive; liu2025's PMP for P(t) discrimination designs.
- **boulle2026 (skip): no conflict** — structural, noise-free identifiability; different niche, already dispositioned.
- **Audit targets among registered components:** brewer2026.streamtube's sigma(phi1) closure (LOO on 3 reconstructed points) and cameron2020.extraction_bdf's two-population rate constants — the same thin-data fits liu2025's card names; this framework adds posterior credible intervals and prior/data decomposition (Eq. 19) to make "how much is prior?" explicit.
- **Backlog bed_dynamics kappa(t) and observables scale/measurement kernels:** direct design input (see Interface mapping); Γ-structure specification is the same concern the observables measurement-kernel item raises.
- Supersedes nothing; models no espresso stage.

## Implementation estimate
Not a shot-chain component. Effort **S** for the highest-value piece: FIM informativeness audit around an existing forward model (finite-difference Jacobian + Eqs. 18–22 + eigen-analysis) applied first to the depth-resolved-kappa identifiability question on DE1 fixture A geometry. Effort **M** for the full Laplace/GN Bayesian layer with GMRF priors and empirical-Bayes hyperparameters on the nonlinear stack. Dependencies: a forward-solvable component with a defined observation map to ShotResultState; none on this paper specifically — the generic layer could equally be implemented from Kaipio–Somersalo, so cite both. Natural gate: the FIM audit must reproduce the known degenerate case (a depth-uniform kappa perturbation is identifiable from total ΔP; higher depth modes should show rapidly decaying eigenvalues) before its verdicts are trusted on backlog design.

VERDICT: implement-later — textbook-but-well-assembled Bayesian/FIM identifiability layer whose distributed-field, prior-aware scope fills exactly the gaps the registered liu2025 methods card leaves open (spatial fields, priors, cheap informativeness maps), with a concrete S-effort first use (depth-resolved kappa identifiability audit before the kappa(t) backlog fit) but zero espresso content or data of its own — effort S–M.
