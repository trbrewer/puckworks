# Model card: Bailey 2026 Espresso-Flow (reduced-order 2D Darcy pipeline)

**Paper/thesis:** Bailey, M. M. (2026). *Espresso Flow* (v0.1.0) [software], MIT license, https://github.com/DemetersSon83/Espresso-Flow (released 2026-03-08; CITATION.cff). Accompanying unrefereed report: Bailey, "A Reduced-Order Axisymmetric Darcy Model for Espresso Extraction," 10 Mar 2026, bundled as `Espresso_Yourself.pdf` (Eqs. 1–26 cited below). No DOI, no journal, no arXiv ID; 0 stars/forks at intake.
**Stage(s):** grind, packing, flow, extraction (touches infiltration heuristically) · **Kind:** runtime (as written; adopting it whole would be the mega-model failure mode)
**Status:** card-only

## Scope and mechanism
An integrated ~1,200-line Python codebase (numpy + matplotlib only) simulating a shot end-to-end: (1) per-cell bimodal lognormal particle sampling on a 2D axisymmetric r–z grid, perturbed by Gaussian random fields with user correlation lengths; (2) a Kozeny–Carman permeability closure with a fines penalty and a large free calibration scale; (3) a steady normalized Darcy pressure solve (dense direct solve, harmonic-mean face permeabilities), with an optional *local post-hoc* Forchheimer rescaling of velocity magnitude; (4) explicit-Euler two-pool (fast/slow) first-order extraction gated by a heuristic wetting state and local speed. The permeability field is frozen for the whole run, so hydraulics are piecewise-steady per pressure stage. The author is explicit that this is "not a CFD-grade or experimentally validated digital twin" and that parameters are "calibration knobs."

## Governing equations
Report equation numbers; all verified against source code (file:line semantics noted where the code and report differ).

1. **Grind (Eq. 2):** d ~ (1−f)·LogNormal(ln d_c, σ_c²) + f·LogNormal(ln d_f, σ_f²), per cell, n = 300 samples. d_c coarse median, d_f fines median, f fines fraction, σ_c, σ_f log-space spreads. Code detail: the fines count is deterministic round(n·f), clipped to [1, n−1], not binomial.
2. **Heterogeneity fields (Eqs. 3–5):** d_c(r,z) = d_c0·exp(σ_g ξ_g); f(r,z) = clip(f_0 + σ_f^(h) ξ_f, 0.02, 0.55); φ(r,z) = clip(φ_u − 0.10·C + σ_φ ξ_φ, 0.24, 0.50), with ξ unit-variance FFT-filtered Gaussian fields and C the compression level. The compression→porosity map is a bare linear ansatz (−0.10·C) with no source. (Report states φ clip lower bound 0.26 for the base value, code clips the base at [0.26, 0.50] then the perturbed field at [0.24, 0.50].)
3. **Sauter mean (Eq. 6):** d₃₂ = Σd³/Σd² over the cell's sample.
4. **Permeability closure (Eq. 7):** K = α_K · d₃₂²φ³ / (C_KC(1−φ)²) · exp(−γ_f f), clipped to [3×10⁻¹⁶, 2×10⁻¹³] m². α_K = 2.5×10⁻⁵ is a 4–5 order-of-magnitude multiplicative fudge on raw KC — permeability here is "emergent" only in spatial pattern; its absolute level is set by α_K.
5. **Pressure (Eqs. 8–11):** (1/r)∂_r(rK ∂_r p̂) + ∂_z(K ∂_z p̂) = 0; p̂ = 1 at z = 0 (top), p̂ = 0 at z = H, ∂_r p̂ = 0 at r = 0 and r = R. Physical pressure p = ΔP(t)·p̂ with ΔP a step schedule (preinfusion bar → brew bar at t_pre). ΔP is applied *entirely across the puck*: no machine, pump, screen, or basket-exit resistance.
6. **Darcy velocity (Eq. 12):** u_D = −(K/μ)∇p, gradients by central differences on p̂.
7. **Optional Forchheimer rescale (Eqs. 13–14):** ‖∇p‖ = (μ/K)u + βρu²/√K, solved per cell for the positive root u = [−μ/K + √((μ/K)² + 4βρ‖∇p‖/√K)]/(2βρ/√K); direction inherited from u_D. Applied in post-processing only — the pressure field is never re-solved, so the corrected velocity field does not satisfy ∇·u = 0.
8. **Outlet flow (Eq. 15):** Q_out = Σ_i max(u_z(r_i, H), 0)·π(r_out²−r_in²) over bottom-row cells; beverage mass rate = ρQ_out (Eq. 22). No water is retained by the bed: beverage accrues at full rate from t = 0 (no W_dead, no infiltration delay).
9. **Solute inventory (Eq. 16):** per cell M_sol = χ_s·M_dry, split M_f = χ_f·M_sol, M_s = (1−χ_f)·M_sol; M_dry ∝ cell solid volume, normalized to the dose.
10. **Wetting (Eq. 17):** w^{n+1} = clip(w^n + Δt·‖u‖/u_w, 0, 1). Dimensionally inconsistent as written: Δt·‖u‖/u_w has units of seconds. It works numerically only via an implicit 1 s reference timescale (i.e., the intended form is Δt·‖u‖/(u_w τ_w) with τ_w = 1 s); flagged, not corrected, per house rules.
11. **Release kinetics (Eqs. 18–21):** k_f = k_f0·exp[η_T(T−T_ref)]·w·(‖u‖/u_ref)^{a_f}, likewise k_s with a_s; per step ΔM = M^n(1−e^{−kΔt}). The velocity ratio is floored at 10⁻⁶ before exponentiation.
12. **Observables (Eqs. 24–26):** TDS_inst = 100·Δm_sol/Δm_b; TDS_cum = 100·m_sol/m_b; EY = 100·m_sol/m_dose. Extracted solids are *not* subtracted from or advected with the liquid — solids appear in the cup the instant they release, with no in-bed transport, holdup, or concentration-driven saturation (no c_sat; extraction never slows from liquid-side saturation, only from pool depletion).

Nothing has been simplified away in this transcription; the dimensional inconsistency (Eq. 17) and the mass-conservation violation of the local Forchheimer rescale are the source's, flagged inline.

## Parameters
All are config defaults (`config.py`); the author states defaults are "intentionally moderate rather than 'correct'" and lists α_K, d_c0, f_0, C, k_f0, k_s0 as the knobs to calibrate against your own shots. None is traced to a measurement.

| symbol | value | units | source |
|---|---|---|---|
| R, H (basket radius, puck depth) | 29, 9 | mm | nominal |
| grid n_r × n_z | 28 × 24 | – | nominal |
| d_c0, σ_c | 320, 0.33 | µm, ln | nominal |
| d_f, σ_f | 60, 0.25 | µm, ln | nominal |
| f_0 (fines fraction) | 0.18 | – | nominal |
| φ_u, C (uncompressed porosity, compression) | 0.43, 0.55 | – | nominal |
| σ_φ, σ_g, σ_f^(h) (heterogeneity stds) | 0.018, 0.16, 0.045 | –, ln, – | assumed |
| ℓ_r, ℓ_z (correlation lengths) | 6.0, 2.5 | mm | assumed |
| C_KC | 180 | – | nominal (KC literature ~150–180) |
| α_K (permeability scale) | 2.5×10⁻⁵ | – | assumed (declared calibration knob) |
| γ_f (fines penalty) | 3.2 | – | assumed |
| µ, ρ | 3.2×10⁻⁴, 970 | Pa·s, kg/m³ | nominal (hot water ~90 °C) |
| ΔP schedule | 2 bar / 6 s → 9 bar, 32 s total, Δt = 0.2 s | bar, s | nominal |
| β (Forchheimer) | 0.55 | – | assumed |
| dose, χ_s, χ_f | 18, 0.30, 0.62 | g, –, – | nominal/assumed |
| k_f0, k_s0 | 0.18, 0.022 | 1/s | assumed (declared calibration knobs) |
| u_ref, a_f, a_s | 0.0028, 0.32, 0.18 | m/s, –, – | assumed |
| u_w (wetting velocity ref) | 0.0018 | m/s | assumed |
| T, T_ref, η_T | 93, 93, 0.018 | °C, °C, 1/°C | nominal/assumed |

## Calibration and validation offered by the source
**None against any measurement.** The report's §3 "results" are the model's own bundled demo outputs: baseline run reaches the 36 g target at 31.6 s with EY 21.38%, cumulative TDS 10.47%, mean porosity 0.375, median K 1.72×10⁻¹⁵ m²; a 6-run Monte Carlo gives time-to-36 g = 28.77 ± 3.00 s, EY 21.60 ± 0.15%, mean TDS 9.49%. These are plausibility demonstrations, not validation — no shot data, no refractometer data, no permeability measurement, no literature curve is compared. The author says so plainly ("best viewed as a research scaffold"; calibration against shot-weight and refractometer data is listed as *future* work). Tests in `tests/` are two smoke tests (shapes/positivity), not physics gates. Note the demo's median K (1.7×10⁻¹⁵ m²) sits 1–2 orders below tamped-bed literature values held in the registry (romancorrochano2017 Table 6.1, ~10⁻¹⁴–10⁻¹³ m²), compensated by driving the full 9 bar across the puck alone; the α_K fudge absorbs the difference.

## Assumptions and validity range
- Saturated single-phase flow from t = 0; the "wetting" state gates *kinetics only* — hydraulics and outflow are full-strength on dry bed (contradicts observed ~7 s first-drip delay; foster2025 territory).
- Permeability frozen over the shot: no compaction, swelling, erosion, or fines migration (author lists all as unresolved). Cannot express the κ(t) rising-flow phenomenology.
- ΔP applied wholly across the puck: no pump characteristic, headspace, shower screen, or basket-exit resistance (G9 silent).
- Forchheimer correction is non-mass-conserving post-processing; at high β/gradients the outlet integral and the interior field are mutually inconsistent.
- Extraction has no liquid-phase concentration state: no c_sat ceiling, no advection of dissolved solids through the bed, instant appearance in cup. Early TDS_inst is an artifact of division by small beverage increments.
- Wetting law dimensionally inconsistent (implicit 1 s timescale); temperature enters only as a scalar Arrhenius-like factor on rate constants, uniform in space and time.
- Deterministic fines-count sampling understates cell-to-cell PSD variance at small n·f.
- Dense O((n_r n_z)³)-ish direct solve: fine grids get expensive fast; default 28×24 only.
- Silent on: multi-species chemistry, crema/gas, channel formation dynamics, headspace filling, puck integrity.

## Interface mapping
Inputs consumed (conceptually): GrindState (fines_fraction, mean/boulder radii map awkwardly onto its four-parameter bimodal config — adapter needed), BedState (dose, depth, area, porosity; but it *derives* k internally and ignores an imposed k_m2), MachineState (only as a two-level gauge-bar step; no P_of_t profile support without a small patch).
Outputs produced: ShotResultState-shaped traces (t, P, flow, beverage_g, TDS, EY) plus 2D fields (K, φ, p̂, u, local EY map) in `fields.npz`.
Couplings: as published it is a competing monolith, not a component. The only registry-consistent uses are offline/calibration-grade: (a) a cheap 2D field-coupled Darcy solve to test the parallel-tube (no radial exchange) approximation underlying brewer2026.streamtube — run its solver on a prescribed K field vs. the same field with radial fluxes zeroed, and quantify when correlation lengths make radial coupling matter (relevant to the ROADMAP P3 hypothesis cluster); (b) its Eq. 14 closed-form local Forchheimer root as a zero-cost first rung for the flow backlog's inertial-correction item, *with the non-conservation caveat carried explicitly*. Both uses need the K-field generation ripped out and replaced by registry closures (wadsworth2026.permeability); its extraction and wetting layers should not be adopted.

## Extractable data
Nothing of registry value: all bundled numbers (Table 1, Figs. 1–4, `docs/demo_baseline/`, `docs/demo_montecarlo/`) are outputs of the model itself under nominal parameters — they characterize the code, not coffee. The genuinely available asset is the code: MIT-licensed, pip-installable, deterministic under seed, with CSV/JSON/npz outputs — usable as a scratch harness without transcription. No experimental data exists to transcribe.

## Overlaps and conflicts
- **cameron2020.extraction_bdf (extraction, runtime):** competes and loses. Cameron's two-population model has a saturation-limited liquid phase, per-bed-volume inventory, and experimental grounding; Bailey's two-pool kinetics have no liquid concentration state, no c_sat, and heuristic velocity/wetting gates with assumed exponents. No new mechanism.
- **brewer2026.streamtube (bed_dynamics, runtime):** competes as a heterogeneity representation (2D correlated fields + field solve vs. lognormal parallel tubes). Bailey's is structurally richer (radial coupling) but its σ's are assumed, whereas streamtube's σ(φ1) closure is at least data-anchored. Complement only as the structural cross-check in Interface mapping (a).
- **wadsworth2026.permeability (packing, calibration):** supersedes Bailey's closure outright — percolation-based, angularity-aware, validated on 21 samples vs. KC with a 2.5×10⁻⁵ fudge factor and an ad hoc exp(−γ_f f) fines penalty.
- **foster2025.infiltration (infiltration, runtime):** supersedes the wetting layer — gated parameter-free vs. dimensionally inconsistent heuristic that lets beverage flow from a dry bed.
- **Flow backlog (Forchheimer/inertial):** the one novel-ish touchpoint. Eq. 14 is the standard quadratic root applied locally; cheaper than a coupled nonlinear solve but non-conservative. Record as rung-0 option; a real implementation should re-solve pressure with the nonlinear closure.
- **kim2026 (card-only, skip):** both are unvalidated theory/code frameworks; Bailey is the healthier specimen (runs, self-consistent Darcy core, honest limitations section) but shares the zero-data problem.
- **G9 (basket/screen resistance), G10 (liquor rheology):** silent; constant Newtonian µ, no exit resistance.

## Implementation estimate
Adopting any piece: effort M — the useful fragments (2D axisymmetric FD Darcy solve, ~150 lines; Forchheimer root, ~10 lines) are cheap to re-derive natively inside puckworks contracts, and the surrounding grind/packing/extraction layers would all be replaced by registered components anyway, so wrapping the repo buys little over rewriting. Gate design if the structural cross-check (a) is ever scheduled: same prescribed K field through (i) this 2D solve, (ii) radially-decoupled columns; acceptance = quantified Q_out and outlet-flux-variance difference as a function of ℓ_r/R, reported into the P3 hypothesis table. No gate against the source itself is possible — there is nothing measured to hit.

VERDICT: skip — a competently written but entirely unvalidated monolith whose every stage is superseded by a registered component; keep the citation as rung-0 for the Forchheimer backlog and as a possible 2D-vs-parallel-tube structural cross-check harness — effort M
