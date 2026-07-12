# Model card: Ellero 2019 SPH mesoscopic extraction (conference version)

**Paper:** Ellero, M. & Navarini, L., "Simulation of espresso coffee extraction using Smoothed Particle Hydrodynamics," Proc. PARTICLES 2019 (VI Int. Conf. on Particle-Based Methods), pp. 68–79. No DOI on the proceedings copy. NOTE: this is the short conference companion to the fuller journal paper, Ellero & Navarini, J. Food Eng. 263, 181–194 (2019) (their ref. [14]), which adds intra-granular solute transport fully coupled.
**Stage(s):** flow, bed_dynamics, extraction · **Kind:** calibration (mesoscopic reference simulation; runtime coupling would be forced)
**Status:** card-only

## Scope and mechanism
2D SPH (Lagrangian meshless Navier–Stokes) simulation of a coffee bed at grain scale. Three dispersed phases by size: fixed solid grains (~450–500 µm) as immobilized SPH particle regions; "fines" (~30 µm) as single mobile SPH particles that are passive tracers in the bulk but immobilize on entering a filter buffer layer, adding mechanical impedance; molecular solutes (~1–10 nm, e.g. caffeine) as a continuum concentration field per SPH particle with solid→liquid release. The central result: fines migration to and accumulation in the filter reproduces the reversible transient permeability decay seen in direct/inverse discharge experiments, and the resulting slow flow raises residence time and cumulative solute output. Release rate D_r, not bulk diffusion D_b, dominates in-cup concentration.

## Governing equations
Their Eq. (1), SPH-discretized isothermal Navier–Stokes (Lagrangian):

  ṙ_i = v_i
  m v̇_i = −Σ_j (p_i/d_i² + p_j/d_j²) W′_ij e_ij + 4 Σ_j η̄_ij (W′_ij / (d_i d_j r_ij)) v_ij + g_i

with W_ij = W(r_ij) a kernel and W′_ij its radial derivative; r_ij = r_i − r_j, e_ij = r_ij/r_ij; v_ij = v_i − v_j; η̄_ij = (η_i + η_j)/2 the pair-averaged dynamic viscosity; p_i particle pressure from the ideal EOS p_i = c_s²(ρ_i − ρ_0), ρ_i = m d_i, d_i = Σ_j W_ij the number density, c_s an artificial sound speed chosen ≫ flow velocity; g_i external body force (used to impose the pressure drop, F = Δp/(L_y ρ)).

Their Eq. (2), solute advection–diffusion (advection implicit in Lagrangian motion):

  ċ_i = 4 Σ_j D̄_ij (W′_ij / (d_i d_j)) (c_ij / r_ij)

with c_ij = c_i − c_j, D̄_ij = (D_i + D_j)/2. Pair-dependent D̄ encodes three coefficients: bulk diffusion D_b (liquid–liquid pairs), release rate D_r (solid–liquid interface pairs), intra-granular D_s (solid–solid; set to zero in this paper). Antisymmetry of the summand conserves solute mass exactly.

Sub-models without equations: no-slip via zero-velocity boundary particles interacting through Eq. (1); fines as single-SPH-particle solids (Pan et al. DPD minimal model, their ref. [17]) with hydrodynamic radius ≈ kernel cutoff r_c, passive in bulk; filter as a buffer layer of finite thickness that converts entering fines into fixed boundary particles.

## Parameters
All simulation values are dimensionless (SPH units); the only SI anchor is the viscous time conversion.

| symbol | value | units | source |
|---|---|---|---|
| d_grain (physical) | ~450–500 | µm | nominal |
| d_fine (physical) | ~30 | µm | nominal |
| d_grain (sim) | 2.0 (16 SPH particles/diameter) | sim | nominal |
| φ (coarse solid fraction) | 0.48 | – | nominal |
| θ (fines volume fraction) | 0.001–0.01 (swept); 0.0058 matches experiment | – | fitted (θ=0.0058 tuned to transient flow data) |
| Bed thickness | 2 cm physical; L_y = 80 sim (L_y/d_grain = 40) | – | nominal |
| Domain | L_x × L_y = 10 × 80, N = 51,200 particles, 2D | sim | nominal |
| ρ | 1 | sim | nominal |
| µ | 3 | sim | nominal |
| F (body force ≡ Δp/(L_y ρ)) | 2000 | sim | nominal (tuned to Re_max ≈ 10) |
| Re_max | ≈ 10 (fines-free) | – | nominal, "matching experimental conditions" |
| c_s | 500 | sim | nominal (numerical) |
| D_b | 0.005–0.1 (Pe 600–6000) | sim | assumed |
| D_r | 0.0005–0.02 | sim | assumed |
| D_s | 0 | sim | assumed (nonzero only in journal version) |
| τ_ν = d_grain²/ν | 1.33 sim = 0.16 s SI | s | nominal conversion |

No SI permeability, pressure, or concentration values are provided anywhere; solute output is reported as mass-percent in dimensionless time.

## Calibration and validation offered by the source
Hydrodynamics only, and qualitative. The direct/inverse discharge Re(t) at θ = 0.005–0.006 is overlaid on experimental transient-discharge data (their refs. [13] Petracco & Suggi Liverani 1993 ASIC; [18] Bandini et al. 1997 ASIC; [12] Navarini et al. 2009), claimed as "substantial agreement": ~one order of magnitude flow decay (Re 10 → ~1) with the right slow relaxation time, and the fines-migration timescale τ*_m ≈ 7.1 matches the observed transient decay. The initial experimental ramp was removed before comparison (finite pressure rise time in experiment vs. instantaneous in simulation). No quantitative error metric, no uncertainty, single fitted θ. The concentration-dynamics results (Figs. 3–4) are purely exploratory parameter sweeps with no experimental comparison. θ = 0.0058 is a fit to the flow data, so the "agreement" at that θ is partly circular; the genuinely predictive content is the shape/timescale of the transient and its reversibility under flow inversion.

## Assumptions and validity range
- 2D, periodic in the transverse direction; fully saturated from t = 0 (no wetting/infiltration stage).
- Grains rigid and fixed: no swelling, no compaction, no erosion — the paper's own intro lists swelling (their phenomenon A) as important, then omits it.
- Fines are passive tracers in the bulk: no fines–flow feedback, no pore clogging inside the bed, no fines–fines interaction; all impedance arises at the filter buffer. Deposition is binary and only at the filter.
- Single fitted θ; fines do not deplete from the grains (fixed initial population).
- D_s = 0: release limited to near-surface solute; no intra-granular depletion physics (journal version relaxes this).
- Dimensionless throughout; mapping to a specific machine/basket requires re-anchoring every parameter.
- Isothermal; no viscosity increase from dissolved solids; no lipids/emulsification (their phenomenon C acknowledged, not modeled).
- Silent on: tamped-bed stress state, headspace/pump dynamics, unsaturated flow, EY accounting (output is compound-to-total mass ratio, not extraction yield of an inventory).

## Interface mapping
Inputs consumed: none of the v0.1 contracts directly — a grain-scale geometry (buildable from brewer2026.pack_generator output) plus dimensionless forcing. Outputs produced: nothing that lands in ShotResultState without a full re-dimensionalization layer.
Couplings: strictly offline calibration. Plausible chain: pack_generator geometry → SPH (or LB) transient run → effective κ(t; θ) curve → informs a future bed_dynamics κ(t) closure. Runtime coupling (SPH inside the shot chain) is the mega-model failure mode and is not proposed. Adapters needed: 2D→3D justification, sim-units→SI anchoring, fines-population ↔ GrindState.fines_fraction mapping — all nontrivial.

## Extractable data
**Figs. 2–4 DIGITIZED 2026-07-12 → `data/ellero2019/`** (Tim drop; pixel
extraction, axis fit <1px; loaders `ellero_fig2_*/fig3_*/fig4_*`; 3 MANIFEST rows;
smoke test). **QUALITATIVE / figure-digitized strength only** — these are the SPH
model's OWN output in dimensionless simulation units with nominal parameters
(they characterize the model, not coffee), plus the fig2 Ref.[8] experimental
markers overlaid on it. θ=0.0058 is a fit to the flow data (circular at that θ).
The digitized set reproduces the card's mechanism qualitatively: direct-discharge
Re decays ~10→~1 and DEEPENS monotonically with θ (fines fraction) as fines
accumulate in the filter (fig3), and in-cup caffeine content rises with release
rate Dr, weakly with bulk diffusion Db (fig4). **Does NOT close G2:** the raw
experimental transient-discharge series (refs. [13] Petracco 1993 / [18] Bandini
1997, ASIC proceedings) is still owed — the digitized simulation curves are a
qualitative pointer for the fines-migration mechanism, not a validation dataset.
No code released. The journal version (J. Food Eng. 263, 2019) remains the copy
worth intaking for equations and the D_s-coupled results.

## Overlaps and conflicts
- **brewer2026.streamtube (Rung B fines migration):** direct mechanistic complement/competitor. This paper is independent support that fines migration alone produces reversible transient permeability — but via filter accumulation, not intra-bed tube redistribution. Useful citation for the Rung B hypothesis; does not validate it.
- **Backlog: κ(t) = κ0·f(P, ε, E) bed_dynamics:** this is a third competing mechanism (fines-at-filter) alongside compaction/swelling and intra-bed migration for the rising-flow residual. The reversibility-under-flow-inversion signature is a discriminating prediction: swelling is irreversible, filter-trapped fines are not.
- **brewer2026.lb_reference / lb_taichi:** methodological overlap (mesoscale flow solver). LB twins already cover fixed-geometry flow at higher verification standard (0.003–0.05%); SPH's marginal value is moving fines, which LB could also host.
- **cameron2020.extraction_bdf:** much lower chemical fidelity here (surface release only, D_s = 0, no inventory/EY accounting) — does not compete. The multi-compound D_r framing gestures at the backlog item "multi-class solute chemistry" but supplies no compound-specific parameters.
- **foster2025.infiltration:** disjoint (this model assumes saturation from t = 0).

## Implementation estimate
Reimplementing the SPH framework: L (custom weakly-compressible SPH with solid boundaries, single-particle fines, buffer filter; then a re-dimensionalization and 3D-credibility study before any output is usable). No code or data to bootstrap from. If the fines-transport mechanism is wanted, a mass-conserving deposition term in the existing LB calibration stack or the backlog 5-state transport model is cheaper than a new solver. Gate design would be blocked anyway: the validation targets (refs. [13], [18]) are not in hand.

VERDICT: skip — 2D, dimensionless, qualitatively-validated conference short of a fuller journal paper, with no code and no transcribable data; intake Ellero & Navarini J. Food Eng. 263 (2019) instead and cite this one as independent support for the fines-migration mechanism in bed_dynamics. — effort L
