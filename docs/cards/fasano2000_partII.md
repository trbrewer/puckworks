# Model card: Fasano 2000 Part II — multi-species removal with porosity (compaction/swelling) dynamics

**Paper/thesis:** Fasano A., Talamucci F., Petracco M., "The Espresso Coffee Problem," ch. 8 (§8.4) in A. Fasano (ed.), *Complex Flows in Industrial Processes*, Springer, pp. 241–280 (2000). DOI not printed in the scan. Underlying analysis in their refs [16], [19] (Fasano & Primicerio).
**Stage(s):** bed_dynamics · **Kind:** runtime
**Status:** proposed (card-only)

## Scope and mechanism
Generalizes Part I to n species removed simultaneously, and lets porosity ε(x,t) evolve under three effects: dilation from mass loss, flow-induced compaction (friction of the fluid on grains), and elastic recovery of the medium. Deliberately drops the compact layer (all transported particles exit the bed) to isolate the removal–flow–matrix interaction; macroscopic deformation neglected while micrometric grain rearrangement changes porosity. This section is the paper's constitutive answer to "why does the bed's resistance depend on flow history?" — i.e., the registry's compaction/swelling hypothesis, in PDE form.

## Governing equations
Nondimensional system, their (8.67)–(8.71) with data (8.72)–(8.75):

1. Species transport (8.67): ∂mᵢ/∂t + ∂/∂x( αᵢ (q/ε) mᵢ ) = −∂bᵢ/∂t, i = 1,…,n; αᵢ = 1 for solutes, αᵢ ≤ 1 for solid particles.
2. Removal kinetics (8.68): ∂bᵢ/∂t = −Fᵢ(q,b) Gᵢ( b − βᵢ(q,b) ); Fᵢ bounded, Fᵢ(0)=0; Gᵢ(ζ)=0 for ζ ≤ 0, positive bounded for ζ > 0; βᵢ may depend on the whole vector b (species interactions, e.g. fat coatings); βᵢ′ ≤ 0.
3. Porosity evolution (8.69): ∂ε/∂t = −Σᵢ δᵢ ∂bᵢ/∂t − g(q) ξ₁(ε − ε_*(q,b)) + h(q) ξ₂(ε*(b) − ε). Terms: mass-loss dilation (δᵢ ≥ 0 constants); flow-induced compaction toward lower bound ε_*(q,b) (g increasing, g(0)=0; ξ₁ = 0 for negative argument, positive increasing otherwise); elastic recovery toward upper bound ε*(b) (h ≥ 0, need not vanish at q=0; ξ₂ like ξ₁). ε_*, ε* bounded away from 0 and 1.
4. Volume balance (8.70): ∂ε/∂t + ∂q/∂x = 0 (rate of change of solute-occupied volume neglected; q now depends on x).
5. Darcy (8.71): q = −K(m,b,ε) ∂p/∂x — permeability responds to porosity.
6. Data (8.72–8.75): bᵢ(x,0) = b_{i,0}(x) > 0 (nonuniform allowed), mᵢ(x,0) = m_{i,0}(x) ≥ 0, m(0,t) = 0, ε(x,0) = ε*(b₀), p(0,t) = p₀(t) (time-dependent allowed), p(L,t) = 0.
7. Initial flux is not data: q(x,0) is determined uniquely by a nonlinear ODE ∂q/∂x = Γ(q,ε,b) (8.76–8.77) plus the pressure-integral compatibility ∫₀¹ q/K dx = 1 (8.78) — Lemma 8.4. Any implementation must include this initialization step.

Well-posedness (Theorem 8.3): unique global solution *provided* the q-derivatives of all constitutive functions are "sufficiently small" (condition 8.86) — the authors read this physically as the coefficients having to vary slowly with q to keep the medium saturated.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| Fᵢ, Gᵢ, βᵢ | functional forms only, properties as above | scaled | assumed |
| δᵢ (dilation weights) | not provided | scaled | not provided |
| g(q), h(q), ξ₁, ξ₂ | functional forms only | scaled | assumed |
| ε_*(q,b), ε*(b) | not provided; bounded away from 0, 1 | — | not provided |
| αᵢ | 1 (solutes), ≤ 1 (particles) | — | nominal |
| K(m,b,ε) | not provided; 0 < K_m ≤ K ≤ K_M | — | assumed |

No numeric value for any constitutive function anywhere.

## Calibration and validation offered by the source
None. No experiment, no simulation, no figure is compared against this model in the chapter. The section is a well-posedness study. Say it plainly: this is an untested constitutive skeleton.

## Assumptions and validity range
- No compact layer: all mobilized particles exit the bed. Wrong for a real basket/pod outlet that retains fines — Part II alone cannot reproduce the Part I flow-decay observations for espresso; its value is the porosity law, not the transport truncation.
- Saturated, 1D, incompressible; solute volume change neglected in (8.70) (valid when dissolution-freed volume ≫ dissolving-substance volume).
- Macroscopic deformation neglected; porosity change is sub-grid rearrangement.
- Existence needs slowly-varying coefficients (8.86) — steep constitutive laws are outside the proven regime and may signal loss of saturation.
- Silent on: temperature, compact-layer physics, grind linkage of the constitutive functions.

## Interface mapping
Inputs consumed: BedState (porosity, k), MachineState.P_of_t (p₀(t) enters directly).
Outputs produced: ε(x,t), hence kappa(t)/k(t) evolution → BedState updates; q(x,t) traces.
Couplings: the natural registry use is to lift equation (8.69) + (8.70)–(8.71) as the **kappa(t) = kappa₀·f(P, eps, E) closure** named in the backlog (compaction from g·ξ₁, swelling/elastic recovery from h·ξ₂, dissolution dilation from δᵢ terms), driven by whatever removal/extraction component is active — rather than adopting the full n-species transport. Adapters: constitutive functions must be parameterized (none provided); porosity field would need a per-depth-cell representation the current BedState scalar contract lacks.

## Extractable data
None. No tables, no fitted curves, no code.

## Overlaps and conflicts
- Supplies the only concrete PDE form on file for the backlog item "pressure/history-dependent permeability kappa(t) (compaction/swelling — competing explanation for rising-flow residual)". Cite it as the source of that closure's structure.
- Competes with Part I (fines migration) as the mechanical explanation of history-dependent resistance; the Fig. 8.4 reversal experiment of Part I discriminates (compaction alone would not replay the decay on inversion in the same way counter-migration does).
- Complements wadsworth2026.permeability: k(ε) there is static/untamped; (8.69) is a dynamic ε law that could drive it — but coupling them is speculative and both closures are unvalidated in the tamped regime.
- The qualitative endpoint result of Part III (§8.5 conclusions) is relevant here: with K = K(b,m) only, the flux can rise again only if p₀(t) increases; with ∂K/∂ε ≥ 0, removal may restart under rising pressure — a testable signature for profiled shots.

## Implementation estimate
As written: L (n-species hyperbolic system + ODE porosity + nonstandard initial-flux ODE + compatibility integral), unjustified given zero data. As a lifted kappa(t) closure (single cell or few cells, eqs. 8.69–8.71 with 2–3 fitted constants): S–M, and that is the recommended path. Gate design: fit compaction/swelling constants to the rising-flow residual on DE1 fixture A; discriminate against the Part I fines explanation via a pressure-step or reversal protocol.

VERDICT: implement-later — worthless as the full n-species system, but its porosity-evolution law (8.69) is the registry's named compaction/swelling closure in concrete form and should be the template when the kappa(t) backlog item is picked up — effort M
