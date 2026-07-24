# Model card: Boullé 2026 — zero-one law for one-shot system identification

**Paper/thesis:** N. Boullé, D. Halikias, S. E. Otto, A. Townsend, "A zero-one law for one-shot system identification." arXiv:2607.15832v1 [math.NA], 17 Jul 2026.
**Stage(s):** none (cross-cutting methods — inverse-problems / identifiability family; same family as liu2025) · **Kind:** calibration (offline methodology; never runtime)
**Status:** proposed

## Scope and mechanism
A pure-mathematics identifiability result, not a process model. For systems **linear in their unknown coefficients**, L(u,f) = Σᵢ cᵢ* Dᵢ(u,f) = D₀(u,f) with prescribed analytic dictionary maps Dᵢ (main Eq. 1), the paper proves a sharp dichotomy (Theorem 1): either the set of degenerate inputs F_deg(c*) is negligible (measure zero under every nondegenerate Gaussian measure), or it is all of F. Practically: if any single input-response pair (f, u) identifies the coefficients, then almost every random Gaussian input does, and full column rank of a tested dictionary matrix G_ij = ψᵢ(Dⱼ(u,f)) (main Eq. 3; SI §1) is an a posteriori certificate of unique recovery. The SI supplies a concrete recovery algorithm (Alg. 1: assemble G, column-pivoted QR, rank-reveal, back-substitute), a Banach-space generalization of Weak SINDy. All demonstrations are canonical benchmarks (Allen–Cahn, lid-driven-cavity Navier–Stokes, Lorenz, Duffing, Hankel/circulant matrices) recovered to 1e-9–1e-15 in a **noise-free** regime.

## Governing equations
Nothing would be implemented as an espresso component. The implementable artifact, were it ever adopted as a diagnostic, is SI Alg. 1: G_ij = ψᵢ(Dⱼ(u,f)) (r₀ × N, r₀ ≥ N test functionals ψᵢ ∈ V*), b_i = ψᵢ(D₀(u,f)); solve Gc = b by column-pivoted QR with numerical-rank truncation; full column rank certifies unique identifiability of c* (Theorem 1 + SI §1). Symbols: u = observed response, f = probe input, Dᵢ = dictionary operators, c* ∈ Rᴺ = unknown coefficient vector, ψᵢ = test functionals.

## Parameters
No physical parameters. All numerical values in the paper (Allen–Cahn coefficients ¼, −5, −1, +1; Lorenz σ=10, ρ=28, β=8/3; Duffing (α,β,δ,γ,ω)=(1,5,0.02,8,0.5); GP forcing σ²=10, ℓ=0.05; matrices n=1000) are nominal benchmark choices, not fitted or measured quantities. None are espresso-relevant.

## Calibration and validation offered by the source
Mathematical proof (Theorem 1, Lemma 1) plus **verification-only** numerics: synthetic benchmarks where ground truth is known by construction, recovered with max abs errors 1.5e-12 (Allen–Cahn), 3.8e-15 / 6.7e-16 (Navier–Stokes momentum/continuity), 5.2e-9 (Lorenz), 1.1e-10 (Duffing), 1.6e-13 / 3.5e-11 (circulant / two-probe Hankel). No experimental data anywhere. The authors state plainly that the analysis "assumes exact model evaluation and noiseless observations"; noise robustness and quantitative stability are explicitly deferred as future work. In registry vocabulary: verification-gated only, and that is the paper's entire intent.

## Assumptions and validity range
- Systems **linear in the unknown coefficients**, with analytic dictionary terms and an analytic, well-posed solution map; input space with countable Schauder basis.
- Noise-free, exact evaluation; near-degeneracy under noise only gestured at via smallest singular value.
- Nothing on parameters entering nonlinearly — which is where most puckworks fitted quantities live (Cameron rate constants inside a stiff ODE solve, brewer2026 sigma(phi1) closure, Wadsworth φ_c/α, foster2025 front dynamics). The theorem does not apply to those fits as posed.
- Silent on: partial observations, test-functional selection, noisy/discretized certificates — all listed as open by the authors.

## Interface mapping
Consumes/produces no contract fields. Hypothetical use would be an offline audit: for any registry component genuinely linear in its coefficients, given one clean simulated (f, u) pair, the rank certificate says whether one experiment can pin the coefficients. But puckworks' identifiability concerns are **practical** (thin noisy data, e.g. sigma(phi1) on 3 reconstructed points), not structural — and that niche is already held by liu2025's profile-likelihood machinery, which handles noise and nonlinear parameters. No adapter chain worth defining.

## Extractable data
None for puckworks/data/ — no coffee content, no transcribable physical tables. Code and datasets public at https://github.com/NBoulle/wias (Firedrake/SciPy benchmarks).

## Overlaps and conflicts
- **liu2025 (methods family):** complements conceptually — Boullé answers structural identifiability ("can any single experiment work, in principle, noise-free") where liu2025 answers practical identifiability and OED under noise. For every live puckworks question (auditing Cameron rate constants, sigma(phi1), discriminating kappa(t) vs lognormal hypotheses), liu2025's machinery is the applicable one; this paper's linear-in-coefficients, noiseless scope excludes them. Does not compete or supersede.
- No overlap with any staged component (cameron2020.extraction_bdf, brewer2026.*, wadsworth2026.permeability, foster2025.infiltration) or any backlog item — none of the backlog asks for structural identifiability theory.
- Worth one line in the ROADMAP validation-strength notes if desired: the paper's "rank of the observed linear system as a certificate of success" is a clean articulation of why post-fit reconstruction on a degenerate design proves nothing — but that principle is already house doctrine.

## Implementation estimate
None proposed. Adopting the rank certificate as a diagnostic would be effort S for any linear-in-coefficients sub-model, but no registered component currently has that form and the noise-free assumption breaks on real shot data.

VERDICT: skip — elegant structural-identifiability theory whose linear-in-coefficients, noise-free scope covers none of puckworks' actual fitted models and whose practical niche (identifiability auditing) is already better served by the registered liu2025 methods card, with no data to extract — effort S
