# Model card: Ellero & Navarini 2019 — SPH mesoscopic espresso extraction (journal version)

**Paper:** Ellero, M. & Navarini, L., "Mesoscopic modelling and simulation of espresso coffee extraction," *Journal of Food Engineering* **263**, 181–194 (2019). DOI 10.1016/j.jfoodeng.2019.06.008. (Uploaded copy is the accepted manuscript, `paperJFE.pdf`; line/figure numbers below refer to that manuscript.)
**Stage(s):** flow, bed_dynamics, extraction · **Kind:** calibration (mesoscopic reference simulation; runtime coupling into the shot chain would be forced)
**Status:** card-only

**Relation to the existing `ellero2019` card.** That card covers the PARTICLES 2019 conference short and explicitly flags this journal paper as "the copy worth intaking." This card is that intake and **supersedes** it: same solver, same Eqs. (1)–(2), same fines/filter model, same fitted θ. What is new here is (i) intra-granular diffusion `D_s` switched on and swept, and (ii) a comparison against experimental per-compound extraction kinetics (Fig. 13) plus a simulated compound-proportion table (Table II). Recommend keeping one Ellero card and marking `ellero2019.md` superseded rather than carrying both.

## Scope and mechanism
2D weakly-compressible SPH (Lagrangian meshless Navier–Stokes) of a coffee bed resolved at grain scale, with three dispersed phases separated by length scale: fixed coarse grains (≈450–500 µm) as immobilized SPH particle regions; "fines" (≈30 µm) as single mobile SPH particles, passive tracers in the bulk that are converted to fixed boundary particles on entering a filter buffer layer at the outlet; molecular solutes (≈1–10 nm) as a per-particle scalar concentration field. Solute transport is a **double-porosity** advection–diffusion problem: a single discretized diffusion equation is solved over the whole domain (solid and liquid) with a pair-dependent diffusivity encoding bulk diffusion `D_b` (liquid–liquid pairs), a uni-directional "washing" release `D_r` (solid–liquid pairs), and intra-granular diffusion `D_s` (solid–solid pairs). Two results are claimed: fines migration into the filter reproduces the reversible transient permeability seen under direct/inverse discharge, and the resulting slower flow raises residence time and hence cumulative solute output; separately, per-compound `D_s` values fitted to caffeine, trigonelline and chlorogenic acid reproduce their distinct extraction-ratio kinetics.

## Governing equations

**Their Eq. (1)** — SPH-discretized isothermal Navier–Stokes, Lagrangian:

    ṙ_i = v_i
    m v̇_i = − Σ_j ( p_i/d_i² + p_j/d_j² ) W′_ij e_ij  +  4 Σ_j η̄_ij ( W′_ij / (d_i d_j r_ij) ) v_ij  +  g_i

The first sum is the conservative force F^C_ij (discrete −(∇p/ρ)_i), the second the dissipative force F^D_ij (discrete η(∇²v/ρ)_i).
Symbols: `m` constant particle mass; `W_ij = W(r_ij)` kernel, `W′_ij = ∂W/∂r|_{r_ij}` its radial derivative; `r_ij = ‖r_i − r_j‖`, `e_ij = r_ij/r_ij` unit vector; `v_ij = v_i − v_j`; `η̄_ij = (η_i + η_j)/2` pair-averaged dynamic viscosity, `η_i` the local viscosity at particle i (the formulation admits variable viscosity; here constant); `d_i = Σ_j W_ij` number density; `ρ_i = m d_i`; `g_i` body force. Pressure closes via the ideal EOS

    p_i = c_s² (ρ_i − ρ_0)

with `c_s` an artificial sound speed required ≫ all flow velocities to suppress artificial compressibility. The pressure drop is imposed as a body acceleration `F = Δp/(L_y ρ)`.

**Their Eq. (2)** — solute transport (advection is implicit in the Lagrangian motion of the carriers):

    ċ_i = 4 Σ_j D̄_ij ( W′_ij / (d_i d_j) ) ( c_ij / r_ij )

with `c_ij = c_i − c_j` and `D̄_ij = (D_i + D_j)/2`. The summand is antisymmetric under i↔j, so solute mass is conserved exactly by construction. The three-coefficient closure (their §II.C, no equation number):

    D̄_ij = D_b   for liquid–liquid pairs
    D̄_ij = D_s   for solid–solid pairs (intra-granular)
    D̄_ij = D_r   for solid–liquid pairs (interfacial "washing" release)
    D̄_ij = 0     if c_i > c_j with i fluid and j solid   ← rectifier, blocks liquid→solid back-transport

The rectifier is the only nonlinearity in the solute model and is what makes release uni-directional rather than diffusive/osmotic. Note it is a *hard switch on the sign of the pair concentration difference*, not a rate law; there is no equilibrium/partition coefficient and no saturation concentration anywhere in the model.

**Observable** (their §IV.B, unnumbered): cumulative output content = `M_compound(t)/M_tot(t)`, with `M_tot(t) = ∫₀^t ρ_0 Q̇(t) dt` and `Q̇(t) = V(t) A`. Reported in "content [%]". This is a **compound-to-cumulative-water mass ratio in simulation concentration units**, not TDS and not EY — the reported peaks (0.014–0.12 %) are not comparable to any measured espresso strength.

**Extraction ratio** (their §IV.B, Fig. 13, unnumbered): extracted mass of a compound divided by its total initial content in the dry grains. This one *is* dimensionally an EY-per-species.

Sub-models stated without equations:
- No-slip via zero-velocity boundary particles interacting through Eq. (1); solid grains are discs (2D) placed randomly to hit the target solid fraction.
- Fines: minimal single-SPH-particle solid model from DPD (their refs. 59–60), hydrodynamic radius ≈ kernel cutoff `r_c`; **no back-reaction on the flow while mobile**.
- Filter: buffer layer of unspecified thickness; a fine entering it changes identity to a fixed boundary particle permanently (until flow reversal frees it).
- Time non-dimensionalization: `τ_ν = d_grain²/ν`.

## Parameters
All simulation values are dimensionless SPH units. The only SI anchors are the physical scoping estimates (§III.A) and the `τ_ν` conversion used for Fig. 13's time axis.

| symbol | value | units | source |
|---|---|---|---|
| H (bed height, physical) | 1.85 × 10⁻² | m | nominal (from their ref. 16, Corrochano 2015) |
| R (basket radius, physical) | 1.8 × 10⁻² | m | nominal (ref. 16) |
| d_grain (physical) | 350–400 (ref. 16); up to 450–500 (illy internal report) | µm | nominal |
| d_fine (physical) | 40–50 (ref. 16); down to 30 | µm | nominal |
| H/d_grain, d_grain/d_fine | ≈ 40–50, ≈ 10–15 | – | nominal (ratios matched in sim) |
| φ (coarse solid fraction) | 0.48 | – | nominal ("conservative choice"); ⇒ porosity 0.52 |
| Q̇ (flow rate, physical) | 0.5–3 × 10⁻⁵ | m³ s⁻¹ | measured (ref. 16); cross-checked vs 2–18 mL/s in ref. 8 |
| V (interstitial velocity, physical) | 0.5–3 × 10⁻² | m s⁻¹ | derived from Q̇/(πR²) |
| ν (water, 25 °C) | 10⁻⁶ | m² s⁻¹ | nominal |
| Re = d_grain V/ν | 2–12 (≈20 if hot) | – | derived |
| D_b (physical, caffeine-class) | 2 × 10⁻⁹ | m² s⁻¹ | nominal (refs. 53, 54, 61) |
| D_r (physical) | 2 × 10⁻¹⁰ | m² s⁻¹ | nominal (ref. 54, Mateus 2007) — "10× smaller than bulk" |
| Sc = ν/D_b | ≈ 500 | – | derived |
| Pe_bulk, Pe_release | 500–5000, 5000–50 000 | – | derived |
| D_fine (Stokes–Einstein) | 1.46 × 10⁻¹⁴ | m² s⁻¹ | derived ⇒ Pe_fine ≥ 1.3 × 10⁸ (Brownian motion neglected) |
| — *simulation units below* — | | | |
| domain L_x × L_y | 10 × 80 | sim | nominal |
| N | 80 × 640 = 51 200 | particles | nominal |
| d_grain (sim) | 2.0, at 16 SPH particles per diameter | sim | nominal |
| d_fine (sim) | one particle (⇒ d_grain/d_fine ≈ 16) | sim | nominal |
| ρ | 1 | sim | nominal |
| µ | 3 (⇒ ν = 3) | sim | nominal |
| c_s | 500 | sim | nominal (numerical, ≫ V_max) |
| F ≡ Δp/(L_y ρ) | 2000 | sim | nominal, tuned to hit Re_max ≈ 10 |
| V_max | ≈ 15 | sim | derived |
| Re_max (fines-free) | ≈ 10 | – | tuned to "match experimental conditions" |
| θ (fines volume fraction) | swept 0.001–0.01; **0.0058** used for all concentration runs | – | **fitted** to the transient flow data |
| D_b | 0.005–0.1 (Pe 600–6000 at peak) | sim | assumed (sweep) |
| D_r | 0.0005–0.02 (paper text also quotes a 0.001–0.1 range) | sim | assumed (sweep) |
| D_s | 0, 0.0005, 0.005, 0.02 | sim | **fitted per compound** (Fig. 13) |
| τ_ν = d_grain²/ν | 1.33 sim = **0.16 s** SI | s | derived conversion |
| filter buffer thickness | **not provided** | – | — |
| kernel type / cutoff r_c | **not provided** | – | — |
| time step, integrator | **not provided** | – | — |
| runtime | ~1 day, single core (Xeon E5-2640 2.5 GHz) | – | reported |

Per-compound fitted intra-granular diffusivities (their §IV.B / Fig. 13): trigonelline `D_s = 0.02`; caffeine `D_s = 0.005`; chlorogenic acid "matched accurately" by "decreasing D_s" but **no value is stated** (see validation flags). `D_s = 0` is shown as the hydrophobic/lipid reference case and saturates at ≈30 % extraction.

No SI permeability, no pressure in bar, no dose, no basket, no brew ratio, no TDS, no EY appears anywhere in the paper.

## Calibration and validation offered by the source

**(a) Hydrodynamics — qualitative, with one fitted knob.** Fig. 3 overlays simulated Re(t) at θ = 0–0.006 on transient direct/inverse discharge data from their ref. 8 (Petracco & Suggi Liverani, ASIC 1993; cold water). Forcing schedule: on t\* = 0–38, off 38–55, on 55–75, off 75–90, reversed 90–140. Claims: θ = 0 gives constant permeability (agreeing with the earlier cellular-automaton work, ref. 13); θ = 0.006 gives "nearly one order in the averaged steady Reynolds number" decay (Re 10 → ≈1) "in substantial agreement" with ref. 15; the decay is reversible under flow inversion, which swelling — being irreversible — cannot explain. The initial experimental ramp was **removed** before comparison (finite pressure rise time in experiment vs instantaneous in simulation), and the simulated peak (Re = 10) sits visibly above the first retained experimental points (≈5–6). No error metric, no uncertainty, no held-out condition, single fitted θ. What is genuinely predictive here is the *shape, timescale and reversibility* of the transient; the magnitude of the steady reduction is tuned.

**(b) Migration timescale.** They report `τ*_m ≈ H/(V_max τ_ν) = 7.1` as the time for all fines to reach the filter, and call the match to Fig. 3's decay "remarkable good agreement." **Arithmetic flag:** the printed formula with the printed values gives 80/(15 × 1.33) ≈ 4.0, not 7.1. The printed value is recoverable only with a velocity ≈8.5, i.e. roughly `V_max × (1 − φ)` — an unstated superficial/interstitial distinction. Either way, **in SI this is ~0.6–1.1 s**, whereas the paper's own introduction puts the flow-decline "phase 1b" at 4–5 s. The mechanism as parameterized is several times faster than the phenomenon it is invoked to explain; that gap is not addressed.

**(c) Solute sweeps — no experimental comparison.** Figs. 7–11 are parameter studies. Findings: cumulative output peaks at 0.014 % (θ = 0.002, t\* ≈ 15) rising to 0.04 % (θ = 0.0058, t\* ≈ 95); `D_b` varied over nearly two decades changes the peak by <5 %; `D_r` from 0.0005 → 0.02 raises the peak from 0.04 % to 0.12 % and moves all release into t\* < 30. Conclusion drawn — `D_r` and `D_s`, not `D_b`, control in-cup content — follows from the sweeps but is untested against data.

**(d) Per-compound kinetics — the only chemistry comparison, and it is weaker than the abstract implies.** Fig. 13 plots experimental transient extraction ratio for caffeine, trigonelline and chlorogenic acid (two replicate series each, labelled I and II, ~8–10 points per series out to ~60 s) against simulated curves at `D_s` = 0.02 / 0.005 / 0.0005 / 0. Source of the experimental data: their ref. 63, Navarini et al., ASIC 2008 — **titled "Hyper espresso coffee extraction," i.e. the illy HIP capsule system, not the "traditional espresso extraction" the abstract and §IV.B claim.** Specific concerns, in order of severity:
  1. **The chlorogenic-acid claim is not visibly supported.** The text says decreasing `D_s` matches CGA "accurately" but names no value; the plotted `D_s = 0.0005` curve reaches only ≈0.65 at 35 s while the CGA points are ≈0.95 by 40 s. The CGA data sit close to (slightly below) caffeine, so the fitted value would lie between 0.005 and 0.0005 — a curve that is not drawn. Of the three compounds, only two have a demonstrated fit.
  2. **One fitted parameter per compound against one curve per compound.** `D_s` is fitted, so the agreement is a one-parameter interpolation of relaxation time, not a prediction. The abstract's "excellent results" should be read as "a monotone one-parameter family can be tuned through each curve."
  3. **The time axis is anchored on a disputed length.** SI time comes from `τ_ν = (400 µm)²/ν = 0.16 s`, but §III.B declares the simulated coarses to be 500 µm. At 500 µm, `τ_ν = 0.25 s` and the whole Fig. 13 abscissa stretches by 56 %, shifting every fitted `D_s`. The `D_s` values are therefore only defined relative to an ambiguous anchor.
  4. **Brew conditions are absent.** No dose, ratio, temperature, pressure, basket or flow trace is given for the Fig. 13 experiment, so the curves cannot be attached to any registry configuration.
  5. Fig. 13's y-axis is labelled "extraction ratio [%]" but runs 0–1.2, i.e. it is a fraction; the legend lists "trigonelline (II)" twice where (I) and (II) are meant.

**(e) Table II is simulation output, not measurement.** The compound proportions at 5/10/20/30 s (caffeine 38.0→40.8 %, trigonelline 25.7→22.7 %, CGA 36.3→36.5 %; each row sums to 100.0) are computed from the model *after* per-compound `D_s` was fitted. It is a re-expression of the fits, not independent evidence for a taste-balance-vs-shot-time claim.

**Overall:** hydrodynamics = qualitative agreement on shape/reversibility with one fitted θ; chemistry = per-compound one-parameter curve fits against secondary, condition-unspecified data from a likely non-traditional extraction system. Nothing here is verification-gated or independently validated.

## Assumptions and validity range
- **2D**, periodic transversely, single random disc packing. The authors are explicit that this "does not have the ambition of reproducing realistic values of a full 3D coffee bed" and describe the approach as reverse-engineering a 2D system to match 3D dimensionless groups.
- Fully saturated from t = 0 — no imbibition, no dry-bed front, no first-drip.
- Grains **rigid, fixed and non-eroding**: no swelling, no compaction, no rearrangement, no CO₂. The intro lists swelling as a primary phenomenon, then omits it (and uses its irreversibility as the argument for fines instead).
- Fines are passive tracers with **no feedback on the flow while mobile**, no fines–fines interaction, no intra-bed clogging, no size distribution, and no source (no generation from grains). *All* impedance arises in the filter buffer layer. Deposition is binary and irreversible except under flow reversal.
- Filter geometry is a fitted abstraction: its thickness is unreported and θ absorbs everything about how much resistance it adds. **Real basket/screen resistance (registry gap G9) is not modelled and cannot be separated from θ.**
- Solute release has no partition coefficient, no saturation, no temperature dependence and no depletion of an inventory; the rectifier `D̄ = 0 if c_fluid > c_solid` is the entire irreversibility.
- `D_s`, `D_r`, `D_b` are constants per compound; no coupling to local concentration, temperature or bed history.
- **Stated-inequality error (their §II.C):** the text argues intra-granular diffusion is "strongly hindered by the internal cellular structure" and concludes "`D_s > D_b` is expected." Hindrance implies `D_s < D_b`. The simulations run both orderings (e.g. `D_s = 0.02` with `D_b = 0.005`), so the fitted values inherit no physical constraint from this argument.
- Isothermal throughout; no viscosity rise from dissolved solids; no lipids/emulsion/crema; Newtonian liquor. All acknowledged as future work.
- **Silent on:** tamp/stress state, pump characteristic and headspace, unsaturated flow, channeling, EY and TDS as measurable quantities, basket/screen resistance, PSD beyond a two-mode caricature, and any absolute permeability.
- Internal inconsistencies to carry with any reuse (in addition to those under Validation): `L_x = 10 = 5 d_fine` (§III.B) — with `d_fine` ≈ 0.125 sim this should read 5 `d_grain`; Fig. 9 right-panel caption says "fixed bulk diffusion `D_r` = 0.0005" where `D_b` = 0.005 is meant; Fig. 11 caption gives θ = 0.00058 where the text uses 0.0058; §III.B says coarses are 500 µm while §II and the `τ_ν` conversion use 450 and 400 µm respectively.

## Interface mapping
Inputs consumed: **none of the v0.1 contracts directly.** The model needs a grain-scale 2D geometry (constructible from `brewer2026.pack_generator` output, with a 3D→2D reduction that nothing justifies), a dimensionless body force, and a fines population. `GrindState.fines_fraction` is the nearest analogue to θ, but θ is fitted to flow data and absorbs filter resistance, so it is not a grind property and must not be mapped onto `fines_fraction`.
Outputs produced: **nothing that lands in `BedState` or `ShotResultState` without a full re-dimensionalization layer.** "content [%]" is not `tds_pct`; the Fig. 13 extraction ratio is per-species and has no counterpart field (the registry has no per-species solute contract — same gap flagged on `bruno2026`).
Couplings: strictly **offline calibration**, and only if reimplemented. The only defensible chain is: `pack_generator` geometry → transient mesoscale run with mobile fines → an effective κ(t; θ) curve → prior for a future `bed_dynamics` κ(t) closure. Running SPH inside the shot chain is the mega-model failure mode and is not proposed by the paper or warranted here. Adapters required: 2D→3D credibility argument, sim-units→SI anchoring (currently ambiguous by 56 % on the time axis alone), and a filter-resistance↔θ decomposition that the model cannot supply.

## Extractable data
Thin, and all of it secondary or simulated.
- **Fig. 13 experimental series (6 curves: caffeine I/II, trigonelline I/II, CGA I/II; extraction ratio vs t to ~60 s).** Digitizable, effort S, and it is dimensionally a per-species EY(t) — but the underlying source is Navarini et al., ASIC 2008 (hyper-espresso/HIP capsule), the brew conditions are unstated, and `angeloni2023` (66 shots, 8 species, time-resolved, full coefficient appendix), `maille2024` (per-species λ_fast/λ_slow with CIs) and `pannusch2024` (fitted per-species with T dependence) already dominate it on every axis. **Low priority; digitize only if a second independent per-species relaxation-ordering check is wanted.**
- **Fig. 3 experimental Re(t) points (ref. 8, Petracco 1993, direct/inverse discharge).** The genuinely interesting dataset in this paper for the κ(t) backlog — a reversible flow transient under forcing reversal. Digitizable from the figure in dimensionless (Re, t/τ_ν) form; re-dimensionalizing requires accepting the disputed τ_ν. The primary source is an ASIC 1993 proceedings volume, still not in hand (flagged on the `ellero2019` card too).
- **Table II** — simulation output, not data. Transcribe only if labelled as such.
- Figs. 4–6, 8, 10–12 are field snapshots in simulation units; nothing to transcribe.
- **No code, no repository, no data-availability statement.** Kernel, time step and filter thickness are unreported, so the runs are not reproducible from the paper.

## Overlaps and conflicts
- **`ellero2019` (card-only) — supersedes it.** Same model; this version adds `D_s` and the Fig. 13 comparison. Fold into one entry.
- **`brewer2026.streamtube` (bed_dynamics, runtime) — complements, does not validate.** Independent support that fines migration *alone* can produce reversible transient permeability, but via accumulation at the filter, not intra-bed tube redistribution. Rung B remains hypothesis-generating; this paper does not test it.
- **Backlog `κ(t) = κ0·f(P, ε, E)` (bed_dynamics)** — supplies a **third** competing mechanism (fines-at-filter) beside compaction/swelling and intra-bed migration, plus a clean discriminator: **reversibility under flow inversion**. Swelling and compaction are irreversible; filter-trapped fines are not. That is a testable prediction on a DE1-class rig and is the most useful thing in the paper. Against it: the model's own migration timescale (~0.6–1.1 s SI) is ~4× faster than the 4–5 s phase-1b decline the paper's introduction cites, so as parameterized it under-explains the target phenomenon.
- **Backlog "mass-conserving 5-state mobile-fines transport"** — the fines model is *not* a candidate. It is two-state (mobile / trapped-at-filter), size-less, with no in-bed deposition, no re-entrainment except by flow reversal, and no coupling to permeability outside the buffer layer. Same shortfall recorded on `khamitova2020`'s advected-tracer fines.
- **`brewer2026.lb_reference` / `lb_taichi` (flow, calibration) — compete methodologically, and win.** The LB twins already cover fixed-geometry flow at 0.003–0.05 % verification; SPH's marginal contribution is moving solids, which LB could also host. Nothing here is verification-gated at all.
- **`wadsworth2026.permeability` (packing, calibration)** — no conflict, no contact: this paper reports no absolute permeability and its φ = 0.48 (porosity 0.52) is loose relative to a tamped puck.
- **Registry gap G9 (basket/screen resistance)** — *touches but confounds it.* The filter buffer is the only resistance element, and θ is fitted to absorb it; the model therefore cannot separate bed from screen. Do not cite as a G9 source.
- **`cameron2020.extraction_bdf` (extraction, runtime)** — different fidelity class, no competition: no inventory accounting, no EY, no saturation, no two-population structure. The `D_r`-dominant / `D_b`-irrelevant finding is qualitatively consistent with surface-limited release but is not quantitatively comparable.
- **Backlog "extraction: multi-class solute chemistry"** — gestures at it with three compounds but does not advance it: fitted `D_s` per compound with no measured diffusivities, no acids/sugars breakdown, no partition or saturation physics, and secondary data from an unspecified brew. `angeloni2023`, `pannusch2024`, `maille2024` and `bruno2026` all sit ahead of it.
- **`egidi2024`, `perticarini2024`, `grudeva2025`** — continuum/REV lineages the paper explicitly positions itself against (its §I critique of the "single component" REV approach). Those provide anchored, dimensional models; this provides a mesoscale caricature. Complementary in framing only.
- **`foster2025.infiltration` (infiltration, runtime)** — disjoint; this model is saturated from t = 0.

## Implementation estimate
Reimplementation is **L**: weakly-compressible SPH with immobilized solid boundaries, single-particle fines, a buffer-layer filter and a rectified pair-diffusivity solute field — with kernel, time step and filter thickness unspecified, so the numerics must be re-derived. That is before the two blocking studies: a 3D-credibility argument and an SI re-anchoring (the 400/450/500 µm ambiguity alone moves the time axis by 56 %). No code or data to bootstrap. A gate cannot currently be designed: the flow validation target (ref. 8, ASIC 1993) is not in hand, and the chemistry target (ref. 63, ASIC 2008) is both unobtainable and from a different extraction system.

If the mechanism rather than the solver is wanted, the cheap paths already exist in the registry: a deposition term in the LB calibration stack, or the backlog 5-state mobile-fines transport model — either of which can be built mass-conserving and dimensional, which this cannot.

VERDICT: skip — the fuller journal version of an already-skipped 2D dimensionless SPH model, whose new content (per-compound fitted D_s) is a one-parameter curve fit against secondary, condition-unspecified hyper-espresso data with one of three compounds left undemonstrated, and whose fines-migration timescale is ~4× faster than the flow decline it is invoked to explain; cite it as the canonical reference for the reversibility-under-flow-inversion discriminator in the bed_dynamics κ(t) backlog, mark `ellero2019` superseded, and treat Fig. 3's Petracco transient as the only acquisition worth chasing — effort L
