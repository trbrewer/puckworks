# Model card: bellantoni2025 — immersed-boundary lattice Boltzmann wetting via wall-interaction force Π(h)

**Paper/thesis:** Bellantoni, E., Guglietta, F., Pelusi, F., Desbrun, M., Um, K., Nicolaou, M., Savva, N., Sbragaglia, M. (2025). Immersed boundary – lattice Boltzmann method for wetting problems. arXiv:2503.20605v2 [physics.flu-dyn]. Preprint (v2, 27 Mar 2025); no journal DOI in the provided copy.
**Stage(s):** infiltration, flow · **Kind:** calibration (method reference; no runtime candidate)
**Status:** proposed

## Scope and mechanism

Numerical-methods preprint: a hybrid immersed-boundary (IB) – lattice Boltzmann (LB) scheme for a single droplet spreading on a flat solid substrate. The droplet interface is a **sharp** Lagrangian triangular mesh carrying surface tension (finite-element strain-energy formulation) and a wall-interaction force Π(h) of Lennard–Jones-like form (repulsive at short range, attractive at intermediate range) that plays the role of a disjoining pressure; the fluids inside and outside the droplet are density-matched D3Q19 BGK LB fluids distinguished only by a viscosity ratio λ. The advance over the authors' prior IB-LB wetting model (Pelusi 2023, their Ref. [28]) is an analytical closure A(θ_eq, σ, ξ, n, m) — Eq. (29) — that sets the equilibrium contact angle a priori, with no pre-calibration, across hydrophilic-to-hydrophobic angles; a tunable lengthscale ξ regularizes interface curvature near the contact line (the interface never touches the wall; a thin film of thickness δ ≈ ξ persists). Zero coffee content; candidate registry value is as a third method route — sharp-interface IB-LB, vs the two diffuse-interface LB routes already carded (kupershtokh2009 pseudopotential, kusumaatmaja2010 free-energy binary) — for the pore-scale unsaturated-wetting backlog contingency.

## Governing equations

What would actually be implemented (source equation numbers in parentheses):

1. **LB evolution** (3): f_i(x + c_iΔt, t + Δt) − f_i(x, t) = Δt[Ω_i + S_i], D3Q19 (velocity set and weights ω_i in their Table I). BGK collision (4): Ω_i = −(1/τ_LB)[f_i − f_i^(eq)]; second-order Maxwell–Boltzmann equilibrium (5); Guo forcing (6): S_i = (1 − Δt/2τ_LB) ω_i [(c_i − U)/c_s² + (U·c_i)c_i/c_s⁴]·F. c_s = Δx/(√3 Δt).
2. **Moments** (7, 8): ρ = Σ_i f_i; U = (1/ρ)Σ_i c_i f_i + FΔt/(2ρ) (half-force correction). Transport closures: μ = ρc_s²(τ_LB − Δt/2), p = c_s²ρ (ideal-gas pressure; **no phase EOS**).
3. **Viscosity contrast** (9): τ_LB(x, t) set per node to τ_LB^in or τ_LB^out by ray-tracing inside/outside the closed mesh; λ = μ_in/μ_out.
4. **IB two-way coupling** (10, 11): F(x, t) = Σ_j φ_j Δ(q_j − x); q̇_j = Σ_x U(x, t) Δ(q_j − x) Δx³, with the 4-point Peskin stencil Δ(x) = Ψ(x)Ψ(y)Ψ(z)/Δx³, Ψ per (12). Node update: forward Euler (13).
5. **Interface force split** (14): F = −[σ n̂(∇·n̂) + Π(h) n̂] δ(x − r), n̂ the outward interface normal, h the vertical distance of the interface node from the wall.
6. **Surface tension via FEM strain energy** (15–25): deformation gradient C = ∂X/∂X₀ (15); surface projection D = P(t)·C·P(0) with P = 1 − n̂⊗n̂ (16); invariants a, b (17a, 17b); strain energy w(a) = σe^a (21) chosen so that Fσ reduces exactly to −σ n̂(∇·n̂) (22); per-triangle discrete D = I + ∇V from shape-function displacements (23, 24); nodal force φ_σ,j = −∂w/∂V_j (25). No terms dropped: the tangential terms of (19) vanish identically for constant σ.
7. **Wetting force** (26, 27): Π(h) = A[(ξ/h)^n − (ξ/h)^m], n > m; nodal force φ_Π,j = −(χ_j/3) Π(h) n̂_j, χ_j the node-associated mesh area, n̂_j the face-averaged nodal normal.
8. **Contact-angle closure** (29) — the paper's central deliverable: A = σ (m − 1)(n − 1)(1 + cos θ_eq) / [(n − m) ξ]. Derived (Appendix A, Eqs. A1–A3) in the wedge limit ξ/R₀ → 0 from the normal force balance (28): Δp = σ∇·n̂ + Π(h).
9. **Equilibrium-shape ODE** (gate material, not runtime): axisymmetric profile r = R₀g(u), u = cos φ, satisfying (B4) with ϵ = ξ/R₀, k = ΔpR₀/σ, h = ug(u) + g(−1) + δ; constraints g(1) = g(−1) (B5) and volume ∫g³du = 2 (B7). Wall-standoff closure for (n, m) = (6, 3) (C10): δ = ϵ[2/(1 + √(1 + 4β))]^{1/3}, β per (C9). Measured-angle estimator from droplet half-height ℓ (C7): tan²(θ_eq/2) = 3ℓ³/(R₀³ − ℓ³). Useful auxiliary: Π-minimum height h* = ξ(n/m)^{1/(n−m)}.

## Parameters

| symbol | value | units | source |
|---|---|---|---|
| (n, m) | (6, 3) | – | nominal (following their Ref. [65]) |
| A | from Eq. (29) given σ, ξ, θ_eq | lattice | derived closure |
| σ | not provided as a number | lattice | assumed (user-chosen) |
| ξ/R₀ (statics sweep) | 0.1 / 0.2 / 0.3 (error study 0.10–0.30) | – | assumed |
| ξ (dynamics) | 2 (inertial study); 3 (viscous study) | lattice | assumed |
| θ_eq | π/4–3π/4 (statics); π/16–π/2 (dynamics) | rad | assumed (imposed) |
| λ = μ_in/μ_out | 1 (statics); 10 (inertial dynamics) | – | assumed |
| R₀ | 20 (statics); 60 (inertial); 90–150 (viscous) | lattice | assumed |
| N_t (triangles) | 20 000–40 000 (statics); 500 000–750 000 (viscous) | – | assumed (resolution study) |
| Δx = Δt = 1, ρ₀ = 1 | 1 | lattice | nominal |
| z_cut/R₀ (contact-radius protocol i, optimum) | ≈ 0.050 (matches h*/R₀) | – | fitted (to inertial scaling) |
| ε (protocol ii flatness, optimum) | ≈ 0.1 | – | fitted (to inertial scaling) |

All values are lattice units; no physical-unit mapping is performed anywhere in the paper.

## Calibration and validation offered by the source

All **verification-grade** (simulation vs their own analytics or literature scaling laws); no experiment.

- **Statics vs axisymmetric ODE (B4)** (Figs. 2, 3): profile L2 error E_L2 (Eq. 30) generally 10⁻³–10⁻² at N_t = 40 000 across θ_eq ∈ {π/4, 3π/8, π/2, 3π/4} and ξ/R₀ ∈ [0.10, 0.30]; error grows below a critical (ξ/R₀)* for small angles, peaking at ≈ 0.01 (N_t = 40 000) vs ≈ 0.1 (N_t = 20 000) for θ_eq = π/4. Note this validates the discretized scheme against the *same* continuum force balance (28) the scheme is built on — internal consistency, not independent physics validation.
- **Imposed vs measured angle** (Fig. 8, via Eq. C7): agreement only as ξ/R₀ → 0 and better for obtuse angles; for θ_eq = π/4 the measured angle is ≈ 0.32π at ξ/R₀ = 0.1 and still ≈ 0.28π at ξ/R₀ = 0.01 (imposed 0.25π). The a-priori closure (29) is therefore accurate in the wedge limit only; at practical ξ/R₀ the realized angle deviates from the imposed one by an amount the paper quantifies but does not correct.
- **Inertial spreading** (Fig. 4): r_c(t) ~ t^{1/2} recovered "very close to 1/2" by visual inspection (exponents not fitted); onset and plateau depend on the contact-radius definition protocol (z_cut or ε), with optima z_cut/R₀ ≈ 0.050, ε ≈ 0.1; stated "nice agreement" with the molecular-dynamics results of Winkels 2012 (their Ref. [69]).
- **Viscous (Tanner) regime** (Fig. 5): transition toward r_c(t) ~ t^{1/10} for small θ_eq; followed more closely as R₀/ξ grows (spherical-cap initializations, R₀ up to 150); prefactor decreases with R₀, consistent with ξ acting as an effective slip length ~1/[log(R₀/ℓ_s)]^{1/10} — stated as suggestive, not quantitatively closed.

No porous-medium, capillary-filling, imbibition, or multi-droplet configuration is validated or even demonstrated.

## Assumptions and validity range

- **Density-matched fluids** (ρ₀ = 1 everywhere; p = c_s²ρ, no phase EOS): liquid–gas density contrast is outside the formulation — same structural limitation as kusumaatmaja2010; only viscosity contrast is representable (λ = 10 demonstrated).
- **Flat-wall wetting only**: Π(h) is defined on the *vertical* distance to a planar substrate, and the A(θ_eq) closure (29) is derived in a flat-wedge limit. Extension to curved/rough grain surfaces (distance-to-nearest-solid generalization) is not given and would invalidate the analytic closure as-derived.
- **Closed single interface, fixed mesh topology**: the IB triangulated-mesh representation cannot undergo breakup, coalescence, or film merging without remeshing machinery the paper does not provide. Pore-scale imbibition through a granular bed is dominated by exactly such topology changes.
- **No true contact**: interface rides at standoff δ ≈ ξ above the wall; contact radius is protocol-dependent (z_cut or ε), with results sensitive to the protocol parameter at early times.
- Closure accuracy requires ξ/R₀ ≪ 1 (wedge limit); degrades for acute angles at finite ξ/R₀ (Fig. 8). Tanner-regime behavior additionally requires large R₀/ξ separation.
- Isothermal, Newtonian, no solute transport/dissolution, no evaporation, no contact-angle hysteresis, no gravity in any reported run.
- Silent on: random porous geometry, trapped-gas compression, dynamic contact angle laws (no Cox-type closure offered), physical-unit mapping.
- Cost datum: 0.5–12 h per spreading run on an NVIDIA A100 64 GB.

## Interface mapping

Inputs consumed: none of the v0.1 contracts. A hypothetical pore-scale study would need voxel/surface geometry from brewer2026.pack_generator plus hot-water-on-coffee σ and θ_eq (held nowhere in the registry).
Outputs produced: nothing writing BedState/ShotResultState.
Couplings: offline calibration chain at most. Implementation would be a major departure from brewer2026.lb_reference/lb_taichi — the D3Q19 BGK core is shared, but the method adds a Lagrangian mesh, FEM strain-energy surface tension, 4-point IB spreading/interpolation, per-step ray tracing for the τ field, and the Π(h) wall force. Solver rewrite, not an adapter. **Route note:** third competing method route for the unsaturated-wetting contingency, alongside kupershtokh2009 (pseudopotential/EOS) and kusumaatmaja2010 (free-energy binary). Unlike those, its wetting closure is substrate-geometry-specific and its interface representation cannot change topology — both disqualifying for imbibition into a random packing without substantial method development the paper does not supply.

## Extractable data

- Closure content worth keeping: A(θ_eq) relation (29); Π(h) form (26) with (n, m) = (6, 3); nodal wetting force (27); standoff δ closure (C10); measured-angle estimator (C7); h* = ξ(n/m)^{1/(n−m)}; optimal protocol values z_cut/R₀ ≈ 0.050, ε ≈ 0.1. All transcribed above — this card is the artifact; no puckworks/data/ file warranted.
- Figs. 2–5, 8 are lattice-unit verification results reproducible from the transcribed equations; digitization unnecessary.
- No raw data or code published; no availability statement in the provided copy.

## Overlaps and conflicts

- **kupershtokh2009 (implement-later)** and **kusumaatmaja2010 (implement-later)**: same contingency slot (pore-scale method reference for the "unsaturated flow at fine grinds" backlog hypothesis). Both registered routes are diffuse-interface LB, which handle topology change (invasion, film merging, snap-off) natively and take arbitrary solid geometry through standard boundary conditions; kusumaatmaja2010 additionally supplies a closure-complete wetting BC and MRT machinery. This paper's distinctive assets — sharp interface, extensible strain-energy constitutive law (elastic/viscous interfaces) — solve problems the registry does not have. Competes; does not supersede; adds no capability the contingency needs.
- **wang2027 (skip)**: analogous situation — wetting-method paper in the wrong configuration for the registry; the skip logic transfers.
- **brewer2026.lb_reference / lb_taichi (flow, calibration)**: shared D3Q19 BGK core only; adopting this method is a rewrite, not an extension (contrast kusumaatmaja2010, which is a collision/BC extension of the existing solver).
- **foster2025.infiltration (infiltration, runtime)**: nominally the same physical stage, but this paper contains no capillary-filling or imbibition physics (no Lucas–Washburn analysis, unlike kusumaatmaja2010), so it offers no test of Foster's sharp-front assumption even in principle without major development.
- Competes with nothing runtime-registered.

## Implementation estimate

Not implementable as a registry component (no coffee-relevant observable; writes no contract). Even if the unsaturated-wetting hypothesis graduates, this route should not be the one built: the flat-wall Π(h) closure and fixed-topology mesh make it structurally worse-suited to imbibition into random granular geometry than the two diffuse-interface routes already held, and building it would be a full solver rewrite (mesh + FEM + IB + ray tracing) — effort L — for capability the registry can get at effort M by extending lb_reference along the kusumaatmaja2010 route. If a single-droplet-on-flat-substrate question ever entered scope (it is not on the backlog), the verification gates would be: (i) statics E_L2 vs the (B4) ODE across θ_eq and ξ/R₀ (target ≤ 0.01 at N_t = 40 000); (ii) measured-vs-imposed angle per (C7) tracking Fig. 8; (iii) t^{1/2} and t^{1/10} spreading regimes.

VERDICT: skip — third method route for the unsaturated-wetting contingency that is structurally worse-suited than the two already carded (flat-wall-specific wetting closure, topology-fixed sharp interface, density-matched fluids, no imbibition physics, no data or code) — effort L (if ever built, which is not recommended)
