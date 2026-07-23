# Model card: dandachi2025 — EspressoSimulations.jl blog draft (multiscale DAE extraction)

**Paper/thesis:** T. Dandachi ("torque"), "Simulating Espresso Extraction," personal blog (torque's blog), 12 January 2025. No DOI; non-peer-reviewed community source. **The post is an unfinished draft**: visible TODO markers throughout, unresolved "insert reference here" placeholders, empty install/usage sections, and a references list containing "TODOTODOTODO". The announced Julia package (EspressoSimulations.jl) has **no working link** — reference [1] reads "Github link to package (update this 1 later)".
**Stage(s):** extraction · **Kind:** runtime (as intended by the author; nothing is deliverable)
**Status:** proposed → skip

## Scope and mechanism
A hobbyist reimplementation plan for a multiscale homogenized reaction–advection–diffusion espresso extraction model, explicitly formulated after Moroney et al. 2015 (Chem. Eng. Sci. 137 — the author's ref [3] and stated primary model source) with flow assumptions borrowed from Cameron et al. 2020 (their ref [2]). Structure: a 1D puck-axis (z) advection–diffusion problem for liquid-phase solute concentration, coupled to per-grain-size 1D spherical intragranular diffusion (shells along grain radius), for N discrete grain sizes (nominally 2: coarse + fine). The coupled system is discretized by finite differences into an index-1 differential-algebraic system with a sparse singular constant mass matrix, to be solved with Rosenbrock methods (Rosenbrock23 / Rodas5P) via DifferentialEquations.jl. This is precisely the model class already registered as `cameron2020.extraction_bdf` and carded as `moroney2016` (the asymptotic reduction of the same parent).

## Governing equations
**Cannot be transcribed: the equation bodies are absent from the source.** The post's LaTeX blocks are unrendered/blank in the published draft; only the surrounding prose survives. What the prose establishes (no equation numbers exist; no symbols are fully defined even in prose):

- (D1, described) A dimensionless per-grain-size "rate of reaction" proportional to the difference between grain-surface solute concentration and liquid concentration — i.e. linear interfacial mass transfer driven by (c_surface − c_liquid). A dimensionless saturation parameter multiplies this, described as encoding the saturation concentration attainable immediately outside a grain.
- (D2, described) An "inverse mass-transfer Biot number" β̃ scaling solid-side vs interface flux, computed from a Brunauer–Emmett–Teller (BET) surface-area normalization (formula not shown).
- (D3, described) A liquid-phase reaction–advection–diffusion equation in Darcy flux u and effective diffusivity, with u assumed steady and z-only (radial/angular terms dropped by symmetry). Called "a generalized equation of [unresolved ref]" following a lithium-ion-battery multiscale paper (uncited). Body missing.
- (D4, described) Per-grain-size local volume fraction from BET area and particle radius — stated as (sphere volume / sphere surface area) × BET area, i.e. (r/3)·A_BET. Body missing.
- (D5, described) Intragranular spherical shell diffusion per grain size, with a signed inter-shell flux J between adjacent shells and boundary conditions at grain center and surface. Bodies of the PDE, the flux definition, and both BCs are all missing. The author flags an unresolved symbol collision between the radial variable and grain radius ("TODO: differentiate between r variable and grain radius").

No closures for permeability, pressure–flow coupling, or the Darcy flux magnitude are given anywhere; u is an unspecified input. Per house rules nothing is reconstructed here from the parent papers — a card must transcribe what the source states, and this source states prose only.

## Parameters
| symbol | value | units | source (measured/fitted/nominal) |
|---|---|---|---|
| — | not provided | — | none: the draft contains **zero** numeric parameter values |

Number of grain sizes is nominally 2 (coarse/fine, motivated by the bimodal PSD figure reproduced from Uman et al. 2016); extensible to N. That is the only quantitative modeling choice stated.

## Calibration and validation offered by the source
None. No comparison to any measurement, no simulated shot output shown, no fitted values, no reproduction of a literature curve. The only performance claim is numerical: Rodas5P is "a factor of 10 faster" than the DifferentialEquations.jl default on this DAE — a solver benchmark, unverifiable without the (unpublished) code, and not a validation of physics.

## Assumptions and validity range
As listed by the author: incompressible flow and constant viscosity (following Cameron 2020); at t = 0 the bed is fully wetted/pre-infused and saturated with zero liquid-phase solute (following Moroney); steady homogeneous two-phase flow; radial symmetry → 1D puck; local (pointwise) transfer operator; isothermal puck; static puck (constant diffusivity, surface areas, height, geometry); drink density = water (author self-flags this as questionable); exactly two dominant PSD modes.
Inherited failure modes of the parent class (unaddressed): no infiltration/unsaturated stage, no bed compaction/swelling or fines migration, no channeling, single lumped solute, no temperature dependence, no flow–extraction feedback. Additionally silent on: how u is obtained at all (no Darcy/permeability closure), basket exit resistance (an explicit TODO section), and every parameter value.

## Interface mapping
Inputs consumed (intended): would need BedState (depth, porosity), GrindState (two grain radii + BET areas — an adapter beyond the current contract, same gap as moroney2016's Sauter-diameter needs), and a Darcy flux the post never derives (MachineState → u closure absent).
Outputs produced (intended): liquid-phase exit concentration → ShotResultState traces.
Couplings: none realizable — with no equations, no parameters, and no code artifact, there is nothing to couple. Were the package ever published, it would compete for the runtime extraction slot occupied by `cameron2020.extraction_bdf`.

## Extractable data
Nothing. The only figure with data content is reproduced from Uman et al. 2016 (Sci. Rep. 6:24483 — bimodal PSD vs bean temperature), which should be acquired from its primary source if the grind backlog ("PSD models beyond bimodal") ever wants it; do not transcribe it from this blog. No tables, no raw data, no code (link placeholder only). The one salvageable implementation note — mass-matrix index-1 DAE formulation with Rosenbrock solvers (Rodas5P) as a fast alternative to BDF for this model class — is preserved by this sentence and needs no data file.

## Overlaps and conflicts
- **cameron2020.extraction_bdf (extraction, runtime):** duplicated at strictly lower fidelity — same model family, but Cameron is registered, parameterized, and validated; this draft has no equations, parameters, or validation. Competes for nothing in its current state.
- **moroney2016 (extraction, calibration card):** the parent formulation (Moroney 2015) that this post follows is the same one the registry already flags as a higher-value acquisition target. This blog is not a substitute for acquiring Moroney 2015 itself.
- **Backlog items:** touches none. The TODO sections on baskets/output pressure gesture at the G9 screen-resistance question but contain no content.
- Supersedes nothing; superseded (pre-emptively) by everything registered in the extraction stage.

## Implementation estimate
Nothing to implement and nothing to gate against — no equations, no parameters, no data, no code. Revisit only if the author publishes EspressoSimulations.jl with source and a completed writeup; even then the bar is showing something `cameron2020.extraction_bdf` does not already do (the DAE/Rosenbrock numerics alone would not clear it).

VERDICT: skip — an unfinished blog draft of a Moroney/Cameron-class multiscale extraction model with unrendered equations, zero parameter values, zero validation, and an unpublished package link, adding nothing over registered components beyond a solver-choice anecdote — effort S.
