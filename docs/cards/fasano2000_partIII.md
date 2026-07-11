# Model card: Fasano 2000 Part III — comprehensive multi-species model with diffusion and compact layer

**Paper/thesis:** Fasano A., Talamucci F., Petracco M., "The Espresso Coffee Problem," ch. 8 (§8.5) in A. Fasano (ed.), *Complex Flows in Industrial Processes*, Springer, pp. 241–280 (2000). DOI not printed in the scan. Full model in their ref [22] (Fasano & Talamucci, SIAM J. Math. Anal., "to appear") and [29] (Talamucci 1998).
**Stage(s):** bed_dynamics, extraction, flow · **Kind:** runtime
**Status:** proposed (card-only)

## Scope and mechanism
Union of Parts I and II: k fine-particle species (convected, threshold removal, repacking into a compact layer behind free boundary s(t)) plus n−k soluble species (extracted without threshold, convected *and* diffusing), with porosity evolving from mass loss (flow-induced compression/elastic response of Part II dropped here) and an exact overall volume balance. The multi-species compact layer requires a packing constraint because the layer composition M₁,…,M_k now depends on process history. This is the paper's "everything coupled" formulation; the chapter proves local-then-global existence/uniqueness under smallness conditions and extracts a few qualitative properties.

## Governing equations
Their (8.96)–(8.114), nondimensional; only the structure that would be implemented:

1. Particle species (i = 1,…,k), active region D_T only: ∂mᵢ/∂t + ∂/∂x( αᵢ mᵢ q/ε ) = −∂bᵢ/∂t (8.96); removal with threshold ∂bᵢ/∂t = −Fᵢ(q,b) Gᵢ[bᵢ − βᵢ(q,b)]⁺ (8.99).
2. Soluble species (i = k+1,…,n), everywhere (extraction continues inside the compact layer): ∂mᵢ/∂t + ∂/∂x( −Dᵢ ε ∂/∂x (mᵢ/ε) ) + ∂/∂x( mᵢ q/ε ) = −∂bᵢ/∂t (8.97), from molecular velocity mᵢV_{mᵢ} = mᵢV − Dᵢ ε ∂/∂x(mᵢ/ε) (8.92, interdiffusion neglected); extraction without threshold ∂bᵢ/∂t = −Hᵢ(q,b) (8.100).
3. Darcy: q = −K(b,m,ε) ∂p/∂x (8.98).
4. Porosity rate: ∂ε/∂t + ∂q/∂x = −∂θ^(k)/∂t (8.101), θ^(k) = Σ_{i>k} bᵢ/ρᵢ; total-volume conservation of moving components: ∂q/∂x + ∂/∂x Σ_{i≤k} αᵢηᵢ q/ε = 0 (8.102), ηᵢ = mᵢ/ρᵢ.
5. Compact layer packing constraint: Σ_{i≤k} Mᵢ/ρᵢ = Θ (8.94), Θ a known critical specific volume; free-boundary speed (Θ − (η_(k)+θ_(k))) ṡ = −(q/ε) Σ_{i≤k} αᵢηᵢ at x = s(t) (8.111).
6. Interface/boundary conditions (8.106)–(8.113): mᵢ(0,t)=0 for particles; zero solute velocity at inlet (8.107); continuity of mᵢ/ε and of diffusive flux across s(t) (8.109–8.110); diffusion neglected at outflow (8.112); [[p]] = 0 (8.108); p(0,t) = p₀(t) > 0, p(1,t) = 0.
7. Initialization: q₀(x) computable in closed form (8.126); inlet flux f(t) = q(0,t) from a pressure-integral compatibility (8.125).

Well-posedness: Theorem 8.4, unique solution provided (i) a compound smallness condition on initial fines inventory and removal-rate norm vs Θ, (ii) p₀^M(1+C₁)²|∂K/∂q| < 1, (iii) Lipschitz constants of the data sufficiently small. Qualitative endpoint: in the stagnant region S₁, with K = K(b,m), removal can restart if and only if p₀(t) increases; if ∂K/∂ε ≥ 0 rising pressure can restart removal even in cases Part I cannot predict (§8.5 conclusions).

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| Fᵢ, Gᵢ, βᵢ, Hᵢ | functional forms only | scaled | assumed |
| Dᵢ (solute diffusivities) | not provided | scaled | not provided |
| Θ (critical packing volume) | not provided; constraint (8.120) | — | not provided |
| ρᵢ, αᵢ | not provided; ρᵢ^(b)=ρᵢ^(m)=ρᵢ assumed | — | assumed |
| K(b,m,ε) | not provided; K_m ≤ K ≤ K_M | — | assumed |

## Calibration and validation offered by the source
None. No comparison to any measurement or simulation for this model in the chapter. Pure existence/uniqueness mathematics plus qualitative remarks.

## Assumptions and validity range
- Saturated, 1D, incompressible; flow-induced compression and elastic response (Part II's g, h terms) dropped; interdiffusion neglected; diffusion neglected at the outflow face; equal bound/dissolved densities per species.
- Extraction kinetics Hᵢ(q,b) is a generic C¹ function — no intragrain diffusion, no surface-dissolution nonlinearity, no solubility ceiling. Far below cameron2020 fidelity for the extraction stage.
- Uniqueness proved only under smallness conditions (i)–(iii); the authors note initial data satisfying the naive condition (8.128) can still violate the packing bound later, spawning a *second* free boundary the theory does not cover — a real failure mode for simulation.
- Silent on: temperature, headspace/pump, wetting.

## Interface mapping
Inputs consumed: BedState, GrindState.fines_fraction, MachineState.P_of_t (p₀(t) native).
Outputs produced: would produce ShotResultState (solute mᵢ outflow → TDS/EY) plus q(t), s(t), ε(x,t).
Couplings: forces runtime coupling of bed_dynamics + extraction + flow into one monolithic free-boundary system — precisely the mega-model failure mode the registry avoids. Everything it offers is available by composing: Part I (fines + compact layer) + Part II's porosity law + cameron2020 (extraction, at much higher chemical fidelity) + foster2025 (wetting). Adapters would need per-cell multi-species inventories not in contracts v0.1.

## Extractable data
None. No tables, figures with data, or code.

## Overlaps and conflicts
- Competes with cameron2020.extraction_bdf and loses on extraction fidelity (generic Hᵢ vs measured two-population kinetics with microstructure tables); its only extraction novelty — extraction continuing inside the compact layer — is a small correction that could be added to a Part I implementation if ever warranted.
- Supersedes Parts I and II formally but not usefully: it inherits their unidentified parameters, adds Dᵢ, Θ, ρᵢ, and removes Part II's compaction terms.
- The multi-species packing constraint (8.94) and the second-free-boundary caveat are the genuinely new ideas; note them in the fasano2000_partI card's future-work rather than implementing here.
- The Hᵢ-driven porosity source in (8.101) overlaps the backlog "infiltration↔extraction coupling" and "kappa(t)" items only indirectly; both are better served by the dedicated cards.

## Implementation estimate
L: coupled hyperbolic + parabolic (diffraction-type) + free boundary + two integral compatibility conditions, with an unhandled second-free-boundary regime. No data exists to gate it. Not worth building.

VERDICT: skip — a forced monolith that reproduces registered components at lower fidelity with zero parameters and zero validation; its two novel ideas (multi-species packing constraint, extraction inside the compact layer) are noted on the Part I card for future use — effort L
